"""Debug-only boundary assertions for commit-phase execution paths.

This module is optional and disabled by default. It must not affect release/runtime
semantics when `DOM_BOUNDARY_DEBUG_ASSERT` is unset.
"""

from __future__ import annotations

import os
import re
from typing import Mapping


_DEBUG_ENABLED = str(os.environ.get("DOM_BOUNDARY_DEBUG_ASSERT", "")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

_RENDER_TRUTH_PATTERN = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
_RENDER_ISOLATION_CHECKED = False


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _assert_render_truth_isolation_contract() -> None:
    global _RENDER_ISOLATION_CHECKED
    if _RENDER_ISOLATION_CHECKED:
        return
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    targets = (
        "src/client/render/render_model_adapter.py",
        "src/client/render/representation_resolver.py",
    )
    for rel_path in targets:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        text = _read_text(abs_path)
        if not text:
            raise AssertionError("missing render contract file '{}'".format(rel_path))
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not _RENDER_TRUTH_PATTERN.search(line):
                continue
            raise AssertionError(
                "render truth isolation violation in {}:{}".format(rel_path, line_no)
            )
    _RENDER_ISOLATION_CHECKED = True


def _assert_component_engine_contracts() -> None:
    from src.core.hazards import hazard_engine
    from src.core.schedule import schedule_engine
    from src.core.state import state_machine_engine

    required = (
        (schedule_engine, "tick_schedules"),
        (state_machine_engine, "apply_transition"),
        (hazard_engine, "tick_hazard_models"),
    )
    for module, token in required:
        if hasattr(module, token):
            continue
        raise AssertionError("missing component-engine token '{}' on {}".format(token, module.__name__))


def debug_assert_after_execute(*, state: Mapping[str, object], intent: Mapping[str, object], result: Mapping[str, object]) -> None:
    """Validate debug-only boundary assertions around commit-phase execution."""
    if not _DEBUG_ENABLED:
        return

    if not isinstance(state, Mapping):
        raise AssertionError("state must be mapping for boundary assertions")
    if not isinstance(intent, Mapping):
        raise AssertionError("intent must be mapping for boundary assertions")
    if not isinstance(result, Mapping):
        raise AssertionError("result must be mapping for boundary assertions")

    # Commit-phase outputs must carry deterministic anchors for audit/replay.
    if str(result.get("result", "")).strip() == "complete":
        if "state_hash_anchor" not in result:
            raise AssertionError("complete process result missing state_hash_anchor")
        if "ledger_hash" not in result:
            raise AssertionError("complete process result missing ledger_hash")

    # Guard against accidental render-state contamination inside authoritative state payloads.
    if isinstance(state.get("render_model"), dict) or isinstance(state.get("render_state"), dict):
        raise AssertionError("authoritative state contains render_model/render_state payload")

    _assert_render_truth_isolation_contract()
    _assert_component_engine_contracts()
