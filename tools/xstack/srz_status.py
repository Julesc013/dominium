#!/usr/bin/env python3
"""CLI: deterministic SRZ shard status for a session save."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.sessionx.common import norm, read_json_object, refusal  # noqa: E402
from tools.xstack.sessionx.srz import build_single_shard, validate_srz_shard  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _load_schema_validated(repo_root: str, schema_name: str, path: str) -> Tuple[dict, Dict[str, object]]:
    payload, err = read_json_object(path)
    if err:
        return {}, refusal(
            "REFUSE_JSON_LOAD_FAILED",
            "unable to parse required JSON file",
            "Ensure the file exists and contains valid JSON object content.",
            {"path": norm(path)},
            "$",
        )
    valid = validate_instance(repo_root=repo_root, schema_name=schema_name, payload=payload, strict_top_level=True)
    if not bool(valid.get("valid", False)):
        return {}, refusal(
            "REFUSE_SCHEMA_INVALID",
            "payload failed schema validation for '{}'".format(schema_name),
            "Fix file fields to satisfy schema validation and retry.",
            {"schema_id": schema_name, "path": norm(path)},
            "$",
        )
    return payload, {}


def _latest_run_meta_hash(save_dir: str) -> str:
    run_meta_dir = os.path.join(save_dir, "run_meta")
    if not os.path.isdir(run_meta_dir):
        return ""
    rows = []
    for name in os.listdir(run_meta_dir):
        if not name.endswith(".json"):
            continue
        rows.append(name)
    for name in sorted(rows, reverse=True):
        payload, err = read_json_object(os.path.join(run_meta_dir, name))
        if err:
            continue
        tick_hashes = payload.get("tick_hash_anchors")
        if isinstance(tick_hashes, list) and tick_hashes:
            last = tick_hashes[-1]
            if isinstance(last, dict):
                token = str(last.get("tick_hash", "")).strip()
                if token:
                    return token
        token = str(payload.get("composite_hash", "")).strip()
        if token:
            return token
    return ""


def _process_log_hash(universe_state: dict) -> str:
    rows = universe_state.get("process_log")
    if not isinstance(rows, list) or not rows:
        return ""
    for row in reversed(rows):
        if not isinstance(row, dict):
            continue
        token = str(row.get("state_hash_anchor", "")).strip()
        if token:
            return token
    return ""


def srz_status(repo_root: str, session_spec_path: str) -> Dict[str, object]:
    session_abs = os.path.normpath(os.path.abspath(session_spec_path))
    session_spec, session_error = _load_schema_validated(repo_root=repo_root, schema_name="session_spec", path=session_abs)
    if session_error:
        return session_error

    save_id = str(session_spec.get("save_id", "")).strip()
    if not save_id:
        return refusal(
            "REFUSE_SAVE_ID_MISSING",
            "SessionSpec save_id is missing",
            "Fix session_spec.json save_id and retry.",
            {"schema_id": "session_spec"},
            "$.save_id",
        )
    save_dir = os.path.join(repo_root, "saves", save_id)
    state_path = os.path.join(save_dir, "universe_state.json")
    universe_state, state_error = _load_schema_validated(repo_root=repo_root, schema_name="universe_state", path=state_path)
    if state_error:
        return state_error

    authority = session_spec.get("authority_context")
    authority_origin = "client"
    if isinstance(authority, dict):
        authority_origin = str(authority.get("authority_origin", "")).strip() or "client"

    last_hash_anchor = _latest_run_meta_hash(save_dir=save_dir) or _process_log_hash(universe_state)
    shard = build_single_shard(
        universe_state=universe_state,
        authority_origin=authority_origin,
        compatibility_version="1.0.0",
        last_hash_anchor=last_hash_anchor,
    )
    shard_check = validate_srz_shard(repo_root=repo_root, shard=shard)
    if not bool(shard_check.get("valid", False)):
        return refusal(
            "SRZ_SHARD_INVALID",
            "computed shard payload failed srz_shard schema validation",
            "Fix SRZ shard construction or schema mismatch and retry.",
            {"shard_id": str(shard.get("shard_id", ""))},
            "$.srz_shard",
        )

    shard_row = {
        "shard_id": str(shard.get("shard_id", "")),
        "authority_origin": str(shard.get("authority_origin", "")),
        "active": bool(shard.get("active", False)),
        "owned_entities_count": len(list(shard.get("owned_entities") or [])),
        "owned_regions_count": len(list(shard.get("owned_regions") or [])),
        "process_queue_count": len(list(shard.get("process_queue") or [])),
        "last_hash_anchor": str(shard.get("last_hash_anchor", "")),
    }
    return {
        "result": "complete",
        "runtime_mode": "single_shard",
        "save_id": save_id,
        "session_spec_path": norm(os.path.relpath(session_abs, repo_root)),
        "shard_count": 1,
        "shards": [shard_row],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print deterministic SRZ shard status for a session.")
    parser.add_argument("session_spec_path", help="path to saves/<save_id>/session_spec.json")
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    result = srz_status(repo_root=repo_root, session_spec_path=str(args.session_spec_path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
