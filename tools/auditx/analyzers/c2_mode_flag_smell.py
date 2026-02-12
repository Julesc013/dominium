"""C2 Mode flag smell analyzer."""

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "C2_MODE_FLAG_SMELL"
SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py", ".json", ".schema")


def _forbidden_tokens():
    return (
        "survival" + "_" + "mode",
        "creative" + "_" + "mode",
        "hardcore" + "_" + "mode",
        "spectator" + "_" + "mode",
    )


MODE_TOKEN_RE = re.compile(
    r"\b(?:{})\b".format("|".join(re.escape(token) for token in _forbidden_tokens())),
    re.IGNORECASE,
)


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del changed_files
    findings = []
    for node in sorted(graph.nodes.values(), key=lambda item: item.label):
        if node.node_type != "file":
            continue
        rel = node.label
        if rel.startswith(("docs/", "legacy/", "dist/", "out/", "build/", ".git/")):
            continue
        if not rel.lower().endswith(SOURCE_EXTS):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        match = MODE_TOKEN_RE.search(text)
        if not match:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="mode_flag_smell",
                severity="VIOLATION",
                confidence=0.90,
                file_path=rel,
                evidence=[
                    "Found hardcoded mode token '{}' in runtime-affecting source.".format(match.group(0)),
                    "Mode behavior must resolve from ExperienceProfile + LawProfile + ParameterBundle.",
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-HARDCODED-MODE-BRANCH", "INV-MODE-AS-PROFILES"],
                related_paths=[rel],
            )
        )
        if len(findings) >= 64:
            break
    return findings
