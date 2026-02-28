"""STRICT test: ranked proof bundle export produces deterministic artifacts."""

from __future__ import annotations

import copy
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout


TEST_ID = "testx.net.ranked_proof_bundle_generated"
TEST_TAGS = ["strict", "net", "security"]


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _run_export(repo_root: str, argv_tail):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.net import tool_export_ranked_proof_bundle as export_tool

    old_argv = list(sys.argv)
    try:
        sys.argv = ["tool_export_ranked_proof_bundle.py"] + list(argv_tail)
        captured = io.StringIO()
        with redirect_stdout(captured):
            exit_code = int(export_tool.main())
    finally:
        sys.argv = old_argv
    raw = str(captured.getvalue() or "").strip()
    payload = {}
    if raw:
        try:
            payload = json.loads(raw)
        except ValueError:
            payload = {"raw": raw}
    return exit_code, payload


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ranked_proof_bundle_generated",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.rank_strict",
        server_profile_id="server.profile.rank_strict",
        server_policy_id="server.policy.ranked.strict",
        securex_policy_id="securex.policy.rank_strict",
    )
    lock_payload = copy.deepcopy(dict(fixture["lock_payload"]))
    lock_payload["resolved_packs"] = [
        dict(dict(row or {}), signature_status="signed")
        for row in list(lock_payload.get("resolved_packs") or [])
        if isinstance(row, dict)
    ]
    handshake = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=dict(fixture["session_spec"]),
        lock_payload=lock_payload,
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        securex_policy_registry=dict(fixture["securex_policy_registry"]),
        server_profile_registry=dict(fixture["server_profile_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )
    if str(handshake.get("result", "")) != "complete":
        return {"status": "fail", "message": "ranked handshake failed before proof bundle export"}

    temp_root = os.path.join(repo_root, "build", "test_ranked_proof_bundle_generated")
    if os.path.isdir(temp_root):
        shutil.rmtree(temp_root, ignore_errors=True)
    os.makedirs(temp_root, exist_ok=True)

    handshake_path = os.path.join(temp_root, "handshake.json")
    handshake_payload = {
        "schema_version": "1.0.0",
        "handshake_id": str(handshake.get("handshake_id", "")),
        "request": dict(handshake.get("request") or {}),
        "response": dict(handshake.get("handshake") or {}),
        "proto_hashes": dict(handshake.get("proto_hashes") or {}),
        "handshake_artifact_hash": str(handshake.get("handshake_artifact_hash", "")),
        "deterministic_artifact": True,
        "extensions": {},
    }
    _write_json(handshake_path, handshake_payload)

    events_rel = "build/test_ranked_proof_bundle_generated/anti_cheat.events.json"
    actions_rel = "build/test_ranked_proof_bundle_generated/anti_cheat.actions.json"
    manifest_rel = "build/test_ranked_proof_bundle_generated/anti_cheat.proof_manifest.json"
    _write_json(
        os.path.join(repo_root, events_rel.replace("/", os.sep)),
        {
            "rows": [
                {
                    "event_id": "ac.event.0001",
                    "tick": 0,
                    "peer_id": "peer.client.alpha",
                    "module_id": "ac.module.sequence_integrity",
                    "severity": "info",
                    "reason_code": "ac.sequence.ok",
                }
            ]
        },
    )
    _write_json(
        os.path.join(repo_root, actions_rel.replace("/", os.sep)),
        {
            "rows": [
                {
                    "action_id": "ac.action.0001",
                    "tick": 0,
                    "peer_id": "peer.client.alpha",
                    "module_id": "ac.module.sequence_integrity",
                    "action": "audit",
                }
            ]
        },
    )
    _write_json(
        os.path.join(repo_root, manifest_rel.replace("/", os.sep)),
        {
            "artifact_paths": {
                "actions": actions_rel,
                "anchor_mismatches": "",
                "events": events_rel,
                "refusal_injections": "",
            }
        },
    )

    out_dir_rel = "build/test_ranked_proof_bundle_generated/out"
    lock_path = os.path.join(repo_root, "build", "lockfile.json")
    argv_tail = [
        "--repo-root",
        repo_root,
        "--handshake-json",
        handshake_path,
        "--lockfile",
        lock_path,
        "--anti-cheat-manifest",
        os.path.join(repo_root, manifest_rel.replace("/", os.sep)),
        "--out-dir",
        out_dir_rel,
        "--out-prefix",
        "ranked_proof",
    ]
    exit_a, payload_a = _run_export(repo_root=repo_root, argv_tail=argv_tail)
    exit_b, payload_b = _run_export(repo_root=repo_root, argv_tail=argv_tail)
    if exit_a != 0 or exit_b != 0:
        return {"status": "fail", "message": "ranked proof bundle tool returned non-zero exit code"}
    if str(payload_a.get("result", "")) != "complete" or str(payload_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "ranked proof bundle tool did not report completion"}
    if str(payload_a.get("proof_bundle_hash", "")) != str(payload_b.get("proof_bundle_hash", "")):
        return {"status": "fail", "message": "ranked proof bundle hash is not deterministic across repeated exports"}

    bundle_rel = str(payload_a.get("json_path", ""))
    bundle_abs = os.path.join(repo_root, bundle_rel.replace("/", os.sep))
    if not os.path.isfile(bundle_abs):
        return {"status": "fail", "message": "ranked proof bundle JSON artifact missing"}
    bundle_payload = json.load(open(bundle_abs, "r", encoding="utf-8"))
    if str(bundle_payload.get("server_profile_id", "")) != "server.profile.rank_strict":
        return {"status": "fail", "message": "ranked proof bundle server_profile_id mismatch"}
    if str(bundle_payload.get("securex_policy_id", "")) != "securex.policy.rank_strict":
        return {"status": "fail", "message": "ranked proof bundle securex_policy_id mismatch"}
    if not isinstance(bundle_payload.get("control_ir_verification_report_hashes"), list):
        return {"status": "fail", "message": "ranked proof bundle missing control_ir_verification_report_hashes list"}
    if not isinstance(bundle_payload.get("control_decision_log_hashes"), list):
        return {"status": "fail", "message": "ranked proof bundle missing control_decision_log_hashes list"}
    return {"status": "pass", "message": "ranked proof bundle export is deterministic and complete"}
