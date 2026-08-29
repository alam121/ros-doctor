# ROS Doctor Diagnosis

- Inferred ROS version: `unknown`
- Files scanned: `4`

## Agent Verification Loop

1. Collected 4 readable evidence files from cases/ros2_dds_domain_mismatch.
2. Inferred ROS version as unknown.
3. Generated 10 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 8 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. ROS2 DDS domain or network discovery mismatch

- Score: `0.96` (high confidence)
- Likely root cause: ROS2 nodes are running but cannot discover each other because ROS_DOMAIN_ID, RMW implementation, host networking, or multicast settings differ.
- Recommended fix: Align ROS_DOMAIN_ID and RMW_IMPLEMENTATION across processes, confirm multicast or container networking, and repeat topic discovery.
- Verification checks:
  - `echo $ROS_DOMAIN_ID`
  - `echo $RMW_IMPLEMENTATION`
  - `ros2 doctor --report`
  - `ros2 multicast receive`

#### Confirming Evidence
- `cases/ros2_dds_domain_mismatch/env_listener.txt:2` [confirm:ROS_DOMAIN_ID] ROS_DOMAIN_ID=7
- `cases/ros2_dds_domain_mismatch/env_listener.txt:3` [confirm:RMW_IMPLEMENTATION] RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
- `cases/ros2_dds_domain_mismatch/env_talker.txt:2` [confirm:ROS_DOMAIN_ID] ROS_DOMAIN_ID=42
- `cases/ros2_dds_domain_mismatch/env_talker.txt:3` [confirm:RMW_IMPLEMENTATION] RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
- `cases/ros2_dds_domain_mismatch/logs/discovery.log:2` [confirm:no nodes discovered] [WARN] [listener]: no nodes discovered after startup
- `cases/ros2_dds_domain_mismatch/logs/discovery.log:3` [confirm:ROS_DOMAIN_ID] [WARN] [rmw_cyclonedds_cpp]: participant discovery timed out; check ROS_DOMAIN_ID and multicast reachability

#### Supporting Context
- `cases/ros2_dds_domain_mismatch/config/docker-compose.yaml:4` [context:network_mode] network_mode: bridge
- `cases/ros2_dds_domain_mismatch/config/docker-compose.yaml:7` [context:network_mode] network_mode: bridge
- `cases/ros2_dds_domain_mismatch/env_listener.txt:2` [context:domain] ROS_DOMAIN_ID=7
- `cases/ros2_dds_domain_mismatch/env_listener.txt:3` [context:CYCLONEDDS] RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
- `cases/ros2_dds_domain_mismatch/env_talker.txt:2` [context:domain] ROS_DOMAIN_ID=42
- `cases/ros2_dds_domain_mismatch/env_talker.txt:3` [context:CYCLONEDDS] RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

### 2. Workspace or ROS environment was not sourced

- Score: `0.08` (low confidence)
- Likely root cause: The shell environment cannot see ROS packages because setup.bash/local_setup.bash was not sourced, or ROS_PACKAGE_PATH/AMENT_PREFIX_PATH points at the wrong workspace.
- Recommended fix: Source the correct ROS distribution and workspace setup file in the active shell, then rerun package discovery before launching.
- Verification checks:
  - `echo $ROS_DISTRO`
  - `echo $AMENT_PREFIX_PATH`
  - `echo $ROS_PACKAGE_PATH`
  - `source /opt/ros/<distro>/setup.bash && source install/setup.bash`

#### Confirming Evidence
- No direct evidence captured.

#### Supporting Context
- `cases/ros2_dds_domain_mismatch/env_listener.txt:1` [context:ROS_DISTRO=] ROS_DISTRO=humble
- `cases/ros2_dds_domain_mismatch/env_talker.txt:1` [context:ROS_DISTRO=] ROS_DISTRO=humble

