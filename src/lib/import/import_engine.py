"""Deterministic LIB-6 import engines."""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import Dict, List, Mapping, Sequence, Tuple

from src.appshell.paths import (
    VROOT_INSTANCES,
    VROOT_SAVES,
    vpath_init,
    vpath_resolve,
)
from src.lib.bundle import BUNDLE_CONTENT_DIR, load_json as load_bundle_json, verify_bundle_directory, write_json
from src.lib.export import (
    BUNDLE_KIND_INSTANCE_LINKED,
    BUNDLE_KIND_INSTANCE_PORTABLE,
    BUNDLE_KIND_PACK,
    BUNDLE_KIND_SAVE,
)
from src.modding import DEFAULT_MOD_POLICY_ID
from src.lib.instance import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
    validate_instance_manifest,
)
from src.lib.save import (
    SAVE_MANIFEST_NAME,
    deterministic_fingerprint as save_deterministic_fingerprint,
    normalize_save_manifest,
    validate_save_manifest,
)
from src.packs.compat import verify_pack_set
from tools.lib.content_store import (
    ARTIFACT_MANIFEST,
    JSON_PAYLOAD,
    TREE_PAYLOAD_DIR,
    build_install_ref,
    build_store_locator,
    initialize_store_root,
    load_json,
    store_add_artifact,
    store_add_tree_artifact,
    store_artifact_root,
)


PACK_STORE_CATEGORY = "packs"
LOCK_STORE_CATEGORY = "locks"
PROFILE_STORE_CATEGORY = "profiles"


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _norm(path: object) -> str:
    text = str(path or "").replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text


def _ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def _copy_file(src: str, dest: str) -> None:
    _ensure_dir(os.path.dirname(os.path.abspath(dest)))
    shutil.copyfile(src, dest)


def _copy_tree(src: str, dest: str) -> None:
    for root, dirnames, filenames in os.walk(src):
        dirnames.sort()
        filenames.sort()
        rel_root = os.path.relpath(root, src)
        target_root = dest if rel_root == "." else os.path.join(dest, rel_root)
        _ensure_dir(target_root)
        for filename in filenames:
            _copy_file(os.path.join(root, filename), os.path.join(target_root, filename))


def _bundle_content_path(bundle_root: str, rel_path: str) -> str:
    return os.path.join(bundle_root, BUNDLE_CONTENT_DIR, _norm(rel_path).replace("/", os.sep))


def _bundled_store_artifacts(bundle_root: str) -> List[dict]:
    store_root = _bundle_content_path(bundle_root, "store")
    if not os.path.isdir(store_root):
        return []
    rows: List[dict] = []
    for category in sorted(os.listdir(store_root)):
        category_root = os.path.join(store_root, category)
        if not os.path.isdir(category_root):
            continue
        for artifact_hash in sorted(os.listdir(category_root)):
            artifact_root = os.path.join(category_root, artifact_hash)
            if not os.path.isdir(artifact_root):
                continue
            payload_json = os.path.join(artifact_root, JSON_PAYLOAD)
            payload_tree = os.path.join(artifact_root, TREE_PAYLOAD_DIR)
            artifact_type = "json" if os.path.isfile(payload_json) else "tree" if os.path.isdir(payload_tree) else ""
            rows.append(
                {
                    "category": str(category),
                    "artifact_hash": str(artifact_hash),
                    "artifact_root": artifact_root,
                    "artifact_type": artifact_type,
                }
            )
    return rows


def _bundled_artifact_root(bundle_root: str, category: str, artifact_hash: str) -> str:
    candidate = _bundle_content_path(bundle_root, "store/{}/{}".format(category, artifact_hash))
    return candidate if os.path.isdir(candidate) else ""


def _load_bundled_json_artifact(bundle_root: str, category: str, artifact_hash: str) -> dict:
    artifact_root = _bundled_artifact_root(bundle_root, category, artifact_hash)
    payload_path = os.path.join(artifact_root, JSON_PAYLOAD)
    if not artifact_root or not os.path.isfile(payload_path):
        return {}
    return load_json(payload_path)


