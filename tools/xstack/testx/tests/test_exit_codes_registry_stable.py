"""FAST test: AppShell exit-code registry preserves the baseline ranges."""

from __future__ import annotations


TEST_ID = "test_exit_codes_registry_stable"
TEST_TAGS = ["fast", "appshell", "registry"]


def run(repo_root: str):
    import json
    import os

    path = os.path.join(repo_root, "data", "registries", "exit_code_registry.json")
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "exit code registry is missing or invalid"}
    ranges = list(dict(payload.get("record") or {}).get("ranges") or [])
    expected = [
        ("exit.success", 0, 0),
        ("exit.usage", 10, 19),
        ("exit.pack_profile", 20, 29),
        ("exit.contract", 30, 39),
        ("exit.transport", 40, 49),
        ("exit.refusal", 50, 59),
        ("exit.internal", 60, 69),
    ]
    actual = [
        (
            str(dict(row or {}).get("range_id", "")).strip(),
            int(dict(row or {}).get("start_code", -1)),
            int(dict(row or {}).get("end_code", -1)),
        )
        for row in ranges
    ]
    if actual != expected:
        return {"status": "fail", "message": "exit code registry drifted from the AppShell baseline"}
    return {"status": "pass", "message": "AppShell exit-code registry remains stable"}

