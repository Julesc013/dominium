"""FAST test: baseline instance manifest contains a valid identity block."""

from __future__ import annotations

import sys


TEST_ID = "test_instance_manifest_contains_identity_block"
TEST_TAGS = ["fast", "omega", "baseline_universe", "identity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.meta.identity.identity_validator import validate_identity_block
    from tools.mvp.baseline_universe_common import BASELINE_INSTANCE_MANIFEST_REL, load_baseline_instance_manifest

    manifest_payload = load_baseline_instance_manifest(repo_root)
    identity_block = dict(manifest_payload.get("universal_identity_block") or {})
    report = validate_identity_block(
        repo_root=repo_root,
        identity_block=identity_block,
        strict_missing=True,
        path=BASELINE_INSTANCE_MANIFEST_REL,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "baseline instance manifest identity block validation failed"}
    if str(identity_block.get("identity_kind_id", "")).strip() != "identity.instance":
        return {"status": "fail", "message": "baseline instance manifest identity kind mismatch"}
    rel_path = str(dict(identity_block.get("extensions") or {}).get("official.rel_path", "")).strip().replace("\\", "/")
    if rel_path != BASELINE_INSTANCE_MANIFEST_REL.replace("\\", "/"):
        return {"status": "fail", "message": "baseline instance manifest identity rel_path mismatch"}
    return {"status": "pass", "message": "baseline instance manifest contains a valid identity block"}
