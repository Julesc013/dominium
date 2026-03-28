"""Deterministic legacy path redirects through the governed virtual path layer."""

from __future__ import annotations

import os
from typing import Mapping

from appshell.paths import (
    VROOT_EXPORTS,
    VROOT_INSTANCES,
    VROOT_IPC,
    VROOT_LOCKS,
    VROOT_LOGS,
    VROOT_PACKS,
    VROOT_PROFILES,
    VROOT_SAVES,
    VROOT_STORE,
    get_current_virtual_paths,
    vpath_init,
    vpath_resolve_existing,
    vpath_resolve,
)

from .common import build_shim_stability, emit_deprecation_warning, stable_rows


PATH_SHIM_WARNING_KEY = "warn.deprecated_path_usage"
PATH_SHIM_ROWS = stable_rows(
    (
        {
            "shim_id": "shim.path.legacy_packs_root",
            "legacy_surface": "../packs | ./packs | packs | data/packs | ./data/packs",
            "legacy_prefixes": ["../packs", "./packs", "packs", "data/packs", "./data/packs"],
            "replacement_surface": "VROOT_PACKS",
            "vroot_id": VROOT_PACKS,
            "vroot_relative_prefix": "",
            "warning_code": "deprecated_path_usage",
            "message_key": PATH_SHIM_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy relative pack roots remain supported during convergence through the virtual path layer.",
                replacement_target="Remove relative pack-root shims after REPO-LAYOUT convergence and path cleanup.",
            ),
        },
        {
            "shim_id": "shim.path.legacy_profiles_root",
            "legacy_surface": "./profiles | profiles | data/profiles | ./data/profiles",
            "legacy_prefixes": ["./profiles", "profiles", "data/profiles", "./data/profiles"],
            "replacement_surface": "VROOT_PROFILES",
            "vroot_id": VROOT_PROFILES,
            "vroot_relative_prefix": "",
            "warning_code": "deprecated_path_usage",
            "message_key": PATH_SHIM_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy profile roots remain loadable through virtual roots during convergence.",
                replacement_target="Remove relative profile-root shims after REPO-LAYOUT convergence and path cleanup.",
            ),
        },
        {
            "shim_id": "shim.path.legacy_data_root",
            "legacy_surface": "./data | data",
            "legacy_prefixes": ["./data", "data"],
            "replacement_surface": "VROOT_STORE/data",
            "vroot_id": VROOT_STORE,
            "vroot_relative_prefix": "data",
            "warning_code": "deprecated_path_usage",
            "message_key": PATH_SHIM_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy generic data roots remain loadable through the store vroot during convergence.",
                replacement_target="Remove generic data-root shims after REPO-LAYOUT convergence and path cleanup.",
            ),
        },
        {
            "shim_id": "shim.path.legacy_store_children",
            "legacy_surface": "./locks | ./instances | ./saves | ./exports | ./logs | ./runtime",
            "legacy_prefixes": [
                "./locks",
                "locks",
                "./instances",
                "instances",
                "./saves",
                "saves",
                "./exports",
                "exports",
                "./logs",
                "logs",
                "./runtime",
                "runtime",
            ],
            "replacement_surface": "governed store vroots",
            "vroot_id": "",
            "vroot_relative_prefix": "",
            "warning_code": "deprecated_path_usage",
            "message_key": PATH_SHIM_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy store-child paths remain redirected through governed vroots during convergence.",
                replacement_target="Remove store-child path shims after REPO-LAYOUT convergence and path cleanup.",
            ),
        },
    )
)

