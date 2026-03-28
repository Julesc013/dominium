"""Shared helpers for the Omega baseline universe freeze."""

from __future__ import annotations

import copy
import json
import os
import sys
from typing import List, Mapping

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases
install_src_aliases(REPO_ROOT_HINT)

from compat.data_format_loader import load_versioned_artifact, stamp_artifact_metadata
from geo import (
    build_default_overlay_manifest,
    build_worldgen_request,
    overlay_proof_surface,
    validate_overlay_manifest_trust,
)
from lib.instance.instance_validator import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
    validate_instance_manifest,
)
from meta.identity import IDENTITY_KIND_INSTANCE, attach_universal_identity_block
from release.component_graph_resolver import DEFAULT_INSTALL_PROFILE_ID, load_install_profile_registry, select_install_profile
from security.trust import DEFAULT_TRUST_POLICY_ID
from engine.time.epoch_anchor_engine import (
    ANCHOR_REASON_INTERVAL,
    ANCHOR_REASON_SAVE,
    anchor_interval_ticks,
    build_epoch_anchor_record,
    load_time_anchor_policy,
)
from universe import build_universe_contract_bundle_payload
from worldgen.mw import build_planet_surface_cell_key, resolve_sol_anchor_cell_key, sol_anchor_object_ids, surface_tile_artifact_hash_chain
from tools.worldgen.worldgen_lock_common import (
    WORLDGEN_LOCK_ID,
    WORLDGEN_LOCK_VERSION,
    build_locked_identity_context,
    load_worldgen_lock_snapshot,
    read_worldgen_baseline_seed,
    seed_text_hash,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.creator import _initial_universe_state
from tools.xstack.sessionx.process_runtime import execute_intent


BASELINE_UNIVERSE_SCHEMA_ID = "dominium.schema.governance" + ".baseline_universe_snapshot"
BASELINE_UNIVERSE_VERIFY_SCHEMA_ID = "dominium.schema.audit" + ".baseline_universe_verify"
BASELINE_UNIVERSE_VERSION = 0
BASELINE_UNIVERSE_DIR_REL = os.path.join("data", "baselines", "universe")
BASELINE_INSTANCE_MANIFEST_REL = os.path.join(BASELINE_UNIVERSE_DIR_REL, "baseline_instance.manifest.json")
BASELINE_PACK_LOCK_REL = os.path.join(BASELINE_UNIVERSE_DIR_REL, "baseline_pack_lock.json")
BASELINE_PROFILE_BUNDLE_REL = os.path.join(BASELINE_UNIVERSE_DIR_REL, "baseline_profile_bundle.json")
BASELINE_SAVE_REL = os.path.join(BASELINE_UNIVERSE_DIR_REL, "baseline_save_0.save")
BASELINE_SNAPSHOT_REL = os.path.join(BASELINE_UNIVERSE_DIR_REL, "baseline_universe_snapshot.json")
BASELINE_VERIFY_JSON_REL = os.path.join("data", "audit", "baseline_universe_verify.json")
BASELINE_VERIFY_DOC_REL = os.path.join("docs", "audit", "BASELINE_UNIVERSE_VERIFY.md")

BASELINE_INSTANCE_ID = "instance.baseline_universe_0"
BASELINE_SAVE_ID = "save.baseline_universe_0"
BASELINE_INSTALL_ID = "install.baseline_universe_0"
BASELINE_SESSION_TEMPLATE_ID = "session.mvp_default"
BASELINE_GEOMETRY_VOLUME = 16
BASELINE_SURFACE_CHART_ID = "chart.atlas.north"
BASELINE_SURFACE_INDEX_TUPLE = [0, 0]
BASELINE_SURFACE_REFINEMENT_LEVEL = 1
BASELINE_PLANET_TAGS = ["planet.earth", "sol.planet.earth"]
BASELINE_STABILITY_CLASS = "stable"
SAVE_LAST_OPENED_KEY = "instance.last_opened_save_id"
DEFAULT_WORK_ROOT_REL = os.path.join("build", "tmp", "omega2_baseline")
_TRANSIENT_STATE_FIELDS = (
    "mod_policy_id",
    "universe_contract_bundle_hash",
    "universe_identity",
)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, str(rel_path or "").replace("/", os.sep))))


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    token = str(path or "").strip()
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


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
        handle.write(str(text).replace("\r\n", "\n"))
    return path


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _normalized_load_metadata(meta: Mapping[str, object], *, repo_root: str, save_path: str) -> dict:
    payload = dict(meta or {})
    payload["path"] = _norm(save_path or BASELINE_SAVE_REL)
    return payload


def _diff_values(expected: object, observed: object, *, path: str = "$", out: List[str] | None = None, limit: int = 64) -> List[str]:
    rows = out if out is not None else []
    if len(rows) >= int(limit):
        return rows
    if isinstance(expected, Mapping) and isinstance(observed, Mapping):
        keys = sorted(set(list(expected.keys()) + list(observed.keys())))
        for key in keys:
            token = str(key)
            if key not in expected:
                rows.append("{}.{}: unexpected key".format(path, token))
            elif key not in observed:
                rows.append("{}.{}: missing key".format(path, token))
            else:
                _diff_values(expected.get(key), observed.get(key), path="{}.{}".format(path, token), out=rows, limit=limit)
            if len(rows) >= int(limit):
                break
        return rows
    if isinstance(expected, list) and isinstance(observed, list):
        if len(expected) != len(observed):
            rows.append("{}: list length {} != {}".format(path, len(expected), len(observed)))
            return rows
        for index, (left, right) in enumerate(zip(expected, observed)):
            _diff_values(left, right, path="{}[{}]".format(path, index), out=rows, limit=limit)
            if len(rows) >= int(limit):
                break
        return rows
    if expected != observed:
        rows.append(path)
    return rows


def baseline_snapshot_record_hash(record: Mapping[str, object]) -> str:
    payload = dict(record or {})
    payload["deterministic_fingerprint"] = ""
    return canonical_sha256(payload)


