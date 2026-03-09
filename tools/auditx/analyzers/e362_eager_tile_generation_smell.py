"""E362 eager tile generation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E362_EAGER_TILE_GENERATION_SMELL"
WATCH_PREFIXES = ("src/worldgen/mw/", "src/geo/worldgen/", "tools/xstack/sessionx/", "docs/worldgen/")
SURFACE_REFINER_REL = "src/worldgen/mw/mw_surface_refiner_l3.py"
INSOLATION_PROXY_REL = "src/worldgen/mw/insolation_proxy.py"
WORLDGEN_ENGINE_REL = "src/geo/worldgen/worldgen_engine.py"
DOC_REL = "docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md"
REQUIRED_REFINER_TOKENS = (
    "surface_geo_cell_key",
    "kind.surface_tile",
    "generated_surface_tile_artifact_rows",
    "field_initializations",
    "geometry_initializations",
)
REQUIRED_ENGINE_TOKENS = (
    "_surface_request_context(",
    "generate_mw_surface_l3_payload(",
    "generated_surface_tile_artifact_rows",
    "surface_summary",
)
REQUIRED_PROXY_TOKENS = (
    "daylight_proxy_permille(",
    "insolation_proxy_permille(",
    "season_phase_permille(",
)
REQUIRED_DOC_TOKENS = (
    "requested tile only",
    "never eagerly expands all surface tiles",
    "no eager neighboring tile generation is permitted",
)
FORBIDDEN_TOKENS = (
    "generate_all_surface_tiles",
    "instantiate_all_surface_tiles",
    "precompute_surface_tiles",
    "expand_entire_surface",
    "planet_surface_full_pass",
    "for tile_index in range(",
    "for latitude_band in range(",
    "for longitude_band in range(",
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
    refiner_text = _read_text(repo_root, SURFACE_REFINER_REL)
    engine_text = _read_text(repo_root, WORLDGEN_ENGINE_REL)
    proxy_text = _read_text(repo_root, INSOLATION_PROXY_REL)
    doc_text = _read_text(repo_root, DOC_REL)

    if not refiner_text:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.eager_tile_generation_smell",
                severity="RISK",
                confidence=0.97,
                file_path=SURFACE_REFINER_REL,
                line=1,
                evidence=["MW-3 surface refiner is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-TILES-ON-DEMAND-ONLY"],
                related_paths=[SURFACE_REFINER_REL],
            )
        ]

    for rel_path, text, required_tokens in (
        (SURFACE_REFINER_REL, refiner_text, REQUIRED_REFINER_TOKENS),
        (WORLDGEN_ENGINE_REL, engine_text, REQUIRED_ENGINE_TOKENS),
        (INSOLATION_PROXY_REL, proxy_text, REQUIRED_PROXY_TOKENS),
        (DOC_REL, doc_text, REQUIRED_DOC_TOKENS),
    ):
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.eager_tile_generation_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MW-3 on-demand surface artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-TILES-ON-DEMAND-ONLY"],
                    related_paths=[rel_path],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.eager_tile_generation_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing on-demand tile marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-TILES-ON-DEMAND-ONLY"],
                    related_paths=[SURFACE_REFINER_REL, WORLDGEN_ENGINE_REL, INSOLATION_PROXY_REL, DOC_REL],
                )
            )

    for rel_path, text in ((SURFACE_REFINER_REL, refiner_text), (WORLDGEN_ENGINE_REL, engine_text)):
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.eager_tile_generation_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden eager tile-generation token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-TILES-ON-DEMAND-ONLY"],
                    related_paths=[SURFACE_REFINER_REL, WORLDGEN_ENGINE_REL],
                )
            )
            break
    return findings
