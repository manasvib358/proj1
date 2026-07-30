#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    nav2_launch = os.path.join(
        get_package_share_directory('multi_robot_system'),
        'launch',
        'unique_multi_tb3_simulation_launch.py'
    )

    map_file = os.path.expanduser('~/maps/my_map.yaml')

    robot1_params = os.path.join(
        get_package_share_directory('multi_robot_system'),
        'config',
        'robot1_nav2.yaml'
    )

    robot2_params = os.path.join(
        get_package_share_directory('multi_robot_system'),
        'config',
        'robot2_nav2.yaml'
    )
    
    robot3_params = os.path.join(
    get_package_share_directory('multi_robot_system'),
    'config',
    'robot3_nav2.yaml'
   )
    
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'map': map_file,
                'robot1_params_file': robot1_params,
                'robot2_params_file': robot2_params,
                'robot3_params_file': robot3_params,
                'autostart': 'True',
                'use_rviz': 'True'
            }.items()
        )
    ])
