"""Deterministic DIST-1 portable bundle assembly and audit helpers."""

from __future__ import annotations

import json
import os
import py_compile
import shutil
import subprocess
import sys
from typing import Mapping, Sequence

from src.lib.install import (
    build_product_build_descriptor,
    deterministic_fingerprint as install_deterministic_fingerprint,
    merge_contract_ranges,
    merge_protocol_ranges,
    normalize_install_manifest,
    sha256_file,
    stable_install_id,
    validate_install_manifest,
)
from src.lib.instance import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
    validate_instance_manifest,
)
from src.release import build_release_manifest, verify_release_manifest, write_release_manifest
from tools.lib.content_store import (
    STORE_ROOT_MANIFEST,
    build_install_ref,
    build_store_locator,
    deterministic_fingerprint as store_deterministic_fingerprint,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DEFAULT_RELEASE_CHANNEL = "mock"
DEFAULT_RELEASE_TAG = "v0.0.0-mock"
DEFAULT_PLATFORM_TAG = "win64"
DEFAULT_OUTPUT_ROOT = "dist"
DEFAULT_BUILD_NUMBER_REL = os.path.join("manifests", "build_number.txt")
DEFAULT_RELEASE_MANIFEST_REL = os.path.join("manifests", "release_manifest.json")
DEFAULT_FILELIST_REL = os.path.join("manifests", "filelist.txt")
DEFAULT_INSTALL_MANIFEST_NAME = "install.manifest.json"
DEFAULT_INSTANCE_MANIFEST_REL = os.path.join("instances", "default", "instance.manifest.json")
DEFAULT_PROFILE_BUNDLE_SOURCE = os.path.join("profiles", "bundles", "bundle.mvp_default.json")
DEFAULT_PACK_LOCK_SOURCE = os.path.join("locks", "pack_lock.mvp_default.json")
DEFAULT_COMPAT_DOC_REL = os.path.join("docs", "COMPATIBILITY.md")
DEFAULT_RELEASE_NOTES_REL = os.path.join("docs", "RELEASE_NOTES_v0_0_0_mock.md")
DEFAULT_STORE_ROOT_ID = "store.default"
DEFAULT_INSTANCE_ID = "instance.default"
DEFAULT_INSTANCE_KIND = "instance.client"
DEFAULT_SESSION_TEMPLATE_ID = "session.mvp_default"

PRODUCT_SPECS = (
    {"product_id": "engine", "module": "tools.appshell.product_stub_cli", "callable": "main", "prefix": ["--product-id", "engine", "--"]},
    {"product_id": "game", "module": "tools.appshell.product_stub_cli", "callable": "main", "prefix": ["--product-id", "game", "--"]},
    {"product_id": "client", "module": "tools.mvp.runtime_entry", "callable": "client_main", "prefix": []},
    {"product_id": "server", "module": "tools.mvp.runtime_entry", "callable": "server_main", "prefix": []},
    {"product_id": "setup", "module": "tools.setup.setup_cli", "callable": "main", "prefix": []},
    {"product_id": "launcher", "module": "tools.launcher.launch", "callable": "main", "prefix": []},
)
PRODUCT_IDS = tuple(str(row["product_id"]) for row in PRODUCT_SPECS)

RUNTIME_SOURCE_ROOTS = ("src", "tools")
EXCLUDED_RUNTIME_PREFIXES = (
    "tools/auditx",
    "tools/convergence",
    "tools/dist",
    "tools/release",
    "tools/xstack/auditx",
    "tools/xstack/controlx",
    "tools/xstack/core",
    "tools/xstack/extensions",
    "tools/xstack/performx",
    "tools/xstack/securex",
    "tools/xstack/out",
    "tools/xstack/repox",
    "tools/xstack/testx",
)
EXCLUDED_RUNTIME_BASENAMES = {"__pycache__"}
EXCLUDED_RUNTIME_FILES = {
    "tools/xstack/bundle_list.py",
    "tools/xstack/bundle_validate.py",
    "tools/xstack/run.py",
    "tools/xstack/session_boot.py",
    "tools/xstack/session_control.py",
    "tools/xstack/session_create.py",
    "tools/xstack/session_script_run.py",
    "tools/xstack/session_server.py",
    "tools/xstack/session_surface.py",
    "tools/xstack/srz_status.py",
    "tools/xstack/testx_all.py",
    "tools/xstack/ui_bind.py",
}
EXCLUDED_DIST_MARKERS = (".git", ".pytest_cache", "__pycache__", "tests", "fixtures", "testdata", "tmp")
EXCLUDED_FILE_SUFFIXES = (".py", ".pyi", ".pdb", ".log", ".tmp")
ALLOWED_TOP_LEVEL = {
    "LICENSE",
    "README",
    "bin",
    "data",
    "docs",
    "install.manifest.json",
    "instances",
    "manifests",
    "saves",
    "schema",
    "schemas",
    "src",
    "store",
    "tools",
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_root(repo_root: str) -> str:
    return os.path.normpath(os.path.abspath(_token(repo_root) or "."))


def _bundle_root(output_root: str, platform_tag: str, channel_id: str) -> str:
    root = os.path.normpath(os.path.abspath(_token(output_root) or DEFAULT_OUTPUT_ROOT))
    release_tag = "v0.0.0-{}".format(_token(channel_id) or DEFAULT_RELEASE_CHANNEL)
    return os.path.join(root, release_tag, _token(platform_tag) or DEFAULT_PLATFORM_TAG, "dominium")


def _write_text(path: str, text: str, *, newline: str = "\n") -> str:
    target = os.path.normpath(os.path.abspath(path))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as handle:
        handle.write(str(text or "").replace("\r\n", "\n").replace("\n", newline))
    return target


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    return _write_text(path, canonical_json_text(dict(payload or {})) + "\n")


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("invalid JSON root object: {}".format(_norm(path)))
    return dict(payload)


def _copy_file(src: str, dest: str) -> str:
    source = os.path.normpath(os.path.abspath(src))
    target = os.path.normpath(os.path.abspath(dest))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copyfile(source, target)
    return target


def _copy_json(src: str, dest: str) -> tuple[str, dict]:
    _copy_file(src, dest)
    return dest, _read_json(dest)


def _iter_json_files(root: str) -> list[str]:
    rows: list[str] = []
    base = os.path.normpath(os.path.abspath(root))
    if not os.path.isdir(base):
        return rows
    for current_root, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(name for name in dirnames if name not in EXCLUDED_RUNTIME_BASENAMES)
        for name in sorted(filenames):
            if not name.endswith(".json"):
                continue
            rows.append(os.path.normpath(os.path.abspath(os.path.join(current_root, name))))
    return sorted(rows)


def _source_is_excluded(rel_path: str) -> bool:
    token = _norm(rel_path)
    if token in EXCLUDED_RUNTIME_FILES:
        return True
    if any(token == prefix or token.startswith(prefix + "/") for prefix in EXCLUDED_RUNTIME_PREFIXES):
        return True
    parts = [part for part in token.split("/") if part]
    return any(part in EXCLUDED_RUNTIME_BASENAMES for part in parts)


def _compile_runtime_tree(repo_root: str, bundle_root: str) -> dict:
    source_root = _repo_root(repo_root)
    target_root = os.path.normpath(os.path.abspath(bundle_root))
    helper_path = os.path.join(source_root, "tools", "dist", "runtime_compile_helper.py")
    env_map = dict(os.environ)
    env_map["PYTHONHASHSEED"] = "0"
    proc = subprocess.run(
        [
            sys.executable,
            helper_path,
            "--source-root",
            source_root,
            "--target-root",
            target_root,
            "--roots-json",
            json.dumps(list(RUNTIME_SOURCE_ROOTS)),
            "--excluded-prefixes-json",
            json.dumps(list(EXCLUDED_RUNTIME_PREFIXES)),
            "--excluded-basenames-json",
            json.dumps(sorted(EXCLUDED_RUNTIME_BASENAMES)),
            "--excluded-files-json",
            json.dumps(sorted(EXCLUDED_RUNTIME_FILES)),
        ],
        cwd=source_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env_map,
    )
    if int(proc.returncode) != 0:
        raise RuntimeError("runtime compile helper failed: {}".format(str(proc.stderr or proc.stdout or "").strip()))
    payload = {}
    try:
        payload = json.loads(str(proc.stdout or "").strip() or "{}")
    except ValueError as exc:
        raise RuntimeError("runtime compile helper returned invalid JSON") from exc
    compiled = [
        _norm(item)
        for item in list(payload.get("compiled_files") or [])
        if _norm(item)
    ]
    return {
        "compiled_count": len(compiled),
        "compiled_files": compiled,
        "compiled_hash": canonical_sha256({"compiled_files": compiled}),
    }


def _copy_runtime_data(repo_root: str, bundle_root: str) -> dict:
    repo_root_abs = _repo_root(repo_root)
    copied: list[str] = []
    for rel_path in (
        "data/registries",
        "data/session_templates/session.mvp_default.json",
        "schema",
        "schemas",
        "tools/xstack/compatx/version_registry.json",
    ):
        src_path = os.path.join(repo_root_abs, rel_path.replace("/", os.sep))
        dest_path = os.path.join(bundle_root, rel_path.replace("/", os.sep))
        if os.path.isdir(src_path):
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(
                src_path,
                dest_path,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".gitkeep"),
            )
            for path in _iter_json_files(dest_path):
                copied.append(_norm(os.path.relpath(path, bundle_root)))
            continue
        _copy_file(src_path, dest_path)
        copied.append(_norm(os.path.relpath(dest_path, bundle_root)))
    return {
        "copied_json_count": len(copied),
        "copied_hash": canonical_sha256({"copied": copied}),
    }


def _build_store_manifest_payload() -> dict:
    payload = {
        "store_id": DEFAULT_STORE_ROOT_ID,
        "root_path": ".",
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = store_deterministic_fingerprint(payload)
    return payload


def _alias_pack_payload(alias_row: Mapping[str, object]) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "pack_alias_id": _token(alias_row.get("pack_id")),
        "runtime_version": "0.0.0",
        "distribution_channel": _token(alias_row.get("distribution_channel")),
        "canonical_hash": _token(alias_row.get("canonical_hash")).lower(),
        "source_packs": list(alias_row.get("source_packs") or []),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _write_store_artifacts(repo_root: str, bundle_root: str) -> dict:
    repo_root_abs = _repo_root(repo_root)
    store_root = os.path.join(bundle_root, "store")
    os.makedirs(store_root, exist_ok=True)
    for rel_dir in ("packs", "profiles", "locks", "bundles"):
        os.makedirs(os.path.join(store_root, rel_dir.replace("/", os.sep)), exist_ok=True)
    store_manifest = _build_store_manifest_payload()
    _write_json(os.path.join(store_root, STORE_ROOT_MANIFEST), store_manifest)

    pack_lock_dest, pack_lock_payload = _copy_json(
        os.path.join(repo_root_abs, DEFAULT_PACK_LOCK_SOURCE.replace("/", os.sep)),
        os.path.join(bundle_root, "store", "locks", "pack_lock.mvp_default.json"),
    )
    profile_dest, profile_payload = _copy_json(
        os.path.join(repo_root_abs, DEFAULT_PROFILE_BUNDLE_SOURCE.replace("/", os.sep)),
        os.path.join(bundle_root, "store", "profiles", "bundles", "bundle.mvp_default.json"),
    )
    copied_pack_paths: list[str] = []
    for row in list(pack_lock_payload.get("ordered_packs") or []):
        alias_row = dict(row or {})
        rel_dir = _norm("store/" + _token(alias_row.get("distribution_rel")))
        alias_path = os.path.join(bundle_root, rel_dir.replace("/", os.sep), "pack.alias.json")
        _write_json(alias_path, _alias_pack_payload(alias_row))
        copied_pack_paths.append(_norm(os.path.relpath(alias_path, bundle_root)))

    return {
        "store_root": _norm(os.path.relpath(store_root, bundle_root)),
        "store_manifest": store_manifest,
        "pack_lock_path": _norm(os.path.relpath(pack_lock_dest, bundle_root)),
        "pack_lock_payload": pack_lock_payload,
        "profile_bundle_path": _norm(os.path.relpath(profile_dest, bundle_root)),
        "profile_bundle_payload": profile_payload,
        "pack_paths": sorted(copied_pack_paths),
    }


def _read_build_number(repo_root: str) -> str:
    path = os.path.join(_repo_root(repo_root), ".dominium_build_number")
    if not os.path.isfile(path):
        return "0"
    with open(path, "r", encoding="utf-8") as handle:
        token = str(handle.read()).strip()
    return token or "0"


def _wrapper_script_text(product_spec: Mapping[str, object]) -> str:
    product_id = _token(product_spec.get("product_id"))
    module_name = _token(product_spec.get("module"))
    callable_name = _token(product_spec.get("callable"))
    prefix = list(product_spec.get("prefix") or [])
    prefix_literal = repr([str(item) for item in prefix])
    setup_alias = "True" if product_id == "setup" else "False"
    runtime_defaults = "True" if product_id in {"client", "server"} else "False"
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import importlib",
            "import os",
            "import sys",
            "",
            "BUNDLE_ROOT = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))",
            "PORTABLE_EXECUTABLE_PATH = os.path.join(BUNDLE_ROOT, {!r})".format(product_id),
            "PRODUCT_ID = {!r}".format(product_id),
            "if BUNDLE_ROOT not in sys.path:",
            "    sys.path.insert(0, BUNDLE_ROOT)",
            "sys.argv[0] = PORTABLE_EXECUTABLE_PATH",
            "BUILD_FILE = os.path.join(BUNDLE_ROOT, 'manifests', 'build_number.txt')",
            "if 'DOMINIUM_FIXED_BUILD_NUMBER' not in os.environ and os.path.isfile(BUILD_FILE):",
            "    with open(BUILD_FILE, 'r', encoding='utf-8') as handle:",
            "        token = str(handle.read()).strip()",
            "    if token:",
            "        os.environ['DOMINIUM_FIXED_BUILD_NUMBER'] = token",
            "",
            "def _has_flag(argv: list[str], *flags: str) -> bool:",
            "    targets = {str(flag).strip() for flag in flags if str(flag).strip()}",
            "    return any(str(token).strip() in targets for token in list(argv or []))",
            "",
            "def _value_after(argv: list[str], *flags: str) -> str:",
            "    values = list(argv or [])",
            "    targets = {str(flag).strip() for flag in flags if str(flag).strip()}",
            "    for index, token in enumerate(values):",
            "        if str(token).strip() not in targets:",
            "            continue",
            "        if index + 1 >= len(values):",
            "            return ''",
            "        return str(values[index + 1]).strip()",
            "    return ''",
            "",
            "def _translate_setup_aliases(argv: list[str]) -> list[str]:",
            "    values = list(argv or [])",
            "    if len(values) >= 2 and values[0] == 'packs' and values[1] == 'verify':",
            "        return ['verify'] + values[2:]",
            "    return values",
            "",
            "ROOT_COMMAND_IDS = {'help', 'version', 'descriptor', 'compat-status', 'profiles', 'packs', 'verify', 'diag', 'console'}",
            "",
            "def _has_root_command(argv: list[str]) -> bool:",
            "    for token in list(argv or []):",
            "        value = str(token).strip()",
            "        if not value or value.startswith('-'):",
            "            continue",
            "        return value in ROOT_COMMAND_IDS",
            "    return False",
            "",
            "def _inject_setup_root(argv: list[str]) -> list[str]:",
            "    values = list(argv or [])",
            "    if not values:",
            "        return values",
            "    if _has_flag(values, '--root', '--install-root', '--release-manifest'):",
            "        return values",
            "    if values[0] not in {'verify', 'list-packs', 'build-lock', 'diagnose-pack'}:",
            "        return values",
            "    return [values[0], '--root', BUNDLE_ROOT] + values[1:]",
            "",
            "def _inject_defaults(argv: list[str]) -> list[str]:",
            "    values = list(argv or [])",
            "    if {}:".format(setup_alias),
            "        values = _translate_setup_aliases(values)",
            "        values = _inject_setup_root(values)",
            "    prefix = []",
            "    if {}:".format(runtime_defaults),
            "        if _has_root_command(values):",
            "            return values",
            "        if not _has_flag(values, '--profile_bundle', '--profile-bundle'):",
            "            prefix.extend(['--profile_bundle', os.path.join(BUNDLE_ROOT, 'store', 'profiles', 'bundles', 'bundle.mvp_default.json')])",
            "        if not _has_flag(values, '--pack_lock', '--pack-lock'):",
            "            prefix.extend(['--pack_lock', os.path.join(BUNDLE_ROOT, 'store', 'locks', 'pack_lock.mvp_default.json')])",
            "    return prefix + values",
            "",
            "def _emit_descriptor(values: list[str]) -> int:",
            "    from src.compat import descriptor_json_text, emit_product_descriptor",
            "    from src.platform.platform_probe import probe_platform_descriptor",
            "",
            "    descriptor_file = _value_after(values, '--descriptor-file')",
            "    platform_probe = probe_platform_descriptor(",
            "        BUNDLE_ROOT,",
            "        product_id=PRODUCT_ID,",
            "        stdin_tty=True,",
            "        stdout_tty=False,",
            "        stderr_tty=False,",
            "    )",
            "    emitted = emit_product_descriptor(",
            "        BUNDLE_ROOT,",
            "        product_id=PRODUCT_ID,",
            "        descriptor_file=descriptor_file,",
            "        platform_descriptor_override=platform_probe,",
            "    )",
            "    sys.stdout.write(descriptor_json_text(dict(emitted.get('descriptor') or {})))",
            "    sys.stdout.write('\\n')",
            "    return 0",
            "",
            "def main(argv: list[str] | None = None) -> int:",
            "    values = _inject_defaults(list(sys.argv[1:] if argv is None else argv))",
            "    if _has_flag(values, '--descriptor', '--descriptor-file'):",
            "        return _emit_descriptor(values)",
            "    module = importlib.import_module({!r})".format(module_name),
            "    entrypoint = getattr(module, {!r})".format(callable_name),
            "    delegate = list({}) + values".format(prefix_literal),
            "    return int(entrypoint(delegate))",
            "",
            "if __name__ == '__main__':",
            "    raise SystemExit(main())",
            "",
        ]
    )


