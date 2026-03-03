"""FAST test: THERM null-boot policy remains unchanged after THERM-5 hardening."""

from __future__ import annotations

import json
import os
import re


TEST_ID = "test_null_boot_unchanged"
TEST_TAGS = ["fast", "thermal", "therm5", "null_boot", "policy"]


def run(repo_root: str):
    registry_rel = "data/registries/thermal_policy_registry.json"
    registry_abs = os.path.join(repo_root, registry_rel)
    if not os.path.isfile(registry_abs):
        return {"status": "fail", "message": "missing thermal policy registry"}

    try:
        record = json.loads(open(registry_abs, "r", encoding="utf-8").read())
    except Exception as exc:  # noqa: BLE001
        return {"status": "fail", "message": "invalid thermal policy registry JSON: {}".format(exc)}

    rows = list(dict(record).get("thermal_policies") or [])
    ids = set(
        str(dict(row).get("policy_id", "")).strip()
        for row in rows
        if isinstance(row, dict)
    )
    if "therm.policy.none" not in ids:
        return {"status": "fail", "message": "therm.policy.none missing; null-boot path is no longer explicit"}

    forced_pattern = re.compile(r"therm\.policy\.default")
    runtime_paths = [
        "tools/xstack/sessionx/creator.py",
        "tools/xstack/sessionx/runner.py",
        "tools/xstack/sessionx/process_runtime.py",
    ]
    for rel_path in runtime_paths:
        abs_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(abs_path):
            continue
        text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
        for line in text.splitlines():
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if forced_pattern.search(snippet):
                return {
                    "status": "fail",
                    "message": "runtime appears to hardcode therm.policy.default: {}".format(rel_path),
                }

    return {"status": "pass", "message": "THERM null-boot policy remains unchanged"}
