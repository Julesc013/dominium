"""C4 Terminology misuse smell analyzer."""

import os

from analyzers.base import make_finding


ANALYZER_ID = "C4_TERMINOLOGY_MISUSE"
GLOSSARY_REL = os.path.join("data", "registries", "glossary.json")


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _load_glossary(repo_root):
    import json

    path = os.path.join(repo_root, GLOSSARY_REL)
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return []
    terms = ((payload.get("record") or {}).get("terms") or [])
    rows = []
    for row in terms:
        if not isinstance(row, dict):
            continue
        display_name = str(row.get("display_name", "")).strip()
        synonyms = row.get("forbidden_synonyms") or []
        if not display_name or not isinstance(synonyms, list):
            continue
        for synonym in synonyms:
            text = str(synonym).strip().lower()
            if text and ("_" in text or "." in text or ":" in text):
                rows.append((display_name, text))
    return rows


def run(graph, repo_root, changed_files=None):
    del changed_files
    findings = []
    forbidden = _load_glossary(repo_root)
    if not forbidden:
        return findings

    for node in sorted(graph.nodes.values(), key=lambda item: item.label):
        if node.node_type != "file":
            continue
        rel = node.label
        if not rel.endswith(".md"):
            continue
        if not rel.startswith("docs/"):
            continue
        if rel.startswith("docs/archive/"):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep))).lower()
        for display_name, synonym in forbidden:
            if synonym not in text:
                continue
            is_canonical_scope = rel.startswith("docs/architecture/") or rel.startswith("docs/governance/")
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="terminology_misuse",
                    severity="RISK" if is_canonical_scope else "WARN",
                    confidence=0.80 if is_canonical_scope else 0.60,
                    file_path=rel,
                    evidence=[
                        "Found glossary-forbidden synonym '{}'.".format(synonym),
                        "Canonical term is '{}'.".format(display_name),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-GLOSSARY-TERM-CANON"],
                    related_paths=[rel, GLOSSARY_REL.replace("\\", "/")],
                )
            )
            break

    return findings
