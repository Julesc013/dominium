"""Deterministic virtual root resolution for portable and installed Dominium layouts."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import IO, Iterable, Mapping


VIRTUAL_ROOT_REGISTRY_REL = os.path.join("data", "registries", "virtual_root_registry.json")
INSTALL_REGISTRY_REL = os.path.join("data", "registries", "install_registry.json")
INSTALL_MANIFEST_NAME = "install.manifest.json"

VROOT_INSTALL = "VROOT_INSTALL"
VROOT_BIN = "VROOT_BIN"
VROOT_STORE = "VROOT_STORE"
VROOT_PACKS = "VROOT_PACKS"
VROOT_PROFILES = "VROOT_PROFILES"
VROOT_LOCKS = "VROOT_LOCKS"
VROOT_INSTANCES = "VROOT_INSTANCES"
VROOT_SAVES = "VROOT_SAVES"
VROOT_EXPORTS = "VROOT_EXPORTS"
VROOT_LOGS = "VROOT_LOGS"
VROOT_IPC = "VROOT_IPC"

_CURRENT_VPATHS = None
_VROOT_ORDER = (
    VROOT_INSTALL,
    VROOT_BIN,
    VROOT_STORE,
    VROOT_PACKS,
    VROOT_PROFILES,
    VROOT_LOCKS,
    VROOT_INSTANCES,
    VROOT_SAVES,
    VROOT_EXPORTS,
    VROOT_LOGS,
    VROOT_IPC,
)
_FLAG_TO_VROOT = {
    "--packs-root": VROOT_PACKS,
    "--profiles-root": VROOT_PROFILES,
    "--locks-root": VROOT_LOCKS,
    "--instances-root": VROOT_INSTANCES,
    "--saves-root": VROOT_SAVES,
    "--exports-root": VROOT_EXPORTS,
    "--logs-root": VROOT_LOGS,
    "--ipc-root": VROOT_IPC,
}
_FALLBACK_INSTALLED_PATTERNS = {
    VROOT_PACKS: "{store_root}/packs",
    VROOT_PROFILES: "{store_root}/profiles",
    VROOT_LOCKS: "{store_root}/locks",
    VROOT_INSTANCES: "{store_root}/instances",
    VROOT_SAVES: "{store_root}/saves",
    VROOT_EXPORTS: "{store_root}/exports",
    VROOT_LOGS: "{store_root}/logs",
    VROOT_IPC: "{store_root}/runtime",
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    token = _token(path).replace("\\", "/")
    while token.startswith("./"):
        token = token[2:]
    return token


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
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


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


def _existing_dir(*candidates: str) -> str:
    for candidate in list(candidates or []):
        token = _token(candidate)
        if token and os.path.isdir(token):
            return _norm(token)
    return ""


def _resolve_store_root_from_manifest(install_root: str, manifest: Mapping[str, object] | None) -> str:
    payload = dict(manifest or {})
    root_ref = dict(payload.get("store_root_ref") or payload.get("store_root") or {})
    manifest_ref = _token(root_ref.get("manifest_ref"))
    root_path = _token(root_ref.get("root_path"))
    if manifest_ref:
        abs_manifest = _resolve_path(install_root, manifest_ref)
        return _norm(os.path.dirname(abs_manifest))
    if root_path:
        return _resolve_path(install_root, root_path)
    return _norm(install_root)


def _load_install_manifest(install_root: str) -> tuple[dict, str, str]:
    manifest_path = os.path.join(_norm(install_root), INSTALL_MANIFEST_NAME)
    if not os.path.isfile(manifest_path):
        return {}, "", "missing"
    payload, error = _read_json(manifest_path)
    if error:
        return {}, _norm(manifest_path), error
    return payload, _norm(manifest_path), ""


def load_virtual_root_registry(repo_root: str) -> tuple[dict, str]:
    path = os.path.join(_norm(repo_root), VIRTUAL_ROOT_REGISTRY_REL)
    payload, error = _read_json(path)
    if error:
        return {}, error
    record = dict(payload.get("record") or {})
    entries = []
    for row in list(record.get("entries") or []):
        if not isinstance(row, Mapping):
            continue
        item = dict(row)
        item["vroot_id"] = _token(item.get("vroot_id"))
        item["portable_default_rel"] = _norm_rel(item.get("portable_default_rel"))
        item["installed_default_pattern"] = _token(item.get("installed_default_pattern"))
        item["extensions"] = dict(_normalize_tree(dict(item.get("extensions") or {})))
        item["stability"] = dict(_normalize_tree(dict(item.get("stability") or {})))
        item["deterministic_fingerprint"] = _token(item.get("deterministic_fingerprint")) or _fingerprint(item)
        entries.append(item)
    entries = sorted(entries, key=lambda item: _token(item.get("vroot_id")))
    record["entries"] = entries
    record["deterministic_fingerprint"] = _token(record.get("deterministic_fingerprint")) or _fingerprint(record)
    return {
        "schema_id": _token(payload.get("schema_id")),
        "schema_version": _token(payload.get("schema_version")) or "1.0.0",
        "record": record,
    }, ""


def _registry_rows_by_vroot(repo_root: str) -> tuple[dict[str, dict], str]:
    payload, error = load_virtual_root_registry(repo_root)
    if error:
        return {}, error
    out: dict[str, dict] = {}
    for row in list(dict(payload.get("record") or {}).get("entries") or []):
        row_map = dict(row or {})
        vroot_id = _token(row_map.get("vroot_id"))
        if vroot_id:
            out[vroot_id] = row_map
    return out, ""


def _installed_registry_path(repo_root: str, explicit_path: str) -> str:
    token = _token(explicit_path)
    if token:
        return _resolve_path(repo_root, token)
    return _norm(os.path.join(_norm(repo_root), INSTALL_REGISTRY_REL))


def _load_install_registry(path: str) -> list[dict]:
    payload, error = _read_json(path)
    if error:
        return []
    installs = []
    record = dict(payload.get("record") or {})
    registry_root = os.path.dirname(_norm(path))
    for row in list(record.get("installs") or []):
        if not isinstance(row, Mapping):
            continue
        item = dict(row)
        install_id = _token(item.get("install_id"))
        rel_path = _token(item.get("path"))
        install_root = _resolve_path(registry_root, rel_path) if rel_path else ""
        if install_id and install_root:
            installs.append(
                {
                    "install_id": install_id,
                    "install_root": install_root,
                    "path": rel_path.replace("\\", "/"),
                }
            )
    return sorted(installs, key=lambda row: (row["install_id"], row["install_root"]))


def _registry_install_choice(repo_root: str, raw_args: Iterable[object]) -> tuple[str, str, str]:
    registry_path = _installed_registry_path(repo_root, _value_after(raw_args, "--install-registry-path"))
    rows = _load_install_registry(registry_path)
    explicit_install_id = _value_after(raw_args, "--install-id")
    if explicit_install_id:
        for row in rows:
            if _token(row.get("install_id")) == _token(explicit_install_id):
                return _token(row.get("install_root")), _token(row.get("install_id")), registry_path
        return "", _token(explicit_install_id), registry_path
    if len(rows) == 1:
        row = dict(rows[0])
        return _token(row.get("install_root")), _token(row.get("install_id")), registry_path
    return "", "", registry_path


def _portable_install_root(executable_dir: str) -> tuple[str, str]:
    manifest_path = os.path.join(_norm(executable_dir), INSTALL_MANIFEST_NAME)
    if os.path.isfile(manifest_path):
        return _norm(executable_dir), _norm(manifest_path)
    return "", ""


def _format_installed_pattern(pattern: str, *, install_root: str, bin_root: str, store_root: str) -> str:
    template = _token(pattern)
    if not template:
        return ""
    return _norm(
        template.format(
            install_root=install_root.replace("\\", "/"),
            bin_root=bin_root.replace("\\", "/"),
            store_root=store_root.replace("\\", "/"),
        )
    )


def _repo_wrapper_roots(repo_root: str) -> dict:
    repo_root_abs = _norm(repo_root)
    dist_root = _existing_dir(os.path.join(repo_root_abs, "dist"))
    install_root = dist_root or repo_root_abs
    bin_root = _existing_dir(os.path.join(install_root, "bin")) or install_root
    store_root = dist_root or repo_root_abs
    return {
        VROOT_INSTALL: install_root,
        VROOT_BIN: bin_root,
        VROOT_STORE: store_root,
        VROOT_PACKS: _existing_dir(os.path.join(repo_root_abs, "packs"), os.path.join(store_root, "packs")) or os.path.join(repo_root_abs, "packs"),
        VROOT_PROFILES: _existing_dir(
            os.path.join(repo_root_abs, "profiles"),
            os.path.join(repo_root_abs, "data", "profiles"),
            os.path.join(store_root, "profiles"),
        ) or os.path.join(repo_root_abs, "profiles"),
        VROOT_LOCKS: _existing_dir(os.path.join(repo_root_abs, "locks"), os.path.join(store_root, "locks")) or os.path.join(repo_root_abs, "locks"),
        VROOT_INSTANCES: _existing_dir(os.path.join(repo_root_abs, "instances"), os.path.join(store_root, "instances")) or os.path.join(repo_root_abs, "instances"),
        VROOT_SAVES: _existing_dir(os.path.join(repo_root_abs, "saves"), os.path.join(store_root, "saves")) or os.path.join(repo_root_abs, "saves"),
        VROOT_EXPORTS: _existing_dir(os.path.join(repo_root_abs, "exports"), os.path.join(store_root, "exports")) or os.path.join(repo_root_abs, "exports"),
        VROOT_LOGS: _norm(os.path.join(repo_root_abs, "build", "appshell", "logs")),
        VROOT_IPC: _existing_dir(os.path.join(store_root, "runtime")) or _norm(os.path.join(store_root, "runtime")),
    }


def _repo_wrapper_search_roots(repo_root: str, roots: Mapping[str, object]) -> dict[str, list[str]]:
    repo_root_abs = _norm(repo_root)
    store_root = _norm(roots.get(VROOT_STORE) or repo_root_abs)
    out = {vroot_id: [_norm(roots.get(vroot_id) or "")] for vroot_id in _VROOT_ORDER if _token(roots.get(vroot_id))}
    search_pairs = (
        (VROOT_PACKS, os.path.join(store_root, "packs"), os.path.join(repo_root_abs, "packs")),
        (VROOT_LOCKS, os.path.join(store_root, "locks"), os.path.join(repo_root_abs, "locks")),
        (VROOT_INSTANCES, os.path.join(store_root, "instances"), os.path.join(repo_root_abs, "instances")),
        (VROOT_SAVES, os.path.join(store_root, "saves"), os.path.join(repo_root_abs, "saves")),
        (VROOT_EXPORTS, os.path.join(store_root, "exports"), os.path.join(repo_root_abs, "exports")),
    )
    for vroot_id, first, second in search_pairs:
        ordered = []
        for candidate in (second, first):
            token = _token(candidate)
            if token and token not in ordered:
                ordered.append(_norm(token))
        if ordered:
            out[vroot_id] = ordered
    profile_roots = []
    for candidate in (
        os.path.join(repo_root_abs, "data", "profiles"),
        os.path.join(repo_root_abs, "profiles"),
        os.path.join(store_root, "profiles"),
    ):
        token = _token(candidate)
        if token:
            normalized = _norm(token)
            if normalized not in profile_roots:
                profile_roots.append(normalized)
    if profile_roots:
        out[VROOT_PROFILES] = profile_roots
    return out


def _default_installed_roots(
    repo_root: str,
    *,
    install_root: str,
    bin_root: str,
    store_root: str,
) -> tuple[dict[str, str], dict[str, list[str]]]:
    rows, _error = _registry_rows_by_vroot(repo_root)
    roots: dict[str, str] = {}
    search_roots: dict[str, list[str]] = {}
    for vroot_id in _VROOT_ORDER:
        row = dict(rows.get(vroot_id) or {})
        if vroot_id == VROOT_INSTALL:
            target = install_root
        elif vroot_id == VROOT_BIN:
            target = bin_root
        elif vroot_id == VROOT_STORE:
            target = store_root
        else:
            target = _format_installed_pattern(
                _token(row.get("installed_default_pattern")) or _FALLBACK_INSTALLED_PATTERNS.get(vroot_id, ""),
                install_root=install_root,
                bin_root=bin_root,
                store_root=store_root,
            )
        roots[vroot_id] = _norm(target)
        search_roots[vroot_id] = [_norm(target)]
    return roots, search_roots


def _apply_overrides(
    *,
    base_root: str,
    raw_args: Iterable[object],
    roots: Mapping[str, object],
    search_roots: Mapping[str, Iterable[object]],
) -> tuple[dict[str, str], dict[str, list[str]], dict[str, str]]:
    updated_roots = {vroot_id: _norm(path) for vroot_id, path in dict(roots or {}).items() if _token(path)}
    updated_search = {
        vroot_id: [_norm(path) for path in list(paths or []) if _token(path)]
        for vroot_id, paths in dict(search_roots or {}).items()
    }
    overrides: dict[str, str] = {}
    explicit_root = _value_after(raw_args, "--root", "--install-root")
    if explicit_root:
        overrides[VROOT_INSTALL] = _resolve_path(base_root, explicit_root)
    store_override = _value_after(raw_args, "--store-root")
    if store_override:
        overrides[VROOT_STORE] = _resolve_path(base_root, store_override)
    for flag, vroot_id in sorted(_FLAG_TO_VROOT.items(), key=lambda item: item[0]):
        token = _value_after(raw_args, flag)
        if token:
            overrides[vroot_id] = _resolve_path(base_root, token)
    for vroot_id, path in sorted(overrides.items(), key=lambda item: item[0]):
        updated_roots[vroot_id] = _norm(path)
        updated_search[vroot_id] = [_norm(path)]
    return updated_roots, updated_search, dict((key, overrides[key]) for key in sorted(overrides.keys()))


def _canonical_context(payload: Mapping[str, object]) -> dict:
    out = dict(_normalize_tree(dict(payload or {})))
    out["deterministic_fingerprint"] = ""
    out["roots"] = dict((key, out.get("roots", {}).get(key, "")) for key in sorted(dict(out.get("roots") or {}).keys()))
    out["search_roots"] = dict(
        (key, list(out.get("search_roots", {}).get(key) or []))
        for key in sorted(dict(out.get("search_roots") or {}).keys())
    )
    out["explicit_overrides"] = dict(
        (key, out.get("explicit_overrides", {}).get(key, ""))
        for key in sorted(dict(out.get("explicit_overrides") or {}).keys())
    )
    return out


def vpath_init(context: Mapping[str, object]) -> dict:
    payload = dict(context or {})
    repo_root = _norm(payload.get("repo_root") or ".")
    raw_args = list(payload.get("raw_args") or [])
    executable_path = _norm(payload.get("executable_path") or sys.argv[0] or ".")
    executable_dir = os.path.dirname(executable_path)
    product_id = _token(payload.get("product_id"))

    install_root = ""
    install_manifest_path = ""
    install_id = ""
    install_registry_path = ""
    warnings: list[str] = []
    resolution_source = ""

    portable_root, portable_manifest_path = _portable_install_root(executable_dir)
    if portable_root:
        install_root = portable_root
        install_manifest_path = portable_manifest_path
        resolution_source = "portable_manifest"

    if not install_root:
        registry_root, registry_install_id, registry_path = _registry_install_choice(repo_root, raw_args)
        install_registry_path = _token(registry_path)
        if registry_root:
            install_root = _norm(registry_root)
            install_id = _token(registry_install_id)
            resolution_source = "installed_registry"

    if not install_root and (os.path.isdir(os.path.join(repo_root, "dist")) or os.path.isdir(os.path.join(repo_root, "packs"))):
        install_root = _repo_wrapper_roots(repo_root)[VROOT_INSTALL]
        resolution_source = "repo_wrapper_shim"
        warnings.append("repo_wrapper_shim.active")

    manifest_payload: dict = {}
    if install_root:
        manifest_payload, resolved_manifest_path, manifest_error = _load_install_manifest(install_root)
        if not install_manifest_path and resolved_manifest_path:
            install_manifest_path = resolved_manifest_path
        if manifest_error and resolution_source != "repo_wrapper_shim":
            warnings.append("install_manifest.{}".format(manifest_error))
        if manifest_payload and not install_id:
            install_id = _token(manifest_payload.get("install_id"))

    bin_root = ""
    store_root = ""
    search_roots: dict[str, list[str]] = {}
    registry_rows, registry_error = _registry_rows_by_vroot(repo_root)
    if registry_error:
        warnings.append("virtual_root_registry.unavailable")

    if resolution_source == "repo_wrapper_shim":
        roots = _repo_wrapper_roots(repo_root)
        search_roots = _repo_wrapper_search_roots(repo_root, roots)
        store_root = _norm(roots[VROOT_STORE])
        bin_root = _norm(roots[VROOT_BIN])
    elif install_root:
        bin_root = _existing_dir(os.path.join(install_root, "bin")) or _norm(install_root)
        store_root = _resolve_store_root_from_manifest(install_root, manifest_payload)
        roots, search_roots = _default_installed_roots(
            repo_root,
            install_root=_norm(install_root),
            bin_root=_norm(bin_root),
            store_root=_norm(store_root),
        )
    else:
        roots = {}

    roots, search_roots, explicit_overrides = _apply_overrides(
        base_root=repo_root,
        raw_args=raw_args,
        roots=roots,
        search_roots=search_roots,
    )
    if explicit_overrides:
        if VROOT_INSTALL in explicit_overrides:
            install_root = _norm(explicit_overrides[VROOT_INSTALL])
        if VROOT_STORE in explicit_overrides:
            store_root = _norm(explicit_overrides[VROOT_STORE])
        if install_root:
            bin_root = _existing_dir(os.path.join(install_root, "bin")) or _norm(install_root)
            roots[VROOT_BIN] = _norm(explicit_overrides.get(VROOT_BIN) or bin_root)
            search_roots[VROOT_BIN] = [_norm(roots[VROOT_BIN])]
            roots[VROOT_INSTALL] = _norm(install_root)
            search_roots[VROOT_INSTALL] = [_norm(install_root)]
        if store_root:
            roots[VROOT_STORE] = _norm(store_root)
            search_roots[VROOT_STORE] = [_norm(store_root)]
        resolution_source = "explicit_override" if resolution_source else "explicit_override"

    result = "complete"
    refusal_code = ""
    if not roots.get(VROOT_INSTALL):
        result = "refused"
        refusal_code = "refusal.paths.no_install_root"

    registry_fingerprint = _token(dict(dict(load_virtual_root_registry(repo_root)[0]).get("record") or {}).get("deterministic_fingerprint"))
    context_payload = {
        "schema_version": "1.0.0",
        "product_id": product_id,
        "repo_root": repo_root.replace("\\", "/"),
        "cwd": _norm(os.getcwd()).replace("\\", "/"),
        "executable_path": executable_path.replace("\\", "/"),
        "executable_dir": _norm(executable_dir).replace("\\", "/"),
        "result": result,
        "refusal_code": refusal_code,
        "resolution_source": _token(resolution_source),
        "install_id": _token(install_id),
        "install_manifest_path": _token(install_manifest_path).replace("\\", "/"),
        "install_registry_path": _token(install_registry_path).replace("\\", "/"),
        "explicit_overrides": dict((key, _token(value).replace("\\", "/")) for key, value in explicit_overrides.items()),
        "warnings": sorted({_token(item) for item in warnings if _token(item)}),
        "roots": dict((key, _token(roots.get(key)).replace("\\", "/")) for key in sorted(roots.keys())),
        "search_roots": dict(
            (
                key,
                [str(item).replace("\\", "/") for item in list(search_roots.get(key) or [])],
            )
            for key in sorted(search_roots.keys())
        ),
        "virtual_root_registry_hash": registry_fingerprint,
        "extensions": {
            "official.store_root": _token(store_root).replace("\\", "/"),
            "official.bin_root": _token(bin_root).replace("\\", "/"),
            "official.install_manifest_present": bool(install_manifest_path),
            "official.registry_entry_count": int(len(list(dict(registry_rows or {}).keys()))),
        },
        "deterministic_fingerprint": "",
    }
    context_payload["deterministic_fingerprint"] = _fingerprint(_canonical_context(context_payload))
    return context_payload


def set_current_virtual_paths(context: Mapping[str, object] | None) -> None:
    global _CURRENT_VPATHS
    _CURRENT_VPATHS = dict(context or {}) if context is not None else None


def get_current_virtual_paths() -> dict | None:
    return dict(_CURRENT_VPATHS or {}) if _CURRENT_VPATHS is not None else None


def clear_current_virtual_paths() -> None:
    set_current_virtual_paths(None)


def _current_or_init(context: Mapping[str, object] | None = None) -> dict:
    if context is not None:
        return dict(context)
    active = get_current_virtual_paths()
    if active is not None:
        return active
    return vpath_init({"repo_root": ".", "product_id": ""})


def vpath_root(vroot_id: str, context: Mapping[str, object] | None = None) -> str:
    active = _current_or_init(context)
    roots = dict(active.get("roots") or {})
    return _norm(roots.get(_token(vroot_id)) or ".")


def vpath_candidate_roots(vroot_id: str, context: Mapping[str, object] | None = None) -> list[str]:
    active = _current_or_init(context)
    roots = list(dict(active.get("search_roots") or {}).get(_token(vroot_id)) or [])
    if roots:
        return [_norm(path) for path in roots if _token(path)]
    primary = dict(active.get("roots") or {}).get(_token(vroot_id))
    return [_norm(primary)] if _token(primary) else []


def _join_under(root: str, relative_path: str) -> str:
    token = _norm_rel(relative_path)
    if not token:
        return _norm(root)
    return _norm(os.path.join(_norm(root), token.replace("/", os.sep)))


def vpath_resolve(vroot_id: str, relative_path: str = "", context: Mapping[str, object] | None = None) -> str:
    return _join_under(vpath_root(vroot_id, context), relative_path)


def vpath_resolve_existing(vroot_id: str, relative_path: str = "", context: Mapping[str, object] | None = None) -> str:
    for root in vpath_candidate_roots(vroot_id, context):
        candidate = _join_under(root, relative_path)
        if os.path.exists(candidate):
            return candidate
    return ""


def vpath_exists(vroot_id: str, relative_path: str = "", context: Mapping[str, object] | None = None) -> bool:
    return bool(vpath_resolve_existing(vroot_id, relative_path, context))


def vpath_list(vroot_id: str, relative_path: str = "", context: Mapping[str, object] | None = None) -> list[str]:
    names = set()
    for root in vpath_candidate_roots(vroot_id, context):
        target = _join_under(root, relative_path)
        if not os.path.isdir(target):
            continue
        for name in os.listdir(target):
            names.add(str(name))
    return sorted(names)


def vpath_open_read(
    vroot_id: str,
    relative_path: str = "",
    mode: str = "r",
    *,
    encoding: str | None = "utf-8",
    context: Mapping[str, object] | None = None,
) -> IO[object]:
    if "w" in mode or "a" in mode or "x" in mode:
        raise ValueError("vpath_open_read only accepts read modes")
    target = vpath_resolve_existing(vroot_id, relative_path, context)
    if not target:
        raise FileNotFoundError(relative_path or _token(vroot_id))
    kwargs = {"mode": mode}
    if "b" not in mode and encoding is not None:
        kwargs["encoding"] = encoding
    return open(target, **kwargs)


def vpath_open_write(
    vroot_id: str,
    relative_path: str = "",
    mode: str = "w",
    *,
    encoding: str | None = "utf-8",
    context: Mapping[str, object] | None = None,
) -> IO[object]:
    if not any(flag in mode for flag in ("w", "a", "x", "+")):
        raise ValueError("vpath_open_write requires a write-capable mode")
    target = vpath_resolve(vroot_id, relative_path, context)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    kwargs = {"mode": mode}
    if "b" not in mode and encoding is not None:
        kwargs["encoding"] = encoding
    return open(target, **kwargs)
