# ROS Doctor Diagnosis

- Inferred ROS version: `ros2`
- Files scanned: `4`

## Agent Verification Loop

1. Collected 4 readable evidence files from cases/ros2_namespace_mismatch.
2. Inferred ROS version as ros2.
3. Generated 9 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 6 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. ROS2 topic or namespace mismatch

- Score: `0.64` (medium confidence)
- Likely root cause: Publisher and subscriber names do not resolve to the same fully qualified topic, often because remaps, namespaces, or leading slashes differ.
- Recommended fix: Normalize topic names and remaps across launch files and node code. Verify with ros2 topic list, ros2 node info, and a minimal pub/sub test.
- Verification checks:
  - `ros2 node list`
  - `ros2 node info <node_name>`
  - `ros2 topic list -t`
  - `ros2 topic echo <expected_topic> --once`

#### Confirming Evidence
- `cases/ros2_namespace_mismatch/logs/runtime.log:1` [confirm:waiting for message] [INFO] [camera_filter]: waiting for message on /camera/image_raw
- `cases/ros2_namespace_mismatch/logs/runtime.log:2` [confirm:no publishers] [WARN] [camera_filter]: no publishers matched requested input topic after 30 seconds

#### Supporting Context
- `cases/ros2_namespace_mismatch/logs/runtime.log:2` [context:topic] [WARN] [camera_filter]: no publishers matched requested input topic after 30 seconds
- `cases/ros2_namespace_mismatch/src/perception/camera_filter.py:5` [context:create_subscription] node.create_subscription(Image, "/camera/image_raw", handle_image, 10)
- `cases/ros2_namespace_mismatch/src/perception/launch/perception.launch.py:10` [context:namespace] namespace="robot1",
- `cases/ros2_namespace_mismatch/src/perception/launch/perception.launch.py:11` [context:remap] remappings=[("image_raw", "/camera/image_raw")],

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
- `cases/ros2_namespace_mismatch/src/perception/camera_filter.py:1` [context:import ] import rclpy
- `cases/ros2_namespace_mismatch/src/perception/launch/perception.launch.py:1` [context:import ] from launch import LaunchDescription
- `cases/ros2_namespace_mismatch/src/perception/launch/perception.launch.py:2` [context:import ] from launch_ros.actions import Node

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
- `cases/ros2_namespace_mismatch/src/perception/launch/perception.launch.py:9` [context:executable=] executable="camera_filter",

