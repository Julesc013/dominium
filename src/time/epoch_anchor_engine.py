"""Deterministic TIME-ANCHOR-0 epoch anchor helpers."""

from __future__ import annotations

import json
import os
from typing import Iterable, Mapping

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
from tools.xstack.compatx.validator import validate_instance

from .tick_t import (
    REFUSAL_TICK_OVERFLOW_IMMINENT,
    TICK_REFUSAL_THRESHOLD,
    TickT,
    assert_tick_t,
    normalize_tick_t,
)


DEFAULT_TIME_ANCHOR_POLICY_ID = "time.anchor.mvp_default"
TIME_ANCHOR_POLICY_REGISTRY_REL = os.path.join("data", "registries", "time_anchor_policy_registry.json")
ANCHOR_REASON_INTERVAL = "interval"
ANCHOR_REASON_SAVE = "save"
ANCHOR_REASON_MIGRATION = "migration"
ANCHOR_REASON_PRIORITY = {
    ANCHOR_REASON_INTERVAL: 0,
    ANCHOR_REASON_SAVE: 1,
    ANCHOR_REASON_MIGRATION: 2,
}


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, Mapping):
        return {}, "invalid root object"
    return dict(payload), ""


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")


def _normalize_hash64(token: object, seed: object) -> str:
    value = _token(token).lower()
    if len(value) == 64 and all(ch in "0123456789abcdef" for ch in value):
        return value
    return canonical_sha256(seed)


def time_anchor_policy_fingerprint(payload: Mapping[str, object] | None) -> str:
    row = _as_map(payload)
    return canonical_sha256(
        {
            "schema_version": _token(row.get("schema_version")) or "1.0.0",
            "time_anchor_policy_id": _token(row.get("time_anchor_policy_id")),
            "tick_type_id": _token(row.get("tick_type_id")),
            "anchor": {
                "interval_ticks": int(max(1, _as_int(_as_map(row.get("anchor")).get("interval_ticks", 1), 1))),
                "emit_on_save": bool(_as_map(row.get("anchor")).get("emit_on_save", False)),
                "emit_on_migration": bool(_as_map(row.get("anchor")).get("emit_on_migration", False)),
            },
            "overflow_policy": {
                "reserved_rollover_ticks": int(
                    max(0, _as_int(_as_map(row.get("overflow_policy")).get("reserved_rollover_ticks", 0), 0))
                ),
                "refusal_threshold_tick": int(
                    max(
                        0,
                        _as_int(
                            _as_map(row.get("overflow_policy")).get("refusal_threshold_tick", TICK_REFUSAL_THRESHOLD),
                            TICK_REFUSAL_THRESHOLD,
                        ),
                    )
                ),
                "refusal_code": _token(_as_map(row.get("overflow_policy")).get("refusal_code"))
                or REFUSAL_TICK_OVERFLOW_IMMINENT,
            },
            "deterministic_fingerprint": "",
            "extensions": dict(sorted(_as_map(row.get("extensions")).items(), key=lambda item: str(item[0]))),
        }
    )


def epoch_anchor_fingerprint(payload: Mapping[str, object] | None) -> str:
    row = _as_map(payload)
    return canonical_sha256(
        {
            "schema_version": "1.0.0",
            "anchor_id": _token(row.get("anchor_id")),
            "tick": int(normalize_tick_t(row.get("tick", 0))),
            "truth_hash": _normalize_hash64(row.get("truth_hash"), row),
            "contract_bundle_hash": _normalize_hash64(row.get("contract_bundle_hash"), row),
            "pack_lock_hash": _normalize_hash64(row.get("pack_lock_hash"), row),
            "overlay_manifest_hash": _normalize_hash64(row.get("overlay_manifest_hash"), row),
            "deterministic_fingerprint": "",
            "extensions": dict(sorted(_as_map(row.get("extensions")).items(), key=lambda item: str(item[0]))),
        }
    )


def load_time_anchor_policy(
    repo_root: str,
    *,
    policy_id: str = DEFAULT_TIME_ANCHOR_POLICY_ID,
) -> tuple[dict, dict]:
    abs_path = os.path.join(os.path.normpath(os.path.abspath(repo_root)), TIME_ANCHOR_POLICY_REGISTRY_REL.replace("/", os.sep))
    payload, error = _read_json(abs_path)
    if error:
        return {}, {
            "result": "refused",
            "reason_code": "refusal.time.anchor_policy_missing",
            "message": "time anchor policy registry is missing or invalid",
        }
    rows = list(_as_map(payload.get("record")).get("policies") or [])
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: _token(item.get("time_anchor_policy_id"))):
        if _token(row.get("time_anchor_policy_id")) != _token(policy_id):
            continue
        expected = time_anchor_policy_fingerprint(row)
        if _token(row.get("deterministic_fingerprint")).lower() != expected:
            return {}, {
                "result": "refused",
                "reason_code": "refusal.time.anchor_policy_fingerprint_mismatch",
                "message": "time anchor policy deterministic_fingerprint does not match canonical content",
                "policy_id": _token(policy_id),
            }
        return row, {}
    return {}, {
        "result": "refused",
        "reason_code": "refusal.time.anchor_policy_missing",
        "message": "time anchor policy is unavailable",
        "policy_id": _token(policy_id),
    }


