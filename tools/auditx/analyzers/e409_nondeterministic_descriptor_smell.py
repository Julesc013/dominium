"""E409 nondeterministic descriptor smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E409_NONDETERMINISTIC_DESCRIPTOR_SMELL"
SCANNED_FILES = (
    "compat/descriptor/descriptor_engine.py",
    "tools/compat/tool_emit_descriptor.py",
    "tools/compat/tool_generate_descriptor_manifest.py",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"\bdatetime\b"),
    re.compile(r"\butcnow\b"),
    re.compile(r"\btime\s*\("),
    re.compile(r"\bclock\b"),
    re.compile(r"\buuid4\b"),
    re.compile(r"\brandom\b"),
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
    related_paths = sorted(SCANNED_FILES)
    for rel_path in SCANNED_FILES:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.endpoint_descriptor.nondeterministic_descriptor_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required descriptor surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-DESCRIPTOR-DETERMINISTIC", "INV-NO-WALLCLOCK-IN-DESCRIPTOR"],
                    related_paths=related_paths,
                )
            )
            continue
        for pattern in FORBIDDEN_PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="compat.endpoint_descriptor.nondeterministic_descriptor_smell",
                        severity="RISK",
                        confidence=0.96,
                        file_path=rel_path,
                        line=1,
                        evidence=["forbidden nondeterministic token in descriptor surface: {}".format(match.group(0))],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="REWRITE",
                        related_invariants=["INV-DESCRIPTOR-DETERMINISTIC", "INV-NO-WALLCLOCK-IN-DESCRIPTOR"],
                        related_paths=related_paths,
                    )
                )
                break
    return findings
