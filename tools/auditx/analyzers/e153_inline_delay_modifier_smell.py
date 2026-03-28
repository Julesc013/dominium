"""E153 inline delay modifier smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E153_INLINE_DELAY_MODIFIER_SMELL"


class InlineDelayModifierSmell:
    analyzer_id = ANALYZER_ID


_INLINE_DELAY_PATTERN = re.compile(
    r"\b(?:edge_eta_ticks|estimated_arrival_tick|delay_ticks|allowed_speed_mm_per_tick|progress_fraction_q16)\b\s*[*+\-\/]=\s*(?:0?\.\d+|\d+\s*/\s*\d+|\d+)",
    re.IGNORECASE,
)
_CONGESTION_CONTEXT_PATTERN = re.compile(
    r"\b(?:congestion|occupancy|capacity|traffic|edge_occupancy|multiplier_permille)\b",
    re.IGNORECASE,
)
_CONDITIONAL_DELAY_PATTERN = re.compile(
    r"\bif\b[^\n]*(?:congestion|occupancy|traffic)[^\n]*(?:speed|eta|delay|arrival|progress)\b",
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

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    allowed_files = {
        "tools/xstack/sessionx/process_runtime.py",
        "mobility/travel/travel_engine.py",
        "mobility/traffic/traffic_engine.py",
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
                    inline_delay = bool(_INLINE_DELAY_PATTERN.search(snippet))
                    conditional_delay = bool(_CONDITIONAL_DELAY_PATTERN.search(snippet))
                    if not (inline_delay or conditional_delay):
                        continue
                    if not (_CONGESTION_CONTEXT_PATTERN.search(snippet) or conditional_delay):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_delay_modifier_smell",
                            severity="RISK",
                            confidence=0.85,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["inline congestion/delay modifier detected outside mobility traffic/travel engines", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-NO-ADHOC-CONGESTION",
                                "INV-TRAVEL-THROUGH-COMMITMENTS",
                            ],
                            related_paths=[
                                rel_path,
                                "mobility/travel/travel_engine.py",
                                "mobility/traffic/traffic_engine.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

