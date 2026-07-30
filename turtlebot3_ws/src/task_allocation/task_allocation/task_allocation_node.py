#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry


class TaskAllocationNode(Node):

    def __init__(self):
        super().__init__('task_allocation_node')

        self.get_logger().info("Task Allocation Node Started")

        self.robot_positions = {}

        self.create_subscription(
            Odometry,
            '/robot1/odom',
            self.robot1_callback,
            10)

        self.create_subscription(
            Odometry,
            '/robot2/odom',
            self.robot2_callback,
            10)

        self.create_subscription(
            Odometry,
            '/robot3/odom',
            self.robot3_callback,
            10)

        self.create_timer(2.0, self.print_positions)

    def robot1_callback(self, msg):
        self.robot_positions["robot1"] = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        )

    def robot2_callback(self, msg):
        self.robot_positions["robot2"] = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        )

    def robot3_callback(self, msg):
        self.robot_positions["robot3"] = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        )

    def print_positions(self):

        self.get_logger().info("----- Robot Positions -----")

        for robot, position in self.robot_positions.items():

            self.get_logger().info(
                f"{robot}: x={position[0]:.2f}, y={position[1]:.2f}"
            )


def main(args=None):

    rclpy.init(args=args)

    node = TaskAllocationNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
    
