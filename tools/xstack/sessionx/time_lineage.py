"""Deterministic time-lineage utilities for RS-3 branching and compaction tooling."""

from __future__ import annotations

import os
import shutil
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance

from .common import norm, read_json_object, refusal, write_canonical_json


def _find_checkpoint_artifact(
    *,
    repo_root: str,
    parent_checkpoint_id: str,
    parent_save_id: str = "",
) -> Tuple[dict, str, Dict[str, object]]:
    requested_save = str(parent_save_id or "").strip()
    candidate_saves: List[str] = []
    if requested_save:
        candidate_saves.append(requested_save)
    else:
        saves_root = os.path.join(repo_root, "saves")
        if os.path.isdir(saves_root):
            candidate_saves.extend(
                sorted(
                    name
                    for name in os.listdir(saves_root)
                    if str(name).strip() and os.path.isdir(os.path.join(saves_root, str(name)))
                )
            )

    matches: List[Tuple[dict, str]] = []
    for save_id in candidate_saves:
        checkpoints_dir = os.path.join(repo_root, "saves", str(save_id), "checkpoints")
        if not os.path.isdir(checkpoints_dir):
            continue
        for name in sorted(item for item in os.listdir(checkpoints_dir) if str(item).endswith(".checkpoint.json")):
            abs_path = os.path.join(checkpoints_dir, name)
            payload, err = read_json_object(abs_path)
            if err:
                continue
            if str(payload.get("checkpoint_id", "")).strip() != str(parent_checkpoint_id).strip():
                continue
            matches.append((dict(payload), abs_path))

    if not matches:
        return {}, "", refusal(
            "refusal.time.checkpoint_missing",
            "checkpoint_id '{}' was not found".format(str(parent_checkpoint_id)),
            "Provide an existing checkpoint_id from save checkpoints and retry branching.",
            {"parent_checkpoint_id": str(parent_checkpoint_id)},
            "$.parent_checkpoint_id",
        )
    if len(matches) > 1:
        return {}, "", refusal(
            "refusal.time.checkpoint_ambiguous",
            "checkpoint_id '{}' resolves to multiple saves".format(str(parent_checkpoint_id)),
            "Specify parent_save_id explicitly to disambiguate deterministic branch source.",
            {"parent_checkpoint_id": str(parent_checkpoint_id)},
            "$.parent_checkpoint_id",
        )
    return matches[0][0], matches[0][1], {}


def _time_policy_for_save(repo_root: str, save_id: str) -> Tuple[dict, dict, Dict[str, object]]:
    spec_path = os.path.join(repo_root, "saves", str(save_id), "session_spec.json")
    spec_payload, spec_err = read_json_object(spec_path)
    if spec_err:
        return {}, {}, refusal(
            "refusal.time.branch_forbidden_by_policy",
            "unable to load parent save session_spec for time policy checks",
            "Restore parent save session_spec.json and retry branching.",
            {"save_id": str(save_id)},
            "$.session_spec",
        )
    time_control_policy_id = str(spec_payload.get("time_control_policy_id", "") or "time.policy.null").strip() or "time.policy.null"

    network = dict(spec_payload.get("network") or {})
    server_profile_id = str(network.get("server_profile_id", "")).strip()
    registries_path = os.path.join(repo_root, "build", "registries", "time_control_policy.registry.json")
    registry_payload, registry_err = read_json_object(registries_path)
    if registry_err:
        return {}, {}, refusal(
            "refusal.time.branch_forbidden_by_policy",
            "time control policy registry is unavailable for branch policy checks",
            "Compile registries and retry branching.",
            {"save_id": str(save_id)},
            "$.time_control_policy_id",
        )
    selected_policy = {}
    for row in sorted((item for item in (registry_payload.get("policies") or []) if isinstance(item, dict)), key=lambda item: str(item.get("time_control_policy_id", ""))):
        if str(row.get("time_control_policy_id", "")).strip() == time_control_policy_id:
            selected_policy = dict(row)
            break
    if not selected_policy:
        return {}, {}, refusal(
            "refusal.time.branch_forbidden_by_policy",
            "time_control_policy_id '{}' is unavailable for branching checks".format(time_control_policy_id),
            "Use a save/session with a valid compiled time control policy.",
            {"save_id": str(save_id), "time_control_policy_id": time_control_policy_id},
            "$.time_control_policy_id",
        )
    return spec_payload, selected_policy, {"server_profile_id": server_profile_id}


