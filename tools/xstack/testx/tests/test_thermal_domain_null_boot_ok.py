"""FAST test: THERM policies remain optional and null-boot compatible."""

from __future__ import annotations

import json
import os
import re


TEST_ID = "test_thermal_domain_null_boot_ok"
TEST_TAGS = ["fast", "thermal", "null_boot", "policy"]


def run(repo_root: str):
    registry_rel = "data/registries/thermal_policy_registry.json"
    registry_abs = os.path.join(repo_root, registry_rel.replace("/", os.sep))
    if not os.path.isfile(registry_abs):
        return {"status": "fail", "message": "missing thermal policy registry"}

    try:
        payload = json.load(open(registry_abs, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"status": "fail", "message": "invalid thermal policy registry JSON: {}".format(exc)}

    record = dict((payload if isinstance(payload, dict) else {}).get("record") or {})
    rows = list(record.get("thermal_policies") or [])
    policy_ids = sorted(
        str(dict(row).get("policy_id", "")).strip()
        for row in rows
        if isinstance(row, dict)
    )
    if "therm.policy.none" not in policy_ids:
        return {"status": "fail", "message": "therm.policy.none missing; thermal null-boot path is not declared"}

    runtime_paths = (
        "tools/xstack/sessionx/creator.py",
        "tools/xstack/sessionx/runner.py",
    )
    default_pattern = re.compile(r"therm\.policy\.default")
    pack_pattern = re.compile(r"packs/.+thermal", re.IGNORECASE)
    for rel_path in runtime_paths:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if default_pattern.search(text):
            return {
                "status": "fail",
                "message": "runtime path hardcodes therm.policy.default: {}".format(rel_path),
            }
        if pack_pattern.search(text):
            return {
                "status": "fail",
                "message": "runtime path appears to require thermal pack: {}".format(rel_path),
            }

    return {"status": "pass", "message": "THERM policy remains optional and null-boot safe"}

