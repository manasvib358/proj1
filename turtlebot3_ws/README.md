# TurtleBot3 Multi-Robot Waste Detection System

## Project Overview

This project is a ROS 2 Humble-based multi-robot waste detection system developed using TurtleBot3, Gazebo, OpenCV, and YOLOv8. The objective is to simulate multiple autonomous robots that detect waste objects and navigate toward them in a simulated environment.

## Technologies Used

* ROS 2 Humble
* Python
* Gazebo
* TurtleBot3
* OpenCV
* YOLOv8 (Ultralytics)
* RViz
* Nav2

## Current Project Status

**Status:** In Progress

The project successfully performs waste detection using YOLOv8 in simulation and includes the foundation for a multi-robot system. Navigation and autonomous object-following are under development.

## Completed Work

* Created a ROS 2 workspace for the project.
* Developed the `waste_detector` package.
* Integrated YOLOv8 for real-time object detection.
* Added camera support to the TurtleBot3 model.
* Published waste detection messages using ROS 2 topics.
* Built a multi-robot simulation environment.
* Created launch files for multiple robots.
* Added robot models and simulation configuration.
* Developed supporting packages for navigation, task allocation, obstacle avoidance, and a shared database.
* Verified robot movement using ROS 2 velocity commands.
* Integrated OpenCV image processing with the detection pipeline.

## Future Work

* Complete the robot controller for autonomous movement.
* Make robots automatically approach detected waste.
* Stop the robot at the target object.
* Integrate autonomous navigation with waste detection.
* Extend autonomous behavior to Robot 2 and Robot 3.
* Improve obstacle avoidance during navigation.
* Complete multi-robot coordination and task allocation.
* Perform full system testing and bug fixing.
* Optimize detection and navigation performance.

## Project Structure

```text
turtlebot3_ws/
└── src/
    ├── waste_detector/
    ├── waste_detection_robot/
    ├── multi_robot_system/
    ├── navigation_pkg/
    ├── task_allocation/
    ├── shared_database/
    ├── obstacle_avoidance/
    ├── my_robot_controller/
    ├── turtlebot3/
    └── turtlebot3_simulations/
```

## Build

```bash
cd ~/turtlebot3_ws
colcon build
source install/setup.bash
```

## Run

Launch the simulation:

```bash
ros2 launch multi_robot_system multi_robot.launch.py
```

Run the waste detector:

```bash
ros2 run waste_detector waste_detector_node
```

## Author

Nalavath Rohan
