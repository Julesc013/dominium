"""E323 random-failure smell analyzer for LOGIC-8."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E323_RANDOM_FAILURE_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e323_random_failure_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/FAULT_NOISE_SECURITY_MODEL.md",
    "src/logic/fault/",
    "src/logic/noise/",
    "src/logic/eval/sense_engine.py",
    "tools/logic/tool_replay_fault_window.py",
)

_NONDETERMINISTIC_PATTERNS = (
    re.compile(r"\brandom\.", re.IGNORECASE),
    re.compile(r"\brandint\s*\(", re.IGNORECASE),
    re.compile(r"\buniform\s*\(", re.IGNORECASE),
    re.compile(r"\btime\.time\s*\(", re.IGNORECASE),
    re.compile(r"\buuid4\s*\(", re.IGNORECASE),
    re.compile(r"\bos\.urandom\s*\(", re.IGNORECASE),
    re.compile(r"\bsecrets\.", re.IGNORECASE),
)


class RandomFailureSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _logic_runtime_paths(repo_root: str):
    for root_rel in ("src/logic/fault", "src/logic/noise", "tools/logic"):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                yield _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    doc_rel = "docs/logic/FAULT_NOISE_SECURITY_MODEL.md"
    doc_text = _read_text(repo_root, doc_rel).lower()
    for token in ("deterministic quantization", "named rng", "proof-visible", "deterministic"):
        if token in doc_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.random_failure_smell",
                severity="RISK",
                confidence=0.84,
                file_path=doc_rel,
                line=1,
                evidence=["fault/noise doctrine missing deterministic-noise token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-NO-UNDECLARED-NOISE"],
                related_paths=[doc_rel],
            )
        )

    noise_rel = "src/logic/noise/noise_engine.py"
    noise_text = _read_text(repo_root, noise_rel)
    for token in ("kind == \"quantize\"", "kind == \"named_rng\"", "rng_stream_name", "build_logic_noise_decision_row("):
        if token in noise_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.random_failure_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=noise_rel,
                line=1,
                evidence=["logic noise engine missing deterministic-noise token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNDECLARED-NOISE"],
                related_paths=[noise_rel],
            )
        )

    for rel_path in sorted(set(_logic_runtime_paths(repo_root))):
        text = _read_text(repo_root, rel_path)
        for pattern in _NONDETERMINISTIC_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="logic.random_failure_smell",
                    severity="VIOLATION",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["logic fault/noise path references nondeterministic token", match.group(0)],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-UNDECLARED-NOISE"],
                    related_paths=[rel_path],
                )
            )
            break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
