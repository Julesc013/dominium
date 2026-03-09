"""E361 hardcoded Earth generator smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E361_HARDCODED_EARTH_GEN_SMELL"
WATCH_PREFIXES = ("src/worldgen/mw/", "src/geo/worldgen/", "tools/xstack/sessionx/", "data/registries/", "docs/worldgen/")
SURFACE_REFINER_REL = "src/worldgen/mw/mw_surface_refiner_l3.py"
ROUTING_REGISTRY_REL = "data/registries/surface_generator_routing_registry.json"
GENERATOR_REGISTRY_REL = "data/registries/surface_generator_registry.json"
DOC_REL = "docs/worldgen/PLANET_SURFACE_MACRO_MODEL.md"
REQUIRED_REFINER_TOKENS = (
    "_select_surface_route(",
    "_resolve_generator(",
    "surface_generator_routing_rows(",
    "surface_generator_rows(",
    "selected_generator_row",
    "handler_row",
)
REQUIRED_ROUTING_TOKENS = (
    "route.earth",
    "planet.earth",
    "gen.surface.earth_stub",
)
REQUIRED_GENERATOR_TOKENS = (
    "gen.surface.default_stub",
    "gen.surface.earth_stub",
    "earth.surface.stub",
    "earth_surface_params_id",
)
REQUIRED_DOC_TOKENS = (
    "runtime code must not branch on",
    "planet.earth",
    "Earth-specific generator",
    "earth.surface.stub",
)
FORBIDDEN_RUNTIME_TOKENS = (
    "planet.earth",
    "gen.surface.earth_stub",
    "earth_surface_generator",
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
    routing_text = _read_text(repo_root, ROUTING_REGISTRY_REL)
    generator_text = _read_text(repo_root, GENERATOR_REGISTRY_REL)
    doc_text = _read_text(repo_root, DOC_REL)

    if not refiner_text:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.hardcoded_earth_gen_smell",
                severity="RISK",
                confidence=0.97,
                file_path=SURFACE_REFINER_REL,
                line=1,
                evidence=["MW-3 surface refiner is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-SURFACE-GEN-ROUTED"],
                related_paths=[SURFACE_REFINER_REL],
            )
        ]

    missing_refiner = [token for token in REQUIRED_REFINER_TOKENS if token not in refiner_text]
    if missing_refiner:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.hardcoded_earth_gen_smell",
                severity="RISK",
                confidence=0.95,
                file_path=SURFACE_REFINER_REL,
                line=1,
                evidence=["missing surface-routing marker(s): {}".format(", ".join(missing_refiner[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-SURFACE-GEN-ROUTED"],
                related_paths=[SURFACE_REFINER_REL, ROUTING_REGISTRY_REL, GENERATOR_REGISTRY_REL, DOC_REL],
            )
        )

    for rel_path, text, required_tokens in (
        (ROUTING_REGISTRY_REL, routing_text, REQUIRED_ROUTING_TOKENS),
        (GENERATOR_REGISTRY_REL, generator_text, REQUIRED_GENERATOR_TOKENS),
        (DOC_REL, doc_text, REQUIRED_DOC_TOKENS),
    ):
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.hardcoded_earth_gen_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MW-3 Earth routing artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-SURFACE-GEN-ROUTED"],
                    related_paths=[rel_path],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.hardcoded_earth_gen_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing Earth-routing marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SURFACE-GEN-ROUTED"],
                    related_paths=[rel_path, SURFACE_REFINER_REL],
                )
            )

    for line_no, line in enumerate(refiner_text.splitlines(), start=1):
        snippet = str(line).strip()
        if not snippet or snippet.startswith("#"):
            continue
        token = next((item for item in FORBIDDEN_RUNTIME_TOKENS if item in snippet), "")
        if not token:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.hardcoded_earth_gen_smell",
                severity="RISK",
                confidence=0.96,
                file_path=SURFACE_REFINER_REL,
                line=line_no,
                evidence=["forbidden hardcoded Earth-routing token detected: {}".format(token), snippet[:160]],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-SURFACE-GEN-ROUTED"],
                related_paths=[SURFACE_REFINER_REL, ROUTING_REGISTRY_REL],
            )
        )
        break
    return findings