def _insert_bundle_store_artifacts(bundle_root: str, target_store_root: str) -> dict:
    initialize_store_root(target_store_root)
    inserted: List[dict] = []
    for row in _bundled_store_artifacts(bundle_root):
        category = str(row.get("category", "")).strip()
        artifact_hash = str(row.get("artifact_hash", "")).strip()
        artifact_root = str(row.get("artifact_root", "")).strip()
        manifest_path = os.path.join(artifact_root, ARTIFACT_MANIFEST)
        if os.path.isfile(manifest_path):
            manifest = load_json(manifest_path)
            if str(manifest.get("artifact_hash", "")).strip() != artifact_hash:
                return {
                    "result": "refused",
                    "refusal_code": "refusal.bundle.artifact_hash_mismatch",
                    "details": {"category": category, "artifact_hash": artifact_hash},
                }
        if str(row.get("artifact_type", "")).strip() == "json":
            payload = load_json(os.path.join(artifact_root, JSON_PAYLOAD))
            add_result = store_add_artifact(target_store_root, category, payload, expected_hash=artifact_hash)
        elif str(row.get("artifact_type", "")).strip() == "tree":
            add_result = store_add_tree_artifact(target_store_root, category, os.path.join(artifact_root, TREE_PAYLOAD_DIR))
        else:
            return {
                "result": "refused",
                "refusal_code": "refusal.bundle.artifact_missing_payload",
                "details": {"category": category, "artifact_hash": artifact_hash},
            }
        if str(add_result.get("artifact_hash", "")).strip() != artifact_hash:
            return {
                "result": "refused",
                "refusal_code": "refusal.bundle.artifact_hash_mismatch",
                "details": {"category": category, "artifact_hash": artifact_hash},
            }
        inserted.append({"category": category, "artifact_hash": artifact_hash})
    return {"result": "complete", "inserted_artifacts": inserted}


def _preview_pack_set(
    *,
    repo_root: str,
    bundle_root: str,
    ordered_pack_ids: Sequence[str],
    pack_hashes: Mapping[str, object],
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    instance_id: str,
    explicit_provides_resolutions: Sequence[Mapping[str, object]] | None = None,
    resolution_policy_id: str = "",
    contract_bundle_source_path: str = "",
) -> dict:
    if not list(ordered_pack_ids or []):
        return {"result": "complete", "report": {}, "pack_lock": {}, "errors": [], "warnings": []}

    with tempfile.TemporaryDirectory(prefix="lib6_pack_preview_") as tmp_root:
        packs_root = os.path.join(tmp_root, "packs")
        _ensure_dir(packs_root)
        data_root = os.path.join(repo_root, "data")
        if os.path.isdir(data_root):
            _copy_tree(data_root, os.path.join(tmp_root, "data"))
        for pack_id in list(ordered_pack_ids or []):
            artifact_hash = str(_as_map(pack_hashes).get(pack_id, "")).strip()
            artifact_root = _bundled_artifact_root(bundle_root, PACK_STORE_CATEGORY, artifact_hash)
            payload_root = os.path.join(artifact_root, TREE_PAYLOAD_DIR)
            if not artifact_root or not os.path.isdir(payload_root):
                return {
                    "result": "refused",
                    "refusal_code": "refusal.bundle.pack_missing",
                    "errors": [{"code": "bundle_pack_missing", "path": "$.store.packs", "message": "bundled pack payload is missing"}],
                    "warnings": [],
                    "report": {},
                    "pack_lock": {},
                }
            category = "source"
            _copy_tree(payload_root, os.path.join(packs_root, category, str(pack_id)))

        contract_bundle_rel = ""
        if str(contract_bundle_source_path or "").strip() and os.path.isfile(contract_bundle_source_path):
            staged_contract = os.path.join(tmp_root, "contract_bundle.json")
            _copy_file(contract_bundle_source_path, staged_contract)
            contract_bundle_rel = os.path.relpath(staged_contract, tmp_root).replace("\\", "/")

        return verify_pack_set(
            repo_root=tmp_root,
            bundle_id="",
            mod_policy_id=str(mod_policy_id or "").strip() or "mod.policy.default",
            overlay_conflict_policy_id=str(overlay_conflict_policy_id or "").strip(),
            instance_id=str(instance_id or "").strip() or "bundle.import",
            explicit_provides_resolutions=list(explicit_provides_resolutions or []),
            resolution_policy_id=str(resolution_policy_id or "").strip(),
            schema_repo_root=repo_root,
            packs_root_rel="packs",
            universe_contract_bundle_path=contract_bundle_rel,
        )


