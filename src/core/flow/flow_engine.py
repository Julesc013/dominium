"""Deterministic core FlowSystem helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.core.graph.network_graph_engine import normalize_network_graph
from src.core.graph.routing_engine import build_cross_shard_route_plan, normalize_graph_partition_row


REFUSAL_CORE_FLOW_INVALID = "refusal.core.flow.invalid"
REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID = "refusal.core.flow.solver_policy_invalid"
REFUSAL_CORE_FLOW_CAPACITY_INSUFFICIENT = "refusal.core.flow.capacity_insufficient"
REFUSAL_CORE_FLOW_OVERFLOW_REFUSED = "refusal.core.flow.overflow_refused"


class FlowEngineError(ValueError):
    """Deterministic FlowSystem refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _ordered_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    out: List[str] = []
    seen = set()
    for item in values:
        token = str(item).strip()
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _round_div_away_from_zero(numerator: int, denominator: int) -> int:
    if int(denominator) == 0:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "division by zero in FlowSystem fixed-point calculation",
            {"denominator": str(denominator)},
        )
    n = int(numerator)
    d = int(denominator)
    sign = -1 if (n < 0) ^ (d < 0) else 1
    abs_n = abs(n)
    abs_d = abs(d)
    quotient = abs_n // abs_d
    remainder = abs_n % abs_d
    if remainder * 2 >= abs_d:
        quotient += 1
    return int(sign * quotient)


def _canonicalize_value(value: object) -> object:
    if isinstance(value, dict):
        out: Dict[str, object] = {}
        for key in sorted(value.keys(), key=lambda item: str(item)):
            out[str(key)] = _canonicalize_value(value[key])
        return out
    if isinstance(value, list):
        return [_canonicalize_value(item) for item in list(value)]
    return value


def _normalize_component_map(value: object) -> Dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    out: Dict[str, int] = {}
    for key in sorted(value.keys(), key=lambda item: str(item)):
        token = str(key).strip()
        if not token:
            continue
        out[token] = int(max(0, _as_int(value.get(key, 0), 0)))
    return out


def _component_policy_row_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("policies")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("policies") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        raw_rules = dict(row.get("per_quantity_rules") or {}) if isinstance(row.get("per_quantity_rules"), Mapping) else {}
        normalized_rules: Dict[str, dict] = {}
        for quantity_id in sorted(raw_rules.keys(), key=lambda item: str(item)):
            token = str(quantity_id).strip()
            if not token:
                continue
            raw_rule = dict(raw_rules.get(quantity_id) or {}) if isinstance(raw_rules.get(quantity_id), Mapping) else {}
            cap_limit = raw_rule.get("capacity_limit")
            if cap_limit is not None:
                cap_limit = int(max(0, _as_int(cap_limit, 0)))
            cap_scale = raw_rule.get("capacity_scale_permille")
            if cap_scale is not None:
                cap_scale = int(max(0, _as_int(cap_scale, 0)))
            loss_fraction = raw_rule.get("loss_fraction")
            if loss_fraction is not None:
                loss_fraction = int(max(0, _as_int(loss_fraction, 0)))
            transform_to_quantity_id = raw_rule.get("transform_to_quantity_id")
            transform_to_quantity_id = None if transform_to_quantity_id is None else str(transform_to_quantity_id).strip() or None
            preserve_conservation = raw_rule.get("preserve_conservation")
            if preserve_conservation is not None:
                preserve_conservation = bool(preserve_conservation)
            normalized_rules[token] = {
                "capacity_limit": cap_limit,
                "capacity_scale_permille": cap_scale,
                "loss_fraction": loss_fraction,
                "transform_to_quantity_id": transform_to_quantity_id,
                "preserve_conservation": preserve_conservation,
                "extensions": dict(_canonicalize_value(dict(raw_rule.get("extensions") or {}))),
            }
        out[policy_id] = {
            "schema_version": "1.0.0",
            "policy_id": policy_id,
            "per_quantity_rules": normalized_rules,
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": dict(_canonicalize_value(dict(row.get("extensions") or {}))),
        }
    return out


def _quantity_bundle_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("quantity_bundles")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("quantity_bundles") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("bundle_id", ""))):
        bundle_id = str(row.get("bundle_id", "")).strip()
        if not bundle_id:
            continue
        quantity_ids = _ordered_unique_strings(list(row.get("quantity_ids") or []))
        if not quantity_ids:
            continue
        out[bundle_id] = {
            "schema_version": "1.0.0",
            "bundle_id": bundle_id,
            "quantity_ids": quantity_ids,
            "description": str(row.get("description", "")).strip(),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": dict(_canonicalize_value(dict(row.get("extensions") or {}))),
        }
    return out


def _allocate_total_by_component_weights(*, total: int, component_ids: List[str], weights: Mapping[str, int] | None = None) -> Dict[str, int]:
    normalized_total = int(max(0, _as_int(total, 0)))
    ordered_ids = [str(item).strip() for item in list(component_ids or []) if str(item).strip()]
    if not ordered_ids:
        return {}
    weight_map_raw = dict(weights or {})
    weight_map: Dict[str, int] = {}
    for component_id in ordered_ids:
        raw_weight = weight_map_raw.get(component_id)
        weight_map[component_id] = int(max(0, _as_int(raw_weight, 0)))
    if all(value <= 0 for value in weight_map.values()):
        weight_map = dict((component_id, 1) for component_id in ordered_ids)
    weight_sum = int(sum(weight_map.values()))
    if weight_sum <= 0:
        return dict((component_id, 0) for component_id in ordered_ids)
    out: Dict[str, int] = {}
    allocated = 0
    for component_id in ordered_ids:
        numerator = int(normalized_total) * int(weight_map.get(component_id, 0))
        share = int(max(0, _round_div_away_from_zero(numerator, weight_sum)))
        out[component_id] = int(share)
        allocated += int(share)
    if allocated > normalized_total:
        overflow = int(allocated - normalized_total)
        for component_id in reversed(ordered_ids):
            if overflow <= 0:
                break
            current = int(out.get(component_id, 0))
            if current <= 0:
                continue
            delta = min(current, overflow)
            out[component_id] = int(current - delta)
            overflow -= int(delta)
    elif allocated < normalized_total:
        remainder = int(normalized_total - allocated)
        for component_id in ordered_ids:
            if remainder <= 0:
                break
            out[component_id] = int(out.get(component_id, 0) + 1)
            remainder -= 1
    return dict((component_id, int(out.get(component_id, 0))) for component_id in ordered_ids)


