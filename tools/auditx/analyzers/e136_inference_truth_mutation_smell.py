"""E136 inference truth mutation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E136_INFERENCE_TRUTH_MUTATION_SMELL"
INFERENCE_REL = "infrastructure/formalization/inference_engine.py"
FORMALIZATION_DIR = "src/infrastructure/formalization"
_FORBIDDEN_PATTERNS = (
    re.compile(r"\bstate\s*\["),
    re.compile(r"\bnetwork_graphs\b"),
    re.compile(r"\bformalization_states\b"),
    re.compile(r"\bformalization_events\b"),
    re.compile(r"\bcreate_commitment_row\s*\("),
    re.compile(r"\bexecute_intent\s*\("),
    re.compile(r"\bprocess\.formalization_", re.IGNORECASE),
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

    inference_text = _read_text(repo_root, INFERENCE_REL)
    if not inference_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="determinism.inference_truth_mutation_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=INFERENCE_REL,
                line=1,
                evidence=["missing formalization inference engine file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-INFERENCE-DERIVED-ONLY"],
                related_paths=[INFERENCE_REL],
            )
        )
        return findings

    for token in ("def infer_candidates(", "degrade.formalization.inference_budget"):
        if token in inference_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="determinism.inference_truth_mutation_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=INFERENCE_REL,
                line=1,
                evidence=["missing derived-only inference token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-INFERENCE-DERIVED-ONLY"],
                related_paths=[INFERENCE_REL],
            )
        )

    for line_no, line in enumerate(inference_text.splitlines(), start=1):
        snippet = str(line).strip()
        if (not snippet) or snippet.startswith("#"):
            continue
        if not any(pattern.search(snippet) for pattern in _FORBIDDEN_PATTERNS):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="determinism.inference_truth_mutation_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=INFERENCE_REL,
                line=line_no,
                evidence=["forbidden mutation/process token in inference engine", snippet[:180]],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-INFERENCE-DERIVED-ONLY"],
                related_paths=[INFERENCE_REL],
            )
        )
        break

    formalization_root = os.path.join(repo_root, FORMALIZATION_DIR.replace("/", os.sep))
    if os.path.isdir(formalization_root):
        for walk_root, _dirs, files in os.walk(formalization_root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if rel_path == INFERENCE_REL:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _FORBIDDEN_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="determinism.inference_truth_mutation_smell",
                            severity="RISK",
                            confidence=0.87,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["formalization module contains potential truth mutation token", snippet[:180]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="ADD_RULE",
                            related_invariants=["INV-INFERENCE-DERIVED-ONLY"],
                            related_paths=[rel_path, INFERENCE_REL],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

