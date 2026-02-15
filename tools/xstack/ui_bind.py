#!/usr/bin/env python3
"""CLI: deterministic UI binding validation for descriptor-driven windows."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.sessionx.ui_host import validate_ui_window_descriptor  # noqa: E402


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _refusal(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str], path: str) -> Dict[str, object]:
    ids = {}
    for key, value in sorted((relevant_ids or {}).items(), key=lambda row: str(row[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": ids,
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def _read_json(path: str):
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _descriptor_view(row: Dict[str, object]) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for key in ("window_id", "title", "required_entitlements", "required_lenses", "widgets"):
        if key in row:
            out[key] = row.get(key)
    return out


def run_ui_bind_check(repo_root: str, ui_registry_path: str = "build/registries/ui.registry.json") -> Dict[str, object]:
    abs_path = ui_registry_path
    if not os.path.isabs(abs_path):
        abs_path = os.path.join(repo_root, str(ui_registry_path).replace("/", os.sep))
    payload, err = _read_json(abs_path)
    if err:
        return _refusal(
            "REFUSE_UI_BIND_REGISTRY_INVALID",
            "ui.registry payload is missing or invalid JSON",
            "Compile registries and rerun ui_bind --check.",
            {"ui_registry_path": str(ui_registry_path)},
            "$.ui_registry",
        )

    windows = payload.get("windows")
    if not isinstance(windows, list):
        return _refusal(
            "REFUSE_UI_BIND_REGISTRY_INVALID",
            "ui.registry.windows must be an array",
            "Recompile ui registry and retry.",
            {"ui_registry_path": str(ui_registry_path)},
            "$.windows",
        )

    checked_rows: List[dict] = []
    for row in sorted((item for item in windows if isinstance(item, dict)), key=lambda item: str(item.get("window_id", ""))):
        window_id = str(row.get("window_id", "")).strip()
        if not window_id:
            return _refusal(
                "REFUSE_UI_BIND_WINDOW_INVALID",
                "ui registry contains an empty window_id",
                "Ensure every ui descriptor declares window_id.",
                {"ui_registry_path": str(ui_registry_path)},
                "$.windows",
            )
        descriptor_view = _descriptor_view(row)
        missing_row_fields = [key for key in ("window_id", "title", "required_entitlements", "widgets") if key not in descriptor_view]
        if missing_row_fields:
            return _refusal(
                "REFUSE_UI_BIND_WINDOW_INVALID",
                "ui registry row '{}' is missing required descriptor fields".format(window_id),
                "Ensure ui.registry rows include window_id/title/required_entitlements/widgets.",
                {"window_id": window_id, "missing_fields": ",".join(sorted(missing_row_fields))},
                "$.windows",
            )
        descriptor_path = str(row.get("path", "")).strip()
        descriptor_abs = os.path.join(repo_root, descriptor_path.replace("/", os.sep)) if descriptor_path else ""
        if descriptor_path and not os.path.isfile(descriptor_abs):
            return _refusal(
                "REFUSE_UI_BIND_WINDOW_PATH_MISSING",
                "ui window descriptor path '{}' is missing".format(descriptor_path),
                "Restore descriptor file and rerun registry compile.",
                {"window_id": window_id, "path": descriptor_path},
                "$.windows",
            )
        if descriptor_path:
            descriptor_payload, descriptor_err = _read_json(descriptor_abs)
            if descriptor_err:
                return _refusal(
                    "REFUSE_UI_BIND_WINDOW_INVALID",
                    "ui descriptor file '{}' is invalid JSON".format(descriptor_path),
                    "Fix descriptor JSON content and rerun.",
                    {"window_id": window_id, "path": descriptor_path},
                    "$.windows",
                )
            file_check = validate_instance(
                repo_root=repo_root,
                schema_name="ui_window",
                payload=descriptor_payload,
                strict_top_level=True,
            )
            if not bool(file_check.get("valid", False)):
                return _refusal(
                    "REFUSE_UI_BIND_WINDOW_INVALID",
                    "ui descriptor file '{}' failed schema validation".format(descriptor_path),
                    "Fix ui_window fields and retry.",
                    {"window_id": window_id, "path": descriptor_path},
                    "$.windows",
                )
            file_window_id = str(descriptor_payload.get("window_id", "")).strip()
            if file_window_id != window_id:
                return _refusal(
                    "REFUSE_UI_BIND_WINDOW_MISMATCH",
                    "ui registry window_id does not match descriptor file window_id",
                    "Keep ui.registry and descriptor file window_id values identical.",
                    {"registry_window_id": window_id, "file_window_id": file_window_id, "path": descriptor_path},
                    "$.windows",
                )

        checked_rows.append(
            {
                "window_id": window_id,
                "path": descriptor_path,
                "pack_id": str(row.get("pack_id", "")),
            }
        )

    return {
        "result": "complete",
        "ui_registry_path": str(ui_registry_path).replace("\\", "/"),
        "checked_windows": len(checked_rows),
        "windows": checked_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate descriptor bindings for ui.registry windows.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--ui-registry", default="build/registries/ui.registry.json")
    args = parser.parse_args()

    if not bool(args.check):
        print(
            json.dumps(
                _refusal(
                    "REFUSE_UI_BIND_INTENT_INVALID",
                    "ui_bind requires --check",
                    "Run tools/xstack/ui_bind --check.",
                    {},
                    "$.check",
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    result = run_ui_bind_check(
        repo_root=_repo_root(str(args.repo_root)),
        ui_registry_path=str(args.ui_registry),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
