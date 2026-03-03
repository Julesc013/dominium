"""E202 unbounded fire-spread smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E202_UNBOUNDED_SPREAD_SMELL"


class UnboundedSpreadSmell:
    analyzer_id = ANALYZER_ID


_SPREAD_LOOP_PATTERN = re.compile(
    r"\b(?:while\s+True|for\s+.*in\s+.*spread|spread_queue\.append|ignite)\b",
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

    thermal_engine_rel = "src/thermal/network/thermal_network_engine.py"
    thermal_engine_text = _read_text(repo_root, thermal_engine_rel)
    required_tokens = (
        "max_fire_spread_per_tick",
        "fire_iteration_limit",
        "spread_cap_reached",
    )
    for token in required_tokens:
        if token in thermal_engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_spread_smell",
                severity="RISK",
                confidence=0.88,
                file_path=thermal_engine_rel,
                line=1,
                evidence=["missing deterministic spread bound token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-FIRE-MODEL-ONLY"],
                related_paths=[thermal_engine_rel],
            )
        )

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
        thermal_engine_rel,
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
                    if not _SPREAD_LOOP_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unbounded_spread_smell",
                            severity="RISK",
                            confidence=0.79,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["potential spread/ignition loop outside canonical bounded thermal handler", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-ADHOC-BURN-LOGIC"],
                            related_paths=[
                                rel_path,
                                "src/thermal/network/thermal_network_engine.py",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

