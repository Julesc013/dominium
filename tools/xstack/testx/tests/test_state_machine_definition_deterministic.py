"""FAST test: LOGIC-2 state machine definitions normalize deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_state_machine_definition_deterministic"
TEST_TAGS = ["fast", "logic", "determinism", "state_machine"]


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic import normalize_state_machine_definition_rows
    from tools.xstack.compatx.canonical_json import canonical_sha256

    payload = _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_state_machine_registry.json")
    rows = list(payload.get("state_machine_definitions") or [])
    if not rows:
        return {"status": "fail", "message": "logic state machine registry missing rows"}

    normalized_a = normalize_state_machine_definition_rows(rows)
    normalized_b = normalize_state_machine_definition_rows(list(reversed(rows)))
    if not normalized_a or normalized_a != normalized_b:
        return {"status": "fail", "message": "state machine normalization is order-sensitive"}
    if canonical_sha256(normalized_a) != canonical_sha256(normalized_b):
        return {"status": "fail", "message": "state machine hash is order-sensitive"}

    for row in normalized_a:
        fingerprint = str(row.get("deterministic_fingerprint", "")).strip()
        expected = canonical_sha256(dict(row, deterministic_fingerprint=""))
        if fingerprint != expected:
            return {
                "status": "fail",
                "message": "{} has unstable deterministic_fingerprint".format(str(row.get("sm_id", "")).strip() or "<missing>"),
            }

    return {"status": "pass", "message": "LOGIC-2 state machine definitions normalize deterministically"}
