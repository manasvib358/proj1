import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class TaskAllocator(Node):

    def __init__(self):
        super().__init__('task_allocator')

        
        self.queue = []

        
        self.robot_status = {
            "robot1": "free",
            "robot2": "free",
            "robot3": "free"
        }

        
        self.create_subscription(
            String,
            '/waste_detection',
            self.waste_callback,
            10
        )

        
        self.create_subscription(
            String,
            '/robot1/status',
            self.robot1_status_callback,
            10
        )

        self.create_subscription(
            String,
            '/robot2/status',
            self.robot2_status_callback,
            10
        )

        self.create_subscription(
            String,
            '/robot3/status',
            self.robot3_status_callback,
            10
        )

        
        self.robot1_task_pub = self.create_publisher(
            String,
            '/robot1/task',
            self.robot1_status_callback,
            10
        )

        self.robot2_task_pub = self.create_publisher(
            String,
            '/robot2/task',
            self.robot2_status_callback,
            10
        )

        self.robot3_task_pub = self.create_publisher(
            String,
            '/robot3/task',
            self.robot3_status_callback,
            10
        )

        self.get_logger().info("Task Allocator Started")

    

    def assign_task(self, robot, task):

        msg = String()
        msg.data = task

        if robot == "robot1":
            self.robot1_task_pub.publish(msg)

        elif robot == "robot2":
            self.robot2_task_pub.publish(msg)

        elif robot == "robot3":
            self.robot3_task_pub.publish(msg)

        self.robot_status[robot] = "busy"

        self.get_logger().info(f"{task} assigned to {robot}")

    

    def waste_callback(self, msg):

        task = msg.data

        if self.robot_status["robot1"] == "free":
            self.assign_task("robot1", task)

        elif self.robot_status["robot2"] == "free":
            self.assign_task("robot2", task)

        elif self.robot_status["robot3"] == "free":
            self.assign_task("robot3", task)

        else:
            self.queue.append(task)
            self.get_logger().info(
                f"No free robot. Added {task} to queue."
            )

        self.get_logger().info(f"Queue: {self.queue}")

    

    def robot1_status_callback(self, msg):

        self.robot_status["robot1"] = msg.data

        self.get_logger().info(f"Robot1 is {msg.data}")

        if msg.data == "free" and len(self.queue) > 0:
            task = self.queue.pop(0)
            self.assign_task("robot1", task)

    

    def robot2_status_callback(self, msg):

        self.robot_status["robot2"] = msg.data

        self.get_logger().info(f"Robot2 is {msg.data}")

        if msg.data == "free" and len(self.queue) > 0:
            task = self.queue.pop(0)
            self.assign_task("robot2", task)

    

    def robot3_status_callback(self, msg):

        self.robot_status["robot3"] = msg.data

        self.get_logger().info(f"Robot3 is {msg.data}")

        if msg.data == "free" and len(self.queue) > 0:
            task = self.queue.pop(0)
            self.assign_task("robot3", task)




def main(args=None):

    rclpy.init(args=args)

    node = TaskAllocator()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
