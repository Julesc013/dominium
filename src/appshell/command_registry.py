"""Registry-backed deterministic AppShell command descriptors."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Iterable, List, Mapping, Sequence, Tuple

from src.meta_extensions_engine import normalize_extensions_tree


COMMAND_REGISTRY_REL = os.path.join("data", "registries", "command_registry.json")
TUI_PANEL_REGISTRY_REL = os.path.join("data", "registries", "tui_panel_registry.json")


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = normalize_extensions_tree(dict(payload))
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


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _normalize_command_row(row: Mapping[str, object]) -> dict:
    payload = normalize_extensions_tree(dict(row or {}))
    payload["product_ids"] = _sorted_tokens(payload.get("product_ids"))
    payload["supported_mode_ids"] = _sorted_tokens(payload.get("supported_mode_ids"))
    payload["refusal_codes"] = _sorted_tokens(payload.get("refusal_codes"))
    payload["command_id"] = str(payload.get("command_id", "")).strip()
    payload["command_path"] = str(payload.get("command_path", "")).strip()
    payload["description"] = str(payload.get("description", "")).strip()
    payload["args_schema_id"] = str(payload.get("args_schema_id", "")).strip()
    payload["output_schema_id"] = str(payload.get("output_schema_id", "")).strip()
    payload["handler_id"] = str(payload.get("handler_id", "")).strip()
    payload["exit_code_mapping_id"] = str(payload.get("exit_code_mapping_id", "")).strip()
    payload["schema_version"] = str(payload.get("schema_version", "")).strip() or "1.1.0"
    payload["extensions"] = normalize_extensions_tree(dict(payload.get("extensions") or {}))
    payload["deterministic_fingerprint"] = str(payload.get("deterministic_fingerprint", "")).strip() or _fingerprint(payload)
    return payload


def load_command_registry(repo_root: str) -> tuple[dict, str]:
    path = os.path.join(repo_root, COMMAND_REGISTRY_REL)
    payload, error = _read_json(path)
    if error:
        return {}, error
    record = dict(payload.get("record") or {})
    commands = [_normalize_command_row(row) for row in list(record.get("commands") or []) if isinstance(row, Mapping)]
    commands = sorted(
        commands,
        key=lambda row: (
            str(row.get("command_path", "")).endswith(".*"),
            len(str(row.get("command_path", "")).split()),
            str(row.get("command_path", "")),
            str(row.get("command_id", "")),
        ),
    )
    record["commands"] = commands
    return {
        "schema_id": str(payload.get("schema_id", "")).strip(),
        "schema_version": str(payload.get("schema_version", "")).strip(),
        "record": record,
    }, ""


def _synthetic_setup_command_rows(product_id: str) -> List[dict]:
    token = str(product_id or "").strip()
    if token != "setup":
        return []
    rows = [
        {
            "args_schema_id": "dominium.schema.appshell.args.install_plan",
            "command_id": "command.setup_install_plan",
            "command_path": "install plan",
            "description": "Resolve a deterministic install plan from the component graph for the selected install profile.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "UPDATE-MODEL-0"},
            "handler_id": "setup_install_plan",
            "output_schema_id": "dominium.schema.release.install_plan",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.not_found",
                "refusal.release.install_profile_missing",
                "refusal.release.component_graph_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup install planning remains provisional while release/update governance converges.",
                "future_series": "DIST-REFINE",
                "replacement_target": "Replace synthetic setup install-plan command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.install_apply",
            "command_id": "command.setup_install_apply",
            "command_path": "install apply",
            "description": "Apply a deterministic install plan to the selected install root.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "UPDATE-MODEL-0"},
            "handler_id": "setup_install_apply",
            "output_schema_id": "dominium.schema.appshell.output.install_apply",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.not_found",
                "refusal.release.install_profile_missing",
                "refusal.release.component_graph_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup install application remains provisional while release/update governance converges.",
                "future_series": "DIST-REFINE",
                "replacement_target": "Replace synthetic setup install-apply command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.update_check",
            "command_id": "command.setup_update_check",
            "command_path": "update check",
            "description": "Compare the current install against a release index and report whether an update is required.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "UPDATE-MODEL-0"},
            "handler_id": "setup_update_check",
            "output_schema_id": "dominium.schema.release.update_plan",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.release.index_missing",
                "refusal.release.contract_incompatible",
                "refusal.release.platform_unavailable",
                "refusal.release.install_profile_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup update check remains provisional while release/update governance converges.",
                "future_series": "UPDATE",
                "replacement_target": "Replace synthetic setup update-check command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.update_plan",
            "command_id": "command.setup_update_plan",
            "command_path": "update plan",
            "description": "Resolve a deterministic update plan from the current install state and a release index.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "UPDATE-MODEL-0"},
            "handler_id": "setup_update_plan",
            "output_schema_id": "dominium.schema.release.update_plan",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.release.index_missing",
                "refusal.release.contract_incompatible",
                "refusal.release.platform_unavailable",
                "refusal.release.install_profile_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup update planning remains provisional while release/update governance converges.",
                "future_series": "UPDATE",
                "replacement_target": "Replace synthetic setup update-plan command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.update_apply",
            "command_id": "command.setup_update_apply",
            "command_path": "update apply",
            "description": "Apply a deterministic update plan after release-manifest verification and transaction-log capture.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "UPDATE-MODEL-0"},
            "handler_id": "setup_update_apply",
            "output_schema_id": "dominium.schema.appshell.output.update_apply",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.release.index_missing",
                "refusal.release.contract_incompatible",
                "refusal.release.platform_unavailable",
                "refusal.release.trust_unmet",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup update application remains provisional while release/update governance converges.",
                "future_series": "UPDATE",
                "replacement_target": "Replace synthetic setup update-apply command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.rollback",
            "command_id": "command.setup_rollback",
            "command_path": "rollback",
            "description": "Restore a previous release state from the deterministic install transaction log.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "UPDATE-MODEL-0"},
            "handler_id": "setup_rollback",
            "output_schema_id": "dominium.schema.appshell.output.rollback",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.release.rollback_missing",
                "refusal.release.install_profile_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup rollback remains provisional while release/update governance converges.",
                "future_series": "UPDATE",
                "replacement_target": "Replace synthetic setup rollback command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.trust_list",
            "command_id": "command.setup_trust_list",
            "command_path": "trust list",
            "description": "List the effective trust policy and trusted signer roots for the current install.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "TRUST-MODEL-0"},
            "handler_id": "setup_trust_list",
            "output_schema_id": "dominium.schema.security.trust_policy",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.not_found",
                "refusal.trust.policy_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup trust listing remains provisional while trust-root bundle governance converges.",
                "future_series": "TRUST/RELEASE",
                "replacement_target": "Replace synthetic setup trust-list command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.trust_status",
            "command_id": "command.setup_trust_status",
            "command_path": "trust status",
            "description": "Report the effective trust policy, trusted signer roots, and local trust status for the current install.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "GOVERNANCE-0"},
            "handler_id": "setup_trust_status",
            "output_schema_id": "dominium.schema.security.trust_policy",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.not_found",
                "refusal.trust.policy_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup trust status remains provisional while governance and trust-root publication policy converges.",
                "future_series": "GOVERNANCE/TRUST",
                "replacement_target": "Replace synthetic setup trust-status command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.trust_import",
            "command_id": "command.setup_trust_import",
            "command_path": "trust import",
            "description": "Import trusted signer roots from a deterministic offline trust bundle.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "TRUST-MODEL-0"},
            "handler_id": "setup_trust_import",
            "output_schema_id": "dominium.schema.appshell.output.trust_import",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.not_found",
                "refusal.io.invalid_args",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup trust import remains provisional while trust-root distribution bundles converge.",
                "future_series": "TRUST/UPDATE",
                "replacement_target": "Replace synthetic setup trust-import command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.trust_policy_set",
            "command_id": "command.setup_trust_policy_set",
            "command_path": "trust policy set",
            "description": "Select the active trust policy for the current install.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "TRUST-MODEL-0"},
            "handler_id": "setup_trust_policy_set",
            "output_schema_id": "dominium.schema.security.trust_policy",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.not_found",
                "refusal.trust.policy_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup trust policy selection remains provisional while release trust governance is being formalized.",
                "future_series": "TRUST/UPDATE",
                "replacement_target": "Replace synthetic setup trust-policy command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.governance_status",
            "command_id": "command.setup_governance_status",
            "command_path": "governance status",
            "description": "Report the active governance profile, archive policy, and fork policy for the current install or repo default.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "GOVERNANCE-0"},
            "handler_id": "setup_governance_status",
            "output_schema_id": "dominium.schema.governance.governance_profile",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.not_found",
                "refusal.governance.profile_missing",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup governance status remains provisional while governance publication and release packaging converge.",
                "future_series": "GOVERNANCE/RELEASE",
                "replacement_target": "Replace synthetic setup governance-status command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
        {
            "args_schema_id": "dominium.schema.appshell.args.store_gc",
            "command_id": "command.setup_store_gc",
            "command_path": "store gc",
            "description": "Verify store integrity, compute deterministic reachability, and apply the selected garbage-collection policy.",
            "exit_code_mapping_id": "exit.success",
            "extensions": {"official.source": "STORE-GC-0"},
            "handler_id": "setup_store_gc",
            "output_schema_id": "dominium.schema.lib.gc_report",
            "product_ids": ["setup"],
            "refusal_codes": [
                "refusal.install.invalid_manifest",
                "refusal.store.gc.policy_required",
                "refusal.store.gc.portable_refused",
                "refusal.store.gc.store_root_missing",
                "refusal.store.gc.verify_failed",
                "refusal.store.gc.explicit_flag_required",
            ],
            "schema_version": "1.1.0",
            "stability": {
                "stability_class_id": "provisional",
                "rationale": "Setup store GC remains provisional while shared-store lifecycle governance converges.",
                "future_series": "STORE/LIB",
                "replacement_target": "Replace synthetic setup store-gc command rows with release-pinned AppShell registry definitions.",
                "contract_id": "",
                "deprecated": False,
                "deterministic_fingerprint": "",
                "extensions": {},
                "schema_version": "1.0.0",
            },
            "supported_mode_ids": ["cli", "tui"],
        },
    ]
    return [_normalize_command_row(row) for row in rows]


def build_root_command_descriptors(repo_root: str, product_id: str) -> List[dict]:
    registry_payload, error = load_command_registry(repo_root)
    if error:
        return []
    token = str(product_id or "").strip()
    rows = []
    for row in list((dict(registry_payload.get("record") or {})).get("commands") or []):
        product_ids = _sorted_tokens(dict(row).get("product_ids"))
        if token and product_ids and token not in product_ids:
            continue
        rows.append(dict(row))
    rows.extend(_synthetic_setup_command_rows(token))
    rows = sorted(rows, key=_command_sort_key)
    return rows


def build_tui_panel_descriptors(product_id: str) -> List[dict]:
    del product_id
    repo_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    payload, error = _read_json(os.path.join(repo_root, TUI_PANEL_REGISTRY_REL))
    if error:
        return []
    rows = []
    for row in list(dict(payload.get("record") or {}).get("panels") or []):
        if not isinstance(row, Mapping):
            continue
        row_map = normalize_extensions_tree(dict(row))
        row_map["required_capabilities"] = _sorted_tokens(row_map.get("required_capabilities"))
        row_map["schema_version"] = str(row_map.get("schema_version", "")).strip() or "1.0.0"
        row_map["panel_id"] = str(row_map.get("panel_id", "")).strip()
        row_map["title"] = str(row_map.get("title", "")).strip()
        row_map["extensions"] = normalize_extensions_tree(dict(row_map.get("extensions") or {}))
        row_map["deterministic_fingerprint"] = (
            str(row_map.get("deterministic_fingerprint", "")).strip() or _fingerprint(row_map)
        )
        rows.append(row_map)
    return sorted(rows, key=lambda row: str(row.get("panel_id", "")))


def _command_sort_key(row: Mapping[str, object]) -> Tuple[object, ...]:
    command_path = str(row.get("command_path", "")).strip()
    return (
        command_path.endswith(".*"),
        command_path.count(" "),
        command_path,
        str(row.get("command_id", "")).strip(),
    )


def _help_example_rows(product_id: str, available_paths: Iterable[str]) -> list[tuple[str, str]]:
    paths = set(_sorted_tokens(available_paths))
    rows: list[tuple[str, str]] = []
    ordered_examples = (
        ("compat-status", "Check compatibility and selected mode"),
        ("packs verify --root .", "Verify packs offline"),
        ("profiles list", "List available profile bundles"),
        ("diag capture", "Capture a deterministic repro bundle"),
        ("console enter", "Open the command console"),
        ("launcher start --seed 456", "Start a session with a fixed seed"),
    )
    for command_text, label in ordered_examples:
        command_path = " ".join(str(command_text).split()[:2]).strip()
        exact_path = " ".join(str(command_text).split()).strip()
        if exact_path in paths or command_path in paths:
            rows.append((label, command_text))
    if not rows:
        rows.append(("Open help", "help"))
    if str(product_id).strip() == "client":
        rows.append(("Show client status", "compat-status --mode cli"))
    return rows


def find_command_descriptor(
    repo_root: str,
    product_id: str,
    command_tokens: Sequence[str],
) -> tuple[dict, list[str], dict | None]:
    rows = build_root_command_descriptors(repo_root, product_id)
    tokens = [str(token).strip() for token in list(command_tokens or []) if str(token).strip()]
    if not tokens:
        return {}, [], None
    best_row = {}
    best_remaining: list[str] = []
    namespace_row = None
    for row in sorted(rows, key=_command_sort_key):
        command_path = str(row.get("command_path", "")).strip()
        if not command_path:
            continue
        if command_path.endswith(".*"):
            prefix = command_path[:-2]
            if tokens and str(tokens[0]).strip() == prefix and namespace_row is None:
                namespace_row = dict(row)
            continue
        path_tokens = command_path.split()
        if len(tokens) < len(path_tokens):
            continue
        if [str(token).strip() for token in path_tokens] != tokens[: len(path_tokens)]:
            continue
        if not best_row or len(path_tokens) > len(str(best_row.get("command_path", "")).split()):
            best_row = dict(row)
            best_remaining = list(tokens[len(path_tokens) :])
    return best_row, best_remaining, namespace_row


def format_help_text(product_id: str, command_rows: Iterable[Mapping[str, object]], topic_tokens: Sequence[str] | None = None) -> str:
    rows = [dict(row) for row in list(command_rows or []) if isinstance(row, Mapping)]
    topic = " ".join(str(token).strip() for token in list(topic_tokens or []) if str(token).strip()).strip()
    if topic:
        filtered = []
        for row in rows:
            command_path = str(row.get("command_path", "")).strip()
            if command_path == topic or command_path.startswith("{} ".format(topic)) or command_path.startswith("{}.".format(topic)):
                filtered.append(row)
        rows = filtered
    exact_rows = sorted(
        [row for row in rows if not str(row.get("command_path", "")).strip().endswith(".*")],
        key=_command_sort_key,
    )
    namespace_rows = sorted(
        [row for row in rows if str(row.get("command_path", "")).strip().endswith(".*")],
        key=_command_sort_key,
    )
    available_paths = [str(row.get("command_path", "")).strip() for row in exact_rows]
    lines = [
        "Dominium AppShell",
        "product_id: {}".format(str(product_id).strip()),
        "tip: use `help <topic>` for a narrower command view.",
    ]
    if topic:
        lines.append("topic: {}".format(topic))
    lines.append("commands:")
    for row in exact_rows:
        command_path = str(row.get("command_path", "")).strip()
        description = str(row.get("description", "")).strip()
        if not command_path:
            continue
        lines.append("  {:<24} {}".format(command_path, description))
    if namespace_rows:
        lines.append("namespaces:")
        for row in namespace_rows:
            command_path = str(row.get("command_path", "")).strip()
            description = str(row.get("description", "")).strip()
            lines.append("  {:<24} {}".format(command_path, description))
    if not exact_rows and not namespace_rows:
        lines.append("  no registered commands matched the requested topic")
    lines.append("examples:")
    for label, command_text in _help_example_rows(str(product_id).strip(), available_paths):
        lines.append("  {:<24} {}".format(label + ":", command_text))
    return "\n".join(lines)


__all__ = [
    "COMMAND_REGISTRY_REL",
    "build_root_command_descriptors",
    "build_tui_panel_descriptors",
    "find_command_descriptor",
    "format_help_text",
    "load_command_registry",
]
