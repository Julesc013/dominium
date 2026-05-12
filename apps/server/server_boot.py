"""SERVER-MVP-0 headless boot, validation, and intent wrapping."""

from __future__ import annotations

import os
from typing import Dict, Mapping, Tuple

from geo import build_default_overlay_manifest, overlay_proof_surface, validate_overlay_manifest_trust
from modding import DEFAULT_MOD_POLICY_ID, proof_bundle_from_lockfile, validate_saved_mod_policy
from net.policies.policy_server_authoritative import (
    POLICY_ID_SERVER_AUTHORITATIVE,
    initialize_authoritative_runtime,
    prepare_server_authoritative_baseline,
    submit_client_intent,
)
from compat import COMPAT_MODE_READ_ONLY, REFUSAL_CONNECTION_NO_NEGOTIATION
from compat.data_format_loader import load_versioned_artifact, stamp_artifact_metadata
from universe import (
    DEFAULT_UNIVERSE_CONTRACT_BUNDLE_REF,
    build_universe_contract_bundle_payload,
    enforce_session_contract_bundle,
    pin_contract_bundle_metadata,
)
from tools.mvp.runtime_bundle import (
    build_default_universe_identity,
    validate_pack_lock_payload as validate_runtime_pack_lock_payload,
)
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.common import norm, read_json_object, refusal, write_canonical_json
from tools.xstack.sessionx.creator import (
    _default_net_schema_versions,
    _initial_universe_state,
    _parse_rng_roots,
    _session_paths,
    create_session_spec,
)
from tools.xstack.sessionx.runner import (
    REGISTRY_FILE_MAP,
    REGISTRY_HASH_KEY_MAP,
    _load_lockfile,
    _load_registry_payload,
    _load_schema_validated,
    _select_law_profile,
    _select_lens_profile,
    _select_time_control_policy,
    _select_transition_policy,
)
from tools.xstack.sessionx.universe_physics import select_physics_profile


SERVER_CONFIG_REGISTRY_REL = os.path.join("data", "registries", "server_config_registry.json")
DEFAULT_SERVER_CONFIG_ID = "server.mvp_default"
REFUSAL_SESSION_CONTRACT_MISMATCH = "refusal.session.contract_mismatch"
REFUSAL_SESSION_PACK_LOCK_MISMATCH = "refusal.session.pack_lock_mismatch"
REFUSAL_CLIENT_UNAUTHORIZED = "refusal.client.unauthorized"
REFUSAL_CLIENT_READ_ONLY = "refusal.client.read_only_connection"


def _server_refusal(
    reason_code: str,
    message: str,
    remediation: str,
    *,
    details: Mapping[str, object] | None = None,
    path: str = "$",
) -> dict:
    relevant_ids = {
        str(key): str(value).strip()
        for key, value in sorted((dict(details or {})).items(), key=lambda item: str(item[0]))
        if str(value).strip()
    }
    return refusal(reason_code, message, remediation, relevant_ids, path)


def _contract_enforcement_to_server_refusal(contract_enforcement: Mapping[str, object] | None) -> dict:
    refusal_payload = dict((dict(contract_enforcement or {})).get("refusal") or {})
    return _server_refusal(
        REFUSAL_SESSION_CONTRACT_MISMATCH,
        "server boot refused due to pinned universe semantic contract validation failure",
        "Restore the pinned universe contract bundle and semantic contract registry hashes or run the explicit CompatX migration tool before boot.",
        details={
            "upstream_reason_code": str(refusal_payload.get("reason_code", "")).strip(),
            "bundle_path": str((dict(contract_enforcement or {})).get("bundle_path", "")).strip(),
        },
        path="$.contract_bundle_hash",
    )


def _normalize_server_config(row: Mapping[str, object] | None) -> dict:
    payload = dict(row or {})
    return {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "server_id": str(payload.get("server_id", "")).strip(),
        "session_template_id": str(payload.get("session_template_id", "")).strip(),
        "mod_policy_id": str(payload.get("mod_policy_id", "")).strip(),
        "overlay_conflict_policy_id": str(payload.get("overlay_conflict_policy_id", "")).strip(),
        "max_clients": int(max(1, int(payload.get("max_clients", 1) or 1))),
        "proof_anchor_interval_ticks": int(max(1, int(payload.get("proof_anchor_interval_ticks", 1) or 1))),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": {
            str(key): value
            for key, value in sorted(dict(payload.get("extensions") or {}).items(), key=lambda item: str(item[0]))
        },
    }


def _server_config_fingerprint(row: Mapping[str, object]) -> str:
    payload = _normalize_server_config(row)
    payload["deterministic_fingerprint"] = ""
    return canonical_sha256(payload)


def _server_config_errors(row: Mapping[str, object] | None) -> list[str]:
    payload = _normalize_server_config(row)
    errors: list[str] = []
    for key in (
        "schema_version",
        "server_id",
        "session_template_id",
        "mod_policy_id",
        "overlay_conflict_policy_id",
    ):
        if not str(payload.get(key, "")).strip():
            errors.append("{} missing".format(key))
    if int(payload.get("max_clients", 0) or 0) < 1:
        errors.append("max_clients invalid")
    if int(payload.get("proof_anchor_interval_ticks", 0) or 0) < 1:
        errors.append("proof_anchor_interval_ticks invalid")
    if not isinstance(payload.get("extensions"), dict):
        errors.append("extensions invalid")
    return sorted(set(errors))


