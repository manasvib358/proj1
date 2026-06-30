#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_share = get_package_share_directory('aqua_robot_gazebo')

    world = os.path.join(pkg_share, 'worlds', 'lake_waste.world')
    urdf = os.path.join(pkg_share, 'urdf', 'aqua_robot.urdf')

    gazebo = ExecuteProcess(
        cmd=['gzserver', '--verbose', '-s', 'libgazebo_ros_factory.so', world],
        output='screen'
    )

    gui = ExecuteProcess(
        cmd=['gzclient'],
        output='screen'
    )

    with open(urdf, 'r') as f:
        robot_desc = f.read()

    positions = [
        (0, 0, "aqua_robot_1"),
        (2, 0, "aqua_robot_2"),
        (-2, 0, "aqua_robot_3"),
    ]

    robots = []

    i = 0
    for x, y, name in positions:

        rsp = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            namespace=name,
            output='screen',
            parameters=[{
                'robot_description': robot_desc,
                'use_sim_time': True
            }]
        )

        spawn = TimerAction(
            period=3.0 + i * 2.0,
            actions=[
                Node(
                    package='gazebo_ros',
                    executable='spawn_entity.py',
                    output='screen',
                    arguments=[
                        '-entity', name,
                        '-topic', f'/{name}/robot_description',
                        '-x', str(x),
                        '-y', str(y),
                        '-z', '0.1'
                    ],
                )
            ]
        )

        robots += [rsp, spawn]
        i += 1

    return LaunchDescription([gazebo, gui] + robots)
