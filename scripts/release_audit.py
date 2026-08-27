"""Small local release audit used when no host-specific Agent T path tool is exposed."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "__pycache__", ".pytest_cache", ".venv"}
PATTERNS = {
    "github_token": re.compile(r"\b(?:gh[pous]_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+)\b"),
    "private_windows_path": re.compile(r"(?i)\b(?:C|D|F):\\(?:Users\\|Shawn-Core\\|Codex\\)"),
    "private_drive_path": re.compile(r"(?i)\b(?:O|W):\\My Drive\\"),
}


def main() -> int:
    findings = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP for part in path.parts) or path.is_dir():
            continue
        if path.is_symlink():
            findings.append(f"symlink: {path.relative_to(ROOT)}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {path.relative_to(ROOT)}")
    if findings:
        print("FAIL")
        print("\n".join(findings))
        return 1
    print("PASS: no symlinks, token-shaped strings, or private machine/Drive paths detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
