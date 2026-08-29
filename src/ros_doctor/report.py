from __future__ import annotations

import json
from pathlib import Path

from .models import Diagnosis, Evidence, Hypothesis


def diagnosis_to_dict(diagnosis: Diagnosis) -> dict:
    return {
        "ros_version": diagnosis.ros_version,
        "scanned_files": [str(path) for path in diagnosis.scanned_files],
        "warnings": diagnosis.warnings,
        "agent_steps": diagnosis.agent_steps,
        "hypotheses": [
            {
                "id": item.rule.identifier,
                "title": item.rule.title,
                "score": item.score,
                "confidence": item.confidence,
                "root_cause": item.rule.root_cause,
                "fix": item.rule.fix,
                "verification": list(item.rule.verification),
                "confirming_evidence": [_evidence_to_dict(ev) for ev in item.confirming],
                "context_evidence": [_evidence_to_dict(ev) for ev in item.context],
                "refuting_evidence": [_evidence_to_dict(ev) for ev in item.refuting],
            }
            for item in diagnosis.hypotheses
        ],
    }


def render_json(diagnosis: Diagnosis) -> str:
    return json.dumps(diagnosis_to_dict(diagnosis), indent=2)


def render_markdown(diagnosis: Diagnosis) -> str:
    lines: list[str] = [
        "# ROS Doctor Diagnosis",
        "",
        f"- Inferred ROS version: `{diagnosis.ros_version}`",
        f"- Files scanned: `{len(diagnosis.scanned_files)}`",
    ]
    for warning in diagnosis.warnings:
        lines.append(f"- Warning: {warning}")

    if not diagnosis.hypotheses:
        lines.extend(
            [
                "",
                "## Result",
                "",
                "No supported root-cause hypothesis had enough evidence. Add logs, launch files, package manifests, environment output, and command transcripts.",
            ]
        )
        return "\n".join(lines) + "\n"

    lines.extend(["", "## Agent Verification Loop", ""])
    lines.extend(f"{index}. {step}" for index, step in enumerate(diagnosis.agent_steps, start=1))
    lines.extend(["", "## Ranked Hypotheses", ""])
    for index, hypothesis in enumerate(diagnosis.hypotheses, start=1):
        lines.extend(_render_hypothesis(index, hypothesis))
    return "\n".join(lines) + "\n"


def write_report(diagnosis: Diagnosis, output: Path, fmt: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    text = render_json(diagnosis) if fmt == "json" else render_markdown(diagnosis)
    output.write_text(text)


def _render_hypothesis(index: int, hypothesis: Hypothesis) -> list[str]:
    lines = [
        f"### {index}. {hypothesis.rule.title}",
        "",
        f"- Score: `{hypothesis.score}` ({hypothesis.confidence} confidence)",
        f"- Likely root cause: {hypothesis.rule.root_cause}",
        f"- Recommended fix: {hypothesis.rule.fix}",
        "- Verification checks:",
    ]
    lines.extend(f"  - `{check}`" for check in hypothesis.rule.verification)
    lines.extend(["", "#### Confirming Evidence"])
    lines.extend(_render_evidence(hypothesis.confirming))
    if hypothesis.context:
        lines.extend(["", "#### Supporting Context"])
        lines.extend(_render_evidence(hypothesis.context))
    if hypothesis.refuting:
        lines.extend(["", "#### Refuting Evidence"])
        lines.extend(_render_evidence(hypothesis.refuting))
    lines.append("")
    return lines


def _render_evidence(items: list[Evidence]) -> list[str]:
    if not items:
        return ["- No direct evidence captured."]
    rendered = []
    for item in items:
        rendered.append(f"- `{item.path}:{item.line}` [{item.signal}] {item.snippet}")
    return rendered


def _evidence_to_dict(evidence: Evidence) -> dict:
    return {
        "path": str(evidence.path),
        "line": evidence.line,
        "signal": evidence.signal,
        "snippet": evidence.snippet,
    }
