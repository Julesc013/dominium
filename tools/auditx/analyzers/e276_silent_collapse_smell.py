"""E276 silent collapse smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E276_SILENT_COLLAPSE_SMELL"


_TIER_MUTATION_PATTERN = re.compile(
    r"\b(?:current_tier|active_capsule_id|system_collapse_event_rows|system_expand_event_rows)\b.*(?:=|append\()",
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
    scheduler_rel = "src/system/roi/system_roi_scheduler.py"
    replay_rel = "tools/system/tool_replay_sys_window.py"

    runtime_text = _read_text(repo_root, runtime_rel)
    for token in (
        "artifact.record.system_tier_change",
        "system_tier_change_event_rows",
        "process.system_collapse",
        "process.system_expand",
        "control_decision_log",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_collapse_smell",
                severity="RISK",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["SYS runtime missing tier/collapse logging token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-TIER-TRANSITION"],
                related_paths=[runtime_rel, scheduler_rel, replay_rel],
            )
        )

    replay_text = _read_text(repo_root, replay_rel)
    for token in (
        "verify_sys_replay_window(",
        "system_collapse_expand_hash_chain",
        "macro_output_record_hash_chain",
    ):
        if token in replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_collapse_smell",
                severity="RISK",
                confidence=0.9,
                file_path=replay_rel,
                line=1,
                evidence=["SYS replay verifier missing collapse/transition proof token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-TIER-TRANSITION"],
                related_paths=[replay_rel, runtime_rel],
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
        scheduler_rel,
        "src/system/system_collapse_engine.py",
        "src/system/system_expand_engine.py",
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
                    if not _TIER_MUTATION_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.silent_collapse_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential silent SYS collapse/expand mutation outside canonical process/runtime pathways",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-SILENT-TIER-TRANSITION"],
                            related_paths=[rel_path, runtime_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
