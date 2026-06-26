cmake_minimum_required(VERSION 3.8)
project(asv_fleet)

find_package(ament_cmake REQUIRED)

# Share files (launch/urdf/worlds/models/config) get installed so
# `ros2 launch asv_fleet ...` and get_package_share_directory() can
# find them after `colcon build`.
install(DIRECTORY
  launch
  urdf
  worlds
  models
  config
  DESTINATION share/${PROJECT_NAME}
)

# Python script installed as a runnable ros2 executable
# (`ros2 run asv_fleet waste_seek_node.py`), without needing to
# convert this whole package to ament_python.
install(PROGRAMS
  scripts/waste_seek_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
