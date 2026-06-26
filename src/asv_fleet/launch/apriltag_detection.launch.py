"""
Starts one apriltag_ros detector per robot, each subscribed to that
robot's own camera feed.

Prerequisite:
    sudo apt install ros-humble-apriltag-ros

Run AFTER spawn_fleet.launch.py is up and the cameras are publishing:
    ros2 launch asv_fleet apriltag_detection.launch.py

Each detector publishes to /<robot_name>/tag_detections
(apriltag_msgs/msg/AprilTagDetectionArray) once it sees a tag.

NOTE: the executable name 'apriltag_node' matches the common ROS2 port
of apriltag_ros. If this errors with "executable not found", run
`ros2 pkg executables apriltag_ros` to see what's actually installed
and swap the executable name below.
"""
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def make_detector(name):
    tags_yaml = os.path.join(
        get_package_share_directory('asv_fleet'), 'config', 'tags.yaml'
    )
    return Node(
        package='apriltag_ros',
        executable='apriltag_node',
        name='apriltag_detector',
        namespace=name,
        remappings=[
            ('image_rect', f'/{name}/camera/image_raw'),
            ('camera_info', f'/{name}/camera/camera_info'),
        ],
        parameters=[tags_yaml],
        output='screen'
    )


def generate_launch_description():
    return LaunchDescription([
        make_detector('red_asv'),
        make_detector('green_asv'),
        make_detector('blue_asv'),
    ])
