#!/usr/bin/env python3
"""Replay deterministic save-open policy decisions and optionally verify a recorded decision."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.lib.save import evaluate_save_open
from tools.lib.content_store import load_instance_json_artifact
from tools.xstack.compatx.canonical_json import canonical_sha256


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload or {}) if isinstance(payload, dict) else {}


def _write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _projection(payload: dict) -> dict:
    save_manifest = dict(payload.get("save_manifest") or {})
    projection = {
        "result": str(payload.get("result", "")).strip(),
        "refusal_code": str(payload.get("refusal_code", "")).strip(),
        "read_only_required": bool(payload.get("read_only_required", False)),
        "migration_applied": bool(payload.get("migration_applied", False)),
        "migration_required": bool(payload.get("migration_required", False)),
        "degrade_reasons": sorted(str(item).strip() for item in list(payload.get("degrade_reasons") or []) if str(item).strip()),
        "read_only_allowed": bool(payload.get("read_only_allowed", False)),
        "save_manifest_fingerprint": str(
            save_manifest.get("deterministic_fingerprint", "")
            or payload.get("save_manifest_fingerprint", "")
        ).strip(),
    }
    save_id = str(save_manifest.get("save_id", "") or payload.get("save_id", "")).strip()
    if save_id:
        projection["save_id"] = save_id
    save_format_version = str(save_manifest.get("save_format_version", "") or payload.get("save_format_version", "")).strip()
    if save_format_version:
        projection["save_format_version"] = save_format_version
    if save_manifest:
        projection["migration_chain_length"] = len(list(save_manifest.get("migration_chain") or []))
    elif "migration_chain_length" in payload:
        projection["migration_chain_length"] = int(payload.get("migration_chain_length", 0) or 0)
    return projection


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay deterministic save-open policy decisions.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--save-manifest", required=True)
    parser.add_argument("--instance-manifest", required=True)
    parser.add_argument("--install-manifest", required=True)
    parser.add_argument("--pack-lock", default="")
    parser.add_argument("--run-mode", default="play")
    parser.add_argument("--allow-read-only-fallback", action="store_true")
    parser.add_argument("--allow-save-migration", action="store_true")
    parser.add_argument("--migration-tick", default="0")
    parser.add_argument("--migration-id", default="")
    parser.add_argument("--recorded-decision", default="")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    save_manifest_path = os.path.normpath(os.path.abspath(str(args.save_manifest or "").strip()))
    instance_manifest_path = os.path.normpath(os.path.abspath(str(args.instance_manifest or "").strip()))
    install_manifest_path = os.path.normpath(os.path.abspath(str(args.install_manifest or "").strip()))
    pack_lock_path = str(args.pack_lock or "").strip()

    instance_manifest = _read_json(instance_manifest_path)
    install_manifest = _read_json(install_manifest_path)
    if pack_lock_path:
        pack_lock_payload = _read_json(os.path.normpath(os.path.abspath(pack_lock_path)))
    else:
        instance_root = os.path.dirname(instance_manifest_path)
        pack_lock_hash = str(instance_manifest.get("pack_lock_hash", "")).strip()
        pack_lock_payload = load_instance_json_artifact(instance_root, instance_manifest, "locks", pack_lock_hash)

    result = evaluate_save_open(
        repo_root=repo_root,
        save_manifest_path=save_manifest_path,
        instance_manifest=instance_manifest,
        install_manifest=install_manifest,
        pack_lock_payload=pack_lock_payload,
        run_mode=str(args.run_mode or "play").strip() or "play",
        instance_allow_read_only_fallback=bool(args.allow_read_only_fallback),
        allow_save_migration=bool(args.allow_save_migration),
        migration_tick=int(str(args.migration_tick or "0").strip() or "0"),
        migration_id=str(args.migration_id or "").strip(),
    )
    projection = _projection(result)
    replay_hash = canonical_sha256(projection)
    payload = {
        "result": str(result.get("result", "")).strip(),
        "refusal_code": str(result.get("refusal_code", "")).strip(),
        "save_open": projection,
        "replay_hash": replay_hash,
        "record_matches": True,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    recorded_path = str(args.recorded_decision or "").strip()
    if recorded_path:
        recorded = _read_json(os.path.normpath(os.path.abspath(recorded_path)))
        payload["recorded_replay_hash"] = canonical_sha256(_projection(recorded))
        payload["record_matches"] = str(payload["recorded_replay_hash"]) == str(replay_hash)
        if not payload["record_matches"]:
            payload["result"] = "refused"
            payload["refusal_code"] = "refusal.save.replay_mismatch"
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))

    output_path = str(args.output_path or "").strip()
    if output_path:
        _write_json(os.path.normpath(os.path.abspath(os.path.join(repo_root, output_path))), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(payload.get("result", "")).strip() == "complete" and bool(payload.get("record_matches", True)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
