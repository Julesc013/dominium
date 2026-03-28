"""Deterministic ACT-3 task/work helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from materials.dimension_engine import FixedPointOverflow, fixed_point_add, fixed_point_config_from_policy, fixed_point_type
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_TASK_TOOL_REQUIRED = "refusal.task.tool_required"
REFUSAL_TASK_FORBIDDEN_BY_LAW = "refusal.task.forbidden_by_law"
REFUSAL_TASK_BUDGET_EXCEEDED = "refusal.task.budget_exceeded"

_VALID_TASK_STATUSES = {"planned", "running", "paused", "completed", "failed", "cancelled"}
_STATUS_SORT_ORDER = {"running": 0, "planned": 1, "paused": 2, "completed": 3, "failed": 4, "cancelled": 5}


class TaskError(ValueError):
    """Deterministic task refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _registry_rows(payload: Mapping[str, object] | None, list_key: str) -> List[dict]:
    root = dict(payload or {})
    rows = root.get(list_key)
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get(list_key)
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, dict)]


def task_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    rows = _registry_rows(registry_payload, "task_types")
    for row in sorted(rows, key=lambda item: str(item.get("task_type_id", ""))):
        task_type_id = str(row.get("task_type_id", "")).strip()
        if not task_type_id:
            continue
        out[task_type_id] = {
            "schema_version": "1.0.0",
            "task_type_id": task_type_id,
            "description": str(row.get("description", "")).strip(),
            "default_progress_units_total": max(1, _as_int(row.get("default_progress_units_total", 1 << 24), 1 << 24)),
            "required_tool_tags": _sorted_unique_strings(row.get("required_tool_tags")),
            "allowed_surface_types": _sorted_unique_strings(row.get("allowed_surface_types")),
            "completion_process_id": str(row.get("completion_process_id", "")).strip(),
            "progress_model_id": str(row.get("progress_model_id", "")).strip() or "progress.linear_default",
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def progress_model_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    rows = _registry_rows(registry_payload, "progress_models")
    for row in sorted(rows, key=lambda item: str(item.get("progress_model_id", ""))):
        progress_model_id = str(row.get("progress_model_id", "")).strip()
        if not progress_model_id:
            continue
        out[progress_model_id] = {
            "schema_version": "1.0.0",
            "progress_model_id": progress_model_id,
            "description": str(row.get("description", "")).strip(),
            "progress_rate_base": max(0, _as_int(row.get("progress_rate_base", 0), 0)),
            "tool_efficiency_applies": bool(row.get("tool_efficiency_applies", False)),
            "actor_efficiency_applies": bool(row.get("actor_efficiency_applies", False)),
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def _fingerprint(row: Mapping[str, object]) -> str:
    seed = dict(row or {})
    seed["deterministic_fingerprint"] = ""
    return canonical_sha256(seed)


def normalize_task_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    task_id = str(payload.get("task_id", "")).strip()
    task_type_id = str(payload.get("task_type_id", "")).strip()
    actor_subject_id = str(payload.get("actor_subject_id", "")).strip()
    target_semantic_id = str(payload.get("target_semantic_id", "")).strip()
    process_id_to_execute = str(payload.get("process_id_to_execute", "")).strip()
    if not task_id or not task_type_id or not actor_subject_id or not target_semantic_id or not process_id_to_execute:
        raise TaskError(
            "PROCESS_INPUT_INVALID",
            "task row is missing required deterministic identity fields",
            {
                "task_id": task_id,
                "task_type_id": task_type_id,
                "actor_subject_id": actor_subject_id,
                "target_semantic_id": target_semantic_id,
                "process_id_to_execute": process_id_to_execute,
            },
        )
    status = str(payload.get("status", "planned")).strip() or "planned"
    if status not in _VALID_TASK_STATUSES:
        status = "planned"
    progress_total = max(1, _as_int(payload.get("progress_units_total", 1 << 24), 1 << 24))
    progress_done = max(0, _as_int(payload.get("progress_units_done", 0), 0))
    if progress_done > progress_total:
        progress_done = progress_total
    normalized = {
        "schema_version": "1.0.0",
        "task_id": task_id,
        "task_type_id": task_type_id,
        "actor_subject_id": actor_subject_id,
        "target_semantic_id": target_semantic_id,
        "surface_id": None if payload.get("surface_id") is None else str(payload.get("surface_id", "")).strip() or None,
        "tool_id": None if payload.get("tool_id") is None else str(payload.get("tool_id", "")).strip() or None,
        "process_id_to_execute": process_id_to_execute,
        "parameters": dict(payload.get("parameters") or {}) if isinstance(payload.get("parameters"), dict) else {},
        "created_tick": max(0, _as_int(payload.get("created_tick", 0), 0)),
        "started_tick": None if payload.get("started_tick") is None else max(0, _as_int(payload.get("started_tick", 0), 0)),
        "last_progress_tick": None if payload.get("last_progress_tick") is None else max(0, _as_int(payload.get("last_progress_tick", 0), 0)),
        "status": status,
        "progress_units_total": int(progress_total),
        "progress_units_done": int(progress_done),
        "cost_units_per_tick": max(0, _as_int(payload.get("cost_units_per_tick", 1), 1)),
        "linked_commitment_id": None if payload.get("linked_commitment_id") is None else str(payload.get("linked_commitment_id", "")).strip() or None,
        "linked_event_ids": _sorted_unique_strings(payload.get("linked_event_ids")),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }
    if not normalized["deterministic_fingerprint"]:
        normalized["deterministic_fingerprint"] = _fingerprint(normalized)
    return normalized


def normalize_task_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("task_id", ""))):
        try:
            normalized = normalize_task_row(row)
        except TaskError:
            continue
        out[str(normalized.get("task_id", ""))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]

