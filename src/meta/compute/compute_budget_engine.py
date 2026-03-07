"""META-COMPUTE0 deterministic compute budget engine."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_COMPUTE_INVALID_OWNER = "refusal.compute.invalid_owner"
REFUSAL_COMPUTE_BUDGET_EXCEEDED = "refusal.compute.budget_exceeded"
REFUSAL_COMPUTE_MEMORY_EXCEEDED = "refusal.compute.memory_exceeded"

_OWNER_KINDS = {"controller", "system", "process"}
_ACTIONS = {"none", "degrade", "defer", "refuse", "shutdown"}

_ACTION_TO_EXPLAIN = {
    "degrade": ("explain.compute_throttle", "compute.throttle"),
    "defer": ("explain.compute_throttle", "compute.throttle"),
    "refuse": ("explain.compute_refusal", "compute.refusal"),
    "shutdown": ("explain.compute_shutdown", "compute.shutdown"),
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_bool(value: object, default_value: bool = False) -> bool:
    if isinstance(value, bool):
        return bool(value)
    token = str(value or "").strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return bool(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _rows_from_registry(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
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


def build_compute_budget_profile_row(
    *,
    compute_profile_id: str,
    instruction_budget_per_tick: int,
    memory_budget_total: int,
    evaluation_cap_per_tick: int,
    degrade_policy_id: str,
    power_coupling_enabled: bool,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "compute_profile_id": _token(compute_profile_id),
        "instruction_budget_per_tick": int(max(0, _as_int(instruction_budget_per_tick, 0))),
        "memory_budget_total": int(max(0, _as_int(memory_budget_total, 0))),
        "evaluation_cap_per_tick": int(max(1, _as_int(evaluation_cap_per_tick, 1))),
        "degrade_policy_id": _token(degrade_policy_id),
        "power_coupling_enabled": bool(power_coupling_enabled),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (not payload["compute_profile_id"]) or (not payload["degrade_policy_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_compute_budget_profile_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: _token(item.get("compute_profile_id"))):
        payload = build_compute_budget_profile_row(
            compute_profile_id=_token(row.get("compute_profile_id")),
            instruction_budget_per_tick=_as_int(row.get("instruction_budget_per_tick"), 0),
            memory_budget_total=_as_int(row.get("memory_budget_total"), 0),
            evaluation_cap_per_tick=_as_int(row.get("evaluation_cap_per_tick"), 1),
            degrade_policy_id=_token(row.get("degrade_policy_id")),
            power_coupling_enabled=_as_bool(row.get("power_coupling_enabled"), False),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        key = _token(payload.get("compute_profile_id"))
        if key:
            out[key] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def compute_budget_profile_rows_by_id(rows: object) -> Dict[str, dict]:
    return {
        _token(row.get("compute_profile_id")): dict(row)
        for row in normalize_compute_budget_profile_rows(rows)
        if _token(row.get("compute_profile_id"))
    }


def compute_budget_profile_rows_by_id_from_registry(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return compute_budget_profile_rows_by_id(_rows_from_registry(payload, ("compute_budget_profiles",)))


def compute_degrade_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(payload, ("compute_degrade_policies",)):
        policy_id = _token(row.get("degrade_policy_id"))
        if policy_id:
            out[policy_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_compute_consumption_record_row(
    *,
    record_id: str,
    tick: int,
    owner_kind: str,
    owner_id: str,
    instruction_units_used: int,
    memory_units_used: int,
    throttled: bool,
    action_taken: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind = _token(owner_kind).lower()
    action = _token(action_taken).lower()
    payload = {
        "schema_version": "1.0.0",
        "record_id": _token(record_id),
        "tick": int(max(0, _as_int(tick, 0))),
        "owner_kind": kind,
        "owner_id": _token(owner_id),
        "instruction_units_used": int(max(0, _as_int(instruction_units_used, 0))),
        "memory_units_used": int(max(0, _as_int(memory_units_used, 0))),
        "throttled": bool(throttled),
        "action_taken": action,
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if kind not in _OWNER_KINDS:
        return {}
    if (not payload["record_id"]) or (not payload["owner_id"]) or (action not in _ACTIONS):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_compute_consumption_record_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (int(max(0, _as_int(item.get("tick", 0), 0))), _token(item.get("owner_id")), _token(item.get("record_id"))),
    ):
        payload = build_compute_consumption_record_row(
            record_id=_token(row.get("record_id")),
            tick=_as_int(row.get("tick"), 0),
            owner_kind=_token(row.get("owner_kind")),
            owner_id=_token(row.get("owner_id")),
            instruction_units_used=_as_int(row.get("instruction_units_used"), 0),
            memory_units_used=_as_int(row.get("memory_units_used"), 0),
            throttled=_as_bool(row.get("throttled"), False),
            action_taken=_token(row.get("action_taken") or "none"),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        key = _token(payload.get("record_id"))
        if key:
            out[key] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def _policy_for_profile(*, profile_row: Mapping[str, object], policy_rows_by_id: Mapping[str, object]) -> dict:
    profile = _as_map(profile_row)
    policy_id = _token(profile.get("degrade_policy_id"))
    policy = dict(_as_map(policy_rows_by_id).get(policy_id) or {})
    if policy:
        return policy
    return {
        "degrade_policy_id": "degrade.default_order",
        "order": [
            "reduce_frequency",
            "degrade_representation",
            "cap_evaluations",
            "refuse_noncritical",
            "shutdown_if_required",
        ],
        "tick_bucket_stride": 2,
        "allow_representation_degrade": True,
        "fail_safe_on_critical_overrun": False,
    }


def _start_tick_state(*, tick: int, state: Mapping[str, object] | None) -> dict:
    src = _as_map(state)
    current_tick = int(max(0, _as_int(src.get("tick", -1), -1)))
    if current_tick != int(max(0, _as_int(tick, 0))):
        return {
            "tick": int(max(0, _as_int(tick, 0))),
            "instruction_used": 0,
            "memory_used": int(max(0, _as_int(src.get("memory_used", 0), 0))),
            "evaluated_count": 0,
            "decision_log_rows": [],
            "consumption_record_rows": [],
            "explain_artifact_rows": [],
            "throttled_owner_ids": [],
            "deferred_owner_ids": [],
            "refused_owner_ids": [],
            "shutdown_owner_ids": [],
        }
    dst = {
        "tick": current_tick,
        "instruction_used": int(max(0, _as_int(src.get("instruction_used", 0), 0))),
        "memory_used": int(max(0, _as_int(src.get("memory_used", 0), 0))),
        "evaluated_count": int(max(0, _as_int(src.get("evaluated_count", 0), 0))),
        "decision_log_rows": [dict(row) for row in _as_list(src.get("decision_log_rows")) if isinstance(row, Mapping)],
        "consumption_record_rows": [dict(row) for row in _as_list(src.get("consumption_record_rows")) if isinstance(row, Mapping)],
        "explain_artifact_rows": [dict(row) for row in _as_list(src.get("explain_artifact_rows")) if isinstance(row, Mapping)],
        "throttled_owner_ids": [str(item) for item in _as_list(src.get("throttled_owner_ids")) if _token(item)],
        "deferred_owner_ids": [str(item) for item in _as_list(src.get("deferred_owner_ids")) if _token(item)],
        "refused_owner_ids": [str(item) for item in _as_list(src.get("refused_owner_ids")) if _token(item)],
        "shutdown_owner_ids": [str(item) for item in _as_list(src.get("shutdown_owner_ids")) if _token(item)],
    }
    return dst


def request_compute(
    *,
    current_tick: int,
    owner_kind: str,
    owner_id: str,
    instruction_units: int,
    memory_units: int = 0,
    owner_priority: int = 100,
    critical: bool = False,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    kind = _token(owner_kind).lower()
    owner = _token(owner_id)
    requested_instruction = int(max(0, _as_int(instruction_units, 0)))
    requested_memory = int(max(0, _as_int(memory_units, 0)))
    priority = int(max(0, _as_int(owner_priority, 100)))
    runtime_state = _start_tick_state(tick=tick, state=compute_runtime_state)

    if (kind not in _OWNER_KINDS) or (not owner):
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPUTE_INVALID_OWNER,
            "action_taken": "refuse",
            "approved_instruction_units": 0,
            "approved_memory_units": 0,
            "throttled": False,
            "runtime_state": runtime_state,
            "decision_log_row": {
                "tick": tick,
                "owner_id": owner,
                "owner_kind": kind,
                "priority": priority,
                "decision_kind": "compute_refusal",
                "reason_code": REFUSAL_COMPUTE_INVALID_OWNER,
                "status": "refused",
                "deterministic_fingerprint": canonical_sha256({"tick": tick, "owner_id": owner, "reason_code": REFUSAL_COMPUTE_INVALID_OWNER}),
            },
            "consumption_record_row": {},
        }

    profiles_by_id = compute_budget_profile_rows_by_id_from_registry(compute_budget_profile_registry_payload)
    profile = dict(profiles_by_id.get(_token(compute_budget_profile_id)) or profiles_by_id.get("compute.default") or {})
    if not profile:
        profile = build_compute_budget_profile_row(
            compute_profile_id="compute.default",
            instruction_budget_per_tick=2048,
            memory_budget_total=65536,
            evaluation_cap_per_tick=256,
            degrade_policy_id="degrade.default_order",
            power_coupling_enabled=False,
            deterministic_fingerprint="",
            extensions={"source": "META-COMPUTE0-3"},
        )

    policy = _policy_for_profile(
        profile_row=profile,
        policy_rows_by_id=compute_degrade_policy_rows_by_id(compute_degrade_policy_registry_payload),
    )

    instruction_budget = int(max(0, _as_int(profile.get("instruction_budget_per_tick"), 0)))
    memory_budget = int(max(0, _as_int(profile.get("memory_budget_total"), 0)))
    eval_cap = int(max(1, _as_int(profile.get("evaluation_cap_per_tick"), 1)))
    stride = int(max(1, _as_int(policy.get("tick_bucket_stride"), 2)))
    allow_degrade = bool(_as_bool(policy.get("allow_representation_degrade"), True))
    fail_safe = bool(_as_bool(policy.get("fail_safe_on_critical_overrun"), False))

    used_instruction = int(max(0, _as_int(runtime_state.get("instruction_used", 0), 0)))
    used_memory = int(max(0, _as_int(runtime_state.get("memory_used", 0), 0)))
    evaluated_count = int(max(0, _as_int(runtime_state.get("evaluated_count", 0), 0)))
    remaining_instruction = int(max(0, instruction_budget - used_instruction))

    action_taken = "none"
    throttled = False
    approved_instruction = 0
    approved_memory = 0
    result = "complete"
    reason_code = ""

    if requested_memory > 0 and int(used_memory + requested_memory) > memory_budget:
        if bool(critical) and fail_safe:
            action_taken = "shutdown"
            result = "shutdown"
        else:
            action_taken = "refuse"
            result = "refused"
        reason_code = REFUSAL_COMPUTE_MEMORY_EXCEEDED
    elif evaluated_count >= eval_cap:
        action_taken = "defer"
        throttled = True
        result = "deferred"
        reason_code = REFUSAL_COMPUTE_BUDGET_EXCEEDED
    elif requested_instruction <= remaining_instruction:
        action_taken = "none"
        result = "complete"
        approved_instruction = requested_instruction
        approved_memory = requested_memory
    else:
        bucket = int(canonical_sha256({"owner_id": owner, "stream": "meta.compute.bucket"})[:8], 16) % stride
        if stride > 1 and (tick % stride) != bucket:
            action_taken = "defer"
            throttled = True
            result = "deferred"
            reason_code = REFUSAL_COMPUTE_BUDGET_EXCEEDED
        elif allow_degrade and remaining_instruction > 0:
            action_taken = "degrade"
            throttled = True
            result = "throttled"
            approved_instruction = int(max(1, min(remaining_instruction, max(1, requested_instruction // 2))))
            approved_memory = requested_memory
            reason_code = REFUSAL_COMPUTE_BUDGET_EXCEEDED
        elif not bool(critical):
            action_taken = "refuse"
            result = "refused"
            reason_code = REFUSAL_COMPUTE_BUDGET_EXCEEDED
        elif fail_safe:
            action_taken = "shutdown"
            result = "shutdown"
            reason_code = REFUSAL_COMPUTE_BUDGET_EXCEEDED
        else:
            action_taken = "defer"
            throttled = True
            result = "deferred"
            reason_code = REFUSAL_COMPUTE_BUDGET_EXCEEDED

    if approved_instruction > 0:
        runtime_state["instruction_used"] = int(max(0, used_instruction + approved_instruction))
        runtime_state["evaluated_count"] = int(max(0, evaluated_count + 1))
    if approved_memory > 0:
        runtime_state["memory_used"] = int(max(0, used_memory + approved_memory))

    if action_taken in {"defer", "degrade"}:
        runtime_state["throttled_owner_ids"] = sorted(set(list(runtime_state.get("throttled_owner_ids") or []) + [owner]))
    if action_taken == "defer":
        runtime_state["deferred_owner_ids"] = sorted(set(list(runtime_state.get("deferred_owner_ids") or []) + [owner]))
    if action_taken == "refuse":
        runtime_state["refused_owner_ids"] = sorted(set(list(runtime_state.get("refused_owner_ids") or []) + [owner]))
    if action_taken == "shutdown":
        runtime_state["shutdown_owner_ids"] = sorted(set(list(runtime_state.get("shutdown_owner_ids") or []) + [owner]))

    record_id = "record.compute.consumption.{}".format(
        canonical_sha256(
            {
                "tick": tick,
                "owner_kind": kind,
                "owner_id": owner,
                "requested_instruction": requested_instruction,
                "approved_instruction": approved_instruction,
                "requested_memory": requested_memory,
                "approved_memory": approved_memory,
                "action_taken": action_taken,
            }
        )[:16]
    )
    record_row = build_compute_consumption_record_row(
        record_id=record_id,
        tick=tick,
        owner_kind=kind,
        owner_id=owner,
        instruction_units_used=int(max(0, approved_instruction)),
        memory_units_used=int(max(0, approved_memory)),
        throttled=bool(throttled),
        action_taken=action_taken,
        deterministic_fingerprint="",
        extensions={
            "requested_instruction_units": requested_instruction,
            "requested_memory_units": requested_memory,
            "compute_profile_id": _token(profile.get("compute_profile_id")) or _token(compute_budget_profile_id),
            "degrade_policy_id": _token(policy.get("degrade_policy_id")),
            "critical": bool(critical),
            "reason_code": reason_code or None,
            "power_coupling_enabled": bool(_as_bool(profile.get("power_coupling_enabled"), False)),
            "owner_priority": int(priority),
        },
    )
    decision_log_row = {
        "tick": int(tick),
        "owner_kind": kind,
        "owner_id": owner,
        "priority": int(priority),
        "decision_kind": "compute_budget",
        "status": str(result),
        "action_taken": str(action_taken),
        "reason_code": str(reason_code or ""),
        "approved_instruction_units": int(max(0, approved_instruction)),
        "approved_memory_units": int(max(0, approved_memory)),
        "compute_profile_id": _token(profile.get("compute_profile_id")) or _token(compute_budget_profile_id),
        "deterministic_fingerprint": canonical_sha256(
            {
                "tick": tick,
                "owner_kind": kind,
                "owner_id": owner,
                "status": result,
                "action_taken": action_taken,
                "reason_code": reason_code,
                "approved_instruction_units": approved_instruction,
            }
        ),
    }
    explain_artifact_row = {}
    explain_contract_id, event_kind_id = _ACTION_TO_EXPLAIN.get(str(action_taken), ("", ""))
    if explain_contract_id:
        explain_artifact_row = {
            "artifact_type_id": "artifact.explain.compute_budget",
            "owner_kind": str(kind),
            "owner_id": str(owner),
            "tick": int(tick),
            "action_taken": str(action_taken),
            "reason_code": str(reason_code or ""),
            "explain_contract_id": str(explain_contract_id),
            "event_kind_id": str(event_kind_id),
            "visibility_policy": "policy.epistemic.inspector",
            "deterministic_fingerprint": canonical_sha256(
                {
                    "owner_kind": kind,
                    "owner_id": owner,
                    "tick": tick,
                    "action_taken": action_taken,
                    "reason_code": reason_code,
                    "explain_contract_id": explain_contract_id,
                    "event_kind_id": event_kind_id,
                }
            ),
            "extensions": {
                "source": "META-COMPUTE0-6",
                "compute_profile_id": _token(profile.get("compute_profile_id")) or _token(compute_budget_profile_id),
                "degrade_policy_id": _token(policy.get("degrade_policy_id")),
            },
        }
    runtime_state["consumption_record_rows"] = normalize_compute_consumption_record_rows(
        list(runtime_state.get("consumption_record_rows") or []) + [record_row]
    )
    runtime_state["decision_log_rows"] = sorted(
        [dict(row) for row in list(runtime_state.get("decision_log_rows") or []) if isinstance(row, Mapping)] + [decision_log_row],
        key=lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), _token(row.get("owner_id")), _token(row.get("decision_kind"))),
    )
    if explain_artifact_row:
        runtime_state["explain_artifact_rows"] = sorted(
            [
                dict(row)
                for row in list(runtime_state.get("explain_artifact_rows") or [])
                if isinstance(row, Mapping)
            ]
            + [dict(explain_artifact_row)],
            key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                _token(row.get("owner_id")),
                _token(row.get("explain_contract_id")),
                _token(row.get("action_taken")),
            ),
        )
    runtime_state["deterministic_fingerprint"] = canonical_sha256(dict(runtime_state, deterministic_fingerprint=""))

    return {
        "result": str(result),
        "reason_code": str(reason_code or ""),
        "action_taken": str(action_taken),
        "throttled": bool(throttled),
        "approved_instruction_units": int(max(0, approved_instruction)),
        "approved_memory_units": int(max(0, approved_memory)),
        "compute_profile_row": dict(profile),
        "degrade_policy_row": dict(policy),
        "consumption_record_row": dict(record_row),
        "decision_log_row": dict(decision_log_row),
        "explain_artifact_row": dict(explain_artifact_row),
        "runtime_state": dict(runtime_state),
    }


def evaluate_compute_budget_tick(
    *,
    current_tick: int,
    owner_rows: object,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    compute_budget_profile_id: str = "compute.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    sorted_owners = sorted(
        [dict(row) for row in _as_list(owner_rows) if isinstance(row, Mapping)],
        key=lambda row: (int(max(0, _as_int(row.get("priority", 100), 100))), _token(row.get("owner_id"))),
    )
    state = _start_tick_state(tick=tick, state=compute_runtime_state)
    decisions: List[dict] = []
    records: List[dict] = []
    explain_rows: List[dict] = []
    for owner in sorted_owners:
        decision = request_compute(
            current_tick=tick,
            owner_kind=_token(owner.get("owner_kind") or "controller"),
            owner_id=_token(owner.get("owner_id")),
            instruction_units=int(max(0, _as_int(owner.get("instruction_units", 0), 0))),
            memory_units=int(max(0, _as_int(owner.get("memory_units", 0), 0))),
            owner_priority=int(max(0, _as_int(owner.get("priority", 100), 100))),
            critical=bool(_as_bool(owner.get("critical", False), False)),
            compute_runtime_state=state,
            compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
            compute_budget_profile_id=str(compute_budget_profile_id or "compute.default"),
            compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        )
        state = dict(decision.get("runtime_state") or state)
        decisions.append(dict(decision))
        record_row = _as_map(decision.get("consumption_record_row"))
        if record_row:
            records.append(record_row)
        explain_row = _as_map(decision.get("explain_artifact_row"))
        if explain_row:
            explain_rows.append(explain_row)

    hash_chain = canonical_sha256(
        [
            {
                "record_id": _token(row.get("record_id")),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "owner_kind": _token(row.get("owner_kind")),
                "owner_id": _token(row.get("owner_id")),
                "instruction_units_used": int(max(0, _as_int(row.get("instruction_units_used", 0), 0))),
                "memory_units_used": int(max(0, _as_int(row.get("memory_units_used", 0), 0))),
                "action_taken": _token(row.get("action_taken")),
            }
            for row in normalize_compute_consumption_record_rows(records)
        ]
    )

    return {
        "result": "complete",
        "tick": int(tick),
        "compute_budget_profile_id": _token(compute_budget_profile_id) or "compute.default",
        "owner_count": int(len(sorted_owners)),
        "decision_rows": decisions,
        "compute_consumption_record_rows": normalize_compute_consumption_record_rows(records),
        "compute_explain_artifact_rows": [
            dict(row)
            for row in sorted(
                (dict(item) for item in explain_rows if isinstance(item, Mapping)),
                key=lambda item: (
                    int(max(0, _as_int(item.get("tick", 0), 0))),
                    _token(item.get("owner_id")),
                    _token(item.get("explain_contract_id")),
                ),
            )
        ],
        "runtime_state": dict(state),
        "compute_consumption_hash_chain": str(hash_chain),
        "deterministic_fingerprint": canonical_sha256(
            {
                "tick": tick,
                "owner_count": len(sorted_owners),
                "compute_consumption_hash_chain": hash_chain,
                "runtime_state": _as_map(state),
            }
        ),
    }


__all__ = [
    "REFUSAL_COMPUTE_INVALID_OWNER",
    "REFUSAL_COMPUTE_BUDGET_EXCEEDED",
    "REFUSAL_COMPUTE_MEMORY_EXCEEDED",
    "build_compute_budget_profile_row",
    "normalize_compute_budget_profile_rows",
    "compute_budget_profile_rows_by_id",
    "compute_budget_profile_rows_by_id_from_registry",
    "compute_degrade_policy_rows_by_id",
    "build_compute_consumption_record_row",
    "normalize_compute_consumption_record_rows",
    "request_compute",
    "evaluate_compute_budget_tick",
]
