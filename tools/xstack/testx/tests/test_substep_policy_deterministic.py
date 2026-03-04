"""FAST test: authoritative substep policies are deterministic and non-adaptive."""

from __future__ import annotations

import json
import os


TEST_ID = "test_substep_policy_deterministic"
TEST_TAGS = ["fast", "time", "policy", "temp0"]

_REQUIRED_POLICY_IDS = {
    "substep.none",
    "substep.fixed_4",
    "substep.fixed_8",
    "substep.closed_form_only",
}


def run(repo_root: str):
    rel_path = "data/registries/substep_policy_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "substep policy registry missing or invalid"}

    rows = list(((payload.get("record") or {}).get("substep_policies") or []))
    if not rows:
        return {"status": "fail", "message": "substep policy registry has no rows"}

    rows_by_id = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        policy_id = str(row.get("substep_policy_id", "")).strip()
        if not policy_id:
            return {"status": "fail", "message": "substep policy row missing substep_policy_id"}
        if policy_id in rows_by_id:
            return {"status": "fail", "message": "duplicate substep policy '{}'".format(policy_id)}
        rows_by_id[policy_id] = dict(row)
        if str(row.get("schema_version", "")).strip() != "1.0.0":
            return {"status": "fail", "message": "policy '{}' missing schema_version=1.0.0".format(policy_id)}
        if bool(row.get("allow_adaptive", False)):
            return {"status": "fail", "message": "policy '{}' must not allow adaptive substeps".format(policy_id)}
        if not bool(row.get("deterministic", False)):
            return {"status": "fail", "message": "policy '{}' must declare deterministic=true".format(policy_id)}
        mode = str(row.get("mode", "")).strip()
        substep_count = int(row.get("substep_count", 0) or 0)
        if mode == "fixed" and substep_count <= 0:
            return {"status": "fail", "message": "fixed mode policy '{}' must have substep_count > 0".format(policy_id)}
        if mode == "none" and substep_count != 1:
            return {"status": "fail", "message": "none mode policy '{}' must have substep_count=1".format(policy_id)}
        if mode == "closed_form_only" and substep_count != 1:
            return {"status": "fail", "message": "closed_form_only policy '{}' must have substep_count=1".format(policy_id)}

    missing = sorted(_REQUIRED_POLICY_IDS - set(rows_by_id.keys()))
    if missing:
        return {"status": "fail", "message": "missing required substep policies: {}".format(",".join(missing))}

    fixed_4 = int((rows_by_id.get("substep.fixed_4") or {}).get("substep_count", 0) or 0)
    fixed_8 = int((rows_by_id.get("substep.fixed_8") or {}).get("substep_count", 0) or 0)
    if fixed_4 != 4:
        return {"status": "fail", "message": "substep.fixed_4 must declare substep_count=4"}
    if fixed_8 != 8:
        return {"status": "fail", "message": "substep.fixed_8 must declare substep_count=8"}

    return {"status": "pass", "message": "substep policies are deterministic and non-adaptive"}
