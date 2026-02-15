"""Deterministic headless intent-script runner for lab camera/time process flows."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload

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
    _validate_registry_hashes,
)
from .scheduler import replay_intent_script_srz


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
    lock_payload, lock_error = _load_lockfile(
        repo_root=repo_root,
        compile_if_missing=bool(compile_if_missing),
        bundle_id=bundle_token,
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
        registries_dir=registries_dir,
    )
    if registry_check.get("result") != "complete":
        return registry_check

    registries = lock_payload.get("registries")
    if not isinstance(registries, dict):
        return refusal(
            "REFUSE_LOCKFILE_REGISTRY_SECTION_MISSING",
            "lockfile registries section is missing",
            "Rebuild lockfile with registry hashes and retry.",
            {"bundle_id": bundle_token},
            "$.registries",
        )

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
    script_result = replay_intent_script_srz(
        repo_root=repo_root,
        universe_state=universe_state,
        law_profile=law_profile,
        authority_context=authority_context,
        intents=intents,
        navigation_indices={
            "astronomy_catalog_index": astronomy_registry,
            "site_registry_index": site_registry,
        },
        policy_context={
            "activation_policy": activation_policy,
            "budget_policy": budget_policy,
            "fidelity_policy": fidelity_policy,
        },
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
    composite_hash = str(script_result.get("composite_hash", ""))
    final_state_hash = str(script_result.get("final_state_hash", ""))
    srz = dict(script_result.get("srz") or {})
    worker_effective = int((srz.get("worker_count_effective", 1) or 1))

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

    if write_state:
        write_canonical_json(state_path, updated_state)

    truth_model = build_truth_model(
        universe_identity=universe_identity,
        universe_state=updated_state,
        lockfile_payload=lock_payload,
        identity_path=norm(os.path.relpath(identity_path, repo_root)),
        state_path=norm(os.path.relpath(state_path, repo_root)),
        registry_payloads={
            "astronomy_catalog_index": astronomy_registry,
            "site_registry_index": site_registry,
            "activation_policy_registry": activation_policy_registry,
            "budget_policy_registry": budget_policy_registry,
            "fidelity_policy_registry": fidelity_policy_registry,
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
    render = build_render_model(perceived_model)
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
        "registry_hashes": registry_hashes,
        "state_hash_anchors": state_hash_anchors,
        "tick_hash_anchors": tick_hash_anchors,
        "checkpoint_hashes": checkpoint_hashes,
        "composite_hash": composite_hash,
        "final_state_hash": final_state_hash,
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
        "registry_hashes": registry_hashes,
        "state_hash_anchors": state_hash_anchors,
        "tick_hash_anchors": tick_hash_anchors,
        "checkpoint_hashes": checkpoint_hashes,
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
