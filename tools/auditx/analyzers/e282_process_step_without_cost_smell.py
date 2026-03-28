"""E282 process-step-without-cost smell analyzer."""

from __future__ import annotations

import json
import os
from typing import Iterable, Mapping

from analyzers.base import make_finding


ANALYZER_ID = "E282_PROCESS_STEP_WITHOUT_COST_SMELL"


class ProcessStepWithoutCostSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _iter_candidate_json_files(repo_root: str) -> Iterable[str]:
    roots = (
        os.path.join(repo_root, "data"),
        os.path.join(repo_root, "packs"),
    )
    for root in roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".json"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                yield rel_path


def _walk_for_steps(node: object) -> Iterable[tuple[list[dict], str]]:
    if isinstance(node, Mapping):
        graph = dict(node.get("step_graph") or {}) if isinstance(node.get("step_graph"), Mapping) else {}
        steps = list(graph.get("steps") or []) if isinstance(graph.get("steps"), list) else []
        if steps:
            yield [dict(item) for item in steps if isinstance(item, Mapping)], str(node.get("process_id", "")).strip()
        for value in node.values():
            yield from _walk_for_steps(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_for_steps(value)


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path in sorted(set(_iter_candidate_json_files(repo_root))):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        payload = _load_json(abs_path)
        if not payload:
            continue
        for steps, process_id in _walk_for_steps(payload):
            for index, step in enumerate(steps):
                step_id = str(step.get("step_id", "")).strip() or "step@{}".format(index)
                kind = str(step.get("step_kind", "")).strip()
                if not kind:
                    continue
                if "cost_units" in step and int(step.get("cost_units", 0) or 0) >= 0:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.process_step_without_cost_smell",
                        severity="RISK",
                        confidence=0.9,
                        file_path=rel_path,
                        line=1,
                        evidence=[
                            "process step missing required cost_units",
                            "process_id={}".format(process_id or "<unknown>"),
                            "step_id={}".format(step_id),
                        ],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="REWRITE",
                        related_invariants=[
                            "INV-PROCESS-STEPS-MAP-TO-ACTION-GRAMMAR",
                        ],
                        related_paths=[
                            rel_path,
                            "process/process_definition_validator.py",
                        ],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