def _write_install_manifest_if_present(bundle_root: str, target_root: str) -> Tuple[str, dict]:
    source_path = _bundle_content_path(bundle_root, "install/install.manifest.json")
    if not os.path.isfile(source_path):
        return "", {}
    target_path = os.path.join(target_root, "install.manifest.json")
    payload = load_bundle_json(source_path)
    _copy_file(source_path, target_path)
    return target_path, payload


def _default_instance_target_root(repo_root: str, store_root: str, instance_id: str) -> str:
    context = vpath_init(
        {
            "repo_root": repo_root,
            "product_id": "tool.attach_console_stub",
            "raw_args": ["--store-root", str(store_root)] if str(store_root or "").strip() else [],
        }
    )
    if str(context.get("result", "")).strip() == "complete":
        return vpath_resolve(VROOT_INSTANCES, str(instance_id), context)
    base_root = os.path.abspath(store_root) if str(store_root or "").strip() else os.path.abspath(repo_root)
    return os.path.join(base_root, "instances", str(instance_id))


def _default_save_target_root(repo_root: str, store_root: str, save_id: str) -> str:
    context = vpath_init(
        {
            "repo_root": repo_root,
            "product_id": "tool.attach_console_stub",
            "raw_args": ["--store-root", str(store_root)] if str(store_root or "").strip() else [],
        }
    )
    if str(context.get("result", "")).strip() == "complete":
        return vpath_resolve(VROOT_SAVES, str(save_id), context)
    base_root = os.path.abspath(store_root) if str(store_root or "").strip() else os.path.abspath(repo_root)
    return os.path.join(base_root, "saves", str(save_id))


def _update_instance_id(payload: Mapping[str, object], instance_id: str) -> dict:
    manifest = dict(payload or {})
    token = str(instance_id or "").strip()
    if not token:
        return manifest
    manifest["instance_id"] = token
    updated = []
    for row in list(manifest.get("provides_resolutions") or []):
        item = dict(row or {})
        item["instance_id"] = token
        updated.append(item)
    manifest["provides_resolutions"] = updated
    return manifest


