"""Deterministic EMB-1 terrain edit tool planners over GEO-7 processes only."""

from __future__ import annotations

from typing import List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from .toolbelt_engine import evaluate_tool_access


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _resolve_target_cell_keys(
    *,
    selection: Mapping[str, object] | None = None,
    target_cell_keys: object = None,
    path_stub: object = None,
) -> List[dict]:
    rows: List[dict] = []
    for raw in list(target_cell_keys or []):
        row = _as_map(raw)
        if row:
            rows.append(dict(row))
    for raw in list(path_stub or []):
        row = _as_map(raw)
        if row:
            rows.append(dict(row))
    if not rows:
        for key in ("geo_cell_key", "tile_cell_key", "target_cell_key", "cell_key"):
            row = _as_map(_as_map(selection).get(key))
            if row:
                rows.append(dict(row))
                break
    normalized = {}
    for row in rows:
        normalized[canonical_sha256(row)] = dict(row)
    return [dict(normalized[key]) for key in sorted(normalized.keys())]


def _refusal(reason_code: str, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "reason_code": str(reason_code or "").strip(),
        "message": str(message or "").strip(),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _task_payload(
    *,
    task_kind: str,
    subject_id: str,
    process_id: str,
    target_cell_keys: object,
    volume_amount: int,
    material_id: str = "",
    geometry_edit_policy_id: str = "geo.edit.default",
    selection: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    inputs = {
        "operator_subject_id": str(subject_id or "").strip() or "subject.player",
        "target_cell_keys": [dict(row) for row in list(target_cell_keys or []) if isinstance(row, Mapping)],
        "volume_amount": int(max(1, _as_int(volume_amount, 1))),
        "geometry_edit_policy_id": str(geometry_edit_policy_id or "").strip() or "geo.edit.default",
    }
    if material_id:
        inputs["material_id"] = str(material_id).strip()
        inputs["material_in"] = {
            "material_id": str(material_id).strip(),
            "quantity_mass_raw": int(max(1, _as_int(volume_amount, 1))),
            "batch_ids": [],
        }
    payload = {
        "result": "complete",
        "task_id": "task.{}.{}".format(
            str(task_kind or "").strip(),
            canonical_sha256(
                {
                    "task_kind": str(task_kind or "").strip(),
                    "subject_id": str(subject_id or "").strip(),
                    "target_cell_keys": [dict(row) for row in list(target_cell_keys or []) if isinstance(row, Mapping)],
                    "volume_amount": int(max(1, _as_int(volume_amount, 1))),
                    "material_id": str(material_id or "").strip(),
                }
            )[:16],
        ),
        "task_kind": str(task_kind or "").strip(),
        "selection": _as_map(selection),
        "process_sequence": [{"process_id": str(process_id or "").strip(), "inputs": inputs}],
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_mine_at_cursor_task(
    *,
    authority_context: Mapping[str, object] | None,
    subject_id: str,
    selection: Mapping[str, object] | None,
    volume_amount: int = 1,
    target_cell_keys: object = None,
    geometry_edit_policy_id: str = "geo.edit.default",
) -> dict:
    access_result = evaluate_tool_access(tool_id="tool.terrain_edit", authority_context=authority_context)
    if str(access_result.get("result", "")).strip() != "complete":
        return dict(access_result)
    resolved_targets = _resolve_target_cell_keys(selection=selection, target_cell_keys=target_cell_keys)
    if not resolved_targets:
        return _refusal("refusal.tool.target_missing", "terrain edit requires a deterministic target cell selection")
    return _task_payload(
        task_kind="task.mine_at_cursor",
        subject_id=subject_id,
        process_id="process.geometry_remove",
        target_cell_keys=resolved_targets,
        volume_amount=volume_amount,
        geometry_edit_policy_id=geometry_edit_policy_id,
        selection=selection,
        extensions={"source": "EMB1-3", "tool_id": "tool.terrain_edit", "operation": "mine"},
    )


def build_fill_at_cursor_task(
    *,
    authority_context: Mapping[str, object] | None,
    subject_id: str,
    selection: Mapping[str, object] | None,
    volume_amount: int = 1,
    material_id: str = "material.soil_fill",
    target_cell_keys: object = None,
    geometry_edit_policy_id: str = "geo.edit.default",
) -> dict:
    access_result = evaluate_tool_access(tool_id="tool.terrain_edit", authority_context=authority_context)
    if str(access_result.get("result", "")).strip() != "complete":
        return dict(access_result)
    resolved_targets = _resolve_target_cell_keys(selection=selection, target_cell_keys=target_cell_keys)
    if not resolved_targets:
        return _refusal("refusal.tool.target_missing", "terrain fill requires a deterministic target cell selection")
    return _task_payload(
        task_kind="task.fill_at_cursor",
        subject_id=subject_id,
        process_id="process.geometry_add",
        target_cell_keys=resolved_targets,
        volume_amount=volume_amount,
        material_id=str(material_id or "").strip() or "material.soil_fill",
        geometry_edit_policy_id=geometry_edit_policy_id,
        selection=selection,
        extensions={"source": "EMB1-3", "tool_id": "tool.terrain_edit", "operation": "fill"},
    )


def build_cut_trench_task(
    *,
    authority_context: Mapping[str, object] | None,
    subject_id: str,
    path_stub: object,
    volume_amount: int = 1,
    selection: Mapping[str, object] | None = None,
    geometry_edit_policy_id: str = "geo.edit.default",
) -> dict:
    access_result = evaluate_tool_access(tool_id="tool.terrain_edit", authority_context=authority_context)
    if str(access_result.get("result", "")).strip() != "complete":
        return dict(access_result)
    resolved_targets = _resolve_target_cell_keys(selection=selection, path_stub=path_stub)
    if not resolved_targets:
        return _refusal("refusal.tool.target_missing", "terrain cut requires a deterministic path_stub or selected cell path")
    return _task_payload(
        task_kind="task.cut_trench",
        subject_id=subject_id,
        process_id="process.geometry_cut",
        target_cell_keys=resolved_targets,
        volume_amount=volume_amount,
        geometry_edit_policy_id=geometry_edit_policy_id,
        selection=selection,
        extensions={"source": "EMB1-3", "tool_id": "tool.terrain_edit", "operation": "cut"},
    )


__all__ = [
    "build_cut_trench_task",
    "build_fill_at_cursor_task",
    "build_mine_at_cursor_task",
]
