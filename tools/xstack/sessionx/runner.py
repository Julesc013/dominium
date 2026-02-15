"""Deterministic minimal boot/shutdown path for SessionSpec v1."""

from __future__ import annotations

import os
from typing import Dict, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.registry_compile.compiler import compile_bundle
from tools.xstack.registry_compile.constants import (
    DEFAULT_BUNDLE_ID,
    REGISTRY_OUTPUT_FILENAMES,
)
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload

from .common import identity_hash_for_payload, norm, now_utc_iso, read_json_object, refusal, write_canonical_json
from .observation import build_truth_model, observe_truth
from .render_model import build_render_model


REGISTRY_HASH_KEY_MAP = {
    "domain_registry_hash": "domain_registry",
    "law_registry_hash": "law_registry",
    "experience_registry_hash": "experience_registry",
    "lens_registry_hash": "lens_registry",
    "activation_policy_registry_hash": "activation_policy_registry",
    "budget_policy_registry_hash": "budget_policy_registry",
    "fidelity_policy_registry_hash": "fidelity_policy_registry",
    "astronomy_catalog_index_hash": "astronomy_catalog_index",
    "site_registry_index_hash": "site_registry_index",
    "ui_registry_hash": "ui_registry",
}
REGISTRY_FILE_MAP = {
    "domain_registry_hash": "domain.registry.json",
    "law_registry_hash": "law.registry.json",
    "experience_registry_hash": "experience.registry.json",
    "lens_registry_hash": "lens.registry.json",
    "activation_policy_registry_hash": "activation_policy.registry.json",
    "budget_policy_registry_hash": "budget_policy.registry.json",
    "fidelity_policy_registry_hash": "fidelity_policy.registry.json",
    "astronomy_catalog_index_hash": "astronomy.catalog.index.json",
    "site_registry_index_hash": "site.registry.index.json",
    "ui_registry_hash": "ui.registry.json",
}


def _load_schema_validated(repo_root: str, schema_name: str, path: str) -> Tuple[dict, Dict[str, object]]:
    payload, err = read_json_object(path)
    if err:
        return {}, refusal(
            "REFUSE_JSON_LOAD_FAILED",
            "unable to parse required JSON file",
            "Ensure the file exists and contains valid JSON object content.",
            {"path": norm(path)},
            "$",
        )
    valid = validate_instance(repo_root=repo_root, schema_name=schema_name, payload=payload, strict_top_level=True)
    if not bool(valid.get("valid", False)):
        return {}, refusal(
            "REFUSE_SCHEMA_INVALID",
            "payload failed schema validation for '{}'".format(schema_name),
            "Fix file fields to satisfy schema validation and retry.",
            {"schema_id": schema_name, "path": norm(path)},
            "$",
        )
    return payload, {}


def _resolve_lockfile_path(repo_root: str, lockfile_path: str) -> str:
    token = str(lockfile_path or "").strip()
    if not token:
        return os.path.join(repo_root, "build", "lockfile.json")
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token))


def _resolve_registries_dir(repo_root: str, registries_dir: str) -> str:
    token = str(registries_dir or "").strip()
    if not token:
        return os.path.join(repo_root, "build", "registries")
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token))


def _load_lockfile(
    repo_root: str,
    compile_if_missing: bool,
    bundle_id: str,
    lockfile_path: str = "",
) -> Tuple[dict, Dict[str, object]]:
    lock_path = _resolve_lockfile_path(repo_root, lockfile_path)
    default_lock_path = _resolve_lockfile_path(repo_root, "")
    if not os.path.isfile(lock_path):
        if not compile_if_missing:
            return {}, refusal(
                "REFUSE_LOCKFILE_MISSING",
                "{} is missing".format(norm(os.path.relpath(lock_path, repo_root))),
                "Run tools/xstack/lockfile_build --bundle {} --out {}.".format(
                    bundle_id,
                    norm(os.path.relpath(lock_path, repo_root)),
                ),
                {"bundle_id": bundle_id},
                "$.lockfile",
            )
        if os.path.normcase(lock_path) != os.path.normcase(default_lock_path):
            return {}, refusal(
                "REFUSE_LOCKFILE_MISSING",
                "explicit lockfile path is missing and cannot be auto-generated",
                "Generate lockfile at the requested path before boot, or omit lockfile override.",
                {"bundle_id": bundle_id},
                "$.lockfile",
            )
        compiled = compile_bundle(
            repo_root=repo_root,
            bundle_id=bundle_id,
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            use_cache=True,
        )
        if compiled.get("result") != "complete":
            return {}, refusal(
                "REFUSE_LOCKFILE_GENERATION_FAILED",
                "unable to generate lockfile for bundle '{}'".format(bundle_id),
                "Resolve registry compile refusal and rerun boot.",
                {"bundle_id": bundle_id},
                "$.lockfile",
            )
    return _load_schema_validated(repo_root=repo_root, schema_name="bundle_lockfile", path=lock_path)


