"""Deterministic SOL-2 orbit-view fixtures shared by replay tools and TestX."""

from __future__ import annotations

import sys
from functools import lru_cache
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


FIXTURE_TICK = 123
SYSTEM_FOCUS_SLOT_ID = "sol.star"
EARTH_FOCUS_SLOT_ID = "sol.planet.earth"
LUNA_FOCUS_SLOT_ID = "sol.moon.luna"


def _ensure_repo_root(repo_root: str) -> str:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    return repo_root


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _generated_rows(result: Mapping[str, object], key: str) -> list[dict]:
    payload = _as_map(result)
    direct = payload.get(key)
    if isinstance(direct, list):
        return [dict(row) for row in direct if isinstance(row, Mapping)]
    ext = _as_map(payload.get("extensions"))
    rows = ext.get(key)
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


@lru_cache(maxsize=4)
def orbit_fixture(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.xstack.testx.tests.sol0_testlib import build_sol_overlay_fixture

    return build_sol_overlay_fixture(normalized, refinement_level=2)


def _focus_object_id(fixture: Mapping[str, object], slot_id: str) -> str:
    slot_object_ids = dict(_as_map(_as_map(fixture).get("patch_document")).get("slot_object_ids") or {})
    return str(slot_object_ids.get(str(slot_id), "")).strip()


def _viewer_ref():
    from geo import build_position_ref

    return build_position_ref(
        object_id="object.viewer.sol2.fixture",
        frame_id="frame.sol2.fixture",
        local_position=[0, 0, 0],
        extensions={"source": "SOL2-7", "derived_only": True},
    )


def build_orbit_surface(
    repo_root: str,
    *,
    focus_slot_id: str,
    current_tick: int = FIXTURE_TICK,
) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from astro.views.orbit_view_engine import build_orbit_view_surface

    fixture = orbit_fixture(normalized)
    worldgen_result = _as_map(fixture.get("worldgen_result"))
    return build_orbit_view_surface(
        current_tick=int(current_tick),
        viewer_ref=_viewer_ref(),
        focus_object_id=_focus_object_id(fixture, focus_slot_id),
        effective_object_views=_as_map(fixture.get("merge_result")).get("effective_object_views"),
        star_artifact_rows=_generated_rows(worldgen_result, "generated_star_artifact_rows"),
        planet_orbit_artifact_rows=_generated_rows(worldgen_result, "generated_planet_orbit_artifact_rows"),
        planet_basic_artifact_rows=_generated_rows(worldgen_result, "generated_planet_basic_artifact_rows"),
        provider_declarations=_as_map(fixture.get("pack_lock")).get("provides_declarations") or [],
        explicit_provider_resolutions=_as_map(fixture.get("pack_lock")).get("provides_resolutions") or [],
        ui_mode="gui",
    )


def _artifact(surface: Mapping[str, object]) -> dict:
    return _as_map(_as_map(surface).get("orbit_view_artifact"))


def _body_positions_by_slot(surface: Mapping[str, object], fixture: Mapping[str, object]) -> dict:
    slot_object_ids = dict(_as_map(_as_map(fixture).get("patch_document")).get("slot_object_ids") or {})
    object_to_slot = dict((str(object_id), str(slot_id)) for slot_id, object_id in sorted(slot_object_ids.items()))
    rows = {}
    for body_row in _as_list(_artifact(surface).get("bodies")):
        if not isinstance(body_row, Mapping):
            continue
        object_id = str(dict(body_row).get("object_id", "")).strip()
        slot_id = object_to_slot.get(object_id, object_id)
        current_position_ref = _as_map(_as_map(body_row).get("current_position_ref"))
        rows[slot_id] = list(current_position_ref.get("local_position") or [])
    return dict((key, list(rows[key])) for key in sorted(rows.keys()))


def _sample_counts_by_slot(surface: Mapping[str, object], fixture: Mapping[str, object]) -> dict:
    slot_object_ids = dict(_as_map(_as_map(fixture).get("patch_document")).get("slot_object_ids") or {})
    object_to_slot = dict((str(object_id), str(slot_id)) for slot_id, object_id in sorted(slot_object_ids.items()))
    rows = {}
    for path_row in _as_list(_artifact(surface).get("sampled_paths")):
        if not isinstance(path_row, Mapping):
            continue
        object_id = str(dict(path_row).get("object_id", "")).strip()
        slot_id = object_to_slot.get(object_id, object_id)
        rows[slot_id] = int(len(_as_list(_as_map(path_row).get("sampled_points"))))
    return dict((key, int(rows[key])) for key in sorted(rows.keys()))


def orbit_replay_report(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from astro.ephemeris.kepler_proxy_engine import DEFAULT_ORBIT_PATH_POLICY_ID, orbit_path_policy_rows
    from astro.views.orbit_view_engine import orbit_view_artifact_hash

    fixture = orbit_fixture(normalized)
    system_surface_first = build_orbit_surface(normalized, focus_slot_id=SYSTEM_FOCUS_SLOT_ID)
    system_surface_second = build_orbit_surface(normalized, focus_slot_id=SYSTEM_FOCUS_SLOT_ID)
    earth_surface_first = build_orbit_surface(normalized, focus_slot_id=EARTH_FOCUS_SLOT_ID)
    earth_surface_second = build_orbit_surface(normalized, focus_slot_id=EARTH_FOCUS_SLOT_ID)

    system_artifact_first = _artifact(system_surface_first)
    system_artifact_second = _artifact(system_surface_second)
    earth_artifact_first = _artifact(earth_surface_first)
    earth_artifact_second = _artifact(earth_surface_second)

    policy_row = dict(orbit_path_policy_rows().get(DEFAULT_ORBIT_PATH_POLICY_ID) or {})
    expected_samples = int(policy_row.get("samples_per_orbit", 128) or 128)
    expected_max_paths = int(policy_row.get("max_paths_per_view", 16) or 16)
    system_sample_counts = _sample_counts_by_slot(system_surface_first, fixture)
    earth_sample_counts = _sample_counts_by_slot(earth_surface_first, fixture)
    stable = (
        dict(system_artifact_first) == dict(system_artifact_second)
        and dict(earth_artifact_first) == dict(earth_artifact_second)
    )
    violations = []
    earth_positions = _body_positions_by_slot(earth_surface_first, fixture)
    if earth_positions.get(EARTH_FOCUS_SLOT_ID) != [0, 0, 0]:
        violations.append("earth local chart did not keep the focused planet at the origin")
    if any(int(count) != int(expected_samples) for count in list(system_sample_counts.values()) + list(earth_sample_counts.values())):
        violations.append("orbit sample counts drifted from the policy")
    if len(_as_list(earth_artifact_first.get("sampled_paths"))) > expected_max_paths:
        violations.append("earth-local orbit path count exceeded the policy bound")
    if len(_as_list(system_artifact_first.get("sampled_paths"))) > expected_max_paths:
        violations.append("system orbit path count exceeded the policy bound")
    if not stable:
        violations.append("orbit replay drifted across repeated runs")

    report = {
        "result": "complete" if not violations else "violation",
        "current_tick": int(FIXTURE_TICK),
        "stable_across_repeated_runs": bool(stable),
        "provider_ids": sorted(
            {
                str(_as_map(system_artifact_first.get("extensions")).get("provider_id", "")).strip(),
                str(_as_map(earth_artifact_first.get("extensions")).get("provider_id", "")).strip(),
            }
            - {""}
        ),
        "orbit_path_policy_id": str(_as_map(earth_artifact_first.get("extensions")).get("orbit_path_policy_id", "")).strip()
        or DEFAULT_ORBIT_PATH_POLICY_ID,
        "expected_samples_per_orbit": int(expected_samples),
        "expected_max_paths_per_view": int(expected_max_paths),
        "system_chart_mode": str(_as_map(system_artifact_first.get("extensions")).get("chart_mode", "")).strip(),
        "earth_chart_mode": str(_as_map(earth_artifact_first.get("extensions")).get("chart_mode", "")).strip(),
        "system_artifact_hash": orbit_view_artifact_hash(system_artifact_first),
        "earth_local_artifact_hash": orbit_view_artifact_hash(earth_artifact_first),
        "system_artifact_fingerprint": str(system_artifact_first.get("deterministic_fingerprint", "")).strip(),
        "earth_local_artifact_fingerprint": str(earth_artifact_first.get("deterministic_fingerprint", "")).strip(),
        "combined_hash": canonical_sha256(
            {
                "system_artifact_hash": orbit_view_artifact_hash(system_artifact_first),
                "earth_local_artifact_hash": orbit_view_artifact_hash(earth_artifact_first),
            }
        ),
        "positions": {
            "system": _body_positions_by_slot(system_surface_first, fixture),
            "earth_local": earth_positions,
        },
        "sample_counts": {
            "system": system_sample_counts,
            "earth_local": earth_sample_counts,
        },
        "path_counts": {
            "system": int(len(_as_list(system_artifact_first.get("sampled_paths")))),
            "earth_local": int(len(_as_list(earth_artifact_first.get("sampled_paths")))),
        },
        "body_counts": {
            "system": int(len(_as_list(system_artifact_first.get("bodies")))),
            "earth_local": int(len(_as_list(earth_artifact_first.get("bodies")))),
        },
        "position_hash": "",
        "sampling_hash": "",
        "violations": list(violations),
        "deterministic_fingerprint": "",
    }
    report["position_hash"] = canonical_sha256(report["positions"])
    report["sampling_hash"] = canonical_sha256(
        {
            "sample_counts": report["sample_counts"],
            "path_counts": report["path_counts"],
            "body_counts": report["body_counts"],
        }
    )
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


__all__ = [
    "EARTH_FOCUS_SLOT_ID",
    "FIXTURE_TICK",
    "LUNA_FOCUS_SLOT_ID",
    "SYSTEM_FOCUS_SLOT_ID",
    "build_orbit_surface",
    "orbit_fixture",
    "orbit_replay_report",
]
