#!/usr/bin/env python3

# ── ROS2 imports ─────────────────────────────────────────────────────────────
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

# ── Message imports ───────────────────────────────────────────────────────────
from apriltag_msgs.msg import AprilTagDetectionArray
from geometry_msgs.msg import PoseArray, Pose, Point, Quaternion
from std_msgs.msg import String

# ── TF2 imports ───────────────────────────────────────────────────────────────
from tf2_ros import Buffer, TransformListener, LookupException, \
                    ConnectivityException, ExtrapolationException
from tf2_geometry_msgs import do_transform_pose

import json


class PoseTransformerNode(Node):
    """
    Converts AprilTag detections from camera frame → map frame.

    Subscribes to:
        /detections     (AprilTagDetectionArray) ← from apriltag_node

    Publishes to:
        /tag_poses_map  (std_msgs/String JSON)   ← map frame poses
                                                    for shared_database

    Why JSON string?
        Avoids custom message definitions during early development.
        Same pattern already used in shared_map_node.py
    """

    def __init__(self):
        super().__init__('pose_transformer')

        # ── Parameters ────────────────────────────────────────────────────────
        # Camera frame name — must match URDF link name exactly
        # Default: 'camera_link' (confirmed from URDF)
        self.declare_parameter('camera_frame', 'camera_link')

        # Map frame name — the global fixed frame in ROS2 navigation
        self.declare_parameter('map_frame', 'map')

        # Robot namespace — for multi-robot deployments
        # e.g. 'robot1', 'robot2', 'robot3'
        self.declare_parameter('robot_id', 'aqua_robot_1')

        self.camera_frame = self.get_parameter('camera_frame').value
        self.map_frame    = self.get_parameter('map_frame').value
        self.robot_id     = self.get_parameter('robot_id').value

        # ── TF2 Setup ─────────────────────────────────────────────────────────
        # Buffer stores transform history (last 10 seconds by default)
        # Why history? Because image timestamps may be slightly in the past
        # and we need the transform at THAT exact moment, not right now
        self.tf_buffer = Buffer()

        # Listener continuously receives transforms from /tf and /tf_static
        # and stores them in the buffer
        # Why separate listener? It runs in background so buffer stays fresh
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # ── Publisher ─────────────────────────────────────────────────────────
        # Publishes map-frame tag poses as JSON string
        # shared_map_node subscribes to this topic
        self.pub_tag_poses = self.create_publisher(
            String,
            'tag_poses_map',
            10
        )

        # ── Subscriber ────────────────────────────────────────────────────────
        # Receives detections from apriltag_node
        self.sub_detections = self.create_subscription(
            AprilTagDetectionArray,
            'detections',
            self.on_detections,
            qos_profile_sensor_data
        )

        self.get_logger().info(
            f"PoseTransformer started. "
            f"Converting {self.camera_frame} → {self.map_frame} "
            f"for {self.robot_id}"
        )

    # ── Main Callback ─────────────────────────────────────────────────────────

    def on_detections(self, msg: AprilTagDetectionArray):
        """
        Runs every time apriltag_node publishes a new detection array.

        For each detected tag:
            1. Build a Pose in camera frame using TF data
            2. Ask TF2 for camera → map transform at detection timestamp
            3. Apply transform to get map frame pose
            4. Publish as JSON for shared_map_node
        """

        # If no detections in this frame, nothing to do
        if not msg.detections:
            return

        # Timestamp of the image — we need transform at THIS moment
        # not at current time, because robot may have moved since image
        stamp = msg.header.stamp

        # Try to get the transform from camera frame to map frame
        # at the exact timestamp of the image
        try:
            # lookup_transform(target, source, time)
            # "give me the transform that converts points FROM camera_frame TO map_frame"
            # rclpy.time.Time() means "latest available" — safe when testing without Gazebo
            transform = self.tf_buffer.lookup_transform(
                self.map_frame,     # target — where we want poses expressed
                self.camera_frame,  # source  — where poses currently are
                rclpy.time.Time()   # use latest available transform
            )

        except LookupException:
            # TF2 doesn't know about these frames yet
            # This happens at startup before robot is spawned
            self.get_logger().warn(
                f"TF frame '{self.camera_frame}' or '{self.map_frame}' "
                f"not found yet. Is robot spawned in Gazebo?",
                throttle_duration_sec=5.0
            )
            return

        except ConnectivityException:
            # No chain of transforms connecting camera_frame to map
            # e.g. missing base_link → camera_link transform in URDF
            self.get_logger().warn(
                f"No TF connection between '{self.camera_frame}' "
                f"and '{self.map_frame}'. Check your URDF.",
                throttle_duration_sec=5.0
            )
            return

        except ExtrapolationException:
            # Requested timestamp is outside the buffer's history
            # Common when using exact image timestamps
            self.get_logger().warn(
                "TF transform timestamp out of range.",
                throttle_duration_sec=5.0
            )
            return

        # ── Process each detection ────────────────────────────────────────────
        results = []

        for det in msg.detections:

            # Each detection has a TF transform already broadcast by apriltag_node
            # We need to look that up and convert it to map frame
            tag_frame = f"{det.family}:{det.id}"  # e.g. "36h11:3"

            try:
                # Get transform from tag frame to map frame
                # This chains: tag → camera → base_link → odom → map
                tag_to_map = self.tf_buffer.lookup_transform(
                    self.map_frame,  # target
                    tag_frame,       # source (tag's own frame)
                    rclpy.time.Time()
                )

            except (LookupException, ConnectivityException, ExtrapolationException) as e:
                self.get_logger().warn(
                    f"Could not transform tag {det.id} to map frame: {e}",
                    throttle_duration_sec=3.0
                )
                continue

            # Extract position from transform
            # Translation = where the tag origin is in map frame
            x = tag_to_map.transform.translation.x
            y = tag_to_map.transform.translation.y
            z = tag_to_map.transform.translation.z

            # Build result dict for this tag
            # This is what shared_map_node will receive and store
            tag_data = {
                'robot_id': self.robot_id,   # which robot saw this tag
                'tag_id':   det.id,           # unique tag identifier
                'x':        x,                # map frame X position
                'y':        y,                # map frame Y position
                'z':        z,                # map frame Z (0 for water surface)
                'confidence': det.decision_margin  # detection quality score
            }

            results.append(tag_data)

            self.get_logger().info(
                f"Tag {det.id} at map position "
                f"({x:.2f}, {y:.2f}, {z:.2f})"
            )

        # ── Publish results ───────────────────────────────────────────────────
        if results:
            msg_out = String()
            msg_out.data = json.dumps(results)
            self.pub_tag_poses.publish(msg_out)


# ── Entry point ───────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = PoseTransformerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()