"""Deterministic AppShell command engine."""

from __future__ import annotations

import argparse
import json
import os
from typing import Mapping, Sequence

from src.compat import build_compat_status_payload, build_product_descriptor, negotiate_product_endpoints
from src.appshell.command_registry import build_root_command_descriptors, find_command_descriptor, format_help_text
from src.appshell.compat_adapter import build_version_payload, emit_descriptor_payload
from src.appshell.config_loader import list_pack_manifests, list_profile_bundles
from src.appshell.console_repl import build_console_session_stub
from src.appshell.diag import write_diag_snapshot_bundle
from src.diag import write_repro_bundle
from src.appshell.ipc import (
    attach_ipc_endpoint,
    detach_ipc_session,
    discover_ipc_endpoints,
    get_current_ipc_endpoint_server,
    query_ipc_log_events,
    query_ipc_status,
    run_ipc_console_command,
)
from src.appshell.logging import get_current_log_engine, log_emit
from src.appshell.pack_verifier_adapter import verify_pack_root
from src.appshell.paths import (
    VROOT_LOCKS,
    VROOT_LOGS,
    VROOT_PROFILES,
    get_current_virtual_paths,
    vpath_candidate_roots,
    vpath_resolve,
)
from src.appshell.supervisor import (
    DEFAULT_SUPERVISOR_POLICY_ID,
    attach_supervisor_children,
    discover_active_supervisor_endpoint,
    get_current_supervisor_engine,
    invoke_supervisor_service_command,
    launch_supervisor_service,
    load_supervisor_runtime_state,
)
from src.appshell.ui_mode_selector import get_current_ui_mode_selection
from src.tools import (
    execute_tool_surface_subprocess,
    format_tool_surface_area_help,
    format_tool_surface_root_help,
    tool_surface_row_from_command,
)
from src.validation import build_validation_report, write_validation_outputs


REFUSAL_TO_EXIT_REGISTRY_REL = os.path.join("data", "registries", "refusal_to_exit_registry.json")
EXIT_INTERNAL = 60
EXIT_SUCCESS = 0


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _refusal(
    refusal_code: str,
    reason: str,
    remediation_hint: str,
    *,
    details: Mapping[str, object] | None = None,
) -> dict:
    detail_map = {}
    for key, value in sorted((dict(details or {})).items(), key=lambda item: str(item[0])):
        token = value
        if isinstance(token, (dict, list)):
            detail_map[str(key)] = token
            continue
        text = str(token).strip()
        if text:
            detail_map[str(key)] = text
    return {
        "result": "refused",
        "refusal_code": str(refusal_code).strip(),
        "reason": str(reason).strip(),
        "remediation_hint": str(remediation_hint).strip(),
        "details": detail_map,
        "refusal": {
            "reason_code": str(refusal_code).strip(),
            "message": str(reason).strip(),
            "remediation_hint": str(remediation_hint).strip(),
            "relevant_ids": {
                str(key): str(value)
                for key, value in sorted(detail_map.items(), key=lambda item: str(item[0]))
                if not isinstance(value, (dict, list))
            },
        },
        "errors": [
            {
                "code": str(refusal_code).strip(),
                "message": str(reason).strip(),
                "path": "$",
            }
        ],
    }


def _load_refusal_to_exit_registry(repo_root: str) -> tuple[list[dict], str]:
    payload, error = _read_json(os.path.join(repo_root, REFUSAL_TO_EXIT_REGISTRY_REL))
    if error:
        return [], error
    rows = []
    record = dict(payload.get("record") or {})
    for row in list(record.get("mappings") or []):
        if not isinstance(row, Mapping):
            continue
        rows.append(dict(row))
    rows = sorted(
        rows,
        key=lambda row: (
            not str(row.get("refusal_code", "")).strip(),
            -len(str(row.get("refusal_prefix", "")).strip()),
            str(row.get("refusal_code", "")).strip(),
            str(row.get("refusal_prefix", "")).strip(),
        ),
    )
    return rows, ""


def _exit_code_for_refusal(repo_root: str, refusal_code: str) -> int:
    rows, error = _load_refusal_to_exit_registry(repo_root)
    if error:
        return EXIT_INTERNAL
    token = str(refusal_code or "").strip()
    for row in rows:
        exact = str(row.get("refusal_code", "")).strip()
        if exact and token == exact:
            return int(row.get("exit_code", EXIT_INTERNAL) or EXIT_INTERNAL)
    for row in rows:
        prefix = str(row.get("refusal_prefix", "")).strip()
        if prefix and token.startswith(prefix):
            return int(row.get("exit_code", EXIT_INTERNAL) or EXIT_INTERNAL)
    return EXIT_INTERNAL


def _json_dispatch(payload: Mapping[str, object], exit_code: int = EXIT_SUCCESS) -> dict:
    return {
        "dispatch_kind": "json",
        "payload": dict(payload or {}),
        "exit_code": int(exit_code),
    }


def _text_dispatch(text: str, exit_code: int = EXIT_SUCCESS) -> dict:
    return {
        "dispatch_kind": "text",
        "text": str(text or ""),
        "exit_code": int(exit_code),
    }


def _refusal_dispatch(repo_root: str, refusal_code: str, reason: str, remediation_hint: str, *, details: Mapping[str, object] | None = None) -> dict:
    payload = _refusal(refusal_code, reason, remediation_hint, details=details)
    log_emit(
        category="refusal",
        severity="error",
        message_key="appshell.refusal",
        params={
            "refusal_code": str(refusal_code).strip(),
            "reason": str(reason).strip(),
        },
    )
    return _json_dispatch(payload, _exit_code_for_refusal(repo_root, refusal_code))


