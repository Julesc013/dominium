"""Deterministic THERM-1 thermal-network helpers (T0/T1 baseline)."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from src.core.flow import normalize_flow_channel
from src.core.graph.network_graph_engine import normalize_network_graph
from src.fields.field_engine import build_field_cell
from src.models.model_engine import (
    cache_policy_rows_by_id,
    evaluate_model_bindings,
    model_type_rows_by_id,
    normalize_constitutive_model_rows,
)
from src.safety.safety_engine import build_safety_event
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_THERM_NETWORK_INVALID = "refusal.therm.network_invalid"

_VALID_NODE_KINDS = {"thermal_mass", "source", "sink", "radiator", "heat_exchanger_stub"}
_VALID_EDGE_KINDS = {"conduction_link", "insulated_link", "radiator_link"}

_Q_HEAT_FLOW = "quantity.thermal.heat_flow_stub"
_Q_HEAT_LOSS = "quantity.thermal.heat_loss_stub"
_Q_THERMAL_ENERGY = "quantity.thermal.energy_store_stub"


class ThermalError(ValueError):
    """Deterministic thermal-domain refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_THERM_NETWORK_INVALID)
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


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _ambient_temperature_value(value: object, default_value: int = 20) -> int:
    return int(max(-273, _as_int(value, default_value)))


def _temperature_from_energy(*, thermal_energy: int, heat_capacity: int, ambient_temperature: int) -> int:
    capacity = int(max(1, heat_capacity))
    energy = int(max(0, thermal_energy))
    return int(_ambient_temperature_value(ambient_temperature, 20) + (energy // capacity))


def _default_model_type_registry_payload() -> dict:
    return {
        "record": {
            "model_types": [
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.therm_heat_capacity",
                    "description": "THERM heat-capacity model",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.therm_conductance",
                    "description": "THERM conduction model",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.therm_loss_to_temp",
                    "description": "THERM loss-to-temperature model",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.therm_insulation_modifier",
                    "description": "THERM insulation modifier model",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.therm_conductance_stub",
                    "description": "THERM conduction model stub",
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
            "model_id": "model.therm_heat_capacity",
            "model_type_id": "model_type.therm_heat_capacity",
            "description": "thermal energy to temperature mapping",
            "supported_tiers": ["meso"],
            "input_signature": [],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.therm.temperature", "extensions": {}},
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
            "model_id": "model.therm_conductance",
            "model_type_id": "model_type.therm_conductance",
            "description": "thermal conduction transfer",
            "supported_tiers": ["meso"],
            "input_signature": [],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.therm.heat_transfer", "extensions": {}},
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_HEAT_FLOW, "extensions": {"quantity_bundle_id": "bundle.thermal_basic", "component_quantity_id": _Q_HEAT_FLOW}},
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
            "model_id": "model.therm_loss_to_temp",
            "model_type_id": "model_type.therm_loss_to_temp",
            "description": "map dissipated losses to node thermal energy",
            "supported_tiers": ["meso"],
            "input_signature": [],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": _Q_THERMAL_ENERGY, "extensions": {"component_quantity_id": _Q_THERMAL_ENERGY}},
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": _Q_HEAT_LOSS, "extensions": {}},
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
            "model_id": "model.therm_insulation_modifier",
            "model_type_id": "model_type.therm_insulation_modifier",
            "description": "insulation-adjusted effective conductance model",
            "supported_tiers": ["meso"],
            "input_signature": [],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.therm.insulation_factor_permille", "extensions": {}},
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.therm.effective_conductance", "extensions": {}},
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


def normalize_thermal_node_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    node_kind = str(payload.get("node_kind", "")).strip()
    if node_kind not in _VALID_NODE_KINDS:
        raise ThermalError(
            REFUSAL_THERM_NETWORK_INVALID,
            "thermal node payload requires valid node_kind",
            {"node_kind": node_kind},
        )
    heat_capacity = int(max(1, _as_int(payload.get("heat_capacity_value", 1), 1)))
    thermal_energy = int(max(0, _as_int(payload.get("current_thermal_energy", 0), 0)))
    result = {
        "schema_version": "1.0.0",
        "node_kind": node_kind,
        "heat_capacity_value": int(heat_capacity),
        "current_thermal_energy": int(thermal_energy),
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "model_bindings": _sorted_tokens(payload.get("model_bindings")),
        "safety_instances": _sorted_tokens(payload.get("safety_instances")),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def normalize_thermal_edge_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    edge_kind = str(payload.get("edge_kind", "")).strip()
    if edge_kind not in _VALID_EDGE_KINDS:
        raise ThermalError(
            REFUSAL_THERM_NETWORK_INVALID,
            "thermal edge payload requires valid edge_kind",
            {"edge_kind": edge_kind},
        )
    result = {
        "schema_version": "1.0.0",
        "edge_kind": edge_kind,
        "conductance_value": int(max(0, _as_int(payload.get("conductance_value", 0), 0))),
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "model_bindings": _sorted_tokens(payload.get("model_bindings")),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def deterministic_thermal_channel_id(*, graph_id: str, edge_id: str) -> str:
    digest = canonical_sha256(
        {
            "graph_id": str(graph_id or "").strip(),
            "edge_id": str(edge_id or "").strip(),
            "kind": "thermal_flow_channel",
        }
    )
    return "channel.therm.{}".format(digest[:16])


def build_thermal_flow_channel(
    *,
    graph_id: str,
    edge_id: str,
    source_node_id: str,
    sink_node_id: str,
    capacity_per_tick: int = 0,
    solver_policy_id: str = "flow.solver.default",
    component_capacity_policy_id: str | None = None,
    component_loss_policy_id: str | None = None,
) -> dict:
    return normalize_flow_channel(
        {
            "schema_version": "1.1.0",
            "channel_id": deterministic_thermal_channel_id(graph_id=graph_id, edge_id=edge_id),
            "graph_id": str(graph_id or "").strip(),
            "quantity_bundle_id": "bundle.thermal_basic",
            "component_capacity_policy_id": None if component_capacity_policy_id is None else str(component_capacity_policy_id).strip() or None,
            "component_loss_policy_id": None if component_loss_policy_id is None else str(component_loss_policy_id).strip() or None,
            "source_node_id": str(source_node_id or "").strip(),
            "sink_node_id": str(sink_node_id or "").strip(),
            "capacity_per_tick": None if int(max(0, _as_int(capacity_per_tick, 0))) <= 0 else int(max(0, _as_int(capacity_per_tick, 0))),
            "delay_ticks": 0,
            "loss_fraction": 0,
            "solver_policy_id": str(solver_policy_id or "").strip() or "flow.solver.default",
            "priority": 0,
            "extensions": {
                "edge_id": str(edge_id or "").strip(),
                "component_weights": {
                    _Q_HEAT_FLOW: 1000,
                    _Q_HEAT_LOSS: 100,
                },
            },
        }
    )


def _heat_input_rows_by_node_id(rows: object) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for row in sorted((dict(item) for item in list(rows or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", ""))):
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        delta = int(max(0, _as_int(row.get("heat_loss", row.get("heat_input", 0)), 0)))
        out[node_id] = int(max(0, int(out.get(node_id, 0)) + delta))
    return out


def _model_binding_rows_for_node(
    *,
    node_id: str,
    node_payload: Mapping[str, object],
    heat_input: int,
    ambient_temperature: int,
) -> Tuple[dict, dict]:
    loss_binding = {
        "schema_version": "1.0.0",
        "binding_id": "binding.therm.loss_to_temp.{}".format(node_id),
        "model_id": "model.therm_loss_to_temp",
        "target_kind": "node",
        "target_id": str(node_id),
        "tier": "meso",
        "parameters": {
            "heat_loss": int(max(0, _as_int(heat_input, 0))),
        },
        "enabled": True,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    heat_capacity_binding = {
        "schema_version": "1.0.0",
        "binding_id": "binding.therm.heat_capacity.{}".format(node_id),
        "model_id": "model.therm_heat_capacity",
        "target_kind": "node",
        "target_id": str(node_id),
        "tier": "meso",
        "parameters": {
            "current_thermal_energy": int(max(0, _as_int(node_payload.get("current_thermal_energy", 0), 0))),
            "heat_capacity_value": int(max(1, _as_int(node_payload.get("heat_capacity_value", 1), 1))),
            "ambient_temperature": int(_ambient_temperature_value(ambient_temperature, 20)),
        },
        "enabled": True,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    return loss_binding, heat_capacity_binding


def _model_binding_row_for_edge(
    *,
    edge_id: str,
    edge_payload: Mapping[str, object],
) -> dict:
    ext = _as_map(edge_payload.get("extensions"))
    insulation_factor = int(max(0, _as_int(ext.get("insulation_factor_permille", 1000), 1000)))
    return {
        "schema_version": "1.0.0",
        "binding_id": "binding.therm.insulation.{}".format(edge_id),
        "model_id": "model.therm_insulation_modifier",
        "target_kind": "edge",
        "target_id": str(edge_id),
        "tier": "meso",
        "parameters": {
            "conductance_value": int(max(0, _as_int(edge_payload.get("conductance_value", 0), 0))),
            "insulation_factor_permille": int(insulation_factor),
        },
        "enabled": True,
        "deterministic_fingerprint": "",
        "extensions": {},
    }


def _effective_conductance_by_edge_id_from_outputs(*, output_actions: List[dict], edge_payloads_by_id: Mapping[str, dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for edge_id in sorted(edge_payloads_by_id.keys()):
        payload = dict(edge_payloads_by_id.get(edge_id) or {})
        out[edge_id] = int(max(0, _as_int(payload.get("conductance_value", 0), 0)))
    for row in sorted((dict(item) for item in list(output_actions or [])), key=lambda item: (str(item.get("binding_id", "")), str(item.get("output_id", "")))):
        if str(row.get("output_kind", "")).strip() != "derived_quantity":
            continue
        if str(row.get("output_id", "")).strip() != "derived.therm.effective_conductance":
            continue
        edge_id = str(row.get("target_id", "")).strip()
        if not edge_id:
            continue
        payload = _as_map(row.get("payload"))
        value = int(max(0, _as_int(payload.get("value", out.get(edge_id, 0)), out.get(edge_id, 0))))
        out[edge_id] = value
    return dict((key, int(out[key])) for key in sorted(out.keys()))


def _insulation_factor_by_edge_id_from_outputs(*, output_actions: List[dict], edge_payloads_by_id: Mapping[str, dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for edge_id in sorted(edge_payloads_by_id.keys()):
        payload = dict(edge_payloads_by_id.get(edge_id) or {})
        ext = _as_map(payload.get("extensions"))
        out[edge_id] = int(max(0, _as_int(ext.get("insulation_factor_permille", 1000), 1000)))
    for row in sorted((dict(item) for item in list(output_actions or [])), key=lambda item: (str(item.get("binding_id", "")), str(item.get("output_id", "")))):
        if str(row.get("output_kind", "")).strip() != "derived_quantity":
            continue
        if str(row.get("output_id", "")).strip() != "derived.therm.insulation_factor_permille":
            continue
        edge_id = str(row.get("target_id", "")).strip()
        if not edge_id:
            continue
        payload = _as_map(row.get("payload"))
        out[edge_id] = int(max(0, _as_int(payload.get("value", out.get(edge_id, 1000)), out.get(edge_id, 1000))))
    return dict((key, int(out[key])) for key in sorted(out.keys()))


def _model_binding_row_for_conductance_edge(
    *,
    edge_id: str,
    edge_payload: Mapping[str, object],
    source_node_id: str,
    sink_node_id: str,
    source_temperature: int,
    sink_temperature: int,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "binding_id": "binding.therm.conductance.{}".format(edge_id),
        "model_id": "model.therm_conductance",
        "target_kind": "edge",
        "target_id": str(edge_id),
        "tier": "meso",
        "parameters": {
            "source_node_id": str(source_node_id),
            "sink_node_id": str(sink_node_id),
            "node_a_temperature": int(source_temperature),
            "node_b_temperature": int(sink_temperature),
            "conductance_value": int(max(0, _as_int(edge_payload.get("conductance_value", 0), 0))),
        },
        "enabled": True,
        "deterministic_fingerprint": "",
        "extensions": {},
    }


def _apply_loss_model_outputs(*, output_actions: List[dict], thermal_energy_by_node_id: Dict[str, int]) -> None:
    for row in sorted((dict(item) for item in list(output_actions or [])), key=lambda item: (str(item.get("binding_id", "")), str(item.get("output_id", "")))):
        if str(row.get("output_kind", "")).strip() != "flow_adjustment":
            continue
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        payload = _as_map(row.get("payload"))
        delta = int(_as_int(payload.get("delta", 0), 0))
        if delta <= 0:
            continue
        thermal_energy_by_node_id[target_id] = int(max(0, int(thermal_energy_by_node_id.get(target_id, 0)) + int(delta)))


def _temperature_map_from_heat_capacity_outputs(*, output_actions: List[dict], fallback_temperature_by_node_id: Dict[str, int]) -> Dict[str, int]:
    out = dict((str(key), int(value)) for key, value in fallback_temperature_by_node_id.items())
    for row in sorted((dict(item) for item in list(output_actions or [])), key=lambda item: (str(item.get("binding_id", "")), str(item.get("output_id", "")))):
        if str(row.get("output_kind", "")).strip() != "derived_quantity":
            continue
        if str(row.get("output_id", "")).strip() != "derived.therm.temperature":
            continue
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        payload = _as_map(row.get("payload"))
        out[target_id] = int(_as_int(payload.get("value", out.get(target_id, 20)), out.get(target_id, 20)))
    return dict((key, int(out[key])) for key in sorted(out.keys()))


def _apply_conduction_outputs(
    *,
    output_actions: List[dict],
    thermal_energy_by_node_id: Dict[str, int],
) -> List[dict]:
    applied_rows: List[dict] = []
    for row in sorted((dict(item) for item in list(output_actions or [])), key=lambda item: (str(item.get("binding_id", "")), str(item.get("output_id", "")))):
        if str(row.get("output_kind", "")).strip() != "derived_quantity":
            continue
        if str(row.get("output_id", "")).strip() != "derived.therm.heat_transfer":
            continue
        payload = _as_map(row.get("payload"))
        from_node_id = str(payload.get("from_node_id", "")).strip()
        to_node_id = str(payload.get("to_node_id", "")).strip()
        transfer = int(max(0, _as_int(payload.get("value", 0), 0)))
        if (not from_node_id) or (not to_node_id) or transfer <= 0:
            continue
        available = int(max(0, _as_int(thermal_energy_by_node_id.get(from_node_id, 0), 0)))
        moved = int(min(transfer, available))
        if moved <= 0:
            continue
        thermal_energy_by_node_id[from_node_id] = int(max(0, available - moved))
        thermal_energy_by_node_id[to_node_id] = int(max(0, _as_int(thermal_energy_by_node_id.get(to_node_id, 0), 0)) + moved)
        applied_rows.append(
            {
                "edge_id": str(row.get("target_id", "")).strip(),
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "heat_transfer": int(moved),
                "model_id": str(row.get("model_id", "")).strip(),
                "binding_id": str(row.get("binding_id", "")).strip(),
            }
        )
    return sorted(applied_rows, key=lambda item: (str(item.get("edge_id", "")), str(item.get("from_node_id", "")), str(item.get("to_node_id", ""))))


def _temperature_cells_from_node_rows(
    *,
    node_rows: List[dict],
    field_id: str,
    current_tick: int,
) -> List[dict]:
    out: List[dict] = []
    for row in sorted((dict(item) for item in list(node_rows or [])), key=lambda item: str(item.get("node_id", ""))):
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        ext = _as_map(row.get("extensions"))
        cell_id = str(ext.get("field_cell_id", "")).strip() or "cell.therm.{}".format(node_id.replace(".", "_"))
        out.append(
            build_field_cell(
                field_id=str(field_id or "field.temperature.global"),
                cell_id=cell_id,
                value=int(_as_int(row.get("temperature", 20), 20)),
                last_updated_tick=int(max(0, _as_int(current_tick, 0))),
                value_kind="scalar",
                extensions={"node_id": node_id},
            )
        )
    return sorted(out, key=lambda item: (str(item.get("field_id", "")), str(item.get("cell_id", ""))))


def _safety_rows_for_overtemp(
    *,
    current_tick: int,
    node_rows: List[dict],
    safety_pattern_id: str,
    default_threshold: int,
) -> Tuple[List[dict], List[dict]]:
    hazard_rows: List[dict] = []
    safety_events: List[dict] = []
    for row in sorted((dict(item) for item in list(node_rows or [])), key=lambda item: str(item.get("node_id", ""))):
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        ext = _as_map(row.get("extensions"))
        threshold = int(max(0, _as_int(ext.get("overtemp_threshold", default_threshold), default_threshold)))
        temp = int(_as_int(row.get("temperature", 20), 20))
        if temp <= threshold:
            continue
        over_by = int(max(0, temp - threshold))
        hazard = {
            "schema_version": "1.0.0",
            "target_id": node_id,
            "hazard_type_id": "hazard.overheat",
            "accumulated_value": int(over_by),
            "last_update_tick": int(max(0, _as_int(current_tick, 0))),
            "deterministic_fingerprint": "",
            "extensions": {
                "temperature": int(temp),
                "threshold": int(threshold),
            },
        }
        hazard["deterministic_fingerprint"] = canonical_sha256(dict(hazard, deterministic_fingerprint=""))
        hazard_rows.append(hazard)
        safety_events.append(
            build_safety_event(
                event_id="",
                tick=int(max(0, _as_int(current_tick, 0))),
                instance_id="instance.safety.overtemp.{}".format(node_id),
                pattern_id=str(safety_pattern_id or "safety.overtemp_trip"),
                pattern_type="failsafe",
                status="triggered",
                target_ids=[node_id],
                action_count=1,
                details={
                    "temperature": int(temp),
                    "threshold": int(threshold),
                    "hazard_type_id": "hazard.overheat",
                    "recommended_action": "effect.shutdown",
                },
                extensions={},
            )
        )
    return (
        sorted(hazard_rows, key=lambda item: (str(item.get("target_id", "")), str(item.get("hazard_type_id", "")))),
        sorted(safety_events, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", "")))),
    )


def solve_thermal_network_t0(
    *,
    graph_row: Mapping[str, object],
    current_tick: int,
    heat_input_rows: object = None,
    ambient_temperature: int = 20,
    downgrade_reason: str = "degrade.therm.t1_disabled",
) -> dict:
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    heat_input_by_node_id = _heat_input_rows_by_node_id(heat_input_rows)
    node_rows = sorted((dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", "")))
    edge_rows = sorted((dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", "")))

    node_status_rows: List[dict] = []
    for node in node_rows:
        node_id = str(node.get("node_id", "")).strip()
        if not node_id:
            continue
        payload = normalize_thermal_node_payload(_as_map(node.get("payload")))
        thermal_energy = int(max(0, _as_int(payload.get("current_thermal_energy", 0), 0)) + int(max(0, _as_int(heat_input_by_node_id.get(node_id, 0), 0))))
        temperature = _temperature_from_energy(
            thermal_energy=int(thermal_energy),
            heat_capacity=int(max(1, _as_int(payload.get("heat_capacity_value", 1), 1))),
            ambient_temperature=int(ambient_temperature),
        )
        node_status_rows.append(
            {
                "node_id": node_id,
                "node_kind": str(payload.get("node_kind", "")),
                "thermal_energy": int(thermal_energy),
                "temperature": int(temperature),
                "heat_input": int(max(0, _as_int(heat_input_by_node_id.get(node_id, 0), 0))),
                "extensions": dict(payload.get("extensions") or {}),
            }
        )

    edge_status_rows: List[dict] = []
    flow_channels: List[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        flow_channel = build_thermal_flow_channel(
            graph_id=graph_id,
            edge_id=edge_id,
            source_node_id=from_node_id,
            sink_node_id=to_node_id,
            capacity_per_tick=0,
        )
        flow_channels.append(flow_channel)
        edge_payload = normalize_thermal_edge_payload(_as_map(edge.get("payload")))
        edge_ext = _as_map(edge_payload.get("extensions"))
        base_conductance = int(max(0, _as_int(edge_payload.get("conductance_value", 0), 0)))
        insulation_factor = int(max(0, _as_int(edge_ext.get("insulation_factor_permille", 1000), 1000)))
        effective_conductance = int(max(0, (base_conductance * insulation_factor) // 1000))
        edge_status_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": str(flow_channel.get("channel_id", "")).strip(),
                "heat_transfer": 0,
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "base_conductance_value": int(base_conductance),
                "effective_conductance_value": int(effective_conductance),
                "insulation_factor_permille": int(insulation_factor),
                "tier": "T0",
            }
        )

    thermal_network_hash = canonical_sha256(
        {
            "graph_id": graph_id,
            "tier": "T0",
            "nodes": [{"node_id": str(row.get("node_id", "")), "temperature": int(_as_int(row.get("temperature", 0), 0))} for row in node_status_rows],
            "edges": [{"edge_id": str(row.get("edge_id", "")), "heat_transfer": int(_as_int(row.get("heat_transfer", 0), 0))} for row in edge_status_rows],
        }
    )
    decision_log_rows = [
        {
            "process_id": "process.therm_budget_degrade",
            "tick": int(max(0, _as_int(current_tick, 0))),
            "target_id": graph_id,
            "reason_code": str(downgrade_reason or "degrade.therm.t1_disabled"),
            "details": {"mode": "T0"},
        }
    ]
    return {
        "mode": "T0",
        "graph_id": graph_id,
        "node_status_rows": sorted(node_status_rows, key=lambda row: str(row.get("node_id", ""))),
        "edge_status_rows": sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", ""))),
        "flow_channels": sorted(flow_channels, key=lambda row: str(row.get("channel_id", ""))),
        "model_evaluation_results": [],
        "model_output_actions": [],
        "model_observation_rows": [],
        "model_cache_rows": [],
        "model_cost_units": 0,
        "model_budget_outcome": "degraded",
        "hazard_rows": [],
        "safety_event_rows": [],
        "field_temperature_rows": _temperature_cells_from_node_rows(
            node_rows=sorted(node_status_rows, key=lambda row: str(row.get("node_id", ""))),
            field_id="field.temperature.global",
            current_tick=int(max(0, _as_int(current_tick, 0))),
        ),
        "thermal_network_hash": str(thermal_network_hash),
        "overheat_event_hash_chain": canonical_sha256([]),
        "decision_log_rows": decision_log_rows,
        "budget_outcome": "degraded",
        "downgrade_reason": str(downgrade_reason or "degrade.therm.t1_disabled"),
    }


def solve_thermal_network_t1(
    *,
    graph_row: Mapping[str, object],
    current_tick: int,
    heat_input_rows: object = None,
    model_rows: object = None,
    model_type_rows: Mapping[str, dict] | None = None,
    model_cache_policy_rows: Mapping[str, dict] | None = None,
    model_cache_rows: object = None,
    max_processed_edges: int = 4096,
    max_cost_units: int = 0,
    ambient_temperature: int = 20,
    overtemp_threshold_default: int = 120,
    safety_pattern_id: str = "safety.overtemp_trip",
) -> dict:
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    node_rows = sorted((dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", "")))
    edge_rows = sorted((dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", "")))
    if int(max_processed_edges) <= 0 or len(edge_rows) > int(max_processed_edges):
        return solve_thermal_network_t0(
            graph_row=graph,
            current_tick=int(current_tick),
            heat_input_rows=heat_input_rows,
            ambient_temperature=int(ambient_temperature),
            downgrade_reason="degrade.therm.t1_budget",
        )
    estimated_cost = int(len(node_rows) + len(edge_rows))
    if int(max_cost_units) > 0 and int(estimated_cost) > int(max_cost_units):
        return solve_thermal_network_t0(
            graph_row=graph,
            current_tick=int(current_tick),
            heat_input_rows=heat_input_rows,
            ambient_temperature=int(ambient_temperature),
            downgrade_reason="degrade.therm.t1_budget",
        )

    heat_input_by_node_id = _heat_input_rows_by_node_id(heat_input_rows)
    normalized_nodes: Dict[str, dict] = {}
    for row in node_rows:
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        normalized_nodes[node_id] = normalize_thermal_node_payload(_as_map(row.get("payload")))

    node_thermal_energy: Dict[str, int] = {}
    for node_id in sorted(normalized_nodes.keys()):
        payload = dict(normalized_nodes.get(node_id) or {})
        node_thermal_energy[node_id] = int(max(0, _as_int(payload.get("current_thermal_energy", 0), 0)))

    merged_model_rows = _merge_model_rows(model_rows)
    merged_model_types = _merge_model_type_rows(model_type_rows)
    merged_cache_policies = _merge_cache_policy_rows(model_cache_policy_rows)
    cache_rows_runtime = [dict(row) for row in list(model_cache_rows or []) if isinstance(row, Mapping)]

    model_evaluation_results: List[dict] = []
    model_output_actions: List[dict] = []
    model_observation_rows: List[dict] = []
    model_cost_units = 0
    model_budget_outcome = "complete"

    def _resolve_input(binding_row: Mapping[str, object], input_ref: Mapping[str, object]):
        params = _as_map(binding_row.get("parameters"))
        input_id = str(input_ref.get("input_id", "")).strip()
        if input_id and input_id in params:
            return params.get(input_id)
        return 0

    loss_bindings: List[dict] = []
    capacity_bindings: List[dict] = []
    for node_id in sorted(normalized_nodes.keys()):
        node_payload = dict(normalized_nodes.get(node_id) or {})
        heat_input = int(max(0, _as_int(heat_input_by_node_id.get(node_id, 0), 0)))
        loss_binding, capacity_binding = _model_binding_rows_for_node(
            node_id=node_id,
            node_payload=node_payload,
            heat_input=int(heat_input),
            ambient_temperature=int(ambient_temperature),
        )
        loss_bindings.append(loss_binding)
        capacity_bindings.append(capacity_binding)
    if loss_bindings:
        loss_eval = evaluate_model_bindings(
            current_tick=int(current_tick),
            model_rows=[dict(row) for row in merged_model_rows.values()],
            binding_rows=loss_bindings,
            cache_rows=cache_rows_runtime,
            model_type_rows=merged_model_types,
            cache_policy_rows=merged_cache_policies,
            input_resolver_fn=_resolve_input,
            max_cost_units=1_000_000 if int(max_cost_units) <= 0 else int(max(1, max_cost_units)),
            far_target_ids=[],
            far_tick_stride=1,
        )
        cache_rows_runtime = [dict(row) for row in list(loss_eval.get("cache_rows") or []) if isinstance(row, Mapping)]
        _apply_loss_model_outputs(
            output_actions=[dict(row) for row in list(loss_eval.get("output_actions") or []) if isinstance(row, Mapping)],
            thermal_energy_by_node_id=node_thermal_energy,
        )
        model_evaluation_results.extend([dict(row) for row in list(loss_eval.get("evaluation_results") or []) if isinstance(row, Mapping)])
        model_output_actions.extend([dict(row) for row in list(loss_eval.get("output_actions") or []) if isinstance(row, Mapping)])
        model_observation_rows.extend([dict(row) for row in list(loss_eval.get("observation_rows") or []) if isinstance(row, Mapping)])
        model_cost_units += int(max(0, _as_int(loss_eval.get("cost_units", 0), 0)))
        if str(loss_eval.get("budget_outcome", "")).strip() == "degraded":
            model_budget_outcome = "degraded"

    for binding in list(capacity_bindings):
        node_id = str(binding.get("target_id", "")).strip()
        params = _as_map(binding.get("parameters"))
        params["current_thermal_energy"] = int(max(0, _as_int(node_thermal_energy.get(node_id, 0), 0)))
        binding["parameters"] = params
    capacity_eval = evaluate_model_bindings(
        current_tick=int(current_tick),
        model_rows=[dict(row) for row in merged_model_rows.values()],
        binding_rows=capacity_bindings,
        cache_rows=cache_rows_runtime,
        model_type_rows=merged_model_types,
        cache_policy_rows=merged_cache_policies,
        input_resolver_fn=_resolve_input,
        max_cost_units=1_000_000 if int(max_cost_units) <= 0 else int(max(1, max_cost_units)),
        far_target_ids=[],
        far_tick_stride=1,
    )
    cache_rows_runtime = [dict(row) for row in list(capacity_eval.get("cache_rows") or []) if isinstance(row, Mapping)]
    model_evaluation_results.extend([dict(row) for row in list(capacity_eval.get("evaluation_results") or []) if isinstance(row, Mapping)])
    model_output_actions.extend([dict(row) for row in list(capacity_eval.get("output_actions") or []) if isinstance(row, Mapping)])
    model_observation_rows.extend([dict(row) for row in list(capacity_eval.get("observation_rows") or []) if isinstance(row, Mapping)])
    model_cost_units += int(max(0, _as_int(capacity_eval.get("cost_units", 0), 0)))
    if str(capacity_eval.get("budget_outcome", "")).strip() == "degraded":
        model_budget_outcome = "degraded"

    temperature_by_node_id = {}
    for node_id in sorted(normalized_nodes.keys()):
        payload = dict(normalized_nodes.get(node_id) or {})
        temperature_by_node_id[node_id] = _temperature_from_energy(
            thermal_energy=int(node_thermal_energy.get(node_id, 0)),
            heat_capacity=int(max(1, _as_int(payload.get("heat_capacity_value", 1), 1))),
            ambient_temperature=int(ambient_temperature),
        )
    temperature_by_node_id = _temperature_map_from_heat_capacity_outputs(
        output_actions=[dict(row) for row in list(capacity_eval.get("output_actions") or []) if isinstance(row, Mapping)],
        fallback_temperature_by_node_id=temperature_by_node_id,
    )

    edge_payloads_by_id: Dict[str, dict] = {}
    edge_endpoint_by_id: Dict[str, dict] = {}
    insulation_bindings: List[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        edge_payload = normalize_thermal_edge_payload(_as_map(edge.get("payload")))
        edge_payloads_by_id[edge_id] = dict(edge_payload)
        edge_endpoint_by_id[edge_id] = {
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
        }
        insulation_bindings.append(
            _model_binding_row_for_edge(
                edge_id=edge_id,
                edge_payload=edge_payload,
            )
        )
    insulation_eval = evaluate_model_bindings(
        current_tick=int(current_tick),
        model_rows=[dict(row) for row in merged_model_rows.values()],
        binding_rows=insulation_bindings,
        cache_rows=cache_rows_runtime,
        model_type_rows=merged_model_types,
        cache_policy_rows=merged_cache_policies,
        input_resolver_fn=_resolve_input,
        max_cost_units=1_000_000 if int(max_cost_units) <= 0 else int(max(1, max_cost_units)),
        far_target_ids=[],
        far_tick_stride=1,
    )
    cache_rows_runtime = [dict(row) for row in list(insulation_eval.get("cache_rows") or []) if isinstance(row, Mapping)]
    model_evaluation_results.extend([dict(row) for row in list(insulation_eval.get("evaluation_results") or []) if isinstance(row, Mapping)])
    model_output_actions.extend([dict(row) for row in list(insulation_eval.get("output_actions") or []) if isinstance(row, Mapping)])
    model_observation_rows.extend([dict(row) for row in list(insulation_eval.get("observation_rows") or []) if isinstance(row, Mapping)])
    model_cost_units += int(max(0, _as_int(insulation_eval.get("cost_units", 0), 0)))
    if str(insulation_eval.get("budget_outcome", "")).strip() == "degraded":
        model_budget_outcome = "degraded"

    effective_conductance_by_edge_id = _effective_conductance_by_edge_id_from_outputs(
        output_actions=[dict(row) for row in list(insulation_eval.get("output_actions") or []) if isinstance(row, Mapping)],
        edge_payloads_by_id=edge_payloads_by_id,
    )
    insulation_factor_by_edge_id = _insulation_factor_by_edge_id_from_outputs(
        output_actions=[dict(row) for row in list(insulation_eval.get("output_actions") or []) if isinstance(row, Mapping)],
        edge_payloads_by_id=edge_payloads_by_id,
    )

    conduction_bindings: List[dict] = []
    for edge_id in sorted(edge_payloads_by_id.keys()):
        edge_payload = dict(edge_payloads_by_id.get(edge_id) or {})
        endpoint = dict(edge_endpoint_by_id.get(edge_id) or {})
        from_node_id = str(endpoint.get("from_node_id", "")).strip()
        to_node_id = str(endpoint.get("to_node_id", "")).strip()
        edge_payload["conductance_value"] = int(max(0, _as_int(effective_conductance_by_edge_id.get(edge_id, edge_payload.get("conductance_value", 0)), 0)))
        conduction_bindings.append(
            _model_binding_row_for_conductance_edge(
                edge_id=edge_id,
                edge_payload=edge_payload,
                source_node_id=from_node_id,
                sink_node_id=to_node_id,
                source_temperature=int(_as_int(temperature_by_node_id.get(from_node_id, ambient_temperature), ambient_temperature)),
                sink_temperature=int(_as_int(temperature_by_node_id.get(to_node_id, ambient_temperature), ambient_temperature)),
            )
        )
    conduction_eval = evaluate_model_bindings(
        current_tick=int(current_tick),
        model_rows=[dict(row) for row in merged_model_rows.values()],
        binding_rows=conduction_bindings,
        cache_rows=cache_rows_runtime,
        model_type_rows=merged_model_types,
        cache_policy_rows=merged_cache_policies,
        input_resolver_fn=_resolve_input,
        max_cost_units=1_000_000 if int(max_cost_units) <= 0 else int(max(1, max_cost_units)),
        far_target_ids=[],
        far_tick_stride=1,
    )
    cache_rows_runtime = [dict(row) for row in list(conduction_eval.get("cache_rows") or []) if isinstance(row, Mapping)]
    model_evaluation_results.extend([dict(row) for row in list(conduction_eval.get("evaluation_results") or []) if isinstance(row, Mapping)])
    model_output_actions.extend([dict(row) for row in list(conduction_eval.get("output_actions") or []) if isinstance(row, Mapping)])
    model_observation_rows.extend([dict(row) for row in list(conduction_eval.get("observation_rows") or []) if isinstance(row, Mapping)])
    model_cost_units += int(max(0, _as_int(conduction_eval.get("cost_units", 0), 0)))
    if str(conduction_eval.get("budget_outcome", "")).strip() == "degraded":
        model_budget_outcome = "degraded"
    conduction_rows = _apply_conduction_outputs(
        output_actions=[dict(row) for row in list(conduction_eval.get("output_actions") or []) if isinstance(row, Mapping)],
        thermal_energy_by_node_id=node_thermal_energy,
    )

    for node_id in sorted(normalized_nodes.keys()):
        payload = dict(normalized_nodes.get(node_id) or {})
        temperature_by_node_id[node_id] = _temperature_from_energy(
            thermal_energy=int(node_thermal_energy.get(node_id, 0)),
            heat_capacity=int(max(1, _as_int(payload.get("heat_capacity_value", 1), 1))),
            ambient_temperature=int(ambient_temperature),
        )

    node_status_rows: List[dict] = []
    for node in node_rows:
        node_id = str(node.get("node_id", "")).strip()
        if not node_id:
            continue
        node_payload = dict(normalized_nodes.get(node_id) or {})
        node_status_rows.append(
            {
                "node_id": node_id,
                "node_kind": str(node_payload.get("node_kind", "")),
                "thermal_energy": int(max(0, _as_int(node_thermal_energy.get(node_id, 0), 0))),
                "temperature": int(_as_int(temperature_by_node_id.get(node_id, ambient_temperature), ambient_temperature)),
                "heat_capacity_value": int(max(1, _as_int(node_payload.get("heat_capacity_value", 1), 1))),
                "heat_input": int(max(0, _as_int(heat_input_by_node_id.get(node_id, 0), 0))),
                "extensions": dict(node_payload.get("extensions") or {}),
            }
        )
    node_status_rows = sorted(node_status_rows, key=lambda row: str(row.get("node_id", "")))

    conduction_by_edge_id = dict((str(row.get("edge_id", "")).strip(), dict(row)) for row in conduction_rows if str(row.get("edge_id", "")).strip())
    edge_status_rows: List[dict] = []
    flow_channels: List[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        flow_channel = build_thermal_flow_channel(
            graph_id=graph_id,
            edge_id=edge_id,
            source_node_id=from_node_id,
            sink_node_id=to_node_id,
            capacity_per_tick=0,
        )
        flow_channels.append(flow_channel)
        conduction = dict(conduction_by_edge_id.get(edge_id) or {})
        base_payload = dict(edge_payloads_by_id.get(edge_id) or {})
        base_conductance = int(max(0, _as_int(base_payload.get("conductance_value", 0), 0)))
        effective_conductance = int(
            max(
                0,
                _as_int(
                    effective_conductance_by_edge_id.get(edge_id, base_conductance),
                    base_conductance,
                ),
            )
        )
        insulation_factor = int(max(0, _as_int(insulation_factor_by_edge_id.get(edge_id, 1000), 1000)))
        edge_status_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": str(flow_channel.get("channel_id", "")).strip(),
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "heat_transfer": int(max(0, _as_int(conduction.get("heat_transfer", 0), 0))),
                "effective_from_node_id": str(conduction.get("from_node_id", from_node_id)).strip() or from_node_id,
                "effective_to_node_id": str(conduction.get("to_node_id", to_node_id)).strip() or to_node_id,
                "base_conductance_value": int(base_conductance),
                "effective_conductance_value": int(effective_conductance),
                "insulation_factor_permille": int(insulation_factor),
                "tier": "T1",
            }
        )
    edge_status_rows = sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", "")))
    flow_channels = sorted(flow_channels, key=lambda row: str(row.get("channel_id", "")))

    hazard_rows, safety_event_rows = _safety_rows_for_overtemp(
        current_tick=int(current_tick),
        node_rows=node_status_rows,
        safety_pattern_id=str(safety_pattern_id or "safety.overtemp_trip"),
        default_threshold=int(max(0, _as_int(overtemp_threshold_default, 120))),
    )
    thermal_network_hash = canonical_sha256(
        {
            "graph_id": graph_id,
            "tier": "T1",
            "nodes": [{"node_id": str(row.get("node_id", "")), "temperature": int(_as_int(row.get("temperature", 0), 0)), "energy": int(_as_int(row.get("thermal_energy", 0), 0))} for row in node_status_rows],
            "edges": [{"edge_id": str(row.get("edge_id", "")), "heat_transfer": int(_as_int(row.get("heat_transfer", 0), 0)), "from_node_id": str(row.get("effective_from_node_id", "")), "to_node_id": str(row.get("effective_to_node_id", ""))} for row in edge_status_rows],
        }
    )
    overheat_event_hash_chain = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "pattern_id": str(row.get("pattern_id", "")).strip(),
                "target_ids": [str(token).strip() for token in list(row.get("target_ids") or []) if str(token).strip()],
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in safety_event_rows
        ]
    )
    decision_log_rows: List[dict] = []
    if model_budget_outcome == "degraded":
        decision_log_rows.append(
            {
                "process_id": "process.therm_budget_degrade",
                "tick": int(max(0, _as_int(current_tick, 0))),
                "target_id": graph_id,
                "reason_code": "degrade.therm.model_budget",
                "details": {"mode": "T1"},
            }
        )

    return {
        "mode": "T1",
        "graph_id": graph_id,
        "node_status_rows": node_status_rows,
        "edge_status_rows": edge_status_rows,
        "flow_channels": flow_channels,
        "model_evaluation_results": sorted(
            (dict(row) for row in list(model_evaluation_results or []) if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("result_id", ""))),
        ),
        "model_output_actions": sorted(
            (dict(row) for row in list(model_output_actions or []) if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("model_id", "")), str(row.get("binding_id", "")), str(row.get("output_kind", "")), str(row.get("output_id", ""))),
        ),
        "model_observation_rows": sorted(
            (dict(row) for row in list(model_observation_rows or []) if isinstance(row, Mapping)),
            key=lambda row: str(row.get("artifact_id", "")),
        ),
        "model_cache_rows": [dict(row) for row in list(cache_rows_runtime or []) if isinstance(row, Mapping)],
        "model_cost_units": int(max(0, model_cost_units)),
        "model_budget_outcome": str(model_budget_outcome),
        "hazard_rows": hazard_rows,
        "safety_event_rows": safety_event_rows,
        "field_temperature_rows": _temperature_cells_from_node_rows(
            node_rows=node_status_rows,
            field_id="field.temperature.global",
            current_tick=int(max(0, _as_int(current_tick, 0))),
        ),
        "thermal_network_hash": str(thermal_network_hash),
        "overheat_event_hash_chain": str(overheat_event_hash_chain),
        "decision_log_rows": decision_log_rows,
        "budget_outcome": "degraded" if str(model_budget_outcome) == "degraded" else "complete",
    }


__all__ = [
    "ThermalError",
    "REFUSAL_THERM_NETWORK_INVALID",
    "build_thermal_flow_channel",
    "deterministic_thermal_channel_id",
    "normalize_thermal_edge_payload",
    "normalize_thermal_node_payload",
    "solve_thermal_network_t0",
    "solve_thermal_network_t1",
]
