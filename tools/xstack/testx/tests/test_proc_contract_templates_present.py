"""FAST test: PROC tier/coupling/explain contract templates are declared."""

from __future__ import annotations

import json
import os


TEST_ID = "test_proc_contract_templates_present"
TEST_TAGS = ["fast", "proc", "contracts"]


def _load(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid json"


def run(repo_root: str):
    tier_payload, tier_err = _load(repo_root, "data/registries/tier_contract_registry.json")
    coupling_payload, coupling_err = _load(repo_root, "data/registries/coupling_contract_registry.json")
    explain_payload, explain_err = _load(repo_root, "data/registries/explain_contract_registry.json")
    if tier_err or coupling_err or explain_err:
        return {"status": "fail", "message": "one or more contract registries are missing or invalid"}

    tier_rows = list((dict(tier_payload.get("record") or {})).get("tier_contracts") or [])
    coupling_rows = list((dict(coupling_payload.get("record") or {})).get("coupling_contracts") or [])
    explain_rows = list((dict(explain_payload.get("record") or {})).get("explain_contracts") or [])

    tier_contract_ids = set(str(row.get("contract_id", "")).strip() for row in tier_rows if isinstance(row, dict))
    coupling_contract_ids = set(str(row.get("contract_id", "")).strip() for row in coupling_rows if isinstance(row, dict))
    explain_contract_ids = set(str(row.get("contract_id", "")).strip() for row in explain_rows if isinstance(row, dict))

    required_tier = {"tier.proc.default"}
    required_coupling = {
        "coupling.proc.capsule_to_chem.outputs",
        "coupling.proc.qc_to_sig.report",
        "coupling.proc.drift_to_sys.fidelity",
    }
    required_explain = {
        "explain.qc_failure",
        "explain.drift_detected",
        "explain.yield_drop",
        "explain.process_refusal",
    }

    missing = sorted(
        (required_tier - tier_contract_ids)
        | (required_coupling - coupling_contract_ids)
        | (required_explain - explain_contract_ids)
    )
    if missing:
        return {"status": "fail", "message": "missing PROC contract templates: {}".format(",".join(missing))}

    repox_path = os.path.join(repo_root, "tools", "xstack", "repox", "check.py")
    try:
        repox_text = open(repox_path, "r", encoding="utf-8").read()
    except OSError:
        return {"status": "fail", "message": "RepoX check file missing"}
    for token in (
        "INV-NO-RECIPE-HACKS",
        "INV-PROCESS-OUTPUTS-LEDGERED",
        "INV-PROCESS-CAPSULE-REQUIRES-STABILIZED",
    ):
        if token not in repox_text:
            return {"status": "fail", "message": "RepoX missing PROC invariant token: {}".format(token)}

    return {"status": "pass", "message": "PROC contract templates are present"}
