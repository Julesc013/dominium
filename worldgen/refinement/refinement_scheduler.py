"""Deterministic MW-4 refinement request, scheduling, and status helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from geo.worldgen.worldgen_engine import build_worldgen_request_for_cell, normalize_worldgen_result_rows
from tools.xstack.compatx.canonical_json import canonical_sha256


EXPLAIN_REFINEMENT_DEFERRED = "explain.refinement_deferred"
EXPLAIN_CONTRACT_MISMATCH_CACHE = "explain.contract_mismatch_cache"
DEFAULT_REFINEMENT_QUEUE_CAPACITY = 256
DEFAULT_REFINEMENT_COST_UNITS = 1

REQUEST_KIND_PRECEDENCE = {
    "teleport": 0,
    "roi": 1,
    "inspect": 2,
    "path": 3,
}

PRIORITY_CLASS_PRECEDENCE = {
    "priority.teleport.destination": 0,
    "priority.roi.current": 1,
    "priority.roi.nearby": 2,
    "priority.inspect.focus": 3,
    "priority.path.current": 4,
    "priority.background.prefetch": 5,
}

REQUEST_KIND_TO_WORLDGEN_REASON = {
    "teleport": "query",
    "roi": "roi",
    "inspect": "query",
    "path": "pathing",
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _coerced_cell_key(cell_key: Mapping[str, object] | None) -> dict:
    return _coerce_cell_key(cell_key) or {}


def _normalized_extensions(extensions: Mapping[str, object] | None) -> dict:
    return dict((str(key), value) for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0])))


def _semantic_geo_cell_key(cell_key: Mapping[str, object] | None) -> dict:
    row = _coerced_cell_key(cell_key)
    return _semantic_cell_key(row) if row else {}


def _geo_sort_tuple(cell_key: Mapping[str, object] | None) -> tuple:
    row = _coerced_cell_key(cell_key)
    chart_id = str(row.get("chart_id", "")).strip()
    index_tuple = [int(_as_int(item, 0)) for item in list(row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return (
        chart_id,
        int(_as_int(row.get("refinement_level", 0), 0)),
        int(index_tuple[0]),
        int(index_tuple[1]),
        int(index_tuple[2]),
    )


def _priority_rank(priority_class: str) -> int:
    return int(PRIORITY_CLASS_PRECEDENCE.get(str(priority_class or "").strip(), 99))


def _request_kind_rank(request_kind: str) -> int:
    return int(REQUEST_KIND_PRECEDENCE.get(str(request_kind or "").strip(), 99))


def build_refinement_request_record(
    *,
    request_id: str,
    request_kind: str,
    geo_cell_key: Mapping[str, object] | None,
    refinement_level: int,
    priority_class: str,
    tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind = str(request_kind or "").strip()
    if kind not in REQUEST_KIND_PRECEDENCE:
        raise ValueError("request_kind is invalid")
    cell_key = _coerced_cell_key(geo_cell_key)
    if not cell_key:
        raise ValueError("geo_cell_key is required")
    payload = {
        "request_id": str(request_id or "").strip(),
        "request_kind": kind,
        "geo_cell_key": dict(cell_key),
        "refinement_level": int(max(0, _as_int(refinement_level, 0))),
        "priority_class": str(priority_class or "").strip() or "priority.background.prefetch",
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _normalized_extensions(extensions),
    }
    if not payload["request_id"]:
        raise ValueError("request_id is required")
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_refinement_request_record(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    request_id = str(payload.get("request_id", "")).strip()
    if not request_id:
        request_id = "refinement.request.{}".format(canonical_sha256(payload)[:16])
    return build_refinement_request_record(
        request_id=request_id,
        request_kind=str(payload.get("request_kind", "")).strip(),
        geo_cell_key=_as_map(payload.get("geo_cell_key")),
        refinement_level=int(max(0, _as_int(payload.get("refinement_level", 0), 0))),
        priority_class=str(payload.get("priority_class", "")).strip() or "priority.background.prefetch",
        tick=int(max(0, _as_int(payload.get("tick", 0), 0))),
        extensions=_as_map(payload.get("extensions")),
    )


def normalize_refinement_request_record_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            continue
        try:
            normalized = normalize_refinement_request_record(raw)
        except ValueError:
            continue
        out[str(normalized.get("request_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def refinement_request_sort_key(row: Mapping[str, object] | None) -> tuple:
    payload = normalize_refinement_request_record(row)
    return (
        _priority_rank(str(payload.get("priority_class", "")).strip()),
        _request_kind_rank(str(payload.get("request_kind", "")).strip()),
        int(max(0, _as_int(payload.get("tick", 0), 0))),
        _geo_sort_tuple(payload.get("geo_cell_key")),
        int(max(0, _as_int(payload.get("refinement_level", 0), 0))),
        str(payload.get("request_id", "")),
    )


def _semantic_request_identity(row: Mapping[str, object] | None) -> str:
    payload = normalize_refinement_request_record(row)
    return canonical_sha256(
        {
            "request_kind": str(payload.get("request_kind", "")).strip(),
            "geo_cell_key": _semantic_geo_cell_key(payload.get("geo_cell_key")),
            "refinement_level": int(max(0, _as_int(payload.get("refinement_level", 0), 0))),
            "priority_class": str(payload.get("priority_class", "")).strip(),
        }
    )


def merge_refinement_request_record_rows(
    *,
    existing_rows: object,
    new_rows: object,
    queue_capacity: int = DEFAULT_REFINEMENT_QUEUE_CAPACITY,
) -> dict:
    candidates = []
    for raw in list(existing_rows or []) + list(new_rows or []):
        if not isinstance(raw, Mapping):
            continue
        try:
            candidates.append(normalize_refinement_request_record(raw))
        except ValueError:
            continue
    by_semantic: Dict[str, dict] = {}
    for row in sorted(candidates, key=refinement_request_sort_key):
        semantic_id = _semantic_request_identity(row)
        if semantic_id not in by_semantic:
            by_semantic[semantic_id] = dict(row)
    merged = sorted(by_semantic.values(), key=refinement_request_sort_key)
    capacity = int(max(1, _as_int(queue_capacity, DEFAULT_REFINEMENT_QUEUE_CAPACITY)))
    queued = [dict(row) for row in merged[:capacity]]
    dropped = [dict(row) for row in merged[capacity:]]
    payload = {
        "result": "complete",
        "queued_rows": [dict(row) for row in queued],
        "dropped_rows": [dict(row) for row in dropped],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_refinement_deferred_artifact(
    *,
    request_row: Mapping[str, object] | None,
    reason_code: str,
    current_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    row = normalize_refinement_request_record(request_row)
    payload = {
        "explain_id": "explain.refinement_deferred.{}".format(canonical_sha256([row, reason_code, int(current_tick)])[:16]),
        "explain_contract_id": EXPLAIN_REFINEMENT_DEFERRED,
        "request_id": str(row.get("request_id", "")).strip(),
        "request_kind": str(row.get("request_kind", "")).strip(),
        "reason_code": str(reason_code or "").strip() or "refinement.deferred.unspecified",
        "tick": int(max(0, _as_int(current_tick, 0))),
        "geo_cell_key": dict(_coerced_cell_key(row.get("geo_cell_key"))),
        "refinement_level": int(max(0, _as_int(row.get("refinement_level", 0), 0))),
        "extensions": _normalized_extensions(extensions),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_scheduler_plan(
    *,
    pending_request_rows: object,
    current_tick: int,
    compute_budget_units: int,
    refinement_cost_units: int = DEFAULT_REFINEMENT_COST_UNITS,
    queue_capacity: int = DEFAULT_REFINEMENT_QUEUE_CAPACITY,
) -> dict:
    merged = merge_refinement_request_record_rows(
        existing_rows=pending_request_rows,
        new_rows=[],
        queue_capacity=queue_capacity,
    )
    queued = [dict(row) for row in list(merged.get("queued_rows") or []) if isinstance(row, Mapping)]
    dropped = [dict(row) for row in list(merged.get("dropped_rows") or []) if isinstance(row, Mapping)]
    budget_units = int(max(0, _as_int(compute_budget_units, 0)))
    cost_units = int(max(1, _as_int(refinement_cost_units, DEFAULT_REFINEMENT_COST_UNITS)))
    approved_count = int(budget_units // cost_units) if budget_units > 0 else 0
    approved_rows = [dict(row) for row in queued[:approved_count]]
    deferred_rows = [dict(row) for row in queued[approved_count:]]
    explain_rows = []
    explain_rows.extend(
        build_refinement_deferred_artifact(
            request_row=row,
            reason_code="refinement.deferred.budget_denied",
            current_tick=int(max(0, _as_int(current_tick, 0))),
            extensions={"source": "MW4-3", "policy": "budget"},
        )
        for row in deferred_rows
    )
    explain_rows.extend(
        build_refinement_deferred_artifact(
            request_row=row,
            reason_code="refinement.deferred.queue_overflow",
            current_tick=int(max(0, _as_int(current_tick, 0))),
            extensions={"source": "MW4-3", "policy": "queue_capacity"},
        )
        for row in dropped
    )
    payload = {
        "result": "complete",
        "approved_rows": [dict(row) for row in approved_rows],
        "deferred_rows": [dict(row) for row in deferred_rows],
        "dropped_rows": [dict(row) for row in dropped],
        "remaining_rows": [dict(row) for row in deferred_rows],
        "explain_rows": [dict(row) for row in sorted(explain_rows, key=lambda item: str(item.get("explain_id", "")))],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def refinement_record_to_worldgen_request(record: Mapping[str, object] | None) -> dict:
    row = normalize_refinement_request_record(record)
    request_kind = str(row.get("request_kind", "")).strip()
    return build_worldgen_request_for_cell(
        geo_cell_key=_as_map(row.get("geo_cell_key")),
        refinement_level=int(max(0, _as_int(row.get("refinement_level", 0), 0))),
        reason=str(REQUEST_KIND_TO_WORLDGEN_REASON.get(request_kind, "query")),
        request_id_prefix="worldgen.refinement",
        extensions={
            "source": "MW4-3",
            "request_kind": request_kind,
            "priority_class": str(row.get("priority_class", "")).strip(),
            "refinement_request_id": str(row.get("request_id", "")).strip(),
            **_as_map(row.get("extensions")),
        },
    )


def build_refinement_status_view(
    *,
    region_id: str,
    cell_keys: object,
    pending_request_rows: object,
    worldgen_result_rows: object,
    refinement_cache_entries: object,
    deferred_request_rows: object = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    normalized_cells = []
    seen_cells = set()
    for raw in list(cell_keys or []):
        row = _coerced_cell_key(raw)
        if not row:
            continue
        cell_token = canonical_sha256(_semantic_geo_cell_key(row))
        if cell_token in seen_cells:
            continue
        seen_cells.add(cell_token)
        normalized_cells.append(dict(row))
    normalized_cells = sorted(normalized_cells, key=_geo_sort_tuple)
    pending_rows = normalize_refinement_request_record_rows(pending_request_rows)
    deferred_rows = normalize_refinement_request_record_rows(deferred_request_rows)
    result_rows = normalize_worldgen_result_rows(worldgen_result_rows)
    cache_rows = []
    from .refinement_cache import normalize_refinement_cache_entry_rows

    cache_rows = normalize_refinement_cache_entry_rows(refinement_cache_entries)
    pending_by_cell: Dict[str, int] = {}
    deferred_by_cell: Dict[str, int] = {}
    present_by_cell: Dict[str, int] = {}
    cache_by_cell_level: Dict[str, dict] = {}
    for row in pending_rows:
        cell_token = canonical_sha256(_semantic_geo_cell_key(row.get("geo_cell_key")))
        pending_by_cell[cell_token] = max(
            int(max(0, _as_int(row.get("refinement_level", 0), 0))),
            int(pending_by_cell.get(cell_token, -1)),
        )
    for row in deferred_rows:
        cell_token = canonical_sha256(_semantic_geo_cell_key(row.get("geo_cell_key")))
        deferred_by_cell[cell_token] = max(
            int(max(0, _as_int(row.get("refinement_level", 0), 0))),
            int(deferred_by_cell.get(cell_token, -1)),
        )
    for row in result_rows:
        cell_key = _as_map(row.get("geo_cell_key"))
        cell_token = canonical_sha256(_semantic_geo_cell_key(cell_key))
        level = int(max(0, _as_int(_as_map(row.get("extensions")).get("refinement_level", 0), 0)))
        present_by_cell[cell_token] = max(level, int(present_by_cell.get(cell_token, -1)))
    for row in cache_rows:
        cell_token = canonical_sha256(_semantic_geo_cell_key(row.get("geo_cell_key")))
        level = int(max(0, _as_int(row.get("refinement_level", 0), 0)))
        cache_by_cell_level["{}::{}".format(cell_token, level)] = dict(row)
    status_rows = []
    for cell_key in normalized_cells:
        cell_token = canonical_sha256(_semantic_geo_cell_key(cell_key))
        max_present = int(present_by_cell.get(cell_token, -1))
        max_pending = int(pending_by_cell.get(cell_token, -1))
        max_deferred = int(deferred_by_cell.get(cell_token, -1))
        for level in range(0, 4):
            status = "absent"
            if max_present >= level:
                status = "present"
            elif max_deferred >= level:
                status = "deferred"
            elif max_pending >= level:
                status = "queued"
            cache_row = dict(cache_by_cell_level.get("{}::{}".format(cell_token, level)) or {})
            status_row = {
                "geo_cell_key": dict(cell_key),
                "refinement_level": int(level),
                "status": status,
                "cache_key": str(cache_row.get("cache_key", "")).strip(),
                "cache_resident": bool(cache_row),
                "last_used_tick": cache_row.get("last_used_tick"),
            }
            status_rows.append(status_row)
    payload = {
        "region_id": str(region_id or "").strip() or "region.refinement.current",
        "cell_keys": [dict(row) for row in normalized_cells],
        "status_per_level": [
            dict(row)
            for row in sorted(
                status_rows,
                key=lambda item: (
                    _geo_sort_tuple(item.get("geo_cell_key")),
                    int(max(0, _as_int(item.get("refinement_level", 0), 0))),
                ),
            )
        ],
        "deterministic_fingerprint": "",
        "extensions": _normalized_extensions(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_refinement_layer_source_payloads(status_view: Mapping[str, object] | None) -> dict:
    view = _as_map(status_view)
    rows = [dict(row) for row in list(view.get("status_per_level") or []) if isinstance(row, Mapping)]
    return {
        "layer.refinement_status": {
            "source_kind": "refinement_status_view",
            "rows": rows,
            "status_view": dict(view),
        }
    }


__all__ = [
    "DEFAULT_REFINEMENT_COST_UNITS",
    "DEFAULT_REFINEMENT_QUEUE_CAPACITY",
    "EXPLAIN_CONTRACT_MISMATCH_CACHE",
    "EXPLAIN_REFINEMENT_DEFERRED",
    "PRIORITY_CLASS_PRECEDENCE",
    "REQUEST_KIND_PRECEDENCE",
    "build_refinement_deferred_artifact",
    "build_refinement_layer_source_payloads",
    "build_refinement_request_record",
    "build_refinement_status_view",
    "build_scheduler_plan",
    "merge_refinement_request_record_rows",
    "normalize_refinement_request_record",
    "normalize_refinement_request_record_rows",
    "refinement_record_to_worldgen_request",
    "refinement_request_sort_key",
]
