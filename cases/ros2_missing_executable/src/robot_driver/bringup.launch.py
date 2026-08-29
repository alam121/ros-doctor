from launch_ros.actions import Node

driver = Node(package="robot_driver", executable="serial_driver_node")
