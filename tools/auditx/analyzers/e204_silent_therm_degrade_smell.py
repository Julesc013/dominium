"""E204 silent thermal degradation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E204_SILENT_THERM_DEGRADE_SMELL"


class SilentThermDegradeSmell:
    analyzer_id = ANALYZER_ID


_INLINE_DEGRADE_PATTERN = re.compile(
    r"\b(?:degrade|downgrade|tick_bucket|t0_budget|defer_noncritical_models)\b[^\n]*(?:=|append\(|update\()",
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

    stress_tool_rel = "tools/thermal/tool_run_therm_stress.py"
    stress_tool_text = _read_text(repo_root, stress_tool_rel)
    required_tokens = (
        "control_decision_log",
        "thermal_degradation_event_rows",
        "thermal_degradation_record_rows",
        "proof_hash_summary",
    )
    for token in required_tokens:
        if token in stress_tool_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_therm_degrade_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=stress_tool_rel,
                line=1,
                evidence=["missing thermal degradation logging token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-THERM-DEGRADE-LOGGED"],
                related_paths=[stress_tool_rel],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "thermal"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
        "schema/",
        "schemas/",
    )
    allowed_files = {
        stress_tool_rel,
        "src/thermal/network/thermal_network_engine.py",
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
                    if not _INLINE_DEGRADE_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.silent_therm_degrade_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["thermal degradation expression outside canonical logging path", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-THERM-DEGRADE-LOGGED"],
                            related_paths=[rel_path, stress_tool_rel],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
