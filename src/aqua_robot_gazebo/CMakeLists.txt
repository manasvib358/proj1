cmake_minimum_required(VERSION 3.8)
project(aqua_robot_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(gazebo_ros REQUIRED)

# Install all resource directories so they're found at runtime
install(
  DIRECTORY
    worlds
    urdf
    launch
    config
    models
  DESTINATION share/${PROJECT_NAME}
  OPTIONAL   # config/models may be empty directories — don't fail
)

# Mark launch files as executable
install(
  PROGRAMS
    launch/lake_simulation.launch.py
  DESTINATION share/${PROJECT_NAME}/launch
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
