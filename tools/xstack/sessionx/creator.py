"""Deterministic out-of-game SessionSpec creator for v1 boot path wiring."""

from __future__ import annotations

import os
import copy
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.compatx.schema_registry import load_version_registry
from tools.xstack.pack_contrib.parser import parse_contributions
from tools.xstack.pack_loader.dependency_resolver import resolve_packs
from tools.xstack.pack_loader.loader import load_pack_set
from tools.xstack.registry_compile.bundle_profile import load_bundle_profile
from tools.xstack.registry_compile.compiler import compile_bundle
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID
from tools.xstack.registry_compile.bundle_profile import resolve_bundle_selection
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload
from worldgen.core.pipeline import run_worldgen_pipeline

from .common import (
    DEFAULT_COMPATIBILITY_VERSION,
    DEFAULT_TIMESTAMP_UTC,
    deterministic_seed_hex,
    identity_hash_for_payload,
    norm,
    read_json_object,
    refusal,
    write_canonical_json,
)
from .pipeline_contract import DEFAULT_PIPELINE_ID, load_session_pipeline_contract


DEFAULT_EXPERIENCE_ID = "profile.lab.developer"
DEFAULT_LAW_PROFILE_ID = "law.lab.unrestricted"
DEFAULT_PARAMETER_BUNDLE_ID = "params.lab.placeholder"
DEFAULT_BUDGET_POLICY_ID = "policy.budget.default_lab"
DEFAULT_FIDELITY_POLICY_ID = "policy.fidelity.default_lab"
DEFAULT_SCENARIO_ID = "scenario.lab.galaxy_nav"
DEFAULT_SCOPE_ID = "epistemic.lab.placeholder"
DEFAULT_VISIBILITY_LEVEL = "placeholder"
DEFAULT_PRIVILEGE_LEVEL = "operator"
DEFAULT_ENTITLEMENTS = (
    "session.boot",
    "entitlement.camera_control",
    "entitlement.teleport",
    "entitlement.time_control",
    "entitlement.inspect",
    "entitlement.control.camera",
    "entitlement.control.possess",
    "entitlement.control.lens_override",
    "lens.nondiegetic.access",
    "ui.window.lab.nav",
)
DEFAULT_PHYSICAL_CONSTANTS = {
    "gravitational_constant": 6.6743e-11,
    "speed_of_light_mps": 299792458.0,
}
DEFAULT_CAMERA_ASSEMBLY = {
    "assembly_id": "camera.main",
    "frame_id": "frame.world",
    "position_mm": {"x": 0, "y": 0, "z": 0},
    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
    "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
    "lens_id": "lens.diegetic.sensor",
}
DEFAULT_INSTRUMENT_ASSEMBLIES = [
    {
        "assembly_id": "instrument.clock",
        "instrument_type": "clock",
        "reading": {
            "tick": 0,
            "rate_permille": 1000,
            "paused": False,
        },
        "quality": "nominal",
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.compass",
        "instrument_type": "compass",
        "reading": {
            "heading_mdeg": 0,
        },
        "quality": "nominal",
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.altimeter",
        "instrument_type": "altimeter",
        "reading": {
            "altitude_mm": 0,
        },
        "quality": "nominal",
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.radio",
        "instrument_type": "radio",
        "reading": {
            "signal_quality_permille": 1000,
        },
        "quality": "nominal",
        "last_update_tick": 0,
    },
]
DEFAULT_WORLDGEN_MODULE_REGISTRY_REL = "data/registries/worldgen_module_registry.json"

REGISTRY_FILE_MAP = {
    "activation_policy_registry_hash": "activation_policy.registry.json",
    "budget_policy_registry_hash": "budget_policy.registry.json",
    "fidelity_policy_registry_hash": "fidelity_policy.registry.json",
    "worldgen_constraints_registry_hash": "worldgen_constraints.registry.json",
}


def _saves_root(repo_root: str, saves_root_rel: str) -> str:
    return os.path.join(repo_root, saves_root_rel.replace("/", os.sep))


def _save_dir(repo_root: str, save_id: str, saves_root_rel: str) -> str:
    return os.path.join(_saves_root(repo_root, saves_root_rel), str(save_id))


def _session_paths(repo_root: str, save_id: str, saves_root_rel: str) -> Dict[str, str]:
    root = _save_dir(repo_root, save_id, saves_root_rel)
    return {
        "save_dir": root,
        "session_spec_path": os.path.join(root, "session_spec.json"),
        "universe_identity_path": os.path.join(root, "universe_identity.json"),
        "universe_state_path": os.path.join(root, "universe_state.json"),
        "worldgen_search_plan_path": os.path.join(root, "worldgen_search_plan.json"),
    }


def _parse_rng_roots(explicit_roots: List[str], rng_seed_string: str) -> List[dict]:
    rows: List[dict] = []
    for raw in explicit_roots:
        token = str(raw).strip()
        if not token:
            continue
        if "=" not in token:
            continue
        stream_name, root_seed = token.split("=", 1)
        stream_token = str(stream_name).strip()
        root_token = str(root_seed).strip()
        if not stream_token or not root_token:
            continue
        rows.append({"stream_name": stream_token, "root_seed": root_token})
    if rows:
        return sorted(rows, key=lambda row: str(row.get("stream_name", "")))

    seed = str(rng_seed_string).strip()
    return [
        {
            "stream_name": "rng.session.core",
            "root_seed": deterministic_seed_hex(seed, "rng.session.core"),
        },
        {
            "stream_name": "rng.session.ui",
            "root_seed": deterministic_seed_hex(seed, "rng.session.ui"),
        },
    ]


