from __future__ import annotations

import re
from pathlib import Path

from .collector import collect_corpus
from .models import Corpus, Diagnosis, Evidence, Hypothesis, Rule
from .rules import RULES


def infer_ros_version(corpus: Corpus) -> str:
    haystack = "\n".join(corpus.files.values()).lower()
    ros2_signals = ("ros2", "ament_", "colcon", "rclpy", "rclcpp", "package not found: \"")
    ros1_signals = ("roscore", "catkin", "rospy", "roslaunch", "rospack", "ros_master_uri")
    ros2_score = sum(signal in haystack for signal in ros2_signals)
    ros1_score = sum(signal in haystack for signal in ros1_signals)
    if ros1_score > ros2_score:
        return "ros1"
    if ros2_score > 0:
        return "ros2"
    return "unknown"


def diagnose(case_path: Path, max_evidence_per_bucket: int = 6) -> Diagnosis:
    corpus = collect_corpus(case_path)
    ros_version = infer_ros_version(corpus)
    warnings: list[str] = []
    if not corpus.files:
        warnings.append("No readable text files were found in the case path.")

    candidate_rules = [
        rule for rule in RULES if ros_version == "unknown" or ros_version in rule.ros_versions
    ]
    hypotheses = [
        hypothesis
        for rule in candidate_rules
        if (hypothesis := evaluate_rule(rule, corpus, max_evidence_per_bucket)).score > 0
    ]
    hypotheses.sort(key=lambda item: item.score, reverse=True)
    agent_steps = [
        f"Collected {len(corpus.files)} readable evidence files from {case_path}.",
        f"Inferred ROS version as {ros_version}.",
        f"Generated {len(candidate_rules)} candidate root-cause hypotheses from the rule library.",
        f"Verified candidates against confirming, supporting, and refuting evidence.",
        f"Rejected {len(candidate_rules) - len(hypotheses)} candidates with no supporting evidence.",
        "Ranked remaining hypotheses by evidence strength and contradiction penalties.",
    ]
    return Diagnosis(
        ros_version=ros_version,
        hypotheses=hypotheses,
        scanned_files=sorted(corpus.files),
        warnings=warnings,
        agent_steps=agent_steps,
    )


def evaluate_rule(rule: Rule, corpus: Corpus, max_evidence: int) -> Hypothesis:
    hypothesis = Hypothesis(rule=rule)
    for path, line_number, line in corpus.lines():
        for pattern in rule.confirm_patterns:
            if _matches(pattern, line):
                _append_limited(
                    hypothesis.confirming,
                    Evidence(path, line_number, line.strip(), f"confirm:{pattern}"),
                    max_evidence,
                )
        for pattern in rule.context_patterns:
            if _matches(pattern, line):
                _append_limited(
                    hypothesis.context,
                    Evidence(path, line_number, line.strip(), f"context:{pattern}"),
                    max_evidence,
                )
        for pattern in rule.refute_patterns:
            if _matches(pattern, line):
                _append_limited(
                    hypothesis.refuting,
                    Evidence(path, line_number, line.strip(), f"refute:{pattern}"),
                    max_evidence,
                )

    confirm_score = min(0.72, len(hypothesis.confirming) * 0.24)
    context_score = min(0.24, len(hypothesis.context) * 0.04)
    refute_penalty = min(0.35, len(hypothesis.refuting) * 0.12)
    hypothesis.score = round(max(0.0, confirm_score + context_score - refute_penalty), 2)
    return hypothesis


def _matches(pattern: str, line: str) -> bool:
    try:
        return re.search(pattern, line, flags=re.IGNORECASE) is not None
    except re.error:
        return pattern.lower() in line.lower()


def _append_limited(target: list[Evidence], evidence: Evidence, limit: int) -> None:
    if len(target) < limit:
        target.append(evidence)
