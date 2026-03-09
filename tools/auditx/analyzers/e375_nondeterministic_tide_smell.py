"""E375 nondeterministic tide smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E375_NONDETERMINISTIC_TIDE_SMELL"
TIDE_PHASE_ENGINE_REL = "src/worldgen/earth/tide_phase_engine.py"
TIDE_FIELD_ENGINE_REL = "src/worldgen/earth/tide_field_engine.py"
PROCESS_RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
TIDE_PROBE_REL = "tools/worldgen/earth3_probe.py"
TIDE_REPLAY_REL = "tools/worldgen/tool_replay_tide_window.py"
TIDE_DOC_REL = "docs/worldgen/EARTH_TIDE_PROXY_MODEL.md"
REQUIRED_TOKENS = {
    TIDE_PHASE_ENGINE_REL: (
        "EARTH_TIDE_PHASE_SCALE",
        "lunar_phase_from_params(",
        "rotation_phase_from_params(",
        "phase_carrier_permille(",
    ),
    TIDE_FIELD_ENGINE_REL: (
        "evaluate_earth_tile_tide(",
        "build_earth_tide_update_plan(",
        "tide_bucket_id(",
        "due_bucket_ids(",
        "build_tide_coupling_stub(",
    ),
    PROCESS_RUNTIME_REL: (
        "_recompute_earth_tide_fields(",
        "process.earth_tide_tick",
        "earth_tide_tile_overlays",
        "tide_window_hash",
    ),
    TIDE_PROBE_REL: (
        "run_tide_tick_fixture",
        "verify_tide_window_replay",
        "tide_day_delta_report",
        "inland_damping_report",
    ),
    TIDE_REPLAY_REL: (
        "verify_tide_window_replay",
        "EARTH-3 tide replay determinism",
    ),
    TIDE_DOC_REL: (
        "Mutation occurs only through `process.earth_tide_tick`.",
        "fixed-point only",
        "tide update buckets are deterministic",
        "time warp is lawful because phase depends only on canonical tick",
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
                    category="worldgen.nondeterministic_tide_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-3 tide artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-TIDE-DETERMINISTIC", "INV-NO-OCEAN-PDE-IN-MVP"],
                    related_paths=[TIDE_PHASE_ENGINE_REL, TIDE_FIELD_ENGINE_REL, PROCESS_RUNTIME_REL, TIDE_PROBE_REL, TIDE_REPLAY_REL, TIDE_DOC_REL],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_tide_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic tide marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-TIDE-DETERMINISTIC", "INV-NO-OCEAN-PDE-IN-MVP"],
                    related_paths=[TIDE_PHASE_ENGINE_REL, TIDE_FIELD_ENGINE_REL, PROCESS_RUNTIME_REL, TIDE_PROBE_REL, TIDE_REPLAY_REL, TIDE_DOC_REL],
                )
            )

    for rel_path in (TIDE_PHASE_ENGINE_REL, TIDE_FIELD_ENGINE_REL, PROCESS_RUNTIME_REL, TIDE_PROBE_REL, TIDE_REPLAY_REL):
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
                    category="worldgen.nondeterministic_tide_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden nondeterministic tide token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-TIDE-DETERMINISTIC"],
                    related_paths=[TIDE_PHASE_ENGINE_REL, TIDE_FIELD_ENGINE_REL, PROCESS_RUNTIME_REL, TIDE_PROBE_REL, TIDE_REPLAY_REL],
                )
            )
            break
    return findings
