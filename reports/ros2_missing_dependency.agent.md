# ROS Doctor Diagnosis

- Inferred ROS version: `ros2`
- Files scanned: `4`

## Agent Verification Loop

1. Collected 4 readable evidence files from cases/ros2_missing_dependency.
2. Inferred ROS version as ros2.
3. Generated 9 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 6 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. ROS2 package dependency is missing or not declared

- Score: `0.48` (medium confidence)
- Likely root cause: A node or launch file imports/executes a package that is not installed, not built, or not declared in package.xml.
- Recommended fix: Install the missing dependency or add it to package.xml, then run rosdep install, rebuild with colcon, and source the workspace.
- Verification checks:
  - `rosdep install --from-paths src --ignore-src -r -y`
  - `colcon build --symlink-install`
  - `source install/setup.bash`
  - `ros2 pkg prefix <missing_package>`

#### Confirming Evidence
- `cases/ros2_missing_dependency/logs/launch.log:2` [confirm:package .* not found] [ERROR] [launch]: Caught exception in launch: "package 'depthimage_to_laserscan' not found, searching: ['/home/dev/ws/install/nav_stack', '/opt/ros/humble']"

#### Supporting Context
- `cases/ros2_missing_dependency/src/nav_stack/launch/bringup.launch.py:1` [context:import ] from launch import LaunchDescription
- `cases/ros2_missing_dependency/src/nav_stack/launch/bringup.launch.py:2` [context:import ] from launch_ros.actions import Node
- `cases/ros2_missing_dependency/src/nav_stack/package.xml:7` [context:exec_depend] <exec_depend>nav2_bringup</exec_depend>
- `cases/ros2_missing_dependency/src/nav_stack/package.xml:7` [context:depend>] <exec_depend>nav2_bringup</exec_depend>
- `cases/ros2_missing_dependency/src/nav_stack/package.xml:8` [context:exec_depend] <exec_depend>slam_toolbox</exec_depend>
- `cases/ros2_missing_dependency/src/nav_stack/package.xml:8` [context:depend>] <exec_depend>slam_toolbox</exec_depend>

### 2. Workspace or ROS environment was not sourced

- Score: `0.32` (low confidence)
- Likely root cause: The shell environment cannot see ROS packages because setup.bash/local_setup.bash was not sourced, or ROS_PACKAGE_PATH/AMENT_PREFIX_PATH points at the wrong workspace.
- Recommended fix: Source the correct ROS distribution and workspace setup file in the active shell, then rerun package discovery before launching.
- Verification checks:
  - `echo $ROS_DISTRO`
  - `echo $AMENT_PREFIX_PATH`
  - `echo $ROS_PACKAGE_PATH`
  - `source /opt/ros/<distro>/setup.bash && source install/setup.bash`

#### Confirming Evidence
- `cases/ros2_missing_dependency/logs/launch.log:2` [confirm:package .* not found] [ERROR] [launch]: Caught exception in launch: "package 'depthimage_to_laserscan' not found, searching: ['/home/dev/ws/install/nav_stack', '/opt/ros/humble']"

#### Supporting Context
- `cases/ros2_missing_dependency/env.txt:1` [context:ROS_DISTRO=] ROS_DISTRO=humble
- `cases/ros2_missing_dependency/env.txt:2` [context:AMENT_PREFIX_PATH=] AMENT_PREFIX_PATH=/home/dev/ws/install/nav_stack:/opt/ros/humble

### 3. ROS2 executable or entry point is missing

- Score: `0.04` (low confidence)
- Likely root cause: The package exists, but the executable named by launch or ros2 run is not installed because setup.py/CMake install rules or console_scripts are wrong.
- Recommended fix: Add the missing console_scripts entry or install target, rebuild, source the install space, and confirm with ros2 pkg executables.
- Verification checks:
  - `ros2 pkg executables <package>`
  - `colcon build --symlink-install`
  - `source install/setup.bash`
  - `ros2 run <package> <executable>`

#### Confirming Evidence
- No direct evidence captured.

#### Supporting Context
- `cases/ros2_missing_dependency/src/nav_stack/launch/bringup.launch.py:9` [context:executable=] executable="depthimage_to_laserscan_node",

