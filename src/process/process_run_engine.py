"""PROC-1 deterministic process-run execution helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Set

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.process.process_definition_validator import (
    REFUSAL_PROCESS_INVALID_DEFINITION,
    build_process_definition_row,
    process_step_rows_by_id,
    validate_process_definition,
)


REFUSAL_PROCESS_RUN_NOT_FOUND = "refusal.process.run_not_found"
REFUSAL_PROCESS_LEDGER_REQUIRED = "refusal.process.ledger_required"
REFUSAL_PROCESS_DIRECT_MASS_ENERGY_MUTATION = "refusal.process.direct_mass_energy_mutation"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def build_process_run_record_row(*, run_id: str, process_id: str, version: str, start_tick: int, end_tick: int | None, status: str, input_refs: object, output_refs: object, deterministic_fingerprint: str = "", extensions: Mapping[str, object] | None = None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "run_id": str(run_id or "").strip(),
        "process_id": str(process_id or "").strip(),
        "version": str(version or "").strip() or "1.0.0",
        "start_tick": int(max(0, _as_int(start_tick, 0))),
        "end_tick": (None if end_tick is None else int(max(0, _as_int(end_tick, 0)))),
        "status": str(status or "").strip().lower() or "running",
        "input_refs": [dict(row) for row in _as_list(input_refs) if isinstance(row, Mapping)],
        "output_refs": [dict(row) for row in _as_list(output_refs) if isinstance(row, Mapping)],
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["run_id"]) or (not payload["process_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_process_step_record_row(*, run_id: str, step_id: str, tick: int, status: str, deterministic_fingerprint: str = "", extensions: Mapping[str, object] | None = None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "run_id": str(run_id or "").strip(),
        "step_id": str(step_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "status": str(status or "").strip().lower() or "started",
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["run_id"]) or (not payload["step_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _deps(process_definition_row: Mapping[str, object]) -> Dict[str, List[str]]:
    graph = _as_map(_as_map(process_definition_row).get("step_graph"))
    steps = process_step_rows_by_id(_as_list(graph.get("steps")))
    out = dict((step_id, []) for step_id in sorted(steps.keys()))
    for edge in sorted((_as_map(row) for row in _as_list(graph.get("edges"))), key=lambda row: (str(row.get("to_step_id", "")), str(row.get("from_step_id", "")))):
        src = str(edge.get("from_step_id", "")).strip()
        dst = str(edge.get("to_step_id", "")).strip()
        if (src in out) and (dst in out):
            out[dst].append(src)
    return dict((key, sorted(set(value))) for key, value in out.items())


def process_run_start(*, current_tick: int, process_definition_row: Mapping[str, object], action_template_registry_payload: Mapping[str, object] | None, temporal_domain_registry_payload: Mapping[str, object] | None, input_refs: object, run_id: str | None = None) -> dict:
    definition = build_process_definition_row(
        process_id=str(_as_map(process_definition_row).get("process_id", "")).strip(),
        version=str(_as_map(process_definition_row).get("version", "")).strip() or "1.0.0",
        description=str(_as_map(process_definition_row).get("description", "")).strip(),
        step_graph=_as_map(process_definition_row).get("step_graph"),
        input_signature=_as_map(process_definition_row).get("input_signature"),
        output_signature=_as_map(process_definition_row).get("output_signature"),
        required_tools=_as_map(process_definition_row).get("required_tools"),
        required_environment=_as_map(process_definition_row).get("required_environment"),
        tier_contract_id=str(_as_map(process_definition_row).get("tier_contract_id", "")).strip(),
        coupling_budget_id=str(_as_map(process_definition_row).get("coupling_budget_id", "")).strip() or None,
        deterministic_fingerprint=str(_as_map(process_definition_row).get("deterministic_fingerprint", "")).strip(),
        extensions=_as_map(_as_map(process_definition_row).get("extensions")),
    )
    validation = validate_process_definition(process_definition_row=definition, action_template_registry_payload=action_template_registry_payload, temporal_domain_registry_payload=temporal_domain_registry_payload)
    if str(validation.get("result", "")).strip() != "complete":
        return {"result": "refused", "reason_code": REFUSAL_PROCESS_INVALID_DEFINITION, "validation": dict(validation)}
    token = str(run_id or "").strip() or "process_run.{}".format(canonical_sha256({"tick": int(max(0, _as_int(current_tick, 0))), "process_id": definition.get("process_id"), "input_refs": _as_list(input_refs)})[:16])
    run_record = build_process_run_record_row(run_id=token, process_id=str(definition.get("process_id", "")).strip(), version=str(definition.get("version", "")).strip(), start_tick=int(max(0, _as_int(current_tick, 0))), end_tick=None, status="running", input_refs=input_refs, output_refs=[], extensions={})
    run_state = {
        "run_id": token,
        "process_id": str(definition.get("process_id", "")).strip(),
        "version": str(definition.get("version", "")).strip(),
        "step_order": _tokens(validation.get("ordered_step_ids")),
        "step_status": dict((step_id, "pending") for step_id in _tokens(validation.get("ordered_step_ids"))),
        "deps": _deps(definition),
        "step_records": [],
        "task_requests": [],
        "output_refs": [],
        "energy_ledger_refs": [],
        "emission_refs": [],
        "entropy_events": [],
        "transform_results": [],
        "observation_artifacts": [],
        "report_artifacts": [],
        "decision_log_rows": [],
        "run_status": "running",
    }
    run_state["deterministic_fingerprint"] = canonical_sha256(dict(run_state, deterministic_fingerprint=""))
    return {"result": "complete", "reason_code": "", "validation": dict(validation), "run_record_row": run_record, "run_state": run_state}


def process_run_tick(*, current_tick: int, run_state: Mapping[str, object], process_definition_row: Mapping[str, object], budget_units: int, completed_action_step_ids: object = None, wait_ready_step_ids: object = None, transform_step_results: Mapping[str, object] | None = None, verify_step_results: Mapping[str, object] | None = None) -> dict:
    state = dict(run_state or {})
    run_id = str(state.get("run_id", "")).strip()
    if not run_id:
        return {"result": "refused", "reason_code": REFUSAL_PROCESS_RUN_NOT_FOUND}
    tick = int(max(0, _as_int(current_tick, 0)))
    budget = int(max(0, _as_int(budget_units, 0)))
    done_actions = set(_tokens(completed_action_step_ids))
    done_wait = set(_tokens(wait_ready_step_ids))
    transform_map = dict((str(k).strip(), _as_map(v)) for k, v in _as_map(transform_step_results).items() if str(k).strip())
    verify_map = dict((str(k).strip(), _as_map(v)) for k, v in _as_map(verify_step_results).items() if str(k).strip())

    definition = build_process_definition_row(
        process_id=str(_as_map(process_definition_row).get("process_id", "")).strip(),
        version=str(_as_map(process_definition_row).get("version", "")).strip() or "1.0.0",
        description=str(_as_map(process_definition_row).get("description", "")).strip(),
        step_graph=_as_map(process_definition_row).get("step_graph"),
        input_signature=_as_map(process_definition_row).get("input_signature"),
        output_signature=_as_map(process_definition_row).get("output_signature"),
        required_tools=_as_map(process_definition_row).get("required_tools"),
        required_environment=_as_map(process_definition_row).get("required_environment"),
        tier_contract_id=str(_as_map(process_definition_row).get("tier_contract_id", "")).strip(),
        coupling_budget_id=str(_as_map(process_definition_row).get("coupling_budget_id", "")).strip() or None,
        deterministic_fingerprint=str(_as_map(process_definition_row).get("deterministic_fingerprint", "")).strip(),
        extensions=_as_map(_as_map(process_definition_row).get("extensions")),
    )
    steps = process_step_rows_by_id(_as_map(definition.get("step_graph")).get("steps"))

    step_status = dict((str(k).strip(), str(v).strip()) for k, v in _as_map(state.get("step_status")).items())
    deps = dict((str(k).strip(), _tokens(v)) for k, v in _as_map(state.get("deps")).items())
    records = [dict(row) for row in _as_list(state.get("step_records")) if isinstance(row, Mapping)]
    consumed = 0

    for step_id in _tokens(state.get("step_order")):
        if step_status.get(step_id) in {"completed", "failed"}:
            continue
        if any(step_status.get(dep) != "completed" for dep in deps.get(step_id, [])):
            continue
        step = dict(steps.get(step_id) or {})
        if not step:
            continue
        cost = int(max(0, _as_int(step.get("cost_units", 0), 0)))
        if consumed + cost > budget:
            state.setdefault("decision_log_rows", []).append({"tick": tick, "step_id": step_id, "reason": "deferred_non_critical_budget"})
            continue
        consumed += cost
        kind = str(step.get("step_kind", "")).strip()
        records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="started", extensions={"step_kind": kind}))
        if kind == "action":
            if step_id in done_actions:
                step_status[step_id] = "completed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "action_signal"}))
            else:
                step_status[step_id] = "waiting_action"
                state.setdefault("task_requests", []).append({"run_id": run_id, "step_id": step_id, "tick": tick, "action_template_id": str(step.get("action_template_id", "")).strip()})
        elif kind == "wait":
            if step_id in done_wait:
                step_status[step_id] = "completed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "temporal_ready"}))
            else:
                step_status[step_id] = "waiting_time"
        elif kind == "verify":
            verify = dict(verify_map.get(step_id) or {})
            passed = bool(verify.get("pass", True))
            state.setdefault("report_artifacts", []).append({"artifact_type_id": "artifact.process.verify_report", "run_id": run_id, "step_id": step_id, "tick": tick, "pass": passed})
            if passed:
                step_status[step_id] = "completed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed"))
            else:
                step_status[step_id] = "failed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="failed"))
        elif kind == "transform":
            result = dict(transform_map.get(step_id) or {})
            if int(_as_int(result.get("direct_mass_delta", 0), 0)) != 0 or int(_as_int(result.get("direct_energy_delta", 0), 0)) != 0:
                return {
                    "result": "refused",
                    "reason_code": REFUSAL_PROCESS_DIRECT_MASS_ENERGY_MUTATION,
                    "step_id": step_id,
                    "run_state": state,
                }
            ext = _as_map(step.get("extensions"))
            if bool(ext.get("moves_mass_energy", False) or ext.get("requires_energy_ledger", False)):
                if (not _tokens(result.get("energy_transform_refs"))) or int(max(0, _as_int(result.get("entropy_increment", 0), 0))) <= 0:
                    return {"result": "refused", "reason_code": REFUSAL_PROCESS_LEDGER_REQUIRED, "step_id": step_id, "run_state": state}
            state["energy_ledger_refs"] = _tokens(list(_as_list(state.get("energy_ledger_refs"))) + list(_tokens(result.get("energy_transform_refs"))))
            state["emission_refs"] = _tokens(list(_as_list(state.get("emission_refs"))) + list(_tokens(result.get("emission_refs"))))
            if int(max(0, _as_int(result.get("entropy_increment", 0), 0))) > 0:
                state.setdefault("entropy_events", [])
                state["entropy_events"] = [dict(row) for row in _as_list(state.get("entropy_events")) if isinstance(row, Mapping)] + [
                    {
                        "run_id": run_id,
                        "step_id": step_id,
                        "tick": tick,
                        "entropy_increment": int(max(0, _as_int(result.get("entropy_increment", 0), 0))),
                    }
                ]
            state.setdefault("transform_results", []).append({
                "run_id": run_id,
                "step_id": step_id,
                "tick": tick,
                "energy_transform_refs": _tokens(result.get("energy_transform_refs")),
                "emission_refs": _tokens(result.get("emission_refs")),
                "entropy_increment": int(max(0, _as_int(result.get("entropy_increment", 0), 0))),
            })
            state["output_refs"] = [dict(row) for row in _as_list(state.get("output_refs")) if isinstance(row, Mapping)] + [dict(row) for row in _as_list(result.get("output_refs")) if isinstance(row, Mapping)] + [dict(row) for row in _as_list(step.get("outputs")) if isinstance(row, Mapping)]
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed"))
        else:
            state.setdefault("observation_artifacts", []).append({"artifact_type_id": "artifact.process.measurement", "run_id": run_id, "step_id": step_id, "tick": tick})
            state["output_refs"] = [dict(row) for row in _as_list(state.get("output_refs")) if isinstance(row, Mapping)] + [dict(row) for row in _as_list(step.get("outputs")) if isinstance(row, Mapping)]
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed"))

    for step_id in _tokens(state.get("step_order")):
        if step_status.get(step_id) == "waiting_action" and step_id in done_actions:
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "action_signal"}))
        if step_status.get(step_id) == "waiting_time" and step_id in done_wait:
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "temporal_ready"}))

    state["step_status"] = step_status
    state["step_records"] = records
    state["cost_units_consumed_total"] = int(max(0, _as_int(state.get("cost_units_consumed_total", 0), 0) + consumed))
    state["run_status"] = "failed" if any(step_status.get(step_id) == "failed" for step_id in _tokens(state.get("step_order"))) else ("completed" if all(step_status.get(step_id) == "completed" for step_id in _tokens(state.get("step_order"))) else "running")
    state["deterministic_fingerprint"] = canonical_sha256(dict(state, deterministic_fingerprint=""))
    return {"result": "complete", "reason_code": "", "run_state": state, "cost_units_consumed": consumed}


def process_run_end(*, current_tick: int, run_record_row: Mapping[str, object], run_state: Mapping[str, object], status: str | None = None) -> dict:
    run_record = dict(_as_map(run_record_row))
    run_id = str(run_record.get("run_id", "")).strip()
    if not run_id:
        return {"result": "refused", "reason_code": REFUSAL_PROCESS_RUN_NOT_FOUND}
    state = dict(_as_map(run_state))
    final_status = str(status or "").strip().lower() or str(state.get("run_status", "completed")).strip().lower() or "completed"
    if final_status == "running":
        final_status = "completed"
    finalized = build_process_run_record_row(
        run_id=run_id,
        process_id=str(run_record.get("process_id", "")).strip(),
        version=str(run_record.get("version", "")).strip() or "1.0.0",
        start_tick=_as_int(run_record.get("start_tick", 0), 0),
        end_tick=int(max(0, _as_int(current_tick, 0))),
        status=final_status,
        input_refs=_as_list(run_record.get("input_refs")),
        output_refs=_as_list(state.get("output_refs")),
        deterministic_fingerprint="",
        extensions=dict(_as_map(run_record.get("extensions")), run_state_fingerprint=str(state.get("deterministic_fingerprint", "")).strip()),
    )
    state["run_status"] = final_status
    state["deterministic_fingerprint"] = canonical_sha256(dict(state, deterministic_fingerprint=""))
    return {"result": "complete", "reason_code": "", "run_record_row": finalized, "run_state": state}


__all__ = [
    "REFUSAL_PROCESS_INVALID_DEFINITION",
    "REFUSAL_PROCESS_RUN_NOT_FOUND",
    "REFUSAL_PROCESS_LEDGER_REQUIRED",
    "REFUSAL_PROCESS_DIRECT_MASS_ENERGY_MUTATION",
    "build_process_run_record_row",
    "build_process_step_record_row",
    "process_run_start",
    "process_run_tick",
    "process_run_end",
]