def _parse_kv_rows(rows: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for raw in rows:
        token = str(raw).strip()
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        key_token = str(key).strip()
        value_token = str(value).strip()
        if key_token and value_token:
            out[key_token] = value_token
    return dict((key, out[key]) for key in sorted(out.keys()))


def _default_net_schema_versions(repo_root: str) -> Dict[str, str]:
    payload, error = load_version_registry(repo_root=repo_root)
    if error:
        return {}
    rows = (payload.get("schemas") or {}) if isinstance(payload, dict) else {}
    if not isinstance(rows, dict):
        return {}
    required = (
        "session_spec",
        "bundle_lockfile",
        "net_handshake",
        "net_proto_message",
        "net_intent_envelope",
    )
    out: Dict[str, str] = {}
    for schema_name in required:
        row = rows.get(schema_name)
        if not isinstance(row, dict):
            continue
        token = str(row.get("current_version", "")).strip()
        if token:
            out[str(schema_name)] = token
    return dict((key, out[key]) for key in sorted(out.keys()))


def _domain_bindings_from_registry(repo_root: str) -> List[str]:
    registry_path = os.path.join(repo_root, "build", "registries", "domain.registry.json")
    payload, err = read_json_object(registry_path)
    if err:
        return []
    rows = payload.get("domains")
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("domain_id", "")).strip()
        if token:
            out.append(token)
    return sorted(set(out))


def _load_worldgen_module_registry(repo_root: str) -> Tuple[dict, Dict[str, object]]:
    registry_path = os.path.join(repo_root, DEFAULT_WORLDGEN_MODULE_REGISTRY_REL.replace("/", os.sep))
    payload, err = read_json_object(registry_path)
    if err:
        return {}, refusal(
            "REFUSE_WORLDGEN_MODULE_REGISTRY_MISSING",
            "worldgen module registry is missing or invalid",
            "Provide a valid data/registries/worldgen_module_registry.json artifact.",
            {"registry_path": norm(DEFAULT_WORLDGEN_MODULE_REGISTRY_REL)},
            "$.worldgen.module_registry",
        )
    return payload, {}


def _resolve_constraints_file_from_registry(
    repo_root: str,
    constraints_registry_payload: dict,
    constraints_id: str,
) -> Tuple[str, Dict[str, object]]:
    constraints_rows = constraints_registry_payload.get("constraints")
    if not isinstance(constraints_rows, list):
        return "", refusal(
            "REFUSE_WORLDGEN_CONSTRAINTS_REGISTRY_INVALID",
            "worldgen constraints registry payload is missing constraints list",
            "Rebuild registries to produce a valid worldgen constraints registry.",
            {"registry_file": REGISTRY_FILE_MAP["worldgen_constraints_registry_hash"]},
            "$.constraints",
        )
    requested = str(constraints_id).strip()
    matches = []
    for row in sorted(
        [item for item in constraints_rows if isinstance(item, dict)],
        key=lambda item: (str(item.get("constraints_id", "")), str(item.get("pack_id", ""))),
    ):
        if str(row.get("constraints_id", "")).strip() == requested:
            matches.append(row)

    if not matches:
        return "", refusal(
            "REFUSE_WORLDGEN_CONSTRAINTS_NOT_REGISTERED",
            "constraints_id is not present in compiled worldgen constraints registry",
            "Install/select a bundle containing the requested worldgen constraints pack.",
            {"constraints_id": requested},
            "$.constraints_id",
        )
    if len(matches) > 1:
        return "", refusal(
            "REFUSE_WORLDGEN_CONSTRAINTS_AMBIGUOUS",
            "constraints_id resolved to multiple pack contributions",
            "Select a unique constraints_id or remove duplicate pack contributions.",
            {"constraints_id": requested},
            "$.constraints_id",
        )

    path_token = str(matches[0].get("path", "")).strip()
    if not path_token:
        return "", refusal(
            "REFUSE_WORLDGEN_CONSTRAINTS_PATH_MISSING",
            "compiled worldgen constraints registry entry is missing path",
            "Rebuild registries after fixing contribution path metadata.",
            {"constraints_id": requested},
            "$.constraints.path",
        )
    abs_path = os.path.normpath(os.path.join(repo_root, path_token.replace("/", os.sep)))
    if not os.path.isfile(abs_path):
        return "", refusal(
            "REFUSE_WORLDGEN_CONSTRAINTS_PATH_MISSING",
            "compiled worldgen constraints path is missing on disk",
            "Restore pack contribution file and rebuild registries.",
            {"constraints_id": requested, "constraints_path": norm(path_token)},
            "$.constraints.path",
        )
    return abs_path, {}


