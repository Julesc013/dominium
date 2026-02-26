"""SessionX wrapper for deterministic client interaction affordance generation."""

from __future__ import annotations

from typing import Dict

from src.client.interaction import build_affordance_list as _build_affordance_list


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

