"""E27 hidden non-diegetic window smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E27_HIDDEN_NONDIEGETIC_WINDOW_SMELL"
PLAYER_WORKSPACE_PACK_PATH = "packs/tool/workspace.player.diegetic_default/pack.json"
PLAYER_WORKSPACE_ROOT = "packs/tool/workspace.player.diegetic_default"
UI_HOST_PATH = "tools/xstack/sessionx/ui_host.py"
FORBIDDEN_WINDOW_PREFIXES = (
    "window.tool.",
    "window.observer.",
    "window.spectator.",
)
FORBIDDEN_ENTITLEMENT_TOKENS = (
    "entitlement.control.admin",
    "entitlement.debug_view",
    "entitlement.inspect",
    "entitlement.teleport",
    "entitlement.time_control",
    "lens.nondiegetic.access",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return {}
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _sorted_tokens(values: object):
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _window_rel(path_token: str) -> str:
    return "{}/{}".format(PLAYER_WORKSPACE_ROOT, str(path_token).strip().replace("\\", "/"))


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    workspace_pack = _load_json(repo_root, PLAYER_WORKSPACE_PACK_PATH)
    if not workspace_pack:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="ui.hidden_nondiegetic_window_smell",
                severity="RISK",
                confidence=0.95,
                file_path=PLAYER_WORKSPACE_PACK_PATH,
                line=1,
                evidence=["Player workspace pack missing/unreadable."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DIEGETIC-DEFAULT-PROFILE-PRESENT"],
                related_paths=[PLAYER_WORKSPACE_PACK_PATH],
            )
        )
        return findings

    contributions = [dict(row) for row in list(workspace_pack.get("contributions") or []) if isinstance(row, dict)]
    for row in sorted(contributions, key=lambda item: str(item.get("id", ""))):
        window_id = str(row.get("id", "")).strip()
        if any(window_id.startswith(prefix) for prefix in FORBIDDEN_WINDOW_PREFIXES):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.hidden_nondiegetic_window_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=PLAYER_WORKSPACE_PACK_PATH,
                    line=1,
                    evidence=[
                        "Player workspace contribution contains non-player window id prefix.",
                        window_id,
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                    related_paths=[PLAYER_WORKSPACE_PACK_PATH],
                )
            )
        rel_path = str(row.get("path", "")).strip()
        if not rel_path:
            continue
        descriptor_rel = _window_rel(rel_path)
        descriptor_payload = _load_json(repo_root, descriptor_rel)
        if not descriptor_payload:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.hidden_nondiegetic_window_smell",
                    severity="WARN",
                    confidence=0.82,
                    file_path=descriptor_rel,
                    line=1,
                    evidence=["Player workspace window descriptor missing/unreadable.", window_id],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-DIEGETIC-DEFAULT-PROFILE-PRESENT"],
                    related_paths=[descriptor_rel, PLAYER_WORKSPACE_PACK_PATH],
                )
            )
            continue
        required_lenses = _sorted_tokens(descriptor_payload.get("required_lenses") or [])
        if any(token.startswith("lens.nondiegetic.") for token in required_lenses):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.hidden_nondiegetic_window_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=descriptor_rel,
                    line=1,
                    evidence=[
                        "Player workspace window requires nondiegetic lens.",
                        ",".join(required_lenses),
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                    related_paths=[descriptor_rel],
                )
            )
        required_entitlements = _sorted_tokens(descriptor_payload.get("required_entitlements") or [])
        forbidden_hits = [token for token in required_entitlements if token in FORBIDDEN_ENTITLEMENT_TOKENS]
        if forbidden_hits:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui.hidden_nondiegetic_window_smell",
                    severity="WARN",
                    confidence=0.84,
                    file_path=descriptor_rel,
                    line=1,
                    evidence=[
                        "Player workspace window requests forbidden debug entitlement token.",
                        forbidden_hits[0],
                    ],
                    suggested_classification="PROTOTYPE",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                    related_paths=[descriptor_rel],
                )
            )

    ui_host_abs = os.path.join(repo_root, UI_HOST_PATH.replace("/", os.sep))
    if not os.path.isfile(ui_host_abs):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="ui.hidden_nondiegetic_window_smell",
                severity="WARN",
                confidence=0.8,
                file_path=UI_HOST_PATH,
                line=1,
                evidence=["UI host missing; non-diegetic window gating cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                related_paths=[UI_HOST_PATH],
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

    try:
        ui_host_text = open(ui_host_abs, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        ui_host_text = ""
    required_tokens = (
        "def _is_nondiegetic_window(",
        "allow_nondiegetic_overlays",
        "window_is_nondiegetic",
    )
    for token in required_tokens:
        if token in ui_host_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="ui.hidden_nondiegetic_window_smell",
                severity="WARN",
                confidence=0.78,
                file_path=UI_HOST_PATH,
                line=1,
                evidence=[
                    "UI host missing nondiegetic window gating token.",
                    token,
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                related_paths=[UI_HOST_PATH],
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
