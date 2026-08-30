# ROS Doctor Diagnosis

- Inferred ROS version: `ros1`
- Files scanned: `3`

## Agent Verification Loop

1. Collected 3 readable evidence files from cases/ros1_not_sourced.
2. Inferred ROS version as ros1.
3. Generated 4 candidate root-cause hypotheses from the rule library.
4. Verified candidates against confirming, supporting, and refuting evidence.
5. Rejected 2 candidates with no supporting evidence.
6. Ranked remaining hypotheses by evidence strength and contradiction penalties.

## Ranked Hypotheses

### 1. Workspace or ROS environment was not sourced

- Score: `0.88` (high confidence)
- Likely root cause: The shell environment cannot see ROS packages because setup.bash/local_setup.bash was not sourced, or ROS_PACKAGE_PATH/AMENT_PREFIX_PATH points at the wrong workspace.
- Recommended fix: Source the correct ROS distribution and workspace setup file in the active shell, then rerun package discovery before launching.
- Verification checks:
  - `echo $ROS_DISTRO`
  - `echo $AMENT_PREFIX_PATH`
  - `echo $ROS_PACKAGE_PATH`
  - `source /opt/ros/<distro>/setup.bash && source install/setup.bash`

#### Confirming Evidence
- `cases/ros1_not_sourced/logs/roslaunch.log:1` [confirm:Resource not found] [roslaunch][ERROR] Resource not found: turtlebot3_bringup
- `cases/ros1_not_sourced/logs/roslaunch.log:3` [confirm:package .* not found] [rospack] Error: package 'turtlebot3_bringup' not found
- `cases/ros1_not_sourced/logs/roslaunch.log:3` [confirm:rospack.*Error] [rospack] Error: package 'turtlebot3_bringup' not found

#### Supporting Context
- `cases/ros1_not_sourced/env.txt:1` [context:ROS_DISTRO=] ROS_DISTRO=noetic
- `cases/ros1_not_sourced/env.txt:3` [context:ROS_PACKAGE_PATH=] ROS_PACKAGE_PATH=/opt/ros/noetic/share
- `cases/ros1_not_sourced/env.txt:4` [context:setup.bash] # Expected workspace path /home/dev/catkin_ws/src is absent because devel/setup.bash was not sourced.
- `cases/ros1_not_sourced/env.txt:4` [context:devel/setup.bash] # Expected workspace path /home/dev/catkin_ws/src is absent because devel/setup.bash was not sourced.

### 2. ROS1 master URI or hostname mismatch

- Score: `0.64` (medium confidence)
- Likely root cause: ROS1 nodes cannot register or communicate because ROS_MASTER_URI, ROS_HOSTNAME, or ROS_IP is unset or points to the wrong host.
- Recommended fix: Start roscore if needed, align ROS_MASTER_URI and ROS_IP/ROS_HOSTNAME for every machine, and verify name resolution.
- Verification checks:
  - `echo $ROS_MASTER_URI`
  - `echo $ROS_IP`
  - `rosnode list`
  - `rostopic list`

#### Confirming Evidence
- `cases/ros1_not_sourced/env.txt:2` [confirm:ROS_MASTER_URI] ROS_MASTER_URI=http://localhost:11311
- `cases/ros1_not_sourced/logs/roslaunch.log:2` [confirm:ROS_MASTER_URI] [roslaunch][INFO] ROS_MASTER_URI=http://localhost:11311

#### Supporting Context
- `cases/ros1_not_sourced/env.txt:2` [context:localhost] ROS_MASTER_URI=http://localhost:11311
- `cases/ros1_not_sourced/env.txt:2` [context:master] ROS_MASTER_URI=http://localhost:11311
- `cases/ros1_not_sourced/logs/roslaunch.log:2` [context:localhost] [roslaunch][INFO] ROS_MASTER_URI=http://localhost:11311
- `cases/ros1_not_sourced/logs/roslaunch.log:2` [context:master] [roslaunch][INFO] ROS_MASTER_URI=http://localhost:11311

