"""E473 duplicate validation surface smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(THIS_DIR)
for _repo_root_probe_depth in range(16):
    if os.path.exists(os.path.join(REPO_ROOT_HINT, "AGENTS.md")):
        break
    parent = os.path.dirname(REPO_ROOT_HINT)
    if parent == REPO_ROOT_HINT:
        REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
        break
    REPO_ROOT_HINT = parent
REPO_ROOT_HINT = os.path.normpath(REPO_ROOT_HINT)
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.validators.suite import validation_surface_findings


ANALYZER_ID = "E473_DUPLICATE_VALIDATION_SURFACE_SMELL"
WATCH_PREFIXES = ("tools/validators", "tools/validators/content/coredata", "src/validation")
RULE_ID = "INV-NO-ADHOC-VALIDATION-ENTRYPOINTS"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in validation_surface_findings(repo_root):
        item = dict(row or {})
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="validation.duplicate_validation_surface_smell",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path,
                evidence=[
                    "code={}".format(str(item.get("code", "")).strip() or "<missing>"),
                    str(item.get("message", "")).strip() or "validation unification drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[RULE_ID],
                related_paths=[rel_path or "contracts/registry/validation_suite_registry.json"],
            )
        )
    return findings
