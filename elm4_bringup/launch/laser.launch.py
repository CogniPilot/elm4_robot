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
    DeclareLaunchArgument('stl27l', default_value='true',
                          choices=['true', 'false'],
                          description='Run STL27L.'),
    DeclareLaunchArgument('rf2o', default_value='true',
                          choices=['true', 'false'],
                          description='Run rf2o laser odometry'),
    DeclareLaunchArgument('stl27l_tf', default_value='true',
                          choices=['true', 'false'],
                          description='Run STL27L TF.'),
    DeclareLaunchArgument('rf2o_tf', default_value='true',
                          choices=['true', 'false'],
                          description='Run rf2o laser odometry TF'),
    DeclareLaunchArgument('use_sim_time', default_value='false',
                          choices=['true', 'false'],
                          description='use_sim_time')
]


def generate_launch_description():

    stl27l_node = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='STL27L',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_STL27L'},
            {'topic_name': 'scan'},
            {'frame_id': 'elm4/base_laser'},
            {'port_name': '/dev/ttymxc2'},
            {'port_baudrate': 921600},
            {'laser_scan_dir': False},
            {'enable_angle_crop_func': False},
            {'angle_crop_min': 0.0},
            {'angle_crop_max': 0.0}],
        condition=IfCondition(LaunchConfiguration("stl27l"))
    )

    rf2o_odom_node = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        name='rf2o_laser_odometry',
        output='screen',
        parameters=[{
            'laser_scan_topic' : '/scan',
            'odom_topic' : '/odom_rf2o',
            'publish_tf' : LaunchConfiguration('rf2o_tf'),
            'base_frame_id' : 'baselink',
            'odom_frame_id' : 'odom',
            'init_pose_from_topic' : '',
            'freq' : 20.0,
            'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration("rf2o"))
    )

    stl27l_tf_node = Node(
        name='base_link_to_base_laser_stl27l',
        package='tf2_ros',
        executable='static_transform_publisher',
        output='screen',
        arguments=[
            '--x', '0.0', '--y', '0.0', '--z', '0.0',
            '--roll', '0.0', '--pitch', '0.0', '--yaw', '0.0',
            '--frame-id', 'elm4/base_laser', '--child-frame-id', 'baselink'],
        condition=IfCondition(LaunchConfiguration("stl27l_tf"))
    )


    # Define LaunchDescription variable
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(stl27l_node)
    ld.add_action(rf2o_odom_node)
    ld.add_action(stl27l_tf_node)
    return ld

