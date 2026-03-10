"""Deterministic SERVER-MVP-1 probe helpers for local singleplayer orchestration."""

from __future__ import annotations

import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.client.local_server import (  # noqa: E402
    build_local_server_launch_spec,
    collect_local_client_messages,
    request_local_server_control,
    start_local_singleplayer,
    supervise_spawned_server_process,
)
from src.server.runtime.tick_loop import advance_server_tick  # noqa: E402
from tools.mvp.runtime_bundle import MVP_PACK_LOCK_REL, MVP_PROFILE_BUNDLE_REL  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


DEFAULT_LOCAL_SINGLEPLAYER_SEED = 0
DEFAULT_LOCAL_SINGLEPLAYER_TICKS = 6


def _ensure_repo_root(repo_root: str) -> str:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))
    if repo_root_abs not in sys.path:
        sys.path.insert(0, repo_root_abs)
    return repo_root_abs


def _step_controller(controller: dict, ticks: int) -> dict:
    rows = []
    log_rows = []
    response_rows = []
    tick_stream_rows = []
    boot = dict(controller.get("server_boot_payload") or {})
    for _idx in range(max(0, int(ticks or 0))):
        step = advance_server_tick(boot)
        if str(step.get("result", "")) != "complete":
            return dict(step)
        drained = collect_local_client_messages(controller)
        rows.append(
            {
                "tick": int(step.get("tick", 0) or 0),
                "proof_anchor_path": str(step.get("proof_anchor_path", "")).strip(),
                "control_rows": list((dict(step.get("control_channel") or {})).get("control_rows") or []),
            }
        )
        log_rows.extend(list(drained.get("log_events") or []))
        response_rows.extend(list(drained.get("control_responses") or []))
        tick_stream_rows.extend(list(drained.get("tick_stream") or []))
    return {
        "result": "complete",
        "steps": rows,
        "log_rows": log_rows,
        "response_rows": response_rows,
        "tick_stream_rows": tick_stream_rows,
    }


def run_local_singleplayer_window(
    repo_root: str = REPO_ROOT_HINT,
    *,
    seed: int = DEFAULT_LOCAL_SINGLEPLAYER_SEED,
    ticks: int = DEFAULT_LOCAL_SINGLEPLAYER_TICKS,
    save_suffix: str = "replay",
) -> dict:
    repo_root_abs = _ensure_repo_root(repo_root)
    save_id = "save.server_mvp1.{}".format(str(save_suffix).strip() or "replay")
    started = start_local_singleplayer(
        repo_root=repo_root_abs,
        seed=str(int(seed)),
        profile_bundle_path=MVP_PROFILE_BUNDLE_REL,
        pack_lock_path=MVP_PACK_LOCK_REL,
        save_id=save_id,
    )
    if str(started.get("result", "")) != "complete":
        return dict(started)

    controller = dict(started.get("controller") or {})
    launch_spec = dict(started.get("launch_spec") or {})
    status_request = request_local_server_control(controller, request_kind="status", payload={})
    status_step = _step_controller(controller, 1)
    snapshot_output = os.path.join(
        repo_root_abs,
        "build",
        "client",
        "local_singleplayer",
        save_id,
        "snapshots",
        "from_control.tick.stub.json",
    )
    snapshot_request = request_local_server_control(
        controller,
        request_kind="save_snapshot",
        payload={"output_path": snapshot_output},
    )
    snapshot_step = _step_controller(controller, 1)
    remaining = _step_controller(controller, max(0, int(ticks or 0) - 2))

    runtime = dict((dict(controller.get("server_boot_payload") or {})).get("runtime") or {})
    server = dict(runtime.get("server") or {})
    meta = dict(runtime.get("server_mvp") or {})
    anchors = [dict(row) for row in list(runtime.get("server_mvp_proof_anchors") or []) if isinstance(row, dict)]
    all_logs = list(status_step.get("log_rows") or []) + list(snapshot_step.get("log_rows") or []) + list(remaining.get("log_rows") or [])
    all_responses = (
        list(status_step.get("response_rows") or [])
        + list(snapshot_step.get("response_rows") or [])
        + list(remaining.get("response_rows") or [])
    )
    all_tick_stream = (
        list(status_step.get("tick_stream_rows") or [])
        + list(snapshot_step.get("tick_stream_rows") or [])
        + list(remaining.get("tick_stream_rows") or [])
    )
    summary = {
        "result": "complete",
        "save_id": save_id,
        "launch_mode": str(launch_spec.get("launch_mode", "")).strip(),
        "server_profile_id": str(launch_spec.get("server_profile_id", "")).strip(),
        "spawn_args": list((dict(launch_spec.get("process_spec") or {})).get("args") or []),
        "spawn_args_hash": canonical_sha256(list((dict(launch_spec.get("process_spec") or {})).get("args") or [])),
        "readiness": dict(started.get("readiness") or {}),
        "ack_payload_schema_id": str((dict(started.get("ack_proto") or {})).get("payload_schema_id", "")).strip(),
        "status_request_result": str(status_request.get("result", "")).strip(),
        "snapshot_request_result": str(snapshot_request.get("result", "")).strip(),
        "control_response_kinds": [str(row.get("request_kind", "")).strip() for row in all_responses],
        "control_response_results": [str(row.get("result", "")).strip() for row in all_responses],
        "log_event_count": len(all_logs),
        "log_sources": sorted(set(str(row.get("source", "")).strip() for row in all_logs if str(row.get("source", "")).strip())),
        "tick_stream_ticks": [int(row.get("tick", 0) or 0) for row in all_tick_stream],
        "proof_anchor_ticks": [int(row.get("tick", 0) or 0) for row in anchors],
        "proof_anchor_hashes": [canonical_sha256(row) for row in anchors],
        "contract_bundle_hash": str(meta.get("contract_bundle_hash", "")).strip(),
        "semantic_contract_registry_hash": str(meta.get("semantic_contract_registry_hash", "")).strip(),
        "overlay_manifest_hash": str(meta.get("overlay_manifest_hash", "")).strip(),
        "final_tick": int(server.get("network_tick", 0) or 0),
        "tick_hash": str(server.get("last_tick_hash", "")).strip(),
        "snapshot_output_exists": os.path.isfile(snapshot_output),
        "deterministic_fingerprint": "",
    }
    summary["cross_platform_local_orch_hash"] = canonical_sha256(
        {
            "launch_mode": str(summary.get("launch_mode", "")),
            "server_profile_id": str(summary.get("server_profile_id", "")),
            "readiness": dict(summary.get("readiness") or {}),
            "control_response_kinds": list(summary.get("control_response_kinds") or []),
            "proof_anchor_hashes": list(summary.get("proof_anchor_hashes") or []),
            "tick_hash": str(summary.get("tick_hash", "")),
            "contract_bundle_hash": str(summary.get("contract_bundle_hash", "")),
            "semantic_contract_registry_hash": str(summary.get("semantic_contract_registry_hash", "")),
        }
    )
    summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
    return summary


