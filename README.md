# ROS Doctor

ROS Doctor is an evidence-driven agent that diagnoses ROS failures by generating competing root-cause hypotheses, using tools to gather evidence, and attempting to disprove its own leading diagnosis before recommending a fix.

## Intended User

ROS Doctor is for robotics engineers, lab teams, students, and field operators who need to debug ROS systems under time pressure. Their bottleneck is evidence correlation: a launch failure, missing topic, TF timeout, or package error may require checking logs, launch files, package manifests, environment variables, topic lists, and command transcripts before the real cause is clear.

## What It Does

- Scans a case folder containing logs, ROS command output, launch/config files, and package manifests.
- Infers whether the case is ROS1, ROS2, or unknown.
- Uses a real LLM agent wrapper when `OPENAI_API_KEY` is set.
- Uses deterministic rules as verification tools, not as the agent itself.
- Collects confirming, supporting, and refuting evidence with file and line references.
- Recommends fix steps and verification commands.
- Evaluates the final system against a one-shot general LLM baseline when an API key is available.
- Records tool-call trajectories for every evaluated case.

## Quick Start

```bash
cd /Users/ALAMSM/Documents/Project/ros-doctor
PYTHONPATH=src python3 -m ros_doctor.cli diagnose cases/ros2_missing_dependency
```

Run the tool-using agent in offline verification mode:

```bash
PYTHONPATH=src python3 -m ros_doctor.cli agent-diagnose cases/ros2_qos_mismatch --offline --trajectory-output reports/trajectories/ros2_qos_mismatch.trajectory.json
```

Run the real LLM agent:

```bash
export OPENAI_API_KEY=...
PYTHONPATH=src python3 -m ros_doctor.cli agent-diagnose cases/ros2_qos_mismatch --trajectory-output reports/trajectories/ros2_qos_mismatch.llm.trajectory.json
```

Run the one-shot general LLM baseline:

```bash
export OPENAI_API_KEY=...
PYTHONPATH=src python3 -m ros_doctor.cli llm-baseline cases/ros2_qos_mismatch --output reports/llm-baselines/ros2_qos_mismatch.json
```

Run the 10-case evaluation without external LLM calls:

```bash
PYTHONPATH=src python3 -m ros_doctor.evaluate cases --baseline-mode none --agent-mode offline --write-diagnoses
```

Run the 10-case evaluation with the one-shot LLM baseline and LLM agent:

```bash
export OPENAI_API_KEY=...
PYTHONPATH=src python3 -m ros_doctor.evaluate cases --baseline-mode one-shot-llm --agent-mode llm --write-diagnoses
```

Run tests without third-party dependencies:

```bash
python3 tests/run_tests.py
```

## Case Folder Format

Create a folder with any combination of:

- `*.log`, `*.txt`, `*.yaml`, `*.launch`, `*.py`, `*.xml`
- `package.xml`
- `CMakeLists.txt`
- command transcripts such as `ros2_topic_list.txt`, `ros2doctor.txt`, `roswtf.txt`, or `env.txt`

For benchmark cases, add `gold.json`:

```json
{
  "expected_rule": "ros2_namespace_or_topic_mismatch",
  "root_cause": "Subscriber and publisher topic names do not resolve to the same fully qualified name."
}
```

## Four Major Changes

1. Added a real tool-using LLM agent around the existing engine.
2. Converted deterministic rules into explicit verification tools.
3. Replaced the intentionally weak first-error baseline with a one-shot general LLM baseline.
4. Reran 10 evaluation cases and wrote per-case tool trajectories.

## Baseline And Evaluation

The baseline is now a one-shot general LLM prompt. It receives the same case evidence as ROS Doctor but does not call verification tools and does not attempt to disprove its own leading diagnosis.

The checked-in evaluation was rerun in offline agent mode because this environment did not have `OPENAI_API_KEY`. That run still executes the same deterministic verification tools and records trajectories, but skips the LLM proposal/synthesis calls.

Current checked-in evaluation across 10 reproducible cases:

