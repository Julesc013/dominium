"""STRICT test: unsatisfiable constraints refuse deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.worldgen.unsatisfiable_constraints_refusal"
TEST_TAGS = ["strict", "worldgen", "determinism"]


def _load_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from worldgen.core.constraint_solver import solve_constraints

    module_registry = _load_json(os.path.join(repo_root, "data", "registries", "worldgen_module_registry.json"))
    payload = {
        "schema_version": "1.0.0",
        "constraints_id": "constraints.test.unsatisfiable",
        "universe_scope": "region",
        "hard_constraints": [
            {
                "constraint_id": "hard.impossible",
                "target": "world.layer.elevation",
                "operator": "range",
                "value": {"min": 20001, "max": 25000},
                "weight": 0,
                "description": "force impossible deterministic threshold",
            }
        ],
        "soft_constraints": [],
        "scoring_functions": [],
        "deterministic_seed_policy": "multi",
        "candidate_count": 4,
        "tie_break_policy": "lexicographic",
        "refusal_codes": [
            "refusal.constraints_unsatisfiable",
            "refusal.search_exhausted",
        ],
        "extensions": {},
    }

    first = solve_constraints(
        repo_root=repo_root,
        constraints_payload=payload,
        module_registry_payload=module_registry,
        base_seed="seed.worldgen.unsat.010",
    )
    second = solve_constraints(
        repo_root=repo_root,
        constraints_payload=payload,
        module_registry_payload=module_registry,
        base_seed="seed.worldgen.unsat.010",
    )
    if first.get("result") != "refused" or second.get("result") != "refused":
        return {"status": "fail", "message": "unsatisfiable constraints must refuse"}
    first_code = str(((first.get("refusal") or {}).get("reason_code", "")))
    second_code = str(((second.get("refusal") or {}).get("reason_code", "")))
    if first_code != "refusal.constraints_unsatisfiable" or second_code != "refusal.constraints_unsatisfiable":
        return {"status": "fail", "message": "unexpected refusal code for unsatisfiable constraints"}
    if first != second:
        return {"status": "fail", "message": "unsatisfiable refusal payload must be deterministic"}
    return {"status": "pass", "message": "unsatisfiable deterministic refusal passed"}
