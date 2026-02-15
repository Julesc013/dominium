"""Deterministic session stage/pipeline registry contract loader."""

from __future__ import annotations

import copy
import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance

from .common import norm, read_json_object, refusal


DEFAULT_PIPELINE_ID = "pipeline.client.default"
STAGE_REGISTRY_REL = os.path.join("data", "registries", "session_stage_registry.json")
PIPELINE_REGISTRY_REL = os.path.join("data", "registries", "session_pipeline_registry.json")


def _read_registry(repo_root: str, rel_path: str, reason_code: str) -> Tuple[dict, Dict[str, object]]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload, err = read_json_object(abs_path)
    if err:
        return {}, refusal(
            reason_code,
            "registry file '{}' is missing or invalid".format(norm(rel_path)),
            "Restore '{}' and rerun the command.".format(norm(rel_path)),
            {"registry_path": norm(rel_path)},
            "$.registry",
        )
    return payload, {}


def _rows(payload: dict, rel_path: str, key: str, reason_code: str) -> Tuple[List[dict], Dict[str, object]]:
    record = payload.get("record")
    if not isinstance(record, dict):
        return [], refusal(
            reason_code,
            "registry '{}' is missing record object".format(norm(rel_path)),
            "Fix registry shape to include top-level record object.",
            {"registry_path": norm(rel_path)},
            "$.record",
        )
    rows = record.get(key)
    if not isinstance(rows, list):
        return [], refusal(
            reason_code,
            "registry '{}' is missing '{}' list".format(norm(rel_path), key),
            "Fix registry shape to include '{}'.".format(key),
            {"registry_path": norm(rel_path)},
            "$.record.{}".format(key),
        )
    out = []
    for row in rows:
        if isinstance(row, dict):
            out.append(dict(row))
        else:
            return [], refusal(
                reason_code,
                "registry '{}' contains non-object '{}' entries".format(norm(rel_path), key),
                "Fix '{}' to contain only objects.".format(key),
                {"registry_path": norm(rel_path)},
                "$.record.{}".format(key),
            )
    return out, {}


def _validate_stage_rows(repo_root: str, stage_rows: List[dict]) -> Tuple[Dict[str, dict], Dict[str, object]]:
    stage_map: Dict[str, dict] = {}
    for row in sorted(stage_rows, key=lambda item: str(item.get("stage_id", ""))):
        stage_id = str(row.get("stage_id", "")).strip()
        if not stage_id:
            return {}, refusal(
                "REFUSE_SESSION_STAGE_REGISTRY_INVALID",
                "stage registry contains an empty stage_id",
                "Provide a stable stage_id for every stage row.",
                {"stage_id": "<empty>"},
                "$.record.stages",
            )
        if stage_id in stage_map:
            return {}, refusal(
                "REFUSE_SESSION_STAGE_REGISTRY_INVALID",
                "duplicate stage_id '{}' in stage registry".format(stage_id),
                "Ensure stage_id values are unique.",
                {"stage_id": stage_id},
                "$.record.stages",
            )
        validated = validate_instance(
            repo_root=repo_root,
            schema_name="session_stage",
            payload=row,
            strict_top_level=True,
        )
        if not bool(validated.get("valid", False)):
            first = list(validated.get("errors") or [{}])[0]
            return {}, refusal(
                "REFUSE_SESSION_STAGE_REGISTRY_INVALID",
                "stage '{}' failed session_stage schema validation".format(stage_id),
                "Fix stage row fields to satisfy schemas/session_stage.schema.json.",
                {"stage_id": stage_id, "schema_id": "session_stage"},
                str(first.get("path", "$")),
            )
        if not bool(row.get("deterministic", False)):
            return {}, refusal(
                "REFUSE_SESSION_STAGE_REGISTRY_INVALID",
                "stage '{}' has deterministic=false; canonical stages must be deterministic".format(stage_id),
                "Set deterministic=true for canonical session stages.",
                {"stage_id": stage_id},
                "$.deterministic",
            )
        stage_map[stage_id] = copy.deepcopy(row)

    for stage_id in sorted(stage_map.keys()):
        stage = stage_map[stage_id]
        allowed = stage.get("allowed_next_stage_ids")
        for candidate in sorted(set(str(item).strip() for item in (allowed or []) if str(item).strip())):
            if candidate not in stage_map:
                return {}, refusal(
                    "REFUSE_SESSION_STAGE_REGISTRY_INVALID",
                    "stage '{}' points to unknown next stage '{}'".format(stage_id, candidate),
                    "Fix allowed_next_stage_ids to reference declared stage IDs.",
                    {"stage_id": stage_id, "next_stage_id": candidate},
                    "$.allowed_next_stage_ids",
                )
    return stage_map, {}


