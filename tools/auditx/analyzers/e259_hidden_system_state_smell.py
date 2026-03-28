"""E259 hidden system state smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E259_HIDDEN_SYSTEM_STATE_SMELL"


class HiddenStateSmell:
    analyzer_id = ANALYZER_ID


_HIDDEN_STATE_PATTERN = re.compile(
    r"\b(system_internal_cache|hidden_system_state|private_capsule_cache|opaque_runtime_state)\b",
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
    collapse_text = _read_text(repo_root, collapse_rel)
    expand_text = _read_text(repo_root, expand_rel)

    for token in (
        "serialized_internal_state",
        "provenance_anchor_hash",
        "build_system_state_vector_row(",
    ):
        if token in collapse_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.hidden_system_state_smell",
                severity="RISK",
                confidence=0.95,
                file_path=collapse_rel,
                line=1,
                evidence=["SYS collapse engine missing required explicit state capture/provenance token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-HIDDEN-SYSTEM-STATE"],
                related_paths=[collapse_rel, expand_rel],
            )
        )

    for token in (
        "provenance_anchor_hash",
        "REFUSAL_SYSTEM_EXPAND_HASH_MISMATCH",
        "serialized_internal_state",
    ):
        if token in expand_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.hidden_system_state_smell",
                severity="RISK",
                confidence=0.92,
                file_path=expand_rel,
                line=1,
                evidence=["SYS expand engine missing required provenance/state validation token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-HIDDEN-SYSTEM-STATE"],
                related_paths=[expand_rel],
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
        collapse_rel,
        expand_rel,
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
                    if not _HIDDEN_STATE_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.hidden_system_state_smell",
                            severity="RISK",
                            confidence=0.88,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential hidden system state token detected",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-HIDDEN-SYSTEM-STATE"],
                            related_paths=[rel_path, collapse_rel, expand_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
