"""E3 Handshake policy bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E3_HANDSHAKE_POLICY_BYPASS_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/",
    "tools/net/",
    "data/registries/net_replication_policy_registry.json",
    "data/registries/net_server_policy_registry.json",
    "data/registries/anti_cheat_policy_registry.json",
)

_POLICY_LITERAL_RE = re.compile(r"(policy\.net\.[a-z0-9_.-]+|policy\.ac\.[a-z0-9_.-]+)", re.IGNORECASE)
_DIRECT_BRANCH_RE = re.compile(
    r"\bif\b[^\n]*(policy\.net\.[a-z0-9_.-]+|policy\.ac\.[a-z0-9_.-]+)",
    re.IGNORECASE,
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_handshake_files(repo_root: str):
    roots = (
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
        os.path.join(repo_root, "tools", "net"),
    )
    for root in roots:
        if not os.path.isdir(root):
            continue
        for walk_root, dirs, files in os.walk(root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                ext = os.path.splitext(name.lower())[1]
                if ext not in {".py", ".json", ".md"}:
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if "handshake" not in rel_path.lower() and "net_cli.py" not in rel_path.lower():
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    required_registry_tokens = ("replication_registry", "anti_cheat_registry", "server_policy_registry")

    for rel_path in _iter_handshake_files(repo_root):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        try:
            lines = open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            continue
        text = "\n".join(lines)
        policy_fields_present = any(
            token in text
            for token in ("requested_replication_policy_id", "anti_cheat_policy_id", "server_policy_id")
        )
        if policy_fields_present:
            missing_tokens = [token for token in required_registry_tokens if token not in text]
            if missing_tokens:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.handshake_policy_bypass_smell",
                        severity="RISK",
                        confidence=0.88,
                        file_path=rel_path,
                        evidence=[
                            "Handshake/policy handling file is missing expected registry token(s): {}".format(
                                ", ".join(sorted(missing_tokens))
                            )
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NET-HANDSHAKE-USES-REGISTRIES"],
                        related_paths=[
                            rel_path,
                            "data/registries/net_replication_policy_registry.json",
                            "data/registries/net_server_policy_registry.json",
                            "data/registries/anti_cheat_policy_registry.json",
                        ],
                    )
                )

        for line_no, line in enumerate(lines, start=1):
            if _DIRECT_BRANCH_RE.search(str(line)):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.handshake_policy_bypass_smell",
                        severity="RISK",
                        confidence=0.9,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "Direct handshake branch on policy literal detected.",
                            str(line).strip()[:200],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NET-HANDSHAKE-USES-REGISTRIES"],
                        related_paths=[rel_path],
                    )
                )
            if _POLICY_LITERAL_RE.search(str(line)):
                lower = str(line).lower()
                if "data/registries/" in lower or "docs/net/" in lower:
                    continue
                if "tools/xstack/testx/tests/" in _norm(rel_path):
                    continue
                if "assert" in lower or "test_" in _norm(rel_path):
                    continue
                if "policy_id" in lower and "==" not in lower and "!=" not in lower and " in " not in lower:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.handshake_policy_bypass_smell",
                        severity="WARN",
                        confidence=0.78,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "Policy literal detected in handshake-related implementation path.",
                            str(line).strip()[:200],
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-HARDCODED-NET-POLICY-FLAGS"],
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
