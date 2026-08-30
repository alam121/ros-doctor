from __future__ import annotations

import json
from pathlib import Path

from .llm import call_openai_response, parse_json_object
from .rules import RULES
from .verifier_tools import evidence_bundle


def run_one_shot_llm_baseline(case_path: Path, model: str | None = None) -> dict:
    rule_ids = [rule.identifier for rule in RULES]
    prompt = f"""
You are a general-purpose coding assistant helping debug a ROS or ROS2 failure.

Read the evidence and choose the single most likely root-cause category.
Do not call tools. Do not request more files. Return only JSON:
{{
  "predicted_rule": "one of {rule_ids}",
  "rationale": "short explanation"
}}

Evidence:
{evidence_bundle(case_path)}
""".strip()
    result = call_openai_response(prompt, model=model) if model else call_openai_response(prompt)
    parsed = parse_json_object(result.text)
    return {
        "case_path": str(case_path),
        "mode": "one_shot_general_llm",
        "prompt": prompt,
        "response": parsed,
        "predicted_rule": str(parsed["predicted_rule"]),
    }


def write_baseline_result(result: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2))
