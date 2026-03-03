"""FAST test: RepoX structural-integrity hardening invariants are wired."""

from __future__ import annotations

import os


TEST_ID = "test_repox_structural_integrity_invariants_registered"
TEST_TAGS = ["fast", "repox", "meta", "integrity"]


_REQUIRED_TOKENS = (
    "INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL",
    "INV-LOSS-MUST-DECLARE-TARGET",
    "INV-INFO-ARTIFACT-MUST-HAVE-FAMILY",
    "def _append_cross_domain_mutation_invariant_findings(",
    "def _append_loss_target_invariant_findings(",
    "def _append_info_grammar_invariant_findings(",
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
            "message": "RepoX structural hardening wiring missing tokens: {}".format(",".join(missing)),
        }
    return {"status": "pass", "message": "RepoX structural hardening invariants wired"}

