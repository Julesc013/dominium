"""E360 unbounded generation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E360_UNBOUNDED_GENERATION_SMELL"
SYSTEM_REFINER_REL = "worldgen/mw/mw_system_refiner_l2.py"
SYSTEM_PRIORS_REGISTRY_REL = "data/registries/system_priors_registry.json"
REQUIRED_REFINER_TOKENS = (
    "max_planets",
    "max_moons_per_planet",
    "for planet_index in range(planet_count):",
    "_moon_stub_count(",
)
REQUIRED_REGISTRY_TOKENS = (
    "\"max_planets\"",
    "\"max_moons_per_planet\"",
)
FORBIDDEN_TOKENS = (
    "while True",
    "instantiate_all_star_systems",
    "generate_all_star_systems",
    "discover_entire_galaxy",
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
    refiner_text = _read_text(repo_root, SYSTEM_REFINER_REL)
    registry_text = _read_text(repo_root, SYSTEM_PRIORS_REGISTRY_REL)

    if not refiner_text:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.unbounded_generation_smell",
                severity="RISK",
                confidence=0.97,
                file_path=SYSTEM_REFINER_REL,
                line=1,
                evidence=["MW-2 system refiner is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-L2-OBJECTS-ID-STABLE"],
                related_paths=[SYSTEM_REFINER_REL],
            )
        ]

    missing_refiner = [token for token in REQUIRED_REFINER_TOKENS if token not in refiner_text]
    if missing_refiner:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.unbounded_generation_smell",
                severity="RISK",
                confidence=0.95,
                file_path=SYSTEM_REFINER_REL,
                line=1,
                evidence=["missing bounded-generation marker(s): {}".format(", ".join(missing_refiner[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN"],
                related_paths=[SYSTEM_REFINER_REL, SYSTEM_PRIORS_REGISTRY_REL],
            )
        )

    if not registry_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.unbounded_generation_smell",
                severity="RISK",
                confidence=0.96,
                file_path=SYSTEM_PRIORS_REGISTRY_REL,
                line=1,
                evidence=["system priors registry missing for MW-2 generation bounds"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN"],
                related_paths=[SYSTEM_PRIORS_REGISTRY_REL],
            )
        )
    else:
        missing_registry = [token for token in REQUIRED_REGISTRY_TOKENS if token not in registry_text]
        if missing_registry:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.unbounded_generation_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=SYSTEM_PRIORS_REGISTRY_REL,
                    line=1,
                    evidence=["missing bounded-prior marker(s): {}".format(", ".join(missing_registry[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN"],
                    related_paths=[SYSTEM_PRIORS_REGISTRY_REL],
                )
            )

    for line_no, line in enumerate(refiner_text.splitlines(), start=1):
        snippet = str(line).strip()
        if not snippet or snippet.startswith("#"):
            continue
        token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
        if not token:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.unbounded_generation_smell",
                severity="RISK",
                confidence=0.96,
                file_path=SYSTEM_REFINER_REL,
                line=line_no,
                evidence=["forbidden unbounded-generation token detected: {}".format(token), snippet[:160]],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN"],
                related_paths=[SYSTEM_REFINER_REL],
            )
        )
        break
    return findings