def _load_constraints_payload(
    repo_root: str,
    constraints_file: str,
    constraints_id: str,
    constraints_registry_payload: dict,
) -> Tuple[dict, Dict[str, object]]:
    requested_constraints_id = str(constraints_id).strip()
    resolved_registry_path = ""
    if requested_constraints_id:
        resolved_registry_path, registry_error = _resolve_constraints_file_from_registry(
            repo_root=repo_root,
            constraints_registry_payload=constraints_registry_payload,
            constraints_id=requested_constraints_id,
        )
        if registry_error:
            return {}, registry_error

    file_token = str(constraints_file).strip()
    if file_token:
        abs_path = os.path.normpath(
            os.path.abspath(file_token if os.path.isabs(file_token) else os.path.join(repo_root, file_token))
        )
    else:
        abs_path = resolved_registry_path

    payload, err = read_json_object(abs_path)
    if err:
        return {}, refusal(
            "REFUSE_CONSTRAINTS_INVALID_JSON",
            "worldgen constraints file is missing or invalid JSON",
            "Fix constraints artifact and retry session creation.",
            {"constraints_file": norm(abs_path)},
            "$.worldgen.constraints",
        )
    schema_result = validate_instance(
        repo_root=repo_root,
        schema_name="worldgen_constraints",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(schema_result.get("valid", False)):
        return {}, refusal(
            "REFUSE_CONSTRAINTS_SCHEMA_INVALID",
            "worldgen constraints payload failed schema validation",
            "Fix constraints fields to satisfy schemas/worldgen_constraints.schema.json.",
            {"constraints_file": norm(abs_path)},
            "$.worldgen.constraints",
        )
    payload_constraints_id = str(payload.get("constraints_id", "")).strip()
    if requested_constraints_id and requested_constraints_id != payload_constraints_id:
        return {}, refusal(
            "REFUSE_CONSTRAINTS_ID_MISMATCH",
            "constraints_id does not match constraints file payload",
            "Use matching constraints_id and constraints file payload.",
            {
                "requested_constraints_id": requested_constraints_id,
                "payload_constraints_id": payload_constraints_id,
            },
            "$.constraints_id",
        )
    return payload, {}


def _load_and_validate_lockfile(repo_root: str, bundle_id: str) -> Tuple[dict, Dict[str, object]]:
    lock_path = os.path.join(repo_root, "build", "lockfile.json")
    payload, err = read_json_object(lock_path)
    if err:
        return {}, refusal(
            "REFUSE_LOCKFILE_MISSING",
            "build/lockfile.json is missing or invalid",
            "Run tools/xstack/lockfile_build --bundle {} --out build/lockfile.json.".format(str(bundle_id)),
            {"lockfile_path": "build/lockfile.json", "bundle_id": str(bundle_id)},
            "$.lockfile",
        )

    schema_result = validate_instance(
        repo_root=repo_root,
        schema_name="bundle_lockfile",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(schema_result.get("valid", False)):
        return {}, refusal(
            "REFUSE_LOCKFILE_SCHEMA_INVALID",
            "build/lockfile.json failed schema validation",
            "Rebuild the lockfile with tools/xstack/lockfile_build and retry.",
            {"lockfile_path": "build/lockfile.json"},
            "$.lockfile",
        )

    semantic = validate_lockfile_payload(payload)
    if semantic.get("result") != "complete":
        return {}, refusal(
            "REFUSE_LOCKFILE_HASH_INVALID",
            "build/lockfile.json failed deterministic hash validation",
            "Rebuild lockfile and ensure no manual edits were applied.",
            {"lockfile_path": "build/lockfile.json"},
            "$.pack_lock_hash",
        )
    return payload, {}


def _load_registry_payload(repo_root: str, file_name: str, expected_hash: str) -> Tuple[dict, Dict[str, object]]:
    registry_path = os.path.join(repo_root, "build", "registries", file_name)
    payload, err = read_json_object(registry_path)
    if err:
        return {}, refusal(
            "REFUSE_REGISTRY_MISSING",
            "required registry '{}' is missing or invalid".format(file_name),
            "Compile registries and retry session creation.",
            {"registry_file": file_name},
            "$.registries",
        )
    actual_hash = str(payload.get("registry_hash", "")).strip() or canonical_sha256(payload)
    if str(expected_hash).strip() != actual_hash:
        return {}, refusal(
            "REFUSE_REGISTRY_HASH_MISMATCH",
            "registry hash mismatch for '{}'".format(file_name),
            "Rebuild lockfile and registries from identical bundle inputs.",
            {"registry_file": file_name},
            "$.registries",
        )
    return payload, {}


def _select_policy_entry(registry_payload: dict, key: str, policy_id: str, refusal_code: str, file_name: str) -> Tuple[dict, Dict[str, object]]:
    rows = registry_payload.get(key)
    if not isinstance(rows, list):
        return {}, refusal(
            refusal_code,
            "policy registry '{}' is missing key '{}'".format(file_name, key),
            "Rebuild registries and retry session creation.",
            {"registry_file": file_name},
            "$.{}".format(key),
        )
    for row in sorted(rows, key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
            return dict(row), {}
    return {}, refusal(
        refusal_code,
        "policy '{}' is not present in '{}'".format(str(policy_id), file_name),
        "Select a policy ID listed in '{}'.".format(file_name),
        {"policy_id": str(policy_id)},
        "$.policy_id",
    )


def _universe_identity_from_seed(seed_text: str, scenario_id: str, base_domain_bindings: List[str]) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "global_seed": str(seed_text),
        "physical_constants": dict(DEFAULT_PHYSICAL_CONSTANTS),
        "base_domain_bindings": list(base_domain_bindings),
        "initial_scenario_id": str(scenario_id),
        "compatibility_version": DEFAULT_COMPATIBILITY_VERSION,
        "identity_hash": "",
    }
    payload["identity_hash"] = identity_hash_for_payload(payload)
    return payload


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _camera_from_payload(payload: dict) -> dict:
    camera_block = payload.get("camera")
    source = camera_block if isinstance(camera_block, dict) else payload
    position = source.get("position_mm") if isinstance(source, dict) else {}
    orientation = source.get("orientation_mdeg") if isinstance(source, dict) else {}
    velocity = source.get("velocity_mm_per_tick") if isinstance(source, dict) else {}
    return {
        "assembly_id": str((source.get("assembly_id") if isinstance(source, dict) else "") or "camera.main"),
        "frame_id": str((source.get("frame_id") if isinstance(source, dict) else "") or "frame.world"),
        "position_mm": {
            "x": _as_int((position or {}).get("x", 0), 0),
            "y": _as_int((position or {}).get("y", 0), 0),
            "z": _as_int((position or {}).get("z", 0), 0),
        },
        "orientation_mdeg": {
            "yaw": _as_int((orientation or {}).get("yaw", 0), 0),
            "pitch": _as_int((orientation or {}).get("pitch", 0), 0),
            "roll": _as_int((orientation or {}).get("roll", 0), 0),
        },
        "velocity_mm_per_tick": {
            "x": _as_int((velocity or {}).get("x", 0), 0),
            "y": _as_int((velocity or {}).get("y", 0), 0),
            "z": _as_int((velocity or {}).get("z", 0), 0),
        },
        "lens_id": str((source.get("lens_id") if isinstance(source, dict) else "") or "lens.diegetic.sensor"),
    }


def _instrument_assemblies_from_payload(payload: dict) -> List[dict]:
    rows = payload.get("instrument_assemblies")
    if not isinstance(rows, list):
        return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)
    out: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
        assembly_id = str(row.get("assembly_id", "")).strip()
        instrument_type = str(row.get("instrument_type", "")).strip()
        if not assembly_id or not instrument_type:
            continue
        out.append(
            {
                "assembly_id": assembly_id,
                "instrument_type": instrument_type,
                "reading": copy.deepcopy(row.get("reading") if isinstance(row.get("reading"), dict) else {}),
                "quality": str(row.get("quality", "nominal")),
                "last_update_tick": _as_int(row.get("last_update_tick", 0), 0),
            }
        )
    if not out:
        return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)
    return out


