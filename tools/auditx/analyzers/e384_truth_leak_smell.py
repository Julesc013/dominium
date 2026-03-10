"""E384 EARTH-9 truth leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E384_TRUTH_LEAK_SMELL"
STRESS_COMMON_REL = "tools/earth/earth9_stress_common.py"
VIEW_REPLAY_REL = "tools/earth/tool_replay_earth_view_window.py"
FINAL_AUDIT_REL = "docs/audit/EARTH_MVP_FINAL_BASELINE.md"
REQUIRED_TOKENS = {
    STRESS_COMMON_REL: (
        "_view_truth_leak_report(",
        '"no_truth_leaks_in_views"',
        '"sky_surfaces"',
        '"illumination_surfaces"',
        '"water_view_surface"',
        '"map_view_surface"',
    ),
    VIEW_REPLAY_REL: (
        "replay_earth_view_window(",
        "derived view windows",
    ),
    FINAL_AUDIT_REL: (
        "EARTH-9 keeps Earth presentation derived-view only.",
        "No new truth-read bridge was introduced into UI or render surfaces.",
    ),
}
FORBIDDEN_TOKENS = (
    "truth_model[",
    "truth_model.",
    "universe_state[",
    "universe_state.",
    "process_runtime[",
    "process_runtime.",
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
    related_paths = [STRESS_COMMON_REL, VIEW_REPLAY_REL, FINAL_AUDIT_REL]
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="earth.truth_leak_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-9 truth-leak guard surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-EARTH-VIEWS-DERIVED-ONLY"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="earth.truth_leak_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-9 truth-leak marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-VIEWS-DERIVED-ONLY"],
                    related_paths=related_paths,
                )
            )
    for rel_path in (STRESS_COMMON_REL, VIEW_REPLAY_REL):
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
                    category="earth.truth_leak_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden EARTH-9 truth-access token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-VIEWS-DERIVED-ONLY"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
