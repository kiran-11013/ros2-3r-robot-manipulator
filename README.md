# 3R Robot Arm – ROS 2

A ROS 2 based **3-DOF (3R) robotic manipulator** project developed for simulation and physical servo control. The package includes a URDF/Xacro robot model, Gazebo simulation, an Arduino-based physical servo bridge, and a forward-kinematics control node.

## Features

- 3R robotic arm modeled using URDF/Xacro
- ROS 2 Python package using `ament_python`
- Gazebo simulation with `ros2_control` / `three_r_arm_controller`
- Arduino interface for physical servo control
- Forward Kinematics (FK) node with interactive terminal input

## Robot Configuration

The physical arm uses three revolute joints:

| Parameter | Value |
|---|---:|
| Number of joints | 3 revolute joints |
| Link 1 length | 5 cm |
| Link 2 length | 11 cm |
| Link 3 length | 11 cm |
| Home position | Approximately (22, 0, 5) cm |
| Servo motors | MG90-class servos |
| Controller | Arduino Uno |

The exact servo offsets and physical calibration are implemented in `fk_node.py` and `arduino_bridge.py`.

## Workspace Structure

```text
ros2_3r_ws/
├── rviz.rviz
├── src/
│   └── three_r_robot/
│       ├── three_r_robot/
│       │   ├── arduino_bridge.py
│       │   ├── fk_node.py
│       │   └── __init__.py
│       ├── urdf/
│       │   └── three_r_robot.urdf.xacro
│       ├── launch/
│       │   └── complete.launch.py
│       ├── config/
│       │   └── controllers.yaml
│       ├── rviz/
│       │   └── three_r_robot.rviz
│       ├── resource/
│       │   └── three_r_robot
│       ├── test/
│       ├── package.xml
│       ├── setup.py
│       └── setup.cfg
└── README.md
```

## Requirements

Recommended environment:

- Ubuntu 22.04
- ROS 2 Humble
- Python 3
- Gazebo Classic 11
- Arduino IDE / Arduino Uno for physical hardware

Install the main ROS dependencies:

```bash
sudo apt update
sudo apt install \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers
```

If Gazebo simulation is used, install the required Gazebo/ROS integration packages for your ROS 2 Humble setup.

## Build the Package

Clone the repository and enter the workspace:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ros2_3r_ws
```

Source ROS 2:

```bash
source /opt/ros/humble/setup.bash
```

Install/build the workspace:

```bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

To make the workspace available in new terminals:

```bash
echo 'source ~/ros2_3r_ws/install/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

## Run the Complete Simulation

Launches Gazebo, spawns the robot, and starts the joint state broadcaster + arm controller:

```bash
ros2 launch three_r_robot complete.launch.py
```

## Forward Kinematics

The FK node takes servo angles from the terminal, converts them to DH joint angles, computes the end-effector position, and publishes `/joint_states` and `/three_r_arm_controller/commands`.

Run:

```bash
ros2 run three_r_robot fk_node
```

Calibrated link dimensions used by the FK implementation:

```text
L1 = 5 cm
L2 = 11 cm
L3 = 11 cm
```

For the planar 3R arm, the end-effector position is:

```text
x = L2 cos(theta1) cos(theta2) + L3 cos(theta1) cos(theta2 + theta3)
y = L2 sin(theta1) cos(theta2) + L3 sin(theta1) cos(theta2 + theta3)
z = L1 + L2 sin(theta2) + L3 sin(theta2 + theta3)
```

`fk_node.py` is the source of truth for the project's joint-angle conventions and servo offsets (servo3 = theta3 + 90°).

## Physical Robot – Arduino

The physical arm is driven over serial by `arduino_bridge.py`, which subscribes to `/joint_states`, converts joint angles to servo commands, and writes them to the Arduino while mirroring the command to Gazebo.

Before running the physical robot:

1. Connect the Arduino to the computer.
2. Identify the serial device:

```bash
ls /dev/ttyACM* /dev/ttyUSB*
```

3. Check that the user has serial-port permissions:

```bash
groups
```

The user normally needs to belong to the `dialout` group:

```bash
sudo usermod -aG dialout $USER
```

Log out and back in after changing the group membership.

> **Important:** Check the serial port and baud rate in `arduino_bridge.py` before operating the physical arm — the code defaults to `/dev/ttyUSB0` at 115200 baud. Do not assume this is always the correct device.

Run:

```bash
ros2 run three_r_robot arduino_bridge
```

## Servo Configuration

The physical arm uses three servo-controlled joints. The calibrated joint convention includes a servo offset for the third joint: the third servo's approximately 90° position is used as the zero reference for the corresponding mathematical joint angle (`theta3 = servo3 - 90`).

Because servo limits and mechanical zero positions depend on the physical assembly, verify the limits before connecting the complete arm.

## Useful ROS 2 Commands

List available nodes:

```bash
ros2 node list
```

List topics:

```bash
ros2 topic list
```

Inspect joint states:

```bash
ros2 topic echo /joint_states
```

List package executables:

```bash
ros2 pkg executables three_r_robot
```

## Package Executables

```text
arduino_bridge
fk_node
```

## Safety

When testing the physical robot:

- Keep the arm clear of people and objects.
- Start with low/safe servo angles.
- Verify the mechanical zero position before commanding joints.
- Do not send commands outside the tested servo range.
- Disconnect servo power when changing wiring.
- Use an appropriate external supply for the servos rather than drawing excessive current from the Arduino 5 V regulator.

## Future Development

Planned extensions include:

- Jacobian-based inverse kinematics
- Pick-and-place control
- End-effector trajectory generation
- Improved joint-limit handling
- Gazebo-to-hardware validation
- Closed-loop servo feedback
- Gripper control integration

## License

This project is released under the **Apache License 2.0**.

## Author

**Kiran**
M.Tech Robotics and Intelligent Systems
Indian Institute of Technology Hyderabad
