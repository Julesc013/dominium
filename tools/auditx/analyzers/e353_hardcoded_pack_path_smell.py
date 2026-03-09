"""E353 hardcoded pack path smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E353_HARDCODED_PACK_PATH_SMELL"
WATCH_PREFIXES = ("client/", "server/", "launcher/", "setup/", "tools/", "scripts/")
SCAN_ROOTS = ("client", "server", "launcher", "setup", "tools", "scripts")
SCAN_EXTS = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".cmd", ".bat", ".ps1", ".sh")
ALLOWLIST = {
    "tools/mvp/runtime_bundle.py",
}
PATH_TOKENS = (
    "dist/packs/",
    "packs/base/pack.base.procedural",
    "packs/official/pack.sol.pin_minimal",
    "packs/official/pack.earth.procedural",
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
            if not any(rel_path.startswith(prefix) for prefix in WATCH_PREFIXES):
                continue
            if rel_path in ALLOWLIST:
                continue
            if not rel_path.endswith(SCAN_EXTS):
                continue
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
                if rel_path in ALLOWLIST:
                    continue
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
            normalized = snippet.replace("\\", "/")
            if not snippet:
                continue
            if snippet.startswith(("#", "//", "*", "/*")):
                continue
            token = next((item for item in PATH_TOKENS if item in normalized), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.hardcoded_pack_path_smell",
                    severity="RISK",
                    confidence=0.92,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "hardcoded MVP pack install path detected outside canonical bundle generator",
                        normalized[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-MVP-PACKS-MINIMAL", "INV-PACK-LOCK-REQUIRED"],
                    related_paths=[rel_path, "tools/mvp/runtime_bundle.py", "locks/pack_lock.mvp_default.json"],
                )
            )
            break
    return findings
