"""FAST test: baseline cross-domain couplings are declared in registry."""

from __future__ import annotations

import json
import os


TEST_ID = "test_all_couplings_declared"
TEST_TAGS = ["fast", "meta", "contracts", "coupling"]


_REQUIRED_CONTRACTS = {
    ("energy_coupling", "ELEC", "THERM", "energy_transform"),
    ("energy_coupling", "FIELD", "THERM", "constitutive_model"),
    ("force_coupling", "THERM", "MECH", "constitutive_model"),
    ("info_coupling", "SIG", "SIG", "signal_policy"),
}


def run(repo_root: str):
    rel_path = "data/registries/coupling_contract_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "coupling contract registry missing or invalid"}

    rows = list((dict(payload.get("record") or {})).get("coupling_contracts") or payload.get("coupling_contracts") or [])
    if not rows:
        return {"status": "fail", "message": "coupling contract registry has no rows"}

    declared = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = (
            str(row.get("coupling_class_id", "")).strip(),
            str(row.get("from_domain_id", "")).strip().upper(),
            str(row.get("to_domain_id", "")).strip().upper(),
            str(row.get("mechanism", "")).strip(),
        )
        if all(key):
            declared.add(key)
        if not str(row.get("contract_id", "")).strip():
            return {"status": "fail", "message": "coupling contract row missing contract_id"}
        if not str(row.get("mechanism_id", "")).strip():
            return {
                "status": "fail",
                "message": "coupling contract '{}' missing mechanism_id".format(str(row.get("contract_id", "")).strip() or "<unknown>"),
            }

    missing = sorted(_REQUIRED_CONTRACTS - declared)
    if missing:
        tokens = ["{}:{}->{} ({})".format(*row) for row in missing]
        return {"status": "fail", "message": "missing baseline coupling declarations: {}".format(",".join(tokens))}
    return {"status": "pass", "message": "baseline coupling contracts present"}

