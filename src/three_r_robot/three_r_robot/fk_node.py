#!/usr/bin/env python3

import math
import threading
import time

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class FKNode(Node):

    def __init__(self):

        super().__init__('fk_node')

        # =========================================================
        # ROBOT DIMENSIONS
        # =========================================================

        self.L1 = 5.0       # cm
        self.L2 = 11.0      # cm
        self.L3 = 11.0      # cm

        # =========================================================
        # JOINT NAMES
        # =========================================================

        self.joint_names = [
            'joint1',
            'joint2',
            'joint3'
        ]

        # =========================================================
        # PUBLISHER 1
        # REAL ROBOT / RVIZ
        #
        # /joint_states
        # =========================================================

        self.joint_state_pub = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        # =========================================================
        # PUBLISHER 2
        # GAZEBO
        #
        # ForwardCommandController
        # =========================================================

        self.gazebo_pub = self.create_publisher(
            Float64MultiArray,
            '/three_r_arm_controller/commands',
            10
        )

        # =========================================================
        # CURRENT SERVO ANGLES
        # =========================================================

        self.servo1 = 0.0
        self.servo2 = 0.0
        self.servo3 = 90.0

        # =========================================================
        # CURRENT DH ANGLES
        # =========================================================

        self.theta1 = 0.0
        self.theta2 = 0.0
        self.theta3 = 0.0

        # =========================================================
        # END EFFECTOR
        # =========================================================

        self.x = 22.0
        self.y = 0.0
        self.z = 5.0

        # =========================================================
        # FLAG
        # =========================================================

        self.new_command = False

        # =========================================================
        # CONTINUOUS PUBLISH
        #
        # 50 Hz
        # =========================================================

        self.timer = self.create_timer(
            0.02,
            self.publish_commands
        )

        # =========================================================
        # USER INPUT THREAD
        # =========================================================

        self.input_thread = threading.Thread(
            target=self.input_loop,
            daemon=True
        )

        self.input_thread.start()

        # =========================================================
        # STARTUP MESSAGE
        # =========================================================

        self.get_logger().info(
            '============================================'
        )

        self.get_logger().info(
            '          3R ROBOT FK CONTROLLER'
        )

        self.get_logger().info(
            '============================================'
        )

        self.get_logger().info(
            'Real Robot + Gazebo + RViz'
        )

        self.get_logger().info(
            'Robot dimensions:'
        )

        self.get_logger().info(
            'L1 = 5 cm'
        )

        self.get_logger().info(
            'L2 = 11 cm'
        )

        self.get_logger().info(
            'L3 = 11 cm'
        )

        self.get_logger().info(
            'Servo 3 = 90 deg -> DH theta3 = 0 deg'
        )

        self.get_logger().info(
            'Waiting for servo angle input...'
        )

    # =========================================================
    # USER INPUT
    # =========================================================

    def input_loop(self):

        while rclpy.ok():

            try:

                print()
                print("============================================")
                print("           ENTER SERVO ANGLES")
                print("============================================")

                servo1 = float(
                    input("Servo 1 [0-180]: ")
                )

                servo2 = float(
                    input("Servo 2 [0-180]: ")
                )

                servo3 = float(
                    input("Servo 3 [0-180]: ")
                )

                # =================================================
                # LIMIT CHECK
                # =================================================

                if not 0.0 <= servo1 <= 180.0:

                    print(
                        "ERROR: Servo 1 must be between 0 and 180."
                    )

                    continue

                if not 0.0 <= servo2 <= 180.0:

                    print(
                        "ERROR: Servo 2 must be between 0 and 180."
                    )

                    continue

                if not 0.0 <= servo3 <= 180.0:

                    print(
                        "ERROR: Servo 3 must be between 0 and 180."
                    )

                    continue

                # =================================================
                # SAVE SERVO ANGLES
                # =================================================

                self.servo1 = servo1
                self.servo2 = servo2
                self.servo3 = servo3

                # =================================================
                # SERVO → DH
                #
                # Your confirmed calibration:
                #
                # theta1 = servo1
                # theta2 = servo2
                # theta3 = servo3 - 90
                # =================================================

                theta1_deg = servo1
                theta2_deg = servo2
                theta3_deg = servo3 - 90.0

                # =================================================
                # DEG → RAD
                # =================================================

                self.theta1 = math.radians(theta1_deg)
                self.theta2 = math.radians(theta2_deg)
                self.theta3 = math.radians(theta3_deg)

                # =================================================
                # FORWARD KINEMATICS
                # =================================================

                self.calculate_fk()

                # =================================================
                # DISPLAY
                # =================================================

                print()
                print("============================================")
                print("              SERVO ANGLES")
                print("============================================")

                print(
                    f"Servo 1 = {servo1:.2f} deg"
                )

                print(
                    f"Servo 2 = {servo2:.2f} deg"
                )

                print(
                    f"Servo 3 = {servo3:.2f} deg"
                )

                print()
                print("============================================")
                print("               DH ANGLES")
                print("============================================")

                print(
                    f"Theta 1 = {theta1_deg:.2f} deg"
                )

                print(
                    f"Theta 2 = {theta2_deg:.2f} deg"
                )

                print(
                    f"Theta 3 = {theta3_deg:.2f} deg"
                )

                print()
                print("============================================")
                print("          FORWARD KINEMATICS")
                print("============================================")

                print(
                    f"X = {self.x:.4f} cm"
                )

                print(
                    f"Y = {self.y:.4f} cm"
                )

                print(
                    f"Z = {self.z:.4f} cm"
                )

                print()
                print("============================================")
                print("              COMMANDS")
                print("============================================")

                print(
                    "Gazebo joint command:"
                )

                print(
                    f"[{self.theta1:.4f}, "
                    f"{self.theta2:.4f}, "
                    f"{self.theta3:.4f}] rad"
                )

                print()

                print(
                    "Physical servo command:"
                )

                print(
                    f"[{servo1:.2f}, "
                    f"{servo2:.2f}, "
                    f"{servo3:.2f}] deg"
                )

                print()
                print(
                    "Command sent to REAL ROBOT + GAZEBO."
                )

                self.new_command = True

            except ValueError:

                print(
                    "ERROR: Enter numbers only."
                )

            except Exception as e:

                self.get_logger().error(
                    f"Input error: {e}"
                )

    # =========================================================
    # FORWARD KINEMATICS
    # =========================================================

    def calculate_fk(self):

        t1 = self.theta1
        t2 = self.theta2
        t3 = self.theta3

        # =====================================================
        # X
        # =====================================================

        self.x = (

            self.L2
            * math.cos(t1)
            * math.cos(t2)

            +

            self.L3
            * math.cos(t1)
            * math.cos(t2 + t3)

        )

        # =====================================================
        # Y
        # =====================================================

        self.y = (

            self.L2
            * math.sin(t1)
            * math.cos(t2)

            +

            self.L3
            * math.sin(t1)
            * math.cos(t2 + t3)

        )

        # =====================================================
        # Z
        # =====================================================

        self.z = (

            self.L1

            +

            self.L2
            * math.sin(t2)

            +

            self.L3
            * math.sin(t2 + t3)

        )

    # =========================================================
    # PUBLISH COMMANDS
    # =========================================================

    def publish_commands(self):

        # =====================================================
        # 1. PUBLISH JOINT STATES
        #
        # This drives RViz / robot_state_publisher.
        # =====================================================

        joint_msg = JointState()

        joint_msg.header.stamp = (
            self.get_clock().now().to_msg()
        )

        joint_msg.name = self.joint_names

        joint_msg.position = [
            self.theta1,
            self.theta2,
            self.theta3
        ]

        self.joint_state_pub.publish(
            joint_msg
        )

        # =====================================================
        # 2. PUBLISH GAZEBO CONTROLLER COMMAND
        #
        # IMPORTANT:
        # ForwardCommandController expects radians.
        # =====================================================

        gazebo_msg = Float64MultiArray()

        gazebo_msg.data = [
            float(self.theta1),
            float(self.theta2),
            float(self.theta3)
        ]

        self.gazebo_pub.publish(
            gazebo_msg
        )

    # =========================================================
    # SHUTDOWN
    # =========================================================

    def destroy_node(self):

        self.get_logger().info(
            'Stopping FK node.'
        )

        super().destroy_node()


# =============================================================
# MAIN
# =============================================================

def main(args=None):

    rclpy.init(args=args)

    node = FKNode()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':

    main()