def load_server_config_registry(repo_root: str) -> Tuple[dict, dict]:
    registry_path = os.path.join(repo_root, SERVER_CONFIG_REGISTRY_REL.replace("/", os.sep))
    payload, err = read_json_object(registry_path)
    if err:
        return {}, _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "server config registry is missing or invalid",
            "Restore data/registries/server_config_registry.json and retry server boot.",
            details={"registry_path": SERVER_CONFIG_REGISTRY_REL},
            path="$.server_config_registry",
        )
    rows = list(((dict(payload.get("record") or {})).get("server_configs") or []))
    normalized_rows = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("server_id", ""))):
        normalized = _normalize_server_config(row)
        config_errors = _server_config_errors(normalized)
        if config_errors:
            return {}, _server_refusal(
                REFUSAL_SESSION_CONTRACT_MISMATCH,
                "server config registry row failed deterministic structural validation",
                "Fix required fields in server_config rows and retry server boot.",
                details={"server_id": str(normalized.get("server_id", "")), "errors": ",".join(config_errors)},
                path="$.server_config_registry",
            )
        expected = _server_config_fingerprint(normalized)
        if str(normalized.get("deterministic_fingerprint", "")).strip() != expected:
            return {}, _server_refusal(
                REFUSAL_SESSION_CONTRACT_MISMATCH,
                "server config registry row deterministic_fingerprint mismatch",
                "Recompute deterministic_fingerprint for the affected server config row.",
                details={"server_id": str(normalized.get("server_id", ""))},
                path="$.server_config_registry",
            )
        normalized_rows.append(normalized)
    return {
        "schema_id": str(payload.get("schema_id", "")).strip(),
        "schema_version": str(payload.get("schema_version", "")).strip(),
        "record": {
            "registry_id": str((dict(payload.get("record") or {})).get("registry_id", "")).strip(),
            "registry_version": str((dict(payload.get("record") or {})).get("registry_version", "")).strip(),
            "server_configs": normalized_rows,
            "extensions": {
                str(key): value
                for key, value in sorted(dict((dict(payload.get("record") or {})).get("extensions") or {}).items(), key=lambda item: str(item[0]))
            },
        },
    }, {}


def server_config_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = list(((dict(payload or {}).get("record") or {}).get("server_configs") or []))
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("server_id", ""))):
        token = str(row.get("server_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def load_server_config(repo_root: str, server_config_id: str = DEFAULT_SERVER_CONFIG_ID) -> Tuple[dict, dict]:
    registry_payload, registry_error = load_server_config_registry(repo_root)
    if registry_error:
        return {}, registry_error
    rows = server_config_rows_by_id(registry_payload)
    config_id = str(server_config_id or DEFAULT_SERVER_CONFIG_ID).strip() or DEFAULT_SERVER_CONFIG_ID
    row = dict(rows.get(config_id) or {})
    if not row:
        return {}, _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "requested server_config_id is not declared",
            "Select a declared server_id from data/registries/server_config_registry.json.",
            details={"server_id": config_id},
            path="$.server_id",
        )
    return row, {}


def _runtime_pack_lock_payload(repo_root: str, pack_lock_path: str) -> Tuple[dict, dict]:
    payload, _meta, load_error = load_versioned_artifact(
        repo_root=repo_root,
        artifact_kind="pack_lock",
        path=pack_lock_path,
        allow_read_only=False,
    )
    if load_error:
        return {}, _server_refusal(
            REFUSAL_SESSION_PACK_LOCK_MISMATCH,
            "runtime pack lock payload is missing or invalid",
            "Restore the requested pack lock artifact and retry server boot.",
            details={"pack_lock_path": norm(pack_lock_path)},
            path="$.pack_lock_hash",
        )
    payload, err = _load_schema_validated(repo_root=repo_root, schema_name="pack_lock", path=pack_lock_path)
    if err:
        payload = dict(payload)
    errors = validate_runtime_pack_lock_payload(repo_root=repo_root, payload=dict(payload))
    if errors:
        return {}, _server_refusal(
            REFUSAL_SESSION_PACK_LOCK_MISMATCH,
            "runtime pack lock payload failed deterministic validation",
            "Regenerate the requested pack lock artifact before retrying server boot.",
            details={"pack_lock_path": norm(pack_lock_path)},
            path="$.pack_lock_hash",
        )
    return dict(payload), {}


def _load_compiled_registry_payloads(repo_root: str, lock_payload: Mapping[str, object], registries_dir: str = "") -> Tuple[dict, dict]:
    registries = dict((dict(lock_payload or {})).get("registries") or {})
    if not registries:
        return {}, _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "compiled lock payload is missing registry hash metadata",
            "Compile registries and lockfile before starting the headless server.",
            details={"field": "registries"},
            path="$.registries",
        )
    payloads = {}
    for hash_key, registry_key in sorted(REGISTRY_HASH_KEY_MAP.items()):
        file_name = REGISTRY_FILE_MAP.get(hash_key, "")
        if not file_name:
            continue
        registry_payload, registry_error = _load_registry_payload(
            repo_root=repo_root,
            file_name=file_name,
            expected_hash=str(registries.get(hash_key, "")).strip(),
            registries_dir=registries_dir,
        )
        if registry_error:
            return {}, registry_error
        payloads[str(registry_key)] = dict(registry_payload)
    return payloads, {}


