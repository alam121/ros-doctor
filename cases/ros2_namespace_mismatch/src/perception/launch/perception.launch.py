from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="perception",
            executable="camera_filter",
            namespace="robot1",
            remappings=[("image_raw", "/camera/image_raw")],
        )
    ])
