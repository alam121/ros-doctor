from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ros_doctor.diagnoser import diagnose
from ros_doctor.evaluate import evaluate_cases


def test_missing_dependency_case_is_ranked_first() -> None:
    diagnosis = diagnose(ROOT / "cases" / "ros2_missing_dependency")
    assert diagnosis.ros_version == "ros2"
    assert diagnosis.hypotheses[0].rule.identifier == "ros2_missing_runtime_dependency"
    assert diagnosis.hypotheses[0].confirming


def test_namespace_mismatch_case_is_ranked_first() -> None:
    diagnosis = diagnose(ROOT / "cases" / "ros2_namespace_mismatch")
    assert diagnosis.hypotheses[0].rule.identifier == "ros2_namespace_or_topic_mismatch"
    assert diagnosis.hypotheses[0].score >= 0.45


def test_evaluation_shows_agent_improves_over_baseline() -> None:
    _, summary = evaluate_cases(ROOT / "cases")
    assert summary["cases"] == 10
    assert summary["ros_doctor_accuracy"] > summary["baseline_accuracy"]
    assert summary["average_top_evidence_count"] >= 2


def test_all_gold_cases_are_top_ranked() -> None:
    results, _ = evaluate_cases(ROOT / "cases")
    misses = [item for item in results if not item.ros_doctor_correct]
    assert misses == []


def main() -> int:
    tests = [
        test_missing_dependency_case_is_ranked_first,
        test_namespace_mismatch_case_is_ranked_first,
        test_evaluation_shows_agent_improves_over_baseline,
        test_all_gold_cases_are_top_ranked,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
