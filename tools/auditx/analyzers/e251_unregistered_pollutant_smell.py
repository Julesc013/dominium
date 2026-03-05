"""E251 unregistered pollutant smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E251_UNREGISTERED_POLLUTANT_SMELL"


class UnregisteredPollutantSmell:
    analyzer_id = ANALYZER_ID


_POLLUTANT_LITERAL_PATTERN = re.compile(
    r"[\"'](pollutant\.[a-z0-9_]+)[\"']",
    re.IGNORECASE,
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_pollutant_ids(repo_root: str):
    rel_path = "data/registries/pollutant_type_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return set(), rel_path
    rows = list((dict(payload.get("record") or {})).get("pollutant_types") or [])
    out = set(
        str(row.get("pollutant_id", "")).strip().lower()
        for row in rows
        if isinstance(row, dict) and str(row.get("pollutant_id", "")).strip()
    )
    return out, rel_path


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

    declared_pollutants, registry_rel = _load_pollutant_ids(repo_root)
    if not declared_pollutants:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="registry.unregistered_pollutant_smell",
                severity="RISK",
                confidence=0.95,
                file_path=registry_rel,
                line=1,
                evidence=[
                    "pollutant_type_registry missing/invalid or empty",
                    "cannot validate pollutant literals against canonical registry",
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-POLLUTANT-TYPE-REGISTERED"],
                related_paths=[registry_rel],
            )
        )
        return findings

    ignored_literals = {
        "pollutant.coarse",
    }
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
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if ("pollutant_id" not in snippet) and ("pollutant_type_id" not in snippet):
                        continue
                    literals = [
                        str(token).strip().lower()
                        for token in _POLLUTANT_LITERAL_PATTERN.findall(snippet)
                    ]
                    if not literals:
                        continue
                    for literal in literals:
                        if literal in ignored_literals:
                            continue
                        if literal in declared_pollutants:
                            continue
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="registry.unregistered_pollutant_smell",
                                severity="RISK",
                                confidence=0.93,
                                file_path=rel_path,
                                line=line_no,
                                evidence=[
                                    "pollutant literal is not declared in pollutant_type_registry",
                                    snippet[:140],
                                ],
                                suggested_classification="NEEDS_REVIEW",
                                recommended_action="REWRITE",
                                related_invariants=["INV-POLLUTANT-TYPE-REGISTERED"],
                                related_paths=[rel_path, registry_rel],
                            )
                        )
                        break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