def _validate_registry_hashes(
    repo_root: str,
    lockfile_payload: dict,
    compile_if_missing: bool,
    bundle_id: str,
    registries_dir: str = "",
) -> Dict[str, object]:
    registries_abs = _resolve_registries_dir(repo_root, registries_dir)
    default_registries_abs = _resolve_registries_dir(repo_root, "")
    registries = lockfile_payload.get("registries")
    if not isinstance(registries, dict):
        return refusal(
            "REFUSE_LOCKFILE_REGISTRY_SECTION_MISSING",
            "lockfile registries section is missing",
            "Rebuild lockfile and ensure registries section exists.",
            {"bundle_id": bundle_id},
            "$.registries",
        )

    missing_files = []
    for key in sorted(REGISTRY_HASH_KEY_MAP.keys()):
        schema_key = REGISTRY_HASH_KEY_MAP[key]
        name = REGISTRY_OUTPUT_FILENAMES[schema_key]
        abs_path = os.path.join(registries_abs, name)
        if not os.path.isfile(abs_path):
            missing_files.append(abs_path)
    if missing_files and compile_if_missing:
        if os.path.normcase(registries_abs) != os.path.normcase(default_registries_abs):
            return refusal(
                "REFUSE_REGISTRY_MISSING",
                "explicit registries path is missing required files and cannot be auto-generated",
                "Generate registries at the requested path before boot, or omit registries override.",
                {"bundle_id": bundle_id},
                "$.registries",
            )
        compiled = compile_bundle(
            repo_root=repo_root,
            bundle_id=bundle_id,
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            use_cache=True,
        )
        if compiled.get("result") != "complete":
            return refusal(
                "REFUSE_REGISTRY_COMPILE_FAILED",
                "unable to compile missing registries",
                "Resolve registry compile refusal and retry boot.",
                {"bundle_id": bundle_id},
                "$.registries",
            )
        # Reload lockfile since compile may regenerate it.
        lock_reloaded, lock_error = _load_schema_validated(
            repo_root=repo_root,
            schema_name="bundle_lockfile",
            path=os.path.join(repo_root, "build", "lockfile.json"),
        )
        if lock_error:
            return lock_error
        lockfile_payload.clear()
        lockfile_payload.update(lock_reloaded)
        registries = lockfile_payload.get("registries") or {}

    for key in sorted(REGISTRY_HASH_KEY_MAP.keys()):
        schema_key = REGISTRY_HASH_KEY_MAP[key]
        file_name = REGISTRY_OUTPUT_FILENAMES[schema_key]
        abs_path = os.path.join(registries_abs, file_name)
        if not os.path.isfile(abs_path):
            return refusal(
                "REFUSE_REGISTRY_MISSING",
                "required registry file '{}' is missing".format(norm(os.path.relpath(abs_path, repo_root))),
                "Run tools/xstack/registry_compile --bundle {} and retry.".format(bundle_id),
                {"registry_file": file_name},
                "$.registries",
            )
        payload, err = read_json_object(abs_path)
        if err:
            return refusal(
                "REFUSE_REGISTRY_INVALID_JSON",
                "registry file '{}' is invalid JSON".format(norm(os.path.relpath(abs_path, repo_root))),
                "Rebuild registries and retry.",
                {"registry_file": file_name},
                "$.registries",
            )
        expected = str(registries.get(key, "")).strip()
        actual = str(payload.get("registry_hash", "")).strip() or canonical_sha256(payload)
        if expected != actual:
            return refusal(
                "REFUSE_REGISTRY_HASH_MISMATCH",
                "registry hash mismatch for '{}'".format(file_name),
                "Rebuild lockfile and registries from the same bundle inputs.",
                {
                    "registry_file": file_name,
                    "expected_hash": expected,
                    "actual_hash": actual,
                },
                "$.registries.{}".format(key),
            )
    return {"result": "complete"}