def _camera_seed_from_bundle(repo_root: str, bundle_id: str) -> dict:
    loaded = load_pack_set(repo_root=repo_root, packs_root_rel="packs", schema_repo_root=repo_root)
    if loaded.get("result") != "complete":
        return copy.deepcopy(DEFAULT_CAMERA_ASSEMBLY)

    selected = resolve_bundle_selection(
        bundle_id=str(bundle_id),
        packs=loaded.get("packs") or [],
        repo_root=repo_root,
        schema_repo_root=repo_root,
    )
    if selected.get("result") != "complete":
        return copy.deepcopy(DEFAULT_CAMERA_ASSEMBLY)

    resolved = resolve_packs(loaded.get("packs") or [], bundle_selection=list(selected.get("selected_pack_ids") or []))
    if resolved.get("result") != "complete":
        return copy.deepcopy(DEFAULT_CAMERA_ASSEMBLY)

    contrib = parse_contributions(repo_root=repo_root, packs=list(resolved.get("ordered_pack_list") or []))
    if contrib.get("result") != "complete":
        return copy.deepcopy(DEFAULT_CAMERA_ASSEMBLY)

    for row in contrib.get("contributions") or []:
        if str(row.get("contrib_type", "")) != "registry_entries":
            continue
        if str(row.get("id", "")) != "registry.camera.assembly.main":
            continue
        payload = row.get("payload")
        if isinstance(payload, dict):
            return _camera_from_payload(payload)
    return copy.deepcopy(DEFAULT_CAMERA_ASSEMBLY)


def _instrument_seed_from_bundle(repo_root: str, bundle_id: str) -> List[dict]:
    loaded = load_pack_set(repo_root=repo_root, packs_root_rel="packs", schema_repo_root=repo_root)
    if loaded.get("result") != "complete":
        return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)

    selected = resolve_bundle_selection(
        bundle_id=str(bundle_id),
        packs=loaded.get("packs") or [],
        repo_root=repo_root,
        schema_repo_root=repo_root,
    )
    if selected.get("result") != "complete":
        return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)

    resolved = resolve_packs(loaded.get("packs") or [], bundle_selection=list(selected.get("selected_pack_ids") or []))
    if resolved.get("result") != "complete":
        return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)

    contrib = parse_contributions(repo_root=repo_root, packs=list(resolved.get("ordered_pack_list") or []))
    if contrib.get("result") != "complete":
        return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)

    for row in contrib.get("contributions") or []:
        if str(row.get("contrib_type", "")) != "registry_entries":
            continue
        if str(row.get("id", "")) != "registry.instrument.assemblies":
            continue
        payload = row.get("payload")
        if isinstance(payload, dict):
            return _instrument_assemblies_from_payload(payload)
    return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)