def _task_id(
    *,
    task_type_id: str,
    actor_subject_id: str,
    target_semantic_id: str,
    process_id_to_execute: str,
    surface_id: str,
    created_tick: int,
) -> str:
    return "task.{}".format(
        canonical_sha256(
            {
                "task_type_id": str(task_type_id),
                "actor_subject_id": str(actor_subject_id),
                "target_semantic_id": str(target_semantic_id),
                "process_id_to_execute": str(process_id_to_execute),
                "surface_id": str(surface_id),
                "created_tick": int(max(0, int(created_tick))),
            }
        )[:20]
    )


def resolve_task_type_for_completion_process(
    *,
    completion_process_id: str,
    surface_type_id: str,
    task_type_registry: Mapping[str, object] | None,
) -> dict:
    process_id = str(completion_process_id).strip()
    surface_type = str(surface_type_id).strip()
    rows_by_id = task_type_rows_by_id(task_type_registry)
    for task_type_id in sorted(rows_by_id.keys()):
        row = dict(rows_by_id[task_type_id])
        if str(row.get("completion_process_id", "")).strip() != process_id:
            continue
        allowed_surface_types = set(_sorted_unique_strings(row.get("allowed_surface_types")))
        if allowed_surface_types and surface_type and surface_type not in allowed_surface_types:
            continue
        return row
    return {}


