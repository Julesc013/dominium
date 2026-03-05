"""E280 output depends on undeclared field smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E280_OUTPUT_DEPENDS_ON_UNDECLARED_FIELD_SMELL"


class OutputDependsOnUndeclaredFieldSmell:
    analyzer_id = ANALYZER_ID


_OUTPUT_FIELD_ASSIGN_PATTERN = re.compile(
    r"(?:output_affecting_state_fields|state_vector_output_fields)\s*[:=]",
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

    collapse_rel = "src/system/system_collapse_engine.py"
    statevec_rel = "src/system/statevec/statevec_engine.py"
    collapse_text = _read_text(repo_root, collapse_rel)
    statevec_text = _read_text(repo_root, statevec_rel)

    for token, message in (
        ("detect_undeclared_output_state(", "collapse path missing undeclared output-state guard"),
        ("state_vector_violation_rows", "collapse path missing state-vector violation logging"),
    ):
        if token in collapse_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.output_depends_on_undeclared_field_smell",
                severity="RISK",
                confidence=0.95,
                file_path=collapse_rel,
                line=1,
                evidence=["STATEVEC debug guard token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNDECLARED-STATE-MUTATION"],
                related_paths=[collapse_rel, statevec_rel],
            )
        )

    if "REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD" not in statevec_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.output_depends_on_undeclared_field_smell",
                severity="RISK",
                confidence=0.9,
                file_path=statevec_rel,
                line=1,
                evidence=[
                    "statevec engine missing canonical undeclared-output-field refusal code",
                    "REFUSAL_STATEVEC_UNDECLARED_OUTPUT_FIELD",
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNDECLARED-STATE-MUTATION"],
                related_paths=[statevec_rel],
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
        statevec_rel,
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
                    if not _OUTPUT_FIELD_ASSIGN_PATTERN.search(snippet):
                        continue
                    if "state_vector" in snippet.lower():
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.output_depends_on_undeclared_field_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential output-affecting field declaration outside explicit state-vector pathway",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-UNDECLARED-STATE-MUTATION"],
                            related_paths=[rel_path, collapse_rel, statevec_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
