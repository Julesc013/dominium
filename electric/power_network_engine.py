"""Deterministic ELEC-1 power-network helpers (E0/E1 baseline)."""

from __future__ import annotations

import math
from typing import Dict, List, Mapping, Tuple

from core.flow import normalize_flow_channel
from core.graph.network_graph_engine import normalize_network_graph
from electric.storage import (
    SOC_SCALE,
    apply_storage_charge,
    apply_storage_discharge,
    normalize_storage_state_rows,
)
from models.model_engine import (
    cache_policy_rows_by_id,
    evaluate_model_bindings,
    model_type_rows_by_id,
    normalize_constitutive_model_rows,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_ELEC_NETWORK_INVALID = "refusal.elec.network_invalid"
REFUSAL_ELEC_SPEC_NONCOMPLIANT = "refusal.elec.spec_noncompliant"

_VALID_NODE_KINDS = {"bus", "generator", "load", "storage", "breaker"}
_VALID_EDGE_KINDS = {"conductor", "switch", "transformer_stub"}

_Q_ACTIVE = "quantity.power.active_stub"
_Q_REACTIVE = "quantity.power.reactive_stub"
_Q_APPARENT = "quantity.power.apparent_stub"
_Q_HEAT_LOSS = "quantity.thermal.heat_loss_stub"

_ELEC_MODEL_IDS = {
    "model.elec_load_resistive_stub",
    "model.elec_load_motor_stub",
    "model.elec_pf_correction",
    "model.elec_transformer_stub",
    "model.elec_storage_battery",
    "model.elec_device_loss",
}


class ElectricError(ValueError):
    """Deterministic electrical-domain refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_ELEC_NETWORK_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _default_model_type_registry_payload() -> dict:
    return {
        "record": {
            "model_types": [
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.elec_load_phasor_stub",
                    "description": "ELEC load phasor stub",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.elec_pf_correction",
                    "description": "ELEC PF correction",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.elec_transformer_stub",
                    "description": "ELEC transformer stub",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.elec_storage_battery",
                    "description": "ELEC storage battery",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.elec_device_loss",
                    "description": "ELEC device loss",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
            ]
        }
    }


def _default_model_cache_policy_registry_payload() -> dict:
    return {
        "record": {
            "cache_policies": [
                {
                    "schema_version": "1.0.0",
                    "cache_policy_id": "cache.none",
                    "mode": "none",
                    "ttl_ticks": None,
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "cache_policy_id": "cache.by_inputs_hash",
                    "mode": "by_inputs_hash",
                    "ttl_ticks": 8,
                    "extensions": {},
                },
            ]
        }
    }


def _default_constitutive_model_rows() -> List[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "model_id": "model.elec_load_resistive_stub",
            "model_type_id": "model_type.elec_load_phasor_stub",
            "description": "resistive load",
            "supported_tiers": ["meso"],
            "input_signature": [],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_ACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_ACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_REACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_REACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_APPARENT, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_APPARENT}},
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.elec_load_motor_stub",
            "model_type_id": "model_type.elec_load_phasor_stub",
            "description": "motor load",
            "supported_tiers": ["meso"],
            "input_signature": [],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_ACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_ACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_REACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_REACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_APPARENT, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_APPARENT}},
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.elec.power_factor", "extensions": {}},
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.elec_pf_correction",
            "model_type_id": "model_type.elec_pf_correction",
            "description": "pf correction",
            "supported_tiers": ["meso"],
            "input_signature": [
                {"schema_version": "1.0.0", "input_kind": "flow_quantity", "input_id": _Q_ACTIVE, "selector": "target.node", "extensions": {}},
                {"schema_version": "1.0.0", "input_kind": "flow_quantity", "input_id": _Q_REACTIVE, "selector": "target.node", "extensions": {}},
            ],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_REACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_REACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.elec.pf_adjusted_q", "extensions": {}},
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.elec_transformer_stub",
            "model_type_id": "model_type.elec_transformer_stub",
            "description": "transformer",
            "supported_tiers": ["meso"],
            "input_signature": [
                {"schema_version": "1.0.0", "input_kind": "flow_quantity", "input_id": _Q_ACTIVE, "selector": "target.edge", "extensions": {}},
                {"schema_version": "1.0.0", "input_kind": "flow_quantity", "input_id": _Q_REACTIVE, "selector": "target.edge", "extensions": {}},
            ],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_ACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_ACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_REACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_REACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_APPARENT, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_APPARENT}},
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": _Q_HEAT_LOSS, "extensions": {}},
            ],
            "cost_units": 2,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.elec_storage_battery",
            "model_type_id": "model_type.elec_storage_battery",
            "description": "storage battery",
            "supported_tiers": ["meso"],
            "input_signature": [],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_ACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_ACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_REACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_REACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_APPARENT, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_APPARENT}},
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": _Q_HEAT_LOSS, "extensions": {}},
                {"schema_version": "1.0.0", "output_kind": "hazard_increment", "output_id": "hazard.elec.storage_degradation", "extensions": {}},
            ],
            "cost_units": 2,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.elec_device_loss",
            "model_type_id": "model_type.elec_device_loss",
            "description": "device loss",
            "supported_tiers": ["meso"],
            "input_signature": [
                {"schema_version": "1.0.0", "input_kind": "flow_quantity", "input_id": _Q_ACTIVE, "selector": "target.edge", "extensions": {}},
            ],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_ACTIVE, "extensions": {"quantity_bundle_id": "bundle.power_phasor", "component_quantity_id": _Q_ACTIVE}},
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": _Q_HEAT_LOSS, "extensions": {}},
                {"schema_version": "1.0.0", "output_kind": "effect", "output_id": "effect.temperature_increase_local", "extensions": {}},
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
    ]


def _merge_model_rows(registry_rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_constitutive_model_rows(_default_constitutive_model_rows()):
        out[str(row.get("model_id", "")).strip()] = dict(row)
    for row in normalize_constitutive_model_rows(registry_rows):
        model_id = str(row.get("model_id", "")).strip()
        if model_id:
            out[model_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _merge_model_type_rows(registry_rows: Mapping[str, dict] | None) -> Dict[str, dict]:
    defaults = model_type_rows_by_id(_default_model_type_registry_payload())
    out = dict((str(key).strip(), dict(value)) for key, value in defaults.items() if str(key).strip())
    for key, value in dict(registry_rows or {}).items():
        token = str(key).strip()
        if token:
            out[token] = dict(value or {})
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _merge_cache_policy_rows(registry_rows: Mapping[str, dict] | None) -> Dict[str, dict]:
    defaults = cache_policy_rows_by_id(_default_model_cache_policy_registry_payload())
    out = dict((str(key).strip(), dict(value)) for key, value in defaults.items() if str(key).strip())
    for key, value in dict(registry_rows or {}).items():
        token = str(key).strip()
        if token:
            out[token] = dict(value or {})
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def compute_pf_permille(*, active_p: int, apparent_s: int) -> int:
    p = int(max(0, _as_int(active_p, 0)))
    s = int(max(0, _as_int(apparent_s, 0)))
    if s <= 0:
        return 1000
    return int(max(0, min(1000, (p * 1000) // s)))


def _apparent_from_components(*, active_p: int, reactive_q: int) -> int:
    p = int(max(0, _as_int(active_p, 0)))
    q = int(max(0, _as_int(reactive_q, 0)))
    return int(math.isqrt((p * p) + (q * q)))


def normalize_elec_node_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    node_kind = str(payload.get("node_kind", "")).strip()
    if node_kind not in _VALID_NODE_KINDS:
        raise ElectricError(
            REFUSAL_ELEC_NETWORK_INVALID,
            "elec node payload requires valid node_kind",
            {"node_kind": node_kind},
        )
    result = {
        "schema_version": "1.0.0",
        "node_kind": node_kind,
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "model_bindings": _sorted_tokens(payload.get("model_bindings")),
        "safety_instances": _sorted_tokens(payload.get("safety_instances")),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def normalize_elec_edge_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    edge_kind = str(payload.get("edge_kind", "")).strip()
    if edge_kind not in _VALID_EDGE_KINDS:
        raise ElectricError(
            REFUSAL_ELEC_NETWORK_INVALID,
            "elec edge payload requires valid edge_kind",
            {"edge_kind": edge_kind},
        )
    length = int(max(0, _as_int(payload.get("length", 0), 0)))
    resistance_proxy = int(max(0, _as_int(payload.get("resistance_proxy", 0), 0)))
    capacity_rating = int(max(0, _as_int(payload.get("capacity_rating", 0), 0)))
    result = {
        "schema_version": "1.0.0",
        "edge_kind": edge_kind,
        "length": int(length),
        "resistance_proxy": int(resistance_proxy),
        "capacity_rating": int(capacity_rating),
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def deterministic_power_channel_id(*, graph_id: str, edge_id: str) -> str:
    digest = canonical_sha256(
        {
            "graph_id": str(graph_id or "").strip(),
            "edge_id": str(edge_id or "").strip(),
            "kind": "power_flow_channel",
        }
    )
    return "channel.elec.{}".format(digest[:16])


def build_power_flow_channel(
    *,
    graph_id: str,
    edge_id: str,
    source_node_id: str,
    sink_node_id: str,
    capacity_rating: int,
    solver_policy_id: str = "flow.solver.default",
    component_capacity_policy_id: str = "comp_capacity.default_bundle",
    component_loss_policy_id: str = "comp_loss.default_bundle",
) -> dict:
    channel_id = deterministic_power_channel_id(graph_id=graph_id, edge_id=edge_id)
    return normalize_flow_channel(
        {
            "schema_version": "1.1.0",
            "channel_id": channel_id,
            "graph_id": str(graph_id or "").strip(),
            "quantity_bundle_id": "bundle.power_phasor",
            "component_capacity_policy_id": str(component_capacity_policy_id or "").strip() or None,
            "component_loss_policy_id": str(component_loss_policy_id or "").strip() or None,
            "source_node_id": str(source_node_id or "").strip(),
            "sink_node_id": str(sink_node_id or "").strip(),
            "capacity_per_tick": int(max(0, _as_int(capacity_rating, 0))),
            "delay_ticks": 0,
            "loss_fraction": 0,
            "solver_policy_id": str(solver_policy_id or "").strip() or "flow.solver.default",
            "priority": 0,
            "extensions": {
                "edge_id": str(edge_id or "").strip(),
                "component_weights": {
                    _Q_ACTIVE: 1000,
                    _Q_REACTIVE: 1000,
                    _Q_APPARENT: 1000,
                },
            },
        }
    )


def _binding_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in list(rows or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("binding_id", ""))):
        binding_id = str(row.get("binding_id", "")).strip()
        if binding_id:
            out[binding_id] = dict(row)
    return out


def _load_binding_rows_for_node(*, node_payload: Mapping[str, object], model_binding_rows_by_id: Mapping[str, dict]) -> List[dict]:
    binding_ids = _sorted_tokens(node_payload.get("model_bindings"))
    rows = []
    for binding_id in binding_ids:
        row = dict(model_binding_rows_by_id.get(binding_id) or {})
        if row:
            rows.append(row)
    return sorted(rows, key=lambda row: (str(row.get("model_id", "")), str(row.get("binding_id", ""))))


def _aggregate_load_for_node(*, node_payload: Mapping[str, object], model_binding_rows_by_id: Mapping[str, dict]) -> dict:
    p_total = 0
    q_total = 0
    for row in _load_binding_rows_for_node(
        node_payload=node_payload,
        model_binding_rows_by_id=model_binding_rows_by_id,
    ):
        model_id = str(row.get("model_id", "")).strip()
        params = _as_map(row.get("parameters"))
        demand_p = int(max(0, _as_int(params.get("demand_p", params.get("demand_kw", 0)), 0)))
        if model_id == "model.elec_load_resistive_stub":
            p_total += int(demand_p)
            q_total += int(max(0, _as_int(params.get("demand_q", 0), 0)))
        elif model_id == "model.elec_load_motor_stub":
            pf_permille = int(max(1, min(1000, _as_int(params.get("pf_permille", 850), 850))))
            s_required = int(max(demand_p, (demand_p * 1000 + pf_permille - 1) // pf_permille))
            q_required = int(math.isqrt(max(0, (s_required * s_required) - (demand_p * demand_p))))
            p_total += int(demand_p)
            q_total += int(max(0, q_required))
    s_total = int(_apparent_from_components(active_p=int(p_total), reactive_q=int(q_total)))
    return {
        "P": int(max(0, p_total)),
        "Q": int(max(0, q_total)),
        "S": int(max(0, s_total)),
    }


def _binding_rows_for_target(
    *,
    target_id: str,
    target_kind: str,
    model_binding_rows: object,
    explicit_binding_ids: object = None,
) -> List[dict]:
    rows_by_id = _binding_rows_by_id(model_binding_rows)
    out: Dict[str, dict] = {}
    for binding_id in _sorted_tokens(explicit_binding_ids):
        row = dict(rows_by_id.get(binding_id) or {})
        if row:
            out[binding_id] = row
    for row in list(rows_by_id.values()):
        binding_id = str(row.get("binding_id", "")).strip()
        if not binding_id:
            continue
        if str(row.get("target_id", "")).strip() != str(target_id).strip():
            continue
        if str(row.get("target_kind", "custom")).strip().lower() != str(target_kind).strip().lower():
            continue
        out[binding_id] = dict(row)
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda token: (str(out[token].get("model_id", "")), token))]


def _filter_elec_model_rows_for_bindings(*, bindings: List[dict], merged_model_rows_by_id: Mapping[str, dict]) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in list(bindings or []):
        model_id = str(row.get("model_id", "")).strip()
        if not model_id:
            continue
        selected = dict(merged_model_rows_by_id.get(model_id) or {})
        if not selected:
            continue
        out[model_id] = selected
    return [dict(out[key]) for key in sorted(out.keys())]


def _model_context_value(
    *,
    context_by_target_id: Mapping[str, Mapping[str, int]],
    binding: Mapping[str, object],
    input_ref: Mapping[str, object],
) -> object:
    target_id = str(binding.get("target_id", "")).strip()
    input_id = str(input_ref.get("input_id", "")).strip()
    row = dict(context_by_target_id.get(target_id) or {})
    return row.get(input_id)


def _sum_model_flow_adjustments(
    *,
    model_output_actions: object,
    target_id: str,
) -> Dict[str, int]:
    p = 0
    q = 0
    s = 0
    heat = 0
    storage_discharge = 0
    for row in list(model_output_actions or []):
        if not isinstance(row, Mapping):
            continue
        if str(row.get("target_id", "")).strip() != str(target_id).strip():
            continue
        output_kind = str(row.get("output_kind", "")).strip()
        output_id = str(row.get("output_id", "")).strip()
        payload = _as_map(row.get("payload"))
        if output_kind == "flow_adjustment":
            delta = int(_as_int(payload.get("delta", 0), 0))
            component_quantity_id = str(payload.get("component_quantity_id", output_id)).strip() or output_id
            if component_quantity_id == _Q_ACTIVE:
                p += delta
                if str(row.get("model_id", "")).strip() == "model.elec_storage_battery" and delta < 0:
                    storage_discharge += int(-1 * delta)
            elif component_quantity_id == _Q_REACTIVE:
                q += delta
            elif component_quantity_id == _Q_APPARENT:
                s += delta
        elif output_kind == "derived_quantity" and output_id == _Q_HEAT_LOSS:
            heat += int(max(0, _as_int(payload.get("value", 0), 0)))
    return {
        "P": int(p),
        "Q": int(q),
        "S": int(s),
        "heat_loss": int(heat),
        "storage_discharge": int(storage_discharge),
    }


def _weighted_integer_split(*, total: int, keys: List[str], weights: Mapping[str, int]) -> Dict[str, int]:
    amount = int(max(0, _as_int(total, 0)))
    ordered_keys = [str(key).strip() for key in list(keys or []) if str(key).strip()]
    if not ordered_keys:
        return {}
    total_weight = 0
    for key in ordered_keys:
        total_weight += int(max(0, _as_int(weights.get(key, 1), 1)))
    if total_weight <= 0:
        total_weight = len(ordered_keys)
    base: Dict[str, int] = {}
    remainders: List[tuple] = []
    allocated = 0
    for key in ordered_keys:
        weight = int(max(0, _as_int(weights.get(key, 1), 1)))
        numer = int(amount * weight)
        part = int(numer // total_weight)
        rem = int(numer % total_weight)
        base[key] = int(part)
        allocated += int(part)
        remainders.append((rem, key))
    remaining = int(max(0, amount - allocated))
    for _rem, key in sorted(remainders, key=lambda row: (-1 * int(row[0]), str(row[1]))):
        if remaining <= 0:
            break
        base[key] = int(base.get(key, 0) + 1)
        remaining -= 1
    return dict((key, int(base.get(key, 0))) for key in ordered_keys)


def solve_power_network_e1(
    *,
    graph_row: Mapping[str, object],
    model_binding_rows: object,
    current_tick: int,
    max_processed_edges: int,
    constitutive_model_rows: object = None,
    model_type_rows: Mapping[str, dict] | None = None,
    model_cache_policy_rows: Mapping[str, dict] | None = None,
    model_cache_rows: object = None,
    storage_state_rows: object = None,
    max_model_cost_units: int = 4096,
) -> dict:
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    nodes = [dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)]
    edges = [dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)]
    if not graph_id:
        raise ElectricError(REFUSAL_ELEC_NETWORK_INVALID, "power graph missing graph_id", {})
    merged_model_rows_by_id = _merge_model_rows(constitutive_model_rows)
    merged_model_type_rows = _merge_model_type_rows(model_type_rows)
    merged_cache_policy_rows = _merge_cache_policy_rows(model_cache_policy_rows)
    storage_rows_runtime = normalize_storage_state_rows(storage_state_rows or [])
    model_cache_rows_runtime = [dict(row) for row in list(model_cache_rows or []) if isinstance(row, Mapping)]

    model_evaluation_results: List[dict] = []
    model_observation_rows: List[dict] = []
    model_output_actions: List[dict] = []
    model_cost_units = 0
    model_budget_outcome = "complete"

    def _run_model_eval(bindings: List[dict], context_by_target_id: Mapping[str, Mapping[str, int]]) -> List[dict]:
        nonlocal model_cache_rows_runtime
        nonlocal model_cost_units
        nonlocal model_budget_outcome
        if not bindings:
            return []
        eval_model_rows = _filter_elec_model_rows_for_bindings(
            bindings=bindings,
            merged_model_rows_by_id=merged_model_rows_by_id,
        )
        if not eval_model_rows:
            return []
        remaining_budget = int(max(0, int(max_model_cost_units) - int(model_cost_units)))
        if remaining_budget <= 0:
            model_budget_outcome = "degraded"
            return []
        evaluated = evaluate_model_bindings(
            current_tick=int(max(0, _as_int(current_tick, 0))),
            model_rows=eval_model_rows,
            binding_rows=bindings,
            cache_rows=model_cache_rows_runtime,
            model_type_rows=merged_model_type_rows,
            cache_policy_rows=merged_cache_policy_rows,
            input_resolver_fn=lambda binding, input_ref: _model_context_value(
                context_by_target_id=context_by_target_id,
                binding=binding,
                input_ref=input_ref,
            ),
            max_cost_units=int(remaining_budget),
        )
        model_cache_rows_runtime = [dict(row) for row in list(evaluated.get("cache_rows") or []) if isinstance(row, Mapping)]
        model_evaluation_results.extend(
            dict(row)
            for row in list(evaluated.get("evaluation_results") or [])
            if isinstance(row, Mapping)
        )
        model_observation_rows.extend(
            dict(row)
            for row in list(evaluated.get("observation_rows") or [])
            if isinstance(row, Mapping)
        )
        model_output_actions.extend(
            dict(row)
            for row in list(evaluated.get("output_actions") or [])
            if isinstance(row, Mapping)
        )
        model_cost_units += int(max(0, _as_int(evaluated.get("cost_units", 0), 0)))
        if str(evaluated.get("budget_outcome", "complete")).strip() == "degraded":
            model_budget_outcome = "degraded"
        return [
            dict(row)
            for row in list(evaluated.get("output_actions") or [])
            if isinstance(row, Mapping)
        ]

    node_loads: Dict[str, dict] = {}
    pending_pf_bindings: List[dict] = []
    pending_storage_bindings: List[Tuple[str, dict]] = []
    for node in sorted(nodes, key=lambda row: str(row.get("node_id", ""))):
        node_id = str(node.get("node_id", "")).strip()
        payload = normalize_elec_node_payload(_as_map(node.get("payload")))
        node_bindings = _binding_rows_for_target(
            target_id=node_id,
            target_kind="node",
            model_binding_rows=model_binding_rows,
            explicit_binding_ids=payload.get("model_bindings"),
        )
        node_kind = str(payload.get("node_kind", "")).strip()
        if node_kind == "load":
            load_bindings = [
                dict(row)
                for row in list(node_bindings or [])
                if str(row.get("model_id", "")).strip() in {"model.elec_load_resistive_stub", "model.elec_load_motor_stub"}
            ]
            load_actions = _run_model_eval(load_bindings, {})
            totals = _sum_model_flow_adjustments(model_output_actions=load_actions, target_id=node_id)
            p = int(max(0, _as_int(totals.get("P", 0), 0)))
            q = int(max(0, _as_int(totals.get("Q", 0), 0)))
            s = int(max(_apparent_from_components(active_p=p, reactive_q=q), _as_int(totals.get("S", 0), 0)))
            node_loads[node_id] = {"P": int(p), "Q": int(q), "S": int(s)}
            pending_pf_bindings.extend(
                dict(row)
                for row in list(node_bindings or [])
                if str(row.get("model_id", "")).strip() == "model.elec_pf_correction"
            )
        elif node_kind == "storage":
            pending_storage_bindings.extend(
                (node_id, dict(row))
                for row in list(node_bindings or [])
                if str(row.get("model_id", "")).strip() == "model.elec_storage_battery"
            )

    for binding_row in sorted(
        (dict(row) for row in list(pending_pf_bindings or [])),
        key=lambda row: str(row.get("binding_id", "")),
    ):
        target_id = str(binding_row.get("target_id", "")).strip()
        current_row = dict(node_loads.get(target_id) or {"P": 0, "Q": 0, "S": 0})
        params = _as_map(binding_row.get("parameters"))
        params["current_p"] = int(max(0, _as_int(current_row.get("P", 0), 0)))
        params["current_q"] = int(max(0, _as_int(current_row.get("Q", 0), 0)))
        runtime_binding = dict(binding_row)
        runtime_binding["parameters"] = params
        pf_actions = _run_model_eval(
            [runtime_binding],
            {
                target_id: {
                    _Q_ACTIVE: int(max(0, _as_int(current_row.get("P", 0), 0))),
                    _Q_REACTIVE: int(max(0, _as_int(current_row.get("Q", 0), 0))),
                }
            },
        )
        deltas = _sum_model_flow_adjustments(model_output_actions=pf_actions, target_id=target_id)
        current_row["Q"] = int(
            max(
                0,
                int(max(0, _as_int(current_row.get("Q", 0), 0)))
                + int(_as_int(deltas.get("Q", 0), 0)),
            )
        )
        current_row["S"] = int(max(_apparent_from_components(active_p=int(current_row.get("P", 0)), reactive_q=int(current_row.get("Q", 0))), int(_as_int(current_row.get("S", 0), 0)) + int(_as_int(deltas.get("S", 0), 0))))
        node_loads[target_id] = current_row

    total_p = sum(int(max(0, _as_int(row.get("P", 0), 0))) for row in node_loads.values())
    total_q = sum(int(max(0, _as_int(row.get("Q", 0), 0))) for row in node_loads.values())
    total_s = max(
        _apparent_from_components(active_p=total_p, reactive_q=total_q),
        sum(int(max(0, _as_int(row.get("S", 0), 0))) for row in node_loads.values()),
    )

    storage_rows_by_node = dict(
        (
            str(row.get("node_id", "")).strip(),
            dict(row),
        )
        for row in list(storage_rows_runtime or [])
        if isinstance(row, Mapping) and str(row.get("node_id", "")).strip()
    )
    for node_id, binding_row in sorted(
        ((str(node_id), dict(binding_row)) for node_id, binding_row in list(pending_storage_bindings or [])),
        key=lambda row: str(row[1].get("binding_id", "")),
    ):
        storage_row = dict(storage_rows_by_node.get(node_id) or {})
        params = _as_map(binding_row.get("parameters"))
        params["state_of_charge"] = int(max(0, _as_int(storage_row.get("state_of_charge", 0), 0)))
        params["capacity_energy"] = int(max(0, _as_int(storage_row.get("capacity_energy", params.get("capacity_energy", 0)), 0)))
        params["current_p"] = int(max(0, total_p))
        runtime_binding = dict(binding_row)
        runtime_binding["parameters"] = params
        storage_actions = _run_model_eval(
            [runtime_binding],
            {node_id: {"derived.elec.storage_state_of_charge": int(max(0, _as_int(params.get("state_of_charge", 0), 0)))}},
        )
        deltas = _sum_model_flow_adjustments(model_output_actions=storage_actions, target_id=node_id)
        total_p = int(max(0, total_p + int(_as_int(deltas.get("P", 0), 0))))
        total_q = int(max(0, total_q + int(_as_int(deltas.get("Q", 0), 0))))
        total_s = int(max(_apparent_from_components(active_p=total_p, reactive_q=total_q), total_s + int(_as_int(deltas.get("S", 0), 0))))
        discharge_amount = int(max(0, _as_int(deltas.get("storage_discharge", 0), 0)))
        if discharge_amount > 0:
            storage_update = apply_storage_discharge(
                storage_rows=[dict(value) for value in storage_rows_by_node.values()],
                node_id=node_id,
                energy_delta=int(discharge_amount),
                current_tick=int(max(0, _as_int(current_tick, 0))),
            )
            storage_rows_by_node = dict(
                (
                    str(row.get("node_id", "")).strip(),
                    dict(row),
                )
                for row in list(storage_update.get("storage_rows") or [])
                if isinstance(row, Mapping) and str(row.get("node_id", "")).strip()
            )
        elif int(_as_int(deltas.get("P", 0), 0)) > 0:
            storage_update = apply_storage_charge(
                storage_rows=[dict(value) for value in storage_rows_by_node.values()],
                node_id=node_id,
                energy_delta=int(_as_int(deltas.get("P", 0), 0)),
                current_tick=int(max(0, _as_int(current_tick, 0))),
            )
            storage_rows_by_node = dict(
                (
                    str(row.get("node_id", "")).strip(),
                    dict(row),
                )
                for row in list(storage_update.get("storage_rows") or [])
                if isinstance(row, Mapping) and str(row.get("node_id", "")).strip()
            )
    storage_rows_runtime = [dict(storage_rows_by_node[key]) for key in sorted(storage_rows_by_node.keys())]

    edge_rows = sorted(edges, key=lambda row: str(row.get("edge_id", "")))
    if int(max_processed_edges) <= 0 or len(edge_rows) > int(max_processed_edges):
        degraded = solve_power_network_e0(
            graph_row=graph,
            model_binding_rows=model_binding_rows,
            current_tick=current_tick,
            reason="degrade.elec.e1_budget",
        )
        degraded["model_evaluation_results"] = [dict(row) for row in model_evaluation_results]
        degraded["model_output_actions"] = [dict(row) for row in model_output_actions]
        degraded["model_observation_rows"] = [dict(row) for row in model_observation_rows]
        degraded["model_cache_rows"] = [dict(row) for row in model_cache_rows_runtime]
        degraded["model_cost_units"] = int(max(0, model_cost_units))
        degraded["model_budget_outcome"] = "degraded"
        degraded["storage_state_rows"] = [dict(row) for row in storage_rows_runtime]
        return degraded

    weights = {}
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        payload = normalize_elec_edge_payload(_as_map(edge.get("payload")))
        weights[edge_id] = int(max(1, _as_int(payload.get("capacity_rating", 0), 0)))
    edge_ids = [str(edge.get("edge_id", "")).strip() for edge in edge_rows]
    p_by_edge = _weighted_integer_split(total=total_p, keys=edge_ids, weights=weights)
    q_by_edge = _weighted_integer_split(total=total_q, keys=edge_ids, weights=weights)
    s_by_edge = _weighted_integer_split(total=total_s, keys=edge_ids, weights=weights)

    edge_status_rows: List[dict] = []
    flow_channels: List[dict] = []
    overloaded_channel_ids: List[str] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        payload = normalize_elec_edge_payload(_as_map(edge.get("payload")))
        capacity = int(max(0, _as_int(payload.get("capacity_rating", 0), 0)))
        resistance = int(max(0, _as_int(payload.get("resistance_proxy", 0), 0)))
        p_req = int(max(0, _as_int(p_by_edge.get(edge_id, 0), 0)))
        q_req = int(max(0, _as_int(q_by_edge.get(edge_id, 0), 0)))
        s_req = int(max(0, _as_int(s_by_edge.get(edge_id, 0), 0)))
        overloaded = bool((capacity <= 0 and s_req > 0) or (capacity > 0 and s_req > capacity))
        if capacity > 0 and s_req > capacity:
            scale = capacity
            p_req = int((p_req * scale) // max(1, s_req))
            q_req = int((q_req * scale) // max(1, s_req))
            s_req = int(scale)

        edge_bindings = _binding_rows_for_target(
            target_id=edge_id,
            target_kind="edge",
            model_binding_rows=model_binding_rows,
        )
        runtime_edge_bindings: List[dict] = []
        synthetic_loss_coeff = int((int(max(0, resistance)) * 1000) // max(1, int(capacity) if capacity > 0 else 1))
        runtime_edge_bindings.append(
            {
                "schema_version": "1.0.0",
                "binding_id": "binding.elec.synthetic_loss.{}".format(edge_id),
                "model_id": "model.elec_device_loss",
                "target_kind": "edge",
                "target_id": edge_id,
                "tier": "meso",
                "parameters": {
                    "current_p": int(p_req),
                    "current_q": int(q_req),
                    "current_s": int(s_req),
                    "loss_coeff_permille": int(max(0, synthetic_loss_coeff)),
                },
                "enabled": True,
                "deterministic_fingerprint": "",
                "extensions": {"synthetic": True},
            }
        )
        for binding_row in list(edge_bindings or []):
            model_id = str(binding_row.get("model_id", "")).strip()
            if model_id not in _ELEC_MODEL_IDS:
                continue
            params = _as_map(binding_row.get("parameters"))
            params["current_p"] = int(p_req)
            params["current_q"] = int(q_req)
            params["current_s"] = int(s_req)
            runtime_binding = dict(binding_row)
            runtime_binding["parameters"] = params
            runtime_edge_bindings.append(runtime_binding)

        edge_actions = _run_model_eval(
            runtime_edge_bindings,
            {
                edge_id: {
                    _Q_ACTIVE: int(p_req),
                    _Q_REACTIVE: int(q_req),
                    _Q_APPARENT: int(s_req),
                }
            },
        )
        deltas = _sum_model_flow_adjustments(model_output_actions=edge_actions, target_id=edge_id)
        p_del = int(max(0, p_req + int(_as_int(deltas.get("P", 0), 0))))
        q_del = int(max(0, q_req + int(_as_int(deltas.get("Q", 0), 0))))
        requested_s = int(max(0, s_req + int(_as_int(deltas.get("S", 0), 0))))
        s_del = int(max(_apparent_from_components(active_p=p_del, reactive_q=q_del), requested_s))
        if capacity > 0 and s_del > capacity:
            scale = int(capacity)
            p_del = int((p_del * scale) // max(1, s_del))
            q_del = int((q_del * scale) // max(1, s_del))
            s_del = int(scale)
            overloaded = True

        channel = build_power_flow_channel(
            graph_id=graph_id,
            edge_id=edge_id,
            source_node_id=from_node_id,
            sink_node_id=to_node_id,
            capacity_rating=capacity,
        )
        flow_channels.append(channel)
        channel_id = str(channel.get("channel_id", "")).strip()
        if overloaded and channel_id:
            overloaded_channel_ids.append(channel_id)
        pf_permille = compute_pf_permille(active_p=p_del, apparent_s=s_del)
        heat_loss = int(max(0, _as_int(deltas.get("heat_loss", 0), 0)))
        edge_status_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": channel_id,
                "tier": "E1",
                "P": int(p_del),
                "Q": int(q_del),
                "S": int(s_del),
                "pf_permille": int(pf_permille),
                "heat_loss_stub": int(heat_loss),
                "capacity_rating": int(capacity),
                "overloaded": bool(overloaded),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "edge_id": edge_id,
                        "P": int(p_del),
                        "Q": int(q_del),
                        "S": int(s_del),
                        "heat_loss_stub": int(heat_loss),
                        "overloaded": bool(overloaded),
                    }
                ),
            }
        )

    power_flow_hash = canonical_sha256(
        [
            {"edge_id": str(row.get("edge_id", "")), "P": int(_as_int(row.get("P", 0), 0)), "Q": int(_as_int(row.get("Q", 0), 0)), "S": int(_as_int(row.get("S", 0), 0))}
            for row in sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", "")))
        ]
    )
    combined_budget_outcome = "degraded" if model_budget_outcome == "degraded" else "complete"
    return {
        "mode": "E1",
        "graph_id": graph_id,
        "flow_channels": flow_channels,
        "edge_status_rows": sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", ""))),
        "node_status_rows": sorted(
            (
                {
                    "node_id": node_id,
                    "node_kind": "load",
                    "P_demand": int(max(0, _as_int(load.get("P", 0), 0))),
                    "Q_demand": int(max(0, _as_int(load.get("Q", 0), 0))),
                    "S_demand": int(max(0, _as_int(load.get("S", 0), 0))),
                }
                for node_id, load in node_loads.items()
            ),
            key=lambda row: str(row.get("node_id", "")),
        ),
        "overloaded_channel_ids": sorted(set(overloaded_channel_ids)),
        "budget_outcome": combined_budget_outcome,
        "power_flow_hash": power_flow_hash,
        "model_evaluation_results": sorted(
            (dict(row) for row in list(model_evaluation_results or []) if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("result_id", ""))),
        ),
        "model_output_actions": sorted(
            (dict(row) for row in list(model_output_actions or []) if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("model_id", "")), str(row.get("binding_id", "")), str(row.get("output_id", ""))),
        ),
        "model_observation_rows": sorted(
            (dict(row) for row in list(model_observation_rows or []) if isinstance(row, Mapping)),
            key=lambda row: str(row.get("artifact_id", "")),
        ),
        "model_cache_rows": [dict(row) for row in list(model_cache_rows_runtime or []) if isinstance(row, Mapping)],
        "model_cost_units": int(max(0, model_cost_units)),
        "model_budget_outcome": model_budget_outcome,
        "storage_state_rows": [dict(row) for row in list(storage_rows_runtime or []) if isinstance(row, Mapping)],
    }


def solve_power_network_e0(
    *,
    graph_row: Mapping[str, object],
    model_binding_rows: object,
    current_tick: int,
    reason: str = "degrade.elec.e1_disabled",
) -> dict:
    del current_tick
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    binding_rows_by_id = _binding_rows_by_id(model_binding_rows)
    total_p = 0
    for node in sorted((dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)), key=lambda row: str(row.get("node_id", ""))):
        payload = normalize_elec_node_payload(_as_map(node.get("payload")))
        if payload.get("node_kind") != "load":
            continue
        load = _aggregate_load_for_node(node_payload=payload, model_binding_rows_by_id=binding_rows_by_id)
        total_p += int(max(0, _as_int(load.get("P", 0), 0)))
    edges = sorted((dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)), key=lambda row: str(row.get("edge_id", "")))
    weights = dict((str(edge.get("edge_id", "")).strip(), int(max(1, _as_int(_as_map(edge.get("payload")).get("capacity_rating", 1), 1)))) for edge in edges)
    p_by_edge = _weighted_integer_split(total=total_p, keys=[str(edge.get("edge_id", "")).strip() for edge in edges], weights=weights)
    edge_status_rows = []
    flow_channels = []
    for edge in edges:
        edge_id = str(edge.get("edge_id", "")).strip()
        payload = normalize_elec_edge_payload(_as_map(edge.get("payload")))
        p = int(max(0, _as_int(p_by_edge.get(edge_id, 0), 0)))
        loss = int((p * 50) // 1000)
        p_del = int(max(0, p - loss))
        channel = build_power_flow_channel(
            graph_id=graph_id,
            edge_id=edge_id,
            source_node_id=str(edge.get("from_node_id", "")).strip(),
            sink_node_id=str(edge.get("to_node_id", "")).strip(),
            capacity_rating=int(max(0, _as_int(payload.get("capacity_rating", 0), 0))),
        )
        flow_channels.append(channel)
        edge_status_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": str(channel.get("channel_id", "")).strip(),
                "tier": "E0",
                "P": int(p_del),
                "Q": 0,
                "S": int(p_del),
                "pf_permille": 1000,
                "heat_loss_stub": int(loss),
            }
        )
    return {
        "mode": "E0",
        "graph_id": graph_id,
        "flow_channels": sorted(flow_channels, key=lambda row: str(row.get("channel_id", ""))),
        "edge_status_rows": sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", ""))),
        "node_status_rows": [],
        "overloaded_channel_ids": [],
        "budget_outcome": "degraded",
        "downgrade_reason": str(reason or "degrade.elec.e1_disabled"),
        "power_flow_hash": canonical_sha256(
            [{"edge_id": str(row.get("edge_id", "")), "P": int(_as_int(row.get("P", 0), 0))} for row in edge_status_rows]
        ),
    }


def _spec_numeric(spec_row: Mapping[str, object], keys: List[str]) -> int | None:
    params = _as_map(spec_row.get("parameters"))
    for key in keys:
        value = params.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
    return None


def evaluate_connection_spec_compatibility(
    *,
    connector_spec_row: Mapping[str, object] | None,
    edge_spec_row: Mapping[str, object] | None,
) -> dict:
    connector = dict(connector_spec_row or {})
    edge = dict(edge_spec_row or {})
    reasons: List[str] = []
    connector_type = str(_as_map(connector.get("parameters")).get("connector_type", "")).strip()
    edge_type = str(_as_map(edge.get("parameters")).get("connector_type", "")).strip()
    if connector_type and edge_type and connector_type != edge_type:
        reasons.append("connector_type_mismatch")
    v_conn = _spec_numeric(connector, ["voltage_rating", "voltage_rating_v", "voltage"])
    v_edge = _spec_numeric(edge, ["voltage_rating", "voltage_rating_v", "voltage"])
    if v_conn is not None and v_edge is not None and v_conn != v_edge:
        reasons.append("voltage_mismatch")
    i_conn = _spec_numeric(connector, ["current_rating", "current_rating_a", "current"])
    i_edge = _spec_numeric(edge, ["current_rating", "current_rating_a", "current"])
    if i_conn is not None and i_edge is not None and i_conn > i_edge:
        reasons.append("current_over_edge_rating")
    return {
        "compatible": len(reasons) == 0,
        "reasons": sorted(reasons),
    }


__all__ = [
    "ElectricError",
    "REFUSAL_ELEC_NETWORK_INVALID",
    "REFUSAL_ELEC_SPEC_NONCOMPLIANT",
    "build_power_flow_channel",
    "compute_pf_permille",
    "deterministic_power_channel_id",
    "evaluate_connection_spec_compatibility",
    "normalize_elec_edge_payload",
    "normalize_elec_node_payload",
    "solve_power_network_e0",
    "solve_power_network_e1",
]
