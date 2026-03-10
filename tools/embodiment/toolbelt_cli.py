#!/usr/bin/env python3
"""EMB-1 toolbelt command stubs for CLI/TUI/client parity."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.embodiment import (  # noqa: E402
    build_cut_trench_task,
    build_fill_at_cursor_task,
    build_logic_probe_task,
    build_logic_trace_task,
    build_mine_at_cursor_task,
    build_scan_result,
    build_teleport_tool_surface,
)
from tools.embodiment.emb1_probe import _authority_context, _field_values, _inspection_snapshot, _property_origin_result, _selection  # noqa: E402


def _emit(payload: dict) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(payload.get("result", "")).strip() == "complete" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="EMB-1 toolbelt command stubs.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("mine")
    sub.add_parser("fill")
    sub.add_parser("cut")
    sub.add_parser("scan")
    sub.add_parser("probe")
    sub.add_parser("trace")
    sub.add_parser("tp")
    args = parser.parse_args()

    authority_context = _authority_context()
    selection = _selection()

    if args.command == "mine":
        return _emit(build_mine_at_cursor_task(authority_context=authority_context, subject_id="subject.player", selection=selection, volume_amount=1))
    if args.command == "fill":
        return _emit(
            build_fill_at_cursor_task(
                authority_context=authority_context,
                subject_id="subject.player",
                selection=selection,
                volume_amount=1,
                material_id="material.soil_fill",
            )
        )
    if args.command == "cut":
        return _emit(
            build_cut_trench_task(
                authority_context=authority_context,
                subject_id="subject.player",
                path_stub=[selection["geo_cell_key"]],
                volume_amount=1,
                selection=selection,
            )
        )
    if args.command == "scan":
        return _emit(
            build_scan_result(
                authority_context=authority_context,
                selection=selection,
                inspection_snapshot=_inspection_snapshot(),
                field_values=_field_values(),
                property_origin_result=_property_origin_result(),
                has_physical_access=True,
            )
        )
    if args.command == "probe":
        return _emit(
            build_logic_probe_task(
                authority_context=authority_context,
                subject_id="net.logic.sample",
                measurement_point_id="measure.logic.signal",
                network_id="net.logic.sample",
                element_id="inst.logic.and.1",
                port_id="out.q",
            )
        )
    if args.command == "trace":
        return _emit(
            build_logic_trace_task(
                authority_context=authority_context,
                subject_id="net.logic.sample",
                measurement_point_ids=["measure.logic.signal"],
                targets=[
                    {
                        "subject_id": "net.logic.sample",
                        "network_id": "net.logic.sample",
                        "element_id": "inst.logic.and.1",
                        "port_id": "out.q",
                        "measurement_point_id": "measure.logic.signal",
                    }
                ],
                current_tick=7,
                duration_ticks=8,
            )
        )
    return _emit(
        build_teleport_tool_surface(
            repo_root=REPO_ROOT_HINT,
            authority_context=authority_context,
            command="/tp earth",
            universe_seed="0",
            authority_mode="dev",
            profile_bundle_path=os.path.join("profiles", "bundles", "bundle.mvp_default.json"),
            pack_lock_path=os.path.join("locks", "pack_lock.mvp_default.json"),
            teleport_counter=1,
            surface_target_cell_key=selection["geo_cell_key"],
            current_tick=7,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
