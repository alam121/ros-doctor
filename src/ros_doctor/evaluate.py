from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .agent import run_agent, write_agent_outputs
from .llm import LLMUnavailable
from .llm_baseline import run_one_shot_llm_baseline


@dataclass(frozen=True)
class CaseResult:
    case: str
    expected: str
    baseline: str | None
    baseline_mode: str
    ros_doctor: str
    baseline_correct: bool
    ros_doctor_correct: bool
    evidence_count: int


def evaluate_cases(
    cases_dir: Path,
    baseline_mode: str = "none",
    agent_mode: str = "offline",
    model: str | None = None,
    write_diagnoses: bool = False,
    reports_dir: Path | None = None,
) -> tuple[list[CaseResult], dict]:
    results = []
    for manifest in sorted(cases_dir.glob("*/gold.json")):
        case_dir = manifest.parent
        gold = json.loads(manifest.read_text())
        expected = gold["expected_rule"]
        baseline = _run_baseline(case_dir, baseline_mode, model)
        agent_run = run_agent(case_dir, model=model, offline=agent_mode == "offline")
        ros_doctor = agent_run.predicted_rule
        evidence_count = _top_evidence_count(agent_run.trajectory)
        if write_diagnoses and reports_dir:
            write_agent_outputs(
                agent_run,
                reports_dir / f"{case_dir.name}.agent.md",
                reports_dir / "trajectories" / f"{case_dir.name}.trajectory.json",
            )
        results.append(
            CaseResult(
                case=case_dir.name,
                expected=expected,
                baseline=baseline,
                baseline_mode=baseline_mode,
                ros_doctor=ros_doctor,
                baseline_correct=baseline == expected if baseline is not None else False,
                ros_doctor_correct=ros_doctor == expected,
                evidence_count=evidence_count,
            )
        )

    total = len(results)
    summary = {
        "cases": total,
        "baseline_mode": baseline_mode,
        "agent_mode": agent_mode,
        "baseline_accuracy": _accuracy(item.baseline_correct for item in results)
        if baseline_mode != "none"
        else None,
        "ros_doctor_accuracy": _accuracy(item.ros_doctor_correct for item in results),
        "average_top_evidence_count": round(
            sum(item.evidence_count for item in results) / total, 2
        )
        if total
        else 0,
    }
    return results, summary


def render_evaluation(results: list[CaseResult], summary: dict) -> str:
    lines = [
        "# ROS Doctor Evaluation",
        "",
        f"- Cases: `{summary['cases']}`",
        f"- Baseline mode: `{summary['baseline_mode']}`",
        f"- Agent mode: `{summary['agent_mode']}`",
        f"- ROS Doctor accuracy: `{summary['ros_doctor_accuracy']}`",
        f"- Average top-hypothesis evidence count: `{summary['average_top_evidence_count']}`",
    ]
    if summary["baseline_accuracy"] is None:
        lines.append("- Baseline accuracy: `not run`")
    else:
        lines.append(f"- Baseline accuracy: `{summary['baseline_accuracy']}`")
    lines.extend(["", "| Case | Expected | Baseline | ROS Doctor | Evidence |", "| --- | --- | --- | --- | ---: |"])
    for item in results:
        baseline = "not run" if item.baseline is None else _mark(item.baseline, item.baseline_correct)
        lines.append(
            f"| {item.case} | {item.expected} | {baseline} | "
            f"{_mark(item.ros_doctor, item.ros_doctor_correct)} | {item.evidence_count} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate ROS Doctor against gold cases.")
    parser.add_argument("cases_dir", type=Path, nargs="?", default=Path("cases"))
    parser.add_argument("--output", type=Path, default=Path("reports/evaluation.md"))
    parser.add_argument("--write-diagnoses", action="store_true")
    parser.add_argument("--model", default=None)
    parser.add_argument("--agent-mode", choices=("offline", "llm"), default="offline")
    parser.add_argument("--baseline-mode", choices=("none", "one-shot-llm"), default="one-shot-llm")
    args = parser.parse_args(argv)

    try:
        results, summary = evaluate_cases(
            args.cases_dir,
            baseline_mode=args.baseline_mode,
            agent_mode=args.agent_mode,
            model=args.model,
            write_diagnoses=args.write_diagnoses,
            reports_dir=args.output.parent,
        )
    except LLMUnavailable as exc:
        raise SystemExit(f"LLM evaluation requires OPENAI_API_KEY: {exc}") from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_evaluation(results, summary))
    print(args.output)
    return 0


def _accuracy(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _mark(value: str, correct: bool) -> str:
    return f"{'OK' if correct else 'MISS'} `{value}`"


def _run_baseline(case_dir: Path, baseline_mode: str, model: str | None) -> str | None:
    if baseline_mode == "none":
        return None
    if baseline_mode == "one-shot-llm":
        return run_one_shot_llm_baseline(case_dir, model=model)["predicted_rule"]
    raise ValueError(f"Unknown baseline mode: {baseline_mode}")


def _top_evidence_count(trajectory: list[dict]) -> int:
    for step in trajectory:
        result = step.get("result", {})
        if result.get("tool") == "verify_hypothesis":
            return (
                len(result.get("confirming_evidence", []))
                + len(result.get("supporting_context", []))
                + len(result.get("refuting_evidence", []))
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
