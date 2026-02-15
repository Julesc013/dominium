"""STRICT test: worldgen search plan validates and round-trips canonically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.worldgen.search_plan_schema_roundtrip"
TEST_TAGS = ["strict", "worldgen", "schema", "determinism"]


def _load_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
    from tools.xstack.compatx.validator import validate_instance
    from worldgen.core.constraint_solver import solve_constraints

    module_registry = _load_json(os.path.join(repo_root, "data", "registries", "worldgen_module_registry.json"))
    constraints_payload = _load_json(
        os.path.join(
            repo_root,
            "packs",
            "core",
            "constraints.worldgen.default_lab",
            "data",
            "constraints.lab.navigation.default.json",
        )
    )

    solved = solve_constraints(
        repo_root=repo_root,
        constraints_payload=constraints_payload,
        module_registry_payload=module_registry,
        base_seed="seed.worldgen.roundtrip.001",
    )
    if solved.get("result") != "complete":
        return {"status": "fail", "message": "solve_constraints failed for roundtrip test"}
    search_plan = dict(solved.get("search_plan") or {})

    validated = validate_instance(
        repo_root=repo_root,
        schema_name="worldgen_search_plan",
        payload=search_plan,
        strict_top_level=True,
    )
    if not bool(validated.get("valid", False)):
        return {"status": "fail", "message": "worldgen search plan schema validation failed"}

    first_hash = canonical_sha256(dict(search_plan, deterministic_hash=""))
    canonical_text = canonical_json_text(search_plan)
    reloaded = json.loads(canonical_text)
    second_hash = canonical_sha256(dict(reloaded, deterministic_hash=""))
    if first_hash != second_hash:
        return {"status": "fail", "message": "canonical roundtrip hash drift detected"}
    if str(search_plan.get("deterministic_hash", "")) != first_hash:
        return {"status": "fail", "message": "deterministic_hash does not match canonical pre-hash payload"}

    return {"status": "pass", "message": "worldgen search plan schema roundtrip passed"}
