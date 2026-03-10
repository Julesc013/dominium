"""E383 EARTH-9 nondeterministic view smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E383_NONDETERMINISTIC_VIEW_SMELL"
STRESS_COMMON_REL = "tools/earth/earth9_stress_common.py"
STRESS_TOOL_REL = "tools/earth/tool_run_earth_mvp_stress.py"
VIEW_REPLAY_REL = "tools/earth/tool_replay_earth_view_window.py"
PHYSICS_REPLAY_REL = "tools/earth/tool_replay_earth_physics_window.py"
BASELINE_REL = "data/regression/earth_mvp_baseline.json"
FINAL_AUDIT_REL = "docs/audit/EARTH_MVP_FINAL_BASELINE.md"
REQUIRED_TOKENS = {
    STRESS_COMMON_REL: (
        "generate_earth_mvp_stress_scenario(",
        "verify_earth_mvp_stress_scenario(",
        "replay_earth_view_window(",
        "replay_earth_physics_window(",
        '"cross_platform_determinism_hash"',
    ),
    STRESS_TOOL_REL: (
        "verify_earth_mvp_stress_scenario(",
        "DEFAULT_EARTH9_SEED",
    ),
    VIEW_REPLAY_REL: (
        "replay_earth_view_window(",
        "DEFAULT_EARTH9_SEED",
    ),
    PHYSICS_REPLAY_REL: (
        "replay_earth_physics_window(",
        "DEFAULT_EARTH9_SEED",
    ),
    BASELINE_REL: (
        '"required_commit_tag": "EARTH-REGRESSION-UPDATE"',
        '"cross_platform_determinism_hash"',
    ),
    FINAL_AUDIT_REL: (
        "cross-platform determinism hash",
        "EARTH-9 regression lock updates require `EARTH-REGRESSION-UPDATE`.",
    ),
}
FORBIDDEN_TOKENS = ("random.", "uuid", "secrets.", "time.time(", "datetime.now(", "os.urandom(", "random.seed(", "time.sleep(")


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
    related_paths = [STRESS_COMMON_REL, STRESS_TOOL_REL, VIEW_REPLAY_REL, PHYSICS_REPLAY_REL, BASELINE_REL, FINAL_AUDIT_REL]
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="earth.nondeterministic_view_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-9 deterministic view surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-EARTH-DETERMINISTIC"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="earth.nondeterministic_view_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-9 deterministic marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-DETERMINISTIC"],
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
                    category="earth.nondeterministic_view_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden EARTH-9 nondeterministic token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-DETERMINISTIC"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
