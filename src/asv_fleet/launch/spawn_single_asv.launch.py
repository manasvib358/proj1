"""
Spawns ONE ASV (red) into the lake world.

Use this first, before spawn_fleet.launch.py, to sanity-check that
Gazebo, the xacro, the spawn, and the sensor plugins all actually
work -- it's much easier to debug one robot than three at once.

Run:
    ros2 launch asv_fleet spawn_single_asv.launch.py
"""
import os
from launch import LaunchDescription
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('asv_fleet')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    world_path = os.path.join(pkg_share, 'worlds', 'lake_world.world')
    xacro_path = os.path.join(pkg_share, 'urdf', 'asv_robot.xacro')

    robot_name = 'red_asv'

    # Running xacro at launch time (via Command substitution) means the
    # URDF is generated fresh every launch -- no stale pre-built URDF
    # files to forget to regenerate after you edit the xacro.
    robot_description = Command([
        'xacro ', xacro_path,
        ' robot_name:=', robot_name,
        ' color_r:=1.0 color_g:=0.0 color_b:=0.0'
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=robot_name,
        output='screen',
        parameters=[{
    'robot_description': ParameterValue(
        robot_description,
        value_type=str
    ),
    'use_sim_time': True
}]
    )

    # spawn_entity.py reads the URDF from the /robot_description topic
    # that robot_state_publisher just published (under this robot's
    # namespace) and asks Gazebo to instantiate it as a real entity --
    # this is the actual "spawn", as opposed to baking the model
    # statically into the world file.
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', f'/{robot_name}/robot_description',
            '-entity', robot_name,
            '-x', '0', '-y', '0', '-z', '0.1'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])
