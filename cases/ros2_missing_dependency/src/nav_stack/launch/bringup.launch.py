from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="depthimage_to_laserscan",
            executable="depthimage_to_laserscan_node",
            name="scan_converter",
        )
    ])
