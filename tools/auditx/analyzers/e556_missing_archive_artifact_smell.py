"""E556 missing archive artifact smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_offline_archive


ANALYZER_ID = "E556_MISSING_ARCHIVE_ARTIFACT_SMELL"
TARGET_CATEGORIES = {"offline_archive.missing_archive_artifact"}


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
                category="offline_archive.missing_archive_artifact_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "offline archive is missing a required retained artifact",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="RESTORE_THE_MISSING_RELEASE_OR_BASELINE_ARTIFACT_IN_THE_FROZEN_OFFLINE_ARCHIVE_LAYOUT",
                related_invariants=["INV-OFFLINE-ARCHIVE-BUILT-FOR-RELEASE"],
                related_paths=[rel_path],
            )
        )
    return findings
