cmake_minimum_required(VERSION 3.5)
project(littlebot_gazebo)

find_package(ament_cmake REQUIRED)

# Gazebo IGN_GAZEBO_RESOURCE_PATH variable configuration
configure_file(
  "hooks/hook.dsv.in"
  "${CMAKE_CURRENT_BINARY_DIR}/hooks/hook.dsv" @ONLY
)

install(DIRECTORY 
  launch
  urdf
  worlds
  models
  ${CMAKE_CURRENT_BINARY_DIR}/hooks
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
