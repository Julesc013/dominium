"""E222 direct interior/fluid mass write smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E222_DIRECT_INTERIOR_MASS_WRITE_SMELL"


class DirectInteriorMassWriteSmell:
    analyzer_id = ANALYZER_ID


_PATTERNS = (
    re.compile(r"\bstored_mass\b\s*=", re.IGNORECASE),
    re.compile(r"\bwater_volume\b\s*=", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


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

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "fluid/network/fluid_network_engine.py",
        "interior/compartment_flow_engine.py",
        "interior/compartment_flow_builder.py",
        "tools/xstack/sessionx/process_runtime.py",
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                if not (rel_path.startswith("src/fluid/") or rel_path.startswith("src/interior/") or rel_path.startswith("tools/xstack/sessionx/")):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.direct_interior_mass_write_smell",
                            severity="RISK",
                            confidence=0.83,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["direct interior/fluid mass write detected outside canonical process files", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-DIRECT-MASS-MUTATION",
                            ],
                            related_paths=[rel_path, "fluid/network/fluid_network_engine.py", "interior/compartment_flow_engine.py"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )