"""E5 Cross-shard direct write smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E5_CROSS_SHARD_WRITE_SMELL"
WATCH_PREFIXES = (
    "src/net/srz/",
    "docs/net/SRZ_HYBRID_POLICY.md",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    rel_path = "net/srz/shard_coordinator.py"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.cross_shard_write_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                evidence=["SRZ shard coordinator module is missing."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-CROSS-SHARD-DIRECT-WRITES"],
                related_paths=[rel_path],
            )
        )
        return findings

    try:
        lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return findings

    text = "\n".join(lines)
    if "owner_shard_id != target_shard_id" not in text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.cross_shard_write_smell",
                severity="RISK",
                confidence=0.92,
                file_path=rel_path,
                evidence=["owner-target shard mismatch guard token is missing."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-CROSS-SHARD-DIRECT-WRITES"],
                related_paths=[rel_path],
            )
        )
    if "refusal.net.cross_shard_unsupported" not in text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.cross_shard_write_smell",
                severity="RISK",
                confidence=0.92,
                file_path=rel_path,
                evidence=["cross-shard refusal reason code token is missing from SRZ coordinator."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-CROSS-SHARD-DIRECT-WRITES"],
                related_paths=[rel_path, "docs/contracts/refusal_contract.md"],
            )
        )

    suspicious = re.compile(
        r"(target_shard_id|source_shard_id).*(runtime\[[\"']global_state[\"']\])"
        r"|"
        r"(runtime\[[\"']global_state[\"']\]).*(target_shard_id|source_shard_id)",
        re.IGNORECASE,
    )
    for line_no, line in enumerate(lines, start=1):
        if suspicious.search(str(line)):
            if "owner_shard_id != target_shard_id" in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.cross_shard_write_smell",
                    severity="WARN",
                    confidence=0.78,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "Potential shard-target/global-state coupling without explicit guard context.",
                        str(line).strip()[:200],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-CROSS-SHARD-DIRECT-WRITES"],
                    related_paths=[rel_path],
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

