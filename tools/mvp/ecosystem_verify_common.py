"""Deterministic Omega ecosystem verification helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.compat.migration_lifecycle import ARTIFACT_KIND_IDS, DECISION_READ_ONLY  # noqa: E402
from src.lib.save import deterministic_fingerprint as save_manifest_fingerprint  # noqa: E402
from src.lib.save import normalize_save_manifest, write_json as write_save_json  # noqa: E402
from src.meta.identity import (  # noqa: E402
    IDENTITY_KIND_SAVE,
    attach_universal_identity_block,
    identity_content_hash_for_payload,
    validate_identity_path,
)
from src.release import build_default_component_install_plan, platform_targets_for_tag, verify_release_manifest  # noqa: E402
from tools.compat.migration_lifecycle_common import build_migration_lifecycle_report  # noqa: E402
from tools.meta.identity_common import build_identity_report  # noqa: E402
from tools.mvp.baseline_universe_common import load_baseline_universe_snapshot  # noqa: E402
from tools.release.component_graph_common import build_component_graph_report  # noqa: E402
from tools.release.install_profile_common import build_install_profile_report  # noqa: E402
from tools.release.release_identity_common import build_release_identity_report  # noqa: E402
from tools.release.release_index_policy_common import (  # noqa: E402
    build_release_index_policy_fixture_cases,
    build_release_index_policy_report,
)
from tools.security.trust_model_common import build_trust_model_report  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


ECOSYSTEM_VERIFY_RUN_SCHEMA_ID = "dominium.schema.audit.ecosystem_verify_run"
ECOSYSTEM_VERIFY_BASELINE_SCHEMA_ID = "dominium.schema.governance.ecosystem_verify_baseline"
ECOSYSTEM_VERIFY_VERSION = 0
ECOSYSTEM_VERIFY_STABILITY_CLASS = "stable"
ECOSYSTEM_VERIFY_RETRO_AUDIT_REL = os.path.join("docs", "audit", "ECOSYSTEM_VERIFY0_RETRO_AUDIT.md")
ECOSYSTEM_VERIFY_MODEL_DOC_REL = os.path.join("docs", "mvp", "ECOSYSTEM_VERIFY_MODEL_v0_0_0.md")
ECOSYSTEM_VERIFY_RUN_JSON_REL = os.path.join("data", "audit", "ecosystem_verify_run.json")
ECOSYSTEM_VERIFY_RUN_DOC_REL = os.path.join("docs", "audit", "ECOSYSTEM_VERIFY_RUN.md")
ECOSYSTEM_VERIFY_BASELINE_REL = os.path.join("data", "regression", "ecosystem_verify_baseline.json")
ECOSYSTEM_VERIFY_BASELINE_DOC_REL = os.path.join("docs", "audit", "ECOSYSTEM_VERIFY_BASELINE.md")
ECOSYSTEM_VERIFY_TOOL_REL = os.path.join("tools", "mvp", "tool_verify_ecosystem")
ECOSYSTEM_VERIFY_TOOL_PY_REL = os.path.join("tools", "mvp", "tool_verify_ecosystem.py")
ECOSYSTEM_REGRESSION_REQUIRED_TAG = "ECOSYSTEM-REGRESSION-UPDATE"
DEFAULT_PLATFORM_TAG = "win64"
DEFAULT_DIST_ROOT_REL = os.path.join("dist", "v0.0.0-mock", DEFAULT_PLATFORM_TAG, "dominium")
DEFAULT_RELEASE_INDEX_REL = os.path.join(DEFAULT_DIST_ROOT_REL, "manifests", "release_index.json")
DEFAULT_RELEASE_MANIFEST_REL = os.path.join(DEFAULT_DIST_ROOT_REL, "manifests", "release_manifest.json")
DEFAULT_INSTALL_MANIFEST_REL = os.path.join(DEFAULT_DIST_ROOT_REL, "install.manifest.json")
DEFAULT_INSTANCE_MANIFEST_REL = os.path.join(DEFAULT_DIST_ROOT_REL, "instances", "default", "instance.manifest.json")
DEFAULT_PACK_LOCK_REL = os.path.join(DEFAULT_DIST_ROOT_REL, "store", "locks", "pack_lock.mvp_default.json")
DEFAULT_PROFILE_BUNDLE_REL = os.path.join(DEFAULT_DIST_ROOT_REL, "store", "profiles", "bundles", "bundle.mvp_default.json")
DEFAULT_COMPONENT_GRAPH_REGISTRY_REL = os.path.join("data", "registries", "component_graph_registry.json")
DEFAULT_INSTALL_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "install_profile_registry.json")
DEFAULT_GOVERNANCE_PROFILE_REL = os.path.join("data", "governance", "governance_profile.json")
DEFAULT_TEMP_SAVE_REL = os.path.join("build", "tmp", "omega5_ecosystem", "save_fixture", "save.manifest.json")
TARGET_INSTALL_PROFILES = ("install.profile.full", "install.profile.server", "install.profile.tools")
REQUIRED_IDENTITY_KINDS = (
    "identity.bundle",
    "identity.install",
    "identity.instance",
    "identity.manifest",
    "identity.pack",
    "identity.product_binary",
    "identity.save",
    "identity.suite_release",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = _token(rel_path)
    if not token:
        return os.path.normpath(os.path.abspath(repo_root))
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token.replace("/", os.sep))))


def _relative_to(repo_root: str, path: str) -> str:
    token = _token(path)
    if not token:
        return ""
    abs_path = os.path.normpath(os.path.abspath(token))
    try:
        rel = os.path.relpath(abs_path, repo_root)
    except ValueError:
        return _norm(abs_path)
    return _norm(rel)


def _ensure_dir(path: str) -> None:
    token = _token(path)
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
        handle.write(str(text or "").replace("\r\n", "\n"))
    return path


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _artifact_input_summary(repo_root: str, path: str) -> dict:
    abs_path = _repo_abs(repo_root, path)
    exists = os.path.isfile(abs_path)
    payload = _load_json(abs_path) if exists else {}
    return {
        "path": _relative_to(repo_root, abs_path),
        "exists": exists,
        "content_hash": canonical_sha256(payload) if payload else "",
    }


def ecosystem_verify_report_hash(report: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(report or {}), deterministic_fingerprint=""))


def ecosystem_verify_baseline_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def load_ecosystem_verify_report(repo_root: str, path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(root, path or ECOSYSTEM_VERIFY_RUN_JSON_REL))


def load_ecosystem_verify_baseline(repo_root: str, path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(root, path or ECOSYSTEM_VERIFY_BASELINE_REL))


def _target_tuple(repo_root: str, platform_tag: str) -> dict:
    return dict(platform_targets_for_tag(platform_tag, repo_root=repo_root) or {})


def _resolve_profile(repo_root: str, profile_id: str, *, platform_tag: str) -> dict:
    target = _target_tuple(repo_root, platform_tag)
    kwargs = {
        "install_profile_id": _token(profile_id),
        "target_platform": _token(target.get("platform_id")),
        "target_arch": _token(target.get("arch_id")),
        "target_abi": _token(target.get("abi_id")),
    }
    first = dict(build_default_component_install_plan(repo_root, **kwargs) or {})
    second = dict(build_default_component_install_plan(repo_root, **kwargs) or {})
    plan = _as_map(first.get("install_plan"))
    selected = []
    selected_ids = []
    pack_ids = []
    binary_product_ids = []
    for row in _as_list(first.get("selected_component_descriptors")):
        item = _as_map(row)
        component_id = _token(item.get("component_id"))
        component_kind = _token(item.get("component_kind"))
        extensions = _as_map(item.get("extensions"))
        selected.append(
            {
                "component_id": component_id,
                "component_kind": component_kind,
                "content_hash": _token(item.get("content_hash")).lower(),
                "version": _token(item.get("version")),
                "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
            }
        )
        if component_id:
            selected_ids.append(component_id)
        if component_kind == "pack":
            pack_id = _token(extensions.get("pack_id")) or component_id
            if pack_id:
                pack_ids.append(pack_id)
        if component_kind == "binary":
            product_id = _token(extensions.get("product_id")) or component_id.replace("binary.", "", 1)
            if product_id:
                binary_product_ids.append(product_id)
    selected = sorted(selected, key=lambda row: (_token(row.get("component_id")), _token(row.get("content_hash"))))
    return {
        "install_profile_id": _token(profile_id),
        "result": _token(first.get("result")) or "refused",
        "deterministic_replay_match": canonical_json_text(first) == canonical_json_text(second),
        "target": {
            "platform_id": _token(target.get("platform_id")),
            "arch_id": _token(target.get("arch_id")),
            "abi_id": _token(target.get("abi_id")),
        },
        "install_plan_fingerprint": _token(plan.get("deterministic_fingerprint")),
        "resolved_provider_count": len(_as_list(plan.get("resolved_providers"))),
        "resolved_providers": list(_as_list(plan.get("resolved_providers"))),
        "selection_reasons": list(_as_list(_as_map(plan.get("extensions")).get("selection_reasons"))),
        "selected_component_ids": sorted(selected_ids),
        "selected_components": selected,
        "component_set_hash": canonical_sha256(selected),
        "pack_ids": sorted(set(pack_ids)),
        "binary_product_ids": sorted(set(binary_product_ids)),
    }


def _selected_pack_source_compat_paths(pack_lock_payload: Mapping[str, object], selected_pack_ids: set[str]) -> list[str]:
    rel_paths: list[str] = []
    for row in _as_list(_as_map(pack_lock_payload).get("ordered_packs")):
        item = _as_map(row)
        if _token(item.get("pack_id")) not in selected_pack_ids:
            continue
        for source_row in _as_list(item.get("source_packs")):
            compat_path = _token(_as_map(source_row).get("compat_manifest_path"))
            if compat_path:
                rel_paths.append(_norm(compat_path))
    return sorted(set(rel_paths))


def _identity_validation_summary(repo_root: str, rel_path: str) -> dict:
    validation = dict(validate_identity_path(repo_root, rel_path, strict_missing=False) or {})
    return {
        "path": _norm(rel_path),
        "result": _token(validation.get("result")) or "refused",
        "identity_kind_id": _token(_as_map(validation.get("expected")).get("identity_kind_id")),
        "identity_present": bool(validation.get("identity_block")),
        "error_count": len(_as_list(validation.get("errors"))),
        "warning_count": len(_as_list(validation.get("warnings"))),
        "deterministic_fingerprint": canonical_sha256(
            {
                "path": _norm(rel_path),
                "result": _token(validation.get("result")) or "refused",
                "expected": _as_map(validation.get("expected")),
                "errors": _as_list(validation.get("errors")),
                "warnings": _as_list(validation.get("warnings")),
            }
        ),
    }


def _build_temp_save_fixture(repo_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    baseline_snapshot = load_baseline_universe_snapshot(root)
    record = _as_map(baseline_snapshot.get("record"))
    save_artifact = _as_map(record.get("save_artifact"))
    rel_path = _norm(DEFAULT_TEMP_SAVE_REL)
    abs_path = _repo_abs(root, rel_path)
    payload = normalize_save_manifest(
        {
            "save_id": "save.omega5_ecosystem_fixture",
            "save_format_version": "1.0.0",
            "universe_identity_hash": _token(record.get("universe_identity_hash")) or canonical_sha256({"fixture": "omega5_ecosystem_universe"}),
            "universe_contract_bundle_hash": _token(record.get("universe_contract_bundle_hash")),
            "semantic_contract_registry_hash": _token(record.get("semantic_contract_registry_hash")),
            "generator_version_id": _token(record.get("generator_version_id")) or "generator.omega5",
            "realism_profile_id": _token(record.get("realism_profile_id")) or "realism.profile.default",
            "pack_lock_hash": _token(record.get("pack_lock_hash")),
            "overlay_manifest_hash": canonical_sha256({"fixture": "omega5_ecosystem_overlay"}),
            "mod_policy_id": _token(record.get("mod_policy_id")) or "mod.policy.default",
            "created_by_build_id": _token(save_artifact.get("engine_version_created")),
            "migration_chain": [],
            "allow_read_only_open": False,
            "contract_bundle_ref": "universe_contract_bundle.json",
            "state_snapshots_ref": "state.snapshots",
            "patches_ref": "patches",
            "proofs_ref": "proofs",
            "extensions": {"official.source": "OMEGA-5", "official.rel_path": rel_path},
            "deterministic_fingerprint": "",
        }
    )
    payload["deterministic_fingerprint"] = save_manifest_fingerprint(payload)
    payload = attach_universal_identity_block(
        payload,
        identity_kind_id=IDENTITY_KIND_SAVE,
        identity_id="identity.save.{}".format(_token(payload.get("save_id")) or "omega5"),
        stability_class_id="provisional",
        build_id=_token(payload.get("created_by_build_id")),
        format_version=_token(payload.get("save_format_version")),
        schema_version="1.1.0",
        contract_bundle_hash=_token(payload.get("universe_contract_bundle_hash")),
        content_hash=identity_content_hash_for_payload(payload),
        extensions={"official.rel_path": rel_path},
    )
    _ensure_dir(os.path.dirname(abs_path))
    _ensure_dir(os.path.join(os.path.dirname(abs_path), "state.snapshots"))
    _ensure_dir(os.path.join(os.path.dirname(abs_path), "patches"))
    _ensure_dir(os.path.join(os.path.dirname(abs_path), "proofs"))
    _write_canonical_json(os.path.join(os.path.dirname(abs_path), "universe_contract_bundle.json"), {"fixture": "omega5_ecosystem"})
    _write_canonical_json(os.path.join(os.path.dirname(abs_path), "state.snapshots", "snapshot.000.json"), {"tick": 0})
    _write_canonical_json(os.path.join(os.path.dirname(abs_path), "patches", "overlay.000.json"), {"patch_id": "omega5"})
    _write_canonical_json(os.path.join(os.path.dirname(abs_path), "proofs", "anchor.000.json"), {"anchor_id": "proof.omega5"})
    write_save_json(abs_path, payload)
    return {"path": rel_path, "payload": payload, "content_hash": canonical_sha256(payload)}


def _binary_identity_summary(repo_root: str, selected_product_ids: set[str], trust_policy_id: str, dist_root_rel: str, release_manifest_rel: str) -> dict:
    release_identity = build_release_identity_report(repo_root)
    matched_rows = [
        {
            "product_id": _token(_as_map(row).get("product_id")),
            "build_id": _token(_as_map(row).get("build_id")),
            "inputs_hash": _token(_as_map(row).get("inputs_hash")),
            "semantic_contract_registry_hash": _token(_as_map(row).get("semantic_contract_registry_hash")),
        }
        for row in _as_list(release_identity.get("products"))
        if _token(_as_map(row).get("product_id")) in selected_product_ids
    ]
    matched_rows = sorted(matched_rows, key=lambda row: _token(row.get("product_id")))
    missing_products = sorted(selected_product_ids.difference({_token(row.get("product_id")) for row in matched_rows}))
    dist_root = _repo_abs(repo_root, dist_root_rel)
    release_manifest_path = _repo_abs(repo_root, release_manifest_rel)
    default_verify = dict(verify_release_manifest(dist_root, release_manifest_path, repo_root=repo_root, trust_policy_id=trust_policy_id) or {})
    strict_verify = dict(verify_release_manifest(dist_root, release_manifest_path, repo_root=repo_root, trust_policy_id="trust.strict_ranked") or {})
    result = (
        _token(release_identity.get("result")) == "complete"
        and not missing_products
        and _token(default_verify.get("result")) == "complete"
        and _token(strict_verify.get("result")) == "refused"
    )
    return {
        "result": "complete" if result else "refused",
        "selected_binary_product_ids": sorted(selected_product_ids),
        "matched_products": matched_rows,
        "missing_product_ids": missing_products,
        "release_identity_report_fingerprint": _token(release_identity.get("deterministic_fingerprint")),
        "default_release_manifest_verification": {
            "result": _token(default_verify.get("result")),
            "trust_policy_id": _token(default_verify.get("trust_policy_id")),
            "signature_status": _token(default_verify.get("signature_status")),
            "verified_signature_count": int(default_verify.get("verified_signature_count", 0) or 0),
            "warning_count": len(_as_list(default_verify.get("warnings"))),
            "error_count": len(_as_list(default_verify.get("errors"))),
        },
        "strict_release_manifest_verification": {
            "result": _token(strict_verify.get("result")),
            "trust_policy_id": _token(strict_verify.get("trust_policy_id")),
            "signature_status": _token(strict_verify.get("signature_status")),
            "verified_signature_count": int(strict_verify.get("verified_signature_count", 0) or 0),
            "warning_count": len(_as_list(strict_verify.get("warnings"))),
            "error_count": len(_as_list(strict_verify.get("errors"))),
        },
    }


def _identity_coverage(
    repo_root: str,
    *,
    selected_pack_ids: set[str],
    selected_product_ids: set[str],
    release_index_rel: str,
    release_manifest_rel: str,
    install_manifest_rel: str,
    instance_manifest_rel: str,
    pack_lock_rel: str,
    profile_bundle_rel: str,
    dist_root_rel: str,
    trust_policy_id: str,
) -> dict:
    pack_lock_payload = _load_json(_repo_abs(repo_root, pack_lock_rel))
    identity_report = build_identity_report(repo_root, strict_missing=False)
    temp_save = _build_temp_save_fixture(repo_root)
    governed_paths = [
        _norm(install_manifest_rel),
        _norm(instance_manifest_rel),
        _norm(pack_lock_rel),
        _norm(profile_bundle_rel),
        _norm(release_index_rel),
        _norm(release_manifest_rel),
    ]
    governed_paths.extend(_selected_pack_source_compat_paths(pack_lock_payload, selected_pack_ids))
    governed_paths.append(_token(temp_save.get("path")))
    governed_paths = sorted(set(path for path in governed_paths if _token(path)))
    validations = [_identity_validation_summary(repo_root, path) for path in governed_paths]
    invalid_paths = sorted(
        row.get("path", "")
        for row in validations
        if _token(row.get("result")) != "complete"
        or not bool(row.get("identity_present"))
        or int(row.get("error_count", 0) or 0) > 0
    )
    binary_identity = _binary_identity_summary(
        repo_root,
        selected_product_ids,
        trust_policy_id,
        dist_root_rel,
        release_manifest_rel,
    )
    available_identity_kinds = sorted(_token(item) for item in _as_list(identity_report.get("identity_kind_ids")) if _token(item))
    missing_identity_kinds = sorted(set(REQUIRED_IDENTITY_KINDS).difference(available_identity_kinds))
    result = (
        _token(identity_report.get("result")) == "complete"
        and not invalid_paths
        and not missing_identity_kinds
        and _token(binary_identity.get("result")) == "complete"
    )
    return {
        "result": "complete" if result else "refused",
        "global_identity_report_fingerprint": _token(identity_report.get("deterministic_fingerprint")),
        "required_identity_kind_ids": list(REQUIRED_IDENTITY_KINDS),
        "available_identity_kind_ids": available_identity_kinds,
        "missing_identity_kind_ids": missing_identity_kinds,
        "governed_identity_paths": governed_paths,
        "governed_identity_validations": validations,
        "invalid_identity_paths": invalid_paths,
        "binary_identity": binary_identity,
        "temp_save_fixture": {"path": _token(temp_save.get("path")), "content_hash": _token(temp_save.get("content_hash"))},
    }


def _migration_coverage(repo_root: str) -> dict:
    report = build_migration_lifecycle_report(repo_root)
    artifact_kind_ids = sorted(_token(item) for item in _as_list(report.get("artifact_kind_ids")) if _token(item))
    policy_ids = sorted(_token(item) for item in _as_list(report.get("policy_ids")) if _token(item))
    missing_policy_ids = sorted(set(ARTIFACT_KIND_IDS).difference(policy_ids))
    read_only_decision = _as_map(_as_map(report.get("sample_decisions")).get("save_future_read_only"))
    read_only_defined = _token(read_only_decision.get("decision_action_id")) == DECISION_READ_ONLY
    result = _token(report.get("result")) == "complete" and artifact_kind_ids == policy_ids and not missing_policy_ids and read_only_defined
    return {
        "result": "complete" if result else "refused",
        "artifact_kind_ids": artifact_kind_ids,
        "policy_ids": policy_ids,
        "missing_policy_ids": missing_policy_ids,
        "read_only_decision_defined": read_only_defined,
        "read_only_decision": {
            "decision_action_id": _token(read_only_decision.get("decision_action_id")),
            "refusal_code": _token(read_only_decision.get("refusal_code")),
            "target_version": _token(read_only_decision.get("target_version")),
            "remediation_hint": _token(read_only_decision.get("remediation_hint")),
        },
        "migration_report_fingerprint": _token(report.get("deterministic_fingerprint")),
    }


def _trust_coverage(repo_root: str, governance_profile_path: str, release_index_rel: str, trust_policy_id: str, dist_root_rel: str, release_manifest_rel: str) -> dict:
    governance = _load_json(_repo_abs(repo_root, governance_profile_path))
    release_index = _load_json(_repo_abs(repo_root, release_index_rel))
    trust_report = build_trust_model_report(repo_root)
    default_trust_policy_id = _token(_as_map(governance.get("extensions")).get("default_trust_policy_id")) or "trust.default_mock"
    governance_profile_hash = canonical_sha256(governance) if governance else ""
    governance_hash_matches = governance_profile_hash == _token(release_index.get("governance_profile_hash"))
    selected_trust_policy_id = _token(trust_policy_id) or default_trust_policy_id
    selected_policy_known = selected_trust_policy_id in {_token(item) for item in _as_list(trust_report.get("policy_ids"))}
    default_verify = dict(
        verify_release_manifest(
            _repo_abs(repo_root, dist_root_rel),
            _repo_abs(repo_root, release_manifest_rel),
            repo_root=repo_root,
            trust_policy_id=default_trust_policy_id,
        )
        or {}
    )
    strict_verify = dict(
        verify_release_manifest(
            _repo_abs(repo_root, dist_root_rel),
            _repo_abs(repo_root, release_manifest_rel),
            repo_root=repo_root,
            trust_policy_id="trust.strict_ranked",
        )
        or {}
    )
    cases = _as_map(trust_report.get("cases"))
    result = (
        _token(trust_report.get("result")) == "complete"
        and governance_hash_matches
        and selected_policy_known
        and _token(_as_map(cases.get("default_unsigned")).get("result")) == "warn"
        and _token(_as_map(cases.get("strict_unsigned")).get("result")) == "refused"
        and _token(default_verify.get("result")) == "complete"
        and _token(strict_verify.get("result")) == "refused"
    )
    return {
        "result": "complete" if result else "refused",
        "default_trust_policy_id": default_trust_policy_id,
        "selected_trust_policy_id": selected_trust_policy_id,
        "selected_policy_known": selected_policy_known,
        "governance_profile_hash": governance_profile_hash,
        "release_index_governance_profile_hash": _token(release_index.get("governance_profile_hash")),
        "governance_hash_matches_release_index": governance_hash_matches,
        "trust_report_fingerprint": _token(trust_report.get("deterministic_fingerprint")),
        "case_results": {
            "default_unsigned": _token(_as_map(cases.get("default_unsigned")).get("result")),
            "strict_unsigned": _token(_as_map(cases.get("strict_unsigned")).get("result")),
            "invalid_signature": _token(_as_map(cases.get("invalid_signature")).get("result")),
            "strict_signed": _token(_as_map(cases.get("strict_signed")).get("result")),
        },
        "default_manifest_verification": {
            "result": _token(default_verify.get("result")),
            "trust_policy_id": _token(default_verify.get("trust_policy_id")),
            "signature_status": _token(default_verify.get("signature_status")),
            "warning_count": len(_as_list(default_verify.get("warnings"))),
            "error_count": len(_as_list(default_verify.get("errors"))),
        },
        "strict_manifest_verification": {
            "result": _token(strict_verify.get("result")),
            "trust_policy_id": _token(strict_verify.get("trust_policy_id")),
            "signature_status": _token(strict_verify.get("signature_status")),
            "warning_count": len(_as_list(strict_verify.get("warnings"))),
            "error_count": len(_as_list(strict_verify.get("errors"))),
        },
    }


def _update_coverage(repo_root: str, platform_tag: str) -> dict:
    report = build_release_index_policy_report(repo_root, platform_tag=platform_tag)
    first_cases = build_release_index_policy_fixture_cases(repo_root, platform_tag=platform_tag)
    second_cases = build_release_index_policy_fixture_cases(repo_root, platform_tag=platform_tag)
    latest_fixture = _as_map(report.get("latest_fixture"))
    first_latest = _as_map(_as_map(first_cases.get("latest_result")).get("update_plan"))
    second_latest = _as_map(_as_map(second_cases.get("latest_result")).get("update_plan"))
    selected_yanked_component_ids = list(_as_list(latest_fixture.get("selected_yanked_component_ids")))
    skipped_yanked_count = int(latest_fixture.get("skipped_yanked_count", 0) or 0)
    deterministic = canonical_json_text(first_latest) == canonical_json_text(second_latest)
    result = _token(report.get("result")) == "complete" and deterministic and not selected_yanked_component_ids and skipped_yanked_count >= 1
    return {
        "result": "complete" if result else "refused",
        "policy_report_fingerprint": _token(report.get("deterministic_fingerprint")),
        "latest_compatible_plan_fingerprint": _token(latest_fixture.get("plan_fingerprint")),
        "latest_compatible_selected_client_version": _token(latest_fixture.get("selected_client_version")),
        "latest_compatible_selected_client_build_id": _token(latest_fixture.get("selected_client_build_id")),
        "selected_yanked_component_ids": selected_yanked_component_ids,
        "skipped_yanked_count": skipped_yanked_count,
        "deterministic_replay_match": deterministic,
        "default_resolution_policy_id": _token(report.get("default_resolution_policy_id")),
        "latest_update_plan_verification_steps": list(_as_list(first_latest.get("verification_steps"))),
    }


def build_ecosystem_verify_baseline(report: Mapping[str, object]) -> dict:
    payload = _as_map(report)
    profile_rows = []
    for row in _as_list(payload.get("resolved_profiles")):
        item = _as_map(row)
        profile_rows.append(
            {
                "install_profile_id": _token(item.get("install_profile_id")),
                "install_plan_fingerprint": _token(item.get("install_plan_fingerprint")),
                "component_set_hash": _token(item.get("component_set_hash")),
                "selected_components": [
                    {
                        "component_id": _token(_as_map(component).get("component_id")),
                        "content_hash": _token(_as_map(component).get("content_hash")),
                    }
                    for component in _as_list(item.get("selected_components"))
                ],
            }
        )
    identity = _as_map(payload.get("identity_coverage"))
    migration = _as_map(payload.get("migration_coverage"))
    update = _as_map(payload.get("update_coverage"))
    trust = _as_map(payload.get("trust_coverage"))
    baseline = {
        "schema_id": ECOSYSTEM_VERIFY_BASELINE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "baseline_id": "ecosystem_verify.baseline.v0_0_0",
        "ecosystem_verify_version": ECOSYSTEM_VERIFY_VERSION,
        "stability_class": ECOSYSTEM_VERIFY_STABILITY_CLASS,
        "result": _token(payload.get("result")) or "refused",
        "platform_tag": _token(payload.get("platform_tag")) or DEFAULT_PLATFORM_TAG,
        "resolved_profiles": sorted(profile_rows, key=lambda row: _token(row.get("install_profile_id"))),
        "identity_coverage": {
            "result": _token(identity.get("result")),
            "governed_identity_paths": list(_as_list(identity.get("governed_identity_paths"))),
            "invalid_identity_paths": list(_as_list(identity.get("invalid_identity_paths"))),
            "required_identity_kind_ids": list(_as_list(identity.get("required_identity_kind_ids"))),
            "missing_identity_kind_ids": list(_as_list(identity.get("missing_identity_kind_ids"))),
            "binary_product_ids": list(_as_list(_as_map(identity.get("binary_identity")).get("selected_binary_product_ids"))),
            "binary_identity_result": _token(_as_map(identity.get("binary_identity")).get("result")),
        },
        "migration_coverage": {
            "result": _token(migration.get("result")),
            "artifact_kind_ids": list(_as_list(migration.get("artifact_kind_ids"))),
            "policy_ids": list(_as_list(migration.get("policy_ids"))),
            "missing_policy_ids": list(_as_list(migration.get("missing_policy_ids"))),
            "read_only_decision_defined": bool(migration.get("read_only_decision_defined")),
        },
        "trust_coverage": {
            "result": _token(trust.get("result")),
            "selected_trust_policy_id": _token(trust.get("selected_trust_policy_id")),
            "governance_hash_matches_release_index": bool(trust.get("governance_hash_matches_release_index")),
        },
        "update_plan_hashes": {
            "latest_compatible_plan_fingerprint": _token(update.get("latest_compatible_plan_fingerprint")),
            "selected_yanked_component_ids": list(_as_list(update.get("selected_yanked_component_ids"))),
            "skipped_yanked_count": int(update.get("skipped_yanked_count", 0) or 0),
            "deterministic_replay_match": bool(update.get("deterministic_replay_match")),
        },
        "verification_hashes": dict(_as_map(payload.get("verification_hashes"))),
        "update_policy": {"required_commit_tag": ECOSYSTEM_REGRESSION_REQUIRED_TAG},
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = ecosystem_verify_baseline_hash(baseline)
    return baseline


def _baseline_comparison(report: Mapping[str, object], committed_baseline: Mapping[str, object]) -> dict:
    expected = build_ecosystem_verify_baseline(report)
    current = _as_map(committed_baseline)
    if not current:
        return {
            "baseline_present": False,
            "baseline_matches": False,
            "expected_baseline_fingerprint": _token(expected.get("deterministic_fingerprint")),
            "committed_baseline_fingerprint": "",
        }
    return {
        "baseline_present": True,
        "baseline_matches": canonical_json_text(expected) == canonical_json_text(current),
        "expected_baseline_fingerprint": _token(expected.get("deterministic_fingerprint")),
        "committed_baseline_fingerprint": _token(current.get("deterministic_fingerprint")),
    }


def verify_ecosystem(
    repo_root: str,
    *,
    release_index_path: str = "",
    component_graph_path: str = "",
    install_profile_registry_path: str = "",
    governance_profile_path: str = "",
    trust_policy_id: str = "",
    platform_tag: str = DEFAULT_PLATFORM_TAG,
) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    release_index_rel = _norm(release_index_path or DEFAULT_RELEASE_INDEX_REL)
    component_graph_rel = _norm(component_graph_path or DEFAULT_COMPONENT_GRAPH_REGISTRY_REL)
    install_profile_rel = _norm(install_profile_registry_path or DEFAULT_INSTALL_PROFILE_REGISTRY_REL)
    governance_rel = _norm(governance_profile_path or DEFAULT_GOVERNANCE_PROFILE_REL)
    dist_root_rel = _norm(DEFAULT_DIST_ROOT_REL)
    release_manifest_rel = _norm(DEFAULT_RELEASE_MANIFEST_REL)
    install_manifest_rel = _norm(DEFAULT_INSTALL_MANIFEST_REL)
    instance_manifest_rel = _norm(DEFAULT_INSTANCE_MANIFEST_REL)
    pack_lock_rel = _norm(DEFAULT_PACK_LOCK_REL)
    profile_bundle_rel = _norm(DEFAULT_PROFILE_BUNDLE_REL)

    component_graph_report = build_component_graph_report(root, platform_tag=platform_tag)
    install_profile_report = build_install_profile_report(root, platform_tag=platform_tag)
    resolved_profiles = [_resolve_profile(root, profile_id, platform_tag=platform_tag) for profile_id in TARGET_INSTALL_PROFILES]
    selected_pack_ids = set()
    selected_product_ids = set()
    for row in resolved_profiles:
        selected_pack_ids.update(str(item).strip() for item in row.get("pack_ids") or [] if str(item).strip())
        selected_product_ids.update(str(item).strip() for item in row.get("binary_product_ids") or [] if str(item).strip())

    selected_trust_policy_id = _token(trust_policy_id) or _token(_as_map(_load_json(_repo_abs(root, governance_rel)).get("extensions")).get("default_trust_policy_id")) or "trust.default_mock"
    identity_coverage = _identity_coverage(
        root,
        selected_pack_ids=selected_pack_ids,
        selected_product_ids=selected_product_ids,
        release_index_rel=release_index_rel,
        release_manifest_rel=release_manifest_rel,
        install_manifest_rel=install_manifest_rel,
        instance_manifest_rel=instance_manifest_rel,
        pack_lock_rel=pack_lock_rel,
        profile_bundle_rel=profile_bundle_rel,
        dist_root_rel=dist_root_rel,
        trust_policy_id=selected_trust_policy_id,
    )
    migration_coverage = _migration_coverage(root)
    trust_coverage = _trust_coverage(root, governance_rel, release_index_rel, selected_trust_policy_id, dist_root_rel, release_manifest_rel)
    update_coverage = _update_coverage(root, platform_tag)

    core_result = (
        _token(component_graph_report.get("result")) == "complete"
        and _token(install_profile_report.get("result")) == "complete"
        and all(_token(row.get("result")) == "complete" for row in resolved_profiles)
        and all(bool(row.get("deterministic_replay_match")) for row in resolved_profiles)
        and _token(identity_coverage.get("result")) == "complete"
        and _token(migration_coverage.get("result")) == "complete"
        and _token(trust_coverage.get("result")) == "complete"
        and _token(update_coverage.get("result")) == "complete"
    )
    report = {
        "schema_id": ECOSYSTEM_VERIFY_RUN_SCHEMA_ID,
        "schema_version": "1.0.0",
        "ecosystem_verify_version": ECOSYSTEM_VERIFY_VERSION,
        "stability_class": ECOSYSTEM_VERIFY_STABILITY_CLASS,
        "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "result": "complete" if core_result else "refused",
        "input_artifacts": {
            "release_index": _artifact_input_summary(root, release_index_rel),
            "component_graph_registry": _artifact_input_summary(root, component_graph_rel),
            "install_profile_registry": _artifact_input_summary(root, install_profile_rel),
            "governance_profile": _artifact_input_summary(root, governance_rel),
            "release_manifest": _artifact_input_summary(root, release_manifest_rel),
        },
        "component_graph_report_fingerprint": _token(component_graph_report.get("deterministic_fingerprint")),
        "install_profile_report_fingerprint": _token(install_profile_report.get("deterministic_fingerprint")),
        "resolved_profiles": resolved_profiles,
        "identity_coverage": identity_coverage,
        "migration_coverage": migration_coverage,
        "trust_coverage": trust_coverage,
        "update_coverage": update_coverage,
        "verification_hashes": {
            "resolved_profiles_hash": canonical_sha256(resolved_profiles),
            "identity_coverage_hash": canonical_sha256(identity_coverage),
            "migration_coverage_hash": canonical_sha256(migration_coverage),
            "trust_coverage_hash": canonical_sha256(trust_coverage),
            "update_coverage_hash": canonical_sha256(update_coverage),
        },
        "deterministic_fingerprint": "",
    }
    report["baseline_comparison"] = _baseline_comparison(report, load_ecosystem_verify_baseline(root))
    if bool(_as_map(report.get("baseline_comparison")).get("baseline_present")) and not bool(_as_map(report.get("baseline_comparison")).get("baseline_matches")):
        report["result"] = "refused"
    report["deterministic_fingerprint"] = ecosystem_verify_report_hash(report)
    return report


def render_ecosystem_verify_run(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: stable",
        "Future Series: OMEGA",
        "Replacement Target: Frozen ecosystem integrity baseline for v0.0.0-mock distribution gating.",
        "",
        "# Ecosystem Verify Run",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- platform_tag: `{}`".format(_token(payload.get("platform_tag"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "- baseline_present: `{}`".format(bool(_as_map(payload.get("baseline_comparison")).get("baseline_present"))),
        "- baseline_matches: `{}`".format(bool(_as_map(payload.get("baseline_comparison")).get("baseline_matches"))),
        "",
        "## Resolved Profiles",
        "",
    ]
    for row in _as_list(payload.get("resolved_profiles")):
        item = _as_map(row)
        lines.append("- `{}` -> result=`{}`, components=`{}`, plan=`{}`".format(_token(item.get("install_profile_id")), _token(item.get("result")), len(_as_list(item.get("selected_components"))), _token(item.get("install_plan_fingerprint"))))
    identity = _as_map(payload.get("identity_coverage"))
    lines.extend(
        [
            "",
            "## Identity Coverage",
            "",
            "- result: `{}`".format(_token(identity.get("result"))),
            "- governed_identity_paths: `{}`".format(len(_as_list(identity.get("governed_identity_paths")))),
            "- invalid_identity_paths: `{}`".format(len(_as_list(identity.get("invalid_identity_paths")))),
            "- binary_identity_result: `{}`".format(_token(_as_map(identity.get("binary_identity")).get("result"))),
            "",
            "## Migration Coverage",
            "",
            "- result: `{}`".format(_token(_as_map(payload.get("migration_coverage")).get("result"))),
            "- artifact_kinds: `{}`".format(len(_as_list(_as_map(payload.get("migration_coverage")).get("artifact_kind_ids")))),
            "- policies: `{}`".format(len(_as_list(_as_map(payload.get("migration_coverage")).get("policy_ids")))),
            "",
            "## Trust Coverage",
            "",
            "- result: `{}`".format(_token(_as_map(payload.get("trust_coverage")).get("result"))),
            "- selected_trust_policy_id: `{}`".format(_token(_as_map(payload.get("trust_coverage")).get("selected_trust_policy_id"))),
            "- governance_hash_matches_release_index: `{}`".format(bool(_as_map(payload.get("trust_coverage")).get("governance_hash_matches_release_index"))),
            "",
            "## Update Coverage",
            "",
            "- result: `{}`".format(_token(_as_map(payload.get("update_coverage")).get("result"))),
            "- latest_compatible_plan_fingerprint: `{}`".format(_token(_as_map(payload.get("update_coverage")).get("latest_compatible_plan_fingerprint"))),
            "- selected_yanked_component_ids: `{}`".format(", ".join(_as_list(_as_map(payload.get("update_coverage")).get("selected_yanked_component_ids"))) or "none"),
            "- skipped_yanked_count: `{}`".format(int(_as_map(payload.get("update_coverage")).get("skipped_yanked_count", 0) or 0)),
            "",
        ]
    )
    return "\n".join(lines)


def render_ecosystem_verify_baseline(baseline: Mapping[str, object]) -> str:
    payload = _as_map(baseline)
    lines = [
        "Status: DERIVED",
        "Stability: stable",
        "Future Series: OMEGA",
        "Replacement Target: Frozen ecosystem integrity baseline for v0.0.0-mock distribution gating.",
        "",
        "# Ecosystem Verify Baseline",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- platform_tag: `{}`".format(_token(payload.get("platform_tag"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Resolved Component Sets",
        "",
    ]
    for row in _as_list(payload.get("resolved_profiles")):
        item = _as_map(row)
        component_ids = ", ".join(_token(_as_map(component).get("component_id")) for component in _as_list(item.get("selected_components")))
        lines.append("- `{}` -> `{}`".format(_token(item.get("install_profile_id")), component_ids or "none"))
    lines.extend(
        [
            "",
            "## Identity Coverage Summary",
            "",
            "- result: `{}`".format(_token(_as_map(payload.get("identity_coverage")).get("result"))),
            "- invalid_identity_paths: `{}`".format(", ".join(_as_list(_as_map(payload.get("identity_coverage")).get("invalid_identity_paths"))) or "none"),
            "",
            "## Migration Coverage Summary",
            "",
            "- result: `{}`".format(_token(_as_map(payload.get("migration_coverage")).get("result"))),
            "- missing_policy_ids: `{}`".format(", ".join(_as_list(_as_map(payload.get("migration_coverage")).get("missing_policy_ids"))) or "none"),
            "",
            "## Update Plan Summary",
            "",
            "- latest_compatible_plan_fingerprint: `{}`".format(_token(_as_map(payload.get("update_plan_hashes")).get("latest_compatible_plan_fingerprint"))),
            "- selected_yanked_component_ids: `{}`".format(", ".join(_as_list(_as_map(payload.get("update_plan_hashes")).get("selected_yanked_component_ids"))) or "none"),
            "- skipped_yanked_count: `{}`".format(int(_as_map(payload.get("update_plan_hashes")).get("skipped_yanked_count", 0) or 0)),
            "",
            "## Readiness",
            "",
            "- Ready for Ω-6 update channel simulation once this baseline stays green under RepoX, AuditX, TestX, and strict build gates.",
            "",
        ]
    )
    return "\n".join(lines)


def write_ecosystem_verify_outputs(repo_root: str, report: Mapping[str, object], *, json_path: str = "", doc_path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return {
        "json_path": _write_canonical_json(_repo_abs(root, json_path or ECOSYSTEM_VERIFY_RUN_JSON_REL), report),
        "doc_path": _write_text(_repo_abs(root, doc_path or ECOSYSTEM_VERIFY_RUN_DOC_REL), render_ecosystem_verify_run(report)),
    }


def write_ecosystem_baseline_outputs(repo_root: str, baseline: Mapping[str, object], *, json_path: str = "", doc_path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return {
        "json_path": _write_canonical_json(_repo_abs(root, json_path or ECOSYSTEM_VERIFY_BASELINE_REL), baseline),
        "doc_path": _write_text(_repo_abs(root, doc_path or ECOSYSTEM_VERIFY_BASELINE_DOC_REL), render_ecosystem_verify_baseline(baseline)),
    }


__all__ = [
    "DEFAULT_PLATFORM_TAG",
    "ECOSYSTEM_REGRESSION_REQUIRED_TAG",
    "ECOSYSTEM_VERIFY_BASELINE_DOC_REL",
    "ECOSYSTEM_VERIFY_BASELINE_REL",
    "ECOSYSTEM_VERIFY_BASELINE_SCHEMA_ID",
    "ECOSYSTEM_VERIFY_MODEL_DOC_REL",
    "ECOSYSTEM_VERIFY_RETRO_AUDIT_REL",
    "ECOSYSTEM_VERIFY_RUN_DOC_REL",
    "ECOSYSTEM_VERIFY_RUN_JSON_REL",
    "ECOSYSTEM_VERIFY_RUN_SCHEMA_ID",
    "build_ecosystem_verify_baseline",
    "ecosystem_verify_baseline_hash",
    "ecosystem_verify_report_hash",
    "load_ecosystem_verify_baseline",
    "load_ecosystem_verify_report",
    "render_ecosystem_verify_baseline",
    "render_ecosystem_verify_run",
    "verify_ecosystem",
    "write_ecosystem_baseline_outputs",
    "write_ecosystem_verify_outputs",
]
