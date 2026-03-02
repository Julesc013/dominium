#!/usr/bin/env python3
"""Export deterministic ranked proof bundles from run-meta/network artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload
from tools.xstack.sessionx.common import norm, read_json_object, write_canonical_json


TOOL_VERSION = "1.0.0"


def _repo_root(raw: str) -> str:
    token = str(raw).strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def _refusal(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, object]) -> Dict[str, object]:
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": dict(relevant_ids or {}),
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": "$",
            }
        ],
    }


def _load_json(abs_path: str) -> Tuple[dict, str]:
    payload, err = read_json_object(abs_path)
    if err:
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _abs(repo_root: str, raw_path: str) -> str:
    token = str(raw_path).strip()
    if not token:
        return ""
    candidate = os.path.normpath(token.replace("/", os.sep))
    if os.path.isabs(candidate):
        return candidate
    return os.path.normpath(os.path.join(repo_root, candidate))


def _latest_file(abs_dir: str, prefix: str) -> str:
    if not os.path.isdir(abs_dir):
        return ""
    rows = []
    for name in sorted(os.listdir(abs_dir)):
        if not str(name).startswith(prefix):
            continue
        if not str(name).lower().endswith(".json"):
            continue
        rows.append(os.path.join(abs_dir, name))
    return sorted(rows)[-1] if rows else ""


def _sorted_registry_hashes(payload: dict) -> dict:
    rows = dict(payload or {})
    return dict((key, rows[key]) for key in sorted(rows.keys()))


def _pack_signatures(lock_payload: dict) -> List[dict]:
    rows = []
    for row in sorted(
        (dict(item) for item in (lock_payload.get("resolved_packs") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("pack_id", "")),
    ):
        rows.append(
            {
                "pack_id": str(row.get("pack_id", "")),
                "version": str(row.get("version", "")),
                "canonical_hash": str(row.get("canonical_hash", "")),
                "signature_status": str(row.get("signature_status", "")),
            }
        )
    return rows


def _load_anchor_rows(run_meta: dict, anchor_json_abs: str) -> Tuple[List[dict], str]:
    if anchor_json_abs:
        payload, err = _load_json(anchor_json_abs)
        if err:
            return [], "invalid hash anchor artifact"
        rows = payload.get("hash_anchor_frames")
        if isinstance(rows, list):
            return sorted((dict(row) for row in rows if isinstance(row, dict)), key=lambda row: int(row.get("tick", 0) or 0)), ""
        return [], "hash anchor artifact missing hash_anchor_frames list"
    rows = run_meta.get("hash_anchor_frames")
    if isinstance(rows, list):
        return sorted((dict(row) for row in rows if isinstance(row, dict)), key=lambda row: int(row.get("tick", 0) or 0)), ""
    return [], ""


def _load_anti_cheat_rows(repo_root: str, run_meta: dict, manifest_abs: str) -> Tuple[Dict[str, List[dict]], str]:
    selected_manifest_abs = manifest_abs
    if not selected_manifest_abs:
        save_id = str(run_meta.get("save_id", "")).strip()
        if save_id:
            default_dir = os.path.join(
                repo_root,
                "build",
                "net",
                "anti_cheat",
                save_id.replace("/", os.sep),
                "run_meta",
                "anti_cheat",
            )
            selected_manifest_abs = _latest_file(default_dir, "anti_cheat.proof_manifest.")
    if not selected_manifest_abs:
        return {
            "events": [],
            "actions": [],
            "anchor_mismatches": [],
            "refusal_injections": [],
            "manifest_path": "",
        }, ""

    manifest_payload, manifest_err = _load_json(selected_manifest_abs)
    if manifest_err:
        return {}, "invalid anti-cheat proof manifest"
    artifact_paths = dict(manifest_payload.get("artifact_paths") or {})
    rows = {
        "events": [],
        "actions": [],
        "anchor_mismatches": [],
        "refusal_injections": [],
        "manifest_path": norm(os.path.relpath(selected_manifest_abs, repo_root)),
    }
    for key in ("events", "actions", "anchor_mismatches", "refusal_injections"):
        rel_path = str(artifact_paths.get(key, "")).strip()
        if not rel_path:
            continue
        artifact_abs = _abs(repo_root, rel_path)
        artifact_payload, artifact_err = _load_json(artifact_abs)
        if artifact_err:
            return {}, "invalid anti-cheat artifact '{}'".format(rel_path)
        values = artifact_payload.get("rows")
        if not isinstance(values, list):
            return {}, "anti-cheat artifact '{}' missing rows[]".format(rel_path)
        rows[key] = sorted(
            (dict(item) for item in values if isinstance(item, dict)),
            key=lambda item: canonical_sha256(item),
        )
    return rows, ""


def _load_control_ir_verification_hashes(repo_root: str, run_meta: dict, run_meta_abs: str) -> Tuple[dict, str]:
    candidate_dirs: List[str] = []
    if run_meta_abs:
        run_meta_dir = os.path.dirname(run_meta_abs)
        candidate_dirs.append(os.path.join(run_meta_dir, "control_decisions"))
    for key in ("control_ir_decision_log_dir", "control_decision_log_dir"):
        token = str(run_meta.get(key, "")).strip()
        if token:
            candidate_dirs.append(_abs(repo_root, token))
    candidate_dirs.append(os.path.join(repo_root, "run_meta", "control_decisions"))

    unique_dirs: List[str] = []
    for path in candidate_dirs:
        normalized = os.path.normpath(str(path or ""))
        if not normalized or normalized in unique_dirs:
            continue
        unique_dirs.append(normalized)

    verification_hashes = set()
    decision_log_hashes = set()
    scanned_files = 0
    for directory in unique_dirs:
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if not str(name).lower().endswith(".json"):
                continue
            abs_path = os.path.join(directory, name)
            payload, err = _load_json(abs_path)
            if err:
                return {}, "invalid control decision log '{}'".format(norm(os.path.relpath(abs_path, repo_root)))
            ext = dict(payload.get("extensions") or {})
            ir_ext = dict(ext.get("control_ir_execution") or {})
            report_hash = str(ir_ext.get("verification_report_hash", "")).strip()
            if report_hash:
                verification_hashes.add(report_hash)
            decision_hash = str(payload.get("deterministic_fingerprint", "")).strip()
            if not decision_hash:
                decision_hash = canonical_sha256(payload)
            if decision_hash:
                decision_log_hashes.add(decision_hash)
            scanned_files += 1
    return {
        "verification_report_hashes": sorted(verification_hashes),
        "decision_log_hashes": sorted(decision_log_hashes),
        "decision_log_count": int(scanned_files),
        "decision_log_dirs": [
            norm(os.path.relpath(path, repo_root))
            for path in unique_dirs
            if os.path.isdir(path)
        ],
    }, ""


def _load_mobility_proof_hashes(repo_root: str, run_meta: dict, run_meta_abs: str) -> Tuple[dict, str]:
    candidate_dirs: List[str] = []
    if run_meta_abs:
        run_meta_dir = os.path.dirname(run_meta_abs)
        candidate_dirs.append(os.path.join(run_meta_dir, "control_proofs"))
    last_ref = str(run_meta.get("control_proof_bundle_ref", "")).strip()
    if last_ref:
        ref_abs = _abs(repo_root, last_ref)
        if ref_abs:
            candidate_dirs.append(os.path.dirname(ref_abs))
    candidate_dirs.append(os.path.join(repo_root, "run_meta", "control_proofs"))

    unique_dirs: List[str] = []
    for path in candidate_dirs:
        normalized = os.path.normpath(str(path or ""))
        if not normalized or normalized in unique_dirs:
            continue
        unique_dirs.append(normalized)

    mobility_event_hashes = set()
    congestion_hashes = set()
    signal_state_hashes = set()
    derailment_hashes = set()
    bundle_refs = set()
    scanned_files = 0
    for directory in unique_dirs:
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if not str(name).lower().endswith(".json"):
                continue
            abs_path = os.path.join(directory, name)
            payload, err = _load_json(abs_path)
            if err:
                return {}, "invalid control proof bundle '{}'".format(norm(os.path.relpath(abs_path, repo_root)))
            for key, sink in (
                ("mobility_event_hash", mobility_event_hashes),
                ("congestion_hash", congestion_hashes),
                ("signal_state_hash", signal_state_hashes),
                ("derailment_hash", derailment_hashes),
            ):
                token = str(payload.get(key, "")).strip()
                if token:
                    sink.add(token)
            bundle_ref = norm(os.path.relpath(abs_path, repo_root))
            if bundle_ref:
                bundle_refs.add(bundle_ref)
            scanned_files += 1

    return {
        "mobility_event_hashes": sorted(mobility_event_hashes),
        "congestion_hashes": sorted(congestion_hashes),
        "signal_state_hashes": sorted(signal_state_hashes),
        "derailment_hashes": sorted(derailment_hashes),
        "control_proof_bundle_refs": sorted(bundle_refs),
        "control_proof_bundle_count": int(scanned_files),
        "control_proof_dirs": [
            norm(os.path.relpath(path, repo_root))
            for path in unique_dirs
            if os.path.isdir(path)
        ],
    }, ""


def _build_markdown(bundle: dict) -> str:
    pack_signatures = list(bundle.get("pack_signatures") or [])
    hash_anchors = list(bundle.get("hash_anchor_frames") or [])
    anti_cheat_events = list(bundle.get("anti_cheat_events") or [])
    anti_cheat_actions = list(bundle.get("enforcement_actions") or [])
    ir_hashes = list(bundle.get("control_ir_verification_report_hashes") or [])
    decision_hashes = list(bundle.get("control_decision_log_hashes") or [])
    mobility_event_hashes = list(bundle.get("mobility_event_hashes") or [])
    congestion_hashes = list(bundle.get("congestion_hashes") or [])
    signal_state_hashes = list(bundle.get("signal_state_hashes") or [])
    derailment_hashes = list(bundle.get("derailment_hashes") or [])
    lines = [
        "# Ranked Proof Bundle",
        "",
        "- Status: `DERIVED`",
        "- Proof Bundle ID: `{}`".format(str(bundle.get("proof_bundle_id", ""))),
        "- Bundle Hash: `{}`".format(str(bundle.get("proof_bundle_hash", ""))),
        "- Server Profile ID: `{}`".format(str(bundle.get("server_profile_id", ""))),
        "- SecureX Policy ID: `{}`".format(str(bundle.get("securex_policy_id", ""))),
        "- Anti-Cheat Policy ID: `{}`".format(str(bundle.get("anti_cheat_policy_id", ""))),
        "- Pack Lock Hash: `{}`".format(str(bundle.get("pack_lock_hash", ""))),
        "- Pack Signatures: `{}`".format(int(len(pack_signatures))),
        "- Hash Anchor Frames: `{}`".format(int(len(hash_anchors))),
        "- Anti-Cheat Events: `{}`".format(int(len(anti_cheat_events))),
        "- Enforcement Actions: `{}`".format(int(len(anti_cheat_actions))),
        "- Control IR Verification Hashes: `{}`".format(int(len(ir_hashes))),
        "- Control Decision Hashes: `{}`".format(int(len(decision_hashes))),
        "- Mobility Event Hashes: `{}`".format(int(len(mobility_event_hashes))),
        "- Congestion Hashes: `{}`".format(int(len(congestion_hashes))),
        "- Signal State Hashes: `{}`".format(int(len(signal_state_hashes))),
        "- Derailment Hashes: `{}`".format(int(len(derailment_hashes))),
        "",
        "## Registry Hashes",
    ]
    for key, value in sorted(dict(bundle.get("registry_hashes") or {}).items(), key=lambda item: item[0]):
        lines.append("- `{}`: `{}`".format(str(key), str(value)))
    lines.append("")
    lines.append("## Source Artifacts")
    source = dict(bundle.get("source_artifacts") or {})
    for key in (
        "run_meta_path",
        "handshake_path",
        "lockfile_path",
        "anti_cheat_manifest_path",
        "hash_anchor_path",
        "control_ir_decision_log_dirs",
        "control_proof_dirs",
    ):
        lines.append("- `{}`: `{}`".format(key, str(source.get(key, "")) or "<none>"))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic ranked proof bundles.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--run-meta", default="")
    parser.add_argument("--handshake-json", default="")
    parser.add_argument("--lockfile", default="")
    parser.add_argument("--anti-cheat-manifest", default="")
    parser.add_argument("--hash-anchors-json", default="")
    parser.add_argument("--out-dir", default="build/net/proofs")
    parser.add_argument("--out-prefix", default="ranked_proof_bundle")
    args = parser.parse_args()

    repo_root = _repo_root(str(args.repo_root))
    run_meta_abs = _abs(repo_root, str(args.run_meta))
    run_meta = {}
    if run_meta_abs:
        run_meta, run_meta_err = _load_json(run_meta_abs)
        if run_meta_err:
            print(
                json.dumps(
                    _refusal(
                        "refusal.net.envelope_invalid",
                        "run-meta artifact is missing or invalid",
                        "Provide a valid run-meta JSON path.",
                        {"run_meta_path": norm(run_meta_abs)},
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    handshake_abs = _abs(repo_root, str(args.handshake_json))
    if not handshake_abs and run_meta:
        handshake_abs = _abs(repo_root, str(run_meta.get("handshake_artifact_path", "")))
    if not handshake_abs:
        print(
            json.dumps(
                _refusal(
                    "refusal.net.envelope_invalid",
                    "handshake artifact is required for ranked proof export",
                    "Provide --handshake-json or run-meta with handshake_artifact_path.",
                    {"command_id": "tool_export_ranked_proof_bundle"},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    handshake_payload, handshake_err = _load_json(handshake_abs)
    if handshake_err:
        print(
            json.dumps(
                _refusal(
                    "refusal.net.envelope_invalid",
                    "handshake artifact is missing or invalid",
                    "Provide a valid handshake artifact JSON.",
                    {"handshake_path": norm(handshake_abs)},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    lock_abs = _abs(repo_root, str(args.lockfile))
    if not lock_abs and run_meta:
        lock_abs = _abs(repo_root, str(run_meta.get("lockfile_path", "")))
    if not lock_abs:
        lock_abs = os.path.join(repo_root, "build", "lockfile.json")
    lock_payload, lock_err = _load_json(lock_abs)
    if lock_err:
        print(
            json.dumps(
                _refusal(
                    "LOCKFILE_MISMATCH",
                    "lockfile artifact is missing or invalid",
                    "Provide --lockfile or run-meta with lockfile_path.",
                    {"lockfile_path": norm(lock_abs)},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    lock_check = validate_lockfile_payload(lock_payload)
    if str(lock_check.get("result", "")) != "complete":
        print(
            json.dumps(
                _refusal(
                    "LOCKFILE_MISMATCH",
                    "lockfile failed deterministic validation",
                    "Rebuild lockfile before exporting ranked proof bundle.",
                    {"lockfile_path": norm(lock_abs)},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    anchor_abs = _abs(repo_root, str(args.hash_anchors_json))
    hash_anchor_frames, anchors_err = _load_anchor_rows(run_meta=run_meta, anchor_json_abs=anchor_abs)
    if anchors_err:
        print(
            json.dumps(
                _refusal(
                    "refusal.net.envelope_invalid",
                    anchors_err,
                    "Provide valid --hash-anchors-json or remove the flag.",
                    {"hash_anchor_path": norm(anchor_abs)},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    anti_cheat_manifest_abs = _abs(repo_root, str(args.anti_cheat_manifest))
    anti_cheat_rows, anti_cheat_err = _load_anti_cheat_rows(
        repo_root=repo_root,
        run_meta=run_meta,
        manifest_abs=anti_cheat_manifest_abs,
    )
    if anti_cheat_err:
        print(
            json.dumps(
                _refusal(
                    "refusal.net.envelope_invalid",
                    anti_cheat_err,
                    "Provide valid anti-cheat proof artifacts or omit them for empty sections.",
                    {"anti_cheat_manifest_path": norm(anti_cheat_manifest_abs)},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    control_ir_hashes, control_ir_hashes_err = _load_control_ir_verification_hashes(
        repo_root=repo_root,
        run_meta=run_meta,
        run_meta_abs=run_meta_abs,
    )
    if control_ir_hashes_err:
        print(
            json.dumps(
                _refusal(
                    "refusal.net.envelope_invalid",
                    control_ir_hashes_err,
                    "Repair control decision-log artifacts before exporting ranked proof bundle.",
                    {"run_meta_path": norm(run_meta_abs) if run_meta_abs else ""},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    mobility_hashes, mobility_hashes_err = _load_mobility_proof_hashes(
        repo_root=repo_root,
        run_meta=run_meta,
        run_meta_abs=run_meta_abs,
    )
    if mobility_hashes_err:
        print(
            json.dumps(
                _refusal(
                    "refusal.net.envelope_invalid",
                    mobility_hashes_err,
                    "Repair control proof artifacts before exporting ranked proof bundle.",
                    {"run_meta_path": norm(run_meta_abs) if run_meta_abs else ""},
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    handshake_response = dict(handshake_payload.get("response") or {})
    network_handshake = dict(run_meta.get("network_handshake") or {})
    securex_policy_id = str(handshake_response.get("securex_policy_id", "")).strip() or str(network_handshake.get("securex_policy_id", "")).strip()
    anti_cheat_policy_id = str(handshake_response.get("anti_cheat_policy_id", "")).strip() or str(network_handshake.get("anti_cheat_policy_id", "")).strip()
    server_profile_id = str(handshake_response.get("server_profile_id", "")).strip() or str(network_handshake.get("server_profile_id", "")).strip()

    pack_lock_hash = str(lock_payload.get("pack_lock_hash", "")).strip()
    registry_hashes = _sorted_registry_hashes(lock_payload.get("registries") or {})
    pack_signatures = _pack_signatures(lock_payload)
    anti_cheat_events = list(anti_cheat_rows.get("events") or [])
    enforcement_actions = list(anti_cheat_rows.get("actions") or [])
    ir_verification_report_hashes = list(control_ir_hashes.get("verification_report_hashes") or [])
    control_decision_log_hashes = list(control_ir_hashes.get("decision_log_hashes") or [])
    mobility_event_hashes = list(mobility_hashes.get("mobility_event_hashes") or [])
    congestion_hashes = list(mobility_hashes.get("congestion_hashes") or [])
    signal_state_hashes = list(mobility_hashes.get("signal_state_hashes") or [])
    derailment_hashes = list(mobility_hashes.get("derailment_hashes") or [])

    deterministic_seed = {
        "pack_lock_hash": pack_lock_hash,
        "registry_hashes": registry_hashes,
        "handshake_hash": canonical_sha256(handshake_payload),
        "pack_signatures_hash": canonical_sha256(pack_signatures),
        "hash_anchor_frames_hash": canonical_sha256(hash_anchor_frames),
        "anti_cheat_events_hash": canonical_sha256(anti_cheat_events),
        "enforcement_actions_hash": canonical_sha256(enforcement_actions),
        "control_ir_verification_report_hashes_hash": canonical_sha256(ir_verification_report_hashes),
        "control_decision_log_hashes_hash": canonical_sha256(control_decision_log_hashes),
        "mobility_event_hashes_hash": canonical_sha256(mobility_event_hashes),
        "congestion_hashes_hash": canonical_sha256(congestion_hashes),
        "signal_state_hashes_hash": canonical_sha256(signal_state_hashes),
        "derailment_hashes_hash": canonical_sha256(derailment_hashes),
    }
    proof_bundle_hash = canonical_sha256(deterministic_seed)
    proof_bundle_id = "ranked.proof.{}".format(proof_bundle_hash[:16])

    bundle = {
        "schema_version": "1.0.0",
        "proof_bundle_id": proof_bundle_id,
        "server_profile_id": server_profile_id,
        "securex_policy_id": securex_policy_id,
        "anti_cheat_policy_id": anti_cheat_policy_id,
        "pack_lock_hash": pack_lock_hash,
        "registry_hashes": registry_hashes,
        "handshake": {
            "request": dict(handshake_payload.get("request") or {}),
            "response": handshake_response,
            "handshake_artifact_hash": str(handshake_payload.get("handshake_artifact_hash", "")),
        },
        "pack_signatures": pack_signatures,
        "hash_anchor_frames": hash_anchor_frames,
        "anti_cheat_events": anti_cheat_events,
        "enforcement_actions": enforcement_actions,
        "control_ir_verification_report_hashes": ir_verification_report_hashes,
        "control_decision_log_hashes": control_decision_log_hashes,
        "mobility_event_hashes": mobility_event_hashes,
        "congestion_hashes": congestion_hashes,
        "signal_state_hashes": signal_state_hashes,
        "derailment_hashes": derailment_hashes,
        "source_artifacts": {
            "run_meta_path": norm(os.path.relpath(run_meta_abs, repo_root)) if run_meta_abs else "",
            "handshake_path": norm(os.path.relpath(handshake_abs, repo_root)),
            "lockfile_path": norm(os.path.relpath(lock_abs, repo_root)),
            "anti_cheat_manifest_path": str(anti_cheat_rows.get("manifest_path", "")),
            "hash_anchor_path": norm(os.path.relpath(anchor_abs, repo_root)) if anchor_abs else "",
            "control_ir_decision_log_dirs": list(control_ir_hashes.get("decision_log_dirs") or []),
            "control_proof_dirs": list(mobility_hashes.get("control_proof_dirs") or []),
        },
        "provenance": {
            "artifact_type_id": "net.ranked_proof_bundle",
            "source_pack_id": str(lock_payload.get("bundle_id", "")),
            "source_hash": canonical_sha256({"pack_lock_hash": pack_lock_hash, "registry_hashes": registry_hashes}),
            "generator_tool_id": "tool_export_ranked_proof_bundle",
            "generator_tool_version": TOOL_VERSION,
            "schema_version": "1.0.0",
            "input_merkle_hash": canonical_sha256(deterministic_seed),
            "pack_lock_hash": pack_lock_hash,
            "deterministic": True,
        },
        "extensions": {
            "control_ir_decision_log_count": int(control_ir_hashes.get("decision_log_count", 0) or 0),
            "control_decision_log_hash_count": int(len(control_decision_log_hashes)),
            "control_proof_bundle_count": int(mobility_hashes.get("control_proof_bundle_count", 0) or 0),
            "mobility_event_hash_count": int(len(mobility_event_hashes)),
            "congestion_hash_count": int(len(congestion_hashes)),
            "signal_state_hash_count": int(len(signal_state_hashes)),
            "derailment_hash_count": int(len(derailment_hashes)),
        },
    }
    bundle["proof_bundle_hash"] = canonical_sha256(bundle)

    out_dir_abs = _abs(repo_root, str(args.out_dir)) or os.path.join(repo_root, "build", "net", "proofs")
    if not os.path.isdir(out_dir_abs):
        os.makedirs(out_dir_abs, exist_ok=True)
    out_prefix = str(args.out_prefix).strip() or "ranked_proof_bundle"
    json_abs = os.path.join(out_dir_abs, "{}.json".format(out_prefix))
    md_abs = os.path.join(out_dir_abs, "{}.md".format(out_prefix))
    write_canonical_json(json_abs, bundle)
    with open(md_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_build_markdown(bundle))

    response = {
        "result": "complete",
        "proof_bundle_id": str(bundle.get("proof_bundle_id", "")),
        "proof_bundle_hash": str(bundle.get("proof_bundle_hash", "")),
        "json_path": norm(os.path.relpath(json_abs, repo_root)),
        "markdown_path": norm(os.path.relpath(md_abs, repo_root)),
        "counts": {
            "pack_signatures": len(pack_signatures),
            "hash_anchor_frames": len(hash_anchor_frames),
            "anti_cheat_events": len(anti_cheat_events),
            "enforcement_actions": len(enforcement_actions),
            "control_ir_verification_report_hashes": len(ir_verification_report_hashes),
            "control_decision_log_hashes": len(control_decision_log_hashes),
            "mobility_event_hashes": len(mobility_event_hashes),
            "congestion_hashes": len(congestion_hashes),
            "signal_state_hashes": len(signal_state_hashes),
            "derailment_hashes": len(derailment_hashes),
        },
    }
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
