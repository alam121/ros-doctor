# ROS Doctor Diagnosis

- Inferred ROS version: `ros2`
- Files scanned: `4`

## Agent Verification Loop

1. Collected 4 readable evidence files from cases/ros2_missing_executable.
2. Inferred ROS version as ros2.
3. Generated 9 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 7 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. ROS2 executable or entry point is missing

- Score: `0.64` (medium confidence)
- Likely root cause: The package exists, but the executable named by launch or ros2 run is not installed because setup.py/CMake install rules or console_scripts are wrong.
- Recommended fix: Add the missing console_scripts entry or install target, rebuild, source the install space, and confirm with ros2 pkg executables.
- Verification checks:
  - `ros2 pkg executables <package>`
  - `colcon build --symlink-install`
  - `source install/setup.bash`
  - `ros2 run <package> <executable>`

#### Confirming Evidence
- `cases/ros2_missing_executable/logs/launch.log:1` [confirm:executable .* not found] [ERROR] [launch_ros.actions.node]: executable 'serial_driver_node' not found on the libexec directory '/home/dev/ws/install/robot_driver/lib/robot_driver'
- `cases/ros2_missing_executable/logs/launch.log:1` [confirm:libexec directory] [ERROR] [launch_ros.actions.node]: executable 'serial_driver_node' not found on the libexec directory '/home/dev/ws/install/robot_driver/lib/robot_driver'

#### Supporting Context
- `cases/ros2_missing_executable/src/robot_driver/bringup.launch.py:3` [context:executable=] driver = Node(package="robot_driver", executable="serial_driver_node")
- `cases/ros2_missing_executable/src/robot_driver/package.xml:7` [context:ament_python] <buildtool_depend>ament_python</buildtool_depend>
- `cases/ros2_missing_executable/src/robot_driver/setup.py:7` [context:entry_points] entry_points={
- `cases/ros2_missing_executable/src/robot_driver/setup.py:8` [context:console_scripts] "console_scripts": [

### 2. ROS2 package dependency is missing or not declared

- Score: `0.12` (low confidence)
- Likely root cause: A node or launch file imports/executes a package that is not installed, not built, or not declared in package.xml.
- Recommended fix: Install the missing dependency or add it to package.xml, then run rosdep install, rebuild with colcon, and source the workspace.
- Verification checks:
  - `rosdep install --from-paths src --ignore-src -r -y`
  - `colcon build --symlink-install`
  - `source install/setup.bash`
  - `ros2 pkg prefix <missing_package>`

#### Confirming Evidence
- No direct evidence captured.

#### Supporting Context
- `cases/ros2_missing_executable/src/robot_driver/bringup.launch.py:1` [context:import ] from launch_ros.actions import Node
- `cases/ros2_missing_executable/src/robot_driver/package.xml:7` [context:depend>] <buildtool_depend>ament_python</buildtool_depend>
- `cases/ros2_missing_executable/src/robot_driver/setup.py:1` [context:import ] from setuptools import setup

