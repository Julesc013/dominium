"""E412 missing degrade rule smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E412_MISSING_DEGRADE_RULE_SMELL"
REQUIRED_TOKENS = {
    "data/registries/degrade_ladder_registry.json": (
        '"ladder.client.mvp"',
        '"ladder.server.mvp"',
        '"ladder.engine.mvp"',
        '"ladder.game.mvp"',
        '"ladder.setup.mvp"',
        '"ladder.launcher.mvp"',
        '"ladder.tool.mvp"',
    ),
    "data/registries/capability_fallback_registry.json": (
        '"cap.ui.rendered"',
        '"cap.logic.compiled_automaton"',
        '"cap.geo.atlas_unwrap"',
        '"cap.logic.protocol_layer"',
    ),
    "docs/compat/DEGRADE_LADDERS.md": (
        "first applicable rule wins",
        "switch_to_read_only",
    ),
}


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
    related_paths = sorted(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.degrade.missing_degrade_rule_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required degrade-ladder surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-DEGRADE-LADDER-DECLARED", "INV-DEGRADE-PLAN-DECLARED"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.degrade.missing_degrade_rule_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing degrade-ladder marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DEGRADE-LADDER-DECLARED", "INV-DEGRADE-PLAN-DECLARED"],
                    related_paths=related_paths,
                )
            )
    return findings
