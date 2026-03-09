"""E365 hardcoded DEM reference smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E365_HARDCODED_DEM_REFERENCE_SMELL"
EARTH_GENERATOR_REL = "src/worldgen/earth/earth_surface_generator.py"
EARTH_PARAMS_REL = "data/registries/earth_surface_params_registry.json"
DOC_REL = "docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md"
VERIFY_TOOL_REL = "tools/worldgen/tool_verify_earth_surface.py"
REQUIRED_GENERATOR_TOKENS = (
    "generate_earth_surface_tile_plan(",
    "continent_count_target",
    "ocean_fraction_target",
    "surface.class.ocean",
)
REQUIRED_DOC_TOKENS = (
    "real DEM data",
    "real coastlines",
    "future higher-fidelity Earth packs",
)
FORBIDDEN_RUNTIME_TOKENS = (
    "gdal",
    ".tif",
    ".hgt",
    "heightmap",
    "shapefile",
    "country_border",
    "city_dataset",
    "real_dem",
    "dem_source",
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
    generator_text = _read_text(repo_root, EARTH_GENERATOR_REL)
    params_text = _read_text(repo_root, EARTH_PARAMS_REL)
    doc_text = _read_text(repo_root, DOC_REL)
    verify_tool_text = _read_text(repo_root, VERIFY_TOOL_REL)

    for rel_path, text, required_tokens in (
        (EARTH_GENERATOR_REL, generator_text, REQUIRED_GENERATOR_TOKENS),
        (EARTH_PARAMS_REL, params_text, ("params.earth.surface_default_stub", "continent_count_target", "ocean_fraction_target")),
        (DOC_REL, doc_text, REQUIRED_DOC_TOKENS),
        (VERIFY_TOOL_REL, verify_tool_text, ("verify_earth_surface_consistency",)),
    ):
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.hardcoded_dem_reference_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-0 governed artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-REAL-DATA-IN-EARTH-STUB"],
                    related_paths=[EARTH_GENERATOR_REL, EARTH_PARAMS_REL, DOC_REL, VERIFY_TOOL_REL],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.hardcoded_dem_reference_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-0 low-data marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-REAL-DATA-IN-EARTH-STUB"],
                    related_paths=[EARTH_GENERATOR_REL, EARTH_PARAMS_REL, DOC_REL, VERIFY_TOOL_REL],
                )
            )

    for rel_path, text in ((EARTH_GENERATOR_REL, generator_text), (VERIFY_TOOL_REL, verify_tool_text)):
        lowered = str(text or "").lower()
        if not lowered:
            continue
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in lowered:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="worldgen.hardcoded_dem_reference_smell",
                        severity="RISK",
                        confidence=0.96,
                        file_path=rel_path,
                        line=1,
                        evidence=["forbidden real-data token detected: {}".format(token)],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-REAL-DATA-IN-EARTH-STUB"],
                        related_paths=[EARTH_GENERATOR_REL, VERIFY_TOOL_REL],
                    )
                )
                break
    return findings
