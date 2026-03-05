"""E272 unlogged shutdown smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E272_UNLOGGED_SHUTDOWN_SMELL"


class UnloggedShutdownSmell:
    analyzer_id = ANALYZER_ID


_SHUTDOWN_MUTATION_PATTERN = re.compile(
    r"\b(?:effect\.system\.safety_shutdown|system_reliability_safe_fallback_rows)\b.*(?:=|append\()",
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
    runtime_text = _read_text(repo_root, runtime_rel)

    for token in (
        "effect.system.safety_shutdown",
        "system_reliability_safe_fallback_rows",
        "artifact.record.system_failure",
        "control_decision_log",
        "generated_explain_ids",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_shutdown_smell",
                severity="RISK",
                confidence=0.94,
                file_path=runtime_rel,
                line=1,
                evidence=["required shutdown logging token missing from runtime", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-NO-SILENT-FAILURE",
                    "INV-FORCED-EXPAND-LOGGED",
                ],
                related_paths=[runtime_rel, "src/system/reliability/reliability_engine.py"],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
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
        "src/system/reliability/reliability_engine.py",
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
                    if not _SHUTDOWN_MUTATION_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unlogged_shutdown_smell",
                            severity="RISK",
                            confidence=0.89,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential unlogged shutdown/fallback mutation detected outside canonical runtime path",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-SILENT-FAILURE",
                                "INV-FORCED-EXPAND-LOGGED",
                            ],
                            related_paths=[rel_path, runtime_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

