"""E378 EARTH-5 renderer truth-leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E378_RENDERER_TRUTH_LEAK_SMELL"
LIGHTING_VIEW_REL = "src/worldgen/earth/lighting/lighting_view_engine.py"
VIEWER_SHELL_REL = "src/client/ui/viewer_shell.py"
RENDER_MODEL_ADAPTER_REL = "src/client/render/render_model_adapter.py"
SOFTWARE_RENDERER_REL = "src/client/render/renderers/software_renderer.py"
NULL_RENDERER_REL = "src/client/render/renderers/null_renderer.py"
DOC_REL = "docs/worldgen/EARTH_ILLUMINATION_SHADOW_MODEL.md"
REQUIRED_TOKENS = {
    LIGHTING_VIEW_REL: (
        '"source_kind": "derived.illumination_view_artifact"',
        '"cache_policy_id": "cache.lighting.observer_tick_bucket"',
        '"lens_layer_ids": ["layer.illumination", "layer.shadow_factor"]',
    ),
    VIEWER_SHELL_REL: (
        "build_lighting_view_surface(",
        '"consumes_illumination_view_artifacts": True',
    ),
    RENDER_MODEL_ADAPTER_REL: (
        "illumination_view_artifact: dict | None = None",
        '"illumination_view_artifact": dict(illumination_view_artifact or {}),',
    ),
    SOFTWARE_RENDERER_REL: (
        'model_extensions.get("illumination_view_artifact")',
        "_apply_illumination(",
    ),
    NULL_RENDERER_REL: (
        'model_extensions.get("illumination_view_artifact")',
        '"illumination_artifact_ignored": illumination_artifact_ignored,',
    ),
    DOC_REL: (
        "UI and renderers consume the derived artifact only.",
        "renderers must not read terrain truth, process runtime, or hidden world state directly",
    ),
}
FORBIDDEN_TOKENS = (
    "truth_model[",
    "truth_model.",
    "universe_state[",
    "universe_state.",
    "process_runtime[",
    "process_runtime.",
)


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
                    category="renderer.renderer_truth_leak_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-5 illumination surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-LIGHTING-DERIVED-ONLY", "INV-NO-TRUTH-READ-IN-RENDER"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="renderer.renderer_truth_leak_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-5 derived-render marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-LIGHTING-DERIVED-ONLY", "INV-NO-TRUTH-READ-IN-RENDER"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )

    for rel_path in (RENDER_MODEL_ADAPTER_REL, SOFTWARE_RENDERER_REL, NULL_RENDERER_REL):
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
                    category="renderer.renderer_truth_leak_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden renderer truth-read token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-LIGHTING-DERIVED-ONLY", "INV-NO-TRUTH-READ-IN-RENDER"],
                    related_paths=[RENDER_MODEL_ADAPTER_REL, SOFTWARE_RENDERER_REL, NULL_RENDERER_REL, DOC_REL],
                )
            )
            break
    return findings
