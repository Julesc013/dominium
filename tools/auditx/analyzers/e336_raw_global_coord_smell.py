"""E336 raw global coordinate smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E336_RAW_GLOBAL_COORD_SMELL"
WATCH_PREFIXES = ("src/geo/frame/", "tools/geo/")
_ALLOWLIST = {
    "tools/geo/tool_replay_frame_window.py",
}
_PATTERNS = (
    re.compile(r"\bglobal_position\b"),
    re.compile(r"\bworld_position\b"),
    re.compile(r"\braw_global_coord"),
    re.compile(r"\bposition_mm\b"),
)


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
                rel_path = os.path.relpath(abs_path, repo_root).replace(os.sep, "/")
                if rel_path in _ALLOWLIST:
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []
    candidates = []
    if changed_files:
        for rel_path in list(changed_files or []):
            rel_norm = str(rel_path).replace(os.sep, "/")
            if rel_norm in _ALLOWLIST or not rel_norm.endswith(".py"):
                continue
            if any(rel_norm.startswith(prefix) for prefix in WATCH_PREFIXES):
                candidates.append(rel_norm)
    else:
        candidates = list(_iter_candidate_files(repo_root))
    for rel_path in sorted(set(candidates)):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in _PATTERNS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="geometry.raw_global_coord_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "raw global coordinate terminology detected inside GEO-2 frame surfaces",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-RAW-GLOBAL-COORDS"],
                    related_paths=[rel_path, "src/geo/frame/frame_engine.py"],
                )
            )
            break
    return findings
