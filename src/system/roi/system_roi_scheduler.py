"""SYS-3 deterministic system ROI tier scheduler."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from src.geo import roi_distance_mm
from src.geo.worldgen import build_worldgen_requests_for_roi
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_SYSTEM_TIER_CONTRACT_MISSING = "refusal.system.tier_contract_missing"
REFUSAL_SYSTEM_TIER_BUDGET_DENIED = "refusal.system.tier_budget_denied"
REFUSAL_SYSTEM_TIER_UNSUPPORTED = "refusal.system.tier_transition_unsupported"
REFUSAL_SYSTEM_TIER_INVALID = "refusal.system.tier_transition_invalid"

_DEFAULT_TIERS = ("micro", "meso", "macro")
_DEFAULT_DEGRADE_ORDER = ("micro", "meso", "macro")
_PRIORITY_RANK = {
    "inspection": 0,
    "hazard": 1,
    "roi": 2,
    "background": 3,
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _rows_from_registry_payload(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
    body = _as_map(payload)
    for key in keys:
        rows = body.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    for key in keys:
        rows = record.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _tier_contract_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        _rows_from_registry_payload(payload, ("tier_contracts",)),
        key=lambda item: str(item.get("contract_id", "")),
    ):
        contract_id = str(row.get("contract_id", "")).strip()
        if contract_id:
            out[contract_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _normalize_system_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("system_id", ""))):
        system_id = str(row.get("system_id", "")).strip()
        if not system_id:
            continue
        ext = _as_map(row.get("extensions"))
        normalized = {
            "system_id": system_id,
            "tier_contract_id": str(row.get("tier_contract_id", "")).strip(),
            "current_tier": str(row.get("current_tier", "micro")).strip().lower() or "micro",
            "active_capsule_id": str(row.get("active_capsule_id", "")).strip(),
            "extensions": ext,
        }
        out[system_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _capsule_id_by_system(rows: object) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("system_id", ""))):
        system_id = str(row.get("system_id", "")).strip()
        capsule_id = str(row.get("capsule_id", "")).strip()
        if system_id and capsule_id:
            out[system_id] = capsule_id
    return dict((key, str(out[key])) for key in sorted(out.keys()))


def _priority_class_for_system(
    *,
    system_id: str,
    inspection_ids: set[str],
    hazard_ids: set[str],
    roi_ids: set[str],
) -> str:
    if system_id in inspection_ids:
        return "inspection"
    if system_id in hazard_ids:
        return "hazard"
    if system_id in roi_ids:
        return "roi"
    return "background"


def _desired_tier_for_system(
    *,
    system_id: str,
    roi_ids: set[str],
    inspection_ids: set[str],
    hazard_ids: set[str],
    fidelity_request_ids: set[str],
) -> str:
    if (
        system_id in roi_ids
        or system_id in inspection_ids
        or system_id in hazard_ids
        or system_id in fidelity_request_ids
    ):
        return "micro"
    return "macro"


def _supported_tiers(contract_row: Mapping[str, object]) -> List[str]:
    supported = [
        str(token).strip().lower()
        for token in list(contract_row.get("supported_tiers") or [])
        if str(token).strip()
    ]
    supported = [token for token in supported if token in {"micro", "meso", "macro"}]
    if not supported:
        supported = list(_DEFAULT_TIERS)
    return list(dict.fromkeys(supported))


def _degrade_order(contract_row: Mapping[str, object], supported: Sequence[str]) -> List[str]:
    declared = [
        str(token).strip().lower()
        for token in list(contract_row.get("deterministic_degradation_order") or [])
        if str(token).strip()
    ]
    declared = [token for token in declared if token in {"micro", "meso", "macro"}]
    if not declared:
        declared = list(_DEFAULT_DEGRADE_ORDER)
    out = [token for token in declared if token in set(supported)]
    for token in supported:
        if token not in out:
            out.append(token)
    return out


def _effective_desired_tier(
    *,
    desired_tier: str,
    supported_tiers: Sequence[str],
    degradation_order: Sequence[str],
) -> str:
    desired = str(desired_tier or "").strip().lower() or "macro"
    supported = [str(token).strip().lower() for token in list(supported_tiers or []) if str(token).strip()]
    if not supported:
        supported = list(_DEFAULT_TIERS)
    if desired in supported:
        return desired
    order = [str(token).strip().lower() for token in list(degradation_order or []) if str(token).strip()]
    if not order:
        order = list(_DEFAULT_DEGRADE_ORDER)
    if desired == "micro":
        for token in order:
            if token in supported:
                return token
        return supported[0]
    if desired == "macro":
        for token in reversed(order):
            if token in supported:
                return token
        return supported[-1]
    # desired == meso (or unknown fallback): pick closest deterministic
    for token in ("meso", "micro", "macro"):
        if token in supported:
            return token
    return supported[0]


def _transition_kind(current_tier: str, target_tier: str) -> str:
    current = str(current_tier or "").strip().lower() or "macro"
    target = str(target_tier or "").strip().lower() or "macro"
    if current == target:
        return "none"
    if current == "macro" and target in {"micro", "meso"}:
        return "expand"
    if current in {"micro", "meso"} and target == "macro":
        return "collapse"
    return "unsupported"


def system_roi_distance_query(
    pos_a_ref: Mapping[str, object] | None,
    pos_b_ref: Mapping[str, object] | None,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
    ) -> dict:
    return roi_distance_mm(
        pos_a_ref,
        pos_b_ref,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
        metric_registry_payload=metric_registry_payload,
    )


def system_roi_worldgen_requests(
    *,
    roi_geo_cell_keys: object,
    refinement_level: int = 0,
    reason: str = "roi",
) -> List[dict]:
    return build_worldgen_requests_for_roi(
        geo_cell_keys=list(roi_geo_cell_keys or []),
        refinement_level=int(max(0, _as_int(refinement_level, 0))),
        reason=str(reason or "").strip() or "roi",
        extensions={"source": "GEO8-5"},
    )


def evaluate_system_roi_tick(
    *,
    current_tick: int,
    state: Mapping[str, object] | None,
    system_rows: object,
    system_macro_capsule_rows: object,
    tier_contract_registry_payload: Mapping[str, object] | None,
    roi_system_ids: object = None,
    inspection_system_ids: object = None,
    hazard_system_ids: object = None,
    fidelity_request_system_ids: object = None,
    denied_system_ids: object = None,
    max_expands_per_tick: int = 16,
    max_collapses_per_tick: int = 32,
) -> dict:
    del state
    tick_value = int(max(0, _as_int(current_tick, 0)))
    max_expands = int(max(0, _as_int(max_expands_per_tick, 16)))
    max_collapses = int(max(0, _as_int(max_collapses_per_tick, 32)))

    systems = _normalize_system_rows(system_rows)
    contracts_by_id = _tier_contract_rows_by_id(tier_contract_registry_payload)
    capsule_by_system = _capsule_id_by_system(system_macro_capsule_rows)

    roi_ids = set(_sorted_tokens(list(roi_system_ids or [])))
    inspection_ids = set(_sorted_tokens(list(inspection_system_ids or [])))
    hazard_ids = set(_sorted_tokens(list(hazard_system_ids or [])))
    fidelity_ids = set(_sorted_tokens(list(fidelity_request_system_ids or [])))
    denied_ids = set(_sorted_tokens(list(denied_system_ids or [])))

    candidate_rows: List[dict] = []
    decision_rows: List[dict] = []
    refusal_rows: List[dict] = []

    for row in systems:
        system_id = str(row.get("system_id", "")).strip()
        if not system_id:
            continue
        current_tier = str(row.get("current_tier", "micro")).strip().lower() or "micro"
        tier_contract_id = str(row.get("tier_contract_id", "")).strip()
        contract_row = dict(contracts_by_id.get(tier_contract_id) or {})
        if not contract_row:
            refusal_rows.append(
                {
                    "system_id": system_id,
                    "reason_code": REFUSAL_SYSTEM_TIER_CONTRACT_MISSING,
                    "tier_contract_id": tier_contract_id,
                }
            )
            decision_rows.append(
                {
                    "decision_id": "decision.system.roi.missing_contract.{}".format(
                        canonical_sha256({"tick": tick_value, "system_id": system_id})[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_roi_tick",
                    "result": "denied",
                    "reason_code": REFUSAL_SYSTEM_TIER_CONTRACT_MISSING,
                    "extensions": {
                        "system_id": system_id,
                        "tier_contract_id": tier_contract_id,
                    },
                }
            )
            continue

        desired_tier = _desired_tier_for_system(
            system_id=system_id,
            roi_ids=roi_ids,
            inspection_ids=inspection_ids,
            hazard_ids=hazard_ids,
            fidelity_request_ids=fidelity_ids,
        )
        supported = _supported_tiers(contract_row)
        degradation = _degrade_order(contract_row, supported)
        effective_tier = _effective_desired_tier(
            desired_tier=desired_tier,
            supported_tiers=supported,
            degradation_order=degradation,
        )
        transition_kind = _transition_kind(current_tier, effective_tier)
        priority_class = _priority_class_for_system(
            system_id=system_id,
            inspection_ids=inspection_ids,
            hazard_ids=hazard_ids,
            roi_ids=roi_ids,
        )
        priority_rank = int(_PRIORITY_RANK.get(priority_class, 99))
        candidate_rows.append(
            {
                "system_id": system_id,
                "current_tier": current_tier,
                "desired_tier": desired_tier,
                "effective_tier": effective_tier,
                "transition_kind": transition_kind,
                "tier_contract_id": tier_contract_id,
                "cost_model_id": str(contract_row.get("cost_model_id", "")).strip(),
                "priority_class": priority_class,
                "priority_rank": priority_rank,
                "capsule_id": str(row.get("active_capsule_id", "")).strip() or str(capsule_by_system.get(system_id, "")).strip(),
            }
        )

    approved_rows: List[dict] = []
    denied_rows: List[dict] = []
    noop_rows: List[dict] = []
    expand_count = 0
    collapse_count = 0

    candidates_sorted = sorted(
        (dict(item) for item in candidate_rows),
        key=lambda item: (
            int(item.get("priority_rank", 99)),
            str(item.get("system_id", "")),
        ),
    )
    for row in candidates_sorted:
        system_id = str(row.get("system_id", "")).strip()
        transition_kind = str(row.get("transition_kind", "")).strip()
        current_tier = str(row.get("current_tier", "")).strip()
        effective_tier = str(row.get("effective_tier", "")).strip()
        decision_base = {
            "system_id": system_id,
            "tier_contract_id": str(row.get("tier_contract_id", "")).strip(),
            "current_tier": current_tier,
            "desired_tier": str(row.get("desired_tier", "")).strip(),
            "effective_tier": effective_tier,
            "transition_kind": transition_kind,
            "priority_class": str(row.get("priority_class", "")).strip(),
            "cost_model_id": str(row.get("cost_model_id", "")).strip(),
            "capsule_id": str(row.get("capsule_id", "")).strip() or None,
        }

        if transition_kind == "none":
            noop_rows.append(dict(row))
            decision_rows.append(
                {
                    "decision_id": "decision.system.roi.noop.{}".format(
                        canonical_sha256({"tick": tick_value, "system_id": system_id, "tier": effective_tier})[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_roi_tick",
                    "result": "no_op",
                    "reason_code": "system.tier.already_satisfied",
                    "extensions": dict(decision_base),
                }
            )
            continue

        if transition_kind == "unsupported":
            denied_row = dict(row)
            denied_row["reason_code"] = REFUSAL_SYSTEM_TIER_UNSUPPORTED
            denied_rows.append(denied_row)
            decision_rows.append(
                {
                    "decision_id": "decision.system.roi.unsupported.{}".format(
                        canonical_sha256({"tick": tick_value, "system_id": system_id, "kind": transition_kind})[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_roi_tick",
                    "result": "denied",
                    "reason_code": REFUSAL_SYSTEM_TIER_UNSUPPORTED,
                    "extensions": dict(decision_base),
                }
            )
            continue

        if system_id in denied_ids:
            denied_row = dict(row)
            denied_row["reason_code"] = REFUSAL_SYSTEM_TIER_BUDGET_DENIED
            denied_row["denied_by"] = "ctrl"
            denied_rows.append(denied_row)
            decision_rows.append(
                {
                    "decision_id": "decision.system.roi.ctrl_denied.{}".format(
                        canonical_sha256({"tick": tick_value, "system_id": system_id, "kind": transition_kind})[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_roi_tick",
                    "result": "denied",
                    "reason_code": REFUSAL_SYSTEM_TIER_BUDGET_DENIED,
                    "extensions": dict(
                        decision_base,
                        denied_by="ctrl",
                    ),
                }
            )
            continue

        if transition_kind == "expand":
            if expand_count >= max_expands:
                denied_row = dict(row)
                denied_row["reason_code"] = REFUSAL_SYSTEM_TIER_BUDGET_DENIED
                denied_row["denied_by"] = "budget.expand_cap"
                denied_rows.append(denied_row)
                decision_rows.append(
                    {
                        "decision_id": "decision.system.roi.expand_cap.{}".format(
                            canonical_sha256({"tick": tick_value, "system_id": system_id})[:16]
                        ),
                        "tick": int(tick_value),
                        "process_id": "process.system_roi_tick",
                        "result": "denied",
                        "reason_code": REFUSAL_SYSTEM_TIER_BUDGET_DENIED,
                        "extensions": dict(
                            decision_base,
                            denied_by="budget.expand_cap",
                        ),
                    }
                )
                continue
            expand_count += 1
            approved = dict(row)
            approved["requested_process_id"] = "process.system_expand"
            approved_rows.append(approved)
            decision_rows.append(
                {
                    "decision_id": "decision.system.roi.expand_approved.{}".format(
                        canonical_sha256({"tick": tick_value, "system_id": system_id})[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_roi_tick",
                    "result": "approved",
                    "reason_code": "system.tier.expand",
                    "extensions": dict(decision_base),
                }
            )
            continue

        if transition_kind == "collapse":
            if collapse_count >= max_collapses:
                denied_row = dict(row)
                denied_row["reason_code"] = REFUSAL_SYSTEM_TIER_BUDGET_DENIED
                denied_row["denied_by"] = "budget.collapse_cap"
                denied_rows.append(denied_row)
                decision_rows.append(
                    {
                        "decision_id": "decision.system.roi.collapse_cap.{}".format(
                            canonical_sha256({"tick": tick_value, "system_id": system_id})[:16]
                        ),
                        "tick": int(tick_value),
                        "process_id": "process.system_roi_tick",
                        "result": "denied",
                        "reason_code": REFUSAL_SYSTEM_TIER_BUDGET_DENIED,
                        "extensions": dict(
                            decision_base,
                            denied_by="budget.collapse_cap",
                        ),
                    }
                )
                continue
            collapse_count += 1
            approved = dict(row)
            approved["requested_process_id"] = "process.system_collapse"
            approved_rows.append(approved)
            decision_rows.append(
                {
                    "decision_id": "decision.system.roi.collapse_approved.{}".format(
                        canonical_sha256({"tick": tick_value, "system_id": system_id})[:16]
                    ),
                    "tick": int(tick_value),
                    "process_id": "process.system_roi_tick",
                    "result": "approved",
                    "reason_code": "system.tier.collapse",
                    "extensions": dict(decision_base),
                }
            )
            continue

        denied_row = dict(row)
        denied_row["reason_code"] = REFUSAL_SYSTEM_TIER_INVALID
        denied_rows.append(denied_row)
        decision_rows.append(
            {
                "decision_id": "decision.system.roi.invalid.{}".format(
                    canonical_sha256({"tick": tick_value, "system_id": system_id, "kind": transition_kind})[:16]
                ),
                "tick": int(tick_value),
                "process_id": "process.system_roi_tick",
                "result": "denied",
                "reason_code": REFUSAL_SYSTEM_TIER_INVALID,
                "extensions": dict(decision_base),
            }
        )

    approved_rows = sorted(
        (dict(item) for item in approved_rows),
        key=lambda item: (
            int(item.get("priority_rank", 99)),
            str(item.get("system_id", "")),
            str(item.get("transition_kind", "")),
        ),
    )
    denied_rows = sorted(
        (dict(item) for item in denied_rows),
        key=lambda item: (
            int(item.get("priority_rank", 99)),
            str(item.get("system_id", "")),
            str(item.get("transition_kind", "")),
            str(item.get("reason_code", "")),
        ),
    )
    noop_rows = sorted(
        (dict(item) for item in noop_rows),
        key=lambda item: str(item.get("system_id", "")),
    )
    decision_rows = sorted(
        (dict(item) for item in decision_rows),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("decision_id", "")),
        ),
    )
    refusal_rows = sorted(
        (dict(item) for item in refusal_rows),
        key=lambda item: (str(item.get("system_id", "")), str(item.get("reason_code", ""))),
    )

    result = {
        "result": "complete",
        "processed_system_ids": [str(row.get("system_id", "")).strip() for row in systems if str(row.get("system_id", "")).strip()],
        "approved_transition_rows": approved_rows,
        "denied_transition_rows": denied_rows,
        "noop_rows": noop_rows,
        "decision_log_rows": decision_rows,
        "refusal_rows": refusal_rows,
        "approved_expand_count": int(len([row for row in approved_rows if str(row.get("transition_kind", "")).strip() == "expand"])),
        "approved_collapse_count": int(len([row for row in approved_rows if str(row.get("transition_kind", "")).strip() == "collapse"])),
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


__all__ = [
    "REFUSAL_SYSTEM_TIER_CONTRACT_MISSING",
    "REFUSAL_SYSTEM_TIER_BUDGET_DENIED",
    "REFUSAL_SYSTEM_TIER_UNSUPPORTED",
    "REFUSAL_SYSTEM_TIER_INVALID",
    "evaluate_system_roi_tick",
    "system_roi_distance_query",
]
