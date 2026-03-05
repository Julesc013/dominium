"""E255 omniscient pollution UI leak smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E255_OMNISCIENT_POLLUTION_UI_LEAK_SMELL"


class OmniscientPollutionUILeakSmell:
    analyzer_id = ANALYZER_ID


_POLLUTION_TRUTH_PATTERN = re.compile(
    r"(field\.pollution\.[a-z0-9_]+_concentration|pollution_exposure_state_rows|pollution_health_risk_event_rows|pollution_compliance_report_rows)",
    re.IGNORECASE,
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
        os.path.join(repo_root, "src", "client"),
        os.path.join(repo_root, "tools", "interaction"),
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
        "tools/xstack/sessionx/process_runtime.py",
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
                    if not _POLLUTION_TRUTH_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="epistemics.omniscient_pollution_ui_leak_smell",
                            severity="RISK",
                            confidence=0.91,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential omniscient pollution truth reference in UI/observer-facing surface",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-OMNISCIENT-POLLUTION-KNOWLEDGE"],
                            related_paths=[
                                rel_path,
                                "docs/pollution/EXPOSURE_AND_COMPLIANCE_MODEL.md",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
