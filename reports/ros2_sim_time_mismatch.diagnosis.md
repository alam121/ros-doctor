# ROS Doctor Diagnosis

- Inferred ROS version: `unknown`
- Files scanned: `3`

## Agent Verification Loop

1. Collected 3 readable evidence files from cases/ros2_sim_time_mismatch.
2. Inferred ROS version as unknown.
3. Generated 10 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 7 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. TF frame, timestamp, or simulation clock failure

- Score: `0.88` (high confidence)
- Likely root cause: Transforms are unavailable or rejected because frame IDs, timestamps, or use_sim_time settings are inconsistent.
- Recommended fix: Verify the TF tree, frame names, /clock publication, and use_sim_time on all nodes that consume transforms.
- Verification checks:
  - `ros2 run tf2_tools view_frames`
  - `ros2 topic echo /tf --once`
  - `ros2 param get <node_name> use_sim_time`
  - `ros2 topic echo /clock --once`

#### Confirming Evidence
- `cases/ros2_sim_time_mismatch/config/slam.yaml:3` [confirm:use_sim_time] use_sim_time: true
- `cases/ros2_sim_time_mismatch/logs/slam.log:1` [confirm:Lookup would require extrapolation] [WARN] [slam_toolbox]: Lookup would require extrapolation into the future. Requested time 203.2 but latest transform is at time 0.0
- `cases/ros2_sim_time_mismatch/logs/slam.log:2` [confirm:use_sim_time] [WARN] [slam_toolbox]: use_sim_time is true, but /clock has not published any messages

#### Supporting Context
- `cases/ros2_sim_time_mismatch/config/slam.yaml:4` [context:\bodom\b] odom_frame: odom
- `cases/ros2_sim_time_mismatch/config/slam.yaml:5` [context:\bmap\b] map_frame: map
- `cases/ros2_sim_time_mismatch/logs/slam.log:2` [context:/clock] [WARN] [slam_toolbox]: use_sim_time is true, but /clock has not published any messages
- `cases/ros2_sim_time_mismatch/ros2_topic_echo_clock.txt:1` [context:/clock] WARNING: topic [/clock] does not appear to be published yet

### 2. ROS2 topic or namespace mismatch

- Score: `0.04` (low confidence)
- Likely root cause: Publisher and subscriber names do not resolve to the same fully qualified topic, often because remaps, namespaces, or leading slashes differ.
- Recommended fix: Normalize topic names and remaps across launch files and node code. Verify with ros2 topic list, ros2 node info, and a minimal pub/sub test.
- Verification checks:
  - `ros2 node list`
  - `ros2 node info <node_name>`
  - `ros2 topic list -t`
  - `ros2 topic echo <expected_topic> --once`

#### Confirming Evidence
- No direct evidence captured.

#### Supporting Context
- `cases/ros2_sim_time_mismatch/ros2_topic_echo_clock.txt:1` [context:topic] WARNING: topic [/clock] does not appear to be published yet

### 3. ROS2 parameter name or type mismatch

- Score: `0.04` (low confidence)
- Likely root cause: A launch file or YAML config provides a parameter name or value type that does not match what the node declares or expects.
- Recommended fix: Compare the node's declared parameters with YAML and launch inputs, correct the name or type, and verify with ros2 param describe/get.
- Verification checks:
  - `ros2 param list <node_name>`
  - `ros2 param describe <node_name> <parameter>`
  - `ros2 param get <node_name> <parameter>`
  - `ros2 launch <package> <launch_file> --show-args`

#### Confirming Evidence
- No direct evidence captured.

#### Supporting Context
- `cases/ros2_sim_time_mismatch/config/slam.yaml:2` [context:ros__parameters] ros__parameters:

