"""Deterministic affordance listing derived from PerceivedModel + law/authority."""

from __future__ import annotations

from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from src.interaction import resolve_action_surfaces


_KNOWN_TARGET_KINDS = (
    "agent",
    "cohort",
    "faction",
    "territory",
    "blueprint",
    "logistics_node",
    "manifest",
    "shipment_commitment",
    "construction_project",
    "installed_structure",
    "micro_part",
    "materialization_state",
    "distribution_aggregate",
    "provenance_event",
    "asset_health",
    "failure_event",
    "maintenance_commitment",
    "commitment",
    "event_stream",
    "reenactment_request",
    "reenactment_artifact",
)
_KNOWN_PREVIEW_MODES = ("none", "cheap", "expensive")


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _refusal(
    reason_code: str,
    message: str,
    remediation_hint: str,
    relevant_ids: Dict[str, object] | None = None,
    path: str = "$",
) -> Dict[str, object]:
    ids = {}
    for key, value in sorted((dict(relevant_ids or {})).items(), key=lambda row: str(row[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": ids,
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _stable_id(prefix: str, payload: dict) -> str:
    return "{}.{}".format(str(prefix), str(canonical_sha256(dict(payload)))[:16])


def _target_kind_from_prefix(target_semantic_id: str) -> str:
    token = str(target_semantic_id or "").strip()
    if token.startswith("blueprint."):
        return "blueprint"
    if token.startswith("logistics.node.") or token.startswith("node."):
        return "logistics_node"
    if token.startswith("manifest.") or token.startswith("shipment.manifest."):
        return "manifest"
    if token.startswith("commitment.shipment.") or token.startswith("shipment.commitment."):
        return "shipment_commitment"
    if token.startswith("project.construction."):
        return "construction_project"
    if token.startswith("assembly.structure_instance."):
        return "installed_structure"
    if token.startswith("micro.part."):
        return "micro_part"
    if token.startswith("materialization.state."):
        return "materialization_state"
    if token.startswith("distribution.aggregate."):
        return "distribution_aggregate"
    if token.startswith("provenance.event."):
        return "provenance_event"
    if token.startswith("asset.health.") or token.startswith("asset_health."):
        return "asset_health"
    if token.startswith("failure.event."):
        return "failure_event"
    if token.startswith("commitment.maintenance."):
        return "maintenance_commitment"
    if token.startswith("commitment."):
        return "commitment"
    if token.startswith("stream.event."):
        return "event_stream"
    if token.startswith("reenactment.request."):
        return "reenactment_request"
    if token.startswith("reenactment."):
        return "reenactment_artifact"
    if token.startswith("agent.") or token.startswith("body.") or token.startswith("camera."):
        return "agent"
    if token.startswith("cohort.") or token.startswith("population."):
        return "cohort"
    if token.startswith("faction."):
        return "faction"
    if token.startswith("territory.") or token.startswith("region."):
        return "territory"
    return ""


def _target_kind_from_entities(perceived_model: dict, target_semantic_id: str) -> str:
    entities = dict((dict(perceived_model or {})).get("entities") or {})
    rows = list(entities.get("entries") or [])
    token = str(target_semantic_id).strip()
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("entity_id", ""))):
        entity_id = str(row.get("semantic_id", "")).strip() or str(row.get("entity_id", "")).strip()
        if entity_id != token:
            continue
        explicit = str(row.get("entity_kind", "")).strip()
        if explicit in _KNOWN_TARGET_KINDS:
            return explicit
        if str(row.get("agent_id", "")).strip():
            return "agent"
        return _target_kind_from_prefix(entity_id)
    return ""


def _target_kind_from_populations(perceived_model: dict, target_semantic_id: str) -> str:
    populations = dict((dict(perceived_model or {})).get("populations") or {})
    rows = list(populations.get("entries") or [])
    token = str(target_semantic_id).strip()
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("cohort_id", ""))):
        cohort_id = str(row.get("cohort_id", "")).strip()
        population_id = str(row.get("population_id", "")).strip()
        if token not in (cohort_id, population_id):
            continue
        return "cohort"
    return ""


