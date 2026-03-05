"""E271 hidden failure logic smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E271_HIDDEN_FAILURE_LOGIC_SMELL"


class HiddenFailureLogicSmell:
    analyzer_id = ANALYZER_ID


_FAILURE_LOGIC_PATTERN = re.compile(
    r"\b(?:system_failure_event_rows|system_reliability_safe_fallback_rows|system_reliability_warning_rows|system_reliability_output_adjustment_rows)\b.*(?:=|append\()",
    re.IGNORECASE,
)


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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    reliability_engine_rel = "src/system/reliability/reliability_engine.py"
    health_engine_rel = "src/system/reliability/system_health_engine.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    reliability_text = _read_text(repo_root, reliability_engine_rel)

    for token in (
        'elif process_id == "process.system_reliability_tick":',
        "evaluate_system_reliability_tick(",
        "system_failure_event_rows",
        "artifact.record.system_failure",
        "control_decision_log",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.hidden_failure_logic_smell",
                severity="RISK",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["required SYS-6 reliability runtime token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-SYSTEM-RELIABILITY-PROFILE-DECLARED",
                    "INV-NO-SILENT-FAILURE",
                ],
                related_paths=[runtime_rel, reliability_engine_rel, health_engine_rel],
            )
        )

    for token in (
        "def evaluate_system_reliability_tick(",
        "build_system_failure_event_row(",
        "safe_fallback_rows",
    ):
        if token in reliability_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.hidden_failure_logic_smell",
                severity="RISK",
                confidence=0.9,
                file_path=reliability_engine_rel,
                line=1,
                evidence=["reliability engine token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-SYSTEM-RELIABILITY-PROFILE-DECLARED",
                    "INV-NO-SILENT-FAILURE",
                ],
                related_paths=[reliability_engine_rel, runtime_rel],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src", "system"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        runtime_rel,
        reliability_engine_rel,
        health_engine_rel,
        "tools/xstack/repox/check.py",
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not _FAILURE_LOGIC_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.hidden_failure_logic_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential hidden failure-logic mutation detected outside canonical SYS-6 pathways",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-SYSTEM-RELIABILITY-PROFILE-DECLARED",
                                "INV-NO-SILENT-FAILURE",
                            ],
                            related_paths=[rel_path, runtime_rel, reliability_engine_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
