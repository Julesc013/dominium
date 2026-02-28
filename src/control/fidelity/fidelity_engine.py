"""Deterministic CTRL-5 fidelity and budget arbitration engine."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


FIDELITY_LEVEL_ORDER = ("micro", "meso", "macro")
_LEVEL_RANK = dict((token, idx) for idx, token in enumerate(FIDELITY_LEVEL_ORDER))

DEFAULT_FIDELITY_POLICY_ID = "fidelity.policy.default"
RANK_FAIR_POLICY_ID = "fidelity.policy.rank_fair"
SINGLEPLAYER_RELAXED_POLICY_ID = "fidelity.policy.singleplayer_relaxed"

DOWNGRADE_BUDGET = "downgrade.budget_insufficient"
DOWNGRADE_POLICY = "downgrade.policy_disallows"
NO_DOWNGRADE = "none"

REFUSAL_CTRL_FIDELITY_DENIED = "refusal.ctrl.fidelity_denied"

_TARGET_KINDS = ("structure", "region", "graph", "vehicle", "replay")

_DEFAULT_POLICY_ROWS = {
    DEFAULT_FIDELITY_POLICY_ID: {
        "schema_version": "1.0.0",
        "policy_id": DEFAULT_FIDELITY_POLICY_ID,
        "description": "Default deterministic priority-first fidelity arbitration.",
        "arbitration_mode": "priority",
        "extensions": {
            "priority_descending": True,
            "equal_share_first": False,
            "singleplayer_relaxed": False,
        },
    },
    RANK_FAIR_POLICY_ID: {
        "schema_version": "1.0.0",
        "policy_id": RANK_FAIR_POLICY_ID,
        "description": "Ranked fairness arbitration with equal baseline share then deterministic leftover.",
        "arbitration_mode": "equal_share",
        "extensions": {
            "priority_descending": True,
            "equal_share_first": True,
            "singleplayer_relaxed": False,
            "ranked_recommended": True,
        },
    },
    SINGLEPLAYER_RELAXED_POLICY_ID: {
        "schema_version": "1.0.0",
        "policy_id": SINGLEPLAYER_RELAXED_POLICY_ID,
        "description": "Singleplayer relaxed fidelity arbitration within envelope only.",
        "arbitration_mode": "relaxed",
        "extensions": {
            "priority_descending": True,
            "equal_share_first": False,
            "singleplayer_relaxed": True,
        },
    },
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _dedupe_preserve_order(values: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for raw in list(values or []):
        token = str(raw).strip()
        if (not token) or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _u32(value: object) -> int:
    return int(max(0, min(4294967295, _as_int(value, 0))))


def _i32(value: object) -> int:
    return int(max(-2147483648, min(2147483647, _as_int(value, 0))))


def _tick_u64(value: object) -> int:
    return int(max(0, _as_int(value, 0)))


def _target_kind(value: object) -> str:
    token = str(value or "").strip()
    if token in _TARGET_KINDS:
        return token
    return "structure"


def _fidelity_level(value: object) -> str:
    token = str(value or "").strip()
    if token in _LEVEL_RANK:
        return token
    return "macro"


def _fidelity_candidates(requested_level: str) -> List[str]:
    level = _fidelity_level(requested_level)
    if level == "micro":
        return ["micro", "meso", "macro"]
    if level == "meso":
        return ["meso", "macro"]
    return ["macro"]


def _sorted_levels(values: Sequence[str]) -> List[str]:
    tokens = [token for token in list(values or []) if token in _LEVEL_RANK]
    if not tokens:
        return []
    return sorted(set(tokens), key=lambda token: _LEVEL_RANK[token])


def build_fidelity_request(
    *,
    requester_subject_id: str,
    target_kind: str,
    target_id: str,
    requested_level: str,
    cost_estimate: int,
    priority: int,
    created_tick: int,
    fidelity_request_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "fidelity_request_id": "",
        "requester_subject_id": str(requester_subject_id).strip() or "subject.unknown",
        "target_kind": _target_kind(target_kind),
        "target_id": str(target_id).strip() or "target.unknown",
        "requested_level": _fidelity_level(requested_level),
        "cost_estimate": _u32(cost_estimate),
        "priority": _i32(priority),
        "created_tick": _tick_u64(created_tick),
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    provided_id = str(fidelity_request_id).strip()
    if provided_id:
        payload["fidelity_request_id"] = provided_id
    else:
        payload["fidelity_request_id"] = "fidelity.request.{}".format(
            canonical_sha256(
                {
                    "requester_subject_id": payload["requester_subject_id"],
                    "target_kind": payload["target_kind"],
                    "target_id": payload["target_id"],
                    "requested_level": payload["requested_level"],
                    "cost_estimate": payload["cost_estimate"],
                    "priority": payload["priority"],
                    "created_tick": payload["created_tick"],
                    "extensions": payload["extensions"],
                }
            )[:16]
        )
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def build_fidelity_allocation(
    *,
    fidelity_request_id: str,
    resolved_level: str,
    cost_allocated: int,
    downgrade_reason: str,
    allocation_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "allocation_id": "",
        "fidelity_request_id": str(fidelity_request_id).strip(),
        "resolved_level": _fidelity_level(resolved_level),
        "cost_allocated": _u32(cost_allocated),
        "downgrade_reason": str(downgrade_reason).strip() or NO_DOWNGRADE,
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    provided_id = str(allocation_id).strip()
    if provided_id:
        payload["allocation_id"] = provided_id
    else:
        payload["allocation_id"] = "fidelity.alloc.{}".format(
            canonical_sha256(
                {
                    "fidelity_request_id": payload["fidelity_request_id"],
                    "resolved_level": payload["resolved_level"],
                    "cost_allocated": payload["cost_allocated"],
                    "downgrade_reason": payload["downgrade_reason"],
                    "extensions": payload["extensions"],
                }
            )[:16]
        )
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def build_budget_allocation_record(
    *,
    tick: int,
    subject_id: str,
    total_cost_allocated: int,
    total_cost_requested: int,
    envelope_id: str,
    allocation_record_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "allocation_record_id": "",
        "tick": _tick_u64(tick),
        "subject_id": str(subject_id).strip() or "subject.unknown",
        "total_cost_allocated": _u32(total_cost_allocated),
        "total_cost_requested": _u32(total_cost_requested),
        "envelope_id": str(envelope_id).strip() or "budget.unknown",
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    provided_id = str(allocation_record_id).strip()
    if provided_id:
        payload["allocation_record_id"] = provided_id
    else:
        payload["allocation_record_id"] = "fidelity.budget.{}".format(
            canonical_sha256(
                {
                    "tick": payload["tick"],
                    "subject_id": payload["subject_id"],
                    "total_cost_allocated": payload["total_cost_allocated"],
                    "total_cost_requested": payload["total_cost_requested"],
                    "envelope_id": payload["envelope_id"],
                    "extensions": payload["extensions"],
                }
            )[:16]
        )
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def _is_ranked(server_profile: Mapping[str, object]) -> bool:
    token = str((dict(server_profile or {})).get("server_profile_id", "")).strip().lower()
    return "rank" in token


def _resolve_policy(
    *,
    fidelity_policy: Mapping[str, object] | None,
    rs5_budget_state: Mapping[str, object],
    server_profile: Mapping[str, object],
    subject_count: int,
) -> dict:
    policy = dict(fidelity_policy or {})
    requested_policy_id = str(policy.get("policy_id", "")).strip() or str(rs5_budget_state.get("fidelity_policy_id", "")).strip()
    if not requested_policy_id:
        if _is_ranked(server_profile):
            requested_policy_id = RANK_FAIR_POLICY_ID
        elif int(max(1, int(subject_count))) <= 1:
            requested_policy_id = SINGLEPLAYER_RELAXED_POLICY_ID
        else:
            requested_policy_id = DEFAULT_FIDELITY_POLICY_ID

    row = dict(_DEFAULT_POLICY_ROWS.get(requested_policy_id) or _DEFAULT_POLICY_ROWS[DEFAULT_FIDELITY_POLICY_ID])
    if policy:
        row.update(policy)
    row["policy_id"] = str(row.get("policy_id", requested_policy_id)).strip() or requested_policy_id
    mode = str(row.get("arbitration_mode", "")).strip()
    if mode not in ("priority", "equal_share", "relaxed"):
        if row["policy_id"] == RANK_FAIR_POLICY_ID:
            mode = "equal_share"
        elif row["policy_id"] == SINGLEPLAYER_RELAXED_POLICY_ID:
            mode = "relaxed"
        else:
            mode = "priority"
    row["arbitration_mode"] = mode
    row["extensions"] = dict(row.get("extensions") or {})
    return row


def _cost_by_level(request_row: Mapping[str, object]) -> Dict[str, int]:
    request = dict(request_row or {})
    ext = _as_map(request.get("extensions"))
    cost_map = _as_map(ext.get("fidelity_cost_by_level"))
    base = _u32(request.get("cost_estimate", 0))

    micro_default = int(base if base > 0 else 1)
    meso_default = int(max(1, micro_default // 2))
    macro_default = int(1 if meso_default > 0 else 0)

    out = {
        "micro": _u32(cost_map.get("micro", micro_default)),
        "meso": _u32(cost_map.get("meso", meso_default)),
        "macro": _u32(cost_map.get("macro", macro_default)),
    }
    return out


def _allowed_levels(request_row: Mapping[str, object]) -> List[str]:
    request = dict(request_row or {})
    ext = _as_map(request.get("extensions"))
    configured = _sorted_levels(_sorted_unique_strings(ext.get("allowed_levels")))
    if not configured:
        configured = list(FIDELITY_LEVEL_ORDER)

    micro_allowed = bool(ext.get("micro_allowed", True))
    micro_available = bool(ext.get("micro_available", True))
    if (not micro_allowed) or (not micro_available):
        configured = [token for token in configured if token != "micro"]
    if not configured:
        configured = ["macro"]
    return configured


def _best_allocation_for_budget(
    *,
    request_row: Mapping[str, object],
    budget_limit: int,
) -> dict:
    request = dict(request_row or {})
    requested_level = _fidelity_level(request.get("requested_level", "macro"))
    allowed_levels = _allowed_levels(request)
    cost_by_level = _cost_by_level(request)

    candidate_chain = [token for token in _fidelity_candidates(requested_level) if token in allowed_levels]
    if not candidate_chain:
        reason = DOWNGRADE_POLICY
        return {
            "resolved_level": "macro",
            "cost_allocated": 0,
            "downgrade_reason": reason,
            "refusal_codes": [REFUSAL_CTRL_FIDELITY_DENIED],
            "requested_level": requested_level,
            "cost_by_level": cost_by_level,
            "allowed_levels": allowed_levels,
            "candidate_chain": [],
            "budget_limit": int(max(0, budget_limit)),
        }

    picked_level = ""
    picked_cost = 0
    for candidate in candidate_chain:
        candidate_cost = int(max(0, _as_int(cost_by_level.get(candidate, 0), 0)))
        if candidate_cost <= int(max(0, budget_limit)):
            picked_level = candidate
            picked_cost = candidate_cost
            break

    if not picked_level:
        fallback_level = candidate_chain[-1]
        reason = DOWNGRADE_BUDGET
        return {
            "resolved_level": fallback_level,
            "cost_allocated": 0,
            "downgrade_reason": reason,
            "refusal_codes": [REFUSAL_CTRL_FIDELITY_DENIED],
            "requested_level": requested_level,
            "cost_by_level": cost_by_level,
            "allowed_levels": allowed_levels,
            "candidate_chain": candidate_chain,
            "budget_limit": int(max(0, budget_limit)),
        }

    downgrade_reason = NO_DOWNGRADE
    if picked_level != requested_level:
        if requested_level not in allowed_levels:
            downgrade_reason = DOWNGRADE_POLICY
        else:
            requested_cost = int(max(0, _as_int(cost_by_level.get(requested_level, picked_cost), 0)))
            if requested_cost > int(max(0, budget_limit)):
                downgrade_reason = DOWNGRADE_BUDGET
            else:
                downgrade_reason = DOWNGRADE_POLICY

    return {
        "resolved_level": picked_level,
        "cost_allocated": int(max(0, picked_cost)),
        "downgrade_reason": downgrade_reason,
        "refusal_codes": [],
        "requested_level": requested_level,
        "cost_by_level": cost_by_level,
        "allowed_levels": allowed_levels,
        "candidate_chain": candidate_chain,
        "budget_limit": int(max(0, budget_limit)),
    }


def _ordered_requests(rows: Sequence[Mapping[str, object]]) -> List[dict]:
    normalized = [
        build_fidelity_request(
            fidelity_request_id=str(dict(row or {}).get("fidelity_request_id", "")).strip(),
            requester_subject_id=str(dict(row or {}).get("requester_subject_id", "")).strip(),
            target_kind=str(dict(row or {}).get("target_kind", "")).strip(),
            target_id=str(dict(row or {}).get("target_id", "")).strip(),
            requested_level=str(dict(row or {}).get("requested_level", "")).strip(),
            cost_estimate=_u32(dict(row or {}).get("cost_estimate", 0)),
            priority=_i32(dict(row or {}).get("priority", 0)),
            created_tick=_tick_u64(dict(row or {}).get("created_tick", 0)),
            extensions=_as_map(dict(row or {}).get("extensions")),
        )
        for row in list(rows or [])
        if isinstance(row, Mapping)
    ]
    return sorted(
        normalized,
        key=lambda row: (
            -int(_as_int(row.get("priority", 0), 0)),
            str(row.get("requester_subject_id", "")),
            str(row.get("fidelity_request_id", "")),
        ),
    )


def arbitrate_fidelity_requests(
    *,
    fidelity_requests: Sequence[Mapping[str, object]],
    rs5_budget_state: Mapping[str, object],
    server_profile: Mapping[str, object] | None = None,
    fidelity_policy: Mapping[str, object] | None = None,
) -> dict:
    """Deterministically arbitrate per-tick fidelity requests under RS-5 budget."""

    requests = _ordered_requests(fidelity_requests)
    server = dict(server_profile or {})
    rs5 = dict(rs5_budget_state or {})

    tick = _tick_u64(rs5.get("tick", 0))
    tick_token = str(tick)
    envelope_id = str(rs5.get("envelope_id", "")).strip() or "budget.unknown"
    max_cost_units_per_tick = _u32(rs5.get("max_cost_units_per_tick", rs5.get("max_budget_units", 0)))

    runtime_budget_state = _as_map(rs5.get("runtime_budget_state"))
    used_by_tick = _as_map(runtime_budget_state.get("used_by_tick"))
    used_before_total = _u32(used_by_tick.get(tick_token, 0))
    total_available = int(max(0, int(max_cost_units_per_tick) - int(used_before_total)))

    fairness_state = _as_map(rs5.get("fairness_state"))
    used_by_tick_subject = _as_map(fairness_state.get("used_by_tick_subject"))
    subject_usage_before_raw = _as_map(used_by_tick_subject.get(tick_token))

    request_subject_ids = sorted(
        set(str(row.get("requester_subject_id", "")).strip() for row in requests if str(row.get("requester_subject_id", "")).strip())
    )
    connected_subject_ids = _sorted_unique_strings(rs5.get("connected_subject_ids"))
    for subject_id in request_subject_ids:
        if subject_id not in connected_subject_ids:
            connected_subject_ids.append(subject_id)
    connected_subject_ids = sorted(set(connected_subject_ids))
    if not connected_subject_ids:
        connected_subject_ids = list(request_subject_ids)

    policy_row = _resolve_policy(
        fidelity_policy=fidelity_policy,
        rs5_budget_state=rs5,
        server_profile=server,
        subject_count=len(connected_subject_ids),
    )
    arbitration_mode = str(policy_row.get("arbitration_mode", "priority")).strip() or "priority"
    policy_id = str(policy_row.get("policy_id", DEFAULT_FIDELITY_POLICY_ID)).strip() or DEFAULT_FIDELITY_POLICY_ID

    subject_requested_totals: Dict[str, int] = {}
    subject_allocated_totals: Dict[str, int] = {}
    subject_usage_before: Dict[str, int] = {}
    for subject_id in connected_subject_ids:
        subject_usage_before[subject_id] = _u32(subject_usage_before_raw.get(subject_id, 0))
    for row in requests:
        subject_id = str(row.get("requester_subject_id", "")).strip() or "subject.unknown"
        subject_requested_totals[subject_id] = int(
            subject_requested_totals.get(subject_id, 0) + _u32(row.get("cost_estimate", 0))
        )
        subject_allocated_totals.setdefault(subject_id, 0)

    ordered_request_ids = [str(row.get("fidelity_request_id", "")).strip() for row in requests]
    allocation_by_request: Dict[str, dict] = {}
    remaining_total = int(total_available)

    if arbitration_mode == "equal_share" and connected_subject_ids:
        base_share = int(remaining_total // len(connected_subject_ids)) if connected_subject_ids else 0
        subject_share_remaining = dict((subject_id, int(base_share)) for subject_id in connected_subject_ids)
        pending: List[dict] = []

        for row in requests:
            request_id = str(row.get("fidelity_request_id", "")).strip()
            subject_id = str(row.get("requester_subject_id", "")).strip() or "subject.unknown"
            subject_limit = int(max(0, subject_share_remaining.get(subject_id, 0)))
            budget_limit = int(min(max(0, remaining_total), subject_limit))
            allocation = _best_allocation_for_budget(request_row=row, budget_limit=budget_limit)
            if int(allocation.get("cost_allocated", 0)) <= 0:
                pending.append(dict(row))
                allocation_by_request[request_id] = {
                    **allocation,
                    "subject_id": subject_id,
                    "phase": "equal_share",
                    "share_limit": int(subject_limit),
                }
                continue
            cost_allocated = int(max(0, _as_int(allocation.get("cost_allocated", 0), 0)))
            remaining_total = int(max(0, remaining_total - cost_allocated))
            subject_share_remaining[subject_id] = int(max(0, subject_limit - cost_allocated))
            subject_allocated_totals[subject_id] = int(subject_allocated_totals.get(subject_id, 0) + cost_allocated)
            allocation_by_request[request_id] = {
                **allocation,
                "subject_id": subject_id,
                "phase": "equal_share",
                "share_limit": int(subject_limit),
            }

        for row in pending:
            request_id = str(row.get("fidelity_request_id", "")).strip()
            prior = dict(allocation_by_request.get(request_id) or {})
            if int(max(0, _as_int(prior.get("cost_allocated", 0), 0))) > 0:
                continue
            subject_id = str(row.get("requester_subject_id", "")).strip() or "subject.unknown"
            allocation = _best_allocation_for_budget(request_row=row, budget_limit=int(max(0, remaining_total)))
            cost_allocated = int(max(0, _as_int(allocation.get("cost_allocated", 0), 0)))
            if cost_allocated > 0:
                remaining_total = int(max(0, remaining_total - cost_allocated))
                subject_allocated_totals[subject_id] = int(subject_allocated_totals.get(subject_id, 0) + cost_allocated)
            allocation_by_request[request_id] = {
                **allocation,
                "subject_id": subject_id,
                "phase": "leftover",
                "share_limit": int(max(0, _as_int(prior.get("share_limit", 0), 0))),
            }
    else:
        phase = "relaxed" if arbitration_mode == "relaxed" else "priority"
        for row in requests:
            request_id = str(row.get("fidelity_request_id", "")).strip()
            subject_id = str(row.get("requester_subject_id", "")).strip() or "subject.unknown"
            allocation = _best_allocation_for_budget(request_row=row, budget_limit=int(max(0, remaining_total)))
            cost_allocated = int(max(0, _as_int(allocation.get("cost_allocated", 0), 0)))
            if cost_allocated > 0:
                remaining_total = int(max(0, remaining_total - cost_allocated))
                subject_allocated_totals[subject_id] = int(subject_allocated_totals.get(subject_id, 0) + cost_allocated)
            allocation_by_request[request_id] = {
                **allocation,
                "subject_id": subject_id,
                "phase": phase,
                "share_limit": 0,
            }

    fidelity_allocations: List[dict] = []
    decision_log_entries: List[dict] = []
    refusal_codes: List[str] = []
    for row in requests:
        request_id = str(row.get("fidelity_request_id", "")).strip()
        subject_id = str(row.get("requester_subject_id", "")).strip() or "subject.unknown"
        allocation_meta = dict(allocation_by_request.get(request_id) or {})
        resolved_level = _fidelity_level(allocation_meta.get("resolved_level", row.get("requested_level", "macro")))
        cost_allocated = _u32(allocation_meta.get("cost_allocated", 0))
        downgrade_reason = str(allocation_meta.get("downgrade_reason", NO_DOWNGRADE)).strip() or NO_DOWNGRADE
        request_refusals = _dedupe_preserve_order(
            [str(item).strip() for item in list(allocation_meta.get("refusal_codes") or []) if str(item).strip()]
        )
        refusal_codes.extend(request_refusals)

        allocation_row = build_fidelity_allocation(
            fidelity_request_id=request_id,
            resolved_level=resolved_level,
            cost_allocated=cost_allocated,
            downgrade_reason=downgrade_reason,
            extensions={
                "policy_id": policy_id,
                "envelope_id": envelope_id,
                "requested_level": _fidelity_level(row.get("requested_level", "macro")),
                "requested_cost": _u32(row.get("cost_estimate", 0)),
                "priority": _i32(row.get("priority", 0)),
                "subject_id": subject_id,
                "refusal_codes": list(request_refusals),
                "phase": str(allocation_meta.get("phase", "priority")),
                "share_limit": _u32(allocation_meta.get("share_limit", 0)),
                "budget_limit": _u32(allocation_meta.get("budget_limit", 0)),
                "allowed_levels": _sorted_levels(_sorted_unique_strings(allocation_meta.get("allowed_levels"))),
                "candidate_chain": _sorted_levels(_sorted_unique_strings(allocation_meta.get("candidate_chain"))),
                "cost_by_level": dict(
                    (token, _u32(value))
                    for token, value in sorted(dict(allocation_meta.get("cost_by_level") or {}).items(), key=lambda item: str(item[0]))
                    if str(token).strip() in _LEVEL_RANK
                ),
            },
        )
        fidelity_allocations.append(allocation_row)

        decision_entry = {
            "schema_version": "1.0.0",
            "fidelity_request_id": request_id,
            "allocation_id": str(allocation_row.get("allocation_id", "")).strip(),
            "resolved_level": str(allocation_row.get("resolved_level", "")).strip(),
            "cost_allocated": _u32(allocation_row.get("cost_allocated", 0)),
            "downgrade_reason": str(allocation_row.get("downgrade_reason", NO_DOWNGRADE)).strip() or NO_DOWNGRADE,
            "envelope_id": envelope_id,
            "policy_id": policy_id,
            "refusal_codes": list(request_refusals),
            "deterministic_fingerprint": "",
            "extensions": {
                "subject_id": subject_id,
            },
        }
        entry_seed = dict(decision_entry)
        entry_seed["deterministic_fingerprint"] = ""
        decision_entry["deterministic_fingerprint"] = canonical_sha256(entry_seed)
        decision_log_entries.append(decision_entry)

    fidelity_allocations = sorted(
        fidelity_allocations,
        key=lambda item: (
            -_as_int((dict(item.get("extensions") or {})).get("priority", 0), 0),
            str((dict(item.get("extensions") or {})).get("subject_id", "")),
            str(item.get("fidelity_request_id", "")),
        ),
    )
    decision_log_entries = sorted(
        decision_log_entries,
        key=lambda item: str(item.get("allocation_id", "")),
    )
    refusal_codes = _dedupe_preserve_order(refusal_codes)

    total_allocated = int(sum(_u32(row.get("cost_allocated", 0)) for row in fidelity_allocations))
    used_after_total = int(used_before_total + total_allocated)
    used_by_tick[tick_token] = int(used_after_total)

    subject_usage_after: Dict[str, int] = {}
    tick_subject_usage = dict(
        (subject_id, _u32(subject_usage_before.get(subject_id, 0)))
        for subject_id in connected_subject_ids
    )
    for subject_id in connected_subject_ids:
        tick_subject_usage[subject_id] = int(
            _u32(subject_usage_before.get(subject_id, 0)) + _u32(subject_allocated_totals.get(subject_id, 0))
        )
        subject_usage_after[subject_id] = int(tick_subject_usage[subject_id])
    used_by_tick_subject[tick_token] = dict(
        (subject_id, int(tick_subject_usage[subject_id]))
        for subject_id in sorted(tick_subject_usage.keys())
        if str(subject_id).strip()
    )

    budget_allocation_records: List[dict] = []
    for subject_id in sorted(set(connected_subject_ids + list(subject_requested_totals.keys()))):
        budget_allocation_records.append(
            build_budget_allocation_record(
                tick=tick,
                subject_id=subject_id,
                total_cost_allocated=_u32(subject_allocated_totals.get(subject_id, 0)),
                total_cost_requested=_u32(subject_requested_totals.get(subject_id, 0)),
                envelope_id=envelope_id,
                extensions={
                    "policy_id": policy_id,
                    "used_before": _u32(subject_usage_before.get(subject_id, 0)),
                    "used_after": _u32(subject_usage_after.get(subject_id, 0)),
                },
            )
        )

    runtime_budget_state_out = {
        "used_by_tick": dict(
            (str(key), _u32(value))
            for key, value in sorted(used_by_tick.items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
    }
    fairness_state_out = {
        "connected_subject_ids": list(connected_subject_ids),
        "used_by_tick_subject": dict(
            (str(key), dict((str(subject), _u32(value2)) for subject, value2 in sorted(dict(value).items(), key=lambda item: str(item[0])) if str(subject).strip()))
            for key, value in sorted(used_by_tick_subject.items(), key=lambda item: str(item[0]))
            if isinstance(value, Mapping)
        ),
    }

    out = {
        "schema_version": "1.0.0",
        "tick": int(tick),
        "policy_id": policy_id,
        "envelope_id": envelope_id,
        "fidelity_requests": [dict(row) for row in requests],
        "fidelity_allocations": list(fidelity_allocations),
        "budget_allocation_records": list(budget_allocation_records),
        "runtime_budget_state": runtime_budget_state_out,
        "fairness_state": fairness_state_out,
        "refusal_codes": list(refusal_codes),
        "decision_log_entries": list(decision_log_entries),
        "total_cost_allocated": int(total_allocated),
        "deterministic_fingerprint": "",
        "extensions": {
            "arbitration_mode": arbitration_mode,
            "ordered_request_ids": list(ordered_request_ids),
            "max_cost_units_per_tick": int(max_cost_units_per_tick),
            "used_before_total": int(used_before_total),
            "used_after_total": int(used_after_total),
            "remaining_total": int(max(0, remaining_total)),
        },
    }
    out["allocations"] = list(out["fidelity_allocations"])
    out["allocation_records"] = list(out["budget_allocation_records"])

    seed = dict(out)
    seed["deterministic_fingerprint"] = ""
    out["deterministic_fingerprint"] = canonical_sha256(seed)
    return out


__all__ = [
    "DEFAULT_FIDELITY_POLICY_ID",
    "DOWNGRADE_BUDGET",
    "DOWNGRADE_POLICY",
    "FIDELITY_LEVEL_ORDER",
    "REFUSAL_CTRL_FIDELITY_DENIED",
    "arbitrate_fidelity_requests",
    "build_budget_allocation_record",
    "build_fidelity_allocation",
    "build_fidelity_request",
]
