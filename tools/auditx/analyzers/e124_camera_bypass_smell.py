"""E124 Camera bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E124_CAMERA_BYPASS_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
CONTROL_ACTION_REGISTRY_PATH = "data/registries/control_action_registry.json"
SCAN_ROOTS = ("src", "tools/xstack/sessionx")
SCAN_EXTENSIONS = (".py",)
LEGACY_CAMERA_PATTERN = re.compile(
    r"process_id\s*(?:==|in)\s*.*process\.camera_(?:bind_target|unbind_target|set_view_mode)",
    re.IGNORECASE,
)
ALLOWED_LEGACY_PATHS = {
    "tools/xstack/sessionx/process_runtime.py",
}


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


def _scan_candidate_files(repo_root: str):
    for root_rel in SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                if not str(name).lower().endswith(SCAN_EXTENSIONS):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith("tools/xstack/testx/tests/"):
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    process_runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    required_runtime_tokens = (
        "elif process_id == \"process.view_bind\":",
        "process_id = \"process.view_bind\"",
        "apply_view_binding(",
    )
    if not process_runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="control.camera_bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime missing; cannot verify camera control-plane routing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-CHANGES-THROUGH-CONTROL", "INV-NO-DIRECT-CAMERA-TOGGLE"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
        return findings

    for token in required_runtime_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="control.camera_bypass_smell",
                severity="RISK",
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["missing camera routing token", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-CHANGES-THROUGH-CONTROL", "INV-NO-DIRECT-CAMERA-TOGGLE"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    registry_text = _read_text(repo_root, CONTROL_ACTION_REGISTRY_PATH)
    if "\"action.view.change_policy\"" not in registry_text or "\"process.view_bind\"" not in registry_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="control.camera_bypass_smell",
                severity="WARN",
                confidence=0.82,
                file_path=CONTROL_ACTION_REGISTRY_PATH,
                line=1,
                evidence=["action.view.change_policy is not bound to process.view_bind"],
                suggested_classification="PROTOTYPE",
                recommended_action="ADD_RULE",
                related_invariants=["INV-VIEW-CHANGES-THROUGH-CONTROL"],
                related_paths=[CONTROL_ACTION_REGISTRY_PATH],
            )
        )

    for rel_path in _scan_candidate_files(repo_root):
        if rel_path in ALLOWED_LEGACY_PATHS:
            continue
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not LEGACY_CAMERA_PATTERN.search(str(line)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="control.camera_bypass_smell",
                    severity="WARN",
                    confidence=0.76,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "legacy direct camera process branch detected outside canonical runtime adapter",
                        str(line).strip()[:200],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-DIRECT-CAMERA-TOGGLE"],
                    related_paths=[rel_path, PROCESS_RUNTIME_PATH],
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