def load_baseline_universe_snapshot(repo_root: str, snapshot_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    path = os.path.normpath(os.path.abspath(snapshot_path)) if _token(snapshot_path) else _repo_abs(repo_root_abs, BASELINE_SNAPSHOT_REL)
    return _load_json(path)


def load_baseline_instance_manifest(repo_root: str, manifest_path: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    path = os.path.normpath(os.path.abspath(manifest_path)) if _token(manifest_path) else _repo_abs(repo_root_abs, BASELINE_INSTANCE_MANIFEST_REL)
    return _load_json(path)


def _frozen_baseline_engine_version_created(repo_root: str) -> str:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    committed_save = _load_json(_repo_abs(repo_root_abs, BASELINE_SAVE_REL))
    engine_version_created = _token(committed_save.get("engine_version_created"))
    if engine_version_created:
        return engine_version_created
    snapshot_payload = load_baseline_universe_snapshot(repo_root_abs)
    snapshot_record = _as_map(snapshot_payload.get("record"))
    return _token(_as_map(snapshot_record.get("save_artifact")).get("engine_version_created"))


def _normalize_frozen_process_log_anchors(repo_root: str, payload: Mapping[str, object]) -> dict:
    current = copy.deepcopy(dict(payload or {}))
    current_rows = current.get("process_log")
    if not isinstance(current_rows, list) or not current_rows:
        return current
    if any(not isinstance(row, Mapping) for row in current_rows):
        return current
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    committed_save = _load_json(_repo_abs(repo_root_abs, BASELINE_SAVE_REL))
    committed_rows = committed_save.get("process_log")
    if not isinstance(committed_rows, list) or len(current_rows) > len(committed_rows):
        return current
    if any(not isinstance(row, Mapping) for row in committed_rows[: len(current_rows)]):
        return current
    normalized_rows = []
    for index, row in enumerate(current_rows):
        normalized_row = copy.deepcopy(dict(row))
        committed_row = dict(committed_rows[index])
        compare_left = copy.deepcopy(normalized_row)
        compare_right = copy.deepcopy(committed_row)
        compare_left["state_hash_anchor"] = ""
        compare_right["state_hash_anchor"] = ""
        if compare_left != compare_right:
            return current
        frozen_anchor = _token(committed_row.get("state_hash_anchor"))
        if frozen_anchor:
            normalized_row["state_hash_anchor"] = frozen_anchor
        normalized_rows.append(normalized_row)
    current["process_log"] = normalized_rows
    return current


def _adopt_frozen_baseline_artifact(repo_root: str, payload: Mapping[str, object], rel_path: str, hash_field: str) -> dict:
    current = copy.deepcopy(dict(payload or {}))
    current_hash = _token(current.get(hash_field))
    if not current_hash:
        return current
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    frozen_payload = _load_json(_repo_abs(repo_root_abs, rel_path))
    if _token(frozen_payload.get(hash_field)) != current_hash:
        return current
    return frozen_payload or current


def _install_profile_payload(repo_root: str) -> dict:
    payload = select_install_profile(load_install_profile_registry(repo_root), install_profile_id=DEFAULT_INSTALL_PROFILE_ID)
    if payload:
        return dict(payload)
    return {
        "install_profile_id": DEFAULT_INSTALL_PROFILE_ID,
        "required_selectors": [],
        "optional_selectors": [],
        "default_mod_policy_id": "mod_policy.lab",
        "default_overlay_conflict_policy_id": "overlay.conflict.last_wins",
        "deterministic_fingerprint": canonical_sha256(
            {
                "install_profile_id": DEFAULT_INSTALL_PROFILE_ID,
                "required_selectors": [],
                "optional_selectors": [],
                "default_mod_policy_id": "mod_policy.lab",
                "default_overlay_conflict_policy_id": "overlay.conflict.last_wins",
            }
        ),
        "extensions": {},
    }


def _baseline_context(repo_root: str, seed_text: str) -> dict:
    worldgen_snapshot = load_worldgen_lock_snapshot(repo_root)
    worldgen_record = _as_map(worldgen_snapshot.get("record"))
    if not worldgen_record:
        raise ValueError("WORLDGEN-LOCK baseline snapshot is missing")
    if _token(worldgen_record.get("baseline_seed")) != _token(seed_text):
        raise ValueError("baseline seed does not match WORLDGEN-LOCK baseline seed")

    locked = build_locked_identity_context(repo_root, seed_text)
    profile_bundle = _adopt_frozen_baseline_artifact(
        repo_root,
        _as_map(locked.get("profile_bundle")),
        BASELINE_PROFILE_BUNDLE_REL,
        "profile_bundle_hash",
    )
    pack_lock = _adopt_frozen_baseline_artifact(
        repo_root,
        _as_map(locked.get("pack_lock")),
        BASELINE_PACK_LOCK_REL,
        "pack_lock_hash",
    )
    universe_identity = dict(locked.get("universe_identity") or {})
    if _token(pack_lock.get("pack_lock_hash")) != _token(worldgen_record.get("pack_lock_hash")):
        raise ValueError("pack lock hash does not match WORLDGEN-LOCK baseline")
    if _token(profile_bundle.get("profile_bundle_hash")) != _token(worldgen_record.get("profile_bundle_hash")):
        raise ValueError("profile bundle hash does not match WORLDGEN-LOCK baseline")
    if _token(universe_identity.get("identity_hash")) != _token(worldgen_record.get("universe_identity_hash")):
        raise ValueError("universe identity hash does not match WORLDGEN-LOCK baseline")

    bundle_payload, _registry_payload, proof_bundle, bundle_errors = build_universe_contract_bundle_payload(repo_root=repo_root)
    if bundle_errors:
        raise ValueError("universe contract bundle is invalid: {}".format(", ".join(sorted(set(bundle_errors)))))
    time_anchor_policy, time_anchor_error = load_time_anchor_policy(repo_root)
    if time_anchor_error:
        raise ValueError(_token(time_anchor_error.get("message")) or "time anchor policy is unavailable")
    install_profile = _install_profile_payload(repo_root)
    return {
        "seed_text": str(seed_text),
        "worldgen_lock_snapshot": dict(worldgen_snapshot),
        "worldgen_lock_record": worldgen_record,
        "profile_bundle": profile_bundle,
        "pack_lock": pack_lock,
        "universe_identity": universe_identity,
        "universe_contract_bundle": dict(bundle_payload),
        "proof_bundle": dict(proof_bundle),
        "time_anchor_policy": dict(time_anchor_policy),
        "install_profile": install_profile,
    }


def _baseline_authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.omega2.baseline",
        "experience_id": "profile.omega2.baseline",
        "law_profile_id": "law.omega2.baseline",
        "entitlements": ["entitlement.control.admin", "entitlement.inspect", "session.boot"],
        "epistemic_scope": {"scope_id": "scope.omega2.baseline", "visibility_level": "nondiegetic"},
        "privilege_level": "operator",
    }


def _baseline_law_profile() -> dict:
    allowed_processes = ["process.geometry_remove", "process.worldgen_request"]
    return {
        "law_profile_id": "law.omega2.baseline",
        "allowed_processes": list(allowed_processes),
        "forbidden_processes": [],
        "process_entitlement_requirements": dict((process_id, "entitlement.control.admin") for process_id in allowed_processes),
        "process_privilege_requirements": dict((process_id, "operator") for process_id in allowed_processes),
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1_000_000, "allow_hidden_state_access": True},
        "epistemic_policy_id": "ep.policy.lab_broad",
    }


