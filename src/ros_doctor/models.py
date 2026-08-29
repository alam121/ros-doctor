from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Evidence:
    path: Path
    line: int
    snippet: str
    signal: str


@dataclass
class Corpus:
    root: Path
    files: dict[Path, str]

    def lines(self):
        for path, text in self.files.items():
            for number, line in enumerate(text.splitlines(), start=1):
                yield path, number, line


@dataclass(frozen=True)
class Rule:
    identifier: str
    title: str
    root_cause: str
    fix: str
    verification: tuple[str, ...]
    confirm_patterns: tuple[str, ...]
    context_patterns: tuple[str, ...] = ()
    refute_patterns: tuple[str, ...] = ()
    ros_versions: tuple[str, ...] = ("ros1", "ros2")


@dataclass
class Hypothesis:
    rule: Rule
    score: float = 0.0
    confirming: list[Evidence] = field(default_factory=list)
    context: list[Evidence] = field(default_factory=list)
    refuting: list[Evidence] = field(default_factory=list)

    @property
    def confidence(self) -> str:
        if self.score >= 0.78:
            return "high"
        if self.score >= 0.45:
            return "medium"
        return "low"


@dataclass
class Diagnosis:
    ros_version: str
    hypotheses: list[Hypothesis]
    scanned_files: list[Path]
    warnings: list[str]
    agent_steps: list[str] = field(default_factory=list)