def _connection_entitlements(
    server_profile: Mapping[str, object] | None,
    session_authority: Mapping[str, object] | None = None,
) -> list[str]:
    rows = []
    rows.extend(list((dict(server_profile or {}).get("allowed_entitlements") or [])))
    rows.extend(list((dict(session_authority or {}).get("entitlements") or [])))
    return sorted(set(str(item).strip() for item in rows if str(item).strip()))


def build_connection_authority_context(
    *,
    session_spec: Mapping[str, object],
    server_profile: Mapping[str, object],
    connection_id: str,
    account_id: str,
    law_profile_id_override: str = "",
    entitlements_override: list[str] | None = None,
) -> dict:
    session_authority = dict((dict(session_spec or {})).get("authority_context") or {})
    selected_law_profile_id = str(law_profile_id_override or session_authority.get("law_profile_id", "")).strip()
    selected_entitlements = (
        sorted(set(str(item).strip() for item in list(entitlements_override or []) if str(item).strip()))
        if entitlements_override is not None
        else _connection_entitlements(server_profile, session_authority)
    )
    return {
        "authority_origin": "client",
        "experience_id": str(session_authority.get("experience_id", "")).strip(),
        "law_profile_id": selected_law_profile_id,
        "entitlements": selected_entitlements,
        "epistemic_scope": dict(session_authority.get("epistemic_scope") or {}),
        "privilege_level": str(session_authority.get("privilege_level", "")).strip(),
        "extensions": {
            "official.connection_id": str(connection_id).strip(),
            "official.account_id": str(account_id).strip(),
        },
    }


def _select_profiles_for_server(
    *,
    session_spec: Mapping[str, object],
    universe_identity: Mapping[str, object],
    registry_payloads: Mapping[str, object],
) -> Tuple[dict, dict, dict, dict, dict, dict, dict, dict, dict]:
    physics_registry = dict(registry_payloads.get("universe_physics_profile_registry") or {})
    time_model_registry = dict(registry_payloads.get("time_model_registry") or {})
    time_control_registry = dict(registry_payloads.get("time_control_policy_registry") or {})
    dt_rule_registry = dict(registry_payloads.get("dt_quantization_rule_registry") or {})
    compaction_registry = dict(registry_payloads.get("compaction_policy_registry") or {})
    transition_policy_registry = dict(registry_payloads.get("transition_policy_registry") or {})
    law_registry = dict(registry_payloads.get("law_registry") or {})
    lens_registry = dict(registry_payloads.get("lens_registry") or {})
    experience_registry = dict(registry_payloads.get("experience_registry") or {})

    selected_physics, physics_error = select_physics_profile(
        physics_profile_id=str((dict(universe_identity or {})).get("physics_profile_id", "")).strip(),
        profile_registry=physics_registry,
    )
    if physics_error:
        return {}, {}, {}, {}, {}, {}, {}, {}, physics_error
    selected_time_policy, selected_dt_rule, selected_compaction_policy, selected_time_model, time_error = _select_time_control_policy(
        time_control_policy_registry=time_control_registry,
        dt_quantization_rule_registry=dt_rule_registry,
        compaction_policy_registry=compaction_registry,
        time_model_registry=time_model_registry,
        selected_physics_profile=selected_physics,
        requested_time_control_policy_id=str((dict(session_spec or {})).get("time_control_policy_id", "")).strip(),
    )
    if time_error:
        return {}, {}, {}, {}, {}, {}, {}, {}, time_error
    selected_transition_policy, transition_error = _select_transition_policy(
        transition_policy_registry=transition_policy_registry,
        selected_physics_profile=selected_physics,
        requested_transition_policy_id=str((dict(session_spec or {})).get("transition_policy_id", "")).strip(),
    )
    if transition_error:
        return {}, {}, {}, {}, {}, {}, {}, {}, transition_error
    law_profile, law_error = _select_law_profile(
        law_registry=law_registry,
        law_profile_id=str((dict((dict(session_spec or {})).get("authority_context") or {})).get("law_profile_id", "")).strip(),
    )
    if law_error:
        return {}, {}, {}, {}, {}, {}, {}, {}, law_error
    lens_profile, lens_error = _select_lens_profile(
        lens_registry=lens_registry,
        experience_registry=experience_registry,
        experience_id=str((dict(session_spec or {})).get("experience_id", "")).strip(),
        law_profile=law_profile,
    )
    if lens_error:
        return {}, {}, {}, {}, {}, {}, {}, {}, lens_error
    return (
        selected_physics,
        selected_time_policy,
        selected_dt_rule,
        selected_compaction_policy,
        selected_time_model,
        selected_transition_policy,
        law_profile,
        lens_profile,
        {},
    )


def _server_runtime_artifact_dir(repo_root: str, save_id: str) -> str:
    return os.path.join(repo_root, "build", "server", str(save_id))


