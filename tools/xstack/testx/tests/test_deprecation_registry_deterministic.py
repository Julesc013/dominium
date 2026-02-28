"""FAST test: governance deprecation registry is deterministic and valid."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_deprecation_registry_deterministic"
TEST_TAGS = ["fast", "governance", "deprecation", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.governance.tool_deprecation_check import (
        DEFAULT_DEPRECATIONS_REL,
        validate_deprecation_registry,
    )
    from tools.xstack.compatx.canonical_json import canonical_sha256

    deprecations_abs = os.path.join(repo_root, DEFAULT_DEPRECATIONS_REL.replace("/", os.sep))
    try:
        payload = json.load(open(deprecations_abs, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"status": "fail", "message": "failed to parse deprecations registry: {}".format(exc)}

    rows = list((dict(payload or {})).get("entries") or [])
    ids = [str((dict(row or {})).get("deprecated_id", "")).strip() for row in rows if isinstance(row, dict)]
    if ids != sorted(ids):
        return {"status": "fail", "message": "deprecation entries must be sorted by deprecated_id"}

    expected = canonical_sha256(dict(payload or {}, deterministic_fingerprint=""))
    actual = str((dict(payload or {})).get("deterministic_fingerprint", "")).strip()
    if actual != expected:
        return {"status": "fail", "message": "deterministic_fingerprint mismatch"}

    result = validate_deprecation_registry(repo_root=repo_root)
    if str(result.get("result", "")) != "pass":
        return {"status": "fail", "message": "deprecation validation failed: {}".format(len(list(result.get("errors") or [])))}

    return {"status": "pass", "message": "governance deprecation registry determinism verified"}

