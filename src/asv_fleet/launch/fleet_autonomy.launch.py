"""
Starts waste_seek_node for all three robots.

Run AFTER spawn_fleet.launch.py and apriltag_detection.launch.py are
both up:
    ros2 launch asv_fleet fleet_autonomy.launch.py
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def make_seeker(name):
    return Node(
        package='asv_fleet',
        executable='waste_seek_node.py',
        name='waste_seek_node',
        namespace=name,
        parameters=[{'robot_name': name}],
        output='screen'
    )


def generate_launch_description():
    return LaunchDescription([
        make_seeker('red_asv'),
        make_seeker('green_asv'),
        make_seeker('blue_asv'),
    ])
