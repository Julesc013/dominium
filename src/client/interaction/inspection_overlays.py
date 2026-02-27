"""Derived inspection overlays for RenderModel overlay layers."""

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


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: list[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip())
)


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


def _overlay_materials(target_semantic_id: str) -> list[dict]:
    highlight_material_id = "mat.inspect.highlight.{}".format(canonical_sha256({"target": target_semantic_id})[:12])
    label_material_id = "mat.inspect.label.{}".format(canonical_sha256({"target": target_semantic_id, "label": True})[:12])
    return sorted(
        [
            {
                "schema_version": "1.0.0",
                "material_id": highlight_material_id,
                "base_color": {"r": 247, "g": 208, "b": 84},
                "roughness": 320,
                "metallic": 0,
                "emission": {"r": 247, "g": 208, "b": 84, "strength": 380},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "highlight"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": label_material_id,
                "base_color": {"r": 229, "g": 236, "b": 242},
                "roughness": 260,
                "metallic": 20,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "label"},
            },
        ],
        key=lambda row: str(row.get("material_id", "")),
    )


def _overlay_renderables(
    *,
    target_semantic_id: str,
    summary_label: str,
    mode: str,
) -> list[dict]:
    highlight_material_id = "mat.inspect.highlight.{}".format(canonical_sha256({"target": target_semantic_id})[:12])
    label_material_id = "mat.inspect.label.{}".format(canonical_sha256({"target": target_semantic_id, "label": True})[:12])
    rows = [
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.highlight.{}".format(canonical_sha256({"target": target_semantic_id})[:12]),
            "semantic_id": "overlay.inspect.highlight.{}".format(target_semantic_id),
            "primitive_id": "prim.line.debug",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "material_id": highlight_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": None,
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": True},
            "extensions": {
                "interaction_overlay": True,
                "target_semantic_id": target_semantic_id,
                "mode": mode,
            },
        },
        {
            "schema_version": "1.0.0",
            "renderable_id": "overlay.inspect.label.{}".format(canonical_sha256({"target": target_semantic_id, "label": True})[:12]),
            "semantic_id": "overlay.inspect.label.{}".format(target_semantic_id),
            "primitive_id": "prim.glyph.label",
            "transform": {
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "material_id": label_material_id,
            "layer_tags": ["overlay", "ui"],
            "label": str(summary_label),
            "lod_hint": "lod.band.near",
            "flags": {"selectable": False, "highlighted": False},
            "extensions": {
                "interaction_overlay": True,
                "target_semantic_id": target_semantic_id,
                "mode": mode,
            },
        },
    ]
    return sorted(rows, key=lambda row: str(row.get("renderable_id", "")))


def _blueprint_overlay_payload(
    *,
    target_semantic_id: str,
    runtime: dict,
) -> Dict[str, object]:
    repo_root = str(runtime.get("repo_root", "")).strip()
    blueprint_id = str(target_semantic_id).strip()
    blueprint_registry = _resolve_registry(runtime, "blueprint_registry", repo_root, "data/registries/blueprint_registry.json")
    part_class_registry = _resolve_registry(runtime, "part_class_registry", repo_root, "data/registries/part_class_registry.json")
    connection_type_registry = _resolve_registry(runtime, "connection_type_registry", repo_root, "data/registries/connection_type_registry.json")
    material_class_registry = _resolve_registry(runtime, "material_class_registry", repo_root, "data/registries/material_class_registry.json")
    if not blueprint_registry or not part_class_registry or not connection_type_registry:
        return {
            "mode": "macro_summary",
            "summary": "blueprint:{} unavailable".format(blueprint_id),
            "target_semantic_id": blueprint_id,
            "inspection_snapshot": {},
            "renderables": _overlay_renderables(
                target_semantic_id=blueprint_id,
                summary_label="blueprint unavailable",
                mode="macro_summary",
            ),
            "materials": _overlay_materials(target_semantic_id=blueprint_id),
            "degraded": True,
            "extensions": {"blueprint_id": blueprint_id, "compile_status": "registry_missing"},
        }

    try:
        compiled = compile_blueprint_artifacts(
            repo_root=repo_root or os.getcwd(),
            blueprint_id=blueprint_id,
            parameter_values={},
            pack_lock_hash=str(runtime.get("pack_lock_hash", "")).strip() or "pack_lock_hash.overlay",
            blueprint_registry=blueprint_registry,
            part_class_registry=part_class_registry,
            connection_type_registry=connection_type_registry,
            material_class_registry=material_class_registry,
        )
    except BlueprintCompileError as exc:
        return {
            "mode": "macro_summary",
            "summary": "blueprint:{} refused".format(blueprint_id),
            "target_semantic_id": blueprint_id,
            "inspection_snapshot": {},
            "renderables": _overlay_renderables(
                target_semantic_id=blueprint_id,
                summary_label="compile refused",
                mode="macro_summary",
            ),
            "materials": _overlay_materials(target_semantic_id=blueprint_id),
            "degraded": True,
            "extensions": {
                "blueprint_id": blueprint_id,
                "compile_status": "refused",
                "reason_code": str(exc.reason_code),
                "details": dict(exc.details),
            },
        }

    summary = blueprint_bom_summary(dict(compiled.get("compiled_bom_artifact") or {}))
    ghost = build_blueprint_ghost_overlay(
        compiled_ag_artifact=dict(compiled.get("compiled_ag_artifact") or {}),
        blueprint_id=blueprint_id,
        include_labels=bool(runtime.get("blueprint_preview_labels", True)),
    )
    return {
        "mode": "blueprint_preview",
        "summary": "blueprint:{} ghost".format(blueprint_id),
        "target_semantic_id": blueprint_id,
        "inspection_snapshot": {
            "summary_hash": str(summary.get("summary_hash", "")),
            "total_mass_raw": int(summary.get("total_mass_raw", 0) or 0),
            "total_part_count": int(summary.get("total_part_count", 0) or 0),
        },
        "renderables": list(ghost.get("renderables") or []),
        "materials": list(ghost.get("materials") or []),
        "degraded": False,
        "extensions": {
            "blueprint_id": blueprint_id,
            "cache_key": str(compiled.get("cache_key", "")),
            "bom_summary": summary,
            "compiled_bom_hash": str((dict(compiled.get("compiled_bom_artifact") or {})).get("artifact_hash", "")),
            "compiled_ag_hash": str((dict(compiled.get("compiled_ag_artifact") or {})).get("artifact_hash", "")),
        },
    }


