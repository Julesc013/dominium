"""E254 direct exposure write smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E254_DIRECT_EXPOSURE_WRITE_SMELL"


class DirectExposureWriteSmell:
    analyzer_id = ANALYZER_ID


_EXPOSURE_TOKEN = re.compile(
    r"(pollution_exposure_state_rows|pollution_health_risk_event_rows|pollution_hazard_hook_rows)",
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


def _looks_like_mutation(snippet: str) -> bool:
    text = str(snippet or "").strip()
    if ".append(" in text:
        return True
    if "=" not in text:
        return False
    if any(op in text for op in ("==", "!=", ">=", "<=", ":=")):
        return False
    return True


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
        "tools/xstack/sessionx/process_runtime.py",
        "src/pollution/exposure_engine.py",
        "src/pollution/dispersion_engine.py",
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
                    if not _EXPOSURE_TOKEN.search(snippet):
                        continue
                    if not _looks_like_mutation(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.direct_exposure_write_smell",
                            severity="RISK",
                            confidence=0.92,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Direct exposure-state mutation detected outside canonical pollution process path",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-EXPOSURE-PROCESS-ONLY"],
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
