#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

import serial
import math


class ArduinoBridge(Node):

    def __init__(self):

        super().__init__('arduino_bridge')

        # =================================================
        # ARDUINO SERIAL
        # =================================================

        self.port = '/dev/ttyUSB0'
        self.baudrate = 115200

        try:

            self.arduino = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1
            )

            self.get_logger().info(
                f'Connected to Arduino on {self.port}'
            )

        except serial.SerialException as e:

            self.get_logger().error(
                f'Could not connect to Arduino: {e}'
            )

            self.arduino = None


        # =================================================
        # SUBSCRIBE TO JOINT STATES
        # =================================================

        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )


        # =================================================
        # GAZEBO COMMAND PUBLISHER
        # =================================================

        self.gazebo_publisher = self.create_publisher(
            Float64MultiArray,
            '/three_r_arm_controller/commands',
            10
        )


        # =================================================
        # CURRENT SERVO VALUES
        # =================================================

        self.servo1 = 0
        self.servo2 = 0
        self.servo3 = 90


        self.get_logger().info(
            'Arduino + Gazebo bridge ready.'
        )

        self.get_logger().info(
            'Waiting for /joint_states...'
        )


    # =====================================================
    # JOINT STATE CALLBACK
    # =====================================================

    def joint_callback(self, msg):

        try:

            # Default ROS joint positions
            joint1 = 0.0
            joint2 = 0.0
            joint3 = 0.0


            # =================================================
            # READ JOINT VALUES
            # =================================================

            for i, name in enumerate(msg.name):

                if i >= len(msg.position):
                    continue

                angle_rad = msg.position[i]


                if name == 'joint1':

                    joint1 = angle_rad

                    angle_deg = math.degrees(angle_rad)

                    self.servo1 = self.ros_to_servo1(
                        angle_deg
                    )


                elif name == 'joint2':

                    joint2 = angle_rad

                    angle_deg = math.degrees(angle_rad)

                    self.servo2 = self.ros_to_servo2(
                        angle_deg
                    )


                elif name == 'joint3':

                    joint3 = angle_rad

                    angle_deg = math.degrees(angle_rad)

                    self.servo3 = self.ros_to_servo3(
                        angle_deg
                    )


            # =================================================
            # SEND TO REAL ARDUINO
            # =================================================

            self.send_to_arduino()


            # =================================================
            # SEND TO GAZEBO
            #
            # Gazebo expects radians.
            #
            # [joint1, joint2, joint3]
            # =================================================

            gazebo_msg = Float64MultiArray()

            gazebo_msg.data = [
                joint1,
                joint2,
                joint3
            ]

            self.gazebo_publisher.publish(
                gazebo_msg
            )


        except Exception as e:

            self.get_logger().error(
                f'Joint conversion error: {e}'
            )


    # =====================================================
    # JOINT 1
    #
    # ROS:
    #   0 to 180 degrees
    #
    # SERVO:
    #   0 to 180 degrees
    # =====================================================

    def ros_to_servo1(self, angle):

        servo = angle

        servo = max(
            0.0,
            min(180.0, servo)
        )

        return int(round(servo))


    # =====================================================
    # JOINT 2
    #
    # ROS:
    #   0 to 180 degrees
    #
    # SERVO:
    #   0 to 180 degrees
    # =====================================================

    def ros_to_servo2(self, angle):

        servo = angle

        servo = max(
            0.0,
            min(180.0, servo)
        )

        return int(round(servo))


    # =====================================================
    # JOINT 3
    #
    # MATLAB:
    #
    # theta3 = servo3 - 90
    #
    # Therefore:
    #
    # servo3 = theta3 + 90
    # =====================================================

    def ros_to_servo3(self, angle):

        servo = angle + 90.0

        servo = max(
            0.0,
            min(180.0, servo)
        )

        return int(round(servo))


    # =====================================================
    # SEND COMMAND TO ARDUINO
    #
    # Arduino expects:
    #
    # Servo1,Servo2,Servo3,Gripper
    # =====================================================

    def send_to_arduino(self):

        if self.arduino is None:
            return


        gripper = 80


        command = (
            f'{self.servo1},'
            f'{self.servo2},'
            f'{self.servo3},'
            f'{gripper}\n'
        )


        try:

            self.arduino.write(
                command.encode()
            )

            self.get_logger().info(
                f'ARDUINO: {command.strip()}'
            )

        except serial.SerialException as e:

            self.get_logger().error(
                f'Failed to send Arduino command: {e}'
            )


    # =====================================================
    # SHUTDOWN
    # =====================================================

    def destroy_node(self):

        if self.arduino is not None:

            self.arduino.close()

            self.get_logger().info(
                'Arduino serial connection closed.'
            )

        super().destroy_node()


# =========================================================
# MAIN
# =========================================================

def main(args=None):

    rclpy.init(args=args)

    node = ArduinoBridge()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':

    main()