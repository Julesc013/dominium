"""Deterministic time-lineage utilities for RS-3 branching and compaction tooling."""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from typing import Dict, List, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases
install_src_aliases(REPO_ROOT_HINT)

from engine.time import (
    ANCHOR_REASON_MIGRATION,
    emit_epoch_anchor,
    load_epoch_anchor_rows,
    resolve_compaction_bounds,
    select_boundary_anchor,
)
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance

from .common import norm, read_json_object, refusal, write_canonical_json


def _safe_remove_file(path: str) -> None:
    token = str(path or "").strip()
    if not token:
        return
    last_error: OSError | None = None
    for _attempt in range(8):
        try:
            if os.path.exists(token):
                try:
                    os.chmod(token, 0o666)
                except OSError:
                    pass
                os.remove(token)
            return
        except FileNotFoundError:
            return
        except OSError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error


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


def _save_anchor_root(repo_root: str, save_id: str) -> str:
    return os.path.join(repo_root, "saves", str(save_id), "anchors")


def _save_anchor_rows(repo_root: str, save_id: str) -> List[dict]:
    return load_epoch_anchor_rows(_save_anchor_root(repo_root, save_id))


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
    if os.path.exists(child_save_dir):
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
    checkpoint_extensions = dict(checkpoint_payload.get("extensions") or {})
    parent_anchor_result = emit_epoch_anchor(
        repo_root=repo_root,
        anchor_root_path=_save_anchor_root(repo_root, resolved_parent_save_id),
        tick=int(divergence_tick),
        truth_hash=str(checkpoint_payload.get("truth_hash_anchor", "")).strip(),
        contract_bundle_hash=str(checkpoint_extensions.get("contract_bundle_hash", "")).strip(),
        pack_lock_hash=str(checkpoint_payload.get("pack_lock_hash", "")).strip(),
        overlay_manifest_hash=str(checkpoint_extensions.get("overlay_manifest_hash", "")).strip(),
        reason=ANCHOR_REASON_MIGRATION,
        extensions={
            "branch_id": branch_id,
            "branch_role": "parent",
            "parent_checkpoint_id": str(parent_checkpoint_id),
            "new_save_id": child_save_id,
        },
    )
    if str(parent_anchor_result.get("result", "")) == "refused":
        return dict(parent_anchor_result)
    child_anchor_result = emit_epoch_anchor(
        repo_root=repo_root,
        anchor_root_path=_save_anchor_root(repo_root, child_save_id),
        tick=int(divergence_tick),
        truth_hash=str(checkpoint_payload.get("truth_hash_anchor", "")).strip(),
        contract_bundle_hash=str(checkpoint_extensions.get("contract_bundle_hash", "")).strip(),
        pack_lock_hash=str(checkpoint_payload.get("pack_lock_hash", "")).strip(),
        overlay_manifest_hash=str(checkpoint_extensions.get("overlay_manifest_hash", "")).strip(),
        reason=ANCHOR_REASON_MIGRATION,
        extensions={
            "branch_id": branch_id,
            "branch_role": "child",
            "parent_checkpoint_id": str(parent_checkpoint_id),
            "parent_save_id": resolved_parent_save_id,
        },
    )
    if str(child_anchor_result.get("result", "")) == "refused":
        return dict(child_anchor_result)
    if str(parent_anchor_result.get("result", "")) == "complete":
        branch_payload["extensions"]["parent_epoch_anchor_id"] = str(
            (dict(parent_anchor_result.get("anchor") or {})).get("anchor_id", "")
        ).strip()
        branch_payload["extensions"]["parent_epoch_anchor_path"] = str(parent_anchor_result.get("anchor_path", "")).strip()
    if str(child_anchor_result.get("result", "")) == "complete":
        branch_payload["extensions"]["new_epoch_anchor_id"] = str(
            (dict(child_anchor_result.get("anchor") or {})).get("anchor_id", "")
        ).strip()
        branch_payload["extensions"]["new_epoch_anchor_path"] = str(child_anchor_result.get("anchor_path", "")).strip()
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
        "parent_epoch_anchor_path": str(branch_payload["extensions"].get("parent_epoch_anchor_path", "")).strip(),
        "new_epoch_anchor_path": str(branch_payload["extensions"].get("new_epoch_anchor_path", "")).strip(),
    }


def _sha256_file(path: str) -> str:
    handle = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            handle.update(chunk)
    return handle.hexdigest()


