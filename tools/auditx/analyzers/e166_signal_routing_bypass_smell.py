"""E166 signal routing bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E166_SIGNAL_ROUTING_BYPASS_SMELL"


class SignalRoutingBypassSmell:
    analyzer_id = ANALYZER_ID


_DIRECT_ROUTE_PATTERN = re.compile(
    r"\bfor\b[^\n]*\bedge\b[^\n]*(from_node_id|to_node_id)|\b_has_direct_route\b",
    re.IGNORECASE,
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

    transport_rel = "signals/transport/transport_engine.py"
    transport_text = _read_text(repo_root, transport_rel)
    if transport_text and "query_route_result(" not in transport_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.signal_routing_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=transport_rel,
                line=1,
                evidence=["SIG transport lacks ABS route query usage", "query_route_result(...) missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-SIGNALS-USE-ABS-ROUTING"],
                related_paths=[transport_rel, "core/graph/routing_engine.py"],
            )
        )

    allow_files = {
        "signals/transport/transport_engine.py",
        "signals/transport/channel_executor.py",
    }
    scan_root = os.path.join(repo_root, "src", "signals")
    if os.path.isdir(scan_root):
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
                    if not _DIRECT_ROUTE_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.signal_routing_bypass_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["potential direct route logic in signals path", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-SIGNALS-USE-ABS-ROUTING"],
                            related_paths=[rel_path, "core/graph/routing_engine.py"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

