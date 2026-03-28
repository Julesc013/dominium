"""E369 UX-0 UI truth leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E369_UI_TRUTH_LEAK_SMELL"
VIEWER_SHELL_REL = "client/ui/viewer_shell.py"
MAP_VIEWS_REL = "client/ui/map_views.py"
INSPECT_PANELS_REL = "client/ui/inspect_panels.py"
DOC_REL = "docs/ux/MVP_VIEWER_SHELL.md"
REQUIRED_TOKENS = {
    VIEWER_SHELL_REL: (
        '"consumes_perceived_model_only": True',
        '"forbidden_truth_inputs": [',
        '"truth_model"',
        '"universe_state"',
        '"process_runtime"',
        "build_map_view_set(",
        "build_inspection_panel_set(",
    ),
    MAP_VIEWS_REL: (
        "_normalized_perceived_model(",
        "build_projected_view_artifact(",
        "truth_hash_anchor",
        '"cache_policy_id": "cache.truth_anchor_keyed"',
    ),
    INSPECT_PANELS_REL: (
        "build_inspection_overlays(",
        "explain_property_origin_report(",
        "process.inspect_generate_snapshot",
        "tool.geo.explain_property_origin",
    ),
    DOC_REL: (
        "UI consumes PerceivedModel and derived view artifacts only.",
        "It must not read or mutate TruthModel directly.",
        "The shell must not synthesize hidden state by reading runtime internals.",
    ),
}
FORBIDDEN_TOKENS = (
    "build_truth_model(",
    "observe_truth(",
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
                    category="ui.truth_leak_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["required UX-0 viewer artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-TRUTH-IN-UI"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.truth_leak_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing UX-0 truth-separation marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-IN-UI"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
    for rel_path in (VIEWER_SHELL_REL, MAP_VIEWS_REL, INSPECT_PANELS_REL):
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
                    category="ui.truth_leak_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden UI truth-access token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-IN-UI"],
                    related_paths=[VIEWER_SHELL_REL, MAP_VIEWS_REL, INSPECT_PANELS_REL],
                )
            )
            break
    return findings