def import_instance_bundle(
    *,
    repo_root: str,
    bundle_path: str,
    out_path: str = "",
    import_mode: str = "",
    store_root: str = "",
    instance_id: str = "",
) -> dict:
    verification = verify_bundle_directory(bundle_path)
    if verification.get("result") != "complete":
        return verification
    bundle_manifest = dict(verification.get("bundle_manifest") or {})
    bundle_kind = str(bundle_manifest.get("bundle_kind", "")).strip()
    if bundle_kind not in {BUNDLE_KIND_INSTANCE_LINKED, BUNDLE_KIND_INSTANCE_PORTABLE}:
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.kind_mismatch",
            "details": {"bundle_kind": bundle_kind},
        }

    source_manifest_path = _bundle_content_path(bundle_path, "instance/instance.manifest.json")
    if not os.path.isfile(source_manifest_path):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.instance_missing_manifest",
        }
    validation = validate_instance_manifest(repo_root=repo_root, instance_manifest_path=source_manifest_path)
    if validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(validation.get("refusal_code", "")).strip() or "refusal.bundle.instance_invalid",
            "instance_validation": validation,
        }

    manifest = dict(validation.get("instance_manifest") or {})
    if instance_id:
        manifest = _update_instance_id(manifest, instance_id)
    requested_mode = str(import_mode or manifest.get("mode") or ("portable" if bundle_kind == BUNDLE_KIND_INSTANCE_PORTABLE else "linked")).strip().lower()
    if requested_mode not in {"linked", "portable"}:
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.invalid_mode",
            "details": {"import_mode": requested_mode},
        }

    target_root = os.path.abspath(str(out_path or _default_instance_target_root(repo_root, store_root, str(manifest.get("instance_id", "")).strip())))
    if os.path.exists(target_root):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.destination_exists",
            "details": {"target_root": target_root.replace("\\", "/")},
        }

    pack_lock_payload = _load_bundled_json_artifact(bundle_path, LOCK_STORE_CATEGORY, str(manifest.get("pack_lock_hash", "")).strip())
    preview = _preview_pack_set(
        repo_root=repo_root,
        bundle_root=bundle_path,
        ordered_pack_ids=list(pack_lock_payload.get("ordered_pack_ids") or []),
        pack_hashes=_as_map(pack_lock_payload.get("pack_hashes")),
        mod_policy_id=str(manifest.get("mod_policy_id", "")).strip(),
        overlay_conflict_policy_id=str(manifest.get("overlay_conflict_policy_id", "")).strip(),
        instance_id=str(manifest.get("instance_id", "")).strip(),
        explicit_provides_resolutions=list(manifest.get("provides_resolutions") or []),
        resolution_policy_id=str(manifest.get("resolution_policy_id", "")).strip(),
    )
    if preview.get("result") != "complete" or list(preview.get("errors") or []) or not bool(_as_map(preview.get("report")).get("valid", True)):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.pack_compat_invalid",
            "compat_preview": preview,
        }

    if requested_mode == "linked":
        if not str(store_root or "").strip():
            return {
                "result": "refused",
                "refusal_code": "refusal.bundle.store_root_required",
            }
        insert_result = _insert_bundle_store_artifacts(bundle_path, store_root)
        if insert_result.get("result") != "complete":
            return insert_result

    try:
        _ensure_dir(target_root)
        install_manifest_path, install_manifest = _write_install_manifest_if_present(bundle_path, target_root)
        if requested_mode == "portable":
            source_instance_root = _bundle_content_path(bundle_path, "instance")
            if os.path.isdir(source_instance_root):
                for rel_path in os.listdir(source_instance_root):
                    if rel_path == "instance.manifest.json":
                        continue
                    source_path = os.path.join(source_instance_root, rel_path)
                    dest_path = os.path.join(target_root, rel_path)
                    if os.path.isdir(source_path):
                        _copy_tree(source_path, dest_path)
                    elif os.path.isfile(source_path):
                        _copy_file(source_path, dest_path)
            for row in _bundled_store_artifacts(bundle_path):
                artifact_root = str(row.get("artifact_root", "")).strip()
                dest_root = os.path.join(
                    target_root,
                    "embedded_artifacts",
                    str(row.get("category", "")).strip(),
                    str(row.get("artifact_hash", "")).strip(),
                )
                _copy_tree(artifact_root, dest_root)
            manifest["mode"] = "portable"
            manifest["store_root"] = {}
        else:
            initialize_store_root(store_root)
            manifest["mode"] = "linked"
            manifest["embedded_artifacts"] = []
            manifest["embedded_builds"] = {}
            manifest["capability_lockfile"] = ""
            manifest["store_root"] = build_store_locator(target_root, store_root, initialize_store_root(store_root))

        if install_manifest_path and install_manifest:
            manifest["install_ref"] = build_install_ref(target_root, install_manifest_path, install_manifest)
            manifest["install_id"] = install_manifest.get("install_id") or manifest.get("install_id")
        else:
            install_ref = _as_map(manifest.get("install_ref"))
            manifest["install_ref"] = {
                "install_id": str(install_ref.get("install_id", "")).strip() or str(manifest.get("install_id", "")).strip(),
                "manifest_ref": "",
                "root_path": "",
            }

        manifest = normalize_instance_manifest(manifest)
        manifest["deterministic_fingerprint"] = instance_deterministic_fingerprint(manifest)
        target_manifest_path = os.path.join(target_root, "instance.manifest.json")
        target_validation = validate_instance_manifest(repo_root=repo_root, instance_manifest_path=target_manifest_path, manifest_payload=manifest)
        if target_validation.get("result") != "complete":
            raise ValueError(str(target_validation.get("refusal_code", "")).strip() or "instance validation failed")
        write_json(target_manifest_path, dict(target_validation.get("instance_manifest") or manifest))
    except Exception as exc:
        shutil.rmtree(target_root, ignore_errors=True)
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.instance_import_failed",
            "message": str(exc),
        }

    return {
        "result": "complete",
        "bundle_manifest": bundle_manifest,
        "compat_preview": preview,
        "import_root": target_root.replace("\\", "/"),
        "instance_manifest_path": os.path.join(target_root, "instance.manifest.json").replace("\\", "/"),
    }


