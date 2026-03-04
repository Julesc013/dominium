"""E103 mount bypass smell analyzer for POSE-1 mount process rules."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E103_MOUNT_BYPASS_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
MOUNT_ENGINE_PATH = "src/interaction/mount/mount_engine.py"

REQUIRED_RUNTIME_TOKENS = (
    "process.mount_attach",
    "process.mount_detach",
    "attach_mount_points(",
    "detach_mount_point(",
    "event.mount_attach",
    "event.mount_detach",
)
REQUIRED_ENGINE_TOKENS = (
    "def attach_mount_points(",
    "def detach_mount_point(",
    "REFUSAL_MOUNT_INCOMPATIBLE",
    "REFUSAL_MOUNT_ALREADY_ATTACHED",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_missing_token_findings(findings, *, repo_root: str, rel_path: str, tokens) -> None:
    text = _read_text(repo_root, rel_path)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="pose.mount_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["required mount integration file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-MOUNT-REQUIRES-PROCESS"],
                related_paths=[rel_path],
            )
        )
        return
    for token in tokens:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="pose.mount_bypass_smell",
                severity="RISK",
                confidence=0.88,
                file_path=rel_path,
                line=1,
                evidence=["missing deterministic mount token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-MOUNT-REQUIRES-PROCESS"],
                related_paths=[rel_path],
            )
        )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=PROCESS_RUNTIME_PATH,
        tokens=REQUIRED_RUNTIME_TOKENS,
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=MOUNT_ENGINE_PATH,
        tokens=REQUIRED_ENGINE_TOKENS,
    )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