def create_task_row(
    *,
    inputs: Mapping[str, object],
    current_tick: int,
    task_type_registry: Mapping[str, object] | None,
    progress_model_registry: Mapping[str, object] | None,
    numeric_policy: Mapping[str, object] | None = None,
) -> dict:
    payload = dict(inputs or {})
    task_type_id = str(payload.get("task_type_id", "")).strip()
    process_id_to_execute = str(payload.get("process_id_to_execute", "") or payload.get("completion_process_id", "") or payload.get("process_id", "")).strip()
    surface_type_id = str(payload.get("surface_type_id", "")).strip()

    task_types = task_type_rows_by_id(task_type_registry)
    task_type_row = dict(task_types.get(task_type_id) or {})
    if not task_type_row:
        task_type_row = resolve_task_type_for_completion_process(
            completion_process_id=process_id_to_execute,
            surface_type_id=surface_type_id,
            task_type_registry=task_type_registry,
        )
    if not task_type_row:
        raise TaskError(
            "PROCESS_INPUT_INVALID",
            "no task_type is available for task creation payload",
            {
                "task_type_id": task_type_id,
                "process_id_to_execute": process_id_to_execute,
                "surface_type_id": surface_type_id,
            },
        )

    task_type_id = str(task_type_row.get("task_type_id", "")).strip()
    completion_process_id = str(task_type_row.get("completion_process_id", "")).strip()
    if not process_id_to_execute:
        process_id_to_execute = completion_process_id
    if not process_id_to_execute:
        raise TaskError("PROCESS_INPUT_INVALID", "task_type has no completion_process_id", {"task_type_id": task_type_id})

    actor_subject_id = str(payload.get("actor_subject_id", "") or payload.get("subject_id", "") or payload.get("agent_id", "") or payload.get("controller_id", "")).strip()
    target_semantic_id = str(payload.get("target_semantic_id", "") or payload.get("target_id", "")).strip()
    if not actor_subject_id or not target_semantic_id:
        raise TaskError(
            "PROCESS_INPUT_INVALID",
            "task creation requires actor_subject_id and target_semantic_id",
            {
                "actor_subject_id": actor_subject_id,
                "target_semantic_id": target_semantic_id,
            },
        )

    required_tool_tags = set(_sorted_unique_strings(task_type_row.get("required_tool_tags")))
    active_tool_tags = set(_sorted_unique_strings(payload.get("active_tool_tags")))
    if required_tool_tags and not active_tool_tags.intersection(required_tool_tags):
        raise TaskError(
            REFUSAL_TASK_TOOL_REQUIRED,
            "task requires compatible tool tag(s)",
            {
                "task_type_id": task_type_id,
                "required_tool_tags": ",".join(sorted(required_tool_tags)),
                "active_tool_tags": ",".join(sorted(active_tool_tags)),
            },
        )

    progress_models = progress_model_rows_by_id(progress_model_registry)
    progress_model_id = str(payload.get("progress_model_id", "")).strip() or str(task_type_row.get("progress_model_id", "")).strip()
    progress_model_row = dict(progress_models.get(progress_model_id) or {})
    if not progress_model_row:
        fallback_id = "progress.linear_default" if "progress.linear_default" in set(progress_models.keys()) else ""
        if fallback_id:
            progress_model_row = dict(progress_models.get(fallback_id) or {})
            progress_model_id = fallback_id
    if not progress_model_row:
        progress_model_row = {
            "progress_model_id": "progress.linear_default",
            "progress_rate_base": 1 << 22,
            "tool_efficiency_applies": True,
            "actor_efficiency_applies": False,
            "extensions": {},
        }
        progress_model_id = "progress.linear_default"

    config = fixed_point_config_from_policy(numeric_policy)
    progress_units_total = _as_int(payload.get("progress_units_total", task_type_row.get("default_progress_units_total", config.scale)), config.scale)
    progress_units_total = max(1, fixed_point_type(int(progress_units_total), config=config))
    progress_units_done = max(0, _as_int(payload.get("progress_units_done", 0), 0))
    if progress_units_done > progress_units_total:
        progress_units_done = progress_units_total
    task_status = str(payload.get("status", "running")).strip() or "running"
    if task_status not in _VALID_TASK_STATUSES:
        task_status = "running"
    created_tick = max(0, _as_int(payload.get("created_tick", current_tick), current_tick))
    started_tick = payload.get("started_tick")
    if started_tick is None and task_status == "running":
        started_tick = int(created_tick)
    last_progress_tick = payload.get("last_progress_tick")
    if last_progress_tick is None and task_status == "running":
        last_progress_tick = int(created_tick)

    surface_id = None if payload.get("surface_id") is None else str(payload.get("surface_id", "")).strip() or None
    tool_id = None if payload.get("tool_id") is None else str(payload.get("tool_id", "")).strip() or None
    deterministic_task_id = str(payload.get("task_id", "")).strip() or _task_id(
        task_type_id=task_type_id,
        actor_subject_id=actor_subject_id,
        target_semantic_id=target_semantic_id,
        process_id_to_execute=process_id_to_execute,
        surface_id=str(surface_id or ""),
        created_tick=int(created_tick),
    )
    extensions = dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {}
    extensions["progress_model_id"] = str(progress_model_id)
    extensions["surface_type_id"] = str(surface_type_id)
    extensions["required_tool_tags"] = sorted(required_tool_tags)
    extensions["task_priority"] = _as_int(extensions.get("task_priority", payload.get("task_priority", 0)), 0)

    return normalize_task_row(
        {
            "schema_version": "1.0.0",
            "task_id": deterministic_task_id,
            "task_type_id": task_type_id,
            "actor_subject_id": actor_subject_id,
            "target_semantic_id": target_semantic_id,
            "surface_id": surface_id,
            "tool_id": tool_id,
            "process_id_to_execute": process_id_to_execute,
            "parameters": dict(payload.get("parameters") or {}) if isinstance(payload.get("parameters"), dict) else {},
            "created_tick": int(created_tick),
            "started_tick": None if started_tick is None else max(0, _as_int(started_tick, created_tick)),
            "last_progress_tick": None if last_progress_tick is None else max(0, _as_int(last_progress_tick, created_tick)),
            "status": task_status,
            "progress_units_total": int(progress_units_total),
            "progress_units_done": int(progress_units_done),
            "cost_units_per_tick": max(0, _as_int(payload.get("cost_units_per_tick", 1), 1)),
            "linked_commitment_id": None if payload.get("linked_commitment_id") is None else str(payload.get("linked_commitment_id", "")).strip() or None,
            "linked_event_ids": _sorted_unique_strings(payload.get("linked_event_ids")),
            "deterministic_fingerprint": "",
            "extensions": extensions,
        }
    )


