"""Deterministic CTRL-4 plan engine."""

from __future__ import annotations

from typing import List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from materials.blueprint_engine import (
    BlueprintCompileError,
    blueprint_bom_summary,
    build_blueprint_ghost_overlay,
    compile_blueprint_artifacts,
)
from control.capability import capability_binding_rows, has_capability

from ..control_plane_engine import build_control_intent, build_control_resolution
from ..ir.control_ir_programs import build_blueprint_execution_ir


REFUSAL_PLAN_INVALID = "refusal.plan.invalid"
REFUSAL_PLAN_NOT_FOUND = "refusal.plan.not_found"
REFUSAL_PLAN_COMPILE_REFUSED = "refusal.plan.compile_refused"
REFUSAL_PLAN_BUDGET_EXCEEDED = "refusal.plan.budget_exceeded"
REFUSAL_PLAN_POLICY_REFUSED = "refusal.plan.policy_refused"

_PLAN_TYPES = {"structure", "track", "road", "vehicle", "custom"}
_PLAN_STATUSES = {"draft", "validated", "approved", "executed", "cancelled"}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _hash(seed: Mapping[str, object]) -> str:
    return canonical_sha256(dict(seed or {}))


def _plan_type_id(token: object) -> str:
    value = str(token or "").strip() or "custom"
    if value in _PLAN_TYPES:
        return value
    return "custom"


def _plan_status(token: object) -> str:
    value = str(token or "").strip() or "draft"
    if value in _PLAN_STATUSES:
        return value
    return "draft"


