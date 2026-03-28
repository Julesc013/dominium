"""Deterministic EMB-1 teleport tool wrappers over MW-4 teleport planning."""

from __future__ import annotations

from typing import Mapping

from worldgen.refinement.refinement_scheduler import build_refinement_request_record
from client.ui.teleport_controller import build_teleport_plan
from tools.xstack.compatx.canonical_json import canonical_sha256

from .toolbelt_engine import evaluate_tool_access


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def build_teleport_tool_surface(
    *,
    repo_root: str,
    authority_context: Mapping[str, object] | None,
    command: str,
    universe_seed: str,
    authority_mode: str = "dev",
    profile_bundle_path: str,
    pack_lock_path: str,
    teleport_counter: int = 0,
    candidate_system_rows: object = None,
    surface_target_cell_key: Mapping[str, object] | None = None,
    current_tick: int = 0,
) -> dict:
    access_result = evaluate_tool_access(tool_id="tool.teleport", authority_context=authority_context, has_physical_access=False)
    if str(access_result.get("result", "")).strip() != "complete":
        return dict(access_result)
    teleport_plan = build_teleport_plan(
        repo_root=str(repo_root),
        command=str(command or "").strip(),
        universe_seed=str(universe_seed or "").strip(),
        authority_mode=str(authority_mode or "").strip() or "dev",
        profile_bundle_path=str(profile_bundle_path or "").strip(),
        pack_lock_path=str(pack_lock_path or "").strip(),
        teleport_counter=int(max(0, _as_int(teleport_counter, 0))),
        candidate_system_rows=candidate_system_rows,
    )
    if str(teleport_plan.get("result", "")).strip() != "complete":
        return dict(teleport_plan)
    process_sequence = [dict(row) for row in list(teleport_plan.get("process_sequence") or []) if isinstance(row, Mapping)]
    if str(teleport_plan.get("target_kind", "")).strip() == "sol_earth" and _as_map(surface_target_cell_key):
        try:
            request_row = build_refinement_request_record(
                request_id="refinement.request.{}".format(
                    canonical_sha256(
                        {
                            "command": str(command or "").strip(),
                            "surface_target_cell_key": dict(_as_map(surface_target_cell_key)),
                            "refinement_level": 3,
                        }
                    )[:16]
                ),
                request_kind="teleport",
                geo_cell_key=_as_map(surface_target_cell_key),
                refinement_level=3,
                priority_class="priority.teleport.destination",
                tick=int(max(0, _as_int(current_tick, 0))),
                extensions={"source": "EMB1-6", "post_move_surface_refine": True},
            )
        except ValueError:
            request_row = {}
        if request_row:
            process_sequence.append(
                {
                    "process_id": "process.refinement_request_enqueue",
                    "inputs": {"refinement_request_record": dict(request_row)},
                }
            )
    payload = {
        "result": "complete",
        "tool_id": "tool.teleport",
        "teleport_plan": dict(teleport_plan),
        "process_sequence": [dict(row) for row in process_sequence],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = ["build_teleport_tool_surface"]
