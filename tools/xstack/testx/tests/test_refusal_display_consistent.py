"""STRICT test: interaction refusal payloads follow consistent UX contract fields."""

from __future__ import annotations

import sys


TEST_ID = "testx.interaction.refusal_display_consistent"
TEST_TAGS = ["strict", "interaction", "refusal", "ux"]


def _has_refusal_contract(payload: dict) -> bool:
    refusal = dict((dict(payload or {})).get("refusal") or {})
    errors = list((dict(payload or {})).get("errors") or [])
    reason_code = str(refusal.get("reason_code", "")).strip()
    message = str(refusal.get("message", "")).strip()
    remediation_hint = str(refusal.get("remediation_hint", "")).strip()
    relevant_ids = dict(refusal.get("relevant_ids") or {})
    if not reason_code or not message or not remediation_hint:
        return False
    if not isinstance(relevant_ids, dict):
        return False
    if not errors:
        return False
    first_error = dict(errors[0] or {})
    return str(first_error.get("code", "")).strip() == reason_code


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.interaction_dispatch import run_interaction_command
    from tools.xstack.testx.tests.interaction_testlib import (
        authority_context,
        interaction_action_registry,
        law_profile,
        perceived_model,
        policy_context,
    )

    command_refusal = run_interaction_command(
        command="interact.unknown",
        perceived_model=perceived_model(),
        law_profile=law_profile(),
        authority_context=authority_context(entitlements=["entitlement.inspect"]),
        interaction_action_registry=interaction_action_registry(),
        target_semantic_id="agent.alpha",
        policy_context=policy_context(max_inspection_budget_per_tick=8),
        repo_root=repo_root,
    )
    preview_refusal = run_interaction_command(
        command="interact.preview",
        perceived_model=perceived_model(),
        law_profile=law_profile(),
        authority_context=authority_context(entitlements=["entitlement.inspect"]),
        interaction_action_registry=interaction_action_registry(),
        target_semantic_id="agent.alpha",
        affordance_id="affordance.missing",
        policy_context=policy_context(max_inspection_budget_per_tick=8),
        repo_root=repo_root,
    )

    if str(command_refusal.get("result", "")) != "refused":
        return {"status": "fail", "message": "unknown interaction command should produce refusal contract"}
    if str(preview_refusal.get("result", "")) != "refused":
        return {"status": "fail", "message": "preview with unknown affordance should produce refusal contract"}
    if not _has_refusal_contract(command_refusal):
        return {"status": "fail", "message": "command refusal payload missing required UX contract fields"}
    if not _has_refusal_contract(preview_refusal):
        return {"status": "fail", "message": "preview refusal payload missing required UX contract fields"}
    return {"status": "pass", "message": "interaction refusal contract consistency passed"}
