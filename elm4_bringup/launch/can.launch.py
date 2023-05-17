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
    DeclareLaunchArgument('leds', default_value='true',
                          choices=['true', 'false'],
                          description='Run LEDs.'),
    DeclareLaunchArgument('vesc', default_value='true',
                          choices=['true', 'false'],
                          description='Run VESC can control')
    DeclareLaunchArgument('joy_test', default_value='true',
                          choices=['true', 'false'],
                          description='Run Joy actuator test.')
]


def generate_launch_description():

    opencyphal_led_node = Node(
        package='opencyphal_led',
        executable='opencyphal_led_node',
        name='opencyphal_led_node_0',
        output='screen',
        parameters=[
            {"led_brightness": 5},
            {"led_image_topic": "/led_image"},
            {"joy_topic": "/joy"},
            {"cyphal_topic": "/CyphalTransmitFrame"},
            {"max_leds": 12}],
        condition=IfCondition(LaunchConfiguration("leds"))
    )

    opencyphal_send_node = Node(
        package='opencyphal_send',
        executable='opencyphal_send_node',
        name='opencyphal_send_0',
        output='screen',
        parameters=[
            {"cyphal_input_topic": "/CyphalTransmitFrame"},
            {"can_channel": "can1"}],
        condition=IfCondition(LaunchConfiguration("leds"))
    )

    vesc_can_control_node = Node(
        package='vesc_can_control',
        executable='vesc_can_control_node',
        name='vesc_can_control_node0',
        output='screen',
        parameters=[
            {"actuators_input_topic": "/actuators"},
            {"can_output_topic": "/can0_send"},
            {"number_vesc": 4},
            {"actuators_index_can": [0, 1, 2, 3]},
            {"actuators_pole_pair": [15, 15, 15, 15]},
            {"can_node_id_actuators": [119, 85, 73, 23]}],
        condition=IfCondition(LaunchConfiguration("vesc"))
    )

    can_send_node = Node(
        package='can_send',
        executable='can_send_node',
        name='can_send_node0',
        output='screen',
        parameters=[
            {"can_channel": "can0"},
            {"can_input_topic": "/can0_send"}],
        condition=IfCondition(LaunchConfiguration("vesc"))
    )
    
    joy_test_mixer_actuators_node = Node(
        package='joy_test_mixer_actuators',
        executable='joy_test_mixer_actuators_node',
        name='joy_test_mixer_actuators_node0',
        output='screen',
        parameters=[
            {"joy_scale": 100},
            {"joy_input_topic": "/joy"},
            {"actuators_output_topic": "/actuators"},
            {"thrust_axes": 1},
            {"yaw_axes": 3},
            {"arm_button": 7},
            {"disarm_button": 6},
            {"mix_thrust": [1.0, 1.0, 1.0, 1.0]},
            {"mix_yaw": [-1.0, 1.0, 1.0, -1.0]}],
            condition=IfCondition(LaunchConfiguration("vesc"))
    )

    # Define LaunchDescription variable
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(opencyphal_led_node)
    ld.add_action(opencyphal_send_node)
    ld.add_action(vesc_can_control_node)
    ld.add_action(can_send_node)
    ld.add_action(joy_test_mixer_actuators_node)
    return ld

