"""E460 phase-shortcut smell analyzer."""

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
from tools.domain.astronomy.sol1_audit_common import SOL1_SCOPE_PATHS, scan_occlusion_policy_violations, scan_phase_shortcuts


ANALYZER_ID = "E460_PHASE_SHORTCUT_SMELL"
WATCH_PREFIXES = tuple(SOL1_SCOPE_PATHS)
RULE_IDS = ("INV-PHASE-DERIVED-FROM-ILLUMINATION", "INV-OCCLUSION-STUB-ONLY")


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in scan_phase_shortcuts(repo_root) + scan_occlusion_policy_violations(repo_root):
        violation = dict(row or {})
        rel_path = str(violation.get("path", "")).replace("\\", "/")
        related_invariants = (
            ["INV-OCCLUSION-STUB-ONLY"]
            if "occlusion" in str(violation.get("message", "")).lower()
            else ["INV-PHASE-DERIVED-FROM-ILLUMINATION"]
        )
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="sol.phase_shortcut_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                line=int(violation.get("line", 0) or 0),
                evidence=[str(violation.get("message", "")).strip(), str(violation.get("snippet", "")).strip()],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=related_invariants,
                related_paths=[rel_path],
            )
        )
    return findings
