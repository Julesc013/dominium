"""A1 Duplicate Concept Analyzer."""

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "A1_DUPLICATE_CONCEPT"
WATCH_PREFIXES = ("schema/", "data/registries/", "docs/")

SCHEMA_ID_RE = re.compile(r"^\s*schema_id\s*:\s*([A-Za-z0-9_.-]+)\s*$", re.MULTILINE)


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    schema_root = os.path.join(repo_root, "schema")
    schema_map = {}
    for root, dirs, files in os.walk(schema_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.lower().endswith(".schema"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, repo_root).replace("\\", "/")
            text = _read(path)
            match = SCHEMA_ID_RE.search(text)
            schema_id = match.group(1) if match else rel
            schema_map.setdefault(schema_id, []).append(rel)

    findings = []
    for schema_id in sorted(schema_map.keys()):
        refs = sorted(schema_map[schema_id])
        if len(refs) <= 1:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="semantic.duplicate_concept",
                severity="RISK",
                confidence=0.88,
                file_path=refs[0],
                evidence=[
                    "Duplicate schema_id detected: {}".format(schema_id),
                    "Definitions: {}".format(", ".join(refs[:6])),
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-SCHEMA-ID-UNIQUENESS"],
                related_paths=refs,
            )
        )
    return findings