def build_inspection_overlays(
    *,
    perceived_model: dict,
    target_semantic_id: str,
    authority_context: dict | None = None,
    inspection_snapshot: dict | None = None,
    overlay_runtime: dict | None = None,
    requested_cost_units: int = 1,
) -> Dict[str, object]:
    """Build deterministic inspection overlays with budgeted degrade path."""
    runtime = dict(overlay_runtime or {})
    perceived = dict(perceived_model or {})
    target_id = str(target_semantic_id).strip()
    tick = int(max(0, _to_int((dict(perceived.get("time_state") or {})).get("tick", 0), 0)))
    if target_id.startswith("blueprint."):
        blueprint_overlay = _blueprint_overlay_payload(
            target_semantic_id=target_id,
            runtime=runtime,
        )
        return {
            "result": "complete",
            "inspection_overlays": blueprint_overlay,
            "overlay_runtime": runtime,
        }

    entitlements = set(_sorted_unique_strings(list((dict(authority_context or {})).get("entitlements") or [])))
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
        requested_cost_units=max(1, int(max(0, _to_int(requested_cost_units, 1)))),
        max_cost_units_per_tick=int(max_inspection_budget),
    )
    degraded = str(reservation.get("result", "")) != "complete"
    if not degraded:
        runtime["inspection_runtime_budget_state"] = dict(reservation.get("runtime_budget_state") or {})

    summary_label = "inspect:{} macro-summary".format(target_id or "unknown")
    mode = "macro_summary" if degraded else "full"
    snapshot = dict(inspection_snapshot or {})
    if (not degraded) and (not snapshot):
        truth_overlay = dict(perceived.get("truth_overlay") or {})
        truth_hash_anchor = str(truth_overlay.get("state_hash_anchor", "")).strip()
        if truth_hash_anchor:
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
            generated_snapshot = build_inspection_snapshot(
                target_id=target_id,
                tick=int(tick),
                physics_profile_id=str(runtime.get("physics_profile_id", "")),
                pack_lock_hash=str(runtime.get("pack_lock_hash", "")),
                truth_hash_anchor=str(truth_hash_anchor),
                policy_id=str(selected_cache_policy.get("cache_policy_id", "")),
                target_payload=_target_payload_from_perceived(perceived_model=perceived, target_semantic_id=target_id),
            )
            cache_key = inspection_build_cache_key(
                target_id=target_id,
                truth_hash_anchor=str(truth_hash_anchor),
                policy_id=str(selected_cache_policy.get("cache_policy_id", "")),
                physics_profile_id=str(runtime.get("physics_profile_id", "")),
                pack_lock_hash=str(runtime.get("pack_lock_hash", "")),
            )
            cache_result = inspection_cache_lookup_or_store(
                cache_state=dict(runtime.get("inspection_cache_state") or {}),
                cache_policy=selected_cache_policy,
                cache_key=str(cache_key),
                snapshot=generated_snapshot,
                tick=int(tick),
            )
            runtime["inspection_cache_state"] = dict(cache_result.get("cache_state") or {})
            snapshot = dict(cache_result.get("snapshot") or {})

    if snapshot:
        payload = dict(snapshot.get("target_payload") or {})
        exists = bool(payload.get("exists", False))
        if exists and ("entitlement.inspect" in entitlements):
            summary_label = "inspect:{} detail".format(target_id or "unknown")
        elif exists:
            summary_label = "inspect:{} observed".format(target_id or "unknown")
        else:
            summary_label = "inspect:{} missing".format(target_id or "unknown")

    overlay_payload = {
        "mode": mode,
        "summary": summary_label,
        "target_semantic_id": target_id,
        "inspection_snapshot": dict(snapshot or {}),
        "renderables": _overlay_renderables(
            target_semantic_id=target_id,
            summary_label=summary_label,
            mode=mode,
        ),
        "materials": _overlay_materials(target_semantic_id=target_id),
        "degraded": bool(degraded),
    }
    return {
        "result": "complete",
        "inspection_overlays": overlay_payload,
        "overlay_runtime": runtime,
    }