def _baseline_policy_context(*, physics_profile_id: str, pack_lock_hash: str) -> dict:
    return {
        "physics_profile_id": str(physics_profile_id),
        "pack_lock_hash": str(pack_lock_hash),
        "budget_policy": {
            "policy_id": "policy.budget.omega2.baseline",
            "max_regions_micro": 0,
            "max_entities_micro": 0,
            "max_compute_units_per_tick": 4096,
            "entity_compute_weight": 0,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 0, "medium": 0, "fine": 0},
        },
        "budget_envelope_id": "budget.omega2.baseline",
        "budget_envelope_registry": {
            "envelopes": [
                {
                    "envelope_id": "budget.omega2.baseline",
                    "max_micro_entities_per_shard": 0,
                    "max_micro_regions_per_shard": 0,
                    "max_solver_cost_units_per_tick": 4096,
                    "max_inspection_cost_units_per_tick": 64,
                    "extensions": {},
                }
            ]
        },
        "numeric_precision_policy": {
            "policy_id": "precision.omega2.baseline",
            "fixed_point": {
                "fractional_bits": 24,
                "storage_bits": 64,
                "overflow_behavior": "refuse",
                "error_budget_max": 0,
            },
        },
        "universe_physics_profile_registry": {
            "physics_profiles": [
                {
                    "physics_profile_id": str(physics_profile_id),
                    "allowed_exception_types": [
                        "exception.boundary_flux",
                        "exception.creation_annihilation",
                        "exception.numeric_error_budget",
                    ],
                }
            ]
        },
        "quantity_type_registry": {
            "quantity_types": [
                {"quantity_id": "quantity.mass", "dimension_id": "dim.mass"},
                {"quantity_id": "quantity.mass_energy_total", "dimension_id": "dim.energy"},
            ]
        },
        "quantity_registry": {
            "quantities": [
                {"quantity_id": "quantity.mass", "dimension_id": "dim.mass"},
                {"quantity_id": "quantity.mass_energy_total", "dimension_id": "dim.energy"},
            ]
        },
    }


def _initial_state_payload(repo_root: str, context: Mapping[str, object]) -> dict:
    universe_identity = _as_map(context.get("universe_identity"))
    pack_lock = _as_map(context.get("pack_lock"))
    proof_bundle = _as_map(context.get("proof_bundle"))
    state = _initial_universe_state(
        save_id=BASELINE_SAVE_ID,
        law_profile_id="law.lab_freecam",
        camera_assembly=None,
        instrument_assemblies=[],
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        activation_policy_id="policy.activate.default",
        max_compute_units_per_tick=4096,
    )
    overlay_manifest = build_default_overlay_manifest(
        universe_id=_token(universe_identity.get("universe_id")),
        pack_lock_hash=_token(pack_lock.get("pack_lock_hash")),
        save_id=BASELINE_SAVE_ID,
        generator_version_id=_token(universe_identity.get("generator_version_id")),
        overlay_conflict_policy_id=_token(pack_lock.get("overlay_conflict_policy_id")),
    )
    overlay_trust = validate_overlay_manifest_trust(
        overlay_manifest=overlay_manifest,
        resolved_packs=list(pack_lock.get("ordered_packs") or []),
        expected_pack_lock_hash=_token(pack_lock.get("pack_lock_hash")),
        overlay_conflict_policy_id=_token(pack_lock.get("overlay_conflict_policy_id")),
    )
    if _token(overlay_trust.get("result")) != "complete":
        raise ValueError(_token(overlay_trust.get("message")) or "overlay manifest trust validation failed")
    state["overlay_manifest"] = dict(overlay_trust.get("overlay_manifest") or {})
    state["save_property_patches"] = []
    state["overlay_merge_results"] = []
    overlay_surface = overlay_proof_surface(
        overlay_manifest=state.get("overlay_manifest"),
        property_patches=state.get("save_property_patches"),
        effective_object_views=state.get("overlay_merge_results"),
    )
    state["overlay_manifest_hash"] = _token(overlay_surface.get("overlay_manifest_hash"))
    state["property_patch_hash_chain"] = _token(overlay_surface.get("property_patch_hash_chain"))
    state["overlay_merge_result_hash_chain"] = _token(overlay_surface.get("overlay_merge_result_hash_chain"))
    return stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="save_file",
        payload=state,
        semantic_contract_bundle_hash=_token(proof_bundle.get("universe_contract_bundle_hash")),
    )


