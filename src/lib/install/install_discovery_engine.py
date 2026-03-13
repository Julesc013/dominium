"""Deterministic install discovery for portable and installed Dominium products."""

from __future__ import annotations

import json
import os
import sys
from typing import Iterable, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


INSTALL_MANIFEST_NAME = "install.manifest.json"
INSTALL_REGISTRY_NAME = "install_registry.json"
ENV_INSTALL_ROOT = "DOMINIUM_INSTALL_ROOT"
ENV_INSTALL_ID = "DOMINIUM_INSTALL_ID"
REFUSAL_INSTALL_NOT_FOUND = "refusal.install.not_found"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _value_after(args: Iterable[object], *flags: str) -> str:
    values = [str(item) for item in list(args or [])]
    targets = {str(flag).strip() for flag in flags if str(flag).strip()}
    for index, token in enumerate(values):
        if str(token).strip() not in targets:
            continue
        if index + 1 >= len(values):
            return ""
        return _token(values[index + 1])
    return ""


def _resolve_path(base_root: str, raw_path: str) -> str:
    token = _token(raw_path)
    if not token:
        return ""
    if os.path.isabs(token):
        return _norm(token)
    return _norm(os.path.join(base_root, token.replace("/", os.sep)))


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _load_install_manifest(install_root: str) -> tuple[dict, str, str]:
    manifest_path = os.path.join(_norm(install_root), INSTALL_MANIFEST_NAME)
    if not os.path.isfile(manifest_path):
        return {}, _norm(manifest_path), "missing"
    payload, error = _read_json(manifest_path)
    if error:
        return {}, _norm(manifest_path), error
    return payload, _norm(manifest_path), ""


def _platform_family(platform_id: str = "") -> str:
    token = _token(platform_id)
    if token:
        if token.startswith("platform.win"):
            return "windows"
        if "macos" in token:
            return "macos"
        return "posix"
    if os.name == "nt":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "posix"


def install_registry_candidate_paths(
    *,
    executable_path: str = "",
    cwd: str = "",
    env: Mapping[str, object] | None = None,
    platform_id: str = "",
    explicit_registry_path: str = "",
) -> list[str]:
    environment = {str(key): _token(value) for key, value in dict(env or os.environ).items()}
    base_root = _norm(cwd or os.getcwd())
    ordered: list[str] = []

    for token in (_token(explicit_registry_path),):
        if token:
            candidate = _resolve_path(base_root, token)
            if candidate not in ordered:
                ordered.append(candidate)

    family = _platform_family(platform_id)
    if family == "windows":
        user_root = _token(environment.get("APPDATA")) or _resolve_path(
            _token(environment.get("USERPROFILE") or environment.get("HOME")),
            os.path.join("AppData", "Roaming"),
        )
        system_root = _token(environment.get("ProgramData"))
        defaults = [
            os.path.join(user_root, "Dominium", INSTALL_REGISTRY_NAME) if user_root else "",
            os.path.join(system_root, "Dominium", INSTALL_REGISTRY_NAME) if system_root else "",
        ]
    elif family == "macos":
        home_root = _token(environment.get("HOME"))
        defaults = [
            os.path.join(home_root, "Library", "Application Support", "Dominium", INSTALL_REGISTRY_NAME) if home_root else "",
            os.path.join(os.sep, "Library", "Application Support", "Dominium", INSTALL_REGISTRY_NAME),
        ]
    else:
        user_root = _token(environment.get("XDG_CONFIG_HOME"))
        if not user_root:
            home_root = _token(environment.get("HOME"))
            if home_root:
                user_root = os.path.join(home_root, ".config")
        defaults = [
            os.path.join(user_root, "dominium", INSTALL_REGISTRY_NAME) if user_root else "",
            os.path.join(os.sep, "etc", "dominium", INSTALL_REGISTRY_NAME),
        ]

    for candidate in defaults:
        token = _token(candidate)
        if token:
            normalized = _norm(token)
            if normalized not in ordered:
                ordered.append(normalized)
    return ordered


