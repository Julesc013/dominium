"""E379 EARTH-5 unbounded shadow sampling smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E379_UNBOUNDED_SHADOW_SAMPLING_SMELL"
HORIZON_SHADOW_REL = "src/worldgen/earth/lighting/horizon_shadow_engine.py"
SHADOW_REGISTRY_REL = "data/registries/shadow_model_registry.json"
LIGHTING_VIEW_REL = "src/worldgen/earth/lighting/lighting_view_engine.py"
PROBE_REL = "tools/worldgen/earth5_probe.py"
REPLAY_REL = "tools/worldgen/tool_replay_illumination_view.py"
DOC_REL = "docs/worldgen/EARTH_ILLUMINATION_SHADOW_MODEL.md"
REQUIRED_TOKENS = {
    HORIZON_SHADOW_REL: (
        "sample_count",
        "step_distance_cells",
        "for sample_index in range(1, sample_count + 1):",
        '"sampling_bounded": True',
    ),
    SHADOW_REGISTRY_REL: (
        '"shadow_model_id": "shadow.horizon_stub_default"',
        '"sample_count": 8',
        '"step_distance_cells": 1',
    ),
    LIGHTING_VIEW_REL: (
        "evaluate_horizon_shadow(",
        '"cache_policy_id": "cache.lighting.observer_tick_bucket"',
    ),
    PROBE_REL: (
        "verify_illumination_view_replay",
        "sampling_bounded_report",
    ),
    REPLAY_REL: (
        "Verify EARTH-5 illumination replay determinism.",
    ),
    DOC_REL: (
        "K is fixed by the shadow model row",
        "no unbounded search is allowed",
    ),
}
FORBIDDEN_TOKENS = ("while ", "recursion", "recurse", "queue.append(", "stack.append(", "random.", "time.time(", "datetime.now(")


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
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.unbounded_shadow_sampling_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-5 bounded-shadow surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-SHADOW-BOUNDED"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.unbounded_shadow_sampling_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-5 bounded-shadow marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SHADOW-BOUNDED"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )

    for rel_path in (HORIZON_SHADOW_REL, LIGHTING_VIEW_REL, PROBE_REL, REPLAY_REL):
        text = _read_text(repo_root, rel_path)
        for line_no, line in enumerate(str(text or "").splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.unbounded_shadow_sampling_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden bounded-shadow token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SHADOW-BOUNDED"],
                    related_paths=[HORIZON_SHADOW_REL, LIGHTING_VIEW_REL, PROBE_REL, REPLAY_REL, DOC_REL],
                )
            )
            break
    return findings
