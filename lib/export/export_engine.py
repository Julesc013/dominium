"""Deterministic LIB-6 export engines."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from appshell.paths import VROOT_STORE, vpath_candidate_roots, vpath_init
from lib.bundle import (
    ZERO_SHA256,
    collect_directory_entries,
    collect_file_entry,
    ensure_dir,
    write_bundle_directory,
    write_json,
)
from lib.instance import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
    validate_instance_manifest,
)
from lib.install import normalize_install_manifest, validate_install_manifest
from lib.save import (
    SAVE_MANIFEST_NAME,
    deterministic_fingerprint as save_deterministic_fingerprint,
    save_semantic_contract_registry_hash,
    validate_save_manifest,
)
from tools.lib.content_store import (
    JSON_PAYLOAD,
    load_instance_json_artifact,
    load_json,
    resolve_instance_artifact_root,
    store_artifact_root,
)


BUNDLE_KIND_INSTANCE_LINKED = "bundle.instance.linked"
BUNDLE_KIND_INSTANCE_PORTABLE = "bundle.instance.portable"
BUNDLE_KIND_MODPACK = "bundle.modpack"
BUNDLE_KIND_PACK = "bundle.pack"
BUNDLE_KIND_SAVE = "bundle.save"

ITEM_KIND_ARTIFACT = "artifact"
ITEM_KIND_INSTANCE = "instance"
ITEM_KIND_LOCK = "lock"
ITEM_KIND_PACK = "pack"
ITEM_KIND_PROFILE = "profile"
ITEM_KIND_SAVE = "save"

PACK_STORE_CATEGORY = "packs"
LOCK_STORE_CATEGORY = "locks"
PROFILE_STORE_CATEGORY = "profiles"


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_unique(values: Iterable[str]) -> List[str]:
    return sorted({str(item).strip() for item in list(values or []) if str(item).strip()})


def _norm(path: object) -> str:
    text = str(path or "").replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text


def _primary_build_id(install_manifest: Mapping[str, object] | None) -> str:
    builds = _as_map(_as_map(install_manifest).get("product_builds") or _as_map(install_manifest).get("product_build_ids"))
    ordered: List[str] = []
    for key in ("game", "client", "server", "engine", "launcher", "setup"):
        token = str(builds.get(key, "")).strip()
        if token:
            ordered.append(token)
    for _product_id, build_id in sorted(builds.items(), key=lambda row: str(row[0])):
        token = str(build_id or "").strip()
        if token and token not in ordered:
            ordered.append(token)
    return ordered[0] if ordered else "build.unknown"


def _resolve_instance_install_manifest_path(instance_root: str, instance_manifest: Mapping[str, object] | None) -> str:
    install_ref = _as_map(_as_map(instance_manifest).get("install_ref"))
    manifest_ref = str(install_ref.get("manifest_ref", "")).strip()
    if manifest_ref:
        return os.path.abspath(manifest_ref if os.path.isabs(manifest_ref) else os.path.join(instance_root, manifest_ref))
    root_path = str(install_ref.get("root_path", "")).strip()
    if root_path:
        install_root = os.path.abspath(root_path if os.path.isabs(root_path) else os.path.join(instance_root, root_path))
        return os.path.join(install_root, "install.manifest.json")
    return ""


def _contract_registry_hash(*candidates: object) -> str:
    for candidate in candidates:
        token = str(candidate or "").strip().lower()
        if len(token) == 64:
            return token
    return ZERO_SHA256


def _copyable_ref_path(root_path: str, rel_path: str) -> str:
    token = _norm(rel_path)
    if not token:
        return ""
    return os.path.join(root_path, token.replace("/", os.sep))


def _find_store_artifact_root(candidate_store_roots: Sequence[str], category: str, artifact_hash: str) -> str:
    for root in list(candidate_store_roots or []):
        token = os.path.abspath(str(root or "").strip()) if str(root or "").strip() else ""
        if not token:
            continue
        candidate = store_artifact_root(token, category, artifact_hash)
        if os.path.isdir(candidate):
            return candidate
    return ""


def _stage_json(path: str, payload: Mapping[str, object]) -> str:
    return write_json(path, dict(payload or {}))


def _artifact_entries(
    *,
    artifact_root: str,
    category: str,
    artifact_hash: str,
    item_kind: str,
    item_id_or_hash: str,
    extra_extensions: Mapping[str, object] | None = None,
) -> List[dict]:
    return collect_directory_entries(
        source_root=artifact_root,
        bundle_rel_root="store/{}/{}".format(category, artifact_hash),
        item_kind=item_kind,
        item_id_or_hash=item_id_or_hash,
        extensions={
            "artifact_hash": str(artifact_hash),
            "category": str(category),
            **dict(extra_extensions or {}),
        },
    )


def _validate_instance_artifacts(instance_root: str, instance_manifest: Mapping[str, object]) -> Tuple[dict, dict, List[Tuple[str, str]]]:
    pack_lock_hash = str(_as_map(instance_manifest).get("pack_lock_hash", "")).strip()
    profile_bundle_hash = str(_as_map(instance_manifest).get("profile_bundle_hash", "")).strip()
    pack_lock_payload = load_instance_json_artifact(instance_root, dict(instance_manifest or {}), LOCK_STORE_CATEGORY, pack_lock_hash)
    profile_bundle_payload = load_instance_json_artifact(instance_root, dict(instance_manifest or {}), PROFILE_STORE_CATEGORY, profile_bundle_hash)
    if not pack_lock_payload or not profile_bundle_payload:
        raise ValueError("instance CAS artifacts are missing")
    pack_hashes = _as_map(pack_lock_payload.get("pack_hashes"))
    ordered_pack_ids = _sorted_unique(pack_lock_payload.get("ordered_pack_ids") or [])
    pack_rows: List[Tuple[str, str]] = []
    for pack_id in ordered_pack_ids:
        artifact_hash = str(pack_hashes.get(pack_id, "")).strip()
        if not artifact_hash:
            raise ValueError("pack '{}' is missing pinned pack_hash".format(pack_id))
        pack_rows.append((pack_id, artifact_hash))
    return pack_lock_payload, profile_bundle_payload, pack_rows


def _export_instance_manifest(
    *,
    source_manifest: Mapping[str, object],
    install_id: str,
    export_mode: str,
    pack_lock_payload: Mapping[str, object],
    profile_bundle_payload: Mapping[str, object],
    pack_rows: Sequence[Tuple[str, str]],
) -> dict:
    payload = normalize_instance_manifest(source_manifest)
    payload["mode"] = str(export_mode).strip()
    payload["store_root"] = {}
    payload["install_ref"] = {
        "install_id": str(install_id or _as_map(payload.get("install_ref")).get("install_id", "")).strip(),
        "manifest_ref": "",
        "root_path": "",
    }
    payload["pack_lock_hash"] = str(_as_map(pack_lock_payload).get("pack_lock_hash", "")).strip() or str(payload.get("pack_lock_hash", "")).strip()
    payload["profile_bundle_hash"] = str(profile_bundle_payload.get("profile_bundle_hash", "")).strip() or str(payload.get("profile_bundle_hash", "")).strip()
    payload["embedded_builds"] = _as_map(payload.get("embedded_builds")) if export_mode == "portable" else {}
    if export_mode == "portable":
        embedded_artifacts = [
            {
                "category": LOCK_STORE_CATEGORY,
                "artifact_hash": str(payload.get("pack_lock_hash", "")).strip(),
                "artifact_id": str(_as_map(pack_lock_payload).get("pack_lock_id", "")).strip(),
                "artifact_type": "json",
                "artifact_path": "embedded_artifacts/{}/{}".format(LOCK_STORE_CATEGORY, str(payload.get("pack_lock_hash", "")).strip()),
            },
            {
                "category": PROFILE_STORE_CATEGORY,
                "artifact_hash": str(payload.get("profile_bundle_hash", "")).strip(),
                "artifact_id": str(_as_map(profile_bundle_payload).get("profile_bundle_id", "")).strip(),
                "artifact_type": "json",
                "artifact_path": "embedded_artifacts/{}/{}".format(PROFILE_STORE_CATEGORY, str(payload.get("profile_bundle_hash", "")).strip()),
            },
        ]
        for pack_id, artifact_hash in sorted(pack_rows, key=lambda row: (row[0], row[1])):
            embedded_artifacts.append(
                {
                    "category": PACK_STORE_CATEGORY,
                    "artifact_hash": str(artifact_hash),
                    "artifact_id": str(pack_id),
                    "artifact_type": "tree",
                    "artifact_path": "embedded_artifacts/{}/{}".format(PACK_STORE_CATEGORY, str(artifact_hash)),
                }
            )
        payload["embedded_artifacts"] = embedded_artifacts
        payload["capability_lockfile"] = "lockfiles/capabilities.lock"
    else:
        payload["embedded_artifacts"] = []
        payload["capability_lockfile"] = ""
    payload["deterministic_fingerprint"] = ""
    payload = normalize_instance_manifest(payload)
    payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload)
    return payload


def _collect_embedded_build_entries(instance_root: str, instance_manifest: Mapping[str, object]) -> List[dict]:
    rows: List[dict] = []
    for descriptor in _as_map(instance_manifest.get("embedded_builds")).values():
        row = _as_map(descriptor)
        extensions = {
            "product_id": str(row.get("product_id", "")).strip(),
            "build_id": str(row.get("build_id", "")).strip(),
        }
        for field_name in ("binary_ref", "descriptor_ref"):
            rel_path = str(row.get(field_name, "")).strip()
            abs_path = _copyable_ref_path(instance_root, rel_path)
            if not rel_path or not abs_path or not os.path.isfile(abs_path):
                continue
            rows.append(
                collect_file_entry(
                    source_path=abs_path,
                    relative_path="instance/{}".format(_norm(rel_path)),
                    item_kind=ITEM_KIND_INSTANCE,
                    item_id_or_hash=str(row.get("build_id", "")).strip() or str(row.get("product_id", "")).strip(),
                    extensions={**extensions, "field_name": field_name},
                )
            )
    return sorted(rows, key=lambda item: str(item.get("relative_path", "")))


def export_instance_bundle(
    *,
    repo_root: str,
    instance_manifest_path: str,
    out_path: str,
    export_mode: str,
    bundle_id: str = "",
) -> dict:
    if os.path.exists(out_path):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.destination_exists",
            "details": {"target_root": os.path.abspath(out_path).replace("\\", "/")},
        }
    validation = validate_instance_manifest(repo_root=repo_root, instance_manifest_path=instance_manifest_path)
    if validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(validation.get("refusal_code", "")).strip() or "refusal.bundle.instance_invalid",
            "instance_validation": validation,
        }

    instance_manifest = dict(validation.get("instance_manifest") or {})
    instance_root = os.path.dirname(os.path.abspath(instance_manifest_path))
    install_manifest = {}
    install_manifest_path = _resolve_instance_install_manifest_path(instance_root, instance_manifest)
    if install_manifest_path and os.path.isfile(install_manifest_path):
        install_validation = validate_install_manifest(repo_root=repo_root, install_manifest_path=install_manifest_path)
        if install_validation.get("result") == "complete":
            install_manifest = dict(install_validation.get("install_manifest") or {})
        else:
            install_manifest = normalize_install_manifest(load_json(install_manifest_path))

    try:
        pack_lock_payload, profile_bundle_payload, pack_rows = _validate_instance_artifacts(instance_root, instance_manifest)
    except ValueError as exc:
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.instance_artifact_missing",
            "message": str(exc),
        }

    requested_mode = str(export_mode or instance_manifest.get("mode") or "portable").strip().lower()
    if requested_mode not in {"linked", "portable"}:
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.invalid_mode",
            "message": "unsupported instance export mode",
            "details": {"export_mode": requested_mode},
        }

    export_manifest = _export_instance_manifest(
        source_manifest=instance_manifest,
        install_id=str(_as_map(instance_manifest.get("install_ref")).get("install_id", "")).strip() or str(instance_manifest.get("install_id", "")).strip(),
        export_mode=requested_mode,
        pack_lock_payload=pack_lock_payload,
        profile_bundle_payload=profile_bundle_payload,
        pack_rows=pack_rows,
    )
    export_validation = validate_instance_manifest(
        repo_root=repo_root,
        instance_manifest_path=instance_manifest_path,
        manifest_payload=export_manifest,
    )
    if export_validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(export_validation.get("refusal_code", "")).strip() or "refusal.bundle.instance_invalid",
            "instance_validation": export_validation,
        }
    export_manifest = dict(export_validation.get("instance_manifest") or export_manifest)

    file_entries: List[dict] = []
    with tempfile.TemporaryDirectory(prefix="dominium_bundle_instance_") as tmp_root:
        staged_instance_manifest = _stage_json(os.path.join(tmp_root, "instance.manifest.json"), export_manifest)
        file_entries.append(
            collect_file_entry(
                source_path=staged_instance_manifest,
                relative_path="instance/instance.manifest.json",
                item_kind=ITEM_KIND_INSTANCE,
                item_id_or_hash=str(export_manifest.get("instance_id", "")).strip(),
                extensions={"manifest_kind": "instance"},
            )
        )

        if requested_mode == "portable":
            staged_lockfile = _stage_json(os.path.join(tmp_root, "capabilities.lock"), pack_lock_payload)
            file_entries.append(
                collect_file_entry(
                    source_path=staged_lockfile,
                    relative_path="instance/lockfiles/capabilities.lock",
                    item_kind=ITEM_KIND_LOCK,
                    item_id_or_hash=str(pack_lock_payload.get("pack_lock_id", "")).strip() or str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
                    extensions={"legacy_compat": True},
                )
            )
            file_entries.extend(_collect_embedded_build_entries(instance_root, export_manifest))

        if install_manifest:
            staged_install_manifest = _stage_json(os.path.join(tmp_root, "install.manifest.json"), install_manifest)
            file_entries.append(
                collect_file_entry(
                    source_path=staged_install_manifest,
                    relative_path="install/install.manifest.json",
                    item_kind=ITEM_KIND_ARTIFACT,
                    item_id_or_hash=str(install_manifest.get("install_id", "")).strip(),
                    extensions={"artifact_kind": "install_manifest"},
                )
            )

        lock_hash = str(pack_lock_payload.get("pack_lock_hash", "")).strip()
        profile_hash = str(export_manifest.get("profile_bundle_hash", "")).strip() or str(instance_manifest.get("profile_bundle_hash", "")).strip()
        lock_root = resolve_instance_artifact_root(instance_root, instance_manifest, LOCK_STORE_CATEGORY, lock_hash)
        profile_root = resolve_instance_artifact_root(instance_root, instance_manifest, PROFILE_STORE_CATEGORY, profile_hash)
        file_entries.extend(
            _artifact_entries(
                artifact_root=lock_root,
                category=LOCK_STORE_CATEGORY,
                artifact_hash=lock_hash,
                item_kind=ITEM_KIND_LOCK,
                item_id_or_hash=str(pack_lock_payload.get("pack_lock_id", "")).strip() or lock_hash,
            )
        )
        file_entries.extend(
            _artifact_entries(
                artifact_root=profile_root,
                category=PROFILE_STORE_CATEGORY,
                artifact_hash=profile_hash,
                item_kind=ITEM_KIND_PROFILE,
                item_id_or_hash=str(profile_bundle_payload.get("profile_bundle_id", "")).strip() or profile_hash,
            )
        )
        for pack_id, artifact_hash in sorted(pack_rows, key=lambda row: (row[0], row[1])):
            artifact_root = resolve_instance_artifact_root(instance_root, instance_manifest, PACK_STORE_CATEGORY, artifact_hash)
            file_entries.extend(
                _artifact_entries(
                    artifact_root=artifact_root,
                    category=PACK_STORE_CATEGORY,
                    artifact_hash=artifact_hash,
                    item_kind=ITEM_KIND_PACK,
                    item_id_or_hash=str(pack_id),
                    extra_extensions={"pack_id": str(pack_id)},
                )
            )

        result = write_bundle_directory(
            bundle_root=out_path,
            bundle_kind=BUNDLE_KIND_INSTANCE_PORTABLE if requested_mode == "portable" else BUNDLE_KIND_INSTANCE_LINKED,
            created_by_build_id=_primary_build_id(install_manifest),
            contract_registry_hash=_contract_registry_hash(
                pack_lock_payload.get("semantic_contract_registry_hash"),
                install_manifest.get("semantic_contract_registry_hash"),
            ),
            file_entries=file_entries,
            bundle_id=bundle_id,
            extensions={
                "instance_id": str(export_manifest.get("instance_id", "")).strip(),
                "instance_kind": str(export_manifest.get("instance_kind", "")).strip(),
                "source_mode": str(instance_manifest.get("mode", "")).strip(),
            },
        )
        result["result"] = "complete"
        result["bundle_kind"] = BUNDLE_KIND_INSTANCE_PORTABLE if requested_mode == "portable" else BUNDLE_KIND_INSTANCE_LINKED
        result["instance_manifest"] = export_manifest
        return result


def _save_bundle_store_roots(repo_root: str, save_root: str, explicit_store_root: str = "") -> List[str]:
    candidates: List[str] = []
    context = vpath_init(
        {
            "repo_root": repo_root,
            "product_id": "tool.attach_console_stub",
            "raw_args": ["--store-root", str(explicit_store_root)] if str(explicit_store_root or "").strip() else [],
        }
    )
    if str(context.get("result", "")).strip() == "complete":
        candidates.extend(vpath_candidate_roots(VROOT_STORE, context))
    for token in (explicit_store_root, repo_root):
        if str(token or "").strip():
            candidates.append(os.path.abspath(str(token)))
    parent = os.path.abspath(os.path.join(save_root, os.pardir, os.pardir))
    if os.path.isdir(os.path.join(parent, "store")):
        candidates.append(parent)
    seen = set()
    out = []
    for item in candidates:
        norm = os.path.abspath(str(item))
        if norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


def export_save_bundle(
    *,
    repo_root: str,
    save_manifest_path: str,
    out_path: str,
    vendor_packs: bool = False,
    bundle_id: str = "",
    store_root: str = "",
) -> dict:
    if os.path.exists(out_path):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.destination_exists",
            "details": {"target_root": os.path.abspath(out_path).replace("\\", "/")},
        }
    validation = validate_save_manifest(repo_root=repo_root, save_manifest_path=save_manifest_path)
    if validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(validation.get("refusal_code", "")).strip() or "refusal.bundle.save_invalid",
            "save_validation": validation,
        }
    save_manifest = dict(validation.get("save_manifest") or {})
    save_manifest["deterministic_fingerprint"] = ""
    save_manifest["deterministic_fingerprint"] = save_deterministic_fingerprint(save_manifest)
    save_root = os.path.dirname(os.path.abspath(save_manifest_path))
    candidate_store_roots = _save_bundle_store_roots(repo_root, save_root, explicit_store_root=store_root)

    file_entries: List[dict] = []
    with tempfile.TemporaryDirectory(prefix="dominium_bundle_save_") as tmp_root:
        staged_manifest = _stage_json(os.path.join(tmp_root, SAVE_MANIFEST_NAME), save_manifest)
        file_entries.append(
            collect_file_entry(
                source_path=staged_manifest,
                relative_path="save/{}".format(SAVE_MANIFEST_NAME),
                item_kind=ITEM_KIND_SAVE,
                item_id_or_hash=str(save_manifest.get("save_id", "")).strip(),
                extensions={"manifest_kind": "save"},
            )
        )

        for field_name, bundle_root, required in (
            ("contract_bundle_ref", "save", True),
            ("state_snapshots_ref", "save", True),
            ("patches_ref", "save", True),
            ("proofs_ref", "save", False),
        ):
            rel_path = str(save_manifest.get(field_name, "")).strip()
            if not rel_path:
                continue
            abs_path = _copyable_ref_path(save_root, rel_path)
            if not abs_path or not os.path.exists(abs_path):
                if not required:
                    continue
                return {
                    "result": "refused",
                    "refusal_code": "refusal.bundle.save_missing_ref",
                    "message": "referenced save payload is missing",
                    "details": {"field_name": field_name, "relative_path": rel_path},
                }
            if os.path.isdir(abs_path):
                file_entries.extend(
                    collect_directory_entries(
                        source_root=abs_path,
                        bundle_rel_root="{}/{}".format(bundle_root, _norm(rel_path)),
                        item_kind=ITEM_KIND_SAVE,
                        item_id_or_hash=str(save_manifest.get("save_id", "")).strip(),
                        extensions={"field_name": field_name},
                    )
                )
            else:
                file_entries.append(
                    collect_file_entry(
                        source_path=abs_path,
                        relative_path="{}/{}".format(bundle_root, _norm(rel_path)),
                        item_kind=ITEM_KIND_SAVE,
                        item_id_or_hash=str(save_manifest.get("save_id", "")).strip(),
                        extensions={"field_name": field_name},
                    )
                )

        pack_lock_hash = str(save_manifest.get("pack_lock_hash", "")).strip()
        pack_lock_root = _find_store_artifact_root(candidate_store_roots, LOCK_STORE_CATEGORY, pack_lock_hash)
        pack_lock_payload = {}
        if pack_lock_root:
            payload_path = os.path.join(pack_lock_root, JSON_PAYLOAD)
            if os.path.isfile(payload_path):
                pack_lock_payload = load_json(payload_path)
            file_entries.extend(
                _artifact_entries(
                    artifact_root=pack_lock_root,
                    category=LOCK_STORE_CATEGORY,
                    artifact_hash=pack_lock_hash,
                    item_kind=ITEM_KIND_LOCK,
                    item_id_or_hash=str(_as_map(pack_lock_payload).get("pack_lock_id", "")).strip() or pack_lock_hash,
                )
            )

        if vendor_packs and pack_lock_payload:
            pack_hashes = _as_map(pack_lock_payload.get("pack_hashes"))
            for pack_id in _sorted_unique(pack_lock_payload.get("ordered_pack_ids") or []):
                artifact_hash = str(pack_hashes.get(pack_id, "")).strip()
                if not artifact_hash:
                    return {
                        "result": "refused",
                        "refusal_code": "refusal.bundle.save_missing_pack_hash",
                        "details": {"pack_id": pack_id},
                    }
                pack_root = _find_store_artifact_root(candidate_store_roots, PACK_STORE_CATEGORY, artifact_hash)
                if not pack_root:
                    return {
                        "result": "refused",
                        "refusal_code": "refusal.bundle.save_missing_pack",
                        "details": {"pack_id": pack_id, "artifact_hash": artifact_hash},
                    }
                file_entries.extend(
                    _artifact_entries(
                        artifact_root=pack_root,
                        category=PACK_STORE_CATEGORY,
                        artifact_hash=artifact_hash,
                        item_kind=ITEM_KIND_PACK,
                        item_id_or_hash=pack_id,
                        extra_extensions={"pack_id": pack_id},
                    )
                )

        result = write_bundle_directory(
            bundle_root=out_path,
            bundle_kind=BUNDLE_KIND_SAVE,
            created_by_build_id=str(save_manifest.get("created_by_build_id", "")).strip() or "build.unknown",
            contract_registry_hash=_contract_registry_hash(
                save_semantic_contract_registry_hash(save_manifest),
                _as_map(pack_lock_payload).get("semantic_contract_registry_hash"),
            ),
            file_entries=file_entries,
            bundle_id=bundle_id,
            extensions={
                "save_id": str(save_manifest.get("save_id", "")).strip(),
                "vendor_packs": bool(vendor_packs),
            },
        )
        result["result"] = "complete"
        result["bundle_kind"] = BUNDLE_KIND_SAVE
        result["save_manifest"] = save_manifest
        return result


def _infer_pack_id(pack_root: str) -> str:
    manifest_path = os.path.join(pack_root, "pack.json")
    if os.path.isfile(manifest_path):
        try:
            payload = json.load(open(manifest_path, "r", encoding="utf-8"))
        except (OSError, ValueError):
            payload = {}
        if isinstance(payload, Mapping) and str(payload.get("pack_id", "")).strip():
            return str(payload.get("pack_id", "")).strip()
    return os.path.basename(os.path.abspath(pack_root))


def export_pack_bundle(
    *,
    repo_root: str,
    pack_root: str,
    out_path: str,
    bundle_id: str = "",
) -> dict:
    del repo_root
    abs_pack_root = os.path.abspath(str(pack_root or "").strip())
    if os.path.exists(out_path):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.destination_exists",
            "details": {"target_root": os.path.abspath(out_path).replace("\\", "/")},
        }
    if not os.path.isdir(abs_pack_root):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.pack_missing",
            "details": {"pack_root": str(pack_root or "")},
        }

    with tempfile.TemporaryDirectory(prefix="dominium_bundle_pack_") as tmp_root:
        staged_store_root = os.path.join(tmp_root, "store_root")
        ensure_dir(staged_store_root)
        from tools.lib.content_store import initialize_store_root, store_add_tree_artifact

        initialize_store_root(staged_store_root)
        add_result = store_add_tree_artifact(staged_store_root, PACK_STORE_CATEGORY, abs_pack_root)
        artifact_hash = str(add_result.get("artifact_hash", "")).strip()
        artifact_root = store_artifact_root(staged_store_root, PACK_STORE_CATEGORY, artifact_hash)
        pack_id = _infer_pack_id(abs_pack_root)
        result = write_bundle_directory(
            bundle_root=out_path,
            bundle_kind=BUNDLE_KIND_PACK,
            created_by_build_id="build.unknown",
            contract_registry_hash=ZERO_SHA256,
            file_entries=_artifact_entries(
                artifact_root=artifact_root,
                category=PACK_STORE_CATEGORY,
                artifact_hash=artifact_hash,
                item_kind=ITEM_KIND_PACK,
                item_id_or_hash=pack_id,
                extra_extensions={"pack_id": pack_id},
            ),
            bundle_id=bundle_id,
            extensions={"pack_id": pack_id, "pack_hash": artifact_hash},
        )
        result["result"] = "complete"
        result["bundle_kind"] = BUNDLE_KIND_PACK
        result["pack_id"] = pack_id
        result["pack_hash"] = artifact_hash
        return result


__all__ = [
    "BUNDLE_KIND_INSTANCE_LINKED",
    "BUNDLE_KIND_INSTANCE_PORTABLE",
    "BUNDLE_KIND_MODPACK",
    "BUNDLE_KIND_PACK",
    "BUNDLE_KIND_SAVE",
    "export_instance_bundle",
    "export_pack_bundle",
    "export_save_bundle",
]
