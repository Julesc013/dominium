"""E357 direct system spawn smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E357_DIRECT_SYSTEM_SPAWN_SMELL"
WATCH_PREFIXES = ("src/worldgen/mw/", "src/geo/worldgen/", "tools/xstack/sessionx/", "tools/worldgen/", "tools/mvp/")
SCAN_ROOTS = ("src/worldgen/mw", "src/geo/worldgen", "tools/xstack/sessionx", "tools/worldgen", "tools/mvp")
SCAN_EXTS = (".py",)
ALLOWLIST = {
    "src/worldgen/mw/mw_cell_generator.py",
    "src/geo/worldgen/worldgen_engine.py",
    "tools/xstack/sessionx/process_runtime.py",
}
SPAWN_TOKENS = (
    "kind.star_system",
    "artifact.star_system_artifact",
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
                if rel_path not in ALLOWLIST:
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
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path not in ALLOWLIST:
                    yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []
    for rel_path in _iter_candidates(repo_root, changed_files=changed_files):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in SPAWN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.direct_system_spawn_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "star-system spawn or attached-model token appears outside the governed worldgen surface",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SYSTEM-INSTANTIATION-VIA-WORLDGEN"],
                    related_paths=[rel_path, "src/geo/worldgen/worldgen_engine.py", "tools/xstack/sessionx/process_runtime.py"],
                )
            )
            break
    return findings
