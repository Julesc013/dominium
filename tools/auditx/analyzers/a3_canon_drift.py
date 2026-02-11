"""A3 Canon drift analyzer."""

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "A3_CANON_DRIFT"
HEADER_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
NORMATIVE_RE = re.compile(r"\b(must|required|forbid|shall|never)\b", re.IGNORECASE)
ENFORCEMENT_RE = re.compile(r"\b(RepoX|TestX|AuditX|INV-[A-Z0-9-]+|test[s]?)\b")


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _iter_docs(repo_root):
    docs_root = os.path.join(repo_root, "docs")
    records = []
    for root, dirs, files in os.walk(docs_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, name), repo_root).replace("\\", "/")
            if rel.startswith("docs/archive/") or rel.startswith("docs/audit/"):
                continue
            records.append(rel)
    return sorted(records)


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    title_map = {}

    for rel in _iter_docs(repo_root):
        text = _read(os.path.join(repo_root, rel.replace("/", os.sep)))
        match = HEADER_RE.search(text)
        title = match.group(1).strip().lower() if match else rel.lower()
        title_map.setdefault(title, []).append(rel)

        if NORMATIVE_RE.search(text) and not ENFORCEMENT_RE.search(text):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="canon_drift",
                    severity="WARN",
                    confidence=0.65,
                    file_path=rel,
                    evidence=[
                        "Normative language detected but no explicit enforcement anchor found.",
                        "Consider linking invariant IDs or tests for this behavior.",
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=[],
                    related_paths=[rel],
                )
            )

    for title, paths in sorted(title_map.items()):
        if len(paths) <= 1:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="canon_drift",
                severity="WARN",
                confidence=0.60,
                file_path=paths[0],
                evidence=[
                    "Duplicate/overlapping doc title detected: {}".format(title),
                    "Paths: {}".format(", ".join(sorted(paths))),
                ],
                suggested_classification="SUPERSEDED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-CANON-INDEX"],
                related_paths=sorted(paths),
            )
        )
        if len(findings) >= 80:
            break

    return sorted(findings, key=lambda item: (item.location.file, item.severity))