def materialize_server_session(
    *,
    repo_root: str,
    seed: str,
    profile_bundle_path: str,
    pack_lock_path: str,
    server_config_id: str = DEFAULT_SERVER_CONFIG_ID,
    authority_mode: str = "dev",
    save_id: str = "",
) -> dict:
    del profile_bundle_path
    server_config, config_error = load_server_config(repo_root, server_config_id=server_config_id)
    if config_error:
        return config_error
    pack_lock_payload, pack_lock_error = _runtime_pack_lock_payload(repo_root, pack_lock_path)
    if pack_lock_error:
        return pack_lock_error

    config_ext = dict(server_config.get("extensions") or {})
    save_token = str(save_id or "save.server.mvp_default").strip() or "save.server.mvp_default"
    session_paths = _session_paths(repo_root=repo_root, save_id=save_token, saves_root_rel="saves")
    seed_token = str(seed or "0").strip() or "0"

    universe_contract_bundle_payload, _registry_payload, proof_bundle, bundle_errors = build_universe_contract_bundle_payload(
        repo_root=repo_root
    )
    if bundle_errors:
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "semantic contract bundle could not be built for server session materialization",
            "Restore semantic contract registry artifacts and retry.",
            details={"server_id": str(server_config.get("server_id", ""))},
            path="$.contract_bundle_hash",
        )

    universe_identity = build_default_universe_identity(
        repo_root=repo_root,
        seed=seed_token,
        authority_mode=str(authority_mode or "dev"),
        pack_lock_payload=pack_lock_payload,
    )
    universe_identity = pin_contract_bundle_metadata(
        universe_identity,
        bundle_ref=DEFAULT_UNIVERSE_CONTRACT_BUNDLE_REF,
        bundle_payload=universe_contract_bundle_payload,
    )

    authority_context = {
        "authority_origin": "client",
        "experience_id": str(config_ext.get("official.experience_id", "profile.lab.developer")).strip()
        or "profile.lab.developer",
        "law_profile_id": str(config_ext.get("official.law_profile_id", "law.lab.unrestricted")).strip()
        or "law.lab.unrestricted",
        "entitlements": sorted(
            {
                "session.boot",
                "entitlement.camera_control",
                "entitlement.control.admin",
                "entitlement.control.camera",
                "entitlement.control.lens_override",
                "entitlement.control.possess",
                "entitlement.debug_view",
                "entitlement.inspect",
                "entitlement.teleport",
                "entitlement.time_control",
                "ui.window.lab.nav",
            }
        ),
        "epistemic_scope": {
            "scope_id": str(config_ext.get("official.epistemic_scope_id", "epistemic.lab.placeholder")).strip()
            or "epistemic.lab.placeholder",
            "visibility_level": str(config_ext.get("official.visibility_level", "placeholder")).strip() or "placeholder",
        },
        "privilege_level": str(config_ext.get("official.privilege_level", "operator")).strip() or "operator",
        "profile_bindings": [],
        "effective_profile_snapshot": {},
    }
    network_payload = {
        "endpoint": str(config_ext.get("official.endpoint", "loopback://server.mvp.default")).strip()
        or "loopback://server.mvp.default",
        "transport_id": "transport.loopback",
        "client_peer_id": "peer.client.loopback",
        "server_peer_id": "peer.server.mvp",
        "requested_replication_policy_id": str(
            config_ext.get("official.requested_replication_policy_id", POLICY_ID_SERVER_AUTHORITATIVE)
        ).strip()
        or POLICY_ID_SERVER_AUTHORITATIVE,
        "anti_cheat_policy_id": str(config_ext.get("official.anti_cheat_policy_id", "policy.ac.private_relaxed")).strip()
        or "policy.ac.private_relaxed",
        "server_profile_id": str(config_ext.get("official.server_profile_id", "server.profile.private_relaxed")).strip()
        or "server.profile.private_relaxed",
        "server_policy_id": str(config_ext.get("official.server_policy_id", "server.policy.private.default")).strip()
        or "server.policy.private.default",
        "desired_law_profile_id": str(config_ext.get("official.law_profile_id", "law.lab.unrestricted")).strip()
        or "law.lab.unrestricted",
        "securex_policy_id": str(config_ext.get("official.securex_policy_id", "securex.policy.private_relaxed")).strip()
        or "securex.policy.private_relaxed",
        "physics_profile_id": str(universe_identity.get("physics_profile_id", "")).strip(),
        "schema_versions": _default_net_schema_versions(repo_root=repo_root),
    }
    session_payload = {
        "schema_version": "1.0.0",
        "universe_id": str(universe_identity.get("universe_id", "")).strip(),
        "save_id": save_token,
        "bundle_id": str(config_ext.get("official.bundle_id", "bundle.base.lab")).strip() or "bundle.base.lab",
        "pipeline_id": "pipeline.client.multiplayer_stub",
        "scenario_id": "scenario.lab.galaxy_nav",
        "mission_id": None,
        "experience_id": str(authority_context.get("experience_id", "")),
        "parameter_bundle_id": str(config_ext.get("official.parameter_bundle_id", "params.lab.placeholder")).strip()
        or "params.lab.placeholder",
        "physics_profile_id": str(universe_identity.get("physics_profile_id", "")).strip(),
        "authority_context": authority_context,
        "profile_bindings": [],
        "pack_lock_hash": str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
        "contract_bundle_hash": str(proof_bundle.get("universe_contract_bundle_hash", "")).strip(),
        "semantic_contract_registry_hash": str(proof_bundle.get("semantic_contract_registry_hash", "")).strip(),
        "mod_policy_id": str(server_config.get("mod_policy_id", "")).strip() or DEFAULT_MOD_POLICY_ID,
        "mod_policy_registry_hash": str(pack_lock_payload.get("mod_policy_registry_hash", "")).strip(),
        "budget_policy_id": str(config_ext.get("official.budget_policy_id", "policy.budget.default_lab")).strip()
        or "policy.budget.default_lab",
        "fidelity_policy_id": str(config_ext.get("official.fidelity_policy_id", "policy.fidelity.default_lab")).strip()
        or "policy.fidelity.default_lab",
        "time_control_policy_id": str(
            config_ext.get("official.time_control_policy_id", "time.policy.default_realistic")
        ).strip()
        or "time.policy.default_realistic",
        "selected_seed": seed_token,
        "deterministic_rng_roots": _parse_rng_roots([], "seed.server.session.{}".format(seed_token)),
        "network": network_payload,
    }
    session_valid = validate_instance(repo_root=repo_root, schema_name="session_spec", payload=session_payload, strict_top_level=True)
    if not bool(session_valid.get("valid", False)):
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "materialized server SessionSpec failed schema validation",
            "Repair the server materialization defaults and retry.",
            details={"save_id": save_token},
            path="$.session_spec",
        )

    state_payload = _initial_universe_state(
        save_id=save_token,
        law_profile_id=str(authority_context.get("law_profile_id", "")),
        camera_assembly=None,
        instrument_assemblies=[],
        budget_policy_id=str(session_payload.get("budget_policy_id", "")),
        fidelity_policy_id=str(session_payload.get("fidelity_policy_id", "")),
        activation_policy_id="policy.activation.default_lab",
        max_compute_units_per_tick=0,
    )
    overlay_manifest = build_default_overlay_manifest(
        universe_id=str(universe_identity.get("universe_id", "")).strip(),
        pack_lock_hash=str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
        save_id=save_token,
        generator_version_id=str(universe_identity.get("generator_version_id", "")).strip(),
        overlay_conflict_policy_id=str(server_config.get("overlay_conflict_policy_id", "")).strip(),
    )
    overlay_trust = validate_overlay_manifest_trust(
        overlay_manifest=overlay_manifest,
        resolved_packs=list(pack_lock_payload.get("ordered_packs") or []),
        expected_pack_lock_hash=str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
        overlay_conflict_policy_id=str(server_config.get("overlay_conflict_policy_id", "")).strip(),
    )
    if str(overlay_trust.get("result", "")) != "complete":
        return dict(overlay_trust)
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
    state_payload = stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="save_file",
        payload=state_payload,
        semantic_contract_bundle_hash=str(proof_bundle.get("universe_contract_bundle_hash", "")).strip(),
    )
    state_valid = validate_instance(repo_root=repo_root, schema_name="universe_state", payload=state_payload, strict_top_level=True)
    if not bool(state_valid.get("valid", False)):
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "materialized server UniverseState failed schema validation",
            "Repair the server materialization defaults and retry.",
            details={"save_id": save_token},
            path="$.universe_state",
        )

    write_canonical_json(session_paths["session_spec_path"], session_payload)
    write_canonical_json(session_paths["universe_identity_path"], universe_identity)
    write_canonical_json(session_paths["universe_contract_bundle_path"], universe_contract_bundle_payload)
    write_canonical_json(session_paths["universe_state_path"], state_payload)
    return {
        "result": "complete",
        "save_id": save_token,
        "bundle_id": str(session_payload.get("bundle_id", "")),
        "session_spec_path": norm(os.path.relpath(session_paths["session_spec_path"], repo_root)),
        "universe_identity_path": norm(os.path.relpath(session_paths["universe_identity_path"], repo_root)),
        "universe_contract_bundle_path": norm(os.path.relpath(session_paths["universe_contract_bundle_path"], repo_root)),
        "universe_state_path": norm(os.path.relpath(session_paths["universe_state_path"], repo_root)),
        "pack_lock_hash": str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
        "mod_policy_id": str(session_payload.get("mod_policy_id", "")).strip(),
        "mod_policy_registry_hash": str(session_payload.get("mod_policy_registry_hash", "")).strip(),
        "semantic_contract_registry_hash": str(proof_bundle.get("semantic_contract_registry_hash", "")).strip(),
        "universe_contract_bundle_hash": str(proof_bundle.get("universe_contract_bundle_hash", "")).strip(),
    }