def _task_event(*, task_row: Mapping[str, object], event_type_id: str, tick: int, sequence: int, progress_units_done: int) -> dict:
    event_id = "provenance.event.{}".format(
        canonical_sha256(
            {
                "task_id": str(task_row.get("task_id", "")),
                "event_type_id": str(event_type_id),
                "tick": int(max(0, int(tick))),
                "sequence": int(max(0, int(sequence))),
            }
        )[:24]
    )
    row = {
        "schema_version": "1.0.0",
        "event_id": event_id,
        "tick": int(max(0, int(tick))),
        "event_type_id": str(event_type_id),
        "actor_subject_id": str(task_row.get("actor_subject_id", "")).strip() or "subject.system",
        "site_ref": "task:{}".format(str(task_row.get("target_semantic_id", "")).strip()),
        "inputs": [],
        "outputs": [],
        "ledger_deltas": {},
        "linked_project_id": None,
        "linked_step_id": None,
        "deterministic_fingerprint": "",
        "extensions": {
            "task_id": str(task_row.get("task_id", "")).strip(),
            "task_type_id": str(task_row.get("task_type_id", "")).strip(),
            "target_semantic_id": str(task_row.get("target_semantic_id", "")).strip(),
            "surface_id": None if task_row.get("surface_id") is None else str(task_row.get("surface_id", "")).strip() or None,
            "tool_id": None if task_row.get("tool_id") is None else str(task_row.get("tool_id", "")).strip() or None,
            "progress_units_done": int(max(0, int(progress_units_done))),
            "progress_units_total": int(max(0, int(task_row.get("progress_units_total", 0) or 0))),
            "commitment_id": None if task_row.get("linked_commitment_id") is None else str(task_row.get("linked_commitment_id", "")).strip() or None,
        },
    }
    row["deterministic_fingerprint"] = _fingerprint(row)
    return row


