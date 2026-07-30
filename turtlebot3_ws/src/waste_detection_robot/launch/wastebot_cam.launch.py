from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"),
                "launch",
                "gazebo.launch.py",
            )
        ),
        launch_arguments={
            "world": os.path.join(
                get_package_share_directory("turtlebot3_gazebo"),
                "worlds",
                "turtlebot3_world.world",
            )
        }.items(),
    )

    model = os.path.join(
        get_package_share_directory("waste_detection_robot"),
        "models",
        "wastebot_cam",
        "model.sdf",
    )

    spawn = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "wastebot",
            "-file", model,
            "-x", "-2.0",
            "-y", "-0.5",
            "-z", "0.01",
        ],
        output="screen",
    )

    return LaunchDescription([
        gazebo_launch,
        spawn,
    ])
