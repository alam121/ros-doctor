# ROS Doctor

ROS Doctor is an agentic debugging system for ROS and ROS2 failures. It diagnoses failures by generating root-cause hypotheses and verifying them against logs, configuration, command output, and repository evidence instead of guessing from one error message.

## Intended User

ROS Doctor is for robotics engineers, lab teams, students, and field operators who need to debug ROS systems under time pressure. Their bottleneck is evidence correlation: a launch failure, missing topic, TF timeout, or package error may require checking logs, launch files, package manifests, environment variables, topic lists, and command transcripts before the real cause is clear.

## What It Does

- Scans a case folder containing logs, ROS command output, launch/config files, and package manifests.
- Infers whether the case is ROS1, ROS2, or unknown.
- Generates ranked root-cause hypotheses from a ruleset.
- Collects confirming, supporting, and refuting evidence with file and line references.
- Recommends fix steps and verification commands.
- Evaluates the final system against a simple baseline on reproducible cases.
- Includes an explicit agent verification loop in every report.

## Quick Start

```bash
cd /Users/ALAMSM/Documents/Project/ros-doctor
PYTHONPATH=src python3 -m ros_doctor.cli diagnose cases/ros2_missing_dependency
```

Write a report:

```bash
PYTHONPATH=src python3 -m ros_doctor.cli diagnose cases/ros2_namespace_mismatch --output reports/example.md
```

Run the benchmark:

```bash
PYTHONPATH=src python3 -m ros_doctor.evaluate cases --write-diagnoses
```

Run tests without third-party dependencies:

```bash
python3 tests/run_tests.py
```

If you prefer an installed CLI:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
ros-doctor diagnose cases/ros2_missing_dependency
ros-doctor-eval cases --write-diagnoses
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

## Baseline

The included baseline simulates a reasonable basic approach: inspect the first relevant error-like line and map it directly to a likely category. This is intentionally simple and brittle. ROS Doctor improves on it by checking multiple evidence sources before ranking the diagnosis.

Current benchmark result across 10 reproducible cases:

| Metric | Simple Baseline | ROS Doctor | Change |
| --- | ---: | ---: | ---: |
| Top diagnosis accuracy | 0.50 | 1.00 | +0.50 |
| Evidence attached to top diagnosis | 0 | 7.50 avg | +7.50 |

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
| Baseline | First-error mapping from log text to root-cause category. | Correct on simple missing dependency and namespace cases, wrong on ROS1 unsourced workspace. | Kept as the comparison baseline. |
| Iteration 1 | Added evidence collection across logs, environment dumps, launch files, source snippets, and package manifests. | Reports include file and line references for each hypothesis. | Kept because it makes diagnoses auditable. |
| Iteration 2 | Added ROS-version inference to avoid ranking ROS1-only failures against ROS2-only rules. | ROS1 case ranks workspace sourcing above ROS2-specific categories. | Kept. |
| Iteration 3 | Tuned rule scoring so environment variables are context, not confirmation by themselves. | Missing-dependency case ranks dependency cause above unsourced workspace. | Kept because it reduces plausible-but-wrong diagnoses. |
| Iteration 4 | Expanded the rule library to cover parameters, executable entry points, URDF/xacro, QoS, DDS, TF, and simulation time. | Benchmark grew from 3 to 10 cases while preserving top-ranked accuracy. | Kept because it makes the system credible across common ROS failure modes. |
| Iteration 5 | Added an explicit agent verification loop to reports. | Diagnosis reports now show collection, version inference, hypothesis generation, verification, rejection, and ranking steps. | Kept because judges can inspect the agent trajectory instead of only the output. |
| Final | Combined hypothesis generation, evidence verification, Markdown/JSON reporting, trajectories, and benchmark evaluation. | `python3 tests/run_tests.py` passes and benchmark reports 1.00 ROS Doctor accuracy on 10 included cases. | Ready for demo and submission packaging. |

## Main Failure Mode and Hot Take

The main failure mode is incomplete evidence. If the case folder only contains a single vague error line, ROS Doctor can still rank a plausible hypothesis, but the confidence should remain low and the report should ask for more artifacts.

Hot take: agentic debugging becomes useful when the agent is forced to disprove its own first answer. In ROS, the visible error is often just the symptom. The winning behavior is not sounding confident; it is tying each diagnosis to observable system evidence and giving the engineer the next verification command.

## Reproducibility Notes

- Python: 3.10 or newer.
- Runtime dependencies: none for the core tool.
- Optional test dependency: `pytest`, though `tests/run_tests.py` uses only the standard library.
- Approximate runtime: less than one second for the included cases.
- Approximate cost: zero for the deterministic local version.

## Submission Checklist

- Complete solution code: included under `src/ros_doctor`.
- Baseline: included in `src/ros_doctor/evaluate.py`.
- Evaluation: 10 gold-labeled cases under `cases`.
- Reproduction guide: included in this README.
- Improvement changelog: included in this README.
- Agent trajectories: included in `docs/agent_trajectories.md` and diagnosis reports.
- Video plan: included in `docs/video_script.md`.
- Private data: none; all cases are synthetic.

## Agent Trajectories

Representative trajectories for this prototype are documented in `docs/agent_trajectories.md`. A concise solution video outline is in `docs/video_script.md`.
