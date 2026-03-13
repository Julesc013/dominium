"""FAST test: build identity enforcement finds no wall-clock usage in the canonical build ID path."""

from __future__ import annotations


TEST_ID = "test_no_wallclock_in_build_id"
TEST_TAGS = ["fast", "release", "identity"]


def run(repo_root: str):
    from tools.release.release_identity_common import release_identity_violations

    bad = [row for row in release_identity_violations(repo_root) if str(dict(row).get("rule_id", "")).strip() == "INV-NO-WALLCLOCK-IN-BUILD_ID"]
    if bad:
        return {"status": "fail", "message": str(dict(bad[0]).get("message", "")).strip() or "wall-clock build ID violation detected"}
    return {"status": "pass", "message": "canonical build identity path is free of wall-clock and host metadata"}
