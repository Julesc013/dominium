"""Deterministic MAT-8 event stream indexing."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _event_matches_target(event_row: Mapping[str, object], target_id: str) -> bool:
    token = str(target_id).strip()
    if not token:
        return False
    row = dict(event_row or {})
    extensions = dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {}
    candidates = {
        str(row.get("event_id", "")).strip(),
        str(row.get("manifest_id", "")).strip(),
        str(row.get("commitment_id", "")).strip(),
        str(row.get("project_id", "")).strip(),
        str(row.get("step_id", "")).strip(),
        str(row.get("linked_project_id", "")).strip(),
        str(row.get("linked_step_id", "")).strip(),
        str(row.get("asset_id", "")).strip(),
        str(row.get("site_ref", "")).strip(),
        str(extensions.get("commitment_id", "")).strip(),
        str(extensions.get("manifest_id", "")).strip(),
        str(extensions.get("project_id", "")).strip(),
        str(extensions.get("asset_id", "")).strip(),
        str(extensions.get("task_id", "")).strip(),
        str(extensions.get("target_semantic_id", "")).strip(),
        str(extensions.get("tool_id", "")).strip(),
    }
    candidates.update(str(item).strip() for item in list(row.get("inputs") or []) if str(item).strip())
    candidates.update(str(item).strip() for item in list(row.get("outputs") or []) if str(item).strip())
    return token in candidates


def normalize_event_stream_index_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    stream_id = str(payload.get("stream_id", "")).strip()
    target_id = str(payload.get("target_id", "")).strip()
    tick_range = dict(payload.get("tick_range") or {})
    start_tick = max(0, _as_int(tick_range.get("start_tick", 0), 0))
    end_tick = max(start_tick, _as_int(tick_range.get("end_tick", start_tick), start_tick))
    event_ids = _sorted_unique_strings(payload.get("event_ids"))
    if not stream_id:
        stream_id = "stream.event.{}".format(
            canonical_sha256(
                {
                    "target_id": target_id,
                    "tick_range": {"start_tick": int(start_tick), "end_tick": int(end_tick)},
                    "event_ids": list(event_ids),
                }
            )[:24]
        )
    out = {
        "schema_version": "1.0.0",
        "stream_id": stream_id,
        "target_id": target_id,
        "tick_range": {
            "start_tick": int(start_tick),
            "end_tick": int(end_tick),
        },
        "event_ids": list(event_ids),
        "stream_hash": "",
        "extensions": dict(payload.get("extensions") or {}),
    }
    out["stream_hash"] = canonical_sha256(
        {
            "stream_id": str(out.get("stream_id", "")),
            "target_id": str(out.get("target_id", "")),
            "tick_range": dict(out.get("tick_range") or {}),
            "event_ids": list(out.get("event_ids") or []),
        }
    )
    return out


def build_event_stream_index(
    *,
    target_id: str,
    events: object,
    start_tick: int = 0,
    end_tick: int = 0,
) -> dict:
    token = str(target_id).strip()
    rows: List[dict] = []
    if isinstance(events, list):
        for row in events:
            if not isinstance(row, dict):
                continue
            tick = max(0, _as_int(row.get("tick", 0), 0))
            if tick < int(max(0, int(start_tick))):
                continue
            if int(end_tick) > 0 and tick > int(end_tick):
                continue
            if not _event_matches_target(row, token):
                continue
            rows.append(dict(row))
    rows = sorted(rows, key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("event_id", ""))))
    event_ids = [str(row.get("event_id", "")).strip() for row in rows if str(row.get("event_id", "")).strip()]
    normalized = normalize_event_stream_index_row(
        {
            "stream_id": "",
            "target_id": token,
            "tick_range": {
                "start_tick": int(max(0, int(start_tick))),
                "end_tick": int(max(max(0, int(start_tick)), int(end_tick))),
            },
            "event_ids": list(event_ids),
            "extensions": {
                "event_count": len(event_ids),
            },
        }
    )
    normalized["extensions"] = dict(normalized.get("extensions") or {})
    normalized["extensions"]["event_count"] = len(event_ids)
    normalized["extensions"]["event_rows"] = [
        {
            "event_id": str(row.get("event_id", "")).strip(),
            "tick": max(0, _as_int(row.get("tick", 0), 0)),
            "event_type_id": str(row.get("event_type_id", "")).strip() or str(row.get("event_type", "")).strip(),
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
            "commitment_id": str(row.get("commitment_id", "")).strip(),
            "manifest_id": str(row.get("manifest_id", "")).strip(),
            "linked_project_id": str(row.get("linked_project_id", "")).strip(),
            "linked_step_id": str(row.get("linked_step_id", "")).strip(),
            "asset_id": str(row.get("asset_id", "")).strip(),
        }
        for row in rows
    ]
    return normalized
