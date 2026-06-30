#!/usr/bin/env python3
"""
Launch file for the Aqua Waste Detection Robot Gazebo simulation.
Starts Gazebo with the lake world, spawns the robot, and launches ROS2 nodes.

Usage:
    ros2 launch aqua_robot_gazebo lake_simulation.launch.py

Optional args:
    use_sim_time:=true       (default: true)
    gui:=true                (default: true  — set false for headless)
    robot_x:=0.0             (default: 0.0)
    robot_y:=0.0             (default: 0.0)
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import (
    get_package_share_directory,
    get_package_prefix,
)

def generate_launch_description():

pkg_share = get_package_share_directory('asv_fleet')
asv_share = get_package_share_directory('asv_fleet')
    # ----------------------------------------------------------------
    # Declare arguments
    # ----------------------------------------------------------------
    declared_args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('robot_x', default_value='0.0'),
        DeclareLaunchArgument('robot_y', default_value='0.0'),
        DeclareLaunchArgument('robot_z', default_value='0.04'),
    ]

    use_sim_time   = LaunchConfiguration('use_sim_time')
    gui            = LaunchConfiguration('gui')
    robot_x        = LaunchConfiguration('robot_x')
    robot_y        = LaunchConfiguration('robot_y')
    robot_z        = LaunchConfiguration('robot_z')

    # ----------------------------------------------------------------
    # Paths
    # ----------------------------------------------------------------
    world_file = os.path.join(pkg_share, 'worlds', 'lake_waste.world')
xacro_file = os.path.join(asv_share, 'urdf', 'asv_robot.xacro')

robot_description_content = Command([
    FindExecutable(name='xacro'),
    ' ',
    xacro_file,
    ' ',
    'robot_name:=red_asv',
    ' ',
    'color_r:=1.0',
    ' ',
    'color_g:=0.0',
    ' ',
    'color_b:=0.0',
])
    # ----------------------------------------------------------------
    # 1. Gazebo server
    # ----------------------------------------------------------------
    gazebo_server = ExecuteProcess(
        cmd=[
            'gzserver',
            '--verbose',
            '-s', 'libgazebo_ros_factory.so',
            '-s', 'libgazebo_ros_init.so',
            world_file,
        ],
        output='screen',
    )

    # ----------------------------------------------------------------
    # 2. Gazebo client (GUI)
    # ----------------------------------------------------------------
    gazebo_client = ExecuteProcess(
        cmd=['gzclient', '--verbose'],
        output='screen',
        condition=IfCondition(gui),
    )

    # ----------------------------------------------------------------
    # 3. Robot State Publisher
    # ----------------------------------------------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': ParameterValue(
    robot_description_content,
    value_type=str
),
             'use_sim_time': use_sim_time}
        ],
    )
    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-entity', 'red_asv',
                    '-topic', '/red_asv/robot_description',
                    '-x', robot_x,
                    '-y', robot_y,
                    '-z', robot_z,
                ],
                output='screen',
            )
        ],
    )

    # ----------------------------------------------------------------
    # 5. Joint State Publisher
    # ----------------------------------------------------------------
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # ----------------------------------------------------------------
    # 6. RViz2 (optional, for visualising camera/LiDAR topics)
    # ----------------------------------------------------------------
    rviz_config = os.path.join(pkg_share, 'config', 'aqua_robot.rviz')
    rviz2 = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='screen',
                arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
                parameters=[{'use_sim_time': use_sim_time}],
                condition=IfCondition(gui),
            )
        ],
    )

    return LaunchDescription(
        declared_args + [
            gazebo_server,
            gazebo_client,
            robot_state_publisher,
            spawn_robot,
            joint_state_publisher,
            rviz2,
        ]
    )
