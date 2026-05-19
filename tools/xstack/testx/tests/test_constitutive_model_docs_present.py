"""FAST test: META-MODEL-0 constitutive model documentation artifacts are present."""

from __future__ import annotations

import os


TEST_ID = "test_constitutive_model_docs_present"
TEST_TAGS = ["fast", "meta", "model", "docs"]


_REQUIRED_DOCS = (
    "docs/archive/audit/META_MODEL0_RETRO_AUDIT.md",
    "docs/governance/meta/CONSTITUTIVE_MODEL_CONSTITUTION.md",
    "docs/governance/meta/CONSTITUTIVE_MODEL_CATALOG.md",
    "docs/governance/meta/INFORMATION_GRAMMAR_CONSTITUTION.md",
    "docs/archive/audit/CONSTITUTIVE_MODEL_CONSTITUTION_BASELINE.md",
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
            "message": "missing constitutive model docs: {}".format(",".join(sorted(missing))),
        }
    return {"status": "pass", "message": "constitutive model docs present"}
