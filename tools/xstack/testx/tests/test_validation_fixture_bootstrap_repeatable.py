"""FAST test: validation fixture bootstrap remains repeatable across fresh Python processes."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "test_validation_fixture_bootstrap_repeatable"
TEST_TAGS = ["fast", "validation", "determinism"]


_PROBE = r"""
import json
import sys

repo_root = sys.argv[1]
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src.validation.validation_engine import _adapt_schema_suite, _suite_row_by_id
from tools.time.time_anchor_common import verify_compaction_anchor_alignment, verify_longrun_ticks

suites = _suite_row_by_id(repo_root)
schema_result = _adapt_schema_suite(repo_root, suites["validate.schemas"], "FAST")
verify_report = verify_longrun_ticks(repo_root)
compaction_report = verify_compaction_anchor_alignment(repo_root)
print(
    json.dumps(
        {
            "schema_fp": str(schema_result.get("deterministic_fingerprint", "")).strip(),
            "time_verify_fp": str(verify_report.get("deterministic_fingerprint", "")).strip(),
            "time_compaction_fp": str(compaction_report.get("deterministic_fingerprint", "")).strip(),
        },
        sort_keys=True,
    )
)
"""


def _run_probe(repo_root: str) -> tuple[int, str, str]:
    completed = subprocess.run(
        [sys.executable, "-c", _PROBE, repo_root],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def run(repo_root: str):
    first_code, first_out, first_err = _run_probe(repo_root)
    if first_code != 0:
        return {
            "status": "fail",
            "message": "first validation fixture bootstrap probe failed: {}".format(first_err or first_out or first_code),
        }
    second_code, second_out, second_err = _run_probe(repo_root)
    if second_code != 0:
        return {
            "status": "fail",
            "message": "second validation fixture bootstrap probe failed: {}".format(second_err or second_out or second_code),
        }
    if first_out != second_out:
        try:
            first_payload = json.loads(first_out)
            second_payload = json.loads(second_out)
        except ValueError:
            first_payload = first_out
            second_payload = second_out
        return {
            "status": "fail",
            "message": "fresh-process validation fixture bootstrap drifted: {} vs {}".format(
                first_payload,
                second_payload,
            ),
        }
    return {"status": "pass", "message": "validation fixture bootstrap is repeatable across fresh processes"}