def import_save_bundle(
    *,
    repo_root: str,
    bundle_path: str,
    out_path: str = "",
    store_root: str = "",
) -> dict:
    verification = verify_bundle_directory(bundle_path)
    if verification.get("result") != "complete":
        return verification
    bundle_manifest = dict(verification.get("bundle_manifest") or {})
    if str(bundle_manifest.get("bundle_kind", "")).strip() != BUNDLE_KIND_SAVE:
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.kind_mismatch",
            "details": {"bundle_kind": bundle_manifest.get("bundle_kind", "")},
        }

    source_manifest_path = _bundle_content_path(bundle_path, "save/{}".format(SAVE_MANIFEST_NAME))
    validation = validate_save_manifest(repo_root=repo_root, save_manifest_path=source_manifest_path)
    if validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(validation.get("refusal_code", "")).strip() or "refusal.bundle.save_invalid",
            "save_validation": validation,
        }

    manifest = dict(validation.get("save_manifest") or {})
    target_root = os.path.abspath(str(out_path or _default_save_target_root(repo_root, store_root, str(manifest.get("save_id", "")).strip())))
    if os.path.exists(target_root):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.destination_exists",
            "details": {"target_root": target_root.replace("\\", "/")},
        }

    contract_bundle_source = ""
    contract_bundle_ref = str(manifest.get("contract_bundle_ref", "")).strip()
    if contract_bundle_ref:
        contract_bundle_source = _bundle_content_path(bundle_path, "save/{}".format(contract_bundle_ref))
    pack_lock_payload = _load_bundled_json_artifact(bundle_path, LOCK_STORE_CATEGORY, str(manifest.get("pack_lock_hash", "")).strip())
    preview = _preview_pack_set(
        repo_root=repo_root,
        bundle_root=bundle_path,
        ordered_pack_ids=list(pack_lock_payload.get("ordered_pack_ids") or []),
        pack_hashes=_as_map(pack_lock_payload.get("pack_hashes")),
        mod_policy_id=str(manifest.get("mod_policy_id", "")).strip(),
        overlay_conflict_policy_id="",
        instance_id=str(manifest.get("save_id", "")).strip(),
        explicit_provides_resolutions=list(pack_lock_payload.get("provides_resolutions") or []),
        resolution_policy_id=str(pack_lock_payload.get("resolution_policy_id", "")).strip(),
        contract_bundle_source_path=contract_bundle_source,
    )
    preview_errors = list(preview.get("errors") or [])
    if preview.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.pack_compat_invalid",
            "compat_preview": preview,
        }
    if preview_errors and list(pack_lock_payload.get("ordered_pack_ids") or []):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.pack_compat_invalid",
            "compat_preview": preview,
        }

    if str(store_root or "").strip():
        insert_result = _insert_bundle_store_artifacts(bundle_path, store_root)
        if insert_result.get("result") != "complete":
            return insert_result

    try:
        _ensure_dir(target_root)
        source_save_root = _bundle_content_path(bundle_path, "save")
        _copy_tree(source_save_root, target_root)
        imported_manifest_path = os.path.join(target_root, SAVE_MANIFEST_NAME)
        imported_manifest = normalize_save_manifest(load_json(imported_manifest_path))
        imported_manifest["deterministic_fingerprint"] = save_deterministic_fingerprint(imported_manifest)
        imported_validation = validate_save_manifest(repo_root=repo_root, save_manifest_path=imported_manifest_path, manifest_payload=imported_manifest)
        if imported_validation.get("result") != "complete":
            raise ValueError(str(imported_validation.get("refusal_code", "")).strip() or "save validation failed")
        write_json(imported_manifest_path, dict(imported_validation.get("save_manifest") or imported_manifest))
    except Exception as exc:
        shutil.rmtree(target_root, ignore_errors=True)
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.save_import_failed",
            "message": str(exc),
        }

    return {
        "result": "complete",
        "bundle_manifest": bundle_manifest,
        "compat_preview": preview,
        "import_root": target_root.replace("\\", "/"),
        "save_manifest_path": os.path.join(target_root, SAVE_MANIFEST_NAME).replace("\\", "/"),
    }


