"""E96 interior occlusion leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E96_INTERIOR_OCCLUSION_LEAK_SMELL"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
INTERIOR_ENGINE_PATH = "src/interior/interior_engine.py"
INSPECTION_ENGINE_PATH = "src/inspection/inspection_engine.py"
REQUIRED_OBSERVATION_TOKENS = (
    "_apply_interior_occlusion(",
    "path_exists(",
    "interior_portal_state_machines",
    "lens.nondiegetic.freecam",
)
REQUIRED_INTERIOR_TOKENS = (
    "portal_allows_connectivity(",
    "apply_portal_transition(",
    "state_machine_id",
)
REQUIRED_INSPECTION_TOKENS = (
    "section.interior.layout",
    "section.interior.portal_states",
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

    for rel_path, tokens in (
        (OBSERVATION_PATH, REQUIRED_OBSERVATION_TOKENS),
        (INTERIOR_ENGINE_PATH, REQUIRED_INTERIOR_TOKENS),
        (INSPECTION_ENGINE_PATH, REQUIRED_INSPECTION_TOKENS),
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interior.interior_occlusion_leak_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["required interior integration file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-ADHOC-OCCLUSION", "INV-PORTAL-USES-STATE-MACHINE"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interior.interior_occlusion_leak_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=rel_path,
                    line=1,
                    evidence=["interior occlusion path missing required deterministic token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-ADHOC-OCCLUSION", "INV-PORTAL-USES-STATE-MACHINE"],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

