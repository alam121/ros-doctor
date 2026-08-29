from rclpy.qos import QoSProfile, ReliabilityPolicy

battery_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
node.create_subscription(BatteryState, "/battery_state", cb, battery_qos)
