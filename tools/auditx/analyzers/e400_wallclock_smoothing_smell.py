"""E400 EMB-2 wallclock/float smoothing smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E400_WALLCLOCK_SMOOTHING_SMELL"
SMOOTHING_REL = "src/embodiment/lens/camera_smoothing.py"
VIEWER_SHELL_REL = "src/client/ui/viewer_shell.py"
DOC_REL = "docs/embodiment/LOCOMOTION_POLISH_MODEL.md"
REQUIRED_TOKENS = {
    SMOOTHING_REL: (
        "resolve_smoothed_camera_state(",
        "// 1000",
        '"smoothing_applied": bool(applied)',
    ),
    VIEWER_SHELL_REL: (
        "resolve_smoothed_camera_state(",
        '"camera_smoothing": {',
    ),
    DOC_REL: (
        "The helper uses fixed-point bounded blending.",
        "no time-based exponential using wall-clock",
    ),
}
FORBIDDEN_TOKENS = (
    "float(",
    "math.exp(",
    "math.sin(",
    "math.cos(",
    "perf_counter(",
    "time.time(",
    "datetime.now(",
    "time.sleep(",
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
                    category="embodiment.wallclock_smoothing_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EMB-2 smoothing surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-CAMERA-SMOOTH-RENDER-ONLY", "INV-NO-FLOAT-SMOOTHING"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.wallclock_smoothing_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EMB-2 fixed-point smoothing marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CAMERA-SMOOTH-RENDER-ONLY", "INV-NO-FLOAT-SMOOTHING"],
                    related_paths=related_paths,
                )
            )

    for rel_path in (SMOOTHING_REL, VIEWER_SHELL_REL):
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
                    category="embodiment.wallclock_smoothing_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden EMB-2 smoothing token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CAMERA-SMOOTH-RENDER-ONLY", "INV-NO-FLOAT-SMOOTHING"],
                    related_paths=related_paths,
                )
            )
            break
    return findings
