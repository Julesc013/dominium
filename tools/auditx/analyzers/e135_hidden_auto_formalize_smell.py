"""E135 hidden auto formalize smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E135_HIDDEN_AUTO_FORMALIZE_SMELL"
RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
INFERENCE_REL = "src/infrastructure/formalization/inference_engine.py"
_AUTO_FORMALIZE_PATTERNS = (
    re.compile(r"\bauto[_\-]?formaliz", re.IGNORECASE),
    re.compile(r"\bformaliz(?:e|ation)[^\n]*\bauto\b", re.IGNORECASE),
    re.compile(r"\bauto[_\-]?accept\b", re.IGNORECASE),
    re.compile(r"\bformalization_[^\n]*\baccept\b[^\n]*\bwithout\b", re.IGNORECASE),
)
_DIRECT_FORMAL_STATE_PATTERN = re.compile(r"[\"']state[\"']\s*[:=]\s*[\"']formal[\"']")


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
    inference_text = _read_text(repo_root, INFERENCE_REL)
    if (not runtime_text) or (not inference_text):
        missing = RUNTIME_REL if not runtime_text else INFERENCE_REL
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.hidden_auto_formalize_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=missing,
                line=1,
                evidence=["missing required formalization runtime/inference integration file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FORMALIZATION-THROUGH-CONTROL", "INV-INFERENCE-DERIVED-ONLY"],
                related_paths=[RUNTIME_REL, INFERENCE_REL],
            )
        )
        return findings

    for token in (
        'elif process_id == "process.formalization_accept_candidate":',
        "require_confirmation = bool(policy_row.get(\"require_confirmation\", True))",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.hidden_auto_formalize_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=RUNTIME_REL,
                line=1,
                evidence=["missing explicit confirmation gate token for formalization accept", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FORMALIZATION-THROUGH-CONTROL"],
                related_paths=[RUNTIME_REL],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    allowed_paths = {
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
                if rel_path in allowed_paths:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if any(pattern.search(snippet) for pattern in _AUTO_FORMALIZE_PATTERNS):
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="architecture.hidden_auto_formalize_smell",
                                severity="RISK",
                                confidence=0.87,
                                file_path=rel_path,
                                line=line_no,
                                evidence=["auto-formalization marker detected outside runtime policy gate", snippet[:180]],
                                suggested_classification="NEEDS_REVIEW",
                                recommended_action="ADD_RULE",
                                related_invariants=["INV-FORMALIZATION-THROUGH-CONTROL"],
                                related_paths=[rel_path, RUNTIME_REL],
                            )
                        )
                        break
                    if _DIRECT_FORMAL_STATE_PATTERN.search(snippet):
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="architecture.hidden_auto_formalize_smell",
                                severity="RISK",
                                confidence=0.85,
                                file_path=rel_path,
                                line=line_no,
                                evidence=["direct formal state marker found outside formalization runtime", snippet[:180]],
                                suggested_classification="NEEDS_REVIEW",
                                recommended_action="ADD_RULE",
                                related_invariants=["INV-FORMALIZATION-THROUGH-CONTROL"],
                                related_paths=[rel_path, RUNTIME_REL],
                            )
                        )
                        break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

