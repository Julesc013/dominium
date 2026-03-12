"""FAST test: SOL-1 does not persist moon phase as truth state."""

from __future__ import annotations

import sys


TEST_ID = "test_no_phase_field_stored_in_truth"
TEST_TAGS = ["fast", "sol", "illumination", "truth_purity", "audit"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.astro.sol1_audit_common import scan_moon_phase_storage

    violations = list(scan_moon_phase_storage(repo_root))
    if violations:
        first = dict(violations[0] or {})
        return {
            "status": "fail",
            "message": "SOL-1 stored moon phase token detected at {}:{}".format(
                str(first.get("path", "")).replace("\\", "/"),
                int(first.get("line", 0) or 0),
            ),
        }
    return {"status": "pass", "message": "SOL-1 stores no moon-phase field in truth paths"}
