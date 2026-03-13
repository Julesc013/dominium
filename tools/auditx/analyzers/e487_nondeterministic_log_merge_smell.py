"""E487 nondeterministic log merge smell analyzer for SUPERVISOR-HARDEN-0."""

from __future__ import annotations

from analyzers.base import make_finding


ANALYZER_ID = "E487_NONDETERMINISTIC_LOG_MERGE_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    try:
        from tools.appshell.supervisor_hardening_common import supervisor_hardening_violations
    except Exception as exc:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.supervisor.nondeterministic_log_merge_smell",
                severity="RISK",
                confidence=0.95,
                file_path="tools/appshell/supervisor_hardening_common.py",
                line=1,
                evidence=["unable to import supervisor hardening checks ({})".format(str(exc))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-SUPERVISOR-LOG-MERGE-STABLE"],
                related_paths=["tools/appshell/supervisor_hardening_common.py"],
            )
        ]
    findings = []
    for row in supervisor_hardening_violations(repo_root):
        violation = dict(row or {})
        if str(violation.get("code", "")).strip() != "log_merge_rule_missing":
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.supervisor.nondeterministic_log_merge_smell",
                severity="RISK",
                confidence=0.98,
                file_path=str(violation.get("file_path", "")).replace("\\", "/"),
                line=1,
                evidence=[str(violation.get("message", "")).strip()],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-SUPERVISOR-LOG-MERGE-STABLE"],
                related_paths=[str(violation.get("file_path", "")).replace("\\", "/")],
            )
        )
    return findings
