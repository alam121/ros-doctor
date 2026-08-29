# ROS Doctor Diagnosis

- Inferred ROS version: `unknown`
- Files scanned: `3`

## Agent Verification Loop

1. Collected 3 readable evidence files from cases/ros2_bad_parameter.
2. Inferred ROS version as unknown.
3. Generated 10 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 9 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. ROS2 parameter name or type mismatch

- Score: `0.84` (high confidence)
- Likely root cause: A launch file or YAML config provides a parameter name or value type that does not match what the node declares or expects.
- Recommended fix: Compare the node's declared parameters with YAML and launch inputs, correct the name or type, and verify with ros2 param describe/get.
- Verification checks:
  - `ros2 param list <node_name>`
  - `ros2 param describe <node_name> <parameter>`
  - `ros2 param get <node_name> <parameter>`
  - `ros2 launch <package> <launch_file> --show-args`

#### Confirming Evidence
- `cases/ros2_bad_parameter/logs/driver.log:1` [confirm:InvalidParameterTypeException] [ERROR] [lidar_driver]: InvalidParameterTypeException: parameter scan_rate has invalid type, expected double got string
- `cases/ros2_bad_parameter/logs/driver.log:1` [confirm:parameter .* has invalid type] [ERROR] [lidar_driver]: InvalidParameterTypeException: parameter scan_rate has invalid type, expected double got string
- `cases/ros2_bad_parameter/logs/driver.log:1` [confirm:expected .* got] [ERROR] [lidar_driver]: InvalidParameterTypeException: parameter scan_rate has invalid type, expected double got string
- `cases/ros2_bad_parameter/logs/driver.log:2` [confirm:failed to parse parameter] [ERROR] [launch]: failed to parse parameter file for node lidar_driver

#### Supporting Context
- `cases/ros2_bad_parameter/config/lidar.yaml:2` [context:ros__parameters] ros__parameters:
- `cases/ros2_bad_parameter/src_driver_snippet.py:1` [context:declare_parameter] node.declare_parameter("scan_rate", 10.0)
- `cases/ros2_bad_parameter/src_driver_snippet.py:2` [context:declare_parameter] node.declare_parameter("frame_id", "laser")

