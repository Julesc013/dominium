"""E35 Role escalation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E35_ROLE_ESCALATION_SMELL"
TARGET_PATH = "tools/xstack/sessionx/process_runtime.py"
REQUIRED_TOKENS = (
    "elif process_id == \"process.role_assign\":",
    "elif process_id == \"process.role_revoke\":",
    "allow_role_delegation",
    "delegable_entitlements",
    "_role_rows(",
    "_institution_type_rows(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


def _scan_targets(repo_root: str):
    roots = ("engine", "game", "server", "client", "tools/xstack")
    out = []
    for root in roots:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in files:
                if not name.lower().endswith((".py", ".cpp", ".cc", ".c", ".h", ".hpp")):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith(("tools/xstack/testx/tests/", "tools/auditx/")):
                    continue
                out.append(rel_path)
    return sorted(set(out))


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    target_rel = _norm(TARGET_PATH)
    target_abs = os.path.join(repo_root, target_rel.replace("/", os.sep))
    if not os.path.isfile(target_abs):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.role_escalation_smell",
                severity="RISK",
                confidence=0.95,
                file_path=target_rel,
                line=1,
                evidence=["process runtime missing; role delegation controls cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-ROLE-DELEGATION-GATED"],
                related_paths=[target_rel],
            )
        )
        return findings

    try:
        text = open(target_abs, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        text = ""
    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.role_escalation_smell",
                severity="RISK",
                confidence=0.9,
                file_path=target_rel,
                line=1,
                evidence=["Missing role delegation token.", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-ROLE-DELEGATION-GATED"],
                related_paths=[target_rel],
            )
        )

    role_write_pattern = re.compile(
        r"state\s*\[\s*[\"'](institution_assemblies|role_assignment_assemblies)[\"']\s*\]\s*=",
        re.IGNORECASE,
    )
    for rel_path in _scan_targets(repo_root):
        if rel_path == target_rel:
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            lowered = str(line).lower()
            if ("role_assignment_assemblies" not in lowered and "institution_assemblies" not in lowered) or (
                "process.role_assign" in lowered or "process.role_revoke" in lowered
            ):
                continue
            if role_write_pattern.search(str(line)) or re.search(
                r"\b(institution_assemblies|role_assignment_assemblies)\s*\.\s*(append|extend|insert|pop|remove|clear)\s*\(",
                str(line),
                re.IGNORECASE,
            ):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="civilisation.role_escalation_smell",
                        severity="VIOLATION",
                        confidence=0.96,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "Direct role/institution mutation detected outside gated process runtime.",
                            str(line).strip()[:140],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-ROLE-DELEGATION-GATED"],
                        related_paths=[target_rel, rel_path],
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

