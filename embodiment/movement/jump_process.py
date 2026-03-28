"""Deterministic EMB-2 jump and impact helper rows."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


JUMP_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "jump_params_registry.json")
DEFAULT_JUMP_PARAMS_ID = "jump.mvp_default"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    current = here
    markers = (
        os.path.join("docs", "canon", "constitution_v1.md"),
        os.path.join("data", "registries"),
        os.path.join("tools", "xstack"),
    )
    while True:
        if all(os.path.exists(os.path.join(current, marker)) for marker in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.normpath(os.path.join(here, "..", "..", ".."))
        current = parent


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def build_jump_params_row(
    *,
    jump_params_id: str,
    impulse_value: int,
    cooldown_ticks: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "jump_params_id": str(jump_params_id or "").strip(),
        "impulse_value": int(max(1, _as_int(impulse_value, 1))),
        "cooldown_ticks": int(max(0, _as_int(cooldown_ticks, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["jump_params_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_jump_params_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: str(item.get("jump_params_id", ""))):
        normalized = build_jump_params_row(
            jump_params_id=str(row.get("jump_params_id", "")).strip(),
            impulse_value=_as_int(row.get("impulse_value", 1), 1),
            cooldown_ticks=_as_int(row.get("cooldown_ticks", 0), 0),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(normalized.get("jump_params_id", "")).strip()
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def jump_params_rows_by_id(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    body = _as_map(payload) or _registry_payload(JUMP_PARAMS_REGISTRY_REL)
    rows = _as_list(body.get("jump_params")) or _as_list(_as_map(body.get("record")).get("jump_params"))
    normalized = normalize_jump_params_rows(rows)
    return dict((str(row.get("jump_params_id", "")).strip(), dict(row)) for row in normalized if str(row.get("jump_params_id", "")).strip())


def jump_params_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(JUMP_PARAMS_REGISTRY_REL))


def resolve_jump_params_row(
    *,
    jump_params_id: str = DEFAULT_JUMP_PARAMS_ID,
    registry_payload: Mapping[str, object] | None = None,
) -> dict:
    rows = jump_params_rows_by_id(registry_payload)
    token = str(jump_params_id or "").strip() or DEFAULT_JUMP_PARAMS_ID
    return dict(rows.get(token) or rows.get(DEFAULT_JUMP_PARAMS_ID) or {})


def build_impact_event_row(
    *,
    event_id: str,
    subject_id: str,
    tick: int,
    impact_speed: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "event_id": str(event_id or "").strip(),
        "subject_id": str(subject_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "impact_speed": int(max(0, _as_int(impact_speed, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["event_id"] or not payload["subject_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_impact_event_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: str(item.get("event_id", ""))):
        normalized = build_impact_event_row(
            event_id=str(row.get("event_id", "")).strip(),
            subject_id=str(row.get("subject_id", "")).strip(),
            tick=_as_int(row.get("tick", 0), 0),
            impact_speed=_as_int(row.get("impact_speed", 0), 0),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(normalized.get("event_id", "")).strip()
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]
