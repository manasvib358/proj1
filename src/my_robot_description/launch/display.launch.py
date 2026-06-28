import xacro
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    robot_desc = xacro.process_file(
    '/home/manasvi3/ros2_ws/src/my_robot_description/urdf/my_robot.urdf.xacro'
).toxml()
    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{
                'robot_description': robot_desc
            }]
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2'
        )

    ])
