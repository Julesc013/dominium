"""Deterministic PerceivedModel -> RenderModel adapter."""

from __future__ import annotations

from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from .representation_resolver import resolve_representation


_ALLOWED_LAYER_TAGS = {"world", "ui", "overlay", "debug"}


def _hash64(value: str, fallback_seed: str) -> str:
    token = str(value or "").strip()
    if len(token) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in token):
        return token.lower()
    return canonical_sha256({"seed": str(fallback_seed), "value": token})


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _stable_semantic_id(row: dict) -> str:
    token = str(row.get("semantic_id", "")).strip() or str(row.get("entity_id", "")).strip()
    return token or "entity.unknown"


def _stable_renderable_id(semantic_id: str) -> str:
    token = str(semantic_id).strip() or "entity.unknown"
    digest = canonical_sha256({"semantic_id": token})
    return "renderable.{}.{}".format(token, str(digest)[:16])


def _normalize_transform(row: dict) -> dict:
    transform = dict(row.get("transform") or {})
    if transform:
        position = dict(transform.get("position_mm") or {})
        orientation = dict(transform.get("orientation_mdeg") or {})
        scale_permille = _to_int(transform.get("scale_permille", 1000), 1000)
    else:
        position = dict(row.get("transform_mm") or {})
        orientation = dict(row.get("orientation_mdeg") or {})
        scale_permille = _to_int(row.get("scale_permille", 1000), 1000)
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
        "scale_permille": max(1, _to_int(scale_permille, 1000)),
    }


def _normalize_layers(layer_tags: List[object]) -> List[str]:
    tags = sorted(set(str(item).strip() for item in (layer_tags or []) if str(item).strip()))
    filtered = [tag for tag in tags if tag in _ALLOWED_LAYER_TAGS]
    if not filtered:
        return ["world"]
    if "world" in filtered:
        return ["world"] + [tag for tag in filtered if tag != "world"]
    return filtered


def _entity_rows(perceived_model: dict) -> List[dict]:
    entities = dict(perceived_model.get("entities") or {})
    entries = list(entities.get("entries") or [])
    rows = [dict(item) for item in entries if isinstance(item, dict)]
    if rows:
        return sorted(rows, key=lambda row: _stable_semantic_id(row))
    observed = sorted(set(str(item).strip() for item in (perceived_model.get("observed_entities") or []) if str(item).strip()))
    return [{"entity_id": token} for token in observed]


def _view_mode_allows_diegetic_overlays(view_mode_id: str) -> bool:
    token = str(view_mode_id).strip()
    if token in ("view.first_person.player", "view.third_person.player", "view.follow.spectator"):
        return True
    return False


def _overlay_rows(perceived_model: dict, view_mode_id: str) -> Tuple[List[dict], List[dict]]:
    overlays: List[dict] = []
    materials: List[dict] = []
    if not _view_mode_allows_diegetic_overlays(view_mode_id):
        return overlays, materials
    instruments = dict(perceived_model.get("diegetic_instruments") or {})

    def add_overlay(overlay_id: str, label: str) -> None:
        material_id = "mat.overlay.{}".format(overlay_id)
        semantic_id = "overlay.{}".format(overlay_id)
        overlays.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": _stable_renderable_id(semantic_id),
                "semantic_id": semantic_id,
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": material_id,
                "layer_tags": ["ui", "overlay"],
                "label": str(label),
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {"view_mode_id": str(view_mode_id)},
            }
        )
        materials.append(
            {
                "schema_version": "1.0.0",
                "material_id": material_id,
                "base_color": {"r": 232, "g": 232, "b": 232},
                "roughness": 300,
                "metallic": 0,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"instrument_overlay": True},
            }
        )

    compass = dict(instruments.get("instrument.compass") or {})
    heading = compass.get("heading_deg")
    if heading is not None:
        add_overlay("instrument.compass", "Compass {}".format(_to_int(heading, 0)))

    clock = dict(instruments.get("instrument.clock") or {})
    tick = clock.get("tick")
    if tick is not None:
        add_overlay("instrument.clock", "Tick {}".format(_to_int(tick, 0)))

    map_local = dict(instruments.get("instrument.map_local") or {})
    discovered = map_local.get("discovered")
    if discovered is not None:
        add_overlay("instrument.map_local", "Map {}".format(_to_int(discovered, 0)))

    notebook = dict(instruments.get("instrument.notebook") or {})
    note_count = notebook.get("entry_count")
    if note_count is not None:
        add_overlay("instrument.notebook", "Notes {}".format(_to_int(note_count, 0)))

    radio = dict(instruments.get("instrument.radio_text") or {})
    pending = radio.get("pending_count")
    if pending is not None:
        add_overlay("instrument.radio_text", "Radio {}".format(_to_int(pending, 0)))

    overlays = sorted(
        overlays,
        key=lambda row: (str(row.get("semantic_id", "")), ",".join(list(row.get("layer_tags") or []))),
    )
    materials = sorted(materials, key=lambda row: str(row.get("material_id", "")))
    return overlays, materials


