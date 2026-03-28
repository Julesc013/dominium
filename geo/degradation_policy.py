"""Deterministic GEO-10 degradation ordering helpers."""

from __future__ import annotations

from typing import List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_GEO_BUDGET_INVALID = "refusal.geo.budget_invalid"


def _as_bool(value: object, default_value: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    token = str(value or "").strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return bool(default_value)


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    result = dict(payload)
    result["deterministic_fingerprint"] = canonical_sha256(payload)
    return result


def geo_degradation_order_rows() -> List[dict]:
    rows = [
        {
            "rank": 1,
            "action_id": "reduce_projection_resolution",
            "decision_target": "projection_request.resolution_spec",
            "log_targets": ["explain.view_downsampled"],
        },
        {
            "rank": 2,
            "action_id": "reduce_neighbor_radius_noncritical",
            "decision_target": "noncritical_neighbor_radius",
            "log_targets": ["artifact.geo.degradation.decision"],
        },
        {
            "rank": 3,
            "action_id": "reduce_path_expansion_cap",
            "decision_target": "path_request.extensions.max_expansions",
            "log_targets": ["explain.path_refused_budget"],
        },
        {
            "rank": 4,
            "action_id": "defer_derived_view_generation",
            "decision_target": "projected_view_artifact",
            "log_targets": ["artifact.geo.degradation.decision"],
        },
        {
            "rank": 5,
            "action_id": "preserve_canonical_geometry_and_overlay",
            "decision_target": "canonical_geometry_overlay_layers",
            "log_targets": ["artifact.geo.degradation.decision"],
        },
    ]
    return [_with_fingerprint(row) for row in rows]


def _downsample_resolution(*, width: int, height: int, max_cells: int) -> dict:
    current_width = int(max(1, _as_int(width, 1)))
    current_height = int(max(1, _as_int(height, 1)))
    budget = int(max(1, _as_int(max_cells, 1)))
    while (current_width * current_height) > budget and (current_width > 1 or current_height > 1):
        if current_width >= current_height and current_width > 1:
            current_width -= 1
            continue
        if current_height > 1:
            current_height -= 1
            continue
        current_width = max(1, current_width - 1)
    return {
        "width": int(current_width),
        "height": int(current_height),
        "estimated_projected_cells": int(current_width * current_height),
    }


def build_view_downsample_explain_artifact(
    *,
    suite_id: str,
    original_resolution_spec: Mapping[str, object],
    effective_resolution_spec: Mapping[str, object],
    max_projection_cells_per_view: int,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "artifact_id": "artifact.geo.view_downsampled.{}".format(
            canonical_sha256(
                {
                    "suite_id": str(suite_id or "").strip(),
                    "original_resolution_spec": dict(_as_map(original_resolution_spec)),
                    "effective_resolution_spec": dict(_as_map(effective_resolution_spec)),
                    "max_projection_cells_per_view": int(max(1, _as_int(max_projection_cells_per_view, 1))),
                }
            )[:16]
        ),
        "contract_id": "explain.view_downsampled",
        "artifact_type_id": "artifact.explain.geo_view_downsampled",
        "suite_id": str(suite_id or "").strip(),
        "details": {
            "original_resolution_spec": dict(_as_map(original_resolution_spec)),
            "effective_resolution_spec": dict(_as_map(effective_resolution_spec)),
            "max_projection_cells_per_view": int(max(1, _as_int(max_projection_cells_per_view, 1))),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_path_refused_budget_explain_artifact(
    *,
    suite_id: str,
    requested_max_expansions: int,
    effective_max_expansions: int,
    path_result: Mapping[str, object] | None,
) -> dict:
    path_payload = _as_map(path_result)
    result_row = _as_map(path_payload.get("path_result"))
    result_ext = _as_map(result_row.get("extensions"))
    payload = {
        "schema_version": "1.0.0",
        "artifact_id": "artifact.geo.path_refused_budget.{}".format(
            canonical_sha256(
                {
                    "suite_id": str(suite_id or "").strip(),
                    "requested_max_expansions": int(max(1, _as_int(requested_max_expansions, 1))),
                    "effective_max_expansions": int(max(1, _as_int(effective_max_expansions, 1))),
                    "path_result": dict(path_payload),
                }
            )[:16]
        ),
        "contract_id": "explain.path_refused_budget",
        "artifact_type_id": "artifact.explain.geo_path_refused_budget",
        "suite_id": str(suite_id or "").strip(),
        "details": {
            "requested_max_expansions": int(max(1, _as_int(requested_max_expansions, 1))),
            "effective_max_expansions": int(max(1, _as_int(effective_max_expansions, 1))),
            "result": str(path_payload.get("result", "")).strip(),
            "expanded_count": int(max(0, _as_int(path_payload.get("expanded_count", 0), 0))),
            "goal_reached": bool(path_payload.get("goal_reached", False)),
            "partial": bool(result_ext.get("partial", False)),
            "partial_reason": str(result_ext.get("partial_reason", "")).strip(),
            "refusal_code": str(path_payload.get("refusal_code", "")).strip(),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def plan_geo_degradation_actions(
    *,
    suite_id: str,
    current_tick: int,
    budget_payload: Mapping[str, object] | None,
    requested_resolution_spec: Mapping[str, object] | None,
    requested_neighbor_radius: int,
    requested_path_max_expansions: int,
    projected_cell_estimate: int = 0,
    view_type_id: str = "",
) -> dict:
    budget = _as_map(budget_payload)
    requested_resolution = _as_map(requested_resolution_spec)
    width = int(max(1, _as_int(requested_resolution.get("width", 1), 1)))
    height = int(max(1, _as_int(requested_resolution.get("height", 1), 1)))
    max_projection_cells = int(max(1, _as_int(budget.get("max_projection_cells_per_view", width * height), width * height)))
    max_neighbor_radius = int(max(0, _as_int(budget.get("max_neighbor_radius_noncritical", requested_neighbor_radius), requested_neighbor_radius)))
    max_path_expansions = int(max(1, _as_int(budget.get("max_path_expansions", requested_path_max_expansions), requested_path_max_expansions)))
    allow_defer_views = _as_bool(budget.get("allow_defer_derived_views", False), False)
    estimated_cells = int(max(1, _as_int(projected_cell_estimate or (width * height), width * height)))

    effective_resolution = {
        "width": int(width),
        "height": int(height),
    }
    effective_neighbor_radius = int(max(0, requested_neighbor_radius))
    effective_path_cap = int(max(1, requested_path_max_expansions))
    defer_derived_views = False
    applied_steps: List[int] = []
    decision_log_rows: List[dict] = []
    explain_artifacts: List[dict] = []

    def _append_step(rank: int, action_id: str, status: str, reason_code: str, details: Mapping[str, object]) -> None:
        decision_log_rows.append(
            _with_fingerprint(
                {
                    "decision_id": "decision.geo.degrade.{}".format(
                        canonical_sha256(
                            {
                                "suite_id": str(suite_id or "").strip(),
                                "current_tick": int(max(0, _as_int(current_tick, 0))),
                                "rank": int(rank),
                                "action_id": str(action_id),
                                "details": dict(_as_map(details)),
                            }
                        )[:16]
                    ),
                    "suite_id": str(suite_id or "").strip(),
                    "current_tick": int(max(0, _as_int(current_tick, 0))),
                    "rank": int(rank),
                    "action_id": str(action_id),
                    "status": str(status),
                    "reason_code": str(reason_code),
                    "details": dict(_as_map(details)),
                }
            )
        )

    if estimated_cells > max_projection_cells:
        effective_resolution = _downsample_resolution(width=width, height=height, max_cells=max_projection_cells)
        applied_steps.append(1)
        explain_artifacts.append(
            build_view_downsample_explain_artifact(
                suite_id=suite_id,
                original_resolution_spec=requested_resolution,
                effective_resolution_spec=effective_resolution,
                max_projection_cells_per_view=max_projection_cells,
            )
        )
        _append_step(
            1,
            "reduce_projection_resolution",
            "applied",
            "degrade.geo.view_downsampled",
            {
                "view_type_id": str(view_type_id or "").strip(),
                "original_resolution_spec": requested_resolution,
                "effective_resolution_spec": effective_resolution,
                "estimated_projected_cells": int(estimated_cells),
                "max_projection_cells_per_view": int(max_projection_cells),
            },
        )
    else:
        _append_step(
            1,
            "reduce_projection_resolution",
            "noop",
            "degrade.geo.view_within_budget",
            {
                "estimated_projected_cells": int(estimated_cells),
                "max_projection_cells_per_view": int(max_projection_cells),
            },
        )

    if requested_neighbor_radius > max_neighbor_radius:
        effective_neighbor_radius = int(max_neighbor_radius)
        applied_steps.append(2)
        _append_step(
            2,
            "reduce_neighbor_radius_noncritical",
            "applied",
            "degrade.geo.neighbor_radius",
            {
                "requested_neighbor_radius": int(requested_neighbor_radius),
                "effective_neighbor_radius": int(effective_neighbor_radius),
            },
        )
    else:
        _append_step(
            2,
            "reduce_neighbor_radius_noncritical",
            "noop",
            "degrade.geo.neighbor_radius_within_budget",
            {
                "requested_neighbor_radius": int(requested_neighbor_radius),
                "effective_neighbor_radius": int(effective_neighbor_radius),
            },
        )

    if requested_path_max_expansions > max_path_expansions:
        effective_path_cap = int(max_path_expansions)
        applied_steps.append(3)
        _append_step(
            3,
            "reduce_path_expansion_cap",
            "applied",
            "degrade.geo.path_budget",
            {
                "requested_max_expansions": int(requested_path_max_expansions),
                "effective_max_expansions": int(effective_path_cap),
            },
        )
    else:
        _append_step(
            3,
            "reduce_path_expansion_cap",
            "noop",
            "degrade.geo.path_within_budget",
            {
                "requested_max_expansions": int(requested_path_max_expansions),
                "effective_max_expansions": int(effective_path_cap),
            },
        )

    if (effective_resolution["width"] * effective_resolution["height"]) > max_projection_cells and allow_defer_views:
        defer_derived_views = True
        applied_steps.append(4)
        _append_step(
            4,
            "defer_derived_view_generation",
            "applied",
            "degrade.geo.defer_view",
            {
                "effective_resolution_spec": dict(effective_resolution),
                "allow_defer_derived_views": bool(allow_defer_views),
            },
        )
    else:
        _append_step(
            4,
            "defer_derived_view_generation",
            "noop",
            "degrade.geo.defer_not_required",
            {
                "effective_resolution_spec": dict(effective_resolution),
                "allow_defer_derived_views": bool(allow_defer_views),
            },
        )

    _append_step(
        5,
        "preserve_canonical_geometry_and_overlay",
        "affirmed",
        "degrade.geo.canonical_preserved",
        {
            "skip_geometry_edit_events": False,
            "skip_overlay_patches": False,
        },
    )

    payload = {
        "schema_version": "1.0.0",
        "suite_id": str(suite_id or "").strip(),
        "current_tick": int(max(0, _as_int(current_tick, 0))),
        "effective_resolution_spec": dict(effective_resolution),
        "effective_neighbor_radius_noncritical": int(effective_neighbor_radius),
        "effective_path_max_expansions": int(effective_path_cap),
        "defer_derived_views": bool(defer_derived_views),
        "applied_steps": list(applied_steps),
        "decision_log_rows": [
            dict(row)
            for row in sorted(
                (dict(row) for row in decision_log_rows if isinstance(row, Mapping)),
                key=lambda row: (int(_as_int(row.get("rank", 0), 0)), str(row.get("decision_id", ""))),
            )
        ],
        "explain_artifacts": [dict(row) for row in explain_artifacts],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def finalize_geo_degradation_report(
    plan: Mapping[str, object] | None,
    *,
    path_result: Mapping[str, object] | None = None,
) -> dict:
    payload = dict(_as_map(plan))
    decision_rows = [dict(row) for row in list(payload.get("decision_log_rows") or []) if isinstance(row, Mapping)]
    explain_artifacts = [dict(row) for row in list(payload.get("explain_artifacts") or []) if isinstance(row, Mapping)]
    step3 = next((row for row in decision_rows if int(_as_int(row.get("rank", 0), 0)) == 3), {})
    step3_status = str(_as_map(step3).get("status", "")).strip()
    path_payload = _as_map(path_result)
    if step3_status == "applied" and str(path_payload.get("result", "")).strip() in {"partial", "refused"}:
        explain_artifacts.append(
            build_path_refused_budget_explain_artifact(
                suite_id=str(payload.get("suite_id", "")).strip(),
                requested_max_expansions=int(
                    _as_int(_as_map(_as_map(step3).get("details")).get("requested_max_expansions", 1), 1)
                ),
                effective_max_expansions=int(
                    _as_int(_as_map(_as_map(step3).get("details")).get("effective_max_expansions", 1), 1)
                ),
                path_result=path_payload,
            )
        )
    payload["explain_artifacts"] = [
        dict(row)
        for row in sorted(
            (dict(row) for row in explain_artifacts if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("contract_id", "")), str(row.get("artifact_id", ""))),
        )
    ]
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "REFUSAL_GEO_BUDGET_INVALID",
    "build_path_refused_budget_explain_artifact",
    "build_view_downsample_explain_artifact",
    "finalize_geo_degradation_report",
    "geo_degradation_order_rows",
    "plan_geo_degradation_actions",
]