def _sum_component_map(values: Mapping[str, object] | None) -> int:
    if not isinstance(values, Mapping):
        return 0
    total = 0
    for key in values.keys():
        total += int(max(0, _as_int(values.get(key, 0), 0)))
    return int(max(0, total))


def _take_from_component_map(
    *,
    component_map: Mapping[str, object] | None,
    amount: int,
    component_ids: List[str],
    weights: Mapping[str, int] | None = None,
) -> Dict[str, int]:
    normalized_map = _normalize_component_map(component_map)
    target = int(max(0, _as_int(amount, 0)))
    if target <= 0:
        return dict((component_id, 0) for component_id in list(component_ids or []))
    available_total = _sum_component_map(normalized_map)
    if available_total <= 0:
        return _allocate_total_by_component_weights(
            total=target,
            component_ids=list(component_ids or []),
            weights=weights,
        )
    desired = _allocate_total_by_component_weights(
        total=min(target, available_total),
        component_ids=list(component_ids or []),
        weights=weights,
    )
    out: Dict[str, int] = {}
    taken = 0
    for component_id in list(component_ids or []):
        value = int(max(0, _as_int(desired.get(component_id, 0), 0)))
        available = int(max(0, _as_int(normalized_map.get(component_id, 0), 0)))
        value = min(value, available)
        out[component_id] = int(value)
        taken += int(value)
    if taken < min(target, available_total):
        remainder = int(min(target, available_total) - taken)
        for component_id in list(component_ids or []):
            if remainder <= 0:
                break
            available = int(max(0, _as_int(normalized_map.get(component_id, 0), 0)))
            current = int(out.get(component_id, 0))
            room = int(max(0, available - current))
            if room <= 0:
                continue
            delta = min(room, remainder)
            out[component_id] = int(current + delta)
            remainder -= int(delta)
    return dict((component_id, int(max(0, _as_int(out.get(component_id, 0), 0)))) for component_id in list(component_ids or []))


def _subtract_component_maps(base: Mapping[str, object] | None, delta: Mapping[str, object] | None) -> Dict[str, int]:
    base_map = _normalize_component_map(base)
    delta_map = _normalize_component_map(delta)
    out: Dict[str, int] = {}
    for key in sorted(set(list(base_map.keys()) + list(delta_map.keys()))):
        value = int(max(0, int(base_map.get(key, 0)) - int(delta_map.get(key, 0))))
        if value > 0:
            out[key] = value
    return out


def _add_component_maps(left: Mapping[str, object] | None, right: Mapping[str, object] | None) -> Dict[str, int]:
    left_map = _normalize_component_map(left)
    right_map = _normalize_component_map(right)
    out: Dict[str, int] = {}
    for key in sorted(set(list(left_map.keys()) + list(right_map.keys()))):
        value = int(max(0, int(left_map.get(key, 0)) + int(right_map.get(key, 0))))
        if value > 0:
            out[key] = value
    return out


def _loss_transform_rows_from_entries(entries: List[dict]) -> List[dict]:
    rows_by_key: Dict[str, dict] = {}
    for row in list(entries or []):
        if not isinstance(row, Mapping):
            continue
        if not bool(row.get("transform_applied", False)):
            continue
        channel_id = str(row.get("channel_id", "")).strip()
        to_quantity_id = str(row.get("quantity_id", "")).strip()
        from_quantity_id = str(row.get("transformed_from_quantity_id", "")).strip()
        amount = int(max(0, _as_int(row.get("lost_amount", 0), 0)))
        if (not channel_id) or (not to_quantity_id) or (not from_quantity_id) or amount <= 0:
            continue
        row_key = "{}::{}::{}".format(channel_id, from_quantity_id, to_quantity_id)
        current = dict(rows_by_key.get(row_key) or {})
        rows_by_key[row_key] = {
            "channel_id": channel_id,
            "from_quantity_id": from_quantity_id,
            "to_quantity_id": to_quantity_id,
            "amount": int(max(0, _as_int(current.get("amount", 0), 0)) + amount),
        }
    return [dict(rows_by_key[key]) for key in sorted(rows_by_key.keys())]


def _loss_conservation_exceptions(entries: List[dict]) -> List[dict]:
    out: List[dict] = []
    for row in list(entries or []):
        if not isinstance(row, Mapping):
            continue
        if not bool(row.get("conservation_exception_logged", False)):
            continue
        out.append(
            {
                "channel_id": str(row.get("channel_id", "")).strip(),
                "quantity_id": str(row.get("quantity_id", "")).strip(),
                "lost_amount": int(max(0, _as_int(row.get("lost_amount", 0), 0))),
                "exception_code": str(row.get("exception_code", "")).strip() or "exception.flow.conservation_unresolved",
            }
        )
    return sorted(
        (dict(item) for item in out),
        key=lambda item: (str(item.get("channel_id", "")), str(item.get("quantity_id", ""))),
    )


