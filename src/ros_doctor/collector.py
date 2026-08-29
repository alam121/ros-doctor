from __future__ import annotations

from pathlib import Path

from .models import Corpus


TEXT_SUFFIXES = {
    ".bash",
    ".cfg",
    ".cmake",
    ".env",
    ".launch",
    ".log",
    ".md",
    ".msg",
    ".py",
    ".srv",
    ".txt",
    ".urdf",
    ".xacro",
    ".xml",
    ".yaml",
    ".yml",
}

TEXT_NAMES = {
    "CMakeLists.txt",
    "package.xml",
    "COLCON_IGNORE",
    "CATKIN_IGNORE",
    "ros2doctor.txt",
    "roswtf.txt",
}


def collect_corpus(case_path: Path) -> Corpus:
    if not case_path.exists():
        raise FileNotFoundError(f"Case path does not exist: {case_path}")
    if case_path.is_file():
        return Corpus(root=case_path.parent, files={case_path: case_path.read_text(errors="replace")})

    files: dict[Path, str] = {}
    for path in sorted(case_path.rglob("*")):
        if not path.is_file():
            continue
        if path.name in TEXT_NAMES or path.suffix in TEXT_SUFFIXES:
            try:
                files[path] = path.read_text(errors="replace")
            except OSError:
                continue
    return Corpus(root=case_path, files=files)
