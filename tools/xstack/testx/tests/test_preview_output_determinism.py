"""STRICT test: worldgen search preview payload is deterministic."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.worldgen.preview_output_determinism"
TEST_TAGS = ["strict", "worldgen", "determinism"]


def _constraints_path(repo_root: str) -> str:
    return os.path.join(
        repo_root,
        "packs",
        "core",
        "constraints.worldgen.default_lab",
        "data",
        "constraints.lab.navigation.default.json",
    )


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "entitlements": ["entitlement.worldgen.constraints"],
        "privilege_level": "operator",
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from worldgen.core.constraint_commands import worldgen_constraints_clear
    from worldgen.core.constraint_commands import worldgen_constraints_set
    from worldgen.core.constraint_commands import worldgen_search_preview

    context = _authority_context()
    constraints_file = _constraints_path(repo_root)
    set_result = worldgen_constraints_set(
        repo_root=repo_root,
        constraints_file=constraints_file,
        constraints_id="constraints.lab.navigation.default",
        base_seed="seed.worldgen.preview.001",
        authority_context=context,
    )
    if set_result.get("result") != "complete":
        return {"status": "fail", "message": "worldgen.constraints.set failed"}

    first = worldgen_search_preview(repo_root=repo_root, authority_context=context)
    second = worldgen_search_preview(repo_root=repo_root, authority_context=context)
    worldgen_constraints_clear(repo_root=repo_root, authority_context=context)

    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "worldgen.search.preview failed"}

    fields = (
        "constraints_id",
        "selected_seed",
        "search_plan_hash",
        "candidate_scores",
        "constraints_satisfied",
        "constraints_violated",
        "search_plan",
    )
    for field_name in fields:
        if first.get(field_name) != second.get(field_name):
            return {
                "status": "fail",
                "message": "preview field '{}' is not deterministic".format(field_name),
            }

    return {"status": "pass", "message": "worldgen preview deterministic output passed"}
