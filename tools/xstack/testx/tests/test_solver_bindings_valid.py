"""STRICT test: solver bindings declare domain_ids and contract_ids."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.domain.solver_bindings_valid"
TEST_TAGS = ["strict", "schema", "repox"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.domain.tool_domain_validate import validate_domain_foundation

    checked = validate_domain_foundation(repo_root=repo_root)
    if str(checked.get("result", "")) != "complete":
        return {"status": "fail", "message": "domain foundation validator refused before solver checks"}

    payload = json.load(open(os.path.join(repo_root, "data", "registries", "solver_registry.json"), "r", encoding="utf-8"))
    rows = payload.get("records")
    if not isinstance(rows, list):
        return {"status": "fail", "message": "solver_registry.records missing"}

    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        solver_id = str(row.get("solver_id", "")).strip()
        domain_ids = [str(item).strip() for item in (row.get("domain_ids") or []) if str(item).strip()]
        contract_ids = [str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip()]
        transition_support = [str(item).strip() for item in (row.get("transition_support") or []) if str(item).strip()]
        if not solver_id:
            return {"status": "fail", "message": "solver row {} missing solver_id".format(idx)}
        if not domain_ids or not contract_ids:
            return {"status": "fail", "message": "solver '{}' missing domain/contract bindings".format(solver_id)}
        if not transition_support:
            return {"status": "fail", "message": "solver '{}' missing transition_support".format(solver_id)}
    return {"status": "pass", "message": "solver binding validation passed"}
