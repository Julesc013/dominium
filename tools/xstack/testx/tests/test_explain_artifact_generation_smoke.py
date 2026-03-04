"""STRICT test: explain generation smoke for enforced event families."""

from __future__ import annotations

import json
import os
import re
import sys


TEST_ID = "test_explain_artifact_generation_smoke"
TEST_TAGS = ["strict", "meta", "contracts", "explain", "smoke"]


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SMOKE_EVENTS = (
    "elec.trip",
    "therm.overheat",
    "fluid.burst",
    "mob.derailment",
    "sig.delivery_loss",
    "phys.exception_event",
)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.explain import generate_explain_artifact

    rel_path = "data/registries/explain_contract_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "explain contract registry missing or invalid"}

    rows = list((dict(payload.get("record") or {})).get("explain_contracts") or payload.get("explain_contracts") or [])
    contract_by_event = dict(
        (str(row.get("event_kind_id", "")).strip(), dict(row))
        for row in rows
        if isinstance(row, dict) and str(row.get("event_kind_id", "")).strip()
    )

    for event_kind_id in _SMOKE_EVENTS:
        contract_row = dict(contract_by_event.get(event_kind_id) or {})
        if not contract_row:
            return {"status": "fail", "message": "missing explain contract for smoke event '{}'".format(event_kind_id)}

        build_inputs = {
            "event_id": "event.{}.001".format(event_kind_id.replace(".", "_")),
            "target_id": "target.{}.main".format(event_kind_id.split(".", 1)[0]),
            "event_kind_id": event_kind_id,
            "truth_hash_anchor": "truth.hash.anchor.meta_contract1",
            "epistemic_policy_id": "policy.epistemic.observer",
            "explain_contract_row": contract_row,
            "decision_log_rows": [{"decision_id": "decision.{}.1".format(event_kind_id.replace(".", "_")), "reason_code": "decision.path"}],
            "safety_event_rows": [{"event_id": "safety.{}.1".format(event_kind_id.replace(".", "_")), "event_kind_id": event_kind_id, "fault_code": "fault.A1"}],
            "hazard_rows": [{"event_id": "hazard.{}.1".format(event_kind_id.replace(".", "_")), "hazard_id": "hazard.base", "pressure_head": 120, "speed": 55}],
            "compliance_rows": [{"result_id": "compliance.{}.1".format(event_kind_id.replace(".", "_")), "transformation_id": "transform.sample"}],
            "model_result_rows": [{"result_id": "model.{}.1".format(event_kind_id.replace(".", "_")), "loss_modifier": 2, "traction": 3}],
        }
        first = generate_explain_artifact(**build_inputs)
        second = generate_explain_artifact(**build_inputs)
        if not first or not second:
            return {"status": "fail", "message": "explain generation returned empty payload for '{}'".format(event_kind_id)}
        if dict(first) != dict(second):
            return {"status": "fail", "message": "explain generation drift for '{}'".format(event_kind_id)}
        if not list(first.get("cause_chain") or []):
            return {"status": "fail", "message": "empty cause_chain for '{}'".format(event_kind_id)}
        if not list(first.get("referenced_artifacts") or []):
            return {"status": "fail", "message": "empty referenced_artifacts for '{}'".format(event_kind_id)}
        fingerprint = str(first.get("deterministic_fingerprint", "")).strip().lower()
        if not _SHA256.fullmatch(fingerprint):
            return {"status": "fail", "message": "invalid deterministic_fingerprint for '{}'".format(event_kind_id)}

    return {"status": "pass", "message": "explain artifact generation smoke passed for enforced event families"}
