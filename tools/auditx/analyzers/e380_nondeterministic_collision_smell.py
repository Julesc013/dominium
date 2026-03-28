"""E380 EARTH-6 nondeterministic collision smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E380_NONDETERMINISTIC_COLLISION_SMELL"
COLLISION_PROVIDER_REL = "embodiment/collision/macro_heightfield_provider.py"
PROCESS_RUNTIME_REL = "tools/xstack/sessionx/process_runtime.py"
PROBE_REL = "tools/embodiment/earth6_probe.py"
REPLAY_REL = "tools/embodiment/tool_replay_movement_window.py"
DOC_REL = "docs/embodiment/TERRAIN_COLLISION_MODEL.md"
REQUIRED_TOKENS = {
    COLLISION_PROVIDER_REL: (
        "resolve_macro_heightfield_sample(",
        "invalidate_macro_heightfield_cache_for_tiles(",
        '"sampling_bounded": True',
        "geo_cell_key_neighbors(",
    ),
    PROCESS_RUNTIME_REL: (
        "_body_surface_query(",
        "_evaluate_slope_response(",
        "_apply_ground_contact(",
        '"terrain_collision_state"',
    ),
    PROBE_REL: (
        "ground_contact_report(",
        "slope_modifier_report(",
        "geometry_edit_height_report(",
        "verify_collision_window_replay(",
    ),
    REPLAY_REL: (
        "Verify EARTH-6 terrain collision replay determinism.",
        "verify_collision_window_replay",
    ),
    DOC_REL: (
        "Terrain height is queried deterministically from the active collision provider.",
        "Geometry edits that change height invalidate collision samples locally.",
        "No UI, renderer, or tool may commit terrain contact directly.",
    ),
}
FORBIDDEN_TOKENS = ("random.", "uuid", "secrets.", "time.time(", "datetime.now(", "os.urandom(", "random.seed(", "time.sleep(")


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
                    category="embodiment.nondeterministic_collision_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-6 collision artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-COLLISION-DETERMINISTIC", "INV-NO-POSITION-WRITE-BYPASS"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.nondeterministic_collision_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-6 collision marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-COLLISION-DETERMINISTIC", "INV-NO-POSITION-WRITE-BYPASS"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )

    for rel_path in (COLLISION_PROVIDER_REL, PROCESS_RUNTIME_REL, PROBE_REL, REPLAY_REL):
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
                    category="embodiment.nondeterministic_collision_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden nondeterministic collision token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-COLLISION-DETERMINISTIC"],
                    related_paths=[COLLISION_PROVIDER_REL, PROCESS_RUNTIME_REL, PROBE_REL, REPLAY_REL, DOC_REL],
                )
            )
            break
    return findings