def _target_kind_from_control(perceived_model: dict, target_semantic_id: str) -> str:
    control = dict((dict(perceived_model or {})).get("control") or {})
    token = str(target_semantic_id).strip()
    for row in sorted((item for item in list(control.get("orders") or []) if isinstance(item, dict)), key=lambda item: str(item.get("order_id", ""))):
        if str(row.get("target_id", "")).strip() == token:
            target_kind = str(row.get("target_kind", "")).strip()
            if target_kind in _KNOWN_TARGET_KINDS:
                return target_kind
    for row in sorted((item for item in list(control.get("institutions") or []) if isinstance(item, dict)), key=lambda item: str(item.get("institution_id", ""))):
        if str(row.get("faction_id", "")).strip() == token:
            return "faction"
    return ""


def _target_kind(perceived_model: dict, target_semantic_id: str) -> str:
    for resolver in (
        _target_kind_from_entities,
        _target_kind_from_populations,
        _target_kind_from_control,
    ):
        token = resolver(perceived_model, target_semantic_id)
        if token in _KNOWN_TARGET_KINDS:
            return token
    fallback = _target_kind_from_prefix(target_semantic_id)
    if fallback in _KNOWN_TARGET_KINDS:
        return fallback
    return "agent"


def _action_rows(interaction_action_registry: dict) -> List[dict]:
    rows = list((dict(interaction_action_registry or {})).get("actions") or [])
    out = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("action_id", ""))):
        out.append(
            {
                "action_id": str(row.get("action_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "display_name": str(row.get("display_name", "")).strip(),
                "target_kinds": _sorted_unique_strings(list(row.get("target_kinds") or [])),
                "parameter_schema_id": str(row.get("parameter_schema_id", "")).strip() or None,
                "preview_mode": str(row.get("preview_mode", "")).strip(),
                "required_lens_channels": _sorted_unique_strings(list(row.get("required_lens_channels") or [])),
                "default_ui_hints": dict(row.get("default_ui_hints") or {}),
                "extensions": dict(row.get("extensions") or {}),
            }
        )
    return out


def _action_rows_by_process(interaction_action_registry: dict) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _action_rows(interaction_action_registry):
        process_id = str(row.get("process_id", "")).strip()
        if process_id and process_id not in out:
            out[process_id] = dict(row)
    return out


def _allowed_processes(law_profile: dict) -> List[str]:
    return _sorted_unique_strings(list((dict(law_profile or {})).get("allowed_processes") or []))


def _process_entitlement_map(law_profile: dict) -> Dict[str, str]:
    payload = dict((dict(law_profile or {})).get("process_entitlement_requirements") or {})
    out = {}
    for key in sorted(payload.keys()):
        process_id = str(key).strip()
        entitlement = str(payload.get(key, "")).strip()
        if process_id and entitlement:
            out[process_id] = entitlement
    return out


def _surface_affordance_row(
    *,
    target_semantic_id: str,
    target_kind: str,
    process_id: str,
    action_row: dict,
    surface_row: dict,
    law_profile: dict,
    authority_context: dict,
    perceived_model: dict,
) -> dict:
    process_id = str(process_id).strip()
    if not process_id:
        return {}
    surface_id = str((dict(surface_row or {})).get("surface_id", "")).strip()
    if not surface_id:
        return {}

    allowed_processes = set(_allowed_processes(law_profile))
    if process_id not in allowed_processes:
        return {}

    entitlement_map = _process_entitlement_map(law_profile)
    registry_required = _sorted_unique_strings(list((dict(action_row or {})).get("required_entitlements") or []))
    mapped_required = str(entitlement_map.get(process_id, "")).strip()
    required_entitlements = _sorted_unique_strings(list(registry_required) + ([mapped_required] if mapped_required else []))
    authority_entitlements = set(_sorted_unique_strings(list((dict(authority_context or {})).get("entitlements") or [])))
    missing_entitlements = [token for token in required_entitlements if token not in authority_entitlements]

    channels = set(_sorted_unique_strings(list((dict(perceived_model or {})).get("channels") or [])))
    required_lens_channels = _sorted_unique_strings(list((dict(action_row or {})).get("required_lens_channels") or []))
    missing_lens_channels = [token for token in required_lens_channels if token not in channels]

    surface_extensions = dict((dict(surface_row or {})).get("extensions") or {})
    tool_compatible = bool(surface_extensions.get("tool_compatible", True))
    tool_process_allowed_ids = _sorted_unique_strings(list(surface_extensions.get("tool_process_allowed_ids") or []))
    tool_process_compatible = True
    if tool_process_allowed_ids:
        tool_process_compatible = process_id in set(tool_process_allowed_ids)
    enabled = (not missing_entitlements) and (not missing_lens_channels) and tool_compatible and tool_process_compatible
    disabled_reason_code = ""
    if (not tool_compatible) or (not tool_process_compatible):
        disabled_reason_code = "refusal.tool.incompatible"
    elif missing_entitlements:
        disabled_reason_code = "ENTITLEMENT_MISSING"
    elif missing_lens_channels:
        disabled_reason_code = "refusal.ep.channel_forbidden"

    display_name = str((dict(action_row or {})).get("display_name", "")).strip() or process_id
    preview_mode = str((dict(action_row or {})).get("preview_mode", "")).strip()
    if preview_mode not in _KNOWN_PREVIEW_MODES:
        preview_mode = "none"
    hints = dict((dict(action_row or {})).get("default_ui_hints") or {})
    cost_units_estimate = hints.get("cost_units_estimate")
    parsed_cost_units = None if cost_units_estimate is None else max(0, _to_int(cost_units_estimate, 0))
    surface_parameter_schema_id = (dict(surface_row or {})).get("parameter_schema_id")
    row = {
        "schema_version": "1.0.0",
        "affordance_id": _stable_id(
            "affordance",
            {
                "target_semantic_id": str(target_semantic_id),
                "surface_id": surface_id,
                "process_id": process_id,
            },
        ),
        "target_semantic_id": str(target_semantic_id),
        "process_id": process_id,
        "display_name": display_name,
        "required_entitlements": required_entitlements,
        "required_lens_channels": required_lens_channels,
        "parameter_schema_id": (
            str(surface_parameter_schema_id).strip()
            if isinstance(surface_parameter_schema_id, str) and str(surface_parameter_schema_id).strip()
            else (dict(action_row or {}).get("parameter_schema_id"))
        ),
        "preview_capability": preview_mode,
        "cost_units_estimate": parsed_cost_units,
        "deterministic_fingerprint": "",
        "extensions": {
            "action_id": str((dict(action_row or {})).get("action_id", "")).strip(),
            "target_kind": target_kind,
            "enabled": bool(enabled),
            "missing_entitlements": list(missing_entitlements),
            "missing_lens_channels": list(missing_lens_channels),
            "default_ui_hints": hints,
            "registry_extensions": dict((dict(action_row or {})).get("extensions") or {}),
            "surface_id": surface_id,
            "surface_type_id": str((dict(surface_row or {})).get("surface_type_id", "")).strip(),
            "surface_visibility_policy_id": str((dict(surface_row or {})).get("visibility_policy_id", "")).strip(),
            "compatible_tool_tags": _sorted_unique_strings(list((dict(surface_row or {})).get("compatible_tool_tags") or [])),
            "tool_compatible": bool(tool_compatible),
            "tool_process_compatible": bool(tool_process_compatible),
            "tool_process_allowed_ids": list(tool_process_allowed_ids),
            "tool_process_disallowed_ids": _sorted_unique_strings(list(surface_extensions.get("tool_process_disallowed_ids") or [])),
            "active_tool_id": surface_extensions.get("active_tool_id"),
            "active_tool_type_id": surface_extensions.get("active_tool_type_id"),
            "active_tool_effect_model_id": surface_extensions.get("active_tool_effect_model_id"),
            "active_tool_tags": _sorted_unique_strings(list(surface_extensions.get("active_tool_tags") or [])),
            "active_tool_effect_parameters": dict(surface_extensions.get("active_tool_effect_parameters") or {}),
            "disabled_reason_code": disabled_reason_code,
        },
    }
    fingerprint_seed = dict(row)
    fingerprint_seed["deterministic_fingerprint"] = ""
    row["deterministic_fingerprint"] = canonical_sha256(fingerprint_seed)
    return row


def _affordance_row(
    *,
    target_semantic_id: str,
    target_kind: str,
    action_row: dict,
    law_profile: dict,
    authority_context: dict,
    perceived_model: dict,
) -> dict | None:
    process_id = str(action_row.get("process_id", "")).strip()
    action_id = str(action_row.get("action_id", "")).strip()
    if (not process_id) or (not action_id):
        return None

    action_target_kinds = _sorted_unique_strings(list(action_row.get("target_kinds") or []))
    if action_target_kinds and target_kind not in set(action_target_kinds):
        return None

    allowed_processes = set(_allowed_processes(law_profile))
    process_allowed = process_id in allowed_processes
    if not process_allowed:
        return None

    entitlement_map = _process_entitlement_map(law_profile)
    registry_required = _sorted_unique_strings(list(action_row.get("required_entitlements") or []))
    mapped_required = str(entitlement_map.get(process_id, "")).strip()
    required_entitlements = _sorted_unique_strings(list(registry_required) + ([mapped_required] if mapped_required else []))
    authority_entitlements = set(_sorted_unique_strings(list((dict(authority_context or {})).get("entitlements") or [])))
    missing_entitlements = [token for token in required_entitlements if token not in authority_entitlements]

    channels = set(_sorted_unique_strings(list((dict(perceived_model or {})).get("channels") or [])))
    required_lens_channels = _sorted_unique_strings(list(action_row.get("required_lens_channels") or []))
    missing_lens_channels = [token for token in required_lens_channels if token not in channels]

    enabled = (not missing_entitlements) and (not missing_lens_channels)
    affordance_id = _stable_id(
        "affordance",
        {
            "target_semantic_id": str(target_semantic_id),
            "process_id": process_id,
        },
    )
    preview_mode = str(action_row.get("preview_mode", "")).strip()
    if preview_mode not in _KNOWN_PREVIEW_MODES:
        preview_mode = "none"
    cost_units_estimate = (dict(action_row.get("default_ui_hints") or {})).get("cost_units_estimate")
    if cost_units_estimate is None:
        parsed_cost_units = None
    else:
        parsed_cost_units = max(0, _to_int(cost_units_estimate, 0))

    row = {
        "schema_version": "1.0.0",
        "affordance_id": affordance_id,
        "target_semantic_id": str(target_semantic_id),
        "process_id": process_id,
        "display_name": str(action_row.get("display_name", "")).strip() or process_id,
        "required_entitlements": required_entitlements,
        "required_lens_channels": required_lens_channels,
        "parameter_schema_id": action_row.get("parameter_schema_id"),
        "preview_capability": preview_mode,
        "cost_units_estimate": parsed_cost_units,
        "deterministic_fingerprint": "",
        "extensions": {
            "action_id": action_id,
            "target_kind": target_kind,
            "enabled": bool(enabled),
            "missing_entitlements": list(missing_entitlements),
            "missing_lens_channels": list(missing_lens_channels),
            "default_ui_hints": dict(action_row.get("default_ui_hints") or {}),
            "registry_extensions": dict(action_row.get("extensions") or {}),
        },
    }
    fingerprint_seed = dict(row)
    fingerprint_seed["deterministic_fingerprint"] = ""
    row["deterministic_fingerprint"] = canonical_sha256(fingerprint_seed)
    return row


def build_affordance_list(
    *,
    perceived_model: dict,
    target_semantic_id: str,
    law_profile: dict,
    authority_context: dict,
    interaction_action_registry: dict,
    surface_type_registry: dict | None = None,
    tool_tag_registry: dict | None = None,
    tool_type_registry: dict | None = None,
    tool_effect_model_registry: dict | None = None,
    surface_visibility_policy_registry: dict | None = None,
    held_tool_tags: list[object] | None = None,
    active_tool: dict | None = None,
    include_disabled: bool = True,
    repo_root: str = "",
) -> Dict[str, object]:
    """Build deterministic affordance list for a selected perceived semantic target."""
    target_id = str(target_semantic_id).strip()
    if not target_id:
        return _refusal(
            "refusal.interaction.target_missing",
            "target_semantic_id is required for affordance generation",
            "Select a valid target semantic id before listing affordances.",
            {},
            "$.target_semantic_id",
        )

    target_kind = _target_kind(perceived_model, target_id)
    resolved_surfaces = resolve_action_surfaces(
        perceived_model=dict(perceived_model or {}),
        target_semantic_id=target_id,
        law_profile=dict(law_profile or {}),
        authority_context=dict(authority_context or {}),
        surface_type_registry=dict(surface_type_registry or {}),
        tool_tag_registry=dict(tool_tag_registry or {}),
        tool_type_registry=dict(tool_type_registry or {}),
        tool_effect_model_registry=dict(tool_effect_model_registry or {}),
        surface_visibility_policy_registry=dict(surface_visibility_policy_registry or {}),
        held_tool_tags=list(held_tool_tags or []),
        active_tool=dict(active_tool or {}),
    )
    surface_rows = [
        dict(row)
        for row in list(dict(resolved_surfaces or {}).get("surfaces") or [])
        if isinstance(row, dict)
    ]

    rows = []
    if surface_rows:
        action_rows_by_process = _action_rows_by_process(interaction_action_registry)
        for surface_row in sorted(surface_rows, key=lambda row: str(row.get("surface_id", ""))):
            for process_id in _sorted_unique_strings(list(surface_row.get("allowed_process_ids") or [])):
                row = _surface_affordance_row(
                    target_semantic_id=target_id,
                    target_kind=target_kind,
                    process_id=process_id,
                    action_row=dict(action_rows_by_process.get(process_id) or {}),
                    surface_row=surface_row,
                    law_profile=law_profile,
                    authority_context=authority_context,
                    perceived_model=perceived_model,
                )
                if not isinstance(row, dict) or not row:
                    continue
                if (not bool(include_disabled)) and (not bool((dict(row.get("extensions") or {})).get("enabled", False))):
                    continue
                rows.append(row)
        rows = sorted(
            rows,
            key=lambda row: (
                str((dict(row.get("extensions") or {})).get("surface_id", "")),
                str(row.get("process_id", "")),
                str(row.get("affordance_id", "")),
            ),
        )
    else:
        for action_row in _action_rows(interaction_action_registry):
            row = _affordance_row(
                target_semantic_id=target_id,
                target_kind=target_kind,
                action_row=action_row,
                law_profile=law_profile,
                authority_context=authority_context,
                perceived_model=perceived_model,
            )
            if not isinstance(row, dict):
                continue
            if (not bool(include_disabled)) and (not bool((dict(row.get("extensions") or {})).get("enabled", False))):
                continue
            rows.append(row)
        rows = sorted(
            rows,
            key=lambda row: (
                str(row.get("display_name", "")).lower(),
                str(row.get("process_id", "")),
                str(row.get("affordance_id", "")),
            ),
        )

    tick = max(0, _to_int((dict((dict(perceived_model or {})).get("time_state") or {})).get("tick", 0), 0))
    viewpoint_id = str((dict(perceived_model or {})).get("viewpoint_id", "")).strip() or "viewpoint.unknown"
    payload = {
        "schema_version": "1.0.0",
        "tick": int(tick),
        "viewpoint_id": viewpoint_id,
        "target_semantic_id": target_id,
        "affordances": list(rows),
        "list_hash": "",
        "extensions": {
            "target_kind": target_kind,
            "include_disabled": bool(include_disabled),
            "surface_driven": bool(surface_rows),
            "action_surfaces": [
                {
                    "surface_id": str(row.get("surface_id", "")).strip(),
                    "surface_type_id": str(row.get("surface_type_id", "")).strip(),
                    "local_transform": dict(row.get("local_transform") or {}),
                    "tool_compatible": bool(dict(row.get("extensions") or {}).get("tool_compatible", True)),
                    "active_tool_id": (dict(row.get("extensions") or {})).get("active_tool_id"),
                    "active_tool_type_id": (dict(row.get("extensions") or {})).get("active_tool_type_id"),
                }
                for row in sorted(surface_rows, key=lambda item: str(item.get("surface_id", "")))
            ],
        },
    }
    hash_seed = dict(payload)
    hash_seed["list_hash"] = ""
    payload["list_hash"] = canonical_sha256(hash_seed)

    if str(repo_root).strip():
        checked = validate_instance(
            repo_root=str(repo_root),
            schema_name="affordance_list",
            payload=payload,
            strict_top_level=True,
        )
        if not bool(checked.get("valid", False)):
            return _refusal(
                "refusal.interaction.schema_invalid",
                "affordance_list payload failed schema validation",
                "Repair affordance generation fields to satisfy schema contracts.",
                {"schema_id": "affordance_list"},
                "$.affordance_list",
            )
    return {
        "result": "complete",
        "target_kind": target_kind,
        "affordance_list": payload,
        "list_hash": str(payload.get("list_hash", "")),
    }
