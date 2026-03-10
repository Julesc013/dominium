"""Deterministic structured logging for AppShell products."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Mapping


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
) -> dict:
    tick_value = _normalize_tick(tick if tick is not None else simulation_tick)
    category_token = str(category or event_kind or "appshell").strip() or "appshell"
    params_payload = dict(_normalize_tree(dict(params or {})))
    if str(message or "").strip() and "message" not in params_payload:
        params_payload["message"] = str(message).strip()
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
        "host_meta": dict(_normalize_tree(dict(host_meta or {}))),
        "extensions": dict(_normalize_tree(dict(extensions or {}))),
        "deterministic_fingerprint": "",
    }
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
    root = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    safe_product_id = str(product_id or "product").strip().replace(".", "_") or "product"
    safe_session_id = str(session_id or "").strip().replace(".", "_")
    file_name = "{}{}.jsonl".format(safe_product_id, ".{}".format(safe_session_id) if safe_session_id else "")
    return os.path.join(root, "build", "appshell", "logs", file_name)


class LogEngine:
    """Process-local deterministic log engine."""

    def __init__(
        self,
        *,
        product_id: str,
        build_id: str,
        session_id: str = "",
        console_enabled: bool = True,
        file_path: str = "",
        ring_capacity: int = DEFAULT_RING_CAPACITY,
    ) -> None:
        self.product_id = str(product_id or "").strip()
        self.build_id = str(build_id or "").strip()
        self.session_id = str(session_id or "").strip()
        self.console_enabled = bool(console_enabled)
        self.file_path = os.path.normpath(os.path.abspath(str(file_path))) if str(file_path or "").strip() else ""
        self.ring_capacity = max(1, int(ring_capacity or DEFAULT_RING_CAPACITY))
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
    session_id: str = "",
    console_enabled: bool = True,
    file_path: str = "",
    ring_capacity: int = DEFAULT_RING_CAPACITY,
) -> LogEngine:
    return LogEngine(
        product_id=product_id,
        build_id=build_id,
        session_id=session_id,
        console_enabled=console_enabled,
        file_path=file_path,
        ring_capacity=ring_capacity,
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
