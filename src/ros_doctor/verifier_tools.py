from __future__ import annotations

from pathlib import Path

from .collector import collect_corpus
from .diagnoser import evaluate_rule, infer_ros_version
from .models import Corpus, Hypothesis, Rule
from .rules import RULES


def tool_collect_evidence(case_path: Path) -> dict:
    corpus = collect_corpus(case_path)
    return {
        "tool": "collect_evidence",
        "files": [str(path) for path in sorted(corpus.files)],
        "file_count": len(corpus.files),
    }


def tool_infer_ros_version(case_path: Path) -> dict:
    corpus = collect_corpus(case_path)
    return {"tool": "infer_ros_version", "ros_version": infer_ros_version(corpus)}


def tool_list_candidate_hypotheses(case_path: Path) -> dict:
    corpus = collect_corpus(case_path)
    ros_version = infer_ros_version(corpus)
    candidates = [
        rule
        for rule in RULES
        if ros_version == "unknown" or ros_version in rule.ros_versions
    ]
    return {
        "tool": "list_candidate_hypotheses",
        "ros_version": ros_version,
        "hypotheses": [
            {
                "id": rule.identifier,
                "title": rule.title,
                "root_cause": rule.root_cause,
            }
            for rule in candidates
        ],
    }


def tool_verify_hypothesis(case_path: Path, hypothesis_id: str) -> dict:
    corpus = collect_corpus(case_path)
    rule = _rule_by_id(hypothesis_id)
    hypothesis = evaluate_rule(rule, corpus, max_evidence=8)
    return {
        "tool": "verify_hypothesis",
        "hypothesis_id": hypothesis_id,
        "score": hypothesis.score,
        "confidence": hypothesis.confidence,
        "confirming_evidence": [_evidence_dict(item) for item in hypothesis.confirming],
        "supporting_context": [_evidence_dict(item) for item in hypothesis.context],
        "refuting_evidence": [_evidence_dict(item) for item in hypothesis.refuting],
        "verification_checks": list(rule.verification),
    }


def tool_attempt_to_disprove(case_path: Path, leading_hypothesis_id: str) -> dict:
    corpus = collect_corpus(case_path)
    leading = evaluate_rule(_rule_by_id(leading_hypothesis_id), corpus, max_evidence=8)
    alternatives = [
        evaluate_rule(rule, corpus, max_evidence=8)
        for rule in _candidate_rules(corpus)
        if rule.identifier != leading_hypothesis_id
    ]
    alternatives.sort(key=lambda item: item.score, reverse=True)
    strongest = alternatives[0] if alternatives else None
    margin = round(leading.score - strongest.score, 2) if strongest else leading.score
    return {
        "tool": "attempt_to_disprove",
        "leading_hypothesis_id": leading_hypothesis_id,
        "leading_score": leading.score,
        "strongest_alternative": _hypothesis_summary(strongest) if strongest else None,
        "margin": margin,
        "disproved": strongest is not None and strongest.score > leading.score,
        "decision": (
            "reject_leading"
            if strongest is not None and strongest.score > leading.score
            else "keep_leading"
        ),
    }


def evidence_bundle(case_path: Path, max_chars_per_file: int = 2800) -> str:
    corpus = collect_corpus(case_path)
    sections = []
    for path, text in sorted(corpus.files.items()):
        clipped = text[:max_chars_per_file]
        suffix = "\n[... clipped ...]" if len(text) > max_chars_per_file else ""
        sections.append(f"## {path}\n{clipped}{suffix}")
    return "\n\n".join(sections)


def run_all_verification_tools(case_path: Path) -> list[dict]:
    steps = [
        tool_collect_evidence(case_path),
        tool_infer_ros_version(case_path),
        tool_list_candidate_hypotheses(case_path),
    ]
    candidates = steps[-1]["hypotheses"]
    verified = [tool_verify_hypothesis(case_path, item["id"]) for item in candidates]
    verified.sort(key=lambda item: item["score"], reverse=True)
    steps.extend(verified)
    if verified:
        steps.append(tool_attempt_to_disprove(case_path, verified[0]["hypothesis_id"]))
    return steps


def _candidate_rules(corpus: Corpus) -> list[Rule]:
    ros_version = infer_ros_version(corpus)
    return [rule for rule in RULES if ros_version == "unknown" or ros_version in rule.ros_versions]


def _rule_by_id(identifier: str) -> Rule:
    for rule in RULES:
        if rule.identifier == identifier:
            return rule
    raise KeyError(f"Unknown hypothesis id: {identifier}")


def _evidence_dict(item) -> dict:
    return {
        "path": str(item.path),
        "line": item.line,
        "signal": item.signal,
        "snippet": item.snippet,
    }


def _hypothesis_summary(item: Hypothesis | None) -> dict | None:
    if item is None:
        return None
    return {
        "id": item.rule.identifier,
        "title": item.rule.title,
        "score": item.score,
        "confidence": item.confidence,
    }
