"""FAST test: deprecation validator tool reports refusal on malformed input."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile


TEST_ID = "test_deprecation_tool_reports_errors"
TEST_TAGS = ["fast", "governance", "deprecation", "tooling"]


def run(repo_root: str):
    tool_path = os.path.join(repo_root, "tools", "governance", "tool_deprecation_check.py")
    topology_path = os.path.join(repo_root, "docs", "audit", "TOPOLOGY_MAP.json")
    if not os.path.isfile(tool_path):
        return {"status": "fail", "message": "missing tool_deprecation_check.py"}

    with tempfile.TemporaryDirectory(prefix="dom_deprecation_tool_test_") as temp_dir:
        invalid_path = os.path.join(temp_dir, "invalid_deprecations.json")
        invalid_payload = {
            "registry_id": "dominium.governance.deprecations",
            "entries": [
                {
                    "deprecated_id": "legacy.example.id",
                    "deprecated_kind": "module",
                    "replacement_id": "",
                    "reason": "test malformed payload",
                    "introduced_version": "1.0.0",
                    "deprecated_version": "1.0.0",
                    "removal_target_version": "",
                    "status": "deprecated",
                    "adapter_path": "",
                    "notes": "",
                    "extensions": {},
                }
            ],
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        with open(invalid_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(invalid_payload, handle, indent=2, sort_keys=True)
            handle.write("\n")

        proc = subprocess.run(
            [
                sys.executable,
                tool_path,
                "--repo-root",
                repo_root,
                "--deprecations",
                invalid_path,
                "--topology-map",
                topology_path,
            ],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
        output = str(proc.stdout or "")
        if int(proc.returncode) == 0:
            return {"status": "fail", "message": "deprecation tool accepted malformed payload unexpectedly"}
        if '"result": "refused"' not in output:
            return {"status": "fail", "message": "deprecation tool did not report refused result on malformed payload"}

    return {"status": "pass", "message": "deprecation tool refusal path verified"}

