"""Shared deterministic LIB-7 stress scenario, replay, and regression helpers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import importlib
from typing import Dict, List, Mapping, Sequence, Tuple

from compat import build_product_descriptor
from lib.export import export_instance_bundle, export_pack_bundle, export_save_bundle
from lib.install import (
    build_product_build_descriptor,
    deterministic_fingerprint as install_deterministic_fingerprint,
    normalize_contract_range,
    normalize_install_manifest,
    normalize_protocol_range,
    validate_install_manifest,
)
from lib.instance import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
    validate_instance_manifest,
)
from lib.instance.instance_clone import clone_instance_local
from lib.provides import (
    RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
    RESOLUTION_POLICY_EXPLICIT_REQUIRED,
    RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
    canonicalize_provides_declaration,
    canonicalize_provides_resolution,
    resolve_providers,
)
from lib.save import (
    CURRENT_SAVE_FORMAT_VERSION,
    deterministic_fingerprint as save_deterministic_fingerprint,
    evaluate_save_open,
    normalize_save_manifest,
    validate_save_manifest,
    write_json as write_save_json,
)
from packs.compat import verify_pack_set
from tools.launcher.launcher_cli import perform_preflight
from tools.lib.content_store import (
    build_install_ref,
    build_pack_lock_payload,
    build_profile_bundle_payload,
    build_store_locator,
    embed_json_artifact,
    embed_tree_artifact,
    initialize_store_root,
    load_json as load_store_json,
    store_add_artifact,
    store_add_tree_artifact,
)
from tools.compatx.core.semantic_contract_validator import build_default_universe_contract_bundle
from tools.xstack.compatx.canonical_json import canonical_sha256


IMPORT_MOD = importlib.import_module("lib.import")
import_instance_bundle = IMPORT_MOD.import_instance_bundle
import_pack_bundle = IMPORT_MOD.import_pack_bundle
import_save_bundle = IMPORT_MOD.import_save_bundle


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))

DEFAULT_LIB7_SEED = 71007
DEFAULT_WORKSPACE_REL = os.path.join("build", "lib", "stress_workspace")
DEFAULT_SCENARIO_REL = os.path.join("build", "lib", "lib_stress_scenario.json")
DEFAULT_REPORT_REL = os.path.join("build", "lib", "lib_stress_report.json")
DEFAULT_BASELINE_REL = os.path.join("data", "regression", "lib_full_baseline.json")

FIXED_TIMESTAMP = "2000-01-01T00:00:00Z"
PACK_RUNTIME_ID = "official.dominium.runtime.core"
PACK_PROVIDER_OFFICIAL_ID = "official.dominium.dem.primary"
PACK_PROVIDER_FORK_ID = "fork.official.dominium.dem.primary.alt.demx"
PACK_OVERLAY_ALPHA_ID = "local.user.overlay.alpha"
PACK_OVERLAY_BETA_ID = "local.user.overlay.beta"
PROVIDES_EARTH_DEM = "provides.earth.dem.v1"
CONTRACT_LOGIC_EVAL = "contract.logic.eval.v1"


def _ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _norm(path: object) -> str:
    token = str(path or "").replace("\\", "/").strip()
    while token.startswith("./"):
        token = token[2:]
    return token


def _slash(path: str, slash_mode: str) -> str:
    token = _norm(path)
    return token if str(slash_mode or "forward").strip().lower() != "backward" else token.replace("/", "\\")


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def write_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.abspath(str(path or "").strip())
    _ensure_dir(os.path.dirname(target))
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")
    return target


def _safe_rmtree(path: str) -> None:
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        return
    except OSError:
        shutil.rmtree(path, ignore_errors=True)


def _write_text(path: str, text: str) -> str:
    target = os.path.abspath(str(path or "").strip())
    _ensure_dir(os.path.dirname(target))
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))
    return target


def _sha_file(path: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_entries(root_path: str) -> List[dict]:
    rows: List[dict] = []
    for current_root, dirnames, filenames in os.walk(root_path):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            abs_path = os.path.join(current_root, filename)
            rel_path = _norm(os.path.relpath(abs_path, root_path))
            rows.append(
                {
                    "relative_path": rel_path,
                    "content_hash": _sha_file(abs_path),
                    "size_bytes": int(os.path.getsize(abs_path)),
                }
            )
    return rows


def _copy_tree(src: str, dst: str) -> None:
    for current_root, dirnames, filenames in os.walk(src):
        dirnames.sort()
        filenames.sort()
        rel_root = os.path.relpath(current_root, src)
        target_root = dst if rel_root == "." else os.path.join(dst, rel_root)
        _ensure_dir(target_root)
        for filename in filenames:
            shutil.copyfile(os.path.join(current_root, filename), os.path.join(target_root, filename))


def _copy_registries(repo_root: str, workspace_root: str) -> None:
    src_root = os.path.join(repo_root, "data", "registries")
    dst_root = os.path.join(workspace_root, "data", "registries")
    _ensure_dir(dst_root)
    for current_root, dirnames, filenames in os.walk(src_root):
        dirnames.sort()
        filenames.sort()
        rel_root = os.path.relpath(current_root, src_root)
        target_root = dst_root if rel_root == "." else os.path.join(dst_root, rel_root)
        _ensure_dir(target_root)
        for filename in filenames:
            shutil.copyfile(os.path.join(current_root, filename), os.path.join(target_root, filename))


def _install_registry_hash(workspace_root: str) -> str:
    return canonical_sha256(_read_json(os.path.join(workspace_root, "data", "registries", "semantic_contract_registry.json")))


def _relative_path(base_root: str, path: str) -> str:
    return _norm(os.path.relpath(os.path.abspath(path), os.path.abspath(base_root)))


def _pack_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(payload or {})
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _canonical_pack_hash(payload: Mapping[str, object]) -> str:
    body = dict(payload or {})
    body["canonical_hash"] = ""
    return canonical_sha256(body)


def _write_overlay_payloads(pack_dir: str, pack_id: str, layer_id: str, display_value: str) -> None:
    layer_payload = {
        "schema_version": "1.0.0",
        "layer_id": layer_id,
        "layer_kind": "mod",
        "precedence_order": 200,
        "source_ref": "overlay.{}".format(pack_id),
        "extensions": {"pack_id": pack_id, "source": "LIB-7"},
        "deterministic_fingerprint": "",
    }
    layer_payload["deterministic_fingerprint"] = _pack_fingerprint(layer_payload)
    patch_row = {
        "schema_version": "1.0.0",
        "target_object_id": "object.lib7.shared",
        "property_path": "display_name",
        "operation": "set",
        "value": display_value,
        "originating_layer_id": layer_id,
        "deterministic_fingerprint": "",
        "extensions": {"source": "LIB-7"},
    }
    patch_row["deterministic_fingerprint"] = _pack_fingerprint(patch_row)
    write_json(os.path.join(pack_dir, "data", "overlay.layer.json"), layer_payload)
    write_json(os.path.join(pack_dir, "data", "overlay.patch.json"), {"property_patches": [patch_row]})


def _write_pack(
    workspace_root: str,
    *,
    pack_id: str,
    version: str,
    trust_level_id: str,
    capability_ids: Sequence[str],
    provides_declarations: Sequence[Mapping[str, object]],
    required_provides_ids: Sequence[str],
    signature_status: str,
    contributions: Sequence[Mapping[str, object]],
    required_contract_ranges: Mapping[str, object] | None = None,
    required_protocol_ranges: Mapping[str, object] | None = None,
    degrade_mode_id: str = "pack.degrade.strict_refuse",
) -> dict:
    pack_dir = os.path.join(workspace_root, "packs", "source", pack_id.replace("/", os.sep))
    _ensure_dir(pack_dir)
    for row in list(contributions or []):
        rel_path = _norm(_as_map(row).get("path", ""))
        payload = dict(_as_map(row).get("payload") or {})
        if rel_path and payload:
            write_json(os.path.join(pack_dir, rel_path.replace("/", os.sep)), payload)
    manifest = {
        "schema_version": "1.0.0",
        "pack_id": str(pack_id).strip(),
        "version": str(version).strip(),
        "compatibility": {"session_spec_min": "1.0.0", "session_spec_max": "1.0.0"},
        "dependencies": [],
        "contribution_types": sorted(
            {
                str(_as_map(row).get("type", "")).strip()
                for row in list(contributions or [])
                if str(_as_map(row).get("type", "")).strip()
            }
        )
        or ["registry_entries"],
        "contributions": [
            {
                "type": str(_as_map(row).get("type", "")).strip(),
                "id": str(_as_map(row).get("id", "")).strip(),
                "path": _norm(_as_map(row).get("path", "")),
            }
            for row in list(contributions or [])
        ],
        "canonical_hash": "",
        "signature_status": str(signature_status).strip(),
    }
    manifest["canonical_hash"] = _canonical_pack_hash(manifest)
    write_json(os.path.join(pack_dir, "pack.json"), manifest)

    trust_payload = {
        "schema_version": "1.0.0",
        "pack_id": str(pack_id).strip(),
        "trust_level_id": str(trust_level_id).strip(),
        "signature_hash": "sig.{}".format(canonical_sha256({"pack_id": pack_id, "signature_status": signature_status})[:16]),
        "deterministic_fingerprint": "",
        "extensions": {"official.source": "LIB-7"},
    }
    trust_payload["deterministic_fingerprint"] = _pack_fingerprint(trust_payload)
    write_json(os.path.join(pack_dir, "pack.trust.json"), trust_payload)

    capabilities_payload = {
        "schema_version": "1.0.0",
        "pack_id": str(pack_id).strip(),
        "capability_ids": sorted({str(item).strip() for item in list(capability_ids or []) if str(item).strip()}),
        "deterministic_fingerprint": "",
        "extensions": {"official.source": "LIB-7"},
    }
    capabilities_payload["deterministic_fingerprint"] = _pack_fingerprint(capabilities_payload)
    write_json(os.path.join(pack_dir, "pack.capabilities.json"), capabilities_payload)

    compat_payload = {
        "schema_version": "1.0.0",
        "pack_id": str(pack_id).strip(),
        "pack_version": str(version).strip(),
        "trust_level_id": str(trust_level_id).strip(),
        "capability_ids": list(capabilities_payload.get("capability_ids") or []),
        "required_contract_ranges": {
            str(key): dict(value)
            for key, value in sorted(_as_map(required_contract_ranges).items(), key=lambda item: str(item[0]))
        },
        "required_protocol_ranges": {
            str(key): dict(value)
            for key, value in sorted(_as_map(required_protocol_ranges).items(), key=lambda item: str(item[0]))
        },
        "supported_engine_version_range": {},
        "required_registry_ids": [],
        "provides_declarations": [
            canonicalize_provides_declaration(row, fallback_pack_id=str(pack_id).strip())
            for row in list(provides_declarations or [])
        ],
        "required_provides_ids": sorted({str(item).strip() for item in list(required_provides_ids or []) if str(item).strip()}),
        "provides": sorted(
            {
                str(_as_map(row).get("provides_id", "")).strip()
                for row in list(provides_declarations or [])
                if str(_as_map(row).get("provides_id", "")).strip()
            }
        ),
        "degrade_mode_id": str(degrade_mode_id).strip(),
        "migration_refs": [],
        "deterministic_fingerprint": "",
        "extensions": {"official.source": "LIB-7"},
    }
    compat_payload["deterministic_fingerprint"] = _pack_fingerprint(compat_payload)
    write_json(os.path.join(pack_dir, "pack.compat.json"), compat_payload)
    return {
        "pack_id": str(pack_id).strip(),
        "pack_dir": pack_dir,
        "manifest": manifest,
        "trust_descriptor": trust_payload,
        "capabilities_descriptor": capabilities_payload,
        "compat_manifest": compat_payload,
    }


def _build_product_files(
    descriptor_repo_root: str,
    install_root: str,
    *,
    product_id: str,
    build_id: str,
    product_version: str,
    slash_mode: str,
    protocol_version_override: str = "",
) -> dict:
    binary_name = "dominium_{}".format(product_id)
    binary_path = os.path.join(install_root, "bin", binary_name)
    _write_text(binary_path, "{}:{}\n".format(product_id, build_id))
    descriptor = build_product_descriptor(descriptor_repo_root, product_id=product_id, product_version=product_version)
    if protocol_version_override:
        updated_rows = []
        for row in list(descriptor.get("protocol_versions_supported") or []):
            item = dict(row)
            item["min_version"] = str(protocol_version_override).strip()
            item["max_version"] = str(protocol_version_override).strip()
            updated_rows.append(item)
        descriptor["protocol_versions_supported"] = updated_rows
        descriptor["deterministic_fingerprint"] = canonical_sha256(dict(descriptor, deterministic_fingerprint=""))
    descriptor_path = os.path.join(install_root, "bin", "{}.descriptor.json".format(binary_name))
    write_json(descriptor_path, descriptor)
    return build_product_build_descriptor(
        product_id=product_id,
        build_id=str(build_id).strip(),
        binary_hash=_sha_file(binary_path),
        endpoint_descriptor_hash=canonical_sha256(descriptor),
        binary_ref=_slash(_relative_path(install_root, binary_path), slash_mode),
        descriptor_ref=_slash(_relative_path(install_root, descriptor_path), slash_mode),
        product_version=product_version,
    )


def _build_install_manifest(
    workspace_root: str,
    *,
    descriptor_repo_root: str,
    install_root: str,
    install_id: str,
    install_version: str,
    mode: str,
    slash_mode: str,
    shared_store_root: str = "",
    local_store_root: str = "",
    protocol_version_override: str = "",
    supported_capabilities: Sequence[str] | None = None,
) -> Tuple[str, dict]:
    _ensure_dir(os.path.join(install_root, "bin"))
    registry_payload = _read_json(os.path.join(workspace_root, "data", "registries", "semantic_contract_registry.json"))
    write_json(os.path.join(install_root, "semantic_contract_registry.json"), registry_payload)
    products = ("engine", "game", "client", "server", "launcher", "setup")
    descriptors: Dict[str, dict] = {}
    product_builds: Dict[str, str] = {}
    protocol_ranges: Dict[str, dict] = {}
    contract_ranges: Dict[str, dict] = {}
    for product_id in products:
        build_id = "build.{}.{}".format(product_id, canonical_sha256({"install_id": install_id, "product_id": product_id})[:12])
        descriptor = _build_product_files(
            descriptor_repo_root,
            install_root,
            product_id=product_id,
            build_id=build_id,
            product_version="0.0.0+{}".format(build_id),
            slash_mode=slash_mode,
            protocol_version_override=protocol_version_override,
        )
        descriptors[product_id] = descriptor
        product_builds[product_id] = build_id
        endpoint = _read_json(
            os.path.join(
                install_root,
                descriptor["extensions"]["official.descriptor_ref"].replace("/", os.sep).replace("\\", os.sep),
            )
        )
        for row in list(endpoint.get("protocol_versions_supported") or []):
            item = normalize_protocol_range(row)
            protocol_ranges[str(item.get("protocol_id", "")).strip()] = item
        for row in list(endpoint.get("semantic_contract_versions_supported") or []):
            item = normalize_contract_range(row)
            contract_ranges[str(item.get("contract_category_id", "")).strip()] = item
    manifest = normalize_install_manifest(
        {
            "install_id": str(install_id).strip(),
            "install_version": str(install_version).strip(),
            "install_root": ".",
            "product_builds": product_builds,
            "semantic_contract_registry_hash": _install_registry_hash(workspace_root),
            "supported_protocol_versions": protocol_ranges,
            "supported_contract_ranges": contract_ranges,
            "default_mod_policy_id": "mod_policy.lab",
            "store_root_ref": {
                "store_id": "store.default" if mode == "portable" else "store.shared",
                "root_path": _slash(_relative_path(install_root, local_store_root if mode == "portable" else shared_store_root), slash_mode),
                "manifest_ref": _slash(
                    _relative_path(
                        install_root,
                        os.path.join(local_store_root if mode == "portable" else shared_store_root, "store.root.json"),
                    ),
                    slash_mode,
                ),
            },
            "mode": str(mode).strip(),
            "supported_capabilities": sorted({str(item).strip() for item in list(supported_capabilities or []) if str(item).strip()}),
            "product_build_descriptors": descriptors,
            "extensions": {
                "official.semantic_contract_registry_ref": _slash("semantic_contract_registry.json", slash_mode),
                "official.source": "LIB-7",
            },
            "deterministic_fingerprint": "",
        }
    )
    manifest["deterministic_fingerprint"] = install_deterministic_fingerprint(manifest)
    manifest_path = os.path.join(install_root, "install.manifest.json")
    write_json(manifest_path, manifest)
    return manifest_path, manifest


def _contract_bundle_payload(workspace_root: str, *, bundle_id: str, variant: str) -> Tuple[dict, str]:
    payload = build_default_universe_contract_bundle(
        _read_json(os.path.join(workspace_root, "data", "registries", "semantic_contract_registry.json"))
    )
    payload["extensions"] = dict(_as_map(payload.get("extensions")))
    payload["extensions"]["bundle_id"] = str(bundle_id).strip()
    payload["extensions"]["variant"] = str(variant).strip()
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload, canonical_sha256(payload)


def _instance_manifest_payload(
    *,
    instance_id: str,
    instance_kind: str,
    mode: str,
    install_manifest_path: str,
    install_manifest: Mapping[str, object],
    instance_root: str,
    shared_store_root: str,
    pack_lock_payload: Mapping[str, object],
    profile_bundle_payload: Mapping[str, object],
    profile_bundle_hash: str,
    save_refs: Sequence[str],
    slash_mode: str,
    resolution_policy_id: str = "",
    provides_resolutions: Sequence[Mapping[str, object]] | None = None,
    embedded_builds: Mapping[str, object] | None = None,
    embedded_artifacts: Sequence[Mapping[str, object]] | None = None,
) -> dict:
    payload = normalize_instance_manifest(
        {
            "instance_id": str(instance_id).strip(),
            "instance_kind": str(instance_kind).strip(),
            "mode": str(mode).strip(),
            "install_ref": {
                key: _slash(value, slash_mode)
                for key, value in build_install_ref(instance_root, install_manifest_path, dict(install_manifest or {})).items()
            },
            "store_root": (
                {
                    key: _slash(value, slash_mode) if isinstance(value, str) else value
                    for key, value in build_store_locator(
                        instance_root,
                        shared_store_root,
                        load_store_json(os.path.join(shared_store_root, "store.root.json")),
                    ).items()
                }
                if mode == "linked"
                else {}
            ),
            "embedded_builds": dict(embedded_builds or {}),
            "pack_lock_hash": str(_as_map(pack_lock_payload).get("pack_lock_hash", "")).strip(),
            "profile_bundle_hash": str(profile_bundle_hash or "").strip(),
            "mod_policy_id": str(_as_map(pack_lock_payload).get("mod_policy_id", "mod_policy.lab")).strip() or "mod_policy.lab",
            "overlay_conflict_policy_id": str(
                _as_map(pack_lock_payload).get("overlay_conflict_policy_id", "overlay.conflict.last_wins")
            ).strip()
            or "overlay.conflict.last_wins",
            "default_session_template_id": "session.template.lib7.default",
            "seed_policy": "deterministic_counter",
            "instance_settings": {
                "renderer_mode": None if instance_kind == "instance.server" else "hardware_stub",
                "ui_mode_default": "cli" if instance_kind == "instance.server" else "rendered",
                "allow_read_only_fallback": True,
                "data_root": ".",
                "extensions": {"source": "LIB-7"},
            },
            "save_refs": sorted({str(item).strip() for item in list(save_refs or []) if str(item).strip()}),
            "resolution_policy_id": str(resolution_policy_id or "").strip(),
            "provides_resolutions": list(provides_resolutions or []),
            "embedded_artifacts": list(embedded_artifacts or []),
            "extensions": {
                "instance.last_opened_save_id": (sorted({str(item).strip() for item in list(save_refs or []) if str(item).strip()}) or [""])[0],
                "official.source": "LIB-7",
            },
            "deterministic_fingerprint": "",
        }
    )
    payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload)
    return payload


def _save_manifest_payload(
    workspace_root: str,
    *,
    save_id: str,
    save_root: str,
    contract_bundle_hash: str,
    contract_registry_hash: str,
    contract_bundle_ref: str,
    pack_lock_hash: str,
    created_by_build_id: str,
    save_format_version: str,
    allow_read_only_open: bool,
    generator_suffix: str,
) -> dict:
    payload = normalize_save_manifest(
        {
            "save_id": str(save_id).strip(),
            "save_format_version": str(save_format_version).strip(),
            "universe_identity_hash": canonical_sha256({"save_id": save_id, "variant": generator_suffix}),
            "universe_contract_bundle_hash": str(contract_bundle_hash).strip(),
            "semantic_contract_registry_hash": str(contract_registry_hash).strip(),
            "generator_version_id": "generator.lib7.{}".format(generator_suffix),
            "realism_profile_id": "realism.profile.default",
            "pack_lock_hash": str(pack_lock_hash).strip(),
            "overlay_manifest_hash": canonical_sha256({"save_id": save_id, "overlay": generator_suffix}),
            "mod_policy_id": "mod_policy.lab",
            "created_by_build_id": str(created_by_build_id).strip(),
            "migration_chain": [],
            "allow_read_only_open": bool(allow_read_only_open),
            "contract_bundle_ref": _norm(contract_bundle_ref),
            "state_snapshots_ref": "state.snapshots",
            "patches_ref": "patches",
            "proofs_ref": "proofs",
            "extensions": {"official.source": "LIB-7"},
            "deterministic_fingerprint": "",
        }
    )
    payload["deterministic_fingerprint"] = save_deterministic_fingerprint(payload)
    write_save_json(os.path.join(save_root, "save.manifest.json"), payload)
    return payload


def _write_save_contents(save_root: str, *, contract_bundle_payload: Mapping[str, object], contract_bundle_name: str) -> None:
    _ensure_dir(os.path.join(save_root, "state.snapshots"))
    _ensure_dir(os.path.join(save_root, "patches"))
    _ensure_dir(os.path.join(save_root, "proofs"))
    write_json(os.path.join(save_root, contract_bundle_name), contract_bundle_payload)
    write_json(os.path.join(save_root, "state.snapshots", "snapshot.000.json"), {"tick": 0, "state_id": "state.zero"})
    write_json(os.path.join(save_root, "patches", "overlay.000.json"), {"patch": 0, "source": "LIB-7"})
    write_json(os.path.join(save_root, "proofs", "anchor.000.json"), {"anchor": "proof.lib7"})


def _write_install_registry(workspace_root: str, installs: Sequence[Mapping[str, object]]) -> None:
    payload = {
        "schema_id": "dominium.registry.install_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.install_registry",
            "registry_version": "1.0.0",
            "installs": [
                {
                    "install_id": str(_as_map(row).get("install_id", "")).strip(),
                    "path": _norm(_as_map(row).get("path", "")),
                    "version": str(_as_map(row).get("version", "")).strip(),
                    "semantic_contract_registry_hash": str(
                        _as_map(row).get("semantic_contract_registry_hash", "")
                    ).strip(),
                }
                for row in sorted(list(installs or []), key=lambda item: str(_as_map(item).get("install_id", "")))
            ],
        },
    }
    write_json(os.path.join(workspace_root, "data", "registries", "install_registry.json"), payload)


def _scenario_projection(payload: Mapping[str, object]) -> dict:
    body = dict(payload or {})
    body["deterministic_fingerprint"] = ""
    return body


def _sanitize_validation_payload(workspace_root: str, payload: object) -> object:
    workspace_abs = os.path.abspath(workspace_root)
    if isinstance(payload, Mapping):
        sanitized = {}
        for key, value in sorted(dict(payload).items(), key=lambda row: str(row[0])):
            key_token = str(key)
            if key_token == "artifact_path" and isinstance(value, str) and str(value).strip():
                candidate = os.path.abspath(str(value))
                try:
                    rel_path = os.path.relpath(candidate, workspace_abs)
                except ValueError:
                    sanitized[key_token] = _norm(value)
                else:
                    if not rel_path.startswith(".."):
                        sanitized[key_token] = _norm(rel_path)
                    else:
                        sanitized[key_token] = _norm(value)
                continue
            sanitized[key_token] = _sanitize_validation_payload(workspace_root, value)
        return sanitized
    if isinstance(payload, list):
        return [_sanitize_validation_payload(workspace_root, item) for item in list(payload)]
    return payload


def generate_lib_stress_scenario(
    *,
    repo_root: str,
    out_root: str,
    seed: int = DEFAULT_LIB7_SEED,
    slash_mode: str = "forward",
) -> dict:
    repo_root = os.path.abspath(str(repo_root or REPO_ROOT_HINT).strip() or REPO_ROOT_HINT)
    workspace_root = os.path.abspath(str(out_root or "").strip())
    if os.path.isdir(workspace_root):
        _safe_rmtree(workspace_root)
    _ensure_dir(workspace_root)
    _copy_registries(repo_root, workspace_root)

    shared_store_root = os.path.join(workspace_root, "store.shared")
    initialize_store_root(shared_store_root, store_id="store.shared")

    install_a_root = os.path.join(workspace_root, "installs", "official")
    install_b_root = os.path.join(workspace_root, "installs", "fork")
    install_c_root = os.path.join(workspace_root, "installs", "legacy")
    initialize_store_root(os.path.join(install_c_root, "store"), store_id="store.legacy")

    install_a_manifest_path, install_a_manifest = _build_install_manifest(
        workspace_root,
        descriptor_repo_root=repo_root,
        install_root=install_a_root,
        install_id="official.dominium.install.a",
        install_version="0.0.0",
        mode="linked",
        slash_mode=slash_mode,
        shared_store_root=shared_store_root,
        supported_capabilities=["cap.ui.cli", "cap.ui.rendered", "cap.overlay_patch"],
    )
    install_b_manifest_path, install_b_manifest = _build_install_manifest(
        workspace_root,
        descriptor_repo_root=repo_root,
        install_root=install_b_root,
        install_id="fork.official.dominium.alt.b",
        install_version="0.0.0-fork",
        mode="linked",
        slash_mode=slash_mode,
        shared_store_root=shared_store_root,
        supported_capabilities=["cap.ui.cli", "cap.overlay_patch"],
    )
    install_c_manifest_path, install_c_manifest = _build_install_manifest(
        workspace_root,
        descriptor_repo_root=repo_root,
        install_root=install_c_root,
        install_id="official.dominium.install.legacy.c",
        install_version="0.0.0-legacy",
        mode="portable",
        slash_mode=slash_mode,
        local_store_root=os.path.join(install_c_root, "store"),
        protocol_version_override="0.9.0",
        supported_capabilities=["cap.ui.cli"],
    )

    registry_hash = _install_registry_hash(workspace_root)
    official_contract_bundle, official_contract_hash = _contract_bundle_payload(
        workspace_root,
        bundle_id="contract.bundle.lib7.official",
        variant="official",
    )
    mismatched_contract_bundle, _mismatched_contract_hash = _contract_bundle_payload(
        workspace_root,
        bundle_id="contract.bundle.lib7.mismatch",
        variant="mismatch",
    )

    base_contract_range = {
        CONTRACT_LOGIC_EVAL: {
            "exact_version": CONTRACT_LOGIC_EVAL,
            "min_version": CONTRACT_LOGIC_EVAL,
            "max_version": CONTRACT_LOGIC_EVAL,
        }
    }
    runtime_contributions = [
        {
            "type": "registry_entries",
            "id": "{}.registry".format(PACK_RUNTIME_ID),
            "path": "data/runtime.registry.json",
            "payload": {"registry_entry_id": "{}.runtime".format(PACK_RUNTIME_ID), "source": "LIB-7"},
        }
    ]
    official_provider_contributions = [
        {
            "type": "registry_entries",
            "id": "{}.registry".format(PACK_PROVIDER_OFFICIAL_ID),
            "path": "data/provider.registry.json",
            "payload": {"registry_entry_id": "{}.provider".format(PACK_PROVIDER_OFFICIAL_ID), "source": "LIB-7"},
        }
    ]
    fork_provider_contributions = [
        {
            "type": "registry_entries",
            "id": "{}.registry".format(PACK_PROVIDER_FORK_ID),
            "path": "data/provider.registry.json",
            "payload": {"registry_entry_id": "{}.provider".format(PACK_PROVIDER_FORK_ID), "source": "LIB-7"},
        }
    ]
    overlay_alpha_contributions = [
        {"type": "registry_entries", "id": "{}.layer".format(PACK_OVERLAY_ALPHA_ID), "path": "data/overlay.layer.json", "payload": {}},
        {"type": "registry_entries", "id": "{}.patch".format(PACK_OVERLAY_ALPHA_ID), "path": "data/overlay.patch.json", "payload": {}},
    ]
    overlay_beta_contributions = [
        {"type": "registry_entries", "id": "{}.layer".format(PACK_OVERLAY_BETA_ID), "path": "data/overlay.layer.json", "payload": {}},
        {"type": "registry_entries", "id": "{}.patch".format(PACK_OVERLAY_BETA_ID), "path": "data/overlay.patch.json", "payload": {}},
    ]
    packs = {
        PACK_RUNTIME_ID: _write_pack(
            workspace_root,
            pack_id=PACK_RUNTIME_ID,
            version="1.0.0",
            trust_level_id="trust.official_signed",
            capability_ids=[],
            provides_declarations=[],
            required_provides_ids=[PROVIDES_EARTH_DEM],
            signature_status="signed",
            contributions=runtime_contributions,
            required_contract_ranges=base_contract_range,
        ),
        PACK_PROVIDER_OFFICIAL_ID: _write_pack(
            workspace_root,
            pack_id=PACK_PROVIDER_OFFICIAL_ID,
            version="1.0.0",
            trust_level_id="trust.official_signed",
            capability_ids=[],
            provides_declarations=[
                canonicalize_provides_declaration(
                    {
                        "pack_id": PACK_PROVIDER_OFFICIAL_ID,
                        "provides_id": PROVIDES_EARTH_DEM,
                        "provides_type": "dataset",
                        "priority": 10,
                        "extensions": {"official.source": "LIB-7"},
                    }
                )
            ],
            required_provides_ids=[],
            signature_status="signed",
            contributions=official_provider_contributions,
        ),
        PACK_PROVIDER_FORK_ID: _write_pack(
            workspace_root,
            pack_id=PACK_PROVIDER_FORK_ID,
            version="1.0.1",
            trust_level_id="trust.thirdparty_signed",
            capability_ids=[],
            provides_declarations=[
                canonicalize_provides_declaration(
                    {
                        "pack_id": PACK_PROVIDER_FORK_ID,
                        "provides_id": PROVIDES_EARTH_DEM,
                        "provides_type": "dataset",
                        "priority": 10,
                        "extensions": {"official.source": "LIB-7"},
                    }
                )
            ],
            required_provides_ids=[],
            signature_status="signed",
            contributions=fork_provider_contributions,
        ),
        PACK_OVERLAY_ALPHA_ID: _write_pack(
            workspace_root,
            pack_id=PACK_OVERLAY_ALPHA_ID,
            version="1.0.0",
            trust_level_id="trust.thirdparty_signed",
            capability_ids=["cap.overlay_patch"],
            provides_declarations=[],
            required_provides_ids=[],
            signature_status="signed",
            contributions=overlay_alpha_contributions,
            degrade_mode_id="pack.degrade.best_effort",
        ),
        PACK_OVERLAY_BETA_ID: _write_pack(
            workspace_root,
            pack_id=PACK_OVERLAY_BETA_ID,
            version="1.0.0",
            trust_level_id="trust.thirdparty_signed",
            capability_ids=["cap.overlay_patch"],
            provides_declarations=[],
            required_provides_ids=[],
            signature_status="signed",
            contributions=overlay_beta_contributions,
            degrade_mode_id="pack.degrade.best_effort",
        ),
    }
    _write_overlay_payloads(packs[PACK_OVERLAY_ALPHA_ID]["pack_dir"], PACK_OVERLAY_ALPHA_ID, "layer.lib7.overlay.alpha", "Overlay Alpha")
    _write_overlay_payloads(packs[PACK_OVERLAY_BETA_ID]["pack_dir"], PACK_OVERLAY_BETA_ID, "layer.lib7.overlay.beta", "Overlay Beta")

    pack_hashes: Dict[str, str] = {}
    for pack_id, row in sorted(packs.items()):
        store_result = store_add_tree_artifact(shared_store_root, "packs", row["pack_dir"])
        pack_hashes[pack_id] = str(store_result.get("artifact_hash", "")).strip()
        store_add_tree_artifact(os.path.join(install_c_root, "store"), "packs", row["pack_dir"])

    def _lock_payload(instance_id: str, pack_ids: Sequence[str], *, mod_policy_id: str, overlay_conflict_policy_id: str) -> Tuple[dict, str]:
        source_payload = {
            "pack_hashes": {pack_id: pack_hashes[pack_id] for pack_id in sorted(pack_ids)},
            "semantic_contract_registry_hash": registry_hash,
            "engine_contract_bundle_hash": official_contract_hash,
        }
        declarations: List[dict] = []
        required_ids: List[str] = []
        for pack_id in list(pack_ids or []):
            compat = dict(_as_map(packs[pack_id]).get("compat_manifest") or {})
            declarations.extend(list(compat.get("provides_declarations") or []))
            required_ids.extend(str(item).strip() for item in list(compat.get("required_provides_ids") or []) if str(item).strip())
        return build_pack_lock_payload(
            instance_id=instance_id,
            pack_ids=list(pack_ids or []),
            mod_policy_id=mod_policy_id,
            overlay_conflict_policy_id=overlay_conflict_policy_id,
            required_provides_ids=required_ids,
            provides_declarations=declarations,
            source_payload=source_payload,
        )

    client_lock_payload, client_lock_hash = _lock_payload(
        "instance.linked.client",
        [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID],
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
    )
    server_lock_payload, server_lock_hash = _lock_payload(
        "instance.linked.server",
        [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID, PACK_OVERLAY_ALPHA_ID, PACK_OVERLAY_BETA_ID],
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
    )
    portable_lock_payload, portable_lock_hash = _lock_payload(
        "instance.portable.client",
        [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID],
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
    )
    strict_lock_payload, strict_lock_hash = _lock_payload(
        "instance.strict.ambiguous",
        [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID, PACK_PROVIDER_FORK_ID],
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
    )
    client_profile_payload, client_profile_hash = build_profile_bundle_payload(
        instance_id="instance.linked.client",
        profile_ids=["profile.lib7.client"],
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
    )
    server_profile_payload, server_profile_hash = build_profile_bundle_payload(
        instance_id="instance.linked.server",
        profile_ids=["profile.lib7.server"],
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
    )
    portable_profile_payload, portable_profile_hash = build_profile_bundle_payload(
        instance_id="instance.portable.client",
        profile_ids=["profile.lib7.portable"],
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
    )
    strict_profile_payload, strict_profile_hash = build_profile_bundle_payload(
        instance_id="instance.strict.ambiguous",
        profile_ids=["profile.lib7.strict"],
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
    )
    for payload, artifact_hash in (
        (client_lock_payload, client_lock_hash),
        (server_lock_payload, server_lock_hash),
        (portable_lock_payload, portable_lock_hash),
        (strict_lock_payload, strict_lock_hash),
    ):
        store_add_artifact(shared_store_root, "locks", payload, expected_hash=artifact_hash)
    for payload, artifact_hash in (
        (client_profile_payload, client_profile_hash),
        (server_profile_payload, server_profile_hash),
        (portable_profile_payload, portable_profile_hash),
        (strict_profile_payload, strict_profile_hash),
    ):
        store_add_artifact(shared_store_root, "profiles", payload, expected_hash=artifact_hash)

    mutable_save_root = os.path.join(shared_store_root, "saves", "save.alpha.mutable")
    readonly_save_root = os.path.join(shared_store_root, "saves", "save.alpha.readonly")
    legacy_save_root = os.path.join(shared_store_root, "saves", "save.alpha.legacy")
    _write_save_contents(mutable_save_root, contract_bundle_payload=official_contract_bundle, contract_bundle_name="universe_contract_bundle.json")
    _write_save_contents(readonly_save_root, contract_bundle_payload=mismatched_contract_bundle, contract_bundle_name="universe_contract_bundle.json")
    _write_save_contents(legacy_save_root, contract_bundle_payload=official_contract_bundle, contract_bundle_name="universe_contract_bundle.json")
    mutable_save_manifest = _save_manifest_payload(
        workspace_root,
        save_id="save.alpha.mutable",
        save_root=mutable_save_root,
        contract_bundle_hash=official_contract_hash,
        contract_registry_hash=registry_hash,
        contract_bundle_ref="universe_contract_bundle.json",
        pack_lock_hash=client_lock_hash,
        created_by_build_id=str(_as_map(install_a_manifest.get("product_builds")).get("game", "")).strip(),
        save_format_version=CURRENT_SAVE_FORMAT_VERSION,
        allow_read_only_open=True,
        generator_suffix="mutable",
    )
    readonly_save_manifest = _save_manifest_payload(
        workspace_root,
        save_id="save.alpha.readonly",
        save_root=readonly_save_root,
        contract_bundle_hash=official_contract_hash,
        contract_registry_hash=registry_hash,
        contract_bundle_ref="universe_contract_bundle.json",
        pack_lock_hash=client_lock_hash,
        created_by_build_id=str(_as_map(install_a_manifest.get("product_builds")).get("game", "")).strip(),
        save_format_version=CURRENT_SAVE_FORMAT_VERSION,
        allow_read_only_open=True,
        generator_suffix="readonly",
    )
    legacy_save_manifest = _save_manifest_payload(
        workspace_root,
        save_id="save.alpha.legacy",
        save_root=legacy_save_root,
        contract_bundle_hash=official_contract_hash,
        contract_registry_hash=registry_hash,
        contract_bundle_ref="universe_contract_bundle.json",
        pack_lock_hash=client_lock_hash,
        created_by_build_id=str(_as_map(install_a_manifest.get("product_builds")).get("game", "")).strip(),
        save_format_version="0.9.0",
        allow_read_only_open=True,
        generator_suffix="legacy",
    )

    instances_root = os.path.join(workspace_root, "instances")
    linked_client_root = os.path.join(instances_root, "instance.linked.client")
    linked_server_root = os.path.join(instances_root, "instance.linked.server")
    portable_root = os.path.join(instances_root, "instance.portable.client")
    strict_root = os.path.join(instances_root, "instance.strict.ambiguous")
    for root in (linked_client_root, linked_server_root, portable_root, strict_root):
        _ensure_dir(root)
    linked_client_manifest = _instance_manifest_payload(
        instance_id="instance.linked.client",
        instance_kind="instance.client",
        mode="linked",
        install_manifest_path=install_a_manifest_path,
        install_manifest=install_a_manifest,
        instance_root=linked_client_root,
        shared_store_root=shared_store_root,
        pack_lock_payload=client_lock_payload,
        profile_bundle_payload=client_profile_payload,
        profile_bundle_hash=client_profile_hash,
        save_refs=["save.alpha.mutable", "save.alpha.readonly", "save.alpha.legacy"],
        slash_mode=slash_mode,
    )
    linked_server_manifest = _instance_manifest_payload(
        instance_id="instance.linked.server",
        instance_kind="instance.server",
        mode="linked",
        install_manifest_path=install_a_manifest_path,
        install_manifest=install_a_manifest,
        instance_root=linked_server_root,
        shared_store_root=shared_store_root,
        pack_lock_payload=server_lock_payload,
        profile_bundle_payload=server_profile_payload,
        profile_bundle_hash=server_profile_hash,
        save_refs=["save.alpha.mutable"],
        slash_mode=slash_mode,
    )

    embedded_builds = {}
    for product_id in ("client", "game"):
        source_descriptor = _as_map(_as_map(install_a_manifest.get("product_build_descriptors")).get(product_id))
        extensions = _as_map(source_descriptor.get("extensions"))
        binary_ref = _norm(extensions.get("official.binary_ref", ""))
        descriptor_ref = _norm(extensions.get("official.descriptor_ref", ""))
        source_binary = os.path.join(install_a_root, binary_ref.replace("/", os.sep))
        source_descriptor_path = os.path.join(install_a_root, descriptor_ref.replace("/", os.sep))
        target_binary_rel = _slash("embedded_builds/{}/{}".format(product_id, os.path.basename(source_binary)), slash_mode)
        target_descriptor_rel = _slash(
            "embedded_builds/{}/{}".format(product_id, os.path.basename(source_descriptor_path)),
            slash_mode,
        )
        _ensure_dir(os.path.join(portable_root, "embedded_builds", product_id))
        shutil.copyfile(source_binary, os.path.join(portable_root, target_binary_rel.replace("\\", os.sep)))
        shutil.copyfile(source_descriptor_path, os.path.join(portable_root, target_descriptor_rel.replace("\\", os.sep)))
        embedded_builds[product_id] = {
            "product_id": product_id,
            "build_id": str(source_descriptor.get("build_id", "")).strip(),
            "binary_hash": str(source_descriptor.get("binary_hash", "")).strip(),
            "endpoint_descriptor_hash": str(source_descriptor.get("endpoint_descriptor_hash", "")).strip(),
            "binary_ref": target_binary_rel,
            "descriptor_ref": target_descriptor_rel,
            "extensions": {"official.source": "LIB-7"},
        }

    embed_json_artifact(portable_root, "locks", portable_lock_payload, expected_hash=portable_lock_hash)
    embed_json_artifact(portable_root, "profiles", portable_profile_payload, expected_hash=portable_profile_hash)
    embedded_artifacts = [
        {
            "category": "locks",
            "artifact_hash": portable_lock_hash,
            "artifact_id": str(portable_lock_payload.get("pack_lock_id", "")).strip(),
            "artifact_type": "json",
            "artifact_path": _slash("embedded_artifacts/locks/{}".format(portable_lock_hash), slash_mode),
        },
        {
            "category": "profiles",
            "artifact_hash": portable_profile_hash,
            "artifact_id": str(portable_profile_payload.get("profile_bundle_id", "")).strip(),
            "artifact_type": "json",
            "artifact_path": _slash("embedded_artifacts/profiles/{}".format(portable_profile_hash), slash_mode),
        },
    ]
    for pack_id in list(portable_lock_payload.get("ordered_pack_ids") or []):
        embed_result = embed_tree_artifact(portable_root, "packs", packs[pack_id]["pack_dir"])
        embedded_artifacts.append(
            {
                "category": "packs",
                "artifact_hash": str(embed_result.get("artifact_hash", "")).strip(),
                "artifact_id": pack_id,
                "artifact_type": "tree",
                "artifact_path": _slash(
                    "embedded_artifacts/packs/{}".format(str(embed_result.get("artifact_hash", "")).strip()),
                    slash_mode,
                ),
            }
        )
    portable_manifest = _instance_manifest_payload(
        instance_id="instance.portable.client",
        instance_kind="instance.client",
        mode="portable",
        install_manifest_path=install_a_manifest_path,
        install_manifest=install_a_manifest,
        instance_root=portable_root,
        shared_store_root=shared_store_root,
        pack_lock_payload=portable_lock_payload,
        profile_bundle_payload=portable_profile_payload,
        profile_bundle_hash=portable_profile_hash,
        save_refs=["save.alpha.mutable"],
        slash_mode=slash_mode,
        embedded_builds=embedded_builds,
        embedded_artifacts=embedded_artifacts,
    )
    strict_manifest = _instance_manifest_payload(
        instance_id="instance.strict.ambiguous",
        instance_kind="instance.client",
        mode="linked",
        install_manifest_path=install_b_manifest_path,
        install_manifest=install_b_manifest,
        instance_root=strict_root,
        shared_store_root=shared_store_root,
        pack_lock_payload=strict_lock_payload,
        profile_bundle_payload=strict_profile_payload,
        profile_bundle_hash=strict_profile_hash,
        save_refs=[],
        slash_mode=slash_mode,
        resolution_policy_id=RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
    )

    write_json(os.path.join(linked_client_root, "instance.manifest.json"), linked_client_manifest)
    write_json(os.path.join(linked_server_root, "instance.manifest.json"), linked_server_manifest)
    write_json(os.path.join(portable_root, "instance.manifest.json"), portable_manifest)
    write_json(os.path.join(strict_root, "instance.manifest.json"), strict_manifest)

    _write_install_registry(
        workspace_root,
        installs=[
            {
                "install_id": install_a_manifest["install_id"],
                "path": _relative_path(workspace_root, install_a_root),
                "version": install_a_manifest["install_version"],
                "semantic_contract_registry_hash": install_a_manifest["semantic_contract_registry_hash"],
            },
            {
                "install_id": install_b_manifest["install_id"],
                "path": _relative_path(workspace_root, install_b_root),
                "version": install_b_manifest["install_version"],
                "semantic_contract_registry_hash": install_b_manifest["semantic_contract_registry_hash"],
            },
            {
                "install_id": install_c_manifest["install_id"],
                "path": _relative_path(workspace_root, install_c_root),
                "version": install_c_manifest["install_version"],
                "semantic_contract_registry_hash": install_c_manifest["semantic_contract_registry_hash"],
            },
        ],
    )

    validations = {
        "installs": {
            _relative_path(workspace_root, install_a_manifest_path): _sanitize_validation_payload(workspace_root, validate_install_manifest(
                repo_root=workspace_root, install_manifest_path=install_a_manifest_path
            )),
            _relative_path(workspace_root, install_b_manifest_path): _sanitize_validation_payload(workspace_root, validate_install_manifest(
                repo_root=workspace_root, install_manifest_path=install_b_manifest_path
            )),
            _relative_path(workspace_root, install_c_manifest_path): _sanitize_validation_payload(workspace_root, validate_install_manifest(
                repo_root=workspace_root, install_manifest_path=install_c_manifest_path
            )),
        },
        "instances": {
            _relative_path(workspace_root, os.path.join(linked_client_root, "instance.manifest.json")): _sanitize_validation_payload(workspace_root, validate_instance_manifest(
                repo_root=workspace_root, instance_manifest_path=os.path.join(linked_client_root, "instance.manifest.json")
            )),
            _relative_path(workspace_root, os.path.join(linked_server_root, "instance.manifest.json")): _sanitize_validation_payload(workspace_root, validate_instance_manifest(
                repo_root=workspace_root, instance_manifest_path=os.path.join(linked_server_root, "instance.manifest.json")
            )),
            _relative_path(workspace_root, os.path.join(portable_root, "instance.manifest.json")): _sanitize_validation_payload(workspace_root, validate_instance_manifest(
                repo_root=workspace_root, instance_manifest_path=os.path.join(portable_root, "instance.manifest.json")
            )),
            _relative_path(workspace_root, os.path.join(strict_root, "instance.manifest.json")): _sanitize_validation_payload(workspace_root, validate_instance_manifest(
                repo_root=workspace_root, instance_manifest_path=os.path.join(strict_root, "instance.manifest.json")
            )),
        },
        "saves": {
            _relative_path(workspace_root, os.path.join(mutable_save_root, "save.manifest.json")): _sanitize_validation_payload(workspace_root, validate_save_manifest(
                repo_root=workspace_root, save_manifest_path=os.path.join(mutable_save_root, "save.manifest.json")
            )),
            _relative_path(workspace_root, os.path.join(readonly_save_root, "save.manifest.json")): _sanitize_validation_payload(workspace_root, validate_save_manifest(
                repo_root=workspace_root, save_manifest_path=os.path.join(readonly_save_root, "save.manifest.json")
            )),
            _relative_path(workspace_root, os.path.join(legacy_save_root, "save.manifest.json")): _sanitize_validation_payload(workspace_root, validate_save_manifest(
                repo_root=workspace_root, save_manifest_path=os.path.join(legacy_save_root, "save.manifest.json")
            )),
        },
    }

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.lib7.{}".format(canonical_sha256({"seed": int(seed), "slash_mode": str(slash_mode)})[:16]),
        "seed": int(seed),
        "slash_mode": str(slash_mode or "forward").strip().lower() or "forward",
        "workspace_root": ".",
        "shared_store_root": _relative_path(workspace_root, shared_store_root),
        "installs": [
            {
                "install_id": install_a_manifest["install_id"],
                "mode": install_a_manifest["mode"],
                "path": _relative_path(workspace_root, install_a_root),
                "manifest_path": _relative_path(workspace_root, install_a_manifest_path),
                "semantic_contract_registry_hash": install_a_manifest["semantic_contract_registry_hash"],
            },
            {
                "install_id": install_b_manifest["install_id"],
                "mode": install_b_manifest["mode"],
                "path": _relative_path(workspace_root, install_b_root),
                "manifest_path": _relative_path(workspace_root, install_b_manifest_path),
                "semantic_contract_registry_hash": install_b_manifest["semantic_contract_registry_hash"],
            },
            {
                "install_id": install_c_manifest["install_id"],
                "mode": install_c_manifest["mode"],
                "path": _relative_path(workspace_root, install_c_root),
                "manifest_path": _relative_path(workspace_root, install_c_manifest_path),
                "semantic_contract_registry_hash": install_c_manifest["semantic_contract_registry_hash"],
            },
        ],
        "packs": [
            {
                "pack_id": pack_id,
                "path": _relative_path(workspace_root, row["pack_dir"]),
                "pack_hash": pack_hashes[pack_id],
                "provides_ids": [
                    str(_as_map(item).get("provides_id", "")).strip()
                    for item in list(_as_map(row).get("compat_manifest", {}).get("provides_declarations") or [])
                    if str(_as_map(item).get("provides_id", "")).strip()
                ],
            }
            for pack_id, row in sorted(packs.items())
        ],
        "instances": [
            {
                "instance_id": linked_client_manifest["instance_id"],
                "instance_kind": linked_client_manifest["instance_kind"],
                "mode": linked_client_manifest["mode"],
                "manifest_path": _relative_path(workspace_root, os.path.join(linked_client_root, "instance.manifest.json")),
                "pack_lock_hash": linked_client_manifest["pack_lock_hash"],
                "profile_bundle_hash": linked_client_manifest["profile_bundle_hash"],
                "save_refs": list(linked_client_manifest.get("save_refs") or []),
            },
            {
                "instance_id": linked_server_manifest["instance_id"],
                "instance_kind": linked_server_manifest["instance_kind"],
                "mode": linked_server_manifest["mode"],
                "manifest_path": _relative_path(workspace_root, os.path.join(linked_server_root, "instance.manifest.json")),
                "pack_lock_hash": linked_server_manifest["pack_lock_hash"],
                "profile_bundle_hash": linked_server_manifest["profile_bundle_hash"],
                "save_refs": list(linked_server_manifest.get("save_refs") or []),
            },
            {
                "instance_id": portable_manifest["instance_id"],
                "instance_kind": portable_manifest["instance_kind"],
                "mode": portable_manifest["mode"],
                "manifest_path": _relative_path(workspace_root, os.path.join(portable_root, "instance.manifest.json")),
                "pack_lock_hash": portable_manifest["pack_lock_hash"],
                "profile_bundle_hash": portable_manifest["profile_bundle_hash"],
                "save_refs": list(portable_manifest.get("save_refs") or []),
            },
            {
                "instance_id": strict_manifest["instance_id"],
                "instance_kind": strict_manifest["instance_kind"],
                "mode": strict_manifest["mode"],
                "manifest_path": _relative_path(workspace_root, os.path.join(strict_root, "instance.manifest.json")),
                "pack_lock_hash": strict_manifest["pack_lock_hash"],
                "profile_bundle_hash": strict_manifest["profile_bundle_hash"],
                "save_refs": list(strict_manifest.get("save_refs") or []),
            },
        ],
        "saves": [
            {
                "save_id": mutable_save_manifest["save_id"],
                "manifest_path": _relative_path(workspace_root, os.path.join(mutable_save_root, "save.manifest.json")),
                "allow_read_only_open": bool(mutable_save_manifest.get("allow_read_only_open", False)),
                "save_format_version": mutable_save_manifest["save_format_version"],
                "pack_lock_hash": mutable_save_manifest["pack_lock_hash"],
            },
            {
                "save_id": readonly_save_manifest["save_id"],
                "manifest_path": _relative_path(workspace_root, os.path.join(readonly_save_root, "save.manifest.json")),
                "allow_read_only_open": bool(readonly_save_manifest.get("allow_read_only_open", False)),
                "save_format_version": readonly_save_manifest["save_format_version"],
                "pack_lock_hash": readonly_save_manifest["pack_lock_hash"],
            },
            {
                "save_id": legacy_save_manifest["save_id"],
                "manifest_path": _relative_path(workspace_root, os.path.join(legacy_save_root, "save.manifest.json")),
                "allow_read_only_open": bool(legacy_save_manifest.get("allow_read_only_open", False)),
                "save_format_version": legacy_save_manifest["save_format_version"],
                "pack_lock_hash": legacy_save_manifest["pack_lock_hash"],
            },
        ],
        "validations": validations,
        "extensions": {
            "contract_bundle_hashes": {"official": official_contract_hash, "readonly_manifest_expected": official_contract_hash},
            "pack_sets": {
                "client_linked": [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID],
                "server_linked": [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID, PACK_OVERLAY_ALPHA_ID, PACK_OVERLAY_BETA_ID],
                "portable": [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID],
                "strict_ambiguous": [PACK_RUNTIME_ID, PACK_PROVIDER_OFFICIAL_ID, PACK_PROVIDER_FORK_ID],
            },
            "source": "LIB-7",
        },
        "deterministic_fingerprint": "",
    }
    scenario["deterministic_fingerprint"] = canonical_sha256(_scenario_projection(scenario))
    write_json(os.path.join(workspace_root, "lib_stress_scenario.json"), scenario)
    return scenario


def _scenario_paths(workspace_root: str, scenario: Mapping[str, object]) -> dict:
    installs = {
        str(_as_map(row).get("install_id", "")).strip(): os.path.join(
            workspace_root,
            _norm(_as_map(row).get("manifest_path", "")).replace("/", os.sep),
        )
        for row in list(scenario.get("installs") or [])
    }
    instances = {
        str(_as_map(row).get("instance_id", "")).strip(): os.path.join(
            workspace_root,
            _norm(_as_map(row).get("manifest_path", "")).replace("/", os.sep),
        )
        for row in list(scenario.get("instances") or [])
    }
    saves = {
        str(_as_map(row).get("save_id", "")).strip(): os.path.join(
            workspace_root,
            _norm(_as_map(row).get("manifest_path", "")).replace("/", os.sep),
        )
        for row in list(scenario.get("saves") or [])
    }
    packs = {
        str(_as_map(row).get("pack_id", "")).strip(): os.path.join(
            workspace_root,
            _norm(_as_map(row).get("path", "")).replace("/", os.sep),
        )
        for row in list(scenario.get("packs") or [])
    }
    return {
        "installs": installs,
        "instances": instances,
        "saves": saves,
        "packs": packs,
        "shared_store_root": os.path.join(workspace_root, _norm(scenario.get("shared_store_root", "")).replace("/", os.sep)),
    }


def _preview_pack_subset(
    *,
    schema_repo_root: str,
    workspace_root: str,
    pack_paths: Mapping[str, str],
    selected_pack_ids: Sequence[str],
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    instance_id: str,
    explicit_resolutions: Sequence[Mapping[str, object]] | None = None,
    resolution_policy_id: str = "",
    universe_contract_bundle_path: str = "",
) -> dict:
    with tempfile.TemporaryDirectory(prefix="lib7_pack_preview_") as temp_root:
        _copy_tree(os.path.join(workspace_root, "data"), os.path.join(temp_root, "data"))
        for pack_id in sorted({str(item).strip() for item in list(selected_pack_ids or []) if str(item).strip()}):
            source_root = str(pack_paths.get(pack_id, "")).strip()
            if not source_root or not os.path.isdir(source_root):
                return {
                    "result": "refused",
                    "errors": [{"code": "pack_missing", "path": "$.packs", "message": "pack '{}' is missing".format(pack_id)}],
                    "warnings": [],
                    "report": {"valid": False, "refusal_codes": ["pack_missing"]},
                    "pack_lock": {},
                }
            _copy_tree(source_root, os.path.join(temp_root, "packs", "source", pack_id))
        contract_rel = ""
        if str(universe_contract_bundle_path or "").strip():
            staged_contract = os.path.join(temp_root, "universe_contract_bundle.json")
            shutil.copyfile(universe_contract_bundle_path, staged_contract)
            contract_rel = "universe_contract_bundle.json"
        return verify_pack_set(
            repo_root=temp_root,
            bundle_id="",
            mod_policy_id=str(mod_policy_id or "").strip(),
            overlay_conflict_policy_id=str(overlay_conflict_policy_id or "").strip(),
            instance_id=str(instance_id or "").strip(),
            explicit_provides_resolutions=list(explicit_resolutions or []),
            resolution_policy_id=str(resolution_policy_id or "").strip(),
            schema_repo_root=schema_repo_root,
            universe_contract_bundle_path=contract_rel,
        )


def _run_python_tool(script_rel: str, args: Sequence[str]) -> Tuple[int, dict]:
    script_path = os.path.join(REPO_ROOT_HINT, script_rel.replace("/", os.sep))
    proc = subprocess.run(
        [sys.executable, script_path] + list(args),
        check=False,
        capture_output=True,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    payload = {}
    stdout = str(proc.stdout or "").strip()
    if stdout:
        try:
            payload = json.loads(stdout)
        except ValueError:
            payload = {"stdout": stdout}
    return int(proc.returncode or 0), payload


def _logical_bundle_metrics(bundle_root: str) -> dict:
    items = _tree_entries(bundle_root)
    size_bytes = sum(int(_as_map(row).get("size_bytes", 0) or 0) for row in items)
    item_count = len(items)
    return {
        "size_bytes": int(size_bytes),
        "item_count": int(item_count),
        "logical_time_units": int(item_count + (size_bytes // 128)),
    }


def _sanitize_save_open(result: Mapping[str, object]) -> dict:
    payload = {
        "result": str(_as_map(result).get("result", "")).strip(),
        "refusal_code": str(_as_map(result).get("refusal_code", "")).strip(),
        "read_only_required": bool(_as_map(result).get("read_only_required", False)),
        "migration_applied": bool(_as_map(result).get("migration_applied", False)),
        "migration_required": bool(_as_map(result).get("migration_required", False)),
        "degrade_reasons": sorted({str(item).strip() for item in list(_as_map(result).get("degrade_reasons") or []) if str(item).strip()}),
        "read_only_allowed": bool(_as_map(result).get("read_only_allowed", False)),
    }
    save_manifest = _as_map(_as_map(result).get("save_manifest"))
    if save_manifest:
        payload["save_manifest_fingerprint"] = str(save_manifest.get("deterministic_fingerprint", "")).strip()
        payload["save_id"] = str(save_manifest.get("save_id", "")).strip()
        payload["save_format_version"] = str(save_manifest.get("save_format_version", "")).strip()
        payload["migration_chain_length"] = len(list(save_manifest.get("migration_chain") or []))
    return payload


def _sanitize_provider_result(result: Mapping[str, object]) -> dict:
    return {
        "result": str(_as_map(result).get("result", "")).strip(),
        "refusal_code": str(_as_map(result).get("refusal_code", "")).strip(),
        "resolution_policy_id": str(_as_map(result).get("resolution_policy_id", "")).strip(),
        "selection_logged": bool(_as_map(result).get("selection_logged", False)),
        "auto_selected_provides_ids": sorted(
            {str(item).strip() for item in list(_as_map(result).get("auto_selected_provides_ids") or []) if str(item).strip()}
        ),
        "ambiguous_provides_ids": sorted(
            {str(item).strip() for item in list(_as_map(result).get("ambiguous_provides_ids") or []) if str(item).strip()}
        ),
        "provides_resolutions": [
            {
                "provides_id": str(_as_map(row).get("provides_id", "")).strip(),
                "chosen_pack_id": str(_as_map(row).get("chosen_pack_id", "")).strip(),
                "resolution_policy_id": str(_as_map(row).get("resolution_policy_id", "")).strip(),
                "deterministic_fingerprint": str(_as_map(row).get("deterministic_fingerprint", "")).strip(),
            }
            for row in list(_as_map(result).get("provides_resolutions") or [])
        ],
    }


def _sanitize_pack_verify(result: Mapping[str, object]) -> dict:
    report = _as_map(_as_map(result).get("report"))
    errors = list(result.get("errors") or [])
    return {
        "result": str(_as_map(result).get("result", "")).strip(),
        "valid": bool(report.get("valid", False)),
        "pack_lock_hash": str(_as_map(result).get("pack_lock", {}).get("pack_lock_hash", "")).strip(),
        "refusal_codes": sorted(
            {
                str(item).strip()
                for item in list(report.get("refusal_codes") or []) + [str(_as_map(row).get("code", "")).strip() for row in errors]
                if str(item).strip()
            }
        ),
        "provider_selection_logged": bool(_as_map(report.get("extensions")).get("provider_selection_logged", False)),
        "provides_resolutions": [
            {
                "provides_id": str(_as_map(row).get("provides_id", "")).strip(),
                "chosen_pack_id": str(_as_map(row).get("chosen_pack_id", "")).strip(),
            }
            for row in list(_as_map(report.get("extensions")).get("provides_resolutions") or [])
        ],
    }


def _preflight_namespace(
    *,
    save_id: str = "",
    compat_out: str = "",
    run_mode: str = "play",
    allow_save_migration: bool = False,
) -> object:
    return type(
        "Lib7Args",
        (),
        {
            "deterministic": True,
            "capability_baseline": "BASELINE_MAINLINE_CORE",
            "save": str(save_id or "").strip(),
            "run_mode": str(run_mode).strip(),
            "allow_save_migration": bool(allow_save_migration),
            "migration_tick": 77,
            "save_migration_id": "migration.lib7.replay",
            "profile": [],
            "pack_root": [],
            "compat_out": str(compat_out or "").strip(),
        },
    )()


def _projection_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(payload or {}))


def _round_summary(
    *,
    workspace_root: str,
    round_id: str,
    scenario: Mapping[str, object],
    schema_repo_root: str,
) -> dict:
    paths = _scenario_paths(workspace_root, scenario)
    decision_root = os.path.join(workspace_root, "build", "decision_logs")
    bundle_root = os.path.join(workspace_root, "exports")
    import_root = os.path.join(workspace_root, "imports")
    clone_root = os.path.join(workspace_root, "clones")
    _ensure_dir(decision_root)
    _ensure_dir(bundle_root)
    _ensure_dir(import_root)
    _ensure_dir(clone_root)

    instance_linked_path = paths["instances"]["instance.linked.client"]
    instance_portable_path = paths["instances"]["instance.portable.client"]
    instance_strict_path = paths["instances"]["instance.strict.ambiguous"]
    install_a_path = paths["installs"]["official.dominium.install.a"]
    install_b_path = paths["installs"]["fork.official.dominium.alt.b"]
    save_mutable_path = paths["saves"]["save.alpha.mutable"]
    save_readonly_path = paths["saves"]["save.alpha.readonly"]
    save_legacy_path = paths["saves"]["save.alpha.legacy"]

    install_a_manifest = _read_json(install_a_path)
    install_b_manifest = _read_json(install_b_path)
    instance_linked_manifest = _read_json(instance_linked_path)
    instance_portable_manifest = _read_json(instance_portable_path)
    strict_manifest = _read_json(instance_strict_path)
    mutable_lock_payload = load_store_json(
        os.path.join(paths["shared_store_root"], "store", "locks", str(instance_linked_manifest.get("pack_lock_hash", "")).strip(), "payload.json")
    )
    strict_lock_payload = load_store_json(
        os.path.join(paths["shared_store_root"], "store", "locks", str(strict_manifest.get("pack_lock_hash", "")).strip(), "payload.json")
    )

    pack_paths = dict(paths["packs"])
    client_pack_ids = list(_as_map(scenario.get("extensions")).get("pack_sets", {}).get("client_linked", []))
    server_pack_ids = list(_as_map(scenario.get("extensions")).get("pack_sets", {}).get("server_linked", []))
    strict_pack_ids = list(_as_map(scenario.get("extensions")).get("pack_sets", {}).get("strict_ambiguous", []))
    contract_bundle_path = os.path.join(os.path.dirname(save_mutable_path), "universe_contract_bundle.json")

    official_pack_verify = _preview_pack_subset(
        schema_repo_root=schema_repo_root,
        workspace_root=workspace_root,
        pack_paths=pack_paths,
        selected_pack_ids=client_pack_ids,
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
        instance_id="instance.linked.client",
        universe_contract_bundle_path=contract_bundle_path,
    )
    overlay_last_wins = _preview_pack_subset(
        schema_repo_root=schema_repo_root,
        workspace_root=workspace_root,
        pack_paths=pack_paths,
        selected_pack_ids=server_pack_ids,
        mod_policy_id="mod_policy.lab",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
        instance_id="instance.linked.server",
        universe_contract_bundle_path=contract_bundle_path,
    )
    overlay_strict = _preview_pack_subset(
        schema_repo_root=schema_repo_root,
        workspace_root=workspace_root,
        pack_paths=pack_paths,
        selected_pack_ids=server_pack_ids,
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
        instance_id="instance.linked.server.strict",
        universe_contract_bundle_path=contract_bundle_path,
    )
    ambiguous_strict = _preview_pack_subset(
        schema_repo_root=schema_repo_root,
        workspace_root=workspace_root,
        pack_paths=pack_paths,
        selected_pack_ids=strict_pack_ids,
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
        instance_id="instance.strict.ambiguous",
        resolution_policy_id=RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
        universe_contract_bundle_path=contract_bundle_path,
    )
    ambiguous_anarchy = _preview_pack_subset(
        schema_repo_root=schema_repo_root,
        workspace_root=workspace_root,
        pack_paths=pack_paths,
        selected_pack_ids=strict_pack_ids,
        mod_policy_id="mod_policy.anarchy",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
        instance_id="instance.strict.ambiguous.anarchy",
        resolution_policy_id=RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
        universe_contract_bundle_path=contract_bundle_path,
    )

    provider_declarations = list(strict_lock_payload.get("provides_declarations") or [])
    required_provides = list(strict_lock_payload.get("required_provides_ids") or [])
    strict_provider_result = resolve_providers(
        instance_id="instance.strict.ambiguous",
        required_provides_ids=required_provides,
        provider_declarations=provider_declarations,
        resolution_policy_id=RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
    )
    anarchy_provider_result = resolve_providers(
        instance_id="instance.strict.ambiguous",
        required_provides_ids=required_provides,
        provider_declarations=provider_declarations,
        resolution_policy_id=RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
        mod_policy_id="mod_policy.anarchy",
        overlay_conflict_policy_id="overlay.conflict.last_wins",
    )
    explicit_provider_result = resolve_providers(
        instance_id="instance.strict.ambiguous",
        required_provides_ids=required_provides,
        provider_declarations=provider_declarations,
        explicit_resolutions=[
            canonicalize_provides_resolution(
                {
                    "instance_id": "instance.strict.ambiguous",
                    "provides_id": PROVIDES_EARTH_DEM,
                    "chosen_pack_id": PACK_PROVIDER_FORK_ID,
                    "resolution_policy_id": RESOLUTION_POLICY_EXPLICIT_REQUIRED,
                    "extensions": {"source": "LIB-7"},
                }
            )
        ],
        resolution_policy_id=RESOLUTION_POLICY_EXPLICIT_REQUIRED,
        mod_policy_id="mod_policy.strict",
        overlay_conflict_policy_id="overlay.conflict.refuse",
    )

    save_same_install = evaluate_save_open(
        repo_root=workspace_root,
        save_manifest_path=save_mutable_path,
        instance_manifest=instance_linked_manifest,
        install_manifest=install_a_manifest,
        pack_lock_payload=mutable_lock_payload,
        run_mode="play",
        instance_allow_read_only_fallback=True,
    )
    save_different_install_refused = evaluate_save_open(
        repo_root=workspace_root,
        save_manifest_path=save_mutable_path,
        instance_manifest=instance_linked_manifest,
        install_manifest=install_b_manifest,
        pack_lock_payload=mutable_lock_payload,
        run_mode="play",
        instance_allow_read_only_fallback=False,
    )
    save_different_install_read_only = evaluate_save_open(
        repo_root=workspace_root,
        save_manifest_path=save_mutable_path,
        instance_manifest=instance_linked_manifest,
        install_manifest=install_b_manifest,
        pack_lock_payload=mutable_lock_payload,
        run_mode="play",
        instance_allow_read_only_fallback=True,
    )
    save_contract_mismatch = evaluate_save_open(
        repo_root=workspace_root,
        save_manifest_path=save_readonly_path,
        instance_manifest=instance_linked_manifest,
        install_manifest=install_a_manifest,
        pack_lock_payload=mutable_lock_payload,
        run_mode="play",
        instance_allow_read_only_fallback=True,
    )
    save_legacy_migrated = evaluate_save_open(
        repo_root=workspace_root,
        save_manifest_path=save_legacy_path,
        instance_manifest=instance_linked_manifest,
        install_manifest=install_a_manifest,
        pack_lock_payload=mutable_lock_payload,
        run_mode="play",
        instance_allow_read_only_fallback=True,
        allow_save_migration=True,
        migration_tick=123,
        migration_id="migration.lib7.legacy_to_v1",
    )

    write_json(os.path.join(decision_root, "provider_resolution.strict.json"), _sanitize_provider_result(strict_provider_result))
    write_json(os.path.join(decision_root, "provider_resolution.anarchy.json"), _sanitize_provider_result(anarchy_provider_result))
    write_json(os.path.join(decision_root, "provider_resolution.explicit.json"), _sanitize_provider_result(explicit_provider_result))
    write_json(os.path.join(decision_root, "pack_verify.official.json"), _sanitize_pack_verify(official_pack_verify))
    write_json(os.path.join(decision_root, "pack_verify.overlay_last_wins.json"), _sanitize_pack_verify(overlay_last_wins))
    write_json(os.path.join(decision_root, "pack_verify.overlay_strict.json"), _sanitize_pack_verify(overlay_strict))
    write_json(os.path.join(decision_root, "save_open.same_install.json"), _sanitize_save_open(save_same_install))
    write_json(os.path.join(decision_root, "save_open.contract_mismatch.json"), _sanitize_save_open(save_contract_mismatch))

    clone_result = clone_instance_local(
        repo_root=workspace_root,
        source_manifest_path=instance_portable_path,
        target_root=os.path.join(clone_root, "instance.clone.linked"),
        instance_id="instance.clone.linked",
        created_at=FIXED_TIMESTAMP,
        deterministic=True,
        duplicate_embedded_artifacts=False,
        store_root=paths["shared_store_root"],
    )

    linked_bundle_root = os.path.join(bundle_root, "instance.linked.bundle")
    portable_bundle_root = os.path.join(bundle_root, "instance.portable.bundle")
    save_bundle_root = os.path.join(bundle_root, "save.bundle")
    pack_bundle_root = os.path.join(bundle_root, "pack.bundle")

    export_linked = export_instance_bundle(
        repo_root=workspace_root,
        instance_manifest_path=instance_linked_path,
        out_path=linked_bundle_root,
        export_mode="linked",
    )
    export_portable = export_instance_bundle(
        repo_root=workspace_root,
        instance_manifest_path=instance_portable_path,
        out_path=portable_bundle_root,
        export_mode="portable",
    )
    export_save = export_save_bundle(
        repo_root=workspace_root,
        save_manifest_path=save_mutable_path,
        out_path=save_bundle_root,
        vendor_packs=True,
        store_root=paths["shared_store_root"],
    )
    export_pack = export_pack_bundle(
        repo_root=workspace_root,
        pack_root=pack_paths[PACK_PROVIDER_OFFICIAL_ID],
        out_path=pack_bundle_root,
    )
    verify_linked_rc, verify_linked = _run_python_tool("tools/lib/tool_verify_bundle.py", ["--bundle", linked_bundle_root])
    verify_portable_rc, verify_portable = _run_python_tool("tools/lib/tool_verify_bundle.py", ["--bundle", portable_bundle_root])
    verify_save_rc, verify_save = _run_python_tool("tools/lib/tool_verify_bundle.py", ["--bundle", save_bundle_root])
    verify_pack_rc, verify_pack = _run_python_tool("tools/lib/tool_verify_bundle.py", ["--bundle", pack_bundle_root])

    import_linked = import_instance_bundle(
        repo_root=schema_repo_root,
        bundle_path=linked_bundle_root,
        out_path=os.path.join(import_root, "instance.linked"),
        import_mode="linked",
        store_root=paths["shared_store_root"],
        instance_id="instance.imported.linked",
    )
    import_portable = import_instance_bundle(
        repo_root=schema_repo_root,
        bundle_path=portable_bundle_root,
        out_path=os.path.join(import_root, "instance.portable"),
        import_mode="portable",
        instance_id="instance.imported.portable",
    )
    import_save = import_save_bundle(
        repo_root=schema_repo_root,
        bundle_path=save_bundle_root,
        out_path=os.path.join(import_root, "save.alpha.mutable"),
        store_root=paths["shared_store_root"],
    )
    import_pack = import_pack_bundle(
        repo_root=schema_repo_root,
        bundle_path=pack_bundle_root,
        out_path=os.path.join(import_root, "pack.provider.official"),
        store_root=paths["shared_store_root"],
    )

    negotiation_out_path = os.path.join(decision_root, "negotiation.replay.json")
    replay_negotiation_rc, replay_negotiation = _run_python_tool(
        "tools/compat/tool_replay_negotiation.py",
        [
            "--repo-root",
            workspace_root,
            "--product-a",
            "client",
            "--product-b",
            "server",
            "--contract-bundle-hash",
            str(_as_map(scenario.get("extensions")).get("contract_bundle_hashes", {}).get("official", "")).strip(),
            "--output-path",
            _relative_path(workspace_root, negotiation_out_path),
        ],
    )
    save_replay_record = os.path.join(decision_root, "save_open.contract_mismatch.json")
    save_replay_out = os.path.join(decision_root, "save_open.replay.json")
    replay_save_rc, replay_save = _run_python_tool(
        "tools/lib/tool_replay_save_open.py",
        [
            "--repo-root",
            workspace_root,
            "--save-manifest",
            save_readonly_path,
            "--instance-manifest",
            instance_linked_path,
            "--install-manifest",
            install_a_path,
            "--run-mode",
            "play",
            "--allow-read-only-fallback",
            "--recorded-decision",
            save_replay_record,
            "--output-path",
            save_replay_out,
        ],
    )

    preflight_linked_rc, preflight_linked = perform_preflight(
        _preflight_namespace(
            save_id="save.alpha.mutable",
            compat_out=os.path.join(decision_root, "compat.linked.client.json"),
            run_mode="play",
        ),
        install_a_path,
        instance_linked_path,
        [],
    )
    preflight_readonly_rc, preflight_readonly = perform_preflight(
        _preflight_namespace(
            save_id="save.alpha.readonly",
            compat_out=os.path.join(decision_root, "compat.readonly.save.json"),
            run_mode="play",
        ),
        install_a_path,
        instance_linked_path,
        [],
    )
    preflight_strict_rc, preflight_strict = perform_preflight(
        _preflight_namespace(
            compat_out=os.path.join(decision_root, "compat.strict.ambiguous.json"),
            run_mode="play",
        ),
        install_b_path,
        instance_strict_path,
        [],
    )

    bundle_metrics = {
        "instance_linked": _logical_bundle_metrics(linked_bundle_root),
        "instance_portable": _logical_bundle_metrics(portable_bundle_root),
        "save": _logical_bundle_metrics(save_bundle_root),
        "pack": _logical_bundle_metrics(pack_bundle_root),
    }
    bundle_hashes = {
        "instance_linked": str(export_linked.get("bundle_hash", "")).strip(),
        "instance_portable": str(export_portable.get("bundle_hash", "")).strip(),
        "save": str(export_save.get("bundle_hash", "")).strip(),
        "pack": str(export_pack.get("bundle_hash", "")).strip(),
    }
    bundle_verifications = {
        "instance_linked": {"rc": verify_linked_rc, "result": str(verify_linked.get("result", "")).strip(), "bundle_hash": str(verify_linked.get("bundle_hash", "")).strip()},
        "instance_portable": {"rc": verify_portable_rc, "result": str(verify_portable.get("result", "")).strip(), "bundle_hash": str(verify_portable.get("bundle_hash", "")).strip()},
        "save": {"rc": verify_save_rc, "result": str(verify_save.get("result", "")).strip(), "bundle_hash": str(verify_save.get("bundle_hash", "")).strip()},
        "pack": {"rc": verify_pack_rc, "result": str(verify_pack.get("result", "")).strip(), "bundle_hash": str(verify_pack.get("bundle_hash", "")).strip()},
    }
    provider_outcomes = {
        "strict": _sanitize_provider_result(strict_provider_result),
        "anarchy": _sanitize_provider_result(anarchy_provider_result),
        "explicit": _sanitize_provider_result(explicit_provider_result),
    }
    pack_verify_outcomes = {
        "official": _sanitize_pack_verify(official_pack_verify),
        "overlay_last_wins": _sanitize_pack_verify(overlay_last_wins),
        "overlay_strict": _sanitize_pack_verify(overlay_strict),
        "ambiguous_strict": _sanitize_pack_verify(ambiguous_strict),
        "ambiguous_anarchy": _sanitize_pack_verify(ambiguous_anarchy),
    }
    save_outcomes = {
        "same_install": _sanitize_save_open(save_same_install),
        "different_install_refused": _sanitize_save_open(save_different_install_refused),
        "different_install_read_only": _sanitize_save_open(save_different_install_read_only),
        "contract_mismatch_read_only": _sanitize_save_open(save_contract_mismatch),
        "legacy_migrated": _sanitize_save_open(save_legacy_migrated),
    }
    launcher_outcomes = {
        "linked_client": {
            "rc": preflight_linked_rc,
            "mode": str(_as_map(_as_map(preflight_linked).get("compat_report")).get("compatibility_mode", "")).strip(),
            "degrade_logged": bool(_as_map(_as_map(_as_map(preflight_linked).get("compat_report")).get("extensions")).get("degrade_logged", False)),
            "provider_selection_logged": bool(
                _as_map(_as_map(_as_map(preflight_linked).get("compat_report")).get("extensions")).get("provider_selection_logged", False)
            ),
        },
        "read_only_save": {
            "rc": preflight_readonly_rc,
            "mode": str(_as_map(_as_map(preflight_readonly).get("compat_report")).get("compatibility_mode", "")).strip(),
            "degrade_logged": bool(_as_map(_as_map(_as_map(preflight_readonly).get("compat_report")).get("extensions")).get("degrade_logged", False)),
            "degrade_reasons": list(_as_map(_as_map(_as_map(preflight_readonly).get("compat_report")).get("extensions")).get("degrade_reasons") or []),
        },
        "strict_ambiguous": {
            "rc": preflight_strict_rc,
            "refusal_codes": list(_as_map(_as_map(preflight_strict).get("compat_report")).get("refusal_codes") or []),
            "provider_selection_logged": bool(
                _as_map(_as_map(_as_map(preflight_strict).get("compat_report")).get("extensions")).get("provider_selection_logged", False)
            ),
        },
    }
    decision_logs = {
        "provider_resolution_strict": canonical_sha256(_read_json(os.path.join(decision_root, "provider_resolution.strict.json"))),
        "pack_verify_official": canonical_sha256(_read_json(os.path.join(decision_root, "pack_verify.official.json"))),
        "save_open_contract_mismatch": canonical_sha256(_read_json(os.path.join(decision_root, "save_open.contract_mismatch.json"))),
    }
    refusal_codes: List[str] = []
    for bucket in (provider_outcomes, pack_verify_outcomes, save_outcomes, launcher_outcomes):
        for row in _as_map(bucket).values():
            if not isinstance(row, Mapping):
                continue
            token = str(_as_map(row).get("refusal_code", "")).strip()
            if token:
                refusal_codes.append(token)
            refusal_codes.extend(str(item).strip() for item in list(_as_map(row).get("refusal_codes") or []) if str(item).strip())
    refusal_summary = sorted({token for token in refusal_codes if token})
    refusal_counts = [{"refusal_code": token, "count": refusal_codes.count(token)} for token in refusal_summary]
    ambiguity_count = len(list(_as_map(provider_outcomes.get("strict")).get("ambiguous_provides_ids") or []))
    projection = {
        "bundle_hashes": bundle_hashes,
        "bundle_verifications": bundle_verifications,
        "provider_outcomes": provider_outcomes,
        "pack_verify_outcomes": pack_verify_outcomes,
        "save_outcomes": save_outcomes,
        "launcher_outcomes": launcher_outcomes,
        "decision_logs": decision_logs,
        "clone_mode": str(_as_map(clone_result).get("clone_mode", "")).strip(),
        "import_results": {
            "instance_linked": str(_as_map(import_linked).get("result", "")).strip(),
            "instance_portable": str(_as_map(import_portable).get("result", "")).strip(),
            "save": str(_as_map(import_save).get("result", "")).strip(),
            "pack": str(_as_map(import_pack).get("result", "")).strip(),
        },
        "replay": {
            "bundle_verify_rcs": {
                "instance_linked": verify_linked_rc,
                "instance_portable": verify_portable_rc,
                "save": verify_save_rc,
                "pack": verify_pack_rc,
            },
            "negotiation_rc": replay_negotiation_rc,
            "negotiation_fingerprint": str(_as_map(replay_negotiation).get("deterministic_fingerprint", "")).strip(),
            "save_open_rc": replay_save_rc,
            "save_open_replay_hash": str(_as_map(replay_save).get("replay_hash", "")).strip(),
        },
        "refusal_counts": refusal_counts,
        "ambiguity_count": ambiguity_count,
    }
    return {
        "round_id": str(round_id).strip(),
        "result": "complete",
        "projection_hash": _projection_hash(projection),
        "projection": projection,
        "bundle_metrics": bundle_metrics,
        "decision_logs": decision_logs,
        "replay_reports": {
            "negotiation": {
                "rc": replay_negotiation_rc,
                "result": str(_as_map(replay_negotiation).get("result", "")).strip(),
                "deterministic_fingerprint": str(_as_map(replay_negotiation).get("deterministic_fingerprint", "")).strip(),
            },
            "save_open": {
                "rc": replay_save_rc,
                "result": str(_as_map(replay_save).get("result", "")).strip(),
                "replay_hash": str(_as_map(replay_save).get("replay_hash", "")).strip(),
            },
        },
    }


def build_lib_regression_baseline(report: Mapping[str, object]) -> dict:
    rounds = list(_as_map(report).get("rounds") or [])
    first_projection = _as_map(_as_map(rounds[0]).get("projection")) if rounds else {}
    baseline = {
        "baseline_id": "lib.full.baseline.v1",
        "schema_version": "1.0.0",
        "description": "Deterministic LIB-7 regression lock for installs, instances, saves, providers, export/import, and read-only fallback.",
        "scenario_seed": int(_as_map(report).get("seed", DEFAULT_LIB7_SEED) or DEFAULT_LIB7_SEED),
        "fixed_seed_scenario": {
            "scenario_id": str(_as_map(report).get("scenario_id", "")).strip(),
            "scenario_fingerprint": str(_as_map(report).get("scenario_fingerprint", "")).strip(),
            "stress_report_fingerprint": str(_as_map(report).get("deterministic_fingerprint", "")).strip(),
        },
        "bundle_hashes": dict(_as_map(first_projection).get("bundle_hashes") or {}),
        "provider_resolution_outcomes": dict(_as_map(first_projection).get("provider_outcomes") or {}),
        "strict_refusal_outcomes": {
            "provider_strict": _as_map(_as_map(first_projection).get("provider_outcomes", {}).get("strict")),
            "overlay_strict": _as_map(_as_map(first_projection).get("pack_verify_outcomes", {}).get("overlay_strict")),
            "ambiguous_strict": _as_map(_as_map(first_projection).get("pack_verify_outcomes", {}).get("ambiguous_strict")),
            "different_install_refused": _as_map(_as_map(first_projection).get("save_outcomes", {}).get("different_install_refused")),
        },
        "read_only_fallback_outcomes": {
            "different_install_read_only": _as_map(_as_map(first_projection).get("save_outcomes", {}).get("different_install_read_only")),
            "contract_mismatch_read_only": _as_map(_as_map(first_projection).get("save_outcomes", {}).get("contract_mismatch_read_only")),
            "launcher_read_only_save": _as_map(_as_map(first_projection).get("launcher_outcomes", {}).get("read_only_save")),
        },
        "decision_log_fingerprints": dict(_as_map(first_projection).get("decision_logs") or {}),
        "update_policy": {
            "required_commit_tag": "LIB-REGRESSION-UPDATE",
            "notes": "Baseline updates require rerunning the LIB-7 stress generator, harness, bundle verification, negotiation replay, and save-open replay under explicit LIB-REGRESSION-UPDATE review.",
        },
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = canonical_sha256(dict(baseline, deterministic_fingerprint=""))
    return baseline


def run_lib_stress(
    *,
    repo_root: str,
    out_root: str,
    seed: int = DEFAULT_LIB7_SEED,
    slash_mode: str = "forward",
    baseline_out: str = "",
) -> dict:
    run_root = os.path.abspath(str(out_root or "").strip())
    if os.path.isdir(run_root):
        _safe_rmtree(run_root)
    _ensure_dir(run_root)

    round_a_root = os.path.join(run_root, "round_a")
    round_b_root = os.path.join(run_root, "round_b")
    scenario_a = generate_lib_stress_scenario(repo_root=repo_root, out_root=round_a_root, seed=seed, slash_mode=slash_mode)
    scenario_b = generate_lib_stress_scenario(repo_root=repo_root, out_root=round_b_root, seed=seed, slash_mode=slash_mode)
    round_a = _round_summary(workspace_root=round_a_root, round_id="round_a", scenario=scenario_a, schema_repo_root=repo_root)
    round_b = _round_summary(workspace_root=round_b_root, round_id="round_b", scenario=scenario_b, schema_repo_root=repo_root)

    stable = str(round_a.get("projection_hash", "")).strip() == str(round_b.get("projection_hash", "")).strip()
    first_projection = dict(_as_map(round_a).get("projection") or {})
    report = {
        "result": "complete",
        "scenario_id": str(_as_map(scenario_a).get("scenario_id", "")).strip(),
        "seed": int(seed),
        "slash_mode": str(slash_mode or "forward").strip().lower() or "forward",
        "scenario_fingerprint": str(_as_map(scenario_a).get("deterministic_fingerprint", "")).strip(),
        "stable_across_repeated_runs": bool(stable),
        "projection_hashes": [
            str(_as_map(round_a).get("projection_hash", "")).strip(),
            str(_as_map(round_b).get("projection_hash", "")).strip(),
        ],
        "rounds": [round_a, round_b],
        "bundle_hashes": dict(_as_map(first_projection).get("bundle_hashes") or {}),
        "bundle_metrics": dict(_as_map(round_a).get("bundle_metrics") or {}),
        "provider_resolution_outcomes": dict(_as_map(first_projection).get("provider_outcomes") or {}),
        "pack_verification_outcomes": dict(_as_map(first_projection).get("pack_verify_outcomes") or {}),
        "save_outcomes": dict(_as_map(first_projection).get("save_outcomes") or {}),
        "launcher_outcomes": dict(_as_map(first_projection).get("launcher_outcomes") or {}),
        "decision_log_fingerprints": dict(_as_map(first_projection).get("decision_logs") or {}),
        "refusal_counts": list(_as_map(first_projection).get("refusal_counts") or []),
        "ambiguity_count": int(_as_map(first_projection).get("ambiguity_count", 0) or 0),
        "replay_reports": dict(_as_map(round_a).get("replay_reports") or {}),
        "assertions": {
            "stress_scenario_deterministic": bool(
                str(_as_map(scenario_a).get("deterministic_fingerprint", "")).strip()
                == str(_as_map(scenario_b).get("deterministic_fingerprint", "")).strip()
            ),
            "stable_across_repeated_runs": bool(stable),
            "bundle_hash_stable": bool(
                dict(_as_map(round_a).get("projection", {})).get("bundle_hashes")
                == dict(_as_map(round_b).get("projection", {})).get("bundle_hashes")
            ),
            "provider_resolution_recorded": bool(_as_map(first_projection).get("provider_outcomes", {}).get("anarchy", {}).get("selection_logged", False)),
            "read_only_fallback_logged": bool(
                _as_map(_as_map(first_projection).get("launcher_outcomes", {}).get("read_only_save")).get("degrade_logged", False)
            ),
        },
        "extensions": {
            "source": "LIB-7",
            "workspace_roots": [_relative_path(run_root, round_a_root), _relative_path(run_root, round_b_root)],
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))

    if str(baseline_out or "").strip():
        write_json(os.path.abspath(str(baseline_out)), build_lib_regression_baseline(report))
    return report


__all__ = [
    "DEFAULT_BASELINE_REL",
    "DEFAULT_LIB7_SEED",
    "DEFAULT_REPORT_REL",
    "DEFAULT_SCENARIO_REL",
    "DEFAULT_WORKSPACE_REL",
    "build_lib_regression_baseline",
    "generate_lib_stress_scenario",
    "run_lib_stress",
    "write_json",
]