def _load_registry_payload(
    repo_root: str,
    file_name: str,
    expected_hash: str,
    registries_dir: str = "",
) -> Tuple[dict, Dict[str, object]]:
    abs_path = os.path.join(_resolve_registries_dir(repo_root, registries_dir), file_name)
    payload, err = read_json_object(abs_path)
    if err:
        return {}, refusal(
            "REFUSE_REGISTRY_INVALID_JSON",
            "registry file '{}' is invalid JSON".format(norm(os.path.relpath(abs_path, repo_root))),
            "Rebuild registries and retry.",
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


def _select_law_profile(law_registry: dict, law_profile_id: str) -> Tuple[dict, Dict[str, object]]:
    for row in sorted((law_registry.get("law_profiles") or []), key=lambda item: str(item.get("law_profile_id", ""))):
        if str(row.get("law_profile_id", "")).strip() == str(law_profile_id).strip():
            return dict(row), {}
    return {}, refusal(
        "LAW_PROFILE_NOT_FOUND",
        "law profile '{}' is not present in compiled law registry".format(str(law_profile_id)),
        "Select a LawProfile listed in build/registries/law.registry.json and rebuild SessionSpec.",
        {"law_profile_id": str(law_profile_id)},
        "$.authority_context.law_profile_id",
    )


def _select_lens_profile(
    lens_registry: dict,
    experience_registry: dict,
    experience_id: str,
    law_profile: dict,
) -> Tuple[dict, Dict[str, object]]:
    default_lens_id = ""
    for row in sorted((experience_registry.get("experience_profiles") or []), key=lambda item: str(item.get("experience_id", ""))):
        if str(row.get("experience_id", "")).strip() == str(experience_id).strip():
            default_lens_id = str(row.get("default_lens_id", "")).strip()
            if not default_lens_id:
                allowed = sorted(str(item).strip() for item in (law_profile.get("allowed_lenses") or []) if str(item).strip())
                default_lens_id = allowed[0] if allowed else ""
            break
    if not default_lens_id:
        allowed = sorted(str(item).strip() for item in (law_profile.get("allowed_lenses") or []) if str(item).strip())
        default_lens_id = allowed[0] if allowed else ""

    if not default_lens_id:
        return {}, refusal(
            "LENS_NOT_FOUND",
            "no default lens could be resolved for experience '{}'".format(str(experience_id)),
            "Set experience default_lens_id or allow at least one lens in the active LawProfile.",
            {"experience_id": str(experience_id)},
            "$.experience_id",
        )

    for row in sorted((lens_registry.get("lenses") or []), key=lambda item: str(item.get("lens_id", ""))):
        if str(row.get("lens_id", "")).strip() == default_lens_id:
            return dict(row), {}
    return {}, refusal(
        "LENS_NOT_FOUND",
        "lens '{}' is not present in compiled lens registry".format(default_lens_id),
        "Select a lens listed in build/registries/lens.registry.json.",
        {"lens_id": default_lens_id},
        "$.lens_id",
    )


def _select_policy_entry(registry_payload: dict, key: str, policy_id: str, refusal_code: str, registry_file: str) -> Tuple[dict, Dict[str, object]]:
    rows = registry_payload.get(key)
    if not isinstance(rows, list):
        return {}, refusal(
            refusal_code,
            "policy registry '{}' is missing key '{}'".format(registry_file, key),
            "Rebuild registries and ensure policy rows are present.",
            {"registry_file": registry_file, "policy_id": policy_id},
            "$.{}".format(key),
        )
    for row in sorted(rows, key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
            return dict(row), {}
    return {}, refusal(
        refusal_code,
        "policy '{}' is not present in compiled registry '{}'".format(str(policy_id), registry_file),
        "Select a policy ID listed in '{}' and rebuild SessionSpec.".format(registry_file),
        {"policy_id": str(policy_id)},
        "$.policy_id",
    )


def boot_session_spec(
    repo_root: str,
    session_spec_path: str,
    bundle_id: str = "",
    compile_if_missing: bool = False,
    lockfile_path: str = "",
    registries_dir: str = "",
) -> Dict[str, object]:
    spec_abs = os.path.normpath(os.path.abspath(session_spec_path))
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
            "Rebuild lockfile and retry boot.",
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

    _state_payload, state_error = _load_schema_validated(repo_root=repo_root, schema_name="universe_state", path=state_path)
    if state_error:
        return state_error

    session_context = session_spec.get("authority_context")
    if not isinstance(session_context, dict):
        return refusal(
            "REFUSE_AUTHORITY_CONTEXT_MISSING",
            "SessionSpec authority_context is missing",
            "Populate authority_context in session_spec.json.",
            {"schema_id": "session_spec"},
            "$.authority_context",
        )

    authority_origin = str(session_context.get("authority_origin", "")).strip()
    if authority_origin != "client":
        return refusal(
            "REFUSE_AUTHORITY_ORIGIN_INVALID",
            "authority_origin must be 'client' for headless client boot",
            "Set authority_context.authority_origin to client.",
            {"authority_origin": authority_origin or "<empty>"},
            "$.authority_context.authority_origin",
        )

    boot_authority_context = {
        "authority_origin": "client",
        "experience_id": str(session_spec.get("experience_id", "")),
        "law_profile_id": str(session_context.get("law_profile_id", "")),
        "entitlements": sorted(
            set(str(item).strip() for item in (session_context.get("entitlements") or []) if str(item).strip())
        ),
        "epistemic_scope": dict(session_context.get("epistemic_scope") or {}),
        "privilege_level": str(session_context.get("privilege_level", "")),
    }
    authority_schema_payload = dict(boot_authority_context)
    authority_schema_payload["schema_version"] = "1.0.0"
    authority_check = validate_instance(
        repo_root=repo_root,
        schema_name="authority_context",
        payload=authority_schema_payload,
        strict_top_level=True,
    )
    if not bool(authority_check.get("valid", False)):
        return refusal(
            "REFUSE_AUTHORITY_CONTEXT_INVALID",
            "constructed AuthorityContext failed schema validation",
            "Fix SessionSpec authority_context fields and retry.",
            {"schema_id": "authority_context"},
            "$.authority_context",
        )

    law_profile, law_profile_error = _select_law_profile(
        law_registry=law_registry,
        law_profile_id=str(boot_authority_context.get("law_profile_id", "")),
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

    truth_model = build_truth_model(
        universe_identity=universe_identity,
        universe_state=_state_payload,
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
        authority_context=boot_authority_context,
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
            "failed to derive RenderModel from PerceivedModel",
            "Inspect observation outputs and renderer adapter contract.",
            {"save_id": save_id},
            "$.render_model",
        )
    render_hash = str(render.get("render_model_hash", ""))

    session_spec_hash = canonical_sha256(session_spec)
    registry_hashes = dict((lock_payload.get("registries") or {}))
    start_tick = 0
    stop_tick = 0
    deterministic_fields = {
        "schema_version": "1.0.0",
        "save_id": save_id,
        "bundle_id": bundle_token,
        "session_spec_hash": session_spec_hash,
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "registry_hashes": registry_hashes,
        "selected_lens_id": str(lens_profile.get("lens_id", "")),
        "budget_policy_id": str(budget_policy.get("policy_id", "")),
        "fidelity_policy_id": str(fidelity_policy.get("policy_id", "")),
        "activation_policy_id": str(activation_policy.get("policy_id", "")),
        "perceived_model_hash": perceived_hash,
        "render_model_hash": render_hash,
        "start_tick": start_tick,
        "stop_tick": stop_tick,
        "authority_context": boot_authority_context,
    }
    deterministic_fields_hash = canonical_sha256(deterministic_fields)
    run_id = "run.{}".format(deterministic_fields_hash[:16])

    now = now_utc_iso()
    run_meta = dict(deterministic_fields)
    lock_path_for_meta = _resolve_lockfile_path(repo_root, lockfile_path)
    run_meta.update(
        {
            "run_id": run_id,
            "session_spec_path": norm(os.path.relpath(spec_abs, repo_root)),
            "universe_identity_path": norm(os.path.relpath(identity_path, repo_root)),
            "universe_state_path": norm(os.path.relpath(state_path, repo_root)),
            "lockfile_path": norm(os.path.relpath(lock_path_for_meta, repo_root)),
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
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "registry_hashes": registry_hashes,
        "selected_lens_id": str(lens_profile.get("lens_id", "")),
        "perceived_model_hash": perceived_hash,
        "render_model_hash": render_hash,
        "start_tick": start_tick,
        "stop_tick": stop_tick,
        "deterministic_fields_hash": deterministic_fields_hash,
    }
