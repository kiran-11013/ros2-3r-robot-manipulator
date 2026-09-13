cmake_minimum_required(VERSION 3.8)

project(three_r_robot)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    urdf
    launch
    meshes
    config
  DESTINATION
    share/${PROJECT_NAME}
)

ament_package()
