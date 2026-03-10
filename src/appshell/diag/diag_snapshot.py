"""Deterministic diagnostic snapshot bundles for AppShell."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Mapping

from src.appshell.logging import append_jsonl


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in value]
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    out_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(_normalize_tree(dict(payload or {}))), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")
    return out_path


def _load_proof_anchor_rows(proof_anchor_dir: str, limit: int) -> list[dict]:
    root = os.path.normpath(os.path.abspath(str(proof_anchor_dir or "")))
    if not root or not os.path.isdir(root):
        return []
    rows = []
    for name in sorted(entry for entry in os.listdir(root) if entry.endswith(".json"))[-max(0, int(limit or 0)) :]:
        payload = _load_json(os.path.join(root, name))
        if payload:
            rows.append(payload)
    return rows


def _write_replay_instructions(path: str, *, product_id: str, bundle_dir: str) -> str:
    out_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    lines = [
        "Dominium AppShell diagnostic snapshot",
        "product_id: {}".format(str(product_id).strip()),
        "bundle_dir: {}".format(str(bundle_dir).replace("\\", "/")),
        "Use the recorded endpoint descriptor, session spec, pack lock, log tail, and proof anchors to replay the failing surface deterministically.",
    ]
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    return out_path


def write_diag_snapshot_bundle(
    *,
    repo_root: str,
    product_id: str,
    descriptor_payload: Mapping[str, object],
    out_dir: str = "",
    session_spec_path: str = "",
    pack_lock_path: str = "",
    contract_bundle_hash: str = "",
    proof_anchor_dir: str = "",
    log_events: list[Mapping[str, object]] | None = None,
    log_tail: int = 32,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    bundle_dir = os.path.normpath(
        os.path.abspath(
            str(out_dir)
            if str(out_dir or "").strip()
            else os.path.join(repo_root_abs, "build", "appshell", "diag", str(product_id or "product"))
        )
    )
    os.makedirs(bundle_dir, exist_ok=True)

    session_spec_abs = os.path.normpath(os.path.abspath(str(session_spec_path))) if str(session_spec_path or "").strip() else ""
    pack_lock_abs = os.path.normpath(os.path.abspath(str(pack_lock_path))) if str(pack_lock_path or "").strip() else ""
    session_spec_payload = _load_json(session_spec_abs) if session_spec_abs else {}
    pack_lock_payload = _load_json(pack_lock_abs) if pack_lock_abs else {}
    log_rows = [dict(_normalize_tree(dict(row))) for row in list(log_events or [])[-max(0, int(log_tail or 0)) :]]
    proof_rows = _load_proof_anchor_rows(proof_anchor_dir, limit=max(0, int(log_tail or 0)))

    descriptor_path = _write_json(os.path.join(bundle_dir, "endpoint_descriptor.json"), descriptor_payload)
    session_spec_out = _write_json(os.path.join(bundle_dir, "session_spec.json"), session_spec_payload)
    pack_lock_out = _write_json(os.path.join(bundle_dir, "pack_lock.json"), pack_lock_payload)

    log_path = os.path.join(bundle_dir, "log_events.jsonl")
    if os.path.exists(log_path):
        os.remove(log_path)
    for row in log_rows:
        append_jsonl(log_path, row)
    proof_path = _write_json(os.path.join(bundle_dir, "proof_anchors.json"), {"proof_anchors": proof_rows})
    replay_path = _write_replay_instructions(
        os.path.join(bundle_dir, "replay_instructions.txt"),
        product_id=product_id,
        bundle_dir=bundle_dir,
    )

    manifest = {
        "schema_version": "1.0.0",
        "product_id": str(product_id or "").strip(),
        "bundle_dir": bundle_dir.replace("\\", "/"),
        "contract_bundle_hash": str(contract_bundle_hash or session_spec_payload.get("contract_bundle_hash", "")).strip(),
        "endpoint_descriptor_hash": str(dict(descriptor_payload or {}).get("descriptor_hash", "")).strip()
        or str(dict(dict(descriptor_payload or {}).get("descriptor") or {}).get("deterministic_fingerprint", "")).strip(),
        "session_id": str(session_spec_payload.get("save_id", "")).strip(),
        "log_event_count": int(len(log_rows)),
        "proof_anchor_count": int(len(proof_rows)),
        "files": {
            "endpoint_descriptor": os.path.basename(descriptor_path),
            "session_spec": os.path.basename(session_spec_out),
            "pack_lock": os.path.basename(pack_lock_out),
            "log_events": os.path.basename(log_path),
            "proof_anchors": os.path.basename(proof_path),
            "replay_instructions": os.path.basename(replay_path),
        },
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    manifest["deterministic_fingerprint"] = _fingerprint(manifest)
    manifest_path = _write_json(os.path.join(bundle_dir, "diag_manifest.json"), manifest)
    return {
        "result": "complete",
        "bundle_dir": bundle_dir.replace("\\", "/"),
        "manifest_path": manifest_path.replace("\\", "/"),
        "manifest": manifest,
    }


__all__ = ["write_diag_snapshot_bundle"]
