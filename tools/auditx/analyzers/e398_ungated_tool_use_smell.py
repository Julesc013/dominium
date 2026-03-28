"""E398 ungated tool-use smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E398_UNGATED_TOOL_USE_SMELL"
REQUIRED_TOKENS = {
    "embodiment/tools/terrain_edit_tool.py": ('evaluate_tool_access(tool_id="tool.terrain_edit"',),
    "embodiment/tools/scanner_tool.py": ('evaluate_tool_access(', '"tool.scanner_basic"'),
    "embodiment/tools/logic_tool.py": (
        'evaluate_tool_access(tool_id="tool.logic_probe"',
        'evaluate_tool_access(tool_id="tool.logic_analyzer"',
    ),
    "embodiment/tools/teleport_tool.py": ('evaluate_tool_access(tool_id="tool.teleport"',),
    "embodiment/tools/toolbelt_engine.py": (
        "required_entitlement_id",
        '"refusal.tool.entitlement_missing"',
    ),
    "docs/embodiment/MVP_TOOLBELT_MODEL.md": (
        "Tool use is granted by `AuthorityContext` and constrained by `LawProfile`.",
        "`ent.tool.terrain_edit`",
    ),
}


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
    related_paths = list(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.ungated_tool_use_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EMB-1 tool entitlement surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-TOOLS-REQUIRE-ENTITLEMENT"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.ungated_tool_use_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EMB-1 tool-gating marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-TOOLS-REQUIRE-ENTITLEMENT"],
                    related_paths=related_paths,
                )
            )
    return findings
