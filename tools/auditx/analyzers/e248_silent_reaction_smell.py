"""E248 silent reaction smell analyzer for CHEM stress/process pathways."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E248_SILENT_REACTION_SMELL"


class SilentReactionSmell:
    analyzer_id = ANALYZER_ID


_REACTION_MUTATION_HINTS = (
    re.compile(r"\breaction_id\b", re.IGNORECASE),
    re.compile(r"\binput_species\b", re.IGNORECASE),
    re.compile(r"\boutput_species\b", re.IGNORECASE),
    re.compile(r"\bchemical_energy_in\b", re.IGNORECASE),
)
_REACTION_LOG_HINTS = (
    "reaction_event_rows",
    "energy_ledger_rows",
    "emission_event_rows",
    "chem_process_run_events",
    "_record_energy_transformation_in_state(",
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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    required_runtime_tokens = (
        "event.chem.process_run.tick.",
        "chem_process_run_events",
        "chem_process_emission_rows",
        "_record_energy_transformation_in_state(",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reliability.silent_reaction_smell",
                severity="RISK",
                confidence=0.89,
                file_path=runtime_rel,
                line=1,
                evidence=[
                    "CHEM process runtime is missing a required reaction logging surface token",
                    token,
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-ALL-REACTIONS-LEDGERED",
                ],
                related_paths=[runtime_rel, "tools/chem/tool_run_chem_stress.py"],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src", "chem"),
        os.path.join(repo_root, "tools", "chem"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        runtime_rel,
        "tools/chem/tool_run_chem_stress.py",
        "tools/chem/tool_replay_chem_window.py",
        "tools/chem/tool_generate_chem_stress.py",
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
                if not any(pattern.search(text) for pattern in _REACTION_MUTATION_HINTS):
                    continue
                if any(token in text for token in _REACTION_LOG_HINTS):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="reliability.silent_reaction_smell",
                        severity="RISK",
                        confidence=0.76,
                        file_path=rel_path,
                        line=1,
                        evidence=[
                            "CHEM reaction mutation hints detected without explicit reaction/ledger/emission logging surfaces",
                            "expected one of: {}".format(", ".join(_REACTION_LOG_HINTS[:3])),
                        ],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="REWRITE",
                        related_invariants=[
                            "INV-ALL-REACTIONS-LEDGERED",
                        ],
                        related_paths=[rel_path, runtime_rel],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

