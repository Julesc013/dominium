"""E393 silent overlay conflict resolution smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E393_SILENT_CONFLICT_RESOLUTION_SMELL"
REQUIRED_TOKENS = {
    "src/geo/overlay/overlay_merge_engine.py": (
        "overlay_conflict_artifacts and overlay_conflict_mode in {\"refuse\", \"prompt_stub\"}",
        "refusal.overlay.conflict",
        "remedy.overlay.resolve_conflict_or_change_policy",
        "remedy.overlay.add_explicit_resolver_layer",
        "overlay_conflict_artifact_hash_chain",
    ),
    "docs/geo/OVERLAY_CONFLICT_POLICIES.md": (
        "overlay.conflict.last_wins",
        "overlay.conflict.refuse",
        "overlay.conflict.prompt_stub",
        "explain.overlay_conflict",
    ),
    "data/registries/overlay_conflict_policy_registry.json": (
        "overlay.conflict.last_wins",
        "overlay.conflict.refuse",
        "overlay.conflict.prompt_stub",
    ),
    "tools/geo/tool_explain_property_origin.py": (
        "overlay_conflict_contract_id",
        "explain.overlay_conflict",
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
                    category="geo.silent_conflict_resolution_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required overlay-conflict artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-OVERLAY-CONFLICT-POLICY-DECLARED",
                        "INV-CONFLICTS-NOT-SILENT-IN-STRICT",
                    ],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="geo.silent_conflict_resolution_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing overlay-conflict marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-OVERLAY-CONFLICT-POLICY-DECLARED",
                        "INV-CONFLICTS-NOT-SILENT-IN-STRICT",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
