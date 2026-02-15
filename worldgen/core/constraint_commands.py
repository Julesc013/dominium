"""Command-graph style worldgen constraint preview/commit helpers."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
from tools.xstack.compatx.validator import validate_instance

from .pipeline import run_worldgen_pipeline


STATE_DIR_REL = "build/cache/assets/worldgen_constraints"
STATE_FILE_NAME = "state.json"
DEFAULT_REQUIRED_ENTITLEMENT = "entitlement.worldgen.constraints"
DEFAULT_COMMIT_ENTITLEMENT = "entitlement.worldgen.commit"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _write_canonical_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def _read_json_object(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _refusal(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str], path: str = "$") -> Dict[str, object]:
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": dict(sorted((relevant_ids or {}).items(), key=lambda item: str(item[0]))),
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def _state_path(repo_root: str) -> str:
    return os.path.join(repo_root, STATE_DIR_REL.replace("/", os.sep), STATE_FILE_NAME)


def _load_module_registry(repo_root: str) -> Tuple[dict, Dict[str, object]]:
    path = os.path.join(repo_root, "data", "registries", "worldgen_module_registry.json")
    payload, err = _read_json_object(path)
    if err:
        return {}, _refusal(
            "REFUSE_WORLDGEN_MODULE_REGISTRY_MISSING",
            "worldgen module registry is missing or invalid",
            "Provide data/registries/worldgen_module_registry.json.",
            {"registry_path": _norm(path)},
            "$.module_registry",
        )
    return payload, {}


def _load_constraints(repo_root: str, constraints_file: str) -> Tuple[dict, Dict[str, object]]:
    token = str(constraints_file).strip()
    if not token:
        return {}, _refusal(
            "REFUSE_CONSTRAINTS_FILE_MISSING",
            "constraints_file is required",
            "Provide --constraints-file path.",
            {"constraints_file": "<missing>"},
            "$.constraints_file",
        )
    abs_path = os.path.normpath(token if os.path.isabs(token) else os.path.join(repo_root, token))
    payload, err = _read_json_object(abs_path)
    if err:
        return {}, _refusal(
            "REFUSE_CONSTRAINTS_INVALID_JSON",
            "constraints file is missing or invalid JSON",
            "Fix constraints artifact file and retry.",
            {"constraints_file": _norm(abs_path)},
            "$.constraints_file",
        )
    valid = validate_instance(
        repo_root=repo_root,
        schema_name="worldgen_constraints",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(valid.get("valid", False)):
        return {}, _refusal(
            "REFUSE_CONSTRAINTS_SCHEMA_INVALID",
            "constraints file failed schema validation",
            "Fix constraints file fields against schemas/worldgen_constraints.schema.json.",
            {"constraints_file": _norm(abs_path)},
            "$.constraints_file",
        )
    return payload, {}


def _authoritative_context(authority_context: dict) -> dict:
    payload = dict(authority_context or {})
    entitlements = payload.get("entitlements")
    if not isinstance(entitlements, list):
        entitlements = []
    payload["entitlements"] = sorted(set(str(item).strip() for item in entitlements if str(item).strip()))
    payload["authority_origin"] = str(payload.get("authority_origin", "tool")).strip() or "tool"
    payload["privilege_level"] = str(payload.get("privilege_level", "operator")).strip() or "operator"
    return payload


def _check_entitlements(authority_context: dict, required: List[str]) -> Dict[str, object]:
    granted = set(str(item).strip() for item in (authority_context.get("entitlements") or []) if str(item).strip())
    missing = sorted(set(str(item).strip() for item in required if str(item).strip()) - granted)
    if missing:
        return _refusal(
            "ENTITLEMENT_MISSING",
            "required entitlements missing for worldgen command",
            "Grant required entitlements before running worldgen command.",
            {"missing_entitlements": ",".join(missing)},
            "$.authority_context.entitlements",
        )
    return {"result": "complete"}


def _intent(command_id: str, payload: dict, authority_context: dict) -> dict:
    body = {
        "command_id": str(command_id),
        "payload": dict(payload or {}),
        "authority_context": _authoritative_context(authority_context),
    }
    body["intent_hash"] = canonical_sha256(body)
    return body


def worldgen_constraints_set(
    repo_root: str,
    constraints_file: str,
    constraints_id: str,
    base_seed: str,
    authority_context: dict,
) -> Dict[str, object]:
    context = _authoritative_context(authority_context)
    auth = _check_entitlements(context, [DEFAULT_REQUIRED_ENTITLEMENT])
    if auth.get("result") != "complete":
        return auth

    constraints_payload, constraints_error = _load_constraints(repo_root=repo_root, constraints_file=constraints_file)
    if constraints_error:
        return constraints_error
    payload_constraints_id = str(constraints_payload.get("constraints_id", "")).strip()
    requested_id = str(constraints_id).strip()
    if requested_id and requested_id != payload_constraints_id:
        return _refusal(
            "REFUSE_CONSTRAINTS_ID_MISMATCH",
            "constraints_id does not match constraints file payload",
            "Use matching constraints_id and constraints file payload.",
            {"constraints_id": requested_id, "payload_constraints_id": payload_constraints_id},
            "$.constraints_id",
        )

    state = {
        "schema_version": "1.0.0",
        "constraints_id": payload_constraints_id,
        "constraints_file": _norm(os.path.relpath(os.path.normpath(constraints_file if os.path.isabs(constraints_file) else os.path.join(repo_root, constraints_file)), repo_root)),
        "base_seed": str(base_seed),
        "intent": _intent(
            command_id="worldgen.constraints.set",
            payload={
                "constraints_id": payload_constraints_id,
                "base_seed": str(base_seed),
            },
            authority_context=context,
        ),
    }
    state_path = _state_path(repo_root)
    _write_canonical_json(state_path, state)
    return {
        "result": "complete",
        "command_id": "worldgen.constraints.set",
        "state_path": _norm(os.path.relpath(state_path, repo_root)),
        "constraints_id": payload_constraints_id,
        "base_seed": str(base_seed),
    }


def worldgen_constraints_clear(repo_root: str, authority_context: dict) -> Dict[str, object]:
    context = _authoritative_context(authority_context)
    auth = _check_entitlements(context, [DEFAULT_REQUIRED_ENTITLEMENT])
    if auth.get("result") != "complete":
        return auth
    state_path = _state_path(repo_root)
    if os.path.isfile(state_path):
        os.remove(state_path)
    return {
        "result": "complete",
        "command_id": "worldgen.constraints.clear",
        "state_path": _norm(os.path.relpath(state_path, repo_root)),
    }


def _load_state(repo_root: str) -> Tuple[dict, Dict[str, object]]:
    state_path = _state_path(repo_root)
    if not os.path.isfile(state_path):
        return {}, _refusal(
            "REFUSE_CONSTRAINT_STATE_MISSING",
            "worldgen constraints state is not set",
            "Run worldgen.constraints.set before preview or commit.",
            {"state_path": _norm(os.path.relpath(state_path, repo_root))},
            "$.state",
        )
    payload, err = _read_json_object(state_path)
    if err:
        return {}, _refusal(
            "REFUSE_CONSTRAINT_STATE_INVALID",
            "worldgen constraints state is invalid JSON",
            "Clear and re-set constraints state.",
            {"state_path": _norm(os.path.relpath(state_path, repo_root))},
            "$.state",
        )
    return payload, {}


def _preview_payload(repo_root: str, state_payload: dict) -> Dict[str, object]:
    constraints_file = str(state_payload.get("constraints_file", "")).strip()
    base_seed = str(state_payload.get("base_seed", "")).strip()
    constraints_payload, constraints_error = _load_constraints(repo_root=repo_root, constraints_file=constraints_file)
    if constraints_error:
        return constraints_error
    module_registry_payload, module_registry_error = _load_module_registry(repo_root=repo_root)
    if module_registry_error:
        return module_registry_error

    pipeline = run_worldgen_pipeline(
        repo_root=repo_root,
        base_seed=base_seed,
        module_registry_payload=module_registry_payload,
        constraints_payload=constraints_payload,
    )
    if pipeline.get("result") != "complete":
        return pipeline
    search_plan = dict(pipeline.get("search_plan") or {})
    scoring_summary = dict(search_plan.get("scoring_summary") or {})
    candidates = list(scoring_summary.get("candidate_results") or [])
    candidates = sorted(
        [dict(row) for row in candidates if isinstance(row, dict)],
        key=lambda row: (int(row.get("rank", 0) or 0), str(row.get("seed", ""))),
    )
    return {
        "result": "complete",
        "constraints_id": str(search_plan.get("constraints_id", "")),
        "selected_seed": str(search_plan.get("selected_seed", "")),
        "search_plan_hash": str(search_plan.get("deterministic_hash", "")),
        "candidate_scores": candidates,
        "constraints_satisfied": int(sum(1 for row in candidates if bool(row.get("hard_pass")))),
        "constraints_violated": int(sum(1 for row in candidates if not bool(row.get("hard_pass")))),
        "stage_log": list(pipeline.get("stage_log") or []),
        "search_plan": search_plan,
    }


def worldgen_search_preview(repo_root: str, authority_context: dict) -> Dict[str, object]:
    context = _authoritative_context(authority_context)
    auth = _check_entitlements(context, [DEFAULT_REQUIRED_ENTITLEMENT])
    if auth.get("result") != "complete":
        return auth
    state_payload, state_error = _load_state(repo_root=repo_root)
    if state_error:
        return state_error
    preview = _preview_payload(repo_root=repo_root, state_payload=state_payload)
    if preview.get("result") != "complete":
        return preview
    preview["command_id"] = "worldgen.search.preview"
    preview["intent"] = _intent(
        command_id="worldgen.search.preview",
        payload={"constraints_id": str(preview.get("constraints_id", ""))},
        authority_context=context,
    )
    return preview


def worldgen_search_commit(repo_root: str, authority_context: dict) -> Dict[str, object]:
    context = _authoritative_context(authority_context)
    auth = _check_entitlements(context, [DEFAULT_REQUIRED_ENTITLEMENT, DEFAULT_COMMIT_ENTITLEMENT])
    if auth.get("result") != "complete":
        return auth
    state_payload, state_error = _load_state(repo_root=repo_root)
    if state_error:
        return state_error
    preview = _preview_payload(repo_root=repo_root, state_payload=state_payload)
    if preview.get("result") != "complete":
        return preview

    constraints_id = str(preview.get("constraints_id", "")).strip()
    out_dir = os.path.join(repo_root, STATE_DIR_REL.replace("/", os.sep), "commits")
    _ensure_dir(out_dir)
    out_path = os.path.join(out_dir, "{}.search_plan.json".format(constraints_id))
    _write_canonical_json(out_path, dict(preview.get("search_plan") or {}))
    return {
        "result": "complete",
        "command_id": "worldgen.search.commit",
        "constraints_id": constraints_id,
        "selected_seed": str(preview.get("selected_seed", "")),
        "search_plan_hash": str(preview.get("search_plan_hash", "")),
        "commit_path": _norm(os.path.relpath(out_path, repo_root)),
        "intent": _intent(
            command_id="worldgen.search.commit",
            payload={
                "constraints_id": constraints_id,
                "selected_seed": str(preview.get("selected_seed", "")),
                "search_plan_hash": str(preview.get("search_plan_hash", "")),
            },
            authority_context=context,
        ),
    }

