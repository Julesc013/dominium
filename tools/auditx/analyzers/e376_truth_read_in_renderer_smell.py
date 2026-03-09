"""E376 sky renderer truth-read smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E376_TRUTH_READ_IN_RENDERER_SMELL"
SKY_VIEW_ENGINE_REL = "src/worldgen/earth/sky/sky_view_engine.py"
VIEWER_SHELL_REL = "src/client/ui/viewer_shell.py"
RENDER_MODEL_ADAPTER_REL = "src/client/render/render_model_adapter.py"
SOFTWARE_RENDERER_REL = "src/client/render/renderers/software_renderer.py"
DOC_REL = "docs/worldgen/EARTH_SKY_STARFIELD_MODEL.md"
REQUIRED_TOKENS = {
    SKY_VIEW_ENGINE_REL: (
        '"source_kind": "derived.sky_view_artifact"',
        '"derived_only": True',
        '"artifact_class": "DERIVED_VIEW"',
    ),
    VIEWER_SHELL_REL: (
        "build_sky_view_surface(",
        '"consumes_sky_view_artifacts": True',
    ),
    RENDER_MODEL_ADAPTER_REL: (
        "sky_view_artifact: dict | None = None",
        '"sky_view_artifact": dict(sky_view_artifact or {}),',
    ),
    SOFTWARE_RENDERER_REL: (
        'model_extensions.get("sky_view_artifact")',
        "_draw_sky_background(",
        "_draw_sky_stars(",
        "_draw_sky_disk(",
    ),
    DOC_REL: (
        "UI and renderers consume sky-view artifacts only.",
        "Mutation of TruthModel is forbidden.",
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
                    category="renderer.truth_read_in_renderer_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-4 sky artifact surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-SKYVIEW-DERIVED-ONLY", "INV-NO-TRUTH-IN-UI"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="renderer.truth_read_in_renderer_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-4 derived-render marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SKYVIEW-DERIVED-ONLY", "INV-NO-TRUTH-IN-UI"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )

    for rel_path in (RENDER_MODEL_ADAPTER_REL, SOFTWARE_RENDERER_REL):
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
                    category="renderer.truth_read_in_renderer_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden renderer truth-read token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SKYVIEW-DERIVED-ONLY", "INV-NO-TRUTH-IN-UI"],
                    related_paths=[RENDER_MODEL_ADAPTER_REL, SOFTWARE_RENDERER_REL, DOC_REL],
                )
            )
            break
    return findings
