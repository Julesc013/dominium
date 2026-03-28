"""STRICT test: representation rule selection uses deterministic tie-breaks."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.render.representation_rule_resolution_deterministic"
TEST_TAGS = ["strict", "render", "representation"]


def _registry_payloads() -> dict:
    return {
        "representation_rule_registry": {
            "representation_rules": [
                {
                    "rule_id": "rule.b",
                    "priority": 50,
                    "match": {
                        "entity_kind": None,
                        "material_tag": None,
                        "domain_id": None,
                        "faction_id": None,
                        "view_mode_id": None,
                        "body_shape": None,
                    },
                    "output": {
                        "primitive_id": "prim.box.default",
                        "procedural_material_template_id": "mat.template.default_by_id_hash",
                        "label_policy_id": "label.none",
                        "lod_policy_id": "lod.null",
                    },
                    "extensions": {},
                },
                {
                    "rule_id": "rule.a",
                    "priority": 50,
                    "match": {
                        "entity_kind": None,
                        "material_tag": None,
                        "domain_id": None,
                        "faction_id": None,
                        "view_mode_id": None,
                        "body_shape": None,
                    },
                    "output": {
                        "primitive_id": "prim.sphere.default",
                        "procedural_material_template_id": "mat.template.default_by_id_hash",
                        "label_policy_id": "label.none",
                        "lod_policy_id": "lod.null",
                    },
                    "extensions": {},
                },
            ]
        },
        "procedural_material_template_registry": {
            "material_templates": [
                {
                    "template_id": "mat.template.default_by_id_hash",
                    "base_color_rule": {"mode": "hash_of_id", "source": "semantic_id"},
                    "roughness_rule": {"mode": "fixed", "value": 650},
                    "metallic_rule": {"mode": "fixed", "value": 80},
                    "emission_rule": {"mode": "none"},
                    "extensions": {},
                }
            ]
        },
        "label_policy_registry": {
            "label_policies": [
                {"label_policy_id": "label.none", "show_label": False, "label_source": "none", "extensions": {}}
            ]
        },
        "lod_policy_registry": {
            "lod_policies": [
                {"lod_policy_id": "lod.null", "distance_bands_mm": [], "default_hint": "lod.band.near", "extensions": {}}
            ]
        },
    }


def _entity_row() -> dict:
    return {
        "entity_id": "agent.alpha",
        "entity_kind": "agent",
        "representation": {"shape_type": "aabb", "material_ref": "asset.material.stub"},
        "transform_mm": {"x": 0, "y": 0, "z": 0},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.render import resolve_representation

    payloads = _registry_payloads()
    first = resolve_representation(copy.deepcopy(_entity_row()), copy.deepcopy(payloads), view_mode_id="")
    second = resolve_representation(copy.deepcopy(_entity_row()), copy.deepcopy(payloads), view_mode_id="")
    if first != second:
        return {"status": "fail", "message": "representation resolver output drifted across identical calls"}
    if str(first.get("rule_id", "")) != "rule.a":
        return {"status": "fail", "message": "tie-break did not select lexicographically-first rule_id at equal priority"}
    return {"status": "pass", "message": "representation rule tie-break deterministic"}
