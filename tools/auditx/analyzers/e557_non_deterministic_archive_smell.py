"""E557 non-deterministic archive smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_offline_archive


ANALYZER_ID = "E557_NON_DETERMINISTIC_ARCHIVE_SMELL"
TARGET_CATEGORIES = {"offline_archive.nondeterministic_archive"}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_offline_archive(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() not in TARGET_CATEGORIES:
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="offline_archive.non_deterministic_archive_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "offline archive hash or fingerprint drifted across identical reruns",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="RESTORE_STABLE_ARCHIVE_MEMBER_ORDERING_HASHING_AND_FROZEN_OUTPUTS_BEFORE_DIST",
                related_invariants=["INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE", "INV-OFFLINE-ARCHIVE-VERIFY-MUST-PASS"],
                related_paths=[rel_path],
            )
        )
    return findings
