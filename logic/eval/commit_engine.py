"""LOGIC-4 COMMIT phase helpers and state-vector update process."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import as_int, as_list, as_map, rows_by_id, token
from .runtime_state import build_logic_state_update_record_row, normalize_logic_state_update_record_rows


PROCESS_STATEVEC_UPDATE = "process.statevec_update"
REFUSAL_STATEVEC_UPDATE_INVALID = "refusal.logic.statevec_update_invalid"


def process_statevec_update(
    *,
    current_tick: int,
    owner_id: str,
    source_state: Mapping[str, object],
    state_vector_definition_rows: object,
    state_vector_snapshot_rows: object,
    expected_version: str | None,
    definition_row: Mapping[str, object] | None,
    normalize_state_vector_definition_rows,
    normalize_state_vector_snapshot_rows,
    serialize_state,
    state_vector_snapshot_rows_by_owner,
) -> dict:
    owner_token = token(owner_id)
    if not owner_token:
        return {"result": "refused", "reason_code": REFUSAL_STATEVEC_UPDATE_INVALID}
    definition_rows = normalize_state_vector_definition_rows(
        list(state_vector_definition_rows or [])
        + ([dict(definition_row)] if isinstance(definition_row, Mapping) and dict(definition_row) else [])
    )
    prior_by_owner = state_vector_snapshot_rows_by_owner(state_vector_snapshot_rows)
    prior_snapshot = dict(prior_by_owner.get(owner_token) or {})
    serialization = serialize_state(
        owner_id=owner_token,
        source_state=source_state,
        state_vector_definition_rows=definition_rows,
        current_tick=int(max(0, as_int(current_tick, 0))),
        expected_version=expected_version,
        extensions={"source": "LOGIC4-5", "process_id": PROCESS_STATEVEC_UPDATE},
    )
    if token(serialization.get("result")) != "complete":
        return {
            "result": "refused",
            "reason_code": token(serialization.get("reason_code")) or REFUSAL_STATEVEC_UPDATE_INVALID,
            "state_vector_definition_rows": definition_rows,
            "state_vector_snapshot_rows": normalize_state_vector_snapshot_rows(state_vector_snapshot_rows),
            "state_update_record_rows": normalize_logic_state_update_record_rows([]),
        }
    snapshot_row = dict(serialization.get("snapshot_row") or {})
    snapshot_rows = normalize_state_vector_snapshot_rows(list(state_vector_snapshot_rows or []) + [snapshot_row])
    prior_hash = None if not prior_snapshot else canonical_sha256(prior_snapshot)
    next_hash = canonical_sha256(snapshot_row)
    update_row = build_logic_state_update_record_row(
        tick=int(max(0, as_int(current_tick, 0))),
        owner_id=owner_token,
        prior_snapshot_hash=prior_hash,
        next_snapshot_hash=next_hash,
        process_id=PROCESS_STATEVEC_UPDATE,
        deterministic_fingerprint="",
        extensions={"version": token(snapshot_row.get("version")) or "1.0.0"},
    )
    return {
        "result": "complete",
        "reason_code": "",
        "state_vector_definition_rows": definition_rows,
        "state_vector_snapshot_rows": snapshot_rows,
        "state_vector_snapshot_row": snapshot_row,
        "state_update_record_rows": normalize_logic_state_update_record_rows([update_row]),
    }


def commit_logic_state_updates(
    *,
    current_tick: int,
    compute_result: Mapping[str, object],
    state_vector_definition_rows: object,
    state_vector_snapshot_rows: object,
    process_statevec_update_fn,
) -> dict:
    definition_rows = list(state_vector_definition_rows or [])
    snapshot_rows = list(state_vector_snapshot_rows or [])
    update_rows = []
    for row in (dict(item) for item in as_list(as_map(compute_result).get("element_results")) if isinstance(item, Mapping)):
        model_kind = token(row.get("model_kind")).lower()
        if model_kind not in {"sequential", "timer", "counter"}:
            continue
        next_state = dict(as_map(row.get("next_state")))
        update_result = process_statevec_update_fn(
            current_tick=current_tick,
            owner_id=token(row.get("element_instance_id")),
            source_state=next_state,
            state_vector_definition_rows=definition_rows,
            state_vector_snapshot_rows=snapshot_rows,
            expected_version="1.0.0",
            definition_row=as_map(row.get("instance_definition_row")),
        )
        if token(update_result.get("result")) != "complete":
            return {
                "result": "refused",
                "reason_code": token(update_result.get("reason_code")) or REFUSAL_STATEVEC_UPDATE_INVALID,
                "state_vector_definition_rows": definition_rows,
                "state_vector_snapshot_rows": snapshot_rows,
                "state_update_record_rows": normalize_logic_state_update_record_rows(update_rows),
            }
        definition_rows = list(update_result.get("state_vector_definition_rows") or definition_rows)
        snapshot_rows = list(update_result.get("state_vector_snapshot_rows") or snapshot_rows)
        update_rows.extend(list(update_result.get("state_update_record_rows") or []))
    return {
        "result": "complete",
        "reason_code": "",
        "state_vector_definition_rows": definition_rows,
        "state_vector_snapshot_rows": snapshot_rows,
        "state_update_record_rows": normalize_logic_state_update_record_rows(update_rows),
    }


def attach_instance_definitions_to_compute_result(
    *,
    compute_result: Mapping[str, object],
    state_vector_definition_rows: object,
) -> dict:
    definitions_by_owner = rows_by_id(state_vector_definition_rows, "owner_id")
    next_rows = []
    for row in (dict(item) for item in as_list(as_map(compute_result).get("element_results")) if isinstance(item, Mapping)):
        owner_id = token(row.get("element_instance_id"))
        row["instance_definition_row"] = dict(definitions_by_owner.get(owner_id) or {})
        next_rows.append(row)
    out = dict(as_map(compute_result))
    out["element_results"] = next_rows
    return out


__all__ = [
    "PROCESS_STATEVEC_UPDATE",
    "REFUSAL_STATEVEC_UPDATE_INVALID",
    "attach_instance_definitions_to_compute_result",
    "commit_logic_state_updates",
    "process_statevec_update",
]
