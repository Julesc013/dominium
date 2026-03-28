"""E76 hardcoded interaction smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E76_HARDCODED_INTERACTION_SMELL"
ACTION_SURFACE_ENGINE_PATH = "interaction/action_surface_engine.py"
AFFORDANCE_PATH = "client/interaction/affordance_generator.py"
REGISTRY_PATHS = (
    "data/registries/surface_type_registry.json",
    "data/registries/tool_tag_registry.json",
    "data/registries/surface_visibility_policy_registry.json",
)
FORBIDDEN_LITERAL_TOKENS = (
    'surface_type_id == "surface.',
    "startswith(\"surface.",
    "startswith('surface.",
    '== "bolt"',
    "== 'bolt'",
    '== "tree"',
    "== 'tree'",
)
REQUIRED_DATA_DRIVEN_TOKENS = (
    "_rows_from_registry(",
    "_surface_type_set(",
    "_tool_tag_set(",
    "_visibility_policy_rows(",
    "_surface_lists_from_entity(",
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

    for rel_path in REGISTRY_PATHS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.hardcoded_interaction_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["required ActionSurface registry file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-ACTION-SURFACE-DATA-DRIVEN"],
                related_paths=[rel_path],
            )
        )

    engine_text = _read_text(repo_root, ACTION_SURFACE_ENGINE_PATH)
    if not engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.hardcoded_interaction_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=ACTION_SURFACE_ENGINE_PATH,
                line=1,
                evidence=["ActionSurface engine missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-ACTION-SURFACE-DATA-DRIVEN"],
                related_paths=[ACTION_SURFACE_ENGINE_PATH],
            )
        )
    else:
        for token in REQUIRED_DATA_DRIVEN_TOKENS:
            if token in engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interaction.hardcoded_interaction_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=ACTION_SURFACE_ENGINE_PATH,
                    line=1,
                    evidence=["ActionSurface engine missing required registry-driven token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-ACTION-SURFACE-DATA-DRIVEN"],
                    related_paths=[ACTION_SURFACE_ENGINE_PATH],
                )
            )
        for token in FORBIDDEN_LITERAL_TOKENS:
            if token not in engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interaction.hardcoded_interaction_smell",
                    severity="VIOLATION",
                    confidence=0.92,
                    file_path=ACTION_SURFACE_ENGINE_PATH,
                    line=1,
                    evidence=["hardcoded interaction literal detected in ActionSurface engine", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-HARDCODED-SURFACE-LOGIC"],
                    related_paths=[ACTION_SURFACE_ENGINE_PATH],
                )
            )

    affordance_text = _read_text(repo_root, AFFORDANCE_PATH)
    if not affordance_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.hardcoded_interaction_smell",
                severity="RISK",
                confidence=0.9,
                file_path=AFFORDANCE_PATH,
                line=1,
                evidence=["affordance generator missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-ACTION-SURFACE-DATA-DRIVEN"],
                related_paths=[AFFORDANCE_PATH],
            )
        )
    else:
        for token in ("resolve_action_surfaces(", "_surface_affordance_row(", "allowed_process_ids"):
            if token in affordance_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interaction.hardcoded_interaction_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=AFFORDANCE_PATH,
                    line=1,
                    evidence=["affordance layer missing ActionSurface-driven token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-ACTION-SURFACE-DATA-DRIVEN"],
                    related_paths=[AFFORDANCE_PATH],
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

