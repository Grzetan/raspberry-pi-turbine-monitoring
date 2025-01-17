#include <opencv2/opencv.hpp>
#include <iostream>
#include <thread>
#include <sys/types.h>
#include <sys/stat.h>
#include <fstream>
#include "argparse.hpp"


#define DEBUG false

std::string fifo_path = "/tmp/visual_tachometer_fifo";
bool VIDEO = true;
bool CLOCKWISE = false;
int MAX_QUEUE_SIZE = 5;


void fill_circle_pixels(std::vector<cv::Point3d>& pixels, const cv::Point2d& center, float inner_radius, float outer_radius, const cv::Point2d& frame_size){
    float diagonal = 2 * inner_radius;
    float inner_square_side = diagonal / sqrt(2);

    for (float y = center.y - outer_radius; y <= center.y + outer_radius; y++){
        for (int x = center.x - outer_radius; x <= center.x + outer_radius; x++)
        {
            // Automatically skip pixels inside the inner square
            if (x > center.x - inner_square_side / 2 && x < center.x + inner_square_side / 2 && y > center.y - inner_square_side / 2 && y < center.y + inner_square_side / 2){
                continue;
            }

            int dx = x - center.x;
            int dy = y - center.y;
            int distanceSquared = dx * dx + dy * dy;

            if (distanceSquared >= inner_radius * inner_radius && distanceSquared <= outer_radius * outer_radius)
            {
                if (x >= 0 && x < frame_size.x && y >= 0 && y < frame_size.y)
                {
                    double angle = atan2(dy, dx) * 180 / CV_PI - 90;
                    if (angle < 0) {
                        angle += 360;
                    }
                    pixels.push_back(cv::Point3d(x, y, angle));
                }
            }
        }
    }
}

bool qualify(const cv::Vec3d& pixel){
    double gray = 0.299 * pixel[2] + 0.587 * pixel[1] + 0.114 * pixel[0];
    return gray > 200; //|| gray < 40;
}

cv::Vec3d get_color(double angle){
    double gray_value = 255 * (1 - angle / 360.0);
    // std::cout << angle << ", " << gray_value << std::endl;
    return cv::Vec3d(gray_value, gray_value, gray_value);
}

double calulate_rpm(const std::deque<std::pair<double, std::chrono::_V2::steady_clock::time_point>>& positions){
    if (positions.size() < 2){
        return 0;
    }

    double sum = 0;
    for (int i = 1; i < positions.size(); i++){
        double angle_diff = positions[i].first - positions[i - 1].first;
        if (!CLOCKWISE && angle_diff > 0){
            angle_diff = 360 - angle_diff;
        } else if (CLOCKWISE && angle_diff < 0) {
            angle_diff = 360 + angle_diff;
        } else {
            angle_diff = abs(angle_diff);
        }
        sum += angle_diff;
    }

    double time_diff = std::chrono::duration_cast<std::chrono::milliseconds>(positions.back().second - positions.front().second).count();
    return (sum / 360.0) / (time_diff / 60000);
}

bool create_fifo(const std::string& fifo_path){
    if (mkfifo(fifo_path.c_str(), 0666) == -1 && errno != EEXIST) {
        std::cerr << "Error: Could not create FIFO." << std::endl;
        return false;
    }
    return true;
}

bool write_to_fifo(std::ofstream& fifo_out, double rpm){
    fifo_out << rpm << "\n";
    fifo_out.flush();
     if (fifo_out.fail()) {
        std::cerr << "Error writing to FIFO." << std::endl;
        fifo_out.close();
        return false;
    }
    return true;
}

