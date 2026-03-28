"""FAST test: AppShell logs deterministic mode degrade events."""

from __future__ import annotations

import json
import os


TEST_ID = "test_mode_degrade_logged"
TEST_TAGS = ["fast", "appshell", "platform", "logging"]


def run(repo_root: str):
    from appshell import bootstrap as bootstrap_module
    from appshell.logging import build_default_log_file_path

    original = bootstrap_module.select_ui_mode
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    log_path = build_default_log_file_path(repo_root_abs, "engine")
    try:
        bootstrap_module.select_ui_mode = lambda *args, **kwargs: {
            "result": "complete",
            "product_id": "engine",
            "requested_mode_id": "os_native",
            "selected_mode_id": "cli",
            "effective_mode_id": "cli",
            "mode_source": "explicit",
            "mode_requested": True,
            "context_kind": "headless",
            "supported_mode_ids": ["cli", "headless", "tui"],
            "available_mode_ids": ["cli"],
            "compatibility_mode_id": "compat.degraded",
            "degrade_chain": [
                {
                    "from_mode_id": "os_native",
                    "to_mode_id": "cli",
                    "step_kind": "capability_fallback",
                    "trigger_capability_id": "cap.ui.os_native",
                    "user_message_key": "explain.compat_degraded.ui_os_native",
                }
            ],
            "probe": {"context_kind": "headless"},
            "policy": {},
            "deterministic_fingerprint": "test.override",
        }
        exit_code = bootstrap_module.appshell_main(product_id="engine", argv=["--mode", "os_native"], repo_root_hint=repo_root_abs)
    finally:
        bootstrap_module.select_ui_mode = original
    if int(exit_code) != 0:
        return {"status": "fail", "message": "bootstrap call failed while checking mode degrade logging"}
    if not os.path.isfile(log_path):
        return {"status": "fail", "message": "appshell log file was not written"}
    try:
        with open(log_path, "r", encoding="utf-8") as handle:
            events = [json.loads(line) for line in handle if str(line).strip()]
    except (OSError, ValueError):
        return {"status": "fail", "message": "appshell log file was invalid"}
    if not any(str(dict(row).get("message_key", "")).strip() == "appshell.mode.degraded" for row in events):
        return {"status": "fail", "message": "mode degrade event was not logged"}
    return {"status": "pass", "message": "mode degrade logging is explicit and deterministic"}
