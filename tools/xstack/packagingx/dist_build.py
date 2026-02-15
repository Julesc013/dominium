"""Deterministic dist layout build/validation helpers for Lab Galaxy packaging."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.pack_loader.dependency_resolver import resolve_packs
from tools.xstack.pack_loader.loader import load_pack_set
from tools.xstack.registry_compile.bundle_profile import load_bundle_profile, resolve_bundle_selection
from tools.xstack.registry_compile.compiler import compile_bundle
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload
from tools.xstack.sessionx.creator import create_session_spec
from tools.xstack.sessionx.runner import boot_session_spec
from tools.xstack.sessionx.script_runner import run_intent_script


LOCKFILE_REGISTRY_FILE_MAP = {
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

MANAGED_SUBDIRS = ("bin", "packs", "bundles", "registries")
MANAGED_FILES = ("lockfile.json", "manifest.json")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _resolve_root(repo_root: str, path: str) -> str:
    token = str(path or "").strip()
    if not token:
        return repo_root
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token))


def _repo_relative(repo_root: str, path: str) -> str:
    try:
        return _norm(os.path.relpath(path, repo_root))
    except ValueError:
        return _norm(path)


def _read_json_object(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _write_canonical_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def _write_text(path: str, text: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\r\n", "\n"))


def _copy_file(src: str, dst: str) -> None:
    parent = os.path.dirname(dst)
    if parent:
        _ensure_dir(parent)
    with open(src, "rb") as in_handle:
        data = in_handle.read()
    with open(dst, "wb") as out_handle:
        out_handle.write(data)


def _copy_tree_deterministic(src_root: str, dst_root: str) -> None:
    _ensure_dir(dst_root)
    for walk_root, dirs, files in os.walk(src_root):
        dirs.sort()
        files.sort()
        rel_root = os.path.relpath(walk_root, src_root)
        target_root = dst_root if rel_root == "." else os.path.join(dst_root, rel_root)
        _ensure_dir(target_root)
        for name in files:
            src_path = os.path.join(walk_root, name)
            dst_path = os.path.join(target_root, name)
            _copy_file(src_path, dst_path)


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _list_files_deterministic(root: str) -> List[str]:
    out: List[str] = []
    if not os.path.isdir(root):
        return out
    for walk_root, dirs, files in os.walk(root):
        dirs.sort()
        files.sort()
        for name in files:
            abs_path = os.path.join(walk_root, name)
            rel_path = _norm(os.path.relpath(abs_path, root))
            out.append(rel_path)
    return sorted(out)


def _version_value(repo_root: str, file_name: str, default_value: str) -> str:
    path = os.path.join(repo_root, file_name)
    try:
        token = open(path, "r", encoding="utf-8").read().strip()
    except OSError:
        token = ""
    return token or default_value


def _errors_sorted(rows: List[dict]) -> List[dict]:
    return sorted(
        [
            {
                "code": str(item.get("code", "")),
                "message": str(item.get("message", "")),
                "path": str(item.get("path", "$")),
            }
            for item in rows
            if isinstance(item, dict)
        ],
        key=lambda item: (item["code"], item["path"], item["message"]),
    )


def _refused(errors: List[dict], **extra) -> Dict[str, object]:
    out = {
        "result": "refused",
        "errors": _errors_sorted(errors),
    }
    out.update(extra)
    return out


def _remove_managed_layout(out_root: str) -> None:
    for rel_dir in MANAGED_SUBDIRS:
        abs_dir = os.path.join(out_root, rel_dir)
        if os.path.isdir(abs_dir):
            shutil.rmtree(abs_dir)
    for rel_file in MANAGED_FILES:
        abs_file = os.path.join(out_root, rel_file)
        if os.path.isfile(abs_file):
            os.remove(abs_file)


def _bin_stub_rows() -> List[Tuple[str, str]]:
    return [
        (
            "bin/client",
            "#!/usr/bin/env python3\n"
            "# Deterministic lab client launcher stub.\n"
            "print('dominium client runtime is not bundled in source dist; use launcher tool')\n",
        ),
        (
            "bin/engine",
            "#!/usr/bin/env python3\n"
            "# Deterministic engine launcher stub.\n"
            "print('dominium engine runtime is not bundled in source dist')\n",
        ),
        (
            "bin/server",
            "#!/usr/bin/env python3\n"
            "# Deterministic server launcher stub.\n"
            "print('dominium server runtime is not bundled in source dist')\n",
        ),
        (
            "bin/setup",
            "#!/usr/bin/env python3\n"
            "# Dist setup entrypoint.\n"
            "print('invoke repo tool: tools/setup/build --bundle bundle.base.lab --out dist')\n",
        ),
        (
            "bin/launcher",
            "#!/usr/bin/env python3\n"
            "# Dist launcher entrypoint.\n"
            "print('invoke repo tool: tools/launcher/launch run --dist dist --session <session_spec>')\n",
        ),
        (
            "bin/setup.cmd",
            "@echo off\r\n"
            "echo invoke repo tool: tools\\setup\\build --bundle bundle.base.lab --out dist\r\n",
        ),
        (
            "bin/launcher.cmd",
            "@echo off\r\n"
            "echo invoke repo tool: tools\\launcher\\launch run --dist dist --session ^<session_spec^>\r\n",
        ),
    ]


def _dist_file_hashes(out_root: str, include_manifest: bool) -> List[dict]:
    rows: List[dict] = []
    for rel_dir in MANAGED_SUBDIRS:
        abs_dir = os.path.join(out_root, rel_dir)
        for rel_file in _list_files_deterministic(abs_dir):
            abs_path = os.path.join(abs_dir, rel_file.replace("/", os.sep))
            rows.append(
                {
                    "path": _norm(os.path.join(rel_dir, rel_file)),
                    "sha256": _sha256_file(abs_path),
                }
            )

    lockfile_path = os.path.join(out_root, "lockfile.json")
    if os.path.isfile(lockfile_path):
        rows.append({"path": "lockfile.json", "sha256": _sha256_file(lockfile_path)})
    manifest_path = os.path.join(out_root, "manifest.json")
    if include_manifest and os.path.isfile(manifest_path):
        rows.append({"path": "manifest.json", "sha256": _sha256_file(manifest_path)})
    return sorted(rows, key=lambda item: (item["path"], item["sha256"]))


def _manifest_payload(
    repo_root: str,
    bundle_id: str,
    lockfile_payload: dict,
    resolved_packs: List[dict],
    file_hash_rows: List[dict],
) -> dict:
    registries = dict(lockfile_payload.get("registries") or {})
    pack_lock_hash = str(lockfile_payload.get("pack_lock_hash", ""))
    composite_baseline = canonical_sha256(
        {
            "pack_lock_hash": pack_lock_hash,
            "registry_hashes": registries,
        }
    )
    return {
        "schema_version": "1.0.0",
        "manifest_type": "dominium.dist_manifest",
        "layout_version": "1.0.0",
        "bundle_id": str(bundle_id),
        "build_version": _version_value(repo_root, ".dominium_build_number", "0"),
        "engine_version": _version_value(repo_root, "VERSION_ENGINE", "0.0.0"),
        "client_version": _version_value(repo_root, "VERSION_CLIENT", "0.0.0"),
        "server_version": _version_value(repo_root, "VERSION_SERVER", "0.0.0"),
        "setup_version": _version_value(repo_root, "VERSION_SETUP", "0.0.0"),
        "launcher_version": _version_value(repo_root, "VERSION_LAUNCHER", "0.0.0"),
        "compatibility_version": str(lockfile_payload.get("compatibility_version", "")),
        "pack_lock_hash": pack_lock_hash,
        "registry_hashes": registries,
        "registry_hash_chain": canonical_sha256(registries),
        "composite_hash_anchor_baseline": composite_baseline,
        "lockfile_path": "lockfile.json",
        "resolved_packs": resolved_packs,
        "managed_file_count": len(file_hash_rows),
        "file_hashes": file_hash_rows,
        # canonical_content_hash intentionally excludes manifest.json to avoid self-reference cycles.
        "canonical_content_hash": canonical_sha256(file_hash_rows),
    }


def _build_lock_and_resolve_packs(
    repo_root: str,
    bundle_id: str,
    use_cache: bool,
) -> Tuple[dict, List[dict], List[dict], Dict[str, object]]:
    compile_result = compile_bundle(
        repo_root=repo_root,
        bundle_id=str(bundle_id),
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=bool(use_cache),
    )
    if compile_result.get("result") != "complete":
        return {}, [], [], _refused(
            compile_result.get("errors") or [
                {
                    "code": "REFUSE_DIST_COMPILE_FAILED",
                    "message": "registry compile failed",
                    "path": "$.registry_compile",
                }
            ]
        )

    lock_path = os.path.join(repo_root, "build", "lockfile.json")
    lockfile_payload, lock_err = _read_json_object(lock_path)
    if lock_err:
        return {}, [], [], _refused(
            [
                {
                    "code": "REFUSE_DIST_LOCKFILE_MISSING",
                    "message": "build/lockfile.json is missing or invalid",
                    "path": "$.lockfile",
                }
            ]
        )

    schema_check = validate_instance(
        repo_root=repo_root,
        schema_name="bundle_lockfile",
        payload=lockfile_payload,
        strict_top_level=True,
    )
    if not bool(schema_check.get("valid", False)):
        return {}, [], [], _refused(schema_check.get("errors") or [])

    semantic = validate_lockfile_payload(lockfile_payload)
    if semantic.get("result") != "complete":
        return {}, [], [], _refused(semantic.get("errors") or [])
    if str(lockfile_payload.get("bundle_id", "")) != str(bundle_id):
        return {}, [], [], _refused(
            [
                {
                    "code": "REFUSE_DIST_BUNDLE_MISMATCH",
                    "message": "lockfile bundle_id does not match requested bundle_id",
                    "path": "$.bundle_id",
                }
            ]
        )

    loaded = load_pack_set(repo_root=repo_root, packs_root_rel="packs", schema_repo_root=repo_root)
    if loaded.get("result") != "complete":
        return {}, [], [], _refused(loaded.get("errors") or [])
    selection = resolve_bundle_selection(
        bundle_id=str(bundle_id),
        packs=loaded.get("packs") or [],
        repo_root=repo_root,
        schema_repo_root=repo_root,
    )
    if selection.get("result") != "complete":
        return {}, [], [], _refused(selection.get("errors") or [])
    resolved = resolve_packs(loaded.get("packs") or [], bundle_selection=list(selection.get("selected_pack_ids") or []))
    if resolved.get("result") != "complete":
        return {}, [], [], _refused(resolved.get("errors") or [])

    resolved_rows: List[dict] = []
    for row in (resolved.get("ordered_pack_list") or []):
        manifest = dict(row.get("manifest") or {})
        resolved_rows.append(
            {
                "pack_id": str(row.get("pack_id", "")),
                "category": str(row.get("category", "")),
                "version": str(row.get("version", "")),
                "canonical_hash": str(manifest.get("canonical_hash", "")),
                "signature_status": str(row.get("signature_status", "")),
                "pack_dir_rel": str(row.get("pack_dir_rel", "")),
            }
        )
    resolved_rows = sorted(resolved_rows, key=lambda item: (item["pack_id"], item["version"]))
    return lockfile_payload, resolved_rows, list(selection.get("selected_pack_ids") or []), {"result": "complete"}


def build_dist_layout(
    repo_root: str,
    bundle_id: str = DEFAULT_BUNDLE_ID,
    out_dir: str = "dist",
    use_cache: bool = True,
) -> Dict[str, object]:
    bundle_profile = load_bundle_profile(repo_root=repo_root, bundle_id=str(bundle_id), schema_repo_root=repo_root)
    if bundle_profile.get("result") != "complete":
        return _refused(bundle_profile.get("errors") or [])

    lockfile_payload, resolved_rows, _selected_pack_ids, prep = _build_lock_and_resolve_packs(
        repo_root=repo_root,
        bundle_id=str(bundle_id),
        use_cache=bool(use_cache),
    )
    if prep.get("result") != "complete":
        return prep

    out_root = _resolve_root(repo_root, out_dir)
    _ensure_dir(out_root)
    _remove_managed_layout(out_root)

    for rel_dir in MANAGED_SUBDIRS:
        _ensure_dir(os.path.join(out_root, rel_dir))

    for rel_path, text in _bin_stub_rows():
        _write_text(os.path.join(out_root, rel_path.replace("/", os.sep)), text)

    for row in resolved_rows:
        src = os.path.join(repo_root, str(row.get("pack_dir_rel", "")).replace("/", os.sep))
        if not os.path.isdir(src):
            return _refused(
                [
                    {
                        "code": "REFUSE_DIST_PACK_MISSING",
                        "message": "resolved pack directory is missing for '{}'".format(str(row.get("pack_id", ""))),
                        "path": "$.packs",
                    }
                ]
            )
        dst = os.path.join(
            out_root,
            "packs",
            str(row.get("category", "")).replace("/", os.sep),
            str(row.get("pack_id", "")).replace("/", os.sep),
        )
        _copy_tree_deterministic(src, dst)

    bundle_src = os.path.join(repo_root, str(bundle_profile.get("bundle_path", "")).replace("/", os.sep))
    bundle_payload, bundle_err = _read_json_object(bundle_src)
    if bundle_err:
        return _refused(
            [
                {
                    "code": "REFUSE_DIST_BUNDLE_INVALID",
                    "message": "bundle manifest is missing or invalid",
                    "path": "$.bundle",
                }
            ]
        )
    bundle_dst = os.path.join(out_root, "bundles", str(bundle_id), "bundle.json")
    _write_canonical_json(bundle_dst, bundle_payload)

    registries = dict(lockfile_payload.get("registries") or {})
    for lock_key, file_name in sorted(LOCKFILE_REGISTRY_FILE_MAP.items(), key=lambda item: item[1]):
        src = os.path.join(repo_root, "build", "registries", file_name)
        payload, err = _read_json_object(src)
        if err:
            return _refused(
                [
                    {
                        "code": "REFUSE_DIST_REGISTRY_MISSING",
                        "message": "compiled registry '{}' is missing or invalid".format(file_name),
                        "path": "$.registries",
                    }
                ]
            )
        actual_hash = str(payload.get("registry_hash", "")).strip() or canonical_sha256(payload)
        expected_hash = str(registries.get(lock_key, "")).strip()
        if expected_hash != actual_hash:
            return _refused(
                [
                    {
                        "code": "REFUSE_DIST_REGISTRY_HASH_MISMATCH",
                        "message": "registry hash mismatch for '{}'".format(file_name),
                        "path": "$.registries.{}".format(lock_key),
                    }
                ]
            )
        dst = os.path.join(out_root, "registries", file_name)
        _write_canonical_json(dst, payload)

    lock_dst = os.path.join(out_root, "lockfile.json")
    _write_canonical_json(lock_dst, lockfile_payload)

    resolved_for_manifest = [
        {
            "pack_id": str(row.get("pack_id", "")),
            "category": str(row.get("category", "")),
            "version": str(row.get("version", "")),
            "canonical_hash": str(row.get("canonical_hash", "")),
            "signature_status": str(row.get("signature_status", "")),
            "path": "packs/{}/{}".format(str(row.get("category", "")), str(row.get("pack_id", ""))),
        }
        for row in resolved_rows
    ]
    file_hash_rows = _dist_file_hashes(out_root, include_manifest=False)
    manifest_payload = _manifest_payload(
        repo_root=repo_root,
        bundle_id=str(bundle_id),
        lockfile_payload=lockfile_payload,
        resolved_packs=resolved_for_manifest,
        file_hash_rows=file_hash_rows,
    )
    manifest_path = os.path.join(out_root, "manifest.json")
    _write_canonical_json(manifest_path, manifest_payload)

    final_file_rows = _dist_file_hashes(out_root, include_manifest=True)
    return {
        "result": "complete",
        "bundle_id": str(bundle_id),
        "out_dir": _repo_relative(repo_root, out_root),
        "manifest_path": _repo_relative(repo_root, manifest_path),
        "lockfile_path": _repo_relative(repo_root, lock_dst),
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "registry_hashes": registries,
        "canonical_content_hash": str(manifest_payload.get("canonical_content_hash", "")),
        "manifest_hash": _sha256_file(manifest_path),
        "lockfile_hash": _sha256_file(lock_dst),
        "file_count": len(final_file_rows),
        "file_hashes": final_file_rows,
    }


def validate_dist_layout(
    repo_root: str,
    dist_root: str = "dist",
) -> Dict[str, object]:
    out_root = _resolve_root(repo_root, dist_root)
    errors: List[dict] = []
    for rel_dir in MANAGED_SUBDIRS:
        abs_dir = os.path.join(out_root, rel_dir)
        if not os.path.isdir(abs_dir):
            errors.append(
                {
                    "code": "REFUSE_DIST_LAYOUT_MISSING",
                    "message": "missing required dist directory '{}'".format(rel_dir),
                    "path": "$.{}".format(rel_dir),
                }
            )
    manifest_path = os.path.join(out_root, "manifest.json")
    lockfile_path = os.path.join(out_root, "lockfile.json")
    if not os.path.isfile(manifest_path):
        errors.append(
            {
                "code": "REFUSE_DIST_MANIFEST_MISSING",
                "message": "missing dist manifest.json",
                "path": "$.manifest",
            }
        )
    if not os.path.isfile(lockfile_path):
        errors.append(
            {
                "code": "REFUSE_DIST_LOCKFILE_MISSING",
                "message": "missing dist lockfile.json",
                "path": "$.lockfile",
            }
        )
    if errors:
        return _refused(errors, dist_root=_repo_relative(repo_root, out_root))

    lockfile_payload, lock_err = _read_json_object(lockfile_path)
    manifest_payload, manifest_err = _read_json_object(manifest_path)
    if lock_err:
        errors.append(
            {
                "code": "REFUSE_DIST_LOCKFILE_INVALID",
                "message": "dist lockfile.json is invalid",
                "path": "$.lockfile",
            }
        )
    if manifest_err:
        errors.append(
            {
                "code": "REFUSE_DIST_MANIFEST_INVALID",
                "message": "dist manifest.json is invalid",
                "path": "$.manifest",
            }
        )
    if errors:
        return _refused(errors, dist_root=_repo_relative(repo_root, out_root))

    schema_check = validate_instance(
        repo_root=repo_root,
        schema_name="bundle_lockfile",
        payload=lockfile_payload,
        strict_top_level=True,
    )
    if not bool(schema_check.get("valid", False)):
        errors.extend(schema_check.get("errors") or [])
    semantic = validate_lockfile_payload(lockfile_payload)
    if semantic.get("result") != "complete":
        errors.extend(semantic.get("errors") or [])
    registries = dict(lockfile_payload.get("registries") or {})

    for lock_key, file_name in sorted(LOCKFILE_REGISTRY_FILE_MAP.items(), key=lambda item: item[1]):
        abs_path = os.path.join(out_root, "registries", file_name)
        payload, err = _read_json_object(abs_path)
        if err:
            errors.append(
                {
                    "code": "REFUSE_DIST_REGISTRY_MISSING",
                    "message": "dist registry '{}' is missing or invalid".format(file_name),
                    "path": "$.registries",
                }
            )
            continue
        expected_hash = str(registries.get(lock_key, "")).strip()
        actual_hash = str(payload.get("registry_hash", "")).strip() or canonical_sha256(payload)
        if expected_hash != actual_hash:
            errors.append(
                {
                    "code": "REFUSE_DIST_REGISTRY_HASH_MISMATCH",
                    "message": "registry hash mismatch for '{}'".format(file_name),
                    "path": "$.registries.{}".format(lock_key),
                }
            )

    for row in (manifest_payload.get("resolved_packs") or []):
        if not isinstance(row, dict):
            errors.append(
                {
                    "code": "REFUSE_DIST_MANIFEST_PACKS_INVALID",
                    "message": "manifest resolved_packs entry must be object",
                    "path": "$.resolved_packs",
                }
            )
            continue
        rel_path = str(row.get("path", "")).strip()
        if not rel_path:
            errors.append(
                {
                    "code": "REFUSE_DIST_MANIFEST_PACK_PATH_MISSING",
                    "message": "manifest resolved_packs entry missing path",
                    "path": "$.resolved_packs.path",
                }
            )
            continue
        abs_path = os.path.join(out_root, rel_path.replace("/", os.sep))
        if not os.path.isdir(abs_path):
            errors.append(
                {
                    "code": "REFUSE_DIST_PACK_MISSING",
                    "message": "pack path '{}' referenced by manifest is missing".format(rel_path),
                    "path": "$.resolved_packs.path",
                }
            )

    file_hash_rows = _dist_file_hashes(out_root, include_manifest=False)
    expected_content_hash = canonical_sha256(file_hash_rows)
    if str(manifest_payload.get("canonical_content_hash", "")) != expected_content_hash:
        errors.append(
            {
                "code": "REFUSE_DIST_CONTENT_HASH_MISMATCH",
                "message": "manifest canonical_content_hash mismatch",
                "path": "$.canonical_content_hash",
            }
        )
    if list(manifest_payload.get("file_hashes") or []) != file_hash_rows:
        errors.append(
            {
                "code": "REFUSE_DIST_FILE_HASH_LIST_MISMATCH",
                "message": "manifest file_hashes list does not match current dist files",
                "path": "$.file_hashes",
            }
        )
    expected_chain = canonical_sha256(registries)
    if str(manifest_payload.get("registry_hash_chain", "")) != expected_chain:
        errors.append(
            {
                "code": "REFUSE_DIST_REGISTRY_CHAIN_MISMATCH",
                "message": "manifest registry_hash_chain mismatch",
                "path": "$.registry_hash_chain",
            }
        )
    expected_composite_baseline = canonical_sha256(
        {
            "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
            "registry_hashes": registries,
        }
    )
    if str(manifest_payload.get("composite_hash_anchor_baseline", "")) != expected_composite_baseline:
        errors.append(
            {
                "code": "REFUSE_DIST_COMPOSITE_BASELINE_MISMATCH",
                "message": "manifest composite_hash_anchor_baseline mismatch",
                "path": "$.composite_hash_anchor_baseline",
            }
        )
    if str(manifest_payload.get("pack_lock_hash", "")) != str(lockfile_payload.get("pack_lock_hash", "")):
        errors.append(
            {
                "code": "REFUSE_DIST_PACK_LOCK_MISMATCH",
                "message": "manifest pack_lock_hash does not match lockfile",
                "path": "$.pack_lock_hash",
            }
        )
    if dict(manifest_payload.get("registry_hashes") or {}) != registries:
        errors.append(
            {
                "code": "REFUSE_DIST_MANIFEST_REGISTRY_HASH_MISMATCH",
                "message": "manifest registry_hashes does not match lockfile",
                "path": "$.registry_hashes",
            }
        )

    if errors:
        return _refused(errors, dist_root=_repo_relative(repo_root, out_root))
    return {
        "result": "complete",
        "dist_root": _repo_relative(repo_root, out_root),
        "bundle_id": str(lockfile_payload.get("bundle_id", "")),
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "registry_hashes": registries,
        "canonical_content_hash": expected_content_hash,
        "manifest_hash": _sha256_file(manifest_path),
        "lockfile_hash": _sha256_file(lockfile_path),
    }


def run_lab_build_validation(
    repo_root: str,
    bundle_id: str = DEFAULT_BUNDLE_ID,
    dist_a: str = "build/dist.lab_validation.a",
    dist_b: str = "build/dist.lab_validation.b",
    save_id: str = "save.xstack.lab_validation",
) -> Dict[str, object]:
    build_a = build_dist_layout(repo_root=repo_root, bundle_id=bundle_id, out_dir=dist_a, use_cache=True)
    if build_a.get("result") != "complete":
        return build_a
    validate_a = validate_dist_layout(repo_root=repo_root, dist_root=dist_a)
    if validate_a.get("result") != "complete":
        return validate_a

    build_b = build_dist_layout(repo_root=repo_root, bundle_id=bundle_id, out_dir=dist_b, use_cache=True)
    if build_b.get("result") != "complete":
        return build_b
    validate_b = validate_dist_layout(repo_root=repo_root, dist_root=dist_b)
    if validate_b.get("result") != "complete":
        return validate_b

    if str(build_a.get("canonical_content_hash", "")) != str(build_b.get("canonical_content_hash", "")):
        return _refused(
            [
                {
                    "code": "REFUSE_DIST_NONDETERMINISTIC",
                    "message": "canonical_content_hash differs across repeated builds",
                    "path": "$.canonical_content_hash",
                }
            ],
            first=build_a,
            second=build_b,
        )
    if str(build_a.get("manifest_hash", "")) != str(build_b.get("manifest_hash", "")):
        return _refused(
            [
                {
                    "code": "REFUSE_DIST_MANIFEST_NONDETERMINISTIC",
                    "message": "manifest hash differs across repeated builds",
                    "path": "$.manifest_hash",
                }
            ],
            first=build_a,
            second=build_b,
        )

    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    fixture_payload, fixture_err = _read_json_object(fixture_path)
    if fixture_err:
        return _refused(
            [
                {
                    "code": "REFUSE_LAB_VALIDATION_FIXTURE_MISSING",
                    "message": "session fixture is missing or invalid",
                    "path": "$.fixture",
                }
            ]
        )

    created = create_session_spec(
        repo_root=repo_root,
        save_id=str(save_id),
        bundle_id=str(fixture_payload.get("bundle_id", bundle_id)),
        scenario_id=str(fixture_payload.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(fixture_payload.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(fixture_payload.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(fixture_payload.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id=str(fixture_payload.get("budget_policy_id", "policy.budget.default_lab")),
        fidelity_policy_id=str(fixture_payload.get("fidelity_policy_id", "policy.fidelity.default_lab")),
        rng_seed_string=str(fixture_payload.get("rng_seed_string", "seed.xstack.lab.validation")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(fixture_payload.get("universe_seed_string", "seed.xstack.lab.validation.universe")),
        universe_id="",
        entitlements=list(fixture_payload.get("entitlements") or []),
        epistemic_scope_id=str(fixture_payload.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(fixture_payload.get("visibility_level", "placeholder")),
        privilege_level=str(fixture_payload.get("privilege_level", "operator")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return created

    session_spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    script_abs = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.region_traversal.fixture.json")
    lock_a = os.path.join(_resolve_root(repo_root, dist_a), "lockfile.json")
    reg_a = os.path.join(_resolve_root(repo_root, dist_a), "registries")
    lock_b = os.path.join(_resolve_root(repo_root, dist_b), "lockfile.json")
    reg_b = os.path.join(_resolve_root(repo_root, dist_b), "registries")

    boot_a = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        bundle_id=str(fixture_payload.get("bundle_id", bundle_id)),
        compile_if_missing=False,
        lockfile_path=lock_a,
        registries_dir=reg_a,
    )
    if boot_a.get("result") != "complete":
        return boot_a
    run_a = run_intent_script(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        script_path=script_abs,
        bundle_id=str(fixture_payload.get("bundle_id", bundle_id)),
        compile_if_missing=False,
        workers=1,
        write_state=False,
        logical_shards=1,
        lockfile_path=lock_a,
        registries_dir=reg_a,
    )
    if run_a.get("result") != "complete":
        return run_a

    boot_b = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        bundle_id=str(fixture_payload.get("bundle_id", bundle_id)),
        compile_if_missing=False,
        lockfile_path=lock_b,
        registries_dir=reg_b,
    )
    if boot_b.get("result") != "complete":
        return boot_b
    run_b = run_intent_script(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        script_path=script_abs,
        bundle_id=str(fixture_payload.get("bundle_id", bundle_id)),
        compile_if_missing=False,
        workers=1,
        write_state=False,
        logical_shards=1,
        lockfile_path=lock_b,
        registries_dir=reg_b,
    )
    if run_b.get("result") != "complete":
        return run_b

    if str(run_a.get("composite_hash", "")) != str(run_b.get("composite_hash", "")):
        return _refused(
            [
                {
                    "code": "REFUSE_LAB_COMPOSITE_HASH_MISMATCH",
                    "message": "composite hash differs across repeated dist launch runs",
                    "path": "$.composite_hash",
                }
            ],
            first=run_a,
            second=run_b,
        )
    if dict(run_a.get("registry_hashes") or {}) != dict(run_b.get("registry_hashes") or {}):
        return _refused(
            [
                {
                    "code": "REFUSE_LAB_REGISTRY_HASH_MISMATCH",
                    "message": "registry hashes differ across repeated dist launch runs",
                    "path": "$.registry_hashes",
                }
            ],
            first=run_a,
            second=run_b,
        )

    return {
        "result": "complete",
        "lab_build_status": "pass",
        "bundle_id": str(bundle_id),
        "dist_a": _repo_relative(repo_root, _resolve_root(repo_root, dist_a)),
        "dist_b": _repo_relative(repo_root, _resolve_root(repo_root, dist_b)),
        "dist_content_hash": str(build_a.get("canonical_content_hash", "")),
        "manifest_hash": str(build_a.get("manifest_hash", "")),
        "composite_hash_anchor": str(run_a.get("composite_hash", "")),
        "pack_lock_hash": str(run_a.get("pack_lock_hash", "")),
        "registry_hashes": dict(run_a.get("registry_hashes") or {}),
        "run_meta_path": str(run_a.get("run_meta_path", "")),
    }
