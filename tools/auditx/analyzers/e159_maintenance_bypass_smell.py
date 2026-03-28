"""E159 maintenance bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E159_MAINTENANCE_BYPASS_SMELL"


class MaintenanceBypassSmell:
    analyzer_id = ANALYZER_ID


_BYPASS_PATTERNS = (
    re.compile(r"\bservice_wear_rows\s*\(", re.IGNORECASE),
    re.compile(r"\bapply_wear_updates\s*\(", re.IGNORECASE),
    re.compile(r"\bstate\s*\[\s*[\"']mobility_wear_states[\"']\s*\]\s*=", re.IGNORECASE),
    re.compile(r"\bprocess\.(?:inspect_track|service_track|inspect_vehicle|service_vehicle)\b"),
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
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    allowed_files = {
        "mobility/maintenance/wear_engine.py",
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
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _BYPASS_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.maintenance_bypass_smell",
                            severity="RISK",
                            confidence=0.89,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["maintenance/wear mutation bypass candidate", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-WEAR-THROUGH-HAZARD-ONLY",
                                "INV-NO-ADHOC-WEAR-FLAGS",
                            ],
                            related_paths=[
                                rel_path,
                                "tools/xstack/sessionx/process_runtime.py",
                                "mobility/maintenance/wear_engine.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