def anchor_interval_ticks(policy_row: Mapping[str, object] | None) -> TickT:
    anchor = _as_map(_as_map(policy_row).get("anchor"))
    return normalize_tick_t(max(1, _as_int(anchor.get("interval_ticks", 1), 1)))


def should_emit_epoch_anchor(*, policy_row: Mapping[str, object] | None, tick: object, reason: str) -> bool:
    tick_value = int(normalize_tick_t(tick))
    reason_token = _token(reason)
    if reason_token == ANCHOR_REASON_INTERVAL:
        interval = int(anchor_interval_ticks(policy_row))
        return interval > 0 and tick_value % interval == 0
    anchor = _as_map(_as_map(policy_row).get("anchor"))
    if reason_token == ANCHOR_REASON_SAVE:
        return bool(anchor.get("emit_on_save", False))
    if reason_token == ANCHOR_REASON_MIGRATION:
        return bool(anchor.get("emit_on_migration", False))
    return False


def build_epoch_anchor_record(
    *,
    tick: object,
    truth_hash: object,
    contract_bundle_hash: object,
    pack_lock_hash: object,
    overlay_manifest_hash: object,
    reason: str,
    anchor_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    tick_value = int(assert_tick_t(tick))
    extensions_payload = dict(_as_map(extensions))
    extensions_payload["reason"] = _token(reason) or ANCHOR_REASON_INTERVAL
    payload = {
        "schema_version": "1.0.0",
        "anchor_id": _token(anchor_id),
        "tick": int(tick_value),
        "truth_hash": _normalize_hash64(truth_hash, {"tick": tick_value, "field": "truth_hash"}),
        "contract_bundle_hash": _normalize_hash64(
            contract_bundle_hash,
            {"tick": tick_value, "field": "contract_bundle_hash"},
        ),
        "pack_lock_hash": _normalize_hash64(pack_lock_hash, {"tick": tick_value, "field": "pack_lock_hash"}),
        "overlay_manifest_hash": _normalize_hash64(
            overlay_manifest_hash,
            {"tick": tick_value, "field": "overlay_manifest_hash"},
        ),
        "deterministic_fingerprint": "",
        "extensions": extensions_payload,
    }
    if not payload["anchor_id"]:
        payload["anchor_id"] = "epoch.anchor.tick.{}.{}.{}".format(
            int(tick_value),
            _token(reason) or ANCHOR_REASON_INTERVAL,
            canonical_sha256(
                {
                    "tick": int(tick_value),
                    "reason": _token(reason) or ANCHOR_REASON_INTERVAL,
                    "truth_hash": payload["truth_hash"],
                    "contract_bundle_hash": payload["contract_bundle_hash"],
                    "pack_lock_hash": payload["pack_lock_hash"],
                    "overlay_manifest_hash": payload["overlay_manifest_hash"],
                }
            )[:16],
        )
    payload["deterministic_fingerprint"] = epoch_anchor_fingerprint(payload)
    return payload


def emit_epoch_anchor(
    *,
    repo_root: str,
    anchor_root_path: str,
    tick: object,
    truth_hash: object,
    contract_bundle_hash: object,
    pack_lock_hash: object,
    overlay_manifest_hash: object,
    reason: str,
    policy_id: str = DEFAULT_TIME_ANCHOR_POLICY_ID,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    policy_row, policy_error = load_time_anchor_policy(repo_root_abs, policy_id=policy_id)
    if policy_error:
        return policy_error
    tick_value = int(assert_tick_t(tick))
    if tick_value > int(_as_int(_as_map(policy_row.get("overflow_policy")).get("refusal_threshold_tick", TICK_REFUSAL_THRESHOLD), TICK_REFUSAL_THRESHOLD)):
        return {
            "result": "refused",
            "reason_code": _token(_as_map(policy_row.get("overflow_policy")).get("refusal_code")) or REFUSAL_TICK_OVERFLOW_IMMINENT,
            "message": "canonical tick advance is beyond the guarded threshold",
            "tick": int(tick_value),
        }
    if not should_emit_epoch_anchor(policy_row=policy_row, tick=tick_value, reason=reason):
        return {
            "result": "skipped",
            "tick": int(tick_value),
            "reason": _token(reason),
            "policy_id": _token(policy_id),
        }

    anchor_root_abs = os.path.normpath(os.path.abspath(anchor_root_path))
    reason_token = _token(reason) or ANCHOR_REASON_INTERVAL
    record = build_epoch_anchor_record(
        tick=tick_value,
        truth_hash=truth_hash,
        contract_bundle_hash=contract_bundle_hash,
        pack_lock_hash=pack_lock_hash,
        overlay_manifest_hash=overlay_manifest_hash,
        reason=reason_token,
        extensions=extensions,
    )
    validation = validate_instance(
        repo_root=repo_root_abs,
        schema_name="epoch_anchor_record",
        payload=record,
        strict_top_level=True,
    )
    if not bool(validation.get("valid", False)):
        return {
            "result": "refused",
            "reason_code": "refusal.time.anchor_schema_invalid",
            "message": "epoch anchor record failed schema validation",
            "tick": int(tick_value),
            "errors": list(validation.get("errors") or []),
        }

    os.makedirs(anchor_root_abs, exist_ok=True)
    file_name = "epoch.anchor.tick.{}.{}.json".format(int(tick_value), reason_token)
    anchor_abs = os.path.join(anchor_root_abs, file_name)
    _write_canonical_json(anchor_abs, record)
    try:
        anchor_rel = _norm(os.path.relpath(anchor_abs, repo_root_abs))
    except ValueError:
        anchor_rel = _norm(anchor_abs)
    return {
        "result": "complete",
        "policy_id": _token(policy_id),
        "tick": int(tick_value),
        "reason": reason_token,
        "anchor": record,
        "anchor_path": anchor_rel,
    }


def load_epoch_anchor_rows(anchor_root_path: str) -> list[dict]:
    root = os.path.normpath(os.path.abspath(str(anchor_root_path or "")))
    if not root or not os.path.isdir(root):
        return []
    rows: list[dict] = []
    for name in sorted(item for item in os.listdir(root) if str(item).endswith(".json")):
        payload, error = _read_json(os.path.join(root, name))
        if error:
            continue
        if _token(payload.get("schema_version")) != "1.0.0":
            continue
        if not _token(payload.get("anchor_id")):
            continue
        rows.append(dict(payload))
    return sorted_anchor_rows(rows)


def sorted_anchor_rows(rows: Iterable[Mapping[str, object]] | None) -> list[dict]:
    return sorted(
        [dict(row) for row in list(rows or []) if isinstance(row, Mapping)],
        key=lambda row: (
            int(normalize_tick_t(row.get("tick", 0))),
            int(ANCHOR_REASON_PRIORITY.get(_token(_as_map(row.get("extensions")).get("reason")), 99)),
            _token(row.get("anchor_id")),
        ),
    )


def anchor_rows_by_tick(rows: Iterable[Mapping[str, object]] | None) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {}
    for row in sorted_anchor_rows(rows):
        tick_value = int(normalize_tick_t(row.get("tick", 0)))
        out.setdefault(tick_value, []).append(dict(row))
    return dict((tick, list(values)) for tick, values in sorted(out.items(), key=lambda item: int(item[0])))


def select_boundary_anchor(rows: Iterable[Mapping[str, object]] | None, *, tick: object) -> dict:
    tick_value = int(normalize_tick_t(tick))
    rows_by_tick = anchor_rows_by_tick(rows)
    selected = list(rows_by_tick.get(tick_value) or [])
    return dict(selected[0]) if selected else {}


def resolve_compaction_bounds(
    rows: Iterable[Mapping[str, object]] | None,
    *,
    start_tick: object,
    end_tick: object,
) -> tuple[dict, dict, dict]:
    start_value = int(normalize_tick_t(start_tick))
    end_value = int(normalize_tick_t(end_tick))
    lower = select_boundary_anchor(rows, tick=start_value)
    upper = select_boundary_anchor(rows, tick=end_value)
    if not lower or not upper:
        return {}, {}, {
            "result": "refused",
            "reason_code": "refusal.time.compaction_anchor_missing",
            "message": "compaction boundaries must align to epoch anchors",
            "start_tick": int(start_value),
            "end_tick": int(end_value),
        }
    return lower, upper, {}


__all__ = [
    "ANCHOR_REASON_INTERVAL",
    "ANCHOR_REASON_MIGRATION",
    "ANCHOR_REASON_PRIORITY",
    "ANCHOR_REASON_SAVE",
    "DEFAULT_TIME_ANCHOR_POLICY_ID",
    "TIME_ANCHOR_POLICY_REGISTRY_REL",
    "anchor_interval_ticks",
    "anchor_rows_by_tick",
    "build_epoch_anchor_record",
    "emit_epoch_anchor",
    "epoch_anchor_fingerprint",
    "load_epoch_anchor_rows",
    "load_time_anchor_policy",
    "resolve_compaction_bounds",
    "select_boundary_anchor",
    "should_emit_epoch_anchor",
    "sorted_anchor_rows",
    "time_anchor_policy_fingerprint",
]
