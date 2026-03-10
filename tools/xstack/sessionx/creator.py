"""Deterministic out-of-game SessionSpec creator for v1 boot path wiring."""

from __future__ import annotations

import os
import copy
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.compatx.schema_registry import load_version_registry
from src.universe import (
    DEFAULT_UNIVERSE_CONTRACT_BUNDLE_REF,
    build_universe_contract_bundle_payload,
    pin_contract_bundle_metadata,
    validate_pinned_contract_bundle_metadata,
)
from src.modding import DEFAULT_MOD_POLICY_ID, load_mod_policy_registry, mod_policy_registry_hash, mod_policy_rows_by_id
from tools.xstack.pack_contrib.parser import parse_contributions
from tools.xstack.pack_loader.dependency_resolver import resolve_packs
from tools.xstack.pack_loader.loader import load_pack_set
from tools.xstack.registry_compile.bundle_profile import load_bundle_profile
from tools.xstack.registry_compile.compiler import compile_bundle
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID
from tools.xstack.registry_compile.bundle_profile import resolve_bundle_selection
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload
from worldgen.core.pipeline import run_worldgen_pipeline

from src.geo import build_default_overlay_manifest, overlay_proof_surface, validate_overlay_manifest_trust
from src.meta.profile import resolve_effective_profile_snapshot

from .common import (
    DEFAULT_TIMESTAMP_UTC,
    deterministic_seed_hex,
    identity_hash_for_payload,
    norm,
    read_json_object,
    refusal,
    write_canonical_json,
)
from .pipeline_contract import DEFAULT_PIPELINE_ID, load_session_pipeline_contract
from .universe_physics import (
    NULL_PHYSICS_PROFILE_ID,
    is_null_bundle_profile,
    select_physics_profile,
    write_null_boot_artifacts,
)


DEFAULT_EXPERIENCE_ID = "profile.lab.developer"
DEFAULT_LAW_PROFILE_ID = "law.lab.unrestricted"
DEFAULT_PARAMETER_BUNDLE_ID = "params.lab.placeholder"
DEFAULT_BUDGET_POLICY_ID = "policy.budget.default_lab"
DEFAULT_FIDELITY_POLICY_ID = "policy.fidelity.default_lab"
DEFAULT_PHYSICS_PROFILE_ID = NULL_PHYSICS_PROFILE_ID
DEFAULT_TOPOLOGY_PROFILE_ID = "geo.topology.r3_infinite"
DEFAULT_METRIC_PROFILE_ID = "geo.metric.euclidean"
DEFAULT_PARTITION_PROFILE_ID = "geo.partition.grid_zd"
DEFAULT_PROJECTION_PROFILE_ID = "geo.projection.perspective_3d"
DEFAULT_GENERATOR_VERSION_ID = "gen.v0_stub"
DEFAULT_REALISM_PROFILE_ID = "realism.realistic_default_milkyway_stub"
DEFAULT_TIME_CONTROL_POLICY_ID = "time.policy.null"
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
    "entitlement.agent.move",
    "entitlement.agent.rotate",
    "entitlement.control.camera",
    "entitlement.control.admin",
    "entitlement.control.possess",
    "entitlement.control.lens_override",
    "entitlement.cosmetic.assign",
    "entitlement.civ.create_faction",
    "entitlement.civ.dissolve_faction",
    "entitlement.civ.affiliation",
    "entitlement.civ.claim",
    "entitlement.civ.diplomacy",
    "entitlement.diegetic.notebook_write",
    "entitlement.diegetic.radio_use",
    "entitlement.tool.equip",
    "entitlement.tool.use",
    "ent.tool.terrain_edit",
    "ent.tool.scan",
    "ent.tool.logic_probe",
    "ent.tool.logic_trace",
    "ent.tool.teleport",
    "lens.nondiegetic.access",
    "ui.window.lab.nav",
)
DEFAULT_CAMERA_ASSEMBLY = {
    "assembly_id": "camera.main",
    "frame_id": "frame.world",
    "position_mm": {"x": 0, "y": 0, "z": 0},
    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
    "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
    "lens_id": "lens.diegetic.sensor",
    "binding_id": None,
    "view_mode_id": "view.free.lab",
    "owner_peer_id": None,
    "target_id": None,
    "target_type": "none",
    "offset_params": {
        "x_mm": 0,
        "y_mm": 0,
        "z_mm": 0,
        "yaw_mdeg": 0,
        "pitch_mdeg": 0,
        "roll_mdeg": 0,
    },
}
INSTRUMENT_TYPE_ID_BY_TYPE = {
    "altimeter": "instr.altimeter",
    "clock": "instr.clock",
    "compass": "instr.compass",
    "map_local": "instr.map_local",
    "notebook": "instr.notebook",
    "radio_text": "instr.radio_text",
}
INSTRUMENT_TYPE_BY_ID = dict((value, key) for key, value in INSTRUMENT_TYPE_ID_BY_TYPE.items())
DEFAULT_INSTRUMENT_ASSEMBLIES = [
    {
        "assembly_id": "instrument.altimeter",
        "instrument_type": "altimeter",
        "instrument_type_id": "instr.altimeter",
        "carrier_agent_id": None,
        "station_site_id": None,
        "reading": {
            "altitude_mm": 0
        },
        "state": {},
        "outputs": {
            "ch.diegetic.altimeter": {
                "altitude_mm": 0
            }
        },
        "quality": "nominal",
        "quality_value": 1000,
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.clock",
        "instrument_type": "clock",
        "instrument_type_id": "instr.clock",
        "carrier_agent_id": None,
        "station_site_id": None,
        "reading": {
            "tick": 0,
            "rate_permille": 1000,
            "paused": False,
        },
        "state": {},
        "outputs": {
            "ch.diegetic.clock": {
                "tick": 0,
                "rate_permille": 1000,
                "paused": False
            }
        },
        "quality": "nominal",
        "quality_value": 1000,
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.compass",
        "instrument_type": "compass",
        "instrument_type_id": "instr.compass",
        "carrier_agent_id": None,
        "station_site_id": None,
        "reading": {
            "heading_mdeg": 0,
        },
        "state": {},
        "outputs": {
            "ch.diegetic.compass": {
                "heading_mdeg": 0
            }
        },
        "quality": "nominal",
        "quality_value": 1000,
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.map_local",
        "instrument_type": "map_local",
        "instrument_type_id": "instr.map_local",
        "carrier_agent_id": None,
        "station_site_id": None,
        "reading": {
            "entries": []
        },
        "state": {
            "entries": []
        },
        "outputs": {
            "ch.diegetic.map_local": {
                "entries": []
            }
        },
        "quality": "nominal",
        "quality_value": 1000,
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.notebook",
        "instrument_type": "notebook",
        "instrument_type_id": "instr.notebook",
        "carrier_agent_id": None,
        "station_site_id": None,
        "reading": {
            "entries": []
        },
        "state": {
            "user_notes": []
        },
        "outputs": {
            "ch.diegetic.notebook": {
                "entries": []
            }
        },
        "quality": "nominal",
        "quality_value": 1000,
        "last_update_tick": 0,
    },
    {
        "assembly_id": "instrument.radio_text",
        "instrument_type": "radio_text",
        "instrument_type_id": "instr.radio_text",
        "carrier_agent_id": None,
        "station_site_id": None,
        "reading": {
            "messages": []
        },
        "state": {
            "inbox": []
        },
        "outputs": {
            "ch.diegetic.radio_text": {
                "messages": []
            }
        },
        "quality": "nominal",
        "quality_value": 1000,
        "last_update_tick": 0,
    },
]
DEFAULT_WORLDGEN_MODULE_REGISTRY_REL = "data/registries/worldgen_module_registry.json"

