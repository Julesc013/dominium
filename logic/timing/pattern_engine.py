"""LOGIC-5 timing pattern helpers for pack-defined elements."""

from __future__ import annotations

from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from logic.eval.common import as_int, as_list, as_map, canon, token


def build_watchdog_definition_row(
    *,
    watchdog_id: str,
    monitored_signal_id: str,
    timeout_ticks: int,
    action_on_timeout: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "watchdog_id": token(watchdog_id),
        "monitored_signal_id": token(monitored_signal_id),
        "timeout_ticks": int(max(1, as_int(timeout_ticks, 1))),
        "action_on_timeout": token(action_on_timeout),
        "deterministic_fingerprint": token(deterministic_fingerprint),
        "extensions": canon(as_map(extensions)),
    }
    if not payload["watchdog_id"] or not payload["monitored_signal_id"] or payload["action_on_timeout"] not in {"signal_set", "refusal"}:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_watchdog_definition_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in as_list(rows) if isinstance(item, Mapping)), key=lambda item: token(item.get("watchdog_id"))):
        normalized = build_watchdog_definition_row(
            watchdog_id=token(row.get("watchdog_id")),
            monitored_signal_id=token(row.get("monitored_signal_id")),
            timeout_ticks=as_int(row.get("timeout_ticks"), 1),
            action_on_timeout=token(row.get("action_on_timeout")),
            deterministic_fingerprint=token(row.get("deterministic_fingerprint")),
            extensions=as_map(row.get("extensions")),
        )
        if normalized:
            out[token(normalized.get("watchdog_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def watchdog_definition_rows_by_id(rows: object) -> dict:
    normalized = normalize_watchdog_definition_rows(rows)
    return dict((token(row.get("watchdog_id")), dict(row)) for row in normalized if token(row.get("watchdog_id")))


def timing_pattern_id_for_element(element_row: Mapping[str, object] | None) -> str:
    return token(as_map(as_map(element_row).get("extensions")).get("timing_pattern_id"))


def synchronizer_stage_count(element_row: Mapping[str, object] | None) -> int:
    extensions = as_map(as_map(element_row).get("extensions"))
    return int(max(2, as_int(extensions.get("stage_count", 2), 2)))


def detect_watchdog_timeout_transitions(
    *,
    current_tick: int,
    network_id: str,
    compute_result: Mapping[str, object] | None,
    logic_element_rows: object,
    watchdog_definition_rows: object,
) -> list[dict]:
    tick = int(max(0, as_int(current_tick, 0)))
    elements_by_id = dict(
        (token(row.get("element_id")), dict(row))
        for row in as_list(logic_element_rows)
        if isinstance(row, Mapping) and token(row.get("element_id"))
    )
    watchdogs_by_id = watchdog_definition_rows_by_id(watchdog_definition_rows)
    out = []
    for row in as_list(as_map(compute_result).get("element_results")):
        if not isinstance(row, Mapping):
            continue
        element_definition_id = token(row.get("element_definition_id"))
        element_row = dict(elements_by_id.get(element_definition_id) or {})
        if timing_pattern_id_for_element(element_row) != "pattern.watchdog_basic":
            continue
        watchdog_id = token(as_map(as_map(element_row).get("extensions")).get("watchdog_definition_id"))
        watchdog_row = dict(watchdogs_by_id.get(watchdog_id) or {})
        if not watchdog_row:
            continue
        current_state = as_map(row.get("current_state"))
        next_state = as_map(row.get("next_state"))
        current_timeout = int(max(0, as_int(current_state.get("timeout_state", 0), 0)))
        next_timeout = int(max(0, as_int(next_state.get("timeout_state", 0), 0)))
        if current_timeout >= 1 or next_timeout < 1:
            continue
        out.append(
            {
                "tick": int(tick),
                "network_id": token(network_id),
                "watchdog_id": token(watchdog_row.get("watchdog_id")),
                "action_on_timeout": token(watchdog_row.get("action_on_timeout")),
                "extensions": {
                    "element_instance_id": token(row.get("element_instance_id")),
                    "element_definition_id": element_definition_id,
                    "monitored_signal_id": token(watchdog_row.get("monitored_signal_id")),
                    "timeout_ticks": int(as_int(watchdog_row.get("timeout_ticks"), 1)),
                },
            }
        )
    return sorted(out, key=lambda row: (int(row.get("tick", 0)), token(row.get("watchdog_id"))))


__all__ = [
    "build_watchdog_definition_row",
    "detect_watchdog_timeout_transitions",
    "normalize_watchdog_definition_rows",
    "synchronizer_stage_count",
    "timing_pattern_id_for_element",
    "watchdog_definition_rows_by_id",
]
