"""STRICT test: contract foundation registry validates and includes baseline IDs."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.domain.contract_registry_valid"
TEST_TAGS = ["strict", "schema", "repox"]

BASELINE_IDS = (
    "dom.contract.mass_conservation",
    "dom.contract.energy_conservation",
    "dom.contract.charge_conservation",
    "dom.contract.ledger_balance",
    "dom.contract.epistemic_non_omniscience",
    "dom.contract.deterministic_transition",
    "dom.contract.port_contract_preservation",
)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.domain.tool_domain_validate import validate_domain_foundation

    checked = validate_domain_foundation(repo_root=repo_root)
    if str(checked.get("result", "")) != "complete":
        return {"status": "fail", "message": "domain foundation validator refused before contract checks"}

    payload = json.load(open(os.path.join(repo_root, "data", "registries", "domain_contract_registry.json"), "r", encoding="utf-8"))
    rows = payload.get("records")
    if not isinstance(rows, list):
        return {"status": "fail", "message": "domain_contract_registry.records missing"}
    ids = sorted(
        set(
            str(row.get("contract_id", "")).strip()
            for row in rows
            if isinstance(row, dict) and str(row.get("contract_id", "")).strip()
        )
    )
    missing = sorted(set(BASELINE_IDS) - set(ids))
    if missing:
        return {"status": "fail", "message": "missing baseline contract IDs: {}".format(",".join(missing))}
    return {"status": "pass", "message": "contract registry validation passed"}
