"""Shared rendered client main-menu surface over the canonical UI model."""

from __future__ import annotations

import hashlib
import json

from ui import MENU_STATE_MAIN, build_ui_model


def build_client_main_menu_surface(
    *,
    repo_root: str,
    current_state_id: str = MENU_STATE_MAIN,
    selected_instance_id: str = "",
    selected_save_id: str = "",
    selected_bundle_id: str = "",
    seed_value: str = "",
) -> dict:
    ui_model = build_ui_model(
        repo_root=repo_root,
        product_id="client",
        current_state_id=current_state_id,
        selected_instance_id=selected_instance_id,
        selected_save_id=selected_save_id,
        selected_bundle_id=selected_bundle_id,
        seed_value=seed_value,
    )
    payload = {
        "result": "complete",
        "surface_id": "surface.client.main_menu.v1",
        "menu_title": "Dominium",
        "menu_subtitle": "Start a session, inspect the current selection, or open the console without leaving the client.",
        "ui_model_id": str(ui_model.get("ui_model_id", "")).strip(),
        "ui_model_fingerprint": str(ui_model.get("deterministic_fingerprint", "")).strip(),
        "current_state_id": str(ui_model.get("current_state_id", "")).strip(),
        "current_state": dict(ui_model.get("current_state") or {}),
        "navigation_state": dict(ui_model.get("navigation_state") or {}),
        "inventory": dict(ui_model.get("inventory") or {}),
        "guidance_lines": list(ui_model.get("guidance_lines") or []),
        "quick_actions": [
            {"label": "Start", "target_state_id": "menu.start_session"},
            {"label": "Seed", "value": str(dict(ui_model.get("navigation_state") or {}).get("seed_value", "")).strip() or "0"},
            {"label": "Instance", "target_state_id": "menu.instance_select"},
            {"label": "Save", "target_state_id": "menu.save_select"},
            {"label": "Console", "command_text": "console enter"},
        ],
        "console_overlay_available": True,
        "console_overlay_hint": "Open the console overlay at any time to run stable commands.",
        "teleport_menu_available": True,
        "teleport_menu_hint": "Teleport actions are available after session start from the console or client controls.",
        "inspect_hotkey": "I",
        "inspect_hint": "Press I after entering the world to inspect the current target.",
        "refinement_status_hint": "Refinement activity appears in the status strip without blocking play.",
        "ui_contract": {
            "shared_ui_model": "ui/ui_model.py",
            "consumes_command_registry": True,
            "consumes_lib_manifests": True,
            "virtual_path_policy": "repo_relative_manifest_refs",
            "forbidden_truth_inputs": [
                "truth_model",
                "universe_state",
                "process_runtime",
            ],
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = hashlib.sha256(
        json.dumps(dict(payload, deterministic_fingerprint=""), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    return payload


__all__ = ["build_client_main_menu_surface"]
