"""E277 invariant check skipped smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E277_INVARIANT_CHECK_SKIPPED_SMELL"


_SKIP_PATTERN = re.compile(
    r"\b(skip_invariant|skip_invariants|skip_boundary_invariant|disable_invariant_check)\b",
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

    collapse_rel = "system/system_collapse_engine.py"
    expand_rel = "system/system_expand_engine.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    stress_rel = "tools/system/tool_run_sys_stress.py"

    collapse_text = _read_text(repo_root, collapse_rel)
    expand_text = _read_text(repo_root, expand_rel)
    runtime_text = _read_text(repo_root, runtime_rel)
    stress_text = _read_text(repo_root, stress_rel)

    for token in (
        "validate_boundary_invariants(",
        "REFUSAL_SYSTEM_COLLAPSE_INVARIANT_VIOLATION",
    ):
        if token in collapse_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.invariant_check_skipped_smell",
                severity="RISK",
                confidence=0.95,
                file_path=collapse_rel,
                line=1,
                evidence=["SYS collapse engine missing invariant-enforcement token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYS-INVARIANTS-ALWAYS-CHECKED"],
                related_paths=[collapse_rel, expand_rel, runtime_rel],
            )
        )

    for token in (
        "validate_boundary_invariants(",
        "REFUSAL_SYSTEM_EXPAND_INVARIANT_VIOLATION",
    ):
        if token in expand_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.invariant_check_skipped_smell",
                severity="RISK",
                confidence=0.92,
                file_path=expand_rel,
                line=1,
                evidence=["SYS expand engine missing invariant-enforcement token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYS-INVARIANTS-ALWAYS-CHECKED"],
                related_paths=[expand_rel, runtime_rel],
            )
        )

    for token in (
        "refusal.system.invariant_violation",
        "system_tier_change_event_rows",
        "system_collapse_event_rows",
        "system_expand_event_rows",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.invariant_check_skipped_smell",
                severity="RISK",
                confidence=0.88,
                file_path=runtime_rel,
                line=1,
                evidence=["SYS runtime missing invariant-violation propagation token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYS-INVARIANTS-ALWAYS-CHECKED"],
                related_paths=[runtime_rel, collapse_rel, expand_rel],
            )
        )

    if "invariants_preserved_roundtrip" not in stress_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.invariant_check_skipped_smell",
                severity="RISK",
                confidence=0.85,
                file_path=stress_rel,
                line=1,
                evidence=["SYS stress harness missing invariant preservation assertion token", "invariants_preserved_roundtrip"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYS-INVARIANTS-ALWAYS-CHECKED"],
                related_paths=[stress_rel],
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
        collapse_rel,
        expand_rel,
        runtime_rel,
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
                    if not _SKIP_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.invariant_check_skipped_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential invariant-check bypass token detected in SYS runtime paths",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-SYS-INVARIANTS-ALWAYS-CHECKED"],
                            related_paths=[rel_path, collapse_rel, expand_rel, runtime_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