def _bundle_component_outcome(
    *,
    transferred_amount: int,
    lost_amount: int,
    component_ids: List[str],
    capacity_policy_row: Mapping[str, object] | None,
    loss_policy_row: Mapping[str, object] | None,
    scale: int,
    channel_loss_fraction: int,
    channel_extensions: Mapping[str, object] | None,
) -> dict:
    ids = [str(item).strip() for item in list(component_ids or []) if str(item).strip()]
    if not ids:
        return {
            "transferred_components": {},
            "lost_components": {},
            "loss_transforms": {},
            "conservation_exceptions": [],
        }
    ext = dict(channel_extensions or {})
    requested_weights = _normalize_component_map(ext.get("component_weights"))
    transfer_components = _allocate_total_by_component_weights(
        total=int(max(0, _as_int(transferred_amount, 0))),
        component_ids=ids,
        weights=requested_weights,
    )
    lost_components = _allocate_total_by_component_weights(
        total=int(max(0, _as_int(lost_amount, 0))),
        component_ids=ids,
        weights=requested_weights,
    )

    capacity_rules = dict((dict(capacity_policy_row or {}).get("per_quantity_rules") or {}))
    adjusted_transfer: Dict[str, int] = dict((component_id, int(transfer_components.get(component_id, 0))) for component_id in ids)
    for component_id in ids:
        rule = dict(capacity_rules.get(component_id) or {})
        value = int(adjusted_transfer.get(component_id, 0))
        capacity_limit = rule.get("capacity_limit")
        if capacity_limit is not None:
            value = min(value, int(max(0, _as_int(capacity_limit, 0))))
        capacity_scale_permille = rule.get("capacity_scale_permille")
        if capacity_scale_permille is not None:
            scaled = _round_div_away_from_zero(
                int(adjusted_transfer.get(component_id, 0)) * int(max(0, _as_int(capacity_scale_permille, 0))),
                1000,
            )
            value = min(value, int(max(0, scaled)))
        trimmed = int(max(0, int(adjusted_transfer.get(component_id, 0)) - int(value)))
        adjusted_transfer[component_id] = int(value)
        if trimmed > 0:
            lost_components[component_id] = int(max(0, int(lost_components.get(component_id, 0)) + int(trimmed)))

    transfer_total = int(sum(adjusted_transfer.values()))
    target_transfer = int(max(0, _as_int(transferred_amount, 0)))
    if transfer_total < target_transfer:
        remainder = int(target_transfer - transfer_total)
        for component_id in ids:
            if remainder <= 0:
                break
            adjusted_transfer[component_id] = int(adjusted_transfer.get(component_id, 0) + 1)
            remainder -= 1
    elif transfer_total > target_transfer:
        overflow = int(transfer_total - target_transfer)
        for component_id in reversed(ids):
            if overflow <= 0:
                break
            current = int(adjusted_transfer.get(component_id, 0))
            if current <= 0:
                continue
            delta = min(current, overflow)
            adjusted_transfer[component_id] = int(current - delta)
            lost_components[component_id] = int(max(0, int(lost_components.get(component_id, 0)) + int(delta)))
            overflow -= int(delta)

    loss_rules = dict((dict(loss_policy_row or {}).get("per_quantity_rules") or {}))
    loss_transforms: Dict[str, int] = {}
    conservation_exceptions: List[dict] = []
    for component_id in ids:
        rule = dict(loss_rules.get(component_id) or {})
        rule_loss_fraction = rule.get("loss_fraction")
        if rule_loss_fraction is not None:
            # Re-partition total loss deterministically with per-component override.
            desired = _round_div_away_from_zero(
                int(max(0, _as_int(adjusted_transfer.get(component_id, 0), 0) + _as_int(lost_components.get(component_id, 0), 0)))
                * int(max(0, _as_int(rule_loss_fraction, 0))),
                int(max(1, _as_int(scale, 1))),
            )
            current_loss = int(max(0, _as_int(lost_components.get(component_id, 0), 0)))
            if desired > current_loss:
                delta = int(desired - current_loss)
                steal = min(delta, int(max(0, _as_int(adjusted_transfer.get(component_id, 0), 0))))
                adjusted_transfer[component_id] = int(max(0, int(adjusted_transfer.get(component_id, 0)) - int(steal)))
                lost_components[component_id] = int(current_loss + int(steal))
            elif desired < current_loss:
                delta = int(current_loss - desired)
                lost_components[component_id] = int(max(0, current_loss - delta))
                adjusted_transfer[component_id] = int(max(0, int(adjusted_transfer.get(component_id, 0)) + int(delta)))
        transform_to_quantity_id = rule.get("transform_to_quantity_id")
        transform_to_quantity_id = None if transform_to_quantity_id is None else str(transform_to_quantity_id).strip() or None
        if transform_to_quantity_id:
            loss_transforms[transform_to_quantity_id] = int(
                max(0, int(loss_transforms.get(transform_to_quantity_id, 0)) + int(max(0, _as_int(lost_components.get(component_id, 0), 0))))
            )
        elif bool(rule.get("preserve_conservation", False)) and int(max(0, _as_int(lost_components.get(component_id, 0), 0))) > 0:
            conservation_exceptions.append(
                {
                    "quantity_id": component_id,
                    "lost_amount": int(max(0, _as_int(lost_components.get(component_id, 0), 0))),
                    "reason": "missing_transform_target",
                }
            )

    if int(max(0, _as_int(channel_loss_fraction, 0))) <= 0:
        # Keep deterministic output stable for zero-loss channels.
        loss_transforms = dict((key, int(loss_transforms[key])) for key in sorted(loss_transforms.keys()))
    return {
        "transferred_components": dict((component_id, int(max(0, _as_int(adjusted_transfer.get(component_id, 0), 0)))) for component_id in ids),
        "lost_components": dict((component_id, int(max(0, _as_int(lost_components.get(component_id, 0), 0)))) for component_id in ids),
        "loss_transforms": dict((key, int(loss_transforms[key])) for key in sorted(loss_transforms.keys())),
        "conservation_exceptions": sorted(
            (dict(row) for row in conservation_exceptions if isinstance(row, dict)),
            key=lambda row: (str(row.get("quantity_id", "")), int(_as_int(row.get("lost_amount", 0), 0))),
        ),
    }


def normalize_flow_solver_policy(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    solver_policy_id = str(payload.get("solver_policy_id", "")).strip()
    mode = str(payload.get("mode", "")).strip()
    allow_partial_transfer = payload.get("allow_partial_transfer")
    overflow_policy = str(payload.get("overflow_policy", "")).strip()
    if not solver_policy_id or mode not in {"bulk", "segmented"} or not isinstance(allow_partial_transfer, bool):
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID,
            "flow solver policy missing required deterministic fields",
            {
                "solver_policy_id": solver_policy_id,
                "mode": mode,
                "allow_partial_transfer": str(allow_partial_transfer),
            },
        )
    if overflow_policy not in {"refuse", "queue", "spill"}:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID,
            "flow solver policy overflow_policy must be refuse|queue|spill",
            {"solver_policy_id": solver_policy_id, "overflow_policy": overflow_policy},
        )
    return {
        "schema_version": "1.0.0",
        "solver_policy_id": solver_policy_id,
        "mode": mode,
        "allow_partial_transfer": bool(allow_partial_transfer),
        "overflow_policy": overflow_policy,
        "extensions": dict(_canonicalize_value(dict(payload.get("extensions") or {}))),
    }


def flow_solver_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("solver_policies")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("solver_policies") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("solver_policy_id", ""))):
        normalized = normalize_flow_solver_policy(row)
        out[str(normalized.get("solver_policy_id", ""))] = normalized
    return out


