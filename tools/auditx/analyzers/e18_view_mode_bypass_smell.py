"""E18 View mode bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E18_VIEW_MODE_BYPASS_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
HYBRID_COORDINATOR_PATH = "src/net/srz/shard_coordinator.py"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return ""
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    process_runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    if not process_runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="view_mode.bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["camera process runtime missing; view mode registry-driven enforcement cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-MODES-REGISTRY-DRIVEN"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
        return findings

    required_tokens = (
        "_view_mode_entries(navigation_indices)",
        "view mode '{}' is not declared in view mode registry",
        "control_policy.allowed_view_modes",
    )
    for token in required_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="view_mode.bypass_smell",
                severity="RISK",
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=[
                    "Missing camera/view registry-driven validation token.",
                    token,
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-MODES-REGISTRY-DRIVEN"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    hardcoded_view_branch = re.compile(
        r"if\s+.*(?:==|!=|in\s*\()\s*[\"']view\.[a-z0-9_.-]+[\"']",
        re.IGNORECASE,
    )
    for idx, line in enumerate(process_runtime_text.splitlines(), start=1):
        if not hardcoded_view_branch.search(str(line)):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="view_mode.bypass_smell",
                severity="WARN",
                confidence=0.8,
                file_path=PROCESS_RUNTIME_PATH,
                line=idx,
                evidence=[
                    "Hardcoded view mode branch detected.",
                    str(line).strip(),
                ],
                suggested_classification="PROTOTYPE",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-MODES-REGISTRY-DRIVEN"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    coordinator_text = _read_text(repo_root, HYBRID_COORDINATOR_PATH)
    if not coordinator_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="view_mode.bypass_smell",
                severity="WARN",
                confidence=0.75,
                file_path=HYBRID_COORDINATOR_PATH,
                line=1,
                evidence=["SRZ coordinator missing; cross-shard view mode policy checks cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-MODES-REGISTRY-DRIVEN"],
                related_paths=[HYBRID_COORDINATOR_PATH],
            )
        )
        return sorted(
            findings,
            key=lambda item: (
                _norm(item.location.file_path),
                item.location.line_start,
                item.severity,
            ),
        )

    coordinator_tokens = (
        "def _view_mode_row(",
        "_is_follow_view_mode(",
        "refusal.view.cross_shard_follow_forbidden",
    )
    for token in coordinator_tokens:
        if token in coordinator_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="view_mode.bypass_smell",
                severity="WARN",
                confidence=0.78,
                file_path=HYBRID_COORDINATOR_PATH,
                line=1,
                evidence=[
                    "Missing SRZ hybrid view mode policy token.",
                    token,
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-MODES-REGISTRY-DRIVEN"],
                related_paths=[HYBRID_COORDINATOR_PATH],
            )
        )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