def _compaction_policy(repo_root: str, compaction_policy_id: str) -> Tuple[dict, Dict[str, object]]:
    registry_path = os.path.join(repo_root, "build", "registries", "compaction_policy.registry.json")
    registry_payload, registry_err = read_json_object(registry_path)
    if registry_err:
        return {}, refusal(
            "refusal.time.compaction_policy_missing",
            "compiled compaction policy registry is unavailable",
            "Compile registries before running deterministic compaction.",
            {"compaction_policy_id": str(compaction_policy_id)},
            "$.compaction_policy_id",
        )
    selected = {}
    for row in sorted((item for item in (registry_payload.get("policies") or []) if isinstance(item, dict)), key=lambda item: str(item.get("compaction_policy_id", ""))):
        if str(row.get("compaction_policy_id", "")).strip() == str(compaction_policy_id).strip():
            selected = dict(row)
            break
    if not selected:
        return {}, refusal(
            "refusal.time.compaction_policy_missing",
            "compaction policy '{}' is not available".format(str(compaction_policy_id)),
            "Use a compaction_policy_id from compiled compaction policy registry.",
            {"compaction_policy_id": str(compaction_policy_id)},
            "$.compaction_policy_id",
        )
    return selected, {}


def compact_save(
    *,
    repo_root: str,
    save_id: str,
    compaction_policy_id: str,
) -> Dict[str, object]:
    selected_policy, policy_error = _compaction_policy(repo_root=repo_root, compaction_policy_id=str(compaction_policy_id))
    if policy_error:
        return policy_error

    save_dir = os.path.join(repo_root, "saves", str(save_id))
    if not os.path.isdir(save_dir):
        return refusal(
            "refusal.time.compaction_save_missing",
            "save '{}' does not exist".format(str(save_id)),
            "Provide an existing save_id before running compaction.",
            {"save_id": str(save_id)},
            "$.save_id",
        )

    checkpoints_dir = os.path.join(save_dir, "checkpoints")
    intent_logs_dir = os.path.join(save_dir, "intent_logs")
    run_meta_dir = os.path.join(save_dir, "run_meta")
    anchors_dir = _save_anchor_root(repo_root, save_id)

    checkpoint_rows: List[dict] = []
    if os.path.isdir(checkpoints_dir):
        for name in sorted(item for item in os.listdir(checkpoints_dir) if str(item).endswith(".checkpoint.json")):
            abs_path = os.path.join(checkpoints_dir, name)
            payload, err = read_json_object(abs_path)
            if err:
                continue
            checkpoint_rows.append(
                {
                    "path": abs_path,
                    "payload": payload,
                    "tick": int(payload.get("tick", 0) or 0),
                    "checkpoint_id": str(payload.get("checkpoint_id", "")),
                    "payload_ref": str(payload.get("payload_ref", "")),
                }
            )
    checkpoint_rows = sorted(checkpoint_rows, key=lambda item: (int(item.get("tick", 0)), str(item.get("checkpoint_id", "")), str(item.get("path", ""))))

    intent_log_rows: List[dict] = []
    if os.path.isdir(intent_logs_dir):
        for name in sorted(item for item in os.listdir(intent_logs_dir) if str(item).endswith(".json")):
            abs_path = os.path.join(intent_logs_dir, name)
            payload, err = read_json_object(abs_path)
            if err:
                continue
            tick_range = dict(payload.get("tick_range") or {})
            intent_log_rows.append(
                {
                    "path": abs_path,
                    "payload": payload,
                    "start_tick": int(tick_range.get("start_tick", 0) or 0),
                    "end_tick": int(tick_range.get("end_tick", 0) or 0),
                    "log_id": str(payload.get("log_id", "")),
                }
            )
    intent_log_rows = sorted(intent_log_rows, key=lambda item: (int(item.get("start_tick", 0)), int(item.get("end_tick", 0)), str(item.get("log_id", ""))))

    anchor_rows = _save_anchor_rows(repo_root, str(save_id))
    anchor_paths: List[str] = []
    if os.path.isdir(anchors_dir):
        anchor_paths = sorted(
            os.path.join(anchors_dir, name)
            for name in os.listdir(anchors_dir)
            if str(name).endswith(".json")
        )

    run_meta_paths: List[str] = []
    if os.path.isdir(run_meta_dir):
        run_meta_paths = sorted(
            os.path.join(run_meta_dir, name)
            for name in os.listdir(run_meta_dir)
            if str(name).endswith(".json")
        )

    tracked_paths_before = sorted(
        set(
            [row.get("path", "") for row in checkpoint_rows]
            + [row.get("path", "") for row in intent_log_rows]
            + list(anchor_paths)
            + list(run_meta_paths)
        )
    )
    tracked_paths_before = [path for path in tracked_paths_before if path and os.path.isfile(path)]
    before_hashes = dict((path, _sha256_file(path)) for path in tracked_paths_before)
    before_bytes = sum(os.path.getsize(path) for path in tracked_paths_before if os.path.isfile(path))

    rules = dict(selected_policy.get("rules") or {})
    keep_every_nth_checkpoint = max(1, int(rules.get("keep_every_nth_checkpoint", 1) or 1))
    keep_checkpoint_paths: set[str] = set()
    if checkpoint_rows:
        for idx, row in enumerate(checkpoint_rows):
            keep = (idx % keep_every_nth_checkpoint == 0) or (idx == len(checkpoint_rows) - 1)
            if keep:
                keep_checkpoint_paths.add(str(row.get("path", "")))
                continue
            checkpoint_path = str(row.get("path", ""))
            if checkpoint_path and os.path.isfile(checkpoint_path):
                _safe_remove_file(checkpoint_path)
            snapshot_rel = str(row.get("payload_ref", "")).replace("/", os.sep)
            if snapshot_rel:
                snapshot_abs = os.path.join(repo_root, snapshot_rel)
                if os.path.isfile(snapshot_abs):
                    _safe_remove_file(snapshot_abs)

    kept_checkpoint_rows = [
        dict(row)
        for row in checkpoint_rows
        if str(row.get("path", "")) in keep_checkpoint_paths
    ]
    lower_epoch_anchor = {}
    upper_epoch_anchor = {}
    if checkpoint_rows and not anchor_rows and (
        len(keep_checkpoint_paths) != len(checkpoint_rows)
        or bool(rules.get("merge_intent_logs", False))
    ):
        return refusal(
            "refusal.time.compaction_anchor_missing",
            "compaction requires epoch anchors for retained checkpoint boundaries",
            "Emit TIME-ANCHOR-0 save anchors before running compaction.",
            {"save_id": str(save_id)},
            "$.anchors",
        )
    if kept_checkpoint_rows and anchor_rows:
        lower_epoch_anchor, upper_epoch_anchor, boundary_error = resolve_compaction_bounds(
            anchor_rows,
            start_tick=int(kept_checkpoint_rows[0].get("tick", 0) or 0),
            end_tick=int(kept_checkpoint_rows[-1].get("tick", 0) or 0),
        )
        if boundary_error and (
            len(keep_checkpoint_paths) != len(checkpoint_rows)
            or bool(rules.get("merge_intent_logs", False))
        ):
            return dict(boundary_error)

    merged_intent_log_path = ""
    keep_intent_log_paths: set[str] = set()
    if bool(rules.get("merge_intent_logs", False)) and intent_log_rows:
        merged_source_rows = [
            dict(row)
            for row in intent_log_rows
            if lower_epoch_anchor
            and upper_epoch_anchor
            and int(row.get("start_tick", 0) or 0) >= int(lower_epoch_anchor.get("tick", 0) or 0)
            and int(row.get("end_tick", 0) or 0) <= int(upper_epoch_anchor.get("tick", 0) or 0)
        ]
        if not merged_source_rows:
            keep_intent_log_paths = set(str(row.get("path", "")) for row in intent_log_rows if str(row.get("path", "")))
        else:
            merged_start = int(lower_epoch_anchor.get("tick", 0) or 0)
            merged_end = int(upper_epoch_anchor.get("tick", 0) or 0)
            merged_tokens: List[str] = []
            for row in merged_source_rows:
                merged_tokens.extend(str(token) for token in list((row.get("payload") or {}).get("envelopes_or_intents") or []))
            merged_tokens = sorted(set(token for token in merged_tokens if token))
            merged_log_id = "intent_log.{}.{}_{}.merged".format(str(save_id), int(merged_start), int(merged_end))
            merged_payload = {
                "schema_version": "1.0.0",
                "log_id": merged_log_id,
                "save_id": str(save_id),
                "tick_range": {"start_tick": int(merged_start), "end_tick": int(merged_end)},
                "envelopes_or_intents": merged_tokens,
                "log_hash": "",
                "extensions": {
                    "compaction_policy_id": str(compaction_policy_id),
                    "merged_source_count": len(merged_source_rows),
                    "lower_epoch_anchor_id": str(lower_epoch_anchor.get("anchor_id", "")).strip(),
                    "upper_epoch_anchor_id": str(upper_epoch_anchor.get("anchor_id", "")).strip(),
                    "lower_epoch_anchor_tick": int(lower_epoch_anchor.get("tick", 0) or 0),
                    "upper_epoch_anchor_tick": int(upper_epoch_anchor.get("tick", 0) or 0),
                },
            }
            merged_payload["log_hash"] = canonical_sha256(
                {
                    "schema_version": merged_payload["schema_version"],
                    "log_id": merged_payload["log_id"],
                    "save_id": merged_payload["save_id"],
                    "tick_range": dict(merged_payload["tick_range"]),
                    "envelopes_or_intents": list(merged_payload["envelopes_or_intents"]),
                    "extensions": dict(merged_payload["extensions"]),
                }
            )
            valid = validate_instance(
                repo_root=repo_root,
                schema_name="intent_log",
                payload=merged_payload,
                strict_top_level=True,
            )
            if not bool(valid.get("valid", False)):
                return refusal(
                    "refusal.time.compaction_failed",
                    "merged intent log failed schema validation",
                    "Repair compaction merge logic and retry.",
                    {"save_id": str(save_id), "compaction_policy_id": str(compaction_policy_id)},
                    "$.intent_log",
                )
            merged_intent_log_path = os.path.join(intent_logs_dir, "{}.json".format(merged_log_id))
            write_canonical_json(merged_intent_log_path, merged_payload)
            keep_intent_log_paths.add(merged_intent_log_path)
            for row in intent_log_rows:
                path = str(row.get("path", ""))
                row_in_merge = any(path == str(candidate.get("path", "")) for candidate in merged_source_rows)
                if row_in_merge:
                    if path and os.path.isfile(path):
                        _safe_remove_file(path)
                    continue
                if path:
                    keep_intent_log_paths.add(path)
    else:
        keep_intent_log_paths = set(str(row.get("path", "")) for row in intent_log_rows if str(row.get("path", "")))

    kept_run_meta_paths: set[str] = set(path for path in run_meta_paths if os.path.isfile(path))
    if bool(rules.get("prune_old_run_meta", False)) and run_meta_paths:
        prune_threshold = max(0, int(rules.get("prune_run_meta_older_than_ticks", 0) or 0))
        parsed: List[Tuple[str, int]] = []
        max_stop_tick = 0
        for path in run_meta_paths:
            payload, err = read_json_object(path)
            if err:
                continue
            stop_tick = int(payload.get("stop_tick", payload.get("baseline_tick", 0)) or 0)
            max_stop_tick = max(max_stop_tick, int(stop_tick))
            parsed.append((path, int(stop_tick)))
        cutoff = int(max_stop_tick - prune_threshold)
        for path, stop_tick in parsed:
            if stop_tick >= cutoff:
                continue
            if os.path.isfile(path):
                _safe_remove_file(path)
            if path in kept_run_meta_paths:
                kept_run_meta_paths.remove(path)

    retained_paths_after = sorted(
        path
        for path in (
            list(keep_checkpoint_paths)
            + list(keep_intent_log_paths)
            + list(anchor_paths)
            + list(kept_run_meta_paths)
        )
        if path and os.path.isfile(path)
    )
    after_hashes = dict((path, _sha256_file(path)) for path in retained_paths_after)
    after_bytes = sum(os.path.getsize(path) for path in retained_paths_after if os.path.isfile(path))

    retained_unchanged = True
    retained_hash_mismatches: List[str] = []
    for path in sorted(set(retained_paths_after) & set(before_hashes.keys())):
        if str(before_hashes.get(path, "")) == str(after_hashes.get(path, "")):
            continue
        retained_unchanged = False
        retained_hash_mismatches.append(norm(os.path.relpath(path, repo_root)))

    return {
        "result": "complete",
        "save_id": str(save_id),
        "compaction_policy_id": str(compaction_policy_id),
        "before_bytes": int(before_bytes),
        "after_bytes": int(after_bytes),
        "bytes_saved": int(max(0, int(before_bytes) - int(after_bytes))),
        "retained_hashes_unchanged": bool(retained_unchanged),
        "retained_hash_mismatches": retained_hash_mismatches,
        "retained_artifact_paths": [norm(os.path.relpath(path, repo_root)) for path in retained_paths_after],
        "merged_intent_log_path": norm(os.path.relpath(merged_intent_log_path, repo_root)) if merged_intent_log_path else "",
        "lower_epoch_anchor_id": str(lower_epoch_anchor.get("anchor_id", "")).strip(),
        "upper_epoch_anchor_id": str(upper_epoch_anchor.get("anchor_id", "")).strip(),
    }
