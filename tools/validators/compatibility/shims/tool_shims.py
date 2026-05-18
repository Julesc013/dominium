"""Deterministic deprecation notices for legacy tool entrypoints."""

from __future__ import annotations

import os
from typing import Iterable

from .common import SHIM_SUNSET_TARGET, build_shim_stability, emit_deprecation_warning, stable_rows


TOOL_WARNING_KEY = "warn.deprecated_tool_usage"
TOOL_SHIM_ROWS = stable_rows(
    (
        {
            "shim_id": "shim.tool.pack_validate",
            "legacy_surface": "tools/pack/pack_validate.py",
            "replacement_surface": "dom pack validate-manifest",
            "message_key": TOOL_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy pack validator entrypoint remains callable during tool-surface convergence.",
                replacement_target="Remove direct pack_validate entrypoint after TOOL-SURFACE convergence and v0.0.1 cleanup.",
            ),
            "sunset_target": SHIM_SUNSET_TARGET,
        },
        {
            "shim_id": "shim.tool.pack_migrate_capability_gating",
            "legacy_surface": "tools/pack/migrate_capability_gating.py",
            "replacement_surface": "dom pack migrate-capability-gating",
            "message_key": TOOL_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy capability-gating migration entrypoint remains callable during tool-surface convergence.",
                replacement_target="Remove direct capability-gating migration entrypoint after TOOL-SURFACE convergence and v0.0.1 cleanup.",
            ),
            "sunset_target": SHIM_SUNSET_TARGET,
        },
    )
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_repo_path(script_path: str) -> str:
    token = _token(script_path).replace("\\", "/")
    marker = "/tools/"
    lower = token.lower()
    if marker in lower:
        return token[lower.index(marker) + 1 :]
    return token


def tool_shim_rows() -> list[dict]:
    return [dict(row) for row in TOOL_SHIM_ROWS]


def emit_legacy_tool_warning(script_path: str, argv: Iterable[object] | None = None) -> dict:
    rel_path = _norm_repo_path(script_path)
    for row in TOOL_SHIM_ROWS:
        row_map = dict(row or {})
        if _token(row_map.get("legacy_surface")) != rel_path:
            continue
        payload = emit_deprecation_warning(
            category="compat",
            severity="warn",
            shim_id=_token(row_map.get("shim_id")),
            warning_code="deprecated_tool_usage",
            message_key=_token(row_map.get("message_key")) or TOOL_WARNING_KEY,
            original_surface=rel_path,
            replacement_surface=_token(row_map.get("replacement_surface")),
            details={"argv": [str(token) for token in list(argv or [])]},
        )
        return payload
    return {}


__all__ = [
    "TOOL_SHIM_ROWS",
    "TOOL_WARNING_KEY",
    "emit_legacy_tool_warning",
    "tool_shim_rows",
]
