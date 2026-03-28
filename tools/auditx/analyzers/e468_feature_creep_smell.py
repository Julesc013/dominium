"""E468 feature creep smell analyzer for the v0.0.0 convergence freeze."""

from __future__ import annotations

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding
from meta.stability import ALL_REGISTRY_PATHS
from tools.release.scope_freeze_common import REQUIRED_SCOPE_FREEZE_DOCS, scope_freeze_violations


ANALYZER_ID = "E468_FEATURE_CREEP_SMELL"
WATCH_PREFIXES = tuple(
    list(REQUIRED_SCOPE_FREEZE_DOCS)
    + ["data/registries/semantic_contract_registry.json", "tools/release/scope_freeze_common.py"]
    + list(ALL_REGISTRY_PATHS)
)
RULE_IDS = (
    "INV-NO-NEW-DOMAIN-SERIES-DURING-CONVERGENCE",
    "INV-NO-SEMANTIC-CONTRACT-CHANGES-POST-FREEZE",
    "INV-PROVISIONAL-MUST-HAVE-REPLACEMENT-PLAN",
)


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in scope_freeze_violations(repo_root):
        violation = dict(row or {})
        rel_path = str(violation.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.feature_creep_smell",
                severity="RISK",
                confidence=0.96,
                file_path=rel_path,
                evidence=[str(violation.get("message", "")).strip()],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[str(violation.get("rule_id", "")).strip() or RULE_IDS[0]],
                related_paths=[rel_path],
            )
        )
    return findings
