from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import run_agent, write_agent_outputs
from .diagnoser import diagnose
from .llm import LLMUnavailable
from .llm_baseline import run_one_shot_llm_baseline, write_baseline_result
from .report import render_json, render_markdown, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ros-doctor",
        description="Diagnose ROS/ROS2 failures from logs, config, and repository evidence.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    diagnose_parser = subparsers.add_parser("diagnose", help="diagnose one case folder")
    diagnose_parser.add_argument("case_path", type=Path, help="folder or file containing logs and evidence")
    diagnose_parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format",
    )
    diagnose_parser.add_argument("--output", type=Path, help="optional report file")

    agent_parser = subparsers.add_parser("agent-diagnose", help="run the tool-using LLM agent")
    agent_parser.add_argument("case_path", type=Path)
    agent_parser.add_argument("--model", default=None)
    agent_parser.add_argument("--offline", action="store_true", help="exercise the tool loop without an LLM call")
    agent_parser.add_argument("--output", type=Path, help="optional Markdown report file")
    agent_parser.add_argument("--trajectory-output", type=Path, help="optional JSON trajectory file")

    baseline_parser = subparsers.add_parser("llm-baseline", help="run the one-shot general LLM baseline")
    baseline_parser.add_argument("case_path", type=Path)
    baseline_parser.add_argument("--model", default=None)
    baseline_parser.add_argument("--output", type=Path, help="optional JSON output file")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "diagnose":
        diagnosis = diagnose(args.case_path)
        if args.output:
            write_report(diagnosis, args.output, args.format)
        else:
            text = render_json(diagnosis) if args.format == "json" else render_markdown(diagnosis)
            sys.stdout.write(text)
        return 0
    if args.command == "agent-diagnose":
        try:
            run = run_agent(args.case_path, model=args.model, offline=args.offline)
        except LLMUnavailable as exc:
            raise SystemExit(f"LLM agent requires OPENAI_API_KEY: {exc}") from exc
        write_agent_outputs(run, args.output, args.trajectory_output)
        if not args.output:
            sys.stdout.write(run.report)
        return 0
    if args.command == "llm-baseline":
        try:
            result = run_one_shot_llm_baseline(args.case_path, model=args.model)
        except LLMUnavailable as exc:
            raise SystemExit(f"LLM baseline requires OPENAI_API_KEY: {exc}") from exc
        if args.output:
            write_baseline_result(result, args.output)
        else:
            sys.stdout.write(render_json_like(result))
        return 0
    return 2


def render_json_like(value: dict) -> str:
    import json

    return json.dumps(value, indent=2) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
