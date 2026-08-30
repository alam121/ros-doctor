from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .diagnoser import diagnose
from .llm import call_openai_response, parse_json_object
from .report import render_markdown
from .rules import RULES
from .verifier_tools import evidence_bundle, run_all_verification_tools


@dataclass(frozen=True)
class AgentRun:
    case_path: Path
    mode: str
    predicted_rule: str
    report: str
    trajectory: list[dict[str, Any]]


def run_agent(case_path: Path, model: str | None = None, offline: bool = False) -> AgentRun:
    if offline:
        return run_offline_agent(case_path)

    trajectory: list[dict[str, Any]] = []
    bundle = evidence_bundle(case_path)
    candidate_ids = [rule.identifier for rule in RULES]
    proposal_prompt = f"""
You are ROS Doctor, an evidence-driven ROS debugging agent.

Generate 2-4 competing root-cause hypotheses for this case. Do not recommend a fix yet.
Return only JSON:
{{
  "hypotheses": [
    {{"id": "one of {candidate_ids}", "reason": "why it might explain the evidence"}}
  ]
}}

Evidence:
{bundle}
""".strip()
    proposal = call_openai_response(proposal_prompt, model=model) if model else call_openai_response(proposal_prompt)
    proposed = parse_json_object(proposal.text)
    trajectory.append(
        {
            "actor": "llm_agent",
            "action": "generate_competing_hypotheses",
            "prompt": proposal_prompt,
            "response": proposed,
        }
    )

    tool_results = run_all_verification_tools(case_path)
    trajectory.extend({"actor": "verification_tool", "result": result} for result in tool_results)
    final_prompt = f"""
You are ROS Doctor. Use only the verification tool results below to write the final diagnosis.

Requirements:
- Choose the strongest root-cause hypothesis.
- Explain which evidence confirms it.
- Mention the strongest alternative and why it did not beat the leader.
- Recommend concrete verification commands and fix steps.
- Return only JSON: {{"predicted_rule": "...", "report_markdown": "..."}}

Initial LLM hypotheses:
{json.dumps(proposed, indent=2)}

Verification tool results:
{json.dumps(tool_results, indent=2)}
""".strip()
    final = call_openai_response(final_prompt, model=model) if model else call_openai_response(final_prompt)
    final_json = parse_json_object(final.text)
    trajectory.append(
        {
            "actor": "llm_agent",
            "action": "synthesize_verified_diagnosis",
            "prompt": final_prompt,
            "response": final_json,
        }
    )
    return AgentRun(
        case_path=case_path,
        mode="llm",
        predicted_rule=str(final_json["predicted_rule"]),
        report=str(final_json["report_markdown"]),
        trajectory=trajectory,
    )


def run_offline_agent(case_path: Path) -> AgentRun:
    diagnosis = diagnose(case_path)
    top = diagnosis.hypotheses[0] if diagnosis.hypotheses else None
    tool_results = run_all_verification_tools(case_path)
    trajectory = [
        {
            "actor": "offline_agent_driver",
            "action": "request_competing_hypotheses",
            "note": "Offline mode skips the LLM call but preserves the tool-using control flow for tests.",
        },
        *({"actor": "verification_tool", "result": result} for result in tool_results),
        {
            "actor": "offline_agent_driver",
            "action": "select_verified_leader",
            "predicted_rule": top.rule.identifier if top else "no_hypothesis",
        },
    ]
    return AgentRun(
        case_path=case_path,
        mode="offline",
        predicted_rule=top.rule.identifier if top else "no_hypothesis",
        report=render_markdown(diagnosis),
        trajectory=trajectory,
    )


def write_agent_outputs(run: AgentRun, report_path: Path | None, trajectory_path: Path | None) -> None:
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(run.report)
    if trajectory_path:
        trajectory_path.parent.mkdir(parents=True, exist_ok=True)
        trajectory_path.write_text(json.dumps(_run_to_dict(run), indent=2))


def _run_to_dict(run: AgentRun) -> dict[str, Any]:
    return {
        "case_path": str(run.case_path),
        "mode": run.mode,
        "predicted_rule": run.predicted_rule,
        "trajectory": run.trajectory,
    }