def load_runtime_install_registry(path: str) -> dict:
    registry_path = _norm(path)
    if not os.path.isfile(registry_path):
        return {
            "schema_id": "dominium.registry.install_registry",
            "schema_version": "1.0.0",
            "record": {
                "registry_id": "dominium.registry.install_registry",
                "registry_version": "1.0.0",
                "installs": [],
            },
        }
    payload, error = _read_json(registry_path)
    if error:
        return {
            "schema_id": "dominium.registry.install_registry",
            "schema_version": "1.0.0",
            "record": {
                "registry_id": "dominium.registry.install_registry",
                "registry_version": "1.0.0",
                "installs": [],
            },
        }
    record = _as_map(payload.get("record"))
    installs = []
    registry_root = os.path.dirname(registry_path)
    for row in list(record.get("installs") or []):
        entry = _as_map(row)
        install_id = _token(entry.get("install_id"))
        path_token = _token(entry.get("path"))
        resolved_path = _resolve_path(registry_root, path_token) if path_token else ""
        if not install_id or not resolved_path:
            continue
        installs.append(
            {
                "install_id": install_id,
                "path": _norm_rel(path_token),
                "install_root": resolved_path,
                "version": _token(entry.get("version")),
                "contract_registry_hash": _token(entry.get("contract_registry_hash") or entry.get("semantic_contract_registry_hash")),
            }
        )
    return {
        "schema_id": _token(payload.get("schema_id")) or "dominium.registry.install_registry",
        "schema_version": _token(payload.get("schema_version")) or "1.0.0",
        "record": {
            "registry_id": _token(record.get("registry_id")) or "dominium.registry.install_registry",
            "registry_version": _token(record.get("registry_version")) or "1.0.0",
            "installs": sorted(installs, key=lambda row: (row["install_id"], row["path"])),
        },
    }


def _cli_install_root(raw_args: Iterable[object], cwd: str) -> tuple[str, str]:
    cli_root = _value_after(raw_args, "--install-root", "--root")
    if cli_root:
        return _resolve_path(cwd, cli_root), "cli_install_root"
    return "", ""


def _env_install_root(env: Mapping[str, object] | None, cwd: str) -> tuple[str, str]:
    env_root = _token(dict(env or os.environ).get(ENV_INSTALL_ROOT))
    if env_root:
        return _resolve_path(cwd, env_root), "env_install_root"
    return "", ""


def _cli_install_id(raw_args: Iterable[object]) -> tuple[str, str]:
    cli_id = _value_after(raw_args, "--install-id")
    if cli_id:
        return _token(cli_id), "cli_install_id"
    return "", ""


def _env_install_id(env: Mapping[str, object] | None) -> tuple[str, str]:
    env_id = _token(dict(env or os.environ).get(ENV_INSTALL_ID))
    if env_id:
        return _token(env_id), "env_install_id"
    return "", ""


