"""Deterministic ELEC-2 fault detection helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from safety.safety_engine import build_safety_event
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_ELEC_FAULT_INVALID = "refusal.elec.fault_invalid"

_VALID_FAULT_KINDS = {
    "fault.overcurrent",
    "fault.short_circuit",
    "fault.ground_fault",
    "fault.open_circuit",
    "fault.insulation_breakdown",
    "fault.undervoltage",
    "fault.overvoltage",
}
_VALID_TARGET_KINDS = {"node", "edge", "device"}
_VALID_GROUNDING_MODES = {"grounded", "floating"}


class ElectricFaultError(ValueError):
    """Deterministic electrical fault refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_ELEC_FAULT_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _fault_id(*, fault_kind_id: str, target_kind: str, target_id: str, graph_id: str | None = None) -> str:
    digest = canonical_sha256(
        {
            "fault_kind_id": str(fault_kind_id or "").strip(),
            "target_kind": str(target_kind or "").strip(),
            "target_id": str(target_id or "").strip(),
            "graph_id": str(graph_id or "").strip(),
        }
    )
    return "fault.elec.{}".format(digest[:16])


def build_fault_state(
    *,
    fault_id: str,
    fault_kind_id: str,
    target_kind: str,
    target_id: str,
    detected_tick: int,
    severity: int,
    active: bool,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    fault_kind = str(fault_kind_id or "").strip()
    if fault_kind not in _VALID_FAULT_KINDS:
        raise ElectricFaultError(
            REFUSAL_ELEC_FAULT_INVALID,
            "fault_kind_id '{}' is not supported".format(fault_kind),
            {"fault_kind_id": fault_kind},
        )
    target_kind_token = str(target_kind or "").strip().lower()
    if target_kind_token not in _VALID_TARGET_KINDS:
        raise ElectricFaultError(
            REFUSAL_ELEC_FAULT_INVALID,
            "target_kind '{}' must be node|edge|device".format(target_kind_token),
            {"target_kind": target_kind_token},
        )
    payload = {
        "schema_version": "1.0.0",
        "fault_id": str(fault_id or "").strip(),
        "fault_kind_id": fault_kind,
        "target_kind": target_kind_token,
        "target_id": str(target_id or "").strip(),
        "detected_tick": int(max(0, _as_int(detected_tick, 0))),
        "severity": int(max(0, _as_int(severity, 0))),
        "active": bool(active),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["fault_id"] or not payload["target_id"]:
        raise ElectricFaultError(
            REFUSAL_ELEC_FAULT_INVALID,
            "fault_state requires fault_id and target_id",
            {"fault_id": payload["fault_id"], "target_id": payload["target_id"]},
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_fault_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("fault_id", ""))):
        fault_id = str(row.get("fault_id", "")).strip()
        if not fault_id:
            continue
        try:
            out[fault_id] = build_fault_state(
                fault_id=fault_id,
                fault_kind_id=str(row.get("fault_kind_id", "")).strip(),
                target_kind=str(row.get("target_kind", "")).strip(),
                target_id=str(row.get("target_id", "")).strip(),
                detected_tick=int(max(0, _as_int(row.get("detected_tick", 0), 0))),
                severity=int(max(0, _as_int(row.get("severity", 0), 0))),
                active=bool(row.get("active", True)),
                extensions=_as_map(row.get("extensions")),
            )
        except ElectricFaultError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def fault_kind_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("fault_kinds")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("fault_kinds")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("fault_kind_id", ""))):
        fault_kind_id = str(row.get("fault_kind_id", "")).strip()
        if fault_kind_id:
            out[fault_kind_id] = {
                "schema_version": "1.0.0",
                "fault_kind_id": fault_kind_id,
                "schema_ref": str(row.get("schema_ref", "")).strip(),
                "extensions": _canon(_as_map(row.get("extensions"))),
            }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def grounding_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("grounding_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("grounding_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("grounding_policy_id", ""))):
        policy_id = str(row.get("grounding_policy_id", "")).strip()
        if not policy_id:
            continue
        ext = _as_map(row.get("extensions"))
        mode = str(row.get("default_mode", ext.get("default_mode", "grounded"))).strip().lower() or "grounded"
        if mode not in _VALID_GROUNDING_MODES:
            mode = "grounded"
        out[policy_id] = {
            "schema_version": "1.0.0",
            "grounding_policy_id": policy_id,
            "default_mode": mode,
            "gfci_required": bool(row.get("gfci_required", ext.get("gfci_required", False))),
            "fault_detection_rule_id": str(
                row.get("fault_detection_rule_id", ext.get("fault_detection_rule_id", "rule.ground.imbalance_basic"))
            ).strip()
            or "rule.ground.imbalance_basic",
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(ext),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _fault_key(*, kind: str, target_id: str) -> Tuple[str, str]:
    return (str(kind or "").strip(), str(target_id or "").strip())


def _overcurrent_severity_permille(*, apparent_s: int, capacity_units: int) -> int:
    s = int(max(0, _as_int(apparent_s, 0)))
    cap = int(max(1, _as_int(capacity_units, 1)))
    if s <= cap:
        return 0
    exceed = int(s - cap)
    return int(min(10_000, (exceed * 1000) // cap))


def _ground_fault_detected(
    *,
    active_p: int,
    reactive_q: int,
    apparent_s: int,
    grounding_policy_row: Mapping[str, object],
    settings_row: Mapping[str, object] | None,
) -> Tuple[bool, int]:
    policy = dict(grounding_policy_row or {})
    settings = dict(settings_row or {})
    mode = str(policy.get("default_mode", "grounded")).strip().lower() or "grounded"
    if mode == "floating":
        return (False, 0)
    imbalance = int(max(0, _as_int(apparent_s, 0) - _as_int(active_p, 0)))
    if int(max(0, _as_int(reactive_q, 0))) > 0:
        imbalance = max(imbalance, int(max(0, _as_int(reactive_q, 0))))
    threshold = int(max(1, _as_int(settings.get("gfci_threshold", 30), 30)))
    if not bool(policy.get("gfci_required", False)):
        threshold = int(max(1, threshold * 2))
    if imbalance < threshold:
        return (False, 0)
    severity = int(min(10_000, (imbalance * 1000) // max(1, threshold)))
    return (True, severity)


def detect_faults(
    *,
    edge_status_rows: object,
    channel_rows: object,
    fault_rows: object,
    current_tick: int,
    max_fault_evals: int,
    grounding_policy_row: Mapping[str, object] | None = None,
    protection_settings_rows_by_target_id: Mapping[str, Mapping[str, object]] | None = None,
) -> dict:
    edge_rows = sorted(
        (dict(item) for item in list(edge_status_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (str(item.get("graph_id", "")), str(item.get("edge_id", ""))),
    )
    channels_by_id = dict(
        (
            str(row.get("channel_id", "")).strip(),
            dict(row),
        )
        for row in list(channel_rows or [])
        if isinstance(row, Mapping) and str(row.get("channel_id", "")).strip()
    )
    settings_by_target = dict(
        (
            str(key).strip(),
            dict(value or {}),
        )
        for key, value in dict(protection_settings_rows_by_target_id or {}).items()
        if str(key).strip()
    )
    policy_row = dict(grounding_policy_row or {"default_mode": "grounded", "gfci_required": False})
    existing_rows = normalize_fault_state_rows(fault_rows)
    existing_by_key = dict(
        (_fault_key(kind=row.get("fault_kind_id", ""), target_id=row.get("target_id", "")), dict(row))
        for row in existing_rows
    )

    next_rows_by_key: Dict[Tuple[str, str], dict] = {}
    events: List[dict] = []
    detected_fault_ids: List[str] = []
    deferred_targets: List[str] = []

    max_evals = int(max(0, _as_int(max_fault_evals, 0)))
    for idx, edge in enumerate(edge_rows):
        edge_id = str(edge.get("edge_id", "")).strip()
        graph_id = str(edge.get("graph_id", "")).strip()
        channel_id = str(edge.get("channel_id", "")).strip()
        if not edge_id:
            continue
        if idx >= max_evals:
            deferred_targets.append(edge_id)
            continue
        channel = dict(channels_by_id.get(channel_id) or {})
        channel_ext = _as_map(channel.get("extensions"))
        settings_row = dict(settings_by_target.get(edge_id) or settings_by_target.get(channel_id) or {})

        p = int(max(0, _as_int(edge.get("P", 0), 0)))
        q = int(max(0, _as_int(edge.get("Q", 0), 0)))
        s = int(max(0, _as_int(edge.get("S", 0), 0)))
        cap = int(max(0, _as_int(edge.get("capacity_rating", channel.get("capacity_per_tick", 0)), 0)))
        overloaded = bool(edge.get("overloaded", False))

        detected_specs: List[Tuple[str, int, dict]] = []

        overcurrent_threshold_s = int(max(1, _as_int(settings_row.get("trip_threshold_S", cap if cap > 0 else 1), cap if cap > 0 else 1)))
        overcurrent_active = overloaded or (cap > 0 and s > overcurrent_threshold_s)
        if overcurrent_active:
            severity = _overcurrent_severity_permille(apparent_s=s, capacity_units=overcurrent_threshold_s)
            detected_specs.append(
                (
                    "fault.overcurrent",
                    int(max(1, severity)),
                    {
                        "graph_id": graph_id,
                        "edge_id": edge_id,
                        "channel_id": channel_id or None,
                        "apparent_s": int(s),
                        "capacity_units": int(overcurrent_threshold_s),
                    },
                )
            )

        open_active = bool(channel_ext.get("manual_open", False) or channel_ext.get("open_circuit", False))
        if open_active:
            detected_specs.append(
                (
                    "fault.open_circuit",
                    1000,
                    {
                        "graph_id": graph_id,
                        "edge_id": edge_id,
                        "channel_id": channel_id or None,
                    },
                )
            )

        short_hint = bool(channel_ext.get("short_circuit", False))
        short_active = bool(short_hint or (cap <= 0 and s > 0 and not bool(channel_ext.get("safety_disconnected", False))))
        if short_active:
            detected_specs.append(
                (
                    "fault.short_circuit",
                    max(1000, int(s)),
                    {
                        "graph_id": graph_id,
                        "edge_id": edge_id,
                        "channel_id": channel_id or None,
                    },
                )
            )

        ground_active, ground_severity = _ground_fault_detected(
            active_p=int(p),
            reactive_q=int(q),
            apparent_s=int(s),
            grounding_policy_row=policy_row,
            settings_row=settings_row,
        )
        if ground_active:
            detected_specs.append(
                (
                    "fault.ground_fault",
                    int(max(1, ground_severity)),
                    {
                        "graph_id": graph_id,
                        "edge_id": edge_id,
                        "channel_id": channel_id or None,
                        "grounding_policy_id": str(policy_row.get("grounding_policy_id", "")).strip() or None,
                    },
                )
            )

        for fault_kind_id, severity, ext in detected_specs:
            key = _fault_key(kind=fault_kind_id, target_id=edge_id)
            previous = dict(existing_by_key.get(key) or {})
            fault_id = str(previous.get("fault_id", "")).strip() or _fault_id(
                fault_kind_id=fault_kind_id,
                target_kind="edge",
                target_id=edge_id,
                graph_id=graph_id,
            )
            detected_tick = int(previous.get("detected_tick", current_tick))
            row = build_fault_state(
                fault_id=fault_id,
                fault_kind_id=fault_kind_id,
                target_kind="edge",
                target_id=edge_id,
                detected_tick=int(detected_tick),
                severity=int(max(0, _as_int(severity, 0))),
                active=True,
                extensions=ext,
            )
            next_rows_by_key[key] = row
            detected_fault_ids.append(fault_id)
            if not bool(previous.get("active", False)):
                events.append(
                    build_safety_event(
                        event_id="",
                        tick=int(max(0, _as_int(current_tick, 0))),
                        instance_id="instance.safety.elec.fault.{}".format(fault_id.split(".")[-1]),
                        pattern_id="safety.breaker_trip" if fault_kind_id in {"fault.overcurrent", "fault.short_circuit", "fault.ground_fault"} else "safety.fail_safe_stop",
                        pattern_type="breaker" if fault_kind_id in {"fault.overcurrent", "fault.short_circuit", "fault.ground_fault"} else "failsafe",
                        status="fault_detected",
                        target_ids=[edge_id],
                        action_count=0,
                        details={
                            "fault_id": fault_id,
                            "fault_kind_id": fault_kind_id,
                            "severity": int(max(0, _as_int(severity, 0))),
                        },
                        extensions={"graph_id": graph_id},
                    )
                )

    # Preserve deterministic lifecycle and emit clear events when no longer active.
    for key, previous in sorted(existing_by_key.items(), key=lambda item: (str(item[0][0]), str(item[0][1]))):
        if key in next_rows_by_key:
            continue
        inactive = build_fault_state(
            fault_id=str(previous.get("fault_id", "")).strip(),
            fault_kind_id=str(previous.get("fault_kind_id", "")).strip(),
            target_kind=str(previous.get("target_kind", "edge")).strip() or "edge",
            target_id=str(previous.get("target_id", "")).strip(),
            detected_tick=int(max(0, _as_int(previous.get("detected_tick", current_tick), current_tick))),
            severity=0,
            active=False,
            extensions=dict(_as_map(previous.get("extensions"))),
        )
        next_rows_by_key[key] = inactive
        if bool(previous.get("active", False)):
            events.append(
                build_safety_event(
                    event_id="",
                    tick=int(max(0, _as_int(current_tick, 0))),
                    instance_id="instance.safety.elec.fault.{}".format(str(inactive.get("fault_id", "")).split(".")[-1]),
                    pattern_id="safety.fail_safe_stop",
                    pattern_type="failsafe",
                    status="fault_cleared",
                    target_ids=[str(inactive.get("target_id", "")).strip()],
                    action_count=0,
                    details={
                        "fault_id": str(inactive.get("fault_id", "")).strip(),
                        "fault_kind_id": str(inactive.get("fault_kind_id", "")).strip(),
                    },
                    extensions={},
                )
            )

    next_rows = [dict(next_rows_by_key[key]) for key in sorted(next_rows_by_key.keys(), key=lambda item: (str(item[0]), str(item[1])))]
    active_rows = [dict(row) for row in next_rows if bool(row.get("active", False))]
    fault_state_hash_chain = canonical_sha256(
        [
            {
                "fault_id": str(row.get("fault_id", "")).strip(),
                "fault_kind_id": str(row.get("fault_kind_id", "")).strip(),
                "target_id": str(row.get("target_id", "")).strip(),
                "severity": int(max(0, _as_int(row.get("severity", 0), 0))),
            }
            for row in sorted(active_rows, key=lambda item: str(item.get("fault_id", "")))
        ]
    )
    return {
        "fault_rows": [dict(row) for row in next_rows],
        "events": sorted(
            [dict(row) for row in events],
            key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("event_id", ""))),
        ),
        "detected_fault_ids": sorted(set(str(item).strip() for item in detected_fault_ids if str(item).strip())),
        "active_fault_ids": sorted(str(row.get("fault_id", "")).strip() for row in active_rows if str(row.get("fault_id", "")).strip()),
        "deferred_target_ids": sorted(set(str(item).strip() for item in deferred_targets if str(item).strip())),
        "cost_units": int(max(0, len(edge_rows) - len(deferred_targets))),
        "budget_outcome": "degraded" if deferred_targets else "complete",
        "fault_state_hash_chain": str(fault_state_hash_chain),
    }


__all__ = [
    "REFUSAL_ELEC_FAULT_INVALID",
    "ElectricFaultError",
    "build_fault_state",
    "detect_faults",
    "fault_kind_rows_by_id",
    "grounding_policy_rows_by_id",
    "normalize_fault_state_rows",
]
