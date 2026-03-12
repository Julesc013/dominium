"""Shared rendered client main-menu surface over the canonical UI model."""

from __future__ import annotations

import hashlib
import json

from src.ui import MENU_STATE_MAIN, build_ui_model


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
        "ui_model_id": str(ui_model.get("ui_model_id", "")).strip(),
        "ui_model_fingerprint": str(ui_model.get("deterministic_fingerprint", "")).strip(),
        "current_state_id": str(ui_model.get("current_state_id", "")).strip(),
        "current_state": dict(ui_model.get("current_state") or {}),
        "navigation_state": dict(ui_model.get("navigation_state") or {}),
        "inventory": dict(ui_model.get("inventory") or {}),
        "ui_contract": {
            "shared_ui_model": "src/ui/ui_model.py",
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