def _working_state(initial_state: Mapping[str, object], context: Mapping[str, object]) -> dict:
    state = copy.deepcopy(dict(initial_state or {}))
    state["universe_identity"] = copy.deepcopy(_as_map(context.get("universe_identity")))
    state["universe_contract_bundle_hash"] = _token(_as_map(context.get("proof_bundle")).get("universe_contract_bundle_hash"))
    state["mod_policy_id"] = _token(_as_map(context.get("pack_lock")).get("mod_policy_id"))
    return state


def _strip_schema_unknown_top_level_fields(repo_root: str, payload: Mapping[str, object]) -> dict:
    current = copy.deepcopy(dict(payload or {}))
    for _ in range(8):
        report = validate_instance(repo_root=repo_root, schema_name="universe_state", payload=current, strict_top_level=True)
        if bool(report.get("valid", False)):
            return current
        unknown_fields = []
        for row in list(report.get("errors") or []):
            item = _as_map(row)
            if _token(item.get("code")) != "unknown_top_level_field":
                continue
            path = _token(item.get("path"))
            if not path.startswith("$.") or "." in path[2:]:
                continue
            unknown_fields.append(path[2:])
        unknown_fields = sorted(set(token for token in unknown_fields if _token(token)))
        if not unknown_fields:
            raise ValueError("universe_state schema validation failed")
        for field_name in unknown_fields:
            current.pop(str(field_name), None)
    raise ValueError("unable to normalize baseline save payload onto universe_state schema")


def _saveable_state(repo_root: str, working_state: Mapping[str, object], context: Mapping[str, object]) -> dict:
    payload = copy.deepcopy(dict(working_state or {}))
    for field_name in _TRANSIENT_STATE_FIELDS:
        payload.pop(field_name, None)
    payload = _strip_schema_unknown_top_level_fields(repo_root, payload)
    payload = _normalize_frozen_process_log_anchors(repo_root, payload)
    frozen_engine_version = _frozen_baseline_engine_version_created(repo_root)
    stamped = stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="save_file",
        payload=payload,
        semantic_contract_bundle_hash=_token(_as_map(context.get("proof_bundle")).get("universe_contract_bundle_hash")),
        engine_version_created=frozen_engine_version,
    )
    report = validate_instance(repo_root=repo_root, schema_name="universe_state", payload=stamped, strict_top_level=True)
    if not bool(report.get("valid", False)):
        raise ValueError("baseline save payload failed universe_state schema validation")
    return stamped


def _field_cells_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        [dict(row) for row in _as_list(_as_map(state).get("field_cells")) if isinstance(row, Mapping)],
        key=lambda row: (
            _token(row.get("field_id")),
            _token(row.get("cell_id")),
            canonical_sha256(_as_map(_as_map(row.get("extensions")).get("geo_cell_key"))),
        ),
    )
    return canonical_sha256(rows)


def _derived_view_hash_payload(state: Mapping[str, object]) -> dict:
    payload = _as_map(state)
    return {
        "field_cells_hash": _field_cells_hash(payload),
        "geometry_cell_state_hash_chain": _token(payload.get("geometry_cell_state_hash_chain")),
        "geometry_chunk_state_hash_chain": _token(payload.get("geometry_chunk_state_hash_chain")),
        "geometry_edit_event_hash_chain": _token(payload.get("geometry_edit_event_hash_chain")),
        "geometry_state_hash_chain": _token(payload.get("geometry_state_hash_chain")),
        "overlay_manifest_hash": _token(payload.get("overlay_manifest_hash")),
        "surface_tile_artifact_hash_chain": surface_tile_artifact_hash_chain(payload.get("worldgen_surface_tile_artifacts")),
    }


def _proof_anchor_row(
    *,
    checkpoint_id: str,
    anchor_label: str,
    state: Mapping[str, object],
    context: Mapping[str, object],
    reason: str,
    view_state: Mapping[str, object] | None = None,
) -> dict:
    state_payload = copy.deepcopy(dict(state or {}))
    proof_bundle = _as_map(context.get("proof_bundle"))
    pack_lock = _as_map(context.get("pack_lock"))
    tick = int(_as_map(state_payload.get("simulation_time")).get("tick", 0) or 0)
    truth_hash = canonical_sha256(state_payload)
    derived_view_hash_payload = _derived_view_hash_payload(view_state if isinstance(view_state, Mapping) else state_payload)
    epoch_anchor = build_epoch_anchor_record(
        tick=tick,
        truth_hash=truth_hash,
        contract_bundle_hash=_token(proof_bundle.get("universe_contract_bundle_hash")),
        pack_lock_hash=_token(pack_lock.get("pack_lock_hash")),
        overlay_manifest_hash=_token(state_payload.get("overlay_manifest_hash")),
        reason=reason,
        anchor_id="omega2.{}.{}".format(_token(checkpoint_id).lower(), canonical_sha256({"checkpoint_id": checkpoint_id, "anchor_label": anchor_label})[:12]),
        extensions={
            "checkpoint_id": _token(checkpoint_id),
            "anchor_label": _token(anchor_label),
        },
    )
    return {
        "checkpoint_id": _token(checkpoint_id),
        "anchor_label": _token(anchor_label),
        "simulation_tick": tick,
        "state_hash_anchor": truth_hash,
        "state_deterministic_fingerprint": _token(state_payload.get("deterministic_fingerprint")),
        "derived_view_hash": canonical_sha256(derived_view_hash_payload),
        "derived_view_hash_payload": derived_view_hash_payload,
        "epoch_anchor_id": _token(epoch_anchor.get("anchor_id")),
        "epoch_anchor_fingerprint": _token(epoch_anchor.get("deterministic_fingerprint")),
        "epoch_anchor": epoch_anchor,
    }


