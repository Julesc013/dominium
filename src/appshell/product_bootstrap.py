"""Shared AppShell product bootstrap context and legacy flag migration helpers."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from src.compat import build_compat_status_payload, emit_product_descriptor, negotiate_product_endpoints
from tools.xstack.compatx.canonical_json import canonical_sha256

from .args_parser import AppShellArgs
from .mode_dispatcher import legacy_mode_args, supported_modes_for_product


_SHELL_FLAGS_WITH_VALUES = {
    "--repo-root",
    "--mode",
    "--tui-layout",
    "--ipc",
    "--ipc-manifest-path",
    "--session-id",
    "--descriptor-file",
}
_SHELL_FLAGS_NO_VALUE = {
    "--descriptor",
    "--version",
    "-h",
    "--help",
}
_LEGACY_MODE_VALUE_MAP = {
    "cli": "cli",
    "gui": "rendered",
    "headless": "headless",
    "rendered": "rendered",
    "tui": "tui",
}
_PRODUCT_ENTRYPOINT_LABELS = {
    "client": "tools/mvp/runtime_entry.py::appshell_product_bootstrap",
    "engine": "tools/appshell/product_stub_cli.py::main",
    "game": "tools/appshell/product_stub_cli.py::main",
    "launcher": "tools/launcher/launch.py::appshell_product_bootstrap",
    "server": "src/server/server_main.py::appshell_product_bootstrap",
    "setup": "tools/setup/setup_cli.py::appshell_product_bootstrap",
    "tool.attach_console_stub": "tools/appshell/product_stub_cli.py::main",
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted({_token(value) for value in list(values or []) if _token(value)})


def _command_token(args: Sequence[str]) -> str:
    for token in list(args or []):
        text = _token(token)
        if text and not text.startswith("-"):
            return text
    return ""


def _value_after(args: Sequence[str], *flags: str) -> str:
    values = list(args or [])
    targets = {str(flag).strip() for flag in flags if str(flag).strip()}
    for index, token in enumerate(values):
        if str(token).strip() not in targets:
            continue
        if index + 1 >= len(values):
            return ""
        return _token(values[index + 1])
    return ""


def _has_flag(args: Sequence[str], flag: str) -> bool:
    return any(_token(token) == str(flag).strip() for token in list(args or []))


def _remove_shell_flags(raw_args: Sequence[str]) -> list[str]:
    values = list(raw_args or [])
    kept: list[str] = []
    index = 0
    while index < len(values):
        token = _token(values[index])
        if token in _SHELL_FLAGS_NO_VALUE:
            index += 1
            continue
        if token in _SHELL_FLAGS_WITH_VALUES:
            index += 2
            continue
        kept.append(str(values[index]))
        index += 1
    return kept


def _strip_flag_with_value(args: Sequence[str], *flags: str) -> list[str]:
    values = list(args or [])
    targets = {str(flag).strip() for flag in flags if str(flag).strip()}
    kept: list[str] = []
    index = 0
    while index < len(values):
        token = _token(values[index])
        if token in targets:
            index += 2
            continue
        kept.append(str(values[index]))
        index += 1
    return kept


def resolve_mode_request(product_id: str, explicit_mode: str, raw_args: Sequence[str]) -> dict:
    product_token = _token(product_id)
    explicit_token = _token(explicit_mode).lower()
    if explicit_token:
        return {
            "requested_mode_id": explicit_token,
            "mode_source": "explicit",
            "mode_requested": True,
            "deprecated_flags": [],
            "migration_rows": [],
        }
    legacy_value = _token(_value_after(raw_args, "--ui")).lower()
    migrated = _LEGACY_MODE_VALUE_MAP.get(legacy_value, "")
    if product_token in {"client", "server"} and migrated:
        warning = {
            "legacy_flag": "--ui",
            "legacy_value": legacy_value,
            "replacement_flag": "--mode",
            "replacement_value": migrated,
            "message": "legacy --ui flag is deprecated; use --mode {}".format(migrated),
        }
        return {
            "requested_mode_id": migrated,
            "mode_source": "legacy_flag",
            "mode_requested": True,
            "deprecated_flags": [dict(warning)],
            "migration_rows": [
                {
                    "product_id": product_token,
                    "legacy_flag": "--ui",
                    "legacy_value": legacy_value,
                    "replacement_flag": "--mode",
                    "replacement_value": migrated,
                }
            ],
        }
    return {
        "requested_mode_id": "",
        "mode_source": "default",
        "mode_requested": False,
        "deprecated_flags": [],
        "migration_rows": [],
    }


def build_delegate_args(
    product_id: str,
    shell_args: AppShellArgs,
    *,
    resolved_mode_id: str,
    mode_source: str,
) -> list[str]:
    delegate_args = _remove_shell_flags(shell_args.raw_args)
    if _token(product_id) in {"client", "server"}:
        delegate_args = _strip_flag_with_value(delegate_args, "--ui")
        translated_mode_args = list(legacy_mode_args(_token(product_id), _token(resolved_mode_id)))
        if translated_mode_args:
            delegate_args = translated_mode_args + list(delegate_args)
    return list(delegate_args)


def _bootstrap_steps(product_id: str, raw_args: Sequence[str]) -> list[str]:
    product_token = _token(product_id)
    command = _command_token(raw_args)
    steps = ["mode_select", "descriptor_emit", "negotiation_preflight"]
    if product_token == "launcher":
        if command == "run":
            steps.extend(["session_spec_validate", "pack_validate", "session_start"])
            if _token(_value_after(raw_args, "--script")):
                steps.append("script_dispatch")
            return steps
        if command == "compat-status":
            return steps + ["pack_validate"]
        if command == "create-session":
            return steps + ["session_create"]
        return steps + ["command_dispatch"]
    if product_token == "setup":
        if command in {"verify", "list-packs", "build-lock", "diagnose-pack"}:
            return steps + ["pack_validate"]
        if command in {"apply", "repair", "rollback", "uninstall"}:
            return steps + ["install_validate", "command_dispatch"]
        if command in {"install", "instance", "save", "pack"}:
            return steps + ["install_validate", "command_dispatch"]
        return steps + ["command_dispatch"]
    if product_token == "server":
        steps.extend(["contract_validate", "pack_validate", "session_start"])
        if _has_flag(raw_args, "--listen-loopback"):
            steps.append("loopback_listen")
        if _has_flag(raw_args, "--accept-once"):
            steps.append("loopback_accept")
        if _token(_value_after(raw_args, "--command")):
            steps.append("server_command")
        return steps
    if product_token == "client":
        steps.extend(["artifact_validate", "session_start"])
        if _has_flag(raw_args, "--local-singleplayer"):
            steps.append("local_server_attach")
        return steps
    if product_token in {"engine", "game", "tool.attach_console_stub"}:
        return steps + ["stub_dispatch"]
    return steps + ["command_dispatch"]


def _bootstrap_refs(product_id: str, raw_args: Sequence[str], repo_root: str) -> dict:
    product_token = _token(product_id)
    refs = {
        "command_id": _command_token(raw_args),
        "repo_root": _token(repo_root).replace("\\", "/"),
    }
    if product_token == "launcher":
        refs.update(
            {
                "dist_root": _token(_value_after(raw_args, "--dist") or "dist"),
                "session_spec_path": _token(_value_after(raw_args, "--session")),
                "bundle_id": _token(_value_after(raw_args, "--bundle")),
                "script_path": _token(_value_after(raw_args, "--script")),
                "mod_policy_id": _token(_value_after(raw_args, "--mod-policy-id")),
                "overlay_conflict_policy_id": _token(_value_after(raw_args, "--overlay-conflict-policy-id")),
                "contract_bundle_path": _token(_value_after(raw_args, "--contract-bundle-path")),
            }
        )
    elif product_token == "setup":
        refs.update(
            {
                "compat_root": _token(_value_after(raw_args, "--root", "--install-root")),
                "schema_root": _token(_value_after(raw_args, "--schema-root")),
                "bundle_id": _token(_value_after(raw_args, "--bundle-id", "--bundle")),
                "mod_policy_id": _token(_value_after(raw_args, "--mod-policy-id")),
                "overlay_conflict_policy_id": _token(_value_after(raw_args, "--overlay-conflict-policy-id")),
                "contract_bundle_path": _token(_value_after(raw_args, "--contract-bundle-path")),
                "manifest_path": _token(_value_after(raw_args, "--manifest")),
                "install_root": _token(_value_after(raw_args, "--install-root")),
                "data_root": _token(_value_after(raw_args, "--data-root")),
                "store_root": _token(_value_after(raw_args, "--store-root")),
            }
        )
    elif product_token == "server":
        refs.update(
            {
                "session_spec_path": _token(_value_after(raw_args, "--session-spec-path")),
                "server_config_id": _token(_value_after(raw_args, "--server-config-id")),
                "seed": _token(_value_after(raw_args, "--seed")),
                "profile_bundle_path": _token(_value_after(raw_args, "--profile-bundle")),
                "pack_lock_path": _token(_value_after(raw_args, "--pack-lock")),
                "contract_bundle_hash": _token(_value_after(raw_args, "--contract-bundle-hash")),
                "save_id": _token(_value_after(raw_args, "--save-id")),
                "listen_loopback": _has_flag(raw_args, "--listen-loopback"),
                "accept_once": _has_flag(raw_args, "--accept-once"),
            }
        )
    elif product_token == "client":
        refs.update(
            {
                "seed": _token(_value_after(raw_args, "--seed")),
                "profile_bundle_path": _token(_value_after(raw_args, "--profile_bundle", "--profile-bundle")),
                "pack_lock_path": _token(_value_after(raw_args, "--pack_lock", "--pack-lock")),
                "teleport": _token(_value_after(raw_args, "--teleport")),
                "authority_mode": _token(_value_after(raw_args, "--authority")),
                "local_singleplayer": _has_flag(raw_args, "--local-singleplayer"),
                "server_config_id": _token(_value_after(raw_args, "--server-config-id")),
            }
        )
    return {
        key: value
        for key, value in sorted(refs.items(), key=lambda item: str(item[0]))
        if value not in ("", None) and value != []
    }


def flag_migration_rows() -> list[dict]:
    return [
        {
            "product_id": "client",
            "legacy_flag": "--ui gui|cli",
            "replacement_flag": "--mode rendered|cli",
            "status": "supported_with_warning",
        },
        {
            "product_id": "server",
            "legacy_flag": "--ui headless|cli",
            "replacement_flag": "--mode headless|cli",
            "status": "supported_with_warning",
        },
    ]


def build_product_bootstrap_context(
    *,
    product_id: str,
    repo_root: str,
    shell_args: AppShellArgs,
    mode_resolution: Mapping[str, object],
    mode_selection: Mapping[str, object],
    version_payload: Mapping[str, object],
) -> dict:
    product_token = _token(product_id)
    selected_mode_id = _token(mode_selection.get("selected_mode_id") or mode_selection.get("effective_mode_id"))
    descriptor_payload = emit_product_descriptor(repo_root, product_id=product_token)
    endpoint_descriptor = dict(descriptor_payload.get("descriptor") or {})
    negotiated = negotiate_product_endpoints(
        repo_root,
        endpoint_descriptor,
        endpoint_descriptor,
        allow_read_only=True,
    )
    negotiation_record = dict(negotiated.get("negotiation_record") or {})
    compat_status = build_compat_status_payload(
        negotiation_record,
        product_id=product_token,
        connection_id="bootstrap",
    )
    delegate_argv = build_delegate_args(
        product_token,
        shell_args,
        resolved_mode_id=selected_mode_id,
        mode_source=_token(mode_resolution.get("mode_source")),
    )
    compat_status = dict(compat_status)
    compat_status["mode_selection"] = {
        "requested_mode_id": _token(mode_selection.get("requested_mode_id")),
        "selected_mode_id": selected_mode_id,
        "mode_source": _token(mode_selection.get("mode_source")) or "default",
        "context_kind": _token(mode_selection.get("context_kind")),
        "compatibility_mode_id": _token(mode_selection.get("compatibility_mode_id")) or "compat.full",
        "degrade_chain": [dict(row) for row in list(mode_selection.get("degrade_chain") or []) if isinstance(row, Mapping)],
    }
    context = {
        "bootstrap_plan_id": "appshell.bootstrap.v1",
        "product_id": product_token,
        "entrypoint_label": _PRODUCT_ENTRYPOINT_LABELS.get(product_token, ""),
        "repo_root": _token(repo_root).replace("\\", "/"),
        "raw_args": list(shell_args.raw_args),
        "delegate_argv": list(delegate_argv),
        "mode": {
            "requested_mode_id": _token(mode_resolution.get("requested_mode_id")),
            "effective_mode_id": selected_mode_id,
            "selected_mode_id": selected_mode_id,
            "mode_source": _token(mode_selection.get("mode_source")) or _token(mode_resolution.get("mode_source")) or "default",
            "mode_requested": bool(mode_resolution.get("mode_requested", False)),
            "context_kind": _token(mode_selection.get("context_kind")),
            "compatibility_mode_id": _token(mode_selection.get("compatibility_mode_id")) or "compat.full",
            "supported_mode_ids": list(supported_modes_for_product(product_token, repo_root=repo_root)),
            "available_mode_ids": list(mode_selection.get("available_mode_ids") or []),
            "degrade_chain": [dict(row) for row in list(mode_selection.get("degrade_chain") or []) if isinstance(row, Mapping)],
            "probe": dict(mode_selection.get("probe") or {}),
            "deprecated_flags": [dict(row) for row in list(mode_resolution.get("deprecated_flags") or []) if isinstance(row, Mapping)],
        },
        "descriptor_payload": dict(descriptor_payload),
        "version_payload": dict(version_payload or {}),
        "negotiation": {
            "result": _token(negotiated.get("result")) or "complete",
            "compatibility_mode_id": _token(negotiated.get("compatibility_mode_id")),
            "negotiation_record_hash": _token(negotiated.get("negotiation_record_hash")),
            "endpoint_a_hash": _token(negotiated.get("endpoint_a_hash")),
            "endpoint_b_hash": _token(negotiated.get("endpoint_b_hash")),
            "compat_status": compat_status,
            "negotiation_record": dict(negotiation_record),
        },
        "bootstrap_steps": list(_bootstrap_steps(product_token, shell_args.raw_args)),
        "bootstrap_refs": dict(_bootstrap_refs(product_token, shell_args.raw_args, repo_root)),
        "ipc": {
            "enabled": bool(shell_args.ipc_enabled),
            "manifest_path": _token(shell_args.ipc_manifest_path).replace("\\", "/"),
            "session_id": _token(shell_args.session_id),
        },
        "supervisor": {
            "required": product_token == "launcher",
        },
        "install_reference": _token(
            _value_after(shell_args.raw_args, "--install-root", "--manifest", "--instance-manifest", "--instance-id")
        ),
        "deterministic_fingerprint": "",
    }
    context["deterministic_fingerprint"] = canonical_sha256(dict(context, deterministic_fingerprint=""))
    return context


__all__ = [
    "build_delegate_args",
    "build_product_bootstrap_context",
    "flag_migration_rows",
    "resolve_mode_request",
]
