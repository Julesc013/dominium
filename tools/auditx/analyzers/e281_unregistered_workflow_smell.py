"""E281 unregistered-workflow smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E281_UNREGISTERED_WORKFLOW_SMELL"


class UnregisteredWorkflowSmell:
    analyzer_id = ANALYZER_ID


_WORKFLOW_PATTERNS = (
    re.compile(r"\bad_hoc_workflow\b", re.IGNORECASE),
    re.compile(r"\bmanual_workflow\b", re.IGNORECASE),
    re.compile(r"\bworkflow_steps?\b", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    process_registry_rel = "data/registries/process_registry.json"
    process_payload = _load_json(repo_root, process_registry_rel)
    rows = list(process_payload.get("records") or [])
    process_ids = set(
        str(row.get("process_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("process_id", "")).strip()
    )

    for process_id in (
        "process.process_run_start",
        "process.process_run_tick",
        "process.process_run_end",
    ):
        if process_id in process_ids:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unregistered_workflow_smell",
                severity="RISK",
                confidence=0.9,
                file_path=process_registry_rel,
                line=1,
                evidence=["required PROC process lifecycle id missing", process_id],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-NO-RECIPE-HACKS",
                    "INV-PROCESS-CAPSULE-REQUIRES-STABILIZED",
                ],
                related_paths=[
                    process_registry_rel,
                    "docs/process/PROCESS_CONSTITUTION.md",
                ],
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
        "tools/xstack/repox/check.py",
        "tools/xstack/sessionx/process_runtime.py",
        "chem/process_run_engine.py",
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
                    if not any(pattern.search(snippet) for pattern in _WORKFLOW_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unregistered_workflow_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["workflow token detected outside registered process pathways", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-RECIPE-HACKS",
                            ],
                            related_paths=[
                                rel_path,
                                process_registry_rel,
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
