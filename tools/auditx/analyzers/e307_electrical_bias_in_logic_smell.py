"""E307 electrical-bias-in-logic smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E307_ELECTRICAL_BIAS_IN_LOGIC_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e307_electrical_bias_in_logic_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/",
    "schema/logic/",
    "data/registries/signal_type_registry.json",
    "src/logic/",
    "tools/logic/",
)

_FORBIDDEN_PATTERNS = (
    re.compile(r"\bvoltage\b", re.IGNORECASE),
    re.compile(r"\b(?:quantity\.elec\.current|measure\.elec\.current|electric current)\b", re.IGNORECASE),
    re.compile(r"\bohm(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bamp(?:ere)?s?\b", re.IGNORECASE),
    re.compile(r"\bpower_factor\b", re.IGNORECASE),
    re.compile(r"\breactive_power\b", re.IGNORECASE),
    re.compile(r"\bpressure(?:_head)?\b", re.IGNORECASE),
    re.compile(r"\bpascal(?:s)?\b", re.IGNORECASE),
    re.compile(r"\bpsi\b", re.IGNORECASE),
)


class ElectricalBiasInLogicSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _logic_scan_paths(repo_root: str):
    fixed_paths = (
        "schema/logic/signal_type.schema",
        "schema/logic/logic_policy.schema",
        "data/registries/signal_type_registry.json",
    )
    for rel_path in fixed_paths:
        yield rel_path
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
    constitution_text = _read_text(repo_root, constitution_rel)
    constitution_lower = constitution_text.lower()
    if constitution_text and not (
        "does not assume any physical carrier" in constitution_lower
        or "does not assume a physical carrier" in constitution_lower
        or "does not assume electricity" in constitution_lower
    ):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.electrical_bias_in_logic_smell",
                severity="RISK",
                confidence=0.87,
                file_path=constitution_rel,
                line=1,
                evidence=["logic constitution missing substrate-agnostic carrier disclaimer"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-LOGIC-SUBSTRATE-AGNOSTIC"],
                related_paths=[constitution_rel],
            )
        )

    seen = set()
    for rel_path in _logic_scan_paths(repo_root):
        if rel_path in seen:
            continue
        seen.add(rel_path)
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in _FORBIDDEN_PATTERNS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="logic.electrical_bias_in_logic_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["logic semantics layer references physical-unit term", snippet[:160]],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="REWRITE",
                    related_invariants=["INV-LOGIC-SUBSTRATE-AGNOSTIC"],
                    related_paths=[rel_path, constitution_rel],
                )
            )
            break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
