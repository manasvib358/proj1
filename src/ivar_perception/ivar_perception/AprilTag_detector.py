#!/usr/bin/env python3

# ROS2 imports
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_sensor_data

# Message imports
from sensor_msgs.msg import Image, CameraInfo
from apriltag_msgs.msg import AprilTagDetection, AprilTagDetectionArray, Point
from geometry_msgs.msg import TransformStamped 

# TF2 for broadcasting 3D transforms
from tf2_ros import TransformBroadcaster

# Image conversion (ROS image → OpenCV)
from cv_bridge import CvBridge

# AprilTag detection library
import apriltag
import numpy as np
import threading


class AprilTagNode(Node):
    """
    ROS2 Python node for detecting AprilTags from a camera feed.

    Subscribes to:
        /image_rect       (sensor_msgs/Image)       — raw camera frames
        /camera_info      (sensor_msgs/CameraInfo)  — camera calibration

    Publishes to:
        /detections       (apriltag_msgs/AprilTagDetectionArray) — detected tags

    Broadcasts:
        TF transforms for each detected tag (3D pose in camera frame)
    """

    def __init__(self):
        super().__init__('apriltag')

        # Tag family — e.g. '36h11', '25h9', '16h5'
        self.declare_parameter('family', 'tag36h11')

        # Default physical size of the tag in meters
        self.declare_parameter('size', 1.0)

        # Max number of corrected bits allowed (0 = strictest)
        self.declare_parameter('max_hamming', 0)

        # Print profiling info
        self.declare_parameter('profile', False)

        # Specific tag IDs to track (empty = track all)
        self.declare_parameter('tag.ids', [])

        # Custom frame names per tag ID
        self.declare_parameter('tag.frames', [])

        # Custom sizes per tag ID
        self.declare_parameter('tag.sizes', [])

        # Read parameter values
        self.tag_family    = self.get_parameter('family').value
        self.tag_edge_size = self.get_parameter('size').value
        self.max_hamming   = self.get_parameter('max_hamming').value
        self.profile       = self.get_parameter('profile').value

        tag_ids    = self.get_parameter('tag.ids').value
        tag_frames = self.get_parameter('tag.frames').value
        tag_sizes  = self.get_parameter('tag.sizes').value

        # Map tag ID → custom frame name
        # e.g. {0: 'obstacle_1', 1: 'obstacle_2'}
        self.tag_frames: dict[int, str] = {}
        if tag_ids and tag_frames:
            if len(tag_ids) != len(tag_frames):
                raise RuntimeError(
                    f"Mismatch: {len(tag_ids)} ids vs {len(tag_frames)} frames"
                )
            self.tag_frames = dict(zip(tag_ids, tag_frames))

        # Map tag ID → custom physical size
        self.tag_sizes: dict[int, float] = {}
        if tag_ids and tag_sizes:
            if len(tag_ids) != len(tag_sizes):
                raise RuntimeError(
                    f"Mismatch: {len(tag_ids)} ids vs {len(tag_sizes)} sizes"
                )
            self.tag_sizes = dict(zip(tag_ids, tag_sizes))

         # The actual detector object — does the heavy lifting
        self.detector = apriltag.apriltag(self.tag_family)
       
        # Thread lock — prevents detector being used simultaneously
        # from multiple threads (same as mutex in C++ version)
        self.mutex = threading.Lock()

        # OpenCV ↔ ROS image converter
        self.bridge = CvBridge()

        # Latest camera info (calibration data) — updated by camera_info callback
        self.camera_info = None

        # ── TF2 broadcaster ─────────────────────────────────────────────────
        # Publishes 3D position/orientation of each detected tag
        self.tf_broadcaster = TransformBroadcaster(self)

        # ── Publisher ────────────────────────────────────────────────────────
        # Publishes array of all detections in each frame
        self.pub_detections = self.create_publisher(
            AprilTagDetectionArray,
            'detections',
            10
        )

        # ── Subscribers ──────────────────────────────────────────────────────
        # Camera info — receives calibration data (focal length, principal point)
        self.sub_camera_info = self.create_subscription(
            CameraInfo,
            'camera_info',
            self.on_camera_info,
            qos_profile_sensor_data
        )

        # Camera image — receives raw frames, triggers detection pipeline
        self.sub_image = self.create_subscription(
            Image,
            'image_rect',
            self.on_camera,
            qos_profile_sensor_data
        )

        self.get_logger().info(
            f"AprilTag node started. Family: {self.tag_family}, "
            f"Default size: {self.tag_edge_size}m"
        )

    # ── Callbacks ────────────────────────────────────────────────────────────

    def on_camera_info(self, msg: CameraInfo):
        """
        Receives camera calibration data.
        Stores it so on_camera() can use it for pose estimation.

        P matrix contains:
            P[0]  = fx  (focal length x)
            P[5]  = fy  (focal length y)
            P[2]  = cx  (principal point x)
            P[6]  = cy  (principal point y)
        """
        self.camera_info = msg

    def on_camera(self, msg_img: Image):
        """
        Main detection pipeline — runs every time a camera frame arrives.

        Steps:
            1. Convert ROS Image → OpenCV grayscale
            2. Run AprilTag detector
            3. For each detection: extract ID, corners, pose
            4. Publish detections array 
            5. Broadcast TF transforms
        """
        # ── Step 1: Convert ROS image to OpenCV grayscale ───────────────────
        # 'mono8' = 8-bit grayscale — AprilTag detector requires this format
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg_img, desired_encoding='mono8')
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {e}")
            return

        # ── Step 2: Check camera calibration ────────────────────────────────
        calibrated = False
        intrinsics = None

        if self.camera_info is not None:
            P = self.camera_info.p  # projection matrix (3x4, stored as flat list)
            fx, fy = P[0], P[5]    # focal lengths
            cx, cy = P[2], P[6]    # principal point (image center)
            calibrated = (
                self.camera_info.width > 0 and
                self.camera_info.height > 0 and
                fx > 0 and fy > 0 and cx > 0 and cy > 0
            )
            if calibrated:
                # intrinsics needed for pose estimation: (fx, fy, cx, cy)
                intrinsics = (fx, fy, cx, cy)

        if not calibrated:
            self.get_logger().warn(
                "Camera not calibrated — pose estimation disabled.",
                throttle_duration_sec=5.0
            )

        # ── Step 3: Detect AprilTags ─────────────────────────────────────────
        with self.mutex:
            # detector.detect() returns a list of Detection objects
            detections = self.detector.detect(cv_image)

        # ── Step 4: Build detections message ─────────────────────────────────
        msg_detections = AprilTagDetectionArray()
        msg_detections.header = msg_img.header  # same timestamp as image

        transforms = []  # list of TF transforms to broadcast

        for det in detections:
            # Filter by hamming distance (corrected bit errors)
            # Higher hamming = less reliable detection
            if det['hamming'] > self.max_hamming:
                continue

            # Filter by tracked IDs (if specific IDs configured)
            if self.tag_frames and det['id'] not in self.tag_frames:
                continue

            self.get_logger().debug(
                f"Detected tag id={det['id']} hamming={det['hamming']} "
                f"margin={det['margin']:.3f}"
            )

            # Build the detection message for this tag
            msg_detection = AprilTagDetection()
            msg_detection.family  = self.tag_family         # e.g. '36h11'
            msg_detection.id      = det['id']               # unique tag ID
            msg_detection.hamming = det['hamming']          # corrected bit errors
            msg_detection.decision_margin = det['margin']   # confidence

            # Centre point of the tag in image pixels (x, y)
            msg_detection.centre.x = float(det['center'][0])
            msg_detection.centre.y = float(det['center'][1])

            # Four corner points of the tag in image pixels
            # corners shape: (4, 2) → [bottom-left, bottom-right, top-right, top-left]
            corners = det['lb-rb-rt-lt']   # numpy array (4,2)
            msg_detection.corners = [
                Point(x = float(corners[0][0]), y =float(corners[0][1])),  # left-bottom
                Point(x = float(corners[1][0]), y = float(corners[1][1])), # right-bottom
                Point(x = float(corners[2][0]), y = float(corners[2][1])), # right-top
                Point(x = float(corners[3][0]), y = float(corners[3][1])),  # left-top
            ]
            msg_detections.detections.append(msg_detection)

            # ── Step 5: Estimate 3D pose ──────────────────────────────────
            if calibrated and intrinsics is not None:
                tag_size = self.tag_sizes.get(det['id'],  self.tag_edge_size)
                transform = self.estimate_pose(
                    det, intrinsics, tag_size, msg_img.header
                )
                if transform is not None:
                    transforms.append(transform)

        # ── Step 6: Publish detections ────────────────────────────────────
        self.pub_detections.publish(msg_detections)

        # ── Step 7: Broadcast TF transforms ──────────────────────────────
        if transforms:
            self.tf_broadcaster.sendTransform(transforms)

    def estimate_pose(
        self,
        det,
        intrinsics: tuple,
        tag_size: float,
        header
    ) -> TransformStamped | None:
        """
        Estimates the 3D pose (position + orientation) of a detected tag.

        Uses PnP (Perspective-n-Point) algorithm:
            - Known: 3D tag corner positions (from tag_size)
            - Known: 2D corner positions in image (from detector)
            - Known: camera intrinsics (fx, fy, cx, cy)
            - Solve: rotation + translation of tag in camera frame

        Returns a TransformStamped message for TF broadcasting.
        """
        import cv2

        fx, fy, cx, cy = intrinsics

        # Camera matrix K — maps 3D points to 2D image points
        K = np.array([
            [fx,  0, cx],
            [ 0, fy, cy],
            [ 0,  0,  1]
        ], dtype=np.float64)

        # No distortion (using rectified image)
        dist_coeffs = np.zeros((4, 1))

        # 3D positions of tag corners in tag's own coordinate frame
        # Tag is centered at origin, lies in XY plane
        half = tag_size / 2.0
        obj_points = np.array([
            [-half,  half, 0],  # left-bottom
            [ half,  half, 0],  # right-bottom
            [ half, -half, 0],  # right-top
            [-half, -half, 0],  # left-top
        ], dtype=np.float64)

        # 2D corner positions detected in the image
        img_points = det['lb-rb-rt-lt'].astype(np.float64)

        # Solve PnP — find rotation and translation
        success, rvec, tvec = cv2.solvePnP(
            obj_points, img_points, K, dist_coeffs
        )

        if not success:
            return None

        # Convert rotation vector → rotation matrix → quaternion
        R, Jcob = cv2.Rodrigues(rvec)
        quat = self.rotation_matrix_to_quaternion(R)

        # Build TF transform message
        tf_msg = TransformStamped()
        tf_msg.header = header

        # Frame name: use custom name if configured, else 'family:id'
        if det['id'] in self.tag_frames:
            tf_msg.child_frame_id = self.tag_frames[det['id']]
        else:
            tf_msg.child_frame_id = f"{self.tag_family}:{det['id']}"

        # Translation (position of tag in camera frame)
        tf_msg.transform.translation.x = float(tvec[0])
        tf_msg.transform.translation.y = float(tvec[1])
        tf_msg.transform.translation.z = float(tvec[2])

        # Rotation (orientation of tag in camera frame)
        tf_msg.transform.rotation.x = quat[0]
        tf_msg.transform.rotation.y = quat[1]
        tf_msg.transform.rotation.z = quat[2]
        tf_msg.transform.rotation.w = quat[3]

        return tf_msg

    def rotation_matrix_to_quaternion(self, R: np.ndarray) -> tuple:
        """
        Converts a 3x3 rotation matrix to a quaternion (x, y, z, w).
        Uses Shepperd's method for numerical stability.
        """
        trace = R[0, 0] + R[1, 1] + R[2, 2]

        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (R[2, 1] - R[1, 2]) * s
            y = (R[0, 2] - R[2, 0]) * s
            z = (R[1, 0] - R[0, 1]) * s
        elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
            s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
            w = (R[2, 1] - R[1, 2]) / s
            x = 0.25 * s
            y = (R[0, 1] + R[1, 0]) / s
            z = (R[0, 2] + R[2, 0]) / s
        elif R[1, 1] > R[2, 2]:
            s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
            w = (R[0, 2] - R[2, 0]) / s
            x = (R[0, 1] + R[1, 0]) / s
            y = 0.25 * s
            z = (R[1, 2] + R[2, 1]) / s
        else:
            s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
            w = (R[1, 0] - R[0, 1]) / s
            x = (R[0, 2] + R[2, 0]) / s
            y = (R[1, 2] + R[2, 1]) / s
            z = 0.25 * s

        return (x, y, z, w)


# ── Entry point ───────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = AprilTagNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()