def normalize_flow_channel(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    channel_id = str(payload.get("channel_id", "")).strip()
    graph_id = str(payload.get("graph_id", "")).strip()
    quantity_id = str(payload.get("quantity_id", "")).strip()
    quantity_bundle_id = str(payload.get("quantity_bundle_id", "")).strip()
    component_capacity_policy_id = str(payload.get("component_capacity_policy_id", "")).strip()
    component_loss_policy_id = str(payload.get("component_loss_policy_id", "")).strip()
    source_node_id = str(payload.get("source_node_id", "")).strip()
    sink_node_id = str(payload.get("sink_node_id", "")).strip()
    solver_policy_id = str(payload.get("solver_policy_id", "")).strip()
    if not channel_id or not graph_id or not source_node_id or not sink_node_id or not solver_policy_id:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "flow channel missing required identifiers",
            {
                "channel_id": channel_id,
                "graph_id": graph_id,
                "quantity_id": quantity_id,
                "quantity_bundle_id": quantity_bundle_id,
                "source_node_id": source_node_id,
                "sink_node_id": sink_node_id,
                "solver_policy_id": solver_policy_id,
            },
        )
    if (not quantity_id) and (not quantity_bundle_id):
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "flow channel requires quantity_id or quantity_bundle_id",
            {
                "channel_id": channel_id,
                "quantity_id": quantity_id,
                "quantity_bundle_id": quantity_bundle_id,
            },
        )
    capacity_per_tick = payload.get("capacity_per_tick")
    if capacity_per_tick is None:
        normalized_capacity = None
    else:
        normalized_capacity = int(_as_int(capacity_per_tick, 0))
        if normalized_capacity < 0:
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_INVALID,
                "flow channel capacity_per_tick must be >= 0",
                {"channel_id": channel_id, "capacity_per_tick": int(normalized_capacity)},
            )
    delay_ticks = payload.get("delay_ticks")
    if delay_ticks is None:
        normalized_delay = 0
    else:
        normalized_delay = int(_as_int(delay_ticks, 0))
        if normalized_delay < 0:
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_INVALID,
                "flow channel delay_ticks must be >= 0",
                {"channel_id": channel_id, "delay_ticks": int(normalized_delay)},
            )
    loss_fraction = payload.get("loss_fraction")
    if loss_fraction is None:
        normalized_loss_fraction = 0
    else:
        normalized_loss_fraction = int(_as_int(loss_fraction, 0))
        if normalized_loss_fraction < 0:
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_INVALID,
                "flow channel loss_fraction must be >= 0",
                {"channel_id": channel_id, "loss_fraction": int(normalized_loss_fraction)},
            )
    priority = int(_as_int(payload.get("priority", 0), 0))
    if priority < 0:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "flow channel priority must be >= 0",
            {"channel_id": channel_id, "priority": int(priority)},
        )
    schema_version = str(payload.get("schema_version", "")).strip()
    if schema_version not in {"1.0.0", "1.1.0"}:
        schema_version = "1.1.0" if quantity_bundle_id else "1.0.0"
    return {
        "schema_version": schema_version,
        "channel_id": channel_id,
        "graph_id": graph_id,
        "quantity_id": quantity_id or None,
        "quantity_bundle_id": quantity_bundle_id or None,
        "component_capacity_policy_id": component_capacity_policy_id or None,
        "component_loss_policy_id": component_loss_policy_id or None,
        "source_node_id": source_node_id,
        "sink_node_id": sink_node_id,
        "capacity_per_tick": normalized_capacity,
        "delay_ticks": int(normalized_delay),
        "loss_fraction": int(normalized_loss_fraction),
        "solver_policy_id": solver_policy_id,
        "priority": int(priority),
        "extensions": dict(_canonicalize_value(dict(payload.get("extensions") or {}))),
    }


def normalize_flow_transfer_event(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    event_id = str(payload.get("event_id", "")).strip()
    channel_id = str(payload.get("channel_id", "")).strip()
    if not event_id or not channel_id:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "flow transfer event requires event_id and channel_id",
            {"event_id": event_id, "channel_id": channel_id},
        )
    tick = max(0, _as_int(payload.get("tick", 0), 0))
    transferred_amount = max(0, _as_int(payload.get("transferred_amount", 0), 0))
    lost_amount = max(0, _as_int(payload.get("lost_amount", 0), 0))
    transferred_components = _normalize_component_map(payload.get("transferred_components"))
    lost_components = _normalize_component_map(payload.get("lost_components"))
    schema_version = str(payload.get("schema_version", "")).strip()
    if schema_version not in {"1.0.0", "1.1.0"}:
        schema_version = "1.1.0" if transferred_components or lost_components else "1.0.0"
    ledger_delta_refs = _sorted_unique_strings(payload.get("ledger_delta_refs"))
    row_out = {
        "schema_version": schema_version,
        "event_id": event_id,
        "tick": int(tick),
        "channel_id": channel_id,
        "transferred_amount": int(transferred_amount),
        "lost_amount": int(lost_amount),
        "transferred_components": dict(transferred_components),
        "lost_components": dict(lost_components),
        "ledger_delta_refs": list(ledger_delta_refs),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": dict(_canonicalize_value(dict(payload.get("extensions") or {}))),
    }
    if not row_out["deterministic_fingerprint"]:
        row_out["deterministic_fingerprint"] = canonical_sha256(dict(row_out, deterministic_fingerprint=""))
    return row_out


def _ledger_delta_refs(channel_id: str, tick: int, source_debit: int, sink_credit: int, lost_amount: int) -> List[str]:
    refs = []
    if int(source_debit) > 0:
        refs.append(
            "ledger.delta.debit.{}".format(
                canonical_sha256({"channel_id": channel_id, "tick": int(tick), "kind": "debit"})[:24]
            )
        )
    if int(sink_credit) > 0:
        refs.append(
            "ledger.delta.credit.{}".format(
                canonical_sha256({"channel_id": channel_id, "tick": int(tick), "kind": "credit"})[:24]
            )
        )
    if int(lost_amount) > 0:
        refs.append(
            "ledger.delta.loss.{}".format(
                canonical_sha256({"channel_id": channel_id, "tick": int(tick), "kind": "loss"})[:24]
            )
        )
    return sorted(refs)


def flow_transfer(
    *,
    quantity: int,
    loss_fraction: int,
    scale: int,
    capacity_per_tick: int | None = None,
    delay_ticks: int = 0,
) -> dict:
    quantity_mass = int(max(0, _as_int(quantity, 0)))
    normalized_capacity = None if capacity_per_tick is None else int(max(0, _as_int(capacity_per_tick, 0)))
    processed_mass = quantity_mass if normalized_capacity is None else int(min(quantity_mass, normalized_capacity))
    normalized_loss_fraction = int(max(0, _as_int(loss_fraction, 0)))
    if normalized_loss_fraction > int(scale):
        normalized_loss_fraction = int(scale)
    if processed_mass <= 0 or normalized_loss_fraction <= 0:
        loss_mass = 0
    else:
        loss_mass = int(max(0, _round_div_away_from_zero(int(processed_mass) * int(normalized_loss_fraction), int(scale))))
    delivered_mass = int(max(0, int(processed_mass) - int(loss_mass)))
    deferred_mass = int(max(0, int(quantity_mass) - int(processed_mass)))
    return {
        "processed_mass": int(processed_mass),
        "delivered_mass": int(delivered_mass),
        "loss_mass": int(loss_mass),
        "deferred_mass": int(deferred_mass),
        "delay_ticks": int(max(0, _as_int(delay_ticks, 0))),
    }


