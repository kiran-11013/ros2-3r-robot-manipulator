import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import xacro


def generate_launch_description():

    # =====================================================
    # PACKAGE
    # =====================================================

    pkg_path = get_package_share_directory(
        'three_r_robot'
    )

    # =====================================================
    # XACRO
    # =====================================================

    xacro_file = os.path.join(
        pkg_path,
        'urdf',
        'three_r_robot.urdf.xacro'
    )

    robot_description_config = xacro.process_file(
        xacro_file
    )

    robot_description = robot_description_config.toxml()

    # =====================================================
    # ROBOT STATE PUBLISHER
    # =====================================================

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',

        parameters=[
            {
                'robot_description': robot_description
            }
        ]
    )

    # =====================================================
    # GAZEBO
    # =====================================================

    gazebo = ExecuteProcess(
        cmd=[
            'gz',
            'sim',
            '-r',
            '-v',
            '4',
            'empty.sdf'
        ],
        output='screen'
    )

    # =====================================================
    # SPAWN ROBOT
    # =====================================================

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_three_r_robot',
        output='screen',

        arguments=[
            '-topic',
            'robot_description',

            '-name',
            'three_r_robot',

            '-allow_renaming',
            'true'
        ]
    )

    # =====================================================
    # JOINT STATE BROADCASTER
    # =====================================================

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',

        arguments=[
            'joint_state_broadcaster',

            '--controller-manager',
            '/controller_manager',

            '--controller-manager-timeout',
            '30'
        ],

        output='screen'
    )

    # =====================================================
    # 3R ARM POSITION CONTROLLER
    # =====================================================

    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',

        arguments=[
            'three_r_arm_controller',

            '--controller-manager',
            '/controller_manager',

            '--controller-manager-timeout',
            '30'
        ],

        output='screen'
    )

    # =====================================================
    # START ROBOT SPAWN AFTER GAZEBO
    # =====================================================

    delayed_spawn = TimerAction(
        period=3.0,
        actions=[
            spawn_robot
        ]
    )

    # =====================================================
    # START JOINT STATE BROADCASTER
    #
    # Give Gazebo + gz_ros2_control time to initialize.
    # =====================================================

    delayed_joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[
            joint_state_broadcaster_spawner
        ]
    )

    # =====================================================
    # START ARM CONTROLLER
    #
    # Start after joint state broadcaster.
    # =====================================================

    delayed_arm_controller = TimerAction(
        period=11.0,
        actions=[
            arm_controller_spawner
        ]
    )

    # =====================================================
    # RETURN
    # =====================================================

    return LaunchDescription([

        # -------------------------------------------------
        # 1. Gazebo
        # -------------------------------------------------

        gazebo,

        # -------------------------------------------------
        # 2. Robot State Publisher
        # -------------------------------------------------

        robot_state_publisher,

        # -------------------------------------------------
        # 3. Spawn robot
        # -------------------------------------------------

        delayed_spawn,

        # -------------------------------------------------
        # 4. Joint State Broadcaster
        # -------------------------------------------------

        delayed_joint_state_broadcaster,

        # -------------------------------------------------
        # 5. 3R Arm Controller
        # -------------------------------------------------

        delayed_arm_controller,

    ])