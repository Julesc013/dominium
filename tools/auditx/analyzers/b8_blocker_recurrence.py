"""A8 Blocker Recurrence Analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "A8_BLOCKER_RECURRENCE"
WATCH_PREFIXES = ("docs/audit/remediation/",)
RECURRENCE_THRESHOLD = 2


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    root = os.path.join(repo_root, "docs", "audit", "remediation")
    if not os.path.isdir(root):
        return []

    counts = {}
    paths_by_code = {}
    for walk_root, dirs, files in os.walk(root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if name != "failure.json":
                continue
            abs_path = os.path.join(walk_root, name)
            rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
            payload = _load_json(abs_path)
            if not isinstance(payload, dict):
                continue
            code = str(payload.get("refusal_code", "")).strip() or str(payload.get("blocker_type", "")).strip()
            if not code:
                continue
            counts[code] = counts.get(code, 0) + 1
            paths_by_code.setdefault(code, []).append(rel)

    findings = []
    for code in sorted(counts.keys()):
        count = counts[code]
        if count <= RECURRENCE_THRESHOLD:
            continue
        refs = sorted(paths_by_code.get(code, []))
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="semantic.blocker_recurrence",
                severity="RISK",
                confidence=0.84,
                file_path=refs[0] if refs else "docs/audit/remediation",
                evidence=[
                    "Recurring blocker/refusal code detected across remediation artifacts.",
                    "Code '{}' seen {} times.".format(code, count),
                ],
                suggested_classification="LEGACY",
                recommended_action="ADD_RULE",
                related_invariants=["INV-PREVENTION-REQUIRED"],
                related_paths=refs[:12],
            )
        )
    return findings

