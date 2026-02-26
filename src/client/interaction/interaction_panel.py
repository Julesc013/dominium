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
                "disabled_reason": ",".join(_sorted_unique_strings(list(extensions.get("missing_entitlements") or []))),
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


def build_selection_overlay(target_semantic_id: str) -> dict:
    token = str(target_semantic_id).strip()
    highlight_material_id = "mat.select.highlight.{}".format(canonical_sha256({"target": token})[:12])
    label_material_id = "mat.select.label.{}".format(canonical_sha256({"target": token, "label": True})[:12])
    return {
        "mode": "selection",
        "summary": "selected {}".format(token or "unknown"),
        "target_semantic_id": token,
        "degraded": False,
        "inspection_snapshot": {},
        "materials": [
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
        ],
        "renderables": [
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
        ],
    }

