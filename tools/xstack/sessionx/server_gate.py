"""Deterministic server-side session pipeline enforcement checks."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from .common import norm, refusal
from .pipeline_contract import DEFAULT_PIPELINE_ID, load_session_pipeline_contract
from .runner import _latest_run_meta, _load_schema_validated


def _normalized_stage_log(rows: object) -> List[dict]:
    out: List[dict] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "stage_index": int(row.get("stage_index", 0) or 0),
                "from_stage_id": str(row.get("from_stage_id", "")),
                "to_stage_id": str(row.get("to_stage_id", "")),
                "command_id": str(row.get("command_id", "")),
            }
        )
    return sorted(
        out,
        key=lambda item: (
            int(item.get("stage_index", 0) or 0),
            str(item.get("command_id", "")),
            str(item.get("to_stage_id", "")),
            str(item.get("from_stage_id", "")),
        ),
    )


def _stage_history(stage_log: List[dict]) -> List[str]:
    ordered: List[str] = []
    for row in stage_log:
        stage_id = str(row.get("to_stage_id", "")).strip()
        if stage_id and stage_id not in ordered:
            ordered.append(stage_id)
    return ordered


def _normalized_entitlements(rows: object) -> List[str]:
    return sorted(set(str(item).strip() for item in (rows or []) if str(item).strip()))


def _authority_compatible(expected: dict, provided: dict) -> bool:
    if not isinstance(expected, dict) or not isinstance(provided, dict):
        return False
    if str(expected.get("authority_origin", "")).strip() != str(provided.get("authority_origin", "")).strip():
        return False
    if str(expected.get("experience_id", "")).strip() != str(provided.get("experience_id", "")).strip():
        return False
    if str(expected.get("law_profile_id", "")).strip() != str(provided.get("law_profile_id", "")).strip():
        return False
    if str(expected.get("privilege_level", "")).strip() != str(provided.get("privilege_level", "")).strip():
        return False
    if _normalized_entitlements(expected.get("entitlements")) != _normalized_entitlements(provided.get("entitlements")):
        return False
    return True


def _required_history_before_running(stage_map: dict, pipeline: dict) -> List[str]:
    out: List[str] = []
    for token in (
        str(pipeline.get("entry_stage_id", "")),
        "stage.acquire_world",
        "stage.verify_world",
        str(pipeline.get("ready_stage_id", "")),
    ):
        stage_id = str(token).strip()
        if stage_id and stage_id in stage_map and stage_id not in out:
            out.append(stage_id)
    return out


def server_validate_transition(
    repo_root: str,
    session_spec_path: str,
    from_stage_id: str = "",
    to_stage_id: str = "",
    authority_context: dict | None = None,
) -> Dict[str, object]:
    spec_abs = os.path.normpath(os.path.abspath(session_spec_path))
    session_spec, spec_error = _load_schema_validated(
        repo_root=repo_root,
        schema_name="session_spec",
        path=spec_abs,
    )
    if spec_error:
        return spec_error

    pipeline_contract = load_session_pipeline_contract(
        repo_root=repo_root,
        pipeline_id=str(session_spec.get("pipeline_id", "")),
    )
    if pipeline_contract.get("result") != "complete":
        return pipeline_contract

    pipeline = dict(pipeline_contract.get("pipeline") or {})
    stage_map = dict(pipeline_contract.get("stage_map") or {})
    if not stage_map:
        return refusal(
            "refusal.server_stage_mismatch",
            "server pipeline registry resolved an empty stage map",
            "Repair data/registries/session_stage_registry.json and retry.",
            {"pipeline_id": str(pipeline_contract.get("pipeline_id", DEFAULT_PIPELINE_ID))},
            "$.pipeline",
        )

    save_id = str(session_spec.get("save_id", "")).strip()
    save_dir = os.path.join(repo_root, "saves", save_id)
    run_meta, _run_meta_path = _latest_run_meta(save_dir)
    history = _stage_history(_normalized_stage_log((run_meta or {}).get("stage_log")))

    from_stage = str(from_stage_id).strip()
    if not from_stage:
        from_stage = str((run_meta or {}).get("last_stage_id", "")).strip()
    if not from_stage:
        from_stage = str(pipeline.get("entry_stage_id", "stage.resolve_session"))

    requested_stage = str(to_stage_id).strip() or str(pipeline.get("running_stage_id", "stage.session_running"))

    if from_stage not in stage_map:
        return refusal(
            "refusal.server_stage_mismatch",
            "server received unknown from_stage_id '{}'".format(from_stage or "<empty>"),
            "Use a declared stage_id from session stage registry.",
            {"from_stage_id": from_stage or "<empty>"},
            "$.from_stage_id",
        )
    if requested_stage not in stage_map:
        return refusal(
            "refusal.server_stage_mismatch",
            "server received unknown to_stage_id '{}'".format(requested_stage or "<empty>"),
            "Use a declared stage_id from session stage registry.",
            {"to_stage_id": requested_stage or "<empty>"},
            "$.to_stage_id",
        )

    if from_stage == requested_stage:
        expected_authority = dict(session_spec.get("authority_context") or {})
        provided_authority = dict(authority_context or expected_authority)
        if not _authority_compatible(expected_authority, provided_authority):
            return refusal(
                "refusal.server_authority_violation",
                "authority_context does not match SessionSpec binding",
                "Provide authority_context identical to SessionSpec authority binding.",
                {"save_id": save_id, "from_stage_id": from_stage, "to_stage_id": requested_stage},
                "$.authority_context",
            )
        return {
            "result": "complete",
            "save_id": save_id,
            "pipeline_id": str(pipeline_contract.get("pipeline_id", DEFAULT_PIPELINE_ID)),
            "from_stage_id": from_stage,
            "to_stage_id": requested_stage,
            "authority_bound": True,
            "stage_history": history,
            "no_transition": True,
        }

    allowed_next = sorted(
        set(str(item).strip() for item in (dict(stage_map.get(from_stage) or {}).get("allowed_next_stage_ids") or []) if str(item).strip())
    )
    if requested_stage not in allowed_next:
        return refusal(
            "refusal.server_stage_mismatch",
            "server rejected stage transition '{}' -> '{}'".format(from_stage, requested_stage),
            "Advance only through allowed_next_stage_ids from session stage registry.",
            {"from_stage_id": from_stage, "to_stage_id": requested_stage},
            "$.pipeline",
        )

    running_stage_id = str(pipeline.get("running_stage_id", "stage.session_running"))
    ready_stage_id = str(pipeline.get("ready_stage_id", "stage.session_ready"))
    if requested_stage == running_stage_id:
        if from_stage != ready_stage_id:
            return refusal(
                "refusal.server_stage_mismatch",
                "server requires '{}' before '{}'".format(ready_stage_id, running_stage_id),
                "Move pipeline to stage.session_ready before requesting client.session.begin.",
                {"from_stage_id": from_stage, "to_stage_id": requested_stage},
                "$.pipeline",
            )
        required = _required_history_before_running(stage_map=stage_map, pipeline=pipeline)
        required_positions: List[int] = []
        for stage_id in required:
            if stage_id not in history:
                return refusal(
                    "refusal.server_stage_mismatch",
                    "server did not observe required stage '{}' before running".format(stage_id),
                    "Re-enter from stage.resolve_session and complete canonical stages.",
                    {"required_stage_id": stage_id, "to_stage_id": requested_stage},
                    "$.stage_log",
                )
            required_positions.append(int(history.index(stage_id)))
        if required_positions != sorted(required_positions):
            return refusal(
                "refusal.server_stage_mismatch",
                "server observed out-of-order canonical stage history before running",
                "Re-enter through canonical stage order and retry.",
                {"to_stage_id": requested_stage},
                "$.stage_log",
            )

    expected_authority = dict(session_spec.get("authority_context") or {})
    if not expected_authority:
        return refusal(
            "refusal.server_authority_violation",
            "SessionSpec authority_context is missing",
            "Populate SessionSpec authority_context before requesting server transition.",
            {"save_id": save_id},
            "$.authority_context",
        )
    provided_authority = dict(authority_context or expected_authority)
    if not _authority_compatible(expected_authority, provided_authority):
        return refusal(
            "refusal.server_authority_violation",
            "authority_context does not match SessionSpec binding",
            "Provide authority_context identical to SessionSpec authority binding.",
            {"save_id": save_id, "from_stage_id": from_stage, "to_stage_id": requested_stage},
            "$.authority_context",
        )

    return {
        "result": "complete",
        "save_id": save_id,
        "pipeline_id": str(pipeline_contract.get("pipeline_id", DEFAULT_PIPELINE_ID)),
        "session_spec_path": norm(os.path.relpath(spec_abs, repo_root)),
        "from_stage_id": from_stage,
        "to_stage_id": requested_stage,
        "authority_bound": True,
        "stage_history": history,
        "required_history_for_running": _required_history_before_running(stage_map=stage_map, pipeline=pipeline),
    }
