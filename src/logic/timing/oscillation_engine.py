"""LOGIC-5 bounded oscillation detection helpers."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.logic.eval.common import as_int, as_list, as_map, canon, token
from src.logic.signal.signal_store import canonical_signal_snapshot
from src.meta.explain import build_explain_artifact


def _graph_element_ids(graph_row: Mapping[str, object]) -> list[str]:
    out = set()
    for node in as_list(as_map(graph_row).get("nodes")):
        if not isinstance(node, Mapping):
            continue
        payload = as_map(node.get("payload"))
        element_instance_id = token(payload.get("element_instance_id"))
        if element_instance_id:
            out.add(element_instance_id)
    return sorted(out)


def build_logic_timing_state_hash(
    *,
    current_tick: int,
    network_id: str,
    graph_row: Mapping[str, object],
    signal_store_state: Mapping[str, object] | None,
    pending_signal_update_rows: object,
    state_vector_snapshot_rows: object,
) -> str:
    network_token = token(network_id)
    element_ids = set(_graph_element_ids(graph_row))
    active_snapshot = canonical_signal_snapshot(state=signal_store_state, tick=current_tick)
    active_signals = []
    for row in as_list(as_map(active_snapshot).get("signals")):
        if not isinstance(row, Mapping):
            continue
        slot = as_map(as_map(row.get("extensions")).get("slot"))
        if token(slot.get("network_id")) != network_token:
            continue
        active_signals.append(
            {
                "element_id": token(slot.get("element_id")),
                "port_id": token(slot.get("port_id")),
                "signal_type_id": token(row.get("signal_type_id")),
                "carrier_type_id": token(row.get("carrier_type_id")),
                "value_ref": canon(as_map(row.get("value_ref"))),
            }
        )
    pending_rows = [
        dict(row)
        for row in as_list(pending_signal_update_rows)
        if isinstance(row, Mapping) and token(row.get("network_id")) == network_token
    ]
    latest_state_rows = {}
    for row in as_list(state_vector_snapshot_rows):
        if not isinstance(row, Mapping):
            continue
        owner_id = token(row.get("owner_id"))
        if owner_id not in element_ids:
            continue
        candidate = dict(row)
        current = dict(latest_state_rows.get(owner_id) or {})
        candidate_key = (
            int(max(0, as_int(candidate.get("tick", 0), 0))),
            token(candidate.get("snapshot_id")),
        )
        current_key = (
            int(max(0, as_int(current.get("tick", 0), 0))),
            token(current.get("snapshot_id")),
        )
        if not current or candidate_key >= current_key:
            latest_state_rows[owner_id] = candidate
    state_rows = [dict(latest_state_rows[owner_id]) for owner_id in sorted(latest_state_rows.keys())]
    return canonical_sha256(
        {
            "network_id": network_token,
            "active_signals": sorted(
                active_signals,
                key=lambda row: (
                    token(as_map(as_map(row.get("extensions")).get("slot")).get("element_id")),
                    token(as_map(as_map(row.get("extensions")).get("slot")).get("port_id")),
                    token(row.get("signal_id")),
                ),
            ),
            "pending_signal_updates": sorted(
                [
                    {
                        "source_element_id": token(row.get("source_element_id")),
                        "source_port_id": token(row.get("source_port_id")),
                        "target_element_id": token(row.get("target_element_id")),
                        "target_port_id": token(row.get("target_port_id")),
                        "signal_type_id": token(row.get("signal_type_id")),
                        "carrier_type_id": token(row.get("carrier_type_id")),
                        "deliver_delay_ticks": int(
                            max(
                                0,
                                as_int(
                                    as_map(row.get("extensions")).get("deliver_delay_ticks"),
                                    as_int(row.get("deliver_tick"), 0) - int(max(0, as_int(current_tick, 0))),
                                ),
                            )
                        ),
                        "value_payload": canon(as_map(row.get("value_payload"))),
                    }
                    for row in pending_rows
                ],
                key=lambda row: (
                    as_int(row.get("deliver_delay_ticks"), 0),
                    token(row.get("target_element_id")),
                    token(row.get("target_port_id")),
                ),
            ),
            "state_snapshots": sorted(
                [
                    {
                        "owner_id": token(row.get("owner_id")),
                        "serialized_state": canon(as_map(row.get("serialized_state"))),
                    }
                    for row in state_rows
                ],
                key=lambda row: (
                    token(row.get("owner_id")),
                ),
            ),
        }
    )


def detect_network_oscillation(
    *,
    current_tick: int,
    network_id: str,
    graph_row: Mapping[str, object],
    signal_store_state: Mapping[str, object] | None,
    pending_signal_update_rows: object,
    state_vector_snapshot_rows: object,
    runtime_row: Mapping[str, object] | None,
    logic_policy_row: Mapping[str, object] | None,
) -> dict:
    tick = int(max(0, as_int(current_tick, 0)))
    network_token = token(network_id)
    policy_extensions = as_map(as_map(logic_policy_row).get("extensions"))
    runtime_extensions = dict(as_map(as_map(runtime_row).get("extensions")))
    window_size = int(max(2, as_int(policy_extensions.get("oscillation_window_ticks", 8), 8)))

    state_hash = build_logic_timing_state_hash(
        current_tick=tick,
        network_id=network_token,
        graph_row=graph_row,
        signal_store_state=signal_store_state,
        pending_signal_update_rows=pending_signal_update_rows,
        state_vector_snapshot_rows=state_vector_snapshot_rows,
    )
    prior_window = [
        {
            "tick": int(max(0, as_int(row.get("tick", 0), 0))),
            "state_hash": token(row.get("state_hash")),
        }
        for row in as_list(runtime_extensions.get("timing_hash_window"))
        if isinstance(row, Mapping) and token(row.get("state_hash"))
    ]
    history = sorted(prior_window + [{"tick": tick, "state_hash": state_hash}], key=lambda row: (int(row["tick"]), str(row["state_hash"])))
    if len(history) > window_size:
        history = history[-window_size:]

    occurrences = [dict(row) for row in history if str(row.get("state_hash")) == state_hash]
    record_rows = []
    explain_rows = []
    classification = {}
    if len(occurrences) >= 2:
        previous_tick = int(occurrences[-2].get("tick", tick))
        period_ticks = int(max(1, tick - previous_tick))
        intervening_history = [
            dict(row)
            for row in history
            if int(row.get("tick", 0)) > previous_tick and int(row.get("tick", 0)) < tick
        ]
        has_state_transition = any(str(row.get("state_hash", "")) != state_hash for row in intervening_history)
        if has_state_transition:
            stable = False
            if len(occurrences) >= 3:
                prior_tick = int(occurrences[-3].get("tick", previous_tick))
                prior_period = int(max(1, previous_tick - prior_tick))
                stable = bool(prior_period == period_ticks)
            classification = {
                "period_ticks": int(period_ticks),
                "stable": bool(stable),
                "state_hash": str(state_hash),
            }
            record_rows.append(
                {
                    "tick": int(tick),
                    "network_id": network_token,
                    "period_ticks": int(period_ticks),
                    "stable": bool(stable),
                    "extensions": {
                        "state_hash": str(state_hash),
                        "window_size": int(window_size),
                        "matched_ticks": [int(row.get("tick", 0)) for row in occurrences[-3:]],
                    },
                }
            )
            if not stable:
                explain_rows.append(
                    build_explain_artifact(
                        explain_id="explain.logic_oscillation.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(tick),
                                    "network_id": network_token,
                                    "state_hash": str(state_hash),
                                    "period_ticks": int(period_ticks),
                                }
                            )[:16]
                        ),
                        event_id="event.logic.oscillation.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(tick),
                                    "network_id": network_token,
                                    "state_hash": str(state_hash),
                                    "period_ticks": int(period_ticks),
                                }
                            )[:16]
                        ),
                        target_id=network_token,
                        cause_chain=["cause.logic.oscillation"],
                        remediation_hints=["inspect loop policy, delay policy, and stateful timing pattern configuration"],
                        extensions={
                            "event_kind_id": "explain.logic_oscillation",
                            "period_ticks": int(period_ticks),
                            "state_hash": str(state_hash),
                        },
                    )
                )

    runtime_extensions["timing_hash_window"] = [
        {
            "tick": int(row.get("tick", 0)),
            "state_hash": str(row.get("state_hash", "")).strip(),
        }
        for row in history
    ]
    runtime_extensions["timing_state_hash"] = str(state_hash)
    if classification:
        runtime_extensions["last_oscillation_classification"] = canon(classification)

    return {
        "runtime_extensions": runtime_extensions,
        "timing_state_hash": str(state_hash),
        "oscillation_record_rows": record_rows,
        "explain_artifact_rows": explain_rows,
        "classification": classification,
    }


__all__ = [
    "build_logic_timing_state_hash",
    "detect_network_oscillation",
]
