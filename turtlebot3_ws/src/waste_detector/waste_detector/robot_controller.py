#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist


class RobotController(Node):

    def __init__(self):
        super().__init__("robot1_controller")

        self.subscription = self.create_subscription(
            String,
            "/robot1/waste_detections",
            self.detection_callback,
            10
        )

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            "/robot1/cmd_vel",
            10
        )

        self.get_logger().info("Robot 1 Controller Started")


    def detection_callback(self, msg):

        self.get_logger().info(f"Received detection: {msg.data}")

        cmd = Twist()

        cmd.linear.x = 0.1
        cmd.angular.z = 0.0

        self.cmd_vel_publisher.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = RobotController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
