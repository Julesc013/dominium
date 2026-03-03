"""FAST test: ELEC-0 baseline registry files exist and parse as objects."""

from __future__ import annotations

import json
import os


TEST_ID = "test_elec0_registry_presence"
TEST_TAGS = ["fast", "elec", "registry"]


_REQUIRED_REGISTRIES = (
    "data/registries/elec_node_kind_registry.json",
    "data/registries/elec_edge_kind_registry.json",
    "data/registries/elec_model_registry.json",
    "data/registries/elec_spec_templates.json",
)


def run(repo_root: str):
    for rel_path in _REQUIRED_REGISTRIES:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {"status": "fail", "message": "missing ELEC-0 registry: {}".format(rel_path)}
        try:
            payload = json.load(open(abs_path, "r", encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return {"status": "fail", "message": "invalid JSON in {}: {}".format(rel_path, exc)}
        if not isinstance(payload, dict):
            return {"status": "fail", "message": "registry root must be object: {}".format(rel_path)}
        if str(payload.get("schema_id", "")).strip() == "":
            return {"status": "fail", "message": "schema_id missing in {}".format(rel_path)}
    return {"status": "pass", "message": "ELEC-0 registries present"}

