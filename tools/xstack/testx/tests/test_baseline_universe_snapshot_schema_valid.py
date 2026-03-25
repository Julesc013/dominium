"""FAST test: baseline universe snapshot structure and fingerprint are valid."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_baseline_universe_snapshot_schema_valid"
TEST_TAGS = ["fast", "omega", "baseline_universe", "schema"]

EXPECTED_CHECKPOINT_IDS = ["T0", "T1", "T2", "T3"]


def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.baseline_universe_common import (
        BASELINE_INSTANCE_MANIFEST_REL,
        BASELINE_PACK_LOCK_REL,
        BASELINE_PROFILE_BUNDLE_REL,
        BASELINE_UNIVERSE_SCHEMA_ID,
        baseline_snapshot_record_hash,
        load_baseline_universe_snapshot,
    )

    payload = load_baseline_universe_snapshot(repo_root)
    record = dict(payload.get("record") or {})
    if str(payload.get("schema_id", "")).strip() != BASELINE_UNIVERSE_SCHEMA_ID:
        return {"status": "fail", "message": "baseline universe snapshot schema_id mismatch"}
    if str(payload.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "baseline universe snapshot schema_version mismatch"}
    version_value = record.get("baseline_universe_version", -1)
    try:
        baseline_universe_version = int(version_value)
    except (TypeError, ValueError):
        baseline_universe_version = -1
    if baseline_universe_version != 0:
        return {"status": "fail", "message": "baseline universe version mismatch"}
    if str(record.get("stability_class", "")).strip() != "stable":
        return {"status": "fail", "message": "baseline universe stability_class mismatch"}
    checkpoint_ids = [str(item.get("checkpoint_id", "")).strip() for item in list(record.get("proof_anchors") or []) if isinstance(item, dict)]
    if checkpoint_ids != EXPECTED_CHECKPOINT_IDS:
        return {"status": "fail", "message": "baseline universe proof anchor schedule mismatch"}
    derived = dict(record.get("derived_view_hashes") or {})
    if sorted(derived.keys()) != ["T1", "T2", "T3"]:
        return {"status": "fail", "message": "baseline universe derived_view_hashes keys mismatch"}
    if str(derived.get("T1", "")).strip() == str(derived.get("T2", "")).strip():
        return {"status": "fail", "message": "baseline universe terrain edit anchor collapsed into post-refinement anchor"}
    fingerprint = str(record.get("deterministic_fingerprint", "")).strip()
    if fingerprint != baseline_snapshot_record_hash(record):
        return {"status": "fail", "message": "baseline universe snapshot deterministic_fingerprint mismatch"}
    for rel_path in (BASELINE_INSTANCE_MANIFEST_REL, BASELINE_PACK_LOCK_REL, BASELINE_PROFILE_BUNDLE_REL):
        artifact = _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
        if not isinstance(artifact, dict) or not dict(artifact.get("universal_identity_block") or {}):
            return {"status": "fail", "message": "baseline artifact missing universal_identity_block ({})".format(rel_path.replace("\\", "/"))}
    return {"status": "pass", "message": "baseline universe snapshot structure valid"}
