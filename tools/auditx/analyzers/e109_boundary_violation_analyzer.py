"""E109 boundary violation analyzer.

Aggregates deterministic boundary scanner failures into AuditX records.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Dict, List

from analyzers.base import make_finding


ANALYZER_ID = "E109_BOUNDARY_VIOLATION_ANALYZER"
WATCH_PREFIXES = (
    "src/",
    "tools/xstack/repox/",
    "scripts/verify_build_target_boundaries.py",
    "CMakeLists.txt",
    "data/registries/intent_dispatch_whitelist.json",
    "data/governance/deprecations.json",
    "legacy/",
    "quarantine/",
)

BOUNDARY_CODE_TO_RULE = {
    "BOUNDARY-TOOLS-001": "INV-NO-TOOLS-IN-RUNTIME",
    "BOUNDARY-PLATFORM-001": "INV-PLATFORM-ISOLATION",
    "BOUNDARY-RENDER-001": "INV-RENDER-TRUTH-ISOLATION",
    "BOUNDARY-CORE-001": "INV-NO-DUPLICATE-GRAPH-SUBSTRATE",
    "BOUNDARY-CMAKE-001": "INV-NO-TOOLS-IN-RUNTIME",
    "BOUNDARY-CMAKE-002": "INV-NO-TOOLS-IN-RUNTIME",
    "BOUNDARY-CMAKE-003": "INV-NO-PRODUCTION-LEGACY-IMPORT",
    "BOUNDARY-LEGACY-000": "INV-NO-PRODUCTION-LEGACY-IMPORT",
    "BOUNDARY-LEGACY-001": "INV-NO-PRODUCTION-LEGACY-IMPORT",
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    script_path = os.path.join(repo_root, "scripts", "verify_build_target_boundaries.py")
    if not os.path.isfile(script_path):
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.boundary_violation_analyzer",
                severity="VIOLATION",
                confidence=0.98,
                file_path="scripts/verify_build_target_boundaries.py",
                line=1,
                evidence=["missing boundary scanner script"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-TOOLS-IN-RUNTIME"],
                related_paths=["scripts/verify_build_target_boundaries.py"],
            )
        ]

    proc = subprocess.run(
        [sys.executable, script_path, "--repo-root", repo_root],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    lines = [str(row).strip() for row in str(proc.stdout or "").splitlines() if str(row).strip()]

    out: List[Dict[str, object]] = []
    for row in lines:
        if row.startswith("BOUNDARY-OK:"):
            continue
        code = str(row.split(" ", 1)[0]).strip()
        rule_id = BOUNDARY_CODE_TO_RULE.get(code, "INV-NO-TOOLS-IN-RUNTIME")
        remainder = str(row[len(code) :]).strip()
        file_path = remainder.split(" ", 1)[0].strip() if remainder else "scripts/verify_build_target_boundaries.py"
        if ":" in file_path:
            file_path = file_path.split(":", 1)[0]
        file_path = _norm(file_path)
        if not file_path or file_path.startswith("BOUNDARY-"):
            file_path = "scripts/verify_build_target_boundaries.py"
        line_no = 1
        if ":" in remainder:
            maybe_line = remainder.split(":", 1)[1].split(" ", 1)[0].strip()
            if maybe_line.isdigit():
                line_no = int(maybe_line)
        evidence = [row]
        if proc.returncode == 0:
            continue
        out.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.boundary_violation_analyzer",
                severity="VIOLATION",
                confidence=0.97,
                file_path=file_path,
                line=line_no,
                evidence=evidence,
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[rule_id],
                related_paths=[file_path],
            )
        )

    return sorted(out, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