def _solver_policy_for_channel(*, channel_row: Mapping[str, object], solver_policies: Mapping[str, object] | None) -> dict:
    rows = dict(solver_policies or {})
    solver_policy_id = str(channel_row.get("solver_policy_id", "")).strip()
    row = dict(rows.get(solver_policy_id) or {})
    if not row:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID,
            "flow channel references unknown solver policy",
            {"channel_id": str(channel_row.get("channel_id", "")), "solver_policy_id": solver_policy_id},
        )
    return normalize_flow_solver_policy(row)


def _normalize_balances(value: Mapping[str, object] | None) -> Dict[str, int]:
    rows = dict(value or {})
    out: Dict[str, int] = {}
    for key in sorted(rows.keys(), key=lambda item: str(item)):
        node_id = str(key).strip()
        if not node_id:
            continue
        out[node_id] = max(0, _as_int(rows.get(key, 0), 0))
    return out


def _normalize_sink_caps(value: Mapping[str, object] | None) -> Dict[str, int]:
    rows = dict(value or {})
    out: Dict[str, int] = {}
    for key in sorted(rows.keys(), key=lambda item: str(item)):
        node_id = str(key).strip()
        if not node_id:
            continue
        out[node_id] = max(0, _as_int(rows.get(key, 0), 0))
    return out


