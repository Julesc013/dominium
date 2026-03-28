"""Deterministic ELEC-2 protection/co-ordination helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from safety.safety_engine import build_safety_event, build_safety_instance
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_ELEC_PROTECTION_INVALID = "refusal.elec.protection_invalid"

_VALID_DEVICE_KINDS = {"breaker", "fuse", "relay", "gfci", "isolator"}
_VALID_COORDINATION_POLICIES = {"coord.downstream_first", "coord.upstream_first", "coord.strict_table"}


class ElectricProtectionError(ValueError):
    """Deterministic electrical protection refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_ELEC_PROTECTION_INVALID)
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


def deterministic_protection_device_id(*, graph_id: str, channel_id: str, device_kind_id: str = "breaker") -> str:
    digest = canonical_sha256(
        {
            "graph_id": str(graph_id or "").strip(),
            "channel_id": str(channel_id or "").strip(),
            "device_kind_id": str(device_kind_id or "").strip() or "breaker",
        }
    )
    return "device.elec.{}".format(digest[:16])


def _attached_to_payload(value: object) -> dict:
    row = dict(value or {}) if isinstance(value, Mapping) else {}
    node_id = str(row.get("node_id", "")).strip()
    edge_id = str(row.get("edge_id", "")).strip()
    if bool(node_id) == bool(edge_id):
        raise ElectricProtectionError(
            REFUSAL_ELEC_PROTECTION_INVALID,
            "attached_to must contain exactly one of node_id or edge_id",
            {"attached_to": row},
        )
    return {"node_id": node_id} if node_id else {"edge_id": edge_id}


def build_protection_device(
    *,
    device_id: str,
    device_kind_id: str,
    attached_to: Mapping[str, object],
    state_machine_id: str,
    settings_ref: str,
    spec_id: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind = str(device_kind_id or "").strip().lower()
    if kind not in _VALID_DEVICE_KINDS:
        raise ElectricProtectionError(
            REFUSAL_ELEC_PROTECTION_INVALID,
            "device_kind_id '{}' is not supported".format(kind),
            {"device_kind_id": kind},
        )
    payload = {
        "schema_version": "1.0.0",
        "device_id": str(device_id or "").strip(),
        "device_kind_id": kind,
        "attached_to": _attached_to_payload(attached_to),
        "state_machine_id": str(state_machine_id or "").strip(),
        "spec_id": None if spec_id is None else str(spec_id).strip() or None,
        "settings_ref": str(settings_ref or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["device_id"]) or (not payload["state_machine_id"]) or (not payload["settings_ref"]):
        raise ElectricProtectionError(
            REFUSAL_ELEC_PROTECTION_INVALID,
            "protection_device requires device_id, state_machine_id, and settings_ref",
            {
                "device_id": payload["device_id"],
                "state_machine_id": payload["state_machine_id"],
                "settings_ref": payload["settings_ref"],
            },
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_protection_device_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("device_id", ""))):
        device_id = str(row.get("device_id", "")).strip()
        if not device_id:
            continue
        try:
            out[device_id] = build_protection_device(
                device_id=device_id,
                device_kind_id=str(row.get("device_kind_id", "")).strip(),
                attached_to=_as_map(row.get("attached_to")),
                state_machine_id=str(row.get("state_machine_id", "")).strip(),
                settings_ref=str(row.get("settings_ref", "")).strip(),
                spec_id=(None if row.get("spec_id") is None else str(row.get("spec_id", "")).strip() or None),
                extensions=_as_map(row.get("extensions")),
            )
        except ElectricProtectionError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def build_protection_settings(
    *,
    settings_id: str,
    trip_threshold_P: int | None = None,
    trip_threshold_S: int | None = None,
    trip_delay_ticks: int | None = None,
    gfci_threshold: int | None = None,
    coordination_group_id: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "settings_id": str(settings_id or "").strip(),
        "trip_threshold_P": None if trip_threshold_P is None else int(max(0, _as_int(trip_threshold_P, 0))),
        "trip_threshold_S": None if trip_threshold_S is None else int(max(0, _as_int(trip_threshold_S, 0))),
        "trip_delay_ticks": None if trip_delay_ticks is None else int(max(0, _as_int(trip_delay_ticks, 0))),
        "gfci_threshold": None if gfci_threshold is None else int(max(0, _as_int(gfci_threshold, 0))),
        "coordination_group_id": None if coordination_group_id is None else str(coordination_group_id).strip() or None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["settings_id"]:
        raise ElectricProtectionError(
            REFUSAL_ELEC_PROTECTION_INVALID,
            "protection_settings requires settings_id",
            {},
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_protection_settings_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("settings_id", ""))):
        settings_id = str(row.get("settings_id", "")).strip()
        if not settings_id:
            continue
        try:
            out[settings_id] = build_protection_settings(
                settings_id=settings_id,
                trip_threshold_P=(None if row.get("trip_threshold_P") is None else _as_int(row.get("trip_threshold_P", 0), 0)),
                trip_threshold_S=(None if row.get("trip_threshold_S") is None else _as_int(row.get("trip_threshold_S", 0), 0)),
                trip_delay_ticks=(None if row.get("trip_delay_ticks") is None else _as_int(row.get("trip_delay_ticks", 0), 0)),
                gfci_threshold=(None if row.get("gfci_threshold") is None else _as_int(row.get("gfci_threshold", 0), 0)),
                coordination_group_id=(
                    None if row.get("coordination_group_id") is None else str(row.get("coordination_group_id", "")).strip() or None
                ),
                extensions=_as_map(row.get("extensions")),
            )
        except ElectricProtectionError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def protection_device_kind_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("device_kinds")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("device_kinds")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("device_kind_id", ""))):
        device_kind_id = str(row.get("device_kind_id", "")).strip().lower()
        if device_kind_id in _VALID_DEVICE_KINDS:
            out[device_kind_id] = {
                "schema_version": "1.0.0",
                "device_kind_id": device_kind_id,
                "schema_ref": str(row.get("schema_ref", "")).strip(),
                "extensions": _canon(_as_map(row.get("extensions"))),
            }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def coordination_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("coordination_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("coordination_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("coordination_policy_id", ""))):
        policy_id = str(row.get("coordination_policy_id", "")).strip()
        if not policy_id:
            continue
        if policy_id not in _VALID_COORDINATION_POLICIES:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "coordination_policy_id": policy_id,
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _fault_device_candidates(
    *,
    fault_row: Mapping[str, object],
    devices_by_edge_id: Mapping[str, List[dict]],
) -> List[dict]:
    target_kind = str(fault_row.get("target_kind", "")).strip()
    target_id = str(fault_row.get("target_id", "")).strip()
    if target_kind != "edge" or not target_id:
        return []
    return [dict(row) for row in list(devices_by_edge_id.get(target_id) or [])]


