# Agent Trajectories

ROS Doctor now separates the agent from the verifier.

- The LLM agent proposes competing hypotheses and synthesizes the final answer.
- The deterministic rule engine is exposed as verification tools.
- The agent loop calls those tools, checks alternatives, and attempts to disprove the leading diagnosis before recommending a fix.

The checked-in trajectories under `reports/trajectories/` were generated in offline mode because this environment did not have `OPENAI_API_KEY`. Offline mode uses the same verification tools and disproof step, but skips the LLM proposal and synthesis calls. To record live LLM trajectories, run:

```bash
export OPENAI_API_KEY=...
PYTHONPATH=src python3 -m ros_doctor.evaluate cases --baseline-mode one-shot-llm --agent-mode llm --write-diagnoses
```

## Trajectory Shape

Each trajectory JSON contains:

- `offline_agent_driver` or `llm_agent` proposal step.
- `collect_evidence` tool result.
- `infer_ros_version` tool result.
- `list_candidate_hypotheses` tool result.
- One `verify_hypothesis` tool result per candidate.
- `attempt_to_disprove` tool result for the leading diagnosis.
- Final agent selection or synthesis step.

## Representative Cases

| Case | Top diagnosis | Key evidence used | Main disproof check |
| --- | --- | --- | --- |
| `ros1_not_sourced` | `workspace_not_sourced` | Package exists locally, but `ROS_PACKAGE_PATH` only includes `/opt/ros/noetic/share`. | Compares against `ros1_master_or_uri_mismatch`; master URI exists but no master-contact failure appears. |
| `ros2_missing_dependency` | `ros2_missing_runtime_dependency` | Launch file references `depthimage_to_laserscan`; manifest does not declare it. | Compares against workspace sourcing; environment shows Humble and install prefix are visible. |
| `ros2_missing_executable` | `ros2_missing_executable_entrypoint` | Launch asks for `serial_driver_node`; `setup.py` installs `serial_node`. | Compares against missing package; package metadata exists, executable name is the mismatch. |
| `ros2_namespace_mismatch` | `ros2_namespace_or_topic_mismatch` | Subscriber waits on `/camera/image_raw`; topic list shows `/robot1/camera/image_raw`. | Compares against missing dependency; no package/import failure evidence exists. |
| `ros2_dds_domain_mismatch` | `ros2_dds_domain_or_network_mismatch` | Talker has `ROS_DOMAIN_ID=42`; listener has `ROS_DOMAIN_ID=7`. | Compares against topic mismatch; discovery fails before topic-level matching. |
| `ros2_tf_missing_frame` | `tf_frame_or_clock_failure` | Navigation waits for `base_link` to `map`; frame report says `map` is missing. | Compares against namespace mismatch; evidence is transform/frame-specific. |
| `ros2_sim_time_mismatch` | `tf_frame_or_clock_failure` | `use_sim_time` is true and `/clock` has not published. | Compares against DDS/network issues; node-level clock evidence is stronger. |
| `ros2_bad_parameter` | `ros2_parameter_type_or_name_mismatch` | `scan_rate` is declared numeric but YAML supplies `"10.0"` as a string. | Compares against missing dependency; failure is parameter parsing/type-specific. |
| `ros2_urdf_xacro_failure` | `urdf_or_xacro_parse_failure` | xacro reports mismatched XML tag; file closes `<visual>` with `</collision>`. | Compares against TF; robot description generation fails before TF publication. |
| `ros2_qos_mismatch` | `ros2_qos_policy_mismatch` | Publisher is `BEST_EFFORT`, subscriber requires `RELIABLE`; log reports incompatible reliability. | Compares against topic mismatch; endpoints exist but QoS prevents matching. |
