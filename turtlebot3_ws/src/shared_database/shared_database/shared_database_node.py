#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SharedDatabaseNode(Node):
    def __init__(self):
        super().__init__('shared_database_node')

        self.database = {}

        self.subscription = self.create_subscription(
            String,
            'task_updates',
            self.task_callback,
            10
        )

        self.get_logger().info('Shared Database Node Started')

    def task_callback(self, msg):
        robot, task = msg.data.split(":", 1)
        self.database[robot] = task

        self.get_logger().info(f"Stored: {robot} -> {task}")


def main(args=None):
    rclpy.init(args=args)

    node = SharedDatabaseNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
