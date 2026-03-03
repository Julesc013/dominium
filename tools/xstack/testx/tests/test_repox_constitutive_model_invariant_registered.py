"""FAST test: RepoX includes constitutive model realism-detail invariant wiring."""

from __future__ import annotations

import os


TEST_ID = "test_repox_constitutive_model_invariant_registered"
TEST_TAGS = ["fast", "repox", "meta", "model"]


_REQUIRED_TOKENS = (
    "INV-REALISM-DETAIL-MUST-BE-MODEL",
    "def _append_constitutive_model_invariant_findings(",
    "_append_constitutive_model_invariant_findings(",
)


def run(repo_root: str):
    rel_path = "tools/xstack/repox/check.py"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        text = open(abs_path, "r", encoding="utf-8").read()
    except OSError:
        return {"status": "fail", "message": "RepoX check file missing"}

    missing = [token for token in _REQUIRED_TOKENS if token not in text]
    if missing:
        return {
            "status": "fail",
            "message": "RepoX constitutive-model invariant wiring missing tokens: {}".format(",".join(missing)
            ),
        }
    return {"status": "pass", "message": "RepoX constitutive-model invariant wiring present"}