def _trip_threshold_for_fault(*, fault_kind_id: str, settings_row: Mapping[str, object]) -> int:
    settings = dict(settings_row or {})
    if str(fault_kind_id).strip() == "fault.ground_fault":
        return int(max(1, _as_int(settings.get("gfci_threshold", 1), 1)))
    if str(fault_kind_id).strip() == "fault.overcurrent":
        return int(max(1, _as_int(settings.get("trip_threshold_S", 1), 1)))
    return 1


def _trip_measure_for_fault(*, fault_row: Mapping[str, object]) -> int:
    fault = _as_map(fault_row)
    ext = _as_map(fault.get("extensions"))
    fault_kind_id = str(fault.get("fault_kind_id", "")).strip()
    if fault_kind_id == "fault.overcurrent":
        return int(
            max(
                0,
                _as_int(
                    ext.get("apparent_s", fault.get("severity", 0)),
                    _as_int(fault.get("severity", 0), 0),
                ),
            )
        )
    return int(max(0, _as_int(fault.get("severity", 0), 0)))


def _coordination_sort_key(
    *,
    candidate_row: Mapping[str, object],
    policy_id: str,
) -> Tuple[int, int, str, str]:
    row = dict(candidate_row or {})
    settings_ext = _as_map(_as_map(row.get("settings")).get("extensions"))
    device_ext = _as_map(_as_map(row.get("device")).get("extensions"))
    downstream_rank = int(
        max(
            0,
            _as_int(
                settings_ext.get(
                    "downstream_rank",
                    device_ext.get("downstream_rank", 0),
                ),
                0,
            ),
        )
    )
    strict_priority = int(
        max(
            0,
            _as_int(
                settings_ext.get(
                    "coord_priority",
                    device_ext.get("coord_priority", downstream_rank),
                ),
                downstream_rank,
            ),
        )
    )
    if policy_id == "coord.upstream_first":
        primary = -1 * downstream_rank
    elif policy_id == "coord.strict_table":
        primary = strict_priority
    else:
        primary = downstream_rank
    delay_ticks = int(max(0, _as_int(_as_map(row.get("settings")).get("trip_delay_ticks", 0), 0)))
    return (
        int(primary),
        int(delay_ticks),
        str(_as_map(row.get("device")).get("device_id", "")),
        str(_as_map(row.get("fault")).get("fault_id", "")),
    )


