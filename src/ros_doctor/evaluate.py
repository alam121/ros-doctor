from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .collector import collect_corpus
from .diagnoser import diagnose
from .report import render_markdown
from .rules import RULES


@dataclass(frozen=True)
class CaseResult:
    case: str
    expected: str
    baseline: str
    ros_doctor: str
    baseline_correct: bool
    ros_doctor_correct: bool
    evidence_count: int


def evaluate_cases(cases_dir: Path) -> tuple[list[CaseResult], dict]:
    results = []
    for manifest in sorted(cases_dir.glob("*/gold.json")):
        case_dir = manifest.parent
        gold = json.loads(manifest.read_text())
        expected = gold["expected_rule"]
        baseline = baseline_guess(case_dir)
        diagnosis = diagnose(case_dir)
        top = diagnosis.hypotheses[0] if diagnosis.hypotheses else None
        ros_doctor = top.rule.identifier if top else "no_hypothesis"
        evidence_count = len(top.confirming) + len(top.context) if top else 0
        results.append(
            CaseResult(
                case=case_dir.name,
                expected=expected,
                baseline=baseline,
                ros_doctor=ros_doctor,
                baseline_correct=baseline == expected,
                ros_doctor_correct=ros_doctor == expected,
                evidence_count=evidence_count,
            )
        )

    total = len(results)
    summary = {
        "cases": total,
        "baseline_accuracy": _accuracy(item.baseline_correct for item in results),
        "ros_doctor_accuracy": _accuracy(item.ros_doctor_correct for item in results),
        "average_top_evidence_count": round(
            sum(item.evidence_count for item in results) / total, 2
        )
        if total
        else 0,
    }
    return results, summary


def baseline_guess(case_dir: Path) -> str:
    """Simulate a brittle error-message-only baseline using the first matching log line."""
    corpus = collect_corpus(case_dir)
    for _, _, line in corpus.lines():
        lowered = line.lower()
        if "package" in lowered and "not found" in lowered:
            return "ros2_missing_runtime_dependency"
        if "transform" in lowered:
            return "tf_frame_or_clock_failure"
        if "ros_master_uri" in lowered or "master" in lowered:
            return "ros1_master_or_uri_mismatch"
        if "domain" in lowered or "multicast" in lowered:
            return "ros2_dds_domain_or_network_mismatch"
        if "waiting for message" in lowered:
            return "ros2_namespace_or_topic_mismatch"
    return "no_hypothesis"


def render_evaluation(results: list[CaseResult], summary: dict) -> str:
    lines = [
        "# ROS Doctor Evaluation",
        "",
        f"- Cases: `{summary['cases']}`",
        f"- Baseline accuracy: `{summary['baseline_accuracy']}`",
        f"- ROS Doctor accuracy: `{summary['ros_doctor_accuracy']}`",
        f"- Average top-hypothesis evidence count: `{summary['average_top_evidence_count']}`",
        "",
        "| Case | Expected | Baseline | ROS Doctor | Evidence |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for item in results:
        lines.append(
            f"| {item.case} | {item.expected} | {_mark(item.baseline, item.baseline_correct)} | "
            f"{_mark(item.ros_doctor, item.ros_doctor_correct)} | {item.evidence_count} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate ROS Doctor against gold cases.")
    parser.add_argument("cases_dir", type=Path, nargs="?", default=Path("cases"))
    parser.add_argument("--output", type=Path, default=Path("reports/evaluation.md"))
    parser.add_argument("--write-diagnoses", action="store_true")
    args = parser.parse_args(argv)

    results, summary = evaluate_cases(args.cases_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_evaluation(results, summary))

    if args.write_diagnoses:
        for case_dir in sorted(args.cases_dir.glob("*")):
            if case_dir.is_dir() and (case_dir / "gold.json").exists():
                report_path = args.output.parent / f"{case_dir.name}.diagnosis.md"
                report_path.write_text(render_markdown(diagnose(case_dir)))
    print(args.output)
    return 0


def _accuracy(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _mark(value: str, correct: bool) -> str:
    return f"{'OK' if correct else 'MISS'} `{value}`"


if __name__ == "__main__":
    raise SystemExit(main())
