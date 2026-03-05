"""Shared POLL-0 TestX fixtures."""

from __future__ import annotations

import copy
import sys
from typing import Mapping


def seed_pollution_state() -> dict:
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state

    state = seed_free_state(initial_velocity_x=0)
    state.setdefault("pollution_source_event_rows", [])
    state.setdefault("pollution_total_rows", [])
    state.setdefault("pollutant_mass_total", {})
    state.setdefault("explain_artifact_rows", [])
    state.setdefault("info_artifact_rows", [])
    state.setdefault("knowledge_artifacts", [])
    return state


def execute_pollution_emit(
    *,
    repo_root: str,
    state: dict,
    inputs: Mapping[str, object] | None = None,
    policy_overrides: Mapping[str, object] | None = None,
    max_compute_units_per_tick: int = 4096,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context as construction_authority_context,
        law_profile as construction_law_profile,
        policy_context as construction_policy_context,
    )

    law = construction_law_profile(["process.pollution_emit"])
    authority = construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect"],
        privilege_level="operator",
    )
    policy = construction_policy_context(
        max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick)))
    )
    if isinstance(policy_overrides, Mapping):
        for key, value in dict(policy_overrides).items():
            policy[str(key)] = copy.deepcopy(value)

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.pollution.emit.test",
            "process_id": "process.pollution_emit",
            "inputs": dict(inputs or {}),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


def _execute_pollution_process(
    *,
    repo_root: str,
    state: dict,
    process_id: str,
    intent_id: str,
    inputs: Mapping[str, object] | None = None,
    policy_overrides: Mapping[str, object] | None = None,
    max_compute_units_per_tick: int = 4096,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context as construction_authority_context,
        law_profile as construction_law_profile,
        policy_context as construction_policy_context,
    )

    law = construction_law_profile([str(process_id)])
    authority = construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect", "entitlement.tool.use"],
        privilege_level="operator",
    )
    policy = construction_policy_context(
        max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick)))
    )
    if isinstance(policy_overrides, Mapping):
        for key, value in dict(policy_overrides).items():
            policy[str(key)] = copy.deepcopy(value)
    return execute_intent(
        state=state,
        intent={
            "intent_id": str(intent_id),
            "process_id": str(process_id),
            "inputs": dict(inputs or {}),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


def execute_pollution_measure(
    *,
    repo_root: str,
    state: dict,
    inputs: Mapping[str, object] | None = None,
    policy_overrides: Mapping[str, object] | None = None,
    max_compute_units_per_tick: int = 4096,
) -> dict:
    return _execute_pollution_process(
        repo_root=repo_root,
        state=state,
        process_id="process.pollution_measure",
        intent_id="intent.pollution.measure.test",
        inputs=inputs,
        policy_overrides=policy_overrides,
        max_compute_units_per_tick=max_compute_units_per_tick,
    )


def execute_pollution_compliance_tick(
    *,
    repo_root: str,
    state: dict,
    inputs: Mapping[str, object] | None = None,
    policy_overrides: Mapping[str, object] | None = None,
    max_compute_units_per_tick: int = 4096,
) -> dict:
    return _execute_pollution_process(
        repo_root=repo_root,
        state=state,
        process_id="process.pollution_compliance_tick",
        intent_id="intent.pollution.compliance.test",
        inputs=inputs,
        policy_overrides=policy_overrides,
        max_compute_units_per_tick=max_compute_units_per_tick,
    )
