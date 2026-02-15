"""E4 Authoritative Truth leak analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E4_AUTHORITATIVE_TRUTH_LEAK"
WATCH_PREFIXES = (
    "src/net/policies/policy_server_authoritative.py",
    "tools/xstack/sessionx/runner.py",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    rel_path = "src/net/policies/policy_server_authoritative.py"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return findings
    try:
        lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return findings

    text = "\n".join(lines)
    if "observe_truth(" not in text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.authoritative_truth_leak",
                severity="RISK",
                confidence=0.92,
                file_path=rel_path,
                evidence=["server-authoritative policy missing observe_truth call for outbound state derivation"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-AUTHORITATIVE-USES-PERCEIVED-ONLY"],
                related_paths=[rel_path],
            )
        )
    if "schema_name=\"net_perceived_delta\"" not in text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.authoritative_truth_leak",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                evidence=["server-authoritative policy does not validate net_perceived_delta artifacts"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-AUTHORITATIVE-USES-PERCEIVED-ONLY"],
                related_paths=[rel_path],
            )
        )

    forbidden = re.compile(
        r"(send|socket|packet|transport|wire|payload_ref).*(truth_model|truthmodel|universe_state)"
        r"|"
        r"(truth_model|truthmodel|universe_state).*(send|socket|packet|transport|wire)",
        re.IGNORECASE,
    )
    for line_no, line in enumerate(lines, start=1):
        lower = str(line).lower()
        if "truth_snapshot_hash" in lower:
            continue
        if forbidden.search(str(line)):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.authoritative_truth_leak",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "Potential truth/universe state transmission indicator in authoritative policy.",
                        str(line).strip()[:200],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=[
                        "INV-AUTHORITATIVE-NO-TRUTH-TRANSMISSION",
                        "INV-NO-TRUTH-OVER-NET",
                    ],
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
