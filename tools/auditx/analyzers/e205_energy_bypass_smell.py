"""E205 energy bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E205_ENERGY_BYPASS_SMELL"


class EnergyBypassSmell:
    analyzer_id = ANALYZER_ID


_ENERGY_ASSIGN_PATTERNS = (
    re.compile(
        r"\b(?:energy_total|energy_kinetic|energy_potential|energy_thermal|energy_electrical|energy_chemical)\b\s*[+\-*/]?=",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bledger_deltas\b\s*=\s*\{[^\n]*quantity\.energy",
        re.IGNORECASE,
    ),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


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

    scan_roots = (
        os.path.join(repo_root, "src", "electric"),
        os.path.join(repo_root, "src", "thermal"),
        os.path.join(repo_root, "src", "mobility"),
        os.path.join(repo_root, "src", "mechanics"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "electric/power_network_engine.py",
        "thermal/network/thermal_network_engine.py",
        "reality/ledger/ledger_engine.py",
        "models/model_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
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
                    if not any(pattern.search(snippet) for pattern in _ENERGY_ASSIGN_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.energy_bypass_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["energy mutation token detected outside canonical ledger/model pathways", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-LOSS-MAPPED-TO-HEAT",
                                "INV-REALISM-DETAIL-MUST-BE-MODEL",
                            ],
                            related_paths=[
                                rel_path,
                                "docs/physics/PHYSICS_CONSTITUTION.md",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
