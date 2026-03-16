"""Deterministic AppShell supervisor engine and local orchestration helpers."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import threading
from typing import Mapping, Sequence

from src.diag import write_repro_bundle
from src.engine.concurrency import build_field_sort_key, canonicalize_parallel_mapping_rows
from src.appshell.ipc import (
    attach_ipc_endpoint,
    discover_ipc_endpoints,
    query_ipc_log_events,
    query_ipc_status,
    run_ipc_console_command,
)
from src.appshell.ipc.ipc_transport import remove_ipc_manifest_entry
from src.appshell.logging import append_jsonl, log_emit
from src.appshell.paths import (
    VROOT_EXPORTS,
    VROOT_IPC,
    VROOT_INSTALL,
    VROOT_LOCKS,
    VROOT_LOGS,
    VROOT_PROFILES,
    VROOT_STORE,
    get_current_virtual_paths,
    vpath_resolve,
    vpath_resolve_existing,
    vpath_root,
)
from src.appshell.pack_verifier_adapter import verify_pack_root
from src.compat import emit_product_descriptor
from src.runtime.process_spawn import build_python_process_spec, poll_process, spawn_process
from src.appshell.supervisor.args_canonicalizer import canonicalize_args
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, read_json_object, refusal, write_canonical_json


SUPERVISOR_POLICY_REGISTRY_REL = os.path.join("data", "registries", "supervisor_policy_registry.json")
SUPERVISOR_STATE_REL = os.path.join("supervisor", "supervisor_state.json")
SUPERVISOR_RUN_MANIFEST_REL = os.path.join("supervisor", "run_manifest.json")
SUPERVISOR_AGGREGATED_LOG_REL = os.path.join("supervisor", "aggregated_logs.jsonl")
SUPERVISOR_DIAG_ROOT_REL = os.path.join("supervisor", "diag")
SUPERVISOR_SERVICE_SCRIPT_REL = os.path.join("tools", "appshell", "supervisor_service.py")
SUPERVISED_PRODUCT_HOST_REL = os.path.join("tools", "appshell", "supervised_product_host.py")
SUPERVISOR_SERVICE_MODULE = "tools.appshell.supervisor_service"
SUPERVISED_PRODUCT_HOST_MODULE = "tools.appshell.supervised_product_host"
MVP_SESSION_TEMPLATE_REL = os.path.join("data", "session_templates", "session.mvp_default.json")
MVP_PROFILE_BUNDLE_REL = os.path.join("profiles", "bundles", "bundle.mvp_default.json")
MVP_PACK_LOCK_REL = os.path.join("locks", "pack_lock.mvp_default.json")
IPC_ENDPOINT_MANIFEST_REL = "ipc_endpoints.json"
DEFAULT_SUPERVISOR_POLICY_ID = "supervisor.policy.default"
DEFAULT_TOPOLOGY = "singleplayer"
STOP_POLL_ITERATIONS = 4
DEFAULT_READY_POLL_ITERATIONS = 6
DEFAULT_RESTART_BACKOFF_ITERATIONS = 1
REFUSAL_SUPERVISOR_ALREADY_RUNNING = "refusal.supervisor.already_running"
REFUSAL_SUPERVISOR_NOT_RUNNING = "refusal.supervisor.not_running"
REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED = "refusal.supervisor.endpoint_unreached"
REFUSAL_SUPERVISOR_RESTART_DENIED = "refusal.supervisor.restart_denied"
REFUSAL_SUPERVISOR_PROCESS_MISSING = "refusal.supervisor.process_missing"
REFUSAL_SUPERVISOR_CHILD_NOT_READY = "refusal.supervisor.child_not_ready"


_CURRENT_SUPERVISOR_ENGINE = None


def set_current_supervisor_engine(engine: "SupervisorEngine | None") -> None:
    global _CURRENT_SUPERVISOR_ENGINE
    _CURRENT_SUPERVISOR_ENGINE = engine


def get_current_supervisor_engine() -> "SupervisorEngine | None":
    return _CURRENT_SUPERVISOR_ENGINE


def clear_current_supervisor_engine() -> None:
    set_current_supervisor_engine(None)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _read_json(path: str) -> dict:
    payload, error = read_json_object(path)
    if error:
        return {}
    return dict(payload)


def _file_hash(path: str) -> str:
    abs_path = os.path.normpath(os.path.abspath(str(path or "")))
    try:
        with open(abs_path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return ""


def _refuse(reason_code: str, message: str, remediation_hint: str, *, details: Mapping[str, object] | None = None, path: str = "$") -> dict:
    relevant_ids = {
        str(key): str(value).strip()
        for key, value in sorted(dict(details or {}).items(), key=lambda item: str(item[0]))
        if str(value).strip()
    }
    return refusal(reason_code, message, remediation_hint, relevant_ids, path)


def _runtime_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.join(os.path.normpath(os.path.abspath(str(repo_root or "."))), rel_path.replace("/", os.sep)))


def _repo_rel(repo_root: str, abs_path: str) -> str:
    return norm(os.path.relpath(os.path.normpath(os.path.abspath(abs_path)), os.path.normpath(os.path.abspath(repo_root))))


def _vpath_context() -> dict | None:
    context = get_current_virtual_paths()
    if context is None or str(context.get("result", "")).strip() != "complete":
        return None
    return dict(context)


def _supervisor_vpath_flag_pairs() -> tuple[tuple[str, str], ...]:
    context = _vpath_context()
    if context is None:
        return ()
    roots = _as_map(context.get("roots"))
    rows: list[tuple[str, str]] = []
    install_root = str(roots.get(VROOT_INSTALL, "")).strip()
    store_root = str(roots.get(VROOT_STORE, "")).strip()
    install_id = str(context.get("install_id", "")).strip()
    install_registry_path = str(context.get("install_registry_path", "")).strip()
    if install_root:
        rows.append(("--install-root", install_root))
    if store_root:
        rows.append(("--store-root", store_root))
    if install_id:
        rows.append(("--install-id", install_id))
    if install_registry_path:
        rows.append(("--install-registry-path", install_registry_path))
    return tuple(rows)


def _deterministic_id(*parts: object, prefix: str, size: int = 12) -> str:
    body = "|".join(str(part).strip() for part in parts)
    return "{}.{}".format(str(prefix).strip(), hashlib.sha256(body.encode("utf-8")).hexdigest()[: max(4, int(size or 12))])


def _write_jsonl(path: str, rows: Sequence[Mapping[str, object]]) -> str:
    output_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)
    for row in list(rows or []):
        append_jsonl(output_path, dict(row))
    return output_path


def _parse_stdout_json_line(process: subprocess.Popen) -> tuple[dict, str]:
    handle = getattr(process, "stdout", None)
    if handle is None:
        return {}, "stdout unavailable"
    line = handle.readline()
    if not line:
        return {}, "ready line missing"
    try:
        payload = json.loads(str(line).strip())
    except ValueError:
        return {}, "ready line invalid json"
    return dict(payload) if isinstance(payload, dict) else {}, ""


def _extract_log_seq_no(event_row: Mapping[str, object], default_seq: int) -> int:
    token = str(dict(event_row or {}).get("event_id", "")).strip()
    if token.startswith("log.") and token.rsplit(".", 1)[-1].isdigit():
        return int(token.rsplit(".", 1)[-1])
    return int(default_seq)


def _build_endpoint_id(product_id: str, session_id: str) -> str:
    return "ipc.{}.{}".format(str(product_id).strip(), str(session_id).strip())


def _ready_poll_iterations(run_spec: Mapping[str, object]) -> int:
    policy = _as_map(run_spec.get("supervisor_policy"))
    return max(1, int(policy.get("readiness_poll_iterations", DEFAULT_READY_POLL_ITERATIONS) or DEFAULT_READY_POLL_ITERATIONS))


def _restart_backoff_iterations(run_spec: Mapping[str, object]) -> int:
    policy = _as_map(run_spec.get("supervisor_policy"))
    return max(0, int(policy.get("restart_backoff_iterations", DEFAULT_RESTART_BACKOFF_ITERATIONS) or 0))


def _log_merge_sort_key(row: Mapping[str, object]) -> tuple[str, str, int, str, str]:
    return _LOG_MERGE_SORT_KEY(dict(row or {}))


_LOG_MERGE_SORT_KEY = build_field_sort_key(
    ("source_product_id", "channel_id", "seq_no", "endpoint_id", "event_id"),
    int_fields=("seq_no",),
)


def _wait_for_endpoint_ready_process(
    repo_root: str,
    process: subprocess.Popen,
    *,
    local_product_id: str,
    product_id: str,
    session_id: str,
    endpoint_id: str,
    iterations: int,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    token_product = str(product_id).strip()
    token_session = str(session_id).strip()
    token_endpoint = str(endpoint_id).strip()
    token_local_product = str(local_product_id).strip()
    last_result: dict[str, object] = {}
    for attempt in range(max(1, int(iterations or 1))):
        polled = poll_process(process)
        if str(polled.get("result", "")).strip() == "exited":
            return _refuse(
                REFUSAL_SUPERVISOR_CHILD_NOT_READY,
                "child product exited before negotiated readiness completed",
                "Inspect child logs or retry the supervised run.",
                details={
                    "product_id": token_product,
                    "endpoint_id": token_endpoint,
                    "exit_code": int(polled.get("exit_code", 0) or 0),
                },
            )
        endpoint_row = _discover_endpoint_row(repo_root_abs, token_endpoint)
        if not endpoint_row:
            last_result = {
                "result": "pending",
                "reason": "endpoint_not_discovered",
                "attempt": int(attempt + 1),
            }
            continue
        try:
            attach = attach_ipc_endpoint(repo_root_abs, local_product_id=token_local_product, endpoint_id=token_endpoint)
        except OSError as exc:
            last_result = {
                "result": "refused",
                "refusal_code": REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED,
                "reason": str(exc),
                "attempt": int(attempt + 1),
            }
            continue
        if str(attach.get("result", "")).strip() != "complete":
            last_result = dict(attach)
            last_result["attempt"] = int(attempt + 1)
            continue
        try:
            status_result = query_ipc_status(repo_root_abs, attach)
        except OSError as exc:
            last_result = {
                "result": "refused",
                "refusal_code": REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED,
                "reason": str(exc),
                "attempt": int(attempt + 1),
            }
            continue
        if str(status_result.get("result", "")).strip() != "complete":
            last_result = dict(status_result)
            last_result["attempt"] = int(attempt + 1)
            continue
        status_payload = dict(status_result.get("status") or {})
        if str(status_payload.get("product_id", "")).strip() != token_product or str(status_payload.get("session_id", "")).strip() != token_session:
            last_result = {
                "result": "refused",
                "refusal_code": REFUSAL_SUPERVISOR_CHILD_NOT_READY,
                "reason": "status payload identity mismatch",
                "attempt": int(attempt + 1),
            }
            continue
        ready_payload = {
            "result": "complete",
            "endpoint_id": token_endpoint,
            "address": str(endpoint_row.get("address", "")).strip(),
            "product_id": token_product,
            "session_id": token_session,
            "deterministic_fingerprint": "",
        }
        ready_payload["deterministic_fingerprint"] = canonical_sha256(dict(ready_payload, deterministic_fingerprint=""))
        return {
            "result": "complete",
            "attach_record": dict(attach),
            "status_payload": status_payload,
            "endpoint_id": token_endpoint,
            "compatibility_mode_id": str(attach.get("compatibility_mode_id", "")).strip(),
            "read_only_mode": bool(attach.get("read_only_mode", False)),
            "ready_payload": ready_payload,
            "readiness_iteration_count": int(attempt + 1),
        }
    return _refuse(
        REFUSAL_SUPERVISOR_CHILD_NOT_READY,
        "child product did not complete negotiated readiness within bounded iterations",
        "Inspect child logs or retry the supervised run.",
        details={
            "product_id": token_product,
            "endpoint_id": token_endpoint,
            "attempts": int(max(1, int(iterations or 1))),
            "last_refusal_code": str(last_result.get("refusal_code", "")).strip(),
        },
    )


def _supervisor_runtime_paths(repo_root: str) -> dict:
    context = _vpath_context()
    if context is not None:
        return {
            "state_path": vpath_resolve(VROOT_IPC, SUPERVISOR_STATE_REL, context),
            "manifest_path": vpath_resolve(VROOT_IPC, SUPERVISOR_RUN_MANIFEST_REL, context),
            "aggregated_log_path": vpath_resolve(VROOT_LOGS, SUPERVISOR_AGGREGATED_LOG_REL, context),
            "diag_root": vpath_resolve(VROOT_EXPORTS, SUPERVISOR_DIAG_ROOT_REL, context),
            "ipc_manifest_path": vpath_resolve(VROOT_IPC, IPC_ENDPOINT_MANIFEST_REL, context),
        }
    return {
        "state_path": _runtime_abs(repo_root, os.path.join("dist", "runtime", SUPERVISOR_STATE_REL)),
        "manifest_path": _runtime_abs(repo_root, os.path.join("dist", "runtime", SUPERVISOR_RUN_MANIFEST_REL)),
        "aggregated_log_path": _runtime_abs(repo_root, os.path.join("dist", "runtime", SUPERVISOR_AGGREGATED_LOG_REL)),
        "diag_root": _runtime_abs(repo_root, os.path.join("build", "appshell", SUPERVISOR_DIAG_ROOT_REL)),
        "ipc_manifest_path": _runtime_abs(repo_root, os.path.join("dist", "runtime", IPC_ENDPOINT_MANIFEST_REL)),
    }


def load_supervisor_runtime_state(repo_root: str) -> dict:
    return _read_json(_supervisor_runtime_paths(repo_root).get("state_path", ""))


def _supervisor_endpoint_rows(repo_root: str) -> list[dict]:
    rows = []
    discovered = discover_ipc_endpoints(repo_root)
    for row in _as_list(discovered.get("endpoints")):
        row_map = _as_map(row)
        session_id = str(row_map.get("session_id", "")).strip()
        endpoint_id = str(row_map.get("endpoint_id", "")).strip()
        if endpoint_id and session_id.startswith("supervisor."):
            rows.append(row_map)
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("endpoint_id", "")).strip(),
            str(row.get("product_id", "")).strip(),
            str(row.get("session_id", "")).strip(),
        ),
    )


def _endpoint_row_reachable(repo_root: str, endpoint_row: Mapping[str, object]) -> bool:
    endpoint_id = str(_as_map(endpoint_row).get("endpoint_id", "")).strip()
    if not endpoint_id:
        return False
    try:
        attach_report = attach_ipc_endpoint(
            repo_root,
            local_product_id="tool.attach_console_stub",
            endpoint_id=endpoint_id,
            allow_read_only=True,
            accept_degraded=True,
        )
    except OSError:
        return False
    return str(dict(attach_report).get("result", "")).strip() == "complete"


def sanitize_supervisor_runtime(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    reachable_ids: set[str] = set()
    pruned_endpoint_ids: list[str] = []
    for row in _supervisor_endpoint_rows(repo_root_abs):
        endpoint_id = str(row.get("endpoint_id", "")).strip()
        if not endpoint_id:
            continue
        if _endpoint_row_reachable(repo_root_abs, row):
            reachable_ids.add(endpoint_id)
            continue
        remove_ipc_manifest_entry(repo_root_abs, endpoint_id)
        pruned_endpoint_ids.append(endpoint_id)
    state_path = _supervisor_runtime_paths(repo_root_abs).get("state_path", "")
    state = load_supervisor_runtime_state(repo_root_abs)
    state_changed = False
    if state:
        state_map = dict(state)
        service = dict(_as_map(state_map.get("service")))
        service_endpoint_id = str(service.get("endpoint_id", "")).strip()
        if service_endpoint_id and service_endpoint_id not in reachable_ids:
            service["endpoint_id"] = ""
            service["address"] = ""
            service["status"] = "stopped"
            state_map["service"] = service
            state_changed = True
        process_rows = []
        for row in _as_list(state_map.get("processes")):
            row_map = dict(_as_map(row))
            endpoint_id = str(row_map.get("endpoint_id", "")).strip()
            status = str(row_map.get("status", "")).strip()
            if status == "running" and endpoint_id and endpoint_id not in reachable_ids:
                row_map["status"] = "exited"
                row_map["attach_status"] = "detached"
                if row_map.get("exit_code") is None:
                    row_map["exit_code"] = 0
                if not str(row_map.get("attach_error", "")).strip():
                    row_map["attach_error"] = "stale endpoint pruned"
                state_changed = True
            process_rows.append(row_map)
        if state_changed:
            state_map["processes"] = process_rows
            state_map["deterministic_fingerprint"] = canonical_sha256(dict(state_map, deterministic_fingerprint=""))
            write_canonical_json(state_path, state_map)
            state = state_map
    return {
        "result": "complete",
        "reachable_endpoint_ids": sorted(reachable_ids),
        "pruned_endpoint_ids": sorted(pruned_endpoint_ids),
        "state_changed": bool(state_changed),
        "state_present": bool(state),
        "deterministic_fingerprint": canonical_sha256(
            {
                "reachable_endpoint_ids": sorted(reachable_ids),
                "pruned_endpoint_ids": sorted(pruned_endpoint_ids),
                "state_changed": bool(state_changed),
                "state_present": bool(state),
            }
        ),
    }


def _load_supervisor_policy(repo_root: str, policy_id: str) -> tuple[dict, str]:
    payload = _read_json(_runtime_abs(repo_root, SUPERVISOR_POLICY_REGISTRY_REL))
    for row in _as_list(_as_map(payload.get("record")).get("policies")):
        row_map = _as_map(row)
        if str(row_map.get("policy_id", "")).strip() == str(policy_id).strip():
            return row_map, ""
    return {}, "missing policy"


def _verification_root(repo_root: str) -> str:
    context = _vpath_context()
    if context is not None:
        store_root = vpath_root(VROOT_STORE, context)
        store_contract_registry = _runtime_abs(
            store_root,
            os.path.join("data", "registries", "semantic_contract_registry.json"),
        )
        store_packs_root = _runtime_abs(store_root, "packs")
        if os.path.isfile(store_contract_registry) and os.path.isdir(store_packs_root):
            return store_root
        repo_contract_registry = _runtime_abs(
            repo_root,
            os.path.join("data", "registries", "semantic_contract_registry.json"),
        )
        if os.path.isfile(repo_contract_registry) and os.path.isdir(store_packs_root):
            return _runtime_abs(repo_root, ".")
        resolution_source = str(context.get("resolution_source", "")).strip()
        if resolution_source != "repo_wrapper_shim":
            return _runtime_abs(repo_root, ".")
        return _runtime_abs(repo_root, ".")
    dist_contract_registry = _runtime_abs(repo_root, os.path.join("dist", "data", "registries", "semantic_contract_registry.json"))
    dist_packs_root = _runtime_abs(repo_root, os.path.join("dist", "packs"))
    if os.path.isfile(dist_contract_registry) and os.path.isdir(dist_packs_root):
        return _runtime_abs(repo_root, "dist")
    return _runtime_abs(repo_root, ".")


def _find_session_template(repo_root: str, template_id: str, template_path: str = "") -> tuple[str, dict]:
    if str(template_path or "").strip():
        abs_path = _runtime_abs(repo_root, str(template_path))
        return abs_path, _read_json(abs_path)
    roots = (
        _runtime_abs(repo_root, os.path.join("data", "session_templates")),
        _runtime_abs(repo_root, os.path.join("dist", "session_templates")),
    )
    token = str(template_id or "").strip() or "session.mvp_default"
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in sorted(entry for entry in os.listdir(root) if entry.endswith(".json")):
            abs_path = os.path.join(root, name)
            payload = _read_json(abs_path)
            if str(payload.get("template_id", "")).strip() == token:
                return abs_path, payload
    fallback = _runtime_abs(repo_root, MVP_SESSION_TEMPLATE_REL)
    return fallback, _read_json(fallback)


def _resolve_pack_lock_path(repo_root: str, pack_lock_path: str) -> str:
    token = str(pack_lock_path or "").strip() or MVP_PACK_LOCK_REL
    if not str(pack_lock_path or "").strip():
        context = _vpath_context()
        if context is not None:
            return vpath_resolve_existing(VROOT_LOCKS, os.path.basename(MVP_PACK_LOCK_REL), context) or vpath_resolve(
                VROOT_LOCKS,
                os.path.basename(MVP_PACK_LOCK_REL),
                context,
            )
    return _runtime_abs(repo_root, token)


def _resolve_profile_bundle_path(repo_root: str, profile_bundle_path: str) -> str:
    token = str(profile_bundle_path or "").strip() or MVP_PROFILE_BUNDLE_REL
    if not str(profile_bundle_path or "").strip():
        context = _vpath_context()
        if context is not None:
            return vpath_resolve_existing(VROOT_PROFILES, os.path.join("bundles", os.path.basename(MVP_PROFILE_BUNDLE_REL)), context) or vpath_resolve(
                VROOT_PROFILES,
                os.path.join("bundles", os.path.basename(MVP_PROFILE_BUNDLE_REL)),
                context,
            )
    return _runtime_abs(repo_root, token)


def _discover_endpoint_row(repo_root: str, endpoint_id: str) -> dict:
    discovered = discover_ipc_endpoints(repo_root)
    for row in _as_list(discovered.get("endpoints")):
        row_map = _as_map(row)
        if str(row_map.get("endpoint_id", "")).strip() == str(endpoint_id).strip():
            return row_map
    return {}


def discover_active_supervisor_endpoint(repo_root: str) -> dict:
    sanitize_supervisor_runtime(repo_root)
    state = load_supervisor_runtime_state(repo_root)
    endpoint_id = str(_as_map(state.get("service")).get("endpoint_id", "")).strip()
    if not endpoint_id:
        return {}
    return _discover_endpoint_row(repo_root, endpoint_id)


def _remote_command_result(repo_root: str, command_text: str) -> dict:
    endpoint = discover_active_supervisor_endpoint(repo_root)
    if not endpoint:
        return _refuse(
            REFUSAL_SUPERVISOR_NOT_RUNNING,
            "no active launcher supervisor endpoint was discovered",
            "Run `launcher start` before requesting supervisor status, stop, or attach actions.",
        )
    try:
        attach = attach_ipc_endpoint(repo_root, local_product_id="launcher", endpoint_id=str(endpoint.get("endpoint_id", "")).strip())
    except OSError as exc:
        return _refuse(
            REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED,
            "launcher supervisor IPC negotiation failed",
            "Retry after the supervisor endpoint is ready, or inspect `console sessions` for active endpoints.",
            details={"endpoint_id": str(endpoint.get("endpoint_id", "")).strip(), "reason": str(exc)},
        )
    if str(attach.get("result", "")).strip() != "complete":
        return _refuse(
            REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED,
            "launcher supervisor IPC negotiation failed",
            "Retry after the supervisor endpoint is ready, or inspect `console sessions` for active endpoints.",
            details={"endpoint_id": str(endpoint.get("endpoint_id", "")).strip()},
        )
    console = run_ipc_console_command(repo_root, attach, str(command_text).strip())
    stdout = str(console.get("stdout", "")).strip()
    if stdout:
        try:
            payload = json.loads(stdout)
        except ValueError:
            payload = {}
        if isinstance(payload, dict):
            return payload
    return dict(console)


def invoke_supervisor_service_command(repo_root: str, command_text: str) -> dict:
    return _remote_command_result(repo_root, command_text)


def attach_supervisor_children(repo_root: str, *, endpoint_id: str = "", attach_all: bool = False) -> dict:
    state = load_supervisor_runtime_state(repo_root)
    rows = sorted(
        [_as_map(row) for row in _as_list(state.get("processes")) if _as_map(row)],
        key=lambda row: (str(row.get("product_id", "")), str(row.get("endpoint_id", ""))),
    )
    if str(endpoint_id or "").strip():
        target_ids = [str(endpoint_id).strip()]
    elif bool(attach_all):
        target_ids = [str(row.get("endpoint_id", "")).strip() for row in rows if str(row.get("endpoint_id", "")).strip()]
    else:
        return {
            "result": "complete",
            "endpoints": [
                {
                    "product_id": str(row.get("product_id", "")).strip(),
                    "endpoint_id": str(row.get("endpoint_id", "")).strip(),
                    "status": str(row.get("status", "")).strip(),
                }
                for row in rows
            ],
        }
    attach_rows = []
    for item in target_ids:
        try:
            attach = attach_ipc_endpoint(repo_root, local_product_id="launcher", endpoint_id=str(item).strip())
        except OSError as exc:
            attach = {
                "result": "refused",
                "refusal_code": REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED,
                "reason": str(exc),
            }
        attach_rows.append(
            {
                "endpoint_id": str(item).strip(),
                "result": str(attach.get("result", "")).strip(),
                "compatibility_mode_id": str(attach.get("compatibility_mode_id", "")).strip(),
                "refusal_code": str(attach.get("refusal_code", "")).strip(),
            }
        )
    return {"result": "complete", "attachments": attach_rows}


def _build_process_rows(repo_root: str, run_spec: Mapping[str, object]) -> list[dict]:
    topology = str(run_spec.get("topology", "")).strip()
    product_ids = ["server"] if topology == "server_only" else ["server", "client"]
    binary_abs = _runtime_abs(repo_root, SUPERVISED_PRODUCT_HOST_REL)
    binary_hash = _file_hash(binary_abs)
    out = []
    for index, product_id in enumerate(product_ids, start=1):
        pid_stub = "proc.{}.{:04d}".format(str(product_id).strip(), int(index))
        session_id = "{}.{}".format(str(run_spec.get("session_id", "")).strip(), str(product_id).strip())
        arg_payload = canonicalize_args(
            positional=[],
            flag_pairs=(
                ("--contract-bundle-hash", str(run_spec.get("contract_bundle_hash", "")).strip()),
                ("--ipc-manifest-path", str(run_spec.get("ipc_manifest_path", "")).strip()),
                ("--mod-policy-id", str(run_spec.get("mod_policy_id", "")).strip()),
                ("--overlay-conflict-policy-id", str(run_spec.get("overlay_conflict_policy_id", "")).strip()),
                ("--pack-lock-hash", str(run_spec.get("pack_lock_hash", "")).strip()),
                ("--pack-lock-path", str(run_spec.get("pack_lock_path", "")).strip()),
                ("--pid-stub", pid_stub),
                ("--product-id", str(product_id).strip()),
                ("--profile-bundle-path", str(run_spec.get("profile_bundle_path", "")).strip()),
                ("--repo-root", "."),
                ("--run-manifest-path", str((dict(run_spec.get("runtime_paths") or {})).get("manifest_path", "")).strip()),
                ("--seed", str(run_spec.get("seed", "")).strip()),
                ("--session-id", session_id),
                ("--session-template-id", str(run_spec.get("session_template_id", "")).strip()),
            ),
        )
        args = list(arg_payload.get("args") or [])
        out.append(
            {
                "product_id": str(product_id).strip(),
                "binary_rel": norm(SUPERVISED_PRODUCT_HOST_REL),
                "binary_hash": binary_hash,
                "args": list(args),
                "args_hash": str(arg_payload.get("args_hash", "")).strip() or canonical_sha256(list(args)),
                "argv_text_hash": str(arg_payload.get("argv_text_hash", "")).strip(),
                "argv_text": str(arg_payload.get("argv_text", "")).strip(),
                "pid_stub": pid_stub,
            }
        )
    return out


def _build_run_manifest(run_spec: Mapping[str, object]) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "manifest_id": str(run_spec.get("manifest_id", "")).strip(),
        "tick_started": int(run_spec.get("tick_started", 0) or 0),
        "seed": str(run_spec.get("seed", "")).strip(),
        "session_template_id": str(run_spec.get("session_template_id", "")).strip(),
        "profile_bundle_hash": str(run_spec.get("profile_bundle_hash", "")).strip(),
        "pack_lock_hash": str(run_spec.get("pack_lock_hash", "")).strip(),
        "contract_bundle_hash": str(run_spec.get("contract_bundle_hash", "")).strip(),
        "processes": [
            {
                "product_id": str(row.get("product_id", "")).strip(),
                "binary_hash": str(row.get("binary_hash", "")).strip(),
                "args_hash": str(row.get("args_hash", "")).strip(),
                "argv_text_hash": str(row.get("argv_text_hash", "")).strip(),
                "pid_stub": str(row.get("pid_stub", "")).strip(),
            }
            for row in list(run_spec.get("processes") or [])
        ],
        "deterministic_fingerprint": "",
        "extensions": {
            "official.mod_policy_id": str(run_spec.get("mod_policy_id", "")).strip(),
            "official.overlay_conflict_policy_id": str(run_spec.get("overlay_conflict_policy_id", "")).strip(),
            "official.topology": str(run_spec.get("topology", "")).strip(),
            "official.supervisor_policy_id": str(run_spec.get("supervisor_policy_id", "")).strip(),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_supervisor_run_spec(
    *,
    repo_root: str,
    seed: str,
    session_template_id: str = "session.mvp_default",
    session_template_path: str = "",
    profile_bundle_path: str = "",
    pack_lock_path: str = "",
    mod_policy_id: str = "",
    overlay_conflict_policy_id: str = "",
    contract_bundle_hash: str = "",
    supervisor_policy_id: str = DEFAULT_SUPERVISOR_POLICY_ID,
    topology: str = DEFAULT_TOPOLOGY,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    template_abs, template_payload = _find_session_template(repo_root_abs, session_template_id, session_template_path)
    if not template_payload:
        return _refuse(
            "refusal.io.invalid_args",
            "session template could not be resolved",
            "Provide a valid `--session-template-id` or `--session-template-path`.",
            details={"session_template_id": str(session_template_id).strip()},
            path="$.session_template_id",
        )
    profile_abs = _resolve_profile_bundle_path(repo_root_abs, profile_bundle_path)
    pack_lock_abs = _resolve_pack_lock_path(repo_root_abs, pack_lock_path)
    pack_lock_payload = _read_json(pack_lock_abs)
    if not pack_lock_payload:
        return _refuse(
            "refusal.pack.schema_invalid",
            "pack lock file is missing or invalid",
            "Run `packs build-lock` or provide a valid `--pack-lock-path`.",
            details={"pack_lock_path": _repo_rel(repo_root_abs, pack_lock_abs)},
            path="$.pack_lock_path",
        )
    selected_contract_bundle_hash = str(
        contract_bundle_hash or template_payload.get("semantic_contract_bundle_hash", "") or template_payload.get("contract_bundle_hash", "")
    ).strip()
    selected_mod_policy_id = str(
        mod_policy_id or template_payload.get("mod_policy_id", "") or pack_lock_payload.get("mod_policy_id", "mod_policy.lab")
    ).strip() or "mod_policy.lab"
    selected_conflict_policy_id = str(
        overlay_conflict_policy_id or pack_lock_payload.get("overlay_conflict_policy_id", "overlay.conflict.last_wins")
    ).strip() or "overlay.conflict.last_wins"
    policy_row, policy_error = _load_supervisor_policy(repo_root_abs, supervisor_policy_id)
    if policy_error:
        return _refuse(
            "refusal.io.invalid_args",
            "supervisor policy id was not found",
            "Choose a declared supervisor policy.",
            details={"supervisor_policy_id": str(supervisor_policy_id).strip()},
            path="$.supervisor_policy_id",
        )
    runtime_paths = _supervisor_runtime_paths(repo_root_abs)
    verify_root = _verification_root(repo_root_abs)
    if os.path.normcase(os.path.normpath(verify_root)) != os.path.normcase(repo_root_abs):
        compatibility = verify_pack_root(
            repo_root=repo_root_abs,
            root=verify_root,
            bundle_id="",
            mod_policy_id=selected_mod_policy_id,
            overlay_conflict_policy_id=selected_conflict_policy_id,
            contract_bundle_path="",
            out_report=os.path.join(os.path.dirname(runtime_paths["manifest_path"]), "pack_compatibility_report.json"),
            out_lock=os.path.join(os.path.dirname(runtime_paths["manifest_path"]), "verified_pack_lock.json"),
            write_outputs=True,
        )
    else:
        compatibility = {
            "result": "complete",
            "dist_root": repo_root_abs.replace("\\", "/"),
            "report": {
                "report_id": _deterministic_id(
                    selected_mod_policy_id,
                    selected_conflict_policy_id,
                    str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
                    prefix="pack_compat_report",
                ),
                "valid": True,
                "warnings": [],
                "conflicts": [],
            },
            "pack_lock": dict(pack_lock_payload),
            "warnings": [],
            "errors": [],
            "written_report_path": "",
            "written_lock_path": "",
        }
    if str(compatibility.get("result", "")).strip() != "complete":
        return dict(compatibility)
    report = _as_map(compatibility.get("report"))
    if not bool(report.get("valid", False)):
        return _refuse(
            "refusal.pack.contract_range_mismatch",
            "offline pack verification refused the selected pack set",
            "Resolve pack compatibility failures before launching a supervised session.",
            details={"report_id": str(report.get("report_id", "")).strip(), "mod_policy_id": selected_mod_policy_id},
            path="$.pack_compatibility_report.valid",
        )
    run_seed = str(seed or _as_map(template_payload.get("universe_seed")).get("dev_default", "0")).strip() or "0"
    session_id = _deterministic_id(
        template_payload.get("template_id", session_template_id),
        run_seed,
        _file_hash(profile_abs),
        str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
        selected_contract_bundle_hash,
        selected_mod_policy_id,
        selected_conflict_policy_id,
        str(topology).strip(),
        prefix="supervisor",
    )
    base_spec = {
        "result": "complete",
        "repo_root": repo_root_abs,
        "seed": run_seed,
            "session_template_id": str(template_payload.get("template_id", "")).strip() or str(session_template_id).strip() or "session.mvp_default",
        "session_template_path": _repo_rel(repo_root_abs, template_abs),
        "profile_bundle_path": _repo_rel(repo_root_abs, profile_abs),
        "profile_bundle_hash": _file_hash(profile_abs),
        "pack_lock_path": _repo_rel(repo_root_abs, pack_lock_abs),
        "pack_lock_hash": str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
        "contract_bundle_hash": selected_contract_bundle_hash,
        "mod_policy_id": selected_mod_policy_id,
        "overlay_conflict_policy_id": selected_conflict_policy_id,
        "supervisor_policy_id": str(supervisor_policy_id).strip(),
        "topology": "server_only" if str(topology).strip() == "server_only" else "singleplayer",
        "pack_verify_root": _repo_rel(repo_root_abs, verify_root),
        "session_id": session_id,
        "manifest_id": _deterministic_id(session_id, "run_manifest", prefix="run_manifest"),
        "tick_started": 1,
        "ipc_manifest_path": _repo_rel(repo_root_abs, runtime_paths["ipc_manifest_path"]),
        "runtime_paths": {
            "state_path": _repo_rel(repo_root_abs, runtime_paths["state_path"]),
            "manifest_path": _repo_rel(repo_root_abs, runtime_paths["manifest_path"]),
            "aggregated_log_path": _repo_rel(repo_root_abs, runtime_paths["aggregated_log_path"]),
        },
        "supervisor_policy": dict(policy_row),
        "pack_compatibility_report": dict(report),
        "verified_pack_lock_hash": str(_as_map(compatibility.get("pack_lock")).get("pack_lock_hash", "")).strip(),
        "processes": [],
        "deterministic_fingerprint": "",
    }
    base_spec["processes"] = _build_process_rows(repo_root_abs, base_spec)
    base_spec["run_manifest"] = _build_run_manifest(base_spec)
    base_spec["deterministic_fingerprint"] = canonical_sha256(
        dict(base_spec, pack_compatibility_report={}, supervisor_policy={}, runtime_paths={}, deterministic_fingerprint="")
    )
    return base_spec


def _build_child_process_spec(repo_root: str, process_row: Mapping[str, object]) -> dict:
    return build_python_process_spec(
        repo_root=repo_root,
        spawn_id="spawn.supervisor.{}".format(str(process_row.get("product_id", "")).strip()),
        script_path=SUPERVISED_PRODUCT_HOST_REL,
        module_name=SUPERVISED_PRODUCT_HOST_MODULE,
        args=[
            *[
                token
                for pair in _supervisor_vpath_flag_pairs()
                for token in pair
            ],
            *list(process_row.get("args") or []),
        ],
        extensions={"pid_stub": str(process_row.get("pid_stub", "")).strip()},
    )


class SupervisorEngine:
    """Deterministic launcher supervisor runtime."""

    def __init__(self, *, repo_root: str, run_spec: Mapping[str, object]) -> None:
        self.repo_root = os.path.normpath(os.path.abspath(str(repo_root or ".")))
        self.run_spec = dict(run_spec or {})
        self.runtime_paths = _supervisor_runtime_paths(self.repo_root)
        self._stop_event = threading.Event()
        self._shutdown_requested = False
        self._service_endpoint_id = ""
        self._service_address = ""
        self._process_handles: dict[str, subprocess.Popen] = {}
        self._runtime_rows: dict[str, dict] = {}
        self._aggregated_logs: list[dict] = []

    def attach_endpoint_server(self, endpoint_server) -> None:
        self._service_endpoint_id = str(getattr(endpoint_server, "endpoint_id", "")).strip()
        self._service_address = str(_as_map(getattr(endpoint_server, "address_payload", {})).get("address", "")).strip()

    def request_shutdown(self) -> None:
        self._stop_event.set()

    def wait_for_shutdown(self) -> None:
        self._stop_event.wait()

    def _write_manifest(self) -> dict:
        manifest = dict(self.run_spec.get("run_manifest") or {})
        write_canonical_json(self.runtime_paths["manifest_path"], manifest)
        return manifest

    def _state_payload(self) -> dict:
        process_rows = sorted(
            [dict(self._runtime_rows[key]) for key in self._runtime_rows.keys()],
            key=lambda row: (str(row.get("product_id", "")), str(row.get("pid_stub", ""))),
        )
        payload = {
            "schema_version": "1.0.0",
            "run_id": str(self.run_spec.get("session_id", "")).strip(),
            "manifest_path": _repo_rel(self.repo_root, self.runtime_paths["manifest_path"]),
            "service": {
                "endpoint_id": str(self._service_endpoint_id).strip(),
                "address": str(self._service_address).strip(),
                "status": "running" if not (self._stop_event.is_set() or self._shutdown_requested) else "stopping",
            },
            "seed": str(self.run_spec.get("seed", "")).strip(),
            "session_template_id": str(self.run_spec.get("session_template_id", "")).strip(),
            "profile_bundle_hash": str(self.run_spec.get("profile_bundle_hash", "")).strip(),
            "pack_lock_hash": str(self.run_spec.get("pack_lock_hash", "")).strip(),
            "contract_bundle_hash": str(self.run_spec.get("contract_bundle_hash", "")).strip(),
            "mod_policy_id": str(self.run_spec.get("mod_policy_id", "")).strip(),
            "overlay_conflict_policy_id": str(self.run_spec.get("overlay_conflict_policy_id", "")).strip(),
            "supervisor_policy_id": str(self.run_spec.get("supervisor_policy_id", "")).strip(),
            "topology": str(self.run_spec.get("topology", "")).strip(),
            "processes": process_rows,
            "aggregated_log_count": int(len(self._aggregated_logs)),
            "latest_logs": list(self._aggregated_logs[-8:]),
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    def _write_state(self) -> dict:
        payload = self._state_payload()
        write_canonical_json(self.runtime_paths["state_path"], payload)
        _write_jsonl(self.runtime_paths["aggregated_log_path"], self._aggregated_logs[-128:])
        return payload

    def _process_diag_bundle(self, product_id: str, process_row: Mapping[str, object]) -> str:
        product_token = str(product_id).strip()
        payload = write_repro_bundle(
            repo_root=self.repo_root,
            created_by_product_id=product_token,
            build_id=str(dict(emit_product_descriptor(self.repo_root, product_id=product_token).get("version") or {}).get("build_id", "")).strip(),
            out_dir=os.path.join(self.runtime_paths["diag_root"], product_token),
            descriptor_payloads=[emit_product_descriptor(self.repo_root, product_id=product_token)],
            run_manifest_payload=dict(self.run_spec.get("run_manifest") or {}),
            pack_lock_path=_runtime_abs(self.repo_root, str(self.run_spec.get("pack_lock_path", "")).strip()),
            contract_bundle_hash=str(self.run_spec.get("contract_bundle_hash", "")).strip(),
            seed=str(self.run_spec.get("seed", "")).strip(),
            session_id=str(self.run_spec.get("session_id", "")).strip(),
            session_template_id=str(self.run_spec.get("session_template_id", "")).strip(),
            log_events=[dict(row) for row in list(self._aggregated_logs[-32:]) if str(dict(row).get("source_product_id", "")).strip() == product_token],
            ipc_attach_rows=[dict(process_row)],
            environment_summary={"supervisor_policy_id": str(self.run_spec.get("supervisor_policy_id", "")).strip()},
        )
        return str(payload.get("bundle_dir", "")).replace("\\", "/")

    def _mark_attach_unreachable(self, row: Mapping[str, object], error_text: str) -> None:
        row_map = row if isinstance(row, dict) else None
        if row_map is None:
            return
        row_map["attach_status"] = "unreachable"
        row_map["attach_error"] = str(error_text or "").strip()

    def _query_status_for_row(self, row: Mapping[str, object]) -> dict:
        row_map = row if isinstance(row, dict) else {}
        endpoint_id = str(row_map.get("endpoint_id", "")).strip()
        if not endpoint_id:
            return {}
        attach_record = _as_map(row_map.get("attach_record"))
        if not attach_record:
            try:
                attach_record = attach_ipc_endpoint(self.repo_root, local_product_id="launcher", endpoint_id=endpoint_id)
            except OSError as exc:
                self._mark_attach_unreachable(row_map, str(exc))
                return {}
            if str(attach_record.get("result", "")).strip() != "complete":
                self._mark_attach_unreachable(row_map, str(attach_record.get("refusal_code", "")).strip())
                return {}
            row_map["attach_record"] = dict(attach_record)
        try:
            status_result = query_ipc_status(self.repo_root, attach_record)
        except OSError as exc:
            self._mark_attach_unreachable(row_map, str(exc))
            return {}
        if str(status_result.get("result", "")).strip() != "complete":
            self._mark_attach_unreachable(row_map, str(status_result.get("refusal_code", "")).strip())
            return {}
        row_map["attach_status"] = "attached"
        row_map["attach_error"] = ""
        row_map["status_payload"] = dict(status_result.get("status") or {})
        return dict(status_result.get("status") or {})

    def _refresh_logs_for_process(self, row: Mapping[str, object]) -> list[dict]:
        row_map = row if isinstance(row, dict) else {}
        endpoint_id = str(row_map.get("endpoint_id", "")).strip()
        if not endpoint_id:
            return []
        attach_record = _as_map(row_map.get("attach_record"))
        if not attach_record:
            try:
                attach_record = attach_ipc_endpoint(self.repo_root, local_product_id="launcher", endpoint_id=endpoint_id)
            except OSError as exc:
                self._mark_attach_unreachable(row_map, str(exc))
                return []
            if str(attach_record.get("result", "")).strip() != "complete":
                self._mark_attach_unreachable(row_map, str(attach_record.get("refusal_code", "")).strip())
                return []
            row_map["attach_record"] = dict(attach_record)
        after_event_id = str(row_map.get("last_event_id", "")).strip()
        try:
            log_rows = query_ipc_log_events(self.repo_root, attach_record, after_event_id=after_event_id, limit=16)
        except OSError as exc:
            self._mark_attach_unreachable(row_map, str(exc))
            return []
        if str(log_rows.get("result", "")).strip() != "complete":
            self._mark_attach_unreachable(row_map, str(log_rows.get("refusal_code", "")).strip())
            return []
        merged = []
        for index, event in enumerate(_as_list(log_rows.get("events")), start=1):
            event_map = _as_map(event)
            merged.append(
                {
                    "source_product_id": str(row_map.get("product_id", "")).strip(),
                    "channel_id": "log",
                    "endpoint_id": endpoint_id,
                    "seq_no": _extract_log_seq_no(event_map, index),
                    "event_id": str(event_map.get("event_id", "")).strip(),
                    "severity": str(event_map.get("severity", "")).strip(),
                    "category": str(event_map.get("category", "")).strip(),
                    "message_key": str(event_map.get("message_key", "")).strip(),
                    "tick": event_map.get("tick"),
                }
            )
        if merged:
            target_row = self._runtime_rows.get(str(row_map.get("product_id", "")).strip())
            if isinstance(target_row, dict):
                target_row["last_event_id"] = str(merged[-1].get("event_id", "")).strip()
                target_row["attach_record"] = dict(attach_record)
                target_row["attach_status"] = "attached"
                target_row["attach_error"] = ""
        return merged

    def _wait_for_endpoint_ready(
        self,
        *,
        process: subprocess.Popen,
        product_id: str,
        session_id: str,
        endpoint_id: str,
        iterations: int,
    ) -> dict:
        result = _wait_for_endpoint_ready_process(
            self.repo_root,
            process,
            local_product_id="launcher",
            product_id=product_id,
            session_id=session_id,
            endpoint_id=endpoint_id,
            iterations=iterations,
        )
        if str(result.get("result", "")).strip() != "complete":
            log_emit(
                category="appshell",
                severity="error",
                message_key=REFUSAL_SUPERVISOR_CHILD_NOT_READY,
                params={
                    "product_id": str(product_id).strip(),
                    "endpoint_id": str(endpoint_id).strip(),
                    "attempts": int(max(1, int(iterations or 1))),
                },
            )
        return result

    def start(self) -> dict:
        self._write_manifest()
        readiness_iterations = _ready_poll_iterations(self.run_spec)
        for row in list(self.run_spec.get("processes") or []):
            row_map = dict(row)
            product_id = str(row_map.get("product_id", "")).strip()
            spawned = spawn_process(_build_child_process_spec(self.repo_root, row_map))
            if str(spawned.get("result", "")).strip() != "complete":
                if self._process_handles:
                    self.stop()
                return dict(spawned)
            process = spawned.get("process")
            self._process_handles[product_id] = process
            ready_payload, ready_error = _parse_stdout_json_line(process)
            if ready_error or str(ready_payload.get("result", "")).strip() != "complete":
                self.stop()
                return _refuse(
                    REFUSAL_SUPERVISOR_CHILD_NOT_READY,
                    "child product did not emit a deterministic ready handshake",
                    "Inspect child process logs or restart the supervised session.",
                    details={"product_id": product_id, "pid_stub": str(row_map.get("pid_stub", "")).strip()},
                )
            session_id = str(ready_payload.get("session_id", "")).strip() or "{}.{}".format(str(self.run_spec.get("session_id", "")).strip(), product_id)
            endpoint_id = str(ready_payload.get("endpoint_id", "")).strip() or _build_endpoint_id(product_id, session_id)
            attach_result = self._wait_for_endpoint_ready(
                process=process,
                product_id=product_id,
                session_id=session_id,
                endpoint_id=endpoint_id,
                iterations=readiness_iterations,
            )
            if str(attach_result.get("result", "")).strip() != "complete":
                self.stop()
                return dict(attach_result)
            self._runtime_rows[product_id] = {
                "product_id": product_id,
                "pid_stub": str(row_map.get("pid_stub", "")).strip(),
                "binary_rel": str(row_map.get("binary_rel", "")).strip(),
                "binary_hash": str(row_map.get("binary_hash", "")).strip(),
                "args_hash": str(row_map.get("args_hash", "")).strip(),
                "argv_text_hash": str(row_map.get("argv_text_hash", "")).strip(),
                "endpoint_id": str(attach_result.get("endpoint_id", "")).strip(),
                "status": "running",
                "exit_code": None,
                "restart_count": 0,
                "restart_backoff_remaining": 0,
                "attach_status": "attached",
                "compatibility_mode_id": str(attach_result.get("compatibility_mode_id", "")).strip(),
                "read_only_mode": bool(attach_result.get("read_only_mode", False)),
                "attach_record": dict(attach_result.get("attach_record") or {}),
                "status_payload": dict(attach_result.get("status_payload") or {}),
                "last_event_id": "",
                "diag_bundle_dir": "",
                "ready_payload": dict(ready_payload or attach_result.get("ready_payload") or {}),
                "readiness_iteration_count": int(attach_result.get("readiness_iteration_count", readiness_iterations) or readiness_iterations),
            }
            log_emit(
                category="supervisor",
                severity="info",
                message_key="supervisor.process.spawned",
                params={"product_id": product_id, "endpoint_id": str(attach_result.get("endpoint_id", "")).strip()},
            )
        self.refresh()
        log_emit(
            category="supervisor",
            severity="info",
            message_key="supervisor.start.complete",
            params={"run_id": str(self.run_spec.get("session_id", "")).strip(), "process_count": len(self._runtime_rows)},
        )
        return self.status()

    def refresh(self) -> dict:
        aggregated_rows = list(self._aggregated_logs)
        for product_id in sorted(self._runtime_rows.keys()):
            row = self._runtime_rows[product_id]
            process = self._process_handles.get(product_id)
            if process is None:
                continue
            polled = poll_process(process)
            row["status"] = str(polled.get("result", "")).strip()
            if str(polled.get("result", "")).strip() == "exited":
                row["exit_code"] = int(polled.get("exit_code", 0) or 0)
                row["attach_status"] = "detached"
                if not str(row.get("diag_bundle_dir", "")).strip():
                    row["diag_bundle_dir"] = self._process_diag_bundle(product_id, row)
                max_restarts = int(_as_map(self.run_spec.get("supervisor_policy")).get("max_restarts", 0) or 0)
                restart_backoff_iterations = _restart_backoff_iterations(self.run_spec)
                stop_requested = bool(row.get("stop_requested", False))
                if not stop_requested and not self._shutdown_requested and int(row.get("restart_count", 0) or 0) < max_restarts:
                    if not bool(row.get("restart_pending", False)):
                        row["restart_pending"] = True
                        row["restart_backoff_remaining"] = int(restart_backoff_iterations)
                        log_emit(
                            category="supervisor",
                            severity="warn",
                            message_key="explain.supervisor_restart",
                            params={
                                "product_id": product_id,
                                "restart_count": int(row.get("restart_count", 0) or 0),
                                "backoff_iterations": int(restart_backoff_iterations),
                            },
                        )
                    if int(row.get("restart_backoff_remaining", 0) or 0) > 0:
                        row["restart_backoff_remaining"] = int(row.get("restart_backoff_remaining", 0) or 0) - 1
                        row["status"] = "restart_pending"
                        continue
                    row["restart_result"] = dict(self.restart(product_id))
                else:
                    row["restart_pending"] = False
                    row["restart_backoff_remaining"] = 0
                continue
            aggregated_rows.extend(self._refresh_logs_for_process(row))
            if str(row.get("endpoint_id", "")).strip():
                self._query_status_for_row(row)
        canonical_rows = canonicalize_parallel_mapping_rows(
            [
                {
                    **dict(row),
                    "deterministic_fingerprint": canonical_sha256(dict(dict(row), deterministic_fingerprint="")),
                }
                for row in aggregated_rows
            ],
            key_fn=_log_merge_sort_key,
        )
        self._aggregated_logs = sorted(canonical_rows, key=_log_merge_sort_key)[-128:]
        return {"result": "complete", "state": self._write_state()}

    def stop(self, *, shutdown_supervisor: bool = False) -> dict:
        self._shutdown_requested = True
        ordered_products = [str(row.get("product_id", "")).strip() for row in list(self.run_spec.get("processes") or [])]
        for product_id in reversed(ordered_products):
            process = self._process_handles.get(product_id)
            row = self._runtime_rows.get(product_id)
            if isinstance(row, dict):
                row["stop_requested"] = True
            if process is None:
                continue
            stdin_handle = getattr(process, "stdin", None)
            if stdin_handle is not None:
                try:
                    stdin_handle.write("stop\n")
                    stdin_handle.flush()
                except OSError:
                    pass
            status = {}
            for _ in range(STOP_POLL_ITERATIONS):
                status = poll_process(process)
                if str(status.get("result", "")).strip() == "exited":
                    break
            if str(status.get("result", "")).strip() != "exited":
                try:
                    process.terminate()
                except OSError:
                    pass
                status = poll_process(process)
            if isinstance(row, dict):
                row["status"] = "exited"
                row["attach_status"] = "detached"
                row["restart_pending"] = False
                row["restart_backoff_remaining"] = 0
                row["exit_code"] = int(status.get("exit_code", 0) or 0) if str(status.get("result", "")).strip() == "exited" else 0
            self._process_handles.pop(product_id, None)
        state = self._write_state()
        if shutdown_supervisor:
            self.request_shutdown()
        log_emit(
            category="supervisor",
            severity="info",
            message_key="explain.supervisor_stop",
            params={"run_id": str(self.run_spec.get("session_id", "")).strip(), "shutdown_supervisor": bool(shutdown_supervisor)},
        )
        return {
            "result": "complete",
            "run_manifest_path": _repo_rel(self.repo_root, self.runtime_paths["manifest_path"]),
            "run_manifest": dict(self.run_spec.get("run_manifest") or {}),
            "state": state,
            "processes": list(_as_list(state.get("processes"))),
            "latest_logs": list(_as_list(state.get("latest_logs"))),
        }

    def restart(self, product_id: str) -> dict:
        token = str(product_id or "").strip()
        row = self._runtime_rows.get(token)
        process_row = None
        for item in list(self.run_spec.get("processes") or []):
            item_map = dict(item)
            if str(item_map.get("product_id", "")).strip() == token:
                process_row = item_map
                break
        if row is None or process_row is None:
            return _refuse(
                REFUSAL_SUPERVISOR_PROCESS_MISSING,
                "requested supervised product is not present in the current run",
                "Choose one of the supervised product ids from `launcher status`.",
                details={"product_id": token},
            )
        max_restarts = int(_as_map(self.run_spec.get("supervisor_policy")).get("max_restarts", 0) or 0)
        if int(row.get("restart_count", 0) or 0) >= max_restarts:
            return _refuse(
                REFUSAL_SUPERVISOR_RESTART_DENIED,
                "restart policy denied another restart for this product",
                "Use a policy with a larger `max_restarts` or start a fresh supervised run.",
                details={"product_id": token, "max_restarts": max_restarts},
            )
        spawned = spawn_process(_build_child_process_spec(self.repo_root, process_row))
        if str(spawned.get("result", "")).strip() != "complete":
            return dict(spawned)
        process = spawned.get("process")
        ready_payload, ready_error = _parse_stdout_json_line(process)
        if ready_error or str(ready_payload.get("result", "")).strip() != "complete":
            return _refuse(
                REFUSAL_SUPERVISOR_CHILD_NOT_READY,
                "restarted product did not emit a deterministic ready handshake",
                "Inspect product logs and retry the supervised run.",
                details={"product_id": token},
            )
        attach_result = self._wait_for_endpoint_ready(
            process=process,
            product_id=token,
            session_id=str(ready_payload.get("session_id", "")).strip() or "{}.{}".format(str(self.run_spec.get("session_id", "")).strip(), token),
            endpoint_id=str(ready_payload.get("endpoint_id", "")).strip() or _build_endpoint_id(token, "{}.{}".format(str(self.run_spec.get("session_id", "")).strip(), token)),
            iterations=_ready_poll_iterations(self.run_spec),
        )
        if str(attach_result.get("result", "")).strip() != "complete":
            return dict(attach_result)
        self._process_handles[token] = process
        row["restart_count"] = int(row.get("restart_count", 0) or 0) + 1
        row["stop_requested"] = False
        row["restart_pending"] = False
        row["restart_backoff_remaining"] = 0
        row["status"] = "running"
        row["exit_code"] = None
        row["endpoint_id"] = str(attach_result.get("endpoint_id", "")).strip()
        row["attach_status"] = "attached" if str(attach_result.get("endpoint_id", "")).strip() else "unreachable"
        row["compatibility_mode_id"] = str(attach_result.get("compatibility_mode_id", "")).strip()
        row["read_only_mode"] = bool(attach_result.get("read_only_mode", False))
        row["attach_record"] = dict(attach_result.get("attach_record") or {})
        row["status_payload"] = dict(attach_result.get("status_payload") or {})
        row["last_event_id"] = ""
        row["diag_bundle_dir"] = ""
        row["ready_payload"] = dict(ready_payload or attach_result.get("ready_payload") or {})
        row["readiness_iteration_count"] = int(attach_result.get("readiness_iteration_count", 0) or 0)
        row["attach_error"] = "" if str(attach_result.get("endpoint_id", "")).strip() else str(attach_result.get("reason", "")).strip()
        log_emit(
            category="supervisor",
            severity="warn",
            message_key="supervisor.restart.applied",
            params={
                "product_id": token,
                "restart_count": int(row.get("restart_count", 0) or 0),
                "backoff_iterations": int(_restart_backoff_iterations(self.run_spec)),
            },
        )
        self._write_state()
        return {"result": "complete", "product_id": token, "restart_count": int(row.get("restart_count", 0) or 0)}

    def status(self) -> dict:
        self.refresh()
        state = load_supervisor_runtime_state(self.repo_root)
        return {
            "result": "complete",
            "run_manifest_path": _repo_rel(self.repo_root, self.runtime_paths["manifest_path"]),
            "run_manifest": dict(self.run_spec.get("run_manifest") or {}),
            "state": state,
            "processes": list(_as_list(state.get("processes"))),
            "latest_logs": list(_as_list(state.get("latest_logs"))),
        }


def launch_supervisor_service(
    *,
    repo_root: str,
    seed: str,
    session_template_id: str = "session.mvp_default",
    session_template_path: str = "",
    profile_bundle_path: str = "",
    pack_lock_path: str = "",
    mod_policy_id: str = "",
    overlay_conflict_policy_id: str = "",
    contract_bundle_hash: str = "",
    supervisor_policy_id: str = DEFAULT_SUPERVISOR_POLICY_ID,
    topology: str = DEFAULT_TOPOLOGY,
) -> dict:
    if discover_active_supervisor_endpoint(repo_root):
        return _refuse(
            REFUSAL_SUPERVISOR_ALREADY_RUNNING,
            "a launcher supervisor is already running",
            "Run `launcher status` or `launcher stop` before starting another supervised run.",
        )
    run_spec = build_supervisor_run_spec(
        repo_root=repo_root,
        seed=seed,
        session_template_id=session_template_id,
        session_template_path=session_template_path,
        profile_bundle_path=profile_bundle_path,
        pack_lock_path=pack_lock_path,
        mod_policy_id=mod_policy_id,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
        contract_bundle_hash=contract_bundle_hash,
        supervisor_policy_id=supervisor_policy_id,
        topology=topology,
    )
    if str(run_spec.get("result", "")).strip() != "complete":
        return dict(run_spec)
    arg_payload = canonicalize_args(
        positional=[],
        flag_pairs=(
            ("--contract-bundle-hash", str(run_spec.get("contract_bundle_hash", "")).strip()),
            *_supervisor_vpath_flag_pairs(),
            ("--mod-policy-id", str(run_spec.get("mod_policy_id", "")).strip()),
            ("--overlay-conflict-policy-id", str(run_spec.get("overlay_conflict_policy_id", "")).strip()),
            ("--pack-lock-path", str(run_spec.get("pack_lock_path", "")).strip()),
            ("--profile-bundle-path", str(run_spec.get("profile_bundle_path", "")).strip()),
            ("--repo-root", "."),
            ("--seed", str(run_spec.get("seed", "")).strip()),
            ("--session-template-id", str(run_spec.get("session_template_id", "")).strip()),
            ("--session-template-path", str(run_spec.get("session_template_path", "")).strip()),
            ("--supervisor-policy-id", str(run_spec.get("supervisor_policy_id", "")).strip()),
            ("--topology", str(run_spec.get("topology", "")).strip()),
        ),
    )
    process_spec = build_python_process_spec(
        repo_root=repo_root,
        spawn_id="spawn.supervisor.service",
        script_path=SUPERVISOR_SERVICE_SCRIPT_REL,
        module_name=SUPERVISOR_SERVICE_MODULE,
        args=list(arg_payload.get("args") or []),
        extensions={
            "service_session_id": str(run_spec.get("session_id", "")).strip(),
            "args_hash": str(arg_payload.get("args_hash", "")).strip(),
            "argv_text_hash": str(arg_payload.get("argv_text_hash", "")).strip(),
        },
    )
    spawned = spawn_process(process_spec)
    if str(spawned.get("result", "")).strip() != "complete":
        return dict(spawned)
    ready_payload, ready_error = _parse_stdout_json_line(spawned.get("process"))
    if ready_error or str(ready_payload.get("result", "")).strip() != "complete":
        return _refuse(
            REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED,
            "supervisor service did not emit a deterministic ready handshake",
            "Inspect launcher logs and retry the supervised start command.",
            details={"ready_error": ready_error},
        )
    ready = _wait_for_endpoint_ready_process(
        repo_root,
        spawned.get("process"),
        local_product_id="launcher",
        product_id="launcher",
        session_id=str(ready_payload.get("session_id", "")).strip() or str(run_spec.get("session_id", "")).strip(),
        endpoint_id=str(ready_payload.get("endpoint_id", "")).strip() or _build_endpoint_id("launcher", str(run_spec.get("session_id", "")).strip()),
        iterations=_ready_poll_iterations(run_spec),
    )
    if str(ready.get("result", "")).strip() != "complete":
        return _refuse(
            REFUSAL_SUPERVISOR_ENDPOINT_UNREACHED,
            "supervisor service did not report readiness",
            "Inspect launcher logs and retry the supervised start command.",
            details={"ready_refusal_code": str(ready.get("refusal_code", "")).strip()},
        )
    return {
        "result": "complete",
        "service_endpoint_id": str(ready.get("endpoint_id", "")).strip(),
        "service_address": str(_as_map(ready.get("ready_payload")).get("address", "")).strip(),
        "run_manifest_path": str(_as_map(run_spec.get("runtime_paths")).get("manifest_path", "")).strip(),
        "supervisor_state_path": str(_as_map(run_spec.get("runtime_paths")).get("state_path", "")).strip(),
        "run_spec": run_spec,
    }


__all__ = [
    "DEFAULT_SUPERVISOR_POLICY_ID",
    "SUPERVISOR_AGGREGATED_LOG_REL",
    "SUPERVISOR_RUN_MANIFEST_REL",
    "SUPERVISOR_STATE_REL",
    "SupervisorEngine",
    "attach_supervisor_children",
    "clear_current_supervisor_engine",
    "discover_active_supervisor_endpoint",
    "get_current_supervisor_engine",
    "invoke_supervisor_service_command",
    "launch_supervisor_service",
    "load_supervisor_runtime_state",
    "set_current_supervisor_engine",
]