def _validate_universe_identity(repo_root: str, payload: dict) -> Dict[str, object]:
    valid = validate_instance(repo_root=repo_root, schema_name="universe_identity", payload=payload, strict_top_level=True)
    if not bool(valid.get("valid", False)):
        return refusal(
            "REFUSE_UNIVERSE_IDENTITY_INVALID",
            "UniverseIdentity payload failed schema validation",
            "Fix universe identity fields to match schemas/universe_identity.schema.json.",
            {"schema_id": "universe_identity"},
            "$.universe_identity",
        )
    expected = identity_hash_for_payload(payload)
    if str(payload.get("identity_hash", "")).strip() != expected:
        return refusal(
            "REFUSE_UNIVERSE_IDENTITY_MUTATION",
            "UniverseIdentity identity_hash does not match canonical payload hash",
            "Regenerate universe_identity.json using tools/xstack/session_create.",
            {"schema_id": "universe_identity"},
            "$.identity_hash",
        )
    return {"result": "complete"}


def _initial_universe_state(
    save_id: str,
    law_profile_id: str,
    camera_assembly: dict,
    instrument_assemblies: List[dict],
    budget_policy_id: str,
    fidelity_policy_id: str,
    activation_policy_id: str,
    max_compute_units_per_tick: int,
) -> dict:
    camera_payload = _camera_from_payload(camera_assembly if isinstance(camera_assembly, dict) else {})
    instrument_rows = [
        {
            "assembly_id": str(row.get("assembly_id", "")),
            "instrument_type": str(row.get("instrument_type", "")),
            "reading": copy.deepcopy(row.get("reading") if isinstance(row.get("reading"), dict) else {}),
            "quality": str(row.get("quality", "nominal")),
            "last_update_tick": _as_int(row.get("last_update_tick", 0), 0),
        }
        for row in sorted((item for item in (instrument_assemblies or []) if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", "")))
        if str(row.get("assembly_id", "")).strip() and str(row.get("instrument_type", "")).strip()
    ]
    world_assemblies = [str(camera_payload.get("assembly_id", "camera.main"))]
    world_assemblies.extend(str(row.get("assembly_id", "")) for row in instrument_rows if str(row.get("assembly_id", "")).strip())
    world_assemblies = sorted(set(world_assemblies))
    return {
        "schema_version": "1.0.0",
        "simulation_time": {
            "tick": 0,
            "timestamp_utc": DEFAULT_TIMESTAMP_UTC,
        },
        "agent_states": [],
        "world_assemblies": world_assemblies,
        "active_law_references": [str(law_profile_id)],
        "session_references": ["session.{}".format(str(save_id))],
        "history_anchors": ["history.anchor.tick.0"],
        "camera_assemblies": [camera_payload],
        "instrument_assemblies": instrument_rows,
        "controller_assemblies": [],
        "control_bindings": [],
        "time_control": {
            "rate_permille": 1000,
            "paused": False,
            "accumulator_permille": 0,
        },
        "process_log": [],
        "interest_regions": [],
        "macro_capsules": [],
        "micro_regions": [],
        "performance_state": {
            "budget_policy_id": str(budget_policy_id),
            "fidelity_policy_id": str(fidelity_policy_id),
            "activation_policy_id": str(activation_policy_id),
            "compute_units_used": 0,
            "max_compute_units_per_tick": max(0, _as_int(max_compute_units_per_tick, 0)),
            "budget_outcome": "ok",
            "active_region_count": 0,
            "fidelity_tier_counts": {
                "coarse": 0,
                "medium": 0,
                "fine": 0
            },
            "transition_log": []
        },
    }


def create_session_spec(
    repo_root: str,
    save_id: str,
    bundle_id: str = DEFAULT_BUNDLE_ID,
    scenario_id: str = DEFAULT_SCENARIO_ID,
    mission_id: str = "",
    experience_id: str = DEFAULT_EXPERIENCE_ID,
    law_profile_id: str = DEFAULT_LAW_PROFILE_ID,
    parameter_bundle_id: str = DEFAULT_PARAMETER_BUNDLE_ID,
    budget_policy_id: str = DEFAULT_BUDGET_POLICY_ID,
    fidelity_policy_id: str = DEFAULT_FIDELITY_POLICY_ID,
    constraints_id: str = "",
    constraints_file: str = "",
    pipeline_id: str = DEFAULT_PIPELINE_ID,
    rng_seed_string: str = "seed.session.default",
    rng_roots: List[str] | None = None,
    universe_identity_path: str = "",
    universe_seed_string: str = "seed.universe.default",
    universe_id: str = "",
    entitlements: List[str] | None = None,
    epistemic_scope_id: str = DEFAULT_SCOPE_ID,
    visibility_level: str = DEFAULT_VISIBILITY_LEVEL,
    privilege_level: str = DEFAULT_PRIVILEGE_LEVEL,
    net_endpoint: str = "",
    net_transport_id: str = "",
    net_client_peer_id: str = "",
    net_server_peer_id: str = "",
    net_replication_policy_id: str = "",
    net_anti_cheat_policy_id: str = "",
    net_server_profile_id: str = "",
    net_server_policy_id: str = "",
    net_securex_policy_id: str = "",
    net_desired_law_profile_id: str = "",
    net_schema_versions: List[str] | None = None,
    compile_outputs: bool = True,
    saves_root_rel: str = "saves",
) -> Dict[str, object]:
    save_token = str(save_id).strip()
    if not save_token:
        return refusal(
            "REFUSE_SAVE_ID_MISSING",
            "save_id is required",
            "Provide a non-empty --save-id value.",
            {"field": "save_id"},
            "$.save_id",
        )

    bundle_profile = load_bundle_profile(repo_root=repo_root, bundle_id=str(bundle_id), schema_repo_root=repo_root)
    if bundle_profile.get("result") != "complete":
        return refusal(
            "REFUSE_BUNDLE_INVALID",
            "bundle validation failed for '{}'".format(str(bundle_id)),
            "Validate bundle using tools/xstack/bundle_validate and retry.",
            {"bundle_id": str(bundle_id)},
            "$.bundle_id",
        )

    network_payload: dict = {}
    network_endpoint = str(net_endpoint).strip()
    if network_endpoint:
        schema_versions = _parse_kv_rows(list(net_schema_versions or []))
        if not schema_versions:
            schema_versions = _default_net_schema_versions(repo_root=repo_root)
        required_network = {
            "transport_id": str(net_transport_id).strip(),
            "client_peer_id": str(net_client_peer_id).strip(),
            "server_peer_id": str(net_server_peer_id).strip(),
            "requested_replication_policy_id": str(net_replication_policy_id).strip(),
            "anti_cheat_policy_id": str(net_anti_cheat_policy_id).strip(),
        }
        for field, value in sorted(required_network.items(), key=lambda item: item[0]):
            if not value:
                return refusal(
                    "REFUSE_NET_CONFIG_INVALID",
                    "network field '{}' is required when --net-endpoint is provided".format(field),
                    "Provide --{} explicitly for multiplayer session creation.".format(field.replace("_", "-")),
                    {"field": field},
                    "$.network.{}".format(field),
                )
        if not schema_versions:
            return refusal(
                "REFUSE_NET_CONFIG_INVALID",
                "network schema_versions could not be resolved",
                "Provide --net-schema-version values explicitly or restore compatx version registry.",
                {"field": "schema_versions"},
                "$.network.schema_versions",
            )
        server_profile_id = str(net_server_profile_id).strip()
        server_policy_id = str(net_server_policy_id).strip()
        if (not server_profile_id) and (not server_policy_id):
            return refusal(
                "REFUSE_NET_CONFIG_INVALID",
                "network requires server_profile_id or legacy server_policy_id",
                "Provide --net-server-profile-id (preferred) or --net-server-policy-id.",
                {"field": "server_profile_id"},
                "$.network",
            )
        network_payload = {
            "endpoint": network_endpoint,
            "transport_id": required_network["transport_id"],
            "client_peer_id": required_network["client_peer_id"],
            "server_peer_id": required_network["server_peer_id"],
            "requested_replication_policy_id": required_network["requested_replication_policy_id"],
            "anti_cheat_policy_id": required_network["anti_cheat_policy_id"],
            "server_profile_id": server_profile_id,
            "server_policy_id": server_policy_id,
            "desired_law_profile_id": str(net_desired_law_profile_id).strip() or None,
            "securex_policy_id": str(net_securex_policy_id).strip(),
            "schema_versions": schema_versions,
        }

    requested_pipeline_id = str(pipeline_id).strip() or DEFAULT_PIPELINE_ID
    selected_pipeline_id = requested_pipeline_id
    if network_payload and requested_pipeline_id == DEFAULT_PIPELINE_ID:
        selected_pipeline_id = "pipeline.client.multiplayer_stub"
    pipeline_contract = load_session_pipeline_contract(
        repo_root=repo_root,
        pipeline_id=selected_pipeline_id,
    )
    if pipeline_contract.get("result") != "complete":
        return pipeline_contract
    stage_order = list(pipeline_contract.get("stage_order") or [])
    has_net_stage = "stage.net_handshake" in stage_order
    if network_payload and not has_net_stage:
        return refusal(
            "REFUSE_NET_CONFIG_INVALID",
            "selected pipeline does not include required net handshake stage",
            "Use pipeline.client.multiplayer_stub when network endpoint is configured.",
            {"pipeline_id": selected_pipeline_id},
            "$.pipeline_id",
        )
    if (not network_payload) and has_net_stage:
        return refusal(
            "REFUSE_NET_CONFIG_INVALID",
            "selected pipeline requires network payload but session create request did not provide one",
            "Set --net-endpoint and required net fields, or select pipeline.client.default.",
            {"pipeline_id": selected_pipeline_id},
            "$.pipeline_id",
        )

    compile_result = {}
    if compile_outputs:
        compile_result = compile_bundle(
            repo_root=repo_root,
            bundle_id=str(bundle_id),
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            use_cache=False,
        )
        if compile_result.get("result") != "complete":
            return refusal(
                "REFUSE_BUNDLE_COMPILE_FAILED",
                "failed to compile registries/lockfile for bundle '{}'".format(str(bundle_id)),
                "Run tools/xstack/lockfile_build --bundle {} and resolve refusal details.".format(str(bundle_id)),
                {"bundle_id": str(bundle_id)},
                "$.bundle_id",
            )

    lockfile_payload, lockfile_error = _load_and_validate_lockfile(repo_root, bundle_id=str(bundle_id))
    if lockfile_error:
        return lockfile_error
    if str(lockfile_payload.get("bundle_id", "")).strip() != str(bundle_id).strip():
        return refusal(
            "REFUSE_LOCKFILE_BUNDLE_MISMATCH",
            "lockfile bundle_id does not match requested bundle_id",
            "Rebuild lockfile with --bundle {}.".format(str(bundle_id)),
            {
                "bundle_id": str(bundle_id),
                "lockfile_bundle_id": str(lockfile_payload.get("bundle_id", "")),
            },
            "$.bundle_id",
        )

    if universe_identity_path:
        identity_abs = os.path.normpath(os.path.abspath(universe_identity_path))
        identity_payload, identity_err = read_json_object(identity_abs)
        if identity_err:
            return refusal(
                "REFUSE_UNIVERSE_IDENTITY_LOAD_FAILED",
                "unable to load universe identity file",
                "Provide a valid --universe-identity-file path.",
                {"universe_identity_path": norm(identity_abs)},
                "$.universe_identity",
            )
    else:
        domain_bindings = _domain_bindings_from_registry(repo_root)
        if not domain_bindings:
            domain_bindings = ["domain.navigation"]
        identity_payload = _universe_identity_from_seed(
            seed_text=str(universe_seed_string),
            scenario_id=str(scenario_id),
            base_domain_bindings=domain_bindings,
        )
        identity_abs = ""

    identity_check = _validate_universe_identity(repo_root=repo_root, payload=identity_payload)
    if identity_check.get("result") != "complete":
        return identity_check

    calculated_universe_id = str(universe_id).strip() or "universe.{}".format(str(identity_payload.get("identity_hash", ""))[:16])
    entitlement_rows = sorted(set(str(item).strip() for item in (entitlements or DEFAULT_ENTITLEMENTS) if str(item).strip()))
    if not entitlement_rows:
        return refusal(
            "REFUSE_ENTITLEMENTS_EMPTY",
            "entitlements must contain at least one value",
            "Provide --entitlement values explicitly.",
            {"field": "entitlements"},
            "$.authority_context.entitlements",
        )

    rng_rows = _parse_rng_roots(explicit_roots=list(rng_roots or []), rng_seed_string=str(rng_seed_string))
    if not rng_rows:
        return refusal(
            "REFUSE_RNG_ROOTS_EMPTY",
            "deterministic_rng_roots cannot be empty",
            "Provide --rng-root values or --rng-seed-string.",
            {"field": "deterministic_rng_roots"},
            "$.deterministic_rng_roots",
        )

    selected_seed = str(identity_payload.get("global_seed", ""))
    search_plan_payload = {}
    selected_constraints_id = str(constraints_id).strip()

    registries = lockfile_payload.get("registries")
    if not isinstance(registries, dict):
        return refusal(
            "REFUSE_LOCKFILE_REGISTRY_SECTION_MISSING",
            "lockfile registries section is missing",
            "Rebuild lockfile and retry session creation.",
            {"bundle_id": str(bundle_id)},
            "$.registries",
        )
    budget_registry, budget_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["budget_policy_registry_hash"],
        expected_hash=str(registries.get("budget_policy_registry_hash", "")),
    )
    if budget_registry_error:
        return budget_registry_error
    fidelity_registry, fidelity_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["fidelity_policy_registry_hash"],
        expected_hash=str(registries.get("fidelity_policy_registry_hash", "")),
    )
    if fidelity_registry_error:
        return fidelity_registry_error
    activation_registry, activation_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["activation_policy_registry_hash"],
        expected_hash=str(registries.get("activation_policy_registry_hash", "")),
    )
    if activation_registry_error:
        return activation_registry_error
    worldgen_constraints_registry, worldgen_constraints_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["worldgen_constraints_registry_hash"],
        expected_hash=str(registries.get("worldgen_constraints_registry_hash", "")),
    )
    if worldgen_constraints_registry_error:
        return worldgen_constraints_registry_error

    if selected_constraints_id:
        module_registry_payload, module_registry_error = _load_worldgen_module_registry(repo_root=repo_root)
        if module_registry_error:
            return module_registry_error
        constraints_payload, constraints_error = _load_constraints_payload(
            repo_root=repo_root,
            constraints_file=str(constraints_file),
            constraints_id=selected_constraints_id,
            constraints_registry_payload=worldgen_constraints_registry,
        )
        if constraints_error:
            return constraints_error
        pipeline_result = run_worldgen_pipeline(
            repo_root=repo_root,
            base_seed=str(identity_payload.get("global_seed", "")),
            module_registry_payload=module_registry_payload,
            constraints_payload=constraints_payload,
        )
        if pipeline_result.get("result") != "complete":
            return pipeline_result
        search_plan_payload = dict(pipeline_result.get("search_plan") or {})
        selected_seed = str(pipeline_result.get("selected_seed", "")).strip() or selected_seed

    budget_policy, budget_policy_error = _select_policy_entry(
        registry_payload=budget_registry,
        key="budget_policies",
        policy_id=str(budget_policy_id),
        refusal_code="BUDGET_POLICY_NOT_FOUND",
        file_name=REGISTRY_FILE_MAP["budget_policy_registry_hash"],
    )
    if budget_policy_error:
        return budget_policy_error
    fidelity_policy, fidelity_policy_error = _select_policy_entry(
        registry_payload=fidelity_registry,
        key="fidelity_policies",
        policy_id=str(fidelity_policy_id),
        refusal_code="FIDELITY_POLICY_NOT_FOUND",
        file_name=REGISTRY_FILE_MAP["fidelity_policy_registry_hash"],
    )
    if fidelity_policy_error:
        return fidelity_policy_error
    activation_policy_id = str(budget_policy.get("activation_policy_id", "")).strip()
    activation_policy, activation_policy_error = _select_policy_entry(
        registry_payload=activation_registry,
        key="activation_policies",
        policy_id=activation_policy_id,
        refusal_code="ACTIVATION_POLICY_NOT_FOUND",
        file_name=REGISTRY_FILE_MAP["activation_policy_registry_hash"],
    )
    if activation_policy_error:
        return activation_policy_error

    session_payload = {
        "schema_version": "1.0.0",
        "universe_id": calculated_universe_id,
        "save_id": save_token,
        "bundle_id": str(bundle_id),
        "pipeline_id": selected_pipeline_id,
        "scenario_id": str(scenario_id),
        "mission_id": None if str(mission_id).strip() in ("", "null", "None") else str(mission_id),
        "experience_id": str(experience_id),
        "parameter_bundle_id": str(parameter_bundle_id),
        "authority_context": {
            "authority_origin": "client",
            "experience_id": str(experience_id),
            "law_profile_id": str(law_profile_id),
            "entitlements": entitlement_rows,
            "epistemic_scope": {
                "scope_id": str(epistemic_scope_id),
                "visibility_level": str(visibility_level),
            },
            "privilege_level": str(privilege_level),
        },
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "budget_policy_id": str(budget_policy_id),
        "fidelity_policy_id": str(fidelity_policy_id),
        "selected_seed": str(selected_seed),
        "deterministic_rng_roots": rng_rows,
    }
    if network_payload:
        session_payload["network"] = dict(network_payload)
    if search_plan_payload:
        session_payload["constraints_id"] = str(search_plan_payload.get("constraints_id", "")).strip() or selected_constraints_id
        session_payload["search_plan_hash"] = str(search_plan_payload.get("deterministic_hash", "")).strip()

    session_valid = validate_instance(repo_root=repo_root, schema_name="session_spec", payload=session_payload, strict_top_level=True)
    if not bool(session_valid.get("valid", False)):
        return refusal(
            "REFUSE_SESSION_SPEC_INVALID",
            "generated SessionSpec failed schema validation",
            "Review session creator arguments and schema constraints.",
            {"schema_id": "session_spec"},
            "$.session_spec",
        )

    camera_assembly = _camera_seed_from_bundle(repo_root=repo_root, bundle_id=str(bundle_id))
    instrument_assemblies = _instrument_seed_from_bundle(repo_root=repo_root, bundle_id=str(bundle_id))
    state_payload = _initial_universe_state(
        save_id=save_token,
        law_profile_id=str(law_profile_id),
        camera_assembly=camera_assembly,
        instrument_assemblies=instrument_assemblies,
        budget_policy_id=str(budget_policy.get("policy_id", "")),
        fidelity_policy_id=str(fidelity_policy.get("policy_id", "")),
        activation_policy_id=str(activation_policy.get("policy_id", "")),
        max_compute_units_per_tick=int(budget_policy.get("max_compute_units_per_tick", 0) or 0),
    )
    state_valid = validate_instance(repo_root=repo_root, schema_name="universe_state", payload=state_payload, strict_top_level=True)
    if not bool(state_valid.get("valid", False)):
        return refusal(
            "REFUSE_UNIVERSE_STATE_INVALID",
            "generated UniverseState failed schema validation",
            "Review generated initial state fields against schemas/universe_state.schema.json.",
            {"schema_id": "universe_state"},
            "$.universe_state",
        )

    paths = _session_paths(repo_root=repo_root, save_id=save_token, saves_root_rel=saves_root_rel)
    write_canonical_json(paths["session_spec_path"], session_payload)
    write_canonical_json(paths["universe_identity_path"], identity_payload)
    write_canonical_json(paths["universe_state_path"], state_payload)
    if search_plan_payload:
        write_canonical_json(paths["worldgen_search_plan_path"], search_plan_payload)

    return {
        "result": "complete",
        "save_id": save_token,
        "bundle_id": str(bundle_id),
        "session_spec_path": norm(os.path.relpath(paths["session_spec_path"], repo_root)),
        "universe_identity_path": norm(os.path.relpath(paths["universe_identity_path"], repo_root)),
        "universe_state_path": norm(os.path.relpath(paths["universe_state_path"], repo_root)),
        "session_spec_hash": canonical_sha256(session_payload),
        "selected_seed": str(session_payload.get("selected_seed", "")),
        "constraints_id": str(session_payload.get("constraints_id", "")),
        "search_plan_hash": str(session_payload.get("search_plan_hash", "")),
        "worldgen_search_plan_path": norm(os.path.relpath(paths["worldgen_search_plan_path"], repo_root))
        if search_plan_payload
        else "",
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "registry_hashes": dict((lockfile_payload.get("registries") or {})),
        "loaded_universe_identity_path": norm(identity_abs) if identity_abs else "",
        "generated_universe_identity": not bool(universe_identity_path),
    }
