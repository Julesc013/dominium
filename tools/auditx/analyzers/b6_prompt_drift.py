"""A6 Prompt Drift Analyzer."""

import os

from analyzers.base import make_finding


ANALYZER_ID = "A6_PROMPT_DRIFT"
WATCH_PREFIXES = ("docs/governance/", "docs/archive/prompts/", "scripts/")
DRIFT_TOKENS = (
    "bypass gate",
    "skip gate",
    "temporary hack",
    "disable invariant",
    "force pass",
    "ignore failure",
)


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
        os.path.join(repo_root, "docs", "governance"),
        os.path.join(repo_root, "docs", "archive", "prompts"),
        os.path.join(repo_root, "scripts"),
    ]
    findings = []
    for base in roots:
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                if not name.lower().endswith((".md", ".txt", ".py", ".yml", ".yaml")):
                    continue
                abs_path = os.path.join(root, name)
                rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                lower = _read(abs_path).lower()
                hits = sorted(token for token in DRIFT_TOKENS if token in lower)
                if not hits:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="semantic.prompt_drift",
                        severity="RISK",
                        confidence=0.81,
                        file_path=rel,
                        evidence=[
                            "Potential governance weakening token(s) detected.",
                            "Tokens: {}".format(", ".join(hits[:5])),
                        ],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-GATE-BYPASS"],
                        related_paths=[rel],
                    )
                )
                if len(findings) >= 120:
                    return findings
    return findings

