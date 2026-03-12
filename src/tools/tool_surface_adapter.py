"""Deterministic TOOL-SURFACE-0 command catalog and adapter helpers."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from typing import Iterable, Mapping, Sequence

from src.appshell.command_registry import COMMAND_REGISTRY_REL, load_command_registry
from src.meta_extensions_engine import normalize_extensions_tree


DOM_PRODUCT_ID = "tool.attach_console_stub"
TOOL_SURFACE_MAP_PATH = "docs/audit/TOOL_SURFACE_MAP.md"
TOOL_SURFACE_FINAL_PATH = "docs/audit/TOOL_SURFACE_FINAL.md"
TOOL_REFERENCE_PATH = "docs/appshell/TOOL_REFERENCE.md"
REPO_INVENTORY_PATH = "data/audit/repo_inventory.json"
TOOL_ADAPTER_OUTPUT_SCHEMA_ID = "dominium.schema.appshell.output.tool_adapter_result"
TOOL_PASSTHROUGH_ARGS_SCHEMA_ID = "dominium.schema.appshell.args.tool_passthrough"
TOOL_SURFACE_COMMAND_PREFIX = "command.dom_"
TOOL_SURFACE_SOURCE_TAG = "TOOL-SURFACE-0"

AREA_ORDER = (
    "geo",
    "worldgen",
    "earth",
    "sol",
    "gal",
    "logic",
    "sys",
    "proc",
    "pack",
    "lib",
    "compat",
    "diag",
    "server",
    "client",
)

AREA_DESCRIPTIONS = {
    "geo": "Deterministic GEO replay, identity, overlay, and metric tooling.",
    "worldgen": "World generation replay, verification, and stress helpers.",
    "earth": "Earth-focused replay, stress, and verification tools.",
    "sol": "Illumination and orbital proxy replay tooling.",
    "gal": "Galaxy proxy and compact-object replay tooling.",
    "logic": "Logic replay, compile, and stress tooling.",
    "sys": "System composition replay, explain, and stress tooling.",
    "proc": "Process, capsule, and drift replay tooling.",
    "pack": "Pack inventory, verification, and capability inspection commands.",
    "lib": "Library bundle and save verification tooling.",
    "compat": "Capability negotiation descriptors, replay, and interop tooling.",
    "diag": "Repro bundle capture, snapshot, and replay tooling.",
    "server": "Server replay and inspection tooling.",
    "client": "Client-facing AppShell inspection commands.",
}

SCRIPT_AREA_SPECS = (
    {"area_id": "geo", "root_relpath": "tools/geo", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "worldgen", "root_relpath": "tools/worldgen", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "earth", "root_relpath": "tools/earth", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "earth", "root_relpath": "tools/worldgen", "include_pattern": r"^tool_(replay_(climate|hydrology|illumination|material|sky|tide|water|wind)|verify_earth_surface).+\.py$"},
    {"area_id": "sol", "root_relpath": "tools/astro", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "gal", "root_relpath": "tools/worldgen", "include_pattern": r"^tool_replay_galaxy_(objects|proxies)\.py$"},
    {"area_id": "logic", "root_relpath": "tools/logic", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "sys", "root_relpath": "tools/system", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "proc", "root_relpath": "tools/process", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "lib", "root_relpath": "tools/lib", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "compat", "root_relpath": "tools/compat", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "diag", "root_relpath": "tools/diag", "include_pattern": r"^tool_.*\.py$"},
    {"area_id": "server", "root_relpath": "tools/server", "include_pattern": r"^tool_.*\.py$"},
)

EXPLICIT_SCRIPT_ROWS = (
    {
        "area_id": "pack",
        "tool_relpath": "tools/pack/capability_inspect.py",
        "command_slug": "capability-inspect",
        "description": "Inspect declared pack capabilities, overlaps, and dependency closure.",
    },
    {
        "area_id": "pack",
        "tool_relpath": "tools/pack/pack_validate.py",
        "command_slug": "validate-manifest",
        "description": "Run the legacy pack manifest validator through the stable umbrella.",
    },
    {
        "area_id": "pack",
        "tool_relpath": "tools/pack/migrate_capability_gating.py",
        "command_slug": "migrate-capability-gating",
        "description": "Run the legacy capability gating migration helper through the stable umbrella.",
    },
)

ALIAS_ROWS = (
    {"area_id": "pack", "command_slug": "list", "alias_command_tokens": ["packs", "list"], "alias_product_id": DOM_PRODUCT_ID},
    {"area_id": "pack", "command_slug": "verify", "alias_command_tokens": ["packs", "verify"], "alias_product_id": DOM_PRODUCT_ID},
    {"area_id": "pack", "command_slug": "build-lock", "alias_command_tokens": ["packs", "build-lock"], "alias_product_id": DOM_PRODUCT_ID},
    {"area_id": "compat", "command_slug": "status", "alias_command_tokens": ["compat-status"], "alias_product_id": DOM_PRODUCT_ID},
    {"area_id": "diag", "command_slug": "capture", "alias_command_tokens": ["diag", "capture"], "alias_product_id": DOM_PRODUCT_ID},
    {"area_id": "diag", "command_slug": "snapshot", "alias_command_tokens": ["diag", "snapshot"], "alias_product_id": DOM_PRODUCT_ID},
    {"area_id": "client", "command_slug": "descriptor", "alias_command_tokens": ["descriptor"], "alias_product_id": "client"},
    {"area_id": "client", "command_slug": "compat-status", "alias_command_tokens": ["compat-status"], "alias_product_id": "client"},
    {"area_id": "client", "command_slug": "console", "alias_command_tokens": ["console"], "alias_product_id": "client"},
    {"area_id": "server", "command_slug": "descriptor", "alias_command_tokens": ["descriptor"], "alias_product_id": "server"},
    {"area_id": "server", "command_slug": "compat-status", "alias_command_tokens": ["compat-status"], "alias_product_id": "server"},
    {"area_id": "server", "command_slug": "console", "alias_command_tokens": ["console"], "alias_product_id": "server"},
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return _token(path).replace("\\", "/")


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted({_token(value) for value in list(values or []) if _token(value)})


def _stable_fingerprint(payload: Mapping[str, object]) -> str:
    body = normalize_extensions_tree(dict(payload or {}))
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
    return normalize_extensions_tree(payload), ""


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _repo_inventory_map(repo_root: str) -> dict[str, dict]:
    payload, error = _read_json(os.path.join(repo_root, REPO_INVENTORY_PATH.replace("/", os.sep)))
    if error:
        return {}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return {}
    out: dict[str, dict] = {}
    for row in entries:
        if not isinstance(row, Mapping):
            continue
        rel_path = _norm(row.get("path", ""))
        if rel_path:
            out[rel_path] = dict(row)
    return out


def _module_doc_summary(abs_path: str) -> str:
    text = _read_text(abs_path)
    if not text:
        return ""
    try:
        module = ast.parse(text, filename=abs_path)
    except SyntaxError:
        return ""
    docstring = ast.get_docstring(module) or ""
    line = docstring.splitlines()[0].strip() if docstring else ""
    return line.rstrip(".")


def _supports_repo_root(abs_path: str) -> bool:
    return '--repo-root' in _read_text(abs_path)


def _script_command_slug(rel_path: str, explicit_slug: str = "") -> str:
    if _token(explicit_slug):
        return _token(explicit_slug)
    stem = os.path.splitext(os.path.basename(rel_path))[0]
    if stem.startswith("tool_"):
        stem = stem[5:]
    return stem.replace("_", "-")


def _module_name_for_path(rel_path: str) -> str:
    return _norm(os.path.splitext(rel_path)[0]).replace("/", ".")


def _command_id_for(area_id: str, command_slug: str) -> str:
    return "{}{}_{}".format(TOOL_SURFACE_COMMAND_PREFIX, _token(area_id), _token(command_slug).replace("-", "_"))


def _stable_id_for(area_id: str, command_slug: str) -> str:
    return "dom.{}.{}.v1".format(_token(area_id), _token(command_slug))


def _stability_payload() -> dict:
    payload = {
        "schema_version": "1.0.0",
        "stability_class_id": "provisional",
        "rationale": "Unified tool umbrella command rows remain provisional while the tool surface converges for release governance.",
        "future_series": "APPSHELL-TOOLS",
        "replacement_target": "Replace provisional tool surface adapters with release-pinned AppShell tool registry semantics.",
        "contract_id": "",
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = _stable_fingerprint(payload)
    return payload


def _base_command_row(command_id: str, command_path: str, description: str, handler_id: str, output_schema_id: str) -> dict:
    return {
        "schema_version": "1.1.0",
        "command_id": _token(command_id),
        "command_path": _token(command_path),
        "product_ids": [DOM_PRODUCT_ID],
        "description": _token(description),
        "supported_mode_ids": ["cli", "headless", "rendered", "tui"],
        "args_schema_id": TOOL_PASSTHROUGH_ARGS_SCHEMA_ID,
        "output_schema_id": _token(output_schema_id),
        "refusal_codes": ["refusal.io.invalid_args"],
        "exit_code_mapping_id": "exit.refusal",
        "handler_id": _token(handler_id),
        "deterministic_fingerprint": "",
        "extensions": {"official.source": TOOL_SURFACE_SOURCE_TAG},
        "stability": _stability_payload(),
    }


def _lookup_alias_descriptor(repo_root: str, product_id: str, alias_command_tokens: Sequence[str]) -> dict:
    registry_payload, error = load_command_registry(repo_root)
    if error:
        return {}
    target_path = " ".join(str(token).strip() for token in list(alias_command_tokens or []) if str(token).strip())
    for row in list((dict(registry_payload.get("record") or {})).get("commands") or []):
        row_map = dict(row or {})
        if _token(row_map.get("command_path")) != target_path:
            continue
        if _token(product_id) not in _sorted_tokens(row_map.get("product_ids")):
            continue
        return row_map
    return {}


def _discover_script_rows(repo_root: str) -> list[dict]:
    inventory_map = _repo_inventory_map(repo_root)
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for spec in SCRIPT_AREA_SPECS:
        area_id = _token(spec.get("area_id"))
        root_relpath = _norm(spec.get("root_relpath"))
        pattern = re.compile(str(spec.get("include_pattern")))
        abs_root = os.path.join(repo_root, root_relpath.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for filename in sorted(os.listdir(abs_root)):
            if not pattern.match(filename):
                continue
            rel_path = _norm(os.path.join(root_relpath, filename))
            command_slug = _script_command_slug(rel_path)
            key = (area_id, command_slug)
            if key in seen:
                continue
            seen.add(key)
            abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
            inventory_row = dict(inventory_map.get(rel_path) or {})
            description = _module_doc_summary(abs_path) or "Run {}.".format(command_slug.replace("-", " "))
            row = {
                "area_id": area_id,
                "command_slug": command_slug,
                "stable_id": _stable_id_for(area_id, command_slug),
                "command_path": "dom {} {}".format(area_id, command_slug),
                "adapter_kind": "python_subprocess",
                "tool_relpath": rel_path,
                "tool_module": _module_name_for_path(rel_path),
                "description": description,
                "required_capabilities": [],
                "refusal_codes": ["refusal.io.invalid_args"],
                "output_schema_id": TOOL_ADAPTER_OUTPUT_SCHEMA_ID,
                "virtual_path_policy": "repo_relative_cwd",
                "pack_context_mode": "repo_root_context_only",
                "offline_only": True,
                "inject_repo_root_arg": _supports_repo_root(abs_path),
                "product": _token(inventory_row.get("product")) or "tool",
                "layer": _token(inventory_row.get("layer")) or "tool",
                "function": _token(inventory_row.get("responsibility")) or description,
                "linked_libraries": _sorted_tokens(inventory_row.get("linked_libraries")),
                "platform_specific": bool(inventory_row.get("platform_specific", False)),
                "uses_wallclock": bool(inventory_row.get("uses_wallclock", False)),
                "uses_float_in_truth": bool(inventory_row.get("uses_float_in_truth", False)),
                "uses_direct_paths": bool(inventory_row.get("uses_direct_paths", False)),
                "entrypoints": [str(item).strip() for item in list(inventory_row.get("entrypoints") or []) if str(item).strip()],
                "deterministic_fingerprint": "",
            }
            row["deterministic_fingerprint"] = _stable_fingerprint(row)
            rows.append(row)
    for spec in EXPLICIT_SCRIPT_ROWS:
        area_id = _token(spec.get("area_id"))
        rel_path = _norm(spec.get("tool_relpath"))
        command_slug = _script_command_slug(rel_path, explicit_slug=_token(spec.get("command_slug")))
        key = (area_id, command_slug)
        if key in seen:
            continue
        seen.add(key)
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        inventory_row = dict(inventory_map.get(rel_path) or {})
        row = {
            "area_id": area_id,
            "command_slug": command_slug,
            "stable_id": _stable_id_for(area_id, command_slug),
            "command_path": "dom {} {}".format(area_id, command_slug),
            "adapter_kind": "python_subprocess",
            "tool_relpath": rel_path,
            "tool_module": _module_name_for_path(rel_path),
            "description": _token(spec.get("description")) or _module_doc_summary(abs_path),
            "required_capabilities": [],
            "refusal_codes": ["refusal.io.invalid_args"],
            "output_schema_id": TOOL_ADAPTER_OUTPUT_SCHEMA_ID,
            "virtual_path_policy": "repo_relative_cwd",
            "pack_context_mode": "repo_root_context_only",
            "offline_only": True,
            "inject_repo_root_arg": _supports_repo_root(abs_path),
            "product": _token(inventory_row.get("product")) or "tool",
            "layer": _token(inventory_row.get("layer")) or "tool",
            "function": _token(inventory_row.get("responsibility")) or _token(spec.get("description")),
            "linked_libraries": _sorted_tokens(inventory_row.get("linked_libraries")),
            "platform_specific": bool(inventory_row.get("platform_specific", False)),
            "uses_wallclock": bool(inventory_row.get("uses_wallclock", False)),
            "uses_float_in_truth": bool(inventory_row.get("uses_float_in_truth", False)),
            "uses_direct_paths": bool(inventory_row.get("uses_direct_paths", False)),
            "entrypoints": [str(item).strip() for item in list(inventory_row.get("entrypoints") or []) if str(item).strip()],
            "deterministic_fingerprint": "",
        }
        row["deterministic_fingerprint"] = _stable_fingerprint(row)
        rows.append(row)
    return sorted(rows, key=lambda item: (_token(item.get("area_id")), _token(item.get("command_slug")), _token(item.get("tool_relpath"))))


def _discover_alias_rows(repo_root: str) -> list[dict]:
    rows: list[dict] = []
    for spec in ALIAS_ROWS:
        area_id = _token(spec.get("area_id"))
        command_slug = _token(spec.get("command_slug"))
        alias_command_tokens = [str(token).strip() for token in list(spec.get("alias_command_tokens") or []) if str(token).strip()]
        alias_product_id = _token(spec.get("alias_product_id")) or DOM_PRODUCT_ID
        alias_row = _lookup_alias_descriptor(repo_root, alias_product_id, alias_command_tokens)
        description = _token(alias_row.get("description")) or "Alias AppShell command {}.".format(" ".join(alias_command_tokens))
        row = {
            "area_id": area_id,
            "command_slug": command_slug,
            "stable_id": _stable_id_for(area_id, command_slug),
            "command_path": "dom {} {}".format(area_id, command_slug),
            "adapter_kind": "appshell_alias",
            "tool_relpath": "",
            "tool_module": "appshell.command.{}".format(".".join(alias_command_tokens)),
            "description": description,
            "required_capabilities": [],
            "refusal_codes": _sorted_tokens(alias_row.get("refusal_codes")) or ["refusal.io.invalid_args"],
            "output_schema_id": _token(alias_row.get("output_schema_id")) or TOOL_ADAPTER_OUTPUT_SCHEMA_ID,
            "virtual_path_policy": "appshell_bootstrap_context",
            "pack_context_mode": "appshell_bootstrap_context",
            "offline_only": True,
            "inject_repo_root_arg": False,
            "alias_command_tokens": alias_command_tokens,
            "alias_product_id": alias_product_id,
            "product": alias_product_id,
            "layer": "tool",
            "function": description,
            "linked_libraries": [],
            "platform_specific": False,
            "uses_wallclock": False,
            "uses_float_in_truth": False,
            "uses_direct_paths": False,
            "entrypoints": [],
            "deterministic_fingerprint": "",
        }
        row["deterministic_fingerprint"] = _stable_fingerprint(row)
        rows.append(row)
    return sorted(rows, key=lambda item: (_token(item.get("area_id")), _token(item.get("command_slug"))))


def build_tool_surface_rows(repo_root: str) -> list[dict]:
    rows = _discover_alias_rows(repo_root) + _discover_script_rows(repo_root)
    return sorted(rows, key=lambda item: (_token(item.get("area_id")), _token(item.get("command_slug")), _token(item.get("tool_relpath")), _token(item.get("alias_product_id"))))


def _build_area_rows(rows: Sequence[Mapping[str, object]]) -> list[dict]:
    out = []
    counts: dict[str, int] = {}
    for row in rows:
        counts[_token(row.get("area_id"))] = counts.get(_token(row.get("area_id")), 0) + 1
    for area_id in AREA_ORDER:
        out.append(
            {
                "area_id": area_id,
                "command_path": "dom {}".format(area_id),
                "command_count": int(counts.get(area_id, 0)),
                "description": AREA_DESCRIPTIONS.get(area_id, ""),
                "deterministic_fingerprint": _stable_fingerprint(
                    {"area_id": area_id, "command_count": int(counts.get(area_id, 0)), "description": AREA_DESCRIPTIONS.get(area_id, "")}
                ),
            }
        )
    return out


def build_tool_surface_report(repo_root: str) -> dict:
    rows = build_tool_surface_rows(repo_root)
    registry_payload, error = load_command_registry(repo_root)
    registered_rows = []
    if not error:
        registered_rows = [
            dict(row)
            for row in list((dict(registry_payload.get("record") or {})).get("commands") or [])
            if _token(dict(row).get("command_path")).startswith("dom ")
            and DOM_PRODUCT_ID in _sorted_tokens(dict(row).get("product_ids"))
        ]
    registered_map = {_token(row.get("command_path")): dict(row) for row in registered_rows}
    discovered_paths = {_token(row.get("command_path")) for row in rows}
    missing_registry = [dict(row) for row in rows if _token(row.get("command_path")) not in registered_map]
    missing_targets = []
    for row in rows:
        row_map = dict(row)
        rel_path = _token(row_map.get("tool_relpath"))
        if not rel_path:
            continue
        if os.path.isfile(os.path.join(repo_root, rel_path.replace("/", os.sep))):
            continue
        missing_targets.append(row_map)
    extra_registry = [dict(row) for row in registered_rows if _token(row.get("command_path")) not in discovered_paths and _token(row.get("handler_id")) == "tool_surface_adapter"]
    report = {
        "result": "complete",
        "tool_surface_id": "tool.surface.v1",
        "inventory_source": REPO_INVENTORY_PATH,
        "areas": _build_area_rows(rows),
        "rows": rows,
        "registered_dom_command_count": len(registered_rows),
        "wrapped_tool_count": len(rows),
        "alias_count": sum(1 for row in rows if _token(row.get("adapter_kind")) == "appshell_alias"),
        "subprocess_count": sum(1 for row in rows if _token(row.get("adapter_kind")) == "python_subprocess"),
        "missing_registry": sorted(missing_registry, key=lambda item: _token(item.get("command_path"))),
        "missing_targets": sorted(missing_targets, key=lambda item: _token(item.get("tool_relpath"))),
        "extra_registry": sorted(extra_registry, key=lambda item: _token(item.get("command_path"))),
        "surface_fingerprint": "",
    }
    report["surface_fingerprint"] = _stable_fingerprint(report)
    return report


def _tool_surface_command_rows(repo_root: str) -> list[dict]:
    report = build_tool_surface_report(repo_root)
    rows = [dict(item) for item in list(report.get("rows") or [])]
    out = []
    root_row = _base_command_row(
        "command.dom_root",
        "dom",
        "List the stable Dominium tool namespaces and wrapped commands.",
        "tool_surface_root_help",
        "dominium.schema.appshell.output.help_text",
    )
    root_row["args_schema_id"] = "dominium.schema.appshell.args.none"
    root_row["exit_code_mapping_id"] = "exit.success"
    root_row["extensions"]["official.tool_surface"] = {
        "surface_role": "root",
        "area_id": "",
        "stable_id": "dom.root.v1",
        "virtual_path_policy": "appshell_bootstrap_context",
    }
    root_row["deterministic_fingerprint"] = _stable_fingerprint(root_row)
    out.append(root_row)
    for area_row in list(report.get("areas") or []):
        area_id = _token(area_row.get("area_id"))
        row = _base_command_row(
            "command.dom_{}".format(area_id),
            "dom {}".format(area_id),
            _token(area_row.get("description")) or "List {} commands.".format(area_id),
            "tool_surface_area_help",
            "dominium.schema.appshell.output.help_text",
        )
        row["args_schema_id"] = "dominium.schema.appshell.args.none"
        row["exit_code_mapping_id"] = "exit.success"
        row["extensions"]["official.tool_surface"] = {
            "surface_role": "area",
            "area_id": area_id,
            "stable_id": "dom.{}.index.v1".format(area_id),
            "virtual_path_policy": "appshell_bootstrap_context",
        }
        row["deterministic_fingerprint"] = _stable_fingerprint(row)
        out.append(row)
    for item in rows:
        area_id = _token(item.get("area_id"))
        command_slug = _token(item.get("command_slug"))
        row = _base_command_row(
            _command_id_for(area_id, command_slug),
            _token(item.get("command_path")),
            _token(item.get("description")),
            "tool_surface_adapter",
            _token(item.get("output_schema_id")) or TOOL_ADAPTER_OUTPUT_SCHEMA_ID,
        )
        row["refusal_codes"] = _sorted_tokens(item.get("refusal_codes")) or ["refusal.io.invalid_args"]
        row["extensions"]["official.tool_surface"] = {
            "surface_role": "leaf",
            "area_id": area_id,
            "stable_id": _token(item.get("stable_id")),
            "adapter_kind": _token(item.get("adapter_kind")),
            "tool_relpath": _token(item.get("tool_relpath")),
            "tool_module": _token(item.get("tool_module")),
            "required_capabilities": _sorted_tokens(item.get("required_capabilities")),
            "virtual_path_policy": _token(item.get("virtual_path_policy")),
            "pack_context_mode": _token(item.get("pack_context_mode")),
            "offline_only": bool(item.get("offline_only", True)),
            "inject_repo_root_arg": bool(item.get("inject_repo_root_arg", False)),
            "alias_command_tokens": [str(token).strip() for token in list(item.get("alias_command_tokens") or []) if str(token).strip()],
            "alias_product_id": _token(item.get("alias_product_id")),
            "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        }
        row["deterministic_fingerprint"] = _stable_fingerprint(row)
        out.append(row)
    return sorted(
        out,
        key=lambda row: (
            str(row.get("command_path", "")).endswith(".*"),
            str(row.get("command_path", "")).count(" "),
            str(row.get("command_path", "")),
            str(row.get("command_id", "")),
        ),
    )


def sync_command_registry_with_tool_surface(repo_root: str) -> dict:
    registry_path = os.path.join(repo_root, COMMAND_REGISTRY_REL.replace("/", os.sep))
    payload, error = _read_json(registry_path)
    if error:
        raise ValueError(error)
    record = dict(payload.get("record") or {})
    commands = [dict(row) for row in list(record.get("commands") or []) if isinstance(row, Mapping)]
    commands = [
        row
        for row in commands
        if not _token(row.get("command_id")).startswith(TOOL_SURFACE_COMMAND_PREFIX)
        and _token(row.get("command_id")) != "command.dom_root"
        and not (_token(row.get("command_id")).startswith("command.dom_") and _token(row.get("command_path")).startswith("dom "))
    ]
    commands.extend(_tool_surface_command_rows(repo_root))
    commands = sorted(
        [normalize_extensions_tree(dict(row)) for row in commands],
        key=lambda row: (
            str(row.get("command_path", "")).endswith(".*"),
            str(row.get("command_path", "")).count(" "),
            str(row.get("command_path", "")),
            str(row.get("command_id", "")),
        ),
    )
    record["commands"] = commands
    output = {"schema_id": _token(payload.get("schema_id")), "schema_version": _token(payload.get("schema_version")), "record": record}
    with open(registry_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return build_tool_surface_report(repo_root)


def tool_surface_row_from_command(row: Mapping[str, object]) -> dict:
    extensions = normalize_extensions_tree(dict(row.get("extensions") or {}))
    payload = dict(extensions.get("official.tool_surface") or {})
    payload["command_path"] = _token(row.get("command_path"))
    payload["description"] = _token(row.get("description"))
    payload["refusal_codes"] = _sorted_tokens(row.get("refusal_codes"))
    payload["output_schema_id"] = _token(row.get("output_schema_id"))
    payload["handler_id"] = _token(row.get("handler_id"))
    return payload


def _registered_dom_rows(repo_root: str) -> list[dict]:
    registry_payload, error = load_command_registry(repo_root)
    if error:
        return []
    rows = []
    for row in list((dict(registry_payload.get("record") or {})).get("commands") or []):
        row_map = dict(row or {})
        if DOM_PRODUCT_ID not in _sorted_tokens(row_map.get("product_ids")):
            continue
        if not _token(row_map.get("command_path")).startswith("dom"):
            continue
        rows.append(row_map)
    return sorted(rows, key=lambda item: (_token(item.get("command_path")), _token(item.get("command_id"))))


def format_tool_surface_root_help(repo_root: str) -> str:
    rows = _registered_dom_rows(repo_root)
    counts: dict[str, int] = {}
    for row in rows:
        command_path = _token(row.get("command_path"))
        parts = command_path.split()
        if len(parts) < 3 or parts[0] != "dom":
            continue
        area_id = parts[1]
        counts[area_id] = counts.get(area_id, 0) + 1
    lines = [
        "Dominium Tool Surface",
        "product_id: {}".format(DOM_PRODUCT_ID),
        "usage: dom <area> <command> [-- ...]",
        "areas:",
    ]
    for area_id in AREA_ORDER:
        lines.append(
            "  {:<18} {} ({})".format(
                "dom {}".format(area_id),
                AREA_DESCRIPTIONS.get(area_id, ""),
                "{} commands".format(int(counts.get(area_id, 0) or 0)),
            )
        )
    lines.append("run `dom <area>` to list commands in a namespace")
    return "\n".join(lines)


def format_tool_surface_area_help(repo_root: str, area_id: str) -> str:
    rows = [dict(row) for row in _registered_dom_rows(repo_root)]
    area_token = _token(area_id)
    lines = ["Dominium Tool Surface", "area: {}".format(area_token), "commands:"]
    matched = []
    prefix = "dom {} ".format(area_token)
    for row in rows:
        command_path = _token(row.get("command_path"))
        if command_path.startswith(prefix):
            matched.append(row)
    for row in matched:
        lines.append("  {:<36} {}".format(_token(row.get("command_path")), _token(row.get("description"))))
    if not matched:
        lines.append("  no wrapped commands are registered for this area")
    return "\n".join(lines)


def execute_tool_surface_subprocess(repo_root: str, row: Mapping[str, object], args: Sequence[str]) -> tuple[dict, int]:
    spec = tool_surface_row_from_command(row)
    rel_path = _token(spec.get("tool_relpath"))
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not rel_path or not os.path.isfile(abs_path):
        payload = {
            "result": "refused",
            "reason": "wrapped tool target is missing",
            "stable_id": _token(spec.get("stable_id")),
            "tool_relpath": rel_path,
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = _stable_fingerprint(payload)
        return payload, 2
    invocation = [sys.executable, rel_path]
    if bool(spec.get("inject_repo_root_arg", False)):
        invocation.extend(["--repo-root", "."])
    invocation.extend([str(token) for token in list(args or [])])
    completed = subprocess.run(
        invocation,
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=dict(os.environ, DOMINIUM_TOOL_SURFACE_STABLE_ID=_token(spec.get("stable_id"))),
    )
    stdout_text = str(completed.stdout or "")
    stderr_text = str(completed.stderr or "")
    stdout_kind = "empty"
    tool_output = None
    tool_output_text = ""
    if stdout_text.strip():
        try:
            tool_output = json.loads(stdout_text)
        except ValueError:
            stdout_kind = "text"
            tool_output_text = stdout_text
        else:
            stdout_kind = "json"
    payload = {
        "result": "complete" if int(completed.returncode) == 0 else "tool_error",
        "stable_id": _token(spec.get("stable_id")),
        "command_path": _token(spec.get("command_path")),
        "adapter_kind": "python_subprocess",
        "tool_relpath": rel_path,
        "tool_module": _token(spec.get("tool_module")),
        "invocation_args": ["python", rel_path] + [str(token) for token in invocation[2:]],
        "virtual_path_policy": _token(spec.get("virtual_path_policy")),
        "pack_context_mode": _token(spec.get("pack_context_mode")),
        "offline_only": bool(spec.get("offline_only", True)),
        "tool_exit_code": int(completed.returncode),
        "stdout_kind": stdout_kind,
        "tool_output": tool_output,
        "tool_output_text": tool_output_text,
        "stderr_text": stderr_text,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _stable_fingerprint(payload)
    return payload, int(completed.returncode)


def _render_tool_surface_map(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-ARCHIVE",
        "Replacement Target: release surface index regenerated from TOOL-SURFACE-0 tooling",
        "",
        "# Tool Surface Map",
        "",
        "Source: `data/audit/repo_inventory.json` + `src/tools/tool_surface_adapter.py`",
        "",
        "- Wrapped commands: `{}`".format(int(report.get("wrapped_tool_count", 0) or 0)),
        "- Alias commands: `{}`".format(int(report.get("alias_count", 0) or 0)),
        "- Subprocess adapters: `{}`".format(int(report.get("subprocess_count", 0) or 0)),
        "- Surface fingerprint: `{}`".format(_token(report.get("surface_fingerprint"))),
        "",
    ]
    for area_id in AREA_ORDER:
        lines.extend(["## `{}`".format(area_id), "", "| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |", "| --- | --- | --- | --- | --- | --- |"])
        matched = [dict(row) for row in list(report.get("rows") or []) if _token(dict(row).get("area_id")) == area_id]
        for row in matched:
            target = _token(row.get("tool_relpath")) or "appshell:{}:{}".format(_token(row.get("alias_product_id")), " ".join(list(row.get("alias_command_tokens") or [])))
            lines.append(
                "| `{}` | {} | `{}` | `{}` | `{}` | {} |".format(
                    target,
                    _token(row.get("function")) or _token(row.get("description")),
                    _token(row.get("command_path")),
                    _token(row.get("stable_id")),
                    _token(row.get("adapter_kind")),
                    ", ".join("`{}`".format(item) for item in list(row.get("required_capabilities") or [])) or "-",
                )
            )
        if not matched:
            lines.append("| - | - | `dom {}` | - | - | - |".format(area_id))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_tool_reference(report: Mapping[str, object]) -> str:
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
    for area_id in AREA_ORDER:
        lines.extend(["## `{}`".format(area_id), "", "{}".format(AREA_DESCRIPTIONS.get(area_id, "")), ""])
        matched = [dict(row) for row in list(report.get("rows") or []) if _token(dict(row).get("area_id")) == area_id]
        for row in matched:
            lines.append("- `{}`: {}".format(_token(row.get("command_path")), _token(row.get("description"))))
        if not matched:
            lines.append("- `dom {}`: namespace reserved; no wrapped commands are currently registered".format(area_id))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_tool_surface_final(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-ARCHIVE",
        "Replacement Target: release tool surface audit regenerated from TOOL-SURFACE-0 tooling",
        "",
        "# Tool Surface Final",
        "",
        "## Summary",
        "",
        "- Stable umbrella product: `{}`".format(DOM_PRODUCT_ID),
        "- Wrapped commands: `{}`".format(int(report.get("wrapped_tool_count", 0) or 0)),
        "- Alias adapters: `{}`".format(int(report.get("alias_count", 0) or 0)),
        "- Subprocess adapters: `{}`".format(int(report.get("subprocess_count", 0) or 0)),
        "- Surface fingerprint: `{}`".format(_token(report.get("surface_fingerprint"))),
        "",
        "## Adapter Policy",
        "",
        "- In-proc aliases are used when a stable AppShell command already exists.",
        "- Out-of-proc Python adapters are used for standalone `tool_*.py` scripts and selected legacy pack scripts.",
        "- Subprocess adapters execute with `cwd = repo root` and inject `--repo-root .` only when the wrapped tool declares that flag.",
        "",
        "## Readiness",
        "",
        "- `dom` namespaces now cover: {}".format(", ".join("`{}`".format(area_id) for area_id in AREA_ORDER)),
        "- Registry drift findings: `{}`".format(len(list(report.get("missing_registry") or [])) + len(list(report.get("extra_registry") or []))),
        "- Missing target findings: `{}`".format(len(list(report.get("missing_targets") or []))),
        "- Readiness: stable command umbrella is prepared for APPSHELL-PLATFORM-1 and virtual path hardening.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_tool_surface_outputs(repo_root: str) -> dict:
    report = build_tool_surface_report(repo_root)
    outputs = {
        TOOL_SURFACE_MAP_PATH: _render_tool_surface_map(report),
        TOOL_REFERENCE_PATH: _render_tool_reference(report),
        TOOL_SURFACE_FINAL_PATH: _render_tool_surface_final(report),
    }
    for rel_path, text in outputs.items():
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    return report


def tool_surface_violations(repo_root: str) -> list[dict]:
    report = build_tool_surface_report(repo_root)
    violations: list[dict] = []
    for row in list(report.get("missing_registry") or []):
        row_map = dict(row or {})
        violations.append(
            {
                "code": "tool_not_exposed_via_registry",
                "file_path": _token(row_map.get("tool_relpath")) or _token(row_map.get("command_path")),
                "message": "governed tool surface item is not exposed via the AppShell command registry",
                "rule_id": "INV-TOOLS-EXPOSED-VIA-REGISTRY",
            }
        )
    for row in list(report.get("extra_registry") or []):
        row_map = dict(row or {})
        violations.append(
            {
                "code": "orphan_tool_registry_leaf",
                "file_path": _token(row_map.get("command_path")),
                "message": "tool surface registry leaf points at a missing or unmanaged target",
                "rule_id": "INV-NO-ADHOC-TOOL-ENTRYPOINTS",
            }
        )
    for row in list(report.get("missing_targets") or []):
        row_map = dict(row or {})
        violations.append(
            {
                "code": "missing_tool_target",
                "file_path": _token(row_map.get("tool_relpath")),
                "message": "tool surface adapter target is missing from the repository",
                "rule_id": "INV-TOOLS-EXPOSED-VIA-REGISTRY",
            }
        )
    return sorted(violations, key=lambda item: (_token(item.get("file_path")), _token(item.get("code"))))


__all__ = [
    "DOM_PRODUCT_ID",
    "TOOL_REFERENCE_PATH",
    "TOOL_SURFACE_FINAL_PATH",
    "TOOL_SURFACE_MAP_PATH",
    "build_tool_surface_report",
    "build_tool_surface_rows",
    "execute_tool_surface_subprocess",
    "format_tool_surface_area_help",
    "format_tool_surface_root_help",
    "sync_command_registry_with_tool_surface",
    "tool_surface_row_from_command",
    "tool_surface_violations",
    "write_tool_surface_outputs",
]
