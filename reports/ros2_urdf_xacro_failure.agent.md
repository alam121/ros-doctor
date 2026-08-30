# ROS Doctor Diagnosis

- Inferred ROS version: `unknown`
- Files scanned: `2`

## Agent Verification Loop

1. Collected 2 readable evidence files from cases/ros2_urdf_xacro_failure.
2. Inferred ROS version as unknown.
3. Generated 10 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 8 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. URDF or xacro parse failure

- Score: `0.88` (high confidence)
- Likely root cause: Robot description generation fails because a URDF/xacro file has malformed XML, an undefined xacro property/macro, or an invalid mesh/reference path.
- Recommended fix: Run xacro directly, fix the reported XML/property/path issue, then restart robot_state_publisher and verify the robot_description parameter.
- Verification checks:
  - `xacro <robot>.urdf.xacro`
  - `check_urdf <robot>.urdf`
  - `ros2 param get /robot_state_publisher robot_description`
  - `ros2 run tf2_tools view_frames`

#### Confirming Evidence
- `cases/ros2_urdf_xacro_failure/logs/robot_state_publisher.log:1` [confirm:xacro: error] [ERROR] [robot_state_publisher]: xacro: error: XML parsing error: mismatched tag: line 14, column 4
- `cases/ros2_urdf_xacro_failure/logs/robot_state_publisher.log:1` [confirm:XML parsing error] [ERROR] [robot_state_publisher]: xacro: error: XML parsing error: mismatched tag: line 14, column 4
- `cases/ros2_urdf_xacro_failure/logs/robot_state_publisher.log:1` [confirm:mismatched tag] [ERROR] [robot_state_publisher]: xacro: error: XML parsing error: mismatched tag: line 14, column 4

#### Supporting Context
- `cases/ros2_urdf_xacro_failure/logs/robot_state_publisher.log:1` [context:robot_state_publisher] [ERROR] [robot_state_publisher]: xacro: error: XML parsing error: mismatched tag: line 14, column 4
- `cases/ros2_urdf_xacro_failure/logs/robot_state_publisher.log:2` [context:robot_description] [ERROR] [launch]: robot_description command failed while evaluating robot.urdf.xacro
- `cases/ros2_urdf_xacro_failure/urdf/robot.urdf.xacro:1` [context:<robot] <robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="badbot">
- `cases/ros2_urdf_xacro_failure/urdf/robot.urdf.xacro:5` [context:mesh filename] <mesh filename="package://badbot/meshes/base.stl"/>

### 2. TF frame, timestamp, or simulation clock failure

- Score: `0.08` (low confidence)
- Likely root cause: Transforms are unavailable or rejected because frame IDs, timestamps, or use_sim_time settings are inconsistent.
- Recommended fix: Verify the TF tree, frame names, /clock publication, and use_sim_time on all nodes that consume transforms.
- Verification checks:
  - `ros2 run tf2_tools view_frames`
  - `ros2 topic echo /tf --once`
  - `ros2 param get <node_name> use_sim_time`
  - `ros2 topic echo /clock --once`

#### Confirming Evidence
- No direct evidence captured.

#### Supporting Context
- `cases/ros2_urdf_xacro_failure/logs/robot_state_publisher.log:1` [context:robot_state_publisher] [ERROR] [robot_state_publisher]: xacro: error: XML parsing error: mismatched tag: line 14, column 4
- `cases/ros2_urdf_xacro_failure/urdf/robot.urdf.xacro:2` [context:\bbase_link\b] <link name="base_link">

