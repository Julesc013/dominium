"""FAST test: ELEC-0 documentation artifacts are present."""

from __future__ import annotations

import os


TEST_ID = "test_elec0_docs_present"
TEST_TAGS = ["fast", "elec", "docs"]


_REQUIRED_DOCS = (
    "docs/audit/ELEC0_RETRO_AUDIT.md",
    "docs/electric/ELECTRICAL_CONSTITUTION.md",
    "docs/audit/ELECTRICAL_CONSTITUTION_BASELINE.md",
)


def run(repo_root: str):
    missing = []
    for rel_path in _REQUIRED_DOCS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
    if missing:
        return {
            "status": "fail",
            "message": "missing ELEC-0 docs: {}".format(",".join(sorted(missing))),
        }
    return {"status": "pass", "message": "ELEC-0 docs present"}

