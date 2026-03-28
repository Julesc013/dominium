"""E172 truth-based trust smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E172_TRUTH_BASED_TRUST_SMELL"


class TruthBasedTrustSmell:
    analyzer_id = ANALYZER_ID


_OMNISCIENT_PATTERNS = (
    re.compile(r"\btruth_model\b", re.IGNORECASE),
    re.compile(r"\buniverse_state\b", re.IGNORECASE),
    re.compile(r"\bground_truth\b", re.IGNORECASE),
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

    trust_engine_rel = "signals/trust/trust_engine.py"
    trust_engine_text = _read_text(repo_root, trust_engine_rel)
    if "truth_verification_state" in trust_engine_text and "allow_truth_observer" not in trust_engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.truth_based_trust_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=trust_engine_rel,
                line=1,
                evidence=["truth verification input present without explicit observer entitlement gate"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-OMNISCIENT-TRUST-UPDATES"],
                related_paths=[trust_engine_rel],
            )
        )

    allow_files = {
        "tools/auditx/analyzers/e172_truth_based_trust_smell.py",
    }
    scan_root = os.path.join(repo_root, "src", "signals")
    if not os.path.isdir(scan_root):
        return findings

    for walk_root, _dirs, files in os.walk(scan_root):
        for name in files:
            if not name.endswith(".py"):
                continue
            abs_path = os.path.join(walk_root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if rel_path in allow_files:
                continue
            text = _read_text(repo_root, rel_path)
            if not text:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                snippet = str(line).strip()
                if (not snippet) or snippet.startswith("#"):
                    continue
                if not any(pattern.search(snippet) for pattern in _OMNISCIENT_PATTERNS):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.truth_based_trust_smell",
                        severity="VIOLATION",
                        confidence=0.92,
                        file_path=rel_path,
                        line=line_no,
                        evidence=["trust/belief flow references omniscient truth symbol", snippet[:140]],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-OMNISCIENT-TRUST-UPDATES"],
                        related_paths=[rel_path, trust_engine_rel],
                    )
                )
                break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
