"""Deterministic conservation/exception ledger helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


MODE_ENFORCE_STRICT = "enforce_strict"
MODE_ENFORCE_LOCAL = "enforce_local"
MODE_ALLOW_WITH_LEDGER = "allow_with_ledger"
MODE_TRACK_ONLY = "track_only"
MODE_IGNORE = "ignore"

_VALID_MODES = {
    MODE_ENFORCE_STRICT,
    MODE_ENFORCE_LOCAL,
    MODE_ALLOW_WITH_LEDGER,
    MODE_TRACK_ONLY,
    MODE_IGNORE,
}

_REMEDIATION_HINTS = [
    "enable exception type in physics profile",
    "switch contract set",
    "use meta-law override in private universe",
]


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(items or []) if str(item).strip()))


def _shard_id(policy_context: dict) -> str:
    token = str((policy_context or {}).get("active_shard_id", "")).strip()
    return token or "shard.0"


def _physics_profile_id(policy_context: dict) -> str:
    token = str((policy_context or {}).get("physics_profile_id", "")).strip()
    return token or "physics.null"


def _profile_row(policy_context: dict) -> dict:
    requested = _physics_profile_id(policy_context)
    registry = dict((policy_context or {}).get("universe_physics_profile_registry") or {})
    rows = registry.get("physics_profiles")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("physics_profile_id", ""))):
        if str(row.get("physics_profile_id", "")).strip() == requested:
            return dict(row)
    return {}


def _contract_set_row(policy_context: dict, contract_set_id: str) -> dict:
    registry = dict((policy_context or {}).get("conservation_contract_set_registry") or {})
    rows = registry.get("contract_sets")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("contract_set_id", ""))):
        if str(row.get("contract_set_id", "")).strip() == str(contract_set_id).strip():
            return dict(row)
    return {}


def _quantity_ids(policy_context: dict) -> List[str]:
    registry = dict((policy_context or {}).get("quantity_registry") or {})
    rows = registry.get("quantities")
    if not isinstance(rows, list):
        return []
    out = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("quantity_id", ""))):
        token = str(row.get("quantity_id", "")).strip()
        if token:
            out.append(token)
    return out


def _exception_type_ids(policy_context: dict) -> List[str]:
    registry = dict((policy_context or {}).get("exception_type_registry") or {})
    rows = registry.get("exception_types")
    if not isinstance(rows, list):
        return []
    out = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("exception_type_id", ""))):
        token = str(row.get("exception_type_id", "")).strip()
        if token:
            out.append(token)
    return out


def _runtime_by_shard(policy_context: dict) -> dict:
    if not isinstance(policy_context, dict):
        return {}
    rows = policy_context.get("conservation_runtime_by_shard")
    if not isinstance(rows, dict):
        rows = {}
        policy_context["conservation_runtime_by_shard"] = rows
    return rows


def _mode_row(contract_set_row: dict, quantity_id: str) -> dict:
    rows = contract_set_row.get("quantities")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("quantity_id", ""))):
        if str(row.get("quantity_id", "")).strip() == str(quantity_id).strip():
            return dict(row)
    return {}


def _new_runtime(policy_context: dict, shard_id: str) -> dict:
    profile = _profile_row(policy_context)
    profile_id = _physics_profile_id(policy_context)
    if profile:
        profile_id = str(profile.get("physics_profile_id", "")).strip() or profile_id
    contract_set_id = str((profile or {}).get("conservation_contract_set_id", "")).strip() or "contracts.null"
    contract_set = _contract_set_row(policy_context, contract_set_id=contract_set_id)

    quantity_ids = _quantity_ids(policy_context)
    exception_types = _exception_type_ids(policy_context)
    allowed_profile_exception_types = _sorted_tokens((profile or {}).get("allowed_exception_types") or [])

    modes: Dict[str, dict] = {}
    for quantity_id in quantity_ids:
        row = _mode_row(contract_set, quantity_id=quantity_id)
        mode = str(row.get("mode", MODE_IGNORE)).strip()
        if mode not in _VALID_MODES:
            mode = MODE_IGNORE
        modes[quantity_id] = {
            "mode": mode,
            "tolerance": int(_as_int(row.get("tolerance", 0), 0)),
            "allowed_exception_types": _sorted_tokens(list(row.get("allowed_exception_types") or [])),
            "notes": str(row.get("notes", "")).strip(),
        }

    return {
        "schema_version": "1.0.0",
        "shard_id": str(shard_id),
        "physics_profile_id": profile_id,
        "contract_set_id": contract_set_id,
        "pack_lock_hash": str((policy_context or {}).get("pack_lock_hash", "")).strip(),
        "known_quantity_ids": list(quantity_ids),
        "known_exception_type_ids": list(exception_types),
        "allowed_profile_exception_types": list(allowed_profile_exception_types),
        "quantity_modes": modes,
        "previous_ledger_hash": "",
        "last_ledger_hash": "",
        "last_ledger_tick": -1,
        "last_ledger": {},
        "ledger_rows": [],
        "pending_entries": [],
        "pending_total_deltas": {},
        "pending_unaccounted_deltas": {},
    }


def resolve_conservation_runtime(policy_context: dict | None) -> dict:
    if not isinstance(policy_context, dict):
        return {}
    shard_id = _shard_id(policy_context)
    runtime_by_shard = _runtime_by_shard(policy_context)
    row = runtime_by_shard.get(shard_id)
    if not isinstance(row, dict):
        row = _new_runtime(policy_context, shard_id=shard_id)
        runtime_by_shard[shard_id] = row
    return row


def begin_process_accounting(policy_context: dict | None, process_id: str = "") -> dict:
    runtime = resolve_conservation_runtime(policy_context)
    if not runtime:
        return {}
    runtime["pending_entries"] = []
    runtime["pending_total_deltas"] = {}
    runtime["pending_unaccounted_deltas"] = {}
    runtime["pending_process_id"] = str(process_id or "")
    return runtime


def _increment_delta(bucket: dict, quantity_id: str, delta: int) -> None:
    token = str(quantity_id).strip()
    if not token:
        return
    current = _as_int(bucket.get(token, 0), 0)
    bucket[token] = int(current + int(delta))


def emit_exception(
    policy_context: dict | None,
    *,
    quantity_id: str,
    delta: int,
    exception_type_id: str,
    domain_id: str,
    process_id: str,
    reason_code: str,
    evidence: List[str] | None = None,
) -> None:
    runtime = resolve_conservation_runtime(policy_context)
    if not runtime:
        return
    rows = list(runtime.get("pending_entries") or [])
    row = {
        "quantity_id": str(quantity_id).strip(),
        "delta": int(_as_int(delta, 0)),
        "exception_type_id": str(exception_type_id).strip(),
        "domain_id": str(domain_id).strip(),
        "process_id": str(process_id).strip(),
        "reason_code": str(reason_code).strip(),
        "evidence": [str(item)[:160] for item in list(evidence or []) if str(item).strip()],
    }
    rows.append(row)
    runtime["pending_entries"] = rows
    _increment_delta(runtime["pending_total_deltas"], str(quantity_id), int(row["delta"]))


def record_unaccounted_delta(
    policy_context: dict | None,
    *,
    quantity_id: str,
    delta: int,
) -> None:
    runtime = resolve_conservation_runtime(policy_context)
    if not runtime:
        return
    _increment_delta(runtime["pending_total_deltas"], str(quantity_id), int(_as_int(delta, 0)))
    _increment_delta(runtime["pending_unaccounted_deltas"], str(quantity_id), int(_as_int(delta, 0)))


def _entry_sort_key(row: dict) -> Tuple[str, str, str, int, str]:
    return (
        str(row.get("quantity_id", "")),
        str(row.get("process_id", "")),
        str(row.get("exception_type_id", "")),
        int(_as_int(row.get("delta", 0), 0)),
        str(row.get("reason_code", "")),
    )


def _entry_payload(
    *,
    shard_id: str,
    tick: int,
    sequence: int,
    row: dict,
) -> dict:
    quantity_id = str(row.get("quantity_id", "")).strip()
    process_id = str(row.get("process_id", "")).strip()
    exception_type_id = str(row.get("exception_type_id", "")).strip()
    delta = int(_as_int(row.get("delta", 0), 0))
    entry_id = canonical_sha256(
        {
            "tick": int(tick),
            "shard_id": str(shard_id),
            "quantity_id": quantity_id,
            "process_id": process_id,
            "exception_type_id": exception_type_id,
            "delta": int(delta),
            "sequence": int(sequence),
        }
    )
    fingerprint = canonical_sha256(
        {
            "entry_id": entry_id,
            "tick": int(tick),
            "shard_id": str(shard_id),
            "quantity_id": quantity_id,
            "exception_type_id": exception_type_id,
            "domain_id": str(row.get("domain_id", "")),
            "process_id": process_id,
            "delta": int(delta),
            "reason_code": str(row.get("reason_code", "")),
            "evidence": list(row.get("evidence") or []),
        }
    )
    return {
        "entry_id": entry_id,
        "tick": int(tick),
        "shard_id": str(shard_id),
        "quantity_id": quantity_id,
        "exception_type_id": exception_type_id,
        "domain_id": str(row.get("domain_id", "")),
        "process_id": process_id,
        "delta": int(delta),
        "reason_code": str(row.get("reason_code", "")),
        "evidence": list(row.get("evidence") or []),
        "deterministic_fingerprint": fingerprint,
    }


def _mode_for_quantity(runtime: dict, quantity_id: str) -> dict:
    rows = dict(runtime.get("quantity_modes") or {})
    row = rows.get(str(quantity_id))
    if isinstance(row, dict):
        mode = str(row.get("mode", MODE_IGNORE)).strip()
        if mode not in _VALID_MODES:
            mode = MODE_IGNORE
        return {
            "mode": mode,
            "tolerance": int(_as_int(row.get("tolerance", 0), 0)),
            "allowed_exception_types": _sorted_tokens(list(row.get("allowed_exception_types") or [])),
        }
    return {"mode": MODE_IGNORE, "tolerance": 0, "allowed_exception_types": []}


def _quantity_refusal(
    *,
    reason_code: str,
    quantity_id: str,
    mode: str,
    net_delta: int,
    tolerance: int,
    unaccounted_delta: int,
) -> dict:
    return {
        "result": "refused",
        "reason_code": str(reason_code),
        "reason": "conservation contract violation",
        "remediation_hints": list(_REMEDIATION_HINTS),
        "details": {
            "quantity_id": str(quantity_id),
            "mode": str(mode),
            "net_delta": int(net_delta),
            "tolerance": int(tolerance),
            "unaccounted_delta": int(unaccounted_delta),
        },
    }


def _evaluate_quantity(
    *,
    runtime: dict,
    quantity_id: str,
    net_delta: int,
    logged_delta: int,
    unaccounted_delta: int,
    entry_types: List[str],
) -> dict:
    mode_row = _mode_for_quantity(runtime, quantity_id=quantity_id)
    mode = str(mode_row.get("mode", MODE_IGNORE))
    tolerance = int(_as_int(mode_row.get("tolerance", 0), 0))
    allowed_exception_types = set(_sorted_tokens(list(mode_row.get("allowed_exception_types") or [])))
    allowed_profile_exception_types = set(_sorted_tokens(list(runtime.get("allowed_profile_exception_types") or [])))
    entry_type_set = set(_sorted_tokens(entry_types))
    disallowed_by_mode = sorted(
        token for token in entry_type_set if token and token not in allowed_exception_types
    )
    disallowed_by_profile = sorted(
        token
        for token in entry_type_set
        if token and allowed_profile_exception_types and token not in allowed_profile_exception_types
    )

    if mode == MODE_IGNORE:
        return {"result": "complete"}

    if mode in (MODE_ENFORCE_STRICT, MODE_ENFORCE_LOCAL):
        if disallowed_by_mode or disallowed_by_profile:
            return _quantity_refusal(
                reason_code="refusal.conservation_violation.{}".format(quantity_id),
                quantity_id=quantity_id,
                mode=mode,
                net_delta=net_delta,
                tolerance=tolerance,
                unaccounted_delta=unaccounted_delta,
            )
        if int(unaccounted_delta) != 0:
            return _quantity_refusal(
                reason_code="refusal.conservation_violation.{}".format(quantity_id),
                quantity_id=quantity_id,
                mode=mode,
                net_delta=net_delta,
                tolerance=tolerance,
                unaccounted_delta=unaccounted_delta,
            )
        if abs(int(net_delta)) > abs(int(tolerance)):
            return _quantity_refusal(
                reason_code="refusal.conservation_violation.{}".format(quantity_id),
                quantity_id=quantity_id,
                mode=mode,
                net_delta=net_delta,
                tolerance=tolerance,
                unaccounted_delta=unaccounted_delta,
            )
        return {"result": "complete"}

    if mode == MODE_ALLOW_WITH_LEDGER:
        if disallowed_by_mode or disallowed_by_profile:
            return _quantity_refusal(
                reason_code="refusal.conservation_unaccounted",
                quantity_id=quantity_id,
                mode=mode,
                net_delta=net_delta,
                tolerance=tolerance,
                unaccounted_delta=unaccounted_delta,
            )
        if int(unaccounted_delta) != 0:
            return _quantity_refusal(
                reason_code="refusal.conservation_unaccounted",
                quantity_id=quantity_id,
                mode=mode,
                net_delta=net_delta,
                tolerance=tolerance,
                unaccounted_delta=unaccounted_delta,
            )
        if int(net_delta) != int(logged_delta):
            return _quantity_refusal(
                reason_code="refusal.conservation_unaccounted",
                quantity_id=quantity_id,
                mode=mode,
                net_delta=net_delta,
                tolerance=tolerance,
                unaccounted_delta=unaccounted_delta,
            )
        return {"result": "complete"}

    # track_only always records and never refuses.
    return {"result": "complete"}


def _build_totals(
    runtime: dict,
    total_deltas: dict,
) -> List[dict]:
    known = set(_sorted_tokens(runtime.get("known_quantity_ids") or []))
    known.update(str(token).strip() for token in (total_deltas or {}).keys() if str(token).strip())
    rows = []
    for quantity_id in sorted(known):
        mode = str(_mode_for_quantity(runtime, quantity_id=quantity_id).get("mode", MODE_IGNORE))
        if mode == MODE_IGNORE:
            continue
        rows.append(
            {
                "quantity_id": str(quantity_id),
                "net_delta": int(_as_int((total_deltas or {}).get(quantity_id, 0), 0)),
            }
        )
    return rows


def _ledger_hash_payload(ledger: dict) -> dict:
    payload = dict(ledger)
    payload.pop("ledger_hash", None)
    return payload


def _update_runtime_after_finalize(runtime: dict, ledger: dict) -> None:
    runtime["last_ledger_hash"] = str(ledger.get("ledger_hash", ""))
    runtime["previous_ledger_hash"] = str(ledger.get("ledger_hash", ""))
    runtime["last_ledger_tick"] = int(_as_int(ledger.get("tick", -1), -1))
    runtime["last_ledger"] = dict(ledger)
    rows = list(runtime.get("ledger_rows") or [])
    rows.append(dict(ledger))
    rows = sorted(
        (dict(item) for item in rows if isinstance(item, dict)),
        key=lambda item: (
            int(_as_int(item.get("tick", 0), 0)),
            str(item.get("shard_id", "")),
            str(item.get("ledger_hash", "")),
        ),
    )
    runtime["ledger_rows"] = rows[-256:]


def finalize_process_accounting(
    policy_context: dict | None,
    *,
    tick: int,
    process_id: str,
) -> dict:
    runtime = resolve_conservation_runtime(policy_context)
    if not runtime:
        return {"result": "complete", "ledger_hash": "", "ledger": {}}

    shard_id = str(runtime.get("shard_id", _shard_id(policy_context or {})))
    pending_entries = sorted((dict(row) for row in list(runtime.get("pending_entries") or []) if isinstance(row, dict)), key=_entry_sort_key)
    pending_total_deltas = dict(runtime.get("pending_total_deltas") or {})
    pending_unaccounted_deltas = dict(runtime.get("pending_unaccounted_deltas") or {})

    entries = []
    for index, row in enumerate(pending_entries, start=1):
        entries.append(_entry_payload(shard_id=shard_id, tick=int(tick), sequence=int(index), row=row))

    logged_by_quantity: Dict[str, int] = {}
    entry_types_by_quantity: Dict[str, List[str]] = {}
    for row in entries:
        quantity_id = str(row.get("quantity_id", "")).strip()
        if not quantity_id:
            continue
        _increment_delta(logged_by_quantity, quantity_id, int(_as_int(row.get("delta", 0), 0)))
        entry_types = list(entry_types_by_quantity.get(quantity_id) or [])
        entry_types.append(str(row.get("exception_type_id", "")).strip())
        entry_types_by_quantity[quantity_id] = entry_types

    quantities_to_evaluate = set(_sorted_tokens(runtime.get("known_quantity_ids") or []))
    quantities_to_evaluate.update(str(token).strip() for token in pending_total_deltas.keys() if str(token).strip())
    quantities_to_evaluate.update(str(token).strip() for token in logged_by_quantity.keys() if str(token).strip())
    quantities_to_evaluate.update(str(token).strip() for token in pending_unaccounted_deltas.keys() if str(token).strip())

    refusal_payload = {}
    for quantity_id in sorted(quantities_to_evaluate):
        net_delta = int(_as_int(pending_total_deltas.get(quantity_id, 0), 0))
        logged_delta = int(_as_int(logged_by_quantity.get(quantity_id, 0), 0))
        unaccounted_delta = int(_as_int(pending_unaccounted_deltas.get(quantity_id, 0), 0))
        evaluation = _evaluate_quantity(
            runtime=runtime,
            quantity_id=quantity_id,
            net_delta=net_delta,
            logged_delta=logged_delta,
            unaccounted_delta=unaccounted_delta,
            entry_types=list(entry_types_by_quantity.get(quantity_id) or []),
        )
        if str(evaluation.get("result", "")) != "complete":
            refusal_payload = dict(evaluation)
            break

    ledger = {
        "schema_version": "1.0.0",
        "ledger_id": "ledger.{}.tick.{}".format(str(shard_id), int(tick)),
        "tick": int(tick),
        "shard_id": str(shard_id),
        "pack_lock_hash": str(runtime.get("pack_lock_hash", "")),
        "physics_profile_id": str(runtime.get("physics_profile_id", "")),
        "contract_set_id": str(runtime.get("contract_set_id", "")),
        "totals": _build_totals(runtime, total_deltas=pending_total_deltas),
        "entries": list(entries),
        "previous_ledger_hash": str(runtime.get("previous_ledger_hash", "")) or None,
        "extensions": {
            "process_id": str(process_id),
        },
    }
    ledger["ledger_hash"] = canonical_sha256(_ledger_hash_payload(ledger))
    _update_runtime_after_finalize(runtime, ledger)

    runtime["pending_entries"] = []
    runtime["pending_total_deltas"] = {}
    runtime["pending_unaccounted_deltas"] = {}

    if refusal_payload:
        refused = dict(refusal_payload)
        refused["ledger_hash"] = str(ledger.get("ledger_hash", ""))
        refused["ledger"] = dict(ledger)
        return refused
    return {
        "result": "complete",
        "ledger_hash": str(ledger.get("ledger_hash", "")),
        "ledger": dict(ledger),
    }


def finalize_noop_tick(
    policy_context: dict | None,
    *,
    tick: int,
    process_id: str = "process.tick_ledger",
) -> dict:
    begin_process_accounting(policy_context, process_id=process_id)
    return finalize_process_accounting(policy_context, tick=int(tick), process_id=str(process_id))


def last_ledger_hash(policy_context: dict | None, shard_id: str = "") -> str:
    if not isinstance(policy_context, dict):
        return ""
    target = str(shard_id or _shard_id(policy_context)).strip()
    runtime_by_shard = _runtime_by_shard(policy_context)
    runtime = runtime_by_shard.get(target)
    if isinstance(runtime, dict):
        return str(runtime.get("last_ledger_hash", ""))
    return ""


def last_ledger_payload(policy_context: dict | None, shard_id: str = "") -> dict:
    if not isinstance(policy_context, dict):
        return {}
    target = str(shard_id or _shard_id(policy_context)).strip()
    runtime_by_shard = _runtime_by_shard(policy_context)
    runtime = runtime_by_shard.get(target)
    if isinstance(runtime, dict):
        return dict(runtime.get("last_ledger") or {})
    return {}

