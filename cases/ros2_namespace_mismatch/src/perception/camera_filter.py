import rclpy


def create_filter_node(node):
    node.create_subscription(Image, "/camera/image_raw", handle_image, 10)
