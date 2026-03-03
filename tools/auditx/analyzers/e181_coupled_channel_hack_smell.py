"""E181 coupled channel hack smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E181_COUPLED_CHANNEL_HACK_SMELL"


class CoupledChannelHackSmell:
    analyzer_id = ANALYZER_ID


_HACK_PATTERNS = (
    re.compile(r"\b(?:channel_p_id|channel_q_id|channel_s_id|p_channel_id|q_channel_id|s_channel_id)\b", re.IGNORECASE),
    re.compile(r"\bif\b[^\n]*quantity_id[^\n]*(?:power\.active|power\.reactive|power\.apparent)", re.IGNORECASE),
    re.compile(r"\blinked_channels?\b[^\n]*(?:phasor|coupled|pressure|latency|heat)", re.IGNORECASE),
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
        os.path.join(repo_root, "src", "core", "flow"),
        os.path.join(repo_root, "src", "models"),
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
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in _HACK_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.coupled_channel_hack_smell",
                            severity="RISK",
                            confidence=0.80,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["possible coupled-quantity hack detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-COUPLED-QUANTITY-HACKS"],
                            related_paths=[rel_path, "docs/architecture/QUANTITY_BUNDLES.md"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
