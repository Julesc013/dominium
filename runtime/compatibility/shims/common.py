"""Deterministic helpers for transitional compatibility shims."""

from __future__ import annotations

import json
import sys
from typing import Iterable, Mapping

from runtime.shell.logging import get_current_log_engine, log_emit
from engine.serialization.canonical_json import canonical_sha256


SHIM_FUTURE_SERIES = "RESTRUCTURE"
SHIM_SUNSET_TARGET = "remove after v0.0.1 or after directory restructure convergence"
_EMITTED_WARNING_KEYS: set[tuple[str, str, str]] = set()


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _marker_seed(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    seed = {
        "schema_version": _token(payload.get("schema_version")),
        "stability_class_id": _token(payload.get("stability_class_id")),
        "rationale": _token(payload.get("rationale")),
        "future_series": _token(payload.get("future_series")),
        "replacement_target": _token(payload.get("replacement_target")),
        "contract_id": _token(payload.get("contract_id")),
        "deterministic_fingerprint": "",
        "extensions": dict(sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))),
    }
    deprecated = payload.get("deprecated")
    if isinstance(deprecated, bool):
        seed["deprecated"] = bool(deprecated)
    return seed


def stability_marker_fingerprint(row: Mapping[str, object] | None) -> str:
    return canonical_sha256(_marker_seed(row))


def build_stability_marker(
    *,
    stability_class_id: str,
    rationale: str,
    future_series: str = "",
    replacement_target: str = "",
    contract_id: str = "",
    deprecated: bool | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": _token(stability_class_id),
        "rationale": _token(rationale),
        "future_series": _token(future_series),
        "replacement_target": _token(replacement_target),
        "contract_id": _token(contract_id),
        "deterministic_fingerprint": "",
        "extensions": dict(_as_map(extensions)),
    }
    if deprecated is not None:
        payload["deprecated"] = bool(deprecated)
    payload["deterministic_fingerprint"] = stability_marker_fingerprint(payload)
    return payload


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)


def build_shim_stability(*, rationale: str, replacement_target: str) -> dict:
    return build_stability_marker(
        stability_class_id="provisional",
        rationale=_token(rationale),
        future_series=SHIM_FUTURE_SERIES,
        replacement_target=_token(replacement_target),
        extensions={"sunset_target": SHIM_SUNSET_TARGET},
    )


def build_deprecation_warning(
    *,
    shim_id: str,
    warning_code: str,
    message_key: str,
    original_surface: str,
    replacement_surface: str,
    details: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "warning_id": "warning.{}".format(_token(shim_id).replace(".", "_")),
        "shim_id": _token(shim_id),
        "warning_code": _token(warning_code),
        "message_key": _token(message_key),
        "original_surface": _token(original_surface),
        "replacement_surface": _token(replacement_surface),
        "details": dict(_normalize_tree(dict(details or {}))),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def emit_deprecation_warning(
    *,
    category: str,
    severity: str,
    shim_id: str,
    warning_code: str,
    message_key: str,
    original_surface: str,
    replacement_surface: str,
    details: Mapping[str, object] | None = None,
) -> dict:
    payload = build_deprecation_warning(
        shim_id=shim_id,
        warning_code=warning_code,
        message_key=message_key,
        original_surface=original_surface,
        replacement_surface=replacement_surface,
        details=details,
    )
    key = (
        _token(payload.get("warning_code")),
        _token(payload.get("original_surface")),
        _token(payload.get("replacement_surface")),
    )
    if key in _EMITTED_WARNING_KEYS:
        return payload
    _EMITTED_WARNING_KEYS.add(key)
    logger = get_current_log_engine()
    if logger is not None:
        log_emit(
            category=_token(category) or "compat",
            severity=_token(severity) or "warn",
            message_key=_token(message_key),
            params={
                "shim_id": _token(payload.get("shim_id")),
                "warning_code": _token(payload.get("warning_code")),
                "original_surface": _token(payload.get("original_surface")),
                "replacement_surface": _token(payload.get("replacement_surface")),
                "details": dict(payload.get("details") or {}),
            },
        )
    else:
        sys.stderr.write(json.dumps(dict(_normalize_tree(payload)), sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n")
        sys.stderr.flush()
    return payload


def reset_emitted_warnings() -> None:
    _EMITTED_WARNING_KEYS.clear()


def stable_rows(rows: Iterable[Mapping[str, object]]) -> list[dict]:
    return sorted(
        [dict(_normalize_tree(dict(row or {}))) for row in list(rows or []) if isinstance(row, Mapping)],
        key=lambda row: (_token(row.get("shim_id")), _token(row.get("legacy_surface")), _token(row.get("replacement_surface"))),
    )


__all__ = [
    "SHIM_FUTURE_SERIES",
    "SHIM_SUNSET_TARGET",
    "build_deprecation_warning",
    "build_shim_stability",
    "emit_deprecation_warning",
    "reset_emitted_warnings",
    "stable_rows",
    "stability_marker_fingerprint",
]