def verify_local_singleplayer_replay(repo_root: str = REPO_ROOT_HINT) -> dict:
    repo_root_abs = _ensure_repo_root(repo_root)
    first = run_local_singleplayer_window(repo_root_abs, save_suffix="verify")
    second = run_local_singleplayer_window(repo_root_abs, save_suffix="verify")
    stable = canonical_sha256(first) == canonical_sha256(second)
    return {
        "result": "complete" if stable else "refused",
        "stable": bool(stable),
        "first_report": first,
        "second_report": second,
        "deterministic_fingerprint": canonical_sha256({"first": first, "second": second}),
    }


def crash_diag_report(repo_root: str = REPO_ROOT_HINT) -> dict:
    repo_root_abs = _ensure_repo_root(repo_root)
    launch = build_local_server_launch_spec(
        repo_root=repo_root_abs,
        seed=str(DEFAULT_LOCAL_SINGLEPLAYER_SEED),
        profile_bundle_path=MVP_PROFILE_BUNDLE_REL,
        pack_lock_path=MVP_PACK_LOCK_REL,
        save_id="save.server_mvp1.crash_diag",
    )
    if str(launch.get("result", "")) != "complete":
        return dict(launch)
    process_spec = dict(launch.get("process_spec") or {})
    process_spec["script_rel"] = "-c"
    process_spec["args"] = ["-c", "import sys; sys.stderr.write('server_mvp1 crash probe\\n'); raise SystemExit(17)"]
    process_spec["deterministic_fingerprint"] = canonical_sha256(dict(process_spec, deterministic_fingerprint=""))
    return supervise_spawned_server_process(
        repo_root=repo_root_abs,
        process_spec=process_spec,
        session_spec=dict(launch.get("session_spec") or {}),
        save_id=str(launch.get("save_id", "")).strip(),
    )


__all__ = [
    "DEFAULT_LOCAL_SINGLEPLAYER_SEED",
    "DEFAULT_LOCAL_SINGLEPLAYER_TICKS",
    "crash_diag_report",
    "run_local_singleplayer_window",
    "verify_local_singleplayer_replay",
]