def build_render_model(
    perceived_model: dict,
    registry_payloads: Dict[str, dict] | None = None,
    pack_lock_hash: str = "",
    physics_profile_id: str = "",
) -> Dict[str, object]:
    """Build schema-versioned RenderModel strictly from PerceivedModel."""
    payloads = dict(registry_payloads or {})
    perceived = dict(perceived_model or {})
    perceived_hash = canonical_sha256(perceived)
    viewpoint_id = str(perceived.get("viewpoint_id", "")).strip() or "viewpoint.unknown"
    view_mode_id = str((dict(perceived.get("camera_viewpoint") or {})).get("view_mode_id", "")).strip()
    time_state = dict(perceived.get("time_state") or {})
    tick = max(0, _to_int(time_state.get("tick", 0), 0))

    materials_by_id: Dict[str, dict] = {}
    renderables: List[dict] = []
    for row in _entity_rows(perceived):
        semantic_id = _stable_semantic_id(row)
        resolved = resolve_representation(
            entity_row=dict(row),
            registry_payloads=payloads,
            view_mode_id=view_mode_id,
        )
        material = dict(resolved.get("material") or {})
        material_id = str(material.get("material_id", "")).strip() or "mat.resolved.{}".format(semantic_id)
        material["material_id"] = material_id
        materials_by_id[material_id] = material
        layer_tags = _normalize_layers(list(resolved.get("layer_tags") or ["world"]))
        renderables.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": _stable_renderable_id(semantic_id),
                "semantic_id": semantic_id,
                "primitive_id": str(resolved.get("primitive_id", "")).strip() or "prim.box.default",
                "transform": _normalize_transform(row),
                "material_id": material_id,
                "layer_tags": layer_tags,
                "label": resolved.get("label"),
                "lod_hint": str(resolved.get("lod_hint", "")).strip() or None,
                "flags": {
                    "selectable": bool(dict(row.get("flags") or {}).get("selectable", True)),
                    "highlighted": bool(dict(row.get("flags") or {}).get("highlighted", False)),
                },
                "extensions": {
                    "rule_id": str(resolved.get("rule_id", "")).strip(),
                    "label_policy_id": str(resolved.get("label_policy_id", "")).strip(),
                    "lod_policy_id": str(resolved.get("lod_policy_id", "")).strip(),
                },
            }
        )

    overlays, overlay_materials = _overlay_rows(perceived_model=perceived, view_mode_id=view_mode_id)
    for row in overlay_materials:
        materials_by_id[str(row.get("material_id", ""))] = dict(row)

    renderables = sorted(
        renderables,
        key=lambda row: (str(row.get("semantic_id", "")), ",".join(list(row.get("layer_tags") or []))),
    )
    materials = sorted(materials_by_id.values(), key=lambda row: str(row.get("material_id", "")))
    pack_hash = _hash64(pack_lock_hash, "pack_lock_hash")
    physics_profile = str(physics_profile_id).strip() or "physics.null"

    render_model = {
        "schema_version": "1.0.0",
        "render_model_id": "render_model.{}.tick.{}".format(viewpoint_id, tick),
        "tick": tick,
        "viewpoint_id": viewpoint_id,
        "pack_lock_hash": pack_hash,
        "physics_profile_id": physics_profile,
        "perceived_hash": perceived_hash,
        "renderables": renderables,
        "overlays": overlays,
        "render_model_hash": "",
        "extensions": {
            "lens_id": str(perceived.get("lens_id", "")),
            "view_mode_id": view_mode_id,
            "materials": materials,
            "camera_viewpoint": dict(perceived.get("camera_viewpoint") or {}),
        },
    }
    render_hash = canonical_sha256(dict(render_model))
    render_model["render_model_hash"] = render_hash
    return {
        "result": "complete",
        "render_model": render_model,
        "render_model_hash": render_hash,
    }