def _completion_intent(*, task_row: Mapping[str, object], completion_index: int, completion_tick: int) -> dict:
    parameters = dict(task_row.get("parameters") or {}) if isinstance(task_row.get("parameters"), dict) else {}
    inputs = dict(parameters)
    inputs["task_id"] = str(task_row.get("task_id", "")).strip()
    inputs["target_semantic_id"] = str(task_row.get("target_semantic_id", "")).strip()
    if task_row.get("surface_id") is not None:
        inputs["surface_id"] = str(task_row.get("surface_id", "")).strip()
    if task_row.get("tool_id") is not None:
        inputs["tool_id"] = str(task_row.get("tool_id", "")).strip()
    intent_id = "intent.task.complete.{}".format(
        canonical_sha256(
            {
                "task_id": str(task_row.get("task_id", "")),
                "process_id": str(task_row.get("process_id_to_execute", "")),
                "completion_index": int(max(0, int(completion_index))),
                "completion_tick": int(max(0, int(completion_tick))),
                "inputs": dict(inputs),
            }
        )[:16]
    )
    return {
        "intent_id": intent_id,
        "process_id": str(task_row.get("process_id_to_execute", "")).strip(),
        "inputs": dict(inputs),
        "authority_context_ref": {
            "authority_origin": "task_engine",
            "law_profile_id": "",
        },
        "extensions": {
            "source": "task_completion",
            "task_id": str(task_row.get("task_id", "")).strip(),
            "task_type_id": str(task_row.get("task_type_id", "")).strip(),
            "target_semantic_id": str(task_row.get("target_semantic_id", "")).strip(),
        },
    }

