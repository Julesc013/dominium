"""Parse AppShell common arguments without consuming product-specific surfaces."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Sequence


ROOT_COMMANDS = (
    "help",
    "version",
    "descriptor",
    "compat-status",
    "profiles",
    "packs",
    "verify",
    "diag",
    "console",
)


@dataclass(frozen=True)
class AppShellArgs:
    product_id: str
    repo_root: str
    mode: str
    mode_requested: bool
    tui_layout: str
    ipc_enabled: bool
    ipc_manifest_path: str
    session_id: str
    descriptor: bool
    descriptor_file: str
    version: bool
    help_requested: bool
    command: str
    command_args: List[str]
    remainder: List[str]
    raw_args: List[str]


def parse_appshell_args(product_id: str, argv: Sequence[str] | None) -> AppShellArgs:
    raw_args = list(argv or [])
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--mode", default="")
    parser.add_argument("--tui-layout", default="")
    parser.add_argument("--ipc", default="")
    parser.add_argument("--ipc-manifest-path", default="")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--descriptor", action="store_true")
    parser.add_argument("--descriptor-file", default="")
    parser.add_argument("--version", action="store_true")
    parsed, remainder = parser.parse_known_args(raw_args)
    help_requested = any(token in {"-h", "--help"} for token in raw_args)
    filtered_remainder = [token for token in list(remainder) if token not in {"-h", "--help"}]
    command = ""
    command_args: List[str] = []
    if filtered_remainder:
        token = str(filtered_remainder[0]).strip()
        if token and not token.startswith("-"):
            command = token
            command_args = list(filtered_remainder[1:])
            filtered_remainder = []
    if command == "help":
        help_requested = True
    return AppShellArgs(
        product_id=str(product_id).strip(),
        repo_root=str(parsed.repo_root or ".").strip() or ".",
        mode=str(parsed.mode or "").strip().lower(),
        mode_requested=bool(str(parsed.mode or "").strip()),
        tui_layout=str(parsed.tui_layout or "").strip(),
        ipc_enabled=str(parsed.ipc or "").strip().lower() in {"1", "true", "yes", "on"},
        ipc_manifest_path=str(parsed.ipc_manifest_path or "").strip(),
        session_id=str(parsed.session_id or "").strip(),
        descriptor=bool(parsed.descriptor),
        descriptor_file=str(parsed.descriptor_file or "").strip(),
        version=bool(parsed.version),
        help_requested=bool(help_requested),
        command=str(command),
        command_args=list(command_args),
        remainder=list(filtered_remainder),
        raw_args=raw_args,
    )


__all__ = ["AppShellArgs", "ROOT_COMMANDS", "parse_appshell_args"]
