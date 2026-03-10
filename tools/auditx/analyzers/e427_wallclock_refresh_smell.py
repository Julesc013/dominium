"""E427 wallclock refresh smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E427_WALLCLOCK_REFRESH_SMELL"
DOCTRINE_REL = "docs/appshell/TUI_FRAMEWORK.md"
ENGINE_REL = "src/appshell/tui/tui_engine.py"
REQUIRED_DOCTRINE_TOKENS = (
    "render ordering must not depend on wall-clock timing",
    "refresh is event-driven or fixed-iteration driven",
)
FORBIDDEN_ENGINE_TOKENS = (
    "time.sleep(",
    "time.monotonic(",
    "time.perf_counter(",
    "datetime.now(",
    "datetime.utcnow(",
)


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
    related_paths = [DOCTRINE_REL, ENGINE_REL]
    doctrine_text = _read_text(repo_root, DOCTRINE_REL)
    missing = [token for token in REQUIRED_DOCTRINE_TOKENS if token not in doctrine_text]
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.wallclock_refresh_smell",
                severity="RISK",
                confidence=0.96,
                file_path=DOCTRINE_REL,
                line=1,
                evidence=["missing refresh-doctrine marker(s): {}".format(", ".join(missing[:3]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-TUI-DETERMINISTIC-ORDER"],
                related_paths=related_paths,
            )
        )
    engine_text = _read_text(repo_root, ENGINE_REL)
    for token in FORBIDDEN_ENGINE_TOKENS:
        if token in engine_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.wallclock_refresh_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=ENGINE_REL,
                    line=1,
                    evidence=["forbidden wallclock refresh token '{}' detected in TUI engine".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-TUI-DETERMINISTIC-ORDER", "INV-NO-WALLCLOCK-IN-SIM"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
