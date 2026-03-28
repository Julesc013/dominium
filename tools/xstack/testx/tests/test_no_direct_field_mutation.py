"""FAST test: direct field-state mutation outside process/field engine is forbidden."""

from __future__ import annotations

import os
import re


TEST_ID = "test_no_direct_field_mutation"
TEST_TAGS = ["fast", "fields", "governance"]

_WRITE_PATTERNS = (
    re.compile(r"\bstate\s*\[\s*[\"']field_layers[\"']\s*\]\s*=", re.IGNORECASE),
    re.compile(r"\bstate\s*\[\s*[\"']field_cells[\"']\s*\]\s*=", re.IGNORECASE),
    re.compile(r"\bstate\s*\[\s*[\"']field_sample_rows[\"']\s*\]\s*=", re.IGNORECASE),
)

_SCAN_ROOTS = (
    "src",
    os.path.join("tools", "xstack", "sessionx"),
)

_SKIP_PREFIXES = (
    "docs/",
    "schema/",
    "schemas/",
    "tools/auditx/analyzers/",
    "tools/xstack/testx/tests/",
)

_ALLOWED_FILES = {
    "tools/xstack/sessionx/process_runtime.py",
    "fields/field_engine.py",
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(repo_root: str):
    violations = []
    for root_rel in _SCAN_ROOTS:
        root_abs = os.path.join(repo_root, root_rel)
        if not os.path.isdir(root_abs):
            continue
        for walk_root, _dirs, files in os.walk(root_abs):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(_SKIP_PREFIXES):
                    continue
                if rel_path in _ALLOWED_FILES:
                    continue
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _WRITE_PATTERNS):
                        continue
                    violations.append("{}:{} {}".format(rel_path, line_no, snippet[:120]))
                    break
    if violations:
        return {
            "status": "fail",
            "message": "direct field mutation patterns found outside allowed files: {}".format("; ".join(violations[:5])),
        }
    return {"status": "pass", "message": "field mutation remains process/field-engine only"}

