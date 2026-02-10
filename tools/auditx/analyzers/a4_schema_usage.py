"""A4 Schema usage analyzer."""

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "A4_SCHEMA_USAGE"
SCHEMA_TOKEN_RE = re.compile(r"\b[a-z][a-z0-9_.-]{2,}\b")
KEY_ACCESS_RE = re.compile(r'\[\s*"([a-z][a-z0-9_.-]+)"\s*\]')
SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py")


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _schema_tokens(repo_root):
    tokens = set()
    schema_root = os.path.join(repo_root, "schema")
    for root, dirs, files in os.walk(schema_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if not name.lower().endswith(".schema"):
                continue
            text = _read(os.path.join(root, name))
            for token in SCHEMA_TOKEN_RE.findall(text):
                tokens.add(token)
    return tokens


def _schema_usage_counts(graph):
    counts = {}
    for edge in graph.edges:
        if edge.edge_type != "schema_usage":
            continue
        counts[edge.dst] = counts.get(edge.dst, 0) + 1
    return counts


def run(graph, repo_root, changed_files=None):
    del changed_files
    findings = []
    schema_tokens = _schema_tokens(repo_root)
    usage = _schema_usage_counts(graph)

    for node in sorted(graph.nodes.values(), key=lambda item: item.node_id):
        if node.node_type != "schema":
            continue
        if usage.get(node.node_id, 0) > 0:
            continue
        path = str(node.data.get("path", node.label))
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="schema_usage",
                severity="WARN",
                confidence=0.75,
                file_path=path,
                evidence=[
                    "Schema appears unreferenced by non-schema files in graph scan.",
                    "May indicate stale, orphaned, or not-yet-integrated schema.",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["SCHEMA_ANCHOR_REQUIRED"],
                related_paths=[path],
            )
        )
        if len(findings) >= 80:
            break

    for node in sorted(graph.nodes.values(), key=lambda item: item.label):
        if node.node_type != "file":
            continue
        rel = node.label
        if rel.startswith(("tests/", "docs/", "schema/", "data/")):
            continue
        if not rel.lower().endswith(SOURCE_EXTS):
            continue
        text = _read(os.path.join(repo_root, rel.replace("/", os.sep)))
        for match in KEY_ACCESS_RE.finditer(text):
            key = match.group(1)
            if key in schema_tokens:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="schema_usage",
                    severity="RISK",
                    confidence=0.55,
                    file_path=rel,
                    evidence=[
                        "Detected key access without obvious schema anchor: {}".format(key),
                        "Best-effort heuristic; verify if schema declaration exists.",
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["SCHEMA_ANCHOR_REQUIRED"],
                    related_paths=[rel],
                )
            )
            if len(findings) >= 160:
                break
        if len(findings) >= 160:
            break

    packs_root = os.path.join(repo_root, "data", "packs")
    if os.path.isdir(packs_root):
        for root, dirs, files in os.walk(packs_root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                if name != "pack_manifest.json":
                    continue
                path = os.path.join(root, name)
                rel = os.path.relpath(path, repo_root).replace("\\", "/")
                try:
                    payload = json.loads(_read(path) or "{}")
                except ValueError:
                    continue
                for field_name in sorted(payload.keys()):
                    if field_name in schema_tokens:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="schema_usage",
                            severity="INFO",
                            confidence=0.40,
                            file_path=rel,
                            evidence=[
                                "Pack field '{}' not found in collected schema token set.".format(field_name),
                                "Verify schema anchors for pack manifest fields.",
                            ],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="DOC_FIX",
                            related_invariants=["SCHEMA_ANCHOR_REQUIRED"],
                            related_paths=[rel],
                        )
                    )
                    if len(findings) >= 200:
                        break
                if len(findings) >= 200:
                    break
            if len(findings) >= 200:
                break

    return sorted(findings, key=lambda item: (item.location.file, item.severity))

