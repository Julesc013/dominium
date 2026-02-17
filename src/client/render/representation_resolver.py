"""Deterministic representation resolver for PerceivedModel -> RenderModel mapping."""

from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple


DEFAULT_PRIMITIVE_ID = "prim.box.default"
DEFAULT_TEMPLATE_ID = "mat.template.default_by_id_hash"
DEFAULT_LABEL_POLICY_ID = "label.none"
DEFAULT_LOD_POLICY_ID = "lod.null"
ALLOWED_LAYER_TAGS = ("world", "ui", "overlay", "debug")

_PALETTES = {
    "palette.wood": [(143, 98, 63), (115, 78, 49), (168, 120, 85)],
    "palette.metal": [(154, 164, 178), (129, 141, 156), (180, 190, 205)],
    "palette.stone": [(120, 120, 120), (98, 98, 104), (145, 140, 133)],
    "palette.water": [(56, 116, 168), (40, 92, 144), (72, 132, 184)],
}


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _hash_bytes(seed: str) -> bytes:
    return hashlib.sha256(str(seed).encode("utf-8")).digest()


def _hsv_to_rgb(h: int, s: int, v: int) -> Tuple[int, int, int]:
    hue = max(0, min(359, int(h)))
    sat = max(0, min(1000, int(s)))
    val = max(0, min(1000, int(v)))
    if sat == 0:
        gray = int((val * 255) // 1000)
        return gray, gray, gray

    region = hue // 60
    rem = hue % 60
    p = (val * (1000 - sat)) // 1000
    q = (val * (1000 - ((sat * rem) // 60))) // 1000
    t = (val * (1000 - ((sat * (60 - rem)) // 60))) // 1000

    if region == 0:
        r, g, b = val, t, p
    elif region == 1:
        r, g, b = q, val, p
    elif region == 2:
        r, g, b = p, val, t
    elif region == 3:
        r, g, b = p, q, val
    elif region == 4:
        r, g, b = t, p, val
    else:
        r, g, b = val, p, q
    return int((r * 255) // 1000), int((g * 255) // 1000), int((b * 255) // 1000)


def _hash_color(seed: str, saturation: int = 620, value: int = 760) -> Dict[str, int]:
    digest = _hash_bytes(seed)
    hue = int(digest[0]) * 360 // 256
    r, g, b = _hsv_to_rgb(h=hue, s=int(saturation), v=int(value))
    return {"r": int(r), "g": int(g), "b": int(b)}


def _first_tag_match(tags: List[str], allowed: Tuple[str, ...]) -> str:
    for token in tags:
        if token in allowed:
            return token
    return ""


def _default_rule_rows() -> List[dict]:
    return [
        {
            "rule_id": "rule.fallback.body_capsule",
            "match": {
                "entity_kind": None,
                "material_tag": None,
                "domain_id": None,
                "faction_id": None,
                "view_mode_id": None,
                "body_shape": "capsule",
            },
            "output": {
                "primitive_id": "prim.capsule.default",
                "procedural_material_template_id": DEFAULT_TEMPLATE_ID,
                "label_policy_id": DEFAULT_LABEL_POLICY_ID,
                "lod_policy_id": DEFAULT_LOD_POLICY_ID,
            },
            "priority": 100,
            "extensions": {},
        },
        {
            "rule_id": "rule.fallback.default",
            "match": {
                "entity_kind": None,
                "material_tag": None,
                "domain_id": None,
                "faction_id": None,
                "view_mode_id": None,
                "body_shape": None,
            },
            "output": {
                "primitive_id": DEFAULT_PRIMITIVE_ID,
                "procedural_material_template_id": DEFAULT_TEMPLATE_ID,
                "label_policy_id": DEFAULT_LABEL_POLICY_ID,
                "lod_policy_id": DEFAULT_LOD_POLICY_ID,
            },
            "priority": 0,
            "extensions": {},
        },
    ]


def _default_template_rows() -> List[dict]:
    return [
        {
            "template_id": DEFAULT_TEMPLATE_ID,
            "base_color_rule": {
                "mode": "hash_of_id",
                "source": "semantic_id",
            },
            "roughness_rule": {"mode": "fixed", "value": 650},
            "metallic_rule": {"mode": "fixed", "value": 80},
            "emission_rule": {"mode": "none"},
            "extensions": {},
        }
    ]


def _default_label_policy_rows() -> List[dict]:
    return [
        {
            "label_policy_id": "label.none",
            "show_label": False,
            "label_source": "none",
            "extensions": {},
        },
        {
            "label_policy_id": "label.debug_ids",
            "show_label": True,
            "label_source": "semantic_id",
            "extensions": {},
        },
    ]


def _default_lod_policy_rows() -> List[dict]:
    return [
        {
            "lod_policy_id": "lod.null",
            "distance_bands_mm": [],
            "default_hint": "lod.band.near",
            "extensions": {"hints": ["lod.band.near"]},
        }
    ]


def _normalize_layer_tags(entity_row: dict, faction_id: str | None) -> List[str]:
    tags = _sorted_unique_strings(entity_row.get("layer_tags") or [])
    filtered = [token for token in tags if token in ALLOWED_LAYER_TAGS]
    if not filtered:
        filtered = ["world"]
    if faction_id and "overlay" not in filtered:
        filtered.append("overlay")
    if "world" in filtered:
        return ["world"] + [token for token in sorted(set(filtered)) if token != "world"]
    return sorted(set(filtered))


def _rule_rows(registry_payloads: Dict[str, dict]) -> List[dict]:
    payload = dict((registry_payloads or {}).get("representation_rule_registry") or {})
    rows = payload.get("representation_rules")
    if not isinstance(rows, list):
        rows = _default_rule_rows()
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "rule_id": str(row.get("rule_id", "")).strip(),
                "match": dict(row.get("match") or {}),
                "output": dict(row.get("output") or {}),
                "priority": _to_int(row.get("priority", 0), 0),
                "extensions": dict(row.get("extensions") or {}),
            }
        )
    if not normalized:
        normalized = _default_rule_rows()
    return sorted(
        normalized,
        key=lambda row: (int(row.get("priority", 0) or 0) * -1, str(row.get("rule_id", ""))),
    )


def _template_rows(registry_payloads: Dict[str, dict]) -> List[dict]:
    payload = dict((registry_payloads or {}).get("procedural_material_template_registry") or {})
    rows = payload.get("material_templates")
    if not isinstance(rows, list):
        rows = _default_template_rows()
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "template_id": str(row.get("template_id", "")).strip(),
                "base_color_rule": dict(row.get("base_color_rule") or {}),
                "roughness_rule": dict(row.get("roughness_rule") or {}),
                "metallic_rule": dict(row.get("metallic_rule") or {}),
                "emission_rule": dict(row.get("emission_rule") or {}),
                "extensions": dict(row.get("extensions") or {}),
            }
        )
    if not normalized:
        normalized = _default_template_rows()
    return sorted(normalized, key=lambda row: str(row.get("template_id", "")))


def _label_policy_rows(registry_payloads: Dict[str, dict]) -> List[dict]:
    payload = dict((registry_payloads or {}).get("label_policy_registry") or {})
    rows = payload.get("label_policies")
    if not isinstance(rows, list):
        rows = _default_label_policy_rows()
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "label_policy_id": str(row.get("label_policy_id", "")).strip(),
                "show_label": bool(row.get("show_label", False)),
                "label_source": str(row.get("label_source", "none")).strip() or "none",
                "extensions": dict(row.get("extensions") or {}),
            }
        )
    if not normalized:
        normalized = _default_label_policy_rows()
    return sorted(normalized, key=lambda row: str(row.get("label_policy_id", "")))


def _lod_policy_rows(registry_payloads: Dict[str, dict]) -> List[dict]:
    payload = dict((registry_payloads or {}).get("lod_policy_registry") or {})
    rows = payload.get("lod_policies")
    if not isinstance(rows, list):
        rows = _default_lod_policy_rows()
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        bands = sorted(set(_to_int(item, 0) for item in (row.get("distance_bands_mm") or [])))
        normalized.append(
            {
                "lod_policy_id": str(row.get("lod_policy_id", "")).strip(),
                "distance_bands_mm": [int(item) for item in bands if int(item) >= 0],
                "default_hint": str(row.get("default_hint", "lod.band.near")).strip() or "lod.band.near",
                "extensions": dict(row.get("extensions") or {}),
            }
        )
    if not normalized:
        normalized = _default_lod_policy_rows()
    return sorted(normalized, key=lambda row: str(row.get("lod_policy_id", "")))


def _normalize_candidate(entity_row: dict, view_mode_id: str) -> dict:
    row = dict(entity_row or {})
    representation = dict(row.get("representation") or {})
    semantic_id = str(row.get("semantic_id", "")).strip() or str(row.get("entity_id", "")).strip()
    material_ref = str(representation.get("material_ref", "")).strip().lower()
    explicit_tags = _sorted_unique_strings(row.get("material_tags") or [])
    parsed_tags = []
    for token in ("wood", "metal", "stone", "water"):
        if token in material_ref:
            parsed_tags.append(token)
    material_tags = _sorted_unique_strings(explicit_tags + parsed_tags)
    body_shape = str(representation.get("shape_type", "")).strip().lower() or "none"
    entity_kind = str(row.get("entity_kind", "")).strip() or ("camera" if semantic_id.startswith("camera.") else "agent")
    faction_id = str(row.get("faction_id", "")).strip() or None
    return {
        "semantic_id": semantic_id,
        "entity_kind": entity_kind,
        "material_tags": material_tags,
        "domain_id": str(row.get("domain_id", "")).strip() or None,
        "faction_id": faction_id,
        "view_mode_id": str(view_mode_id).strip() or None,
        "body_shape": body_shape,
        "layer_tags": _normalize_layer_tags(row, faction_id),
    }


def _rule_matches(rule: dict, candidate: dict) -> bool:
    match_row = dict(rule.get("match") or {})
    for key in ("entity_kind", "domain_id", "faction_id", "view_mode_id", "body_shape"):
        expected = match_row.get(key)
        if expected is None:
            continue
        token = str(expected).strip()
        if not token:
            continue
        if str(candidate.get(key, "")).strip() != token:
            return False
    expected_material_tag = match_row.get("material_tag")
    if expected_material_tag is not None:
        token = str(expected_material_tag).strip()
        if token and token not in set(candidate.get("material_tags") or []):
            return False
    return True


def _select_rule(candidate: dict, registry_payloads: Dict[str, dict]) -> dict:
    for row in _rule_rows(registry_payloads):
        if not _rule_matches(row, candidate):
            continue
        return dict(row)
    fallback = _default_rule_rows()
    return dict(fallback[-1])


def _material_from_template(
    candidate: dict,
    template_id: str,
    registry_payloads: Dict[str, dict],
) -> dict:
    templates = _template_rows(registry_payloads)
    template_map = dict((str(row.get("template_id", "")), dict(row)) for row in templates)
    template = dict(
        template_map.get(
            str(template_id),
            template_map.get(DEFAULT_TEMPLATE_ID, _default_template_rows()[0]),
        )
    )
    semantic_id = str(candidate.get("semantic_id", "")).strip() or "semantic.unknown"
    source_token = str(candidate.get("faction_id", "")).strip() or semantic_id

    base_color_rule = dict(template.get("base_color_rule") or {})
    base_color_mode = str(base_color_rule.get("mode", "hash_of_id")).strip()
    if base_color_mode == "fixed":
        fixed = dict(base_color_rule.get("value") or {})
        base_color = {
            "r": max(0, min(255, _to_int(fixed.get("r", 180), 180))),
            "g": max(0, min(255, _to_int(fixed.get("g", 180), 180))),
            "b": max(0, min(255, _to_int(fixed.get("b", 180), 180))),
        }
    elif base_color_mode == "palette":
        palette_id = str(base_color_rule.get("palette_id", "palette.stone")).strip()
        palette = list(_PALETTES.get(palette_id) or _PALETTES["palette.stone"])
        digest = _hash_bytes(source_token)
        index = int(digest[1]) % max(1, len(palette))
        rgb = palette[index]
        base_color = {"r": int(rgb[0]), "g": int(rgb[1]), "b": int(rgb[2])}
    else:
        base_color = _hash_color(seed=source_token)

    def _resolve_scalar(rule: dict, default_value: int) -> int:
        mode = str((rule or {}).get("mode", "fixed")).strip()
        if mode == "hash_band":
            minimum = max(0, min(1000, _to_int((rule or {}).get("min", 0), 0)))
            maximum = max(minimum, min(1000, _to_int((rule or {}).get("max", 1000), 1000)))
            digest = _hash_bytes(source_token)
            span = int(maximum - minimum)
            if span <= 0:
                return int(minimum)
            return int(minimum + (int(digest[2]) * span // 255))
        return max(0, min(1000, _to_int((rule or {}).get("value", default_value), default_value)))

    roughness = _resolve_scalar(dict(template.get("roughness_rule") or {}), 650)
    metallic = _resolve_scalar(dict(template.get("metallic_rule") or {}), 80)

    emission_rule = dict(template.get("emission_rule") or {})
    emission_mode = str(emission_rule.get("mode", "none")).strip()
    emission = None
    if emission_mode == "fixed":
        emission = {
            "r": max(0, min(255, _to_int(emission_rule.get("r", 0), 0))),
            "g": max(0, min(255, _to_int(emission_rule.get("g", 0), 0))),
            "b": max(0, min(255, _to_int(emission_rule.get("b", 0), 0))),
            "strength": max(0, min(1000, _to_int(emission_rule.get("strength", 0), 0))),
        }
    elif emission_mode == "hash_band":
        color = _hash_color(seed="emission.{}".format(source_token), saturation=700, value=850)
        emission = {
            "r": int(color["r"]),
            "g": int(color["g"]),
            "b": int(color["b"]),
            "strength": max(0, min(1000, _to_int(emission_rule.get("max_strength", 200), 200))),
        }

    return {
        "schema_version": "1.0.0",
        "material_id": "mat.resolved.{}".format(semantic_id),
        "base_color": base_color,
        "roughness": roughness,
        "metallic": metallic,
        "emission": emission,
        "transparency": None,
        "pattern_id": None,
        "extensions": {
            "template_id": str(template.get("template_id", DEFAULT_TEMPLATE_ID)),
        },
    }


def _label_from_policy(candidate: dict, label_policy_id: str, registry_payloads: Dict[str, dict]) -> str | None:
    policies = _label_policy_rows(registry_payloads)
    policy_map = dict((str(row.get("label_policy_id", "")), dict(row)) for row in policies)
    policy = dict(
        policy_map.get(
            str(label_policy_id),
            policy_map.get(DEFAULT_LABEL_POLICY_ID, _default_label_policy_rows()[0]),
        )
    )
    if not bool(policy.get("show_label", False)):
        return None
    source = str(policy.get("label_source", "none")).strip()
    if source == "semantic_id":
        return str(candidate.get("semantic_id", "")).strip() or None
    if source == "entity_id":
        return str(candidate.get("semantic_id", "")).strip() or None
    if source == "faction_tag":
        return str(candidate.get("faction_id", "")).strip() or None
    if source == "custom":
        semantic_id = str(candidate.get("semantic_id", "")).strip()
        if not semantic_id:
            return None
        return semantic_id.split(".")[-1]
    return None


def _lod_hint_for_candidate(candidate: dict, lod_policy_id: str, registry_payloads: Dict[str, dict], entity_row: dict) -> str:
    policies = _lod_policy_rows(registry_payloads)
    policy_map = dict((str(row.get("lod_policy_id", "")), dict(row)) for row in policies)
    policy = dict(
        policy_map.get(
            str(lod_policy_id),
            policy_map.get(DEFAULT_LOD_POLICY_ID, _default_lod_policy_rows()[0]),
        )
    )
    default_hint = str(policy.get("default_hint", "lod.band.near")).strip() or "lod.band.near"
    bands = [int(value) for value in list(policy.get("distance_bands_mm") or []) if _to_int(value, -1) >= 0]
    if not bands:
        return default_hint
    transform = dict(entity_row.get("transform_mm") or {})
    distance_mm = abs(_to_int(transform.get("x", 0), 0)) + abs(_to_int(transform.get("y", 0), 0)) + abs(_to_int(transform.get("z", 0), 0))
    hints = _sorted_unique_strings((dict(policy.get("extensions") or {}).get("hints") or []))
    if not hints:
        hints = ["lod.band.near", "lod.band.mid", "lod.band.far", "lod.band.extreme"]
    band_index = len(bands)
    for idx, threshold in enumerate(sorted(bands)):
        if int(distance_mm) <= int(threshold):
            band_index = idx
            break
    if band_index >= len(hints):
        return hints[-1]
    return hints[band_index]


def resolve_representation(entity_row: dict, registry_payloads: Dict[str, dict] | None, view_mode_id: str) -> dict:
    """Resolve primitive/material/label/lod deterministically for one perceived semantic record."""
    payloads = dict(registry_payloads or {})
    candidate = _normalize_candidate(entity_row=entity_row, view_mode_id=view_mode_id)
    rule = _select_rule(candidate=candidate, registry_payloads=payloads)
    output_row = dict(rule.get("output") or {})

    primitive_id = str(output_row.get("primitive_id", DEFAULT_PRIMITIVE_ID)).strip() or DEFAULT_PRIMITIVE_ID
    template_id = str(output_row.get("procedural_material_template_id", DEFAULT_TEMPLATE_ID)).strip() or DEFAULT_TEMPLATE_ID
    label_policy_id = str(output_row.get("label_policy_id", DEFAULT_LABEL_POLICY_ID)).strip() or DEFAULT_LABEL_POLICY_ID
    lod_policy_id = str(output_row.get("lod_policy_id", DEFAULT_LOD_POLICY_ID)).strip() or DEFAULT_LOD_POLICY_ID

    material = _material_from_template(candidate=candidate, template_id=template_id, registry_payloads=payloads)
    label = _label_from_policy(candidate=candidate, label_policy_id=label_policy_id, registry_payloads=payloads)
    lod_hint = _lod_hint_for_candidate(
        candidate=candidate,
        lod_policy_id=lod_policy_id,
        registry_payloads=payloads,
        entity_row=dict(entity_row or {}),
    )
    return {
        "rule_id": str(rule.get("rule_id", "")).strip(),
        "primitive_id": primitive_id,
        "material": material,
        "label_policy_id": label_policy_id,
        "label": label,
        "lod_policy_id": lod_policy_id,
        "lod_hint": lod_hint,
        "layer_tags": list(candidate.get("layer_tags") or ["world"]),
    }
