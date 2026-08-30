# ROS Doctor Diagnosis

- Inferred ROS version: `ros2`
- Files scanned: `3`

## Agent Verification Loop

1. Collected 3 readable evidence files from cases/ros2_qos_mismatch.
2. Inferred ROS version as ros2.
3. Generated 9 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 6 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. ROS2 QoS policy mismatch

- Score: `0.92` (high confidence)
- Likely root cause: A publisher and subscriber are on the same topic but use incompatible QoS policies such as reliability, durability, or history depth.
- Recommended fix: Align QoS profiles for the publisher and subscriber, then verify endpoint compatibility with ros2 topic info --verbose.
- Verification checks:
  - `ros2 topic info <topic> --verbose`
  - `ros2 topic echo <topic> --qos-reliability best_effort`
  - `ros2 topic echo <topic> --qos-reliability reliable`
  - `ros2 doctor --report`

#### Confirming Evidence
- `cases/ros2_qos_mismatch/logs/telemetry.log:1` [confirm:incompatible QoS] [WARN] [mission_monitor]: New publisher discovered on /battery_state, offering incompatible QoS. Last incompatible policy: RELIABILITY_QOS_POLICY
- `cases/ros2_qos_mismatch/logs/telemetry.log:1` [confirm:New publisher discovered.*incompatible] [WARN] [mission_monitor]: New publisher discovered on /battery_state, offering incompatible QoS. Last incompatible policy: RELIABILITY_QOS_POLICY
- `cases/ros2_qos_mismatch/logs/telemetry.log:2` [confirm:reliability policy] [WARN] [mission_monitor]: subscription matched zero endpoints because reliability policy differs

#### Supporting Context
- `cases/ros2_qos_mismatch/ros2_topic_info.txt:4` [context:BEST_EFFORT] Publisher reliability: BEST_EFFORT
- `cases/ros2_qos_mismatch/ros2_topic_info.txt:5` [context:RELIABLE] Subscription reliability: RELIABLE
- `cases/ros2_qos_mismatch/src/telemetry/monitor.py:1` [context:QoSProfile] from rclpy.qos import QoSProfile, ReliabilityPolicy
- `cases/ros2_qos_mismatch/src/telemetry/monitor.py:3` [context:QoSProfile] battery_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
- `cases/ros2_qos_mismatch/src/telemetry/monitor.py:3` [context:RELIABLE] battery_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)

### 2. ROS2 topic or namespace mismatch

- Score: `0.08` (low confidence)
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
- `cases/ros2_qos_mismatch/ros2_topic_info.txt:1` [context:topic] Topic: /battery_state
- `cases/ros2_qos_mismatch/src/telemetry/monitor.py:4` [context:create_subscription] node.create_subscription(BatteryState, "/battery_state", cb, battery_qos)

### 3. ROS2 package dependency is missing or not declared

- Score: `0.04` (low confidence)
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
- `cases/ros2_qos_mismatch/src/telemetry/monitor.py:1` [context:import ] from rclpy.qos import QoSProfile, ReliabilityPolicy

