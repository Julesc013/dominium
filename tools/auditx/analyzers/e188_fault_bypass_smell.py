"""E188 fault bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E188_FAULT_BYPASS_SMELL"


class FaultBypassSmell:
    analyzer_id = ANALYZER_ID


_FAULT_MUTATION_PATTERNS = (
    re.compile(r"\bstate\s*\[\s*[\"']elec_fault_states[\"']\s*\]\s*=", re.IGNORECASE),
    re.compile(r"\belec_fault_states\s*=\s*\[", re.IGNORECASE),
    re.compile(r"\bfault_state_hash_chain\b\s*=", re.IGNORECASE),
    re.compile(r"\bfault\.(?:overcurrent|short_circuit|ground_fault|open_circuit)\b", re.IGNORECASE),
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

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
        "schema/",
        "schemas/",
    )
    allowed_files = {
        "src/electric/fault/fault_engine.py",
        "src/electric/protection/protection_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _FAULT_MUTATION_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="authority.fault_bypass_smell",
                            severity="RISK",
                            confidence=0.89,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["fault mutation/detection path appears outside canonical electrical fault engine", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-ELEC-PROTECTION-THROUGH-SAFETY",
                                "INV-NO-ADHOC-FAULT-TRIP",
                            ],
                            related_paths=[
                                rel_path,
                                "src/electric/fault/fault_engine.py",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

