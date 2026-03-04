"""FAST test: future receipt references are rejected by deterministic causality guards."""

from __future__ import annotations

import os
import re


TEST_ID = "test_no_future_receipt_references"
TEST_TAGS = ["fast", "time", "causality", "temp0"]

_FUTURE_RECEIPT_PATTERNS = (
    re.compile(r"\bacquired_tick\b[^\n]*>[^\n]*\b(?:current_tick|tick|decision_tick)\b", re.IGNORECASE),
    re.compile(r"\breceived_tick\b[^\n]*>[^\n]*\b(?:current_tick|tick|decision_tick)\b", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(repo_root: str):
    compliant_fixtures = (
        "if received_tick <= current_tick: accept = True",
        "if acquired_tick <= decision_tick: can_use = True",
        "accepted = int(max(0, min(received_tick, current_tick)))",
    )
    violating_fixtures = (
        "if received_tick > current_tick: accept = True",
        "if acquired_tick > tick: consume_receipt()",
    )
    for snippet in compliant_fixtures:
        if any(pattern.search(snippet) for pattern in _FUTURE_RECEIPT_PATTERNS):
            return {"status": "fail", "message": "compliant fixture matched future-receipt detector: {}".format(snippet)}
    for snippet in violating_fixtures:
        if not any(pattern.search(snippet) for pattern in _FUTURE_RECEIPT_PATTERNS):
            return {"status": "fail", "message": "violating fixture did not match future-receipt detector: {}".format(snippet)}

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
        "tools/xstack/repox/check.py",
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
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    lowered = snippet.lower()
                    if ("acquired_tick" not in lowered) and ("received_tick" not in lowered):
                        continue
                    if not any(pattern.search(snippet) for pattern in _FUTURE_RECEIPT_PATTERNS):
                        continue
                    violations.append("{}:{} {}".format(rel_path, line_no, snippet[:120]))
                    break

    if violations:
        return {
            "status": "fail",
            "message": "future receipt references detected: {}".format("; ".join(violations[:5])),
        }
    return {"status": "pass", "message": "no future receipt references detected"}
