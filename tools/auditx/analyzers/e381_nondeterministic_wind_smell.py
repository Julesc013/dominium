"""E381 nondeterministic wind smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E381_NONDETERMINISTIC_WIND_SMELL"
WIND_ENGINE_REL = "worldgen/earth/wind/wind_field_engine.py"
PROCESS_RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
WIND_PROBE_REL = "tools/worldgen/earth7_probe.py"
WIND_REPLAY_REL = "tools/worldgen/tool_replay_wind_window.py"
WIND_DOC_REL = "docs/worldgen/EARTH_WIND_PROXY_MODEL.md"
WIND_PARAMS_REGISTRY_REL = "data/registries/wind_params_registry.json"
REQUIRED_TOKENS = {
    WIND_ENGINE_REL: (
        "evaluate_earth_tile_wind(",
        "build_earth_wind_update_plan(",
        "wind_bucket_id(",
        "wind_tick_bucket(",
        "build_poll_advection_stub(",
    ),
    PROCESS_RUNTIME_REL: (
        "_recompute_earth_wind_fields(",
        "process.earth_wind_tick",
        "earth_wind_tile_overlays",
        "wind_window_hash",
    ),
    WIND_PARAMS_REGISTRY_REL: (
        "\"wind_params_id\": \"wind.earth_stub_default\"",
        "\"update_interval_ticks\"",
        "\"seasonal_shift_amplitude\"",
    ),
    WIND_PROBE_REL: (
        "run_wind_tick_fixture",
        "verify_wind_window_replay",
        "wind_latitude_band_report",
        "wind_seasonal_shift_report",
    ),
    WIND_REPLAY_REL: (
        "verify_wind_window_replay",
        "EARTH-7 wind replay determinism",
    ),
    WIND_DOC_REL: (
        "Mutation occurs only through `process.earth_wind_tick`.",
        "deterministic bucket scheduling",
        "time warp is lawful because wind evaluation depends only on canonical tick buckets and stable tile identity",
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
    related_paths = [WIND_ENGINE_REL, PROCESS_RUNTIME_REL, WIND_PROBE_REL, WIND_REPLAY_REL, WIND_DOC_REL, WIND_PARAMS_REGISTRY_REL]
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_wind_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-7 wind artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-WIND-DETERMINISTIC", "INV-NO-WALLCLOCK-WIND"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_wind_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic wind marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-WIND-DETERMINISTIC", "INV-NO-WALLCLOCK-WIND"],
                    related_paths=related_paths,
                )
            )

    for rel_path in (WIND_ENGINE_REL, PROCESS_RUNTIME_REL, WIND_PROBE_REL, WIND_REPLAY_REL):
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
                    category="worldgen.nondeterministic_wind_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden nondeterministic wind token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-WIND-DETERMINISTIC"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
