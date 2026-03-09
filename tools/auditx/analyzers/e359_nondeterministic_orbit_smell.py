"""E359 nondeterministic orbit smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E359_NONDETERMINISTIC_ORBIT_SMELL"
SYSTEM_REFINER_REL = "src/worldgen/mw/mw_system_refiner_l2.py"
REQUIRED_TOKENS = (
    "_named_substream_seed(",
    "rng.worldgen.system.planet.",
    "push_out_ratio_permille",
    "max_eccentricity_permille",
    "canonical_sha256(",
)
FORBIDDEN_TOKENS = (
    "random.",
    "uuid",
    "secrets.",
    "time.time(",
    "datetime.now(",
    "os.urandom(",
    "retry(",
    "random_retry",
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
    text = _read_text(repo_root, SYSTEM_REFINER_REL)
    if not text:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.nondeterministic_orbit_smell",
                severity="RISK",
                confidence=0.97,
                file_path=SYSTEM_REFINER_REL,
                line=1,
                evidence=["MW-2 system refiner is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN"],
                related_paths=[SYSTEM_REFINER_REL],
            )
        ]

    missing = [token for token in REQUIRED_TOKENS if token not in text]
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.nondeterministic_orbit_smell",
                severity="RISK",
                confidence=0.95,
                file_path=SYSTEM_REFINER_REL,
                line=1,
                evidence=["missing deterministic orbit marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN"],
                related_paths=[SYSTEM_REFINER_REL, "docs/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md"],
            )
        )

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
                category="worldgen.nondeterministic_orbit_smell",
                severity="RISK",
                confidence=0.96,
                file_path=SYSTEM_REFINER_REL,
                line=line_no,
                evidence=["forbidden nondeterministic orbit token detected: {}".format(token), snippet[:160]],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN"],
                related_paths=[SYSTEM_REFINER_REL],
            )
        )
        break
    return findings
