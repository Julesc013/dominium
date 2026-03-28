"""FAST test: XI-5a-v4 rewrites quoted path-segment literals used in audit/tooling code."""

from __future__ import annotations

import json
import os


TEST_ID = "test_xi5a_v4_rewrites_segment_literal_paths"
TEST_TAGS = ["fast", "xi5a", "regression", "review"]


def run(repo_root: str):
    from tools.review.xi5a_v4_execute_common import _apply_replacements, _build_replacement_maps

    lock_path = os.path.join(repo_root, "data", "restructure", "src_domain_mapping_lock_approved_v4.json")
    with open(lock_path, "r", encoding="utf-8") as handle:
        lock_payload = json.load(handle)

    needed = {
        "compat/capability_negotiation.py",
        "universe/universe_contract_enforcer.py",
        "release/component_graph_resolver.py",
    }
    rows = [row for row in list(lock_payload.get("approved_for_xi5") or []) if row.get("source_path") in needed]
    replacements = _build_replacement_maps(rows)

    sample = "\n".join(
        [
            'NEGOTIATION = os.path.join("compat", "capability_negotiation.py")',
            'CONTRACT = os.path.join("universe", "universe_contract_enforcer.py")',
            'COMPONENT = os.path.join("release", "component_graph_resolver.py")',
        ]
    )
    updated = _apply_replacements(sample, replacements)

    if 'os.path.join("compat", "capability_negotiation.py")' not in updated:
        return {"status": "fail", "message": "segment-literal rewrite missed compat capability negotiation path"}
    if 'os.path.join("universe", "universe_contract_enforcer.py")' not in updated:
        return {"status": "fail", "message": "segment-literal rewrite missed universe contract enforcer path"}
    if 'os.path.join("release", "component_graph_resolver.py")' not in updated:
        return {"status": "fail", "message": "segment-literal rewrite missed release component graph resolver path"}
    if 'os.path.join("compat", "capability_negotiation.py")' in updated:
        return {"status": "fail", "message": "segment-literal rewrite left stale compat src path behind"}
    if 'os.path.join("universe", "universe_contract_enforcer.py")' in updated:
        return {"status": "fail", "message": "segment-literal rewrite left stale universe src path behind"}
    if 'os.path.join("release", "component_graph_resolver.py")' in updated:
        return {"status": "fail", "message": "segment-literal rewrite left stale release src path behind"}
    return {"status": "pass", "message": "segment-literal rewrite updates path-builder literals for Xi-5a-v4"}