def _target_context(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    out = {}
    for key in ("site_ref", "region_id", "spatial_node_id"):
        token = str(row.get(key, "")).strip()
        if token:
            out[key] = token
    if out:
        return out
    fallback = str(row.get("target_id", "")).strip()
    if fallback:
        return {"site_ref": fallback}
    return {"site_ref": "site.unknown"}


def _target_context_ref(target_context: Mapping[str, object]) -> str:
    row = _as_map(target_context)
    for key in ("site_ref", "spatial_node_id", "region_id"):
        token = str(row.get(key, "")).strip()
        if token:
            return token
    return "site.unknown"


def _capability_bindings(policy_context: Mapping[str, object] | None) -> List[dict]:
    payload = _as_map(policy_context)
    for key in ("capability_bindings", "capability_binding_registry"):
        value = payload.get(key)
        if isinstance(value, (dict, list)):
            return capability_binding_rows(value)
    return []


def _plan_target_entity_id(plan_intent: Mapping[str, object]) -> str:
    row = _as_map(plan_intent)
    params = _as_map(row.get("parameters"))
    for token in (
        params.get("target_entity_id"),
        params.get("target_id"),
        _as_map(row.get("target_context")).get("spatial_node_id"),
        _as_map(row.get("target_context")).get("site_ref"),
    ):
        value = str(token or "").strip()
        if value:
            return value
    return ""


def _refusal(
    reason_code: str,
    message: str,
    remediation_hint: str,
    relevant_ids: Mapping[str, object] | None = None,
    path: str = "$",
) -> dict:
    ids = {}
    for key, value in sorted((_as_map(relevant_ids)).items(), key=lambda item: str(item[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": ids,
            "path": str(path),
        },
        "errors": [{"code": str(reason_code), "message": str(message), "path": str(path)}],
    }


def _plan_id_seed(plan_intent: Mapping[str, object]) -> dict:
    row = dict(plan_intent or {})
    return {
        "plan_intent_id": str(row.get("plan_intent_id", "")).strip(),
        "requester_subject_id": str(row.get("requester_subject_id", "")).strip(),
        "target_context": _target_context(row.get("target_context")),
        "plan_type_id": _plan_type_id(row.get("plan_type_id")),
        "parameters": _canon(_as_map(row.get("parameters"))),
    }


def _plan_id(plan_intent: Mapping[str, object]) -> str:
    return "plan.{}".format(_hash(_plan_id_seed(plan_intent))[:24])


def _plan_compile_budget_units(policy_context: Mapping[str, object] | None, control_policy: Mapping[str, object] | None) -> int:
    context = _as_map(policy_context)
    policy_ext = _as_map(_as_map(control_policy).get("extensions"))
    for token in (
        context.get("plan_compile_budget_units"),
        context.get("max_control_cost_units"),
        context.get("rs5_budget_units"),
        policy_ext.get("plan_compile_budget_units"),
        policy_ext.get("max_control_cost_units"),
        policy_ext.get("rs5_budget_units"),
    ):
        value = int(max(0, _as_int(token, 0)))
        if value > 0:
            return value
    return 0


def _resource_summary_from_compiled(compiled: Mapping[str, object]) -> dict:
    bom_artifact = _as_map(_as_map(compiled).get("compiled_bom_artifact"))
    bom = _as_map(bom_artifact.get("bom"))
    material_mass = {}
    total_mass = 0
    for row in [dict(item) for item in list(bom.get("required_materials") or []) if isinstance(item, Mapping)]:
        material_id = str(row.get("material_id_or_class", "")).strip()
        if not material_id:
            continue
        mass = int(max(0, _as_int(row.get("quantity_mass_raw", 0), 0)))
        material_mass[material_id] = int(material_mass.get(material_id, 0) + mass)
        total_mass += mass
    part_counts = {}
    total_parts = 0
    for row in [dict(item) for item in list(bom.get("required_part_classes") or []) if isinstance(item, Mapping)]:
        part_class_id = str(row.get("part_class_id", "")).strip()
        if not part_class_id:
            continue
        count = int(max(0, _as_int(row.get("count", 0), 0)))
        part_counts[part_class_id] = int(part_counts.get(part_class_id, 0) + count)
        total_parts += count
    return {
        "total_mass_raw": int(total_mass),
        "total_part_count": int(total_parts),
        "material_mass_raw": dict((key, material_mass[key]) for key in sorted(material_mass.keys())),
        "part_counts": dict((key, part_counts[key]) for key in sorted(part_counts.keys())),
        "bom_summary_hash": str(_as_map(blueprint_bom_summary(bom_artifact)).get("summary_hash", "")).strip(),
    }


def _fallback_preview(parameters: Mapping[str, object], plan_id: str) -> dict:
    params = _as_map(parameters)
    preview = _as_map(params.get("spatial_preview_data"))
    if preview:
        return {
            "renderables": [dict(item) for item in list(preview.get("renderables") or []) if isinstance(item, Mapping)],
            "materials": [dict(item) for item in list(preview.get("materials") or []) if isinstance(item, Mapping)],
            "metadata": _as_map(preview.get("metadata")),
        }
    return {"renderables": [], "materials": [], "metadata": {"plan_id": str(plan_id)}}


def build_plan_intent(
    *,
    requester_subject_id: str,
    target_context: Mapping[str, object] | None,
    plan_type_id: str,
    parameters: Mapping[str, object] | None = None,
    created_tick: int = 0,
    plan_intent_id: str = "",
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "plan_intent_id": str(plan_intent_id).strip(),
        "requester_subject_id": str(requester_subject_id).strip() or "subject.unknown",
        "target_context": _target_context(target_context),
        "plan_type_id": _plan_type_id(plan_type_id),
        "parameters": _canon(_as_map(parameters)),
        "created_tick": int(max(0, _as_int(created_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    if not payload["plan_intent_id"]:
        payload["plan_intent_id"] = "plan.intent.{}".format(_hash(_plan_id_seed(payload))[:24])
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = _hash(seed)
    return payload


def build_execute_plan_intent(
    *,
    plan_id: str,
    abstraction_level_requested: str = "AL3",
    created_tick: int = 0,
    execute_plan_intent_id: str = "",
) -> dict:
    requested = str(abstraction_level_requested).strip()
    if requested not in {"AL0", "AL1", "AL2", "AL3", "AL4"}:
        requested = "AL3"
    payload = {
        "schema_version": "1.0.0",
        "execute_plan_intent_id": str(execute_plan_intent_id).strip(),
        "plan_id": str(plan_id).strip(),
        "abstraction_level_requested": requested,
        "created_tick": int(max(0, _as_int(created_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    if not payload["execute_plan_intent_id"]:
        payload["execute_plan_intent_id"] = "execute.plan.intent.{}".format(_hash(payload)[:24])
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = _hash(seed)
    return payload


def create_plan_artifact(
    *,
    plan_intent: Mapping[str, object],
    law_profile: Mapping[str, object],
    authority_context: Mapping[str, object],
    control_policy: Mapping[str, object],
    control_action_registry: Mapping[str, object],
    control_policy_registry: Mapping[str, object],
    policy_context: Mapping[str, object] | None = None,
    repo_root: str = "",
    pack_lock_hash: str = "",
    blueprint_registry: Mapping[str, object] | None = None,
    part_class_registry: Mapping[str, object] | None = None,
    connection_type_registry: Mapping[str, object] | None = None,
    material_class_registry: Mapping[str, object] | None = None,
) -> dict:
    intent = build_plan_intent(
        requester_subject_id=str(_as_map(plan_intent).get("requester_subject_id", "")),
        target_context=_as_map(plan_intent).get("target_context"),
        plan_type_id=str(_as_map(plan_intent).get("plan_type_id", "")),
        parameters=_as_map(_as_map(plan_intent).get("parameters")),
        created_tick=int(max(0, _as_int(_as_map(plan_intent).get("created_tick", 0), 0))),
        plan_intent_id=str(_as_map(plan_intent).get("plan_intent_id", "")).strip(),
    )
    plan_id = _plan_id(intent)
    plan_type_id = _plan_type_id(intent.get("plan_type_id"))
    params = _as_map(intent.get("parameters"))
    blueprint_id = str(params.get("blueprint_id", "")).strip()
    site_ref = str(_target_context_ref(intent.get("target_context"))).strip()
    plan_target_entity_id = _plan_target_entity_id(intent)
    capability_rows = _capability_bindings(policy_context)
    target_can_be_planned = bool(plan_type_id == "structure")
    if plan_target_entity_id and capability_rows:
        target_can_be_planned = has_capability(
            entity_id=plan_target_entity_id,
            capability_id="capability.can_be_planned",
            capability_bindings=capability_rows,
        )
    compile_cost_units = 1
    ag_node_ids = []
    compiled_blueprint_ref = None
    estimated_bom_ref = None
    required_resources_summary = _as_map(params.get("required_resources_summary"))
    spatial_preview_data = _fallback_preview(params, plan_id)
    if blueprint_id and target_can_be_planned:
        try:
            compiled = compile_blueprint_artifacts(
                repo_root=str(repo_root or ""),
                blueprint_id=blueprint_id,
                parameter_values=_as_map(params.get("blueprint_parameters")),
                pack_lock_hash=str(pack_lock_hash).strip() or ("0" * 64),
                blueprint_registry=_as_map(blueprint_registry),
                part_class_registry=_as_map(part_class_registry),
                connection_type_registry=_as_map(connection_type_registry),
                material_class_registry=_as_map(material_class_registry),
            )
        except BlueprintCompileError as exc:
            return _refusal(
                REFUSAL_PLAN_COMPILE_REFUSED,
                "plan blueprint compilation refused",
                "Fix blueprint references/parameters before creating the plan artifact.",
                {"plan_intent_id": str(intent.get("plan_intent_id", "")), "reason_code": str(exc.reason_code)},
                "$.parameters.blueprint_id",
            )
        bom_artifact = _as_map(compiled.get("compiled_bom_artifact"))
        ag_artifact = _as_map(compiled.get("compiled_ag_artifact"))
        ag_nodes = _as_map(_as_map(ag_artifact.get("ag")).get("nodes"))
        ag_node_ids = _sorted_unique_strings(list(ag_nodes.keys()))
        ghost = _as_map(build_blueprint_ghost_overlay(compiled_ag_artifact=ag_artifact, blueprint_id=blueprint_id, include_labels=True))
        spatial_preview_data = {
            "renderables": [dict(item) for item in list(ghost.get("renderables") or []) if isinstance(item, Mapping)],
            "materials": [dict(item) for item in list(ghost.get("materials") or []) if isinstance(item, Mapping)],
            "metadata": {"source": "blueprint_compile", "blueprint_id": blueprint_id},
        }
        required_resources_summary = _resource_summary_from_compiled(compiled)
        compiled_blueprint_ref = blueprint_id
        estimated_bom_ref = str(_as_map(bom_artifact.get("bom")).get("bom_id", "")).strip() or str(bom_artifact.get("artifact_hash", "")).strip() or None
        compile_cost_units = int(max(1, len(ag_node_ids)))
    budget_limit = _plan_compile_budget_units(policy_context, control_policy)
    if int(budget_limit) > 0 and int(compile_cost_units) > int(budget_limit):
        return _refusal(
            REFUSAL_PLAN_BUDGET_EXCEEDED,
            "plan compilation cost exceeds RS-5 budget envelope",
            "Reduce plan complexity or increase plan compile budget units.",
            {"plan_intent_id": str(intent.get("plan_intent_id", "")), "compile_cost_units": str(compile_cost_units), "budget_units": str(budget_limit)},
            "$.parameters",
        )
    control_intent = build_control_intent(
        requester_subject_id=str(intent.get("requester_subject_id", "")),
        requested_action_id="action.plan.blueprint",
        target_kind="structure" if target_can_be_planned else "surface",
        target_id=site_ref,
        parameters={"plan_intent_id": str(intent.get("plan_intent_id", "")), "plan_id": str(plan_id), "plan_type_id": str(plan_type_id), "plan_compile_cost_units": int(compile_cost_units), "site_ref": site_ref},
        abstraction_level_requested="AL3",
        fidelity_requested="meso",
        view_requested=str(_as_map(policy_context).get("view_requested", "view.mode.first_person")) or "view.mode.first_person",
        created_tick=int(max(0, _as_int(intent.get("created_tick", 0), 0))),
    )
    control_resolution_result = build_control_resolution(
        control_intent=control_intent,
        law_profile=_as_map(law_profile),
        authority_context=_as_map(authority_context),
        policy_context=_as_map(policy_context),
        control_action_registry=_as_map(control_action_registry),
        control_policy_registry=_as_map(control_policy_registry),
        repo_root=str(repo_root or ""),
    )
    if str(control_resolution_result.get("result", "")) != "complete":
        refusal_row = _as_map(control_resolution_result.get("refusal"))
        if refusal_row:
            return {"result": "refused", "refusal": dict(refusal_row), "errors": [{"code": str(refusal_row.get("reason_code", REFUSAL_PLAN_POLICY_REFUSED)), "message": str(refusal_row.get("message", "plan policy validation refused")), "path": str(refusal_row.get("path", "$"))}]}
        return _refusal(REFUSAL_PLAN_POLICY_REFUSED, "plan policy validation refused", "Adjust authority/control policy constraints and retry plan creation.", {"plan_intent_id": str(intent.get("plan_intent_id", ""))}, "$.control_policy")
    resolution = _as_map(control_resolution_result.get("resolution"))
    artifact = {
        "schema_version": "1.0.0",
        "plan_id": str(plan_id),
        "plan_type_id": str(plan_type_id),
        "compiled_ir_id": None,
        "compiled_blueprint_ref": compiled_blueprint_ref,
        "estimated_bom_ref": estimated_bom_ref,
        "spatial_preview_data": _as_map(spatial_preview_data),
        "required_resources_summary": _as_map(required_resources_summary),
        "status": "validated",
        "deterministic_fingerprint": "",
        "extensions": {
            "plan_intent_id": str(intent.get("plan_intent_id", "")),
            "target_context": _target_context(intent.get("target_context")),
            "parameters": _canon(params),
            "compile_cost_units": int(compile_cost_units),
            "budget_limit_units": int(budget_limit),
            "control_decision_log_ref": str(resolution.get("decision_log_ref", "")).strip(),
            "control_resolution_id": str(resolution.get("resolution_id", "")).strip(),
            "blueprint_id": blueprint_id or None,
            "site_ref": site_ref,
            "ag_node_ids": list(ag_node_ids),
            "target_entity_id": plan_target_entity_id or None,
            "target_can_be_planned": bool(target_can_be_planned),
        },
    }
    seed = dict(artifact)
    seed["deterministic_fingerprint"] = ""
    artifact["deterministic_fingerprint"] = _hash(seed)
    return {"result": "complete", "plan_intent": intent, "control_intent": control_intent, "control_resolution": resolution, "plan_artifact": artifact}


def _generic_plan_execution_ir(plan_id: str, plan_type_id: str, actor_subject_id: str, step_rows: Sequence[Mapping[str, object]], tick: int) -> dict:
    op_rows = []
    op_ids = []
    for index, step in enumerate(list(step_rows or [])):
        row = _as_map(step)
        op_id = "op.{}".format(str(index + 1).zfill(4))
        op_ids.append(op_id)
        op_rows.append(
            {
                "schema_version": "1.0.0",
                "op_id": op_id,
                "op_type": "op.emit_commitment",
                "parameters": {"plan_id": str(plan_id), "plan_type_id": str(plan_type_id), "step_id": str(row.get("step_id", "")).strip() or "step.{}".format(str(index + 1).zfill(4)), "commitment_kind": str(row.get("commitment_kind", "construction.step")).strip() or "construction.step", "actor_subject_id": str(actor_subject_id), "required_manifest_ids": _sorted_unique_strings(row.get("required_manifest_ids"))},
                "static_requirements": {"entitlements": ["entitlement.control.admin"], "capabilities": []},
                "cost_estimate": int(max(1, _as_int(row.get("cost_estimate", 1), 1))),
                "extensions": {},
            }
        )
    if not op_ids:
        op_ids = ["op.0001"]
        op_rows = [{"schema_version": "1.0.0", "op_id": "op.0001", "op_type": "op.noop", "parameters": {"plan_id": str(plan_id)}, "static_requirements": {"entitlements": [], "capabilities": []}, "cost_estimate": 1, "extensions": {}}]
    ir_program = {"schema_version": "1.0.0", "control_ir_id": "control.ir.plan.{}".format(_hash({"plan_id": str(plan_id), "tick": int(tick), "step_count": len(op_ids)})[:16]), "root_block": "block.main", "blocks": [{"schema_version": "1.0.0", "block_id": "block.main", "op_sequence": list(op_ids), "next_block_on_success": None, "next_block_on_failure": None, "extensions": {}}], "metadata": {"creator": "planner.plan.execute", "tick": int(max(0, int(tick)))}, "deterministic_fingerprint": "", "extensions": {"op_rows": list(op_rows), "source": "plan_artifact"}}
    seed = dict(ir_program)
    seed["deterministic_fingerprint"] = ""
    ir_program["deterministic_fingerprint"] = _hash(seed)
    return ir_program


def build_plan_execution_ir(*, plan_artifact: Mapping[str, object], actor_subject_id: str, tick: int = 0) -> dict:
    artifact = _as_map(plan_artifact)
    plan_id = str(artifact.get("plan_id", "")).strip()
    if not plan_id:
        return _refusal(REFUSAL_PLAN_INVALID, "plan_id is required to build execution IR", "Provide a valid plan artifact with plan_id.", {}, "$.plan_artifact.plan_id")
    plan_type_id = _plan_type_id(artifact.get("plan_type_id"))
    ext = _as_map(artifact.get("extensions"))
    blueprint_id = str(ext.get("blueprint_id", "")).strip() or str(artifact.get("compiled_blueprint_ref", "")).strip()
    site_ref = str(ext.get("site_ref", "")).strip() or _target_context_ref(ext.get("target_context"))
    ag_node_ids = _sorted_unique_strings(ext.get("ag_node_ids"))
    target_can_be_planned = bool(ext.get("target_can_be_planned", plan_type_id == "structure"))
    if blueprint_id and target_can_be_planned:
        return {"result": "complete", "ir_program": build_blueprint_execution_ir(project_id=str(plan_id), blueprint_id=str(blueprint_id), site_ref=site_ref or "site.unknown", ag_node_ids=list(ag_node_ids), actor_subject_id=str(actor_subject_id).strip() or "subject.system", tick=int(max(0, int(tick))))}
    step_rows = [dict(item) for item in list(ext.get("manual_steps") or []) if isinstance(item, Mapping)]
    return {"result": "complete", "ir_program": _generic_plan_execution_ir(str(plan_id), str(plan_type_id), str(actor_subject_id).strip() or "subject.system", step_rows, int(max(0, int(tick))))}


def update_plan_artifact_incremental(*, plan_artifact: Mapping[str, object], update_payload: Mapping[str, object], current_tick: int = 0) -> dict:
    artifact = dict(plan_artifact or {})
    plan_id = str(artifact.get("plan_id", "")).strip()
    if not plan_id:
        return _refusal(REFUSAL_PLAN_INVALID, "plan_id is required for incremental update", "Provide an existing plan artifact with plan_id.", {}, "$.plan_artifact.plan_id")
    status = _plan_status(artifact.get("status"))
    if status in {"cancelled", "executed"}:
        return _refusal(REFUSAL_PLAN_INVALID, "terminal plan artifact cannot be updated incrementally", "Create a new plan artifact for further planning changes.", {"plan_id": plan_id, "status": status}, "$.plan_artifact.status")
    update = _as_map(update_payload)
    preview = _as_map(artifact.get("spatial_preview_data"))
    renderables = dict((str(row.get("renderable_id", "")).strip(), dict(row)) for row in list(preview.get("renderables") or []) if isinstance(row, Mapping) and str(row.get("renderable_id", "")).strip())
    materials = dict((str(row.get("material_id", "")).strip(), dict(row)) for row in list(preview.get("materials") or []) if isinstance(row, Mapping) and str(row.get("material_id", "")).strip())
    for renderable_id in _sorted_unique_strings(update.get("remove_renderable_ids")):
        renderable = dict(renderables.get(renderable_id) or {})
        material_id = str(renderable.get("material_id", "")).strip()
        renderables.pop(renderable_id, None)
        if material_id:
            materials.pop(material_id, None)
    for row in [dict(item) for item in list(update.get("add_renderables") or []) if isinstance(item, Mapping)]:
        renderable_id = str(row.get("renderable_id", "")).strip()
        if renderable_id:
            renderables[renderable_id] = dict(row)
    for row in [dict(item) for item in list(update.get("add_materials") or []) if isinstance(item, Mapping)]:
        material_id = str(row.get("material_id", "")).strip()
        if material_id:
            materials[material_id] = dict(row)
    resources = _as_map(artifact.get("required_resources_summary"))
    material_mass = _as_map(resources.get("material_mass_raw"))
    for key, value in sorted(_as_map(update.get("material_mass_delta")).items(), key=lambda item: str(item[0])):
        token = str(key).strip()
        if not token:
            continue
        next_mass = int(max(0, _as_int(material_mass.get(token, 0), 0) + _as_int(value, 0)))
        if next_mass <= 0:
            material_mass.pop(token, None)
        else:
            material_mass[token] = next_mass
    resources["material_mass_raw"] = dict((key, int(material_mass[key])) for key in sorted(material_mass.keys()))
    resources["total_mass_raw"] = int(sum(int(_as_int(item, 0)) for item in resources["material_mass_raw"].values()))
    resources["total_part_count"] = int(max(0, _as_int(resources.get("total_part_count", 0), 0) + _as_int(update.get("part_count_delta", 0), 0)))
    update_id = "plan.update.{}".format(_hash({"plan_id": plan_id, "tick": int(max(0, int(current_tick))), "update": _canon(update)})[:24])
    ext = _as_map(artifact.get("extensions"))
    history = [dict(item) for item in list(ext.get("update_history") or []) if isinstance(item, Mapping)]
    history.append({"update_id": update_id, "tick": int(max(0, int(current_tick))), "change_kind": str(update.get("change_kind", "manual")).strip() or "manual"})
    ext["update_history"] = sorted((dict(item) for item in history if str(item.get("update_id", "")).strip()), key=lambda item: (int(max(0, _as_int(item.get("tick", 0), 0))), str(item.get("update_id", ""))))
    artifact["spatial_preview_data"] = {"renderables": [dict(renderables[key]) for key in sorted(renderables.keys())], "materials": [dict(materials[key]) for key in sorted(materials.keys())], "metadata": _as_map(preview.get("metadata"))}
    artifact["required_resources_summary"] = dict(resources)
    artifact["status"] = "draft"
    artifact["extensions"] = dict(ext)
    seed = dict(artifact)
    seed["deterministic_fingerprint"] = ""
    artifact["deterministic_fingerprint"] = _hash(seed)
    return {"result": "complete", "plan_artifact": artifact, "update_id": update_id}


__all__ = [
    "REFUSAL_PLAN_BUDGET_EXCEEDED",
    "REFUSAL_PLAN_COMPILE_REFUSED",
    "REFUSAL_PLAN_INVALID",
    "REFUSAL_PLAN_NOT_FOUND",
    "REFUSAL_PLAN_POLICY_REFUSED",
    "build_execute_plan_intent",
    "build_plan_execution_ir",
    "build_plan_intent",
    "create_plan_artifact",
    "update_plan_artifact_incremental",
]
