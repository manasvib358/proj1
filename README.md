# 🚤 Autonomous Waste Detection and Multi-Agent Task Allocation Framework

A ROS 2 and Gazebo based multi-agent robotic system for autonomous waste detection, localization, and cooperative task allocation in aquatic environments.

---

## 📖 Overview

The **Autonomous Waste Detection Framework** is a multi-agent robotic system designed to simulate intelligent waste detection and collaborative task allocation in water bodies. The project leverages **ROS 2**, **Gazebo**, and **Nav2** to enable multiple autonomous surface vehicles (ASVs) to explore environments, detect floating waste, share information, and coordinate cleanup tasks efficiently.

The framework combines robotics, computer vision, autonomous navigation, distributed communication, and swarm intelligence to create a scalable solution for smart environmental monitoring and waste management.

---

## 🎯 Objectives

* Detect floating waste autonomously using computer vision.
* Localize detected waste objects accurately.
* Enable multiple robots to collaboratively explore the environment.
* Share detections among robots in real time.
* Avoid duplicate detections and redundant task assignments.
* Dynamically assign cleanup tasks to the most suitable robot.
* Build a scalable swarm robotics framework for aquatic waste management.

---

# ✨ Features

* 🤖 Multi-agent autonomous surface vehicles
* 🗺️ Autonomous navigation using Nav2
* 📷 Waste detection using AprilTags and OpenCV
* 📍 Global localization of detected waste
* 📡 Inter-robot communication using ROS2 topics/services
* 🗄️ Shared database for synchronized information
* 🚧 Obstacle avoidance
* 🔄 Dynamic task allocation
* 🌊 Scalable aquatic environment simulation
* ⚡ Real-time coordination among robots

---

# 🏗️ System Architecture

```text
                    Gazebo Simulation

        +-------------------------------+
        |     Aquatic Environment        |
        |                               |
        | Floating Waste + Obstacles    |
        +-------------------------------+

          ↓                 ↓

   Robot 1             Robot 2             Robot 3

 Navigation         Navigation         Navigation
 Localization       Localization       Localization
 Camera             Camera             Camera
 LiDAR              LiDAR              LiDAR

          ↓                 ↓

        Waste Detection (AprilTags)

                 ↓

        Position Estimation

                 ↓

      Shared ROS2 Database Node

                 ↓

      Dynamic Task Allocation

                 ↓

 Assigned Robot navigates to waste
```

---

# 🛠️ Tech Stack

| Domain               | Technology              |
| -------------------- | ----------------------- |
| Robotics Framework   | ROS 2                   |
| Simulation           | Gazebo                  |
| Navigation           | Nav2                    |
| Mapping              | SLAM Toolbox (Optional) |
| Computer Vision      | OpenCV                  |
| Marker Detection     | AprilTag                |
| Programming Language | Python                  |
| Visualization        | RViz                    |
| Version Control      | Git & GitHub            |

---

# 🤖 Robot Configuration

Each Autonomous Surface Vehicle (ASV) contains:

* Navigation Stack
* Localization Node
* Camera
* LiDAR
* IMU
* GPS
* Odometry
* Perception Node
* Communication Interface

Each robot operates independently under its own ROS2 namespace while collaborating through a shared communication framework.

---

# 🔍 Waste Detection Pipeline

```text
RGB Camera

      ↓

AprilTag Detection

      ↓

Marker ID Extraction

      ↓

Pose Estimation

      ↓

Global Coordinate Transformation

      ↓

Duplicate Detection Filtering

      ↓

Database Update
```

---

# 📡 Communication Framework

The robots continuously exchange:

* Detected waste locations
* Robot positions
* Navigation status
* Active tasks
* Availability

A centralized ROS2 database node synchronizes information among all agents and prevents duplicate detections.

---

# 🧭 Navigation

The project utilizes the **ROS2 Nav2 Stack** to provide:

* Global path planning
* Local obstacle avoidance
* Waypoint navigation
* Recovery behaviors
* Dynamic route updates
* Cooperative navigation between robots

Robots share obstacle and traffic information to reduce congestion and avoid overlapping paths.

---

# 🗂️ Task Allocation

Once waste is detected, the system assigns it to the most suitable robot based on:

* Distance to target
* Robot availability
* Current workload
* Target priority

Possible allocation strategies include:

* Greedy Algorithm
* Hungarian Algorithm
* Auction-Based Allocation

Assignments are dynamically updated whenever:

* New waste appears
* Robots become unavailable
* Workload becomes unbalanced

---

# 📂 Repository Structure

```text
Autonomous-Waste-Detection/
│
├── launch/
├── .gitignore/
├── install/
├── build/
├── log/
├── src/
│   ├── aqua_robot_gazebo/
│   ├── ivar_perception/
|                    ├── ivar_perception/
|                    |                 ├── AprilTag_detector.py
|                    |                 ├── pose_estimator.py
|                    |                 ├── __init__.py
|                    ├── config/
|                    ├── launch/
│                    ├── resource/
|                    ├── test/
|                    ├── package.xml
|                    ├── setup.config
|                    ├── setup.py
|
│
└── README.md
```

---

# 🚀 Installation

## Clone the repository

```bash
git clone https://github.com/<username>/Autonomous-Waste-Detection.git
cd Autonomous-Waste-Detection
```

## Build Workspace

```bash
colcon build
```

## Source Workspace

```bash
source install/setup.bash
```

## Launch Simulation

```bash
ros2 launch <package_name> simulation.launch.py
```

---

# ▶️ Running the Project

Launch Gazebo

```bash
ros2 launch <package_name> gazebo.launch.py
```

Launch Navigation

```bash
ros2 launch <package_name> navigation.launch.py
```

Launch Waste Detection

```bash
ros2 run <package_name> perception_node
```

Launch Task Allocation

```bash
ros2 run <package_name> task_allocator
```

---

# 📊 Expected Workflow

1. Robots explore the aquatic environment.
2. AprilTag Detection pipeline will detect the apriltag. 
3. Task allocator assigns the nearest available robot.
4. Database updates robot status.

---

# 📌 Future Improvements

* Integrate AprilTag to the waste objects .
* Integrate the perception pipeline with gazebo simulation .
* Robots will work autonomously.
* Integration with task allocator and database.

---

# 🤝 Contributions

Contributions are welcome.

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# ⭐ Acknowledgements

* ROS 2 Community
* Gazebo Simulator
* OpenCV
* AprilTag Library
* Nav2
* SLAM Toolbox
* IIT Indore Summer of Code

---

> Building intelligent, collaborative robotic systems for a cleaner and smarter environment.

