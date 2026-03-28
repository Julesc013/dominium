"""E331 raw XYZ distance smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E331_RAW_XYZ_DISTANCE_SMELL"
WATCH_PREFIXES = ("src/client/render/",)
TARGET_FILES = ("client/render/representation_resolver.py",)
LEGACY_TOKENS = (
    'abs(_to_int(transform.get("x", 0), 0))',
    'abs(_to_int(transform.get("y", 0), 0))',
    'abs(_to_int(transform.get("z", 0), 0))',
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
    for rel_path in TARGET_FILES:
        text = _read_text(repo_root, rel_path)
        if not text or "geo_distance(" in text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(token in snippet for token in LEGACY_TOKENS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="geometry.raw_xyz_distance_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "raw XYZ distance heuristic detected outside GEO kernel",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-GEO-API-ONLY-FOR-DOMAIN-DISTANCE",
                        "INV-NO-HARDCODED-DIMENSION-ASSUMPTIONS",
                    ],
                    related_paths=[rel_path, "geo/kernel/geo_kernel.py"],
                )
            )
            break
    return findings
