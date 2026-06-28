from __future__ import annotations

import re
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    re.compile(r"facebook-[a-z0-9_.-]+-\d{4}-\d{2}-\d{2}", re.IGNORECASE),
    re.compile(r"\b\d{3}-\d{3}-\d{4}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
]

FORBIDDEN_TOP_LEVEL_NAMES = {"jobs", "CHECKPOINTS", "workspace", "intake", "outputs", "release"}
IGNORED_NAMES = {"__pycache__", ".git", ".venv", ".pytest_cache", ".mypy_cache"}


def scan_public_tree(root: Path) -> dict[str, object]:
    findings: list[str] = []
    root = Path(root).resolve()
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if any(part in IGNORED_NAMES for part in relative_parts):
            continue
        if relative_parts and relative_parts[0] in FORBIDDEN_TOP_LEVEL_NAMES:
            findings.append(f"forbidden runtime path present: {path}")
            continue
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".xlsx"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(text):
                findings.append(f"suspicious private-data pattern in {path}")
                break
    return {"status": "pass" if not findings else "fail", "findings": findings}
