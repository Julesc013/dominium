"""Deterministic UX-0 teleport and query controls over lawful process plans."""

from __future__ import annotations

import re
from typing import Iterable, Mapping

from src.geo.worldgen import build_worldgen_request_for_query
from src.worldgen.mw.sol_anchor import resolve_sol_anchor_cell_key, sol_anchor_object_ids
from src.worldgen.mw.system_query_engine import (
    build_system_teleport_plan,
    filter_habitable_candidates,
    list_systems_in_cell,
    query_nearest_system,
)
from tools.mvp.runtime_bundle import (
    MVP_PACK_LOCK_REL,
    MVP_PROFILE_BUNDLE_REL,
    build_default_universe_identity,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


COORDS_RE = re.compile(
    r"^(?:(?P<frame>[A-Za-z0-9_.-]+)\s*:)?\s*(?P<x>-?\d+)\s*,\s*(?P<y>-?\d+)\s*,\s*(?P<z>-?\d+)\s*$"
)
RNG_UI_TELEPORT_RANDOM_STAR = "rng.ui.teleport.random_star"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_strings(values: Iterable[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _refusal(message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _identity_payload(
    *,
    repo_root: str,
    universe_seed: str,
    authority_mode: str,
    profile_bundle_path: str,
    pack_lock_path: str,
) -> dict:
    return build_default_universe_identity(
        repo_root=str(repo_root),
        seed=str(universe_seed),
        authority_mode=str(authority_mode),
        profile_bundle_payload=None,
        pack_lock_payload=None,
    )


def _sol_slot_ids(
    *,
    repo_root: str,
    universe_seed: str,
    authority_mode: str,
    profile_bundle_path: str,
    pack_lock_path: str,
) -> tuple[dict, dict]:
    identity = _identity_payload(
        repo_root=repo_root,
        universe_seed=universe_seed,
        authority_mode=authority_mode,
        profile_bundle_path=profile_bundle_path,
        pack_lock_path=pack_lock_path,
    )
    slot_ids = sol_anchor_object_ids(universe_identity_hash=str(identity.get("identity_hash", "")).strip())
    return identity, slot_ids


def _sol_process_sequence(*, object_id: str, refinement_level: int, extensions: Mapping[str, object] | None = None) -> list[dict]:
    worldgen_request = build_worldgen_request_for_query(
        geo_cell_key=resolve_sol_anchor_cell_key(),
        refinement_level=int(max(0, refinement_level)),
        extensions={
            "source": "ux0.teleport.sol_anchor",
            "target_object_id": str(object_id or "").strip(),
            **_as_map(extensions),
        },
    )
    return [
        {
            "process_id": "process.worldgen_request",
            "inputs": {"worldgen_request": dict(worldgen_request)},
        },
        {
            "process_id": "process.camera_teleport",
            "inputs": {
                "target_object_id": str(object_id or "").strip(),
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            },
        },
    ]


def _coords_process_sequence(frame_id: str, position_mm: Mapping[str, object]) -> list[dict]:
    return [
        {
            "process_id": "process.camera_teleport",
            "inputs": {
                "target_frame_id": str(frame_id or "").strip() or "frame.world",
                "position_mm": {
                    "x": int(_as_int(_as_map(position_mm).get("x", 0), 0)),
                    "y": int(_as_int(_as_map(position_mm).get("y", 0), 0)),
                    "z": int(_as_int(_as_map(position_mm).get("z", 0), 0)),
                },
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            },
        }
    ]


def _match_coords(command: str) -> dict:
    match = COORDS_RE.fullmatch(str(command or "").strip())
    if not match:
        return {}
    return {
        "frame_id": str(match.group("frame") or "frame.world").strip() or "frame.world",
        "position_mm": {
            "x": int(match.group("x")),
            "y": int(match.group("y")),
            "z": int(match.group("z")),
        },
    }


def _normalized_system_rows(rows: object) -> list[dict]:
    out = []
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        payload = {
            "object_id": str(dict(row).get("object_id", "")).strip(),
            "cell_key": _as_map(dict(row).get("cell_key")),
            "galaxy_position_ref": _as_map(dict(row).get("galaxy_position_ref")),
            "local_index": int(max(0, _as_int(dict(row).get("local_index", 0), 0))),
            "system_seed_value": str(dict(row).get("system_seed_value", "")).strip(),
            "habitable_filter_bias_permille": int(max(0, _as_int(dict(row).get("habitable_filter_bias_permille", 0), 0))),
            "deterministic_fingerprint": "",
        }
        if not payload["object_id"]:
            continue
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out.append(payload)
    return sorted(out, key=lambda item: (str(item.get("object_id", "")), int(item.get("local_index", 0))))


def _random_star_row(*, universe_seed: str, teleport_counter: int, candidate_system_rows: object) -> dict:
    rows = _normalized_system_rows(candidate_system_rows)
    if not rows:
        return {}
    selection_seed = {
        "rng_stream_id": RNG_UI_TELEPORT_RANDOM_STAR,
        "universe_seed": str(universe_seed),
        "teleport_counter": int(max(0, int(teleport_counter))),
        "candidate_ids": [str(row.get("object_id", "")) for row in rows],
    }
    selection_hash = canonical_sha256(selection_seed)
    selection_index = int(selection_hash[:8], 16) % int(len(rows))
    row = dict(rows[selection_index])
    row["selection_hash"] = selection_hash
    row["selection_index"] = int(selection_index)
    return row


def build_teleport_plan(
    *,
    repo_root: str,
    command: str,
    universe_seed: str,
    authority_mode: str = "dev",
    profile_bundle_path: str = MVP_PROFILE_BUNDLE_REL,
    pack_lock_path: str = MVP_PACK_LOCK_REL,
    teleport_counter: int = 0,
    candidate_system_rows: object = None,
) -> dict:
    """Return a deterministic process-only teleport plan. No UI, renderer, or tool may write truth directly."""

    token = str(command or "").strip()
    if not token:
        return _refusal("teleport command is empty", {"command": token})

    identity, slot_ids = _sol_slot_ids(
        repo_root=repo_root,
        universe_seed=universe_seed,
        authority_mode=authority_mode,
        profile_bundle_path=profile_bundle_path,
        pack_lock_path=pack_lock_path,
    )

    if token in ("/tp sol", "sol"):
        target_object_id = str(slot_ids.get("sol.system", "")).strip()
        if not target_object_id:
            return _refusal("Sol system object id is unavailable", {"command": token})
        process_sequence = _sol_process_sequence(
            object_id=target_object_id,
            refinement_level=2,
            extensions={"teleport_alias": "sol"},
        )
        payload = {
            "result": "complete",
            "command": token,
            "target_kind": "sol_anchor",
            "target_object_id": target_object_id,
            "process_sequence": process_sequence,
            "universe_identity": identity,
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    if token in ("/tp earth", "earth"):
        target_object_id = str(slot_ids.get("sol.planet.earth", "")).strip()
        if not target_object_id:
            return _refusal("Earth object id is unavailable", {"command": token})
        process_sequence = _sol_process_sequence(
            object_id=target_object_id,
            refinement_level=2,
            extensions={"teleport_alias": "earth"},
        )
        payload = {
            "result": "complete",
            "command": token,
            "target_kind": "sol_earth",
            "target_object_id": target_object_id,
            "process_sequence": process_sequence,
            "universe_identity": identity,
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    if token in ("/tp random_star", "random_star"):
        selected = _random_star_row(
            universe_seed=str(universe_seed),
            teleport_counter=int(max(0, int(teleport_counter))),
            candidate_system_rows=candidate_system_rows,
        )
        if not selected:
            return _refusal("random_star requires candidate_system_rows", {"command": token})
        plan = build_system_teleport_plan(selected)
        if str(plan.get("result", "")) != "complete":
            return dict(plan)
        payload = {
            "result": "complete",
            "command": token,
            "target_kind": "random_star",
            "target_object_id": str(plan.get("target_object_id", "")).strip(),
            "rng_stream_id": RNG_UI_TELEPORT_RANDOM_STAR,
            "selection_hash": str(selected.get("selection_hash", "")).strip(),
            "selection_index": int(selected.get("selection_index", 0)),
            "process_sequence": [
                {
                    "process_id": "process.worldgen_request",
                    "inputs": {"worldgen_request": dict(plan.get("worldgen_request") or {})},
                },
                {
                    "process_id": "process.camera_teleport",
                    "inputs": dict(plan.get("camera_teleport_inputs") or {}),
                },
            ],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    if token.startswith("/tp "):
        target = token[4:].strip()
        coords = _match_coords(target)
        if coords:
            payload = {
                "result": "complete",
                "command": token,
                "target_kind": "coords",
                "target_object_id": "",
                "process_sequence": _coords_process_sequence(
                    frame_id=str(coords.get("frame_id", "")).strip(),
                    position_mm=_as_map(coords.get("position_mm")),
                ),
                "deterministic_fingerprint": "",
            }
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
            return payload
        target_object_id = str(target).strip()
        if target_object_id:
            payload = {
                "result": "complete",
                "command": token,
                "target_kind": "object_id",
                "target_object_id": target_object_id,
                "process_sequence": [
                    {
                        "process_id": "process.camera_teleport",
                        "inputs": {
                            "target_object_id": target_object_id,
                            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                        },
                    }
                ],
                "deterministic_fingerprint": "",
            }
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
            return payload

    coords = _match_coords(token)
    if coords:
        payload = {
            "result": "complete",
            "command": token,
            "target_kind": "coords",
            "target_object_id": "",
            "process_sequence": _coords_process_sequence(
                frame_id=str(coords.get("frame_id", "")).strip(),
                position_mm=_as_map(coords.get("position_mm")),
            ),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    return _refusal("unsupported teleport command", {"command": token})


def query_nearest_system_plan(
    *,
    repo_root: str,
    universe_seed: str,
    position_ref: Mapping[str, object] | None,
    radius_mm: int,
    authority_mode: str = "dev",
) -> dict:
    identity = _identity_payload(
        repo_root=repo_root,
        universe_seed=universe_seed,
        authority_mode=authority_mode,
        profile_bundle_path=MVP_PROFILE_BUNDLE_REL,
        pack_lock_path=MVP_PACK_LOCK_REL,
    )
    return query_nearest_system(
        universe_identity=identity,
        position_ref=position_ref,
        radius=int(max(0, _as_int(radius_mm, 0))),
    )


def list_systems_for_cell_plan(
    *,
    repo_root: str,
    universe_seed: str,
    geo_cell_key: Mapping[str, object] | None,
    refinement_level: int = 1,
    authority_mode: str = "dev",
) -> dict:
    identity = _identity_payload(
        repo_root=repo_root,
        universe_seed=universe_seed,
        authority_mode=authority_mode,
        profile_bundle_path=MVP_PROFILE_BUNDLE_REL,
        pack_lock_path=MVP_PACK_LOCK_REL,
    )
    return list_systems_in_cell(
        universe_identity=identity,
        geo_cell_key=geo_cell_key,
        refinement_level=int(max(0, _as_int(refinement_level, 1))),
    )


def filter_habitable_systems_plan(
    *,
    system_rows: object,
    criteria_stub: Mapping[str, object] | None = None,
    repo_root: str = ".",
    universe_seed: str = "0",
    authority_mode: str = "dev",
) -> dict:
    identity = _identity_payload(
        repo_root=repo_root,
        universe_seed=universe_seed,
        authority_mode=authority_mode,
        profile_bundle_path=MVP_PROFILE_BUNDLE_REL,
        pack_lock_path=MVP_PACK_LOCK_REL,
    )
    return filter_habitable_candidates(
        system_rows=system_rows,
        criteria_stub=criteria_stub,
        universe_identity=identity,
    )


__all__ = [
    "RNG_UI_TELEPORT_RANDOM_STAR",
    "build_teleport_plan",
    "filter_habitable_systems_plan",
    "list_systems_for_cell_plan",
    "query_nearest_system_plan",
]
