"""E293 magic-unlock smell analyzer for PROC-7 research promotion discipline."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E293_MAGIC_UNLOCK_SMELL"


class MagicUnlockSmell:
    analyzer_id = ANALYZER_ID


_PROMOTION_PATTERNS = (
    re.compile(r"\bprocess_definition_rows\.append\s*\(", re.IGNORECASE),
    re.compile(r"\bcandidate_promotion_record_rows\b", re.IGNORECASE),
    re.compile(r"\bprocess\.candidate_promote_to_defined\b", re.IGNORECASE),
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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    for token in (
        'elif process_id == "process.candidate_promote_to_defined":',
        "evaluate_candidate_promotion(",
        "required_replications",
        "promotion_replication_threshold",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="governance.magic_unlock_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=[
                    "PROC-7 candidate promotion runtime path is missing required replication gate token",
                    token,
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-NO-MAGIC-UNLOCKS-RESEARCH",
                    "INV-PROMOTION-REQUIRES-REPLICATION",
                ],
                related_paths=[
                    runtime_rel,
                    "src/process/research/inference_engine.py",
                ],
            )
        )
    if (
        "refusal.process.candidate.promotion_denied" not in runtime_text
        and "REFUSAL_CANDIDATE_PROMOTION_DENIED" not in runtime_text
    ):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="governance.magic_unlock_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=[
                    "PROC-7 candidate promotion runtime path is missing required replication gate token",
                    "refusal.process.candidate.promotion_denied",
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-NO-MAGIC-UNLOCKS-RESEARCH",
                    "INV-PROMOTION-REQUIRES-REPLICATION",
                ],
                related_paths=[
                    runtime_rel,
                    "src/process/research/inference_engine.py",
                ],
            )
        )

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
        runtime_rel,
        "src/process/research/inference_engine.py",
        "tools/xstack/repox/check.py",
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
                    if not any(pattern.search(snippet) for pattern in _PROMOTION_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="governance.magic_unlock_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "candidate promotion token appears outside declared PROC-7 promotion pathways",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-MAGIC-UNLOCKS-RESEARCH",
                                "INV-PROMOTION-REQUIRES-REPLICATION",
                            ],
                            related_paths=[
                                rel_path,
                                runtime_rel,
                                "src/process/research/inference_engine.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
