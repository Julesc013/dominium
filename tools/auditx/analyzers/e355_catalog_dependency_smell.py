"""E355 catalog dependency smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E355_CATALOG_DEPENDENCY_SMELL"
WATCH_PREFIXES = ("src/worldgen/mw/", "src/geo/worldgen/", "tools/geo/", "tools/xstack/sessionx/")
SCAN_ROOTS = ("src/worldgen/mw", "src/geo/worldgen", "tools/geo", "tools/xstack/sessionx")
SCAN_EXTS = (".py",)
CATALOG_TOKENS = (
    "data/world/milky_way/",
    "data/worldgen/real/milky_way/",
    "milky_way.galaxy.json",
    "milky_way.arms.json",
    "milky_way.anchors.json",
    "milky_way.regions.json",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_candidates(repo_root: str, changed_files=None):
    if changed_files:
        for rel_path in sorted(set(_norm(path) for path in (changed_files or []))):
            if any(rel_path.startswith(prefix) for prefix in WATCH_PREFIXES) and rel_path.endswith(SCAN_EXTS):
                yield rel_path
        return
    for rel_root in SCAN_ROOTS:
        abs_root = os.path.join(repo_root, rel_root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(SCAN_EXTS):
                    continue
                yield _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []
    for rel_path in _iter_candidates(repo_root, changed_files=changed_files):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            normalized = snippet.replace("\\", "/")
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in CATALOG_TOKENS if item in normalized), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.catalog_dependency_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "runtime Milky Way generation surface references catalog or real-data path",
                        normalized[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-CATALOG-REQUIRED"],
                    related_paths=[rel_path, "src/worldgen/mw/mw_cell_generator.py", "data/registries/galaxy_priors_registry.json"],
                )
            )
            break
    return findings
