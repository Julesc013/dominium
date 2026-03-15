"""E489 convergence gate missing smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding


ANALYZER_ID = "E489_CONVERGENCE_GATE_MISSING_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    try:
        from tools.convergence.convergence_gate_common import convergence_gate_violations
    except Exception as exc:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.convergence_gate_missing_smell",
                severity="RISK",
                confidence=0.96,
                file_path="tools/convergence/convergence_gate_common.py",
                line=1,
                evidence=["unable to import convergence gate checks ({})".format(str(exc))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE"],
                related_paths=["tools/convergence/convergence_gate_common.py"],
            )
        ]
    findings = []
    for row in convergence_gate_violations(repo_root):
        violation = dict(row or {})
        rel_path = str(violation.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.convergence_gate_missing_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                line=1,
                evidence=[str(violation.get("code", "")).strip(), str(violation.get("message", "")).strip()],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REGENERATE_AND_FIX_CONVERGENCE_GATE",
                related_invariants=[str(violation.get("rule_id", "")).strip() or "INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE"],
                related_paths=[rel_path or "data/audit/convergence_final.json", "tools/convergence/tool_run_convergence_gate.py"],
            )
        )
    return findings