def tick_tasks(
    *,
    task_rows: object,
    current_tick: int,
    dt_ticks: int,
    task_type_registry: Mapping[str, object] | None,
    progress_model_registry: Mapping[str, object] | None,
    numeric_policy: Mapping[str, object] | None = None,
    max_cost_units: int = 0,
    strict_budget: bool = False,
    event_sequence_start: int = 0,
) -> dict:
    config = fixed_point_config_from_policy(numeric_policy)
    rows = normalize_task_rows(task_rows)
    task_types = task_type_rows_by_id(task_type_registry)
    progress_models = progress_model_rows_by_id(progress_model_registry)
    now_tick = int(max(0, int(current_tick)))
    dt = int(max(0, int(dt_ticks)))
    if dt <= 0:
        return {
            "tasks": rows,
            "events": [],
            "completion_intents": [],
            "cost_units_used": 0,
            "processed_task_ids": [],
            "degraded_task_ids": [],
            "completed_task_ids": [],
            "next_event_sequence": int(max(0, int(event_sequence_start))),
        }

    ordered = sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=lambda row: (
            int(_STATUS_SORT_ORDER.get(str(row.get("status", "planned")).strip(), 9)),
            -int(_as_int(dict(row.get("extensions") or {}).get("task_priority", 0), 0)),
            str(row.get("task_id", "")),
        ),
    )
    bounded_budget = max(0, int(max_cost_units))
    strict = bool(strict_budget)
    cost_used = 0
    sequence = int(max(0, int(event_sequence_start)))
    events: List[dict] = []
    completion_intents: List[dict] = []
    processed_task_ids: List[str] = []
    degraded_task_ids: List[str] = []
    completed_task_ids: List[str] = []

    for row in ordered:
        task_id = str(row.get("task_id", "")).strip()
        if not task_id:
            continue
        status = str(row.get("status", "planned")).strip() or "planned"
        if status in ("completed", "failed", "cancelled"):
            continue
        if status == "paused":
            continue
        if status == "planned":
            row["status"] = "running"
            row["started_tick"] = int(now_tick)
            row["last_progress_tick"] = int(now_tick)
            events.append(
                _task_event(
                    task_row=row,
                    event_type_id="event.task_started",
                    tick=int(now_tick),
                    sequence=sequence,
                    progress_units_done=int(_as_int(row.get("progress_units_done", 0), 0)),
                )
            )
            sequence += 1

        task_cost = int(max(0, _as_int(row.get("cost_units_per_tick", 0), 0)))
        if bounded_budget > 0 and int(cost_used + task_cost) > int(bounded_budget):
            if strict:
                raise TaskError(
                    REFUSAL_TASK_BUDGET_EXCEEDED,
                    "task tick budget exceeded under strict mode",
                    {
                        "task_id": task_id,
                        "max_cost_units": int(bounded_budget),
                        "cost_used": int(cost_used),
                        "task_cost_units": int(task_cost),
                    },
                )
            row["status"] = "paused"
            ext = dict(row.get("extensions") or {})
            ext["paused_reason"] = "budget_degrade"
            ext["paused_tick"] = int(now_tick)
            row["extensions"] = ext
            degraded_task_ids.append(task_id)
            continue
        cost_used += int(task_cost)
        processed_task_ids.append(task_id)

        task_type_row = dict(task_types.get(str(row.get("task_type_id", "")).strip()) or {})
        progress_model_id = str((dict(row.get("extensions") or {})).get("progress_model_id", "")).strip() or str(task_type_row.get("progress_model_id", "")).strip()
        progress_model_row = dict(progress_models.get(progress_model_id) or {})
        progress_rate_base = int(max(0, _as_int(progress_model_row.get("progress_rate_base", 0), 0)))
        if progress_rate_base <= 0:
            progress_rate_base = int(config.scale // 8)

        tool_effect = dict((dict(row.get("parameters") or {})).get("tool_effect") or {})
        efficiency_permille = int(max(1, _as_int(tool_effect.get("efficiency_multiplier", 1000), 1000)))
        if not bool(progress_model_row.get("tool_efficiency_applies", False)):
            efficiency_permille = 1000
        delta_units = int((int(progress_rate_base) * int(dt) * int(efficiency_permille)) // 1000)
        delta_units = max(0, delta_units)

        try:
            updated_done = fixed_point_add(int(_as_int(row.get("progress_units_done", 0), 0)), int(delta_units), config=config)
            updated_done = fixed_point_type(updated_done, config=config)
        except FixedPointOverflow as exc:
            raise TaskError(str(exc.reason_code), str(exc), {"task_id": task_id})

        total_units = int(max(1, _as_int(row.get("progress_units_total", config.scale), config.scale)))
        if updated_done > total_units:
            updated_done = int(total_units)
        row["progress_units_done"] = int(updated_done)
        row["last_progress_tick"] = int(now_tick)
        row["deterministic_fingerprint"] = _fingerprint(row)
        events.append(
            _task_event(
                task_row=row,
                event_type_id="event.task_progress",
                tick=int(now_tick),
                sequence=sequence,
                progress_units_done=int(updated_done),
            )
        )
        sequence += 1

        if int(updated_done) < int(total_units):
            continue
        row["status"] = "completed"
        row["last_progress_tick"] = int(now_tick)
        row["deterministic_fingerprint"] = _fingerprint(row)
        completed_task_ids.append(task_id)
        completion_intents.append(
            _completion_intent(
                task_row=row,
                completion_index=int(len(completed_task_ids) - 1),
                completion_tick=int(now_tick),
            )
        )
        events.append(
            _task_event(
                task_row=row,
                event_type_id="event.task_completed",
                tick=int(now_tick),
                sequence=sequence,
                progress_units_done=int(updated_done),
            )
        )
        sequence += 1

    normalized_out = normalize_task_rows(ordered)
    completion_intents = sorted((dict(row) for row in completion_intents if isinstance(row, dict)), key=lambda row: str(row.get("intent_id", "")))
    events = sorted((dict(row) for row in events if isinstance(row, dict)), key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("event_id", ""))))
    return {
        "tasks": normalized_out,
        "events": events,
        "completion_intents": completion_intents,
        "cost_units_used": int(cost_used),
        "processed_task_ids": sorted(set(str(item).strip() for item in processed_task_ids if str(item).strip())),
        "degraded_task_ids": sorted(set(str(item).strip() for item in degraded_task_ids if str(item).strip())),
        "completed_task_ids": sorted(set(str(item).strip() for item in completed_task_ids if str(item).strip())),
        "next_event_sequence": int(sequence),
    }

