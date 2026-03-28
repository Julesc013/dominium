"""E173 unlogged trust change smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E173_UNLOGGED_TRUST_CHANGE_SMELL"


class UnloggedTrustChangeSmell:
    analyzer_id = ANALYZER_ID


_TRUST_MUTATION_PATTERNS = (
    re.compile(r"\btrust_edge_rows\s*=", re.IGNORECASE),
    re.compile(r"\bsignal_trust_edge_rows\s*=", re.IGNORECASE),
    re.compile(r"\btrust_weight\s*=", re.IGNORECASE),
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
    required_tokens = (
        '"process_id": "process.trust_update"',
        '"process_id": "process.message_verify_claim"',
        "decision_id",
    )
    for token in required_tokens:
        if token in trust_engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_trust_change_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=trust_engine_rel,
                line=1,
                evidence=["missing trust decision-log anchor token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-VERIFICATION-PROCESS-ONLY"],
                related_paths=[trust_engine_rel],
            )
        )

    allow_files = {
        trust_engine_rel,
        "tools/auditx/analyzers/e173_unlogged_trust_change_smell.py",
    }
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
    )
    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path in allow_files:
                    continue
                if rel_path.startswith(skip_prefixes):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _TRUST_MUTATION_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unlogged_trust_change_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["possible trust mutation path outside logged trust engine process", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-VERIFICATION-PROCESS-ONLY"],
                            related_paths=[rel_path, trust_engine_rel],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
