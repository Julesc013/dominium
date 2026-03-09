"""E373 float trig smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E373_FLOAT_TRIG_SMELL"
SEASON_ENGINE_REL = "src/worldgen/earth/season_phase_engine.py"
CLIMATE_ENGINE_REL = "src/worldgen/earth/climate_field_engine.py"
CLIMATE_PROBE_REL = "tools/worldgen/earth2_probe.py"
CLIMATE_DOC_REL = "docs/worldgen/EARTH_SEASONAL_CLIMATE_MODEL.md"
REQUIRED_TOKENS = {
    SEASON_ENGINE_REL: (
        "EARTH_ORBIT_PHASE_SCALE",
        "earth_orbit_phase_from_params(",
        "solar_declination_mdeg(",
        "phase_scale",
    ),
    CLIMATE_ENGINE_REL: (
        "earth_orbit_phase_from_params(",
        "solar_declination_mdeg(",
        "temperature_value",
        "daylight_value",
    ),
    CLIMATE_PROBE_REL: (
        "orbit_phase_report",
        "polar_daylight_report",
    ),
    CLIMATE_DOC_REL: (
        "fixed-point math only",
        "no floating trig is required or assumed",
        "platform-stable and integer-rounded",
    ),
}
FORBIDDEN_TOKENS = ("math.sin(", "math.cos(", "numpy.sin(", "numpy.cos(", "np.sin(", "np.cos(")


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
                    category="worldgen.float_trig_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-2 climate artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-CLIMATE-DETERMINISTIC"],
                    related_paths=[SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, CLIMATE_PROBE_REL, CLIMATE_DOC_REL],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.float_trig_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic climate marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CLIMATE-DETERMINISTIC"],
                    related_paths=[SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, CLIMATE_PROBE_REL, CLIMATE_DOC_REL],
                )
            )

    for rel_path in (SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, CLIMATE_PROBE_REL):
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
                    category="worldgen.float_trig_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden float trig token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CLIMATE-DETERMINISTIC"],
                    related_paths=[SEASON_ENGINE_REL, CLIMATE_ENGINE_REL, CLIMATE_PROBE_REL],
                )
            )
            break
    return findings
