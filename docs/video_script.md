# Five-Minute Demo Script

## 0:00-0:35 Problem

ROS debugging is rarely solved by the first error line. A missing topic, launch failure, or TF timeout can depend on logs, package manifests, launch files, parameters, environment variables, and command output. The intended user is a robotics engineer who needs a diagnosis they can verify, not a confident guess.

## 0:35-1:10 Baseline

Show the baseline result from `reports/evaluation.md`: a simple first-error mapper gets 5 of 10 cases correct. Explain that this represents a common workflow: look at the most visible error and jump to a likely cause.

## 1:10-2:30 Live Run

Run:

```bash
cd /Users/ALAMSM/Documents/Project/ros-doctor
PYTHONPATH=src python3 -m ros_doctor.cli diagnose cases/ros2_missing_executable
```

Point out the agent loop:

- Evidence files collected.
- ROS version inferred.
- Candidate hypotheses generated.
- Confirming/supporting evidence gathered.
- Weak candidates rejected.
- Final hypotheses ranked.

Show that the launch file asks for `serial_driver_node`, while `setup.py` installs `serial_node`.

## 2:30-3:20 Evidence-Backed Fix

Explain the recommended fix: add the correct console script or update the launch executable, rebuild with `colcon build --symlink-install`, source the workspace, then verify with `ros2 pkg executables robot_driver`.

## 3:20-4:15 Evaluation

Run:

```bash
PYTHONPATH=src python3 -m ros_doctor.evaluate cases --write-diagnoses
```

Show:

- 10 cases.
- Baseline accuracy: 0.50.
- ROS Doctor accuracy: 1.00.
- Average evidence count: 7.40 for the top diagnosis.

## 4:15-4:45 Removed/Changed Experiment

Mention that the environment-sourcing rule was initially too eager because it treated environment variables as direct confirmation. That caused a plausible-but-wrong ranking on a missing dependency case. The fix was to treat variables like `AMENT_PREFIX_PATH` and `ROS_PACKAGE_PATH` as context unless paired with package discovery failure.

## 4:45-5:00 Hot Take

The practical lesson: reliable agentic debugging is not about sounding smart from an error message. It is about forcing the agent to connect every claim to observable evidence and tell the engineer exactly how to verify or falsify the diagnosis.
