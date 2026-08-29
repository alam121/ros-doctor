from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .diagnoser import diagnose
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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
