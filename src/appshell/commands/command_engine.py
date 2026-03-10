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


def _run_compat_status_command(repo_root: str, product_id: str, args: Sequence[str]) -> dict:
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
        if not out_report:
            out_report = os.path.join(repo_root, "build", "appshell", "pack_compatibility_report.json")
        if not out_lock:
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
    roots = (
        os.path.join(repo_root, "profiles", "bundles"),
        os.path.join(repo_root, "dist", "profiles"),
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
        return _run_compat_status_command(repo_root, product_id, remaining)
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
    if handler_id == "diag":
        return _run_diag_command(repo_root, product_id, mode_id)
    if handler_id == "diag_snapshot":
        return _run_diag_snapshot_command(repo_root, product_id, remaining)
    if handler_id == "console_enter":
        return _run_console_command(repo_root, product_id)
    if handler_id == "console_sessions":
        return _run_console_sessions_command(repo_root, remaining)
    if handler_id == "console_attach":
        return _run_console_attach_command(repo_root, product_id, remaining)
    if handler_id == "console_detach":
        return _run_console_detach_command(repo_root, remaining)
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
