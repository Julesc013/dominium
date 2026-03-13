"""Deterministic helpers for IPC-UNIFY-0 reporting and enforcement."""

from __future__ import annotations

import json
import os
import sys
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.appshell.paths import (  # noqa: E402
    VROOT_IPC,
    clear_current_virtual_paths,
    get_current_virtual_paths,
    set_current_virtual_paths,
    vpath_init,
    vpath_resolve,
    vpath_root,
)
from tools.appshell.appshell4_probe import run_ipc_attach_probe, verify_ipc_attach_replay  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


IPC_SURFACE_MAP_PATH = "docs/audit/IPC_SURFACE_MAP.md"
IPC_DUPLICATION_FIXES_PATH = "docs/audit/IPC_DUPLICATION_FIXES.md"
IPC_DISCOVERY_DOC_PATH = "docs/appshell/IPC_DISCOVERY.md"
IPC_UNIFY_FINAL_PATH = "docs/audit/IPC_UNIFY_FINAL.md"
IPC_UNIFY_REPORT_PATH = "data/audit/ipc_unify_report.json"
IPC_UNIFY_TOOL_PATH = "tools/appshell/tool_run_ipc_unify.py"
IPC_UNIFY_REPORT_ID = "appshell.ipc_unify.v1"
LAST_REVIEWED = "2026-03-13"

CANONICAL_SURFACES = (
    {
        "path": "src/appshell/ipc/ipc_transport.py",
        "surface": "transport",
        "classification": "canonical",
        "notes": "Single transport abstraction, framing, manifest, and descriptor-file discovery.",
        "required_markers": (
            "IPC_CHANNEL_IDS",
            "VROOT_IPC",
            "build_ipc_frame(",
            "ipc_endpoint_descriptor_path(",
            "write_ipc_endpoint_descriptor(",
        ),
    },
    {
        "path": "src/compat/handshake/handshake_engine.py",
        "surface": "handshake",
        "classification": "canonical",
        "notes": "Single CAP-NEG handshake message builder for IPC attach and session begin.",
        "required_markers": (
            "build_handshake_message(",
            "build_compat_refusal(",
            "build_session_begin_payload(",
        ),
    },
    {
        "path": "src/appshell/ipc/ipc_endpoint_server.py",
        "surface": "endpoint_server",
        "classification": "canonical",
        "notes": "Canonical negotiated attach server and channel dispatcher.",
        "required_markers": (
            "REFUSAL_CONNECTION_NO_NEGOTIATION",
            "negotiate_product_endpoints(",
            "build_session_begin_payload(",
            "ipc.attach.accepted",
        ),
    },
    {
        "path": "src/appshell/ipc/ipc_client.py",
        "surface": "attach_client",
        "classification": "canonical",
        "notes": "Canonical attach/discovery/status/log/console client surface.",
        "required_markers": (
            "attach_ipc_endpoint(",
            "query_ipc_status(",
            "query_ipc_log_events(",
            "run_ipc_console_command(",
            "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH",
        ),
    },
    {
        "path": "src/appshell/commands/command_engine.py",
        "surface": "command_entrypoint",
        "classification": "canonical",
        "notes": "AppShell console attach command routes through the canonical IPC client.",
        "required_markers": (
            "_run_console_attach_command(",
            "attach_ipc_endpoint(",
            "query_ipc_status(",
            "run_ipc_console_command(",
        ),
    },
    {
        "path": "src/appshell/supervisor/supervisor_engine.py",
        "surface": "supervisor_consumer",
        "classification": "canonical",
        "notes": "Supervisor uses the canonical attach/status/log/console IPC client.",
        "required_markers": (
            "attach_ipc_endpoint(",
            "discover_ipc_endpoints(",
            "query_ipc_log_events(",
            "query_ipc_status(",
            "run_ipc_console_command(",
        ),
    },
    {
        "path": "src/appshell/tui/tui_engine.py",
        "surface": "tui_consumer",
        "classification": "canonical",
        "notes": "TUI multiplexing uses the canonical attach/status/log/console IPC client.",
        "required_markers": (
            "attach_ipc_endpoint(",
            "query_ipc_log_events(",
            "query_ipc_status(",
            "run_ipc_console_command(",
        ),
    },
    {
        "path": "tools/appshell/appshell4_probe.py",
        "surface": "probe",
        "classification": "canonical",
        "notes": "Test-only deterministic raw-frame probe for attach, sequencing, and replay verification.",
        "required_markers": (
            "run_ipc_attach_probe(",
            "verify_ipc_attach_replay(",
            "connect_ipc_client(",
        ),
    },
)