def _registry_rows_by_candidate(candidate_paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for path in candidate_paths:
        payload = load_runtime_install_registry(path)
        for row in list(_as_map(payload.get("record")).get("installs") or []):
            entry = dict(row or {})
            entry["registry_path"] = _norm(path)
            rows.append(entry)
    return rows


def _entry_matches_executable(entry: Mapping[str, object], executable_path: str) -> bool:
    install_root = _norm(entry.get("install_root"))
    executable_abs = _norm(executable_path)
    try:
        common = os.path.commonpath([install_root, executable_abs])
    except ValueError:
        return False
    return os.path.normcase(common) == os.path.normcase(install_root)


def _build_refusal(
    *,
    executable_path: str,
    candidate_paths: list[str],
    requested_install_id: str,
    requested_install_root: str,
    resolution_source: str,
    warnings: list[str],
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "result": "refused",
        "refusal_code": REFUSAL_INSTALL_NOT_FOUND,
        "resolved_install_id": _token(requested_install_id),
        "resolved_install_root_path": _token(requested_install_root).replace("\\", "/"),
        "mode": "",
        "resolution_source": _token(resolution_source),
        "install_manifest_path": "",
        "install_registry_path": "",
        "registry_candidate_paths": [str(item).replace("\\", "/") for item in candidate_paths],
        "warnings": sorted({_token(item) for item in warnings if _token(item)}),
        "errors": [
            {
                "code": REFUSAL_INSTALL_NOT_FOUND,
                "path": "$.install_root",
                "message": "no install root could be resolved from CLI, portable adjacency, environment overrides, or the install registry",
            }
        ],
        "extensions": {
            "official.executable_path": _token(executable_path).replace("\\", "/"),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _complete_payload(
    *,
    result_mode: str,
    resolution_source: str,
    install_root: str,
    install_manifest: Mapping[str, object],
    manifest_path: str,
    registry_path: str,
    candidate_paths: list[str],
    warnings: list[str],
    executable_abs: str,
    requested_install_id: str = "",
) -> dict:
    manifest_payload = dict(install_manifest or {})
    payload = {
        "schema_version": "1.0.0",
        "result": "complete",
        "resolved_install_id": _token(requested_install_id) or _token(manifest_payload.get("install_id")),
        "resolved_install_root_path": _token(install_root).replace("\\", "/"),
        "mode": _token(result_mode),
        "resolution_source": _token(resolution_source),
        "install_manifest_path": _token(manifest_path).replace("\\", "/"),
        "install_registry_path": _token(registry_path).replace("\\", "/"),
        "registry_candidate_paths": [str(item).replace("\\", "/") for item in candidate_paths],
        "install_manifest": manifest_payload,
        "warnings": sorted({_token(item) for item in warnings if _token(item)}),
        "errors": [],
        "extensions": {
            "official.executable_path": _token(executable_abs).replace("\\", "/"),
            "official.version": _token(manifest_payload.get("install_version")),
            "official.contract_registry_hash": _token(manifest_payload.get("semantic_contract_registry_hash")),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def discover_install(
    *,
    raw_args: Iterable[object] | None = None,
    executable_path: str = "",
    cwd: str = "",
    env: Mapping[str, object] | None = None,
    platform_id: str = "",
    explicit_registry_path: str = "",
) -> dict:
    args = list(raw_args or [])
    working_dir = _norm(cwd or os.getcwd())
    executable_abs = _norm(executable_path or sys.argv[0] or ".")
    executable_dir = os.path.dirname(executable_abs)
    warnings: list[str] = []

    requested_install_root, resolution_source = _cli_install_root(args, working_dir)
    requested_install_id, install_id_source = _cli_install_id(args)
    candidate_paths = install_registry_candidate_paths(
        executable_path=executable_abs,
        cwd=working_dir,
        env=env,
        platform_id=platform_id,
        explicit_registry_path=explicit_registry_path or _value_after(args, "--install-registry-path"),
    )
    if requested_install_root:
        manifest_payload, manifest_path, manifest_error = _load_install_manifest(requested_install_root)
        if not manifest_error:
            return _complete_payload(
                result_mode="explicit",
                resolution_source=resolution_source,
                install_root=requested_install_root,
                install_manifest=manifest_payload,
                manifest_path=manifest_path,
                registry_path="",
                candidate_paths=candidate_paths,
                warnings=warnings,
                executable_abs=executable_abs,
            )
        warnings.append("explicit_install_root.{}".format(manifest_error))
        return _build_refusal(
            executable_path=executable_abs,
            candidate_paths=candidate_paths,
            requested_install_id="",
            requested_install_root=requested_install_root,
            resolution_source=resolution_source,
            warnings=warnings,
        )

    if requested_install_id:
        registry_rows = _registry_rows_by_candidate(candidate_paths)
        for row in registry_rows:
            if _token(row.get("install_id")) != requested_install_id:
                continue
            manifest_payload, manifest_path, manifest_error = _load_install_manifest(_token(row.get("install_root")))
            if manifest_error:
                warnings.append("cli_install_id.{}".format(manifest_error))
                break
            return _complete_payload(
                result_mode="explicit",
                resolution_source=install_id_source,
                install_root=_token(row.get("install_root")),
                install_manifest=manifest_payload,
                manifest_path=manifest_path,
                registry_path=_token(row.get("registry_path")),
                candidate_paths=candidate_paths,
                warnings=warnings,
                executable_abs=executable_abs,
                requested_install_id=requested_install_id,
            )
        warnings.append("cli_install_id.not_found")
        return _build_refusal(
            executable_path=executable_abs,
            candidate_paths=candidate_paths,
            requested_install_id=requested_install_id,
            requested_install_root="",
            resolution_source=install_id_source,
            warnings=warnings,
        )

    if os.path.isfile(os.path.join(executable_dir, INSTALL_MANIFEST_NAME)):
        manifest_payload, manifest_path, manifest_error = _load_install_manifest(executable_dir)
        if not manifest_error:
            return _complete_payload(
                result_mode="portable",
                resolution_source="portable_manifest",
                install_root=executable_dir,
                install_manifest=manifest_payload,
                manifest_path=manifest_path,
                registry_path="",
                candidate_paths=candidate_paths,
                warnings=warnings,
                executable_abs=executable_abs,
            )
        warnings.append("portable_manifest.{}".format(manifest_error))

    requested_install_root, resolution_source = _env_install_root(env, working_dir)
    if requested_install_root:
        manifest_payload, manifest_path, manifest_error = _load_install_manifest(requested_install_root)
        if not manifest_error:
            return _complete_payload(
                result_mode="explicit",
                resolution_source=resolution_source,
                install_root=requested_install_root,
                install_manifest=manifest_payload,
                manifest_path=manifest_path,
                registry_path="",
                candidate_paths=candidate_paths,
                warnings=warnings,
                executable_abs=executable_abs,
            )
        warnings.append("env_install_root.{}".format(manifest_error))
        return _build_refusal(
            executable_path=executable_abs,
            candidate_paths=candidate_paths,
            requested_install_id="",
            requested_install_root=requested_install_root,
            resolution_source=resolution_source,
            warnings=warnings,
        )

    requested_install_id, resolution_source = _env_install_id(env)
    registry_rows = _registry_rows_by_candidate(candidate_paths)
    if requested_install_id:
        for row in registry_rows:
            if _token(row.get("install_id")) != requested_install_id:
                continue
            manifest_payload, manifest_path, manifest_error = _load_install_manifest(_token(row.get("install_root")))
            if manifest_error:
                warnings.append("env_install_id.{}".format(manifest_error))
                break
            return _complete_payload(
                result_mode="explicit",
                resolution_source=resolution_source,
                install_root=_token(row.get("install_root")),
                install_manifest=manifest_payload,
                manifest_path=manifest_path,
                registry_path=_token(row.get("registry_path")),
                candidate_paths=candidate_paths,
                warnings=warnings,
                executable_abs=executable_abs,
                requested_install_id=requested_install_id,
            )
        warnings.append("env_install_id.not_found")
        return _build_refusal(
            executable_path=executable_abs,
            candidate_paths=candidate_paths,
            requested_install_id=requested_install_id,
            requested_install_root="",
            resolution_source=resolution_source,
            warnings=warnings,
        )

    matching_rows = [row for row in registry_rows if _entry_matches_executable(row, executable_abs)]
    if len(matching_rows) == 1:
        row = dict(matching_rows[0])
        manifest_payload, manifest_path, manifest_error = _load_install_manifest(_token(row.get("install_root")))
        if not manifest_error:
            return _complete_payload(
                result_mode="installed",
                resolution_source="installed_registry_match",
                install_root=_token(row.get("install_root")),
                install_manifest=manifest_payload,
                manifest_path=manifest_path,
                registry_path=_token(row.get("registry_path")),
                candidate_paths=candidate_paths,
                warnings=warnings,
                executable_abs=executable_abs,
            )
        warnings.append("installed_registry_match.{}".format(manifest_error))

    if len(registry_rows) == 1:
        row = dict(registry_rows[0])
        manifest_payload, manifest_path, manifest_error = _load_install_manifest(_token(row.get("install_root")))
        if not manifest_error:
            return _complete_payload(
                result_mode="installed",
                resolution_source="installed_registry_single",
                install_root=_token(row.get("install_root")),
                install_manifest=manifest_payload,
                manifest_path=manifest_path,
                registry_path=_token(row.get("registry_path")),
                candidate_paths=candidate_paths,
                warnings=warnings,
                executable_abs=executable_abs,
            )
        warnings.append("installed_registry_single.{}".format(manifest_error))

    if len(matching_rows) > 1:
        warnings.append("installed_registry.ambiguous_executable_match")
    elif len(registry_rows) > 1:
        warnings.append("installed_registry.ambiguous_registry")

    return _build_refusal(
        executable_path=executable_abs,
        candidate_paths=candidate_paths,
        requested_install_id=requested_install_id,
        requested_install_root=requested_install_root,
        resolution_source=resolution_source,
        warnings=warnings,
    )


__all__ = [
    "ENV_INSTALL_ID",
    "ENV_INSTALL_ROOT",
    "INSTALL_MANIFEST_NAME",
    "INSTALL_REGISTRY_NAME",
    "REFUSAL_INSTALL_NOT_FOUND",
    "discover_install",
    "install_registry_candidate_paths",
    "load_runtime_install_registry",
]
