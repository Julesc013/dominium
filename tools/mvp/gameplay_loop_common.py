"""Deterministic Omega gameplay loop harness built on the frozen baseline universe."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402
install_src_aliases(REPO_ROOT_HINT)

from embodiment.tools.scanner_tool import build_scan_result  # noqa: E402
from embodiment.tools.teleport_tool import build_teleport_tool_surface  # noqa: E402
from embodiment.tools.terrain_edit_tool import build_mine_at_cursor_task  # noqa: E402
from tools.mvp.baseline_universe_common import (  # noqa: E402
    ANCHOR_REASON_INTERVAL,
    ANCHOR_REASON_SAVE,
    BASELINE_GEOMETRY_VOLUME,
    BASELINE_INSTANCE_MANIFEST_REL,
    BASELINE_PACK_LOCK_REL,
    BASELINE_PROFILE_BUNDLE_REL,
    BASELINE_SAVE_REL,
    _baseline_context,
    _diff_values,
    _initial_state_payload,
    _proof_anchor_row,
    _run_baseline_terrain_edit,
    _run_worldgen_refinement,
    _saveable_state,
    _working_state,
    generate_baseline_universe,
    load_baseline_universe_snapshot,
    load_versioned_artifact,
    read_worldgen_baseline_seed,
)
from tools.mvp.mvp_smoke_common import run_logic_smoke_suite  # noqa: E402
from tools.mvp.runtime_bundle import build_runtime_bootstrap  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


MVP_GAMEPLAY_SCHEMA_ID = "dominium.schema.governance.mvp_gameplay_loop_snapshot"
MVP_GAMEPLAY_VERIFY_SCHEMA_ID = "dominium.schema.audit.mvp_gameplay_loop_verify"
MVP_GAMEPLAY_VERSION = 0
MVP_GAMEPLAY_STABILITY_CLASS = "stable"
MVP_GAMEPLAY_DIR_REL = os.path.join("data", "baselines", "gameplay")
MVP_GAMEPLAY_SNAPSHOT_REL = os.path.join(MVP_GAMEPLAY_DIR_REL, "gameplay_loop_snapshot.json")
MVP_GAMEPLAY_VERIFY_JSON_REL = os.path.join("data", "audit", "gameplay_verify.json")
MVP_GAMEPLAY_VERIFY_DOC_REL = os.path.join("docs", "audit", "MVP_GAMEPLAY_VERIFY.md")
MVP_GAMEPLAY_RUN_DOC_REL = os.path.join("docs", "audit", "MVP_GAMEPLAY_LOOP_RUN.md")
MVP_GAMEPLAY_BASELINE_DOC_REL = os.path.join("docs", "audit", "MVP_GAMEPLAY_BASELINE.md")
DEFAULT_GAMEPLAY_WORK_ROOT_REL = os.path.join("build", "tmp", "omega3_gameplay")
DEFAULT_GAMEPLAY_REPLAY_ROOT_REL = os.path.join("build", "tmp", "omega3_gameplay_replay")
DEFAULT_TEMP_SAVE_NAME = "gameplay_loop_save_0.save"


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.join(repo_root, str(rel_path or "").replace("/", os.sep)))


def _ensure_dir(path: str) -> None:
    if path and (not os.path.isdir(path)):
        os.makedirs(path, exist_ok=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return path


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or ""))
    return path


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def gameplay_snapshot_record_hash(record: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(record or {}), deterministic_fingerprint=""))


def load_gameplay_snapshot(repo_root: str, snapshot_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    target = os.path.normpath(os.path.abspath(snapshot_path)) if _token(snapshot_path) else _repo_abs(repo_root_abs, MVP_GAMEPLAY_SNAPSHOT_REL)
    return _load_json(target)


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.lab_freecam",
        "entitlements": [
            "session.boot",
            "entitlement.inspect",
            "entitlement.control.admin",
            "entitlement.teleport",
            "entitlement.tool.equip",
            "entitlement.tool.use",
            "entitlement.observer.truth",
            "ent.tool.terrain_edit",
            "ent.tool.scan",
            "ent.tool.logic_probe",
            "ent.tool.logic_trace",
            "ent.tool.teleport",
        ],
        "privilege_level": "operator",
        "epistemic_scope": {"scope_id": "epistemic.admin_full", "visibility_level": "nondiegetic"},
    }


def _relative_path(repo_root: str, path: str) -> str:
    token = _token(path)
    if not token:
        return ""
    abs_path = os.path.normpath(os.path.abspath(token))
    try:
        rel = os.path.relpath(abs_path, repo_root)
    except ValueError:
        return _norm(abs_path)
    return _norm(rel)


def _default_paths(repo_root: str, *, output_root_rel: str = "", write_outputs: bool = True) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    snapshot_root_rel = _norm(output_root_rel) if _token(output_root_rel) else (_norm(MVP_GAMEPLAY_DIR_REL) if write_outputs else _norm(DEFAULT_GAMEPLAY_WORK_ROOT_REL))
    snapshot_root_abs = _repo_abs(repo_root_abs, snapshot_root_rel)
    work_root_abs = _repo_abs(repo_root_abs, DEFAULT_GAMEPLAY_WORK_ROOT_REL)
    replay_root_abs = _repo_abs(repo_root_abs, DEFAULT_GAMEPLAY_REPLAY_ROOT_REL)
    return {
        "snapshot_root_abs": snapshot_root_abs,
        "snapshot_root_rel": snapshot_root_rel,
        "snapshot_path": os.path.join(snapshot_root_abs, os.path.basename(MVP_GAMEPLAY_SNAPSHOT_REL)),
        "run_doc_path": _repo_abs(repo_root_abs, MVP_GAMEPLAY_RUN_DOC_REL),
        "verify_json_path": _repo_abs(repo_root_abs, MVP_GAMEPLAY_VERIFY_JSON_REL),
        "verify_doc_path": _repo_abs(repo_root_abs, MVP_GAMEPLAY_VERIFY_DOC_REL),
        "baseline_doc_path": _repo_abs(repo_root_abs, MVP_GAMEPLAY_BASELINE_DOC_REL),
        "runtime_save_path": os.path.join(work_root_abs, DEFAULT_TEMP_SAVE_NAME),
        "replay_root_rel": _norm(DEFAULT_GAMEPLAY_REPLAY_ROOT_REL),
        "replay_root_abs": replay_root_abs,
    }


def _load_instance_manifest(repo_root: str, instance_path: str = "") -> tuple[dict, str]:
    target = _repo_abs(repo_root, BASELINE_INSTANCE_MANIFEST_REL) if not _token(instance_path) else os.path.normpath(os.path.abspath(instance_path))
    return _load_json(target), target


def _field_value(field_rows: object, field_type_id: str) -> int:
    expected = str(field_type_id or "").strip()
    for row in list(field_rows or []):
        if not isinstance(row, Mapping):
            continue
        payload = dict(row)
        extension_type = _token(_as_map(payload.get("extensions")).get("field_type_id"))
        if extension_type == expected:
            try:
                return int(payload.get("value", 0) or 0)
            except (TypeError, ValueError):
                return 0
    for row in list(field_rows or []):
        if not isinstance(row, Mapping):
            continue
        payload = dict(row)
        field_id = _token(payload.get("field_id"))
        if field_id == expected or field_id.startswith(expected + "."):
            try:
                return int(payload.get("value", 0) or 0)
            except (TypeError, ValueError):
                return 0
    return 0


def _surface_selection(surface_tile: Mapping[str, object], target_cell_key: Mapping[str, object]) -> dict:
    cell_key = dict(_as_map(target_cell_key))
    return {
        "object_id": _token(_as_map(surface_tile).get("tile_object_id")) or "tile.baseline",
        "position_ref": {"x": 0, "y": 0, "z": 0},
        "geo_cell_key": cell_key,
        "tile_cell_key": cell_key,
        "target_cell_key": cell_key,
    }


def _inspection_snapshot(surface_tile: Mapping[str, object], selection: Mapping[str, object]) -> dict:
    return {
        "target_payload": {
            "target_id": _token(_as_map(selection).get("object_id")),
            "position_ref": dict(_as_map(selection).get("position_ref")),
            "row": {
                "object_kind_id": "kind.surface_tile",
                "surface_tile_artifact": dict(_as_map(surface_tile)),
            },
        }
    }


def _property_origin_result(surface_tile: Mapping[str, object]) -> dict:
    tile = _as_map(surface_tile)
    return {
        "report": {
            "current_layer_id": "base.procedural",
            "prior_value_chain": [
                {
                    "layer_id": "base.procedural",
                    "value": int(_as_map(tile.get("elevation_params_ref")).get("height_proxy", 0) or 0),
                }
            ],
        }
    }


def _compact_anchor_row(row: Mapping[str, object]) -> dict:
    anchor = _as_map(row)
    return {
        "checkpoint_id": _token(anchor.get("checkpoint_id")),
        "anchor_label": _token(anchor.get("anchor_label")),
        "simulation_tick": int(anchor.get("simulation_tick", 0) or 0),
        "state_hash_anchor": _token(anchor.get("state_hash_anchor")),
        "state_deterministic_fingerprint": _token(anchor.get("state_deterministic_fingerprint")),
        "derived_view_hash": _token(anchor.get("derived_view_hash")),
        "epoch_anchor_id": _token(anchor.get("epoch_anchor_id")),
        "epoch_anchor_fingerprint": _token(anchor.get("epoch_anchor_fingerprint")),
    }


def _step_row(
    *,
    step_id: str,
    title: str,
    commands: list[str],
    expected_result: str,
    proof_anchor_hash: str = "",
    derived_view_hash: str = "",
    details: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "step_id": str(step_id),
        "title": str(title),
        "commands": [str(item).strip() for item in list(commands or []) if str(item).strip()],
        "expected_result": str(expected_result or "").strip(),
        "proof_anchor_hash": str(proof_anchor_hash or "").strip(),
        "derived_view_hash": str(derived_view_hash or "").strip(),
        "details": dict(details or {}),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _snapshot_record(result: Mapping[str, object]) -> dict:
    payload = _as_map(result)
    baseline_record = _as_map(payload.get("baseline_record"))
    instance_manifest = _as_map(payload.get("instance_manifest"))
    launch = _as_map(payload.get("launch"))
    teleports = _as_map(payload.get("teleports"))
    inspect_result = _as_map(payload.get("inspect"))
    mine_task = _as_map(payload.get("mine_task"))
    logic = _as_map(payload.get("logic"))
    save_reload = _as_map(payload.get("save_reload"))
    replay = _as_map(payload.get("replay"))
    anchors = [
        _compact_anchor_row(row)
        for row in list(payload.get("proof_anchors") or [])
        if isinstance(row, Mapping)
    ]
    coordinate_command = _token(_as_map(payload.get("coordinate_target")).get("command"))
    target_cell_key = _as_map(payload.get("target_cell_key"))
    record = {
        "gameplay_loop_version": MVP_GAMEPLAY_VERSION,
        "stability_class": MVP_GAMEPLAY_STABILITY_CLASS,
        "baseline_seed": _token(payload.get("seed_text")),
        "baseline_seed_hash": canonical_sha256({"seed_text": _token(payload.get("seed_text"))}),
        "worldgen_lock_id": _token(baseline_record.get("worldgen_lock_id")),
        "worldgen_lock_version": int(baseline_record.get("worldgen_lock_version", 0) or 0),
        "semantic_contract_registry_hash": _token(baseline_record.get("semantic_contract_registry_hash")),
        "universe_contract_bundle_hash": _token(baseline_record.get("universe_contract_bundle_hash")),
        "pack_lock_id": _token(baseline_record.get("pack_lock_id")),
        "pack_lock_hash": _token(baseline_record.get("pack_lock_hash")),
        "profile_bundle_id": _token(baseline_record.get("profile_bundle_id")),
        "profile_bundle_hash": _token(baseline_record.get("profile_bundle_hash")),
        "instance_manifest_rel": _token(payload.get("instance_manifest_rel")),
        "instance_manifest_fingerprint": _token(instance_manifest.get("deterministic_fingerprint")),
        "instance_manifest_identity_fingerprint": _token(_as_map(instance_manifest.get("universal_identity_block")).get("deterministic_fingerprint")),
        "baseline_save_rel": _token(payload.get("baseline_save_rel")),
        "baseline_save_hash": _token(_as_map(baseline_record.get("save_artifact")).get("save_file_hash")),
        "runtime_temp_save_rel": _token(payload.get("runtime_temp_save_rel")),
        "install_profile_id": _token(baseline_record.get("install_profile_id")),
        "requested_mod_policy_id": _token(baseline_record.get("requested_mod_policy_id")),
        "effective_mod_policy_id": _token(baseline_record.get("mod_policy_id")),
        "trust_policy_id": _token(baseline_record.get("trust_policy_id")),
        "physics_profile_id": _token(baseline_record.get("physics_profile_id")),
        "proof_anchor_schedule": dict(baseline_record.get("proof_anchor_schedule") or {}),
        "proof_anchors": anchors,
        "launch": {
            "command": _token(payload.get("launch_command")),
            "ui_mode": _token(launch.get("ui_mode")),
            "entrypoint": _token(launch.get("entrypoint")),
            "deterministic_fingerprint": _token(launch.get("deterministic_fingerprint")),
            "session_universe_id": _token(_as_map(launch.get("session_spec")).get("universe_id")),
            "session_seed": _token(_as_map(launch.get("session_spec")).get("universe_seed")),
        },
        "teleport": {
            "commands": [
                "/tp sol",
                "/tp earth",
                coordinate_command,
            ],
            "sol_plan_fingerprint": _token(_as_map(teleports.get("sol")).get("deterministic_fingerprint")),
            "earth_plan_fingerprint": _token(_as_map(teleports.get("earth")).get("deterministic_fingerprint")),
            "coordinate_plan_fingerprint": _token(_as_map(teleports.get("coordinate")).get("deterministic_fingerprint")),
            "coordinate_command": coordinate_command,
        },
        "inspect": {
            "command": "tool scan",
            "scan_id": _token(inspect_result.get("scan_id")),
            "tile_cell_key": dict(inspect_result.get("tile_cell_key") or {}),
            "surface_flags": dict(inspect_result.get("surface_flags") or {}),
            "material_baseline_id": _token(inspect_result.get("material_baseline_id")),
            "biome_stub_id": _token(inspect_result.get("biome_stub_id")),
            "elevation_proxy_mm": int(inspect_result.get("elevation_proxy_mm", 0) or 0),
            "temperature": int(inspect_result.get("temperature", 0) or 0),
            "daylight": int(inspect_result.get("daylight", 0) or 0),
            "tide_height_proxy": int(inspect_result.get("tide_height_proxy", 0) or 0),
            "wind_vector": dict(inspect_result.get("wind_vector") or {}),
            "pollution": int(inspect_result.get("pollution", 0) or 0),
            "deterministic_fingerprint": _token(inspect_result.get("deterministic_fingerprint")),
        },
        "terrain_edit": {
            "command": "tool mine",
            "task_fingerprint": _token(mine_task.get("deterministic_fingerprint")),
            "process_id": "process.geometry_remove",
            "target_cell_key": target_cell_key,
            "selected_tile_count": 1,
            "volume_amount": int(_as_map(payload.get("terrain_edit")).get("volume_amount", BASELINE_GEOMETRY_VOLUME) or BASELINE_GEOMETRY_VOLUME),
            "edited_cell_count": int(_as_map(payload.get("terrain_edit")).get("edited_cell_count", 0) or 0),
            "material_out_batch_ids": [str(item) for item in list(_as_map(payload.get("terrain_edit")).get("material_out_batch_ids") or []) if _token(item)],
        },
        "logic": {
            "commands": [
                "tool probe",
                "process.logic_compile_request",
                "tool trace",
            ],
            "result": _token(logic.get("result")),
            "network_id": _token(logic.get("network_id")),
            "compiled_model_hash": _token(logic.get("compiled_model_hash")),
            "toggle_off_final_signal_hash": _token(logic.get("toggle_off_final_signal_hash")),
            "toggle_on_final_signal_hash": _token(logic.get("toggle_on_final_signal_hash")),
            "logic_debug_request_hash_chain": _token(logic.get("logic_debug_request_hash_chain")),
            "logic_debug_trace_hash_chain": _token(logic.get("logic_debug_trace_hash_chain")),
            "logic_protocol_summary_hash_chain": _token(logic.get("logic_protocol_summary_hash_chain")),
            "deterministic_fingerprint": _token(logic.get("deterministic_fingerprint")),
        },
        "save_reload": {
            "save_command": "save_snapshot",
            "reload_command": "load_versioned_artifact",
            "fresh_save_hash": _token(save_reload.get("fresh_save_hash")),
            "loaded_save_hash": _token(save_reload.get("loaded_save_hash")),
            "committed_save_hash": _token(save_reload.get("committed_save_hash")),
            "save_reload_matches": bool(save_reload.get("save_reload_matches")),
            "fresh_save_matches_committed": bool(save_reload.get("fresh_save_matches_committed")),
        },
        "replay": {
            "command": _token(payload.get("verify_command")),
            "replay_t3_state_hash_anchor": _token(replay.get("replay_t3_state_hash_anchor")),
            "replay_t3_derived_view_hash": _token(replay.get("replay_t3_derived_view_hash")),
            "final_anchor_matches_reload": bool(replay.get("final_anchor_matches_reload")),
            "final_anchor_matches_baseline": bool(replay.get("final_anchor_matches_baseline")),
        },
        "steps": [
            _step_row(
                step_id="STEP_1",
                title="Launch",
                commands=[_token(payload.get("launch_command"))],
                expected_result="deterministic CLI bootstrap opens the baseline universe context",
                proof_anchor_hash=_token(_as_map(anchors[0] if len(anchors) > 0 else {}).get("state_hash_anchor")),
                derived_view_hash=_token(_as_map(anchors[0] if len(anchors) > 0 else {}).get("derived_view_hash")),
                details={"launch_fingerprint": _token(_as_map(launch).get("deterministic_fingerprint"))},
            ),
            _step_row(
                step_id="STEP_2",
                title="Teleport",
                commands=["tool tp /tp sol", "tool tp /tp earth", "tool tp {}".format(coordinate_command)],
                expected_result="teleport planning remains deterministic for sol, earth, and the baseline surface coordinate",
                proof_anchor_hash=_token(_as_map(anchors[1] if len(anchors) > 1 else {}).get("state_hash_anchor")),
                derived_view_hash=_token(_as_map(anchors[1] if len(anchors) > 1 else {}).get("derived_view_hash")),
                details={
                    "sol_plan_fingerprint": _token(_as_map(teleports.get("sol")).get("deterministic_fingerprint")),
                    "earth_plan_fingerprint": _token(_as_map(teleports.get("earth")).get("deterministic_fingerprint")),
                    "coordinate_plan_fingerprint": _token(_as_map(teleports.get("coordinate")).get("deterministic_fingerprint")),
                },
            ),
            _step_row(
                step_id="STEP_3",
                title="Inspect",
                commands=["tool scan"],
                expected_result="scanner surfaces elevation and climate proxies for the baseline tile without GUI-only state",
                proof_anchor_hash=_token(_as_map(anchors[1] if len(anchors) > 1 else {}).get("state_hash_anchor")),
                derived_view_hash=_token(_as_map(anchors[1] if len(anchors) > 1 else {}).get("derived_view_hash")),
                details={
                    "scan_fingerprint": _token(inspect_result.get("deterministic_fingerprint")),
                    "elevation_proxy_mm": int(inspect_result.get("elevation_proxy_mm", 0) or 0),
                    "temperature": int(inspect_result.get("temperature", 0) or 0),
                    "daylight": int(inspect_result.get("daylight", 0) or 0),
                    "tide_height_proxy": int(inspect_result.get("tide_height_proxy", 0) or 0),
                },
            ),
            _step_row(
                step_id="STEP_4",
                title="Modify Terrain",
                commands=["tool mine"],
                expected_result="one baseline surface tile selection is mined deterministically through process.geometry_remove",
                proof_anchor_hash=_token(_as_map(anchors[2] if len(anchors) > 2 else {}).get("state_hash_anchor")),
                derived_view_hash=_token(_as_map(anchors[2] if len(anchors) > 2 else {}).get("derived_view_hash")),
                details={
                    "terrain_task_fingerprint": _token(mine_task.get("deterministic_fingerprint")),
                    "edited_cell_count": int(_as_map(payload.get("terrain_edit")).get("edited_cell_count", 0) or 0),
                    "volume_amount": int(_as_map(payload.get("terrain_edit")).get("volume_amount", BASELINE_GEOMETRY_VOLUME) or BASELINE_GEOMETRY_VOLUME),
                },
            ),
            _step_row(
                step_id="STEP_5",
                title="Logic Interaction",
                commands=["tool probe", "process.logic_compile_request", "tool trace"],
                expected_result="L1 and compiled L2 logic outputs remain deterministic for the canonical smoke network",
                details={
                    "compiled_model_hash": _token(logic.get("compiled_model_hash")),
                    "toggle_off_final_signal_hash": _token(logic.get("toggle_off_final_signal_hash")),
                    "toggle_on_final_signal_hash": _token(logic.get("toggle_on_final_signal_hash")),
                },
            ),
            _step_row(
                step_id="STEP_6",
                title="Save",
                commands=["save_snapshot"],
                expected_result="the gameplay loop emits the same save hash as the frozen baseline universe save",
                proof_anchor_hash=_token(_as_map(anchors[2] if len(anchors) > 2 else {}).get("state_hash_anchor")),
                derived_view_hash=_token(_as_map(anchors[2] if len(anchors) > 2 else {}).get("derived_view_hash")),
                details={
                    "fresh_save_hash": _token(save_reload.get("fresh_save_hash")),
                    "committed_save_hash": _token(save_reload.get("committed_save_hash")),
                },
            ),
            _step_row(
                step_id="STEP_7",
                title="Reload",
                commands=["load_versioned_artifact"],
                expected_result="reloading the saved universe reproduces the same post-edit proof anchor",
                proof_anchor_hash=_token(_as_map(anchors[3] if len(anchors) > 3 else {}).get("state_hash_anchor")),
                derived_view_hash=_token(_as_map(anchors[3] if len(anchors) > 3 else {}).get("derived_view_hash")),
                details={
                    "loaded_save_hash": _token(save_reload.get("loaded_save_hash")),
                    "save_reload_matches": bool(save_reload.get("save_reload_matches")),
                },
            ),
            _step_row(
                step_id="STEP_8",
                title="Replay",
                commands=[_token(payload.get("verify_command"))],
                expected_result="replaying from the baseline seed reproduces the same final anchor as reload",
                proof_anchor_hash=_token(replay.get("replay_t3_state_hash_anchor")),
                derived_view_hash=_token(replay.get("replay_t3_derived_view_hash")),
                details={
                    "final_anchor_matches_reload": bool(replay.get("final_anchor_matches_reload")),
                    "final_anchor_matches_baseline": bool(replay.get("final_anchor_matches_baseline")),
                },
            ),
        ],
        "deterministic_fingerprint": "",
    }
    record["deterministic_fingerprint"] = gameplay_snapshot_record_hash(record)
    return record


def run_gameplay_loop(
    repo_root: str,
    *,
    seed_text: str = "",
    instance_path: str = "",
    save_path: str = "",
    output_root_rel: str = "",
    write_outputs: bool = True,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    paths = _default_paths(repo_root_abs, output_root_rel=output_root_rel, write_outputs=write_outputs)
    _ensure_dir(os.path.dirname(paths["runtime_save_path"]))
    _ensure_dir(paths["replay_root_abs"])
    if write_outputs:
        _ensure_dir(paths["snapshot_root_abs"])
    baseline_snapshot = load_baseline_universe_snapshot(repo_root_abs)
    baseline_record = _as_map(baseline_snapshot.get("record"))
    resolved_seed = read_worldgen_baseline_seed(repo_root_abs, seed_text=seed_text)
    context = _baseline_context(repo_root_abs, resolved_seed)
    instance_manifest, instance_manifest_path = _load_instance_manifest(repo_root_abs, instance_path=instance_path)
    committed_save_path = os.path.normpath(os.path.abspath(save_path)) if _token(save_path) else _repo_abs(repo_root_abs, BASELINE_SAVE_REL)

    launch_command = (
        'python tools/mvp/runtime_entry.py client --repo-root . --seed "{}" '
        "--profile_bundle {} --pack_lock {} --ui cli"
    ).format(
        resolved_seed,
        _norm(BASELINE_PROFILE_BUNDLE_REL),
        _norm(BASELINE_PACK_LOCK_REL),
    )
    verify_command = (
        "python tools/mvp/tool_verify_gameplay_loop.py --repo-root . --seed-text \"{}\" "
        "--snapshot-path {}"
    ).format(
        resolved_seed,
        _norm(MVP_GAMEPLAY_SNAPSHOT_REL),
    )
    launch_payload = build_runtime_bootstrap(
        repo_root=repo_root_abs,
        entrypoint="client",
        ui="cli",
        seed=resolved_seed,
        profile_bundle_path=_norm(BASELINE_PROFILE_BUNDLE_REL),
        pack_lock_path=_norm(BASELINE_PACK_LOCK_REL),
        teleport="",
        authority_mode="dev",
    )
    if not _token(launch_payload.get("deterministic_fingerprint")):
        launch_payload["deterministic_fingerprint"] = canonical_sha256(dict(launch_payload, deterministic_fingerprint=""))

    initial_state = _initial_state_payload(repo_root_abs, context)
    working_state = _working_state(initial_state, context)
    t0_state = _saveable_state(repo_root_abs, working_state, context)
    t0_anchor = _proof_anchor_row(
        checkpoint_id="T0",
        anchor_label="initialization",
        state=t0_state,
        context=context,
        reason=ANCHOR_REASON_INTERVAL,
        view_state=t0_state,
    )

    execution = _run_worldgen_refinement(repo_root_abs, context, working_state)
    t1_state = _saveable_state(repo_root_abs, working_state, context)
    t1_anchor = _proof_anchor_row(
        checkpoint_id="T1",
        anchor_label="post_refinement",
        state=t1_state,
        context=context,
        reason=ANCHOR_REASON_INTERVAL,
        view_state=working_state,
    )

    target_cell_key = _as_map(execution.get("target_cell_key"))
    surface_tile = _as_map((_as_list(working_state.get("worldgen_surface_tile_artifacts")) or [{}])[0])
    selection = _surface_selection(surface_tile, target_cell_key)
    field_rows = _as_list(working_state.get("field_cells"))
    inspect_result = build_scan_result(
        authority_context=_authority_context(),
        selection=selection,
        inspection_snapshot=_inspection_snapshot(surface_tile, selection),
        field_values={
            "temperature": _field_value(field_rows, "field.temperature"),
            "daylight": _field_value(field_rows, "field.daylight"),
            "tide_height_proxy": _field_value(field_rows, "field.tide_height_proxy"),
            "wind_vector": {"x": 0, "y": 0, "z": 0},
            "pollution": 0,
        },
        property_origin_result=_property_origin_result(surface_tile),
        has_physical_access=True,
    )

    surface_cell_key = _as_map(_as_map(execution.get("surface_plan")).get("surface_cell_key"))
    coordinate_command = "/tp {}:0,0,0".format(_token(surface_cell_key.get("chart_id")) or _token(target_cell_key.get("chart_id")) or "frame.world")
    teleports = {
        "sol": build_teleport_tool_surface(
            repo_root=repo_root_abs,
            authority_context=_authority_context(),
            command="/tp sol",
            universe_seed=resolved_seed,
            authority_mode="dev",
            profile_bundle_path=_norm(BASELINE_PROFILE_BUNDLE_REL),
            pack_lock_path=_norm(BASELINE_PACK_LOCK_REL),
            teleport_counter=0,
            candidate_system_rows=[],
            surface_target_cell_key=surface_cell_key,
            current_tick=0,
        ),
        "earth": build_teleport_tool_surface(
            repo_root=repo_root_abs,
            authority_context=_authority_context(),
            command="/tp earth",
            universe_seed=resolved_seed,
            authority_mode="dev",
            profile_bundle_path=_norm(BASELINE_PROFILE_BUNDLE_REL),
            pack_lock_path=_norm(BASELINE_PACK_LOCK_REL),
            teleport_counter=1,
            candidate_system_rows=[],
            surface_target_cell_key=surface_cell_key,
            current_tick=0,
        ),
        "coordinate": build_teleport_tool_surface(
            repo_root=repo_root_abs,
            authority_context=_authority_context(),
            command=coordinate_command,
            universe_seed=resolved_seed,
            authority_mode="dev",
            profile_bundle_path=_norm(BASELINE_PROFILE_BUNDLE_REL),
            pack_lock_path=_norm(BASELINE_PACK_LOCK_REL),
            teleport_counter=2,
            candidate_system_rows=[],
            surface_target_cell_key=surface_cell_key,
            current_tick=0,
        ),
    }

    mine_task = build_mine_at_cursor_task(
        authority_context=_authority_context(),
        subject_id="subject.player",
        selection=selection,
        volume_amount=BASELINE_GEOMETRY_VOLUME,
    )
    terrain_edit = _run_baseline_terrain_edit(context, working_state, target_cell_key)
    t2_state = _saveable_state(repo_root_abs, working_state, context)
    t2_anchor = _proof_anchor_row(
        checkpoint_id="T2",
        anchor_label="after_first_terrain_edit",
        state=t2_state,
        context=context,
        reason=ANCHOR_REASON_INTERVAL,
        view_state=working_state,
    )

    logic_report = run_logic_smoke_suite(repo_root_abs)

    _write_canonical_json(paths["runtime_save_path"], t2_state)
    loaded_payload, loaded_meta, loaded_error = load_versioned_artifact(
        repo_root=repo_root_abs,
        artifact_kind="save_file",
        path=paths["runtime_save_path"],
        semantic_contract_bundle_hash=_token(_as_map(context.get("proof_bundle")).get("universe_contract_bundle_hash")),
        allow_read_only=False,
        strip_loaded_metadata=False,
    )
    if loaded_error:
        raise ValueError(_token(_as_map(loaded_error.get("refusal")).get("message")) or "gameplay loop save reload failed")
    t3_anchor = _proof_anchor_row(
        checkpoint_id="T3",
        anchor_label="after_save_reload",
        state=loaded_payload,
        context=context,
        reason=ANCHOR_REASON_SAVE,
        view_state=loaded_payload,
    )

    committed_save_payload = _load_json(committed_save_path)
    replay_run = generate_baseline_universe(
        repo_root_abs,
        seed_text=resolved_seed,
        output_root_rel=paths["replay_root_rel"],
        write_outputs=False,
    )
    replay_record = _as_map(_as_map(replay_run.get("snapshot_payload")).get("record"))
    replay_anchors = [_as_map(row) for row in _as_list(replay_record.get("proof_anchors"))]
    replay_t3 = replay_anchors[3] if len(replay_anchors) > 3 else {}

    save_reload = {
        "fresh_save_hash": _token(_as_map(t2_state).get("deterministic_fingerprint")),
        "loaded_save_hash": _token(_as_map(loaded_payload).get("deterministic_fingerprint")),
        "committed_save_hash": _token(_as_map(baseline_record.get("save_artifact")).get("save_file_hash"))
        or _token(_as_map(committed_save_payload).get("deterministic_fingerprint")),
        "save_reload_matches": canonical_sha256(loaded_payload) == canonical_sha256(t2_state),
        "fresh_save_matches_committed": _token(_as_map(t2_state).get("deterministic_fingerprint"))
        == (_token(_as_map(baseline_record.get("save_artifact")).get("save_file_hash")) or _token(_as_map(committed_save_payload).get("deterministic_fingerprint"))),
        "loaded_save_metadata": dict(loaded_meta or {}),
    }
    replay = {
        "replay_t3_state_hash_anchor": _token(replay_t3.get("state_hash_anchor")),
        "replay_t3_derived_view_hash": _token(replay_t3.get("derived_view_hash")),
        "final_anchor_matches_reload": _token(replay_t3.get("state_hash_anchor")) == _token(t3_anchor.get("state_hash_anchor")),
        "final_anchor_matches_baseline": _token(replay_t3.get("state_hash_anchor"))
        == _token(_as_map((_as_list(baseline_record.get("proof_anchors")) or [{}, {}, {}, {}])[3]).get("state_hash_anchor")),
        "replay_snapshot_fingerprint": _token(replay_record.get("deterministic_fingerprint")),
    }
    result_payload = {
        "seed_text": resolved_seed,
        "baseline_record": baseline_record,
        "instance_manifest": instance_manifest,
        "instance_manifest_rel": _relative_path(repo_root_abs, instance_manifest_path),
        "baseline_save_rel": _relative_path(repo_root_abs, committed_save_path),
        "runtime_temp_save_rel": _relative_path(repo_root_abs, paths["runtime_save_path"]),
        "launch_command": launch_command,
        "verify_command": verify_command,
        "launch": launch_payload,
        "teleports": teleports,
        "coordinate_target": {"command": coordinate_command},
        "target_cell_key": target_cell_key,
        "inspect": inspect_result,
        "mine_task": mine_task,
        "terrain_edit": terrain_edit,
        "logic": logic_report,
        "save_reload": save_reload,
        "replay": replay,
        "proof_anchors": [t0_anchor, t1_anchor, t2_anchor, t3_anchor],
    }
    record = _snapshot_record(result_payload)
    snapshot_payload = {
        "schema_id": MVP_GAMEPLAY_SCHEMA_ID,
        "schema_version": "1.0.0",
        "record": record,
    }
    if write_outputs:
        write_gameplay_loop_outputs(repo_root_abs, snapshot_payload, snapshot_path=paths["snapshot_path"], doc_path=paths["run_doc_path"])
    return {
        "result": "complete",
        "snapshot_payload": snapshot_payload,
        "output_paths": paths,
        "runtime_save_path": paths["runtime_save_path"],
        "instance_manifest_path": instance_manifest_path,
        "baseline_save_path": committed_save_path,
    }


def verify_gameplay_loop(
    repo_root: str,
    *,
    seed_text: str = "",
    instance_path: str = "",
    save_path: str = "",
    snapshot_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    expected_snapshot = load_gameplay_snapshot(repo_root_abs, snapshot_path=snapshot_path)
    expected_record = _as_map(expected_snapshot.get("record"))
    observed = run_gameplay_loop(
        repo_root_abs,
        seed_text=seed_text,
        instance_path=instance_path,
        save_path=save_path,
        output_root_rel=DEFAULT_GAMEPLAY_WORK_ROOT_REL,
        write_outputs=False,
    )
    observed_record = _as_map(_as_map(observed.get("snapshot_payload")).get("record"))
    mismatched_fields = _diff_values(expected_record, observed_record)
    observed_save_reload = _as_map(observed_record.get("save_reload"))
    observed_logic = _as_map(observed_record.get("logic"))
    observed_replay = _as_map(observed_record.get("replay"))
    report = {
        "schema_id": MVP_GAMEPLAY_VERIFY_SCHEMA_ID,
        "schema_version": "1.0.0",
        "result": (
            "complete"
            if (not mismatched_fields)
            and bool(observed_save_reload.get("save_reload_matches"))
            and bool(observed_replay.get("final_anchor_matches_reload"))
            and bool(observed_replay.get("final_anchor_matches_baseline"))
            and _token(observed_logic.get("result")) == "complete"
            else "violation"
        ),
        "matches_snapshot": not mismatched_fields,
        "save_reload_matches": bool(observed_save_reload.get("save_reload_matches")),
        "replay_matches_final_anchor": bool(observed_replay.get("final_anchor_matches_reload")),
        "replay_matches_baseline": bool(observed_replay.get("final_anchor_matches_baseline")),
        "logic_deterministic": _token(observed_logic.get("result")) == "complete",
        "expected_snapshot_fingerprint": _token(expected_record.get("deterministic_fingerprint")),
        "observed_snapshot_fingerprint": _token(observed_record.get("deterministic_fingerprint")),
        "mismatched_fields": mismatched_fields,
        "expected_record": expected_record,
        "observed_record": observed_record,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_gameplay_loop_run(snapshot_payload: Mapping[str, object]) -> str:
    record = _as_map(_as_map(snapshot_payload).get("record"))
    lines = [
        "# MVP Gameplay Loop Run",
        "",
        "- Result: `PASS`",
        "- Seed: `{}`".format(_token(record.get("baseline_seed"))),
        "- Snapshot Fingerprint: `{}`".format(_token(record.get("deterministic_fingerprint"))),
        "- Launch Fingerprint: `{}`".format(_token(_as_map(record.get("launch")).get("deterministic_fingerprint"))),
        "- Save Hash: `{}`".format(_token(_as_map(record.get("save_reload")).get("fresh_save_hash"))),
        "- Replay Final Anchor: `{}`".format(_token(_as_map(record.get("replay")).get("replay_t3_state_hash_anchor"))),
        "",
        "## Steps",
        "",
    ]
    for row in _as_list(record.get("steps")):
        step = _as_map(row)
        lines.append("### {}".format(_token(step.get("title")) or _token(step.get("step_id"))))
        for command in [str(item).strip() for item in list(step.get("commands") or []) if str(item).strip()]:
            lines.append("- Command: `{}`".format(command))
        lines.append("- Expected Result: `{}`".format(_token(step.get("expected_result"))))
        if _token(step.get("proof_anchor_hash")):
            lines.append("- Proof Anchor: `{}`".format(_token(step.get("proof_anchor_hash"))))
        if _token(step.get("derived_view_hash")):
            lines.append("- Derived View Hash: `{}`".format(_token(step.get("derived_view_hash"))))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_gameplay_loop_outputs(
    repo_root: str,
    snapshot_payload: Mapping[str, object],
    *,
    snapshot_path: str = "",
    doc_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    snapshot_target = os.path.normpath(os.path.abspath(snapshot_path)) if _token(snapshot_path) else _repo_abs(repo_root_abs, MVP_GAMEPLAY_SNAPSHOT_REL)
    doc_target = os.path.normpath(os.path.abspath(doc_path)) if _token(doc_path) else _repo_abs(repo_root_abs, MVP_GAMEPLAY_RUN_DOC_REL)
    _write_canonical_json(snapshot_target, _as_map(snapshot_payload))
    _write_text(doc_target, render_gameplay_loop_run(snapshot_payload))
    return {"snapshot_path": snapshot_target, "doc_path": doc_target}


def write_gameplay_verify_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    json_path: str = "",
    doc_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    json_target = os.path.normpath(os.path.abspath(json_path)) if _token(json_path) else _repo_abs(repo_root_abs, MVP_GAMEPLAY_VERIFY_JSON_REL)
    doc_target = os.path.normpath(os.path.abspath(doc_path)) if _token(doc_path) else _repo_abs(repo_root_abs, MVP_GAMEPLAY_VERIFY_DOC_REL)
    _write_canonical_json(json_target, _as_map(report))
    mismatches = [str(item).strip() for item in list(_as_map(report).get("mismatched_fields") or []) if str(item).strip()]
    lines = [
        "# MVP Gameplay Verify",
        "",
        "- Result: `{}`".format("PASS" if _token(_as_map(report).get("result")) == "complete" else "FAIL"),
        "- Matches Snapshot: `{}`".format(bool(_as_map(report).get("matches_snapshot"))),
        "- Save Reload Matches: `{}`".format(bool(_as_map(report).get("save_reload_matches"))),
        "- Replay Matches Reload: `{}`".format(bool(_as_map(report).get("replay_matches_final_anchor"))),
        "- Replay Matches Baseline: `{}`".format(bool(_as_map(report).get("replay_matches_baseline"))),
        "- Logic Deterministic: `{}`".format(bool(_as_map(report).get("logic_deterministic"))),
        "- Expected Snapshot Fingerprint: `{}`".format(_token(_as_map(report).get("expected_snapshot_fingerprint"))),
        "- Observed Snapshot Fingerprint: `{}`".format(_token(_as_map(report).get("observed_snapshot_fingerprint"))),
        "",
        "## Mismatches",
    ]
    if mismatches:
        lines.extend("- `{}`".format(item) for item in mismatches)
    else:
        lines.append("- None")
    _write_text(doc_target, "\n".join(lines) + "\n")
    return {"json_path": json_target, "doc_path": doc_target}


def render_gameplay_baseline_report(snapshot_payload: Mapping[str, object], verify_report: Mapping[str, object]) -> str:
    record = _as_map(_as_map(snapshot_payload).get("record"))
    verify = _as_map(verify_report)
    lines = [
        "# MVP Gameplay Baseline",
        "",
        "- Seed: `{}`".format(_token(record.get("baseline_seed"))),
        "- Pack Lock: `{}` (`{}`)".format(_token(record.get("pack_lock_id")), _token(record.get("pack_lock_hash"))),
        "- Profile Bundle: `{}` (`{}`)".format(_token(record.get("profile_bundle_id")), _token(record.get("profile_bundle_hash"))),
        "- Save Hash: `{}`".format(_token(_as_map(record.get("save_reload")).get("fresh_save_hash"))),
        "- Replay Confirmation: `{}`".format(bool(_as_map(record.get("replay")).get("final_anchor_matches_reload"))),
        "- Verification: `{}`".format("PASS" if _token(verify.get("result")) == "complete" else "FAIL"),
        "",
        "## Steps",
        "",
    ]
    for row in _as_list(record.get("steps")):
        step = _as_map(row)
        lines.append("- `{}` {}".format(_token(step.get("step_id")), _token(step.get("title"))))
    lines.extend(
        [
            "",
            "## Commands",
            "",
        ]
    )
    for row in _as_list(record.get("steps")):
        step = _as_map(row)
        title = _token(step.get("title")) or _token(step.get("step_id"))
        for command in [str(item).strip() for item in list(step.get("commands") or []) if str(item).strip()]:
            lines.append("- {}: `{}`".format(title, command))
    lines.extend(
        [
            "",
            "## Proof Anchors",
            "",
        ]
    )
    for row in _as_list(record.get("proof_anchors")):
        anchor = _as_map(row)
        lines.append(
            "- `{}`: truth `{}`, derived `{}`".format(
                _token(anchor.get("checkpoint_id")),
                _token(anchor.get("state_hash_anchor")),
                _token(anchor.get("derived_view_hash")),
            )
        )
    logic = _as_map(record.get("logic"))
    lines.extend(
        [
            "",
            "## Logic Hashes",
            "",
            "- Compiled Model: `{}`".format(_token(logic.get("compiled_model_hash"))),
            "- Toggle Off Final Signal: `{}`".format(_token(logic.get("toggle_off_final_signal_hash"))),
            "- Toggle On Final Signal: `{}`".format(_token(logic.get("toggle_on_final_signal_hash"))),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_gameplay_baseline_report(
    repo_root: str,
    *,
    snapshot_payload: Mapping[str, object],
    verify_report: Mapping[str, object],
    path: str = "",
) -> str:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    target = os.path.normpath(os.path.abspath(path)) if _token(path) else _repo_abs(repo_root_abs, MVP_GAMEPLAY_BASELINE_DOC_REL)
    return _write_text(target, render_gameplay_baseline_report(snapshot_payload, verify_report))


__all__ = [
    "MVP_GAMEPLAY_BASELINE_DOC_REL",
    "MVP_GAMEPLAY_DIR_REL",
    "MVP_GAMEPLAY_RUN_DOC_REL",
    "MVP_GAMEPLAY_SCHEMA_ID",
    "MVP_GAMEPLAY_SNAPSHOT_REL",
    "MVP_GAMEPLAY_VERIFY_DOC_REL",
    "MVP_GAMEPLAY_VERIFY_JSON_REL",
    "MVP_GAMEPLAY_VERIFY_SCHEMA_ID",
    "gameplay_snapshot_record_hash",
    "load_gameplay_snapshot",
    "render_gameplay_baseline_report",
    "render_gameplay_loop_run",
    "run_gameplay_loop",
    "verify_gameplay_loop",
    "write_gameplay_baseline_report",
    "write_gameplay_loop_outputs",
    "write_gameplay_verify_outputs",
]
