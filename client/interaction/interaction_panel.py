"""Deterministic asset-free interaction panel payloads for TUI/CLI/workspace shells."""

from __future__ import annotations

from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _hash_color(seed: str) -> dict:
    digest = canonical_sha256({"seed": str(seed)})
    return {
        "r": int(int(digest[0:2], 16)),
        "g": int(int(digest[2:4], 16)),
        "b": int(int(digest[4:6], 16)),
    }


def _panel_slot_id(target_semantic_id: str, affordance_id: str) -> str:
    return "slot.{}".format(canonical_sha256({"target": target_semantic_id, "affordance_id": affordance_id})[:12])


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _normalize_surface_transform(row: dict) -> dict:
    payload = dict(row or {})
    transform = dict(payload.get("local_transform") or {})
    position = dict(transform.get("position_mm") or {})
    orientation = dict(transform.get("orientation_mdeg") or {})
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
        "scale_permille": max(1, _to_int(transform.get("scale_permille", 300), 300)),
    }


def build_interaction_panel(
    *,
    affordance_list: dict,
    selected_affordance_id: str = "",
) -> Dict[str, object]:
    payload = dict(affordance_list or {})
    target_semantic_id = str(payload.get("target_semantic_id", "")).strip()
    rows = []
    for row in sorted((item for item in list(payload.get("affordances") or []) if isinstance(item, dict)), key=lambda item: (str(item.get("display_name", "")).lower(), str(item.get("affordance_id", "")))):
        affordance_id = str(row.get("affordance_id", "")).strip()
        if not affordance_id:
            continue
        process_id = str(row.get("process_id", "")).strip()
        display_name = str(row.get("display_name", "")).strip() or process_id
        extensions = dict(row.get("extensions") or {})
        ui_hints = dict(extensions.get("default_ui_hints") or {})
        enabled = bool(extensions.get("enabled", False))
        disabled_reason = str(extensions.get("disabled_reason_code", "")).strip()
        if not disabled_reason:
            disabled_reason = ",".join(_sorted_unique_strings(list(extensions.get("missing_entitlements") or [])))
        rows.append(
            {
                "slot_id": _panel_slot_id(target_semantic_id=target_semantic_id, affordance_id=affordance_id),
                "affordance_id": affordance_id,
                "display_name": display_name,
                "process_id": process_id,
                "enabled": bool(enabled),
                "selected": affordance_id == str(selected_affordance_id).strip(),
                "glyph_id": str(ui_hints.get("icon", "glyph.action")).strip() or "glyph.action",
                "group": str(ui_hints.get("group", "general")).strip() or "general",
                "color_rgb": _hash_color(process_id or affordance_id),
                "disabled_reason": disabled_reason,
            }
        )
    rows = sorted(rows, key=lambda row: (str(row.get("display_name", "")).lower(), str(row.get("affordance_id", ""))))
    panel_payload = {
        "panel_id": "panel.interaction.{}".format(canonical_sha256({"target": target_semantic_id})[:12]),
        "target_semantic_id": target_semantic_id,
        "rows": rows,
        "row_count": len(rows),
        "enabled_count": len([row for row in rows if bool(row.get("enabled", False))]),
        "selected_affordance_id": str(selected_affordance_id or "").strip(),
    }
    panel_payload["panel_hash"] = canonical_sha256(panel_payload)
    return panel_payload


def build_selection_overlay(target_semantic_id: str, action_surfaces: list[dict] | None = None) -> dict:
    token = str(target_semantic_id).strip()
    highlight_material_id = "mat.select.highlight.{}".format(canonical_sha256({"target": token})[:12])
    label_material_id = "mat.select.label.{}".format(canonical_sha256({"target": token, "label": True})[:12])
    surfaces = [
        dict(item)
        for item in list(action_surfaces or [])
        if isinstance(item, dict) and str(item.get("surface_id", "")).strip()
    ]
    surface_rows = sorted(surfaces, key=lambda row: str(row.get("surface_id", "")))
    surface_material_rows = []
    surface_renderable_rows = []
    for surface_row in surface_rows:
        surface_id = str(surface_row.get("surface_id", "")).strip()
        surface_type_id = str(surface_row.get("surface_type_id", "")).strip() or "surface.unknown"
        material_id = "mat.select.surface.{}".format(canonical_sha256({"surface_id": surface_id})[:12])
        color = _hash_color(surface_type_id)
        surface_material_rows.append(
            {
                "schema_version": "1.0.0",
                "material_id": material_id,
                "base_color": {"r": color["r"], "g": color["g"], "b": color["b"]},
                "roughness": 260,
                "metallic": 0,
                "emission": {"r": color["r"], "g": color["g"], "b": color["b"], "strength": 120},
                "transparency": None,
                "pattern_id": None,
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "action_surface_marker",
                    "surface_id": surface_id,
                    "surface_type_id": surface_type_id,
                },
            }
        )
        surface_renderable_rows.append(
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.select.surface.{}".format(canonical_sha256({"surface_id": surface_id})[:12]),
                "semantic_id": "overlay.select.surface.{}.{}".format(token, surface_id),
                "primitive_id": "prim.glyph.label",
                "transform": _normalize_surface_transform(surface_row),
                "material_id": material_id,
                "layer_tags": ["overlay", "ui"],
                "label": surface_type_id,
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": bool(surface_row.get("tool_compatible", True))},
                "extensions": {
                    "interaction_overlay": True,
                    "overlay_kind": "action_surface_marker",
                    "target_semantic_id": token,
                    "surface_id": surface_id,
                    "surface_type_id": surface_type_id,
                    "tool_compatible": bool(surface_row.get("tool_compatible", True)),
                },
            }
        )
    return {
        "mode": "selection",
        "summary": "selected {}".format(token or "unknown"),
        "target_semantic_id": token,
        "degraded": False,
        "inspection_snapshot": {},
        "materials": sorted(
            [
            {
                "schema_version": "1.0.0",
                "material_id": highlight_material_id,
                "base_color": {"r": 86, "g": 178, "b": 255},
                "roughness": 300,
                "metallic": 0,
                "emission": {"r": 86, "g": 178, "b": 255, "strength": 220},
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "selection"},
            },
            {
                "schema_version": "1.0.0",
                "material_id": label_material_id,
                "base_color": {"r": 232, "g": 236, "b": 241},
                "roughness": 260,
                "metallic": 10,
                "emission": None,
                "transparency": None,
                "pattern_id": None,
                "extensions": {"interaction_overlay": True, "overlay_kind": "selection_label"},
            },
        ]
            + list(surface_material_rows),
            key=lambda row: str(row.get("material_id", "")),
        ),
        "renderables": sorted(
            [
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.select.highlight.{}".format(canonical_sha256({"target": token})[:12]),
                "semantic_id": "overlay.select.highlight.{}".format(token),
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
                "extensions": {"interaction_overlay": True, "target_semantic_id": token},
            },
            {
                "schema_version": "1.0.0",
                "renderable_id": "overlay.select.label.{}".format(canonical_sha256({"target": token, "label": True})[:12]),
                "semantic_id": "overlay.select.label.{}".format(token),
                "primitive_id": "prim.glyph.label",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": label_material_id,
                "layer_tags": ["overlay", "ui"],
                "label": token,
                "lod_hint": "lod.band.near",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {"interaction_overlay": True, "target_semantic_id": token},
            },
        ]
            + list(surface_renderable_rows),
            key=lambda row: str(row.get("renderable_id", "")),
        ),
        "action_surfaces": surface_rows,
    }
