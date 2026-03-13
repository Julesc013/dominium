#!/usr/bin/env python3
"""Generate deterministic AppShell CLI reference from the command registry."""

from __future__ import annotations

import argparse
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.appshell.command_registry import load_command_registry
from src.appshell.commands.command_engine import REFUSAL_TO_EXIT_REGISTRY_REL
from src.tools import TOOL_REFERENCE_PATH, build_tool_surface_report


def _read_json(path: str) -> tuple[dict, str]:
    try:
        import json

        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _load_refusal_mappings(repo_root: str) -> list[dict]:
    payload, error = _read_json(os.path.join(repo_root, REFUSAL_TO_EXIT_REGISTRY_REL))
    if error:
        return []
    rows = [dict(row) for row in list((dict(payload.get("record") or {})).get("mappings") or []) if isinstance(row, dict)]
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("refusal_code", "") or row.get("refusal_prefix", "")),
            int(row.get("exit_code", 0) or 0),
        ),
    )


def _command_sort_key(row: dict) -> tuple[object, ...]:
    command_path = str(row.get("command_path", "")).strip()
    return (
        command_path.endswith(".*"),
        command_path.count(" "),
        command_path,
        str(row.get("command_id", "")).strip(),
    )


def _rows_for_products(command_rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in command_rows:
        for product_id in sorted(set(str(item).strip() for item in list(row.get("product_ids") or []) if str(item).strip())):
            out.setdefault(product_id, []).append(dict(row))
    return dict((key, sorted(value, key=_command_sort_key)) for key, value in sorted(out.items()))


def _group_title(command_path: str) -> str:
    token = str(command_path or "").strip().split(" ", 1)[0]
    return {
        "compat-status": "General",
        "console": "Console",
        "descriptor": "General",
        "diag": "Diagnostics",
        "help": "General",
        "packs": "Packs",
        "profiles": "Profiles",
        "validate": "Validation",
        "verify": "Packs",
        "version": "General",
    }.get(token, "Additional")


def generate_cli_reference(repo_root: str) -> str:
    registry_payload, error = load_command_registry(repo_root)
    if error:
        raise ValueError(error)
    command_rows = [dict(row) for row in list((dict(registry_payload.get("record") or {})).get("commands") or [])]
    refusal_rows = _load_refusal_mappings(repo_root)
    product_rows = _rows_for_products(command_rows)
    root_rows = [row for row in command_rows if not str(row.get("command_path", "")).strip().endswith(".*")]
    namespace_rows = [row for row in command_rows if str(row.get("command_path", "")).strip().endswith(".*")]
    grouped_rows: dict[str, list[dict]] = {}
    for row in sorted(root_rows, key=_command_sort_key):
        grouped_rows.setdefault(_group_title(str(row.get("command_path", "")).strip()), []).append(row)

    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-14",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: release CLI reference regenerated from AppShell registry and DIST-5 tooling",
        "",
        "# CLI Reference",
        "",
        "This reference is generated from `data/registries/command_registry.json`,",
        "`data/registries/refusal_to_exit_registry.json`, and the stable tool umbrella surface.",
        "",
        "## Getting Started",
        "",
        "```text",
        "help",
        "compat-status",
        "packs verify --root .",
        "launcher start --seed 456",
        "diag capture",
        "bin/setup instance export --instance-id default --out exports/default.instance.bundle",
        "```",
        "",
        "## Shared Commands",
    ]
    for group_name in sorted(grouped_rows):
        lines.extend(
            [
                "",
                "### {}".format(group_name),
                "",
                "| Command | Description | Refusals |",
                "| --- | --- | --- |",
            ]
        )
        for row in grouped_rows[group_name]:
            lines.append(
                "| `{}` | {} | {} |".format(
                    str(row.get("command_path", "")).strip(),
                    str(row.get("description", "")).strip(),
                    ", ".join("`{}`".format(code) for code in list(row.get("refusal_codes") or [])) or "-",
                )
            )

    lines.extend(
        [
            "",
            "## Namespaces",
            "",
            "| Namespace | Products | Description |",
            "| --- | --- | --- |",
        ]
    )
    for row in sorted(namespace_rows, key=_command_sort_key):
        lines.append(
            "| `{}` | {} | {} |".format(
                str(row.get("command_path", "")).strip(),
                ", ".join("`{}`".format(product_id) for product_id in list(row.get("product_ids") or [])),
                str(row.get("description", "")).strip(),
            )
        )

    lines.extend(["", "## Refusal To Exit Mapping", "", "| Refusal Match | Exit Code | Description |", "| --- | --- | --- |"])
    for row in refusal_rows:
        label = str(row.get("refusal_code", "")).strip() or "{}*".format(str(row.get("refusal_prefix", "")).strip())
        lines.append("| `{}` | `{}` | {} |".format(label, int(row.get("exit_code", 0) or 0), str(row.get("description", "")).strip()))

    lines.append("")
    lines.append("## Product Views")
    for product_id, rows in product_rows.items():
        lines.extend(["", "### `{}`".format(product_id), ""])
        for row in rows:
            lines.append("- `{}`: {}".format(str(row.get("command_path", "")).strip(), str(row.get("description", "")).strip()))

    lines.extend(
        [
            "",
            "## UX Notes",
            "",
            "- Use `help <topic>` for a narrower command view without exposing internal ids in the default flow.",
            "- Refusals should always include a stable refusal code and a remediation hint.",
            "- Use `--json` when you need machine-readable status output from launcher and setup legacy surfaces.",
        ]
    )

    return "\n".join(lines) + "\n"


def generate_tool_reference(repo_root: str) -> str:
    report = build_tool_surface_report(repo_root)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-ARCHIVE",
        "Replacement Target: release tool reference regenerated from TOOL-SURFACE-0 tooling",
        "",
        "# Tool Reference",
        "",
        "Use the stable umbrella form:",
        "",
        "```text",
        "dom <area> <command> ...",
        "```",
        "",
    ]
    for area_row in list(report.get("areas") or []):
        area_id = str(dict(area_row).get("area_id", "")).strip()
        lines.extend(["## `{}`".format(area_id), "", str(dict(area_row).get("description", "")).strip(), ""])
        matched = [dict(row) for row in list(report.get("rows") or []) if str(dict(row).get("area_id", "")).strip() == area_id]
        for row in matched:
            lines.append("- `{}`: {}".format(str(row.get("command_path", "")).strip(), str(row.get("description", "")).strip()))
        if not matched:
            lines.append("- `dom {}`: namespace reserved; no wrapped commands are currently registered".format(area_id))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic AppShell CLI reference.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--output-path", default=os.path.join("docs", "appshell", "CLI_REFERENCE.md"))
    parser.add_argument("--tool-output-path", default=TOOL_REFERENCE_PATH)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    output_path = str(args.output_path)
    if not os.path.isabs(output_path):
        output_path = os.path.join(repo_root, output_path)
    tool_output_path = str(args.tool_output_path)
    if not os.path.isabs(tool_output_path):
        tool_output_path = os.path.join(repo_root, tool_output_path)
    text = generate_cli_reference(repo_root)
    tool_text = generate_tool_reference(repo_root)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.makedirs(os.path.dirname(tool_output_path), exist_ok=True)
    with open(tool_output_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(tool_text)
    print(output_path.replace("\\", "/"))
    print(tool_output_path.replace("\\", "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
