"""E358 nondeterministic query smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E358_NONDETERMINISTIC_QUERY_SMELL"
QUERY_ENGINE_REL = "src/worldgen/mw/system_query_engine.py"
REQUIRED_TOKENS = (
    "sorted(",
    "geo_cell_key_neighbors(",
    "geo_distance(",
    "canonical_sha256(",
)
FORBIDDEN_TOKENS = (
    "random.",
    "uuid",
    "secrets.",
    "time.time(",
    "datetime.now(",
    "os.urandom(",
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
    text = _read_text(repo_root, QUERY_ENGINE_REL)
    if not text:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.nondeterministic_query_smell",
                severity="RISK",
                confidence=0.97,
                file_path=QUERY_ENGINE_REL,
                line=1,
                evidence=["MW-1 system query engine is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-EAGER-SYSTEM-GENERATION"],
                related_paths=[QUERY_ENGINE_REL],
            )
        ]

    missing = [token for token in REQUIRED_TOKENS if token not in text]
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.nondeterministic_query_smell",
                severity="RISK",
                confidence=0.95,
                file_path=QUERY_ENGINE_REL,
                line=1,
                evidence=["missing deterministic query marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-EAGER-SYSTEM-GENERATION"],
                related_paths=[QUERY_ENGINE_REL, "src/geo/worldgen/worldgen_engine.py"],
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
                category="worldgen.nondeterministic_query_smell",
                severity="RISK",
                confidence=0.96,
                file_path=QUERY_ENGINE_REL,
                line=line_no,
                evidence=["forbidden nondeterministic query token detected: {}".format(token), snippet[:160]],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-EAGER-SYSTEM-GENERATION"],
                related_paths=[QUERY_ENGINE_REL],
            )
        )
        break
    return findings
