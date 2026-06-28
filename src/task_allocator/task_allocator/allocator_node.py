import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TaskAllocator(Node):

    def __init__(self):
        super().__init__('task_allocator')

        
        self.robots = {
            "robot_1": "free",
            "robot_2": "free",
            "robot_3": "free"
        }

        
        self.pending_tasks = []

        
        self.subscription = self.create_subscription(
            String,
            '/waste_detection',
            self.allocate_task,
            10
        )

        
        self.robot1_sub = self.create_subscription(
            String,
            '/robot1/status',
            self.robot1_callback,
            10
        )

        self.robot2_sub = self.create_subscription(
            String,
            '/robot2/status',
            self.robot2_callback,
            10
        )

        self.robot3_sub = self.create_subscription(
            String,
            '/robot3/status',
            self.robot3_callback,
            10
        )

        self.get_logger().info("Task Allocator Started")

        
        self.robot1_pub = self.create_publisher(
            String,
            '/robot1/task',
            10
        )

        self.robot2_pub = self.create_publisher(
            String,
            '/robot2/task',
            10
        )

        self.robot3_pub = self.create_publisher(
            String,
            '/robot3/task',
            10
        )    
    
    

    def allocate_task(self, msg):

        marker_id = msg.data

        free_robot = None

        for robot, status in self.robots.items():
            if status == "free":
                free_robot = robot
                break

        if free_robot:

            self.robots[free_robot] = "busy"

            self.get_logger().info(
                f"Assigned {marker_id} to {free_robot}"
            )
            
            task_msg = String()
            task_msg.data = marker_id

            if free_robot == "robot_1":
                self.robot1_pub.publish(task_msg)

            elif free_robot == "robot_2":
                self.robot2_pub.publish(task_msg)

            else:
                self.robot3_pub.publish(task_msg)       
    
  
        else:

            self.pending_tasks.append(marker_id)

            self.get_logger().info(
                f"No free robot. Added {marker_id} to queue."
            )

            self.get_logger().info(
                f"Queue: {self.pending_tasks}"
            )

    
    
    

    def robot1_callback(self, msg):
        if msg.data == "free":
            self.robot_available("robot_1")

    def robot2_callback(self, msg):
        if msg.data == "free":
            self.robot_available("robot_2")

    def robot3_callback(self, msg):
        if msg.data == "free":
            self.robot_available("robot_3")

    
    
    

    def robot_available(self, robot):

        self.robots[robot] = "free"

        self.get_logger().info(f"{robot} is now FREE")

        if len(self.pending_tasks) > 0:

            next_task = self.pending_tasks.pop(0)

            self.robots[robot] = "busy"

            self.get_logger().info(
                f"Assigned queued task {next_task} to {robot}"
            )
    
            task_msg = String()
            task_msg.data = next_task
            
            if robot == "robot_1":
                self.robot1_pub.publish(task_msg)
           
            elif robot == "robot_2":
                self.robot2_pub.publish(task_msg)
 
            else:
                self.robot3_pub.publish(task_msg)

            self.get_logger().info(
                f"Remaining Queue: {self.pending_tasks}"
            )       

        self.get_logger().info(
            f"Robot Status: {self.robots}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = TaskAllocator()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
