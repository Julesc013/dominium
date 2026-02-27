"""Deterministic interaction preview generation (derived only, budget-gated)."""

from __future__ import annotations

import json
import os
from typing import Dict

from src.materials.blueprint_engine import (
    BlueprintCompileError,
    blueprint_bom_summary,
    build_blueprint_ghost_overlay,
    compile_blueprint_artifacts,
)
from src.performance.cost_engine import normalize_budget_envelope, reserve_inspection_budget
from src.performance.inspection_cache import (
    build_cache_key as inspection_build_cache_key,
    build_inspection_snapshot,
    cache_lookup_or_store as inspection_cache_lookup_or_store,
)
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance

_BLUEPRINT_PREVIEW_PROCESSES = {
    "process.blueprint_inspect",
    "process.blueprint_place_ghost",
    "process.blueprint_generate_bom_summary",
}


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: list[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _read_json_payload(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve_registry(runtime: dict, key: str, repo_root: str, fallback_rel_path: str) -> dict:
    payload = dict(runtime.get(key) or {})
    if payload:
        return payload
    if not str(repo_root).strip():
        return {}
    path = os.path.join(str(repo_root), fallback_rel_path.replace("/", os.sep))
    return _read_json_payload(path)


def _canonical_payload(value: object):
    if isinstance(value, dict):
        return dict((str(key), _canonical_payload(value[key])) for key in sorted(value.keys()))
    if isinstance(value, list):
        return [_canonical_payload(item) for item in value]
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


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


def _target_payload_from_perceived(perceived_model: dict, target_semantic_id: str) -> dict:
    token = str(target_semantic_id).strip()
    entities = list((dict((dict(perceived_model or {})).get("entities") or {})).get("entries") or [])
    for row in sorted((item for item in entities if isinstance(item, dict)), key=lambda item: str(item.get("entity_id", ""))):
        entity_id = str(row.get("semantic_id", "")).strip() or str(row.get("entity_id", "")).strip()
        if entity_id == token:
            return {
                "target_id": token,
                "exists": True,
                "collection": "entities.entries",
                "row": dict(row),
            }
    populations = list((dict((dict(perceived_model or {})).get("populations") or {})).get("entries") or [])
    for row in sorted((item for item in populations if isinstance(item, dict)), key=lambda item: str(item.get("cohort_id", ""))):
        cohort_id = str(row.get("cohort_id", "")).strip()
        population_id = str(row.get("population_id", "")).strip()
        if token in (cohort_id, population_id):
            return {
                "target_id": token,
                "exists": True,
                "collection": "populations.entries",
                "row": dict(row),
            }
    return {
        "target_id": token,
        "exists": False,
    }


def _preview_tick(perceived_model: dict) -> int:
    return int(max(0, _to_int((dict((dict(perceived_model or {})).get("time_state") or {})).get("tick", 0), 0)))


def _preview_hash_payload(payload: dict) -> str:
    seed = dict(payload)
    seed["preview_hash"] = ""
    return canonical_sha256(seed)


def _base_preview(
    *,
    tick: int,
    target_semantic_id: str,
    process_id: str,
    parameters: dict,
    predicted_effects: dict,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "preview_id": "preview.{}".format(
            canonical_sha256(
                {
                    "tick": int(tick),
                    "target_semantic_id": str(target_semantic_id),
                    "process_id": str(process_id),
                    "parameters": _canonical_payload(parameters),
                }
            )[:16]
        ),
        "tick": int(tick),
        "target_semantic_id": str(target_semantic_id),
        "process_id": str(process_id),
        "parameters": _canonical_payload(parameters),
        "predicted_effects": _canonical_payload(dict(predicted_effects or {})),
        "preview_hash": "",
        "extensions": {},
    }
    payload["preview_hash"] = _preview_hash_payload(payload)
    return payload


def _validate_preview(repo_root: str, payload: dict) -> Dict[str, object]:
    if not str(repo_root).strip():
        return {"result": "complete"}
    checked = validate_instance(
        repo_root=str(repo_root),
        schema_name="interaction_preview",
        payload=payload,
        strict_top_level=True,
    )
    if bool(checked.get("valid", False)):
        return {"result": "complete"}
    return _refusal(
        "refusal.preview.schema_invalid",
        "interaction_preview payload failed schema validation",
        "Repair preview payload fields to satisfy interaction_preview schema.",
        {"schema_id": "interaction_preview"},
        "$.interaction_preview",
    )


def _ranked_redact_preview(runtime: dict, payload: dict) -> dict:
    profile_id = str((dict(runtime or {})).get("server_profile_id", "")).strip()
    if profile_id != "server.profile.rank_strict":
        return dict(payload)
    redacted = dict(payload)
    predicted = dict(redacted.get("predicted_effects") or {})
    summary = str(predicted.get("summary", "")).strip() or "preview redacted by ranked profile"
    redacted["predicted_effects"] = {"summary": summary}
    redacted["extensions"] = {
        "preview_capability": str((dict(redacted.get("extensions") or {})).get("preview_capability", "")),
        "ranked_redacted": True,
    }
    redacted["preview_hash"] = _preview_hash_payload(redacted)
    return redacted


def _blueprint_preview_payload(
    *,
    repo_root: str,
    runtime: dict,
    process_id: str,
    target_semantic_id: str,
    parameters: dict,
    tick: int,
) -> Dict[str, object]:
    blueprint_id = str(target_semantic_id).strip()
    if not blueprint_id.startswith("blueprint."):
        blueprint_id = str((dict(parameters or {})).get("blueprint_id", "")).strip()
    if not blueprint_id.startswith("blueprint."):
        return _refusal(
            "refusal.blueprint.invalid_graph",
            "blueprint preview target is missing a blueprint id",
            "Set target_semantic_id to a blueprint id or provide blueprint_id in parameters.",
            {"target_semantic_id": target_semantic_id},
            "$.target_semantic_id",
        )

    blueprint_registry = _resolve_registry(runtime, "blueprint_registry", repo_root, "data/registries/blueprint_registry.json")
    part_class_registry = _resolve_registry(runtime, "part_class_registry", repo_root, "data/registries/part_class_registry.json")
    connection_type_registry = _resolve_registry(runtime, "connection_type_registry", repo_root, "data/registries/connection_type_registry.json")
    material_class_registry = _resolve_registry(runtime, "material_class_registry", repo_root, "data/registries/material_class_registry.json")
    if not blueprint_registry or not part_class_registry or not connection_type_registry:
        return _refusal(
            "refusal.blueprint.invalid_graph",
            "required blueprint registries are unavailable for preview generation",
            "Load blueprint, part-class, and connection registries before requesting preview.",
            {"blueprint_id": blueprint_id},
            "$.registry_payloads",
        )

    try:
        compiled = compile_blueprint_artifacts(
            repo_root=str(repo_root),
            blueprint_id=blueprint_id,
            parameter_values=dict(parameters or {}),
            pack_lock_hash=str(runtime.get("pack_lock_hash", "")).strip() or "pack_lock_hash.preview",
            blueprint_registry=blueprint_registry,
            part_class_registry=part_class_registry,
            connection_type_registry=connection_type_registry,
            material_class_registry=material_class_registry,
        )
    except BlueprintCompileError as exc:
        return _refusal(
            str(exc.reason_code),
            str(exc),
            "Fix blueprint references or parameters and retry preview generation.",
            dict(exc.details),
            "$.blueprint_compile",
        )

    bom_summary = blueprint_bom_summary(dict(compiled.get("compiled_bom_artifact") or {}))
    ghost_overlay = build_blueprint_ghost_overlay(
        compiled_ag_artifact=dict(compiled.get("compiled_ag_artifact") or {}),
        blueprint_id=blueprint_id,
        include_labels=bool(runtime.get("blueprint_preview_labels", True)),
    )
    payload = _base_preview(
        tick=tick,
        target_semantic_id=blueprint_id,
        process_id=process_id,
        parameters=_canonical_payload(parameters),
        predicted_effects={
            "summary": "blueprint {} compiled for preview".format(blueprint_id),
            "compiled_bom_hash": str((dict(compiled.get("compiled_bom_artifact") or {})).get("artifact_hash", "")),
            "compiled_ag_hash": str((dict(compiled.get("compiled_ag_artifact") or {})).get("artifact_hash", "")),
            "bom_summary": bom_summary,
        },
    )
    payload["extensions"] = {
        "preview_capability": "cheap",
        "blueprint_id": blueprint_id,
        "cache_key": str(compiled.get("cache_key", "")),
        "blueprint_ghost_overlay": ghost_overlay,
    }
    return {
        "result": "complete",
        "preview": payload,
        "preview_hash": str(payload.get("preview_hash", "")),
        "preview_runtime": runtime,
    }


def generate_interaction_preview(
    *,
    perceived_model: dict,
    affordance_row: dict,
    parameters: dict | None,
    preview_runtime: dict | None = None,
    repo_root: str = "",
) -> Dict[str, object]:
    """Generate a deterministic interaction preview without mutating truth."""
    runtime = dict(preview_runtime or {})
    affordance = dict(affordance_row or {})
    process_id = str(affordance.get("process_id", "")).strip()
    target_semantic_id = str(affordance.get("target_semantic_id", "")).strip()
    preview_capability = str(affordance.get("preview_capability", "none")).strip() or "none"
    tick = _preview_tick(perceived_model)
    canonical_parameters = _canonical_payload(dict(parameters or {}))

    if process_id in _BLUEPRINT_PREVIEW_PROCESSES:
        preview_result = _blueprint_preview_payload(
            repo_root=str(repo_root or ""),
            runtime=runtime,
            process_id=process_id,
            target_semantic_id=target_semantic_id,
            parameters=dict(canonical_parameters or {}),
            tick=int(tick),
        )
        if str(preview_result.get("result", "")) != "complete":
            return preview_result
        payload = _ranked_redact_preview(runtime=runtime, payload=dict(preview_result.get("preview") or {}))
        valid = _validate_preview(repo_root=repo_root, payload=payload)
        if str(valid.get("result", "")) != "complete":
            return valid
        return {
            "result": "complete",
            "preview": payload,
            "preview_hash": str(payload.get("preview_hash", "")),
            "preview_runtime": dict(preview_result.get("preview_runtime") or runtime),
        }

    if preview_capability == "none":
        payload = _base_preview(
            tick=tick,
            target_semantic_id=target_semantic_id,
            process_id=process_id,
            parameters=canonical_parameters,
            predicted_effects={"summary": "no preview available"},
        )
        payload["extensions"] = {"preview_capability": "none"}
        payload = _ranked_redact_preview(runtime=runtime, payload=payload)
        valid = _validate_preview(repo_root=repo_root, payload=payload)
        if str(valid.get("result", "")) != "complete":
            return valid
        return {
            "result": "complete",
            "preview": payload,
            "preview_hash": str(payload.get("preview_hash", "")),
            "preview_runtime": runtime,
        }

    if preview_capability == "cheap":
        payload = _base_preview(
            tick=tick,
            target_semantic_id=target_semantic_id,
            process_id=process_id,
            parameters=canonical_parameters,
            predicted_effects={
                "summary": "will attempt {}".format(process_id),
                "target_semantic_id": target_semantic_id,
            },
        )
        payload["extensions"] = {
            "preview_capability": "cheap",
        }
        payload = _ranked_redact_preview(runtime=runtime, payload=payload)
        valid = _validate_preview(repo_root=repo_root, payload=payload)
        if str(valid.get("result", "")) != "complete":
            return valid
        return {
            "result": "complete",
            "preview": payload,
            "preview_hash": str(payload.get("preview_hash", "")),
            "preview_runtime": runtime,
        }

    truth_overlay = dict((dict(perceived_model or {})).get("truth_overlay") or {})
    truth_hash_anchor = str(truth_overlay.get("state_hash_anchor", "")).strip()
    if not truth_hash_anchor:
        return _refusal(
            "refusal.preview.forbidden_by_epistemics",
            "expensive preview requires truth overlay anchor not available under current epistemic channels",
            "Enable an entitled inspection lens/channel or fall back to cheap preview.",
            {"target_semantic_id": target_semantic_id},
            "$.perceived_model.truth_overlay.state_hash_anchor",
        )

    requested_cost_units = max(
        0,
        _to_int((dict(affordance.get("cost_units_estimate", None) or {}) if isinstance(affordance.get("cost_units_estimate"), dict) else affordance.get("cost_units_estimate", 1)), 1),
    )
    if requested_cost_units == 0:
        requested_cost_units = 1

    budget_envelope_registry = dict(runtime.get("budget_envelope_registry") or {})
    budget_policy_row = dict(runtime.get("budget_policy") or {})
    budget_envelope_id = str(runtime.get("budget_envelope_id", "")).strip()
    selected_budget_envelope = {}
    for row in sorted((item for item in list(budget_envelope_registry.get("envelopes") or []) if isinstance(item, dict)), key=lambda item: str(item.get("envelope_id", ""))):
        if str(row.get("envelope_id", "")).strip() == budget_envelope_id:
            selected_budget_envelope = dict(row)
            break
    normalized_budget_envelope = normalize_budget_envelope(
        envelope=selected_budget_envelope,
        budget_policy=budget_policy_row,
    )
    max_inspection_budget = max(0, _to_int(normalized_budget_envelope.get("max_inspection_cost_units_per_tick", 0), 0))
    reservation = reserve_inspection_budget(
        runtime_budget_state=dict(runtime.get("inspection_runtime_budget_state") or {}),
        tick=int(tick),
        requested_cost_units=int(requested_cost_units),
        max_cost_units_per_tick=int(max_inspection_budget),
    )
    if str(reservation.get("result", "")) != "complete":
        return _refusal(
            "refusal.preview.budget_exceeded",
            "preview budget exceeded for this tick",
            "Retry next tick, lower preview cost, or use a higher inspection budget envelope.",
            {
                "requested_cost_units": str(requested_cost_units),
                "max_inspection_cost_units_per_tick": str(max_inspection_budget),
            },
            "$.preview.cost_units",
        )
    runtime["inspection_runtime_budget_state"] = dict(reservation.get("runtime_budget_state") or {})

    cache_policy_registry = dict(runtime.get("inspection_cache_policy_registry") or {})
    cache_policy_id = str(runtime.get("inspection_cache_policy_id", "")).strip()
    selected_cache_policy = {}
    for row in sorted((item for item in list(cache_policy_registry.get("policies") or []) if isinstance(item, dict)), key=lambda item: str(item.get("cache_policy_id", ""))):
        if str(row.get("cache_policy_id", "")).strip() == cache_policy_id:
            selected_cache_policy = dict(row)
            break
    if not selected_cache_policy:
        selected_cache_policy = {
            "cache_policy_id": "cache.off",
            "enable_caching": False,
            "invalidation_rules": [],
            "max_cache_entries": 0,
            "eviction_rule_id": "evict.none",
            "extensions": {},
        }

    target_payload = _target_payload_from_perceived(perceived_model=perceived_model, target_semantic_id=target_semantic_id)
    snapshot = build_inspection_snapshot(
        target_id=target_semantic_id,
        tick=int(tick),
        physics_profile_id=str(runtime.get("physics_profile_id", "")),
        pack_lock_hash=str(runtime.get("pack_lock_hash", "")),
        truth_hash_anchor=str(truth_hash_anchor),
        policy_id=str(selected_cache_policy.get("cache_policy_id", "")),
        target_payload=target_payload,
    )
    cache_key = inspection_build_cache_key(
        target_id=target_semantic_id,
        truth_hash_anchor=str(truth_hash_anchor),
        policy_id=str(selected_cache_policy.get("cache_policy_id", "")),
        physics_profile_id=str(runtime.get("physics_profile_id", "")),
        pack_lock_hash=str(runtime.get("pack_lock_hash", "")),
    )
    cache_result = inspection_cache_lookup_or_store(
        cache_state=dict(runtime.get("inspection_cache_state") or {}),
        cache_policy=selected_cache_policy,
        cache_key=str(cache_key),
        snapshot=snapshot,
        tick=int(tick),
    )
    runtime["inspection_cache_state"] = dict(cache_result.get("cache_state") or {})

    payload = _base_preview(
        tick=tick,
        target_semantic_id=target_semantic_id,
        process_id=process_id,
        parameters=canonical_parameters,
        predicted_effects={
            "summary": "expensive preview generated from cached inspection snapshot",
            "inspection_snapshot_id": str((dict(cache_result.get("snapshot") or {})).get("snapshot_id", "")),
            "cache_hit": bool(cache_result.get("cache_hit", False)),
        },
    )
    payload["extensions"] = {
        "preview_capability": "expensive",
        "inspection_snapshot": dict(cache_result.get("snapshot") or {}),
        "cache_key": str(cache_result.get("cache_key", "")),
        "cache_hit": bool(cache_result.get("cache_hit", False)),
        "evicted_cache_keys": _sorted_unique_strings(list(cache_result.get("evicted_keys") or [])),
        "inspection_cost_units": int(requested_cost_units),
    }
    payload = _ranked_redact_preview(runtime=runtime, payload=payload)
    valid = _validate_preview(repo_root=repo_root, payload=payload)
    if str(valid.get("result", "")) != "complete":
        return valid
    return {
        "result": "complete",
        "preview": payload,
        "preview_hash": str(payload.get("preview_hash", "")),
        "preview_runtime": runtime,
    }
