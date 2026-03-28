"""E366 nondeterministic Earth noise smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E366_NONDETERMINISTIC_NOISE_SMELL"
EARTH_GENERATOR_REL = "worldgen/earth/earth_surface_generator.py"
MW_SURFACE_REFINER_REL = "worldgen/mw/mw_surface_refiner_l3.py"
EARTH_PROBE_REL = "tools/worldgen/earth0_probe.py"
DOC_REL = "docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md"
REQUIRED_GENERATOR_TOKENS = (
    "canonical_sha256(",
    "_interpolated_noise_permille(",
    "_triangle_wave_permille(",
    "tile_seed",
)
REQUIRED_REFINER_TOKENS = (
    'handler_id == "earth.surface.stub"',
    "earth_surface_params_rows(",
    "generate_earth_surface_tile_plan(",
)
REQUIRED_PROBE_TOKENS = (
    "worldgen_rng_stream_policy(",
    "RNG_WORLDGEN_SURFACE",
    "generate_mw_surface_l3_payload(",
)
REQUIRED_DOC_TOKENS = (
    "All random variation must use named RNG substreams only.",
    "wall-clock time must never participate",
    "Earth generation is selected only through routing data.",
)
FORBIDDEN_TOKENS = ("random.", "uuid", "secrets.", "time.time(", "datetime.now(", "os.urandom(")


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
    refiner_text = _read_text(repo_root, MW_SURFACE_REFINER_REL)
    probe_text = _read_text(repo_root, EARTH_PROBE_REL)
    doc_text = _read_text(repo_root, DOC_REL)

    for rel_path, text, required_tokens in (
        (EARTH_GENERATOR_REL, generator_text, REQUIRED_GENERATOR_TOKENS),
        (MW_SURFACE_REFINER_REL, refiner_text, REQUIRED_REFINER_TOKENS),
        (EARTH_PROBE_REL, probe_text, REQUIRED_PROBE_TOKENS),
        (DOC_REL, doc_text, REQUIRED_DOC_TOKENS),
    ):
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_noise_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-0 deterministic artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-EARTH-GEN-DETERMINISTIC"],
                    related_paths=[EARTH_GENERATOR_REL, MW_SURFACE_REFINER_REL, EARTH_PROBE_REL, DOC_REL],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_noise_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic EARTH-0 marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-GEN-DETERMINISTIC"],
                    related_paths=[EARTH_GENERATOR_REL, MW_SURFACE_REFINER_REL, EARTH_PROBE_REL, DOC_REL],
                )
            )

    for rel_path, text in ((EARTH_GENERATOR_REL, generator_text), (EARTH_PROBE_REL, probe_text)):
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
                    category="worldgen.nondeterministic_noise_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden nondeterministic token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EARTH-GEN-DETERMINISTIC"],
                    related_paths=[EARTH_GENERATOR_REL, EARTH_PROBE_REL],
                )
            )
            break
    return findings
