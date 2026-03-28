"""FAST test: deterministic numeric substrate avoids implicit float conversion in critical paths."""

from __future__ import annotations

import os
import re


TEST_ID = "test_no_float_usage"
TEST_TAGS = ["fast", "meta", "numeric", "governance"]

_FLOAT_PATTERN = re.compile(r"\bfloat\s*\(", re.IGNORECASE)
_TARGET_FILES = (
    "engine/time/time_mapping_engine.py",
    "physics/momentum_engine.py",
    "physics/energy/energy_ledger_engine.py",
    "mobility/micro/free_motion_solver.py",
    "meta/numeric.py",
)


def run(repo_root: str):
    violations = []
    for rel_path in _TARGET_FILES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
        except OSError:
            violations.append("{}: missing file".format(rel_path))
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not _FLOAT_PATTERN.search(snippet):
                continue
            violations.append("{}:{} {}".format(rel_path, line_no, snippet[:120]))
            break
    if violations:
        return {
            "status": "fail",
            "message": "implicit float conversion detected in deterministic substrate: {}".format("; ".join(violations[:5])),
        }
    return {"status": "pass", "message": "critical deterministic numeric paths are free of float() usage"}
