"""E134 spec bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E134_SPEC_BYPASS_SMELL"
RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
CONTROL_REL = "src/control/control_plane_engine.py"
SPEC_ENGINE_REL = "src/specs/spec_engine.py"


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

    runtime_text = _read_text(repo_root, RUNTIME_REL)
    control_text = _read_text(repo_root, CONTROL_REL)
    spec_engine_text = _read_text(repo_root, SPEC_ENGINE_REL)
    if (not runtime_text) or (not control_text) or (not spec_engine_text):
        missing = RUNTIME_REL if not runtime_text else (CONTROL_REL if not control_text else SPEC_ENGINE_REL)
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.spec_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=missing,
                line=1,
                evidence=["missing required spec integration file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-SPECSHEET-OPTIONAL"],
                related_paths=[RUNTIME_REL, CONTROL_REL, SPEC_ENGINE_REL],
            )
        )
        return findings

    required_runtime_tokens = (
        'elif process_id == "process.spec_apply_to_target":',
        'elif process_id == "process.spec_check_compliance":',
        "execution_policy_context[\"spec_compliance\"]",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.spec_bypass_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=RUNTIME_REL,
                line=1,
                evidence=["missing spec process/plan integration token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-SPECSHEET-OPTIONAL"],
                related_paths=[RUNTIME_REL],
            )
        )

    required_control_tokens = (
        "CONTROL_REFUSAL_SPEC_NONCOMPLIANT",
        "DOWNGRADE_SPEC_NONCOMPLIANT",
        "spec_compliance",
    )
    for token in required_control_tokens:
        if token in control_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.spec_bypass_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=CONTROL_REL,
                line=1,
                evidence=["missing control-plane spec compliance enforcement/logging token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-CONTROL-PLANE-ONLY-DISPATCH"],
                related_paths=[CONTROL_REL],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    allowed_eval_paths = {
        SPEC_ENGINE_REL,
        RUNTIME_REL,
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_eval_paths:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if not snippet or snippet.startswith("#"):
                        continue
                    if "evaluate_compliance(" not in snippet:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.spec_bypass_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["direct compliance evaluation outside runtime/spec engine", snippet[:180]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="ADD_RULE",
                            related_invariants=["INV-CONTROL-PLANE-ONLY-DISPATCH"],
                            related_paths=[rel_path, RUNTIME_REL, SPEC_ENGINE_REL],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