def _build_verify_parser(prog: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog, add_help=False)
    parser.add_argument("--root", default="dist")
    parser.add_argument("--bundle-id", default="")
    parser.add_argument("--mod-policy-id", default="mod_policy.lab")
    parser.add_argument("--overlay-conflict-policy-id", default="")
    parser.add_argument("--contract-bundle-path", default="")
    parser.add_argument("--out-report", default="")
    parser.add_argument("--out-lock", default="")
    parser.add_argument("--write-outputs", action="store_true")
    return parser


def _parse_command_args(repo_root: str, parser: argparse.ArgumentParser, command_path: str, args: Sequence[str]) -> tuple[argparse.Namespace | None, dict | None]:
    try:
        parsed = parser.parse_args(list(args or []))
    except SystemExit:
        return None, _refusal(
            "refusal.io.invalid_args",
            "arguments are invalid for the requested command",
            "Run `help {}` to inspect the stable command shape.".format(str(command_path).strip()),
            details={"command_path": str(command_path).strip()},
        )
    return parsed, None


def _run_help_command(repo_root: str, product_id: str, topic_tokens: Sequence[str]) -> dict:
    rows = build_command_rows(repo_root, product_id)
    return _text_dispatch(format_help_text(product_id, rows, topic_tokens))


def _run_version_command(repo_root: str, product_id: str) -> dict:
    return _json_dispatch(build_version_payload(repo_root, product_id=product_id))


