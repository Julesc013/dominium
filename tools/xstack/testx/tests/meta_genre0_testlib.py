"""Shared META-GENRE-0 TestX helpers."""

from __future__ import annotations

import json
import os
from typing import Iterable


MATRIX_REL = "data/meta/player_demand_matrix.json"


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError) as exc:
        return {}, str(exc)


def load_matrix(repo_root: str):
    return _load_json(repo_root, MATRIX_REL)


def matrix_demands(payload: dict) -> list[dict]:
    rows = list((payload if isinstance(payload, dict) else {}).get("demands") or [])
    return [dict(row) for row in rows if isinstance(row, dict)]


def _ids(rows: Iterable[dict], key: str) -> set[str]:
    out = set()
    for row in rows:
        token = str(dict(row).get(key, "")).strip()
        if token:
            out.add(token)
    return out


def known_reference_ids(repo_root: str) -> dict[str, set[str]]:
    action_family_payload, _ = _load_json(repo_root, "data/registries/action_family_registry.json")
    action_template_payload, _ = _load_json(repo_root, "data/registries/action_template_registry.json")
    explain_payload, _ = _load_json(repo_root, "data/registries/explain_contract_registry.json")
    law_payload, _ = _load_json(repo_root, "data/registries/law_profiles.json")
    phys_payload, _ = _load_json(repo_root, "data/registries/physics_profile_registry.json")
    rwam_payload, _ = _load_json(repo_root, "data/meta/real_world_affordance_matrix.json")

    family_rows = list((dict(action_family_payload.get("record") or {})).get("families") or [])
    template_rows = list((dict(action_template_payload.get("record") or {})).get("templates") or [])
    explain_rows = list((dict(explain_payload.get("record") or {})).get("explain_contracts") or [])
    law_rows = list((dict(law_payload.get("record") or {})).get("profiles") or [])
    phys_rows = list((dict(phys_payload.get("record") or {})).get("physics_profiles") or [])
    rwam_rows = list((rwam_payload if isinstance(rwam_payload, dict) else {}).get("affordances") or [])

    return {
        "action_families": _ids(family_rows, "action_family_id"),
        "action_templates": _ids(template_rows, "action_template_id"),
        "explain_contracts": _ids(explain_rows, "contract_id"),
        "law_profiles": _ids(law_rows, "law_profile_id"),
        "physics_profiles": _ids(phys_rows, "physics_profile_id"),
        "rwam_affordances": _ids(rwam_rows, "id"),
    }
