"""Shared deterministic AppShell bootstrap."""

from __future__ import annotations

import argparse
import json
from typing import Callable, Sequence

from .args_parser import parse_appshell_args
from .command_registry import build_root_command_descriptors, build_tui_panel_descriptors, format_help_text
from .compat_adapter import build_version_payload, emit_descriptor_payload
from .config_loader import list_pack_manifests, list_profile_bundles, resolve_repo_root
from .mode_dispatcher import build_mode_stub, legacy_mode_args, normalize_mode, supported_modes_for_product
from .pack_verifier_adapter import verify_pack_root


EXIT_SUCCESS = 0
EXIT_USAGE = 10
EXIT_PACK = 20
EXIT_CONTRACT = 30
EXIT_TRANSPORT = 40
EXIT_REFUSAL = 50
EXIT_INTERNAL = 60


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _refusal(code: str, message: str, remediation_hint: str, **extra) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": str(code),
        "message": str(message),
        "remediation_hint": str(remediation_hint),
        "details": {}
    }
    for key, value in sorted(extra.items(), key=lambda item: str(item[0])):
        payload["details"][str(key)] = value
    return payload


def _run_verify_command(repo_root: str, args: Sequence[str]) -> tuple[dict, int]:
    parser = argparse.ArgumentParser(prog="verify", add_help=False)
    parser.add_argument("--root", default="dist")
    parser.add_argument("--bundle-id", default="")
    parser.add_argument("--mod-policy-id", default="mod_policy.lab")
    parser.add_argument("--overlay-conflict-policy-id", default="")
    parser.add_argument("--contract-bundle-path", default="")
    parser.add_argument("--out-report", default="")
    parser.add_argument("--out-lock", default="")
    parser.add_argument("--write-outputs", action="store_true")
    parsed = parser.parse_args(list(args or []))
    result = verify_pack_root(
        repo_root=repo_root,
        root=str(parsed.root),
        bundle_id=str(parsed.bundle_id),
        mod_policy_id=str(parsed.mod_policy_id),
        overlay_conflict_policy_id=str(parsed.overlay_conflict_policy_id),
        contract_bundle_path=str(parsed.contract_bundle_path),
        out_report=str(parsed.out_report),
        out_lock=str(parsed.out_lock),
        write_outputs=bool(parsed.write_outputs),
    )
    exit_code = EXIT_SUCCESS if str(result.get("result", "")) == "complete" else EXIT_PACK
    return result, exit_code


def _run_packs_command(repo_root: str, args: Sequence[str]) -> tuple[dict, int]:
    parser = argparse.ArgumentParser(prog="packs", add_help=False)
    parser.add_argument("--root", default="")
    parsed = parser.parse_args(list(args or []))
    return {
        "result": "complete",
        "packs": list_pack_manifests(repo_root, root=str(parsed.root))
    }, EXIT_SUCCESS


def _run_profiles_command(repo_root: str) -> tuple[dict, int]:
    return {
        "result": "complete",
        "profiles": list_profile_bundles(repo_root)
    }, EXIT_SUCCESS


def _run_diag_command(repo_root: str, product_id: str, mode_id: str) -> tuple[dict, int]:
    descriptor = emit_descriptor_payload(repo_root, product_id=product_id)
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "mode": str(mode_id).strip(),
        "repo_root": str(repo_root).replace("\\", "/"),
        "descriptor_hash": str(descriptor.get("descriptor_hash", "")).strip()
    }, EXIT_SUCCESS


def _handle_root_command(repo_root: str, product_id: str, mode_id: str, command: str, command_args: Sequence[str]) -> tuple[dict, int] | None:
    token = str(command or "").strip()
    if not token:
        return None
    if token == "version":
        return build_version_payload(repo_root, product_id=product_id), EXIT_SUCCESS
    if token == "descriptor":
        return emit_descriptor_payload(repo_root, product_id=product_id), EXIT_SUCCESS
    if token in {"verify", "compat-status"}:
        return _run_verify_command(repo_root, command_args)
    if token == "packs":
        return _run_packs_command(repo_root, command_args)
    if token == "profiles":
        return _run_profiles_command(repo_root)
    if token == "diag":
        return _run_diag_command(repo_root, product_id=product_id, mode_id=mode_id)
    return None


