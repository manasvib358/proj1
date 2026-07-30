from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    model = os.path.join(
        get_package_share_directory('waste_detection_robot'),
        'models',
        'wastebot_cam',
        'model.sdf'
    )

    return LaunchDescription([

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'wastebot',
                '-file', model,
                '-x', '0',
                '-y', '0',
                '-z', '0.01'
            ],
            output='screen'
        )

    ])
