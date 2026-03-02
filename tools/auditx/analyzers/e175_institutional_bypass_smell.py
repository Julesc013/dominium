"""E175 institutional bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E175_INSTITUTIONAL_BYPASS_SMELL"


class InstitutionalBypassSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = ("src/signals/",)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    bulletin_rel = "src/signals/institutions/bulletin_engine.py"
    dispatch_rel = "src/signals/institutions/dispatch_engine.py"
    standards_rel = "src/signals/institutions/standards_engine.py"
    required_anchor_sets = {
        bulletin_rel: ("process_signal_send(", "artifact.report.institution"),
        dispatch_rel: ("build_control_intent(", "process.travel_schedule_set"),
        standards_rel: ("artifact.report.compliance", "process_signal_send("),
    }
    for rel_path, anchors in required_anchor_sets.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.institutional_bypass_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing institutional SIG-6 engine file"],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-ADHOC-BULLETINS"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in anchors:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.institutional_bypass_smell",
                    severity="VIOLATION",
                    confidence=0.92,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing institutional comm anchor token", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-ADHOC-BULLETINS", "INV-REPORTS-ARE-ARTIFACTS"],
                    related_paths=[rel_path],
                )
            )

    allow_files = {
        bulletin_rel,
        dispatch_rel,
        standards_rel,
        "tools/auditx/analyzers/e175_institutional_bypass_smell.py",
    }
    scan_root = os.path.join(repo_root, "src", "signals")
    if os.path.isdir(scan_root):
        for walk_root, _dirs, files in os.walk(scan_root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path in allow_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if "artifact.report.institution" not in snippet and "bulletin_policy_id" not in snippet:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.institutional_bypass_smell",
                            severity="RISK",
                            confidence=0.89,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["possible ad-hoc institutional bulletin/report logic outside SIG-6 engines", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-ADHOC-BULLETINS"],
                            related_paths=[rel_path, bulletin_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
