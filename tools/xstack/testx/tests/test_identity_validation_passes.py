"""FAST test: Omega ecosystem identity coverage passes for the frozen surfaces."""

from __future__ import annotations

import sys


TEST_ID = "test_identity_validation_passes"
TEST_TAGS = ["fast", "omega", "ecosystem", "identity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.ecosystem_verify_common import verify_ecosystem

    report = verify_ecosystem(repo_root)
    identity = dict(report.get("identity_coverage") or {})
    if str(identity.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ecosystem identity coverage failed"}
    if list(identity.get("invalid_identity_paths") or []):
        return {"status": "fail", "message": "ecosystem identity coverage contains invalid paths"}
    if str(dict(identity.get("binary_identity") or {}).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "binary identity coverage failed"}
    return {"status": "pass", "message": "ecosystem identity coverage passes"}
