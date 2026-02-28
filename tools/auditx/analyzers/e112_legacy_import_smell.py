"""E112 legacy import smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E112_LEGACY_IMPORT_SMELL"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    runtime_roots = ("src", "engine", "game", "client", "server", "platform")
    code_exts = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp")

    for root in runtime_roots:
        abs_root = os.path.join(repo_root, root)
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(code_exts):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                try:
                    lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
                except OSError:
                    continue
                for line_no, line in enumerate(lines, start=1):
                    token = str(line).replace("\\", "/")
                    if "legacy/" not in token and "quarantine/" not in token:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.legacy_import_smell",
                            severity="VIOLATION",
                            confidence=0.95,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[line.strip()[:180], "runtime import/reference to legacy/quarantine path"],
                            suggested_classification="INVALID",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-PRODUCTION-LEGACY-IMPORT"],
                            related_paths=[rel_path, "legacy/", "quarantine/"],
                        )
                    )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))

