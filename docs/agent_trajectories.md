# Agent Trajectories

These are representative trajectories for the current deterministic agent loop. They are written so judges can see the instruction, tool-like observations, retries, and final decision path.

## Trajectory 1: Missing ROS2 Dependency

Agent instruction:

> Diagnose the failure using logs, repository files, and environment evidence. Generate hypotheses, verify them against the evidence, and rank only supported causes.

Observations:

- `logs/launch.log` reports `package 'depthimage_to_laserscan' not found`.
- `launch/bringup.launch.py` references `package="depthimage_to_laserscan"`.
- `package.xml` declares `nav2_bringup` and `slam_toolbox`, but not `depthimage_to_laserscan`.
- `env.txt` shows the Humble environment and workspace are visible.

Hypotheses considered:

- Missing runtime dependency.
- Workspace not sourced.

Verification:

- Missing dependency is confirmed by launch log plus launch file reference plus absent manifest dependency.
- Workspace sourcing is plausible but less supported because the workspace and ROS distribution are present.

Final decision:

- Top diagnosis: `ros2_missing_runtime_dependency`.
- Suggested checks: `rosdep install`, `colcon build`, `source install/setup.bash`, `ros2 pkg prefix depthimage_to_laserscan`.

## Trajectory 2: ROS2 Namespace Mismatch

Agent instruction:

> Diagnose why a perception node never receives images. Compare runtime logs with topic discovery and launch/source configuration.

Observations:

- Runtime log says the node waits on `/camera/image_raw`.
- Runtime log says there are no publishers for that requested input.
- `ros2_topic_list.txt` shows `/robot1/camera/image_raw`.
- Launch file sets `namespace="robot1"` but also remaps `image_raw` to absolute `/camera/image_raw`.

Hypotheses considered:

- Topic or namespace mismatch.
- Missing package.
- TF failure.

Verification:

- Topic mismatch is confirmed by requested topic and discovered topic differing by namespace.
- Missing package has only generic Python import context and no failure evidence.
- TF has no transform-specific confirmation.

Final decision:

- Top diagnosis: `ros2_namespace_or_topic_mismatch`.
- Suggested checks: `ros2 topic list -t`, `ros2 node info <node_name>`, and a one-message echo on the expected topic.

## Trajectory 3: ROS1 Workspace Not Sourced

Agent instruction:

> Diagnose a ROS1 launch failure using logs, environment output, and repository evidence. Do not assume the package is absent until checking the workspace.

Observations:

- `roslaunch.log` says `Resource not found: turtlebot3_bringup`.
- `rospack` says the package was not found.
- `src/turtlebot3_bringup/package.xml` proves the package exists in the repository.
- `env.txt` shows `ROS_PACKAGE_PATH=/opt/ros/noetic/share`, with the expected catkin workspace absent.

Hypotheses considered:

- Workspace not sourced.
- ROS1 master URI mismatch.

Verification:

- Workspace not sourced is confirmed by package discovery failure plus the package existing locally plus missing workspace path.
- Master URI evidence exists, but the log does not show failed master contact.

Final decision:

- Top diagnosis: `workspace_not_sourced`.
- Suggested checks: `echo $ROS_PACKAGE_PATH`, `source /opt/ros/noetic/setup.bash`, `source devel/setup.bash`, and `rospack find turtlebot3_bringup`.

## Additional Benchmark Trajectories

| Case | Top diagnosis | Key evidence used | Main verification command |
| --- | --- | --- | --- |
| `ros2_dds_domain_mismatch` | `ros2_dds_domain_or_network_mismatch` | Talker has `ROS_DOMAIN_ID=42`, listener has `ROS_DOMAIN_ID=7`, discovery log reports no nodes discovered. | `echo $ROS_DOMAIN_ID` in both shells. |
| `ros2_tf_missing_frame` | `tf_frame_or_clock_failure` | Navigation waits for `base_link` to `map`; frame report says `map` is missing. | `ros2 run tf2_tools view_frames`. |
| `ros2_sim_time_mismatch` | `tf_frame_or_clock_failure` | `use_sim_time` is true and `/clock` has not published. | `ros2 topic echo /clock --once`. |
| `ros2_bad_parameter` | `ros2_parameter_type_or_name_mismatch` | Log expects `scan_rate` as double but YAML supplies `"10.0"` as a string. | `ros2 param describe <node_name> scan_rate`. |
| `ros2_missing_executable` | `ros2_missing_executable_entrypoint` | Launch asks for `serial_driver_node`, while `setup.py` installs `serial_node`. | `ros2 pkg executables robot_driver`. |
| `ros2_urdf_xacro_failure` | `urdf_or_xacro_parse_failure` | xacro reports a mismatched XML tag; file closes `<visual>` with `</collision>`. | `xacro urdf/robot.urdf.xacro`. |
| `ros2_qos_mismatch` | `ros2_qos_policy_mismatch` | Topic info shows publisher `BEST_EFFORT`, subscriber `RELIABLE`; log reports incompatible reliability. | `ros2 topic info /battery_state --verbose`. |
