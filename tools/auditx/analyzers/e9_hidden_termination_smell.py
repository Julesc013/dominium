"""E9 Hidden termination smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E9_HIDDEN_TERMINATION_SMELL"
WATCH_PREFIXES = (
    "src/net/anti_cheat/",
    "src/net/policies/",
    "src/net/srz/",
    "tools/xstack/repox/check.py",
)

ANTI_CHEAT_ENGINE_PATH = "net/anti_cheat/anti_cheat_engine.py"
POLICY_PATHS = (
    "net/policies/policy_server_authoritative.py",
    "net/srz/shard_coordinator.py",
    "net/policies/policy_lockstep.py",
)
DIRECT_TERMINATION_TOKENS = (
    "terminate_session(",
    "disconnect_peer(",
    "ban_peer(",
    "kick_peer(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return open(abs_path, "r", encoding="utf-8").read()


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    try:
        anti_cheat_engine_text = _read_text(repo_root, ANTI_CHEAT_ENGINE_PATH)
    except OSError:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.hidden_termination_smell",
                severity="RISK",
                confidence=0.95,
                file_path=ANTI_CHEAT_ENGINE_PATH,
                line=1,
                evidence=["anti-cheat engine missing; cannot verify explicit enforcement action logging"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-HIDDEN-BAN"],
                related_paths=[ANTI_CHEAT_ENGINE_PATH],
            )
        )
        return findings

    required_engine_tokens = (
        "anti_cheat_events",
        "anti_cheat_enforcement_actions",
        "_record_refusal_injection(",
        "ACTION_TERMINATE",
    )
    for token in required_engine_tokens:
        if token not in anti_cheat_engine_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.hidden_termination_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=ANTI_CHEAT_ENGINE_PATH,
                    line=1,
                    evidence=["missing anti-cheat enforcement/log token '{}'".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-HIDDEN-BAN"],
                    related_paths=[ANTI_CHEAT_ENGINE_PATH],
                )
            )

    for rel_path in POLICY_PATHS:
        try:
            text = _read_text(repo_root, rel_path)
        except OSError:
            continue
        if "terminate" not in text:
            continue
        required_tokens = ("_apply_enforcement_result(", "anti_cheat_enforcement_actions")
        if rel_path.endswith("policy_lockstep.py"):
            required_tokens = ("refusal_from_decision(",)
        for token in required_tokens:
            if token not in text:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.hidden_termination_smell",
                        severity="WARN",
                        confidence=0.8,
                        file_path=rel_path,
                        line=1,
                        evidence=["missing termination-governance token '{}'".format(token)],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-HIDDEN-BAN"],
                        related_paths=[rel_path],
                    )
                )

    net_root = os.path.join(repo_root, "src", "net")
    if os.path.isdir(net_root):
        for walk_root, dirs, files in os.walk(net_root):
            dirs[:] = sorted(dirs)
            for filename in sorted(files):
                _, ext = os.path.splitext(filename.lower())
                if ext not in (".py", ".c", ".cc", ".cpp", ".h", ".hpp"):
                    continue
                abs_path = os.path.join(walk_root, filename)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                try:
                    lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
                except OSError:
                    continue
                for line_no, line in enumerate(lines, start=1):
                    lower = str(line).lower()
                    if "terminated_peers" in lower and rel_path != ANTI_CHEAT_ENGINE_PATH:
                        if '"terminated_peers": []' in lower or "'terminated_peers': []" in lower:
                            continue
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="net.hidden_termination_smell",
                                severity="VIOLATION",
                                confidence=0.94,
                                file_path=rel_path,
                                line=line_no,
                                evidence=["terminated_peers mutation outside anti-cheat engine", str(line).strip()[:200]],
                                suggested_classification="INVALID",
                                recommended_action="ADD_RULE",
                                related_invariants=["INV-NO-HIDDEN-BAN"],
                                related_paths=[rel_path, ANTI_CHEAT_ENGINE_PATH],
                            )
                        )
                    if any(token in lower for token in DIRECT_TERMINATION_TOKENS):
                        if "anti_cheat" not in lower and "enforcement" not in lower:
                            findings.append(
                                make_finding(
                                    analyzer_id=ANALYZER_ID,
                                    category="net.hidden_termination_smell",
                                    severity="WARN",
                                    confidence=0.72,
                                    file_path=rel_path,
                                    line=line_no,
                                    evidence=["direct termination call without anti-cheat context", str(line).strip()[:200]],
                                    suggested_classification="TODO-BLOCKED",
                                    recommended_action="ADD_RULE",
                                    related_invariants=["INV-NO-HIDDEN-BAN"],
                                    related_paths=[rel_path],
                                )
                            )
                    if re.search(r"\baction\s*==\s*['\"]terminate['\"]", str(line), flags=re.IGNORECASE):
                        joined = "\n".join(lines[max(0, line_no - 3) : min(len(lines), line_no + 2)])
                        if "anti_cheat" not in joined and "refusal" not in joined:
                            findings.append(
                                make_finding(
                                    analyzer_id=ANALYZER_ID,
                                    category="net.hidden_termination_smell",
                                    severity="WARN",
                                    confidence=0.69,
                                    file_path=rel_path,
                                    line=line_no,
                                    evidence=["terminate branch not obviously tied to anti-cheat refusal/action log"],
                                    suggested_classification="TODO-BLOCKED",
                                    recommended_action="ADD_RULE",
                                    related_invariants=["INV-NO-HIDDEN-BAN"],
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

