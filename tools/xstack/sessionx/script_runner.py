"""Deterministic headless intent-script runner for lab camera/time process flows."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload
from src.compat.data_format_loader import stamp_artifact_metadata
from src.modding import DEFAULT_MOD_POLICY_ID, proof_bundle_from_lockfile, validate_saved_mod_policy
from src.universe import enforce_session_contract_bundle

from .common import identity_hash_for_payload, norm, now_utc_iso, read_json_object, refusal, write_canonical_json
from .observation import build_truth_model, observe_truth
from .render_model import build_render_model
from .runner import (
    REGISTRY_FILE_MAP,
    _load_lockfile,
    _load_registry_payload,
    _resolve_lockfile_path,
    _load_schema_validated,
    _select_law_profile,
    _select_lens_profile,
    _select_policy_entry,
    _select_time_control_policy,
    _select_transition_policy,
    _validate_registry_hashes,
)
from .scheduler import replay_intent_script_srz
from .universe_physics import select_physics_profile


DEFAULT_GENERATOR_VERSION_ID = "gen.v0_stub"
DEFAULT_REALISM_PROFILE_ID = "realism.realistic_default_milkyway_stub"


def _is_sha256_hex(token: str) -> bool:
    value = str(token or "").strip()
    if len(value) != 64:
        return False
    for ch in value:
        if ch not in "0123456789abcdefABCDEF":
            return False
    return True


def _normalize_hash64(token: str, seed: object) -> str:
    value = str(token or "").strip()
    if _is_sha256_hex(value):
        return value.lower()
    return canonical_sha256(seed)


def _write_checkpoint_artifacts(
    *,
    repo_root: str,
    save_id: str,
    pack_lock_hash: str,
    physics_profile_id: str,
    registry_hashes: dict,
    checkpoint_snapshots: List[dict],
) -> Tuple[List[dict], List[str], Dict[str, object]]:
    rows: List[dict] = []
    paths: List[str] = []
    for snapshot_row in sorted(
        (dict(item) for item in (checkpoint_snapshots or []) if isinstance(item, dict)),
        key=lambda item: (
            int(item.get("scheduler_tick", 0) or 0),
            int(item.get("simulation_tick", 0) or 0),
            str(item.get("checkpoint_hash", "")),
        ),
    ):
        scheduler_tick = int(snapshot_row.get("scheduler_tick", 0) or 0)
        simulation_tick = int(snapshot_row.get("simulation_tick", 0) or 0)
        checkpoint_hash = str(snapshot_row.get("checkpoint_hash", "")).strip()
        tick_hash = str(snapshot_row.get("tick_hash", "")).strip()
        composite_hash = str(snapshot_row.get("composite_hash", "")).strip()
        snapshot_state = dict(snapshot_row.get("state_snapshot") or {})
        checkpoint_id = "checkpoint.{}.sched.{}.tick.{}".format(str(save_id), int(scheduler_tick), int(simulation_tick))

        snapshot_rel = norm(
            os.path.join("saves", str(save_id), "checkpoints", "{}.snapshot.json".format(checkpoint_id))
        )
        snapshot_abs = os.path.join(repo_root, snapshot_rel.replace("/", os.sep))
        write_canonical_json(snapshot_abs, snapshot_state)

        truth_hash_anchor = _normalize_hash64(
            str(snapshot_row.get("truth_hash_anchor", "")),
            {"snapshot": snapshot_state},
        )
        ledger_hash = _normalize_hash64(
            str(snapshot_row.get("ledger_hash", "")),
            {
                "checkpoint_id": checkpoint_id,
                "scheduler_tick": int(scheduler_tick),
                "simulation_tick": int(simulation_tick),
                "tick_hash": tick_hash,
            },
        )
        checkpoint_payload = {
            "schema_version": "1.0.0",
            "checkpoint_id": checkpoint_id,
            "save_id": str(save_id),
            "tick": int(simulation_tick),
            "pack_lock_hash": _normalize_hash64(pack_lock_hash, {"save_id": str(save_id)}),
            "physics_profile_id": str(physics_profile_id),
            "registry_hashes": dict(registry_hashes or {}),
            "truth_hash_anchor": truth_hash_anchor,
            "ledger_hash": ledger_hash,
            "payload_ref": snapshot_rel,
            "extensions": {
                "scheduler_tick": int(scheduler_tick),
                "checkpoint_hash": checkpoint_hash,
                "tick_hash": tick_hash,
                "composite_hash": composite_hash,
            },
        }
        valid = validate_instance(
            repo_root=repo_root,
            schema_name="time_checkpoint",
            payload=checkpoint_payload,
            strict_top_level=True,
        )
        if not bool(valid.get("valid", False)):
            return [], [], refusal(
                "REFUSE_TIME_CHECKPOINT_SCHEMA_INVALID",
                "checkpoint artifact payload failed schema validation",
                "Repair checkpoint artifact generation fields and retry script run.",
                {"checkpoint_id": checkpoint_id},
                "$.checkpoint",
            )
        checkpoint_meta_rel = norm(
            os.path.join("saves", str(save_id), "checkpoints", "{}.checkpoint.json".format(checkpoint_id))
        )
        checkpoint_meta_abs = os.path.join(repo_root, checkpoint_meta_rel.replace("/", os.sep))
        write_canonical_json(checkpoint_meta_abs, checkpoint_payload)

        rows.append(dict(checkpoint_payload))
        paths.append(checkpoint_meta_rel)
    return rows, paths, {}


def _write_intent_log_artifacts(
    *,
    repo_root: str,
    save_id: str,
    accepted_envelopes: List[dict],
) -> Tuple[List[dict], List[str], Dict[str, object]]:
    grouped: Dict[int, List[str]] = {}
    for row in sorted(
        (dict(item) for item in (accepted_envelopes or []) if isinstance(item, dict)),
        key=lambda item: (
            int(item.get("submission_tick", 0) or 0),
            int(item.get("deterministic_sequence_number", 0) or 0),
            str(item.get("envelope_id", "")),
        ),
    ):
        tick = int(row.get("submission_tick", 0) or 0)
        envelope_id = str(row.get("envelope_id", "")).strip()
        intent_id = str(row.get("intent_id", "")).strip()
        token = envelope_id or intent_id
        if not token:
            continue
        grouped.setdefault(int(tick), []).append(token)

    rows: List[dict] = []
    paths: List[str] = []
    for tick in sorted(grouped.keys()):
        envelopes = sorted(set(str(item) for item in grouped[tick] if str(item).strip()))
        if not envelopes:
            continue
        log_id = "intent_log.{}.{}_{}".format(str(save_id), int(tick), int(tick))
        payload = {
            "schema_version": "1.0.0",
            "log_id": log_id,
            "save_id": str(save_id),
            "tick_range": {
                "start_tick": int(tick),
                "end_tick": int(tick),
            },
            "envelopes_or_intents": list(envelopes),
            "log_hash": "",
            "extensions": {},
        }
        payload["log_hash"] = canonical_sha256(
            {
                "schema_version": payload["schema_version"],
                "log_id": payload["log_id"],
                "save_id": payload["save_id"],
                "tick_range": dict(payload["tick_range"]),
                "envelopes_or_intents": list(payload["envelopes_or_intents"]),
                "extensions": dict(payload["extensions"]),
            }
        )
        valid = validate_instance(
            repo_root=repo_root,
            schema_name="intent_log",
            payload=payload,
            strict_top_level=True,
        )
        if not bool(valid.get("valid", False)):
            return [], [], refusal(
                "REFUSE_TIME_INTENT_LOG_SCHEMA_INVALID",
                "intent log artifact payload failed schema validation",
                "Repair intent log artifact generation fields and retry script run.",
                {"log_id": log_id},
                "$.intent_log",
            )
        rel_path = norm(os.path.join("saves", str(save_id), "intent_logs", "{}.json".format(log_id)))
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        write_canonical_json(abs_path, payload)
        rows.append(dict(payload))
        paths.append(rel_path)
    return rows, paths, {}


def _load_script(path: str) -> Tuple[dict, List[dict], Dict[str, object]]:
    payload, err = read_json_object(path)
    if err:
        return {}, [], refusal(
            "REFUSE_SCRIPT_INVALID",
            "script file is missing or invalid JSON object",
            "Provide a valid script JSON payload with an intents array.",
            {"script_path": norm(path)},
            "$.script",
        )
    intents = payload.get("intents")
    if not isinstance(intents, list):
        return {}, [], refusal(
            "REFUSE_SCRIPT_INVALID",
            "script file must contain an intents array",
            "Set script.intents to an ordered array of intent objects.",
            {"script_path": norm(path)},
            "$.script.intents",
        )
    rows: List[dict] = []
    for item in intents:
        if not isinstance(item, dict):
            return {}, [], refusal(
                "REFUSE_SCRIPT_INVALID",
                "script intents must contain only objects",
                "Fix script intent rows to be JSON objects.",
                {"script_path": norm(path)},
                "$.script.intents",
            )
        rows.append(dict(item))
    return payload, rows, {}


def _authority_from_session_spec(repo_root: str, session_spec: dict) -> Tuple[dict, Dict[str, object]]:
    session_context = session_spec.get("authority_context")
    if not isinstance(session_context, dict):
        return {}, refusal(
            "REFUSE_AUTHORITY_CONTEXT_MISSING",
            "SessionSpec authority_context is missing",
            "Populate authority_context in session_spec.json.",
            {"schema_id": "session_spec"},
            "$.authority_context",
        )
    authority_origin = str(session_context.get("authority_origin", "")).strip()
    if authority_origin != "client":
        return {}, refusal(
            "REFUSE_AUTHORITY_ORIGIN_INVALID",
            "authority_origin must be 'client' for headless script execution",
            "Set authority_context.authority_origin to client.",
            {"authority_origin": authority_origin or "<empty>"},
            "$.authority_context.authority_origin",
        )

    authority_context = {
        "authority_origin": "client",
        "experience_id": str(session_spec.get("experience_id", "")),
        "law_profile_id": str(session_context.get("law_profile_id", "")),
        "entitlements": sorted(
            set(str(item).strip() for item in (session_context.get("entitlements") or []) if str(item).strip())
        ),
        "epistemic_scope": dict(session_context.get("epistemic_scope") or {}),
        "privilege_level": str(session_context.get("privilege_level", "")),
    }
    authority_schema_payload = dict(authority_context)
    authority_schema_payload["schema_version"] = "1.0.0"
    authority_check = validate_instance(
        repo_root=repo_root,
        schema_name="authority_context",
        payload=authority_schema_payload,
        strict_top_level=True,
    )
    if not bool(authority_check.get("valid", False)):
        return {}, refusal(
            "REFUSE_AUTHORITY_CONTEXT_INVALID",
            "constructed AuthorityContext failed schema validation",
            "Fix SessionSpec authority_context fields and retry.",
            {"schema_id": "authority_context"},
            "$.authority_context",
        )
    return authority_context, {}


def run_intent_script(
    repo_root: str,
    session_spec_path: str,
    script_path: str,
    bundle_id: str = "",
    compile_if_missing: bool = False,
    workers: int = 1,
    write_state: bool = True,
    logical_shards: int = 1,
    lockfile_path: str = "",
    registries_dir: str = "",
) -> Dict[str, object]:
    worker_count = int(workers)
    if worker_count < 1:
        return refusal(
            "REFUSE_WORKER_COUNT_INVALID",
            "workers must be >= 1",
            "Set --workers to a positive integer.",
            {"workers": str(worker_count)},
            "$.workers",
        )
    logical_shard_count = int(logical_shards)
    if logical_shard_count < 1:
        return refusal(
            "REFUSE_LOGICAL_SHARD_COUNT_INVALID",
            "logical_shards must be >= 1",
            "Set --logical-shards to a positive integer.",
            {"logical_shards": str(logical_shard_count)},
            "$.logical_shards",
        )

    spec_abs = os.path.normpath(os.path.abspath(session_spec_path))
    script_abs = os.path.normpath(os.path.abspath(script_path))
    session_spec, spec_error = _load_schema_validated(repo_root=repo_root, schema_name="session_spec", path=spec_abs)
    if spec_error:
        return spec_error

    bundle_token = str(bundle_id).strip() or str(session_spec.get("bundle_id", "")).strip() or DEFAULT_BUNDLE_ID
    selected_mod_policy_id = str(session_spec.get("mod_policy_id", "")).strip() or DEFAULT_MOD_POLICY_ID
    lock_payload, lock_error = _load_lockfile(
        repo_root=repo_root,
        compile_if_missing=bool(compile_if_missing),
        bundle_id=bundle_token,
        mod_policy_id=selected_mod_policy_id,
        lockfile_path=lockfile_path,
    )
    if lock_error:
        return lock_error
    lock_semantic = validate_lockfile_payload(lock_payload)
    if lock_semantic.get("result") != "complete":
        return refusal(
            "REFUSE_LOCKFILE_HASH_INVALID",
            "lockfile failed deterministic pack_lock_hash validation",
            "Rebuild lockfile and retry script execution.",
            {"bundle_id": bundle_token},
            "$.pack_lock_hash",
        )
    if str(lock_payload.get("bundle_id", "")).strip() != bundle_token:
        return refusal(
            "REFUSE_LOCKFILE_BUNDLE_MISMATCH",
            "lockfile bundle_id does not match requested/session bundle_id",
            "Regenerate lockfile with matching --bundle id.",
            {
                "bundle_id": bundle_token,
                "lockfile_bundle_id": str(lock_payload.get("bundle_id", "")),
            },
            "$.bundle_id",
        )

    registry_check = _validate_registry_hashes(
        repo_root=repo_root,
        lockfile_payload=lock_payload,
        compile_if_missing=bool(compile_if_missing),
        bundle_id=bundle_token,
        mod_policy_id=selected_mod_policy_id,
        registries_dir=registries_dir,
    )
    if registry_check.get("result") != "complete":
        return registry_check
    mod_policy_proof_bundle = proof_bundle_from_lockfile(lock_payload)
    mod_policy_enforcement = validate_saved_mod_policy(
        expected_mod_policy_id=selected_mod_policy_id,
        expected_registry_hash=str(session_spec.get("mod_policy_registry_hash", "")).strip(),
        actual_proof_bundle=mod_policy_proof_bundle,
    )
    if mod_policy_enforcement.get("result") != "complete":
        return mod_policy_enforcement

    registries = lock_payload.get("registries")
    if not isinstance(registries, dict):
        return refusal(
            "REFUSE_LOCKFILE_REGISTRY_SECTION_MISSING",
            "lockfile registries section is missing",
            "Rebuild lockfile with registry hashes and retry.",
            {"bundle_id": bundle_token},
            "$.registries",
        )

    universe_physics_profile_registry, universe_physics_profile_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["universe_physics_profile_registry_hash"],
        expected_hash=str(registries.get("universe_physics_profile_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if universe_physics_profile_registry_error:
        return universe_physics_profile_registry_error
    time_model_registry, time_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["time_model_registry_hash"],
        expected_hash=str(registries.get("time_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if time_model_registry_error:
        return time_model_registry_error
    time_control_policy_registry, time_control_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["time_control_policy_registry_hash"],
        expected_hash=str(registries.get("time_control_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if time_control_policy_registry_error:
        return time_control_policy_registry_error
    dt_quantization_rule_registry, dt_quantization_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["dt_quantization_rule_registry_hash"],
        expected_hash=str(registries.get("dt_quantization_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if dt_quantization_rule_registry_error:
        return dt_quantization_rule_registry_error
    compaction_policy_registry, compaction_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["compaction_policy_registry_hash"],
        expected_hash=str(registries.get("compaction_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if compaction_policy_registry_error:
        return compaction_policy_registry_error
    numeric_precision_policy_registry, numeric_precision_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["numeric_precision_policy_registry_hash"],
        expected_hash=str(registries.get("numeric_precision_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if numeric_precision_policy_registry_error:
        return numeric_precision_policy_registry_error
    tier_taxonomy_registry, tier_taxonomy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["tier_taxonomy_registry_hash"],
        expected_hash=str(registries.get("tier_taxonomy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if tier_taxonomy_registry_error:
        return tier_taxonomy_registry_error
    transition_policy_registry, transition_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["transition_policy_registry_hash"],
        expected_hash=str(registries.get("transition_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if transition_policy_registry_error:
        return transition_policy_registry_error
    arbitration_rule_registry, arbitration_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["arbitration_rule_registry_hash"],
        expected_hash=str(registries.get("arbitration_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if arbitration_rule_registry_error:
        return arbitration_rule_registry_error
    budget_envelope_registry, budget_envelope_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["budget_envelope_registry_hash"],
        expected_hash=str(registries.get("budget_envelope_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if budget_envelope_registry_error:
        return budget_envelope_registry_error
    arbitration_policy_registry, arbitration_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["arbitration_policy_registry_hash"],
        expected_hash=str(registries.get("arbitration_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if arbitration_policy_registry_error:
        return arbitration_policy_registry_error
    inspection_cache_policy_registry, inspection_cache_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["inspection_cache_policy_registry_hash"],
        expected_hash=str(registries.get("inspection_cache_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if inspection_cache_policy_registry_error:
        return inspection_cache_policy_registry_error
    inspection_section_registry, inspection_section_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["inspection_section_registry_hash"],
        expected_hash=str(registries.get("inspection_section_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if inspection_section_registry_error:
        return inspection_section_registry_error
    boundary_model_registry, boundary_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["boundary_model_registry_hash"],
        expected_hash=str(registries.get("boundary_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if boundary_model_registry_error:
        return boundary_model_registry_error
    conservation_contract_set_registry, conservation_contract_set_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["conservation_contract_set_registry_hash"],
        expected_hash=str(registries.get("conservation_contract_set_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if conservation_contract_set_registry_error:
        return conservation_contract_set_registry_error
    quantity_registry, quantity_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["quantity_registry_hash"],
        expected_hash=str(registries.get("quantity_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if quantity_registry_error:
        return quantity_registry_error
    exception_type_registry, exception_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["exception_type_registry_hash"],
        expected_hash=str(registries.get("exception_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if exception_type_registry_error:
        return exception_type_registry_error
    base_dimension_registry, base_dimension_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["base_dimension_registry_hash"],
        expected_hash=str(registries.get("base_dimension_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if base_dimension_registry_error:
        return base_dimension_registry_error
    dimension_registry, dimension_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["dimension_registry_hash"],
        expected_hash=str(registries.get("dimension_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if dimension_registry_error:
        return dimension_registry_error
    unit_registry, unit_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["unit_registry_hash"],
        expected_hash=str(registries.get("unit_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if unit_registry_error:
        return unit_registry_error
    quantity_type_registry, quantity_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["quantity_type_registry_hash"],
        expected_hash=str(registries.get("quantity_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if quantity_type_registry_error:
        return quantity_type_registry_error
    element_registry, element_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["element_registry_hash"],
        expected_hash=str(registries.get("element_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if element_registry_error:
        return element_registry_error
    compound_registry, compound_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["compound_registry_hash"],
        expected_hash=str(registries.get("compound_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if compound_registry_error:
        return compound_registry_error
    mixture_registry, mixture_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["mixture_registry_hash"],
        expected_hash=str(registries.get("mixture_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if mixture_registry_error:
        return mixture_registry_error
    material_class_registry, material_class_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["material_class_registry_hash"],
        expected_hash=str(registries.get("material_class_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if material_class_registry_error:
        return material_class_registry_error
    quality_distribution_registry, quality_distribution_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["quality_distribution_registry_hash"],
        expected_hash=str(registries.get("quality_distribution_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if quality_distribution_registry_error:
        return quality_distribution_registry_error
    part_class_registry, part_class_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["part_class_registry_hash"],
        expected_hash=str(registries.get("part_class_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if part_class_registry_error:
        return part_class_registry_error
    connection_type_registry, connection_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["connection_type_registry_hash"],
        expected_hash=str(registries.get("connection_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if connection_type_registry_error:
        return connection_type_registry_error
    blueprint_registry, blueprint_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["blueprint_registry_hash"],
        expected_hash=str(registries.get("blueprint_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if blueprint_registry_error:
        return blueprint_registry_error
    interior_volume_type_registry, interior_volume_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["interior_volume_type_registry_hash"],
        expected_hash=str(registries.get("interior_volume_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if interior_volume_type_registry_error:
        return interior_volume_type_registry_error
    portal_type_registry, portal_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["portal_type_registry_hash"],
        expected_hash=str(registries.get("portal_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if portal_type_registry_error:
        return portal_type_registry_error
    compartment_flow_policy_registry, compartment_flow_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["compartment_flow_policy_registry_hash"],
        expected_hash=str(registries.get("compartment_flow_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if compartment_flow_policy_registry_error:
        return compartment_flow_policy_registry_error
    portal_flow_template_registry, portal_flow_template_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["portal_flow_template_registry_hash"],
        expected_hash=str(registries.get("portal_flow_template_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if portal_flow_template_registry_error:
        return portal_flow_template_registry_error
    logistics_routing_rule_registry, logistics_routing_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["logistics_routing_rule_registry_hash"],
        expected_hash=str(registries.get("logistics_routing_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if logistics_routing_rule_registry_error:
        return logistics_routing_rule_registry_error
    logistics_graph_registry, logistics_graph_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["logistics_graph_registry_hash"],
        expected_hash=str(registries.get("logistics_graph_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if logistics_graph_registry_error:
        return logistics_graph_registry_error
    provenance_event_type_registry, provenance_event_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["provenance_event_type_registry_hash"],
        expected_hash=str(registries.get("provenance_event_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if provenance_event_type_registry_error:
        return provenance_event_type_registry_error
    construction_policy_registry, construction_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["construction_policy_registry_hash"],
        expected_hash=str(registries.get("construction_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if construction_policy_registry_error:
        return construction_policy_registry_error
    commitment_type_registry, commitment_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["commitment_type_registry_hash"],
        expected_hash=str(registries.get("commitment_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if commitment_type_registry_error:
        return commitment_type_registry_error
    causality_strictness_registry, causality_strictness_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["causality_strictness_registry_hash"],
        expected_hash=str(registries.get("causality_strictness_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if causality_strictness_registry_error:
        return causality_strictness_registry_error

    law_registry, law_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["law_registry_hash"],
        expected_hash=str(registries.get("law_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if law_registry_error:
        return law_registry_error
    lens_registry, lens_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["lens_registry_hash"],
        expected_hash=str(registries.get("lens_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if lens_registry_error:
        return lens_registry_error
    experience_registry, experience_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["experience_registry_hash"],
        expected_hash=str(registries.get("experience_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if experience_registry_error:
        return experience_registry_error
    governance_type_registry, governance_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["governance_type_registry_hash"],
        expected_hash=str(registries.get("governance_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if governance_type_registry_error:
        return governance_type_registry_error
    diplomatic_state_registry, diplomatic_state_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["diplomatic_state_registry_hash"],
        expected_hash=str(registries.get("diplomatic_state_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if diplomatic_state_registry_error:
        return diplomatic_state_registry_error
    cohort_mapping_policy_registry, cohort_mapping_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["cohort_mapping_policy_registry_hash"],
        expected_hash=str(registries.get("cohort_mapping_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if cohort_mapping_policy_registry_error:
        return cohort_mapping_policy_registry_error
    order_type_registry, order_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["order_type_registry_hash"],
        expected_hash=str(registries.get("order_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if order_type_registry_error:
        return order_type_registry_error
    role_registry, role_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["role_registry_hash"],
        expected_hash=str(registries.get("role_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if role_registry_error:
        return role_registry_error
    institution_type_registry, institution_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["institution_type_registry_hash"],
        expected_hash=str(registries.get("institution_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if institution_type_registry_error:
        return institution_type_registry_error
    demography_policy_registry, demography_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["demography_policy_registry_hash"],
        expected_hash=str(registries.get("demography_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if demography_policy_registry_error:
        return demography_policy_registry_error
    death_model_registry, death_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["death_model_registry_hash"],
        expected_hash=str(registries.get("death_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if death_model_registry_error:
        return death_model_registry_error
    birth_model_registry, birth_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["birth_model_registry_hash"],
        expected_hash=str(registries.get("birth_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if birth_model_registry_error:
        return birth_model_registry_error
    migration_model_registry, migration_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["migration_model_registry_hash"],
        expected_hash=str(registries.get("migration_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if migration_model_registry_error:
        return migration_model_registry_error
    astronomy_registry, astronomy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["astronomy_catalog_index_hash"],
        expected_hash=str(registries.get("astronomy_catalog_index_hash", "")),
        registries_dir=registries_dir,
    )
    if astronomy_registry_error:
        return astronomy_registry_error
    site_registry, site_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["site_registry_index_hash"],
        expected_hash=str(registries.get("site_registry_index_hash", "")),
        registries_dir=registries_dir,
    )
    if site_registry_error:
        return site_registry_error
    ephemeris_registry, ephemeris_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["ephemeris_registry_hash"],
        expected_hash=str(registries.get("ephemeris_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if ephemeris_registry_error:
        return ephemeris_registry_error
    terrain_tile_registry, terrain_tile_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["terrain_tile_registry_hash"],
        expected_hash=str(registries.get("terrain_tile_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if terrain_tile_registry_error:
        return terrain_tile_registry_error
    activation_policy_registry, activation_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["activation_policy_registry_hash"],
        expected_hash=str(registries.get("activation_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if activation_policy_registry_error:
        return activation_policy_registry_error
    budget_policy_registry, budget_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["budget_policy_registry_hash"],
        expected_hash=str(registries.get("budget_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if budget_policy_registry_error:
        return budget_policy_registry_error
    fidelity_policy_registry, fidelity_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["fidelity_policy_registry_hash"],
        expected_hash=str(registries.get("fidelity_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if fidelity_policy_registry_error:
        return fidelity_policy_registry_error
    perception_interest_policy_registry, perception_interest_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["perception_interest_policy_registry_hash"],
        expected_hash=str(registries.get("perception_interest_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if perception_interest_policy_registry_error:
        return perception_interest_policy_registry_error
    epistemic_policy_registry, epistemic_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["epistemic_policy_registry_hash"],
        expected_hash=str(registries.get("epistemic_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if epistemic_policy_registry_error:
        return epistemic_policy_registry_error
    retention_policy_registry, retention_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["retention_policy_registry_hash"],
        expected_hash=str(registries.get("retention_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if retention_policy_registry_error:
        return retention_policy_registry_error
    decay_model_registry, decay_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["decay_model_registry_hash"],
        expected_hash=str(registries.get("decay_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if decay_model_registry_error:
        return decay_model_registry_error
    eviction_rule_registry, eviction_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["eviction_rule_registry_hash"],
        expected_hash=str(registries.get("eviction_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if eviction_rule_registry_error:
        return eviction_rule_registry_error
    view_mode_registry, view_mode_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["view_mode_registry_hash"],
        expected_hash=str(registries.get("view_mode_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if view_mode_registry_error:
        return view_mode_registry_error
    view_policy_registry, view_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["view_policy_registry_hash"],
        expected_hash=str(registries.get("view_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if view_policy_registry_error:
        return view_policy_registry_error
    instrument_type_registry, instrument_type_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["instrument_type_registry_hash"],
        expected_hash=str(registries.get("instrument_type_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if instrument_type_registry_error:
        return instrument_type_registry_error
    calibration_model_registry, calibration_model_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["calibration_model_registry_hash"],
        expected_hash=str(registries.get("calibration_model_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if calibration_model_registry_error:
        return calibration_model_registry_error
    render_proxy_registry, render_proxy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["render_proxy_registry_hash"],
        expected_hash=str(registries.get("render_proxy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if render_proxy_registry_error:
        return render_proxy_registry_error
    cosmetic_registry, cosmetic_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["cosmetic_registry_hash"],
        expected_hash=str(registries.get("cosmetic_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if cosmetic_registry_error:
        return cosmetic_registry_error
    cosmetic_policy_registry, cosmetic_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["cosmetic_policy_registry_hash"],
        expected_hash=str(registries.get("cosmetic_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if cosmetic_policy_registry_error:
        return cosmetic_policy_registry_error
    render_primitive_registry, render_primitive_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["render_primitive_registry_hash"],
        expected_hash=str(registries.get("render_primitive_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if render_primitive_registry_error:
        return render_primitive_registry_error
    procedural_material_template_registry, procedural_material_template_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["procedural_material_template_registry_hash"],
        expected_hash=str(registries.get("procedural_material_template_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if procedural_material_template_registry_error:
        return procedural_material_template_registry_error
    label_policy_registry, label_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["label_policy_registry_hash"],
        expected_hash=str(registries.get("label_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if label_policy_registry_error:
        return label_policy_registry_error
    lod_policy_registry, lod_policy_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["lod_policy_registry_hash"],
        expected_hash=str(registries.get("lod_policy_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if lod_policy_registry_error:
        return lod_policy_registry_error
    representation_rule_registry, representation_rule_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["representation_rule_registry_hash"],
        expected_hash=str(registries.get("representation_rule_registry_hash", "")),
        registries_dir=registries_dir,
    )
    if representation_rule_registry_error:
        return representation_rule_registry_error

    save_id = str(session_spec.get("save_id", "")).strip()
    if not save_id:
        return refusal(
            "REFUSE_SAVE_ID_MISSING",
            "SessionSpec save_id is missing",
            "Fix session_spec.json save_id and retry.",
            {"schema_id": "session_spec"},
            "$.save_id",
        )
    save_dir = os.path.join(repo_root, "saves", save_id)
    identity_path = os.path.join(save_dir, "universe_identity.json")
    state_path = os.path.join(save_dir, "universe_state.json")
    universe_identity, identity_error = _load_schema_validated(
        repo_root=repo_root,
        schema_name="universe_identity",
        path=identity_path,
    )
    if identity_error:
        return identity_error
    expected_identity_hash = identity_hash_for_payload(universe_identity)
    if str(universe_identity.get("identity_hash", "")).strip() != expected_identity_hash:
        return refusal(
            "REFUSE_UNIVERSE_IDENTITY_MUTATION",
            "UniverseIdentity identity_hash mismatch detected",
            "Restore canonical universe_identity.json or regenerate the save.",
            {"save_id": save_id},
            "$.identity_hash",
        )
    contract_enforcement = enforce_session_contract_bundle(
        repo_root=repo_root,
        session_spec=session_spec,
        universe_identity=universe_identity,
        identity_path=identity_path,
        replay_mode=True,
    )
    if contract_enforcement.get("result") != "complete":
        return contract_enforcement
    identity_physics_profile_id = str(universe_identity.get("physics_profile_id", "")).strip()
    if not identity_physics_profile_id:
        return refusal(
            "refusal.physics_profile_missing",
            "UniverseIdentity is missing physics_profile_id",
            "Regenerate universe identity with an explicit physics profile id.",
            {"save_id": save_id},
            "$.physics_profile_id",
        )
    identity_generator_version_id = (
        str(universe_identity.get("generator_version_id", "")).strip() or DEFAULT_GENERATOR_VERSION_ID
    )
    identity_realism_profile_id = (
        str(universe_identity.get("realism_profile_id", "")).strip() or DEFAULT_REALISM_PROFILE_ID
    )
    selected_physics_profile, selected_physics_profile_error = select_physics_profile(
        physics_profile_id=identity_physics_profile_id,
        profile_registry=universe_physics_profile_registry,
    )
    if selected_physics_profile_error:
        return selected_physics_profile_error
    identity_conservation_contract_set_id = (
        str(selected_physics_profile.get("conservation_contract_set_id", "")).strip() or "contracts.null"
    )
    identity_time_control_policy_id = str(session_spec.get("time_control_policy_id", "")).strip()
    (
        selected_time_control_policy,
        selected_dt_quantization_rule,
        selected_compaction_policy,
        selected_time_model,
        selected_time_control_policy_error,
    ) = _select_time_control_policy(
        time_control_policy_registry=time_control_policy_registry,
        dt_quantization_rule_registry=dt_quantization_rule_registry,
        compaction_policy_registry=compaction_policy_registry,
        time_model_registry=time_model_registry,
        selected_physics_profile=selected_physics_profile,
        requested_time_control_policy_id=identity_time_control_policy_id,
    )
    if selected_time_control_policy_error:
        return selected_time_control_policy_error
    selected_transition_policy, selected_transition_policy_error = _select_transition_policy(
        transition_policy_registry=transition_policy_registry,
        selected_physics_profile=selected_physics_profile,
        requested_transition_policy_id="",
    )
    if selected_transition_policy_error:
        return selected_transition_policy_error
    universe_state, state_error = _load_schema_validated(repo_root=repo_root, schema_name="universe_state", path=state_path)
    if state_error:
        return state_error

    authority_context, authority_error = _authority_from_session_spec(repo_root=repo_root, session_spec=session_spec)
    if authority_error:
        return authority_error
    law_profile, law_profile_error = _select_law_profile(
        law_registry=law_registry,
        law_profile_id=str(authority_context.get("law_profile_id", "")),
    )
    if law_profile_error:
        return law_profile_error
    lens_profile, lens_profile_error = _select_lens_profile(
        lens_registry=lens_registry,
        experience_registry=experience_registry,
        experience_id=str(session_spec.get("experience_id", "")),
        law_profile=law_profile,
    )
    if lens_profile_error:
        return lens_profile_error
    budget_policy, budget_policy_error = _select_policy_entry(
        registry_payload=budget_policy_registry,
        key="budget_policies",
        policy_id=str(session_spec.get("budget_policy_id", "")),
        refusal_code="BUDGET_POLICY_NOT_FOUND",
        registry_file=REGISTRY_FILE_MAP["budget_policy_registry_hash"],
    )
    if budget_policy_error:
        return budget_policy_error
    fidelity_policy, fidelity_policy_error = _select_policy_entry(
        registry_payload=fidelity_policy_registry,
        key="fidelity_policies",
        policy_id=str(session_spec.get("fidelity_policy_id", "")),
        refusal_code="FIDELITY_POLICY_NOT_FOUND",
        registry_file=REGISTRY_FILE_MAP["fidelity_policy_registry_hash"],
    )
    if fidelity_policy_error:
        return fidelity_policy_error
    activation_policy, activation_policy_error = _select_policy_entry(
        registry_payload=activation_policy_registry,
        key="activation_policies",
        policy_id=str(budget_policy.get("activation_policy_id", "")),
        refusal_code="ACTIVATION_POLICY_NOT_FOUND",
        registry_file=REGISTRY_FILE_MAP["activation_policy_registry_hash"],
    )
    if activation_policy_error:
        return activation_policy_error

    script_payload, intents, script_error = _load_script(script_abs)
    if script_error:
        return script_error
    representation_state = {
        "assignments": {},
        "events": [],
    }
    script_policy_context = {
        "save_id": str(save_id),
        "physics_profile_id": identity_physics_profile_id,
        "conservation_contract_set_id": identity_conservation_contract_set_id,
        "time_control_policy_id": str(selected_time_control_policy.get("time_control_policy_id", "")),
        "dt_quantization_rule_id": str(selected_dt_quantization_rule.get("dt_rule_id", "")),
        "compaction_policy_id": str(selected_compaction_policy.get("compaction_policy_id", "")),
        "time_model_id": str(selected_time_model.get("time_model_id", "")),
        "tier_taxonomy_id": str(selected_physics_profile.get("tier_taxonomy_id", "")),
        "transition_policy_id": str(selected_transition_policy.get("transition_policy_id", "")),
        "budget_envelope_id": str(selected_physics_profile.get("budget_envelope_id", "")),
        "arbitration_policy_id": str(selected_physics_profile.get("arbitration_policy_id", "")),
        "inspection_cache_policy_id": str(selected_physics_profile.get("inspection_cache_policy_id", "")),
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "active_shard_id": "shard.0",
        "activation_policy": activation_policy,
        "budget_policy": budget_policy,
        "fidelity_policy": fidelity_policy,
        "transition_policy": selected_transition_policy,
        "time_control_policy": selected_time_control_policy,
        "dt_quantization_rule": selected_dt_quantization_rule,
        "compaction_policy": selected_compaction_policy,
        "time_model": selected_time_model,
        "transition_policy_registry": transition_policy_registry,
        "arbitration_rule_registry": arbitration_rule_registry,
        "budget_envelope_registry": budget_envelope_registry,
        "arbitration_policy_registry": arbitration_policy_registry,
        "inspection_cache_policy_registry": inspection_cache_policy_registry,
        "inspection_section_registry": inspection_section_registry,
        "time_control_policy_registry": time_control_policy_registry,
        "dt_quantization_rule_registry": dt_quantization_rule_registry,
        "compaction_policy_registry": compaction_policy_registry,
        "conservation_contract_set_registry": conservation_contract_set_registry,
        "quantity_registry": quantity_registry,
        "exception_type_registry": exception_type_registry,
        "base_dimension_registry": base_dimension_registry,
        "dimension_registry": dimension_registry,
        "unit_registry": unit_registry,
        "quantity_type_registry": quantity_type_registry,
        "element_registry": element_registry,
        "compound_registry": compound_registry,
        "mixture_registry": mixture_registry,
        "material_class_registry": material_class_registry,
        "quality_distribution_registry": quality_distribution_registry,
        "part_class_registry": part_class_registry,
        "connection_type_registry": connection_type_registry,
        "blueprint_registry": blueprint_registry,
        "interior_volume_type_registry": interior_volume_type_registry,
        "portal_type_registry": portal_type_registry,
        "compartment_flow_policy_registry": compartment_flow_policy_registry,
        "portal_flow_template_registry": portal_flow_template_registry,
        "logistics_routing_rule_registry": logistics_routing_rule_registry,
        "logistics_graph_registry": logistics_graph_registry,
        "provenance_event_type_registry": provenance_event_type_registry,
        "construction_policy_registry": construction_policy_registry,
        "commitment_type_registry": commitment_type_registry,
        "causality_strictness_registry": causality_strictness_registry,
        "governance_type_registry": governance_type_registry,
        "diplomatic_state_registry": diplomatic_state_registry,
        "cohort_mapping_policy_registry": cohort_mapping_policy_registry,
        "order_type_registry": order_type_registry,
        "role_registry": role_registry,
        "institution_type_registry": institution_type_registry,
        "demography_policy_registry": demography_policy_registry,
        "death_model_registry": death_model_registry,
        "birth_model_registry": birth_model_registry,
        "migration_model_registry": migration_model_registry,
        "render_proxy_registry": render_proxy_registry,
        "cosmetic_registry": cosmetic_registry,
        "cosmetic_policy_registry": cosmetic_policy_registry,
        "render_primitive_registry": render_primitive_registry,
        "procedural_material_template_registry": procedural_material_template_registry,
        "label_policy_registry": label_policy_registry,
        "lod_policy_registry": lod_policy_registry,
        "representation_rule_registry": representation_rule_registry,
        "cosmetic_policy_id": "policy.cosmetics.private_relaxed",
        "representation_state": representation_state,
        "resolved_packs": list(lock_payload.get("resolved_packs") or []),
        "parameter_bundle_id": str(session_spec.get("parameter_bundle_id", "")),
    }
    script_result = replay_intent_script_srz(
        repo_root=repo_root,
        universe_state=universe_state,
        law_profile=law_profile,
        authority_context=authority_context,
        intents=intents,
        navigation_indices={
            "astronomy_catalog_index": astronomy_registry,
            "site_registry_index": site_registry,
            "ephemeris_registry": ephemeris_registry,
            "terrain_tile_registry": terrain_tile_registry,
            "view_mode_registry": view_mode_registry,
            "view_policy_registry": view_policy_registry,
        },
        policy_context=script_policy_context,
        pack_lock_hash=str(lock_payload.get("pack_lock_hash", "")),
        registry_hashes=dict(registries),
        worker_count=int(worker_count),
        logical_shards=int(logical_shard_count),
    )
    if script_result.get("result") != "complete":
        return script_result
    updated_state = dict(script_result.get("universe_state") or {})
    state_hash_anchors = list(script_result.get("state_hash_anchors") or [])
    tick_hash_anchors = list(script_result.get("tick_hash_anchors") or [])
    checkpoint_hashes = list(script_result.get("checkpoint_hashes") or [])
    checkpoint_snapshots = list(script_result.get("checkpoint_snapshots") or [])
    accepted_envelopes = list(script_result.get("accepted_envelopes") or [])
    composite_hash = str(script_result.get("composite_hash", ""))
    final_state_hash = str(script_result.get("final_state_hash", ""))
    srz = dict(script_result.get("srz") or {})
    worker_effective = int((srz.get("worker_count_effective", 1) or 1))
    updated_state = stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="save_file",
        payload=updated_state,
        semantic_contract_bundle_hash=str(contract_enforcement.get("contract_bundle_hash", "")).strip(),
    )

    updated_state_valid = validate_instance(
        repo_root=repo_root,
        schema_name="universe_state",
        payload=updated_state,
        strict_top_level=True,
    )
    if not bool(updated_state_valid.get("valid", False)):
        return refusal(
            "REFUSE_UNIVERSE_STATE_INVALID",
            "post-process UniverseState failed schema validation",
            "Fix process runtime outputs to match schemas/universe_state.schema.json.",
            {"schema_id": "universe_state"},
            "$.universe_state",
        )

    checkpoint_artifacts, checkpoint_artifact_paths, checkpoint_artifact_error = _write_checkpoint_artifacts(
        repo_root=repo_root,
        save_id=save_id,
        pack_lock_hash=str(lock_payload.get("pack_lock_hash", "")),
        physics_profile_id=identity_physics_profile_id,
        registry_hashes=dict(registries),
        checkpoint_snapshots=checkpoint_snapshots,
    )
    if checkpoint_artifact_error:
        return checkpoint_artifact_error
    intent_log_artifacts, intent_log_artifact_paths, intent_log_artifact_error = _write_intent_log_artifacts(
        repo_root=repo_root,
        save_id=save_id,
        accepted_envelopes=accepted_envelopes,
    )
    if intent_log_artifact_error:
        return intent_log_artifact_error

    if write_state:
        write_canonical_json(state_path, updated_state)

    truth_model = build_truth_model(
        universe_identity=universe_identity,
        universe_state=updated_state,
        lockfile_payload=lock_payload,
        identity_path=norm(os.path.relpath(identity_path, repo_root)),
        state_path=norm(os.path.relpath(state_path, repo_root)),
        registry_payloads={
            "universe_physics_profile_registry": universe_physics_profile_registry,
            "time_model_registry": time_model_registry,
            "time_control_policy_registry": time_control_policy_registry,
            "dt_quantization_rule_registry": dt_quantization_rule_registry,
            "compaction_policy_registry": compaction_policy_registry,
            "numeric_precision_policy_registry": numeric_precision_policy_registry,
            "tier_taxonomy_registry": tier_taxonomy_registry,
            "transition_policy_registry": transition_policy_registry,
            "arbitration_rule_registry": arbitration_rule_registry,
            "boundary_model_registry": boundary_model_registry,
            "conservation_contract_set_registry": conservation_contract_set_registry,
            "quantity_registry": quantity_registry,
            "exception_type_registry": exception_type_registry,
            "base_dimension_registry": base_dimension_registry,
            "dimension_registry": dimension_registry,
            "unit_registry": unit_registry,
            "quantity_type_registry": quantity_type_registry,
            "element_registry": element_registry,
            "compound_registry": compound_registry,
            "mixture_registry": mixture_registry,
            "material_class_registry": material_class_registry,
            "quality_distribution_registry": quality_distribution_registry,
            "part_class_registry": part_class_registry,
            "connection_type_registry": connection_type_registry,
            "blueprint_registry": blueprint_registry,
            "interior_volume_type_registry": interior_volume_type_registry,
            "portal_type_registry": portal_type_registry,
            "compartment_flow_policy_registry": compartment_flow_policy_registry,
            "portal_flow_template_registry": portal_flow_template_registry,
            "logistics_routing_rule_registry": logistics_routing_rule_registry,
            "logistics_graph_registry": logistics_graph_registry,
            "provenance_event_type_registry": provenance_event_type_registry,
            "construction_policy_registry": construction_policy_registry,
            "commitment_type_registry": commitment_type_registry,
            "causality_strictness_registry": causality_strictness_registry,
            "astronomy_catalog_index": astronomy_registry,
            "site_registry_index": site_registry,
            "ephemeris_registry": ephemeris_registry,
            "terrain_tile_registry": terrain_tile_registry,
            "governance_type_registry": governance_type_registry,
            "diplomatic_state_registry": diplomatic_state_registry,
            "cohort_mapping_policy_registry": cohort_mapping_policy_registry,
            "order_type_registry": order_type_registry,
            "role_registry": role_registry,
            "institution_type_registry": institution_type_registry,
            "demography_policy_registry": demography_policy_registry,
            "death_model_registry": death_model_registry,
            "birth_model_registry": birth_model_registry,
            "migration_model_registry": migration_model_registry,
            "activation_policy_registry": activation_policy_registry,
            "budget_policy_registry": budget_policy_registry,
            "fidelity_policy_registry": fidelity_policy_registry,
            "perception_interest_policy_registry": perception_interest_policy_registry,
            "epistemic_policy_registry": epistemic_policy_registry,
            "retention_policy_registry": retention_policy_registry,
            "decay_model_registry": decay_model_registry,
            "eviction_rule_registry": eviction_rule_registry,
            "view_mode_registry": view_mode_registry,
            "view_policy_registry": view_policy_registry,
            "instrument_type_registry": instrument_type_registry,
            "calibration_model_registry": calibration_model_registry,
            "render_proxy_registry": render_proxy_registry,
            "cosmetic_registry": cosmetic_registry,
            "cosmetic_policy_registry": cosmetic_policy_registry,
            "render_primitive_registry": render_primitive_registry,
            "procedural_material_template_registry": procedural_material_template_registry,
            "label_policy_registry": label_policy_registry,
            "lod_policy_registry": lod_policy_registry,
            "representation_rule_registry": representation_rule_registry,
            "representation_state": dict(representation_state),
        },
    )
    observation = observe_truth(
        truth_model=truth_model,
        lens=lens_profile,
        law_profile=law_profile,
        authority_context=authority_context,
        viewpoint_id="viewpoint.client.{}".format(save_id),
    )
    if observation.get("result") != "complete":
        return observation
    perceived_model = dict(observation.get("perceived_model") or {})
    perceived_hash = str(observation.get("perceived_model_hash", ""))
    render = build_render_model(
        perceived_model,
        registry_payloads={
            "render_primitive_registry": render_primitive_registry,
            "procedural_material_template_registry": procedural_material_template_registry,
            "label_policy_registry": label_policy_registry,
            "lod_policy_registry": lod_policy_registry,
            "representation_rule_registry": representation_rule_registry,
        },
        pack_lock_hash=str(lock_payload.get("pack_lock_hash", "")),
        physics_profile_id=str(universe_identity.get("physics_profile_id", "")),
    )
    if render.get("result") != "complete":
        return refusal(
            "RENDER_MODEL_BUILD_FAILED",
            "failed to derive RenderModel from PerceivedModel after script execution",
            "Inspect observation outputs and renderer adapter contract.",
            {"save_id": save_id},
            "$.render_model",
        )
    render_hash = str(render.get("render_model_hash", ""))

    simulation_time = updated_state.get("simulation_time")
    start_tick = int((universe_state.get("simulation_time") or {}).get("tick", 0))
    stop_tick = int((simulation_time or {}).get("tick", 0)) if isinstance(simulation_time, dict) else start_tick
    session_spec_hash = canonical_sha256(session_spec)
    script_hash = canonical_sha256(script_payload)
    registry_hashes = dict((lock_payload.get("registries") or {}))
    deterministic_fields = {
        "schema_version": "1.0.0",
        "save_id": save_id,
        "bundle_id": bundle_token,
        "session_spec_hash": session_spec_hash,
        "script_hash": script_hash,
        "script_step_count": len(intents),
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "contract_bundle_hash": str(contract_enforcement.get("contract_bundle_hash", "")),
        "semantic_contract_registry_hash": str(contract_enforcement.get("semantic_contract_registry_hash", "")),
        "semantic_contract_proof_bundle": dict(contract_enforcement.get("proof_bundle") or {}),
        "mod_policy_id": selected_mod_policy_id,
        "mod_policy_registry_hash": str(mod_policy_proof_bundle.get("mod_policy_registry_hash", "")).strip(),
        "mod_policy_proof_bundle": dict(mod_policy_proof_bundle),
        "overlay_manifest_hash": str(updated_state.get("overlay_manifest_hash", "")).strip(),
        "worldgen_request_hash_chain": str(updated_state.get("worldgen_request_hash_chain", "")).strip(),
        "worldgen_result_hash_chain": str(updated_state.get("worldgen_result_hash_chain", "")).strip(),
        "refinement_request_hash_chain": str(updated_state.get("refinement_request_hash_chain", "")).strip(),
        "refinement_cache_hash_chain": str(updated_state.get("refinement_cache_hash_chain", "")).strip(),
        "registry_hashes": registry_hashes,
        "state_hash_anchors": state_hash_anchors,
        "tick_hash_anchors": tick_hash_anchors,
        "checkpoint_hashes": checkpoint_hashes,
        "checkpoint_artifact_hashes": [canonical_sha256(item) for item in checkpoint_artifacts],
        "checkpoint_artifact_paths": checkpoint_artifact_paths,
        "intent_log_hashes": [str(item.get("log_hash", "")) for item in intent_log_artifacts],
        "intent_log_artifact_paths": intent_log_artifact_paths,
        "composite_hash": composite_hash,
        "final_state_hash": final_state_hash,
        "physics_profile_id": identity_physics_profile_id,
        "generator_version_id": identity_generator_version_id,
        "realism_profile_id": identity_realism_profile_id,
        "conservation_contract_set_id": identity_conservation_contract_set_id,
        "time_control_policy_id": str(selected_time_control_policy.get("time_control_policy_id", "")),
        "dt_quantization_rule_id": str(selected_dt_quantization_rule.get("dt_rule_id", "")),
        "compaction_policy_id": str(selected_compaction_policy.get("compaction_policy_id", "")),
        "time_model_id": str(selected_time_model.get("time_model_id", "")),
        "performance_state": dict(updated_state.get("performance_state") or {}),
        "selected_lens_id": str(lens_profile.get("lens_id", "")),
        "budget_policy_id": str(budget_policy.get("policy_id", "")),
        "fidelity_policy_id": str(fidelity_policy.get("policy_id", "")),
        "activation_policy_id": str(activation_policy.get("policy_id", "")),
        "perceived_model_hash": perceived_hash,
        "render_model_hash": render_hash,
        "start_tick": start_tick,
        "stop_tick": stop_tick,
    }
    deterministic_fields_hash = canonical_sha256(deterministic_fields)
    run_id = "run.script.{}".format(deterministic_fields_hash[:16])

    now = now_utc_iso()
    run_meta = dict(deterministic_fields)
    lock_path_for_meta = _resolve_lockfile_path(repo_root, lockfile_path)
    run_meta.update(
        {
            "run_id": run_id,
            "session_spec_path": norm(os.path.relpath(spec_abs, repo_root)),
            "script_path": norm(os.path.relpath(script_abs, repo_root)),
            "universe_identity_path": norm(os.path.relpath(identity_path, repo_root)),
            "universe_state_path": norm(os.path.relpath(state_path, repo_root)),
            "lockfile_path": norm(os.path.relpath(lock_path_for_meta, repo_root)),
            "workers_requested": int(worker_count),
            "workers_effective": int(worker_effective),
            "logical_shards_requested": int(logical_shard_count),
            "srz": srz,
            "started_utc": now,
            "stopped_utc": now_utc_iso(),
            "deterministic_fields_hash": deterministic_fields_hash,
        }
    )
    run_meta_dir = os.path.join(save_dir, "run_meta")
    run_meta_path = os.path.join(run_meta_dir, "{}.json".format(run_id))
    write_canonical_json(run_meta_path, run_meta)
    return {
        "result": "complete",
        "save_id": save_id,
        "bundle_id": bundle_token,
        "run_id": run_id,
        "run_meta_path": norm(os.path.relpath(run_meta_path, repo_root)),
        "session_spec_hash": session_spec_hash,
        "script_hash": script_hash,
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "contract_bundle_hash": str(contract_enforcement.get("contract_bundle_hash", "")),
        "semantic_contract_registry_hash": str(contract_enforcement.get("semantic_contract_registry_hash", "")),
        "semantic_contract_proof_bundle": dict(contract_enforcement.get("proof_bundle") or {}),
        "mod_policy_id": selected_mod_policy_id,
        "mod_policy_registry_hash": str(mod_policy_proof_bundle.get("mod_policy_registry_hash", "")).strip(),
        "mod_policy_proof_bundle": dict(mod_policy_proof_bundle),
        "overlay_manifest_hash": str(updated_state.get("overlay_manifest_hash", "")).strip(),
        "worldgen_request_hash_chain": str(updated_state.get("worldgen_request_hash_chain", "")).strip(),
        "worldgen_result_hash_chain": str(updated_state.get("worldgen_result_hash_chain", "")).strip(),
        "refinement_request_hash_chain": str(updated_state.get("refinement_request_hash_chain", "")).strip(),
        "refinement_cache_hash_chain": str(updated_state.get("refinement_cache_hash_chain", "")).strip(),
        "registry_hashes": registry_hashes,
        "physics_profile_id": identity_physics_profile_id,
        "generator_version_id": identity_generator_version_id,
        "realism_profile_id": identity_realism_profile_id,
        "conservation_contract_set_id": identity_conservation_contract_set_id,
        "time_control_policy_id": str(selected_time_control_policy.get("time_control_policy_id", "")),
        "state_hash_anchors": state_hash_anchors,
        "tick_hash_anchors": tick_hash_anchors,
        "checkpoint_hashes": checkpoint_hashes,
        "checkpoint_artifact_hashes": [canonical_sha256(item) for item in checkpoint_artifacts],
        "checkpoint_artifact_paths": checkpoint_artifact_paths,
        "intent_log_hashes": [str(item.get("log_hash", "")) for item in intent_log_artifacts],
        "intent_log_artifact_paths": intent_log_artifact_paths,
        "composite_hash": composite_hash,
        "final_state_hash": final_state_hash,
        "performance_state": dict(updated_state.get("performance_state") or {}),
        "selected_lens_id": str(lens_profile.get("lens_id", "")),
        "perceived_model_hash": perceived_hash,
        "render_model_hash": render_hash,
        "start_tick": start_tick,
        "stop_tick": stop_tick,
        "deterministic_fields_hash": deterministic_fields_hash,
        "workers_requested": int(worker_count),
        "workers_effective": int(worker_effective),
        "logical_shards_requested": int(logical_shard_count),
        "srz": srz,
    }
