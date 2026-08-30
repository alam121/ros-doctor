# ROS Doctor Evaluation

- Cases: `10`
- Baseline mode: `none`
- Agent mode: `offline`
- ROS Doctor accuracy: `1.0`
- Average top-hypothesis evidence count: `8.1`
- Baseline accuracy: `not run`

| Case | Expected | Baseline | ROS Doctor | Evidence |
| --- | --- | --- | --- | ---: |
| ros1_not_sourced | workspace_not_sourced | not run | OK `workspace_not_sourced` | 7 |
| ros2_bad_parameter | ros2_parameter_type_or_name_mismatch | not run | OK `ros2_parameter_type_or_name_mismatch` | 7 |
| ros2_dds_domain_mismatch | ros2_dds_domain_or_network_mismatch | not run | OK `ros2_dds_domain_or_network_mismatch` | 16 |
| ros2_missing_dependency | ros2_missing_runtime_dependency | not run | OK `ros2_missing_runtime_dependency` | 7 |
| ros2_missing_executable | ros2_missing_executable_entrypoint | not run | OK `ros2_missing_executable_entrypoint` | 6 |
| ros2_namespace_mismatch | ros2_namespace_or_topic_mismatch | not run | OK `ros2_namespace_or_topic_mismatch` | 6 |
| ros2_qos_mismatch | ros2_qos_policy_mismatch | not run | OK `ros2_qos_policy_mismatch` | 8 |
| ros2_sim_time_mismatch | tf_frame_or_clock_failure | not run | OK `tf_frame_or_clock_failure` | 7 |
| ros2_tf_missing_frame | tf_frame_or_clock_failure | not run | OK `tf_frame_or_clock_failure` | 10 |
| ros2_urdf_xacro_failure | urdf_or_xacro_parse_failure | not run | OK `urdf_or_xacro_parse_failure` | 7 |