def _run_descriptor_command(repo_root: str, product_id: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="descriptor", add_help=False)
    parser.add_argument("--descriptor-file", default="")
    parsed, refusal = _parse_command_args(repo_root, parser, "descriptor", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    return _json_dispatch(
        emit_descriptor_payload(
            repo_root,
            product_id=product_id,
            descriptor_file=str(getattr(parsed, "descriptor_file", "")).strip(),
        )
    )


def _load_descriptor_payload(peer_descriptor_file: str) -> tuple[dict, str]:
    payload, error = _read_json(str(peer_descriptor_file))
    if error:
        return {}, error
    if isinstance(payload.get("descriptor"), Mapping):
        return dict(payload.get("descriptor") or {}), ""
    return dict(payload), ""


def _run_compat_status_command(repo_root: str, product_id: str, mode_id: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="compat-status", add_help=False)
    parser.add_argument("--peer-product-id", default="")
    parser.add_argument("--peer-descriptor-file", default="")
    parser.add_argument("--allow-read-only", action="store_true")
    parser.add_argument("--contract-bundle-hash", default="")
    parsed, refusal = _parse_command_args(repo_root, parser, "compat-status", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    endpoint_a = build_product_descriptor(repo_root, product_id=product_id)
    peer_file = str(getattr(parsed, "peer_descriptor_file", "")).strip()
    peer_product_id = str(getattr(parsed, "peer_product_id", "")).strip()
    if peer_file:
        endpoint_b, error = _load_descriptor_payload(peer_file)
        if error:
            return _refusal_dispatch(
                repo_root,
                "refusal.io.invalid_args",
                "peer descriptor file is missing or invalid",
                "Provide a valid `--peer-descriptor-file` emitted by a product `--descriptor` command.",
                details={"peer_descriptor_file": peer_file},
            )
    elif peer_product_id:
        endpoint_b = build_product_descriptor(repo_root, product_id=peer_product_id)
    else:
        endpoint_b = build_product_descriptor(repo_root, product_id=product_id)
    negotiated = negotiate_product_endpoints(
        repo_root,
        endpoint_a,
        endpoint_b,
        allow_read_only=bool(getattr(parsed, "allow_read_only", False)),
        chosen_contract_bundle_hash=str(getattr(parsed, "contract_bundle_hash", "")).strip(),
    )
    negotiation_record = dict(negotiated.get("negotiation_record") or {})
    status_payload = build_compat_status_payload(
        negotiation_record,
        product_id=product_id,
        connection_id="",
    )
    status_payload["peer_product_id"] = str(dict(endpoint_b).get("product_id", "")).strip()
    status_payload["negotiation_record_hash"] = str(negotiated.get("negotiation_record_hash", "")).strip()
    status_payload["endpoint_descriptor_hashes"] = {
        "endpoint_a_hash": str(negotiated.get("endpoint_a_hash", "")).strip(),
        "endpoint_b_hash": str(negotiated.get("endpoint_b_hash", "")).strip(),
    }
    mode_selection = dict(get_current_ui_mode_selection() or {})
    vpath_context = dict(get_current_virtual_paths() or {})
    status_payload["mode_selection"] = {
        "requested_mode_id": str(mode_selection.get("requested_mode_id", "")).strip(),
        "selected_mode_id": str(mode_selection.get("selected_mode_id", "")).strip() or str(mode_id).strip(),
        "mode_source": str(mode_selection.get("mode_source", "")).strip() or "runtime",
        "context_kind": str(mode_selection.get("context_kind", "")).strip(),
        "compatibility_mode_id": str(mode_selection.get("compatibility_mode_id", "")).strip() or "compat.full",
        "degrade_chain": list(mode_selection.get("degrade_chain") or []),
    }
    install_discovery = dict(vpath_context.get("install_discovery") or {})
    status_payload["install_discovery"] = {
        "result": str(install_discovery.get("result", "")).strip() or str(vpath_context.get("result", "")).strip(),
        "refusal_code": str(install_discovery.get("refusal_code", "")).strip() or str(vpath_context.get("refusal_code", "")).strip(),
        "mode": str(install_discovery.get("mode", "")).strip(),
        "resolution_source": str(install_discovery.get("resolution_source", "")).strip() or str(vpath_context.get("resolution_source", "")).strip(),
        "resolved_install_id": str(install_discovery.get("resolved_install_id", "")).strip() or str(vpath_context.get("install_id", "")).strip(),
        "resolved_install_root_path": str(install_discovery.get("resolved_install_root_path", "")).strip()
        or str(dict(vpath_context.get("roots") or {}).get("VROOT_INSTALL", "")).strip(),
        "install_manifest_path": str(install_discovery.get("install_manifest_path", "")).strip()
        or str(vpath_context.get("install_manifest_path", "")).strip(),
        "install_registry_path": str(install_discovery.get("install_registry_path", "")).strip()
        or str(vpath_context.get("install_registry_path", "")).strip(),
        "registry_candidate_paths": list(install_discovery.get("registry_candidate_paths") or []),
        "warnings": list(install_discovery.get("warnings") or list(vpath_context.get("warnings") or [])),
        "deterministic_fingerprint": str(install_discovery.get("deterministic_fingerprint", "")).strip(),
    }
    if str(negotiated.get("result", "")).strip() == "refused":
        log_emit(
            category="compat",
            severity="warn",
            message_key="compat.negotiation.refused",
            params={
                "product_id": str(product_id).strip(),
                "peer_product_id": str(dict(endpoint_b).get("product_id", "")).strip(),
            },
        )
        refusal_payload = dict(negotiated.get("refusal") or {})
        return _refusal_dispatch(
            repo_root,
            str(refusal_payload.get("reason_code", "")).strip() or "refusal.compat.contract_mismatch",
            str(refusal_payload.get("message", "")).strip() or "compatibility negotiation refused the connection",
            str(refusal_payload.get("remediation_hint", "")).strip() or "Provide compatible endpoint descriptors or allow read-only mode.",
            details={"compatibility_mode_id": str(negotiated.get("compatibility_mode_id", "")).strip()},
        )
    log_emit(
        category="compat",
        severity="info",
        message_key="compat.negotiation.result",
        params={
            "product_id": str(product_id).strip(),
            "peer_product_id": str(dict(endpoint_b).get("product_id", "")).strip(),
            "compatibility_mode_id": str(negotiated.get("compatibility_mode_id", "")).strip(),
            "disabled_capability_count": int(len(list(negotiation_record.get("disabled_capabilities") or []))),
        },
    )
    return _json_dispatch(status_payload)


def _run_packs_list_command(repo_root: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="packs list", add_help=False)
    parser.add_argument("--root", default="")
    parsed, refusal = _parse_command_args(repo_root, parser, "packs list", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    return _json_dispatch(
        {
            "result": "complete",
            "packs": list_pack_manifests(repo_root, root=str(getattr(parsed, "root", "")).strip()),
        }
    )


def _verify_pack_command(repo_root: str, args: Sequence[str], *, build_lock: bool) -> dict:
    parser = _build_verify_parser("packs build-lock" if build_lock else "packs verify")
    parsed, refusal = _parse_command_args(repo_root, parser, "packs build-lock" if build_lock else "packs verify", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    out_report = str(getattr(parsed, "out_report", "")).strip()
    out_lock = str(getattr(parsed, "out_lock", "")).strip()
    if build_lock:
        context = get_current_virtual_paths()
        if not out_report:
            if context is not None and str(context.get("result", "")).strip() == "complete":
                out_report = vpath_resolve(VROOT_LOGS, "pack_compatibility_report.json", context)
            else:
                out_report = os.path.join(repo_root, "build", "appshell", "pack_compatibility_report.json")
        if not out_lock:
            if context is not None and str(context.get("result", "")).strip() == "complete":
                out_lock = vpath_resolve(VROOT_LOCKS, "pack_lock.json", context)
            else:
                out_lock = os.path.join(repo_root, "build", "appshell", "pack_lock.json")
    result = verify_pack_root(
        repo_root=repo_root,
        root=str(getattr(parsed, "root", "")).strip(),
        bundle_id=str(getattr(parsed, "bundle_id", "")).strip(),
        mod_policy_id=str(getattr(parsed, "mod_policy_id", "")).strip(),
        overlay_conflict_policy_id=str(getattr(parsed, "overlay_conflict_policy_id", "")).strip(),
        contract_bundle_path=str(getattr(parsed, "contract_bundle_path", "")).strip(),
        out_report=out_report,
        out_lock=out_lock,
        write_outputs=bool(build_lock or getattr(parsed, "write_outputs", False)),
    )
    log_emit(
        category="packs",
        severity="info" if str(result.get("result", "")).strip() == "complete" else "warn",
        message_key="packs.lock.generated" if build_lock and str(result.get("result", "")).strip() == "complete" else "packs.verify.result",
        params={
            "result": str(result.get("result", "")).strip(),
            "dist_root": str(result.get("dist_root", "")).strip(),
            "error_count": int(len(list(result.get("errors") or []))),
            "warning_count": int(len(list(result.get("warnings") or []))),
        },
    )
    exit_code = EXIT_SUCCESS if str(result.get("result", "")).strip() == "complete" else _exit_code_for_refusal(
        repo_root,
        "refusal.pack.schema_invalid" if list(result.get("errors") or []) else "refusal.pack.contract_range_mismatch",
    )
    return _json_dispatch(result, exit_code)


def _load_profile_bundle(repo_root: str, bundle_id: str) -> tuple[dict, str]:
    token = str(bundle_id or "").strip()
    if not token:
        return {}, "missing bundle_id"
    context = get_current_virtual_paths()
    roots = []
    if context is not None and str(context.get("result", "")).strip() == "complete":
        for base_root in vpath_candidate_roots(VROOT_PROFILES, context):
            roots.append(base_root)
            roots.append(os.path.join(base_root, "bundles"))
    else:
        roots.extend(
            (
                os.path.join(repo_root, "profiles", "bundles"),
                os.path.join(repo_root, "dist", "profiles"),
            )
        )
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in sorted(entry for entry in os.listdir(root) if entry.endswith(".json")):
            payload, error = _read_json(os.path.join(root, name))
            if error:
                continue
            bundle_id = str(payload.get("bundle_id", "")).strip() or str(payload.get("profile_bundle_id", "")).strip()
            if bundle_id == token:
                return payload, ""
    return {}, "not found"


def _run_profiles_list_command(repo_root: str) -> dict:
    return _json_dispatch({"result": "complete", "profiles": list_profile_bundles(repo_root)})


def _run_profiles_show_command(repo_root: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="profiles show", add_help=False)
    parser.add_argument("bundle_id_positional", nargs="?")
    parser.add_argument("--bundle-id", default="")
    parsed, refusal = _parse_command_args(repo_root, parser, "profiles show", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    bundle_id = str(getattr(parsed, "bundle_id", "")).strip() or str(getattr(parsed, "bundle_id_positional", "")).strip()
    if not bundle_id:
        return _refusal_dispatch(
            repo_root,
            "refusal.io.invalid_args",
            "profiles show requires a bundle id",
            "Provide `profiles show <bundle_id>` or `profiles show --bundle-id <bundle_id>`.",
            details={"command_path": "profiles show"},
        )
    payload, error = _load_profile_bundle(repo_root, bundle_id)
    if error:
        return _refusal_dispatch(
            repo_root,
            "refusal.io.profile_not_found",
            "profile bundle was not found",
            "Run `profiles list` and choose an available bundle id.",
            details={"bundle_id": bundle_id},
        )
    return _json_dispatch({"result": "complete", "profile": payload})


def _run_validate_command(repo_root: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="validate", add_help=False)
    parser.add_argument("--all", dest="run_all", action="store_true")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    parsed, refusal = _parse_command_args(repo_root, parser, "validate", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    if not bool(getattr(parsed, "run_all", False)):
        return _refusal_dispatch(
            repo_root,
            "refusal.io.invalid_args",
            "validate requires the explicit `--all` selector",
            "Run `validate --all --profile FAST|STRICT|FULL` through AppShell.",
            details={"command_path": "validate"},
        )
    profile = str(getattr(parsed, "profile", "FAST") or "FAST").strip().upper() or "FAST"
    report = build_validation_report(repo_root, profile=profile)
    write_validation_outputs(repo_root, report)
    log_emit(
        category="validation",
        severity="info" if str(report.get("result", "")).strip() == "complete" else "warn",
        message_key="validation.pipeline.result",
        params={
            "profile": profile,
            "result": str(report.get("result", "")).strip(),
            "suite_count": int(dict(report.get("metrics") or {}).get("suite_count", 0) or 0),
            "error_count": int(len(list(report.get("errors") or []))),
        },
    )
    return _json_dispatch(report, EXIT_SUCCESS if str(report.get("result", "")).strip() == "complete" else 1)


def _run_diag_command(repo_root: str, product_id: str, mode_id: str) -> dict:
    descriptor = emit_descriptor_payload(repo_root, product_id=product_id)
    logger = get_current_log_engine()
    return _json_dispatch(
        {
            "result": "complete",
            "product_id": str(product_id).strip(),
            "mode": str(mode_id).strip(),
            "repo_root": str(repo_root).replace("\\", "/"),
            "descriptor_hash": str(descriptor.get("descriptor_hash", "")).strip(),
            "log_file_path": str(getattr(logger, "file_path", "")).replace("\\", "/"),
            "ring_event_count": int(len(list(logger.ring_events() if logger is not None else []))),
        }
    )


def _run_diag_snapshot_command(repo_root: str, product_id: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="diag snapshot", add_help=False)
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--session-spec-path", default="")
    parser.add_argument("--pack-lock-path", default="")
    parser.add_argument("--contract-bundle-hash", default="")
    parser.add_argument("--proof-anchor-dir", default="")
    parser.add_argument("--log-tail", default=32, type=int)
    parsed, refusal = _parse_command_args(repo_root, parser, "diag snapshot", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    logger = get_current_log_engine()
    snapshot = write_diag_snapshot_bundle(
        repo_root=repo_root,
        product_id=product_id,
        descriptor_payload=emit_descriptor_payload(repo_root, product_id=product_id),
        out_dir=str(getattr(parsed, "out_dir", "")).strip(),
        session_spec_path=str(getattr(parsed, "session_spec_path", "")).strip(),
        pack_lock_path=str(getattr(parsed, "pack_lock_path", "")).strip(),
        contract_bundle_hash=str(getattr(parsed, "contract_bundle_hash", "")).strip(),
        proof_anchor_dir=str(getattr(parsed, "proof_anchor_dir", "")).strip(),
        log_events=list(logger.ring_events() if logger is not None else []),
        log_tail=int(max(0, int(getattr(parsed, "log_tail", 32) or 32))),
        ipc_attach_rows=list((get_current_ipc_endpoint_server().recent_attach_records() if get_current_ipc_endpoint_server() is not None else [])),
    )
    log_emit(
        category="diag",
        severity="info",
        message_key="diag.snapshot.written",
        params={
            "product_id": str(product_id).strip(),
            "bundle_dir": str(snapshot.get("bundle_dir", "")).replace("\\", "/"),
            "manifest_path": str(snapshot.get("manifest_path", "")).replace("\\", "/"),
        },
    )
    return _json_dispatch(snapshot)


def _run_diag_capture_command(repo_root: str, product_id: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="diag capture", add_help=False)
    parser.add_argument("--out", default="")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--window", type=int, default=32)
    parser.add_argument("--include-views", action="store_true")
    parser.add_argument("--session-spec-path", default="")
    parser.add_argument("--pack-lock-path", default="")
    parser.add_argument("--contract-bundle-path", default="")
    parser.add_argument("--run-manifest-path", default="")
    parser.add_argument("--proof-anchor-dir", default="")
    parser.add_argument("--overlay-manifest-hash", default="")
    parser.add_argument("--seed", default="")
    parser.add_argument("--session-template-id", default="")
    parsed, refusal = _parse_command_args(repo_root, parser, "diag capture", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))

    version_payload = build_version_payload(repo_root, product_id=product_id)
    logger = get_current_log_engine()
    ipc_server = get_current_ipc_endpoint_server()
    ipc_meta = dict(getattr(ipc_server, "session_metadata", {}) or {}) if ipc_server is not None else {}
    supervisor_engine = get_current_supervisor_engine()
    supervisor_run_spec = dict(getattr(supervisor_engine, "run_spec", {}) or {}) if supervisor_engine is not None else {}
    supervisor_paths = dict(getattr(supervisor_engine, "runtime_paths", {}) or {}) if supervisor_engine is not None else {}

    session_spec_path = str(getattr(parsed, "session_spec_path", "")).strip() or str(ipc_meta.get("session_spec_path", "")).strip()
    contract_bundle_path = str(getattr(parsed, "contract_bundle_path", "")).strip() or str(ipc_meta.get("contract_bundle_path", "")).strip()
    if (not contract_bundle_path) and session_spec_path:
        save_dir = os.path.dirname(os.path.normpath(os.path.abspath(session_spec_path)))
        candidate = os.path.join(save_dir, "universe_contract_bundle.json")
        if os.path.isfile(candidate):
            contract_bundle_path = candidate
    pack_lock_path = (
        str(getattr(parsed, "pack_lock_path", "")).strip()
        or str(ipc_meta.get("pack_lock_path", "")).strip()
        or str(supervisor_run_spec.get("pack_lock_path", "")).strip()
    )
    run_manifest_path = (
        str(getattr(parsed, "run_manifest_path", "")).strip()
        or str(ipc_meta.get("run_manifest_path", "")).strip()
        or str(supervisor_paths.get("manifest_path", "")).strip()
    )
    proof_anchor_dir = (
        str(getattr(parsed, "proof_anchor_dir", "")).strip()
        or str(ipc_meta.get("proof_anchor_dir", "")).strip()
    )
    bundle_result = write_repro_bundle(
        repo_root=repo_root,
        created_by_product_id=product_id,
        build_id=str(version_payload.get("build_id", "")).strip(),
        out_dir=str(getattr(parsed, "out_dir", "")).strip() or str(getattr(parsed, "out", "")).strip(),
        window=int(max(0, int(getattr(parsed, "window", 32) or 32))),
        include_views=bool(getattr(parsed, "include_views", False)),
        descriptor_payloads=[emit_descriptor_payload(repo_root, product_id=product_id)],
        run_manifest_path=run_manifest_path,
        session_spec_path=session_spec_path,
        contract_bundle_path=contract_bundle_path,
        pack_lock_path=pack_lock_path,
        semantic_contract_registry_hash=str(ipc_meta.get("semantic_contract_registry_hash", "")).strip(),
        contract_bundle_hash=str(ipc_meta.get("contract_bundle_hash", "")).strip() or str(supervisor_run_spec.get("contract_bundle_hash", "")).strip(),
        overlay_manifest_hash=(
            str(getattr(parsed, "overlay_manifest_hash", "")).strip()
            or str(ipc_meta.get("overlay_manifest_hash", "")).strip()
            or str(supervisor_run_spec.get("overlay_manifest_hash", "")).strip()
        ),
        seed=str(getattr(parsed, "seed", "")).strip() or str(ipc_meta.get("seed", "")).strip() or str(supervisor_run_spec.get("seed", "")).strip(),
        session_id=str(ipc_meta.get("session_id", "")).strip(),
        session_template_id=(
            str(getattr(parsed, "session_template_id", "")).strip()
            or str(ipc_meta.get("session_template_id", "")).strip()
            or str(supervisor_run_spec.get("session_template_id", "")).strip()
        ),
        proof_anchor_dir=proof_anchor_dir,
        log_events=list(logger.ring_events() if logger is not None else []),
        ipc_attach_rows=list(ipc_server.recent_attach_records() if ipc_server is not None else []),
    )
    log_emit(
        category="diag",
        severity="info",
        message_key="diag.capture.written",
        params={
            "product_id": str(product_id).strip(),
            "bundle_dir": str(bundle_result.get("bundle_dir", "")).replace("\\", "/"),
            "bundle_hash": str(bundle_result.get("bundle_hash", "")).strip(),
        },
    )
    return _json_dispatch(bundle_result)


def _run_console_command(repo_root: str, product_id: str) -> dict:
    rows = build_command_rows(repo_root, product_id)
    return _json_dispatch(build_console_session_stub(product_id, rows))


def _run_console_sessions_command(repo_root: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="console sessions", add_help=False)
    parser.add_argument("--manifest-path", default="")
    parsed, refusal = _parse_command_args(repo_root, parser, "console sessions", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    return _json_dispatch(discover_ipc_endpoints(repo_root, manifest_path=str(getattr(parsed, "manifest_path", "")).strip()))


def _run_console_attach_command(repo_root: str, product_id: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="console attach", add_help=False)
    parser.add_argument("--endpoint-id", required=True)
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--require-full", action="store_true")
    parser.add_argument("--disallow-read-only", action="store_true")
    parser.add_argument("--command", default="")
    parsed, refusal = _parse_command_args(repo_root, parser, "console attach", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    attach_result = attach_ipc_endpoint(
        repo_root,
        local_product_id=str(product_id).strip(),
        endpoint_id=str(getattr(parsed, "endpoint_id", "")).strip(),
        manifest_path=str(getattr(parsed, "manifest_path", "")).strip(),
        allow_read_only=not bool(getattr(parsed, "disallow_read_only", False)),
        accept_degraded=not bool(getattr(parsed, "require_full", False)),
    )
    if str(attach_result.get("result", "")).strip() != "complete":
        refusal_code = str(attach_result.get("refusal_code", "")).strip() or "refusal.connection.no_negotiation"
        if refusal_code == "refusal.connection.negotiation_mismatch":
            reason = "IPC attach negotiation record mismatch prevented session attach"
            remediation = "Retry the attach so both sides negotiate against the same descriptors and capability sets."
        elif refusal_code == "refusal.law.attach_denied":
            reason = "IPC attach was denied by the active law or attach policy"
            remediation = "Use an allowed local policy/profile or attach in a read-only-safe mode."
        else:
            reason = "IPC attach negotiation failed or was refused"
            remediation = "Inspect compat-status or attach to a compatible endpoint/mode."
        log_emit(
            category="ipc",
            severity="warn",
            message_key="ipc.attach.refused",
            params={
                "product_id": str(product_id).strip(),
                "endpoint_id": str(getattr(parsed, "endpoint_id", "")).strip(),
                "refusal_code": refusal_code,
            },
        )
        return _refusal_dispatch(
            repo_root,
            refusal_code,
            reason,
            remediation,
            details={
                "endpoint_id": str(getattr(parsed, "endpoint_id", "")).strip(),
                "compatibility_mode_id": str(attach_result.get("compatibility_mode_id", "")).strip(),
            },
        )
    status_result = query_ipc_status(repo_root, attach_result)
    log_result = query_ipc_log_events(repo_root, attach_result, limit=8)
    command_result = {}
    if str(getattr(parsed, "command", "")).strip():
        command_result = run_ipc_console_command(repo_root, attach_result, str(getattr(parsed, "command", "")).strip())
    log_emit(
        category="ipc",
        severity="info",
        message_key="ipc.attach.accepted",
        params={
            "product_id": str(product_id).strip(),
            "endpoint_id": str(getattr(parsed, "endpoint_id", "")).strip(),
            "compatibility_mode_id": str(dict(attach_result).get("compatibility_mode_id", "")).strip(),
        },
    )
    return _json_dispatch(
        {
            "result": "complete",
            "attach": attach_result,
            "status": dict(status_result.get("status") or {}),
            "log_events": list(log_result.get("events") or []),
            "command": command_result,
        }
    )


def _run_console_detach_command(repo_root: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="console detach", add_help=False)
    parser.add_argument("--endpoint-id", required=True)
    parsed, refusal = _parse_command_args(repo_root, parser, "console detach", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    return _json_dispatch(detach_ipc_session({"endpoint": {"endpoint_id": str(getattr(parsed, "endpoint_id", "")).strip()}}))


def _supervisor_state_payload(repo_root: str) -> dict:
    state = load_supervisor_runtime_state(repo_root)
    state_map = dict(state or {})
    process_rows = sorted(
        [dict(row) for row in list(state_map.get("processes") or []) if isinstance(row, Mapping)],
        key=lambda row: (str(row.get("product_id", "")), str(row.get("pid_stub", ""))),
    )
    return {
        "result": "complete",
        "service_running": bool(discover_active_supervisor_endpoint(repo_root)),
        "state": state_map,
        "processes": process_rows,
        "latest_logs": list(state_map.get("latest_logs") or []),
        "run_manifest_path": str(state_map.get("manifest_path", "")).strip(),
    }


def _run_launcher_start_command(repo_root: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="launcher start", add_help=False)
    parser.add_argument("--seed", default="0")
    parser.add_argument("--session-template-id", default="session.mvp_default")
    parser.add_argument("--session-template-path", default="")
    parser.add_argument("--profile-bundle-path", default="")
    parser.add_argument("--pack-lock-path", default="")
    parser.add_argument("--mod-policy-id", default="")
    parser.add_argument("--overlay-conflict-policy-id", default="")
    parser.add_argument("--contract-bundle-hash", default="")
    parser.add_argument("--supervisor-policy-id", default=DEFAULT_SUPERVISOR_POLICY_ID)
    parser.add_argument("--topology", choices=("singleplayer", "server_only"), default="singleplayer")
    parsed, refusal = _parse_command_args(repo_root, parser, "launcher start", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    if get_current_supervisor_engine() is not None:
        return _refusal_dispatch(
            repo_root,
            "refusal.supervisor.already_running",
            "this launcher process already owns an active supervisor engine",
            "Use `launcher status` or `launcher stop` instead of starting another supervisor in the same process.",
        )
    result = launch_supervisor_service(
        repo_root=repo_root,
        seed=str(getattr(parsed, "seed", "0") or "0").strip() or "0",
        session_template_id=str(getattr(parsed, "session_template_id", "session.mvp_default") or "session.mvp_default").strip(),
        session_template_path=str(getattr(parsed, "session_template_path", "") or "").strip(),
        profile_bundle_path=str(getattr(parsed, "profile_bundle_path", "") or "").strip(),
        pack_lock_path=str(getattr(parsed, "pack_lock_path", "") or "").strip(),
        mod_policy_id=str(getattr(parsed, "mod_policy_id", "") or "").strip(),
        overlay_conflict_policy_id=str(getattr(parsed, "overlay_conflict_policy_id", "") or "").strip(),
        contract_bundle_hash=str(getattr(parsed, "contract_bundle_hash", "") or "").strip(),
        supervisor_policy_id=str(getattr(parsed, "supervisor_policy_id", DEFAULT_SUPERVISOR_POLICY_ID) or DEFAULT_SUPERVISOR_POLICY_ID).strip(),
        topology=str(getattr(parsed, "topology", "singleplayer") or "singleplayer").strip(),
    )
    if str(result.get("result", "")).strip() != "complete":
        return _refusal_dispatch(
            repo_root,
            str(result.get("refusal_code", "")).strip() or "refusal.supervisor.endpoint_unreached",
            str(result.get("reason", "")).strip() or "launcher could not start the supervisor service",
            str(result.get("remediation_hint", "")).strip() or "Inspect pack verification and supervisor policy inputs, then retry launch.",
            details=dict(result.get("details") or {}),
        )
    attach_summary = attach_supervisor_children(repo_root, attach_all=True)
    payload = {
        "result": "complete",
        "service_endpoint_id": str(result.get("service_endpoint_id", "")).strip(),
        "service_address": str(result.get("service_address", "")).strip(),
        "run_manifest_path": str(result.get("run_manifest_path", "")).strip(),
        "supervisor_state_path": str(result.get("supervisor_state_path", "")).strip(),
        "attachments": list(attach_summary.get("attachments") or []),
        "run_spec": dict(result.get("run_spec") or {}),
    }
    log_emit(
        category="appshell",
        severity="info",
        message_key="supervisor.command.start",
        params={"service_endpoint_id": str(payload.get("service_endpoint_id", "")).strip()},
    )
    return _json_dispatch(payload)


def _run_launcher_status_command(repo_root: str) -> dict:
    engine = get_current_supervisor_engine()
    if engine is not None:
        return _json_dispatch(engine.status())
    endpoint = discover_active_supervisor_endpoint(repo_root)
    if endpoint:
        payload = invoke_supervisor_service_command(repo_root, "launcher status")
        if str(payload.get("result", "")).strip() == "complete":
            return _json_dispatch(payload)
    state_payload = _supervisor_state_payload(repo_root)
    if dict(state_payload.get("state") or {}):
        return _json_dispatch(state_payload)
    return _refusal_dispatch(
        repo_root,
        "refusal.supervisor.not_running",
        "no launcher supervisor is currently active",
        "Run `launcher start` before requesting supervisor status.",
    )


def _run_launcher_stop_command(repo_root: str) -> dict:
    engine = get_current_supervisor_engine()
    if engine is not None:
        return _json_dispatch(engine.stop(shutdown_supervisor=True))
    endpoint = discover_active_supervisor_endpoint(repo_root)
    if not endpoint:
        return _refusal_dispatch(
            repo_root,
            "refusal.supervisor.not_running",
            "no launcher supervisor is currently active",
            "Run `launcher start` before requesting shutdown.",
        )
    payload = invoke_supervisor_service_command(repo_root, "launcher stop")
    if str(payload.get("result", "")).strip() != "complete":
        return _refusal_dispatch(
            repo_root,
            str(payload.get("refusal_code", "")).strip() or "refusal.supervisor.endpoint_unreached",
            str(payload.get("reason", "")).strip() or "launcher supervisor stop failed",
            str(payload.get("remediation_hint", "")).strip() or "Inspect supervisor logs or retry the stop command.",
            details=dict(payload.get("details") or {}),
        )
    log_emit(
        category="appshell",
        severity="info",
        message_key="supervisor.command.stop",
        params={"endpoint_id": str(endpoint.get("endpoint_id", "")).strip()},
    )
    return _json_dispatch(payload)


def _run_launcher_attach_command(repo_root: str, args: Sequence[str]) -> dict:
    parser = argparse.ArgumentParser(prog="launcher attach", add_help=False)
    parser.add_argument("--endpoint-id", default="")
    parser.add_argument("--all", action="store_true")
    parsed, refusal = _parse_command_args(repo_root, parser, "launcher attach", args)
    if refusal is not None:
        return _json_dispatch(refusal, _exit_code_for_refusal(repo_root, str(refusal.get("refusal_code", ""))))
    if not discover_active_supervisor_endpoint(repo_root) and not dict(load_supervisor_runtime_state(repo_root) or {}):
        return _refusal_dispatch(
            repo_root,
            "refusal.supervisor.not_running",
            "no launcher supervisor is currently active",
            "Run `launcher start` before requesting IPC attachments.",
        )
    payload = attach_supervisor_children(
        repo_root,
        endpoint_id=str(getattr(parsed, "endpoint_id", "") or "").strip(),
        attach_all=bool(getattr(parsed, "all", False)),
    )
    log_emit(
        category="ipc",
        severity="info",
        message_key="supervisor.command.attach",
        params={
            "endpoint_id": str(getattr(parsed, "endpoint_id", "") or "").strip(),
            "attach_all": bool(getattr(parsed, "all", False)),
        },
    )
    return _json_dispatch(payload)


def _run_namespace_placeholder(repo_root: str, row: Mapping[str, object], attempted_tokens: Sequence[str]) -> dict:
    command_path = str(row.get("command_path", "")).strip()
    return _refusal_dispatch(
        repo_root,
        "refusal.debug.command_unavailable",
        "command namespace is declared but not bound in the APPSHELL-1 baseline",
        "Use the shared root commands, or wait for the product-specific subtree to be bound in a later AppShell phase.",
        details={
            "namespace": command_path,
            "attempted_command": " ".join(str(token).strip() for token in list(attempted_tokens or []) if str(token).strip()),
        },
    )


def _run_tool_surface_root_help(repo_root: str) -> dict:
    return _text_dispatch(format_tool_surface_root_help(repo_root))


def _run_tool_surface_area_help(repo_root: str, row: Mapping[str, object]) -> dict:
    spec = tool_surface_row_from_command(row)
    return _text_dispatch(format_tool_surface_area_help(repo_root, str(spec.get("area_id", "")).strip()))


def build_command_rows(repo_root: str, product_id: str) -> list[dict]:
    return build_root_command_descriptors(repo_root, product_id)


def dispatch_registered_command(
    repo_root: str,
    *,
    product_id: str,
    mode_id: str,
    command_tokens: Sequence[str],
) -> dict:
    tokens = [str(token).strip() for token in list(command_tokens or []) if str(token).strip()]
    if not tokens:
        return _json_dispatch({"result": "empty"}, EXIT_SUCCESS)
    log_emit(
        category="appshell",
        severity="info",
        message_key="appshell.command.dispatch",
        params={
            "product_id": str(product_id).strip(),
            "mode_id": str(mode_id).strip(),
            "command_path": " ".join(tokens),
        },
    )
    row, remaining, namespace_row = find_command_descriptor(repo_root, product_id, tokens)
    if not row:
        if namespace_row is not None:
            return _run_namespace_placeholder(repo_root, namespace_row, tokens)
        return _refusal_dispatch(
            repo_root,
            "refusal.debug.command_unknown",
            "command is not registered in the AppShell registry",
            "Run `--help` to inspect the stable command tree for this product.",
            details={"attempted_command": " ".join(tokens), "product_id": str(product_id).strip()},
        )
    handler_id = str(row.get("handler_id", "")).strip()
    if handler_id == "help":
        return _run_help_command(repo_root, product_id, remaining)
    if handler_id == "version":
        return _run_version_command(repo_root, product_id)
    if handler_id == "descriptor":
        return _run_descriptor_command(repo_root, product_id, remaining)
    if handler_id == "compat_status":
        return _run_compat_status_command(repo_root, product_id, mode_id, remaining)
    if handler_id == "packs_list":
        return _run_packs_list_command(repo_root, remaining)
    if handler_id == "packs_verify":
        return _verify_pack_command(repo_root, remaining, build_lock=False)
    if handler_id == "packs_build_lock":
        return _verify_pack_command(repo_root, remaining, build_lock=True)
    if handler_id == "profiles_list":
        return _run_profiles_list_command(repo_root)
    if handler_id == "profiles_show":
        return _run_profiles_show_command(repo_root, remaining)
    if handler_id == "validate":
        return _run_validate_command(repo_root, remaining)
    if handler_id == "diag":
        return _run_diag_command(repo_root, product_id, mode_id)
    if handler_id == "diag_snapshot":
        return _run_diag_snapshot_command(repo_root, product_id, remaining)
    if handler_id == "diag_capture":
        return _run_diag_capture_command(repo_root, product_id, remaining)
    if handler_id == "console_enter":
        return _run_console_command(repo_root, product_id)
    if handler_id == "console_sessions":
        return _run_console_sessions_command(repo_root, remaining)
    if handler_id == "console_attach":
        return _run_console_attach_command(repo_root, product_id, remaining)
    if handler_id == "console_detach":
        return _run_console_detach_command(repo_root, remaining)
    if handler_id == "launcher_start":
        return _run_launcher_start_command(repo_root, remaining)
    if handler_id == "launcher_status":
        return _run_launcher_status_command(repo_root)
    if handler_id == "launcher_stop":
        return _run_launcher_stop_command(repo_root)
    if handler_id == "launcher_attach":
        return _run_launcher_attach_command(repo_root, remaining)
    if handler_id == "tool_surface_root_help":
        return _run_tool_surface_root_help(repo_root)
    if handler_id == "tool_surface_area_help":
        return _run_tool_surface_area_help(repo_root, row)
    if handler_id == "tool_surface_adapter":
        spec = tool_surface_row_from_command(row)
        if str(spec.get("adapter_kind", "")).strip() == "appshell_alias":
            alias_product_id = str(spec.get("alias_product_id", "")).strip() or str(product_id).strip()
            alias_tokens = [str(token).strip() for token in list(spec.get("alias_command_tokens") or []) if str(token).strip()]
            return dispatch_registered_command(
                repo_root,
                product_id=alias_product_id,
                mode_id=mode_id,
                command_tokens=alias_tokens + list(remaining),
            )
        payload, exit_code = execute_tool_surface_subprocess(repo_root, row, remaining)
        return _json_dispatch(payload, exit_code)
    if handler_id == "namespace_placeholder":
        return _run_namespace_placeholder(repo_root, row, tokens)
    return _refusal_dispatch(
        repo_root,
        "refusal.debug.command_unavailable",
        "registered command does not have a bound handler",
        "Bind the command handler in the AppShell command engine.",
        details={"command_path": str(row.get("command_path", "")).strip(), "handler_id": handler_id},
    )


__all__ = ["dispatch_registered_command"]
