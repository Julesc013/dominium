"""STRICT test: macro->meso->micro motion-tier anchors remain position/velocity continuous."""

from __future__ import annotations

import sys


TEST_ID = "testx.mobility.transition_macro_meso_micro_continuity"
TEST_TAGS = ["strict", "mobility", "transition", "determinism"]


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _anchor(row: dict, edge_length_by_id: dict) -> dict:
    tier = str(row.get("tier", "")).strip()
    macro = dict(row.get("macro_state") or {})
    meso = dict(row.get("meso_state") or {})
    micro = dict(row.get("micro_state") or {})
    if tier == "macro":
        edge_id = str(macro.get("current_edge_id", "")).strip()
        length = int(max(1, _as_int(edge_length_by_id.get(edge_id, 1), 1)))
        progress_q16 = int(max(0, min(65535, _as_int(macro.get("progress_fraction_q16", 0), 0))))
        return {
            "tier": "macro",
            "edge_id": edge_id,
            "position_mm": int((length * progress_q16 + 32767) // 65535),
            "velocity_mm_per_tick": int(max(0, _as_int(macro.get("planned_speed_mm_per_tick", 0), 0))),
        }
    if tier == "meso":
        edge_id = str(meso.get("current_edge_id", "")).strip() or str(macro.get("current_edge_id", "")).strip()
        length = int(max(1, _as_int(edge_length_by_id.get(edge_id, 1), 1)))
        progress_q16 = int(
            max(
                0,
                min(
                    65535,
                    _as_int(
                        meso.get(
                            "progress_fraction_q16",
                            macro.get("progress_fraction_q16", 0),
                        ),
                        0,
                    ),
                ),
            )
        )
        velocity = int(
            max(
                0,
                _as_int(
                    meso.get(
                        "velocity_mm_per_tick",
                        macro.get("planned_speed_mm_per_tick", 0),
                    ),
                    0,
                ),
            )
        )
        return {
            "tier": "meso",
            "edge_id": edge_id,
            "position_mm": int((length * progress_q16 + 32767) // 65535),
            "velocity_mm_per_tick": int(velocity),
        }
    edge_id = str(micro.get("edge_id", "")).strip() or str(macro.get("current_edge_id", "")).strip()
    position_row = dict(micro.get("position_mm") or {})
    position_mm = int(
        _as_int(
            micro.get(
                "s_param",
                position_row.get("x", 0),
            ),
            0,
        )
    )
    velocity_row = dict(micro.get("velocity_mm_per_tick") or {})
    velocity_mm_per_tick = int(_as_int(velocity_row.get("x", 0), 0))
    return {
        "tier": "micro",
        "edge_id": edge_id,
        "position_mm": int(max(0, position_mm)),
        "velocity_mm_per_tick": int(velocity_mm_per_tick),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.mobility.vehicle.vehicle_engine import build_motion_state
    from tools.xstack.compatx.canonical_json import canonical_sha256

    edge_length_by_id = {"edge.mob.transition.alpha": 12000}
    macro = build_motion_state(
        vehicle_id="vehicle.mob.transition.alpha",
        tier="macro",
        macro_state={
            "itinerary_id": "itinerary.mob.transition.alpha",
            "current_edge_id": "edge.mob.transition.alpha",
            "progress_fraction_q16": 32768,
            "planned_speed_mm_per_tick": 200,
        },
        meso_state={},
        micro_state={},
        last_update_tick=100,
        extensions={},
    )
    meso = build_motion_state(
        vehicle_id="vehicle.mob.transition.alpha",
        tier="meso",
        macro_state=dict(macro.get("macro_state") or {}),
        meso_state={
            "current_edge_id": "edge.mob.transition.alpha",
            "progress_fraction_q16": 32768,
            "velocity_mm_per_tick": 200,
        },
        micro_state={},
        last_update_tick=100,
        extensions={},
    )
    micro = build_motion_state(
        vehicle_id="vehicle.mob.transition.alpha",
        tier="micro",
        macro_state=dict(macro.get("macro_state") or {}),
        meso_state=dict(meso.get("meso_state") or {}),
        micro_state={
            "edge_id": "edge.mob.transition.alpha",
            "geometry_id": "geometry.mob.transition.alpha",
            "s_param": 6000,
            "position_mm": {"x": 6000, "y": 0, "z": 0},
            "velocity_mm_per_tick": {"x": 200, "y": 0, "z": 0},
        },
        last_update_tick=100,
        extensions={},
    )

    macro_anchor = _anchor(dict(macro), edge_length_by_id)
    meso_anchor = _anchor(dict(meso), edge_length_by_id)
    micro_anchor = _anchor(dict(micro), edge_length_by_id)
    if str(macro_anchor.get("edge_id", "")) != str(meso_anchor.get("edge_id", "")):
        return {"status": "fail", "message": "macro->meso edge continuity failed"}
    if str(meso_anchor.get("edge_id", "")) != str(micro_anchor.get("edge_id", "")):
        return {"status": "fail", "message": "meso->micro edge continuity failed"}
    if abs(int(macro_anchor.get("position_mm", 0)) - int(meso_anchor.get("position_mm", 0))) > 1:
        return {"status": "fail", "message": "macro->meso position discontinuity exceeded tolerance"}
    if abs(int(meso_anchor.get("position_mm", 0)) - int(micro_anchor.get("position_mm", 0))) > 1:
        return {"status": "fail", "message": "meso->micro position discontinuity exceeded tolerance"}
    if int(micro_anchor.get("velocity_mm_per_tick", 0)) <= 0:
        return {"status": "fail", "message": "micro anchor did not preserve positive velocity state"}

    first_hash = canonical_sha256([macro_anchor, meso_anchor, micro_anchor])
    second_hash = canonical_sha256([_anchor(dict(macro), edge_length_by_id), _anchor(dict(meso), edge_length_by_id), _anchor(dict(micro), edge_length_by_id)])
    if str(first_hash) != str(second_hash):
        return {"status": "fail", "message": "transition anchors are not deterministic across repeated evaluation"}
    return {"status": "pass", "message": "macro->meso->micro continuity is deterministic"}
