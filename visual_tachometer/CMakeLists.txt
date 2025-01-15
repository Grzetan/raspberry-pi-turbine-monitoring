cmake_minimum_required(VERSION 3.15)
project(visualTachometer)

set(CMAKE_CXX_STANDARD 17)
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
add_executable(visualTachometer visual_tachometer.cpp)
target_link_libraries(visualTachometer ${OpenCV_LIBS})