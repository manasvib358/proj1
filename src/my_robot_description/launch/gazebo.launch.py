from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import xacro

def generate_launch_description():

    robot_description = xacro.process_file(
        '/home/manasvi3/ros2_ws/src/my_robot_description/urdf/my_robot.urdf.xacro'
    ).toxml()

    return LaunchDescription([

        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description
            }]
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'water_robot',
                '-topic', 'robot_description'
            ],
            output='screen'
        )
    ])