def _wrapper_cmd_text(product_id: str) -> str:
    return "@echo off\r\npython \"%~dp0{}\" %*\r\n".format(_token(product_id))


def _write_product_wrappers(bundle_root: str) -> dict:
    product_rows: list[dict[str, str]] = []
    for spec in PRODUCT_SPECS:
        product_id = _token(spec.get("product_id"))
        script_path = _write_text(os.path.join(bundle_root, "bin", product_id), _wrapper_script_text(spec))
        cmd_path = _write_text(os.path.join(bundle_root, "bin", product_id + ".cmd"), _wrapper_cmd_text(product_id), newline="")
        product_rows.append(
            {
                "product_id": product_id,
                "script_path": _norm(os.path.relpath(script_path, bundle_root)),
                "cmd_path": _norm(os.path.relpath(cmd_path, bundle_root)),
            }
        )
    return {"products": product_rows}


def _run_wrapper(bundle_root: str, product_id: str, args: Sequence[str]) -> dict:
    wrapper_path = os.path.join(bundle_root, "bin", _token(product_id))
    proc = subprocess.run(
        [sys.executable, wrapper_path] + [str(item) for item in list(args or [])],
        cwd=bundle_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    stdout = str(proc.stdout or "").strip()
    stderr = str(proc.stderr or "").strip()
    payload = {}
    if stdout:
        try:
            parsed = json.loads(stdout)
        except ValueError:
            parsed = {}
        if isinstance(parsed, dict):
            payload = dict(parsed)
    return {
        "returncode": int(proc.returncode or 0),
        "stdout": stdout,
        "stderr": stderr,
        "payload": payload,
    }


def _build_install_manifest(bundle_root: str, repo_root: str, platform_tag: str) -> dict:
    descriptors: dict[str, dict] = {}
    descriptor_hashes: dict[str, str] = {}
    binary_hashes: dict[str, str] = {}
    product_builds: dict[str, str] = {}
    product_build_descriptors: dict[str, dict] = {}
    protocol_rows: list[dict] = []
    contract_rows: list[dict] = []
    for product_id in PRODUCT_IDS:
        result = _run_wrapper(bundle_root, product_id, ["--descriptor"])
        payload = dict(result.get("payload") or {})
        descriptor = dict(payload.get("descriptor") or payload)
        if int(result.get("returncode", 0)) != 0 or _token(descriptor.get("product_id")) != product_id:
            raise RuntimeError("descriptor emission failed for '{}'".format(product_id))
        descriptor_hash = canonical_sha256(descriptor)
        descriptor_rel = _norm(os.path.join("bin", "{}.descriptor.json".format(product_id)))
        _write_json(os.path.join(bundle_root, descriptor_rel.replace("/", os.sep)), descriptor)
        binary_rel = _norm(os.path.join("bin", product_id))
        build_id = _token((dict(descriptor.get("extensions") or {})).get("official.build_id"))
        descriptors[product_id] = descriptor
        descriptor_hashes[product_id] = descriptor_hash
        binary_hashes[product_id] = sha256_file(os.path.join(bundle_root, binary_rel.replace("/", os.sep)))
        product_builds[product_id] = build_id
        product_build_descriptors[product_id] = build_product_build_descriptor(
            product_id=product_id,
            build_id=build_id,
            binary_hash=binary_hashes[product_id],
            endpoint_descriptor_hash=descriptor_hash,
            binary_ref=binary_rel,
            descriptor_ref=descriptor_rel,
            product_version=_token(descriptor.get("product_version")),
        )
        protocol_rows.extend(list(descriptor.get("protocol_versions_supported") or []))
        contract_rows.extend(list(descriptor.get("semantic_contract_versions_supported") or []))

    semantic_registry_path = os.path.join(bundle_root, "data", "registries", "semantic_contract_registry.json")
    semantic_registry_hash = canonical_sha256(_read_json(semantic_registry_path))
    install_id = stable_install_id(
        {
            "channel_id": DEFAULT_RELEASE_CHANNEL,
            "platform_tag": _token(platform_tag),
            "product_builds": product_builds,
            "semantic_contract_registry_hash": semantic_registry_hash,
        }
    )
    payload = {
        "install_id": install_id,
        "install_version": "0.0.0",
        "product_builds": dict((key, product_builds[key]) for key in sorted(product_builds.keys())),
        "product_build_ids": dict((key, product_builds[key]) for key in sorted(product_builds.keys())),
        "semantic_contract_registry_hash": semantic_registry_hash,
        "supported_protocol_versions": merge_protocol_ranges(protocol_rows),
        "supported_contract_ranges": merge_contract_ranges(contract_rows),
        "default_mod_policy_id": "mod_policy.lab",
        "store_root_ref": {
            "store_id": DEFAULT_STORE_ROOT_ID,
            "root_path": "store",
            "manifest_ref": "store/store.root.json",
        },
        "mode": "portable",
        "install_root": ".",
        "product_build_descriptors": dict(
            (key, product_build_descriptors[key]) for key in sorted(product_build_descriptors.keys())
        ),
        "extensions": {
            "official.semantic_contract_registry_ref": "data/registries/semantic_contract_registry.json",
        },
        "deterministic_fingerprint": "",
    }
    payload = normalize_install_manifest(payload)
    payload["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = install_deterministic_fingerprint(payload)
    install_manifest_path = os.path.join(bundle_root, DEFAULT_INSTALL_MANIFEST_NAME)
    _write_json(install_manifest_path, payload)
    validation = validate_install_manifest(
        repo_root=bundle_root,
        install_manifest_path=install_manifest_path,
        manifest_payload=payload,
    )
    if _token(validation.get("result")) != "complete":
        raise RuntimeError("install manifest validation failed")
    return {
        "install_manifest_path": _norm(os.path.relpath(install_manifest_path, bundle_root)),
        "install_manifest": payload,
        "descriptors": descriptors,
    }


def _write_default_instance_manifest(bundle_root: str, install_manifest: Mapping[str, object], store_manifest: Mapping[str, object]) -> dict:
    instance_root = os.path.join(bundle_root, "instances", "default")
    os.makedirs(instance_root, exist_ok=True)
    pack_lock_payload = _read_json(os.path.join(bundle_root, "store", "locks", "pack_lock.mvp_default.json"))
    profile_bundle_payload = _read_json(os.path.join(bundle_root, "store", "profiles", "bundles", "bundle.mvp_default.json"))
    install_manifest_path = os.path.join(bundle_root, DEFAULT_INSTALL_MANIFEST_NAME)
    instance_payload = {
        "instance_id": DEFAULT_INSTANCE_ID,
        "instance_kind": DEFAULT_INSTANCE_KIND,
        "mode": "linked",
        "install_ref": build_install_ref(instance_root, install_manifest_path, dict(install_manifest or {})),
        "embedded_builds": {},
        "pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
        "profile_bundle_hash": _token(profile_bundle_payload.get("profile_bundle_hash")),
        "mod_policy_id": _token(pack_lock_payload.get("mod_policy_id")) or "mod_policy.lab",
        "overlay_conflict_policy_id": _token(pack_lock_payload.get("overlay_conflict_policy_id")) or "overlay.conflict.last_wins",
        "default_session_template_id": DEFAULT_SESSION_TEMPLATE_ID,
        "seed_policy": "prompt",
        "instance_settings": {
            "data_root": ".",
            "active_profiles": ["profile.bundle.mvp_default"],
            "active_modpacks": [],
            "sandbox_policy_ref": "sandbox.default",
            "update_channel": "mock",
            "renderer_mode": "",
            "ui_mode_default": "rendered",
            "allow_read_only_fallback": False,
            "tick_budget_policy_id": "tick.budget.default",
            "compute_profile_id": "compute.profile.default",
            "extensions": {},
        },
        "save_refs": [],
        "required_product_builds": dict((key, _token(value)) for key, value in sorted(dict(install_manifest.get("product_builds") or {}).items())),
        "required_contract_ranges": dict((key, dict(value)) for key, value in sorted(dict(install_manifest.get("supported_contract_ranges") or {}).items())),
        "resolution_policy_id": "",
        "provides_resolutions": [],
        "store_root": build_store_locator(instance_root, os.path.join(bundle_root, "store"), dict(store_manifest or {})),
        "embedded_artifacts": [],
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    instance_payload = normalize_instance_manifest(instance_payload)
    instance_payload["deterministic_fingerprint"] = ""
    instance_payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(instance_payload)
    manifest_path = os.path.join(instance_root, "instance.manifest.json")
    _write_json(manifest_path, instance_payload)
    validation = validate_instance_manifest(
        repo_root=bundle_root,
        instance_manifest_path=manifest_path,
        manifest_payload=instance_payload,
    )
    if _token(validation.get("result")) != "complete":
        raise RuntimeError("instance manifest validation failed")
    return {
        "instance_manifest_path": _norm(os.path.relpath(manifest_path, bundle_root)),
        "instance_manifest": instance_payload,
    }


def _write_bundle_docs(repo_root: str, bundle_root: str, pack_lock_payload: Mapping[str, object]) -> dict:
    included_packs = [_token(row.get("pack_id")) for row in list(pack_lock_payload.get("ordered_packs") or []) if _token(row.get("pack_id"))]
    readme_text = "\n".join(
        [
            "Dominium v0.0.0-mock portable bundle",
            "",
            "Products:",
            "  client",
            "  server",
            "  setup",
            "  launcher",
            "  engine",
            "  game",
            "",
            "Offline verification:",
            "  python bin/setup packs verify",
            "  python bin/setup verify --release-manifest manifests/release_manifest.json",
            "",
            "Default store content:",
        ]
        + ["  {}".format(pack_id) for pack_id in included_packs]
        + [
            "",
            "This bundle is portable. Launching binaries from bin/ uses bundled wrapper defaults for repo-root and install-root.",
            "",
        ]
    )
    compat_text = "\n".join(
        [
            "# Compatibility Instructions",
            "",
            "- Use `python bin/setup verify --release-manifest manifests/release_manifest.json` for offline bundle verification.",
            "- Use `python bin/launcher compat-status` to inspect negotiated compatibility and the bundled release identity.",
            "- Mix-and-match interoperability remains governed by CAP-NEG; identical versions are not assumed.",
            "",
        ]
    )
    release_notes_text = "\n".join(
        [
            "# Dominium v0.0.0-mock",
            "",
            "Included:",
            "- deterministic AppShell entrypoints",
            "- portable install discovery and virtual paths",
            "- offline pack verification and release manifest verification",
            "- default linked instance and base universe pack lock",
            "",
            "Out of scope:",
            "- installers",
            "- signing enforcement",
            "- real fluid simulation",
            "- chemistry and economy systems",
            "",
        ]
    )
    _copy_file(os.path.join(_repo_root(repo_root), "LICENSE.md"), os.path.join(bundle_root, "LICENSE"))
    _write_text(os.path.join(bundle_root, "README"), readme_text)
    _write_text(os.path.join(bundle_root, DEFAULT_COMPAT_DOC_REL.replace("/", os.sep)), compat_text)
    _write_text(os.path.join(bundle_root, DEFAULT_RELEASE_NOTES_REL.replace("/", os.sep)), release_notes_text)
    return {
        "docs": [
            "README",
            "LICENSE",
            _norm(DEFAULT_COMPAT_DOC_REL),
            _norm(DEFAULT_RELEASE_NOTES_REL),
        ]
    }


def _iter_bundle_files(bundle_root: str, *, exclude_paths: Sequence[str] | None = None) -> list[str]:
    root = os.path.normpath(os.path.abspath(bundle_root))
    excluded = {_norm(path) for path in list(exclude_paths or []) if _token(path)}
    rows: list[str] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(dirnames)
        rel_root = os.path.relpath(current_root, root)
        rel_root_norm = "" if rel_root in (".", "") else _norm(rel_root)
        for name in sorted(filenames):
            rel_path = name if not rel_root_norm else "{}/{}".format(rel_root_norm, name)
            rel_norm = _norm(rel_path)
            if rel_norm in excluded:
                continue
            rows.append(rel_norm)
    return sorted(rows)


def _write_filelist(bundle_root: str, *, exclude_paths: Sequence[str] | None = None) -> dict:
    file_rows = _iter_bundle_files(bundle_root, exclude_paths=exclude_paths)
    lines = ["{}  {}".format(sha256_file(os.path.join(bundle_root, rel_path.replace("/", os.sep))), rel_path) for rel_path in file_rows]
    target = os.path.join(bundle_root, DEFAULT_FILELIST_REL.replace("/", os.sep))
    _write_text(target, "\n".join(lines) + ("\n" if lines else ""))
    return {
        "file_count": len(file_rows),
        "file_list_path": _norm(os.path.relpath(target, bundle_root)),
        "file_hash": canonical_sha256({"files": [{"path": rel_path, "sha256": lines[index].split("  ", 1)[0]} for index, rel_path in enumerate(file_rows)]}),
    }


def _run_smoke_checks(bundle_root: str) -> dict:
    checks = (
        ("client_descriptor", "client", ["--descriptor"], "descriptor"),
        ("server_descriptor", "server", ["--descriptor"], "descriptor"),
        ("setup_packs_verify", "setup", ["packs", "verify"], "complete"),
        ("launcher_instances_list", "launcher", ["instances", "list"], "complete"),
        ("launcher_compat_status", "launcher", ["compat-status"], "complete"),
    )
    rows: list[dict[str, object]] = []
    for check_id, product_id, argv, expected_result in checks:
        result = _run_wrapper(bundle_root, product_id, argv)
        payload = dict(result.get("payload") or {})
        row = {
            "check_id": check_id,
            "product_id": product_id,
            "argv": list(argv),
            "returncode": int(result.get("returncode", 0)),
            "result": _token(payload.get("result")),
            "stderr": _token(result.get("stderr")),
        }
        if row["returncode"] != 0:
            raise RuntimeError("smoke check '{}' failed with returncode {}".format(check_id, row["returncode"]))
        if expected_result == "descriptor":
            if _token(payload.get("product_id")) != product_id:
                raise RuntimeError("descriptor smoke check '{}' did not emit product descriptor".format(check_id))
        elif row["result"] != expected_result:
            raise RuntimeError("smoke check '{}' returned '{}'".format(check_id, row["result"]))
        rows.append(row)
    return {
        "smoke_checks": rows,
        "smoke_hash": canonical_sha256({"smoke_checks": rows}),
    }


def _build_top_level_summary(bundle_root: str) -> dict:
    entries = sorted(os.listdir(bundle_root))
    return {
        "top_level_entries": entries,
        "top_level_hash": canonical_sha256({"entries": entries}),
    }


def build_dist_tree(
    repo_root: str,
    *,
    platform_tag: str = DEFAULT_PLATFORM_TAG,
    channel_id: str = DEFAULT_RELEASE_CHANNEL,
    output_root: str = DEFAULT_OUTPUT_ROOT,
) -> dict:
    repo_root_abs = _repo_root(repo_root)
    bundle_root = _bundle_root(output_root, platform_tag, channel_id)
    if os.path.isdir(bundle_root):
        shutil.rmtree(bundle_root)
    os.makedirs(os.path.join(bundle_root, "manifests"), exist_ok=True)
    os.makedirs(os.path.join(bundle_root, "instances", "default"), exist_ok=True)
    os.makedirs(os.path.join(bundle_root, "saves"), exist_ok=True)
    build_number = _read_build_number(repo_root_abs)
    _write_text(os.path.join(bundle_root, DEFAULT_BUILD_NUMBER_REL.replace("/", os.sep)), build_number + "\n")

    runtime_row = _compile_runtime_tree(repo_root_abs, bundle_root)
    runtime_data_row = _copy_runtime_data(repo_root_abs, bundle_root)
    wrapper_row = _write_product_wrappers(bundle_root)
    store_row = _write_store_artifacts(repo_root_abs, bundle_root)
    install_row = _build_install_manifest(bundle_root, repo_root_abs, platform_tag)
    install_payload = dict(install_row.get("install_manifest") or {})
    install_manifest_path = os.path.join(bundle_root, DEFAULT_INSTALL_MANIFEST_NAME)
    _copy_file(install_manifest_path, os.path.join(bundle_root, "manifests", DEFAULT_INSTALL_MANIFEST_NAME))
    instance_row = _write_default_instance_manifest(bundle_root, install_payload, dict(store_row.get("store_manifest") or {}))
    docs_row = _write_bundle_docs(repo_root_abs, bundle_root, dict(store_row.get("pack_lock_payload") or {}))
    filelist_row = _write_filelist(
        bundle_root,
        exclude_paths=(
            DEFAULT_FILELIST_REL,
            DEFAULT_RELEASE_MANIFEST_REL,
        ),
    )
    manifest_payload = build_release_manifest(
        bundle_root,
        platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
        channel_id=_token(channel_id) or DEFAULT_RELEASE_CHANNEL,
        repo_root=repo_root_abs,
        verify_build_ids=True,
    )
    release_manifest_path = write_release_manifest(bundle_root, manifest_payload, manifest_path=os.path.join(bundle_root, DEFAULT_RELEASE_MANIFEST_REL.replace("/", os.sep)))
    verify_row = verify_release_manifest(bundle_root, release_manifest_path, repo_root=repo_root_abs)
    if _token(verify_row.get("result")) != "complete":
        raise RuntimeError("release manifest verification failed")
    smoke_row = _run_smoke_checks(bundle_root)
    rel_files = _iter_bundle_files(bundle_root)
    report = {
        "report_id": "dist.tree.assembly.v1",
        "result": "complete",
        "release_tag": "v0.0.0-{}".format(_token(channel_id) or DEFAULT_RELEASE_CHANNEL),
        "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "channel_id": _token(channel_id) or DEFAULT_RELEASE_CHANNEL,
        "bundle_root": _norm(os.path.relpath(bundle_root, repo_root_abs)),
        "bundle_root_abs": bundle_root,
        "build_number": build_number,
        "runtime": runtime_row,
        "runtime_data": runtime_data_row,
        "wrappers": wrapper_row,
        "store": {
            "pack_paths": list(store_row.get("pack_paths") or []),
            "profile_bundle_path": _token(store_row.get("profile_bundle_path")),
            "pack_lock_path": _token(store_row.get("pack_lock_path")),
        },
        "install_manifest_path": _token(install_row.get("install_manifest_path")),
        "instance_manifest_path": _token(instance_row.get("instance_manifest_path")),
        "docs": list(docs_row.get("docs") or []),
        "filelist": filelist_row,
        "release_manifest_path": _norm(os.path.relpath(release_manifest_path, bundle_root)),
        "release_manifest_hash": _token(manifest_payload.get("manifest_hash")).lower(),
        "smoke": smoke_row,
        "top_level": _build_top_level_summary(bundle_root),
        "file_count": len(rel_files),
        "bundle_hash": canonical_sha256(
            {
                "files": [
                    {
                        "path": rel_path,
                        "sha256": sha256_file(os.path.join(bundle_root, rel_path.replace("/", os.sep))),
                    }
                    for rel_path in rel_files
                ]
            }
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, bundle_root_abs="", deterministic_fingerprint=""))
    return report


def build_dist_minimize_report(bundle_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(bundle_root))
    pack_lock_payload = _read_json(os.path.join(root, "store", "locks", "pack_lock.mvp_default.json"))
    expected_packs = sorted(
        _norm("store/" + _token(row.get("distribution_rel")))
        for row in list(pack_lock_payload.get("ordered_packs") or [])
        if _token(row.get("distribution_rel"))
    )
    actual_packs = sorted(
        _norm(os.path.relpath(os.path.dirname(path), root))
        for path in _iter_json_files(os.path.join(root, "store", "packs"))
        if os.path.basename(path) == "pack.alias.json"
    )
    unexpected_top_level = sorted(name for name in os.listdir(root) if name not in ALLOWED_TOP_LEVEL)
    dev_artifacts = sorted(
        rel_path
        for rel_path in _iter_bundle_files(root)
        if any(part in EXCLUDED_DIST_MARKERS for part in rel_path.split("/")) or rel_path.endswith(EXCLUDED_FILE_SUFFIXES)
    )
    large_files = []
    for rel_path in _iter_bundle_files(root):
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        size = os.path.getsize(abs_path)
        if size >= 1024 * 1024:
            large_files.append({"path": rel_path, "size_bytes": int(size)})
    report = {
        "report_id": "dist.content.audit.v1",
        "result": "complete",
        "bundle_root": _norm(root),
        "expected_packs": expected_packs,
        "actual_packs": actual_packs,
        "unexpected_pack_paths": sorted(set(actual_packs) - set(expected_packs)),
        "missing_pack_paths": sorted(set(expected_packs) - set(actual_packs)),
        "profile_paths": sorted(
            rel_path for rel_path in _iter_bundle_files(root) if rel_path.startswith("store/profiles/")
        ),
        "lock_paths": sorted(
            rel_path for rel_path in _iter_bundle_files(root) if rel_path.startswith("store/locks/")
        ),
        "unexpected_top_level": unexpected_top_level,
        "dev_artifacts": dev_artifacts,
        "large_files": sorted(large_files, key=lambda row: (_token(row.get("path")), int(row.get("size_bytes", 0)))),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_dist_content_audit(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-2 artifact integrity verification and installer-free packaging hardening",
        "",
        "# Distribution Content Audit",
        "",
        "## Included Packs",
        "",
    ]
    for rel_path in list(report.get("actual_packs") or []):
        lines.append("- `{}`".format(_token(rel_path)))
    lines.extend(
        [
            "",
            "## Layout Findings",
            "",
            "- Unexpected top-level entries: `{}`".format(", ".join(list(report.get("unexpected_top_level") or [])) or "none"),
            "- Dev artifacts: `{}`".format(", ".join(list(report.get("dev_artifacts") or [])) or "none"),
            "- Missing required packs: `{}`".format(", ".join(list(report.get("missing_pack_paths") or [])) or "none"),
            "- Unexpected extra packs: `{}`".format(", ".join(list(report.get("unexpected_pack_paths") or [])) or "none"),
            "",
            "## Large Files",
            "",
        ]
    )
    large_files = list(report.get("large_files") or [])
    if not large_files:
        lines.append("- none")
    else:
        for row in large_files:
            lines.append("- `{}`: {} bytes".format(_token(dict(row or {}).get("path")), int(dict(row or {}).get("size_bytes", 0))))
    return "\n".join(lines) + "\n"


def render_dist_final_report(assembly_report: Mapping[str, object], audit_report: Mapping[str, object]) -> str:
    pack_paths = list(dict(assembly_report or {}).get("store", {}).get("pack_paths") or [])
    docs = list(dict(assembly_report or {}).get("docs") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-2 artifact integrity verification and DIST-3 installer constitution",
        "",
        "# Dist Tree Assembly Final",
        "",
        "## Platform Tags Built",
        "",
        "- `{}`".format(_token(assembly_report.get("platform_tag"))),
        "",
        "## Included Packs and Profiles",
        "",
    ]
    for rel_path in pack_paths:
        lines.append("- `{}`".format(_token(rel_path)))
    lines.extend(
        [
            "- `{}`".format(_token(dict(assembly_report.get("store") or {}).get("profile_bundle_path"))),
            "- `{}`".format(_token(dict(assembly_report.get("store") or {}).get("pack_lock_path"))),
            "",
            "## File Counts and Hashes",
            "",
            "- Bundle file count: `{}`".format(int(assembly_report.get("file_count", 0))),
            "- Bundle hash: `{}`".format(_token(assembly_report.get("bundle_hash"))),
            "- File list hash: `{}`".format(_token(dict(assembly_report.get("filelist") or {}).get("file_hash"))),
            "- Release manifest hash: `{}`".format(_token(assembly_report.get("release_manifest_hash"))),
            "- Smoke hash: `{}`".format(_token(dict(assembly_report.get("smoke") or {}).get("smoke_hash"))),
            "",
            "## Included Docs",
            "",
        ]
    )
    for rel_path in docs:
        lines.append("- `{}`".format(_token(rel_path)))
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "- DIST-2 artifact integrity verification: ready",
            "- Unexpected top-level entries: `{}`".format(", ".join(list(audit_report.get("unexpected_top_level") or [])) or "none"),
            "- Dev artifacts: `{}`".format(", ".join(list(audit_report.get("dev_artifacts") or [])) or "none"),
            "- Missing required packs: `{}`".format(", ".join(list(audit_report.get("missing_pack_paths") or [])) or "none"),
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def dist_tree_violations(repo_root: str) -> list[dict]:
    repo_root_abs = _repo_root(repo_root)
    bundle_root = _bundle_root(DEFAULT_OUTPUT_ROOT, DEFAULT_PLATFORM_TAG, DEFAULT_RELEASE_CHANNEL)
    violations: list[dict] = []
    if not os.path.isdir(bundle_root):
        return [
            {
                "code": "dist_tree_missing",
                "file_path": _norm(os.path.relpath(bundle_root, repo_root_abs)),
                "message": "deterministic DIST-1 bundle root is missing",
                "rule_id": "INV-DIST-TREE-DETERMINISTIC",
            }
        ]
    audit = build_dist_minimize_report(bundle_root)
    for rel_path in list(audit.get("dev_artifacts") or []):
        violations.append(
            {
                "code": "dist_tree_dev_artifact_present",
                "file_path": rel_path,
                "message": "development artifact present in assembled distribution tree",
                "rule_id": "INV-DIST-EXCLUSION-LIST-ENFORCED",
            }
        )
    for rel_path in list(audit.get("unexpected_top_level") or []):
        violations.append(
            {
                "code": "dist_tree_unexpected_top_level",
                "file_path": rel_path,
                "message": "unexpected top-level entry present in assembled distribution tree",
                "rule_id": "INV-DIST-EXCLUSION-LIST-ENFORCED",
            }
        )
    for rel_path in list(audit.get("missing_pack_paths") or []):
        violations.append(
            {
                "code": "dist_tree_missing_required_pack",
                "file_path": rel_path,
                "message": "required pack referenced by the default pack lock is missing from the assembled distribution tree",
                "rule_id": "INV-DIST-TREE-DETERMINISTIC",
            }
        )
    report_path = os.path.join(bundle_root, DEFAULT_FILELIST_REL.replace("/", os.sep))
    if os.path.isfile(report_path):
        lines = [line.strip() for line in open(report_path, "r", encoding="utf-8").read().splitlines() if line.strip()]
        paths = [line.split("  ", 1)[1] for line in lines if "  " in line]
        if paths != sorted(paths):
            violations.append(
                {
                    "code": "dist_tree_file_order_non_deterministic",
                    "file_path": _norm(os.path.relpath(report_path, repo_root_abs)),
                    "message": "distribution file list is not sorted deterministically",
                    "rule_id": "INV-DIST-TREE-DETERMINISTIC",
                }
            )
    else:
        violations.append(
            {
                "code": "dist_tree_filelist_missing",
                "file_path": _norm(os.path.relpath(os.path.join(bundle_root, DEFAULT_FILELIST_REL.replace("/", os.sep)), repo_root_abs)),
                "message": "distribution file list is missing",
                "rule_id": "INV-DIST-TREE-DETERMINISTIC",
            }
        )
    return violations


__all__ = [
    "DEFAULT_OUTPUT_ROOT",
    "DEFAULT_PLATFORM_TAG",
    "DEFAULT_RELEASE_CHANNEL",
    "build_dist_tree",
    "build_dist_minimize_report",
    "dist_tree_violations",
    "render_dist_content_audit",
    "render_dist_final_report",
]
