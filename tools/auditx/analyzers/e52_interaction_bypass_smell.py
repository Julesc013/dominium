"""E52 interaction bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E52_INTERACTION_BYPASS_SMELL"
WATCH_PREFIXES = (
    "src/client/interaction/",
    "tools/interaction/",
    "tools/xstack/sessionx/interaction.py",
)
DISPATCH_PATH = "src/client/interaction/interaction_dispatch.py"
SURFACE_PATHS = (
    "src/client/interaction/affordance_generator.py",
    "src/client/interaction/interaction_dispatch.py",
    "src/client/interaction/preview_generator.py",
    "src/client/interaction/inspection_overlays.py",
    "src/client/interaction/interaction_panel.py",
    "tools/interaction/interaction_cli.py",
    "tools/xstack/sessionx/interaction.py",
)
TRUTH_MUTATION_PATTERN = re.compile(
    r"\[\s*['\"](agent_states|world_assemblies|history_anchors|process_log|cohort_assemblies|faction_assemblies|"
    r"territory_assemblies|body_assemblies|macro_capsules|micro_regions|simulation_time|time_control)['\"]\s*\]\s*="
)
TRUTH_SYMBOL_PATTERN = re.compile(r"\b(truth_model|truthmodel)\b", re.IGNORECASE)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    dispatch_text = _read_text(repo_root, DISPATCH_PATH)
    if not dispatch_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.interaction_bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=DISPATCH_PATH,
                line=1,
                evidence=["interaction dispatch file missing; cannot verify intent-only execution path."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-INTERACTION-INTENTS-ONLY"],
                related_paths=[DISPATCH_PATH],
            )
        )
    else:
        for token in (
            "def run_interaction_command(",
            "build_affordance_list(",
            "build_interaction_intent(",
            "build_interaction_envelope(",
            "execute_intent(",
            "interact.list_affordances",
            "interact.execute",
        ):
            if token in dispatch_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interaction.interaction_bypass_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=DISPATCH_PATH,
                    line=1,
                    evidence=["missing interaction dispatch token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-INTERACTION-INTENTS-ONLY"],
                    related_paths=[DISPATCH_PATH],
                )
            )

    for rel_path in SURFACE_PATHS:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interaction.interaction_bypass_smell",
                    severity="RISK",
                    confidence=0.93,
                    file_path=rel_path,
                    line=1,
                    evidence=["interaction surface file missing."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-UI-NEVER-MUTATES-TRUTH", "INV-INTERACTION-INTENTS-ONLY"],
                    related_paths=[rel_path],
                )
            )
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            snippet = str(line).strip()
            if not snippet:
                continue
            if "execute_intent(" in snippet and rel_path != DISPATCH_PATH:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="interaction.interaction_bypass_smell",
                        severity="VIOLATION",
                        confidence=0.95,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "interaction surface invoked process runtime directly outside canonical dispatch path",
                            snippet[:200],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-INTERACTION-INTENTS-ONLY"],
                        related_paths=[DISPATCH_PATH, rel_path],
                    )
                )
            if TRUTH_SYMBOL_PATTERN.search(snippet) or TRUTH_MUTATION_PATTERN.search(snippet):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="interaction.interaction_bypass_smell",
                        severity="VIOLATION",
                        confidence=0.93,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "interaction surface touched forbidden truth symbols/mutation pattern",
                            snippet[:200],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-UI-NEVER-MUTATES-TRUTH"],
                        related_paths=[rel_path],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
