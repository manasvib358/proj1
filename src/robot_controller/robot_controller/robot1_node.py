import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Robot1(Node):

    def __init__(self):
        super().__init__('robot1')

        self.subscription = self.create_subscription(
            String,
            '/robot1/task',
            self.task_callback,
            10
        )

        self.status_pub = self.create_publisher(
            String,
            '/robot1/status',
            10
        )

        self.get_logger().info("Robot 1 Started")

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

    node = Robot1()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