int main(int argc, char **argv)
{
    argparse::ArgumentParser args("Turbine Monitoring");

    args.add_argument("--webcam_index")
        .help("Path to video")
        .scan<'i', int>();

    args.add_argument("--video_path")
        .help("Path to video");

    args.add_argument("--clockwise")
        .help("Pass if turbine is rotating clockwise")
        .default_value(false)
        .implicit_value(true);
    
    try {
        args.parse_args(argc, argv);
    } catch (const std::runtime_error& err) {
        std::cerr << err.what() << std::endl;
        std::cerr << args;
        std::exit(1);
    }
    
    bool is_webcam = args.present("--webcam_index").has_value();
    bool is_video = args.present("--video_path").has_value();
    if(is_webcam == is_video){
        std::cerr << "Error: Please provide either video path or webcam index" << std::endl;
        std::cerr << args;
        std::exit(1);
    }

    VIDEO = is_video;
    CLOCKWISE = args.get<bool>("--clockwise");

    cv::VideoCapture cap;
    if(is_video){
        cap.open(args.get<std::string>("--video_path"));
    }else{
        cap.open(args.get<int>("--webcam_index"));
    }

    if (!cap.isOpened()){
        std::cerr << "Error: Could not open video capture." << std::endl;
        return -1;
    }

    if(!create_fifo(fifo_path)){
        return -1;
    }
    std::ofstream fifo_out(fifo_path, std::ios::out);
    if (!fifo_out.is_open()) {
        std::cerr << "Error opening FIFO for writing." << std::endl;
        return 1;
    }

    # if VIDEO
    double fps = cap.get(cv::CAP_PROP_FPS);
    std::cout << "FPS: " << fps << std::endl;
    double frame_time = 1000.0 / fps;
    # endif

    cv::Point2d center(590, 900);
    cv::Point2d frame_size(1280, 720);
    int innerRadius = 700;
    int outerRadius = innerRadius + 100;
    std::vector<cv::Point3d> pixels;
    fill_circle_pixels(pixels, center, innerRadius, outerRadius, frame_size);

    cv::Mat frame;

    # if DEBUG
    int frame_count = 0;
    auto start = std::chrono::high_resolution_clock::now();
    # endif

    std::deque<std::pair<double, std::chrono::_V2::steady_clock::time_point>> positions; 

    auto start_time = std::chrono::steady_clock::now();
    
    # if VIDEO
    auto previous_time = start_time;
    # endif

    while (true){
        cap >> frame;
        if (frame.empty()){
            break;
        }

        auto current_time = std::chrono::steady_clock::now();
        # if VIDEO // If the algorithm is ran on the video, adjust the time to video FPS
        double elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - previous_time).count();

        if (elapsed_time < frame_time){
            std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(frame_time - elapsed_time)));
        }
        
        previous_time = current_time;
        # endif

        double max_angle = -1;
        double min_angle = 361;
        for (const cv::Point3d& pixel : pixels){
            if(qualify(frame.at<cv::Vec3b>(pixel.y, pixel.x))){
                if (pixel.z > max_angle){
                    max_angle = pixel.z;
                }
                if (pixel.z < min_angle){
                    min_angle = pixel.z;
                }
            }
            
            # if DEBUG
            frame.at<cv::Vec3b>(pixel.y, pixel.x) = get_color(pixel.z);
            # endif
        }

        if(min_angle != 361){ // If marker was found on the frame
            double angle = (max_angle + min_angle) / 2;
            if(positions.size() > MAX_QUEUE_SIZE){
                positions.pop_front();
            }
            positions.push_back(std::make_pair(angle, current_time));

            double rpm = calulate_rpm(positions);
            if(!write_to_fifo(fifo_out, rpm)){
                break;
            }
        }

        # if DEBUG
        frame_count++;
        cv::imshow("Frame", frame);
        cv::waitKey(1);
        # endif
    }

    # if DEBUG
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    double calulated_fps = frame_count / elapsed.count();
    std::cout << "FPS: " << calulated_fps << std::endl;
    # endif

    fifo_out.close();
    cap.release();
    # if DEBUG
    cv::destroyAllWindows();
    # endif
    return 0;
}