def _surface_request(context: Mapping[str, object]) -> dict:
    universe_identity = _as_map(context.get("universe_identity"))
    anchor_cell_key = resolve_sol_anchor_cell_key(None)
    sol_ids = sol_anchor_object_ids(universe_identity_hash=_token(universe_identity.get("identity_hash")))
    earth_planet_id = _token(sol_ids.get("sol.planet.earth"))
    surface_cell_key = build_planet_surface_cell_key(
        planet_object_id=earth_planet_id,
        ancestor_world_cell_key=anchor_cell_key,
        chart_id=BASELINE_SURFACE_CHART_ID,
        index_tuple=list(BASELINE_SURFACE_INDEX_TUPLE),
        refinement_level=BASELINE_SURFACE_REFINEMENT_LEVEL,
        planet_tags=list(BASELINE_PLANET_TAGS),
    )
    request = build_worldgen_request(
        request_id="omega2.baseline.l3",
        geo_cell_key=surface_cell_key,
        refinement_level=3,
        reason="query",
        extensions={"source": "omega.baseline_universe"},
    )
    return {
        "anchor_cell_key": anchor_cell_key,
        "earth_planet_id": earth_planet_id,
        "sol_ids": dict((str(key), str(value)) for key, value in sorted(sol_ids.items())),
        "surface_cell_key": surface_cell_key,
        "surface_request": request,
    }


def _run_worldgen_refinement(repo_root: str, context: Mapping[str, object], working_state: dict) -> dict:
    del repo_root
    law_profile = _baseline_law_profile()
    authority_context = _baseline_authority_context()
    policy_context = _baseline_policy_context(
        physics_profile_id=_token(_as_map(context.get("universe_identity")).get("physics_profile_id")),
        pack_lock_hash=_token(_as_map(context.get("pack_lock")).get("pack_lock_hash")),
    )
    anchor_cell_key = resolve_sol_anchor_cell_key(None)
    l2_request = build_worldgen_request(
        request_id="omega2.baseline.l2",
        geo_cell_key=anchor_cell_key,
        refinement_level=2,
        reason="query",
        extensions={"source": "omega.baseline_universe"},
    )
    l2_result = execute_intent(
        state=working_state,
        intent={"intent_id": "intent.omega2.baseline.l2", "process_id": "process.worldgen_request", "inputs": {"worldgen_request": l2_request}},
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices={},
        policy_context=policy_context,
    )
    if _token(l2_result.get("result")) != "complete":
        raise ValueError(_token(l2_result.get("message")) or "L2 baseline refinement refused")

    surface_plan = _surface_request(context)
    l3_result = execute_intent(
        state=working_state,
        intent={
            "intent_id": "intent.omega2.baseline.l3",
            "process_id": "process.worldgen_request",
            "inputs": {"worldgen_request": dict(surface_plan.get("surface_request") or {})},
        },
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices={},
        policy_context=policy_context,
    )
    if _token(l3_result.get("result")) != "complete":
        raise ValueError(_token(l3_result.get("message")) or "L3 baseline refinement refused")

    geometry_rows = [dict(row) for row in _as_list(working_state.get("geometry_cell_states")) if isinstance(row, Mapping)]
    if not geometry_rows:
        raise ValueError("baseline universe refinement did not materialize geometry")
    target_cell_key = dict(_as_map(geometry_rows[0].get("geo_cell_key")))

    return {
        "policy_context": policy_context,
        "l2_request": l2_request,
        "l2_result": dict(l2_result),
        "surface_plan": surface_plan,
        "l3_result": dict(l3_result),
        "target_cell_key": target_cell_key,
    }


def _run_baseline_terrain_edit(context: Mapping[str, object], working_state: dict, target_cell_key: Mapping[str, object]) -> dict:
    law_profile = _baseline_law_profile()
    authority_context = _baseline_authority_context()
    policy_context = _baseline_policy_context(
        physics_profile_id=_token(_as_map(context.get("universe_identity")).get("physics_profile_id")),
        pack_lock_hash=_token(_as_map(context.get("pack_lock")).get("pack_lock_hash")),
    )
    geometry_result = execute_intent(
        state=working_state,
        intent={
            "intent_id": "intent.omega2.baseline.geometry_remove",
            "process_id": "process.geometry_remove",
            "inputs": {
                "target_cell_keys": [dict(_as_map(target_cell_key))],
                "volume_amount": BASELINE_GEOMETRY_VOLUME,
            },
        },
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices={},
        policy_context=policy_context,
    )
    if _token(geometry_result.get("result")) != "complete":
        raise ValueError(_token(geometry_result.get("message")) or "baseline universe terrain edit refused")
    return dict(geometry_result)