def appshell_main(
    *,
    product_id: str,
    argv: Sequence[str] | None = None,
    repo_root_hint: str = ".",
    legacy_main: Callable[[Sequence[str]], int] | None = None,
    legacy_accepts_repo_root: bool = False,
) -> int:
    shell_args = parse_appshell_args(product_id=str(product_id).strip(), argv=argv)
    repo_root = resolve_repo_root(shell_args.repo_root, repo_root_hint=repo_root_hint)
    mode_id = normalize_mode(product_id=str(product_id).strip(), requested_mode=shell_args.mode)
    command_rows = build_root_command_descriptors(str(product_id).strip())
    panel_rows = build_tui_panel_descriptors(str(product_id).strip())

    if shell_args.help_requested:
        print(format_help_text(str(product_id).strip(), command_rows))
        return EXIT_SUCCESS

    if bool(shell_args.descriptor) or str(shell_args.descriptor_file).strip():
        _print_json(
            emit_descriptor_payload(
                repo_root,
                product_id=str(product_id).strip(),
                descriptor_file=str(shell_args.descriptor_file),
            )
        )
        return EXIT_SUCCESS

    if bool(shell_args.version):
        _print_json(build_version_payload(repo_root, product_id=str(product_id).strip()))
        return EXIT_SUCCESS

    handled = _handle_root_command(
        repo_root,
        product_id=str(product_id).strip(),
        mode_id=str(mode_id),
        command=str(shell_args.command),
        command_args=list(shell_args.command_args),
    )
    if handled is not None:
        payload, exit_code = handled
        _print_json(payload)
        return exit_code

    supported_modes = supported_modes_for_product(str(product_id).strip())
    if bool(shell_args.mode_requested) and str(mode_id).strip() not in supported_modes:
        _print_json(
            _refusal(
                "refusal.debug.mode_unsupported",
                "requested shell mode is not supported by this product",
                "Choose one of the declared AppShell modes for the product.",
                product_id=str(product_id).strip(),
                mode_id=str(mode_id).strip(),
                supported_mode_ids=list(supported_modes),
            )
        )
        return EXIT_REFUSAL

    if bool(shell_args.mode_requested) and str(mode_id).strip() == "tui":
        _print_json(build_mode_stub(str(product_id).strip(), "tui", command_rows, panel_rows))
        return EXIT_SUCCESS

    if bool(shell_args.mode_requested) and str(mode_id).strip() == "rendered" and str(product_id).strip() != "client":
        _print_json(
            _refusal(
                "refusal.debug.rendered_client_only",
                "rendered mode is client-only",
                "Use --mode cli or --mode tui for this product.",
                product_id=str(product_id).strip(),
            )
        )
        return EXIT_REFUSAL

    if legacy_main is None:
        _print_json(build_mode_stub(str(product_id).strip(), str(mode_id).strip(), command_rows, panel_rows))
        return EXIT_SUCCESS

    delegate_args = list(shell_args.remainder)
    mode_tokens = legacy_mode_args(str(product_id).strip(), str(mode_id).strip()) if bool(shell_args.mode_requested) else []
    if mode_tokens:
        delegate_args = list(mode_tokens) + delegate_args
    if legacy_accepts_repo_root:
        delegate_args = ["--repo-root", repo_root] + delegate_args
    return int(legacy_main(delegate_args))


__all__ = [
    "EXIT_CONTRACT",
    "EXIT_INTERNAL",
    "EXIT_PACK",
    "EXIT_REFUSAL",
    "EXIT_SUCCESS",
    "EXIT_TRANSPORT",
    "EXIT_USAGE",
    "appshell_main",
]
