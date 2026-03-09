"""E374 nondeterministic climate smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E374_NONDETERMINISTIC_CLIMATE_SMELL"
SEASON_ENGINE_REL = "src/worldgen/earth/season_phase_engine.py"
CLIMATE_ENGINE_REL = "src/worldgen/earth/climate_field_engine.py"
PROCESS_RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
CLIMATE_PROBE_REL = "tools/worldgen/earth2_probe.py"
CLIMATE_REPLAY_REL = "tools/worldgen/tool_replay_climate_window.py"
CLIMATE_DOC_REL = "docs/worldgen/EARTH_SEASONAL_CLIMATE_MODEL.md"
REQUIRED_TOKENS = {
    CLIMATE_ENGINE_REL: (
        "build_earth_climate_update_plan(",
        "due_bucket_ids(",
        "climate_bucket_id(",
        "evaluate_earth_tile_climate(",
    ),
    PROCESS_RUNTIME_REL: (
        "_recompute_earth_climate_fields(",
        "process.earth_climate_tick",
        "tick_window_span",
        "earth_climate_tile_overlays",
    ),
    CLIMATE_PROBE_REL: (
        "run_climate_tick_fixture",
        "verify_climate_window_replay",
        "climate_year_delta_report",
    ),
    CLIMATE_REPLAY_REL: (
        "verify_climate_window_replay",
        "EARTH-2 seasonal climate replay determinism",
    ),
    CLIMATE_DOC_REL: (
        "wall-clock time is forbidden",
        "skipped intermediate ticks may affect which buckets are due",
        "replayed batched execution must match step-by-step canonical hashes",
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
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_climate_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-2 climate artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-CLIMATE-DETERMINISTIC", "INV-NO-WALLCLOCK-CLIMATE"],
                    related_paths=[SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, PROCESS_RUNTIME_REL, CLIMATE_PROBE_REL, CLIMATE_REPLAY_REL, CLIMATE_DOC_REL],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_climate_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic climate marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CLIMATE-DETERMINISTIC", "INV-NO-WALLCLOCK-CLIMATE"],
                    related_paths=[SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, PROCESS_RUNTIME_REL, CLIMATE_PROBE_REL, CLIMATE_REPLAY_REL, CLIMATE_DOC_REL],
                )
            )

    for rel_path in (SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, PROCESS_RUNTIME_REL, CLIMATE_PROBE_REL, CLIMATE_REPLAY_REL):
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
                    category="worldgen.nondeterministic_climate_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden nondeterministic climate token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CLIMATE-DETERMINISTIC", "INV-NO-WALLCLOCK-CLIMATE"],
                    related_paths=[SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, PROCESS_RUNTIME_REL, CLIMATE_PROBE_REL, CLIMATE_REPLAY_REL],
                )
            )
            break
    return findings
