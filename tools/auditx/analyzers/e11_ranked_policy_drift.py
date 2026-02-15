"""E11 Ranked policy drift analyzer."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E11_RANKED_POLICY_DRIFT"
WATCH_PREFIXES = (
    "data/registries/server_profile_registry.json",
    "data/registries/securex_policy_registry.json",
    "data/registries/anti_cheat_policy_registry.json",
    "docs/net/RANKED_SERVER_GOVERNANCE.md",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(path: str) -> Tuple[Dict[str, object], str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_object"
    return payload, ""


def _rows(payload: dict, key: str) -> List[dict]:
    rows = (((payload.get("record") or {}).get(key)) or [])
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, dict)]


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    server_profile_path = os.path.join(repo_root, "data", "registries", "server_profile_registry.json")
    securex_policy_path = os.path.join(repo_root, "data", "registries", "securex_policy_registry.json")
    anti_cheat_policy_path = os.path.join(repo_root, "data", "registries", "anti_cheat_policy_registry.json")

    server_profile_payload, server_profile_err = _load_json(server_profile_path)
    securex_policy_payload, securex_policy_err = _load_json(securex_policy_path)
    anti_cheat_policy_payload, anti_cheat_policy_err = _load_json(anti_cheat_policy_path)
    if server_profile_err or securex_policy_err or anti_cheat_policy_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.ranked_policy_drift",
                severity="RISK",
                confidence=0.95,
                file_path="data/registries/server_profile_registry.json",
                evidence=["Ranked-governance registries are missing or invalid JSON."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=[
                    "data/registries/server_profile_registry.json",
                    "data/registries/securex_policy_registry.json",
                    "data/registries/anti_cheat_policy_registry.json",
                ],
            )
        )
        return findings

    server_profile_rows = _rows(server_profile_payload, "profiles")
    securex_policy_rows = _rows(securex_policy_payload, "policies")
    anti_cheat_policy_rows = _rows(anti_cheat_policy_payload, "policies")
    securex_ids = set(str(row.get("securex_policy_id", "")).strip() for row in securex_policy_rows if str(row.get("securex_policy_id", "")).strip())
    anti_cheat_ids = set(str(row.get("policy_id", "")).strip() for row in anti_cheat_policy_rows if str(row.get("policy_id", "")).strip())

    ranked_row = {}
    for row in server_profile_rows:
        if str(row.get("server_profile_id", "")).strip() == "server.profile.rank_strict":
            ranked_row = dict(row)
            break
    if not ranked_row:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.ranked_policy_drift",
                severity="VIOLATION",
                confidence=0.98,
                file_path="data/registries/server_profile_registry.json",
                evidence=["Missing canonical ranked server profile 'server.profile.rank_strict'."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=["data/registries/server_profile_registry.json"],
            )
        )
        return findings

    ranked_securex_policy_id = str(ranked_row.get("securex_policy_id", "")).strip()
    ranked_anti_cheat_policy_id = str(ranked_row.get("anti_cheat_policy_id", "")).strip()

    if ranked_securex_policy_id != "securex.policy.rank_strict":
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.ranked_policy_drift",
                severity="VIOLATION",
                confidence=0.98,
                file_path="data/registries/server_profile_registry.json",
                evidence=[
                    "Ranked profile references securex_policy_id='{}'.".format(ranked_securex_policy_id or "<empty>"),
                    "Expected securex_policy_id='securex.policy.rank_strict'.",
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=["data/registries/server_profile_registry.json"],
            )
        )
    elif ranked_securex_policy_id not in securex_ids:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.ranked_policy_drift",
                severity="RISK",
                confidence=0.93,
                file_path="data/registries/server_profile_registry.json",
                evidence=["Ranked profile securex policy id is missing from securex policy registry."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=[
                    "data/registries/server_profile_registry.json",
                    "data/registries/securex_policy_registry.json",
                ],
            )
        )

    if ranked_anti_cheat_policy_id != "policy.ac.rank_strict":
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.ranked_policy_drift",
                severity="VIOLATION",
                confidence=0.98,
                file_path="data/registries/server_profile_registry.json",
                evidence=[
                    "Ranked profile references anti_cheat_policy_id='{}'.".format(ranked_anti_cheat_policy_id or "<empty>"),
                    "Expected anti_cheat_policy_id='policy.ac.rank_strict'.",
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=["data/registries/server_profile_registry.json"],
            )
        )
    elif ranked_anti_cheat_policy_id not in anti_cheat_ids:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.ranked_policy_drift",
                severity="RISK",
                confidence=0.93,
                file_path="data/registries/server_profile_registry.json",
                evidence=["Ranked profile anti-cheat policy id is missing from anti-cheat policy registry."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=[
                    "data/registries/server_profile_registry.json",
                    "data/registries/anti_cheat_policy_registry.json",
                ],
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