| Metric | One-Shot LLM Baseline | ROS Doctor Offline Agent | Notes |
| --- | ---: | ---: | --- |
| Top diagnosis accuracy | not run | 1.00 | LLM run requires `OPENAI_API_KEY`. |
| Evidence attached to top diagnosis | not run | 8.10 avg | From verification tool trajectories. |

See `reports/evaluation.md` after running the benchmark.

Included failure families:

- ROS1 workspace not sourced.
- ROS2 missing runtime dependency.
- ROS2 missing executable entry point.
- ROS2 namespace/topic mismatch.
- ROS2 DDS domain or network mismatch.
- TF missing frame.
- Simulation time without `/clock`.
- Parameter type/name mismatch.
- URDF/xacro parse failure.
- QoS policy mismatch.

## Improvement Changelog

| Stage | What changed and why | Evidence | Decision |
| --- | --- | --- | --- |
| Baseline | One-shot general LLM prompt reads the same evidence bundle but cannot call tools. | Implemented in `src/ros_doctor/llm_baseline.py`; requires `OPENAI_API_KEY` for live runs. | Kept as the fair comparison baseline. |
| Iteration 1 | Added evidence collection across logs, environment dumps, launch files, source snippets, and package manifests. | Reports include file and line references for each hypothesis. | Kept because it makes diagnoses auditable. |
| Iteration 2 | Added ROS-version inference to avoid ranking ROS1-only failures against ROS2-only rules. | ROS1 case ranks workspace sourcing above ROS2-specific categories. | Kept. |
| Iteration 3 | Tuned rule scoring so environment variables are context, not confirmation by themselves. | Missing-dependency case ranks dependency cause above unsourced workspace. | Kept because it reduces plausible-but-wrong diagnoses. |
| Iteration 4 | Expanded the rule library to cover parameters, executable entry points, URDF/xacro, QoS, DDS, TF, and simulation time. | Benchmark grew from 3 to 10 cases while preserving top-ranked accuracy. | Kept because it makes the system credible across common ROS failure modes. |
| Iteration 5 | Wrapped the verifier tools with an LLM-driven agent flow: propose competing hypotheses, run tools, attempt disproof, synthesize diagnosis. | `agent-diagnose` command writes a Markdown report and JSON trajectory. | Kept because it separates agent reasoning from deterministic verification. |
| Final | Replaced the weak baseline with one-shot LLM baseline support and reran 10 cases in offline tool-agent mode. | `python3 tests/run_tests.py` passes and benchmark reports 1.00 ROS Doctor accuracy on 10 included cases. | Ready for keyed LLM baseline run and demo recording. |

## Main Failure Mode and Hot Take

The main failure mode is incomplete evidence. If the case folder only contains a single vague error line, ROS Doctor can still rank a plausible hypothesis, but the confidence should remain low and the report should ask for more artifacts.

Hot take: agentic debugging becomes useful when the agent is forced to disprove its own first answer. In ROS, the visible error is often just the symptom. The winning behavior is not sounding confident; it is tying each diagnosis to observable system evidence and giving the engineer the next verification command.

## Reproducibility Notes

- Python: 3.10 or newer.
- Runtime dependencies: none for offline verification.
- LLM runtime: set `OPENAI_API_KEY`; uses the OpenAI Responses API over HTTPS.
- Optional test dependency: `pytest`, though `tests/run_tests.py` uses only the standard library.
- Approximate runtime: less than one second for the included cases.
- Approximate cost: zero for offline mode; live LLM mode depends on the selected model and token usage.

## Submission Checklist

- Complete solution code: included under `src/ros_doctor`.
- LLM agent: included in `src/ros_doctor/agent.py`.
- Verification tools: included in `src/ros_doctor/verifier_tools.py`.
- One-shot LLM baseline: included in `src/ros_doctor/llm_baseline.py`.
- Evaluation: 10 gold-labeled cases under `cases`.
- Reproduction guide: included in this README.
- Improvement changelog: included in this README.
- Agent trajectories: generated under `reports/trajectories`.
- Video plan: included in `docs/video_script.md`.
- Private data: none; all cases are synthetic.

## Agent Trajectories

Representative trajectories for this prototype are documented in `docs/agent_trajectories.md`. A concise solution video outline is in `docs/video_script.md`.