def import_pack_bundle(
    *,
    repo_root: str,
    bundle_path: str,
    out_path: str = "",
    store_root: str = "",
) -> dict:
    verification = verify_bundle_directory(bundle_path)
    if verification.get("result") != "complete":
        return verification
    bundle_manifest = dict(verification.get("bundle_manifest") or {})
    if str(bundle_manifest.get("bundle_kind", "")).strip() != BUNDLE_KIND_PACK:
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.kind_mismatch",
            "details": {"bundle_kind": bundle_manifest.get("bundle_kind", "")},
        }

    pack_artifacts = [row for row in _bundled_store_artifacts(bundle_path) if str(row.get("category", "")).strip() == PACK_STORE_CATEGORY]
    if not pack_artifacts:
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.pack_missing",
        }

    pack_hashes = {}
    ordered_pack_ids: List[str] = []
    for row in pack_artifacts:
        artifact_root = str(row.get("artifact_root", "")).strip()
        payload_root = os.path.join(artifact_root, TREE_PAYLOAD_DIR)
        pack_id = ""
        pack_json_path = os.path.join(payload_root, "pack.json")
        if os.path.isfile(pack_json_path):
            pack_json = load_json(pack_json_path)
            pack_id = str(pack_json.get("pack_id", "")).strip()
        if not pack_id:
            pack_id = str(row.get("artifact_hash", "")).strip()
        ordered_pack_ids.append(pack_id)
        pack_hashes[pack_id] = str(row.get("artifact_hash", "")).strip()

    preview = _preview_pack_set(
        repo_root=repo_root,
        bundle_root=bundle_path,
        ordered_pack_ids=sorted(ordered_pack_ids),
        pack_hashes=pack_hashes,
        mod_policy_id=DEFAULT_MOD_POLICY_ID,
        overlay_conflict_policy_id="",
        instance_id="pack.import",
    )
    if preview.get("result") != "complete" or list(preview.get("errors") or []) or not bool(_as_map(preview.get("report")).get("valid", True)):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.pack_compat_invalid",
            "compat_preview": preview,
        }

    if str(store_root or "").strip():
        insert_result = _insert_bundle_store_artifacts(bundle_path, store_root)
        if insert_result.get("result") != "complete":
            return insert_result

    materialized_root = ""
    if str(out_path or "").strip():
        if os.path.exists(out_path):
            return {
                "result": "refused",
                "refusal_code": "refusal.bundle.destination_exists",
                "details": {"target_root": os.path.abspath(out_path).replace("\\", "/")},
            }
        artifact_root = str(pack_artifacts[0].get("artifact_root", "")).strip()
        _copy_tree(os.path.join(artifact_root, TREE_PAYLOAD_DIR), out_path)
        materialized_root = os.path.abspath(out_path).replace("\\", "/")

    return {
        "result": "complete",
        "bundle_manifest": bundle_manifest,
        "compat_preview": preview,
        "pack_ids": sorted(ordered_pack_ids),
        "materialized_root": materialized_root,
    }


__all__ = [
    "import_instance_bundle",
    "import_pack_bundle",
    "import_save_bundle",
]
