"""E250 direct smoke visual hack smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E250_DIRECT_SMOKE_VISUAL_HACK_SMELL"


class DirectSmokeVisualHackSmell:
    analyzer_id = ANALYZER_ID


_SMOKE_PATTERN = re.compile(r"\b(smoke_density|avg_smoke|smoke_)\b", re.IGNORECASE)
_VISIBILITY_PATTERN = re.compile(r"\b(field\.visibility|visibility_permille|visibility)\b", re.IGNORECASE)


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
    # Known transitional paths are explicitly allowlisted until POLL-1 visibility coupling migration.
    allowed_files = {
        "tools/xstack/sessionx/process_runtime.py",
        "interior/compartment_flow_engine.py",
        "interior/compartment_flow_builder.py",
        "tools/xstack/repox/check.py",
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
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not _SMOKE_PATTERN.search(snippet):
                        continue
                    if not _VISIBILITY_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.direct_smoke_visual_hack_smell",
                            severity="RISK",
                            confidence=0.91,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Smoke-to-visibility coupling detected outside approved transitional paths",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-DIRECT-POLLUTION-FIELD-WRITES",
                            ],
                            related_paths=[
                                rel_path,
                                "docs/pollution/POLLUTION_CONSTITUTION.md",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
