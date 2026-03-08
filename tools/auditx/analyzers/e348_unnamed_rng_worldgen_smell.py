"""E348 unnamed RNG worldgen smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E348_UNNAMED_RNG_WORLDGEN_SMELL"
WATCH_PREFIXES = ("src/geo/worldgen/", "tools/geo/", "tools/xstack/sessionx/")
_BANNED_TOKENS = ("random.", "uuid", "secrets.", "time.time(", "datetime.now(", "os.urandom(")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_candidate_files(repo_root: str):
    for prefix in WATCH_PREFIXES:
        abs_prefix = os.path.join(repo_root, prefix.replace("/", os.sep))
        if not os.path.isdir(abs_prefix):
            continue
        for root, _dirs, files in os.walk(abs_prefix):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(root, name)
                yield os.path.relpath(abs_path, repo_root).replace(os.sep, "/")


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []
    candidates = []
    if changed_files:
        for rel_path in list(changed_files or []):
            rel_norm = str(rel_path).replace(os.sep, "/")
            if rel_norm.endswith(".py") and any(rel_norm.startswith(prefix) for prefix in WATCH_PREFIXES):
                candidates.append(rel_norm)
    else:
        candidates = list(_iter_candidate_files(repo_root))
    for rel_path in sorted(set(candidates)):
        text = _read_text(repo_root, rel_path)
        if not text or "worldgen" not in text.lower():
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(token in snippet for token in _BANNED_TOKENS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.unnamed_rng_worldgen_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "nondeterministic or unnamed RNG source detected in GEO worldgen surface",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-WORLDGEN-RNG-NAMED-ONLY"],
                    related_paths=[rel_path, "src/geo/worldgen/worldgen_engine.py"],
                )
            )
            break
    return findings