def load_session_pipeline_contract(repo_root: str, pipeline_id: str = "") -> Dict[str, object]:
    stage_payload, stage_error = _read_registry(
        repo_root=repo_root,
        rel_path=norm(STAGE_REGISTRY_REL),
        reason_code="REFUSE_SESSION_STAGE_REGISTRY_INVALID",
    )
    if stage_error:
        return stage_error
    stage_rows, stage_rows_error = _rows(
        payload=stage_payload,
        rel_path=norm(STAGE_REGISTRY_REL),
        key="stages",
        reason_code="REFUSE_SESSION_STAGE_REGISTRY_INVALID",
    )
    if stage_rows_error:
        return stage_rows_error
    stage_map, stage_map_error = _validate_stage_rows(repo_root=repo_root, stage_rows=stage_rows)
    if stage_map_error:
        return stage_map_error

    pipeline_payload, pipeline_error = _read_registry(
        repo_root=repo_root,
        rel_path=norm(PIPELINE_REGISTRY_REL),
        reason_code="REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
    )
    if pipeline_error:
        return pipeline_error
    pipeline_rows, pipeline_rows_error = _rows(
        payload=pipeline_payload,
        rel_path=norm(PIPELINE_REGISTRY_REL),
        key="pipelines",
        reason_code="REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
    )
    if pipeline_rows_error:
        return pipeline_rows_error

    selected_pipeline_id = str(pipeline_id).strip() or DEFAULT_PIPELINE_ID
    selected = {}
    for row in sorted(pipeline_rows, key=lambda item: str(item.get("pipeline_id", ""))):
        token = str(row.get("pipeline_id", "")).strip()
        if not token:
            return refusal(
                "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
                "pipeline registry contains an empty pipeline_id",
                "Set pipeline_id for all pipeline rows.",
                {"pipeline_id": "<empty>"},
                "$.record.pipelines",
            )
        if token == selected_pipeline_id:
            selected = dict(row)
            break
    if not selected:
        return refusal(
            "REFUSE_SESSION_PIPELINE_UNKNOWN",
            "pipeline_id '{}' is not defined in session pipeline registry".format(selected_pipeline_id),
            "Use a declared pipeline_id from data/registries/session_pipeline_registry.json.",
            {"pipeline_id": selected_pipeline_id},
            "$.pipeline_id",
        )

    validated_pipeline = validate_instance(
        repo_root=repo_root,
        schema_name="session_pipeline",
        payload=selected,
        strict_top_level=True,
    )
    if not bool(validated_pipeline.get("valid", False)):
        first = list(validated_pipeline.get("errors") or [{}])[0]
        return refusal(
            "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
            "pipeline '{}' failed session_pipeline schema validation".format(selected_pipeline_id),
            "Fix pipeline fields to satisfy schemas/session_pipeline.schema.json.",
            {"pipeline_id": selected_pipeline_id, "schema_id": "session_pipeline"},
            str(first.get("path", "$")),
        )

    stage_order = [str(item).strip() for item in (selected.get("stages") or []) if str(item).strip()]
    if len(stage_order) != len(set(stage_order)):
        return refusal(
            "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
            "pipeline '{}' contains duplicate stage IDs".format(selected_pipeline_id),
            "Ensure stages list is unique and ordered.",
            {"pipeline_id": selected_pipeline_id},
            "$.stages",
        )
    for stage_id in stage_order:
        if stage_id not in stage_map:
            return refusal(
                "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
                "pipeline '{}' references unknown stage '{}'".format(selected_pipeline_id, stage_id),
                "Add the stage to session_stage_registry or remove it from pipeline.",
                {"pipeline_id": selected_pipeline_id, "stage_id": stage_id},
                "$.stages",
            )

    for token in (
        str(selected.get("entry_stage_id", "")).strip(),
        str(selected.get("ready_stage_id", "")).strip(),
        str(selected.get("running_stage_id", "")).strip(),
        str(selected.get("teardown_stage_id", "")).strip(),
    ):
        if token not in stage_map:
            return refusal(
                "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
                "pipeline '{}' references unknown canonical stage '{}'".format(selected_pipeline_id, token),
                "Set pipeline canonical stage IDs to declared stage IDs.",
                {"pipeline_id": selected_pipeline_id, "stage_id": token},
                "$",
            )
        if token not in stage_order:
            return refusal(
                "REFUSE_SESSION_PIPELINE_REGISTRY_INVALID",
                "pipeline '{}' canonical stage '{}' is missing from ordered stages".format(selected_pipeline_id, token),
                "Include canonical stage IDs in the pipeline stage order.",
                {"pipeline_id": selected_pipeline_id, "stage_id": token},
                "$.stages",
            )

    return {
        "result": "complete",
        "pipeline_id": selected_pipeline_id,
        "stage_order": list(stage_order),
        "stage_map": stage_map,
        "pipeline": copy.deepcopy(selected),
        "stage_registry_path": norm(STAGE_REGISTRY_REL),
        "pipeline_registry_path": norm(PIPELINE_REGISTRY_REL),
        "stage_registry_hash": canonical_sha256(stage_payload),
        "pipeline_registry_hash": canonical_sha256(pipeline_payload),
    }
