"""E100 interior information leak smell analyzer for INT-3 diegetic inspection."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E100_INTERIOR_INFO_LEAK_SMELL"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
INSPECTION_ENGINE_PATH = "src/inspection/inspection_engine.py"
OVERLAY_PATH = "src/client/interaction/inspection_overlays.py"

REQUIRED_OBSERVATION_TOKENS = (
    "ch.diegetic.pressure_status",
    "ch.diegetic.oxygen_status",
    "ch.diegetic.door_indicator",
    "_viewer_graph_portal_entity_ids(",
)
REQUIRED_INSPECTION_TOKENS = (
    "section.interior.connectivity_summary",
    "section.interior.portal_state_table",
    "section.interior.pressure_summary",
    "section.interior.flood_summary",
    "section.interior.smoke_summary",
    "section.interior.flow_summary",
    "allow_hidden_state",
)
REQUIRED_OVERLAY_TOKENS = (
    "_interior_overlay_payload(",
    "section.interior.pressure_summary",
    "section.interior.portal_state_table",
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
        (INSPECTION_ENGINE_PATH, REQUIRED_INSPECTION_TOKENS),
        (OVERLAY_PATH, REQUIRED_OVERLAY_TOKENS),
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interior.interior_info_leak_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["required INT-3 integration file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-INTERIOR-STATE-DIEGETIC-GATED",
                        "INV-NO-OMNISCIENT-INTERIOR-UI",
                    ],
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
                    category="interior.interior_info_leak_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing required INT-3 token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=[
                        "INV-INTERIOR-STATE-DIEGETIC-GATED",
                        "INV-NO-OMNISCIENT-INTERIOR-UI",
                    ],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

