"""Deterministic ActionSurface resolution from PerceivedModel metadata."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.control.capability import resolve_missing_capabilities
from tools.xstack.compatx.canonical_json import canonical_sha256


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _surface_id(parent_semantic_id: str, local_surface_index: int) -> str:
    return "surface.{}".format(
        canonical_sha256(
            {
                "parent_semantic_id": str(parent_semantic_id).strip(),
                "local_surface_index": int(max(0, _to_int(local_surface_index, 0))),
            }
        )[:24]
    )


def _normalize_transform(raw: object) -> dict:
    payload = dict(raw or {}) if isinstance(raw, dict) else {}
    position = dict(payload.get("position_mm") or {})
    orientation = dict(payload.get("orientation_mdeg") or {})
    return {
        "position_mm": {
            "x": _to_int(position.get("x", 0), 0),
            "y": _to_int(position.get("y", 0), 0),
            "z": _to_int(position.get("z", 0), 0),
        },
        "orientation_mdeg": {
            "yaw": _to_int(orientation.get("yaw", 0), 0),
            "pitch": _to_int(orientation.get("pitch", 0), 0),
            "roll": _to_int(orientation.get("roll", 0), 0),
        },
        "scale_permille": max(1, _to_int(payload.get("scale_permille", 1000), 1000)),
    }


def _rows_from_registry(payload: Mapping[str, object], key: str) -> List[dict]:
    root = dict(payload or {})
    rows = root.get(key)
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get(key)
    if not isinstance(rows, list):
        return []
    return [dict(item) for item in rows if isinstance(item, dict)]


def _surface_type_set(registry_payload: Mapping[str, object] | None) -> set[str]:
    rows = _rows_from_registry(dict(registry_payload or {}), "surface_types")
    return set(
        str(row.get("surface_type_id", "")).strip()
        for row in rows
        if str(row.get("surface_type_id", "")).strip()
    )


def _tool_tag_set(registry_payload: Mapping[str, object] | None) -> set[str]:
    rows = _rows_from_registry(dict(registry_payload or {}), "tool_tags")
    return set(
        str(row.get("tool_tag_id", "")).strip()
        for row in rows
        if str(row.get("tool_tag_id", "")).strip()
    )


def _visibility_policy_rows(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    rows = _rows_from_registry(dict(registry_payload or {}), "policies")
    for row in sorted(rows, key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        requires_entitlement = row.get("requires_entitlement")
        requires_lens_channel = row.get("requires_lens_channel")
        out[policy_id] = {
            "policy_id": policy_id,
            "requires_entitlement": (
                str(requires_entitlement).strip() if isinstance(requires_entitlement, str) and str(requires_entitlement).strip() else None
            ),
            "requires_lens_channel": (
                str(requires_lens_channel).strip() if isinstance(requires_lens_channel, str) and str(requires_lens_channel).strip() else None
            ),
        }
    if "visibility.default" not in out:
        out["visibility.default"] = {
            "policy_id": "visibility.default",
            "requires_entitlement": None,
            "requires_lens_channel": None,
        }
    return out


def _tool_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(dict(registry_payload or {}), "tool_types")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("tool_type_id", ""))):
        tool_type_id = str(row.get("tool_type_id", "")).strip()
        if not tool_type_id:
            continue
        out[tool_type_id] = dict(row)
    return out


def _tool_effect_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(dict(registry_payload or {}), "effect_models")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("effect_model_id", ""))):
        effect_model_id = str(row.get("effect_model_id", "")).strip()
        if not effect_model_id:
            continue
        out[effect_model_id] = dict(row)
    return out


def _visible_under_policy(policy_row: Mapping[str, object], entitlements: set[str], channels: set[str]) -> bool:
    raw_entitlement = policy_row.get("requires_entitlement")
    requires_entitlement = (
        str(raw_entitlement).strip() if isinstance(raw_entitlement, str) and str(raw_entitlement).strip() else ""
    )
    if requires_entitlement and requires_entitlement not in entitlements:
        return False
    raw_channel = policy_row.get("requires_lens_channel")
    requires_lens_channel = (
        str(raw_channel).strip() if isinstance(raw_channel, str) and str(raw_channel).strip() else ""
    )
    if requires_lens_channel and requires_lens_channel not in channels:
        return False
    return True


def _surface_lists_from_entity(entity_row: Mapping[str, object], interaction_block: Mapping[str, object], target_id: str) -> List[tuple[str, list]]:
    row = dict(entity_row or {})
    out: List[tuple[str, list]] = []
    surfaces = row.get("action_surfaces")
    if isinstance(surfaces, list):
        out.append(("entity.action_surfaces", list(surfaces)))
    assembly = dict(row.get("assembly_metadata") or {})
    if isinstance(assembly.get("action_surfaces"), list):
        out.append(("entity.assembly_metadata.action_surfaces", list(assembly.get("action_surfaces") or [])))
    ag_node = dict(row.get("ag_node_metadata") or {})
    if isinstance(ag_node.get("action_surfaces"), list):
        out.append(("entity.ag_node_metadata.action_surfaces", list(ag_node.get("action_surfaces") or [])))
    blueprint = dict(row.get("blueprint_metadata") or {})
    if isinstance(blueprint.get("action_surfaces"), list):
        out.append(("entity.blueprint_metadata.action_surfaces", list(blueprint.get("action_surfaces") or [])))
    extensions = dict(row.get("extensions") or {})
    if isinstance(extensions.get("action_surfaces"), list):
        out.append(("entity.extensions.action_surfaces", list(extensions.get("action_surfaces") or [])))
    interaction_map = dict(interaction_block.get("action_surfaces") or {})
    keyed = interaction_map.get(str(target_id).strip())
    if isinstance(keyed, list):
        out.append(("interaction.action_surfaces[target]", list(keyed)))
    return out


def _target_entity_row(perceived_model: Mapping[str, object], target_semantic_id: str) -> dict:
    entities = dict((dict(perceived_model or {})).get("entities") or {})
    rows = list(entities.get("entries") or [])
    token = str(target_semantic_id).strip()
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("entity_id", ""))):
        semantic_id = str(row.get("semantic_id", "")).strip() or str(row.get("entity_id", "")).strip()
        if semantic_id == token:
            return dict(row)
    return {}


def _held_tool_tags(held_tool_tags: object, authority_context: Mapping[str, object]) -> List[str]:
    explicit = _sorted_unique_strings(held_tool_tags)
    authority = dict(authority_context or {})
    direct = _sorted_unique_strings(authority.get("held_tool_tags"))
    ext = dict(authority.get("extensions") or {})
    ext_tags = _sorted_unique_strings(ext.get("held_tool_tags"))
    return _sorted_unique_strings(list(explicit) + list(direct) + list(ext_tags))


def resolve_action_surfaces(
    *,
    perceived_model: Mapping[str, object],
    target_semantic_id: str,
    law_profile: Mapping[str, object],
    authority_context: Mapping[str, object],
    surface_type_registry: Mapping[str, object] | None = None,
    tool_tag_registry: Mapping[str, object] | None = None,
    tool_type_registry: Mapping[str, object] | None = None,
    tool_effect_model_registry: Mapping[str, object] | None = None,
    surface_visibility_policy_registry: Mapping[str, object] | None = None,
    capability_bindings: object = None,
    held_tool_tags: object = None,
    active_tool: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    target_id = str(target_semantic_id).strip()
    if not target_id:
        return {"result": "complete", "target_semantic_id": "", "surfaces": [], "surface_count": 0}

    entity_row = _target_entity_row(perceived_model, target_id)
    if not entity_row:
        return {"result": "complete", "target_semantic_id": target_id, "surfaces": [], "surface_count": 0}

    interaction_block = dict((dict(perceived_model or {})).get("interaction") or {})
    channels = set(_sorted_unique_strings((dict(perceived_model or {})).get("channels")))
    authority_entitlements = set(_sorted_unique_strings((dict(authority_context or {})).get("entitlements")))
    allowed_processes = set(_sorted_unique_strings((dict(law_profile or {})).get("allowed_processes")))
    process_entitlement_requirements = dict((dict(law_profile or {})).get("process_entitlement_requirements") or {})
    known_surface_types = _surface_type_set(surface_type_registry)
    known_tool_tags = _tool_tag_set(tool_tag_registry)
    tool_type_rows = _tool_type_rows_by_id(tool_type_registry)
    tool_effect_rows = _tool_effect_rows_by_id(tool_effect_model_registry)
    visibility_policies = _visibility_policy_rows(surface_visibility_policy_registry)
    held_tags = set(_held_tool_tags(held_tool_tags, authority_context))
    active_tool_row = dict(active_tool or {})
    active_tool_id = str(active_tool_row.get("tool_id", "")).strip()
    active_tool_type_id = str(active_tool_row.get("tool_type_id", "")).strip()
    active_tool_effect_model_id = str(active_tool_row.get("effect_model_id", "")).strip()
    active_tool_type_row = dict(tool_type_rows.get(active_tool_type_id) or {})
    active_tool_effect_row = dict(tool_effect_rows.get(active_tool_effect_model_id) or {})
    active_tool_default_tags = set(_sorted_unique_strings(list(active_tool_type_row.get("default_tool_tags") or [])))
    active_tool_tags = set(_sorted_unique_strings(list(active_tool_row.get("tool_tags") or [])))
    active_tool_tags = set(_sorted_unique_strings(list(active_tool_tags) + list(active_tool_default_tags) + list(held_tags)))
    active_tool_allowed_surface_types = set(
        _sorted_unique_strings(list(active_tool_type_row.get("allowed_surface_types") or []))
    )
    active_tool_allowed_process_ids = set(
        _sorted_unique_strings(list(active_tool_type_row.get("allowed_process_ids") or []))
    )
    active_tool_effect_parameters = dict(active_tool_effect_row.get("parameters") or {})
    active_tool_enabled = bool(active_tool_id and active_tool_type_id)

    candidates: List[dict] = []
    source_lists = _surface_lists_from_entity(entity_row, interaction_block, target_id)
    for source_name, rows in source_lists:
        for source_index, raw in enumerate(rows):
            if not isinstance(raw, dict):
                continue
            surface_type_id = str(raw.get("surface_type_id", "")).strip()
            if not surface_type_id:
                continue
            if known_surface_types and surface_type_id not in known_surface_types:
                continue
            allowed = _sorted_unique_strings(list(raw.get("allowed_process_ids") or []))
            if not allowed:
                continue
            normalized_tool_tags = _sorted_unique_strings(list(raw.get("compatible_tool_tags") or []))
            if known_tool_tags:
                normalized_tool_tags = [tag for tag in normalized_tool_tags if tag in known_tool_tags]
            required_capabilities = _sorted_unique_strings(
                list(raw.get("required_capabilities") or [])
            )
            if not required_capabilities:
                required_capabilities = _sorted_unique_strings(
                    list((dict(raw.get("extensions") or {})).get("required_capabilities") or [])
                )
            if required_capabilities:
                missing_caps = resolve_missing_capabilities(
                    entity_id=target_id,
                    required_capabilities=required_capabilities,
                    capability_bindings=capability_bindings,
                )
                if missing_caps:
                    continue
            visibility_policy_id = str(raw.get("visibility_policy_id", "")).strip() or "visibility.default"
            policy_row = dict(visibility_policies.get(visibility_policy_id) or visibility_policies["visibility.default"])
            if not _visible_under_policy(policy_row, authority_entitlements, channels):
                continue
            filtered_allowed = []
            for process_id in allowed:
                if process_id not in allowed_processes:
                    continue
                required_entitlement = str(process_entitlement_requirements.get(process_id, "")).strip()
                if required_entitlement and required_entitlement not in authority_entitlements:
                    continue
                filtered_allowed.append(process_id)
            filtered_allowed = _sorted_unique_strings(filtered_allowed)
            if not filtered_allowed:
                continue
            tool_surface_compatible = True
            if active_tool_enabled and active_tool_allowed_surface_types:
                tool_surface_compatible = surface_type_id in active_tool_allowed_surface_types
            tool_tag_compatible = True
            if normalized_tool_tags:
                tool_tag_compatible = bool(active_tool_tags.intersection(set(normalized_tool_tags)))
            tool_compatible = bool(tool_surface_compatible and tool_tag_compatible)
            tool_process_allowed_ids = list(filtered_allowed)
            tool_process_disallowed_ids: List[str] = []
            if active_tool_enabled and active_tool_allowed_process_ids:
                tool_process_allowed_ids = [token for token in filtered_allowed if token in active_tool_allowed_process_ids]
                tool_process_disallowed_ids = [
                    token for token in filtered_allowed if token not in active_tool_allowed_process_ids
                ]
            normalized = {
                "schema_version": "1.0.0",
                "surface_id": "",
                "parent_semantic_id": target_id,
                "surface_type_id": surface_type_id,
                "local_transform": _normalize_transform(raw.get("local_transform")),
                "compatible_tool_tags": normalized_tool_tags,
                "allowed_process_ids": filtered_allowed,
                "parameter_schema_id": str(raw.get("parameter_schema_id", "")).strip() or None,
                "constraints": dict(raw.get("constraints") or {}) if isinstance(raw.get("constraints"), dict) else None,
                "visibility_policy_id": visibility_policy_id,
                "deterministic_fingerprint": "",
                "extensions": {
                    "source": source_name,
                    "source_index": int(max(0, _to_int(source_index, 0))),
                    "required_capabilities": list(required_capabilities),
                    "tool_compatible": bool(tool_compatible),
                    "tool_surface_compatible": bool(tool_surface_compatible),
                    "tool_tag_compatible": bool(tool_tag_compatible),
                    "tool_process_allowed_ids": _sorted_unique_strings(tool_process_allowed_ids),
                    "tool_process_disallowed_ids": _sorted_unique_strings(tool_process_disallowed_ids),
                    "held_tool_tags": sorted(held_tags),
                    "active_tool_id": active_tool_id or None,
                    "active_tool_type_id": active_tool_type_id or None,
                    "active_tool_effect_model_id": active_tool_effect_model_id or None,
                    "active_tool_tags": _sorted_unique_strings(list(active_tool_tags)),
                    "active_tool_effect_parameters": dict(active_tool_effect_parameters),
                },
            }
            sort_hash = canonical_sha256(
                {
                    "surface_type_id": normalized["surface_type_id"],
                    "local_transform": normalized["local_transform"],
                    "compatible_tool_tags": normalized["compatible_tool_tags"],
                    "allowed_process_ids": normalized["allowed_process_ids"],
                    "parameter_schema_id": normalized["parameter_schema_id"],
                    "constraints": normalized["constraints"],
                    "visibility_policy_id": normalized["visibility_policy_id"],
                }
            )
            candidates.append(
                {
                    "source": source_name,
                    "source_index": int(max(0, _to_int(source_index, 0))),
                    "sort_hash": sort_hash,
                    "row": normalized,
                }
            )

    ordered = sorted(
        candidates,
        key=lambda item: (
            str(item.get("source", "")),
            str(item.get("sort_hash", "")),
            int(item.get("source_index", 0)),
        ),
    )
    resolved: List[dict] = []
    for local_surface_index, candidate in enumerate(ordered):
        row = dict(candidate.get("row") or {})
        row["surface_id"] = _surface_id(target_id, local_surface_index)
        seed = dict(row)
        seed["deterministic_fingerprint"] = ""
        row["deterministic_fingerprint"] = canonical_sha256(seed)
        resolved.append(row)

    resolved = sorted(resolved, key=lambda row: str(row.get("surface_id", "")))
    return {
        "result": "complete",
        "target_semantic_id": target_id,
        "surfaces": resolved,
        "surface_count": len(resolved),
    }


__all__ = ["resolve_action_surfaces"]
