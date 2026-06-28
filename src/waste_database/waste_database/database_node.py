import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class DatabaseNode(Node):

    def __init__(self):
        super().__init__('database_node')

        self.database = {}

        self.subscription = self.create_subscription(
            String,
            '/waste_detection',
            self.waste_callback,
            10
        )

        self.create_timer(5.0, self.show_database)

        self.get_logger().info("Database node started")

    def waste_callback(self, msg):

        marker_id = msg.data

        if marker_id not in self.database:
            self.database[marker_id] = {
                "status" : "unassigned"
            }

            self.get_logger().info(
                f"Stored {marker_id}"
            )

        else:
            self.get_logger().info(
                f"{marker_id} already exists"
            )

    def show_database(self):

        self.get_logger().info(
            f"Database = {self.database}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = DatabaseNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
