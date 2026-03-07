"""E309 omniscient-logic-debug smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E309_OMNISCIENT_LOGIC_DEBUG_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e309_omniscient_logic_debug_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/",
    "data/registries/instrument_type_registry.json",
    "src/logic/",
    "tools/logic/",
)

_TRUTH_PATTERN = re.compile(r"\b(truth_model|universe_state|render_model)\b", re.IGNORECASE)


class OmniscientLogicDebugSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid"


def _logic_runtime_paths(repo_root: str):
    for root_rel in ("src/logic", "tools/logic"):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                rel_lower = rel_path.lower()
                if "transducer" in rel_lower or "carrier" in rel_lower:
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    constitution_rel = "docs/logic/LOGIC_CONSTITUTION.md"
    constitution_text = _read_text(repo_root, constitution_rel).lower()
    for token in ("instrumentation surfaces",):
        if token in constitution_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.omniscient_logic_debug_smell",
                severity="RISK",
                confidence=0.84,
                file_path=constitution_rel,
                line=1,
                evidence=["logic constitution missing debug instrumentation/access token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-LOGIC-DEBUG-REQUIRES-INSTRUMENTATION"],
                related_paths=[constitution_rel],
            )
        )
    if ("access policy" not in constitution_text) and ("access policies" not in constitution_text):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.omniscient_logic_debug_smell",
                severity="RISK",
                confidence=0.84,
                file_path=constitution_rel,
                line=1,
                evidence=["logic constitution missing debug instrumentation/access token", "access policy"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-LOGIC-DEBUG-REQUIRES-INSTRUMENTATION"],
                related_paths=[constitution_rel],
            )
        )

    instrument_rel = "data/registries/instrument_type_registry.json"
    instrument_payload, instrument_err = _read_json(repo_root, instrument_rel)
    instrument_rows = list((dict(instrument_payload.get("record") or {})).get("instrument_types") or instrument_payload.get("instrument_types") or [])
    known_instrument_ids = {
        str(row.get("instrument_type_id", "")).strip()
        for row in instrument_rows
        if isinstance(row, dict) and str(row.get("instrument_type_id", "")).strip()
    }
    for instrument_id in ("instrument.logic_probe", "instrument.logic_analyzer"):
        if (not instrument_err) and instrument_id in known_instrument_ids:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.omniscient_logic_debug_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=instrument_rel,
                line=1,
                evidence=["required logic instrumentation type missing", instrument_id],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-DEBUG-REQUIRES-INSTRUMENTATION"],
                related_paths=[instrument_rel],
            )
        )

    for rel_path in _logic_runtime_paths(repo_root):
        text = _read_text(repo_root, rel_path)
        if not _TRUTH_PATTERN.search(text):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.omniscient_logic_debug_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=["logic debug/readout path references omniscient truth symbol"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-LOGIC-DEBUG-REQUIRES-INSTRUMENTATION"],
                related_paths=[rel_path, instrument_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
