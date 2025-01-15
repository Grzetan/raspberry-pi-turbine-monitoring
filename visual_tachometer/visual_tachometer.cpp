#include <opencv2/opencv.hpp>
#include <iostream>

int main(int argc, char** argv) {
    cv::VideoCapture cap("/home/grzetan/Projects/raspberry-pi-turbine-monitoring/videos/1.mp4");

    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open video file" << std::endl;
        return -1;
    }

    cv::Mat frame;
    while (true) {
        cap >> frame;
        if (frame.empty()) {
            break;
        }

        cv::imshow("Frame", frame);
        std::cout << "Press any key to display the next frame..." << std::endl;
        cv::waitKey(0); // Wait for a keystroke in the window
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}