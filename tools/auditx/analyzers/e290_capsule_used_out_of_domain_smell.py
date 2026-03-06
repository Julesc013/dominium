"""E290 capsule-used-out-of-domain smell analyzer for PROC-5 validity discipline."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E290_CAPSULE_USED_OUT_OF_DOMAIN_SMELL"


class CapsuleUsedOutOfDomainSmell:
    analyzer_id = ANALYZER_ID


_CAPSULE_USE_PATTERNS = (
    re.compile(r"\bprocess_capsule_rows\b", re.IGNORECASE),
    re.compile(r"\bcapsule_id\b", re.IGNORECASE),
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
        os.path.join(repo_root, "src", "process"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "src/process/capsules/capsule_builder.py",
        "src/process/capsules/capsule_executor.py",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/process/tool_replay_capsule_window.py",
        "tools/xstack/repox/check.py",
    }
    required_validity_tokens = (
        "validity_domain_ref",
        "_range_violations(",
        "REFUSAL_PROCESS_CAPSULE_OUT_OF_DOMAIN",
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
                    if not any(pattern.search(snippet) for pattern in _CAPSULE_USE_PATTERNS):
                        continue
                    if any(token in text for token in required_validity_tokens):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="governance.capsule_used_out_of_domain_smell",
                            severity="RISK",
                            confidence=0.84,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "process capsule access appears outside validity-domain guarded execution paths",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-CAPSULE-ERROR-BOUNDS-REQUIRED",
                            ],
                            related_paths=[
                                rel_path,
                                "src/process/capsules/capsule_executor.py",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