def _server_profile_row(registry_payload: Mapping[str, object] | None, server_profile_id: str) -> dict:
    rows = list(((dict(registry_payload or {}).get("profiles") or [])))
    token = str(server_profile_id or "").strip()
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("server_profile_id", ""))):
        if str(row.get("server_profile_id", "")).strip() == token:
            return dict(row)
    return {}


def boot_server_runtime(
    *,
    repo_root: str,
    session_spec_path: str = "",
    seed: str = "",
    profile_bundle_path: str = "",
    pack_lock_path: str = "",
    server_config_id: str = DEFAULT_SERVER_CONFIG_ID,
    authority_mode: str = "dev",
    save_id: str = "",
    expected_contract_bundle_hash: str = "",
    compile_if_missing: bool = False,
    registries_dir: str = "",
) -> dict:
    del profile_bundle_path
    server_config, config_error = load_server_config(repo_root, server_config_id=server_config_id)
    if config_error:
        return config_error

    session_spec_abs = os.path.normpath(os.path.abspath(session_spec_path)) if str(session_spec_path or "").strip() else ""
    materialized = False
    materialized_paths = {}
    if not session_spec_abs:
        created = materialize_server_session(
            repo_root=repo_root,
            seed=str(seed or "0"),
            profile_bundle_path="",
            pack_lock_path=str(pack_lock_path or os.path.join(repo_root, "locks", "pack_lock.mvp_default.json")),
            server_config_id=server_config_id,
            authority_mode=authority_mode,
            save_id=save_id,
        )
        if str(created.get("result", "")) != "complete":
            return dict(created)
        materialized = True
        materialized_paths = dict(created)
        session_spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))

    session_spec, spec_error = _load_schema_validated(repo_root=repo_root, schema_name="session_spec", path=session_spec_abs)
    if spec_error:
        return spec_error
    save_token = str(session_spec.get("save_id", "")).strip()
    if not save_token:
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "SessionSpec save_id is missing for headless server boot",
            "Restore session_spec.json save_id or recreate the server session.",
            details={"session_spec_path": norm(session_spec_abs)},
            path="$.save_id",
        )

    save_dir = os.path.join(repo_root, "saves", save_token)
    identity_path = os.path.join(save_dir, "universe_identity.json")
    state_path = os.path.join(save_dir, "universe_state.json")
    universe_identity, identity_error = _load_schema_validated(
        repo_root=repo_root,
        schema_name="universe_identity",
        path=identity_path,
    )
    if identity_error:
        return identity_error
    universe_state, state_error = _load_schema_validated(
        repo_root=repo_root,
        schema_name="universe_state",
        path=state_path,
    )
    if state_error:
        return state_error

    selected_mod_policy_id = str(server_config.get("mod_policy_id", "")).strip() or DEFAULT_MOD_POLICY_ID
    session_mod_policy_id = str(session_spec.get("mod_policy_id", "")).strip() or DEFAULT_MOD_POLICY_ID
    if session_mod_policy_id != selected_mod_policy_id:
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "SessionSpec mod_policy_id does not match server config",
            "Use a SessionSpec created under the requested server mod policy or select a matching server_config_id.",
            details={"session_mod_policy_id": session_mod_policy_id, "server_mod_policy_id": selected_mod_policy_id},
            path="$.mod_policy_id",
        )

    if not str(session_spec.get("semantic_contract_registry_hash", "")).strip():
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "SessionSpec semantic_contract_registry_hash is missing for headless server boot",
            "Recreate the server SessionSpec so it records the pinned semantic contract registry hash before boot.",
            details={"save_id": save_token, "session_spec_path": norm(session_spec_abs)},
            path="$.semantic_contract_registry_hash",
        )

    contract_enforcement = enforce_session_contract_bundle(
        repo_root=repo_root,
        session_spec=session_spec,
        universe_identity=universe_identity,
        identity_path=identity_path,
        replay_mode=False,
    )
    if str(contract_enforcement.get("result", "")) != "complete":
        return _contract_enforcement_to_server_refusal(contract_enforcement)
    expected_contract_hash = str(expected_contract_bundle_hash or "").strip()
    actual_contract_hash = str(contract_enforcement.get("contract_bundle_hash", "")).strip()
    if expected_contract_hash and actual_contract_hash != expected_contract_hash:
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "explicit expected contract_bundle_hash does not match the pinned universe contract bundle",
            "Pass the universe contract bundle hash recorded by the target SessionSpec, or recreate the session before boot.",
            details={"expected_contract_bundle_hash": expected_contract_hash, "actual_contract_bundle_hash": actual_contract_hash},
            path="$.contract_bundle_hash",
        )

    bundle_token = (
        str(session_spec.get("bundle_id", "")).strip()
        or str((dict(server_config.get("extensions") or {})).get("official.bundle_id", "")).strip()
        or "bundle.base.lab"
    )
    compiled_lock_payload, compiled_lock_error = _load_lockfile(
        repo_root=repo_root,
        compile_if_missing=bool(compile_if_missing),
        bundle_id=bundle_token,
        mod_policy_id=selected_mod_policy_id,
    )
    if compiled_lock_error:
        return compiled_lock_error
    effective_lock_payload = dict(compiled_lock_payload)
    runtime_pack_lock_path = str(pack_lock_path or "").strip()
    if runtime_pack_lock_path:
        runtime_lock_payload, runtime_lock_error = _runtime_pack_lock_payload(
            repo_root=repo_root,
            pack_lock_path=os.path.normpath(os.path.abspath(runtime_pack_lock_path)),
        )
        if runtime_lock_error:
            return runtime_lock_error
        effective_lock_payload = dict(runtime_lock_payload)

    session_pack_lock_hash = str(session_spec.get("pack_lock_hash", "")).strip()
    effective_pack_lock_hash = str(effective_lock_payload.get("pack_lock_hash", "")).strip()
    if session_pack_lock_hash != effective_pack_lock_hash:
        return _server_refusal(
            REFUSAL_SESSION_PACK_LOCK_MISMATCH,
            "SessionSpec pack_lock_hash does not match runtime pack lock",
            "Boot the server with the pinned pack lock for this save or recreate the server session.",
            details={"session_pack_lock_hash": session_pack_lock_hash, "runtime_pack_lock_hash": effective_pack_lock_hash},
            path="$.pack_lock_hash",
        )
    identity_pack_lock_hash = str(universe_identity.get("initial_pack_set_hash_expectation", "")).strip()
    if identity_pack_lock_hash and identity_pack_lock_hash != effective_pack_lock_hash:
        return _server_refusal(
            REFUSAL_SESSION_PACK_LOCK_MISMATCH,
            "UniverseIdentity pack set expectation does not match runtime pack lock",
            "Use the original pack lock for this universe lineage or recreate the universe under the new pack set.",
            details={"identity_pack_lock_hash": identity_pack_lock_hash, "runtime_pack_lock_hash": effective_pack_lock_hash},
            path="$.initial_pack_set_hash_expectation",
        )

    registry_payloads, registry_error = _load_compiled_registry_payloads(
        repo_root=repo_root,
        lock_payload=compiled_lock_payload,
        registries_dir=registries_dir,
    )
    if registry_error:
        return registry_error
    mod_policy_proof_bundle = proof_bundle_from_lockfile(compiled_lock_payload)
    mod_policy_enforcement = validate_saved_mod_policy(
        expected_mod_policy_id=selected_mod_policy_id,
        expected_registry_hash=str(session_spec.get("mod_policy_registry_hash", "")).strip(),
        actual_proof_bundle=mod_policy_proof_bundle,
    )
    if str(mod_policy_enforcement.get("result", "")) != "complete":
        return mod_policy_enforcement

    selected_overlay_conflict_policy_id = str(server_config.get("overlay_conflict_policy_id", "")).strip()
    actual_overlay_conflict_policy_id = str(mod_policy_proof_bundle.get("overlay_conflict_policy_id", "")).strip()
    if selected_overlay_conflict_policy_id and actual_overlay_conflict_policy_id and (
        selected_overlay_conflict_policy_id != actual_overlay_conflict_policy_id
    ):
        return _server_refusal(
            REFUSAL_SESSION_CONTRACT_MISMATCH,
            "server overlay_conflict_policy_id does not match runtime mod policy proof bundle",
            "Align server_config overlay_conflict_policy_id with the pinned mod policy or regenerate lock/proof artifacts.",
            details={
                "server_overlay_conflict_policy_id": selected_overlay_conflict_policy_id,
                "runtime_overlay_conflict_policy_id": actual_overlay_conflict_policy_id,
            },
            path="$.overlay_conflict_policy_id",
        )

    (
        selected_physics,
        selected_time_policy,
        selected_dt_rule,
        selected_compaction_policy,
        selected_time_model,
        selected_transition_policy,
        law_profile,
        lens_profile,
        profile_error,
    ) = _select_profiles_for_server(
        session_spec=session_spec,
        universe_identity=universe_identity,
        registry_payloads=registry_payloads,
    )
    if profile_error:
        return profile_error

    runtime_result = initialize_authoritative_runtime(
        repo_root=repo_root,
        save_id=save_token,
        session_spec=dict(session_spec),
        lock_payload=dict(compiled_lock_payload),
        universe_identity=dict(universe_identity),
        universe_state=dict(universe_state),
        law_profile=dict(law_profile),
        lens_profile=dict(lens_profile),
        authority_context=dict(session_spec.get("authority_context") or {}),
        anti_cheat_policy_registry=dict(registry_payloads.get("anti_cheat_policy_registry") or {}),
        anti_cheat_module_registry=dict(registry_payloads.get("anti_cheat_module_registry") or {}),
        replication_policy_registry=dict(registry_payloads.get("net_replication_policy_registry") or {}),
        registry_payloads=dict(registry_payloads),
        snapshot_cadence_ticks=int(server_config.get("proof_anchor_interval_ticks", 1) or 1),
    )
    if str(runtime_result.get("result", "")) != "complete":
        return runtime_result
    runtime = dict(runtime_result.get("runtime") or {})
    baseline = prepare_server_authoritative_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return baseline

    network_payload = dict(session_spec.get("network") or {})
    server_profile_row = _server_profile_row(
        registry_payload=dict(registry_payloads.get("server_profile_registry") or {}),
        server_profile_id=str(network_payload.get("server_profile_id", "")).strip(),
    )
    artifact_root = _server_runtime_artifact_dir(repo_root=repo_root, save_id=save_token)
    os.makedirs(artifact_root, exist_ok=True)
    runtime["server_mvp"] = {
        "server_config": dict(server_config),
        "contract_bundle_hash": str(contract_enforcement.get("contract_bundle_hash", "")).strip(),
        "semantic_contract_registry_hash": str(contract_enforcement.get("semantic_contract_registry_hash", "")).strip(),
        "mod_policy_id": selected_mod_policy_id,
        "mod_policy_registry_hash": str(session_spec.get("mod_policy_registry_hash", "")).strip(),
        "overlay_conflict_policy_id": selected_overlay_conflict_policy_id or actual_overlay_conflict_policy_id,
        "overlay_manifest_hash": str(universe_state.get("overlay_manifest_hash", "")).strip(),
        "proof_anchor_interval_ticks": int(server_config.get("proof_anchor_interval_ticks", 1) or 1),
        "time_anchor_policy_id": "time.anchor.mvp_default",
        "artifact_root": norm(os.path.relpath(artifact_root, repo_root)),
        "listener_endpoint": str(network_payload.get("endpoint", "")).strip(),
        "listener_peer_id": str(network_payload.get("server_peer_id", "")).strip(),
        "server_profile_id": str(network_payload.get("server_profile_id", "")).strip(),
        "server_profile": dict(server_profile_row),
        "law_profile": dict(law_profile),
        "lens_profile": dict(lens_profile),
        "selected_profiles": {
            "physics_profile_id": str(selected_physics.get("physics_profile_id", "")).strip(),
            "time_control_policy_id": str(selected_time_policy.get("time_control_policy_id", "")).strip(),
            "dt_quantization_rule_id": str(selected_dt_rule.get("rule_id", "")).strip(),
            "compaction_policy_id": str(selected_compaction_policy.get("policy_id", "")).strip(),
            "time_model_id": str(selected_time_model.get("time_model_id", "")).strip(),
            "transition_policy_id": str(selected_transition_policy.get("policy_id", "")).strip(),
            "law_profile_id": str(law_profile.get("law_profile_id", "")).strip(),
            "lens_profile_id": str(lens_profile.get("lens_id", "")).strip(),
        },
    }
    runtime["server_mvp_connections"] = {}
    runtime["server_mvp_proof_anchors"] = []
    runtime["server_mvp_epoch_anchors"] = []
    runtime["server_mvp_console_log"] = []
    return {
        "result": "complete",
        "runtime": runtime,
        "server_config": dict(server_config),
        "session_spec": dict(session_spec),
        "universe_identity": dict(universe_identity),
        "universe_state": dict(universe_state),
        "compiled_lock_payload": dict(compiled_lock_payload),
        "effective_lock_payload": dict(effective_lock_payload),
        "registry_payloads": dict(registry_payloads),
        "baseline": dict(baseline),
        "proof_bundle": dict(mod_policy_proof_bundle),
        "contract_proof_bundle": dict(contract_enforcement.get("proof_bundle") or {}),
        "selected_profiles": dict((runtime.get("server_mvp") or {}).get("selected_profiles") or {}),
        "materialized": bool(materialized),
        "materialized_paths": dict(materialized_paths),
        "artifact_root": norm(os.path.relpath(artifact_root, repo_root)),
    }


