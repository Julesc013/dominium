"""E401 EMB-2 truth-mutation-from-lens smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E401_TRUTH_MUTATION_FROM_LENS_SMELL"
SMOOTHING_REL = "src/embodiment/lens/camera_smoothing.py"
LENS_ENGINE_REL = "src/embodiment/lens/lens_engine.py"
VIEWER_SHELL_REL = "src/client/ui/viewer_shell.py"
DOC_REL = "docs/embodiment/LOCOMOTION_POLISH_MODEL.md"
REQUIRED_TOKENS = {
    SMOOTHING_REL: (
        "resolve_smoothed_camera_state(",
        '"camera_state": dict(smoothed_state)',
        '"smoothing_applied": bool(applied)',
    ),
    VIEWER_SHELL_REL: (
        '"camera_target_state": dict(camera_state)',
        "camera_viewpoint_override=_as_map(control_surface.get(\"camera_state\"))",
    ),
    DOC_REL: (
        "Camera smoothing is render-only.",
        "No smoothing state may mutate authoritative body or camera truth.",
    ),
}
FORBIDDEN_TOKENS = (
    'state["body_assemblies"]',
    "state['body_assemblies']",
    'state["body_states"]',
    "state['body_states']",
    'state["momentum_states"]',
    "state['momentum_states']",
    "truth_model.",
    "universe_state.",
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
    related_paths = list(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.truth_mutation_from_lens_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EMB-2 render-only lens surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-CAMERA-SMOOTH-RENDER-ONLY"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.truth_mutation_from_lens_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EMB-2 render-only lens marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CAMERA-SMOOTH-RENDER-ONLY"],
                    related_paths=related_paths,
                )
            )

    for rel_path in (SMOOTHING_REL, LENS_ENGINE_REL):
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
                    category="embodiment.truth_mutation_from_lens_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden EMB-2 lens mutation token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CAMERA-SMOOTH-RENDER-ONLY"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