def _normalize_channel_runtime(value: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = dict(value or {})
    out: Dict[str, dict] = {}
    for key in sorted(rows.keys(), key=lambda item: str(item)):
        channel_id = str(key).strip()
        if not channel_id:
            continue
        row = dict(rows.get(key) or {})
        queued_amount = max(0, _as_int(row.get("queued_amount", 0), 0))
        queued_components = _normalize_component_map(row.get("queued_components"))
        in_transit = []
        for item in sorted((entry for entry in list(row.get("in_transit") or []) if isinstance(entry, dict)), key=lambda entry: (_as_int(entry.get("ready_tick", 0), 0), _as_int(entry.get("amount", 0), 0))):
            amount = max(0, _as_int(item.get("amount", 0), 0))
            ready_tick = max(0, _as_int(item.get("ready_tick", 0), 0))
            if amount <= 0:
                continue
            in_transit.append(
                {
                    "ready_tick": int(ready_tick),
                    "amount": int(amount),
                    "components": _normalize_component_map(item.get("components")),
                }
            )
        out[channel_id] = {
            "queued_amount": int(queued_amount),
            "queued_components": dict(queued_components),
            "in_transit": list(in_transit),
        }
    return out


def _route_node_ids_from_edges(graph_row: Mapping[str, object], source_node_id: str, edge_ids: List[str]) -> List[str]:
    graph = normalize_network_graph(graph_row)
    edge_index: Dict[str, dict] = {}
    for edge in list(graph.get("edges") or []):
        row = dict(edge or {})
        edge_id = str(row.get("edge_id", "")).strip()
        if edge_id:
            edge_index[edge_id] = row
    current = str(source_node_id).strip()
    node_ids = [current] if current else []
    for edge_id in list(edge_ids or []):
        row = dict(edge_index.get(str(edge_id).strip()) or {})
        if not row:
            return []
        from_node_id = str(row.get("from_node_id", "")).strip()
        to_node_id = str(row.get("to_node_id", "")).strip()
        if current and from_node_id != current:
            return []
        current = to_node_id
        if current:
            node_ids.append(current)
    return node_ids


def _cross_shard_flow_plan(*, channel_row: Mapping[str, object], graph_row: Mapping[str, object] | None, partition_row: Mapping[str, object] | None) -> dict:
    if not graph_row or not partition_row:
        return {
            "partitioned": False,
            "deterministic_fingerprint": canonical_sha256({"partitioned": False, "channel_id": str(channel_row.get("channel_id", ""))}),
            "segments": [],
            "cross_shard_boundaries": [],
        }
    graph = normalize_network_graph(graph_row)
    partition = normalize_graph_partition_row(partition_row, graph_row=graph)
    ext = dict(channel_row.get("extensions") or {})
    route_edge_ids = _sorted_unique_strings(ext.get("route_edge_ids"))
    route_node_ids = _sorted_unique_strings(ext.get("route_node_ids"))
    if not route_edge_ids:
        return {
            "partitioned": False,
            "deterministic_fingerprint": canonical_sha256({"partitioned": False, "channel_id": str(channel_row.get("channel_id", ""))}),
            "segments": [],
            "cross_shard_boundaries": [],
        }
    if not route_node_ids:
        route_node_ids = _route_node_ids_from_edges(graph, str(channel_row.get("source_node_id", "")), route_edge_ids)
    return build_cross_shard_route_plan(
        graph_row=graph,
        partition_row=partition,
        path_node_ids=list(route_node_ids),
        path_edge_ids=list(route_edge_ids),
    )


def tick_flow_channels(
    *,
    channels: object,
    node_balances: Mapping[str, object] | None,
    current_tick: int,
    fixed_point_scale: int,
    solver_policies: Mapping[str, object] | None,
    conserved_quantity_ids: object = None,
    max_channels: int | None = None,
    strict_budget: bool = False,
    sink_capacities: Mapping[str, object] | None = None,
    channel_runtime: Mapping[str, object] | None = None,
    graph_row: Mapping[str, object] | None = None,
    partition_row: Mapping[str, object] | None = None,
    cost_units_per_channel: int = 1,
    quantity_bundle_rows: Mapping[str, object] | None = None,
    component_capacity_policies: Mapping[str, object] | None = None,
    component_loss_policies: Mapping[str, object] | None = None,
) -> dict:
    if not isinstance(channels, list):
        channels = []
    normalized_channels = sorted(
        (normalize_flow_channel(dict(row)) for row in list(channels or []) if isinstance(row, dict)),
        key=lambda row: (str(row.get("channel_id", "")), int(_as_int(row.get("priority", 0), 0))),
    )
    balances = _normalize_balances(node_balances)
    sink_caps = _normalize_sink_caps(sink_capacities)
    runtime_by_channel = _normalize_channel_runtime(channel_runtime)
    conserved_ids = set(_sorted_unique_strings(list(conserved_quantity_ids or [])))
    policy_rows = dict(solver_policies or {})
    bundle_rows_by_id = _quantity_bundle_rows_by_id(quantity_bundle_rows)
    if (not bundle_rows_by_id) and isinstance(quantity_bundle_rows, Mapping):
        for key in sorted(quantity_bundle_rows.keys(), key=lambda item: str(item)):
            token = str(key).strip()
            row = dict(quantity_bundle_rows.get(key) or {}) if isinstance(quantity_bundle_rows.get(key), Mapping) else {}
            quantity_ids = _ordered_unique_strings(list(row.get("quantity_ids") or []))
            if token and quantity_ids:
                bundle_rows_by_id[token] = {
                    "schema_version": "1.0.0",
                    "bundle_id": token,
                    "quantity_ids": quantity_ids,
                    "description": str(row.get("description", "")).strip(),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                    "extensions": dict(_canonicalize_value(dict(row.get("extensions") or {}))),
                }
    capacity_policy_rows = _component_policy_row_by_id(component_capacity_policies)
    if (not capacity_policy_rows) and isinstance(component_capacity_policies, Mapping):
        for key in sorted(component_capacity_policies.keys(), key=lambda item: str(item)):
            token = str(key).strip()
            row = dict(component_capacity_policies.get(key) or {}) if isinstance(component_capacity_policies.get(key), Mapping) else {}
            if token and isinstance(row.get("per_quantity_rules"), Mapping):
                capacity_policy_rows[token] = {
                    "schema_version": "1.0.0",
                    "policy_id": token,
                    "per_quantity_rules": dict(row.get("per_quantity_rules") or {}),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                    "extensions": dict(_canonicalize_value(dict(row.get("extensions") or {}))),
                }
    loss_policy_rows = _component_policy_row_by_id(component_loss_policies)
    if (not loss_policy_rows) and isinstance(component_loss_policies, Mapping):
        for key in sorted(component_loss_policies.keys(), key=lambda item: str(item)):
            token = str(key).strip()
            row = dict(component_loss_policies.get(key) or {}) if isinstance(component_loss_policies.get(key), Mapping) else {}
            if token and isinstance(row.get("per_quantity_rules"), Mapping):
                loss_policy_rows[token] = {
                    "schema_version": "1.0.0",
                    "policy_id": token,
                    "per_quantity_rules": dict(row.get("per_quantity_rules") or {}),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                    "extensions": dict(_canonicalize_value(dict(row.get("extensions") or {}))),
                }

    scale = max(1, _as_int(fixed_point_scale, 1))
    tick = max(0, _as_int(current_tick, 0))
    limit = len(normalized_channels) if max_channels is None else max(0, _as_int(max_channels, 0))

    transfer_events: List[dict] = []
    loss_entries: List[dict] = []
    channel_results: List[dict] = []
    cross_shard_transfer_plans: List[dict] = []
    processed_count = 0
    remaining_count = 0

    for channel_row in normalized_channels:
        channel_id = str(channel_row.get("channel_id", ""))
        if processed_count >= int(limit):
            remaining_count += 1
            continue
        policy_row = _solver_policy_for_channel(channel_row=channel_row, solver_policies=policy_rows)
        overflow_policy = str(policy_row.get("overflow_policy", "queue"))
        allow_partial = bool(policy_row.get("allow_partial_transfer", True))

        source_node_id = str(channel_row.get("source_node_id", ""))
        sink_node_id = str(channel_row.get("sink_node_id", ""))
        source_available = max(0, _as_int(balances.get(source_node_id, 0), 0))
        sink_current = max(0, _as_int(balances.get(sink_node_id, 0), 0))
        runtime_row = dict(runtime_by_channel.get(channel_id) or {"queued_amount": 0, "queued_components": {}, "in_transit": []})
        queued_amount = max(0, _as_int(runtime_row.get("queued_amount", 0), 0))
        queued_components = _normalize_component_map(runtime_row.get("queued_components"))
        in_transit_rows = [
            dict(item)
            for item in sorted(
                (entry for entry in list(runtime_row.get("in_transit") or []) if isinstance(entry, dict)),
                key=lambda entry: (_as_int(entry.get("ready_tick", 0), 0), _as_int(entry.get("amount", 0), 0)),
            )
        ]

        releasable_amount = 0
        releasable_components: Dict[str, int] = {}
        future_in_transit: List[dict] = []
        for row in in_transit_rows:
            amount = max(0, _as_int(row.get("amount", 0), 0))
            ready_tick = max(0, _as_int(row.get("ready_tick", 0), 0))
            components = _normalize_component_map(row.get("components"))
            if amount <= 0:
                continue
            if ready_tick <= int(tick):
                releasable_amount += int(amount)
                for quantity_id in sorted(components.keys()):
                    releasable_components[quantity_id] = int(
                        max(0, int(releasable_components.get(quantity_id, 0)) + int(components.get(quantity_id, 0)))
                    )
            else:
                future_in_transit.append(
                    {
                        "ready_tick": int(ready_tick),
                        "amount": int(amount),
                        "components": dict(components),
                    }
                )

        channel_extensions = dict(channel_row.get("extensions") or {})
        quantity_bundle_id = str(channel_row.get("quantity_bundle_id", "") or "").strip()
        is_bundle_channel = bool(quantity_bundle_id)
        component_ids: List[str] = []
        if is_bundle_channel:
            bundle_row = dict(bundle_rows_by_id.get(quantity_bundle_id) or {})
            component_ids = _ordered_unique_strings(list(bundle_row.get("quantity_ids") or []))
            if not component_ids:
                component_ids = _ordered_unique_strings(list(channel_extensions.get("bundle_quantity_ids") or []))
            if not component_ids and str(channel_row.get("quantity_id", "") or "").strip():
                component_ids = [str(channel_row.get("quantity_id", "")).strip()]
            if not component_ids:
                raise FlowEngineError(
                    REFUSAL_CORE_FLOW_INVALID,
                    "bundle flow channel requires component quantity ids",
                    {"channel_id": channel_id, "quantity_bundle_id": quantity_bundle_id},
                )
        component_capacity_policy_row = dict(
            capacity_policy_rows.get(str(channel_row.get("component_capacity_policy_id", "") or "").strip()) or {}
        )
        component_loss_policy_row = dict(
            loss_policy_rows.get(str(channel_row.get("component_loss_policy_id", "") or "").strip()) or {}
        )

        requested_outbound = int(source_available + queued_amount)
        channel_capacity = channel_row.get("capacity_per_tick")
        if channel_capacity is None:
            capacity_processed = requested_outbound
        else:
            capacity_processed = min(requested_outbound, max(0, _as_int(channel_capacity, 0)))
        overflow_from_capacity = int(max(0, requested_outbound - capacity_processed))
        if overflow_from_capacity > 0 and (not allow_partial) and overflow_policy == "refuse":
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_CAPACITY_INSUFFICIENT,
                "flow channel exceeds capacity and policy refuses partial transfer",
                {
                    "channel_id": channel_id,
                    "requested": int(requested_outbound),
                    "capacity_per_tick": int(_as_int(channel_capacity, 0)),
                },
            )

        consumed_from_queue = min(int(queued_amount), int(capacity_processed))
        consumed_from_source = int(max(0, int(capacity_processed) - int(consumed_from_queue)))
        queued_after = int(max(0, int(queued_amount) - int(consumed_from_queue)))
        source_overflow = int(max(0, int(source_available) - int(consumed_from_source)))

        spill_loss = 0
        if overflow_from_capacity > 0:
            if overflow_policy == "refuse":
                raise FlowEngineError(
                    REFUSAL_CORE_FLOW_OVERFLOW_REFUSED,
                    "flow channel overflow policy refused capacity overflow",
                    {"channel_id": channel_id, "overflow_amount": int(overflow_from_capacity)},
                )
            if overflow_policy == "queue":
                # Source-side overflow remains at source for next tick. We only
                # track explicit queued/in-transit mass that has already left
                # source custody.
                pass
            elif overflow_policy == "spill":
                # Spilled overflow reflects source mass not launched this tick.
                spill_loss += int(source_overflow)

        launched_amount = int(capacity_processed)
        source_debit = int(consumed_from_source)
        if overflow_from_capacity > 0 and overflow_policy == "spill":
            source_debit += int(source_overflow)
        if source_debit > 0:
            balances[source_node_id] = int(max(0, int(source_available) - int(source_debit)))
        component_weights = _normalize_component_map(channel_extensions.get("component_weights"))

        delay_ticks = int(max(0, _as_int(channel_row.get("delay_ticks", 0), 0)))
        immediate_arrival = 0
        if launched_amount > 0:
            if delay_ticks > 0:
                future_in_transit.append({"ready_tick": int(tick + delay_ticks), "amount": int(launched_amount)})
            else:
                immediate_arrival = int(launched_amount)

        arriving_amount = int(max(0, int(releasable_amount) + int(immediate_arrival)))
        sink_capacity = sink_caps.get(sink_node_id)
        overflow_at_sink = 0
        if sink_capacity is not None:
            sink_room = max(0, int(_as_int(sink_capacity, 0)) - int(sink_current))
            if arriving_amount > sink_room:
                overflow_at_sink = int(arriving_amount - sink_room)
                arriving_amount = int(sink_room)
        if overflow_at_sink > 0:
            if overflow_policy == "refuse":
                raise FlowEngineError(
                    REFUSAL_CORE_FLOW_OVERFLOW_REFUSED,
                    "flow channel overflow policy refused sink overflow",
                    {"channel_id": channel_id, "overflow_amount": int(overflow_at_sink)},
                )
            if overflow_policy == "queue":
                future_in_transit.append({"ready_tick": int(tick + 1), "amount": int(overflow_at_sink)})
            elif overflow_policy == "spill":
                spill_loss += int(overflow_at_sink)

        transfer_result = flow_transfer(
            quantity=int(arriving_amount),
            loss_fraction=int(channel_row.get("loss_fraction", 0)),
            scale=int(scale),
            capacity_per_tick=None,
            delay_ticks=0,
        )
        net_transfer = int(max(0, _as_int(transfer_result.get("delivered_mass", 0), 0)))
        loss_fraction_loss = int(max(0, _as_int(transfer_result.get("loss_mass", 0), 0)))
        total_lost = int(max(0, int(loss_fraction_loss) + int(spill_loss)))
        transferred_components: Dict[str, int] = {}
        lost_components: Dict[str, int] = {}
        loss_transforms: Dict[str, int] = {}
        conservation_exceptions: List[dict] = []
        if is_bundle_channel:
            effective_weights = dict(component_weights)
            if not effective_weights:
                effective_weights = _add_component_maps(queued_components, releasable_components)
            bundle_outcome = _bundle_component_outcome(
                transferred_amount=int(net_transfer),
                lost_amount=int(total_lost),
                component_ids=list(component_ids),
                capacity_policy_row=component_capacity_policy_row,
                loss_policy_row=component_loss_policy_row,
                scale=int(scale),
                channel_loss_fraction=int(channel_row.get("loss_fraction", 0)),
                channel_extensions={**channel_extensions, "component_weights": effective_weights},
            )
            transferred_components = dict(bundle_outcome.get("transferred_components") or {})
            lost_components = dict(bundle_outcome.get("lost_components") or {})
            loss_transforms = dict(bundle_outcome.get("loss_transforms") or {})
            conservation_exceptions = [
                dict(row)
                for row in list(bundle_outcome.get("conservation_exceptions") or [])
                if isinstance(row, dict)
            ]
            net_transfer = int(max(0, _sum_component_map(transferred_components)))
            total_lost = int(max(0, _sum_component_map(lost_components)))
        if net_transfer > 0:
            balances[sink_node_id] = int(max(0, int(sink_current) + int(net_transfer)))

        queued_components_out = {}
        if is_bundle_channel:
            queued_components_out = _allocate_total_by_component_weights(
                total=int(max(0, queued_after)),
                component_ids=list(component_ids),
                weights=queued_components if queued_components else component_weights,
            )
        runtime_by_channel[channel_id] = {
            "queued_amount": int(max(0, int(queued_after))),
            "queued_components": dict(queued_components_out),
            "in_transit": sorted(
                (
                    {
                        "ready_tick": int(max(0, _as_int(item.get("ready_tick", 0), 0))),
                        "amount": int(max(0, _as_int(item.get("amount", 0), 0))),
                        "components": _normalize_component_map(item.get("components")),
                    }
                    for item in future_in_transit
                    if max(0, _as_int(item.get("amount", 0), 0)) > 0
                ),
                key=lambda item: (int(item.get("ready_tick", 0)), int(item.get("amount", 0))),
            ),
        }

        ledger_refs = _ledger_delta_refs(
            channel_id=channel_id,
            tick=int(tick),
            source_debit=int(source_debit),
            sink_credit=int(net_transfer),
            lost_amount=int(total_lost),
        )
        event_row = normalize_flow_transfer_event(
            {
                "schema_version": "1.1.0" if is_bundle_channel else "1.0.0",
                "event_id": "flow.event.{}".format(
                    canonical_sha256({"channel_id": channel_id, "tick": int(tick), "sequence": int(processed_count)})[:24]
                ),
                "tick": int(tick),
                "channel_id": channel_id,
                "transferred_amount": int(net_transfer),
                "lost_amount": int(total_lost),
                "transferred_components": dict(transferred_components),
                "lost_components": dict(lost_components),
                "ledger_delta_refs": list(ledger_refs),
                "deterministic_fingerprint": "",
                "extensions": {
                    "quantity_id": str(channel_row.get("quantity_id", "")),
                    "quantity_bundle_id": quantity_bundle_id or None,
                    "source_node_id": source_node_id,
                    "sink_node_id": sink_node_id,
                    "launched_amount": int(launched_amount),
                    "releasable_amount": int(releasable_amount),
                    "spill_loss": int(spill_loss),
                    "policy_id": str(policy_row.get("solver_policy_id", "")),
                    "loss_transforms": dict(loss_transforms),
                    "conservation_exceptions": list(conservation_exceptions),
                },
            }
        )
        transfer_events.append(event_row)

        if int(total_lost) > 0:
            if is_bundle_channel and lost_components:
                component_rules = dict(component_loss_policy_row.get("per_quantity_rules") or {})
                for quantity_id in sorted(lost_components.keys()):
                    component_lost = int(max(0, _as_int(lost_components.get(quantity_id, 0), 0)))
                    if component_lost <= 0:
                        continue
                    rule = dict(component_rules.get(quantity_id) or {})
                    loss_row = {
                        "channel_id": channel_id,
                        "quantity_id": quantity_id,
                        "source_node_id": source_node_id,
                        "sink_node_id": sink_node_id,
                        "lost_amount": int(component_lost),
                        "conserved": bool(quantity_id in conserved_ids),
                        "transform_to_quantity_id": (
                            None
                            if rule.get("transform_to_quantity_id") is None
                            else str(rule.get("transform_to_quantity_id", "")).strip() or None
                        ),
                        "preserve_conservation": bool(rule.get("preserve_conservation", False)),
                    }
                    transform_to_quantity_id = loss_row.get("transform_to_quantity_id")
                    if bool(loss_row.get("preserve_conservation", False)) and bool(loss_row.get("conserved", False)) and not transform_to_quantity_id:
                        loss_row["conservation_exception_logged"] = True
                        loss_row["exception_code"] = "exception.flow.missing_transform_target"
                    loss_entries.append(loss_row)
                    if transform_to_quantity_id and component_lost > 0:
                        loss_entries.append(
                            {
                                "channel_id": channel_id,
                                "quantity_id": str(transform_to_quantity_id),
                                "source_node_id": source_node_id,
                                "sink_node_id": sink_node_id,
                                "lost_amount": int(component_lost),
                                "conserved": bool(str(transform_to_quantity_id) in conserved_ids),
                                "transformed_from_quantity_id": quantity_id,
                                "transform_applied": True,
                            }
                        )
            else:
                loss_row = {
                    "channel_id": channel_id,
                    "quantity_id": str(channel_row.get("quantity_id", "")).strip() or quantity_bundle_id,
                    "source_node_id": source_node_id,
                    "sink_node_id": sink_node_id,
                    "lost_amount": int(total_lost),
                    "conserved": bool(str(channel_row.get("quantity_id", "")).strip() in conserved_ids),
                }
                loss_entries.append(loss_row)

        deferred_amount = int(
            max(0, int(runtime_by_channel[channel_id]["queued_amount"]))
            + sum(int(_as_int(item.get("amount", 0), 0)) for item in list(runtime_by_channel[channel_id]["in_transit"]))
        )
        channel_results.append(
            {
                "channel_id": channel_id,
                "quantity_id": str(channel_row.get("quantity_id", "")).strip() or quantity_bundle_id,
                "quantity_bundle_id": quantity_bundle_id or None,
                "source_node_id": source_node_id,
                "sink_node_id": sink_node_id,
                "launched_amount": int(launched_amount),
                "transferred_amount": int(net_transfer),
                "lost_amount": int(total_lost),
                "transferred_components": dict(transferred_components),
                "lost_components": dict(lost_components),
                "deferred_amount": int(max(0, deferred_amount)),
            }
        )

        plan_row = _cross_shard_flow_plan(
            channel_row=channel_row,
            graph_row=graph_row,
            partition_row=partition_row,
        )
        cross_shard_transfer_plans.append(
            {
                "channel_id": channel_id,
                "tick": int(tick),
                "plan": dict(plan_row),
            }
        )
        processed_count += 1

    if strict_budget and remaining_count > 0:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_CAPACITY_INSUFFICIENT,
            "flow tick exceeded deterministic channel budget",
            {"processed_count": int(processed_count), "remaining_count": int(remaining_count)},
        )

    loss_transform_rows = _loss_transform_rows_from_entries(loss_entries)
    conservation_exceptions = _loss_conservation_exceptions(loss_entries)

    return {
        "node_balances": dict((str(key), int(balances[key])) for key in sorted(balances.keys())),
        "channel_runtime": dict(
            (str(key), dict(runtime_by_channel[key]))
            for key in sorted(runtime_by_channel.keys())
            if str(key).strip()
        ),
        "transfer_events": sorted(
            (dict(row) for row in transfer_events if isinstance(row, dict)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "loss_entries": sorted(
            (dict(row) for row in loss_entries if isinstance(row, dict)),
            key=lambda row: (str(row.get("channel_id", "")), str(row.get("quantity_id", ""))),
        ),
        "loss_transform_rows": list(loss_transform_rows),
        "conservation_exceptions": list(conservation_exceptions),
        "channel_results": sorted(
            (dict(row) for row in channel_results if isinstance(row, dict)),
            key=lambda row: str(row.get("channel_id", "")),
        ),
        "cross_shard_transfer_plans": sorted(
            (dict(row) for row in cross_shard_transfer_plans if isinstance(row, dict)),
            key=lambda row: str(row.get("channel_id", "")),
        ),
        "processed_count": int(processed_count),
        "remaining_count": int(remaining_count),
        "cost_units": int(max(0, _as_int(cost_units_per_channel, 1)) * int(processed_count)),
        "budget_outcome": "degraded" if int(remaining_count) > 0 else "complete",
    }
