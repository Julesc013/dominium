"""Deterministic MAT-5 construction project and installation helpers."""

from __future__ import annotations

import copy
from typing import Dict, List, Mapping, Tuple

from src.logistics.logistics_engine import (
    build_inventory_index,
    normalize_node_inventory,
)
from src.materials.blueprint_engine import (
    BlueprintCompileError,
    compile_blueprint_artifacts,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_CONSTRUCTION_BLUEPRINT_MISSING = "refusal.construction.blueprint_missing"
REFUSAL_CONSTRUCTION_SITE_INVALID = "refusal.construction.site_invalid"
REFUSAL_CONSTRUCTION_INSUFFICIENT_MATERIAL = "refusal.construction.insufficient_material"
REFUSAL_CONSTRUCTION_POLICY_INVALID = "refusal.construction.policy_invalid"

_PROJECT_ACTIVE_STATUSES = {"planned", "executing"}
_PROJECT_TERMINAL_STATUSES = {"completed", "failed"}
_STEP_ACTIVE_STATUSES = {"planned", "executing"}


class ConstructionError(ValueError):
    """Deterministic construction refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _rows_by_id(rows: object, key_field: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(key_field, ""))):
        token = str(row.get(key_field, "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _material_requirement_rows(rows: object) -> List[dict]:
    out: List[dict] = []
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("material_id_or_class", ""))):
        material_id_or_class = str(row.get("material_id_or_class", "")).strip()
        quantity_mass_raw = int(max(0, _as_int(row.get("quantity_mass_raw", 0), 0)))
        if not material_id_or_class:
            continue
        out.append(
            {
                "material_id_or_class": material_id_or_class,
                "quantity_mass_raw": int(quantity_mass_raw),
            }
        )
    return out


def _part_class_requirement_rows(rows: object) -> List[dict]:
    out: List[dict] = []
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("part_class_id", ""))):
        part_class_id = str(row.get("part_class_id", "")).strip()
        count = int(max(0, _as_int(row.get("count", 0), 0)))
        if not part_class_id:
            continue
        out.append({"part_class_id": part_class_id, "count": int(count)})
    return out


def _event_fingerprint(event_row: Mapping[str, object]) -> str:
    seed = dict(event_row or {})
    seed["deterministic_fingerprint"] = ""
    return canonical_sha256(seed)


def _event_row(
    *,
    event_type_id: str,
    tick: int,
    actor_subject_id: str,
    site_ref: str,
    linked_project_id: str,
    linked_step_id: str | None,
    inputs: List[str] | None,
    outputs: List[str] | None,
    ledger_deltas: Mapping[str, object] | None,
    sequence: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    normalized_inputs = _sorted_unique_strings(list(inputs or []))
    normalized_outputs = _sorted_unique_strings(list(outputs or []))
    normalized_ledger_deltas = dict(
        (str(key).strip(), int(_as_int(value, 0)))
        for key, value in sorted((dict(ledger_deltas or {})).items(), key=lambda item: str(item[0]))
        if str(key).strip()
    )
    identity = {
        "event_type_id": str(event_type_id),
        "tick": int(max(0, int(tick))),
        "linked_project_id": str(linked_project_id),
        "linked_step_id": str(linked_step_id or ""),
        "inputs": list(normalized_inputs),
        "outputs": list(normalized_outputs),
        "ledger_deltas": dict(normalized_ledger_deltas),
        "sequence": int(max(0, int(sequence))),
    }
    event_id = "provenance.event.{}".format(canonical_sha256(identity)[:24])
    row = {
        "schema_version": "1.0.0",
        "event_id": event_id,
        "tick": int(max(0, int(tick))),
        "event_type_id": str(event_type_id),
        "actor_subject_id": str(actor_subject_id).strip() or "subject.system",
        "site_ref": str(site_ref),
        "inputs": list(normalized_inputs),
        "outputs": list(normalized_outputs),
        "ledger_deltas": dict(normalized_ledger_deltas),
        "linked_project_id": str(linked_project_id),
        "linked_step_id": str(linked_step_id) if linked_step_id is not None else None,
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    row["deterministic_fingerprint"] = _event_fingerprint(row)
    return row


def _construction_commitment_row(
    *,
    commitment_id: str,
    project_id: str,
    step_id: str,
    commitment_kind: str,
    scheduled_tick: int,
    actor_subject_id: str,
    manifest_ids: List[str] | None = None,
    status: str = "planned",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "commitment_id": str(commitment_id),
        "project_id": str(project_id),
        "step_id": str(step_id),
        "commitment_kind": str(commitment_kind),
        "scheduled_tick": int(max(0, int(scheduled_tick))),
        "status": str(status),
        "actor_subject_id": str(actor_subject_id).strip() or "subject.system",
        "manifest_ids": _sorted_unique_strings(list(manifest_ids or [])),
        "extensions": dict(extensions or {}),
    }


def _construction_commitment_rows_by_id(rows: object) -> Dict[str, dict]:
    return _rows_by_id(rows, "commitment_id")


def _construction_step_rows_by_project(rows: object) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: (str(item.get("project_id", "")), str(item.get("ag_node_id", "")), str(item.get("step_id", "")))):
        project_id = str(row.get("project_id", "")).strip()
        if not project_id:
            continue
        out.setdefault(project_id, []).append(dict(row))
    for project_id in sorted(out.keys()):
        out[project_id] = sorted(
            [dict(item) for item in list(out.get(project_id) or [])],
            key=lambda item: (str(item.get("ag_node_id", "")), str(item.get("step_id", ""))),
        )
    return out


def _project_rows_by_id(rows: object) -> Dict[str, dict]:
    return _rows_by_id(rows, "project_id")


def _installed_structure_rows_by_project(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("project_id", ""))):
        project_id = str(row.get("project_id", "")).strip()
        if project_id:
            out[project_id] = dict(row)
    return out


def _inventory_hash(node_id: str, material_stocks: Mapping[str, object], batch_refs: List[object]) -> str:
    payload = {
        "node_id": str(node_id),
        "material_stocks": dict(
            (str(key).strip(), int(_as_int(value, 0)))
            for key, value in sorted((material_stocks or {}).items(), key=lambda item: str(item[0]))
            if str(key).strip()
        ),
        "batch_refs": _sorted_unique_strings(list(batch_refs or [])),
    }
    return canonical_sha256(payload)


def _inventory_ensure(index: Dict[str, dict], node_id: str) -> dict:
    token = str(node_id).strip()
    row = dict(index.get(token) or {})
    if not row:
        row = {
            "schema_version": "1.0.0",
            "node_id": token,
            "material_stocks": {},
            "batch_refs": [],
            "inventory_hash": "",
            "extensions": {},
        }
    normalized = normalize_node_inventory(row)
    index[token] = normalized
    return normalized


def _inventory_apply(
    index: Dict[str, dict],
    *,
    node_id: str,
    material_id: str,
    delta_mass: int,
) -> dict:
    material_token = str(material_id).strip()
    if not material_token:
        raise ConstructionError(
            REFUSAL_CONSTRUCTION_INSUFFICIENT_MATERIAL,
            "material_id is required for inventory mutation",
            {"node_id": str(node_id)},
        )
    row = _inventory_ensure(index, node_id)
    stocks = dict(row.get("material_stocks") or {})
    current = int(_as_int(stocks.get(material_token, 0), 0))
    updated = int(current + int(delta_mass))
    if updated < 0:
        raise ConstructionError(
            REFUSAL_CONSTRUCTION_INSUFFICIENT_MATERIAL,
            "inventory mutation would produce negative stock",
            {
                "node_id": str(node_id),
                "material_id": material_token,
                "current_mass": int(current),
                "delta_mass": int(delta_mass),
            },
        )
    if updated <= 0:
        stocks.pop(material_token, None)
    else:
        stocks[material_token] = int(updated)
    batch_refs = _sorted_unique_strings(list(row.get("batch_refs") or []))
    row["material_stocks"] = dict((key, int(stocks[key])) for key in sorted(stocks.keys()))
    row["batch_refs"] = list(batch_refs)
    row["inventory_hash"] = _inventory_hash(str(node_id), row["material_stocks"], row["batch_refs"])
    index[str(node_id).strip()] = row
    return row


def _construction_policy_row(policy_row: Mapping[str, object]) -> dict:
    row = dict(policy_row or {})
    policy_id = str(row.get("policy_id", "")).strip()
    if not policy_id:
        raise ConstructionError(
            REFUSAL_CONSTRUCTION_POLICY_INVALID,
            "construction policy missing policy_id",
            {},
        )
    default_step_duration_ticks = row.get("default_step_duration_ticks")
    if isinstance(default_step_duration_ticks, dict):
        normalized_duration = dict(
            (str(key).strip(), int(max(0, _as_int(value, 0))))
            for key, value in sorted(default_step_duration_ticks.items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
    else:
        normalized_duration = int(max(0, _as_int(default_step_duration_ticks, 1)))
    return {
        "schema_version": "1.0.0",
        "policy_id": policy_id,
        "default_step_duration_ticks": normalized_duration,
        "allow_parallel_steps": bool(row.get("allow_parallel_steps", False)),
        "max_parallel_steps": int(max(1, _as_int(row.get("max_parallel_steps", 1), 1))),
        "deterministic_scheduling_rule_id": str(row.get("deterministic_scheduling_rule_id", "")).strip() or "schedule.ag_node_lexicographic",
        "extensions": dict(row.get("extensions") or {}),
    }


def construction_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    direct = root.get("policies")
    if not isinstance(direct, list):
        direct = ((root.get("record") or {}).get("policies") or [])
    rows: Dict[str, dict] = {}
    for row in sorted((item for item in list(direct or []) if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        normalized = _construction_policy_row(row)
        rows[str(normalized.get("policy_id", ""))] = normalized
    return rows


def _resolve_policy(
    *,
    construction_policy_registry: Mapping[str, object] | None,
    construction_policy_id: str,
) -> dict:
    policy_map = construction_policy_rows_by_id(construction_policy_registry)
    token = str(construction_policy_id).strip()
    if token and token in policy_map:
        return dict(policy_map[token])
    if "build.policy.default" in policy_map:
        return dict(policy_map["build.policy.default"])
    if policy_map:
        first_key = sorted(policy_map.keys())[0]
        return dict(policy_map[first_key])
    raise ConstructionError(
        REFUSAL_CONSTRUCTION_POLICY_INVALID,
        "construction policy registry is empty",
        {},
    )


def _resolve_step_duration(policy_row: Mapping[str, object], node_kind: str) -> int:
    default_step_duration_ticks = (dict(policy_row or {})).get("default_step_duration_ticks")
    if isinstance(default_step_duration_ticks, dict):
        key = str(node_kind).strip()
        duration = _as_int(
            default_step_duration_ticks.get(key, default_step_duration_ticks.get("default", 1)),
            1,
        )
    else:
        duration = _as_int(default_step_duration_ticks, 1)
    return int(max(1, int(duration)))


def _node_material_requirements(
    *,
    node_row: Mapping[str, object],
    bom_material_rows: List[dict],
    is_primary_node: bool,
) -> List[dict]:
    node_requirements = _material_requirement_rows(list((dict(node_row or {})).get("material_requirements") or []))
    if node_requirements:
        return node_requirements
    if bool(is_primary_node):
        return _material_requirement_rows(list(bom_material_rows or []))
    return []


def _resolve_schedule_windows(
    *,
    created_tick: int,
    step_seed_rows: Dict[str, dict],
) -> Dict[str, Tuple[int, int]]:
    visiting = set()
    resolved: Dict[str, Tuple[int, int]] = {}

    def _resolve(node_id: str) -> Tuple[int, int]:
        token = str(node_id).strip()
        cached = resolved.get(token)
        if cached:
            return cached
        if token in visiting:
            raise ConstructionError(
                REFUSAL_CONSTRUCTION_BLUEPRINT_MISSING,
                "construction scheduling graph contains cycle",
                {"ag_node_id": token},
            )
        seed = dict(step_seed_rows.get(token) or {})
        if not seed:
            raise ConstructionError(
                REFUSAL_CONSTRUCTION_BLUEPRINT_MISSING,
                "construction scheduling graph references unknown node",
                {"ag_node_id": token},
            )
        visiting.add(token)
        dependency_end = int(max(0, int(created_tick)))
        for dep_id in sorted(set(str(item).strip() for item in list(seed.get("dependency_node_ids") or []) if str(item).strip())):
            dep_start, dep_end = _resolve(dep_id)
            del dep_start
            dependency_end = max(int(dependency_end), int(dep_end))
        start_tick = int(max(int(created_tick), int(dependency_end)))
        duration_ticks = int(max(1, _as_int(seed.get("duration_ticks", 1), 1)))
        end_tick = int(start_tick + duration_ticks)
        resolved[token] = (start_tick, end_tick)
        visiting.remove(token)
        return resolved[token]

    for ag_node_id in sorted(step_seed_rows.keys()):
        _resolve(ag_node_id)
    return dict((node_id, tuple(resolved[node_id])) for node_id in sorted(resolved.keys()))


def _project_identity(
    *,
    blueprint_id: str,
    site_ref: str,
    created_tick: int,
    params_hash: str,
) -> str:
    digest = canonical_sha256(
        {
            "blueprint_id": str(blueprint_id),
            "site_ref": str(site_ref),
            "created_tick": int(max(0, int(created_tick))),
            "params_hash": str(params_hash),
        }
    )
    return "project.construction.{}".format(digest[:20])


def _structure_instance_id(*, project_id: str, ag_id: str, site_ref: str) -> str:
    return "assembly.structure_instance.{}".format(
        canonical_sha256(
            {
                "project_id": str(project_id),
                "ag_id": str(ag_id),
                "site_ref": str(site_ref),
            }
        )[:20]
    )


def _step_output_batch_id(
    *,
    project_id: str,
    step_id: str,
    ag_node_id: str,
    scheduled_end_tick: int,
) -> str:
    return "batch.part.{}".format(
        canonical_sha256(
            {
                "project_id": str(project_id),
                "step_id": str(step_id),
                "ag_node_id": str(ag_node_id),
                "scheduled_end_tick": int(max(0, int(scheduled_end_tick))),
            }
        )[:24]
    )


def _construction_actor_subject_id(actor_subject_id: str) -> str:
    token = str(actor_subject_id).strip()
    if token:
        return token
    return "subject.system"


def _set_commitment_status(commitment_rows: Dict[str, dict], commitment_id: str, status: str, tick: int) -> None:
    token = str(commitment_id).strip()
    if not token:
        return
    row = dict(commitment_rows.get(token) or {})
    if not row:
        return
    row["status"] = str(status).strip() or "planned"
    extensions = dict(row.get("extensions") or {})
    extensions["last_status_tick"] = int(max(0, int(tick)))
    row["extensions"] = extensions
    commitment_rows[token] = row


def _material_requirements_total_mass(required_materials: List[dict]) -> int:
    total = 0
    for row in required_materials:
        if not isinstance(row, dict):
            continue
        total += int(max(0, _as_int(row.get("quantity_mass_raw", 0), 0)))
    return int(total)


def _validate_materials_available(
    *,
    inventory_index: Dict[str, dict],
    node_id: str,
    required_materials: List[dict],
) -> Tuple[dict, List[str]]:
    inventory_row = _inventory_ensure(inventory_index, node_id)
    stocks = dict(inventory_row.get("material_stocks") or {})
    consumed_batches = _sorted_unique_strings(list(inventory_row.get("batch_refs") or []))
    for row in required_materials:
        material_id = str((dict(row or {})).get("material_id_or_class", "")).strip()
        quantity_mass_raw = int(max(0, _as_int((dict(row or {})).get("quantity_mass_raw", 0), 0)))
        if not material_id or quantity_mass_raw <= 0:
            continue
        available_mass = int(max(0, _as_int(stocks.get(material_id, 0), 0)))
        if available_mass < quantity_mass_raw:
            raise ConstructionError(
                REFUSAL_CONSTRUCTION_INSUFFICIENT_MATERIAL,
                "construction step requires unavailable material stock",
                {
                    "node_id": str(node_id),
                    "material_id": material_id,
                    "required_mass": int(quantity_mass_raw),
                    "available_mass": int(available_mass),
                },
            )
        stocks[material_id] = int(available_mass - int(quantity_mass_raw))
    return inventory_row, consumed_batches


def _apply_material_consumption(
    *,
    inventory_index: Dict[str, dict],
    node_id: str,
    required_materials: List[dict],
) -> None:
    for row in required_materials:
        material_id = str((dict(row or {})).get("material_id_or_class", "")).strip()
        quantity_mass_raw = int(max(0, _as_int((dict(row or {})).get("quantity_mass_raw", 0), 0)))
        if not material_id or quantity_mass_raw <= 0:
            continue
        _inventory_apply(
            inventory_index,
            node_id=str(node_id),
            material_id=material_id,
            delta_mass=-1 * int(quantity_mass_raw),
        )


def create_construction_project(
    *,
    repo_root: str,
    blueprint_id: str,
    parameter_values: Mapping[str, object] | None,
    pack_lock_hash: str,
    site_ref: str,
    logistics_node_id: str,
    construction_policy_registry: Mapping[str, object] | None,
    construction_policy_id: str,
    blueprint_registry: Mapping[str, object],
    part_class_registry: Mapping[str, object],
    connection_type_registry: Mapping[str, object],
    material_class_registry: Mapping[str, object] | None,
    actor_subject_id: str,
    intent_id: str,
    current_tick: int,
    event_sequence_start: int = 0,
    owner_faction_id: str | None = None,
) -> Dict[str, object]:
    blueprint_token = str(blueprint_id).strip()
    site_token = str(site_ref).strip()
    source_node_id = str(logistics_node_id).strip()
    if not blueprint_token:
        raise ConstructionError(
            REFUSAL_CONSTRUCTION_BLUEPRINT_MISSING,
            "blueprint_id is required for construction project creation",
            {"field": "blueprint_id"},
        )
    if not site_token or not source_node_id:
        raise ConstructionError(
            REFUSAL_CONSTRUCTION_SITE_INVALID,
            "site_ref and logistics_node_id are required for construction project creation",
            {"site_ref": site_token, "logistics_node_id": source_node_id},
        )

    params = dict((str(key), (dict(parameter_values or {})).get(key)) for key in sorted((parameter_values or {}).keys()))
    params_hash = canonical_sha256(params)
    policy_row = _resolve_policy(
        construction_policy_registry=construction_policy_registry,
        construction_policy_id=str(construction_policy_id),
    )
    selected_policy_id = str(policy_row.get("policy_id", "")).strip()
    try:
        compiled = compile_blueprint_artifacts(
            repo_root=str(repo_root),
            blueprint_id=blueprint_token,
            parameter_values=params,
            pack_lock_hash=str(pack_lock_hash).strip() or ("0" * 64),
            blueprint_registry=blueprint_registry,
            part_class_registry=part_class_registry,
            connection_type_registry=connection_type_registry,
            material_class_registry=material_class_registry,
        )
    except BlueprintCompileError as exc:
        raise ConstructionError(
            REFUSAL_CONSTRUCTION_BLUEPRINT_MISSING,
            "construction project cannot compile blueprint artifact",
            {
                "blueprint_id": blueprint_token,
                "reason_code": str(exc.reason_code),
                "details": dict(exc.details),
            },
        )

    ag_artifact = dict(compiled.get("compiled_ag_artifact") or {})
    bom_artifact = dict(compiled.get("compiled_bom_artifact") or {})
    ag = dict(ag_artifact.get("ag") or {})
    bom = dict(bom_artifact.get("bom") or {})
    ag_nodes = dict(ag.get("nodes") or {})
    bom_material_rows = _material_requirement_rows(list(bom.get("required_materials") or []))
    bom_part_rows = _part_class_requirement_rows(list(bom.get("required_part_classes") or []))
    ag_node_ids = sorted(set(str(node_id).strip() for node_id in ag_nodes.keys() if str(node_id).strip()))

    project_id = _project_identity(
        blueprint_id=blueprint_token,
        site_ref=site_token,
        created_tick=int(max(0, int(current_tick))),
        params_hash=params_hash,
    )
    actor_subject_token = _construction_actor_subject_id(actor_subject_id)
    structure_instance_id = _structure_instance_id(
        project_id=project_id,
        ag_id=str(ag.get("ag_id", "")).strip(),
        site_ref=site_token,
    )

    step_seed_rows: Dict[str, dict] = {}
    for index, ag_node_id in enumerate(ag_node_ids):
        node_row = dict(ag_nodes.get(ag_node_id) or {})
        node_kind = str(node_row.get("node_kind", "")).strip() or "part"
        step_seed_rows[ag_node_id] = {
            "ag_node_id": ag_node_id,
            "index": int(index),
            "node_kind": node_kind,
            "part_class_id": str(node_row.get("part_class_id", "")).strip() or None,
            "required_materials": _node_material_requirements(
                node_row=node_row,
                bom_material_rows=bom_material_rows,
                is_primary_node=bool(index == 0),
            ),
            "required_part_classes": (
                [{"part_class_id": str(node_row.get("part_class_id", "")).strip(), "count": 1}]
                if str(node_row.get("part_class_id", "")).strip()
                else (list(bom_part_rows) if index == 0 else [])
            ),
            "duration_ticks": _resolve_step_duration(policy_row, node_kind=node_kind),
            "dependency_node_ids": _sorted_unique_strings(list(node_row.get("children") or [])),
            "planned_commitment_ids": _sorted_unique_strings(list(node_row.get("planned_commitment_ids") or [])),
            "tags": _sorted_unique_strings(list(node_row.get("tags") or [])),
        }

    schedule = _resolve_schedule_windows(
        created_tick=int(max(0, int(current_tick))),
        step_seed_rows=step_seed_rows,
    )
    step_rows: List[dict] = []
    commitment_rows: List[dict] = []
    milestone_commitment_ids: List[str] = []
    for ag_node_id in sorted(step_seed_rows.keys()):
        seed = dict(step_seed_rows.get(ag_node_id) or {})
        start_tick, end_tick = schedule.get(ag_node_id, (int(max(0, int(current_tick))), int(max(0, int(current_tick)) + 1)))
        step_id = "step.{}".format(
            canonical_sha256(
                {
                    "project_id": project_id,
                    "ag_node_id": ag_node_id,
                }
            )[:24]
        )
        start_commitment_id = "commitment.construction.start.{}".format(
            canonical_sha256({"project_id": project_id, "step_id": step_id, "kind": "start"})[:20]
        )
        end_commitment_id = "commitment.construction.end.{}".format(
            canonical_sha256({"project_id": project_id, "step_id": step_id, "kind": "end"})[:20]
        )
        milestone_commitment_ids.extend([start_commitment_id, end_commitment_id])
        required_materials = _material_requirement_rows(list(seed.get("required_materials") or []))
        required_part_classes = _part_class_requirement_rows(list(seed.get("required_part_classes") or []))
        step_rows.append(
            {
                "schema_version": "1.0.0",
                "step_id": step_id,
                "project_id": project_id,
                "ag_node_id": ag_node_id,
                "required_materials": list(required_materials),
                "required_part_classes": list(required_part_classes),
                "scheduled_start_tick": int(max(0, int(start_tick))),
                "scheduled_end_tick": int(max(int(start_tick), int(end_tick))),
                "status": "planned",
                "output_batch_id": None,
                "extensions": {
                    "node_kind": str(seed.get("node_kind", "")).strip(),
                    "part_class_id": seed.get("part_class_id"),
                    "dependency_node_ids": _sorted_unique_strings(list(seed.get("dependency_node_ids") or [])),
                    "start_commitment_id": start_commitment_id,
                    "end_commitment_id": end_commitment_id,
                    "consumed_batch_ids": [],
                    "planned_commitment_ids": _sorted_unique_strings(list(seed.get("planned_commitment_ids") or [])),
                    "tags": _sorted_unique_strings(list(seed.get("tags") or [])),
                },
            }
        )
        commitment_rows.append(
            _construction_commitment_row(
                commitment_id=start_commitment_id,
                project_id=project_id,
                step_id=step_id,
                commitment_kind="construction.step_start",
                scheduled_tick=int(start_tick),
                actor_subject_id=actor_subject_token,
                status="scheduled",
                extensions={"process_id": "process.construction_project_tick", "ag_node_id": ag_node_id},
            )
        )
        commitment_rows.append(
            _construction_commitment_row(
                commitment_id=end_commitment_id,
                project_id=project_id,
                step_id=step_id,
                commitment_kind="construction.step_end",
                scheduled_tick=int(end_tick),
                actor_subject_id=actor_subject_token,
                status="scheduled",
                extensions={"process_id": "process.construction_project_tick", "ag_node_id": ag_node_id},
            )
        )

    milestone_commitment_ids = _sorted_unique_strings(milestone_commitment_ids)
    project_row = {
        "schema_version": "1.0.0",
        "project_id": project_id,
        "blueprint_id": blueprint_token,
        "compiled_ag_id": str(ag.get("ag_id", "")).strip() or "compiled_ag.{}".format(str(ag_artifact.get("artifact_hash", ""))[:20]),
        "bom_id": str(bom.get("bom_id", "")).strip() or "compiled_bom.{}".format(str(bom_artifact.get("artifact_hash", ""))[:20]),
        "site_ref": site_token,
        "owner_faction_id": str(owner_faction_id).strip() if owner_faction_id is not None else None,
        "logistics_node_id": source_node_id,
        "created_tick": int(max(0, int(current_tick))),
        "status": "planned",
        "milestone_commitment_ids": list(milestone_commitment_ids),
        "progress_state_ref": None,
        "extensions": {
            "construction_policy_id": selected_policy_id,
            "ag_id": str(ag.get("ag_id", "")).strip(),
            "root_node_id": str(ag.get("root_node_id", "")).strip(),
            "compiled_ag_hash": str(ag_artifact.get("artifact_hash", "")).strip(),
            "compiled_bom_hash": str(bom_artifact.get("artifact_hash", "")).strip(),
            "cache_key": str(compiled.get("cache_key", "")).strip(),
            "params_hash": params_hash,
            "parameters": dict(params),
            "pack_lock_hash": str(pack_lock_hash).strip(),
            "intent_id": str(intent_id).strip(),
            "ag_node_order": list(ag_node_ids),
            "batches_consumed": [],
            "output_batch_ids": [],
            "reenactment_descriptor": {
                "project_id": project_id,
                "actor_subject_id": actor_subject_token,
                "site_ref": site_token,
                "policy_id": selected_policy_id,
                "step_sequence": [],
            },
        },
    }
    structure_instance = {
        "schema_version": "1.0.0",
        "instance_id": structure_instance_id,
        "project_id": project_id,
        "ag_id": str((dict(project_row.get("extensions") or {})).get("ag_id", "")).strip() or str(project_row.get("compiled_ag_id", "")),
        "site_ref": site_token,
        "installed_node_states": [],
        "maintenance_backlog": {"pending_count": 0, "items": []},
        "extensions": {
            "project_status": "planned",
            "created_tick": int(max(0, int(current_tick))),
            "ag_node_order": list(ag_node_ids),
        },
    }

    sequence = int(max(0, _as_int(event_sequence_start, 0)))
    project_event = _event_row(
        event_type_id="event.construct_project_created",
        tick=int(max(0, int(current_tick))),
        actor_subject_id=actor_subject_token,
        site_ref=site_token,
        linked_project_id=project_id,
        linked_step_id=None,
        inputs=[],
        outputs=[str(structure_instance.get("instance_id", ""))],
        ledger_deltas={},
        sequence=sequence,
        extensions={"blueprint_id": blueprint_token, "construction_policy_id": selected_policy_id},
    )
    sequence += 1
    return {
        "project": project_row,
        "steps": sorted(step_rows, key=lambda row: (str(row.get("ag_node_id", "")), str(row.get("step_id", "")))),
        "commitments": sorted(commitment_rows, key=lambda row: str(row.get("commitment_id", ""))),
        "provenance_events": [project_event],
        "installed_structure_instance": structure_instance,
        "compiled": dict(compiled),
        "next_event_sequence": int(sequence),
    }


def _active_project_ids(project_rows: Dict[str, dict]) -> List[str]:
    ids = []
    for project_id in sorted(project_rows.keys()):
        status = str((project_rows.get(project_id) or {}).get("status", "")).strip() or "planned"
        if status in _PROJECT_ACTIVE_STATUSES:
            ids.append(project_id)
    return ids


def _normalize_step_status(status: object) -> str:
    token = str(status or "").strip() or "planned"
    if token not in ("planned", "executing", "completed", "failed"):
        return "planned"
    return token


def _normalize_project_status(status: object) -> str:
    token = str(status or "").strip() or "planned"
    if token not in ("planned", "executing", "paused", "completed", "failed"):
        return "planned"
    return token


def _apply_step_preflight(
    *,
    preview_inventory: Dict[str, dict],
    node_id: str,
    start_step_rows: List[dict],
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for step_row in start_step_rows:
        step_id = str(step_row.get("step_id", "")).strip()
        required_materials = _material_requirement_rows(list(step_row.get("required_materials") or []))
        inventory_row, consumed_batches = _validate_materials_available(
            inventory_index=preview_inventory,
            node_id=node_id,
            required_materials=required_materials,
        )
        del inventory_row
        _apply_material_consumption(
            inventory_index=preview_inventory,
            node_id=node_id,
            required_materials=required_materials,
        )
        out[step_id] = {
            "required_materials": list(required_materials),
            "consumed_batch_ids": list(consumed_batches),
            "total_mass_raw": _material_requirements_total_mass(required_materials),
        }
    return out


def _project_step_progress(step_rows: List[dict]) -> Tuple[int, int]:
    total = 0
    completed = 0
    for row in step_rows:
        if not isinstance(row, dict):
            continue
        total += 1
        if _normalize_step_status(row.get("status", "planned")) == "completed":
            completed += 1
    return int(completed), int(total)


def tick_construction_projects(
    *,
    projects: object,
    steps: object,
    commitments: object,
    installed_structures: object,
    inventory_index: Mapping[str, object] | None,
    current_tick: int,
    actor_subject_id: str,
    construction_policy_registry: Mapping[str, object] | None,
    event_sequence_start: int = 0,
    max_projects_to_tick: int = 0,
    max_parallel_steps_override: int = 0,
) -> Dict[str, object]:
    project_rows = _project_rows_by_id(projects)
    step_rows_by_project = _construction_step_rows_by_project(steps)
    commitment_rows = _construction_commitment_rows_by_id(commitments)
    structure_rows = _installed_structure_rows_by_project(installed_structures)
    inventory = build_inventory_index(list((inventory_index or {}).values()) if isinstance(inventory_index, dict) else inventory_index)
    policy_rows = construction_policy_rows_by_id(construction_policy_registry)
    selected_project_ids = _active_project_ids(project_rows)
    skipped_project_ids: List[str] = []
    if int(max_projects_to_tick) > 0 and len(selected_project_ids) > int(max_projects_to_tick):
        skipped_project_ids = list(selected_project_ids[int(max_projects_to_tick):])
        selected_project_ids = list(selected_project_ids[: int(max_projects_to_tick)])
    actor_subject_token = _construction_actor_subject_id(actor_subject_id)
    sequence = int(max(0, _as_int(event_sequence_start, 0)))
    events: List[dict] = []
    started_step_count = 0
    completed_step_count = 0
    active_step_count = 0

    for project_id in selected_project_ids:
        project_row = dict(project_rows.get(project_id) or {})
        project_status = _normalize_project_status(project_row.get("status", "planned"))
        if project_status in ("paused",) or project_status in _PROJECT_TERMINAL_STATUSES:
            continue
        project_extensions = dict(project_row.get("extensions") or {})
        site_ref = str(project_row.get("site_ref", "")).strip()
        node_id = str(project_row.get("logistics_node_id", "")).strip()
        policy_id = str(project_extensions.get("construction_policy_id", "")).strip()
        policy_row = dict(policy_rows.get(policy_id) or {})
        if not policy_row:
            policy_row = _resolve_policy(
                construction_policy_registry=construction_policy_registry,
                construction_policy_id="build.policy.default",
            )
            project_extensions["construction_policy_id"] = str(policy_row.get("policy_id", ""))

        allow_parallel = bool(policy_row.get("allow_parallel_steps", False))
        max_parallel_steps = int(max(1, _as_int(policy_row.get("max_parallel_steps", 1), 1)))
        if not allow_parallel:
            max_parallel_steps = 1
        if int(max_parallel_steps_override) > 0:
            max_parallel_steps = int(min(max_parallel_steps, int(max_parallel_steps_override)))

        project_steps = [dict(row) for row in list(step_rows_by_project.get(project_id) or []) if isinstance(row, dict)]
        if not project_steps:
            project_row["status"] = "completed"
            project_row["progress_state_ref"] = "progress.completed.0/0"
            project_extensions["completion_tick"] = int(max(0, int(current_tick)))
            project_row["extensions"] = project_extensions
            project_rows[project_id] = project_row
            structure_row = dict(structure_rows.get(project_id) or {})
            if structure_row:
                structure_extensions = dict(structure_row.get("extensions") or {})
                structure_extensions["project_status"] = "completed"
                structure_extensions["last_project_tick"] = int(max(0, int(current_tick)))
                structure_row["extensions"] = structure_extensions
                structure_rows[project_id] = structure_row
            continue

        completed_step_ids = set(
            str(row.get("ag_node_id", "")).strip()
            for row in project_steps
            if _normalize_step_status(row.get("status", "planned")) == "completed"
        )
        executing_steps = [
            row for row in project_steps if _normalize_step_status(row.get("status", "planned")) == "executing"
        ]
        planned_candidates = []
        for row in project_steps:
            status = _normalize_step_status(row.get("status", "planned"))
            if status != "planned":
                continue
            scheduled_start_tick = int(max(0, _as_int(row.get("scheduled_start_tick", 0), 0)))
            if int(current_tick) < scheduled_start_tick:
                continue
            dependencies = _sorted_unique_strings(list((dict(row.get("extensions") or {})).get("dependency_node_ids") or []))
            if any(dep_id not in completed_step_ids for dep_id in dependencies):
                continue
            planned_candidates.append(dict(row))
        planned_candidates = sorted(
            planned_candidates,
            key=lambda row: (str(row.get("ag_node_id", "")), str(row.get("step_id", ""))),
        )
        available_slots = int(max(0, int(max_parallel_steps) - len(executing_steps)))
        start_steps = list(planned_candidates[:available_slots]) if available_slots > 0 else []

        if start_steps:
            preview_inventory = copy.deepcopy(inventory)
            preflight = _apply_step_preflight(
                preview_inventory=preview_inventory,
                node_id=node_id,
                start_step_rows=start_steps,
            )
            for step_row in start_steps:
                step_id = str(step_row.get("step_id", "")).strip()
                preflight_row = dict(preflight.get(step_id) or {})
                required_materials = _material_requirement_rows(list(preflight_row.get("required_materials") or []))
                consumed_batch_ids = _sorted_unique_strings(list(preflight_row.get("consumed_batch_ids") or []))
                total_mass_raw = int(max(0, _as_int(preflight_row.get("total_mass_raw", 0), 0)))
                _apply_material_consumption(
                    inventory_index=inventory,
                    node_id=node_id,
                    required_materials=required_materials,
                )
                row_extensions = dict(step_row.get("extensions") or {})
                row_extensions["started_tick"] = int(max(0, int(current_tick)))
                row_extensions["actor_subject_id"] = actor_subject_token
                row_extensions["consumed_batch_ids"] = list(consumed_batch_ids)
                step_row["extensions"] = row_extensions
                step_row["status"] = "executing"
                started_step_count += 1
                start_commitment_id = str(row_extensions.get("start_commitment_id", "")).strip()
                if start_commitment_id:
                    _set_commitment_status(
                        commitment_rows,
                        commitment_id=start_commitment_id,
                        status="completed",
                        tick=int(current_tick),
                    )
                start_event = _event_row(
                    event_type_id="event.construct_step_started",
                    tick=int(max(0, int(current_tick))),
                    actor_subject_id=actor_subject_token,
                    site_ref=site_ref,
                    linked_project_id=project_id,
                    linked_step_id=step_id,
                    inputs=list(consumed_batch_ids),
                    outputs=[],
                    ledger_deltas={},
                    sequence=sequence,
                    extensions={"ag_node_id": str(step_row.get("ag_node_id", "")).strip()},
                )
                sequence += 1
                events.append(start_event)
                if total_mass_raw > 0:
                    consume_event = _event_row(
                        event_type_id="event.material_consumed",
                        tick=int(max(0, int(current_tick))),
                        actor_subject_id=actor_subject_token,
                        site_ref=site_ref,
                        linked_project_id=project_id,
                        linked_step_id=step_id,
                        inputs=list(consumed_batch_ids),
                        outputs=[],
                        ledger_deltas={"quantity.mass": -1 * int(total_mass_raw)},
                        sequence=sequence,
                        extensions={
                            "ag_node_id": str(step_row.get("ag_node_id", "")).strip(),
                            "logistics_node_id": node_id,
                        },
                    )
                    sequence += 1
                    events.append(consume_event)
                    project_extensions["batches_consumed"] = _sorted_unique_strings(
                        list(project_extensions.get("batches_consumed") or []) + list(consumed_batch_ids)
                    )
                for idx, row in enumerate(project_steps):
                    if str(row.get("step_id", "")).strip() == step_id:
                        project_steps[idx] = dict(step_row)
                        break

        executing_steps = [
            dict(row) for row in project_steps if _normalize_step_status(row.get("status", "planned")) == "executing"
        ]
        completion_candidates = []
        for row in executing_steps:
            end_tick = int(max(0, _as_int(row.get("scheduled_end_tick", row.get("scheduled_start_tick", 0)), 0)))
            if int(current_tick) >= int(end_tick):
                completion_candidates.append(dict(row))
        completion_candidates = sorted(
            completion_candidates,
            key=lambda row: (str(row.get("ag_node_id", "")), str(row.get("step_id", ""))),
        )
        for step_row in completion_candidates:
            step_id = str(step_row.get("step_id", "")).strip()
            ag_node_id = str(step_row.get("ag_node_id", "")).strip()
            required_materials = _material_requirement_rows(list(step_row.get("required_materials") or []))
            total_mass_raw = _material_requirements_total_mass(required_materials)
            step_extensions = dict(step_row.get("extensions") or {})
            output_batch_id = str(step_row.get("output_batch_id", "")).strip()
            if not output_batch_id:
                output_batch_id = _step_output_batch_id(
                    project_id=project_id,
                    step_id=step_id,
                    ag_node_id=ag_node_id,
                    scheduled_end_tick=int(max(0, _as_int(step_row.get("scheduled_end_tick", current_tick), current_tick))),
                )
            step_row["output_batch_id"] = output_batch_id
            step_row["status"] = "completed"
            step_extensions["completed_tick"] = int(max(0, int(current_tick)))
            step_extensions["actor_subject_id"] = actor_subject_token
            step_row["extensions"] = step_extensions
            completed_step_count += 1

            end_commitment_id = str(step_extensions.get("end_commitment_id", "")).strip()
            if end_commitment_id:
                _set_commitment_status(
                    commitment_rows,
                    commitment_id=end_commitment_id,
                    status="completed",
                    tick=int(current_tick),
                )
            completed_event = _event_row(
                event_type_id="event.construct_step_completed",
                tick=int(max(0, int(current_tick))),
                actor_subject_id=actor_subject_token,
                site_ref=site_ref,
                linked_project_id=project_id,
                linked_step_id=step_id,
                inputs=_sorted_unique_strings(list(step_extensions.get("consumed_batch_ids") or [])),
                outputs=[output_batch_id],
                ledger_deltas={},
                sequence=sequence,
                extensions={"ag_node_id": ag_node_id},
            )
            sequence += 1
            events.append(completed_event)
            batch_event = _event_row(
                event_type_id="event.batch_created",
                tick=int(max(0, int(current_tick))),
                actor_subject_id=actor_subject_token,
                site_ref=site_ref,
                linked_project_id=project_id,
                linked_step_id=step_id,
                inputs=[],
                outputs=[output_batch_id],
                ledger_deltas={"quantity.mass": int(total_mass_raw)},
                sequence=sequence,
                extensions={"ag_node_id": ag_node_id},
            )
            sequence += 1
            events.append(batch_event)
            install_event = _event_row(
                event_type_id="event.install_part",
                tick=int(max(0, int(current_tick))),
                actor_subject_id=actor_subject_token,
                site_ref=site_ref,
                linked_project_id=project_id,
                linked_step_id=step_id,
                inputs=[],
                outputs=[output_batch_id],
                ledger_deltas={},
                sequence=sequence,
                extensions={"ag_node_id": ag_node_id},
            )
            sequence += 1
            events.append(install_event)
            project_extensions["output_batch_ids"] = _sorted_unique_strings(
                list(project_extensions.get("output_batch_ids") or []) + [output_batch_id]
            )

            structure_row = dict(structure_rows.get(project_id) or {})
            if structure_row:
                installed_nodes = _sorted_unique_strings(list(structure_row.get("installed_node_states") or []) + [ag_node_id])
                structure_row["installed_node_states"] = list(installed_nodes)
                structure_extensions = dict(structure_row.get("extensions") or {})
                structure_extensions["last_install_tick"] = int(max(0, int(current_tick)))
                structure_extensions["project_status"] = "executing"
                structure_row["extensions"] = structure_extensions
                structure_rows[project_id] = structure_row
            for idx, row in enumerate(project_steps):
                if str(row.get("step_id", "")).strip() == step_id:
                    project_steps[idx] = dict(step_row)
                    break

        completed_count, total_count = _project_step_progress(project_steps)
        any_failed = any(_normalize_step_status(row.get("status", "planned")) == "failed" for row in project_steps)
        if any_failed:
            project_status = "failed"
        elif int(total_count) > 0 and int(completed_count) >= int(total_count):
            project_status = "completed"
        else:
            project_status = "executing"
        project_row["status"] = project_status
        project_row["progress_state_ref"] = "progress.completed.{}/{}".format(int(completed_count), int(total_count))
        project_extensions["progress"] = {"completed": int(completed_count), "total": int(total_count)}
        project_extensions["last_project_tick"] = int(max(0, int(current_tick)))
        reenactment_descriptor = dict(project_extensions.get("reenactment_descriptor") or {})
        step_sequence = list(reenactment_descriptor.get("step_sequence") or [])
        for event_row in [row for row in events if str(row.get("linked_project_id", "")).strip() == project_id]:
            step_sequence.append(
                {
                    "event_id": str(event_row.get("event_id", "")),
                    "tick": int(max(0, _as_int(event_row.get("tick", 0), 0))),
                    "event_type_id": str(event_row.get("event_type_id", "")),
                    "linked_step_id": str(event_row.get("linked_step_id", "")),
                    "inputs": _sorted_unique_strings(list(event_row.get("inputs") or [])),
                    "outputs": _sorted_unique_strings(list(event_row.get("outputs") or [])),
                }
            )
        reenactment_descriptor["step_sequence"] = sorted(
            (
                dict(item)
                for item in step_sequence
                if isinstance(item, dict) and str(item.get("event_id", "")).strip()
            ),
            key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("event_id", ""))),
        )
        project_extensions["reenactment_descriptor"] = reenactment_descriptor
        project_row["extensions"] = project_extensions
        project_rows[project_id] = project_row
        step_rows_by_project[project_id] = sorted(
            (dict(item) for item in project_steps if isinstance(item, dict)),
            key=lambda item: (str(item.get("ag_node_id", "")), str(item.get("step_id", ""))),
        )

        structure_row = dict(structure_rows.get(project_id) or {})
        if structure_row:
            structure_extensions = dict(structure_row.get("extensions") or {})
            structure_extensions["project_status"] = str(project_status)
            structure_extensions["last_project_tick"] = int(max(0, int(current_tick)))
            if project_status == "completed":
                structure_extensions["completion_tick"] = int(max(0, int(current_tick)))
            structure_row["extensions"] = structure_extensions
            structure_rows[project_id] = structure_row

        active_step_count += len(
            [
                row
                for row in project_steps
                if _normalize_step_status(row.get("status", "planned")) in _STEP_ACTIVE_STATUSES
            ]
        )

    project_rows_out = [dict(project_rows[key]) for key in sorted(project_rows.keys())]
    step_rows_out: List[dict] = []
    for project_id in sorted(step_rows_by_project.keys()):
        step_rows_out.extend(
            sorted(
                (dict(item) for item in list(step_rows_by_project.get(project_id) or []) if isinstance(item, dict)),
                key=lambda item: (str(item.get("project_id", "")), str(item.get("ag_node_id", "")), str(item.get("step_id", ""))),
            )
        )
    commitment_rows_out = [dict(commitment_rows[key]) for key in sorted(commitment_rows.keys())]
    structure_rows_out = [dict(structure_rows[key]) for key in sorted(structure_rows.keys())]
    events_out = sorted(
        (dict(row) for row in events if isinstance(row, dict) and str(row.get("event_id", "")).strip()),
        key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
    )
    budget_outcome = "complete"
    if skipped_project_ids:
        budget_outcome = "degraded"
    return {
        "projects": project_rows_out,
        "steps": step_rows_out,
        "commitments": commitment_rows_out,
        "installed_structures": structure_rows_out,
        "inventory_index": inventory,
        "events": events_out,
        "next_event_sequence": int(sequence),
        "processed_project_count": int(len(selected_project_ids)),
        "skipped_project_ids": list(skipped_project_ids),
        "budget_outcome": budget_outcome,
        "started_step_count": int(started_step_count),
        "completed_step_count": int(completed_step_count),
        "active_step_count": int(active_step_count),
    }
