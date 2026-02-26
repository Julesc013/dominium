"""SessionX wrapper for deterministic client interaction affordance/dispatch."""

from __future__ import annotations

from typing import Dict

from src.client.interaction import (
    build_affordance_list as _build_affordance_list,
    build_inspection_overlays as _build_inspection_overlays,
    execute_affordance as _execute_affordance,
    generate_interaction_preview as _generate_interaction_preview,
    run_interaction_command as _run_interaction_command,
)


def build_affordance_list(
    *,
    perceived_model: dict,
    target_semantic_id: str,
    law_profile: dict,
    authority_context: dict,
    interaction_action_registry: dict,
    include_disabled: bool = True,
    repo_root: str = "",
) -> Dict[str, object]:
    return _build_affordance_list(
        perceived_model=dict(perceived_model or {}),
        target_semantic_id=str(target_semantic_id or ""),
        law_profile=dict(law_profile or {}),
        authority_context=dict(authority_context or {}),
        interaction_action_registry=dict(interaction_action_registry or {}),
        include_disabled=bool(include_disabled),
        repo_root=str(repo_root or ""),
    )


def execute_affordance(
    *,
    state: dict,
    affordance_list: dict,
    affordance_id: str,
    parameters: dict,
    law_profile: dict,
    authority_context: dict,
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
    peer_id: str = "",
    deterministic_sequence_number: int = 0,
    submission_tick: int = 0,
    source_shard_id: str = "shard.0",
    target_shard_id: str = "shard.0",
    repo_root: str = "",
) -> Dict[str, object]:
    return _execute_affordance(
        state=dict(state or {}),
        affordance_list=dict(affordance_list or {}),
        affordance_id=str(affordance_id or ""),
        parameters=dict(parameters or {}),
        law_profile=dict(law_profile or {}),
        authority_context=dict(authority_context or {}),
        navigation_indices=navigation_indices,
        policy_context=policy_context,
        peer_id=str(peer_id or ""),
        deterministic_sequence_number=int(deterministic_sequence_number),
        submission_tick=int(submission_tick),
        source_shard_id=str(source_shard_id or "shard.0"),
        target_shard_id=str(target_shard_id or "shard.0"),
        repo_root=str(repo_root or ""),
    )


def run_interaction_command(
    *,
    command: str,
    perceived_model: dict,
    law_profile: dict,
    authority_context: dict,
    interaction_action_registry: dict,
    target_semantic_id: str = "",
    affordance_id: str = "",
    parameters: dict | None = None,
    state: dict | None = None,
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
    peer_id: str = "",
    deterministic_sequence_number: int = 0,
    submission_tick: int = 0,
    source_shard_id: str = "shard.0",
    target_shard_id: str = "shard.0",
    include_disabled: bool = True,
    repo_root: str = "",
) -> Dict[str, object]:
    return _run_interaction_command(
        command=str(command or ""),
        perceived_model=dict(perceived_model or {}),
        law_profile=dict(law_profile or {}),
        authority_context=dict(authority_context or {}),
        interaction_action_registry=dict(interaction_action_registry or {}),
        target_semantic_id=str(target_semantic_id or ""),
        affordance_id=str(affordance_id or ""),
        parameters=dict(parameters or {}),
        state=dict(state or {}),
        navigation_indices=navigation_indices,
        policy_context=policy_context,
        peer_id=str(peer_id or ""),
        deterministic_sequence_number=int(deterministic_sequence_number),
        submission_tick=int(submission_tick),
        source_shard_id=str(source_shard_id or "shard.0"),
        target_shard_id=str(target_shard_id or "shard.0"),
        include_disabled=bool(include_disabled),
        repo_root=str(repo_root or ""),
    )


def generate_interaction_preview(
    *,
    perceived_model: dict,
    affordance_row: dict,
    parameters: dict | None = None,
    preview_runtime: dict | None = None,
    repo_root: str = "",
) -> Dict[str, object]:
    return _generate_interaction_preview(
        perceived_model=dict(perceived_model or {}),
        affordance_row=dict(affordance_row or {}),
        parameters=dict(parameters or {}),
        preview_runtime=dict(preview_runtime or {}),
        repo_root=str(repo_root or ""),
    )


def build_inspection_overlays(
    *,
    perceived_model: dict,
    target_semantic_id: str,
    authority_context: dict | None = None,
    inspection_snapshot: dict | None = None,
    overlay_runtime: dict | None = None,
    requested_cost_units: int = 1,
) -> Dict[str, object]:
    return _build_inspection_overlays(
        perceived_model=dict(perceived_model or {}),
        target_semantic_id=str(target_semantic_id or ""),
        authority_context=dict(authority_context or {}),
        inspection_snapshot=dict(inspection_snapshot or {}),
        overlay_runtime=dict(overlay_runtime or {}),
        requested_cost_units=int(requested_cost_units),
    )