_PREFIX_TO_VROOT = {
    "./locks": (VROOT_LOCKS, ""),
    "locks": (VROOT_LOCKS, ""),
    "./instances": (VROOT_INSTANCES, ""),
    "instances": (VROOT_INSTANCES, ""),
    "./saves": (VROOT_SAVES, ""),
    "saves": (VROOT_SAVES, ""),
    "./exports": (VROOT_EXPORTS, ""),
    "exports": (VROOT_EXPORTS, ""),
    "./logs": (VROOT_LOGS, ""),
    "logs": (VROOT_LOGS, ""),
    "./runtime": (VROOT_IPC, ""),
    "runtime": (VROOT_IPC, ""),
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _normalize_relpath(value: object) -> str:
    token = _token(value).replace("\\", "/")
    while token.startswith("./"):
        token = token[2:]
    while token.startswith("/"):
        token = token[1:]
    return token


def _repo_local_candidate(repo_root: str, normalized_path: str) -> str:
    repo_root_token = _token(repo_root)
    if not repo_root_token or not normalized_path:
        return ""
    candidate = os.path.normpath(
        os.path.abspath(os.path.join(repo_root_token, normalized_path.replace("/", os.sep)))
    )
    if os.path.exists(candidate):
        return candidate
    return ""


def _context(repo_root: str, product_id: str, executable_path: str, active_context: Mapping[str, object] | None = None) -> dict:
    if active_context is not None:
        return dict(active_context)
    current = get_current_virtual_paths()
    if current is not None and _token(current.get("result")) == "complete":
        return dict(current)
    return vpath_init(
        {
            "repo_root": os.path.normpath(os.path.abspath(repo_root or ".")),
            "product_id": _token(product_id) or "tool.attach_console_stub",
            "raw_args": [],
            "executable_path": _token(executable_path),
        }
    )


def path_shim_rows() -> list[dict]:
    return [dict(row) for row in PATH_SHIM_ROWS]


def redirect_legacy_path(
    raw_path: str,
    *,
    repo_root: str = ".",
    product_id: str = "tool.attach_console_stub",
    executable_path: str = "",
    context: Mapping[str, object] | None = None,
    emit_warning: bool = False,
) -> dict:
    token = _token(raw_path)
    if not token or os.path.isabs(token):
        return {
            "result": "complete",
            "shim_applied": False,
            "original_path": token,
            "rewritten_path": token,
            "warning": {},
            "deterministic_fingerprint": "",
        }
    normalized = _normalize_relpath(token)
    matches: list[tuple[str, str, str, dict]] = []
    for row in PATH_SHIM_ROWS:
        row_map = dict(row or {})
        for prefix in list(row_map.get("legacy_prefixes") or []):
            prefix_token = _normalize_relpath(prefix)
            if not prefix_token:
                continue
            if normalized == prefix_token:
                matches.append((prefix_token, "", "", row_map))
            elif normalized.startswith(prefix_token + "/"):
                suffix = normalized[len(prefix_token) + 1 :]
                matches.append((prefix_token, suffix, "", row_map))
    for prefix, (vroot_id, rel_prefix) in sorted(_PREFIX_TO_VROOT.items(), key=lambda item: -len(_normalize_relpath(item[0]))):
        prefix_token = _normalize_relpath(prefix)
        if normalized == prefix_token:
            matches.append((prefix_token, "", rel_prefix, {"shim_id": "shim.path.legacy_store_children", "vroot_id": vroot_id, "message_key": PATH_SHIM_WARNING_KEY, "warning_code": "deprecated_path_usage"}))
        elif normalized.startswith(prefix_token + "/"):
            matches.append((prefix_token, normalized[len(prefix_token) + 1 :], rel_prefix, {"shim_id": "shim.path.legacy_store_children", "vroot_id": vroot_id, "message_key": PATH_SHIM_WARNING_KEY, "warning_code": "deprecated_path_usage"}))
    if not matches:
        return {
            "result": "complete",
            "shim_applied": False,
            "original_path": token,
            "rewritten_path": token,
            "warning": {},
            "deterministic_fingerprint": "",
        }
    prefix, suffix, rel_prefix_override, row = sorted(matches, key=lambda item: (-len(item[0]), item[0]))[0]
    row_map = dict(row or {})
    vroot_id = _token(row_map.get("vroot_id"))
    active_context = _context(repo_root, product_id, executable_path, active_context=context)
    rel_prefix = _token(rel_prefix_override) or _token(row_map.get("vroot_relative_prefix"))
    rewritten_rel = "/".join(part for part in (rel_prefix, suffix) if _token(part))
    repo_local_fallback = _repo_local_candidate(repo_root, normalized)
    rewritten_path = (
        repo_local_fallback
        or vpath_resolve_existing(vroot_id, rewritten_rel, active_context)
        or vpath_resolve(vroot_id, rewritten_rel, active_context)
    )
    warning = {}
    if emit_warning:
        warning = emit_deprecation_warning(
            category="paths",
            severity="warn",
            shim_id=_token(row_map.get("shim_id")),
            warning_code=_token(row_map.get("warning_code")) or "deprecated_path_usage",
            message_key=_token(row_map.get("message_key")) or PATH_SHIM_WARNING_KEY,
            original_surface=token,
            replacement_surface="{}{}".format(vroot_id, "/{}".format(rewritten_rel) if _token(rewritten_rel) else ""),
            details={
                "legacy_prefix": prefix,
                "replacement_vroot": vroot_id,
                "repo_local_fallback_used": bool(repo_local_fallback),
                "rewritten_path": rewritten_path.replace("\\", "/"),
            },
        )
    return {
        "result": "complete",
        "shim_applied": True,
        "shim_id": _token(row_map.get("shim_id")),
        "original_path": token,
        "rewritten_path": rewritten_path.replace("\\", "/"),
        "vroot_id": vroot_id,
        "rewritten_relative_path": rewritten_rel,
        "warning": warning,
        "deterministic_fingerprint": canonical_sha256(
            {
                "shim_id": _token(row_map.get("shim_id")),
                "original_path": token.replace("\\", "/"),
                "rewritten_path": rewritten_path.replace("\\", "/"),
                "vroot_id": vroot_id,
                "rewritten_relative_path": rewritten_rel,
            }
        ),
    }


from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


__all__ = [
    "PATH_SHIM_ROWS",
    "PATH_SHIM_WARNING_KEY",
    "path_shim_rows",
    "redirect_legacy_path",
]