def set_task_status(*, task_rows: object, task_id: str, status: str, current_tick: int, event_sequence_start: int = 0) -> dict:
    token = str(task_id).strip()
    status_token = str(status).strip()
    if status_token not in _VALID_TASK_STATUSES:
        raise TaskError("PROCESS_INPUT_INVALID", "invalid task status transition target", {"status": status_token})
    rows = normalize_task_rows(task_rows)
    out: List[dict] = []
    sequence = int(max(0, int(event_sequence_start)))
    events: List[dict] = []
    found = False
    for row in rows:
        task_row = dict(row)
        if str(task_row.get("task_id", "")).strip() != token:
            out.append(task_row)
            continue
        found = True
        task_row["status"] = status_token
        if status_token == "running" and task_row.get("started_tick") is None:
            task_row["started_tick"] = int(max(0, int(current_tick)))
        task_row["last_progress_tick"] = int(max(0, int(current_tick)))
        task_row["deterministic_fingerprint"] = _fingerprint(task_row)
        out.append(task_row)
        event_type = "event.task_status_changed"
        if status_token == "paused":
            event_type = "event.task_paused"
        elif status_token == "running":
            event_type = "event.task_resumed"
        elif status_token == "cancelled":
            event_type = "event.task_cancelled"
        events.append(
            _task_event(
                task_row=task_row,
                event_type_id=event_type,
                tick=int(max(0, int(current_tick))),
                sequence=sequence,
                progress_units_done=int(_as_int(task_row.get("progress_units_done", 0), 0)),
            )
        )
        sequence += 1
    if not found:
        raise TaskError("PROCESS_INPUT_INVALID", "task_id is not present in state", {"task_id": token})
    return {
        "tasks": normalize_task_rows(out),
        "events": sorted(events, key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("event_id", "")))),
        "next_event_sequence": int(sequence),
    }


def build_task_timeline(*, task_rows: object, event_rows: object, task_id: str = "") -> dict:
    task_map = dict((str(row.get("task_id", "")).strip(), dict(row)) for row in normalize_task_rows(task_rows) if str(row.get("task_id", "")).strip())
    event_list = [dict(row) for row in list(event_rows or []) if isinstance(row, dict) and str(row.get("event_id", "")).strip()]
    target_task_id = str(task_id).strip()
    ordered_task_ids = sorted(task_map.keys()) if not target_task_id else ([target_task_id] if target_task_id in set(task_map.keys()) else [])

    timeline_rows = []
    for token in ordered_task_ids:
        task_row = dict(task_map[token])
        task_events = []
        for event in sorted(event_list, key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("event_id", "")))):
            ext = dict(event.get("extensions") or {}) if isinstance(event.get("extensions"), dict) else {}
            if str(ext.get("task_id", "")).strip() != token:
                continue
            task_events.append(
                {
                    "tick": int(max(0, _as_int(event.get("tick", 0), 0))),
                    "event_id": str(event.get("event_id", "")).strip(),
                    "event_type_id": str(event.get("event_type_id", "")).strip(),
                    "progress_units_done": int(max(0, _as_int(ext.get("progress_units_done", 0), 0))),
                }
            )
        timeline_rows.append(
            {
                "task_id": token,
                "task_type_id": str(task_row.get("task_type_id", "")).strip(),
                "status": str(task_row.get("status", "")).strip(),
                "created_tick": int(max(0, _as_int(task_row.get("created_tick", 0), 0))),
                "started_tick": None if task_row.get("started_tick") is None else int(max(0, _as_int(task_row.get("started_tick", 0), 0))),
                "last_progress_tick": None if task_row.get("last_progress_tick") is None else int(max(0, _as_int(task_row.get("last_progress_tick", 0), 0))),
                "progress_units_total": int(max(0, _as_int(task_row.get("progress_units_total", 0), 0))),
                "progress_units_done": int(max(0, _as_int(task_row.get("progress_units_done", 0), 0))),
                "linked_commitment_id": None if task_row.get("linked_commitment_id") is None else str(task_row.get("linked_commitment_id", "")).strip() or None,
                "event_timeline": task_events,
            }
        )
    return {
        "schema_version": "1.0.0",
        "task_id_filter": target_task_id or None,
        "tasks": timeline_rows,
        "timeline_hash": canonical_sha256(timeline_rows),
    }


__all__ = [
    "TaskError",
    "REFUSAL_TASK_TOOL_REQUIRED",
    "REFUSAL_TASK_FORBIDDEN_BY_LAW",
    "REFUSAL_TASK_BUDGET_EXCEEDED",
    "task_type_rows_by_id",
    "progress_model_rows_by_id",
    "normalize_task_row",
    "normalize_task_rows",
    "resolve_task_type_for_completion_process",
    "create_task_row",
    "tick_tasks",
    "set_task_status",
    "build_task_timeline",
]
