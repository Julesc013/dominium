"""Deterministic CTRL-3 negotiation kernel for downgrade/refusal arbitration."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


NEGOTIATION_AXIS_ORDER = (
    "abstraction",
    "view",
    "epistemic",
    "fidelity",
    "budget",
)

REFUSAL_CTRL_FORBIDDEN_BY_LAW = "refusal.ctrl.forbidden_by_law"
REFUSAL_CTRL_ENTITLEMENT_MISSING = "refusal.ctrl.entitlement_missing"
REFUSAL_CTRL_VIEW_FORBIDDEN = "refusal.ctrl.view_forbidden"
REFUSAL_CTRL_FIDELITY_DENIED = "refusal.ctrl.fidelity_denied"
REFUSAL_CTRL_META_FORBIDDEN = "refusal.ctrl.meta_forbidden"
REFUSAL_CTRL_IR_COST_EXCEEDED = "refusal.ctrl.ir_cost_exceeded"

DOWNGRADE_BUDGET = "downgrade.budget_insufficient"
DOWNGRADE_RANK_FAIRNESS = "downgrade.rank_fairness"
DOWNGRADE_EPISTEMIC = "downgrade.epistemic_limits"
DOWNGRADE_POLICY = "downgrade.policy_disallows"
DOWNGRADE_TARGET_NOT_AVAILABLE = "downgrade.target_not_available"

_ABSTRACTION_LEVELS = ("AL0", "AL1", "AL2", "AL3", "AL4")
_FIDELITY_LEVELS = ("macro", "meso", "micro")
_AL_RANK = dict((token, idx) for idx, token in enumerate(_ABSTRACTION_LEVELS))
_FIDELITY_RANK = dict((token, idx) for idx, token in enumerate(_FIDELITY_LEVELS))
_AXIS_RANK = dict((token, idx) for idx, token in enumerate(NEGOTIATION_AXIS_ORDER))

DEFAULT_VIEW_POLICY_ID = "view.mode.first_person"
DEFAULT_ABSTRACTION_LEVEL = "AL0"
DEFAULT_FIDELITY = "meso"
DEFAULT_EPISTEMIC_SCOPE = "ep.scope.default"


def _to_int(value: object, default_value: int = 0) -> int:
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
    seen = set()
    out: List[str] = []
    for raw in list(values or []):
        token = str(raw).strip()
        if (not token) or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _al_token(value: object) -> str:
    token = str(value or "").strip()
    if token in _AL_RANK:
        return token
    return DEFAULT_ABSTRACTION_LEVEL


def _fidelity_token(value: object) -> str:
    token = str(value or "").strip()
    if token in _FIDELITY_RANK:
        return token
    return DEFAULT_FIDELITY


def _is_ranked(server_profile: Mapping[str, object], request_context: Mapping[str, object]) -> bool:
    profile_id = str((dict(server_profile or {})).get("server_profile_id", "")).strip().lower()
    context_id = str((dict(request_context or {})).get("server_profile_id", "")).strip().lower()
    return "rank" in profile_id or "rank" in context_id


def _first_non_freecam(values: Sequence[str]) -> str:
    for token in list(values or []):
        value = str(token).strip()
        if value and "freecam" not in value.lower():
            return value
    return ""


def _view_mode_for_policy(view_policy_id: str) -> str:
    token = str(view_policy_id or "").strip().lower()
    if not token:
        return "unknown"
    if "freecam" in token or token.endswith(".freecam") or ".free." in token:
        return "freecam"
    if "third_person" in token or "third.person" in token or "third_person" in token:
        return "third_person"
    if "first_person" in token or "first.person" in token or "first_person" in token:
        return "first_person"
    if "spectator" in token:
        return "spectator"
    if "replay" in token:
        return "replay"
    return "unknown"


def _first_view_by_mode(values: Sequence[str], mode: str) -> str:
    target_mode = str(mode or "").strip()
    rows = [
        str(token).strip()
        for token in list(values or [])
        if str(token).strip() and _view_mode_for_policy(str(token)) == target_mode
    ]
    if not rows:
        return ""
    return sorted(set(rows))[0]


def _view_downgrade_target(allowed_view: Sequence[str], requested_view: str) -> str:
    requested_mode = _view_mode_for_policy(requested_view)
    if requested_mode == "freecam":
        for mode in ("third_person", "first_person"):
            candidate = _first_view_by_mode(allowed_view, mode)
            if candidate:
                return candidate
        return ""
    if requested_mode == "third_person":
        return _first_view_by_mode(allowed_view, "first_person")
    return ""


def _min_fidelity(requested: str, allowed: Sequence[str]) -> str:
    rows = [token for token in list(allowed or []) if token in _FIDELITY_RANK]
    if not rows:
        return _fidelity_token(requested)
    return sorted(rows, key=lambda token: _FIDELITY_RANK[token])[0]


def _fidelity_candidates(requested: str) -> List[str]:
    token = _fidelity_token(requested)
    if token == "micro":
        return ["micro", "meso", "macro"]
    if token == "meso":
        return ["meso", "macro"]
    return ["macro"]


def _policy_id_rows(
    control_policy: Mapping[str, object],
    view_policy: Mapping[str, object],
    epistemic_policy: Mapping[str, object],
    server_profile: Mapping[str, object],
    request_context: Mapping[str, object],
) -> List[str]:
    rows = []
    for token in (
        (dict(control_policy or {})).get("control_policy_id"),
        (dict(view_policy or {})).get("view_policy_id"),
        (dict(epistemic_policy or {})).get("epistemic_policy_id"),
        (dict(server_profile or {})).get("server_profile_id"),
        (dict(request_context or {})).get("law_profile_id"),
        (dict(request_context or {})).get("server_profile_id"),
    ):
        value = str(token or "").strip()
        if value:
            rows.append(value)
    return _dedupe_preserve_order(rows)


def build_downgrade_entry(
    *,
    axis: str,
    from_value: object,
    to_value: object,
    reason_code: str,
    remediation_hint: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "downgrade_id": "",
        "axis": str(axis).strip(),
        "from_value": str(from_value if from_value is not None else ""),
        "to_value": str(to_value if to_value is not None else ""),
        "reason_code": str(reason_code).strip(),
        "remediation_hint": str(remediation_hint).strip(),
        "extensions": dict(extensions or {}),
    }
    payload["downgrade_id"] = "downgrade.{}".format(
        canonical_sha256(
            {
                "axis": payload["axis"],
                "from_value": payload["from_value"],
                "to_value": payload["to_value"],
                "reason_code": payload["reason_code"],
                "remediation_hint": payload["remediation_hint"],
                "extensions": payload["extensions"],
            }
        )[:16]
    )
    return payload


def _append_downgrade(
    rows: List[dict],
    *,
    axis: str,
    from_value: object,
    to_value: object,
    reason_code: str,
    remediation_hint: str,
    extensions: Mapping[str, object] | None = None,
) -> None:
    from_token = str(from_value if from_value is not None else "")
    to_token = str(to_value if to_value is not None else "")
    if from_token == to_token:
        return
    rows.append(
        build_downgrade_entry(
            axis=axis,
            from_value=from_token,
            to_value=to_token,
            reason_code=reason_code,
            remediation_hint=remediation_hint,
            extensions=extensions,
        )
    )


def build_negotiation_request(
    *,
    requester_subject_id: str,
    request_vector: Mapping[str, object] | None,
    law_profile_id: str,
    server_profile_id: str,
    control_intent_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "requester_subject_id": str(requester_subject_id).strip() or "subject.unknown",
        "request_vector": dict(request_vector or {}),
        "context": {
            "law_profile_id": str(law_profile_id).strip() or "law.unknown",
            "server_profile_id": str(server_profile_id).strip() or "server.profile.unknown",
        },
        "extensions": dict(extensions or {}),
    }
    control_intent_token = str(control_intent_id).strip()
    if control_intent_token:
        payload["control_intent_id"] = control_intent_token
    return payload


def negotiate_request(
    *,
    negotiation_request: Mapping[str, object],
    rs5_budget_state: Mapping[str, object] | None,
    control_policy: Mapping[str, object],
    view_policy: Mapping[str, object] | None = None,
    epistemic_policy: Mapping[str, object] | None = None,
    server_profile: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    law_profile: Mapping[str, object] | None = None,
) -> dict:
    """Negotiate abstraction/view/epistemic/fidelity/budget with deterministic ordering."""

    request = dict(negotiation_request or {})
    request_vector = _as_map(request.get("request_vector"))
    request_context = _as_map(request.get("context"))
    request_ext = _as_map(request.get("extensions"))
    authority = dict(authority_context or {})
    law = dict(law_profile or {})
    policy = dict(control_policy or {})
    view = dict(view_policy or {})
    epistemic = dict(epistemic_policy or {})
    server = dict(server_profile or {})
    rs5 = dict(rs5_budget_state or {})

    requester_subject_id = str(request.get("requester_subject_id", "")).strip() or "subject.unknown"
    control_intent_id = str(request.get("control_intent_id", "")).strip()

    downgrades: List[dict] = []
    refusals: List[str] = []
    validation_extensions: dict = {}

    # 1) Validate entitlements.
    required_entitlements = _sorted_unique_strings(request_ext.get("required_entitlements"))
    authority_entitlements = set(_sorted_unique_strings(authority.get("entitlements")))
    missing_entitlements = [token for token in required_entitlements if token not in authority_entitlements]
    if missing_entitlements:
        refusals.append(REFUSAL_CTRL_ENTITLEMENT_MISSING)
        validation_extensions["missing_entitlements"] = list(missing_entitlements)

    # 2) Validate law profile process permission when requested.
    required_process_id = str(request_ext.get("required_process_id", "")).strip()
    if required_process_id:
        allowed_processes = set(_sorted_unique_strings(law.get("allowed_processes")))
        forbidden_processes = set(_sorted_unique_strings(law.get("forbidden_processes")))
        if required_process_id in forbidden_processes or (allowed_processes and required_process_id not in allowed_processes):
            refusals.append(REFUSAL_CTRL_FORBIDDEN_BY_LAW)
            validation_extensions["forbidden_process_id"] = required_process_id

    is_ranked = _is_ranked(server_profile=server, request_context=request_context)

    # 3) Abstraction axis.
    requested_al = _al_token(request_vector.get("abstraction_level_requested"))
    allowed_al = [token for token in _sorted_unique_strings(policy.get("allowed_abstraction_levels")) if token in _AL_RANK]
    resolved_al = requested_al
    if allowed_al and requested_al not in allowed_al:
        req_rank = int(_AL_RANK[requested_al])
        below_or_equal = sorted((token for token in allowed_al if _AL_RANK[token] <= req_rank), key=lambda token: _AL_RANK[token])
        if below_or_equal:
            resolved_al = below_or_equal[-1]
        else:
            resolved_al = sorted(allowed_al, key=lambda token: _AL_RANK[token])[0]
        _append_downgrade(
            downgrades,
            axis="abstraction",
            from_value=requested_al,
            to_value=resolved_al,
            reason_code=DOWNGRADE_POLICY,
            remediation_hint="remedy.ctrl.select_allowed_abstraction",
        )
    if is_ranked and resolved_al == "AL4":
        refusals.append(REFUSAL_CTRL_META_FORBIDDEN)

    # 4) View axis.
    requested_view = str(request_vector.get("view_requested", "")).strip() or DEFAULT_VIEW_POLICY_ID
    allowed_view = _sorted_unique_strings(
        view.get("allowed_view_policies") if isinstance(view.get("allowed_view_policies"), list) else policy.get("allowed_view_policies")
    )
    resolved_view = requested_view
    if allowed_view and requested_view not in allowed_view:
        resolved_view = _view_downgrade_target(allowed_view, requested_view) or allowed_view[0]
        if resolved_view:
            _append_downgrade(
                downgrades,
                axis="view",
                from_value=requested_view,
                to_value=resolved_view,
                reason_code=DOWNGRADE_POLICY,
                remediation_hint="remedy.ctrl.select_allowed_view",
            )
    forbid_freecam = bool(is_ranked or request_ext.get("forbid_freecam", False))
    if forbid_freecam and _view_mode_for_policy(resolved_view) == "freecam":
        fallback_view = _view_downgrade_target(allowed_view, resolved_view) or _first_non_freecam(allowed_view)
        if fallback_view and fallback_view != resolved_view:
            _append_downgrade(
                downgrades,
                axis="view",
                from_value=resolved_view,
                to_value=fallback_view,
                reason_code=DOWNGRADE_RANK_FAIRNESS if is_ranked else DOWNGRADE_POLICY,
                remediation_hint="remedy.ctrl.rank_use_diegetic_view" if is_ranked else "remedy.ctrl.select_allowed_view",
            )
            resolved_view = fallback_view
    if forbid_freecam and _view_mode_for_policy(resolved_view) == "freecam":
        refusals.append(REFUSAL_CTRL_VIEW_FORBIDDEN)

    # 5) Epistemic axis.
    requested_epistemic = (
        str(request_vector.get("epistemic_scope_requested", "")).strip()
        or str((_as_map(authority.get("epistemic_scope"))).get("scope_id", "")).strip()
        or DEFAULT_EPISTEMIC_SCOPE
    )
    allowed_epistemic = _sorted_unique_strings(
        epistemic.get("allowed_scope_ids") if isinstance(epistemic.get("allowed_scope_ids"), list) else epistemic.get("allowed_epistemic_scopes")
    )
    resolved_epistemic = requested_epistemic
    if allowed_epistemic and requested_epistemic not in allowed_epistemic:
        resolved_epistemic = allowed_epistemic[0]
        _append_downgrade(
            downgrades,
            axis="epistemic",
            from_value=requested_epistemic,
            to_value=resolved_epistemic,
            reason_code=DOWNGRADE_EPISTEMIC,
            remediation_hint="remedy.ctrl.reduce_epistemic_scope",
        )

    # 6) Fidelity axis.
    requested_fidelity = _fidelity_token(request_vector.get("fidelity_requested"))
    allowed_fidelity = [token for token in _sorted_unique_strings(policy.get("allowed_fidelity_ranges")) if token in _FIDELITY_RANK]
    if not allowed_fidelity:
        allowed_fidelity = list(_FIDELITY_LEVELS)
    resolved_fidelity = requested_fidelity

    micro_allowed = bool(request_ext.get("micro_allowed", True))
    micro_available = bool(request_ext.get("micro_available", True))
    max_fidelity = _fidelity_token(
        request_ext.get("max_fidelity")
        or rs5.get("max_fidelity")
        or _as_map(policy.get("extensions")).get("max_control_fidelity")
    )
    if max_fidelity in _FIDELITY_RANK and _FIDELITY_RANK[resolved_fidelity] > _FIDELITY_RANK[max_fidelity]:
        _append_downgrade(
            downgrades,
            axis="fidelity",
            from_value=resolved_fidelity,
            to_value=max_fidelity,
            reason_code=DOWNGRADE_BUDGET,
            remediation_hint="remedy.ctrl.reduce_requested_fidelity",
        )
        resolved_fidelity = max_fidelity

    fidelity_candidates = _fidelity_candidates(resolved_fidelity)
    if resolved_fidelity == "micro" and (not micro_allowed or not micro_available):
        fidelity_candidates = ["meso", "macro"]
    fidelity_candidates = [token for token in fidelity_candidates if token in allowed_fidelity]
    if not fidelity_candidates:
        resolved_candidate = _min_fidelity(requested=resolved_fidelity, allowed=allowed_fidelity)
        fidelity_candidates = [resolved_candidate]
    resolved_from_candidates = fidelity_candidates[0]
    if resolved_from_candidates != resolved_fidelity:
        if not micro_allowed:
            reason_code = DOWNGRADE_EPISTEMIC
            remediation_hint = "remedy.ctrl.expand_epistemic_scope"
        elif not micro_available:
            reason_code = DOWNGRADE_TARGET_NOT_AVAILABLE
            remediation_hint = "remedy.ctrl.select_available_micro_target"
        else:
            reason_code = DOWNGRADE_POLICY
            remediation_hint = "remedy.ctrl.select_allowed_fidelity"
        _append_downgrade(
            downgrades,
            axis="fidelity",
            from_value=resolved_fidelity,
            to_value=resolved_from_candidates,
            reason_code=reason_code,
            remediation_hint=remediation_hint,
        )
        resolved_fidelity = resolved_from_candidates
    if requested_fidelity == "micro" and resolved_fidelity != "micro" and bool(request_ext.get("micro_strict_refusal", False)):
        refusals.append(REFUSAL_CTRL_FIDELITY_DENIED)

    # 7) Budget axis (RS-5 envelope + deterministic fair-share).
    requested_budget = int(
        max(
            0,
            _to_int(
                request_vector.get("budget_requested", request_ext.get("budget_requested", rs5.get("requested_cost_units", 0))),
                0,
            ),
        )
    )
    max_budget_per_tick = int(max(0, _to_int(rs5.get("max_cost_units_per_tick", rs5.get("max_budget_units", 0)), 0)))
    zero_budget_means_unbounded = bool(request_ext.get("budget_zero_means_unbounded", False))
    tick = int(max(0, _to_int(rs5.get("tick", 0), 0)))
    tick_token = str(tick)

    runtime_budget_state = _as_map(rs5.get("runtime_budget_state"))
    used_by_tick = _as_map(runtime_budget_state.get("used_by_tick"))
    used_before = int(max(0, _to_int(used_by_tick.get(tick_token, 0), 0)))

    fairness_state = _as_map(rs5.get("fairness_state"))
    connected_subject_ids = _sorted_unique_strings(
        fairness_state.get("connected_subject_ids")
        if isinstance(fairness_state.get("connected_subject_ids"), list)
        else rs5.get("connected_subject_ids")
    )
    if requester_subject_id not in connected_subject_ids:
        connected_subject_ids.append(requester_subject_id)
    connected_subject_ids = sorted(set(connected_subject_ids))
    fair_share_cap = int(max_budget_per_tick // max(1, len(connected_subject_ids))) if (max_budget_per_tick > 0 and connected_subject_ids) else 0

    used_by_tick_subject = _as_map(fairness_state.get("used_by_tick_subject"))
    peer_usage = _as_map(used_by_tick_subject.get(tick_token))
    used_subject_before = int(max(0, _to_int(peer_usage.get(requester_subject_id, 0), 0)))

    if max_budget_per_tick <= 0:
        allocated_budget = int(requested_budget if zero_budget_means_unbounded else 0)
    else:
        total_available = int(max(0, max_budget_per_tick - used_before))
        if fair_share_cap > 0:
            subject_available = int(max(0, fair_share_cap - used_subject_before))
            allocated_budget = int(min(requested_budget, total_available, subject_available))
        else:
            allocated_budget = int(min(requested_budget, total_available))

    fidelity_cost_by_level = _as_map(request_ext.get("fidelity_cost_by_level"))
    if fidelity_cost_by_level:
        candidate_chain = _fidelity_candidates(resolved_fidelity)
        if resolved_fidelity == "micro" and (not micro_allowed or not micro_available):
            candidate_chain = ["meso", "macro"]
        candidate_chain = [token for token in candidate_chain if token in allowed_fidelity]
        if not candidate_chain:
            candidate_chain = [_min_fidelity(requested=resolved_fidelity, allowed=allowed_fidelity)]

        selected_fidelity = ""
        fallback_fidelity = ""
        for candidate in candidate_chain:
            fallback_fidelity = candidate
            candidate_cost = int(
                max(
                    0,
                    _to_int(
                        fidelity_cost_by_level.get(
                            candidate,
                            requested_budget if candidate == requested_fidelity else requested_budget,
                        ),
                        requested_budget,
                    ),
                )
            )
            if zero_budget_means_unbounded or candidate_cost <= allocated_budget:
                selected_fidelity = candidate
                break
        if not selected_fidelity:
            selected_fidelity = fallback_fidelity or candidate_chain[-1]
        if selected_fidelity != resolved_fidelity:
            _append_downgrade(
                downgrades,
                axis="fidelity",
                from_value=resolved_fidelity,
                to_value=selected_fidelity,
                reason_code=DOWNGRADE_BUDGET,
                remediation_hint="remedy.ctrl.reduce_requested_fidelity",
                extensions={
                    "allocated_budget": int(allocated_budget),
                },
            )
            resolved_fidelity = selected_fidelity

    budget_shortfall = allocated_budget != requested_budget
    if budget_shortfall:
        _append_downgrade(
            downgrades,
            axis="budget",
            from_value=str(requested_budget),
            to_value=str(allocated_budget),
            reason_code=DOWNGRADE_BUDGET,
            remediation_hint="remedy.ctrl.increase_budget_or_reduce_scope",
        )
        if bool(request_ext.get("budget_refuse_on_shortfall", False)):
            refusals.append(str(request_ext.get("budget_refusal_code", REFUSAL_CTRL_IR_COST_EXCEEDED)))

    used_after = int(used_before + allocated_budget)
    if max_budget_per_tick > 0:
        used_by_tick[tick_token] = used_after
    runtime_budget_state_out = {
        "used_by_tick": dict(
            (str(key), int(max(0, _to_int(value, 0))))
            for key, value in sorted(used_by_tick.items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
    }

    if connected_subject_ids:
        peer_usage[requester_subject_id] = int(max(0, used_subject_before + allocated_budget))
        used_by_tick_subject[tick_token] = dict(
            (str(key), int(max(0, _to_int(value, 0))))
            for key, value in sorted(peer_usage.items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
    fairness_state_out = {
        "connected_subject_ids": list(connected_subject_ids),
        "used_by_tick_subject": dict(
            (str(key), dict(value))
            for key, value in sorted(used_by_tick_subject.items(), key=lambda item: str(item[0]))
            if isinstance(value, Mapping)
        ),
    }

    resolved_vector = {
        "abstraction_level_resolved": str(resolved_al),
        "view_resolved": str(resolved_view),
        "epistemic_scope_resolved": str(resolved_epistemic),
        "fidelity_resolved": str(resolved_fidelity),
        "budget_allocated": int(allocated_budget),
    }
    if requested_budget > 0:
        resolved_vector["budget_requested"] = int(requested_budget)

    ordered_downgrades = sorted(
        downgrades,
        key=lambda row: (
            int(_AXIS_RANK.get(str(row.get("axis", "")), 999)),
            str(row.get("downgrade_id", "")),
        ),
    )
    refusal_codes = _dedupe_preserve_order(refusals)

    result = {
        "schema_version": "1.0.0",
        "resolved_vector": resolved_vector,
        "downgrade_entries": ordered_downgrades,
        "refusal_codes": list(refusal_codes),
        "deterministic_fingerprint": "",
        "extensions": {
            "axis_order": list(NEGOTIATION_AXIS_ORDER),
            "requester_subject_id": requester_subject_id,
            "control_intent_id": control_intent_id,
            "policy_ids_applied": _policy_id_rows(
                control_policy=policy,
                view_policy=view,
                epistemic_policy=epistemic,
                server_profile=server,
                request_context=request_context,
            ),
            "request_vector": dict(request_vector),
            "validation": dict(validation_extensions),
            "budget": {
                "tick": int(tick),
                "requested_units": int(requested_budget),
                "allocated_units": int(allocated_budget),
                "max_units_per_tick": int(max_budget_per_tick),
                "used_before": int(used_before),
                "used_after": int(used_after),
                "fair_share_cap": int(fair_share_cap),
                "used_by_subject_before": int(used_subject_before),
                "runtime_budget_state": runtime_budget_state_out,
                "fairness_state": fairness_state_out,
            },
        },
    }
    seed = dict(result)
    seed["deterministic_fingerprint"] = ""
    result["deterministic_fingerprint"] = canonical_sha256(seed)
    return result


def arbitrate_negotiation_requests(
    *,
    negotiation_requests: Sequence[Mapping[str, object]],
    rs5_budget_state: Mapping[str, object] | None,
    control_policy: Mapping[str, object],
    view_policy: Mapping[str, object] | None = None,
    epistemic_policy: Mapping[str, object] | None = None,
    server_profile: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    authority_context_by_subject: Mapping[str, Mapping[str, object]] | None = None,
    law_profile: Mapping[str, object] | None = None,
) -> dict:
    """Deterministically arbitrate multiple requests by subject_id then control_intent_id."""

    requests = [dict(row) for row in list(negotiation_requests or []) if isinstance(row, Mapping)]
    ordered_requests = sorted(
        requests,
        key=lambda row: (
            str(row.get("requester_subject_id", "")).strip(),
            str(row.get("control_intent_id", "")).strip(),
            canonical_sha256(row),
        ),
    )

    rs5_state = dict(rs5_budget_state or {})
    auth_by_subject = dict(authority_context_by_subject or {})
    results: List[dict] = []
    ordered_keys: List[str] = []
    for row in ordered_requests:
        requester_subject_id = str(row.get("requester_subject_id", "")).strip()
        control_intent_id = str(row.get("control_intent_id", "")).strip()
        authority_row = dict(auth_by_subject.get(requester_subject_id) or dict(authority_context or {}))
        negotiated = negotiate_request(
            negotiation_request=row,
            rs5_budget_state=rs5_state,
            control_policy=control_policy,
            view_policy=view_policy,
            epistemic_policy=epistemic_policy,
            server_profile=server_profile,
            authority_context=authority_row,
            law_profile=law_profile,
        )
        results.append(negotiated)
        ordered_keys.append("{}::{}".format(requester_subject_id, control_intent_id))
        budget_ext = _as_map(_as_map(negotiated.get("extensions")).get("budget"))
        rs5_state["runtime_budget_state"] = _as_map(budget_ext.get("runtime_budget_state"))
        rs5_state["fairness_state"] = _as_map(budget_ext.get("fairness_state"))

    output = {
        "schema_version": "1.0.0",
        "ordered_request_keys": list(ordered_keys),
        "results": list(results),
        "runtime_budget_state": _as_map(rs5_state.get("runtime_budget_state")),
        "fairness_state": _as_map(rs5_state.get("fairness_state")),
        "deterministic_fingerprint": "",
    }
    seed = dict(output)
    seed["deterministic_fingerprint"] = ""
    output["deterministic_fingerprint"] = canonical_sha256(seed)
    return output


__all__ = [
    "DOWNGRADE_BUDGET",
    "DOWNGRADE_EPISTEMIC",
    "DOWNGRADE_POLICY",
    "DOWNGRADE_RANK_FAIRNESS",
    "DOWNGRADE_TARGET_NOT_AVAILABLE",
    "NEGOTIATION_AXIS_ORDER",
    "REFUSAL_CTRL_ENTITLEMENT_MISSING",
    "REFUSAL_CTRL_FIDELITY_DENIED",
    "REFUSAL_CTRL_FORBIDDEN_BY_LAW",
    "REFUSAL_CTRL_IR_COST_EXCEEDED",
    "REFUSAL_CTRL_META_FORBIDDEN",
    "REFUSAL_CTRL_VIEW_FORBIDDEN",
    "arbitrate_negotiation_requests",
    "build_downgrade_entry",
    "build_negotiation_request",
    "negotiate_request",
]