def evaluate_protection_trip_plan(
    *,
    fault_rows: object,
    protection_device_rows: object,
    protection_settings_rows: object,
    current_tick: int,
    coordination_policy_id: str,
    max_trip_actions: int,
) -> dict:
    active_faults = sorted(
        (
            dict(row)
            for row in list(fault_rows or [])
            if isinstance(row, Mapping) and bool(row.get("active", False))
        ),
        key=lambda row: (str(row.get("target_kind", "")), str(row.get("target_id", "")), str(row.get("fault_kind_id", ""))),
    )
    devices = normalize_protection_device_rows(protection_device_rows)
    settings_by_id = dict(
        (
            str(row.get("settings_id", "")).strip(),
            dict(row),
        )
        for row in normalize_protection_settings_rows(protection_settings_rows)
        if str(row.get("settings_id", "")).strip()
    )
    devices_by_edge_id: Dict[str, List[dict]] = {}
    for row in devices:
        attached_to = _as_map(row.get("attached_to"))
        edge_id = str(attached_to.get("edge_id", "")).strip()
        if edge_id:
            devices_by_edge_id.setdefault(edge_id, []).append(dict(row))
    for edge_id in sorted(devices_by_edge_id.keys()):
        devices_by_edge_id[edge_id] = sorted(
            devices_by_edge_id[edge_id],
            key=lambda row: str(row.get("device_id", "")),
        )

    policy_id = str(coordination_policy_id or "").strip() or "coord.downstream_first"
    if policy_id not in _VALID_COORDINATION_POLICIES:
        policy_id = "coord.downstream_first"

    candidate_rows: List[dict] = []
    for fault_row in active_faults:
        for device_row in _fault_device_candidates(fault_row=fault_row, devices_by_edge_id=devices_by_edge_id):
            settings_ref = str(device_row.get("settings_ref", "")).strip()
            settings_row = dict(settings_by_id.get(settings_ref) or {"settings_id": settings_ref})
            threshold = _trip_threshold_for_fault(
                fault_kind_id=str(fault_row.get("fault_kind_id", "")).strip(),
                settings_row=settings_row,
            )
            trip_measure = _trip_measure_for_fault(fault_row=fault_row)
            if trip_measure < threshold:
                continue
            candidate_rows.append(
                {
                    "fault": dict(fault_row),
                    "device": dict(device_row),
                    "settings": dict(settings_row),
                    "coordination_group_id": str(
                        settings_row.get("coordination_group_id", "")
                    ).strip()
                    or str(_as_map(settings_row.get("extensions")).get("coordination_group_id", "")).strip()
                    or "coord.group.default",
                }
            )

    grouped: Dict[str, List[dict]] = {}
    for row in candidate_rows:
        group_id = str(row.get("coordination_group_id", "")).strip() or "coord.group.default"
        grouped.setdefault(group_id, []).append(dict(row))

    ordered_candidates: List[dict] = []
    for group_id in sorted(grouped.keys()):
        group_rows = sorted(
            grouped[group_id],
            key=lambda row: _coordination_sort_key(candidate_row=row, policy_id=policy_id),
        )
        ordered_candidates.extend(group_rows)

    max_actions = int(max(0, _as_int(max_trip_actions, 0)))
    planned_rows: List[dict] = []
    deferred_device_ids: List[str] = []
    events: List[dict] = []
    seen_device_ids = set()
    for idx, row in enumerate(ordered_candidates):
        device = _as_map(row.get("device"))
        fault = _as_map(row.get("fault"))
        settings = _as_map(row.get("settings"))
        device_id = str(device.get("device_id", "")).strip()
        if (not device_id) or (device_id in seen_device_ids):
            continue
        if idx >= max_actions:
            deferred_device_ids.append(device_id)
            continue
        seen_device_ids.add(device_id)
        ext = _as_map(device.get("extensions"))
        channel_id = str(ext.get("channel_id", "")).strip() or None
        edge_id = str(_as_map(device.get("attached_to")).get("edge_id", "")).strip() or None
        trip_row = {
            "device_id": device_id,
            "device_kind_id": str(device.get("device_kind_id", "")).strip(),
            "state_machine_id": str(device.get("state_machine_id", "")).strip(),
            "channel_id": channel_id,
            "edge_id": edge_id,
            "fault_id": str(fault.get("fault_id", "")).strip(),
            "fault_kind_id": str(fault.get("fault_kind_id", "")).strip(),
            "coordination_group_id": str(row.get("coordination_group_id", "")).strip() or "coord.group.default",
            "coordination_policy_id": policy_id,
            "trip_delay_ticks": int(max(0, _as_int(settings.get("trip_delay_ticks", 0), 0))),
            "trip_tick": int(max(0, _as_int(current_tick, 0))),
            "trip_threshold": int(_trip_threshold_for_fault(fault_kind_id=str(fault.get("fault_kind_id", "")).strip(), settings_row=settings)),
            "fault_severity": int(max(0, _as_int(fault.get("severity", 0), 0))),
        }
        planned_rows.append(trip_row)
        events.append(
            build_safety_event(
                event_id="",
                tick=int(max(0, _as_int(current_tick, 0))),
                instance_id="instance.safety.elec.trip.{}".format(canonical_sha256({"device_id": device_id})[:16]),
                pattern_id="safety.breaker_trip",
                pattern_type="breaker",
                status="trip_planned",
                target_ids=[channel_id or edge_id or device_id],
                action_count=1,
                details={
                    "device_id": device_id,
                    "fault_id": str(fault.get("fault_id", "")).strip(),
                    "fault_kind_id": str(fault.get("fault_kind_id", "")).strip(),
                    "coordination_policy_id": policy_id,
                    "coordination_group_id": str(row.get("coordination_group_id", "")).strip() or "coord.group.default",
                },
                extensions={},
            )
        )

    safety_instances: List[dict] = []
    for row in sorted(planned_rows, key=lambda item: (str(item.get("coordination_group_id", "")), str(item.get("device_id", "")))):
        channel_id = str(row.get("channel_id", "")).strip()
        if not channel_id:
            continue
        instance_id = "instance.safety.elec.breaker.{}".format(canonical_sha256({"channel_id": channel_id})[:16])
        safety_instances.append(
            build_safety_instance(
                instance_id=instance_id,
                pattern_id="safety.breaker_trip",
                target_ids=[channel_id],
                active=True,
                created_tick=int(max(0, _as_int(current_tick, 0))),
                extensions={
                    "device_id": str(row.get("device_id", "")).strip(),
                    "coordination_group_id": str(row.get("coordination_group_id", "")).strip(),
                    "coordination_policy_id": policy_id,
                    "fault_id": str(row.get("fault_id", "")).strip(),
                    "fault_kind_id": str(row.get("fault_kind_id", "")).strip(),
                    "edge_id": str(row.get("edge_id", "")).strip() or None,
                    "trip_threshold": int(max(1, _as_int(row.get("trip_threshold", 1), 1))),
                    "fault_severity": int(max(0, _as_int(row.get("fault_severity", 0), 0))),
                },
            )
        )

    trip_event_hash_chain = canonical_sha256(
        [
            {
                "device_id": str(row.get("device_id", "")).strip(),
                "fault_id": str(row.get("fault_id", "")).strip(),
                "fault_kind_id": str(row.get("fault_kind_id", "")).strip(),
                "coordination_group_id": str(row.get("coordination_group_id", "")).strip(),
                "coordination_policy_id": str(row.get("coordination_policy_id", "")).strip(),
            }
            for row in sorted(planned_rows, key=lambda item: (str(item.get("coordination_group_id", "")), str(item.get("device_id", ""))))
        ]
    )
    return {
        "trip_rows": [
            dict(row)
            for row in sorted(
                planned_rows,
                key=lambda item: (str(item.get("coordination_group_id", "")), str(item.get("device_id", ""))),
            )
        ],
        "safety_instances": [dict(row) for row in sorted(safety_instances, key=lambda item: str(item.get("instance_id", "")))],
        "events": sorted(
            [dict(row) for row in events],
            key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("event_id", ""))),
        ),
        "deferred_device_ids": sorted(set(str(item).strip() for item in deferred_device_ids if str(item).strip())),
        "budget_outcome": "degraded" if deferred_device_ids else "complete",
        "cost_units": int(len(planned_rows)),
        "trip_event_hash_chain": str(trip_event_hash_chain),
    }


__all__ = [
    "REFUSAL_ELEC_PROTECTION_INVALID",
    "ElectricProtectionError",
    "build_protection_device",
    "build_protection_settings",
    "coordination_policy_rows_by_id",
    "deterministic_protection_device_id",
    "evaluate_protection_trip_plan",
    "normalize_protection_device_rows",
    "normalize_protection_settings_rows",
    "protection_device_kind_rows_by_id",
]