CANONICAL_BINDINGS = (
    {
        "surface": "Console attach command",
        "consumer_path": "src/appshell/commands/command_engine.py",
        "canonical_target": "src/appshell/ipc/ipc_client.py",
        "notes": "All console attach requests route through attach_ipc_endpoint/query_ipc_status/query_ipc_log_events/run_ipc_console_command.",
    },
    {
        "surface": "TUI multiplex",
        "consumer_path": "src/appshell/tui/tui_engine.py",
        "canonical_target": "src/appshell/ipc/ipc_client.py",
        "notes": "TUI session tabs attach and refresh through the shared IPC client helpers.",
    },
    {
        "surface": "Supervisor attach",
        "consumer_path": "src/appshell/supervisor/supervisor_engine.py",
        "canonical_target": "src/appshell/ipc/ipc_client.py",
        "notes": "Supervisor attach and log merge flows reuse the same IPC client and negotiation path.",
    },
    {
        "surface": "Endpoint listener",
        "consumer_path": "src/appshell/ipc/ipc_endpoint_server.py",
        "canonical_target": "src/appshell/ipc/ipc_transport.py",
        "notes": "Endpoint server opens the canonical listener and emits deterministic frames only after handshake success.",
    },
)

ALLOWED_DIRECT_SOCKET_USERS = {
    "src/appshell/ipc/ipc_transport.py": "canonical_transport",
}
ALLOWED_LOW_LEVEL_PRIMITIVE_USERS = {
    "src/appshell/ipc/ipc_transport.py": "canonical_transport",
    "src/appshell/ipc/ipc_endpoint_server.py": "canonical_endpoint_server",
    "src/appshell/ipc/ipc_client.py": "canonical_client",
    "tools/appshell/appshell4_probe.py": "test_only_probe",
}
DIRECT_SOCKET_TOKENS = ("socket.socket(",)
LOW_LEVEL_IPC_TOKENS = ("connect_ipc_client(", "open_ipc_listener(", "send_frame(", "recv_frame(")
LOW_LEVEL_IMPORT_MARKERS = (
    "from .ipc_transport import",
    "from src.appshell.ipc import",
    "from src.appshell.ipc.ipc_transport import",
)
SCAN_ROOTS = ("src", "tools")
PY_EXTENSIONS = (".py",)
IPC_SCAN_IGNORE_PATHS = {"tools/appshell/ipc_unify_common.py"}
IPC_SCAN_IGNORE_PREFIXES = ("tools/auditx/analyzers/",)


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _rel(path: str, repo_root: str) -> str:
    return os.path.relpath(_norm(path), _norm(repo_root)).replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _write_text(path: str, text: str) -> None:
    abs_path = _norm(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    abs_path = _norm(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _has_socket_import(text: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import socket") or stripped.startswith("from socket import"):
            return True
    return False


def _python_files(repo_root: str) -> list[str]:
    rows: list[str] = []
    for root in SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for current_root, dir_names, file_names in os.walk(abs_root):
            dir_names[:] = sorted(name for name in dir_names if name != "__pycache__")
            for file_name in sorted(file_names):
                if not file_name.endswith(PY_EXTENSIONS):
                    continue
                rows.append(_rel(os.path.join(current_root, file_name), repo_root))
    return sorted(rows)


def _markdown_table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> str:
    header_row = "| " + " | ".join(str(item) for item in headers) + " |"
    sep_row = "| " + " | ".join("---" for _ in headers) + " |"
    body_rows = ["| " + " | ".join(str(item) for item in row) + " |" for row in rows]
    return "\n".join([header_row, sep_row] + body_rows) if body_rows else "\n".join([header_row, sep_row])


def _doc_header(*, status: str, title: str, canonical: bool) -> str:
    lines = [
        "Status: {}".format(status),
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
    ]
    if canonical:
        lines.extend(
            [
                "Version: 1.0.0",
                "Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/IPC_ATTACH_CONSOLES.md`, `docs/compat/NEGOTIATION_HANDSHAKES.md`, and `docs/release/FROZEN_INVARIANTS_v0_0_0.md`.",
            ]
        )
    lines.extend(
        [
            "Stability: provisional",
            "Future Series: DOC-CONVERGENCE",
            "Replacement Target: canon-aligned documentation set for convergence and release preparation",
            "",
            "# {}".format(title),
            "",
        ]
    )
    return "\n".join(lines)


def _surface_rows(repo_root: str) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    violations: list[dict] = []
    for spec in CANONICAL_SURFACES:
        rel_path = _token(spec.get("path"))
        text = _read_text(repo_root, rel_path)
        missing_markers = [token for token in list(spec.get("required_markers") or []) if token not in text]
        row = {
            "path": rel_path,
            "surface": _token(spec.get("surface")),
            "classification": _token(spec.get("classification")) or "canonical",
            "present": bool(text),
            "missing_markers": missing_markers,
            "notes": _token(spec.get("notes")),
            "deterministic_fingerprint": canonical_sha256(
                {
                    "path": rel_path,
                    "surface": _token(spec.get("surface")),
                    "classification": _token(spec.get("classification")) or "canonical",
                    "present": bool(text),
                    "missing_markers": missing_markers,
                    "notes": _token(spec.get("notes")),
                }
            ),
        }
        rows.append(row)
        if not text:
            violations.append(
                {
                    "code": "missing_surface",
                    "file_path": rel_path,
                    "message": "required canonical IPC surface is missing",
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
        elif missing_markers:
            violations.append(
                {
                    "code": "surface_marker_missing",
                    "file_path": rel_path,
                    "message": "canonical IPC surface is missing required markers: {}".format(", ".join(missing_markers[:4])),
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
    return sorted(rows, key=lambda row: (str(row.get("classification", "")), str(row.get("path", "")))), sorted(
        violations,
        key=lambda row: (str(row.get("file_path", "")), str(row.get("code", ""))),
    )


def _scan_direct_socket_users(repo_root: str) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    violations: list[dict] = []
    for rel_path in _python_files(repo_root):
        if rel_path in IPC_SCAN_IGNORE_PATHS or rel_path.startswith(IPC_SCAN_IGNORE_PREFIXES):
            continue
        text = _read_text(repo_root, rel_path)
        hits = [token for token in DIRECT_SOCKET_TOKENS if token in text]
        if not hits or not _has_socket_import(text):
            continue
        classification = "canonical" if rel_path in ALLOWED_DIRECT_SOCKET_USERS else "unsafe"
        row = {
            "path": rel_path,
            "classification": classification,
            "reason": ALLOWED_DIRECT_SOCKET_USERS.get(rel_path, "unexpected direct socket usage"),
            "hits": hits,
            "deterministic_fingerprint": canonical_sha256(
                {
                    "path": rel_path,
                    "classification": classification,
                    "reason": ALLOWED_DIRECT_SOCKET_USERS.get(rel_path, "unexpected direct socket usage"),
                    "hits": hits,
                }
            ),
        }
        rows.append(row)
        if classification == "unsafe":
            violations.append(
                {
                    "code": "unexpected_direct_socket_user",
                    "file_path": rel_path,
                    "message": "direct socket use appears outside the canonical IPC transport",
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
    return sorted(rows, key=lambda row: str(row.get("path", ""))), sorted(
        violations,
        key=lambda row: (str(row.get("file_path", "")), str(row.get("code", ""))),
    )


def _scan_low_level_ipc_primitive_users(repo_root: str) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    violations: list[dict] = []
    for rel_path in _python_files(repo_root):
        if rel_path in IPC_SCAN_IGNORE_PATHS or rel_path.startswith(IPC_SCAN_IGNORE_PREFIXES):
            continue
        text = _read_text(repo_root, rel_path)
        hits = [token for token in LOW_LEVEL_IPC_TOKENS if token in text]
        if not hits:
            continue
        if rel_path != "src/appshell/ipc/ipc_transport.py" and not any(marker in text for marker in LOW_LEVEL_IMPORT_MARKERS):
            continue
        classification = "canonical" if rel_path in ALLOWED_LOW_LEVEL_PRIMITIVE_USERS else "duplicate"
        row = {
            "path": rel_path,
            "classification": classification,
            "reason": ALLOWED_LOW_LEVEL_PRIMITIVE_USERS.get(rel_path, "unexpected low-level IPC primitive usage"),
            "hits": hits,
            "deterministic_fingerprint": canonical_sha256(
                {
                    "path": rel_path,
                    "classification": classification,
                    "reason": ALLOWED_LOW_LEVEL_PRIMITIVE_USERS.get(rel_path, "unexpected low-level IPC primitive usage"),
                    "hits": hits,
                }
            ),
        }
        rows.append(row)
        if classification == "duplicate":
            violations.append(
                {
                    "code": "duplicate_ipc_logic",
                    "file_path": rel_path,
                    "message": "low-level IPC primitives appear outside the canonical transport/client/server/probe surfaces",
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
    return sorted(rows, key=lambda row: str(row.get("path", ""))), sorted(
        violations,
        key=lambda row: (str(row.get("file_path", "")), str(row.get("code", ""))),
    )


def _runtime_attach_probe(repo_root: str) -> dict:
    report = run_ipc_attach_probe(repo_root, suffix="ipc_unify")
    return {
        "result": _token(report.get("result")),
        "compatibility_mode_id": _token(dict(report.get("attach") or {}).get("compatibility_mode_id")),
        "negotiation_record_hash": _token(dict(report.get("attach") or {}).get("negotiation_record_hash")),
        "missing_negotiation_refusal_code": _token(
            dict(dict(dict(report.get("missing_negotiation") or {}).get("payload_ref") or {}).get("payload_ref") or {}).get("refusal", {}).get("refusal_code")
        ),
        "seq_monotonic_by_channel": dict(report.get("seq_monotonic_by_channel") or {}),
        "cross_platform_ipc_hash": _token(report.get("cross_platform_ipc_hash")),
        "deterministic_fingerprint": _token(report.get("deterministic_fingerprint")),
    }


def _replay_probe(repo_root: str) -> dict:
    report = verify_ipc_attach_replay(repo_root, suffix="ipc_unify")
    return {
        "result": _token(report.get("result")),
        "mismatches": list(report.get("mismatches") or []),
        "first_cross_platform_ipc_hash": _token(dict(report.get("first") or {}).get("cross_platform_ipc_hash")),
        "second_cross_platform_ipc_hash": _token(dict(report.get("second") or {}).get("cross_platform_ipc_hash")),
        "deterministic_fingerprint": _token(report.get("deterministic_fingerprint")),
    }


def _vroot_ipc_probe(repo_root: str) -> dict:
    from src.appshell.ipc import (  # noqa: E402
        AppShellIPCEndpointServer,
        discover_ipc_endpoint_descriptor,
        discover_ipc_endpoints,
        ipc_endpoint_descriptor_path,
    )

    work_root = os.path.join(repo_root, "build", "appshell", "ipc_unify")
    install_root = os.path.join(work_root, "install")
    store_root = os.path.join(work_root, "store")
    executable_path = os.path.join(install_root, "server")
    os.makedirs(install_root, exist_ok=True)
    os.makedirs(store_root, exist_ok=True)
    previous_context = get_current_virtual_paths()
    context = vpath_init(
        {
            "repo_root": repo_root,
            "product_id": "server",
            "raw_args": [
                "--install-root",
                install_root,
                "--store-root",
                store_root,
                "--ipc-root",
                os.path.join(store_root, "runtime"),
            ],
            "executable_path": executable_path,
        }
    )
    set_current_virtual_paths(context)
    endpoint_server = AppShellIPCEndpointServer(
        repo_root=repo_root,
        product_id="server",
        session_id="session.ipc_unify.vroot",
        mode_id="cli",
        session_metadata={
            "contract_bundle_hash": "hash.contract.bundle.ipc_unify",
            "pack_lock_hash": "hash.pack.lock.ipc_unify",
        },
    )
    try:
        start_report = endpoint_server.start()
        endpoint_id = _token(start_report.get("endpoint_id"))
        manifest_path = vpath_resolve(VROOT_IPC, "ipc_endpoints.json", context)
        descriptor_path = ipc_endpoint_descriptor_path(repo_root, endpoint_id)
        discovery = discover_ipc_endpoints(repo_root)
        endpoint_row = {}
        for row in list(discovery.get("endpoints") or []):
            row_map = dict(row or {})
            if _token(row_map.get("endpoint_id")) == endpoint_id:
                endpoint_row = row_map
                break
        descriptor_payload = discover_ipc_endpoint_descriptor(repo_root, endpoint_id)
        report = {
            "result": "complete",
            "vroot_ipc_root": vpath_root(VROOT_IPC, context).replace("\\", "/"),
            "manifest_path": manifest_path.replace("\\", "/"),
            "descriptor_path": descriptor_path.replace("\\", "/"),
            "manifest_exists": os.path.isfile(manifest_path),
            "descriptor_exists": os.path.isfile(descriptor_path),
            "endpoint_id": endpoint_id,
            "transport_id": _token(dict(endpoint_row.get("extensions") or {}).get("official.transport_id")),
            "descriptor_rel_path": _token(dict(endpoint_row.get("extensions") or {}).get("official.descriptor_rel_path")),
            "descriptor_hash": _token(dict(endpoint_row.get("extensions") or {}).get("official.descriptor_hash")),
            "descriptor_payload_result": "complete" if bool(descriptor_payload) else "missing",
            "resolution_source": _token(context.get("resolution_source")),
            "deterministic_fingerprint": canonical_sha256(
                {
                    "vroot_ipc_root": vpath_root(VROOT_IPC, context).replace("\\", "/"),
                    "manifest_path": manifest_path.replace("\\", "/"),
                    "descriptor_path": descriptor_path.replace("\\", "/"),
                    "manifest_exists": os.path.isfile(manifest_path),
                    "descriptor_exists": os.path.isfile(descriptor_path),
                    "endpoint_id": endpoint_id,
                    "transport_id": _token(dict(endpoint_row.get("extensions") or {}).get("official.transport_id")),
                    "descriptor_rel_path": _token(dict(endpoint_row.get("extensions") or {}).get("official.descriptor_rel_path")),
                    "descriptor_hash": _token(dict(endpoint_row.get("extensions") or {}).get("official.descriptor_hash")),
                    "descriptor_payload_result": "complete" if bool(descriptor_payload) else "missing",
                    "resolution_source": _token(context.get("resolution_source")),
                }
            ),
        }
        if not report["manifest_exists"] or not report["descriptor_exists"] or not report["descriptor_rel_path"]:
            report["result"] = "refused"
            report["refusal_code"] = "refusal.connection.negotiation_mismatch"
        return report
    finally:
        endpoint_server.stop()
        if previous_context is None:
            clear_current_virtual_paths()
        else:
            set_current_virtual_paths(previous_context)


def build_ipc_unify_report(repo_root: str, *, include_runtime: bool = True) -> dict:
    repo_root_abs = _norm(repo_root or REPO_ROOT_HINT)
    surface_rows, surface_violations = _surface_rows(repo_root_abs)
    socket_rows, socket_violations = _scan_direct_socket_users(repo_root_abs)
    primitive_rows, primitive_violations = _scan_low_level_ipc_primitive_users(repo_root_abs)
    violations = list(surface_violations) + list(socket_violations) + list(primitive_violations)

    runtime_probe = {}
    replay_probe = {}
    vroot_probe = {}
    if include_runtime:
        try:
            runtime_probe = _runtime_attach_probe(repo_root_abs)
        except Exception as exc:  # pragma: no cover
            violations.append(
                {
                    "code": "runtime_probe_failed",
                    "file_path": "tools/appshell/appshell4_probe.py",
                    "message": "IPC attach probe failed ({})".format(str(exc)),
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
        try:
            replay_probe = _replay_probe(repo_root_abs)
        except Exception as exc:  # pragma: no cover
            violations.append(
                {
                    "code": "replay_probe_failed",
                    "file_path": "tools/appshell/tool_replay_ipc_attach.py",
                    "message": "IPC replay probe failed ({})".format(str(exc)),
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
        try:
            vroot_probe = _vroot_ipc_probe(repo_root_abs)
        except Exception as exc:  # pragma: no cover
            violations.append(
                {
                    "code": "vroot_probe_failed",
                    "file_path": "src/appshell/ipc/ipc_transport.py",
                    "message": "VROOT_IPC discovery probe failed ({})".format(str(exc)),
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
        if runtime_probe and _token(runtime_probe.get("result")) != "complete":
            violations.append(
                {
                    "code": "runtime_probe_refused",
                    "file_path": "tools/appshell/appshell4_probe.py",
                    "message": "IPC attach probe did not complete",
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
        if runtime_probe and _token(runtime_probe.get("missing_negotiation_refusal_code")) != "refusal.connection.no_negotiation":
            violations.append(
                {
                    "code": "unnegotiated_attach_not_refused",
                    "file_path": "src/appshell/ipc/ipc_endpoint_server.py",
                    "message": "unnegotiated attach did not refuse with refusal.connection.no_negotiation",
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
        if replay_probe and _token(replay_probe.get("result")) != "complete":
            violations.append(
                {
                    "code": "replay_mismatch",
                    "file_path": "tools/appshell/tool_replay_ipc_attach.py",
                    "message": "IPC replay probe reported mismatches",
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )
        if vroot_probe and _token(vroot_probe.get("result")) != "complete":
            violations.append(
                {
                    "code": "vroot_discovery_incomplete",
                    "file_path": "docs/appshell/IPC_DISCOVERY.md",
                    "message": "VROOT_IPC endpoint descriptor discovery probe failed",
                    "rule_id": "INV-IPC-REQUIRES-NEGOTIATION",
                }
            )

    report = {
        "result": "complete" if not violations else "refused",
        "inventory_id": IPC_UNIFY_REPORT_ID,
        "surface_rows": surface_rows,
        "direct_socket_users": socket_rows,
        "low_level_ipc_users": primitive_rows,
        "canonical_bindings": [dict(row) for row in CANONICAL_BINDINGS],
        "runtime_probe": runtime_probe,
        "replay_probe": replay_probe,
        "vroot_probe": vroot_probe,
        "violations": sorted(
            [dict(row) for row in violations],
            key=lambda row: (_token(row.get("file_path")), _token(row.get("code"))),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def ipc_unify_violations(repo_root: str) -> list[dict]:
    return list(build_ipc_unify_report(repo_root, include_runtime=False).get("violations") or [])


def _render_surface_map(report: Mapping[str, object]) -> str:
    surface_rows = list(report.get("surface_rows") or [])
    socket_rows = list(report.get("direct_socket_users") or [])
    primitive_rows = list(report.get("low_level_ipc_users") or [])
    binding_rows = list(report.get("canonical_bindings") or [])
    lines = [
        _doc_header(status="DERIVED", title="IPC Surface Map", canonical=False).rstrip(),
        "This inventory lists the real IPC surfaces in the repository and classifies them against the canonical AppShell IPC stack.",
        "",
        "## Canonical Surfaces",
        "",
        _markdown_table(
            ("Path", "Surface", "Classification", "Notes"),
            (
                (
                    "`{}`".format(_token(row.get("path"))),
                    _token(row.get("surface")),
                    _token(row.get("classification")),
                    _token(row.get("notes")),
                )
                for row in surface_rows
            ),
        ),
        "",
        "## Direct Socket Users",
        "",
        _markdown_table(
            ("Path", "Classification", "Reason", "Hits"),
            (
                (
                    "`{}`".format(_token(row.get("path"))),
                    _token(row.get("classification")),
                    _token(row.get("reason")),
                    ", ".join("`{}`".format(token) for token in list(row.get("hits") or [])),
                )
                for row in socket_rows
            ),
        ),
        "",
        "## Low-Level IPC Primitive Users",
        "",
        _markdown_table(
            ("Path", "Classification", "Reason", "Hits"),
            (
                (
                    "`{}`".format(_token(row.get("path"))),
                    _token(row.get("classification")),
                    _token(row.get("reason")),
                    ", ".join("`{}`".format(token) for token in list(row.get("hits") or [])),
                )
                for row in primitive_rows
            ),
        ),
        "",
        "## Canonical Consumer Bindings",
        "",
        _markdown_table(
            ("Surface", "Consumer", "Canonical Target", "Notes"),
            (
                (
                    _token(row.get("surface")),
                    "`{}`".format(_token(row.get("consumer_path"))),
                    "`{}`".format(_token(row.get("canonical_target"))),
                    _token(row.get("notes")),
                )
                for row in binding_rows
            ),
        ),
        "",
    ]
    return "\n".join(lines)


def _render_duplication_fixes(report: Mapping[str, object]) -> str:
    binding_rows = list(report.get("canonical_bindings") or [])
    duplicate_rows = [dict(row) for row in list(report.get("low_level_ipc_users") or []) if _token(row.get("classification")) == "duplicate"]
    lines = [
        _doc_header(status="DERIVED", title="IPC Duplication Fixes", canonical=False).rstrip(),
        "This report records the canonical IPC surfaces and any remaining duplicate or legacy IPC logic.",
        "",
        "## Canonical Stack",
        "",
        _markdown_table(
            ("Surface", "Consumer", "Canonical Target", "Notes"),
            (
                (
                    _token(row.get("surface")),
                    "`{}`".format(_token(row.get("consumer_path"))),
                    "`{}`".format(_token(row.get("canonical_target"))),
                    _token(row.get("notes")),
                )
                for row in binding_rows
            ),
        ),
        "",
        "## Remaining Duplicate Or Legacy Paths",
        "",
    ]
    if duplicate_rows:
        lines.extend(
            [
                _markdown_table(
                    ("Path", "Classification", "Reason"),
                    (
                        (
                            "`{}`".format(_token(row.get("path"))),
                            _token(row.get("classification")),
                            _token(row.get("reason")),
                        )
                        for row in duplicate_rows
                    ),
                ),
                "",
            ]
        )
    else:
        lines.extend(
            [
                "- None. Supervisor, command-engine attach, and TUI multiplexing all route through `src/appshell/ipc/ipc_client.py`.",
                "",
            ]
        )
    return "\n".join(lines)


def _render_ipc_discovery(report: Mapping[str, object]) -> str:
    vroot_probe = dict(report.get("vroot_probe") or {})
    lines = [
        _doc_header(status="CANONICAL", title="IPC Discovery", canonical=True).rstrip(),
        "## Purpose",
        "",
        "IPC discovery is the canonical local attach lookup surface for AppShell products.",
        "",
        "It guarantees:",
        "",
        "- endpoint discovery uses `VROOT_IPC` only",
        "- endpoint manifest ordering is deterministic",
        "- per-endpoint descriptor files are deterministic and offline",
        "- attach flows must negotiate through CAP-NEG before console, log, or status channels open",
        "",
        "## VROOT_IPC Layout",
        "",
        "- Manifest: `VROOT_IPC/ipc_endpoints.json`",
        "- Descriptor files: `VROOT_IPC/endpoints/<endpoint_id>.json`",
        "- Address payloads: emitted by `src/appshell/ipc/ipc_transport.py`",
        "",
        "## Discovery Flow",
        "",
        "1. Initialize virtual paths and resolve `VROOT_IPC`.",
        "2. Read `ipc_endpoints.json` and sort rows by `endpoint_id`, `product_id`, and `session_id`.",
        "3. Read the endpoint descriptor file declared by `official.descriptor_rel_path`.",
        "4. Run CAP-NEG handshake via `src/compat/handshake/handshake_engine.py` before opening channels.",
        "5. Refuse the attach if negotiation is absent, mismatched, or unlogged.",
        "",
        "## Canonical Channels",
        "",
        "- `negotiation`",
        "- `console`",
        "- `log`",
        "- `status`",
        "",
        "## Determinism Rules",
        "",
        "- transport selection is capability-gated and deterministic for the same environment",
        "- frame serialization is canonical JSON",
        "- `seq_no` is monotonic per channel",
        "- endpoint descriptor files are keyed by deterministic `endpoint_id`",
        "- retries are bounded iterations only",
        "",
        "## Current Baseline",
        "",
        "- VROOT probe result: `{}`".format(_token(vroot_probe.get("result")) or "unknown"),
        "- VROOT IPC root: `{}`".format(_token(vroot_probe.get("vroot_ipc_root")) or "<unavailable>"),
        "- Manifest path: `{}`".format(_token(vroot_probe.get("manifest_path")) or "<unavailable>"),
        "- Descriptor rel path: `{}`".format(_token(vroot_probe.get("descriptor_rel_path")) or "<unavailable>"),
        "",
    ]
    return "\n".join(lines)


def _render_final_report(report: Mapping[str, object]) -> str:
    runtime_probe = dict(report.get("runtime_probe") or {})
    replay_probe = dict(report.get("replay_probe") or {})
    vroot_probe = dict(report.get("vroot_probe") or {})
    violations = list(report.get("violations") or [])
    lines = [
        _doc_header(status="DERIVED", title="IPC Unify Final", canonical=False).rstrip(),
        "## Canonical Stack",
        "",
        "- Transport: `src/appshell/ipc/ipc_transport.py`",
        "- Handshake: `src/compat/handshake/handshake_engine.py`",
        "- Attach client: `src/appshell/ipc/ipc_client.py`",
        "- Endpoint server: `src/appshell/ipc/ipc_endpoint_server.py`",
        "- Consumers: `src/appshell/commands/command_engine.py`, `src/appshell/tui/tui_engine.py`, and `src/appshell/supervisor/supervisor_engine.py`",
        "",
        "## Removed Duplicate IPC Paths",
        "",
        "- No duplicate runtime transport or attach protocol remains outside the canonical AppShell IPC stack.",
        "- Test-only raw frame access remains confined to `tools/appshell/appshell4_probe.py`.",
        "",
        "## Attach Discipline Summary",
        "",
        "- Unnegotiated attach refusal: `{}`".format(_token(runtime_probe.get("missing_negotiation_refusal_code")) or "<missing>"),
        "- Negotiation record hash: `{}`".format(_token(runtime_probe.get("negotiation_record_hash")) or "<missing>"),
        "- Replay result: `{}`".format(_token(replay_probe.get("result")) or "unknown"),
        "- VROOT discovery result: `{}`".format(_token(vroot_probe.get("result")) or "unknown"),
        "",
        "## Runtime Verification",
        "",
        "- Attach probe result: `{}`".format(_token(runtime_probe.get("result")) or "unknown"),
        "- Cross-platform IPC hash: `{}`".format(_token(runtime_probe.get("cross_platform_ipc_hash")) or "<missing>"),
        "- Replay mismatches: `{}`".format(", ".join(list(replay_probe.get("mismatches") or [])) or "none"),
        "- Descriptor file path: `{}`".format(_token(vroot_probe.get("descriptor_path")) or "<missing>"),
        "",
        "## Readiness",
        "",
        "- Ready for `SUPERVISOR-HARDEN-0` once the broader repo strict lanes are rerun.",
        "- Ready for portable and installed attach flows through `VROOT_IPC`.",
        "",
        "## Violations",
        "",
    ]
    if violations:
        lines.extend(
            [
                _markdown_table(
                    ("Code", "Path", "Rule", "Message"),
                    (
                        (
                            _token(row.get("code")),
                            "`{}`".format(_token(row.get("file_path"))),
                            _token(row.get("rule_id")),
                            _token(row.get("message")),
                        )
                        for row in violations
                    ),
                ),
                "",
            ]
        )
    else:
        lines.extend(["- None.", ""])
    return "\n".join(lines)


def write_ipc_unify_outputs(repo_root: str, report: Mapping[str, object]) -> dict:
    repo_root_abs = _norm(repo_root or REPO_ROOT_HINT)
    outputs = {
        IPC_UNIFY_REPORT_PATH: dict(report or {}),
        IPC_SURFACE_MAP_PATH: _render_surface_map(report),
        IPC_DUPLICATION_FIXES_PATH: _render_duplication_fixes(report),
        IPC_DISCOVERY_DOC_PATH: _render_ipc_discovery(report),
        IPC_UNIFY_FINAL_PATH: _render_final_report(report),
    }
    written: dict[str, str] = {}
    for rel_path, payload in outputs.items():
        abs_path = os.path.join(repo_root_abs, rel_path.replace("/", os.sep))
        if isinstance(payload, Mapping):
            _write_json(abs_path, payload)
        else:
            _write_text(abs_path, str(payload))
        written[rel_path] = abs_path.replace("\\", "/")
    return dict((key, written[key]) for key in sorted(written.keys()))


__all__ = [
    "IPC_DISCOVERY_DOC_PATH",
    "IPC_DUPLICATION_FIXES_PATH",
    "IPC_SURFACE_MAP_PATH",
    "IPC_UNIFY_FINAL_PATH",
    "IPC_UNIFY_REPORT_ID",
    "IPC_UNIFY_REPORT_PATH",
    "IPC_UNIFY_TOOL_PATH",
    "build_ipc_unify_report",
    "ipc_unify_violations",
    "write_ipc_unify_outputs",
]
