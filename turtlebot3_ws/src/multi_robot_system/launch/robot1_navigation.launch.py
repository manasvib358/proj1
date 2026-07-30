#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import PushRosNamespace


def generate_launch_description():

    map_file = os.path.expanduser('~/maps/my_map.yaml')

    params_file = os.path.join(
        get_package_share_directory('multi_robot_system'),
        'config',
        'robot1_nav2.yaml'
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            )
        ),
        launch_arguments={  
    'namespace': 'robot1',
    'use_sim_time': 'True',
    'map': map_file,
    'params_file': params_file
      }.items()
    )

    return LaunchDescription([
        PushRosNamespace('robot1'),
        nav2
    ])
