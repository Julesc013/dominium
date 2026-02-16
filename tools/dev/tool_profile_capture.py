"""Deterministic profile trace capture for developer acceleration diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402
from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.registry_compile.compiler import compile_bundle  # noqa: E402
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID  # noqa: E402
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload  # noqa: E402


TOOL_ID = "tool_profile_capture"
TOOL_VERSION = "1.0.0"
LOCKFILE_REL = "build/lockfile.json"
REGISTRY_DIR_REL = "build/registries"

PROFILE_TRACE_REGISTRY_KEYS = (
    "domain_registry_hash",
    "law_registry_hash",
    "experience_registry_hash",
    "lens_registry_hash",
    "net_replication_policy_registry_hash",
    "net_resync_strategy_registry_hash",
    "net_server_policy_registry_hash",
    "securex_policy_registry_hash",
    "server_profile_registry_hash",
    "shard_map_registry_hash",
    "perception_interest_policy_registry_hash",
    "anti_cheat_policy_registry_hash",
    "anti_cheat_module_registry_hash",
    "activation_policy_registry_hash",
    "budget_policy_registry_hash",
    "fidelity_policy_registry_hash",
    "worldgen_constraints_registry_hash",
    "astronomy_catalog_index_hash",
    "site_registry_index_hash",
    "ephemeris_registry_hash",
    "terrain_tile_registry_hash",
    "ui_registry_hash",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _resolve_root(repo_root: str, path: str) -> str:
    token = str(path or "").strip()
    if not token:
        return repo_root
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token))


def _repo_relative(repo_root: str, path: str) -> str:
    try:
        return _norm(os.path.relpath(path, repo_root))
    except ValueError:
        return _norm(path)


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def _resolve_bii(repo_root: str, explicit_bii: str) -> str:
    token = str(explicit_bii or "").strip()
    if token:
        return token
    build_number_path = os.path.join(repo_root, ".dominium_build_number")
    if os.path.isfile(build_number_path):
        try:
            number = open(build_number_path, "r", encoding="utf-8").read().strip()
        except OSError:
            number = ""
        if number:
            return number
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return "unknown"
    if int(proc.returncode) == 0:
        commit_token = str(proc.stdout or "").strip()
        if commit_token:
            return commit_token
    return "unknown"


def capture_profile_trace(
    repo_root: str,
    bundle_id: str,
    session_id: str,
    scenario_id: str,
    out_rel: str,
    bii: str,
    multiplayer_policy_id: str = "",
    multiplayer_client_count: int = 0,
    multiplayer_shard_count: int = 0,
    multiplayer_resync_count: int = 0,
    multiplayer_message_units_per_tick: int = 0,
    multiplayer_perceived_delta_units: int = 0,
) -> Dict[str, object]:
    compile_result = compile_bundle(
        repo_root=repo_root,
        bundle_id=str(bundle_id),
        out_dir_rel=REGISTRY_DIR_REL,
        lockfile_out_rel=LOCKFILE_REL,
        packs_root_rel="packs",
        use_cache=True,
    )
    if compile_result.get("result") != "complete":
        return {
            "result": "refused",
            "reason_code": "refusal.profile.compile_failed",
            "message": "registry compile failed before profile capture",
            "errors": list(compile_result.get("errors") or []),
        }

    lockfile_abs = os.path.join(repo_root, LOCKFILE_REL.replace("/", os.sep))
    lock_payload, lock_err = _read_json(lockfile_abs)
    if lock_err:
        return {
            "result": "refused",
            "reason_code": "refusal.profile.lockfile_missing",
            "message": "required build/lockfile.json is missing or invalid",
            "errors": [{"code": "lockfile_missing", "path": "$.lockfile", "message": lock_err}],
        }

    lock_schema_check = validate_instance(
        repo_root=repo_root,
        schema_name="bundle_lockfile",
        payload=lock_payload,
        strict_top_level=True,
    )
    if not bool(lock_schema_check.get("valid", False)):
        return {
            "result": "refused",
            "reason_code": "refusal.profile.lockfile_schema_invalid",
            "message": "lockfile schema validation failed",
            "errors": list(lock_schema_check.get("errors") or []),
        }

    lock_semantic = validate_lockfile_payload(lock_payload)
    if lock_semantic.get("result") != "complete":
        return {
            "result": "refused",
            "reason_code": "refusal.profile.lockfile_semantic_invalid",
            "message": "lockfile semantic validation failed",
            "errors": list(lock_semantic.get("errors") or []),
        }

    lock_registry_hashes = dict(lock_payload.get("registries") or {})
    registry_hashes = dict(
        (key, str(lock_registry_hashes.get(key, "")).strip())
        for key in PROFILE_TRACE_REGISTRY_KEYS
    )
    resolved_packs = list(lock_payload.get("resolved_packs") or [])
    estimated_units = int(len(resolved_packs) * 45 + len(registry_hashes) * 3)
    profile_bii = _resolve_bii(repo_root=repo_root, explicit_bii=bii)
    trace_seed = {
        "bundle_id": str(bundle_id),
        "scenario_id": str(scenario_id),
        "session_id": str(session_id),
        "bii": profile_bii,
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "registry_hashes": registry_hashes,
        "resolved_pack_count": len(resolved_packs),
    }
    trace_id = canonical_sha256(trace_seed)
    trace_payload = {
        "schema_version": "1.0.0",
        "trace_id": trace_id,
        "artifact_class": "DERIVED",
        "deterministic": True,
        "bii": profile_bii,
        "bundle_id": str(bundle_id),
        "session_id": str(session_id),
        "scenario_id": str(scenario_id),
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "registry_hashes": registry_hashes,
        "metrics": {
            "metric_schema_version": "1.0.0",
            "resolved_pack_count": len(resolved_packs),
            "registry_count": len(registry_hashes),
            "estimated_compute_units": estimated_units,
            "profile_ms": 0,
        },
        "capture_meta": {
            "tool_id": TOOL_ID,
            "tool_version": TOOL_VERSION,
            "source_lockfile_path": LOCKFILE_REL,
            "source_registry_dir": REGISTRY_DIR_REL,
        },
        "extensions": {},
    }
    policy_token = str(multiplayer_policy_id or "").strip()
    if policy_token:
        trace_payload["extensions"]["multiplayer_metrics"] = {
            "policy_id": policy_token,
            "client_count": max(0, int(multiplayer_client_count)),
            "shard_count": max(0, int(multiplayer_shard_count)),
            "resync_count": max(0, int(multiplayer_resync_count)),
            "message_units_per_tick": max(0, int(multiplayer_message_units_per_tick)),
            "perceived_delta_units": max(0, int(multiplayer_perceived_delta_units)),
        }
    trace_schema_check = validate_instance(
        repo_root=repo_root,
        schema_name="profile_trace",
        payload=trace_payload,
        strict_top_level=True,
    )
    if not bool(trace_schema_check.get("valid", False)):
        return {
            "result": "refused",
            "reason_code": "refusal.profile.trace_schema_invalid",
            "message": "profile trace payload failed schema validation",
            "errors": list(trace_schema_check.get("errors") or []),
        }

    out_abs = _resolve_root(repo_root, out_rel)
    _write_json(out_abs, trace_payload)
    return {
        "result": "complete",
        "trace_path": _repo_relative(repo_root, out_abs),
        "trace_hash": canonical_sha256(trace_payload),
        "bii": profile_bii,
        "bundle_id": str(bundle_id),
        "session_id": str(session_id),
        "scenario_id": str(scenario_id),
        "pack_lock_hash": str(trace_payload.get("pack_lock_hash", "")),
        "registry_hashes": dict(trace_payload.get("registry_hashes") or {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture deterministic profile trace artifact.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--bundle-id", default=DEFAULT_BUNDLE_ID)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--scenario-id", required=True)
    parser.add_argument("--bii", default="")
    parser.add_argument("--out", default="docs/audit/perf/profile_trace.sample.json")
    parser.add_argument("--multiplayer-policy-id", default="")
    parser.add_argument("--multiplayer-client-count", type=int, default=0)
    parser.add_argument("--multiplayer-shard-count", type=int, default=0)
    parser.add_argument("--multiplayer-resync-count", type=int, default=0)
    parser.add_argument("--multiplayer-message-units-per-tick", type=int, default=0)
    parser.add_argument("--multiplayer-perceived-delta-units", type=int, default=0)
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = capture_profile_trace(
        repo_root=repo_root,
        bundle_id=str(args.bundle_id),
        session_id=str(args.session_id),
        scenario_id=str(args.scenario_id),
        out_rel=str(args.out),
        bii=str(args.bii),
        multiplayer_policy_id=str(args.multiplayer_policy_id),
        multiplayer_client_count=int(args.multiplayer_client_count),
        multiplayer_shard_count=int(args.multiplayer_shard_count),
        multiplayer_resync_count=int(args.multiplayer_resync_count),
        multiplayer_message_units_per_tick=int(args.multiplayer_message_units_per_tick),
        multiplayer_perceived_delta_units=int(args.multiplayer_perceived_delta_units),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    token = str(result.get("result", "error"))
    if token == "complete":
        return 0
    if token == "refused":
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
