import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchContext, LaunchDescription, SomeSubstitutionsType, Substitution
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('sync', default_value='true',
                          choices=['true', 'false'],
                          description='Run async or sync SLAM'),
    DeclareLaunchArgument('localization', default_value='slam',
                          choices=['off', 'localization', 'slam'],
                          description='Whether to run localization or SLAM'),
    DeclareLaunchArgument('nav2', default_value='true',
                          choices=['true', 'false'],
                          description='Run nav2'),
    DeclareLaunchArgument('corti', default_value='false',
                          choices=['true', 'false'],
                          description='Run corti'),
    DeclareLaunchArgument('can', default_value='true',
                          choices=['true', 'false'],
                          description='Run CAN'),
    DeclareLaunchArgument('laser', default_value='true',
                          choices=['true', 'false'],
                          description='Run laser'),
    DeclareLaunchArgument('synapse', default_value='true',
                          choices=['true', 'false'],
                          description='Run synapse_ros'),
    DeclareLaunchArgument('use_sim_time', default_value='false',
                          choices=['true', 'false'],
                          description='use_sim_time'),
    DeclareLaunchArgument('model', default_value='lidar',
                          choices=['base', 'lidar'],
                          description='El Mandadero Model'),
    DeclareLaunchArgument('robot_name', default_value='elm4',
                          description='Robot name')
]


def generate_launch_description():

    # Directories
    pkg_elm4_bringup = get_package_share_directory(
        'elm4_bringup')
    pkg_elm4_description = get_package_share_directory(
        'elm4_description')
    pkg_elm4_nav2 = get_package_share_directory(
        'elm4_nav2')
    pkg_synapse_ros = get_package_share_directory(
        'synapse_ros')
    pkg_corti = get_package_share_directory('corti')

    # Paths
    nav2_launch = PathJoinSubstitution(
        [pkg_elm4_nav2, 'launch', 'nav2.launch.py'])
    corti_launch = PathJoinSubstitution(
        [pkg_corti, 'launch', 'corti.launch.py'])
    slam_launch = PathJoinSubstitution(
        [pkg_elm4_nav2, 'launch', 'slam.launch.py'])
    localization_launch = PathJoinSubstitution(
        [pkg_elm4_nav2, 'launch', 'localization.launch.py'])
    robot_description_launch = PathJoinSubstitution(
        [pkg_elm4_description, 'launch', 'robot_description.launch.py'])
    laser_launch = PathJoinSubstitution(
        [pkg_elm4_bringup, 'launch', 'laser.launch.py'])
    can_launch = PathJoinSubstitution(
        [pkg_elm4_bringup, 'launch', 'can.launch.py'])
    synapse_ros_launch = PathJoinSubstitution(
        [pkg_synapse_ros, 'launch', 'synapse_ros.launch.py'])

    # Parameters
    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=PathJoinSubstitution(
            [pkg_elm4_nav2, 'maps', 'depot.yaml']),
        description='Full path to map yaml file to load')

    # leds
    can = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([can_launch]),
        condition=IfCondition(LaunchConfiguration('can')),
        launch_arguments=[
            ('vesc', True),
            ('led', True)
        ]
    )

    # laser
    laser = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([laser_launch]),
        condition=IfCondition(LaunchConfiguration('laser')),
        launch_arguments=[
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('stl27l', True),
            ('stl27l_tf', True),
            ('rf2o', True),
            ('rf2o_tf', True)
        ]
    )

    # Synapse ROS
    synapse_ros = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([synapse_ros_launch]),
        condition=IfCondition(LaunchConfiguration('synapse')),
        launch_arguments=[
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('host', 192.0.2.2),
            ('port', 4242)
        ]
    )

    # Robot description
    robot_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([robot_description_launch]),
        launch_arguments=[('model', LaunchConfiguration('model')),
                          ('use_sim_time', LaunchConfiguration('use_sim_time'))]
    )

    # NAV2
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([nav2_launch]),
        condition=IfCondition(LaunchConfiguration('nav2')),
        launch_arguments=[
            ('use_sim_time', LaunchConfiguration('use_sim_time'))
        ]
    )

    # Corti
    corti = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([corti_launch]),
        condition=IfCondition(LaunchConfiguration('corti')),
        launch_arguments=[
            ('use_sim_time', LaunchConfiguration('use_sim_time'))
        ]
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([slam_launch]),
        condition=LaunchConfigurationEquals('localization', 'slam'),
        launch_arguments=[
            ('sync', LaunchConfiguration('sync')),
            ('use_sim_time', LaunchConfiguration('use_sim_time'))
        ]
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([localization_launch]),
        condition=LaunchConfigurationEquals('localization', 'localization'),
        launch_arguments=[
            ('map', LaunchConfiguration('map')),
            ('use_sim_time', LaunchConfiguration('use_sim_time'))
        ]
    )

    # Define LaunchDescription variable
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(laser)
    ld.add_action(robot_description)
    ld.add_action(leds_can)
    ld.add_action(vesc_can_control)
    ld.add_action(synapse_ros)
    ld.add_action(nav2)
    ld.add_action(corti)
    ld.add_action(slam)
    ld.add_action(localization)
    return ld

