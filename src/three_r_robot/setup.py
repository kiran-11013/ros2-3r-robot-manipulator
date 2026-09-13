from setuptools import find_packages, setup
import os


package_name = 'three_r_robot'


setup(

    # =====================================================
    # PACKAGE INFORMATION
    # =====================================================

    name=package_name,

    version='0.0.1',

    packages=find_packages(
        include=[
            package_name,
            package_name + '.*'
        ]
    ),

    # =====================================================
    # INSTALL DATA FILES
    # =====================================================

    data_files=[

        # -------------------------------------------------
        # ROS 2 package index
        # -------------------------------------------------

        (
            'share/ament_index/resource_index/packages',
            [
                'resource/' + package_name
            ]
        ),

        # -------------------------------------------------
        # package.xml
        # -------------------------------------------------

        (
            'share/' + package_name,
            [
                'package.xml'
            ]
        ),

        # -------------------------------------------------
        # LAUNCH FILES
        # -------------------------------------------------

        (
            os.path.join(
                'share',
                package_name,
                'launch'
            ),
            [
                'launch/display.launch.py',
                'launch/complete.launch.py'
            ]
        ),

        # -------------------------------------------------
        # URDF / XACRO
        # -------------------------------------------------

        (
            os.path.join(
                'share',
                package_name,
                'urdf'
            ),
            [
                'urdf/three_r_robot.urdf.xacro'
            ]
        ),

        # -------------------------------------------------
        # CONTROLLERS
        # -------------------------------------------------

        (
            os.path.join(
                'share',
                package_name,
                'config'
            ),
            [
                'config/controllers.yaml'
            ]
        ),

        # -------------------------------------------------
        # RVIZ
        # -------------------------------------------------

        (
            os.path.join(
                'share',
                package_name,
                'rviz'
            ),
            [
                'rviz/three_r_robot.rviz'
            ]
        ),
    ],

    # =====================================================
    # DEPENDENCIES
    # =====================================================

    install_requires=[
        'setuptools',
    ],

    zip_safe=True,

    # =====================================================
    # MAINTAINER
    # =====================================================

    maintainer='kiran',

    maintainer_email='kiran@example.com',

    # =====================================================
    # DESCRIPTION
    # =====================================================

    description='3R robotic manipulator ROS 2 package',

    license='Apache-2.0',

    # =====================================================
    # TESTING
    # =====================================================

    tests_require=[
        'pytest'
    ],

    # =====================================================
    # ROS 2 EXECUTABLES
    # =====================================================

    entry_points={

        'console_scripts': [

            # Physical Arduino bridge
            'arduino_bridge = '
            'three_r_robot.arduino_bridge:main',

            # Servo bridge
            'servo_bridge = '
            'three_r_robot.servo_bridge:main',

            # Forward kinematics
            'fk_node = '
            'three_r_robot.fk_node:main',
        ],
    },
)