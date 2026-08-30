from pathlib import Path

from ros_doctor.diagnoser import diagnose
from ros_doctor.evaluate import evaluate_cases
from ros_doctor.verifier_tools import tool_attempt_to_disprove, tool_verify_hypothesis


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


def test_offline_agent_evaluation_covers_all_cases():
    _, summary = evaluate_cases(ROOT / "cases", baseline_mode="none", agent_mode="offline")

    assert summary["cases"] == 10
    assert summary["baseline_accuracy"] is None
    assert summary["ros_doctor_accuracy"] == 1.0
    assert summary["average_top_evidence_count"] >= 2


def test_all_gold_cases_are_top_ranked():
    results, _ = evaluate_cases(ROOT / "cases", baseline_mode="none", agent_mode="offline")

    assert [item.case for item in results if not item.ros_doctor_correct] == []


def test_rules_are_exposed_as_verification_tools():
    case_path = ROOT / "cases" / "ros2_qos_mismatch"
    verification = tool_verify_hypothesis(case_path, "ros2_qos_policy_mismatch")
    disproof = tool_attempt_to_disprove(case_path, "ros2_qos_policy_mismatch")

    assert verification["score"] > 0
    assert verification["confirming_evidence"]
    assert disproof["decision"] == "keep_leading"
