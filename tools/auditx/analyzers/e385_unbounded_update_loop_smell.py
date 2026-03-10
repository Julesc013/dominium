"""E385 EARTH-9 unbounded update-loop smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E385_UNBOUNDED_UPDATE_LOOP_SMELL"
STRESS_COMMON_REL = "tools/earth/earth9_stress_common.py"
STRESS_TOOL_REL = "tools/earth/tool_run_earth_mvp_stress.py"
VIEW_REPLAY_REL = "tools/earth/tool_replay_earth_view_window.py"
PHYSICS_REPLAY_REL = "tools/earth/tool_replay_earth_physics_window.py"
FINAL_AUDIT_REL = "docs/audit/EARTH_MVP_FINAL_BASELINE.md"
REQUIRED_TOKENS = {
    STRESS_COMMON_REL: (
        "CLIMATE_MAX_TILES_PER_UPDATE",
        "WIND_MAX_TILES_PER_UPDATE",
        "TIDE_MAX_TILES_PER_UPDATE",
        "sampling_bounded_report(",
        '"debug_view_limit"',
        '"debug_throttled_view_count"',
        '"map_downsampled"',
        '"explain.view_downsampled"',
    ),
    STRESS_TOOL_REL: (
        "verify_earth_mvp_stress_scenario(",
        "EARTH-9 MVP stress validation",
    ),
    FINAL_AUDIT_REL: (
        "EARTH-9 preserves bounded update envelopes.",
        "Hydrology local recompute region size remained 1 tile.",
        "Deterministic degradation remained explicit through `explain.view_downsampled`.",
    ),
}
FORBIDDEN_TOKENS = ("while ", "time.sleep(", "datetime.now(", "time.time(")


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
    related_paths = [STRESS_COMMON_REL, STRESS_TOOL_REL, VIEW_REPLAY_REL, PHYSICS_REPLAY_REL, FINAL_AUDIT_REL]
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="earth.unbounded_update_loop_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-9 bounded-update surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-EARTH-UPDATES-BOUNDED"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="earth.unbounded_update_loop_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-9 bounded-update marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-UPDATES-BOUNDED"],
                    related_paths=related_paths,
                )
            )
    for rel_path in (STRESS_COMMON_REL, STRESS_TOOL_REL, VIEW_REPLAY_REL, PHYSICS_REPLAY_REL):
        text = _read_text(repo_root, rel_path)
        for line_no, line in enumerate(str(text or "").splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="earth.unbounded_update_loop_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden EARTH-9 unbounded-update token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-UPDATES-BOUNDED"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
