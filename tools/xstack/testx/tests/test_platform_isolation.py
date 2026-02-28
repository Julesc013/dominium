"""FAST test: platform isolation scan must remain clean."""

from __future__ import annotations

import os
import re


TEST_ID = "test_platform_isolation"
TEST_TAGS = ["fast", "architecture", "platform"]


OS_TOKEN_PATTERNS = (
    re.compile(r"^\s*#\s*include\s*[<\"]windows\.h[\">]", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]X11/", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]Cocoa/", re.IGNORECASE),
    re.compile(r"\bctypes\.windll\b", re.IGNORECASE),
    re.compile(r"\bimport\s+win32api\b", re.IGNORECASE),
)


def run(repo_root: str):
    src_root = os.path.join(repo_root, "src")
    if not os.path.isdir(src_root):
        return {"status": "fail", "message": "missing src directory"}

    violations = []
    for walk_root, dirs, files in os.walk(src_root):
        dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
        rel_root = os.path.relpath(walk_root, repo_root).replace("\\", "/")
        if rel_root.startswith("src/platform"):
            continue
        for name in sorted(files):
            if not name.endswith((".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp")):
                continue
            abs_path = os.path.join(walk_root, name)
            rel_path = os.path.relpath(abs_path, repo_root).replace("\\", "/")
            try:
                lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, start=1):
                if not any(pattern.search(line) for pattern in OS_TOKEN_PATTERNS):
                    continue
                violations.append("{}:{}".format(rel_path, line_no))

    if violations:
        return {"status": "fail", "message": "platform isolation violations detected: {}".format(len(violations))}
    return {"status": "pass", "message": "platform isolation scan clean"}
