"""FAST test: LOGIC-2 behavior definitions remain substrate-agnostic."""

from __future__ import annotations

import os
import re


TEST_ID = "test_no_physics_leak_in_logic_behavior"
TEST_TAGS = ["fast", "logic", "static", "substrate"]


_FORBIDDEN_PATTERNS = (
    re.compile(r"\bvoltage\b", re.IGNORECASE),
    re.compile(r"\bcurrent\b", re.IGNORECASE),
    re.compile(r"\bohm(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bamp(?:ere)?s?\b", re.IGNORECASE),
    re.compile(r"\bpressure(?:_head)?\b", re.IGNORECASE),
    re.compile(r"\bpascal(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bjoule(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bwatt(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bquantity\.energy\b", re.IGNORECASE),
    re.compile(r"\bquantity\.pressure\b", re.IGNORECASE),
)


def _read(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(repo_root: str):
    rel_paths = (
        "schema/logic/logic_behavior_model.schema",
        "schema/logic/state_machine_definition.schema",
        "packs/core/pack.core.logic_base/data/logic_behavior_model_registry.json",
        "packs/core/pack.core.logic_base/data/logic_state_machine_registry.json",
    )
    for rel_path in rel_paths:
        text = _read(repo_root, rel_path)
        if not text:
            return {"status": "fail", "message": "{} missing".format(rel_path)}
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet:
                continue
            for pattern in _FORBIDDEN_PATTERNS:
                if not pattern.search(snippet):
                    continue
                return {
                    "status": "fail",
                    "message": "{}:{} leaks physical semantics into logic behavior: {}".format(rel_path, line_no, snippet[:120]),
                }
    return {"status": "pass", "message": "LOGIC-2 behavior definitions stay substrate-agnostic"}
