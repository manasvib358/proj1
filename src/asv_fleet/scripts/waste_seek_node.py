#!/usr/bin/env python3
"""
waste_seek_node.py

The simplest possible "detect waste, drive towards it" behaviour:
  - If an AprilTag (waste marker) is visible in the camera, steer
    towards it using a basic proportional controller on its
    horizontal pixel offset from the image center.
  - If nothing is visible, rotate slowly in place to search the lake.

This is deliberately bare-bones (no obstacle avoidance, no path
planning, chases whatever tag it sees first) so you can read every
line and understand exactly what it's doing before replacing it with
something smarter (state machine, lidar-based avoidance, multi-robot
task allocation, etc).

Run for one robot:
    ros2 run asv_fleet waste_seek_node.py --ros-args -p robot_name:=red_asv

Or launch all three via launch/fleet_autonomy.launch.py.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from apriltag_msgs.msg import AprilTagDetectionArray

IMAGE_WIDTH_PX = 640.0  # must match the camera <width> in asv_macro.xacro


class WasteSeekNode(Node):

    def __init__(self):
        super().__init__('waste_seek_node')

        self.declare_parameter('robot_name', 'red_asv')
        self.declare_parameter('cruise_speed', 0.3)     # m/s forward when chasing a tag
        self.declare_parameter('search_turn_speed', 0.4)  # rad/s when searching
        self.declare_parameter('steer_gain', 1.0)        # proportional gain on pixel error

        self.robot_name = self.get_parameter('robot_name').value
        self.cruise_speed = self.get_parameter('cruise_speed').value
        self.search_turn_speed = self.get_parameter('search_turn_speed').value
        self.steer_gain = self.get_parameter('steer_gain').value

        self.cmd_pub = self.create_publisher(Twist, f'/{self.robot_name}/cmd_vel', 10)
        self.tag_sub = self.create_subscription(
            AprilTagDetectionArray,
            f'/{self.robot_name}/tag_detections',
            self.tag_callback,
            10
        )

        # If we haven't seen a tag in a while, fall back to a slow search spin.
        self.search_timer = self.create_timer(0.5, self.search_if_idle)
        self.last_seen = self.get_clock().now()
        self.seeing_tag = False

        self.get_logger().info(f'{self.robot_name}: waste_seek_node started')

    def tag_callback(self, msg: AprilTagDetectionArray):
        if not msg.detections:
            self.seeing_tag = False
            return

        # Chase whichever tag the detector lists first. Good enough for
        # a single-target demo; for multiple simultaneous waste items
        # you'd add logic here to pick the closest/highest-priority one.
        tag = msg.detections[0]
        cx = tag.centre.x
        image_center_x = IMAGE_WIDTH_PX / 2.0

        # error: +1.0 = tag is far left, -1.0 = tag is far right, 0 = centered
        error = (image_center_x - cx) / image_center_x

        cmd = Twist()
        cmd.linear.x = self.cruise_speed
        cmd.angular.z = self.steer_gain * error
        self.cmd_pub.publish(cmd)

        self.seeing_tag = True
        self.last_seen = self.get_clock().now()

    def search_if_idle(self):
        if self.seeing_tag:
            return
        idle_seconds = (self.get_clock().now() - self.last_seen).nanoseconds / 1e9
        if idle_seconds > 1.0:
            cmd = Twist()
            cmd.angular.z = self.search_turn_speed
            self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = WasteSeekNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