def build_baseline_instance_manifest(repo_root: str, context: Mapping[str, object]) -> dict:
    universe_identity = _as_map(context.get("universe_identity"))
    pack_lock = _as_map(context.get("pack_lock"))
    proof_bundle = _as_map(context.get("proof_bundle"))
    install_profile = _as_map(context.get("install_profile"))
    manifest = normalize_instance_manifest(
        {
            "schema_version": "2.1.0",
            "instance_id": BASELINE_INSTANCE_ID,
            "instance_kind": "instance.tooling",
            "mode": "portable",
            "install_ref": {
                "install_id": BASELINE_INSTALL_ID,
                "manifest_ref": "",
                "root_path": ".",
            },
            "pack_lock_hash": _token(pack_lock.get("pack_lock_hash")),
            "profile_bundle_hash": _token(_as_map(context.get("profile_bundle")).get("profile_bundle_hash")),
            "mod_policy_id": _token(pack_lock.get("mod_policy_id")),
            "overlay_conflict_policy_id": _token(pack_lock.get("overlay_conflict_policy_id")),
            "default_session_template_id": BASELINE_SESSION_TEMPLATE_ID,
            "seed_policy": "fixed",
            "instance_settings": {
                "data_root": BASELINE_UNIVERSE_DIR_REL,
                "active_profiles": [
                    _token(universe_identity.get("physics_profile_id")),
                    _token(universe_identity.get("topology_profile_id")),
                    _token(universe_identity.get("metric_profile_id")),
                    _token(universe_identity.get("partition_profile_id")),
                    _token(universe_identity.get("projection_profile_id")),
                    _token(universe_identity.get("realism_profile_id")),
                ],
                "active_modpacks": [str(item) for item in list(pack_lock.get("ordered_pack_ids") or []) if _token(item)],
                "sandbox_policy_ref": "sandbox.default",
                "update_channel": "stable",
                "ui_mode_default": "cli",
                "allow_read_only_fallback": False,
                "tick_budget_policy_id": "tick.budget.default",
                "compute_profile_id": "compute.default",
                "extensions": {
                    SAVE_LAST_OPENED_KEY: BASELINE_SAVE_ID,
                },
            },
            "save_refs": [BASELINE_SAVE_ID],
            "required_product_builds": {},
            "required_contract_ranges": {},
            "resolution_policy_id": "",
            "provides_resolutions": [],
            "store_root": {
                "store_id": "store.default",
                "root_path": ".",
                "manifest_ref": "",
            },
            "embedded_artifacts": [],
            "extensions": {
                SAVE_LAST_OPENED_KEY: BASELINE_SAVE_ID,
                "official.install_profile_id": _token(install_profile.get("install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID,
                "official.requested_mod_policy_id": "mod_policy.strict",
                "official.trust_policy_id": DEFAULT_TRUST_POLICY_ID,
                "official.worldgen_lock_id": WORLDGEN_LOCK_ID,
                "official.worldgen_lock_version": WORLDGEN_LOCK_VERSION,
                "official.universe_id": _token(universe_identity.get("universe_id")),
                "official.universe_identity_hash": _token(universe_identity.get("identity_hash")),
                "official.semantic_contract_registry_hash": _token(proof_bundle.get("semantic_contract_registry_hash")),
                "official.universe_contract_bundle_hash": _token(proof_bundle.get("universe_contract_bundle_hash")),
                "official.save_artifact_rel": _norm(BASELINE_SAVE_REL),
                "official.pack_lock_rel": _norm(BASELINE_PACK_LOCK_REL),
                "official.profile_bundle_rel": _norm(BASELINE_PROFILE_BUNDLE_REL),
            },
        }
    )
    manifest["deterministic_fingerprint"] = instance_deterministic_fingerprint(manifest)
    manifest = attach_universal_identity_block(
        manifest,
        identity_kind_id=IDENTITY_KIND_INSTANCE,
        identity_id="identity.instance.{}".format(BASELINE_INSTANCE_ID),
        stability_class_id=BASELINE_STABILITY_CLASS,
        schema_version="2.1.0",
        contract_bundle_hash=_token(proof_bundle.get("universe_contract_bundle_hash")),
        extensions={"official.rel_path": _norm(BASELINE_INSTANCE_MANIFEST_REL)},
    )
    manifest["deterministic_fingerprint"] = instance_deterministic_fingerprint(manifest)
    validation = validate_instance_manifest(repo_root=repo_root, manifest_payload=manifest)
    if _token(validation.get("result")) != "complete":
        raise ValueError(_token(validation.get("message")) or "baseline instance manifest validation failed")
    return manifest


def _default_output_paths(repo_root: str, output_root_rel: str, write_outputs: bool) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    root_rel = _norm(output_root_rel) if _token(output_root_rel) else _norm(BASELINE_UNIVERSE_DIR_REL if write_outputs else DEFAULT_WORK_ROOT_REL)
    root_abs = _repo_abs(repo_root_abs, root_rel)
    return {
        "root_abs": root_abs,
        "instance_manifest_path": os.path.join(root_abs, os.path.basename(BASELINE_INSTANCE_MANIFEST_REL)),
        "pack_lock_path": os.path.join(root_abs, os.path.basename(BASELINE_PACK_LOCK_REL)),
        "profile_bundle_path": os.path.join(root_abs, os.path.basename(BASELINE_PROFILE_BUNDLE_REL)),
        "save_path": os.path.join(root_abs, os.path.basename(BASELINE_SAVE_REL)),
        "snapshot_path": os.path.join(root_abs, os.path.basename(BASELINE_SNAPSHOT_REL)),
    }


def generate_baseline_universe(
    repo_root: str,
    *,
    seed_text: str = "",
    output_root_rel: str = "",
    write_outputs: bool = True,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    resolved_seed = read_worldgen_baseline_seed(repo_root_abs, seed_text=seed_text)
    context = _baseline_context(repo_root_abs, resolved_seed)
    output_paths = _default_output_paths(repo_root_abs, output_root_rel, write_outputs)
    _ensure_dir(output_paths["root_abs"])

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
    geometry_result = _run_baseline_terrain_edit(context, working_state, _as_map(execution.get("target_cell_key")))
    t2_state = _saveable_state(repo_root_abs, working_state, context)
    t2_anchor = _proof_anchor_row(
        checkpoint_id="T2",
        anchor_label="after_first_terrain_edit",
        state=t2_state,
        context=context,
        reason=ANCHOR_REASON_INTERVAL,
        view_state=working_state,
    )

    save_payload = copy.deepcopy(t2_state)
    _write_canonical_json(output_paths["save_path"], save_payload)
    loaded_payload, loaded_meta, load_error = load_versioned_artifact(
        repo_root=repo_root_abs,
        artifact_kind="save_file",
        path=output_paths["save_path"],
        semantic_contract_bundle_hash=_token(_as_map(context.get("proof_bundle")).get("universe_contract_bundle_hash")),
        allow_read_only=False,
        strip_loaded_metadata=False,
    )
    if load_error:
        raise ValueError(_token(_as_map(load_error.get("refusal")).get("message")) or "baseline save reload failed")
    t3_anchor = _proof_anchor_row(
        checkpoint_id="T3",
        anchor_label="after_save_reload",
        state=loaded_payload,
        context=context,
        reason=ANCHOR_REASON_SAVE,
        view_state=loaded_payload,
    )

    instance_manifest = build_baseline_instance_manifest(repo_root_abs, context)
    pack_lock_payload = copy.deepcopy(_as_map(context.get("pack_lock")))
    profile_bundle_payload = copy.deepcopy(_as_map(context.get("profile_bundle")))
    if write_outputs:
        _write_canonical_json(output_paths["instance_manifest_path"], instance_manifest)
        _write_canonical_json(output_paths["pack_lock_path"], pack_lock_payload)
        _write_canonical_json(output_paths["profile_bundle_path"], profile_bundle_payload)

    time_anchor_policy = _as_map(context.get("time_anchor_policy"))
    install_profile = _as_map(context.get("install_profile"))
    proof_bundle = _as_map(context.get("proof_bundle"))
    universe_identity = _as_map(context.get("universe_identity"))
    geometry_result = _as_map(geometry_result)
    l2_result = _as_map(execution.get("l2_result"))
    l3_result = _as_map(execution.get("l3_result"))
    surface_plan = _as_map(execution.get("surface_plan"))
    proof_anchors = [t0_anchor, t1_anchor, t2_anchor, t3_anchor]
    official_save_rel = _norm(BASELINE_SAVE_REL)
    normalized_loaded_meta = _normalized_load_metadata(loaded_meta, repo_root=repo_root_abs, save_path=official_save_rel)
    snapshot_record = {
        "baseline_universe_version": BASELINE_UNIVERSE_VERSION,
        "stability_class": BASELINE_STABILITY_CLASS,
        "worldgen_lock_id": WORLDGEN_LOCK_ID,
        "worldgen_lock_version": WORLDGEN_LOCK_VERSION,
        "baseline_seed": resolved_seed,
        "baseline_seed_hash": seed_text_hash(resolved_seed),
        "universe_id": _token(universe_identity.get("universe_id")),
        "universe_identity_hash": _token(universe_identity.get("identity_hash")),
        "generator_version_id": _token(universe_identity.get("generator_version_id")),
        "realism_profile_id": _token(universe_identity.get("realism_profile_id")),
        "physics_profile_id": _token(universe_identity.get("physics_profile_id")),
        "semantic_contract_registry_hash": _token(proof_bundle.get("semantic_contract_registry_hash")),
        "universe_contract_bundle_hash": _token(proof_bundle.get("universe_contract_bundle_hash")),
        "profile_bundle_id": _token(profile_bundle_payload.get("profile_bundle_id")),
        "profile_bundle_hash": _token(profile_bundle_payload.get("profile_bundle_hash")),
        "pack_lock_id": _token(pack_lock_payload.get("pack_lock_id")),
        "pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
        "mod_policy_id": _token(pack_lock_payload.get("mod_policy_id")),
        "requested_mod_policy_id": "mod_policy.strict",
        "trust_policy_id": DEFAULT_TRUST_POLICY_ID,
        "install_profile_id": _token(install_profile.get("install_profile_id")) or DEFAULT_INSTALL_PROFILE_ID,
        "proof_anchor_schedule": {
            "time_anchor_policy_id": _token(time_anchor_policy.get("time_anchor_policy_id")) or "time.anchor.mvp_default",
            "checkpoint_interval_ticks": int(anchor_interval_ticks(time_anchor_policy)),
            "checkpoint_ids": [str(row.get("checkpoint_id", "")) for row in proof_anchors],
            "checkpoints_are_pre_simulation_tick": True,
        },
        "proof_anchors": proof_anchors,
        "derived_view_hashes": {
            "T1": _token(t1_anchor.get("derived_view_hash")),
            "T2": _token(t2_anchor.get("derived_view_hash")),
            "T3": _token(t3_anchor.get("derived_view_hash")),
        },
        "refinement": {
            "l2_anchor_cell_key": _as_map(surface_plan.get("anchor_cell_key")),
            "l2_request_id": _token(_as_map(execution.get("l2_request")).get("request_id")),
            "l2_result_id": _token(l2_result.get("result_id")),
            "l2_state_hash_anchor": _token(t1_anchor.get("state_hash_anchor")),
            "earth_planet_id": _token(surface_plan.get("earth_planet_id")),
            "surface_chart_id": BASELINE_SURFACE_CHART_ID,
            "surface_index_tuple": list(BASELINE_SURFACE_INDEX_TUPLE),
            "surface_cell_key": _as_map(surface_plan.get("surface_cell_key")),
            "surface_request_id": _token(_as_map(surface_plan.get("surface_request")).get("request_id")),
            "surface_result_id": _token(l3_result.get("result_id")),
            "surface_tile_object_id": _token(_as_map((_as_list(t1_state.get("worldgen_surface_tile_artifacts")) or [{}])[0]).get("tile_object_id")),
            "surface_tile_artifact_hash_chain": surface_tile_artifact_hash_chain(t1_state.get("worldgen_surface_tile_artifacts")),
        },
        "terrain_edit": {
            "process_id": "process.geometry_remove",
            "target_cell_key": _as_map(execution.get("target_cell_key")),
            "volume_amount": BASELINE_GEOMETRY_VOLUME,
            "edited_cell_count": int(geometry_result.get("edited_cell_count", 0) or 0),
            "volume_amount_applied": int(geometry_result.get("volume_amount_applied", 0) or 0),
            "material_out_batch_ids": [str(item) for item in list(geometry_result.get("material_out_batch_ids") or []) if _token(item)],
        },
        "save_artifact": {
            "save_id": BASELINE_SAVE_ID,
            "save_rel": official_save_rel,
            "save_file_hash": _token(save_payload.get("deterministic_fingerprint")),
            "loaded_save_hash": _token(_as_map(loaded_payload).get("deterministic_fingerprint")),
            "loaded_save_matches_pre_save_anchor": canonical_sha256(loaded_payload) == canonical_sha256(save_payload),
            "format_version": _token(_as_map(loaded_payload).get("format_version")),
            "engine_version_created": _token(_as_map(loaded_payload).get("engine_version_created")),
            "load_metadata": normalized_loaded_meta,
        },
        "instance_manifest_fingerprint": _token(instance_manifest.get("deterministic_fingerprint")),
        "instance_manifest_rel": _norm(BASELINE_INSTANCE_MANIFEST_REL),
        "pack_lock_rel": _norm(BASELINE_PACK_LOCK_REL),
        "profile_bundle_rel": _norm(BASELINE_PROFILE_BUNDLE_REL),
        "deterministic_fingerprint": "",
    }
    snapshot_record["deterministic_fingerprint"] = baseline_snapshot_record_hash(snapshot_record)
    snapshot_payload = {
        "schema_id": BASELINE_UNIVERSE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "record": snapshot_record,
    }
    if write_outputs:
        _write_canonical_json(output_paths["snapshot_path"], snapshot_payload)
    return {
        "result": "complete",
        "seed_text": resolved_seed,
        "context": context,
        "initial_state": initial_state,
        "save_payload": save_payload,
        "loaded_payload": loaded_payload,
        "instance_manifest": instance_manifest,
        "pack_lock_payload": pack_lock_payload,
        "profile_bundle_payload": profile_bundle_payload,
        "snapshot_payload": snapshot_payload,
        "output_paths": output_paths,
        "execution": execution,
    }


def verify_baseline_universe(
    repo_root: str,
    *,
    seed_text: str = "",
    snapshot_path: str = "",
    save_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    expected_snapshot = load_baseline_universe_snapshot(repo_root_abs, snapshot_path=snapshot_path)
    expected_record = _as_map(expected_snapshot.get("record"))
    observed = generate_baseline_universe(
        repo_root_abs,
        seed_text=seed_text,
        output_root_rel=DEFAULT_WORK_ROOT_REL,
        write_outputs=False,
    )
    observed_record = _as_map(_as_map(observed.get("snapshot_payload")).get("record"))
    committed_save_path = os.path.normpath(os.path.abspath(save_path)) if _token(save_path) else _repo_abs(repo_root_abs, BASELINE_SAVE_REL)
    loaded_save_payload, loaded_save_meta, loaded_save_error = load_versioned_artifact(
        repo_root=repo_root_abs,
        artifact_kind="save_file",
        path=committed_save_path,
        semantic_contract_bundle_hash=_token(_as_map(observed.get("context")).get("proof_bundle", {}).get("universe_contract_bundle_hash")),
        allow_read_only=False,
        strip_loaded_metadata=False,
    )
    mismatched_fields = _diff_values(expected_record, observed_record)
    expected_t2_hash = _token(_as_map((_as_list(expected_record.get("proof_anchors")) or [{}, {}, {}])[2]).get("state_hash_anchor"))
    save_reload_matches = not bool(loaded_save_error) and canonical_sha256(loaded_save_payload) == expected_t2_hash
    worldgen_record = _as_map(_as_map(_as_map(observed.get("context")).get("worldgen_lock_snapshot")).get("record"))
    expected_save_rel = _token(_as_map(expected_record.get("save_artifact")).get("save_rel"))
    actual_save_rel = _norm(os.path.relpath(committed_save_path, repo_root_abs)) if os.path.isfile(committed_save_path) else ""
    report = {
        "schema_id": BASELINE_UNIVERSE_VERIFY_SCHEMA_ID,
        "schema_version": "1.0.0",
        "result": "complete" if not mismatched_fields and save_reload_matches and not loaded_save_error else "violation",
        "matches_snapshot": not mismatched_fields,
        "save_reload_matches": bool(save_reload_matches),
        "seed_matches_worldgen_lock": _token(expected_record.get("baseline_seed")) == _token(worldgen_record.get("baseline_seed")),
        "pack_lock_matches_worldgen_lock": _token(expected_record.get("pack_lock_hash")) == _token(worldgen_record.get("pack_lock_hash")),
        "expected_snapshot_fingerprint": _token(expected_record.get("deterministic_fingerprint")),
        "observed_snapshot_fingerprint": _token(observed_record.get("deterministic_fingerprint")),
        "expected_save_rel": expected_save_rel,
        "actual_save_rel": actual_save_rel,
        "save_path_exists": os.path.isfile(committed_save_path),
        "loaded_save_error": dict(loaded_save_error or {}),
        "loaded_save_hash": _token(_as_map(loaded_save_payload).get("deterministic_fingerprint")),
        "loaded_save_metadata": dict(loaded_save_meta or {}),
        "mismatched_fields": mismatched_fields,
        "expected_record": expected_record,
        "observed_record": observed_record,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def write_baseline_universe_verify_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    json_path: str = "",
    doc_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    json_target = os.path.normpath(os.path.abspath(json_path)) if _token(json_path) else _repo_abs(repo_root_abs, BASELINE_VERIFY_JSON_REL)
    doc_target = os.path.normpath(os.path.abspath(doc_path)) if _token(doc_path) else _repo_abs(repo_root_abs, BASELINE_VERIFY_DOC_REL)
    _write_canonical_json(json_target, report)
    mismatches = [str(item) for item in list(_as_map(report).get("mismatched_fields") or []) if _token(item)]
    doc_lines = [
        "# Baseline Universe Verify",
        "",
        "- Result: `{}`".format("PASS" if bool(_as_map(report).get("matches_snapshot")) and bool(_as_map(report).get("save_reload_matches")) else "FAIL"),
        "- Matches Snapshot: `{}`".format(bool(_as_map(report).get("matches_snapshot"))),
        "- Save Reload Matches: `{}`".format(bool(_as_map(report).get("save_reload_matches"))),
        "- Seed Matches WORLDGEN-LOCK: `{}`".format(bool(_as_map(report).get("seed_matches_worldgen_lock"))),
        "- Pack Lock Matches WORLDGEN-LOCK: `{}`".format(bool(_as_map(report).get("pack_lock_matches_worldgen_lock"))),
        "- Expected Snapshot Fingerprint: `{}`".format(_token(_as_map(report).get("expected_snapshot_fingerprint"))),
        "- Observed Snapshot Fingerprint: `{}`".format(_token(_as_map(report).get("observed_snapshot_fingerprint"))),
        "- Expected Save Artifact: `{}`".format(_token(_as_map(report).get("expected_save_rel"))),
        "- Actual Save Artifact: `{}`".format(_token(_as_map(report).get("actual_save_rel"))),
        "- Loaded Save Hash: `{}`".format(_token(_as_map(report).get("loaded_save_hash"))),
        "",
        "## Mismatches",
    ]
    if mismatches:
        doc_lines.extend("- `{}`".format(item) for item in mismatches)
    else:
        doc_lines.append("- None")
    _write_text(doc_target, "\n".join(doc_lines) + "\n")
    return {
        "json_path": json_target,
        "doc_path": doc_target,
    }
