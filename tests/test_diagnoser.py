from pathlib import Path

from ros_doctor.diagnoser import diagnose
from ros_doctor.evaluate import evaluate_cases


ROOT = Path(__file__).resolve().parents[1]


def test_missing_dependency_case_is_ranked_first():
    diagnosis = diagnose(ROOT / "cases" / "ros2_missing_dependency")

    assert diagnosis.ros_version == "ros2"
    assert diagnosis.hypotheses[0].rule.identifier == "ros2_missing_runtime_dependency"
    assert diagnosis.hypotheses[0].confirming


def test_namespace_mismatch_case_is_ranked_first():
    diagnosis = diagnose(ROOT / "cases" / "ros2_namespace_mismatch")

    assert diagnosis.hypotheses[0].rule.identifier == "ros2_namespace_or_topic_mismatch"
    assert diagnosis.hypotheses[0].score >= 0.45


def test_evaluation_shows_agent_improves_over_baseline():
    _, summary = evaluate_cases(ROOT / "cases")

    assert summary["cases"] == 10
    assert summary["ros_doctor_accuracy"] > summary["baseline_accuracy"]
    assert summary["average_top_evidence_count"] >= 2


def test_all_gold_cases_are_top_ranked():
    results, _ = evaluate_cases(ROOT / "cases")

    assert [item.case for item in results if not item.ros_doctor_correct] == []