def submit_client_intent(
    server_boot_payload: Mapping[str, object],
    *,
    connection_id: str,
    intent: Mapping[str, object],
) -> dict:
    runtime = dict((dict(server_boot_payload or {})).get("runtime") or {})
    connection_rows = dict(runtime.get("server_mvp_connections") or {})
    connection = dict(connection_rows.get(str(connection_id or "").strip()) or {})
    if not connection:
        return _server_refusal(
            REFUSAL_CLIENT_UNAUTHORIZED,
            "client connection is not authorized for intent submission",
            "Join through the deterministic loopback handshake before sending intents.",
            details={"connection_id": str(connection_id or "").strip() or "<empty>"},
            path="$.connection_id",
        )
    compatibility_mode_id = str(connection.get("compatibility_mode_id", "")).strip()
    negotiation_record_hash = str(connection.get("negotiation_record_hash", "")).strip()
    if (not compatibility_mode_id) or (not negotiation_record_hash):
        return _server_refusal(
            REFUSAL_CONNECTION_NO_NEGOTIATION,
            "client connection is missing a completed negotiation record",
            "Complete deterministic capability negotiation before submitting client intents.",
            details={"connection_id": str(connection_id or "").strip() or "<empty>"},
            path="$.connection_id",
        )
    if compatibility_mode_id == COMPAT_MODE_READ_ONLY:
        return _server_refusal(
            REFUSAL_CLIENT_READ_ONLY,
            "negotiated read-only compatibility forbids mutation intents",
            "Reconnect with fully compatible products or remain in observation-only mode.",
            details={
                "connection_id": str(connection_id or "").strip() or "<empty>",
                "compatibility_mode_id": compatibility_mode_id,
                "law_profile_id": str(connection.get("law_profile_id_override", "")).strip(),
            },
            path="$.connection_id",
        )
    intent_payload = dict(intent or {})
    intent_id = str(intent_payload.get("intent_id", "")).strip()
    target = str(intent_payload.get("target", "")).strip()
    process_id = str(intent_payload.get("process_id", "")).strip()
    if (not intent_id) or (not target):
        return _server_refusal(
            REFUSAL_CLIENT_UNAUTHORIZED,
            "incoming client intent must declare intent_id and target",
            "Populate intent_id and target before submitting client intents to the authoritative server.",
            details={"connection_id": str(connection_id).strip(), "peer_id": str(connection.get("peer_id", "")).strip()},
            path="$.intent",
        )
    if not process_id:
        return _server_refusal(
            REFUSAL_CLIENT_UNAUTHORIZED,
            "incoming client intent must declare process_id",
            "Map the command or UI action to a canonical process_id before submission.",
            details={"intent_id": intent_id, "target": target},
            path="$.process_id",
        )
    inputs = dict(intent_payload.get("inputs") or {})
    inputs.setdefault("target", target)
    queued = submit_client_intent(
        repo_root=str((dict(server_boot_payload or {})).get("repo_root", "")) or os.getcwd(),
        runtime=runtime,
        peer_id=str(connection.get("peer_id", "")).strip(),
        intent_id=intent_id,
        process_id=process_id,
        inputs=inputs,
    )
    if str(queued.get("result", "")) != "complete":
        return dict(queued)
    return {
        "result": "complete",
        "connection_id": str(connection_id).strip(),
        "peer_id": str(connection.get("peer_id", "")).strip(),
        "intent_id": intent_id,
        "target": target,
        "queue_size": int(queued.get("queue_size", 0) or 0),
    }
