#include <opencv2/opencv.hpp>
#include <iostream>

void fill_circle_pixels(std::vector<cv::Point2d>& pixels, const cv::Point2d& center, float inner_radius, float outer_radius){
    float diagonal = 2 * innerRadius;
    float inner_square_side = diagonal / sqrt(2);

    for (float y = centerY - outerRadius; y <= centerY + outerRadius; y++){
        for (int x = centerX - outerRadius; x <= centerX + outerRadius; x++)
        {
            // Automatically skip pixels inside the inner square
            if (x > centerX - inner_square_side / 2 && x < centerX + inner_square_side / 2 && y > centerY - inner_square_side / 2 && y < centerY + inner_square_side / 2){
                continue;
            }

            int dx = x - centerX;
            int dy = y - centerY;
            int distanceSquared = dx * dx + dy * dy;

            if (distanceSquared >= innerRadius * innerRadius && distanceSquared <= outerRadius * outerRadius)
            {
                if (x >= 0 && x < frame.cols && y >= 0 && y < frame.rows)
                {
                    frame.at<cv::Vec3b>(y, x) = cv::Vec3b(0, 0, 255);
                }
            }
        }
    }
}

int main(int argc, char **argv)
{
    cv::VideoCapture cap("/home/grzetan/Projects/raspberry-pi-turbine-monitoring/videos/1.mp4");

    if (!cap.isOpened())
    {
        std::cerr << "Error: Could not open video file" << std::endl;
        return -1;
    }

    int centerX = 590;
    int centerY = 900;
    int innerRadius = 700;
    int outerRadius = innerRadius + 100;

    // Calculate the length of square inside the inner circle
    float diagonal = 2 * innerRadius;
    float inner_square_side = diagonal / sqrt(2);

    cv::Mat frame;
    while (true)
    {
        cap >> frame;
        if (frame.empty())
        {
            break;
        }

        // Iterate through the bounding box of the outer circle
        std::cout << centerY - outerRadius << ", " << centerY + outerRadius << std::endl;
        for (float y = centerY - outerRadius; y <= centerY + outerRadius; y++)
        {
            for (int x = centerX - outerRadius; x <= centerX + outerRadius; x++)
            {
                // Automatically skip pixels inside the inner square
                if (x > centerX - inner_square_side / 2 && x < centerX + inner_square_side / 2 && y > centerY - inner_square_side / 2 && y < centerY + inner_square_side / 2)
                {
                    continue;
                }

                int dx = x - centerX;
                int dy = y - centerY;
                int distanceSquared = dx * dx + dy * dy;

                if (distanceSquared >= innerRadius * innerRadius && distanceSquared <= outerRadius * outerRadius)
                {
                    if (x >= 0 && x < frame.cols && y >= 0 && y < frame.rows)
                    {
                        frame.at<cv::Vec3b>(y, x) = cv::Vec3b(0, 0, 255);
                    }
                }
            }
        }

        cv::imshow("Frame", frame);
        std::cout << "Press any key to display the next frame..." << std::endl;
        cv::waitKey(0); // Wait for a keystroke in the window
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}