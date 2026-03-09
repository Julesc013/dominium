"""E368 embodiment direct position write smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E368_DIRECT_POSITION_WRITE_SMELL"
WATCH_PREFIXES = ("src/embodiment/", "tools/xstack/sessionx/", "tools/mvp/", "docs/embodiment/")
BODY_SYSTEM_REL = "src/embodiment/body/body_system.py"
LENS_ENGINE_REL = "src/embodiment/lens/lens_engine.py"
PROCESS_RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
RUNTIME_BUNDLE_REL = "tools/mvp/runtime_bundle.py"
DOC_REL = "docs/embodiment/EMBODIMENT_BASELINE.md"
REQUIRED_TOKENS = {
    PROCESS_RUNTIME_REL: (
        'elif process_id == "process.body_apply_input":',
        'elif process_id == "process.body_tick":',
        "build_force_application(",
        "_upsert_body_state_for_body(",
        "_resolve_body_collisions(",
        'state["force_application_rows"]',
    ),
    RUNTIME_BUNDLE_REL: (
        '"move": "process.body_apply_input"',
        '"look": "process.body_apply_input"',
        '"teleport": "process.camera_teleport"',
    ),
    BODY_SYSTEM_REL: (
        "build_body_state(",
        "instantiate_body_system(",
        '"template_instance_record"',
        '"movement_params_ref"',
    ),
    DOC_REL: (
        "process.body_apply_input",
        "process.body_tick",
        "all authoritative body motion must occur through these processes",
        "no UI, renderer, or tool may write body transforms directly",
    ),
}
FORBIDDEN_TOKENS = (
    'state["body_assemblies"]',
    "state['body_assemblies']",
    'state["body_states"]',
    "state['body_states']",
    'state["momentum_states"]',
    "state['momentum_states']",
    'state["camera_assemblies"]',
    "state['camera_assemblies']",
    'body["transform_mm"] =',
    "body['transform_mm'] =",
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
                    category="embodiment.direct_position_write_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EMB-0 motion-governance artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-BODY-MOTION-PROCESS-ONLY"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.direct_position_write_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EMB-0 process-only motion marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-BODY-MOTION-PROCESS-ONLY"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )

    for rel_path in (BODY_SYSTEM_REL, LENS_ENGINE_REL):
        text = _read_text(repo_root, rel_path)
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
                    category="embodiment.direct_position_write_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden direct-position token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-BODY-MOTION-PROCESS-ONLY"],
                    related_paths=[BODY_SYSTEM_REL, LENS_ENGINE_REL, PROCESS_RUNTIME_REL],
                )
            )
            break
    return findings
