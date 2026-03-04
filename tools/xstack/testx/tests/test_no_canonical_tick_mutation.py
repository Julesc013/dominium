"""FAST test: canonical tick mutation is restricted to time_engine."""

from __future__ import annotations

import os
import re


TEST_ID = "test_no_canonical_tick_mutation"
TEST_TAGS = ["fast", "time", "temp1", "governance"]

_PATTERNS = (
    re.compile(r"\b(?:sim|simulation_time)\s*\[\s*['\"]tick['\"]\s*\]\s*=", re.IGNORECASE),
    re.compile(r"\bstate\s*\[\s*['\"]simulation_time['\"]\s*\]\s*\[\s*['\"]tick['\"]\s*\]\s*=", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(repo_root: str):
    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "src/time/time_engine.py",
    }
    violations = []

    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _PATTERNS):
                        continue
                    violations.append("{}:{} {}".format(rel_path, line_no, snippet[:120]))
                    break

    if violations:
        return {
            "status": "fail",
            "message": "direct canonical tick mutation detected outside time_engine: {}".format("; ".join(violations[:5])),
        }
    return {"status": "pass", "message": "canonical tick mutation restricted to time_engine"}
