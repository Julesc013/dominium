"""E382 water simulation leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E382_WATER_SIM_LEAK_SMELL"
WATER_ENGINE_REL = "worldgen/earth/water/water_view_engine.py"
VIEWER_SHELL_REL = "client/ui/viewer_shell.py"
RENDER_ADAPTER_REL = "client/render/render_model_adapter.py"
SOFTWARE_RENDERER_REL = "client/render/renderers/software_renderer.py"
WATER_PROBE_REL = "tools/worldgen/earth8_probe.py"
WATER_REPLAY_REL = "tools/worldgen/tool_replay_water_view.py"
WATER_DOC_REL = "docs/worldgen/EARTH_WATER_VISUAL_MODEL.md"
WATER_POLICY_REL = "data/registries/water_visual_policy_registry.json"
REQUIRED_TOKENS = {
    WATER_ENGINE_REL: (
        "build_water_view_surface(",
        '"source_kind": "derived.water_view_artifact"',
        '"artifact_class": "DERIVED_VIEW"',
        "tide_offset_value",
        "flow_target_tile_key",
    ),
    VIEWER_SHELL_REL: (
        "build_water_view_surface(",
        "build_water_layer_source_payloads(",
        '"water_view_surface": dict(water_view_surface)',
    ),
    RENDER_ADAPTER_REL: (
        "water_view_artifact: dict | None = None",
        '"water_view_artifact": dict(water_view_artifact or {}),',
    ),
    SOFTWARE_RENDERER_REL: (
        '_draw_water_surface_overlay(',
        'model_extensions.get("water_view_artifact")',
    ),
    WATER_PROBE_REL: (
        "verify_water_view_replay",
        "river_mask_report",
        "tide_offset_report",
    ),
    WATER_REPLAY_REL: (
        "EARTH-8 water-view replay determinism",
    ),
    WATER_POLICY_REL: (
        '"policy_id": "water.mvp_default"',
        '"tide_visual_strength"',
        '"reflection_strength"',
    ),
    WATER_DOC_REL: (
        "EARTH-8 is derived-view only.",
        "It does not simulate water volume, shoreline transport, or fluid pressure.",
        "Renderer-side fluid simulation is forbidden in MVP.",
    ),
}
FORBIDDEN_TOKENS = (
    "navier",
    "stokes",
    "shallow_water",
    "fluid_solve",
    "volume_sim",
    "wave_equation",
    "pressure_solve",
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
    related_paths = [
        WATER_ENGINE_REL,
        VIEWER_SHELL_REL,
        RENDER_ADAPTER_REL,
        SOFTWARE_RENDERER_REL,
        WATER_PROBE_REL,
        WATER_REPLAY_REL,
        WATER_POLICY_REL,
        WATER_DOC_REL,
    ]
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.water_sim_leak_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-8 water artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-WATER-VIEW-DERIVED-ONLY", "INV-NO-FLUID-SIM-IN-MVP"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.water_sim_leak_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-8 water marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-WATER-VIEW-DERIVED-ONLY", "INV-NO-FLUID-SIM-IN-MVP"],
                    related_paths=related_paths,
                )
            )
    for rel_path in (WATER_ENGINE_REL, WATER_PROBE_REL, WATER_REPLAY_REL, SOFTWARE_RENDERER_REL):
        text = _read_text(repo_root, rel_path).lower()
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.water_sim_leak_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden EARTH-8 water simulation token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-FLUID-SIM-IN-MVP"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
