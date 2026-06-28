import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Robot3(Node):

    def __init__(self):
        super().__init__('robot3')

        self.subscription = self.create_subscription(
            String,
            '/robot3/task',
            self.task_callback,
            10
        )

        self.status_pub = self.create_publisher(
            String,
            '/robot3/status',
            10
        )

        self.get_logger().info("Robot 3 Started")

    def task_callback(self, msg):

        task = msg.data

        self.get_logger().info(f"Received task: {task}")

        self.get_logger().info("Moving to marker...")

        time.sleep(5)

        self.get_logger().info("Task Completed")

        status = String()
        status.data = "free"

        self.status_pub.publish(status)

        self.get_logger().info("Published FREE status")


def main(args=None):

    rclpy.init(args=args)

    node = Robot3()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
