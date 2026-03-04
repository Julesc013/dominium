"""CHEM-2 deterministic process-run helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    out: List[str] = []
    for item in values:
        token = str(item or "").strip()
        if token and token not in out:
            out.append(token)
    return sorted(out)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def build_process_run_state(
    *,
    run_id: str,
    reaction_id: str,
    equipment_id: str,
    input_batch_ids: object,
    output_batch_ids: object,
    start_tick: int,
    end_tick: int | None = None,
    progress: int = 0,
    status: str = "active",
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    run_token = str(run_id or "").strip()
    reaction_token = str(reaction_id or "").strip()
    equipment_token = str(equipment_id or "").strip()
    if (not run_token) or (not reaction_token) or (not equipment_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "run_id": run_token,
        "reaction_id": reaction_token,
        "equipment_id": equipment_token,
        "input_batch_ids": _sorted_tokens(input_batch_ids),
        "output_batch_ids": _sorted_tokens(output_batch_ids),
        "start_tick": int(max(0, _as_int(start_tick, 0))),
        "end_tick": (None if end_tick is None else int(max(0, _as_int(end_tick, 0)))),
        "progress": int(max(0, min(1000, _as_int(progress, 0)))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    payload["extensions"]["status"] = str(status or "").strip() or "active"
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_process_run_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("run_id", ""))):
        normalized = build_process_run_state(
            run_id=str(row.get("run_id", "")).strip(),
            reaction_id=str(row.get("reaction_id", "")).strip(),
            equipment_id=str(row.get("equipment_id", "")).strip(),
            input_batch_ids=list(row.get("input_batch_ids") or []),
            output_batch_ids=list(row.get("output_batch_ids") or []),
            start_tick=int(max(0, _as_int(row.get("start_tick", 0), 0))),
            end_tick=(None if row.get("end_tick") is None else int(max(0, _as_int(row.get("end_tick", 0), 0)))),
            progress=int(max(0, min(1000, _as_int(row.get("progress", 0), 0)))),
            status=str(_as_map(row.get("extensions")).get("status", "active")).strip() or "active",
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if normalized:
            out[str(normalized.get("run_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def process_run_rows_by_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_process_run_state_rows(rows)
    return dict(
        (str(row.get("run_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("run_id", "")).strip()
    )


def build_batch_quality_row(
    *,
    batch_id: str,
    quality_grade: str,
    defect_flags: object,
    contamination_tags: object,
    yield_factor: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    batch_token = str(batch_id or "").strip()
    if not batch_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "batch_id": batch_token,
        "quality_grade": str(quality_grade or "").strip() or "grade.C",
        "defect_flags": _sorted_tokens(defect_flags),
        "contamination_tags": _sorted_tokens(contamination_tags),
        "yield_factor": int(max(0, min(1000, _as_int(yield_factor, 0)))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_batch_quality_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("batch_id", ""))):
        normalized = build_batch_quality_row(
            batch_id=str(row.get("batch_id", "")).strip(),
            quality_grade=str(row.get("quality_grade", "")).strip() or "grade.C",
            defect_flags=list(row.get("defect_flags") or []),
            contamination_tags=list(row.get("contamination_tags") or []),
            yield_factor=int(max(0, min(1000, _as_int(row.get("yield_factor", 0), 0)))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if normalized:
            out[str(normalized.get("batch_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def batch_quality_rows_by_batch_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_batch_quality_rows(rows)
    return dict(
        (str(row.get("batch_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("batch_id", "")).strip()
    )


__all__ = [
    "batch_quality_rows_by_batch_id",
    "build_batch_quality_row",
    "build_process_run_state",
    "normalize_batch_quality_rows",
    "normalize_process_run_state_rows",
    "process_run_rows_by_id",
]