def branch_from_checkpoint(
    *,
    repo_root: str,
    parent_checkpoint_id: str,
    new_save_id: str,
    reason: str,
    parent_save_id: str = "",
) -> Dict[str, object]:
    checkpoint_payload, checkpoint_path, checkpoint_error = _find_checkpoint_artifact(
        repo_root=repo_root,
        parent_checkpoint_id=str(parent_checkpoint_id),
        parent_save_id=str(parent_save_id),
    )
    if checkpoint_error:
        return checkpoint_error

    resolved_parent_save_id = str(checkpoint_payload.get("save_id", "")).strip()
    if not resolved_parent_save_id:
        return refusal(
            "refusal.time.checkpoint_missing",
            "checkpoint artifact is missing save_id",
            "Regenerate checkpoint artifacts before branching.",
            {"parent_checkpoint_id": str(parent_checkpoint_id)},
            "$.checkpoint.save_id",
        )

    parent_save_dir = os.path.join(repo_root, "saves", str(resolved_parent_save_id))
    child_save_id = str(new_save_id).strip()
    if not child_save_id:
        return refusal(
            "PROCESS_INPUT_INVALID",
            "new_save_id is required for branch creation",
            "Provide a deterministic new_save_id and retry.",
            {"parent_checkpoint_id": str(parent_checkpoint_id)},
            "$.new_save_id",
        )
    child_save_dir = os.path.join(repo_root, "saves", str(child_save_id))
    if os.path.isdir(child_save_dir):
        return refusal(
            "refusal.time.branch_save_exists",
            "target new_save_id already exists",
            "Choose a new deterministic save id that does not already exist.",
            {"new_save_id": child_save_id},
            "$.new_save_id",
        )

    spec_payload, time_policy, time_context_or_error = _time_policy_for_save(repo_root=repo_root, save_id=resolved_parent_save_id)
    if "refusal" in time_context_or_error:
        return time_context_or_error
    time_context = dict(time_context_or_error)
    if str(time_context.get("server_profile_id", "")).strip() == "server.profile.rank_strict":
        return refusal(
            "refusal.time.branch_forbidden_by_policy",
            "branching is forbidden for ranked server profiles",
            "Create branches only from non-ranked saves.",
            {
                "parent_save_id": resolved_parent_save_id,
                "server_profile_id": "server.profile.rank_strict",
            },
            "$.session_spec.network.server_profile_id",
        )
    if str(time_policy.get("time_control_policy_id", "")).strip() == "time.policy.rank_strict":
        return refusal(
            "refusal.time.branch_forbidden_by_policy",
            "branching is forbidden for time.policy.rank_strict",
            "Select a non-ranked time control policy before creating branch lineage.",
            {
                "parent_save_id": resolved_parent_save_id,
                "time_control_policy_id": "time.policy.rank_strict",
            },
            "$.time_control_policy_id",
        )
    policy_extensions = dict(time_policy.get("extensions") or {})
    if not bool(policy_extensions.get("allow_branching", False)):
        return refusal(
            "refusal.time.branch_forbidden_by_policy",
            "active time control policy does not allow branching",
            "Use a save/session configured with extensions.allow_branching=true.",
            {
                "parent_save_id": resolved_parent_save_id,
                "time_control_policy_id": str(time_policy.get("time_control_policy_id", "")),
            },
            "$.time_control_policy_id",
        )

    shutil.copytree(parent_save_dir, child_save_dir)

    child_spec_path = os.path.join(child_save_dir, "session_spec.json")
    child_spec_payload, child_spec_err = read_json_object(child_spec_path)
    if child_spec_err:
        return refusal(
            "refusal.time.branch_create_failed",
            "new save session_spec is unavailable after copy",
            "Retry branching after restoring parent save artifacts.",
            {"new_save_id": child_save_id},
            "$.session_spec",
        )
    child_spec_payload["save_id"] = child_save_id
    write_canonical_json(child_spec_path, child_spec_payload)

    divergence_tick = int(checkpoint_payload.get("tick", 0) or 0)
    normalized_reason = str(reason).strip() or "user.tool.branch"
    branch_seed = {
        "parent_save_id": resolved_parent_save_id,
        "parent_checkpoint_id": str(parent_checkpoint_id),
        "new_save_id": child_save_id,
        "divergence_tick": int(divergence_tick),
        "reason": normalized_reason,
    }
    branch_id = "branch.{}".format(canonical_sha256(branch_seed)[:16])
    branch_payload = {
        "schema_version": "1.0.0",
        "branch_id": branch_id,
        "parent_save_id": resolved_parent_save_id,
        "parent_checkpoint_id": str(parent_checkpoint_id),
        "divergence_tick": int(divergence_tick),
        "new_save_id": child_save_id,
        "reason": normalized_reason,
        "extensions": {
            "checkpoint_path": norm(os.path.relpath(checkpoint_path, repo_root)),
        },
    }
    valid = validate_instance(
        repo_root=repo_root,
        schema_name="time_branch",
        payload=branch_payload,
        strict_top_level=True,
    )
    if not bool(valid.get("valid", False)):
        return refusal(
            "refusal.time.branch_create_failed",
            "branch artifact failed schema validation",
            "Repair branch artifact generation and retry.",
            {"branch_id": branch_id},
            "$.branch",
        )

    parent_branch_rel = norm(os.path.join("saves", resolved_parent_save_id, "branches", "{}.json".format(branch_id)))
    child_branch_rel = norm(os.path.join("saves", child_save_id, "branches", "{}.json".format(branch_id)))
    write_canonical_json(os.path.join(repo_root, parent_branch_rel.replace("/", os.sep)), branch_payload)
    write_canonical_json(os.path.join(repo_root, child_branch_rel.replace("/", os.sep)), branch_payload)

    return {
        "result": "complete",
        "branch_id": branch_id,
        "parent_save_id": resolved_parent_save_id,
        "parent_checkpoint_id": str(parent_checkpoint_id),
        "new_save_id": child_save_id,
        "divergence_tick": int(divergence_tick),
        "reason": normalized_reason,
        "parent_branch_artifact_path": parent_branch_rel,
        "new_branch_artifact_path": child_branch_rel,
        "new_session_spec_path": norm(os.path.join("saves", child_save_id, "session_spec.json")),
    }
