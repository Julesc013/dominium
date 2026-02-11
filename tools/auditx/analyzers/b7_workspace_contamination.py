"""A7 Workspace Contamination Analyzer."""

import os

from analyzers.base import make_finding


ANALYZER_ID = "A7_WORKSPACE_CONTAMINATION"
WATCH_PREFIXES = ("scripts/dev/", "scripts/ci/", ".github/workflows/")
FORBIDDEN_SNIPPETS = (
    "dist/sys/",
    "out/build/vs2026",
    "out\\build\\vs2026",
)
ALLOWLIST = {
    "scripts/dev/env_tools_lib.py",
}


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    roots = [
        os.path.join(repo_root, "scripts", "dev"),
        os.path.join(repo_root, "scripts", "ci"),
        os.path.join(repo_root, ".github", "workflows"),
    ]
    findings = []
    for base in roots:
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                if not name.lower().endswith((".py", ".yml", ".yaml", ".cmd", ".bat", ".ps1", ".sh")):
                    continue
                abs_path = os.path.join(root, name)
                rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                if rel in ALLOWLIST:
                    continue
                text = _read(abs_path)
                hits = sorted(snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text)
                if not hits:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="semantic.workspace_contamination",
                        severity="WARN",
                        confidence=0.78,
                        file_path=rel,
                        evidence=[
                            "Potential non-workspace-scoped path usage detected.",
                            "Snippets: {}".format(", ".join(hits)),
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-WORKSPACE-ISOLATION"],
                        related_paths=[rel],
                    )
                )
    return findings

