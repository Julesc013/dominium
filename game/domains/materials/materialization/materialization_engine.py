"""Deterministic MAT-7 macro/micro materialization helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from control.fidelity import (
    DEFAULT_FIDELITY_POLICY_ID,
    REFUSAL_CTRL_FIDELITY_DENIED,
    RANK_FAIR_POLICY_ID,
    arbitrate_fidelity_requests,
    build_fidelity_request,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_MATERIALIZATION_BUDGET_EXCEEDED = "refusal.materialization.budget_exceeded"
REFUSAL_TRANSITION_INVARIANT_VIOLATION = "refusal.transition.invariant_violation"


class MaterializationError(ValueError):
    """Deterministic materialization refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _distribution_rows_for_structure(rows: object, structure_id: str) -> List[dict]:
    token = str(structure_id).strip()
    out: List[dict] = []
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("ag_node_id", ""))):
        if str(row.get("structure_id", "")).strip() != token:
            continue
        out.append(dict(row))
    return out


def _materialization_state_key(structure_id: str, roi_id: str) -> str:
    return "{}::{}".format(str(structure_id).strip(), str(roi_id).strip())


def _materialization_state_rows_by_key(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("structure_id", "")) + "::" + str(item.get("roi_id", ""))):
        key = _materialization_state_key(str(row.get("structure_id", "")), str(row.get("roi_id", "")))
        if "::" in key:
            out[key] = normalize_materialization_state_row(row)
    return out


def _micro_rows_by_structure_roi(rows: object, structure_id: str, roi_id: str) -> List[dict]:
    structure_token = str(structure_id).strip()
    roi_token = str(roi_id).strip()
    out: List[dict] = []
    if not isinstance(rows, list):
        return out
    for row in sorted(
        (item for item in rows if isinstance(item, dict)),
        key=lambda item: (
            str(item.get("ag_node_id", "")),
            str(item.get("batch_id", "")),
            str(item.get("micro_part_id", "")),
        ),
    ):
        if str(row.get("parent_structure_id", "")).strip() != structure_token:
            continue
        ext = dict(row.get("extensions") or {})
        if str(ext.get("roi_id", "")).strip() != roi_token:
            continue
        out.append(normalize_micro_part_instance_row(row))
    return out


def _stable_materialization_seed(
    *,
    parent_structure_id: str,
    ag_node_id: str,
    batch_id: str,
    index: int,
    tick_bucket: int,
) -> str:
    return canonical_sha256(
        {
            "stream": "materialization",
            "parent_structure_id": str(parent_structure_id),
            "ag_node_id": str(ag_node_id),
            "batch_id": str(batch_id),
            "index": int(max(0, int(index))),
            "tick_bucket": int(max(0, int(tick_bucket))),
        }
    )


def _micro_part_id(parent_structure_id: str, ag_node_id: str, batch_id: str, index: int) -> str:
    return "micro.part.{}".format(
        canonical_sha256(
            {
                "parent_structure_id": str(parent_structure_id),
                "ag_node_id": str(ag_node_id),
                "batch_id": str(batch_id),
                "index": int(max(0, int(index))),
            }
        )[:24]
    )


