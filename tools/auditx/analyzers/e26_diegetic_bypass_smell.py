"""E26 diegetic bypass smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E26_DIEGETIC_BYPASS_SMELL"
PLAYER_LAW_PATH = "packs/law/law.player.diegetic_default/data/law_profile.player.diegetic_default.json"
PLAYER_EXPERIENCE_PATH = "packs/experience/profile.player.default/data/experience_profile.player.default.json"
SERVER_PROFILE_PATH = "data/registries/server_profile_registry.json"
FORBIDDEN_PLAYER_PROCESSES = (
    "process.camera_teleport",
    "process.control_set_view_lens",
    "process.observe.telemetry",
    "process.time_control_set_rate",
    "process.time_pause",
    "process.time_resume",
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


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    law_payload = _load_json(repo_root, PLAYER_LAW_PATH)
    if not law_payload:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetic.bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=PLAYER_LAW_PATH,
                line=1,
                evidence=["Player diegetic law profile missing/unreadable."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DIEGETIC-DEFAULT-PROFILE-PRESENT"],
                related_paths=[PLAYER_LAW_PATH],
            )
        )
    else:
        allowed_lenses = _sorted_tokens(law_payload.get("allowed_lenses") or [])
        if any(token.startswith("lens.nondiegetic.") for token in allowed_lenses):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetic.bypass_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=PLAYER_LAW_PATH,
                    line=1,
                    evidence=["Player law allows nondiegetic lens token.", ",".join(allowed_lenses[:4])],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                    related_paths=[PLAYER_LAW_PATH],
                )
            )
        debug_allowances = dict(law_payload.get("debug_allowances") or {})
        if bool(debug_allowances.get("allow_nondiegetic_overlays", False)):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetic.bypass_smell",
                    severity="RISK",
                    confidence=0.92,
                    file_path=PLAYER_LAW_PATH,
                    line=1,
                    evidence=["Player law enables allow_nondiegetic_overlays=true."],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                    related_paths=[PLAYER_LAW_PATH],
                )
            )
        forbidden_processes = set(_sorted_tokens(law_payload.get("forbidden_processes") or []))
        for process_id in FORBIDDEN_PLAYER_PROCESSES:
            if process_id in forbidden_processes:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetic.bypass_smell",
                    severity="WARN",
                    confidence=0.8,
                    file_path=PLAYER_LAW_PATH,
                    line=1,
                    evidence=[
                        "Player law missing expected forbidden debug process.",
                        process_id,
                    ],
                    suggested_classification="PROTOTYPE",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                    related_paths=[PLAYER_LAW_PATH],
                )
            )

    experience_payload = _load_json(repo_root, PLAYER_EXPERIENCE_PATH)
    if not experience_payload:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetic.bypass_smell",
                severity="WARN",
                confidence=0.85,
                file_path=PLAYER_EXPERIENCE_PATH,
                line=1,
                evidence=["Player default experience profile missing/unreadable."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-DIEGETIC-DEFAULT-PROFILE-PRESENT"],
                related_paths=[PLAYER_EXPERIENCE_PATH],
            )
        )
    else:
        default_law_profile_id = str(experience_payload.get("default_law_profile_id", "")).strip()
        if default_law_profile_id != "law.player.diegetic_default":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetic.bypass_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=PLAYER_EXPERIENCE_PATH,
                    line=1,
                    evidence=[
                        "Player default experience does not bind player diegetic law profile.",
                        default_law_profile_id,
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DIEGETIC-DEFAULT-PROFILE-PRESENT"],
                    related_paths=[PLAYER_EXPERIENCE_PATH],
                )
            )

    server_profiles = _load_json(repo_root, SERVER_PROFILE_PATH)
    rows = (((server_profiles.get("record") or {}).get("profiles")) or []) if isinstance(server_profiles, dict) else []
    if isinstance(rows, list):
        ranked = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            if str(row.get("server_profile_id", "")).strip() == "server.profile.rank_strict":
                ranked = dict(row)
                break
        if ranked:
            allowed_laws = _sorted_tokens(ranked.get("allowed_law_profile_ids") or [])
            if "law.observer.truth" in allowed_laws or "law.admin.lab" in allowed_laws:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="diegetic.bypass_smell",
                        severity="RISK",
                        confidence=0.88,
                        file_path=SERVER_PROFILE_PATH,
                        line=1,
                        evidence=[
                            "Ranked strict profile allows observer/admin law profile carve-outs.",
                            ",".join(allowed_laws),
                        ],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-PLAYER_DEBUG_SURFACES"],
                        related_paths=[SERVER_PROFILE_PATH],
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