REGISTRY_FILE_MAP = {
    "universe_physics_profile_registry_hash": "universe_physics_profile.registry.json",
    "time_model_registry_hash": "time_model.registry.json",
    "time_control_policy_registry_hash": "time_control_policy.registry.json",
    "dt_quantization_rule_registry_hash": "dt_quantization_rule.registry.json",
    "compaction_policy_registry_hash": "compaction_policy.registry.json",
    "transition_policy_registry_hash": "transition_policy.registry.json",
    "arbitration_rule_registry_hash": "arbitration_rule.registry.json",
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
        "universe_contract_bundle_path": os.path.join(root, "universe_contract_bundle.json"),
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


def _compatibility_schema_refs(repo_root: str) -> List[str]:
    payload, error = load_version_registry(repo_root=repo_root)
    if error:
        return []
    rows = (payload.get("schemas") or {}) if isinstance(payload, dict) else {}
    if not isinstance(rows, dict):
        return []
    include = (
        "bundle_lockfile",
        "metric_profile",
        "partition_profile",
        "projection_profile",
        "generator_version",
        "realism_profile",
        "session_spec",
        "space_topology_profile",
        "universe_identity",
        "universe_physics_profile",
        "time_model",
        "time_control_policy",
        "dt_quantization_rule",
        "compaction_policy",
        "numeric_precision_policy",
        "tier_taxonomy",
        "boundary_model",
    )
    out: List[str] = []
    for schema_name in include:
        row = rows.get(schema_name)
        if not isinstance(row, dict):
            continue
        version = str(row.get("current_version", "")).strip()
        if version:
            out.append("{}@{}".format(schema_name, version))
    return sorted(set(out))


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


def _select_time_control_policy(
    *,
    time_control_policy_registry: dict,
    dt_quantization_rule_registry: dict,
    compaction_policy_registry: dict,
    time_model_registry: dict,
    selected_physics_profile: dict,
    requested_time_control_policy_id: str,
) -> Tuple[dict, Dict[str, object]]:
    policy_rows = list(time_control_policy_registry.get("policies") or [])
    if not isinstance(policy_rows, list):
        return {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_FOUND",
            "time control policy registry is missing policies list",
            "Rebuild registries and ensure time control policies are present.",
            {"registry_file": REGISTRY_FILE_MAP["time_control_policy_registry_hash"]},
            "$.policies",
        )
    requested_id = str(requested_time_control_policy_id or "").strip()
    selected_policy = {}
    if requested_id:
        for row in sorted(
            (item for item in policy_rows if isinstance(item, dict)),
            key=lambda item: str(item.get("time_control_policy_id", "")),
        ):
            if str(row.get("time_control_policy_id", "")).strip() == requested_id:
                selected_policy = dict(row)
                break
    else:
        for row in sorted(
            (item for item in policy_rows if isinstance(item, dict)),
            key=lambda item: str(item.get("time_control_policy_id", "")),
        ):
            selected_policy = dict(row)
            requested_id = str(selected_policy.get("time_control_policy_id", "")).strip()
            break
    if not selected_policy:
        return {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_FOUND",
            "time control policy '{}' is not present in compiled registry".format(requested_id or "<empty>"),
            "Select a policy ID listed in '{}' and rebuild SessionSpec.".format(REGISTRY_FILE_MAP["time_control_policy_registry_hash"]),
            {"time_control_policy_id": requested_id},
            "$.time_control_policy_id",
        )

    dt_rule_id = str(selected_policy.get("dt_quantization_rule_id", "")).strip()
    dt_rows = list(dt_quantization_rule_registry.get("rules") or [])
    has_dt_rule = False
    for row in sorted((item for item in dt_rows if isinstance(item, dict)), key=lambda item: str(item.get("dt_rule_id", ""))):
        if str(row.get("dt_rule_id", "")).strip() == dt_rule_id:
            has_dt_rule = True
            break
    if not has_dt_rule:
        return {}, refusal(
            "REFUSE_DT_RULE_NOT_FOUND",
            "time control policy '{}' references unknown dt_quantization_rule_id '{}'".format(requested_id, dt_rule_id or "<empty>"),
            "Select a valid dt quantization rule from '{}'.".format(REGISTRY_FILE_MAP["dt_quantization_rule_registry_hash"]),
            {"time_control_policy_id": requested_id, "dt_quantization_rule_id": dt_rule_id},
            "$.time_control_policy_id",
        )

    compaction_policy_id = str(selected_policy.get("compaction_policy_id", "")).strip()
    compaction_rows = list(compaction_policy_registry.get("policies") or [])
    has_compaction_policy = False
    for row in sorted(
        (item for item in compaction_rows if isinstance(item, dict)),
        key=lambda item: str(item.get("compaction_policy_id", "")),
    ):
        if str(row.get("compaction_policy_id", "")).strip() == compaction_policy_id:
            has_compaction_policy = True
            break
    if not has_compaction_policy:
        return {}, refusal(
            "REFUSE_COMPACTION_POLICY_NOT_FOUND",
            "time control policy '{}' references unknown compaction_policy_id '{}'".format(requested_id, compaction_policy_id or "<empty>"),
            "Select a valid compaction policy from '{}'.".format(REGISTRY_FILE_MAP["compaction_policy_registry_hash"]),
            {"time_control_policy_id": requested_id, "compaction_policy_id": compaction_policy_id},
            "$.time_control_policy_id",
        )

    time_model_id = str((selected_physics_profile or {}).get("time_model_id", "")).strip()
    time_model_rows = list(time_model_registry.get("time_models") or [])
    selected_time_model = {}
    for row in sorted((item for item in time_model_rows if isinstance(item, dict)), key=lambda item: str(item.get("time_model_id", ""))):
        if str(row.get("time_model_id", "")).strip() == time_model_id:
            selected_time_model = dict(row)
            break
    if not selected_time_model:
        return {}, refusal(
            "REFUSE_TIME_MODEL_NOT_FOUND",
            "physics profile references unknown time_model_id '{}'".format(time_model_id or "<empty>"),
            "Select a valid UniversePhysicsProfile time_model_id.",
            {"time_model_id": time_model_id},
            "$.physics_profile_id",
        )

    extensions = dict(selected_policy.get("extensions") or {})
    allowed_models = sorted(
        set(str(item).strip() for item in (extensions.get("allowed_time_model_ids") or []) if str(item).strip())
    )
    if allowed_models and time_model_id not in set(allowed_models):
        return {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_ALLOWED_BY_PHYSICS",
            "time control policy '{}' is not allowed for time_model_id '{}'".format(requested_id, time_model_id),
            "Select a compatible time_control_policy_id for the active physics profile.",
            {
                "time_control_policy_id": requested_id,
                "time_model_id": time_model_id,
            },
            "$.time_control_policy_id",
        )

    allow_variable_dt = bool(selected_policy.get("allow_variable_dt", False))
    if allow_variable_dt and not bool(selected_time_model.get("allow_variable_dt", False)):
        return {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_ALLOWED_BY_PHYSICS",
            "time control policy '{}' requires variable dt but active time model forbids it".format(requested_id),
            "Choose a non-variable-dt policy or a compatible physics profile time model.",
            {
                "time_control_policy_id": requested_id,
                "time_model_id": time_model_id,
            },
            "$.time_control_policy_id",
        )

    allow_branching = bool(extensions.get("allow_branching", False))
    if allow_branching and not bool(selected_time_model.get("allow_branching", False)):
        return {}, refusal(
            "REFUSE_TIME_CONTROL_POLICY_NOT_ALLOWED_BY_PHYSICS",
            "time control policy '{}' enables branching while active time model forbids it".format(requested_id),
            "Choose a compatible policy/time_model combination.",
            {
                "time_control_policy_id": requested_id,
                "time_model_id": time_model_id,
            },
            "$.time_control_policy_id",
        )

    return selected_policy, {}


def _universe_identity_from_seed(
    *,
    seed_text: str,
    universe_id: str,
    scenario_id: str,
    domain_binding_ids: List[str],
    physics_profile_id: str,
    topology_profile_id: str,
    metric_profile_id: str,
    partition_profile_id: str,
    projection_profile_id: str,
    generator_version_id: str,
    realism_profile_id: str,
    initial_pack_set_hash_expectation: str,
    compatibility_schema_refs: List[str],
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "universe_id": str(universe_id).strip(),
        "global_seed": str(seed_text),
        "domain_binding_ids": sorted(set(str(item).strip() for item in (domain_binding_ids or []) if str(item).strip())),
        "physics_profile_id": str(physics_profile_id).strip() or NULL_PHYSICS_PROFILE_ID,
        "topology_profile_id": str(topology_profile_id).strip() or DEFAULT_TOPOLOGY_PROFILE_ID,
        "metric_profile_id": str(metric_profile_id).strip() or DEFAULT_METRIC_PROFILE_ID,
        "partition_profile_id": str(partition_profile_id).strip() or DEFAULT_PARTITION_PROFILE_ID,
        "projection_profile_id": str(projection_profile_id).strip() or DEFAULT_PROJECTION_PROFILE_ID,
        "generator_version_id": str(generator_version_id).strip() or DEFAULT_GENERATOR_VERSION_ID,
        "realism_profile_id": str(realism_profile_id).strip() or DEFAULT_REALISM_PROFILE_ID,
        "base_scenario_id": str(scenario_id),
        "initial_pack_set_hash_expectation": str(initial_pack_set_hash_expectation).strip(),
        "compatibility_schema_refs": sorted(
            set(str(item).strip() for item in (compatibility_schema_refs or []) if str(item).strip())
        ),
        "immutable_after_create": True,
        "extensions": {},
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
    offset_source = source.get("offset_params") if isinstance(source, dict) else {}
    if not isinstance(offset_source, dict):
        offset_source = {}
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
        "binding_id": None
        if not isinstance(source, dict) or source.get("binding_id") is None
        else str(source.get("binding_id", "")).strip() or None,
        "view_mode_id": str((source.get("view_mode_id") if isinstance(source, dict) else "") or "view.free.lab"),
        "owner_peer_id": None
        if not isinstance(source, dict) or source.get("owner_peer_id") is None
        else str(source.get("owner_peer_id", "")).strip() or None,
        "target_id": None
        if not isinstance(source, dict) or source.get("target_id") is None
        else str(source.get("target_id", "")).strip() or None,
        "target_type": str((source.get("target_type") if isinstance(source, dict) else "") or "none"),
        "offset_params": {
            "x_mm": _as_int(offset_source.get("x_mm", 0), 0),
            "y_mm": _as_int(offset_source.get("y_mm", 0), 0),
            "z_mm": _as_int(offset_source.get("z_mm", 0), 0),
            "yaw_mdeg": _as_int(offset_source.get("yaw_mdeg", 0), 0),
            "pitch_mdeg": _as_int(offset_source.get("pitch_mdeg", 0), 0),
            "roll_mdeg": _as_int(offset_source.get("roll_mdeg", 0), 0),
        },
    }


def _instrument_assemblies_from_payload(payload: dict) -> List[dict]:
    rows = payload.get("instrument_assemblies")
    if not isinstance(rows, list):
        return copy.deepcopy(DEFAULT_INSTRUMENT_ASSEMBLIES)
    out: List[dict] = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
        assembly_id = str(row.get("assembly_id", "")).strip()
        instrument_type = str(row.get("instrument_type", "")).strip()
        instrument_type_id = str(row.get("instrument_type_id", "")).strip()
        if (not instrument_type) and instrument_type_id:
            instrument_type = str(INSTRUMENT_TYPE_BY_ID.get(instrument_type_id, "")).strip()
        if instrument_type and (not instrument_type_id):
            instrument_type_id = str(INSTRUMENT_TYPE_ID_BY_TYPE.get(instrument_type, "")).strip()
        if not assembly_id or not instrument_type:
            continue
        out.append(
            {
                "assembly_id": assembly_id,
                "instrument_type": instrument_type,
                "instrument_type_id": instrument_type_id or str(INSTRUMENT_TYPE_ID_BY_TYPE.get(instrument_type, "")),
                "carrier_agent_id": None if row.get("carrier_agent_id") is None else str(row.get("carrier_agent_id", "")).strip() or None,
                "station_site_id": None if row.get("station_site_id") is None else str(row.get("station_site_id", "")).strip() or None,
                "reading": copy.deepcopy(row.get("reading") if isinstance(row.get("reading"), dict) else {}),
                "state": copy.deepcopy(row.get("state") if isinstance(row.get("state"), dict) else {}),
                "outputs": copy.deepcopy(row.get("outputs") if isinstance(row.get("outputs"), dict) else {}),
                "quality": str(row.get("quality", "nominal")),
                "quality_value": max(0, _as_int(row.get("quality_value", 1000), 1000)),
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
    camera_assembly: dict | None,
    instrument_assemblies: List[dict],
    budget_policy_id: str,
    fidelity_policy_id: str,
    activation_policy_id: str,
    max_compute_units_per_tick: int,
) -> dict:
    has_camera = isinstance(camera_assembly, dict) and bool(camera_assembly)
    camera_payload = _camera_from_payload(camera_assembly if has_camera else {})
    camera_rows = [camera_payload] if has_camera else []
    instrument_rows = [
        {
            "assembly_id": str(row.get("assembly_id", "")),
            "instrument_type": str(row.get("instrument_type", "")),
            "instrument_type_id": str(row.get("instrument_type_id", "")),
            "carrier_agent_id": None if row.get("carrier_agent_id") is None else str(row.get("carrier_agent_id", "")).strip() or None,
            "station_site_id": None if row.get("station_site_id") is None else str(row.get("station_site_id", "")).strip() or None,
            "reading": copy.deepcopy(row.get("reading") if isinstance(row.get("reading"), dict) else {}),
            "state": copy.deepcopy(row.get("state") if isinstance(row.get("state"), dict) else {}),
            "outputs": copy.deepcopy(row.get("outputs") if isinstance(row.get("outputs"), dict) else {}),
            "quality": str(row.get("quality", "nominal")),
            "quality_value": max(0, _as_int(row.get("quality_value", 1000), 1000)),
            "last_update_tick": _as_int(row.get("last_update_tick", 0), 0),
        }
        for row in sorted((item for item in (instrument_assemblies or []) if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", "")))
        if str(row.get("assembly_id", "")).strip() and str(row.get("instrument_type", "")).strip()
    ]
    world_assemblies: List[str] = []
    if has_camera:
        world_assemblies.append(str(camera_payload.get("assembly_id", "camera.main")))
    world_assemblies.extend(str(row.get("assembly_id", "")) for row in instrument_rows if str(row.get("assembly_id", "")).strip())
    world_assemblies = sorted(set(world_assemblies))
    return {
        "schema_version": "1.0.0",
        "simulation_time": {
            "tick": 0,
            "timestamp_utc": DEFAULT_TIMESTAMP_UTC,
            "sim_time_permille": 0,
            "last_dt_permille": 1000,
        },
        "agent_states": [],
        "world_assemblies": world_assemblies,
        "active_law_references": [str(law_profile_id)],
        "session_references": ["session.{}".format(str(save_id))],
        "history_anchors": ["history.anchor.tick.0"],
        "camera_assemblies": camera_rows,
        "instrument_assemblies": instrument_rows,
        "tool_assemblies": [],
        "tool_bindings": [],
        "machine_assemblies": [],
        "machine_ports": [],
        "machine_port_connections": [],
        "machine_provenance_events": [],
        "tasks": [],
        "task_provenance_events": [],
        "pending_task_completion_intents": [],
        "controller_assemblies": [],
        "control_bindings": [],
        "faction_assemblies": [],
        "affiliations": [],
        "territory_assemblies": [],
        "diplomatic_relations": [],
        "cohort_assemblies": [],
        "order_assemblies": [],
        "order_queue_assemblies": [],
        "institution_assemblies": [],
        "role_assignment_assemblies": [],
        "time_control": {
            "rate_permille": 1000,
            "paused": False,
            "accumulator_permille": 0,
            "current_rate_permille": 1000,
            "current_dt_permille": 1000,
            "time_control_policy_id": str(DEFAULT_TIME_CONTROL_POLICY_ID),
            "dt_rule_id": "dt.rule.single_tick",
        },
        "time_tick_log": [],
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


def _profile_binding_row(*, scope: str, target_id: str, profile_id: str) -> dict:
    scope_token = str(scope or "").strip().lower()
    target_token = str(target_id or "").strip() or "*"
    profile_token = str(profile_id or "").strip()
    if (not scope_token) or (not target_token) or (not profile_token):
        return {}
    payload = {
        "binding_id": "binding.profile.{}".format(
            canonical_sha256(
                {
                    "scope": scope_token,
                    "target_id": target_token,
                    "profile_id": profile_token,
                }
            )[:16]
        ),
        "scope": scope_token,
        "target_id": target_token,
        "profile_id": profile_token,
        "tick_applied": 0,
        "extensions": {
            "source": "sessionx.creator",
        },
    }
    return payload


def _physics_overlay_profile_id(physics_profile_id: str) -> str:
    token = str(physics_profile_id or "").strip().lower()
    if "magic" in token:
        return "physics.alternate_magic"
    return "physics.default_realistic"


def _law_overlay_profile_id(law_profile_id: str) -> str:
    token = str(law_profile_id or "").strip().lower()
    if ("strict" in token) or ("hardcore" in token):
        return "law.strict"
    return "law.softcore"


def _epistemic_overlay_profile_id(privilege_level: str) -> str:
    token = str(privilege_level or "").strip().lower()
    if token in {"system", "admin"}:
        return "epistemic.admin_full"
    return "epistemic.default_diegetic"


def _default_profile_bindings(
    *,
    universe_id: str,
    session_id: str,
    authority_id: str,
    physics_profile_id: str,
    topology_profile_id: str,
    metric_profile_id: str,
    partition_profile_id: str,
    projection_profile_id: str,
    law_profile_id: str,
    privilege_level: str,
) -> List[dict]:
    rows = [
        _profile_binding_row(
            scope="universe",
            target_id=str(universe_id or "").strip() or "*",
            profile_id=_physics_overlay_profile_id(physics_profile_id),
        ),
        _profile_binding_row(
            scope="universe",
            target_id=str(universe_id or "").strip() or "*",
            profile_id=str(topology_profile_id or "").strip() or DEFAULT_TOPOLOGY_PROFILE_ID,
        ),
        _profile_binding_row(
            scope="universe",
            target_id=str(universe_id or "").strip() or "*",
            profile_id=str(metric_profile_id or "").strip() or DEFAULT_METRIC_PROFILE_ID,
        ),
        _profile_binding_row(
            scope="universe",
            target_id=str(universe_id or "").strip() or "*",
            profile_id=str(partition_profile_id or "").strip() or DEFAULT_PARTITION_PROFILE_ID,
        ),
        _profile_binding_row(
            scope="universe",
            target_id=str(universe_id or "").strip() or "*",
            profile_id=str(projection_profile_id or "").strip() or DEFAULT_PROJECTION_PROFILE_ID,
        ),
        _profile_binding_row(
            scope="session",
            target_id=str(session_id or "").strip() or "*",
            profile_id="process.default",
        ),
        _profile_binding_row(
            scope="session",
            target_id=str(session_id or "").strip() or "*",
            profile_id="safety.default",
        ),
        _profile_binding_row(
            scope="session",
            target_id=str(session_id or "").strip() or "*",
            profile_id="coupling.default",
        ),
        _profile_binding_row(
            scope="session",
            target_id=str(session_id or "").strip() or "*",
            profile_id="compute.default",
        ),
        _profile_binding_row(
            scope="authority",
            target_id=str(authority_id or "").strip() or "*",
            profile_id=_law_overlay_profile_id(law_profile_id),
        ),
        _profile_binding_row(
            scope="authority",
            target_id=str(authority_id or "").strip() or "*",
            profile_id=_epistemic_overlay_profile_id(privilege_level),
        ),
    ]
    out = [dict(row) for row in rows if row]
    return sorted(out, key=lambda row: (str(row.get("scope", "")), str(row.get("target_id", "")), str(row.get("profile_id", ""))))


def create_session_spec(
    repo_root: str,
    save_id: str,
    bundle_id: str = DEFAULT_BUNDLE_ID,
    mod_policy_id: str = DEFAULT_MOD_POLICY_ID,
    physics_profile_id: str = "",
    scenario_id: str = DEFAULT_SCENARIO_ID,
    mission_id: str = "",
    experience_id: str = DEFAULT_EXPERIENCE_ID,
    law_profile_id: str = DEFAULT_LAW_PROFILE_ID,
    parameter_bundle_id: str = DEFAULT_PARAMETER_BUNDLE_ID,
    budget_policy_id: str = DEFAULT_BUDGET_POLICY_ID,
    fidelity_policy_id: str = DEFAULT_FIDELITY_POLICY_ID,
    time_control_policy_id: str = DEFAULT_TIME_CONTROL_POLICY_ID,
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
    paths = _session_paths(repo_root=repo_root, save_id=save_token, saves_root_rel=saves_root_rel)

    bundle_profile = load_bundle_profile(repo_root=repo_root, bundle_id=str(bundle_id), schema_repo_root=repo_root)
    if bundle_profile.get("result") != "complete":
        return refusal(
            "REFUSE_BUNDLE_INVALID",
            "bundle validation failed for '{}'".format(str(bundle_id)),
            "Validate bundle using tools/xstack/bundle_validate and retry.",
            {"bundle_id": str(bundle_id)},
            "$.bundle_id",
        )
    null_bundle = is_null_bundle_profile(bundle_profile)

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
        if null_bundle:
            compile_result = write_null_boot_artifacts(
                repo_root=repo_root,
                out_dir_rel="build/registries",
                lockfile_out_rel="build/lockfile.json",
                bundle_id=str(bundle_id),
                schema_repo_root=repo_root,
            )
        else:
            compile_result = compile_bundle(
                repo_root=repo_root,
                bundle_id=str(bundle_id),
                out_dir_rel="build/registries",
                lockfile_out_rel="build/lockfile.json",
                packs_root_rel="packs",
                schema_repo_root=repo_root,
                mod_policy_id=str(mod_policy_id or DEFAULT_MOD_POLICY_ID),
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
    requested_mod_policy_id = str(mod_policy_id or DEFAULT_MOD_POLICY_ID).strip() or DEFAULT_MOD_POLICY_ID
    lockfile_mod_policy_id = str(lockfile_payload.get("mod_policy_id", "")).strip()
    lockfile_mod_policy_registry_hash = str(lockfile_payload.get("mod_policy_registry_hash", "")).strip()
    if lockfile_mod_policy_id and lockfile_mod_policy_id != requested_mod_policy_id:
        return refusal(
            "REFUSE_MOD_POLICY_MISMATCH",
            "lockfile mod_policy_id does not match requested session mod policy",
            "Regenerate lockfile with the requested --mod-policy-id or reuse the original policy.",
            {
                "requested_mod_policy_id": requested_mod_policy_id,
                "lockfile_mod_policy_id": lockfile_mod_policy_id,
            },
            "$.mod_policy_id",
        )
    if not compile_outputs and (not lockfile_mod_policy_id or not lockfile_mod_policy_registry_hash):
        return refusal(
            "REFUSE_MOD_POLICY_METADATA_MISSING",
            "existing lockfile missing mod policy metadata required for new session creation",
            "Rebuild build/lockfile.json under the requested mod policy before creating this session.",
            {"mod_policy_id": requested_mod_policy_id},
            "$.mod_policy_id",
        )
    mod_policy_registry_payload, mod_policy_registry_errors = load_mod_policy_registry(repo_root)
    if mod_policy_registry_errors:
        return refusal(
            "REFUSE_MOD_POLICY_REGISTRY_INVALID",
            "mod policy registry failed validation during session creation",
            "Repair data/registries/mod_policy_registry.json and retry session creation.",
            {"errors": mod_policy_registry_errors},
            "$.mod_policy_registry",
        )
    mod_policy_row = dict(mod_policy_rows_by_id(mod_policy_registry_payload).get(requested_mod_policy_id) or {})
    if not mod_policy_row:
        return refusal(
            "REFUSE_MOD_POLICY_INVALID",
            "requested mod_policy_id is not declared",
            "Select a declared mod_policy_id and retry session creation.",
            {"mod_policy_id": requested_mod_policy_id},
            "$.mod_policy_id",
        )
    selected_mod_policy_registry_hash = lockfile_mod_policy_registry_hash or mod_policy_registry_hash(
        mod_policy_registry_payload
    )
    selected_overlay_conflict_policy_id = str(lockfile_payload.get("overlay_conflict_policy_id", "")).strip() or str(
        mod_policy_row.get("conflict_policy_id", "")
    ).strip()

    registries = lockfile_payload.get("registries")
    if not isinstance(registries, dict):
        return refusal(
            "REFUSE_LOCKFILE_REGISTRY_SECTION_MISSING",
            "lockfile registries section is missing",
            "Rebuild lockfile and retry session creation.",
            {"bundle_id": str(bundle_id)},
            "$.registries",
        )
    universe_physics_registry, universe_physics_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["universe_physics_profile_registry_hash"],
        expected_hash=str(registries.get("universe_physics_profile_registry_hash", "")),
    )
    if universe_physics_registry_error:
        return universe_physics_registry_error

    explicit_physics_profile_id = str(physics_profile_id).strip()
    requested_physics_profile_id = explicit_physics_profile_id or DEFAULT_PHYSICS_PROFILE_ID
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
        identity_physics_profile_id = str(identity_payload.get("physics_profile_id", "")).strip()
        if not identity_physics_profile_id:
            return refusal(
                "refusal.physics_profile_missing",
                "provided universe identity is missing physics_profile_id",
                "Set universe_identity.physics_profile_id explicitly or regenerate via session_create.",
                {"universe_identity_path": norm(identity_abs)},
                "$.universe_identity.physics_profile_id",
            )
        if explicit_physics_profile_id and explicit_physics_profile_id != identity_physics_profile_id:
            return refusal(
                "refusal.physics_profile_mismatch",
                "requested physics_profile_id does not match provided universe identity",
                "Use matching physics profile inputs or remove explicit --physics-profile-id override.",
                {
                    "requested_physics_profile_id": explicit_physics_profile_id,
                    "identity_physics_profile_id": identity_physics_profile_id,
                },
                "$.physics_profile_id",
            )
        requested_physics_profile_id = identity_physics_profile_id
    else:
        selected_profile, profile_error = select_physics_profile(
            physics_profile_id=requested_physics_profile_id,
            profile_registry=universe_physics_registry,
        )
        if profile_error:
            return profile_error
        domain_bindings = sorted(
            set(str(item).strip() for item in (selected_profile.get("enabled_domain_ids") or []) if str(item).strip())
        )
        generated_universe_id = str(universe_id).strip() or "universe.{}".format(
            deterministic_seed_hex(str(universe_seed_string), "universe.identity")[:16]
        )
        identity_payload = _universe_identity_from_seed(
            universe_id=generated_universe_id,
            seed_text=str(universe_seed_string),
            scenario_id=str(scenario_id),
            domain_binding_ids=domain_bindings,
            physics_profile_id=str(selected_profile.get("physics_profile_id", "")),
            topology_profile_id=DEFAULT_TOPOLOGY_PROFILE_ID,
            metric_profile_id=DEFAULT_METRIC_PROFILE_ID,
            partition_profile_id=DEFAULT_PARTITION_PROFILE_ID,
            projection_profile_id=DEFAULT_PROJECTION_PROFILE_ID,
            generator_version_id=DEFAULT_GENERATOR_VERSION_ID,
            realism_profile_id=DEFAULT_REALISM_PROFILE_ID,
            initial_pack_set_hash_expectation=str(lockfile_payload.get("pack_lock_hash", "")),
            compatibility_schema_refs=_compatibility_schema_refs(repo_root=repo_root),
        )
        identity_abs = ""

    (
        universe_contract_bundle_payload,
        _semantic_contract_registry_payload,
        semantic_contract_proof_bundle,
        universe_contract_bundle_errors,
    ) = build_universe_contract_bundle_payload(repo_root=repo_root)
    if universe_contract_bundle_errors:
        if "refuse.semantic_contract_registry_missing" in universe_contract_bundle_errors:
            return refusal(
                "REFUSE_SEMANTIC_CONTRACT_REGISTRY_MISSING",
                "semantic contract registry could not be loaded",
                "Restore data/registries/semantic_contract_registry.json and retry session creation.",
                {"registry_id": "dominium.registry.semantic_contracts"},
                "$.universe_contract_bundle",
            )
        return refusal(
            "REFUSE_UNIVERSE_CONTRACT_BUNDLE_INVALID",
            "universe semantic contract bundle failed validation",
            "Repair semantic contract registry and universe contract bundle metadata, then retry session creation.",
            {"schema_id": "universe_contract_bundle"},
            "$.universe_contract_bundle",
        )

    if identity_abs:
        pinned_identity_errors = validate_pinned_contract_bundle_metadata(
            identity_payload,
            bundle_ref=DEFAULT_UNIVERSE_CONTRACT_BUNDLE_REF,
            bundle_payload=universe_contract_bundle_payload,
        )
        if pinned_identity_errors:
            return refusal(
                "REFUSE_UNIVERSE_IDENTITY_CONTRACT_BUNDLE_MISMATCH",
                "provided UniverseIdentity is missing or mismatches its pinned universe contract bundle metadata",
                "Run the CompatX migration tool or recreate the universe so it pins the current semantic contract bundle.",
                {"schema_id": "universe_identity"},
                "$.universe_identity",
            )
    else:
        identity_payload = pin_contract_bundle_metadata(
            identity_payload,
            bundle_ref=DEFAULT_UNIVERSE_CONTRACT_BUNDLE_REF,
            bundle_payload=universe_contract_bundle_payload,
        )

    selected_profile, profile_error = select_physics_profile(
        physics_profile_id=requested_physics_profile_id,
        profile_registry=universe_physics_registry,
    )
    if profile_error:
        return profile_error
    if str(identity_payload.get("physics_profile_id", "")).strip() != str(selected_profile.get("physics_profile_id", "")).strip():
        return refusal(
            "refusal.physics_profile_mismatch",
            "universe identity physics_profile_id does not match selected profile",
            "Use an identity payload with a compatible physics profile id.",
            {
                "identity_physics_profile_id": str(identity_payload.get("physics_profile_id", "")),
                "selected_physics_profile_id": str(selected_profile.get("physics_profile_id", "")),
            },
            "$.universe_identity.physics_profile_id",
        )

    identity_check = _validate_universe_identity(repo_root=repo_root, payload=identity_payload)
    if identity_check.get("result") != "complete":
        return identity_check

    calculated_universe_id = str(identity_payload.get("universe_id", "")).strip() or str(universe_id).strip()
    if not calculated_universe_id:
        calculated_universe_id = "universe.{}".format(str(identity_payload.get("identity_hash", ""))[:16])
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
    time_model_registry, time_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["time_model_registry_hash"],
        expected_hash=str(registries.get("time_model_registry_hash", "")),
    )
    if time_model_registry_error:
        return time_model_registry_error
    time_control_policy_registry, time_control_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["time_control_policy_registry_hash"],
        expected_hash=str(registries.get("time_control_policy_registry_hash", "")),
    )
    if time_control_policy_registry_error:
        return time_control_policy_registry_error
    dt_quantization_rule_registry, dt_quantization_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["dt_quantization_rule_registry_hash"],
        expected_hash=str(registries.get("dt_quantization_rule_registry_hash", "")),
    )
    if dt_quantization_rule_registry_error:
        return dt_quantization_rule_registry_error
    compaction_policy_registry, compaction_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["compaction_policy_registry_hash"],
        expected_hash=str(registries.get("compaction_policy_registry_hash", "")),
    )
    if compaction_policy_registry_error:
        return compaction_policy_registry_error

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

    resolved_time_control_policy_id = str(time_control_policy_id).strip() or DEFAULT_TIME_CONTROL_POLICY_ID
    selected_time_control_policy, time_control_policy_error = _select_time_control_policy(
        time_control_policy_registry=time_control_policy_registry,
        dt_quantization_rule_registry=dt_quantization_rule_registry,
        compaction_policy_registry=compaction_policy_registry,
        time_model_registry=time_model_registry,
        selected_physics_profile=selected_profile,
        requested_time_control_policy_id=resolved_time_control_policy_id,
    )
    if time_control_policy_error:
        return time_control_policy_error

    if network_payload:
        network_payload["physics_profile_id"] = str(identity_payload.get("physics_profile_id", "")).strip()

    profile_registry_path = os.path.join(repo_root, "data", "registries", "profile_registry.json")
    if os.path.isfile(profile_registry_path):
        profile_registry_payload, _profile_registry_error = read_json_object(profile_registry_path)
    else:
        profile_registry_payload = {}
    authority_binding_target = "client"
    session_profile_bindings = _default_profile_bindings(
        universe_id=calculated_universe_id,
        session_id=save_token,
        authority_id=authority_binding_target,
        physics_profile_id=str(identity_payload.get("physics_profile_id", "")).strip(),
        topology_profile_id=str(identity_payload.get("topology_profile_id", "")).strip() or DEFAULT_TOPOLOGY_PROFILE_ID,
        metric_profile_id=str(identity_payload.get("metric_profile_id", "")).strip() or DEFAULT_METRIC_PROFILE_ID,
        partition_profile_id=str(identity_payload.get("partition_profile_id", "")).strip() or DEFAULT_PARTITION_PROFILE_ID,
        projection_profile_id=str(identity_payload.get("projection_profile_id", "")).strip() or DEFAULT_PROJECTION_PROFILE_ID,
        law_profile_id=str(law_profile_id),
        privilege_level=str(privilege_level),
    )
    effective_profile_snapshot_payload = resolve_effective_profile_snapshot(
        owner_context={
            "universe_id": calculated_universe_id,
            "session_id": save_token,
            "authority_id": authority_binding_target,
            "session_spec": {
                "save_id": save_token,
                "profile_bindings": session_profile_bindings,
            },
        },
        profile_registry_payload=profile_registry_payload,
        profile_binding_rows=session_profile_bindings,
    )
    effective_profile_snapshot = dict(effective_profile_snapshot_payload.get("snapshot") or {})

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
        "physics_profile_id": str(identity_payload.get("physics_profile_id", "")).strip(),
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
            "profile_bindings": [
                dict(row)
                for row in session_profile_bindings
                if str(row.get("scope", "")).strip() == "authority"
            ],
            "effective_profile_snapshot": dict(effective_profile_snapshot),
        },
        "profile_bindings": [dict(row) for row in session_profile_bindings],
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "contract_bundle_hash": str(semantic_contract_proof_bundle.get("universe_contract_bundle_hash", "")).strip(),
        "semantic_contract_registry_hash": str(
            semantic_contract_proof_bundle.get("semantic_contract_registry_hash", "")
        ).strip(),
        "mod_policy_id": requested_mod_policy_id,
        "mod_policy_registry_hash": selected_mod_policy_registry_hash,
        "budget_policy_id": str(budget_policy_id),
        "fidelity_policy_id": str(fidelity_policy_id),
        "time_control_policy_id": str(selected_time_control_policy.get("time_control_policy_id", "")),
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

    camera_assembly = None if null_bundle else _camera_seed_from_bundle(repo_root=repo_root, bundle_id=str(bundle_id))
    instrument_assemblies = [] if null_bundle else _instrument_seed_from_bundle(repo_root=repo_root, bundle_id=str(bundle_id))
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
    overlay_manifest = build_default_overlay_manifest(
        universe_id=calculated_universe_id,
        pack_lock_hash=str(lockfile_payload.get("pack_lock_hash", "")),
        save_id=save_token,
        generator_version_id=str(identity_payload.get("generator_version_id", "")).strip(),
        overlay_conflict_policy_id=selected_overlay_conflict_policy_id,
    )
    overlay_trust = validate_overlay_manifest_trust(
        overlay_manifest=overlay_manifest,
        resolved_packs=list(lockfile_payload.get("resolved_packs") or []),
        expected_pack_lock_hash=str(lockfile_payload.get("pack_lock_hash", "")),
        overlay_conflict_policy_id=selected_overlay_conflict_policy_id,
    )
    if str(overlay_trust.get("result", "")) != "complete":
        return overlay_trust
    state_payload["overlay_manifest"] = dict(overlay_trust.get("overlay_manifest") or {})
    state_payload["save_property_patches"] = []
    state_payload["overlay_merge_results"] = []
    overlay_surface = overlay_proof_surface(
        overlay_manifest=state_payload.get("overlay_manifest"),
        property_patches=state_payload.get("save_property_patches"),
        effective_object_views=state_payload.get("overlay_merge_results"),
    )
    state_payload["overlay_manifest_hash"] = str(overlay_surface.get("overlay_manifest_hash", "")).strip()
    state_payload["property_patch_hash_chain"] = str(overlay_surface.get("property_patch_hash_chain", "")).strip()
    state_payload["overlay_merge_result_hash_chain"] = str(overlay_surface.get("overlay_merge_result_hash_chain", "")).strip()
    state_valid = validate_instance(repo_root=repo_root, schema_name="universe_state", payload=state_payload, strict_top_level=True)
    if not bool(state_valid.get("valid", False)):
        return refusal(
            "REFUSE_UNIVERSE_STATE_INVALID",
            "generated UniverseState failed schema validation",
            "Review generated initial state fields against schemas/universe_state.schema.json.",
            {"schema_id": "universe_state"},
            "$.universe_state",
        )

    write_canonical_json(paths["session_spec_path"], session_payload)
    write_canonical_json(paths["universe_identity_path"], identity_payload)
    write_canonical_json(paths["universe_contract_bundle_path"], universe_contract_bundle_payload)
    write_canonical_json(paths["universe_state_path"], state_payload)
    if search_plan_payload:
        write_canonical_json(paths["worldgen_search_plan_path"], search_plan_payload)

    return {
        "result": "complete",
        "save_id": save_token,
        "bundle_id": str(bundle_id),
        "session_spec_path": norm(os.path.relpath(paths["session_spec_path"], repo_root)),
        "universe_identity_path": norm(os.path.relpath(paths["universe_identity_path"], repo_root)),
        "universe_contract_bundle_path": norm(os.path.relpath(paths["universe_contract_bundle_path"], repo_root)),
        "universe_state_path": norm(os.path.relpath(paths["universe_state_path"], repo_root)),
        "session_spec_hash": canonical_sha256(session_payload),
        "selected_seed": str(session_payload.get("selected_seed", "")),
        "constraints_id": str(session_payload.get("constraints_id", "")),
        "search_plan_hash": str(session_payload.get("search_plan_hash", "")),
        "worldgen_search_plan_path": norm(os.path.relpath(paths["worldgen_search_plan_path"], repo_root))
        if search_plan_payload
        else "",
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "mod_policy_id": requested_mod_policy_id,
        "mod_policy_registry_hash": selected_mod_policy_registry_hash,
        "registry_hashes": dict((lockfile_payload.get("registries") or {})),
        "physics_profile_id": str(identity_payload.get("physics_profile_id", "")),
        "time_control_policy_id": str(selected_time_control_policy.get("time_control_policy_id", "")),
        "loaded_universe_identity_path": norm(identity_abs) if identity_abs else "",
        "generated_universe_identity": not bool(universe_identity_path),
        "semantic_contract_registry_hash": str(semantic_contract_proof_bundle.get("semantic_contract_registry_hash", "")).strip(),
        "universe_contract_bundle_hash": str(semantic_contract_proof_bundle.get("universe_contract_bundle_hash", "")).strip(),
    }
