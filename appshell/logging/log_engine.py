"""Deterministic structured logging for AppShell products."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Mapping

from appshell.paths import VROOT_LOGS, get_current_virtual_paths, vpath_resolve
from meta.observability import redact_observability_mapping, validate_observability_event


LOG_SCHEMA_VERSION = "1.0.0"
DEFAULT_RING_CAPACITY = 128
_CURRENT_LOG_ENGINE = None


def _normalize_scalar(value: object) -> object:
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)


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
    return _normalize_scalar(value)


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    body["host_meta"] = {}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _normalize_tick(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def build_log_event(
    *,
    product_id: str,
    build_id: str = "",
    session_id: str = "",
    event_index: int = 1,
    tick: int | None = None,
    severity: str = "info",
    category: str = "appshell",
    message_key: str = "",
    params: Mapping[str, object] | None = None,
    host_meta: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
    event_kind: str = "",
    message: str = "",
    simulation_tick: int | None = None,
    strict_guarantees: bool = False,
    repo_root: str = "",
) -> dict:
    tick_value = _normalize_tick(tick if tick is not None else simulation_tick)
    category_token = str(category or event_kind or "appshell").strip() or "appshell"
    params_redacted, params_redaction_count = redact_observability_mapping(params)
    host_meta_redacted, host_meta_redaction_count = redact_observability_mapping(host_meta)
    params_payload = dict(_normalize_tree(params_redacted))
    if str(message or "").strip() and "message" not in params_payload:
        params_payload["message"] = str(message).strip()
    extensions_payload = dict(_normalize_tree(dict(extensions or {})))
    payload = {
        "schema_version": LOG_SCHEMA_VERSION,
        "event_id": "log.{:016d}".format(max(1, int(event_index or 1))),
        "product_id": str(product_id or "").strip(),
        "build_id": str(build_id or "").strip(),
        "session_id": str(session_id or "").strip(),
        "tick": tick_value,
        "severity": str(severity or "info").strip().lower() or "info",
        "category": category_token,
        "message_key": str(message_key or "appshell.log.event").strip() or "appshell.log.event",
        "params": params_payload,
        "host_meta": dict(_normalize_tree(host_meta_redacted)),
        "extensions": extensions_payload,
        "deterministic_fingerprint": "",
    }
    contract_report = validate_observability_event(payload, repo_root=repo_root)
    observability_meta = {
        "guaranteed": bool(contract_report.get("guaranteed", False)),
        "redacted_field_count": int(params_redaction_count) + int(host_meta_redaction_count),
        "warning_codes": [str(dict(row).get("code", "")).strip() for row in list(contract_report.get("warnings") or []) if str(dict(row).get("code", "")).strip()],
        "error_codes": [str(dict(row).get("code", "")).strip() for row in list(contract_report.get("errors") or []) if str(dict(row).get("code", "")).strip()],
    }
    merged_extensions = dict(payload.get("extensions") or {})
    merged_extensions["observability"] = dict(_normalize_tree(observability_meta))
    payload["extensions"] = merged_extensions
    if bool(strict_guarantees) and list(contract_report.get("errors") or []):
        raise ValueError(
            "; ".join(
                str(dict(row).get("message", "")).strip() or "observability contract violation"
                for row in list(contract_report.get("errors") or [])
            )
        )
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def append_jsonl(path: str, event: Mapping[str, object]) -> str:
    output_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(dict(_normalize_tree(dict(event or {}))), sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        handle.write("\n")
    return output_path


def build_default_log_file_path(repo_root: str, product_id: str, session_id: str = "") -> str:
    safe_product_id = str(product_id or "product").strip().replace(".", "_") or "product"
    safe_session_id = str(session_id or "").strip().replace(".", "_")
    file_name = "{}{}.jsonl".format(safe_product_id, ".{}".format(safe_session_id) if safe_session_id else "")
    context = get_current_virtual_paths()
    if context is not None and str(context.get("result", "")).strip() == "complete":
        return vpath_resolve(VROOT_LOGS, file_name, context)
    root = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    return os.path.join(root, "build", "appshell", "logs", file_name)


class LogEngine:
    """Process-local deterministic log engine."""

    def __init__(
        self,
        *,
        product_id: str,
        build_id: str,
        repo_root: str = "",
        session_id: str = "",
        console_enabled: bool = True,
        file_path: str = "",
        ring_capacity: int = DEFAULT_RING_CAPACITY,
        strict_guarantees: bool = False,
    ) -> None:
        self.product_id = str(product_id or "").strip()
        self.build_id = str(build_id or "").strip()
        self.repo_root = os.path.normpath(os.path.abspath(str(repo_root))) if str(repo_root or "").strip() else ""
        self.session_id = str(session_id or "").strip()
        self.console_enabled = bool(console_enabled)
        self.file_path = os.path.normpath(os.path.abspath(str(file_path))) if str(file_path or "").strip() else ""
        self.ring_capacity = max(1, int(ring_capacity or DEFAULT_RING_CAPACITY))
        self.strict_guarantees = bool(strict_guarantees)
        self._event_index = 0
        self._ring: list[dict] = []
        if self.file_path:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write("")

    def emit(
        self,
        *,
        category: str,
        severity: str,
        message_key: str,
        params: Mapping[str, object] | None = None,
        tick: int | None = None,
        host_meta: Mapping[str, object] | None = None,
        extensions: Mapping[str, object] | None = None,
        session_id: str = "",
    ) -> dict:
        self._event_index += 1
        payload = build_log_event(
            product_id=self.product_id,
            build_id=self.build_id,
            session_id=str(session_id or self.session_id).strip(),
            event_index=self._event_index,
            tick=tick,
            severity=severity,
            category=category,
            message_key=message_key,
            params=params,
            host_meta=host_meta,
            extensions=extensions,
            strict_guarantees=self.strict_guarantees,
            repo_root=self.repo_root,
        )
        self._ring.append(dict(payload))
        self._ring = list(self._ring[-self.ring_capacity :])
        if self.file_path:
            append_jsonl(self.file_path, payload)
        if self.console_enabled:
            sys.stderr.write(
                json.dumps(dict(_normalize_tree(payload)), sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
            )
            sys.stderr.flush()
        return payload

    def ring_events(self) -> list[dict]:
        return [dict(row) for row in self._ring]


def create_log_engine(
    *,
    product_id: str,
    build_id: str,
    repo_root: str = "",
    session_id: str = "",
    console_enabled: bool = True,
    file_path: str = "",
    ring_capacity: int = DEFAULT_RING_CAPACITY,
    strict_guarantees: bool = False,
) -> LogEngine:
    return LogEngine(
        product_id=product_id,
        build_id=build_id,
        repo_root=repo_root,
        session_id=session_id,
        console_enabled=console_enabled,
        file_path=file_path,
        ring_capacity=ring_capacity,
        strict_guarantees=strict_guarantees,
    )


def set_current_log_engine(engine: LogEngine | None) -> None:
    global _CURRENT_LOG_ENGINE
    _CURRENT_LOG_ENGINE = engine


def get_current_log_engine() -> LogEngine | None:
    return _CURRENT_LOG_ENGINE


def clear_current_log_engine() -> None:
    set_current_log_engine(None)


def log_emit(
    *,
    category: str,
    severity: str,
    message_key: str,
    params: Mapping[str, object] | None = None,
    tick: int | None = None,
    host_meta: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
    session_id: str = "",
    product_id: str = "",
    build_id: str = "",
    repo_root: str = "",
) -> dict:
    engine = get_current_log_engine()
    if engine is None:
        return build_log_event(
            product_id=str(product_id or "appshell").strip() or "appshell",
            build_id=str(build_id or "").strip(),
            session_id=str(session_id or "").strip(),
            event_index=1,
            tick=tick,
            severity=severity,
            category=category,
            message_key=message_key,
            params=params,
            host_meta=host_meta,
            extensions=extensions,
            repo_root=repo_root,
        )
    return engine.emit(
        category=category,
        severity=severity,
        message_key=message_key,
        params=params,
        tick=tick,
        host_meta=host_meta,
        extensions=extensions,
        session_id=session_id,
    )


__all__ = [
    "DEFAULT_RING_CAPACITY",
    "LOG_SCHEMA_VERSION",
    "LogEngine",
    "append_jsonl",
    "build_default_log_file_path",
    "build_log_event",
    "clear_current_log_engine",
    "create_log_engine",
    "get_current_log_engine",
    "log_emit",
    "set_current_log_engine",
]
