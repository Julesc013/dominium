"""A2 Schema Shadowing Analyzer."""

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "A2_SCHEMA_SHADOWING"
WATCH_PREFIXES = ("schema/", "data/packs/", "data/registries/")

SCHEMA_ID_RE = re.compile(r'["\']schema_id["\']\s*:\s*["\']([A-Za-z0-9_.-]+)["\']')
SCHEMA_DECL_RE = re.compile(r"^\s*schema_id\s*:\s*([A-Za-z0-9_.-]+)\s*$", re.MULTILINE)


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    core_schema_ids = set()
    schema_root = os.path.join(repo_root, "schema")
    for root, dirs, files in os.walk(schema_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.lower().endswith(".schema"):
                continue
            path = os.path.join(root, name)
            text = _read(path)
            match = SCHEMA_DECL_RE.search(text)
            if match:
                core_schema_ids.add(match.group(1))

    findings = []
    probe_roots = [
        os.path.join(repo_root, "data", "packs"),
        os.path.join(repo_root, "data", "registries"),
    ]
    for probe_root in probe_roots:
        if not os.path.isdir(probe_root):
            continue
        for root, dirs, files in os.walk(probe_root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                if not name.lower().endswith((".json", ".yaml", ".yml")):
                    continue
                path = os.path.join(root, name)
                rel = os.path.relpath(path, repo_root).replace("\\", "/")
                text = _read(path)
                for match in sorted(set(SCHEMA_ID_RE.findall(text))):
                    if match not in core_schema_ids:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="semantic.schema_shadowing",
                            severity="WARN",
                            confidence=0.76,
                            file_path=rel,
                            evidence=[
                                "Pack/registry references core schema_id in extensible surface: {}".format(match),
                                "Review for shadowing or override semantics.",
                            ],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="ADD_TEST",
                            related_invariants=["INV-SCHEMA-SHADOWING-CONTROL"],
                            related_paths=[rel],
                        )
                    )
                    if len(findings) >= 120:
                        return findings
    return findings