def normalize_distribution_aggregate_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    structure_id = str(payload.get("structure_id", "")).strip()
    ag_node_id = str(payload.get("ag_node_id", "")).strip()
    if not structure_id or not ag_node_id:
        raise MaterializationError(
            "refusal.materialization.invalid_structure",
            "distribution aggregate row missing structure_id or ag_node_id",
            {"structure_id": structure_id, "ag_node_id": ag_node_id},
        )
    defect_vector = dict(
        (str(key).strip(), max(0, _as_int(value, 0)))
        for key, value in sorted((dict(payload.get("defect_distribution_vector") or {})).items(), key=lambda item: str(item[0]))
        if str(key).strip()
    )
    wear_vector = dict(
        (str(key).strip(), max(0, _as_int(value, 0)))
        for key, value in sorted((dict(payload.get("wear_distribution_vector") or {})).items(), key=lambda item: str(item[0]))
        if str(key).strip()
    )
    return {
        "schema_version": "1.0.0",
        "structure_id": structure_id,
        "ag_node_id": ag_node_id,
        "total_mass": max(0, _as_int(payload.get("total_mass", 0), 0)),
        "defect_distribution_vector": defect_vector,
        "wear_distribution_vector": wear_vector,
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def normalize_micro_part_instance_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    micro_part_id = str(payload.get("micro_part_id", "")).strip()
    parent_structure_id = str(payload.get("parent_structure_id", "")).strip()
    ag_node_id = str(payload.get("ag_node_id", "")).strip()
    batch_id = str(payload.get("batch_id", "")).strip()
    material_id = str(payload.get("material_id", "")).strip()
    if not micro_part_id or not parent_structure_id or not ag_node_id or not batch_id or not material_id:
        raise MaterializationError(
            "refusal.materialization.invalid_structure",
            "micro part row missing required identity fields",
            {
                "micro_part_id": micro_part_id,
                "parent_structure_id": parent_structure_id,
                "ag_node_id": ag_node_id,
            },
        )
    return {
        "schema_version": "1.0.0",
        "micro_part_id": micro_part_id,
        "parent_structure_id": parent_structure_id,
        "ag_node_id": ag_node_id,
        "batch_id": batch_id,
        "material_id": material_id,
        "mass": max(0, _as_int(payload.get("mass", 0), 0)),
        "defect_flags": _sorted_unique_strings(list(payload.get("defect_flags") or [])),
        "wear_state": dict(payload.get("wear_state") or {}) if isinstance(payload.get("wear_state"), dict) else {},
        "transform": dict(payload.get("transform") or {}) if isinstance(payload.get("transform"), dict) else {},
        "deterministic_seed": str(payload.get("deterministic_seed", "")).strip(),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def normalize_materialization_state_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    structure_id = str(payload.get("structure_id", "")).strip()
    roi_id = str(payload.get("roi_id", "")).strip()
    if not structure_id or not roi_id:
        raise MaterializationError(
            "refusal.materialization.invalid_structure",
            "materialization state missing structure_id or roi_id",
            {"structure_id": structure_id, "roi_id": roi_id},
        )
    return {
        "schema_version": "1.0.0",
        "structure_id": structure_id,
        "roi_id": roi_id,
        "materialized_nodes": _sorted_unique_strings(list(payload.get("materialized_nodes") or [])),
        "materialized_part_ids": _sorted_unique_strings(list(payload.get("materialized_part_ids") or [])),
        "last_materialization_tick": max(0, _as_int(payload.get("last_materialization_tick", 0), 0)),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def normalize_reenactment_descriptor_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    structure_id = str(payload.get("structure_id", "")).strip()
    tick_range = dict(payload.get("tick_range") or {})
    if not structure_id:
        raise MaterializationError(
            "refusal.materialization.invalid_structure",
            "reenactment descriptor missing structure_id",
            {},
        )
    tick_start = max(0, _as_int(tick_range.get("tick_start", 0), 0))
    tick_end = max(tick_start, _as_int(tick_range.get("tick_end", tick_start), tick_start))
    return {
        "schema_version": "1.0.0",
        "structure_id": structure_id,
        "tick_range": {
            "tick_start": int(tick_start),
            "tick_end": int(tick_end),
        },
        "ag_nodes_involved": _sorted_unique_strings(list(payload.get("ag_nodes_involved") or [])),
        "batch_ids": _sorted_unique_strings(list(payload.get("batch_ids") or [])),
        "seed_reference": str(payload.get("seed_reference", "")).strip(),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def _mass_parts(total_mass: int, part_count: int) -> List[int]:
    total = max(0, int(total_mass))
    count = max(0, int(part_count))
    if count <= 0:
        return []
    base = int(total // count)
    remainder = int(total % count)
    out = []
    for idx in range(count):
        out.append(int(base + (1 if idx < remainder else 0)))
    return out


def _pick_weighted_key(weighted: Mapping[str, object], seed_hex: str) -> str:
    rows = [
        (str(key).strip(), max(0, _as_int(value, 0)))
        for key, value in sorted((dict(weighted or {})).items(), key=lambda item: str(item[0]))
        if str(key).strip()
    ]
    rows = [(key, value) for key, value in rows if value > 0]
    if not rows:
        return ""
    total = int(sum(value for _, value in rows))
    marker = int(seed_hex[:8], 16) % max(1, total)
    running = 0
    for key, value in rows:
        running += int(value)
        if marker < running:
            return key
    return rows[-1][0]


def _wear_sample(wear_vector: Mapping[str, object], part_count: int, index: int) -> Dict[str, int]:
    count = max(1, int(part_count))
    idx = max(0, int(index))
    out: Dict[str, int] = {}
    for key, value in sorted((dict(wear_vector or {})).items(), key=lambda item: str(item[0])):
        mode_id = str(key).strip()
        if not mode_id:
            continue
        total = max(0, _as_int(value, 0))
        base = total // count
        remainder = total % count
        out[mode_id] = int(base + (1 if idx < remainder else 0))
    return out


def _part_transform(parent_structure_id: str, ag_node_id: str, index: int) -> dict:
    seed = canonical_sha256(
        {
            "parent_structure_id": str(parent_structure_id),
            "ag_node_id": str(ag_node_id),
            "index": int(max(0, int(index))),
            "shape": "materialization_transform",
        }
    )
    x = int(int(seed[0:4], 16) % 4000) - 2000
    y = int(int(seed[4:8], 16) % 4000) - 2000
    z = int(int(seed[8:12], 16) % 4000) - 2000
    yaw = int(int(seed[12:16], 16) % 360000)
    pitch = int(int(seed[16:20], 16) % 360000)
    roll = int(int(seed[20:24], 16) % 360000)
    return {
        "position_mm": {"x": int(x), "y": int(y), "z": int(z)},
        "orientation_mdeg": {"yaw": int(yaw), "pitch": int(pitch), "roll": int(roll)},
        "scale_permille": 1000,
    }


def materialize_structure_roi(
    *,
    structure_row: Mapping[str, object],
    roi_id: str,
    current_tick: int,
    max_micro_parts: int,
    distribution_aggregates: object,
    existing_micro_parts: object,
    existing_materialization_states: object,
    strict_budget: bool = False,
    roi_node_ids: List[object] | None = None,
    law_profile: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    policy_context: Mapping[str, object] | None = None,
) -> dict:
    structure_id = str((dict(structure_row or {})).get("instance_id", "")).strip()
    if not structure_id:
        raise MaterializationError(
            "refusal.materialization.invalid_structure",
            "materialization requires installed structure instance_id",
            {},
        )
    roi_token = str(roi_id).strip()
    if not roi_token:
        raise MaterializationError(
            "refusal.materialization.invalid_structure",
            "materialization requires roi_id",
            {"structure_id": structure_id},
        )
    budget = max(0, int(max_micro_parts))
    aggregates = _distribution_rows_for_structure(distribution_aggregates, structure_id)
    if not aggregates:
        return {
            "micro_parts": [],
            "materialization_state": normalize_materialization_state_row(
                {
                    "structure_id": structure_id,
                    "roi_id": roi_token,
                    "materialized_nodes": [],
                    "materialized_part_ids": [],
                    "last_materialization_tick": int(max(0, int(current_tick))),
                    "extensions": {"truncated": False, "requested_parts": 0, "materialized_parts": 0},
                }
            ),
            "source_mass_total": 0,
            "micro_mass_total": 0,
            "invariant_delta": 0,
            "truncated": False,
            "truncated_count": 0,
            "remaining_micro_parts": [
                normalize_micro_part_instance_row(row)
                for row in list(existing_micro_parts or [])
                if isinstance(row, dict)
                and str(row.get("parent_structure_id", "")).strip() != structure_id
            ],
            "remaining_materialization_states": [normalize_materialization_state_row(row) for row in list(existing_materialization_states or []) if isinstance(row, dict)],
            "reenactment_descriptor": normalize_reenactment_descriptor_row(
                {
                    "structure_id": structure_id,
                    "tick_range": {"tick_start": int(max(0, int(current_tick))), "tick_end": int(max(0, int(current_tick)))},
                    "ag_nodes_involved": [],
                    "batch_ids": [],
                    "seed_reference": canonical_sha256({"stream": "materialization", "structure_id": structure_id, "roi_id": roi_token}),
                    "extensions": {"roi_id": roi_token, "materialized_part_count": 0},
                }
            ),
        }

    installed_nodes = set(_sorted_unique_strings(list((dict(structure_row or {})).get("installed_node_states") or [])))
    allowed_nodes = set(_sorted_unique_strings(list(roi_node_ids or [])))
    candidates: List[dict] = []
    source_mass_total = 0
    for row in sorted((normalize_distribution_aggregate_row(item) for item in aggregates), key=lambda item: str(item.get("ag_node_id", ""))):
        ag_node_id = str(row.get("ag_node_id", "")).strip()
        if installed_nodes and ag_node_id not in installed_nodes:
            continue
        if allowed_nodes and ag_node_id not in allowed_nodes:
            continue
        total_mass = max(0, _as_int(row.get("total_mass", 0), 0))
        source_mass_total += int(total_mass)
        ext = dict(row.get("extensions") or {})
        part_count = max(0, _as_int(ext.get("part_count", 0), 0))
        if part_count <= 0:
            part_count = 1 if total_mass > 0 else 0
        batch_id = str(ext.get("batch_id", "")).strip() or "batch.materialization.{}".format(canonical_sha256({"structure_id": structure_id, "ag_node_id": ag_node_id})[:16])
        material_id = str(ext.get("material_id", "")).strip() or "material.unknown"
        for index, part_mass in enumerate(_mass_parts(total_mass=total_mass, part_count=part_count)):
            candidates.append(
                {
                    "ag_node_id": ag_node_id,
                    "batch_id": batch_id,
                    "material_id": material_id,
                    "index": int(index),
                    "part_count": int(part_count),
                    "mass": int(part_mass),
                    "defect_distribution_vector": dict(row.get("defect_distribution_vector") or {}),
                    "wear_distribution_vector": dict(row.get("wear_distribution_vector") or {}),
                }
            )

    candidates = sorted(
        candidates,
        key=lambda item: (
            str(item.get("ag_node_id", "")),
            str(item.get("batch_id", "")),
            int(_as_int(item.get("index", 0), 0)),
        ),
    )
    desired_count = len(candidates)
    truncated = False
    truncated_count = 0
    authority = dict(authority_context or {})
    law = dict(law_profile or {})
    policy = dict(policy_context or {})
    requester_subject_id = (
        str(authority.get("subject_id", "")).strip()
        or str(authority.get("agent_id", "")).strip()
        or str(authority.get("peer_id", "")).strip()
        or "subject.system"
    )
    connected_subject_ids = _sorted_unique_strings(list(policy.get("connected_peer_ids") or []))
    if requester_subject_id not in connected_subject_ids:
        connected_subject_ids.append(requester_subject_id)
    fidelity_policy_id = (
        str(policy.get("fidelity_policy_id", "")).strip()
        or (RANK_FAIR_POLICY_ID if "rank" in str(policy.get("server_profile_id", "")).strip().lower() else DEFAULT_FIDELITY_POLICY_ID)
    )
    fidelity_request = build_fidelity_request(
        requester_subject_id=requester_subject_id,
        target_kind="structure",
        target_id=str(structure_id),
        requested_level="micro",
        cost_estimate=int(desired_count),
        priority=_as_int((dict(policy.get("extensions") or {})).get("materialization_priority", 0), 0),
        created_tick=int(max(0, int(current_tick))),
        extensions={
            "allowed_levels": ["micro", "meso", "macro"],
            "fidelity_cost_by_level": {
                "micro": int(max(1, int(desired_count))),
                "meso": int(max(1, int(desired_count // 2))),
                "macro": 1,
            },
            "micro_allowed": True,
            "micro_available": True,
            "strict_budget": bool(strict_budget),
            "law_profile_id": str(law.get("law_profile_id", "law.unknown")).strip() or "law.unknown",
        },
    )
    materialization_arbitration = arbitrate_fidelity_requests(
        fidelity_requests=[dict(fidelity_request)],
        rs5_budget_state={
            "tick": int(max(0, int(current_tick))),
            "envelope_id": str(policy.get("budget_envelope_id", "")).strip() or "budget.unknown",
            "fidelity_policy_id": str(fidelity_policy_id),
            "max_cost_units_per_tick": int(max(0, int(budget))),
            "runtime_budget_state": dict(policy.get("materialization_runtime_budget_state") or {}),
            "fairness_state": {
                "connected_subject_ids": list(connected_subject_ids),
                "used_by_tick_subject": dict((dict(policy.get("materialization_arbitration_state") or {})).get("used_by_tick_peer") or {}),
            },
            "connected_subject_ids": list(connected_subject_ids),
        },
        server_profile={"server_profile_id": str(policy.get("server_profile_id", "")).strip() or "server.profile.unknown"},
        fidelity_policy={"policy_id": str(fidelity_policy_id)},
    )
    materialization_allocations = [
        dict(row) for row in list(materialization_arbitration.get("fidelity_allocations") or []) if isinstance(row, dict)
    ]
    materialization_allocation = dict(materialization_allocations[0] if materialization_allocations else {})
    allocation_ext = dict(materialization_allocation.get("extensions") or {})
    refusal_codes = _sorted_unique_strings(list(allocation_ext.get("refusal_codes") or []))
    allocation_cost = int(max(0, _as_int(materialization_allocation.get("cost_allocated", 0), 0)))
    if REFUSAL_CTRL_FIDELITY_DENIED in set(refusal_codes) and bool(strict_budget):
        raise MaterializationError(
            REFUSAL_MATERIALIZATION_BUDGET_EXCEEDED,
            "materialization budget exceeded",
            {
                "structure_id": structure_id,
                "roi_id": roi_token,
                "requested_parts": int(desired_count),
                "max_micro_parts": int(budget),
                "fidelity_request_id": str(fidelity_request.get("fidelity_request_id", "")),
            },
        )
    effective_budget = int(min(max(0, int(budget)), int(allocation_cost)))
    if desired_count > effective_budget:
        candidates = list(candidates[:effective_budget])
        truncated = True
        truncated_count = int(desired_count - len(candidates))

    micro_rows: List[dict] = []
    for candidate in candidates:
        ag_node_id = str(candidate.get("ag_node_id", ""))
        batch_id = str(candidate.get("batch_id", ""))
        index = int(_as_int(candidate.get("index", 0), 0))
        seed = _stable_materialization_seed(
            parent_structure_id=structure_id,
            ag_node_id=ag_node_id,
            batch_id=batch_id,
            index=index,
            tick_bucket=int(max(0, int(current_tick))),
        )
        selected_defect = _pick_weighted_key(candidate.get("defect_distribution_vector") or {}, seed)
        defect_flags = [selected_defect] if selected_defect else []
        micro_rows.append(
            normalize_micro_part_instance_row(
                {
                    "micro_part_id": _micro_part_id(structure_id, ag_node_id, batch_id, index),
                    "parent_structure_id": structure_id,
                    "ag_node_id": ag_node_id,
                    "batch_id": batch_id,
                    "material_id": str(candidate.get("material_id", "")),
                    "mass": int(max(0, _as_int(candidate.get("mass", 0), 0))),
                    "defect_flags": list(defect_flags),
                    "wear_state": _wear_sample(
                        candidate.get("wear_distribution_vector") or {},
                        part_count=max(1, _as_int(candidate.get("part_count", 1), 1)),
                        index=index,
                    ),
                    "transform": _part_transform(structure_id, ag_node_id, index),
                    "deterministic_seed": seed,
                    "extensions": {"roi_id": roi_token},
                }
            )
        )
    micro_rows = sorted(
        micro_rows,
        key=lambda item: (
            str(item.get("ag_node_id", "")),
            str(item.get("batch_id", "")),
            str(item.get("micro_part_id", "")),
        ),
    )
    micro_mass_total = int(sum(max(0, _as_int(row.get("mass", 0), 0)) for row in micro_rows))
    invariant_delta = int(source_mass_total - micro_mass_total)

    state_row = normalize_materialization_state_row(
        {
            "structure_id": structure_id,
            "roi_id": roi_token,
            "materialized_nodes": _sorted_unique_strings([str(row.get("ag_node_id", "")) for row in micro_rows]),
            "materialized_part_ids": _sorted_unique_strings([str(row.get("micro_part_id", "")) for row in micro_rows]),
            "last_materialization_tick": int(max(0, int(current_tick))),
            "extensions": {
                "truncated": bool(truncated),
                "requested_parts": int(desired_count),
                "materialized_parts": int(len(micro_rows)),
                "truncated_count": int(truncated_count),
                "resolved_fidelity": str(materialization_allocation.get("resolved_level", "macro")).strip() or "macro",
                "fidelity_request": dict(fidelity_request),
                "fidelity_allocation": dict(materialization_allocation),
                "fidelity_policy_id": str(materialization_arbitration.get("policy_id", fidelity_policy_id)),
                "fidelity_runtime_budget_state": dict(materialization_arbitration.get("runtime_budget_state") or {}),
                "fidelity_fairness_state": dict(materialization_arbitration.get("fairness_state") or {}),
                # Backward-compatible alias retained while callers migrate from CTRL-3 terminology.
                "negotiation_result": dict(materialization_arbitration),
            },
        }
    )
    descriptors = normalize_reenactment_descriptor_row(
        {
            "structure_id": structure_id,
            "tick_range": {"tick_start": int(max(0, int(current_tick))), "tick_end": int(max(0, int(current_tick)))},
            "ag_nodes_involved": list(state_row.get("materialized_nodes") or []),
            "batch_ids": _sorted_unique_strings([str(row.get("batch_id", "")) for row in micro_rows]),
            "seed_reference": canonical_sha256(
                {
                    "stream": "materialization",
                    "structure_id": structure_id,
                    "roi_id": roi_token,
                    "tick": int(max(0, int(current_tick))),
                    "part_ids": list(state_row.get("materialized_part_ids") or []),
                }
            ),
            "extensions": {"roi_id": roi_token, "materialized_part_count": int(len(micro_rows))},
        }
    )
    remaining_micro_parts = [
        normalize_micro_part_instance_row(row)
        for row in list(existing_micro_parts or [])
        if isinstance(row, dict)
        and (
            str(row.get("parent_structure_id", "")).strip() != structure_id
            or str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() != roi_token
        )
    ]
    remaining_states = [
        normalize_materialization_state_row(row)
        for row in list(existing_materialization_states or [])
        if isinstance(row, dict)
        and _materialization_state_key(str(row.get("structure_id", "")), str(row.get("roi_id", "")))
        != _materialization_state_key(structure_id, roi_token)
    ]
    return {
        "micro_parts": list(micro_rows),
        "materialization_state": state_row,
        "source_mass_total": int(source_mass_total),
        "micro_mass_total": int(micro_mass_total),
        "invariant_delta": int(invariant_delta),
        "truncated": bool(truncated),
        "truncated_count": int(truncated_count),
        "fidelity_request": dict(fidelity_request),
        "fidelity_allocation": dict(materialization_allocation),
        "fidelity_arbitration": dict(materialization_arbitration),
        "negotiation_result": dict(materialization_arbitration),
        "remaining_micro_parts": list(remaining_micro_parts),
        "remaining_materialization_states": list(remaining_states),
        "reenactment_descriptor": descriptors,
    }


def dematerialize_structure_roi(
    *,
    structure_id: str,
    roi_id: str,
    current_tick: int,
    existing_micro_parts: object,
    existing_distribution_aggregates: object,
    existing_materialization_states: object,
) -> dict:
    structure_token = str(structure_id).strip()
    roi_token = str(roi_id).strip()
    if not structure_token or not roi_token:
        raise MaterializationError(
            "refusal.materialization.invalid_structure",
            "dematerialization requires structure_id and roi_id",
            {"structure_id": structure_token, "roi_id": roi_token},
        )
    collapse_rows = _micro_rows_by_structure_roi(existing_micro_parts, structure_token, roi_token)
    aggregate_by_node: Dict[str, dict] = {}
    for row in collapse_rows:
        ag_node_id = str(row.get("ag_node_id", "")).strip()
        aggregate = dict(aggregate_by_node.get(ag_node_id) or {})
        if not aggregate:
            aggregate = {
                "schema_version": "1.0.0",
                "structure_id": structure_token,
                "ag_node_id": ag_node_id,
                "total_mass": 0,
                "defect_distribution_vector": {},
                "wear_distribution_vector": {},
                "extensions": {
                    "batch_id": str(row.get("batch_id", "")).strip(),
                    "material_id": str(row.get("material_id", "")).strip(),
                    "part_count": 0,
                    "last_dematerialization_tick": int(max(0, int(current_tick))),
                    "source_roi_id": roi_token,
                },
            }
        mass = max(0, _as_int(row.get("mass", 0), 0))
        aggregate["total_mass"] = int(_as_int(aggregate.get("total_mass", 0), 0) + mass)
        defect_vector = dict(aggregate.get("defect_distribution_vector") or {})
        for defect_flag in _sorted_unique_strings(list(row.get("defect_flags") or [])):
            defect_vector[defect_flag] = int(_as_int(defect_vector.get(defect_flag, 0), 0) + mass)
        aggregate["defect_distribution_vector"] = dict((key, int(defect_vector[key])) for key in sorted(defect_vector.keys()))
        wear_vector = dict(aggregate.get("wear_distribution_vector") or {})
        for wear_key, wear_value in sorted((dict(row.get("wear_state") or {})).items(), key=lambda item: str(item[0])):
            token = str(wear_key).strip()
            if not token:
                continue
            wear_vector[token] = int(_as_int(wear_vector.get(token, 0), 0) + max(0, _as_int(wear_value, 0)))
        aggregate["wear_distribution_vector"] = dict((key, int(wear_vector[key])) for key in sorted(wear_vector.keys()))
        ext = dict(aggregate.get("extensions") or {})
        ext["part_count"] = int(max(0, _as_int(ext.get("part_count", 0), 0)) + 1)
        aggregate["extensions"] = ext
        aggregate_by_node[ag_node_id] = aggregate

    existing_aggregates = [
        normalize_distribution_aggregate_row(row)
        for row in list(existing_distribution_aggregates or [])
        if isinstance(row, dict)
        and (
            str(row.get("structure_id", "")).strip() != structure_token
            or str(row.get("ag_node_id", "")).strip() not in set(aggregate_by_node.keys())
        )
    ]
    collapsed_aggregates = [normalize_distribution_aggregate_row(aggregate_by_node[key]) for key in sorted(aggregate_by_node.keys())]
    distribution_aggregates = sorted(
        list(existing_aggregates) + list(collapsed_aggregates),
        key=lambda item: (str(item.get("structure_id", "")), str(item.get("ag_node_id", ""))),
    )

    remaining_micro_parts = [
        normalize_micro_part_instance_row(row)
        for row in list(existing_micro_parts or [])
        if isinstance(row, dict)
        and (
            str(row.get("parent_structure_id", "")).strip() != structure_token
            or str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() != roi_token
        )
    ]
    remaining_states = [
        normalize_materialization_state_row(row)
        for row in list(existing_materialization_states or [])
        if isinstance(row, dict)
        and _materialization_state_key(str(row.get("structure_id", "")), str(row.get("roi_id", "")))
        != _materialization_state_key(structure_token, roi_token)
    ]

    micro_mass_total = int(sum(max(0, _as_int(row.get("mass", 0), 0)) for row in collapse_rows))
    aggregate_mass_total = int(sum(max(0, _as_int(row.get("total_mass", 0), 0)) for row in collapsed_aggregates))
    return {
        "collapsed_micro_parts": list(collapse_rows),
        "distribution_aggregates": list(distribution_aggregates),
        "remaining_micro_parts": list(remaining_micro_parts),
        "remaining_materialization_states": list(remaining_states),
        "micro_mass_total": int(micro_mass_total),
        "aggregate_mass_total": int(aggregate_mass_total),
        "invariant_delta": int(aggregate_mass_total - micro_mass_total),
        "collapsed_count": int(len(collapse_rows)),
    }


__all__ = [
    "MaterializationError",
    "REFUSAL_MATERIALIZATION_BUDGET_EXCEEDED",
    "REFUSAL_TRANSITION_INVARIANT_VIOLATION",
    "dematerialize_structure_roi",
    "materialize_structure_roi",
    "normalize_distribution_aggregate_row",
    "normalize_materialization_state_row",
    "normalize_micro_part_instance_row",
    "normalize_reenactment_descriptor_row",
]
