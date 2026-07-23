#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration ,PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """
    Launches the full IVAR perception pipeline:
        1. apriltag_node      — detects tags from camera
        2. pose_transformer   — converts poses to map frame

    Usage:
        ros2 launch ivar_perception apriltag.launch.py
        ros2 launch ivar_perception apriltag.launch.py robot_id:=robot2
    """

    pkg_path = get_package_share_directory('ivar_perception')
    config_file = os.path.join(pkg_path, 'config', 'tags.yaml')

    robot_id_arg = DeclareLaunchArgument(
        'robot_id',
        default_value='aqua_robot_1',
        description='Robot identifier for multi-robot deployment'
    )

    camera_frame_arg = DeclareLaunchArgument(
        'camera_frame',
        default_value='camera_link',
        description='Camera frame name from URDF'
    )

    robot_id = LaunchConfiguration('robot_id')


    # Node 1 — AprilTag detector
    apriltag_node = Node(
        package='ivar_perception',
        executable='apriltag_node',
        name='apriltag_node',
        namespace = robot_id,
        # parameters loads config from yaml file
        # overrides defaults declared in the node
        parameters=[config_file],
        # remappings connect this node's topics to the right camera topics
        # left side = node's internal topic name
        # right side = actual topic published by camera/Gazebo
        remappings=[
            ('image_rect',  PathJoinSubstitution(['/' , robot_id , 'waste_camera' , 'image_raw'])),
            ('camera_info', PathJoinSubstitution(['/' , robot_id , 'waste_camera' , 'camera_info'])),
            ('detections',  PathJoinSubstitution(['/' , robot_id , 'detections'])),
        ],
        output='screen'  # print logs to terminal
    )

    # Node 2 — Pose transformer
    pose_transformer_node = Node(
        package='ivar_perception',
        executable='pose_transformer',
        name='pose_transformer',
        namespace = robot_id , 
        parameters=[
            config_file,
            # Override robot_id with command line argument
            # so each robot can have different id without editing yaml
            {'robot_id': LaunchConfiguration('robot_id')},
            {'camera_frame': LaunchConfiguration('camera_frame')},
        ],
        remappings=[
            ('detections',   PathJoinSubstitution(['/' , robot_id , 'detections'])),
            ('tag_poses_map', PathJoinSubstitution(['/' , robot_id , 'tag_poses_map'])),
        ],
        output='screen'
    )

    # ── Launch Description ────────────────────────────────────────────────────
    # This is what ROS2 actually executes
    return LaunchDescription([
        robot_id_arg,
        camera_frame_arg,
        apriltag_node,
        pose_transformer_node,
    ])