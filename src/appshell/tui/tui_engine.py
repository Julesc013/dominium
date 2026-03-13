"""Deterministic AppShell TUI engine with curses and lite backends."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from typing import Iterable, Mapping, Sequence

from src.appshell.command_registry import build_root_command_descriptors
from src.appshell.commands import dispatch_registered_command
from src.appshell.compat_adapter import emit_descriptor_payload
from src.appshell.console_repl import build_console_session_stub
from src.appshell.ipc import attach_ipc_endpoint, query_ipc_log_events, query_ipc_status, run_ipc_console_command
from src.appshell.logging import get_current_log_engine, log_emit
from src.appshell.supervisor import SUPERVISOR_AGGREGATED_LOG_REL, load_supervisor_runtime_state
from src.client.ui.inspect_panels import build_inspection_panel_set
from src.client.ui.map_views import build_map_view_set
from src.meta_extensions_engine import normalize_extensions_tree
from src.ui import MENU_STATE_MAIN, build_ui_model


TUI_PANEL_REGISTRY_REL = os.path.join("data", "registries", "tui_panel_registry.json")
TUI_LAYOUT_REGISTRY_REL = os.path.join("data", "registries", "tui_layout_registry.json")
PRODUCT_CAPABILITY_DEFAULTS_REL = os.path.join("data", "registries", "product_capability_defaults.json")

DEFAULT_LAYOUT_BY_PRODUCT = {
    "client": "layout.viewer",
    "engine": "layout.default",
    "game": "layout.default",
    "launcher": "layout.default",
    "server": "layout.server",
    "setup": "layout.default",
    "tool.attach_console_stub": "layout.default",
}
DEFAULT_ACTIVE_PANEL_BY_PRODUCT = {
    "client": "panel.map",
    "engine": "panel.menu",
    "game": "panel.menu",
    "launcher": "panel.menu",
    "server": "panel.status",
    "setup": "panel.menu",
    "tool.attach_console_stub": "panel.menu",
}
DEFAULT_KEYBINDINGS = (
    ("F1", "help"),
    ("F2", "focus menu"),
    ("Tab", "cycle panels"),
    ("Ctrl+L", "focus logs"),
    ("Ctrl+C", "focus console"),
    ("Ctrl+S", "focus status"),
    ("Ctrl+M", "focus map"),
    ("Ctrl+I", "focus inspect"),
    (":", "command prompt"),
)
DEFAULT_HISTORY_LIMIT = 12
DEFAULT_LOG_LINE_LIMIT = 10
TUI_BACKEND_CURSES = "curses"
TUI_BACKEND_LITE = "lite"


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return normalize_extensions_tree(payload), ""


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = normalize_extensions_tree(dict(payload or {}))
    body["deterministic_fingerprint"] = ""
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _normalize_panel_row(row: Mapping[str, object]) -> dict:
    payload = normalize_extensions_tree(dict(row or {}))
    payload["schema_version"] = str(payload.get("schema_version", "")).strip() or "1.0.0"
    payload["panel_id"] = str(payload.get("panel_id", "")).strip()
    payload["title"] = str(payload.get("title", "")).strip()
    payload["required_capabilities"] = _sorted_tokens(payload.get("required_capabilities"))
    payload["extensions"] = normalize_extensions_tree(dict(payload.get("extensions") or {}))
    payload["deterministic_fingerprint"] = (
        str(payload.get("deterministic_fingerprint", "")).strip() or _fingerprint(payload)
    )
    return payload


def _normalize_layout_row(row: Mapping[str, object]) -> dict:
    payload = normalize_extensions_tree(dict(row or {}))
    payload["schema_version"] = str(payload.get("schema_version", "")).strip() or "1.0.0"
    payload["layout_id"] = str(payload.get("layout_id", "")).strip()
    panels = []
    for item in _as_list(payload.get("panels")):
        if not isinstance(item, Mapping):
            continue
        row_map = normalize_extensions_tree(dict(item))
        panels.append(
            {
                "panel_id": str(row_map.get("panel_id", "")).strip(),
                "slot_id": str(row_map.get("slot_id", "")).strip(),
                "order": int(row_map.get("order", 0) or 0),
                "extensions": normalize_extensions_tree(dict(row_map.get("extensions") or {})),
            }
        )
    payload["panels"] = sorted(panels, key=lambda item: (int(item.get("order", 0)), str(item.get("panel_id", ""))))
    payload["extensions"] = normalize_extensions_tree(dict(payload.get("extensions") or {}))
    payload["deterministic_fingerprint"] = (
        str(payload.get("deterministic_fingerprint", "")).strip() or _fingerprint(payload)
    )
    return payload


def load_tui_panel_registry(repo_root: str) -> tuple[dict, str]:
    payload, error = _read_json(os.path.join(repo_root, TUI_PANEL_REGISTRY_REL))
    if error:
        return {}, error
    record = dict(payload.get("record") or {})
    record["panels"] = sorted(
        [_normalize_panel_row(row) for row in _as_list(record.get("panels")) if isinstance(row, Mapping)],
        key=lambda row: str(row.get("panel_id", "")),
    )
    return {
        "schema_id": str(payload.get("schema_id", "")).strip(),
        "schema_version": str(payload.get("schema_version", "")).strip(),
        "record": record,
    }, ""


def load_tui_layout_registry(repo_root: str) -> tuple[dict, str]:
    payload, error = _read_json(os.path.join(repo_root, TUI_LAYOUT_REGISTRY_REL))
    if error:
        return {}, error
    record = dict(payload.get("record") or {})
    record["layouts"] = sorted(
        [_normalize_layout_row(row) for row in _as_list(record.get("layouts")) if isinstance(row, Mapping)],
        key=lambda row: str(row.get("layout_id", "")),
    )
    return {
        "schema_id": str(payload.get("schema_id", "")).strip(),
        "schema_version": str(payload.get("schema_version", "")).strip(),
        "record": record,
    }, ""


def _panel_rows_by_id(repo_root: str) -> dict[str, dict]:
    payload, _error = load_tui_panel_registry(repo_root)
    out = {}
    for row in _as_list(_as_map(payload.get("record")).get("panels")):
        row_map = dict(row)
        panel_id = str(row_map.get("panel_id", "")).strip()
        if panel_id:
            out[panel_id] = row_map
    return dict((key, out[key]) for key in sorted(out.keys()))


def _layout_rows_by_id(repo_root: str) -> dict[str, dict]:
    payload, _error = load_tui_layout_registry(repo_root)
    out = {}
    for row in _as_list(_as_map(payload.get("record")).get("layouts")):
        row_map = dict(row)
        layout_id = str(row_map.get("layout_id", "")).strip()
        if layout_id:
            out[layout_id] = row_map
    return dict((key, out[key]) for key in sorted(out.keys()))


def _product_capability_ids(repo_root: str, product_id: str) -> list[str]:
    payload, error = _read_json(os.path.join(repo_root, PRODUCT_CAPABILITY_DEFAULTS_REL))
    if error:
        return []
    for row in _as_list(_as_map(payload.get("record")).get("defaults")):
        row_map = _as_map(row)
        if str(row_map.get("product_id", "")).strip() == str(product_id).strip():
            return _sorted_tokens(row_map.get("feature_capabilities"))
    return []


def _resolve_layout_id(repo_root: str, product_id: str, requested_layout_id: str) -> str:
    rows = _layout_rows_by_id(repo_root)
    requested = str(requested_layout_id or "").strip()
    if requested and requested in rows:
        return requested
    return str(DEFAULT_LAYOUT_BY_PRODUCT.get(str(product_id).strip(), "layout.default")).strip()


def _build_console_sessions(repo_root: str, product_id: str, sessions: Sequence[Mapping[str, object]] | None) -> list[dict]:
    command_rows = build_root_command_descriptors(repo_root, str(product_id).strip())
    default_dispatch = build_console_session_stub(str(product_id).strip(), command_rows)
    out = []
    for index, row in enumerate(list(sessions or []), start=1):
        if not isinstance(row, Mapping):
            continue
        row_map = normalize_extensions_tree(dict(row))
        out.append(
            {
                "session_id": str(row_map.get("session_id", "")).strip() or "console.{:04d}".format(index),
                "title": str(row_map.get("title", "")).strip() or "Session {}".format(index),
                "history": list(_as_list(row_map.get("history"))[-DEFAULT_HISTORY_LIMIT:]),
                "last_dispatch": _as_map(row_map.get("last_dispatch")) or dict(default_dispatch),
                "extensions": normalize_extensions_tree(dict(row_map.get("extensions") or {})),
            }
        )
    if out:
        return sorted(out, key=lambda row: str(row.get("session_id", "")))
    return [
        {
            "session_id": "console.0001",
            "title": "Local",
            "history": [],
            "last_dispatch": dict(default_dispatch),
            "extensions": {"official.source": "APPSHELL-3"},
        }
    ]


def _backend_state(backend_override: str = "") -> dict:
    override = str(backend_override or "").strip().lower()
    backend_id = override if override in {TUI_BACKEND_CURSES, TUI_BACKEND_LITE} else TUI_BACKEND_LITE
    if not override:
        try:
            importlib.import_module("curses")
            if sys.stdin.isatty() and sys.stdout.isatty():
                backend_id = TUI_BACKEND_CURSES
        except Exception:
            backend_id = TUI_BACKEND_LITE
    if backend_id == TUI_BACKEND_CURSES:
        return {
            "backend_id": TUI_BACKEND_CURSES,
            "compatibility_mode_id": "compat.full",
            "effective_ui_mode": "tui",
            "disabled_capabilities": [],
            "substituted_capabilities": [],
            "explain_keys": [],
        }
    return {
        "backend_id": TUI_BACKEND_LITE,
        "compatibility_mode_id": "compat.degraded",
        "effective_ui_mode": "cli",
        "disabled_capabilities": [
            {
                "capability_id": "cap.ui.tui",
                "owner_product_id": "local.shell",
                "reason_code": "compat.local.tui_backend_missing",
                "user_message_key": "explain.compat_degraded.ui_tui",
            }
        ],
        "substituted_capabilities": [
            {
                "capability_id": "cap.ui.tui",
                "substitute_capability_id": "cap.ui.cli",
                "owner_product_id": "local.shell",
                "user_message_key": "explain.compat_degraded.ui_tui",
            }
        ],
        "explain_keys": ["explain.compat_degraded", "explain.feature_disabled"],
    }


def _status_lines(repo_root: str, product_id: str, layout_id: str, backend_state: Mapping[str, object]) -> list[str]:
    descriptor_payload = emit_descriptor_payload(repo_root, product_id=str(product_id).strip(), descriptor_file="")
    descriptor = _as_map(descriptor_payload.get("descriptor"))
    extensions = _as_map(descriptor.get("extensions"))
    logger = get_current_log_engine()
    ticks = [int(event.get("tick")) for event in list(logger.ring_events() if logger is not None else []) if event.get("tick") is not None]
    lines = [
        "product_id: {}".format(str(product_id).strip()),
        "product_version: {}".format(str(descriptor.get("product_version", "")).strip()),
        "build_id: {}".format(str(extensions.get("official.build_id", "")).strip()),
        "layout_id: {}".format(str(layout_id).strip()),
        "backend_id: {}".format(str(backend_state.get("backend_id", "")).strip()),
        "compatibility_mode: {}".format(str(backend_state.get("compatibility_mode_id", "")).strip()),
        "effective_ui_mode: {}".format(str(backend_state.get("effective_ui_mode", "")).strip()),
        "pack_verification_status: not_run",
        "session_tick: {}".format(max(ticks, default=0)),
        "log_event_count: {}".format(int(len(list(logger.ring_events() if logger is not None else [])))),
    ]
    if str(product_id).strip() == "launcher":
        supervisor_state = _as_map(load_supervisor_runtime_state(repo_root))
        process_rows = sorted(
            [dict(row) for row in _as_list(supervisor_state.get("processes")) if isinstance(row, Mapping)],
            key=lambda row: (str(row.get("product_id", "")), str(row.get("pid_stub", ""))),
        )
        service_row = _as_map(supervisor_state.get("service"))
        lines.append("supervisor_run_id: {}".format(str(supervisor_state.get("run_id", "")).strip() or "idle"))
        lines.append("supervisor_service: {}".format(str(service_row.get("status", "")).strip() or "inactive"))
        lines.append("supervisor_process_count: {}".format(int(len(process_rows))))
        for row in process_rows[:4]:
            lines.append(
                "  {}: {} attach={} exit={}".format(
                    str(row.get("product_id", "")).strip(),
                    str(row.get("status", "")).strip(),
                    str(row.get("attach_status", "")).strip(),
                    row.get("exit_code"),
                )
            )
    return lines


def _console_lines(session_rows: Sequence[Mapping[str, object]], active_session_id: str) -> list[str]:
    tabs = []
    active = {}
    for row in list(session_rows or []):
        row_map = _as_map(row)
        session_id = str(row_map.get("session_id", "")).strip()
        tabs.append("[{}{}]".format(str(row_map.get("title", "")).strip() or session_id, "*" if session_id == active_session_id else ""))
        if session_id == active_session_id:
            active = row_map
    lines = ["sessions: {}".format(" ".join(tabs).strip() or "<none>")]
    history = list(_as_list(active.get("history"))[-5:])
    if history:
        lines.append("history:")
        for row in history:
            row_map = _as_map(row)
            lines.append("  {} -> {}".format(str(row_map.get("command_text", "")).strip(), int(row_map.get("exit_code", 0) or 0)))
    dispatch = _as_map(active.get("last_dispatch"))
    if str(dispatch.get("dispatch_kind", "")).strip() == "text":
        lines.append("last_output:")
        for line in str(dispatch.get("text", "")).replace("\r\n", "\n").splitlines()[:6]:
            lines.append("  {}".format(line.rstrip()))
    else:
        payload = _as_map(dispatch.get("payload"))
        lines.append("last_output:")
        lines.append("  result: {}".format(str(payload.get("result", "")).strip() or "complete"))
        welcome_message = str(payload.get("welcome_message", "")).strip()
        prompt = str(payload.get("prompt", "")).strip()
        if welcome_message:
            lines.append("  note: {}".format(welcome_message))
        if prompt:
            lines.append("  prompt: {}".format(prompt))
        examples = [str(item).strip() for item in _as_list(payload.get("examples")) if str(item).strip()]
        if examples:
            lines.append("  try: {}".format(" | ".join(examples[:3])))
        for key in ("refusal_code", "reason", "compatibility_mode_id", "descriptor_hash"):
            value = payload.get(key)
            if value not in (None, "", []):
                lines.append("  {}: {}".format(key, value))
    return lines


def _help_lines(product_id: str) -> list[str]:
    lines = [
        "F1 Help",
        "  Tab cycles panels.",
        "  F2 focuses the main menu.",
        "  Ctrl+L shows logs, Ctrl+C shows console, Ctrl+S shows status.",
        "  : opens the command prompt, q exits the TUI shell.",
    ]
    if str(product_id).strip() == "client":
        lines.extend(
            [
                "  Ctrl+M focuses the map, Ctrl+I focuses inspect.",
                "  Start Session launches the selected seed and instance.",
            ]
        )
    return lines


def _logs_lines(log_category_filter: str) -> list[str]:
    logger = get_current_log_engine()
    category_filter = str(log_category_filter or "").strip()
    rows = []
    for event in sorted(list(logger.ring_events() if logger is not None else []), key=lambda row: str(_as_map(row).get("event_id", ""))):
        event_map = _as_map(event)
        if category_filter and str(event_map.get("category", "")).strip() != category_filter:
            continue
        rows.append(
            "{event_id} [{severity}/{category}] {message_key}".format(
                event_id=str(event_map.get("event_id", "")).strip(),
                severity=str(event_map.get("severity", "")).strip(),
                category=str(event_map.get("category", "")).strip(),
                message_key=str(event_map.get("message_key", "")).strip(),
            )
        )
    return list(rows[-DEFAULT_LOG_LINE_LIMIT:]) or ["no log events"]


def _remote_log_lines(console_sessions: Sequence[Mapping[str, object]]) -> list[str]:
    rows = []
    for session in list(console_sessions or []):
        ext = _as_map(_as_map(session).get("extensions"))
        remote_events = list(ext.get("official.remote_log_events") or [])
        session_id = str(_as_map(session).get("session_id", "")).strip()
        for event in remote_events:
            event_map = _as_map(event)
            rows.append(
                "{event_id} [remote:{session_id}/{severity}/{category}] {message_key}".format(
                    event_id=str(event_map.get("event_id", "")).strip(),
                    session_id=session_id,
                    severity=str(event_map.get("severity", "")).strip(),
                    category=str(event_map.get("category", "")).strip(),
                    message_key=str(event_map.get("message_key", "")).strip(),
                )
            )
    return sorted(rows)[-DEFAULT_LOG_LINE_LIMIT:]


def _supervisor_aggregated_log_lines(repo_root: str, product_id: str) -> list[str]:
    if str(product_id).strip() != "launcher":
        return []
    abs_path = os.path.normpath(os.path.join(repo_root, SUPERVISOR_AGGREGATED_LOG_REL.replace("/", os.sep)))
    if not os.path.isfile(abs_path):
        return []
    rows = []
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                token = str(raw_line or "").strip()
                if not token:
                    continue
                try:
                    payload = json.loads(token)
                except ValueError:
                    continue
                if isinstance(payload, Mapping):
                    rows.append(dict(payload))
    except OSError:
        return []
    out = []
    for row in rows[-DEFAULT_LOG_LINE_LIMIT:]:
        row_map = _as_map(row)
        out.append(
            "{event_id} [supervisor:{product}/{severity}/{category}] {message_key}".format(
                event_id=str(row_map.get("event_id", "")).strip(),
                product=str(row_map.get("source_product_id", "")).strip(),
                severity=str(row_map.get("severity", "")).strip(),
                category=str(row_map.get("category", "")).strip(),
                message_key=str(row_map.get("message_key", "")).strip(),
            )
        )
    return out


def _map_lines(product_id: str) -> list[str]:
    if str(product_id).strip() != "client":
        return ["map panel unavailable for this product"]
    view_set = build_map_view_set(perceived_model={}, ui_mode="tui")
    ascii_lines = list(_as_map(_as_map(_as_map(view_set.get("map_view")).get("display")).get("ascii")).get("ascii_lines") or [])
    return [str(line) for line in ascii_lines[:12]] or ["map view unavailable"]


def _inspect_lines(product_id: str) -> list[str]:
    if str(product_id).strip() != "client":
        return ["inspect panel unavailable for this product"]
    inspection = build_inspection_panel_set(perceived_model={}, target_semantic_id="")
    panels = sorted([dict(row) for row in _as_list(inspection.get("panels")) if isinstance(row, Mapping)], key=lambda row: str(row.get("panel_id", "")))
    if not panels:
        return ["inspect view unavailable"]
    lines = []
    for panel in panels[:3]:
        lines.append("{}: {}".format(str(panel.get("panel_title", "")).strip(), str(panel.get("summary", "")).strip()))
        for row in list(_as_list(panel.get("rows"))[:3]):
            row_map = _as_map(row)
            lines.append("  {}: {}".format(str(row_map.get("key", "")).strip(), row_map.get("value")))
    return lines or ["inspect view unavailable"]


def _menu_lines(repo_root: str, product_id: str) -> list[str]:
    ui_model = build_ui_model(repo_root=repo_root, product_id=str(product_id).strip(), current_state_id=MENU_STATE_MAIN)
    current_state = _as_map(ui_model.get("current_state"))
    inventory = _as_map(ui_model.get("inventory"))
    lines = [
        "state: {}".format(str(current_state.get("title", "")).strip() or MENU_STATE_MAIN),
        "summary: {}".format(str(current_state.get("summary", "")).strip() or "menu unavailable"),
        "instances={} saves={} bundles={} commands={}".format(
            int(inventory.get("instance_count", 0) or 0),
            int(inventory.get("save_count", 0) or 0),
            int(inventory.get("bundle_count", 0) or 0),
            int(inventory.get("command_descriptor_count", 0) or 0),
        ),
    ]
    entries = [dict(row) for row in _as_list(current_state.get("entries")) if isinstance(row, Mapping)]
    if entries:
        lines.append("entries:")
        for row in entries[:4]:
            row_map = _as_map(row)
            label = str(row_map.get("label", "")).strip() or str(row_map.get("item_id", "")).strip()
            lines.append("  - {}".format(label))
    actions = [dict(row) for row in _as_list(current_state.get("actions")) if isinstance(row, Mapping)]
    if actions:
        lines.append("actions:")
        for row in actions[:6]:
            row_map = _as_map(row)
            label = str(row_map.get("label", "")).strip() or str(row_map.get("action_id", "")).strip()
            command_tokens = [str(token).strip() for token in _as_list(row_map.get("command_tokens")) if str(token).strip()]
            suffix = " -> {}".format(" ".join(command_tokens)) if command_tokens else ""
            lines.append("  - {}{}".format(label, suffix))
    return lines


def _panel_lines(
    panel_id: str,
    *,
    product_id: str,
    repo_root: str,
    layout_id: str,
    backend_state: Mapping[str, object],
    console_sessions: Sequence[Mapping[str, object]],
    active_session_id: str,
    log_category_filter: str,
    remote_log_lines: Sequence[str] | None = None,
) -> list[str]:
    if panel_id == "panel.menu":
        return _menu_lines(repo_root, product_id)
    if panel_id == "panel.console":
        return _console_lines(console_sessions, active_session_id)
    if panel_id == "panel.logs":
        combined = _logs_lines(log_category_filter) + list(remote_log_lines or []) + _supervisor_aggregated_log_lines(repo_root, product_id)
        return list(combined[-DEFAULT_LOG_LINE_LIMIT:]) or ["no log events"]
    if panel_id == "panel.status":
        return _status_lines(repo_root, product_id, layout_id, backend_state)
    if panel_id == "panel.map":
        return _map_lines(product_id)
    if panel_id == "panel.inspect":
        return _inspect_lines(product_id)
    return ["panel unavailable"]


def build_tui_surface(
    repo_root: str,
    *,
    product_id: str,
    requested_layout_id: str = "",
    active_panel_id: str = "",
    console_sessions: Sequence[Mapping[str, object]] | None = None,
    active_session_id: str = "",
    log_category_filter: str = "",
    backend_override: str = "",
) -> dict:
    layout_id = _resolve_layout_id(repo_root, str(product_id).strip(), requested_layout_id)
    layout_row = dict(_layout_rows_by_id(repo_root).get(layout_id) or {})
    panel_rows_by_id = _panel_rows_by_id(repo_root)
    capability_ids = set(_product_capability_ids(repo_root, str(product_id).strip()))
    backend_state = _backend_state(backend_override=backend_override)
    session_rows = _build_console_sessions(repo_root, str(product_id).strip(), console_sessions)
    active_session = str(active_session_id or "").strip() or str(session_rows[0].get("session_id", "")).strip()
    remote_lines = _remote_log_lines(session_rows)
    help_lines = _help_lines(str(product_id).strip())

    rendered_panels = []
    for row in list(layout_row.get("panels") or []):
        panel_id = str(_as_map(row).get("panel_id", "")).strip()
        panel_row = dict(panel_rows_by_id.get(panel_id) or {})
        required_capabilities = _sorted_tokens(panel_row.get("required_capabilities"))
        missing = [token for token in required_capabilities if token not in capability_ids]
        rendered_panels.append(
            {
                "panel_id": panel_id,
                "title": str(panel_row.get("title", "")).strip() or panel_id,
                "required_capabilities": list(required_capabilities),
                "slot_id": str(_as_map(row).get("slot_id", "")).strip(),
                "order": int(_as_map(row).get("order", 0) or 0),
                "enabled": not missing,
                "lines": (
                    _panel_lines(
                        panel_id,
                        product_id=str(product_id).strip(),
                        repo_root=repo_root,
                        layout_id=layout_id,
                        backend_state=backend_state,
                        console_sessions=session_rows,
                        active_session_id=active_session,
                        log_category_filter=log_category_filter,
                        remote_log_lines=remote_lines,
                    )
                    if not missing
                    else ["disabled: missing {}".format(", ".join(missing))]
                ),
                "extensions": {
                    "panel_kind": str(_as_map(panel_row.get("extensions")).get("panel_kind", "")).strip(),
                    "focus_key": str(_as_map(panel_row.get("extensions")).get("focus_key", "")).strip(),
                },
            }
        )
    rendered_panels = sorted(rendered_panels, key=lambda row: (int(row.get("order", 0) or 0), str(row.get("panel_id", ""))))
    active = str(active_panel_id or "").strip() or str(DEFAULT_ACTIVE_PANEL_BY_PRODUCT.get(str(product_id).strip(), "")).strip()
    panel_order = [str(row.get("panel_id", "")).strip() for row in rendered_panels if str(row.get("panel_id", "")).strip()]
    if active not in panel_order:
        active = panel_order[0] if panel_order else ""

    payload = {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "requested_mode_id": "tui",
        "effective_mode_id": str(backend_state.get("effective_ui_mode", "")).strip() or "tui",
        "backend_id": str(backend_state.get("backend_id", "")).strip() or TUI_BACKEND_LITE,
        "requested_layout_id": str(requested_layout_id or "").strip(),
        "effective_layout_id": layout_id,
        "active_panel_id": active,
        "console_sessions": list(session_rows),
        "active_session_id": active_session,
        "keybindings": [{"key": key, "action": action} for key, action in DEFAULT_KEYBINDINGS],
        "show_help": True,
        "help_lines": help_lines,
        "panels": rendered_panels,
        "panel_order": list(panel_order),
        "compatibility_mode_id": str(backend_state.get("compatibility_mode_id", "")).strip() or "compat.full",
        "disabled_capabilities": list(backend_state.get("disabled_capabilities") or []),
        "substituted_capabilities": list(backend_state.get("substituted_capabilities") or []),
        "explain_keys": list(_sorted_tokens(backend_state.get("explain_keys"))),
        "status_summary": {
            "pack_verification_status": "not_run",
            "session_status": "detached",
            "menu_available": True,
            "map_available": bool(str(product_id).strip() == "client"),
            "inspect_available": bool(str(product_id).strip() == "client"),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def render_tui_text(surface_payload: Mapping[str, object]) -> str:
    payload = normalize_extensions_tree(dict(surface_payload or {}))
    lines = [
        "Dominium TUI",
        "product_id: {}".format(str(payload.get("product_id", "")).strip()),
        "backend_id: {}".format(str(payload.get("backend_id", "")).strip()),
        "effective_mode_id: {}".format(str(payload.get("effective_mode_id", "")).strip()),
        "layout_id: {}".format(str(payload.get("effective_layout_id", "")).strip()),
        "active_panel_id: {}".format(str(payload.get("active_panel_id", "")).strip()),
    ]
    if list(payload.get("explain_keys") or []):
        lines.append("explain_keys: {}".format(", ".join(_sorted_tokens(payload.get("explain_keys")))))
    key_rows = ["{}={}".format(str(row.get("key", "")).strip(), str(row.get("action", "")).strip()) for row in _as_list(payload.get("keybindings"))]
    if key_rows:
        lines.append("keybindings: {}".format(" | ".join(key_rows)))
    if bool(payload.get("show_help")):
        lines.append("")
        for row in _as_list(payload.get("help_lines")):
            lines.append(str(row))
    lines.append("")
    for panel in sorted([dict(row) for row in _as_list(payload.get("panels")) if isinstance(row, Mapping)], key=lambda row: (int(row.get("order", 0) or 0), str(row.get("panel_id", "")))):
        marker = "*" if str(panel.get("panel_id", "")).strip() == str(payload.get("active_panel_id", "")).strip() else " "
        lines.append("[{}] {} {}".format(marker, str(panel.get("title", "")).strip(), str(panel.get("panel_id", "")).strip()))
        for row in list(_as_list(panel.get("lines"))[:14]):
            lines.append("  {}".format(str(row)))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _focus_panel(surface_payload: Mapping[str, object], panel_id: str) -> dict:
    payload = dict(surface_payload or {})
    panel_order = [str(item).strip() for item in _as_list(payload.get("panel_order")) if str(item).strip()]
    if str(panel_id).strip() in panel_order:
        payload["active_panel_id"] = str(panel_id).strip()
    return payload


def _cycle_panel(surface_payload: Mapping[str, object]) -> dict:
    payload = dict(surface_payload or {})
    panel_order = [str(item).strip() for item in _as_list(payload.get("panel_order")) if str(item).strip()]
    if not panel_order:
        return payload
    active = str(payload.get("active_panel_id", "")).strip()
    if active not in panel_order:
        payload["active_panel_id"] = panel_order[0]
        return payload
    payload["active_panel_id"] = panel_order[(panel_order.index(active) + 1) % len(panel_order)]
    return payload


def execute_console_session_command(
    repo_root: str,
    *,
    product_id: str,
    mode_id: str,
    surface_payload: Mapping[str, object],
    command_text: str,
) -> dict:
    surface = normalize_extensions_tree(dict(surface_payload or {}))
    text = str(command_text or "").strip()
    if not text:
        return {
            "result": "refused",
            "reason_code": "refusal.io.invalid_args",
            "message": "console command text is required",
            "surface": dict(surface),
        }
    sessions = _build_console_sessions(repo_root, str(product_id).strip(), _as_list(surface.get("console_sessions")))
    active_session = str(surface.get("active_session_id", "")).strip() or str(sessions[0].get("session_id", "")).strip()
    active_row = {}
    for row in sessions:
        row_map = dict(row)
        if str(row_map.get("session_id", "")).strip() == active_session:
            active_row = row_map
            break
    extensions = _as_map(active_row.get("extensions"))
    attach_record = _as_map(extensions.get("official.attach_record"))
    if str(extensions.get("official.remote_endpoint_id", "")).strip():
        remote_dispatch = run_ipc_console_command(repo_root, attach_record, text)
        dispatch = {
            "dispatch_kind": "text",
            "text": str(remote_dispatch.get("stdout", "")).strip() or str(remote_dispatch.get("stderr", "")).strip(),
            "payload": dict(remote_dispatch),
            "exit_code": int(_as_map(remote_dispatch.get("dispatch")).get("exit_code", 0) or 0),
        }
        refreshed_status = query_ipc_status(repo_root, attach_record)
        refreshed_logs = query_ipc_log_events(
            repo_root,
            attach_record,
            after_event_id=str(extensions.get("official.remote_last_event_id", "")).strip(),
            limit=8,
        )
    else:
        dispatch = dispatch_registered_command(
            repo_root,
            product_id=str(product_id).strip(),
            mode_id=str(mode_id).strip() or "tui",
            command_tokens=text.split(),
        )
        refreshed_status = {}
        refreshed_logs = {}
    updated = []
    for row in sessions:
        row_map = dict(row)
        if str(row_map.get("session_id", "")).strip() != active_session:
            updated.append(row_map)
            continue
        history = list(_as_list(row_map.get("history")))
        history.append(
            {
                "command_text": text,
                "dispatch_kind": str(dispatch.get("dispatch_kind", "")).strip(),
                "exit_code": int(dispatch.get("exit_code", 0) or 0),
            }
        )
        row_map["history"] = history[-DEFAULT_HISTORY_LIMIT:]
        row_map["last_dispatch"] = normalize_extensions_tree(dict(dispatch))
        if refreshed_status:
            ext = dict(_as_map(row_map.get("extensions")))
            ext["official.remote_status"] = dict(refreshed_status.get("status") or {})
            ext["official.remote_log_events"] = list(refreshed_logs.get("events") or [])
            if list(refreshed_logs.get("events") or []):
                ext["official.remote_last_event_id"] = str(dict(list(refreshed_logs.get("events") or [])[-1]).get("event_id", "")).strip()
            row_map["extensions"] = ext
        updated.append(row_map)
    log_emit(
        category="ui",
        severity="info",
        message_key="appshell.tui.command.executed",
        params={
            "product_id": str(product_id).strip(),
            "session_id": active_session,
            "command_text": text,
            "exit_code": int(dispatch.get("exit_code", 0) or 0),
        },
    )
    rebuilt = build_tui_surface(
        repo_root,
        product_id=str(product_id).strip(),
        requested_layout_id=str(surface.get("effective_layout_id", "")).strip() or str(surface.get("requested_layout_id", "")).strip(),
        active_panel_id="panel.console",
        console_sessions=updated,
        active_session_id=active_session,
        backend_override=str(surface.get("backend_id", "")).strip() or TUI_BACKEND_LITE,
    )
    return {"result": "complete", "dispatch": normalize_extensions_tree(dict(dispatch)), "surface": rebuilt, "session_id": active_session}


def attach_ipc_session_to_surface(
    repo_root: str,
    *,
    product_id: str,
    surface_payload: Mapping[str, object],
    endpoint_id: str,
) -> dict:
    surface = normalize_extensions_tree(dict(surface_payload or {}))
    attach = attach_ipc_endpoint(repo_root, local_product_id=str(product_id).strip(), endpoint_id=str(endpoint_id).strip())
    if str(attach.get("result", "")).strip() != "complete":
        return {"result": "refused", "attach": attach, "surface": dict(surface)}
    status = query_ipc_status(repo_root, attach)
    logs = query_ipc_log_events(repo_root, attach, limit=8)
    sessions = _build_console_sessions(repo_root, str(product_id).strip(), _as_list(surface.get("console_sessions")))
    remote_session_id = "ipc.{}".format(str(endpoint_id).strip())
    sessions = [row for row in sessions if str(dict(row).get("session_id", "")).strip() != remote_session_id]
    sessions.append(
        {
            "session_id": remote_session_id,
            "title": "{} [{}]".format(str(dict(attach.get("endpoint") or {}).get("product_id", "")).strip(), str(endpoint_id).strip()),
            "history": [],
            "last_dispatch": {
                "dispatch_kind": "json",
                "payload": {"result": "complete", "attach": attach, "status": dict(status.get("status") or {})},
                "exit_code": 0,
            },
            "extensions": {
                "official.remote_endpoint_id": str(endpoint_id).strip(),
                "official.attach_record": dict(attach),
                "official.remote_status": dict(status.get("status") or {}),
                "official.remote_log_events": list(logs.get("events") or []),
                "official.remote_last_event_id": str(dict(list(logs.get("events") or [])[-1]).get("event_id", "")).strip() if list(logs.get("events") or []) else "",
                "official.compatibility_mode_id": str(attach.get("compatibility_mode_id", "")).strip(),
            },
        }
    )
    rebuilt = build_tui_surface(
        repo_root,
        product_id=str(product_id).strip(),
        requested_layout_id=str(surface.get("effective_layout_id", "")).strip() or str(surface.get("requested_layout_id", "")).strip(),
        active_panel_id="panel.console",
        console_sessions=sessions,
        active_session_id=remote_session_id,
        backend_override=str(surface.get("backend_id", "")).strip() or TUI_BACKEND_LITE,
    )
    return {"result": "complete", "attach": attach, "surface": rebuilt}


def detach_ipc_session_from_surface(
    repo_root: str,
    *,
    product_id: str,
    surface_payload: Mapping[str, object],
    session_id: str,
) -> dict:
    surface = normalize_extensions_tree(dict(surface_payload or {}))
    sessions = [
        dict(row)
        for row in _as_list(surface.get("console_sessions"))
        if str(dict(row).get("session_id", "")).strip() != str(session_id).strip()
    ]
    rebuilt = build_tui_surface(
        repo_root,
        product_id=str(product_id).strip(),
        requested_layout_id=str(surface.get("effective_layout_id", "")).strip() or str(surface.get("requested_layout_id", "")).strip(),
        console_sessions=sessions or None,
        active_session_id="",
        backend_override=str(surface.get("backend_id", "")).strip() or TUI_BACKEND_LITE,
    )
    return {"result": "complete", "surface": rebuilt}


def refresh_ipc_sessions_in_surface(
    repo_root: str,
    *,
    product_id: str,
    surface_payload: Mapping[str, object],
) -> dict:
    surface = normalize_extensions_tree(dict(surface_payload or {}))
    refreshed_sessions = []
    for row in _as_list(surface.get("console_sessions")):
        row_map = dict(row)
        ext = _as_map(row_map.get("extensions"))
        attach_record = _as_map(ext.get("official.attach_record"))
        if not str(ext.get("official.remote_endpoint_id", "")).strip():
            refreshed_sessions.append(row_map)
            continue
        status = query_ipc_status(repo_root, attach_record)
        logs = query_ipc_log_events(
            repo_root,
            attach_record,
            after_event_id=str(ext.get("official.remote_last_event_id", "")).strip(),
            limit=8,
        )
        ext["official.remote_status"] = dict(status.get("status") or {})
        ext["official.remote_log_events"] = list(logs.get("events") or [])
        if list(logs.get("events") or []):
            ext["official.remote_last_event_id"] = str(dict(list(logs.get("events") or [])[-1]).get("event_id", "")).strip()
        row_map["extensions"] = ext
        refreshed_sessions.append(row_map)
    rebuilt = build_tui_surface(
        repo_root,
        product_id=str(product_id).strip(),
        requested_layout_id=str(surface.get("effective_layout_id", "")).strip() or str(surface.get("requested_layout_id", "")).strip(),
        console_sessions=refreshed_sessions,
        active_session_id=str(surface.get("active_session_id", "")).strip(),
        backend_override=str(surface.get("backend_id", "")).strip() or TUI_BACKEND_LITE,
    )
    return {"result": "complete", "surface": rebuilt}


def _run_curses_loop(surface_payload: Mapping[str, object]) -> None:
    curses = importlib.import_module("curses")

    def _render(stdscr, payload: Mapping[str, object]) -> None:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        for index, line in enumerate(render_tui_text(payload).replace("\r\n", "\n").splitlines()[: max(1, height - 1)]):
            stdscr.addnstr(index, 0, str(line), max(1, width - 1))
        stdscr.refresh()

    def _loop(stdscr) -> None:
        payload = dict(surface_payload or {})
        focus_keys = {
            12: "panel.logs",
            3: "panel.console",
            19: "panel.status",
            13: "panel.map",
            9: None,
        }
        curses.curs_set(0)
        stdscr.keypad(True)
        _render(stdscr, payload)
        while True:
            key = stdscr.getch()
            if key in (27, ord("q"), ord("Q")):
                return
            if key == curses.KEY_F1:
                payload["show_help"] = not bool(payload.get("show_help"))
            elif key == curses.KEY_F2:
                payload = _focus_panel(payload, "panel.menu")
            elif key == 9:
                payload = _cycle_panel(payload)
            elif key in focus_keys and focus_keys[key] is not None:
                payload = _focus_panel(payload, str(focus_keys[key]))
            _render(stdscr, payload)

    curses.wrapper(_loop)


def run_tui_mode(
    repo_root: str,
    *,
    product_id: str,
    requested_layout_id: str = "",
) -> dict:
    surface = build_tui_surface(repo_root, product_id=str(product_id).strip(), requested_layout_id=str(requested_layout_id).strip())
    log_emit(
        category="ui",
        severity="info",
        message_key="appshell.tui.surface.ready",
        params={
            "product_id": str(product_id).strip(),
            "layout_id": str(surface.get("effective_layout_id", "")).strip(),
            "backend_id": str(surface.get("backend_id", "")).strip(),
            "compatibility_mode_id": str(surface.get("compatibility_mode_id", "")).strip(),
        },
    )
    if str(surface.get("backend_id", "")).strip() == TUI_BACKEND_LITE:
        log_emit(
            category="ui",
            severity="warn",
            message_key="appshell.tui.backend_degraded",
            params={
                "product_id": str(product_id).strip(),
                "requested_mode_id": "tui",
                "effective_mode_id": str(surface.get("effective_mode_id", "")).strip(),
            },
        )
        return {"dispatch_kind": "text", "text": render_tui_text(surface), "payload": surface, "exit_code": 0}
    try:
        _run_curses_loop(surface)
    except Exception:
        degraded = build_tui_surface(
            repo_root,
            product_id=str(product_id).strip(),
            requested_layout_id=str(requested_layout_id).strip(),
            backend_override=TUI_BACKEND_LITE,
        )
        log_emit(
            category="ui",
            severity="warn",
            message_key="appshell.tui.backend_degraded",
            params={
                "product_id": str(product_id).strip(),
                "requested_mode_id": "tui",
                "effective_mode_id": str(degraded.get("effective_mode_id", "")).strip(),
            },
        )
        return {"dispatch_kind": "text", "text": render_tui_text(degraded), "payload": degraded, "exit_code": 0}
    return {"dispatch_kind": "text", "text": "", "payload": surface, "exit_code": 0}


__all__ = [
    "attach_ipc_session_to_surface",
    "build_tui_surface",
    "detach_ipc_session_from_surface",
    "execute_console_session_command",
    "load_tui_layout_registry",
    "load_tui_panel_registry",
    "refresh_ipc_sessions_in_surface",
    "render_tui_text",
    "run_tui_mode",
]
