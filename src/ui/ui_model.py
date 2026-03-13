"""Deterministic shared UI model over command descriptors and LIB manifests."""

from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache
from typing import Iterable, Mapping

from src.appshell.command_registry import build_root_command_descriptors
from src.appshell.config_loader import list_profile_bundles
from src.appshell.paths import (
    VROOT_INSTANCES,
    VROOT_SAVES,
    get_current_virtual_paths,
    vpath_candidate_roots,
)
from src.appshell.ui_mode_selector import policy_row_for_product
from src.lib.instance import instance_ui_mode_default, validate_instance_manifest
from src.lib.save import validate_save_manifest


MENU_STATE_MAIN = "menu.main"
MENU_STATE_INSTANCE_SELECT = "menu.instance_select"
MENU_STATE_SAVE_SELECT = "menu.save_select"
MENU_STATE_SETTINGS = "menu.settings"
MENU_STATE_START_SESSION = "menu.start_session"
MENU_STATE_IDS = (
    MENU_STATE_MAIN,
    MENU_STATE_INSTANCE_SELECT,
    MENU_STATE_SAVE_SELECT,
    MENU_STATE_SETTINGS,
    MENU_STATE_START_SESSION,
)

_INSTANCE_SCAN_ROOTS = ("instances", "dist/instances")
_SAVE_SCAN_ROOTS = ("saves", "dist/saves")
_COMMAND_ACTION_SPECS = (
    ("action.help", "Help", ("help",)),
    ("action.validate_fast", "Validate FAST", ("validate", "--all", "--profile", "FAST")),
    ("action.packs_list", "List Packs", ("packs", "list")),
    ("action.profiles_list", "List Profiles", ("profiles", "list")),
    ("action.compat_status", "Compatibility Status", ("compat-status",)),
    ("action.launcher_status", "Launcher Status", ("launcher", "status")),
    ("action.launcher_start", "Launcher Start", ("launcher", "start")),
)
_FRIENDLY_LABELS = {
    "default": "Default",
    "mvp_default": "MVP Default",
    "profile.bundle.mvp_default": "MVP Default Profile",
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted({_token(item) for item in list(values or []) if _token(item)})


def _repo_root(repo_root: str) -> str:
    return os.path.normpath(os.path.abspath(_token(repo_root) or "."))


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _fingerprint(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(dict(dict(payload or {}), deterministic_fingerprint=""), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _rel_path(repo_root: str, abs_path: str) -> str:
    try:
        return _norm(os.path.relpath(abs_path, repo_root))
    except ValueError:
        return _norm(abs_path)


def _friendly_token(value: str) -> str:
    token = _token(value)
    if token in _FRIENDLY_LABELS:
        return _FRIENDLY_LABELS[token]
    parts = [item for item in token.replace(".", "_").split("_") if item]
    if not parts:
        return token
    return " ".join(part.capitalize() for part in parts)


def _friendly_entry_label(item_id: str, entry_kind: str) -> str:
    token = _token(item_id)
    if token in _FRIENDLY_LABELS:
        return _FRIENDLY_LABELS[token]
    if _token(entry_kind) == "profile_bundle" and token.startswith("profile.bundle."):
        return "{} Profile".format(_friendly_token(token.rsplit(".", 1)[-1]))
    if _token(entry_kind) == "instance_manifest":
        return "{} Instance".format(_friendly_token(token))
    if _token(entry_kind) == "save_manifest":
        return "{} Save".format(_friendly_token(token))
    return token


def _sorted_manifest_paths(repo_root: str, roots: Iterable[str], manifest_name: str) -> list[str]:
    repo_root_abs = _repo_root(repo_root)
    paths: list[str] = []
    active = get_current_virtual_paths()
    resolved_roots: list[str] = []
    if active is not None and str(active.get("result", "")).strip() == "complete":
        if str(manifest_name).strip() == "instance.manifest.json":
            resolved_roots.extend(vpath_candidate_roots(VROOT_INSTANCES, active))
        elif str(manifest_name).strip() == "save.manifest.json":
            resolved_roots.extend(vpath_candidate_roots(VROOT_SAVES, active))
    if not resolved_roots:
        for rel_root in list(roots or []):
            resolved_roots.append(os.path.join(repo_root_abs, str(rel_root).replace("/", os.sep)))
    for abs_root in list(dict.fromkeys(os.path.normpath(os.path.abspath(item)) for item in resolved_roots)):
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = sorted(dirnames)
            if str(manifest_name) not in filenames:
                continue
            paths.append(os.path.normpath(os.path.join(dirpath, str(manifest_name))))
    return sorted(set(paths))


def _menu_entry(
    *,
    item_id: str,
    label: str,
    entry_kind: str,
    event_id: str = "",
    selected: bool = False,
    details: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "item_id": _token(item_id),
        "label": _token(label),
        "entry_kind": _token(entry_kind),
        "event_id": _token(event_id),
        "selected": bool(selected),
        "details": dict(details or {}),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _action_row(
    *,
    action_id: str,
    label: str,
    action_kind: str,
    command_tokens: Iterable[str] | None = None,
    event_id: str = "",
    target_state_id: str = "",
    enabled: bool = True,
    notes: str = "",
) -> dict:
    payload = {
        "action_id": _token(action_id),
        "label": _token(label),
        "action_kind": _token(action_kind),
        "command_tokens": [_token(token) for token in list(command_tokens or []) if _token(token)],
        "event_id": _token(event_id),
        "target_state_id": _token(target_state_id),
        "enabled": bool(enabled),
        "notes": _token(notes),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


@lru_cache(maxsize=8)
def discover_profile_bundle_menu_entries(repo_root: str) -> tuple[dict, ...]:
    rows = []
    for row in list_profile_bundles(_repo_root(repo_root)):
        row_map = dict(row or {})
        bundle_id = _token(row_map.get("bundle_id"))
        if not bundle_id:
            continue
        rows.append(
            _menu_entry(
                item_id=bundle_id,
                label=_friendly_entry_label(bundle_id, "profile_bundle"),
                entry_kind="profile_bundle",
                event_id="ui.select.profile_bundle",
                details={
                    "manifest_ref": _token(row_map.get("path")),
                    "profile_bundle_hash": _token(row_map.get("profile_bundle_hash")),
                    "display_label": _friendly_entry_label(bundle_id, "profile_bundle"),
                },
            )
        )
    return tuple(sorted(rows, key=lambda row: (_token(row.get("label")), _token(row.get("item_id")))))


@lru_cache(maxsize=8)
def discover_instance_menu_entries(repo_root: str) -> tuple[dict, ...]:
    repo_root_abs = _repo_root(repo_root)
    rows = []
    for manifest_path in _sorted_manifest_paths(repo_root_abs, _INSTANCE_SCAN_ROOTS, "instance.manifest.json"):
        validation = validate_instance_manifest(repo_root=repo_root_abs, instance_manifest_path=manifest_path)
        if str(validation.get("result", "")).strip() != "complete":
            continue
        manifest = _as_map(validation.get("instance_manifest"))
        instance_id = _token(manifest.get("instance_id"))
        if not instance_id:
            continue
        rows.append(
            _menu_entry(
                item_id=instance_id,
                label=_friendly_entry_label(instance_id, "instance_manifest"),
                entry_kind="instance_manifest",
                event_id="ui.select.instance",
                details={
                    "manifest_ref": _rel_path(repo_root_abs, manifest_path),
                    "instance_kind": _token(manifest.get("instance_kind")),
                    "save_ref_count": len(_as_list(manifest.get("save_refs"))),
                    "ui_mode_default": instance_ui_mode_default(manifest),
                    "display_label": _friendly_entry_label(instance_id, "instance_manifest"),
                },
            )
        )
    return tuple(sorted(rows, key=lambda row: (_token(row.get("label")), _token(row.get("item_id")))))


@lru_cache(maxsize=8)
def discover_save_menu_entries(repo_root: str) -> tuple[dict, ...]:
    repo_root_abs = _repo_root(repo_root)
    rows = []
    for manifest_path in _sorted_manifest_paths(repo_root_abs, _SAVE_SCAN_ROOTS, "save.manifest.json"):
        validation = validate_save_manifest(repo_root=repo_root_abs, save_manifest_path=manifest_path)
        if str(validation.get("result", "")).strip() != "complete":
            continue
        manifest = _as_map(validation.get("save_manifest"))
        save_id = _token(manifest.get("save_id"))
        if not save_id:
            continue
        rows.append(
            _menu_entry(
                item_id=save_id,
                label=_friendly_entry_label(save_id, "save_manifest"),
                entry_kind="save_manifest",
                event_id="ui.select.save",
                details={
                    "manifest_ref": _rel_path(repo_root_abs, manifest_path),
                    "pack_lock_hash": _token(manifest.get("pack_lock_hash")),
                    "contract_bundle_hash": _token(manifest.get("universe_contract_bundle_hash")),
                    "display_label": _friendly_entry_label(save_id, "save_manifest"),
                },
            )
        )
    return tuple(sorted(rows, key=lambda row: (_token(row.get("label")), _token(row.get("item_id")))))


def _command_rows_by_path(repo_root: str, product_id: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in build_root_command_descriptors(_repo_root(repo_root), _token(product_id)):
        row_map = dict(row or {})
        path = _token(row_map.get("command_path"))
        if path:
            out[path] = row_map
    return dict((key, out[key]) for key in sorted(out.keys()))


def _command_actions(command_rows_by_path: Mapping[str, object], *, seed: str) -> list[dict]:
    actions: list[dict] = []
    available_paths = set(_sorted_tokens(command_rows_by_path.keys()))
    for action_id, label, command_tokens in _COMMAND_ACTION_SPECS:
        path = " ".join(list(command_tokens)[:2]).strip() if list(command_tokens)[:2] else ""
        exact_path = " ".join(list(command_tokens)).strip()
        if exact_path not in available_paths and path not in available_paths:
            continue
        tokens = list(command_tokens)
        if action_id == "action.launcher_start" and _token(seed):
            tokens = ["launcher", "start", "--seed", _token(seed)]
        notes = ""
        if action_id == "action.help":
            notes = "Show the stable command list for this product."
        elif action_id == "action.validate_fast":
            notes = "Run the FAST validation profile without leaving the current surface."
        elif action_id == "action.packs_list":
            notes = "List the packs available to the current install."
        elif action_id == "action.profiles_list":
            notes = "List profile bundles you can launch with."
        elif action_id == "action.compat_status":
            notes = "Show selected mode, install root, and compatibility state."
        elif action_id == "action.launcher_status":
            notes = "Show launcher/supervisor status for the current session."
        elif action_id == "action.launcher_start":
            notes = "Start the selected session with the requested seed."
        actions.append(
            _action_row(
                action_id=action_id,
                label=label,
                action_kind="command",
                command_tokens=tokens,
                enabled=True,
                notes=notes,
            )
        )
    return actions


def _selection_actions() -> list[dict]:
    return [
        _action_row(
            action_id="action.select_instance",
            label="Choose Instance",
            action_kind="selection_event",
            event_id="ui.select.instance_menu",
            target_state_id=MENU_STATE_INSTANCE_SELECT,
        ),
        _action_row(
            action_id="action.select_save",
            label="Choose Save",
            action_kind="selection_event",
            event_id="ui.select.save_menu",
            target_state_id=MENU_STATE_SAVE_SELECT,
        ),
        _action_row(
            action_id="action.settings",
            label="Settings",
            action_kind="selection_event",
            event_id="ui.select.settings_menu",
            target_state_id=MENU_STATE_SETTINGS,
        ),
        _action_row(
            action_id="action.start_session_menu",
            label="Start Session",
            action_kind="selection_event",
            event_id="ui.select.start_session_menu",
            target_state_id=MENU_STATE_START_SESSION,
        ),
    ]


def _state_row(
    *,
    state_id: str,
    title: str,
    summary: str,
    entries: Iterable[Mapping[str, object]] | None = None,
    actions: Iterable[Mapping[str, object]] | None = None,
) -> dict:
    payload = {
        "state_id": _token(state_id),
        "title": _token(title),
        "summary": _token(summary),
        "entries": [dict(row) for row in list(entries or []) if isinstance(row, Mapping)],
        "actions": [dict(row) for row in list(actions or []) if isinstance(row, Mapping)],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def build_ui_model(
    *,
    repo_root: str,
    product_id: str,
    current_state_id: str = MENU_STATE_MAIN,
    selected_instance_id: str = "",
    selected_save_id: str = "",
    selected_bundle_id: str = "",
    seed_value: str = "",
) -> dict:
    repo_root_abs = _repo_root(repo_root)
    product_token = _token(product_id)
    state_token = _token(current_state_id)
    command_rows_by_path = _command_rows_by_path(repo_root_abs, product_token)
    instance_entries = [dict(row) for row in discover_instance_menu_entries(repo_root_abs)]
    save_entries = [dict(row) for row in discover_save_menu_entries(repo_root_abs)]
    bundle_entries = [dict(row) for row in discover_profile_bundle_menu_entries(repo_root_abs)]

    selected_instance = _token(selected_instance_id) or (_token(instance_entries[0].get("item_id")) if instance_entries else "")
    selected_save = _token(selected_save_id) or (_token(save_entries[0].get("item_id")) if save_entries else "")
    selected_bundle = _token(selected_bundle_id) or (_token(bundle_entries[0].get("item_id")) if bundle_entries else "")
    resolved_state = state_token if state_token in set(MENU_STATE_IDS) else MENU_STATE_MAIN
    policy = _as_map(policy_row_for_product(repo_root_abs, product_token))

    main_actions = _selection_actions() + _command_actions(command_rows_by_path, seed=_token(seed_value))
    start_actions = []
    for row in main_actions:
        action_row = dict(row)
        if _token(action_row.get("action_id")) == "action.launcher_start":
            start_actions.append(action_row)
    if not start_actions:
        start_actions.append(
            _action_row(
                action_id="action.start_session",
                label="Start Session",
                action_kind="selection_event",
                event_id="ui.command.start_session",
                target_state_id=MENU_STATE_START_SESSION,
                enabled=True,
                notes="No product-local launcher command is registered; emit selection event and delegate through AppShell workflow binding.",
            )
        )

    settings_entries = [
        _menu_entry(
            item_id="setting.ui_mode_order",
            label="Mode Order",
            entry_kind="setting",
            details={
                "gui_mode_order": list(_as_list(policy.get("gui_mode_order"))),
                "tty_mode_order": list(_as_list(policy.get("tty_mode_order"))),
                "headless_mode_order": list(_as_list(policy.get("headless_mode_order"))),
            },
        ),
        _menu_entry(
            item_id="setting.selection",
            label="Current Selection",
            entry_kind="setting",
            details={
                "selected_instance_id": selected_instance,
                "selected_save_id": selected_save,
                "selected_bundle_id": selected_bundle,
                "seed_value": _token(seed_value) or "0",
            },
        ),
    ]

    states = [
        _state_row(
            state_id=MENU_STATE_MAIN,
            title="Main Menu",
            summary="Choose a starting profile, inspect status, or launch the next session from a command-driven menu.",
            entries=bundle_entries[:4],
            actions=main_actions,
        ),
        _state_row(
            state_id=MENU_STATE_INSTANCE_SELECT,
            title="Instance Select",
            summary="Choose which verified instance to use for the next session.",
            entries=[
                dict(row, selected=_token(dict(row).get("item_id")) == selected_instance)
                for row in instance_entries
            ],
            actions=[
                _action_row(
                    action_id="action.back_main_from_instance",
                    label="Back",
                    action_kind="selection_event",
                    event_id="ui.select.main_menu",
                    target_state_id=MENU_STATE_MAIN,
                )
            ],
        ),
        _state_row(
            state_id=MENU_STATE_SAVE_SELECT,
            title="Save Select",
            summary="Choose an existing save, or leave this empty to start from the instance default.",
            entries=[
                dict(row, selected=_token(dict(row).get("item_id")) == selected_save)
                for row in save_entries
            ],
            actions=[
                _action_row(
                    action_id="action.back_main_from_save",
                    label="Back",
                    action_kind="selection_event",
                    event_id="ui.select.main_menu",
                    target_state_id=MENU_STATE_MAIN,
                )
            ],
        ),
        _state_row(
            state_id=MENU_STATE_SETTINGS,
            title="Settings",
            summary="Review the derived mode order and current selection before launch.",
            entries=settings_entries,
            actions=[
                _action_row(
                    action_id="action.back_main_from_settings",
                    label="Back",
                    action_kind="selection_event",
                    event_id="ui.select.main_menu",
                    target_state_id=MENU_STATE_MAIN,
                )
            ],
        ),
        _state_row(
            state_id=MENU_STATE_START_SESSION,
            title="Start Session",
            summary="Confirm the selected instance, save, profile, and seed before starting.",
            entries=[
                _menu_entry(
                    item_id="session.summary",
                    label="Launch Summary",
                    entry_kind="summary",
                    details={
                        "selected_instance_id": selected_instance,
                        "selected_save_id": selected_save,
                        "selected_bundle_id": selected_bundle,
                        "seed_value": _token(seed_value) or "0",
                    },
                )
            ],
            actions=start_actions + [
                _action_row(
                    action_id="action.back_main_from_start",
                    label="Back",
                    action_kind="selection_event",
                    event_id="ui.select.main_menu",
                    target_state_id=MENU_STATE_MAIN,
                )
            ],
        ),
    ]
    current_state = next((dict(row) for row in states if _token(row.get("state_id")) == resolved_state), dict(states[0]))
    payload = {
        "result": "complete",
        "ui_model_id": "ui.model.v1",
        "product_id": product_token,
        "current_state_id": resolved_state,
        "current_state": current_state,
        "states": states,
        "navigation_state": {
            "selected_instance_id": selected_instance,
            "selected_save_id": selected_save,
            "selected_bundle_id": selected_bundle,
            "seed_value": _token(seed_value) or "0",
        },
        "inventory": {
            "instance_count": len(instance_entries),
            "save_count": len(save_entries),
            "bundle_count": len(bundle_entries),
            "command_descriptor_count": len(command_rows_by_path),
        },
        "guidance_lines": [
            "Start Session uses the selected profile, instance, and seed.",
            "Help shows the stable command list for this product.",
            "Compatibility Status shows mode selection, install discovery, and release identity.",
        ],
        "ui_contract": {
            "consumes_command_registry": True,
            "consumes_lib_manifests": True,
            "emits_command_invocations": True,
            "emits_selection_events": True,
            "virtual_path_policy": "repo_relative_manifest_refs",
            "forbidden_truth_inputs": [
                "truth_model",
                "universe_state",
                "process_runtime",
            ],
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


__all__ = [
    "MENU_STATE_IDS",
    "MENU_STATE_INSTANCE_SELECT",
    "MENU_STATE_MAIN",
    "MENU_STATE_SAVE_SELECT",
    "MENU_STATE_SETTINGS",
    "MENU_STATE_START_SESSION",
    "build_ui_model",
    "discover_instance_menu_entries",
    "discover_profile_bundle_menu_entries",
    "discover_save_menu_entries",
]
