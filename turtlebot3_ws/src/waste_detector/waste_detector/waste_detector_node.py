#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2
from ultralytics import YOLO


class WasteDetectorNode(Node):

    def __init__(self):
        super().__init__("waste_detector_node")

        self.bridge = CvBridge()

        self.get_logger().info("Loading YOLOv8 model...")
        self.model = YOLO("yolov8n.pt")
        self.get_logger().info("YOLO model loaded successfully.")

        self.subscription = self.create_subscription(
            Image,
            "/robot1/camera/image_raw",
            self.image_callback,
            10
        )

        self.publisher = self.create_publisher(
            String,
            "/robot1/waste_detections",
            10
        )

        self.waste_classes = [
            "bottle",
            "cup",
            "can",
            "backpack"
        ]

        self.get_logger().info("Waste Detector Node Started")

    def image_callback(self, msg):

        print("Image callback received")

        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding="bgr8"
        )
        
        print("Frame shape:", frame.shape)
        print("Frame dtype:", frame.dtype)
        print("Pixel [0,0]:", frame[0,0])
        cv2.imwrite("/tmp/robot1_camera.jpg", frame)

        results = self.model(frame, verbose=True)

        detected_objects = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                class_name = self.model.names[class_id]

                print(f"Detected: {class_name} ({confidence:.2f})")

                if class_name in self.waste_classes:

                    x1, y1, x2, y2 = box.xyxy[0]

                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    detection = (
                        f"{class_name},"
                        f"{center_x},"
                        f"{center_y}"
                    )

                    detected_objects.append(detection)

        if detected_objects:

            detection_msg = String()
            detection_msg.data = ";".join(detected_objects)

            self.publisher.publish(detection_msg)

            print("Published:", detection_msg.data)

        annotated_frame = results[0].plot()

        cv2.imshow("Waste Detection", annotated_frame)
        cv2.waitKey(1)


def main(args=None):

    rclpy.init(args=args)

    node = WasteDetectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
