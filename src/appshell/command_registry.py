"""Deterministic shared AppShell command descriptors."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable, List


ROOT_COMMAND_ROWS = (
    ("command.help", "help", "Show AppShell help and shared command surfaces."),
    ("command.version", "version", "Emit deterministic product version metadata."),
    ("command.descriptor", "descriptor", "Emit the CAP-NEG endpoint descriptor."),
    ("command.compat_status", "compat-status", "Run offline compatibility verification against a pack set."),
    ("command.profiles", "profiles", "List available profile bundle surfaces."),
    ("command.packs", "packs", "List available pack surfaces."),
    ("command.verify", "verify", "Run offline verification for pack/profile inputs."),
    ("command.diag", "diag", "Emit deterministic diagnostic shell metadata."),
)


def _fingerprint(payload: dict) -> str:
    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _supported_modes(product_id: str) -> List[str]:
    if str(product_id).strip() == "client":
        return ["cli", "rendered", "tui"]
    if str(product_id).strip() in {"engine", "server"}:
        return ["cli", "headless", "tui"]
    return ["cli", "tui"]


def build_root_command_descriptors(product_id: str) -> List[dict]:
    product_token = str(product_id).strip()
    mode_ids = _supported_modes(product_token)
    rows = []
    for command_id, command_path, description in ROOT_COMMAND_ROWS:
        payload = {
            "schema_version": "1.0.0",
            "command_id": command_id,
            "command_path": command_path,
            "product_ids": [product_token],
            "description": description,
            "supported_mode_ids": list(mode_ids),
            "deterministic_fingerprint": "",
            "extensions": {
                "official.source": "APPSHELL-0"
            },
        }
        payload["deterministic_fingerprint"] = _fingerprint(payload)
        rows.append(payload)
    subtree = {
        "schema_version": "1.0.0",
        "command_id": "command.{}.subtree".format(product_token.replace(".", "_")),
        "command_path": "{}.*".format(product_token),
        "product_ids": [product_token],
        "description": "Reserved product-specific AppShell subtree for {}.".format(product_token),
        "supported_mode_ids": list(mode_ids),
        "deterministic_fingerprint": "",
        "extensions": {
            "official.source": "APPSHELL-0"
        },
    }
    subtree["deterministic_fingerprint"] = _fingerprint(subtree)
    rows.append(subtree)
    return rows


def build_tui_panel_descriptors(product_id: str) -> List[dict]:
    payload = {
        "schema_version": "1.0.0",
        "panel_id": "panel.{}.console".format(str(product_id).strip().replace(".", "_")),
        "product_id": str(product_id).strip(),
        "title": "{} Console".format(str(product_id).strip()),
        "position_hint": "main",
        "deterministic_fingerprint": "",
        "extensions": {
            "official.source": "APPSHELL-0"
        },
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return [payload]


def format_help_text(product_id: str, command_rows: Iterable[dict]) -> str:
    commands = list(command_rows or [])
    lines = [
        "Dominium AppShell",
        "product_id: {}".format(str(product_id).strip()),
        "root commands:",
    ]
    for row in commands:
        command_path = str(dict(row).get("command_path", "")).strip()
        description = str(dict(row).get("description", "")).strip()
        if not command_path or command_path.endswith(".*"):
            continue
        lines.append("  {:<14} {}".format(command_path, description))
    lines.append("product subtree:")
    lines.append("  {}.*".format(str(product_id).strip()))
    return "\n".join(lines)


__all__ = [
    "build_root_command_descriptors",
    "build_tui_panel_descriptors",
    "format_help_text",
]
