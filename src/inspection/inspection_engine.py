"""Deterministic MAT-9 inspection snapshot engine (derived-only)."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_INSPECT_FORBIDDEN_BY_LAW = "refusal.inspect.forbidden_by_law"
REFUSAL_INSPECT_BUDGET_EXCEEDED = "refusal.inspect.budget_exceeded"
REFUSAL_INSPECT_TARGET_INVALID = "refusal.inspect.target_invalid"

_VALID_TARGET_KINDS = {"structure", "project", "node", "manifest", "cohort", "faction"}
_VALID_FIDELITY = ("macro", "meso", "micro")
_SECTION_IDS_BY_FIDELITY = {
    "macro": [
        "section.material_stocks",
        "section.flow_summary",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
    ],
    "meso": [
        "section.material_stocks",
        "section.batches_summary",
        "section.flow_summary",
        "section.ag_progress",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
        "section.reenactment_link",
    ],
    "micro": [
        "section.material_stocks",
        "section.batches_summary",
        "section.flow_summary",
        "section.ag_progress",
        "section.maintenance_backlog",
        "section.failure_risk_summary",
        "section.commitments_summary",
        "section.events_summary",
        "section.reenactment_link",
        "section.micro_parts_summary",
    ],
}
_DEFAULT_SECTION_ROWS = {
    "section.material_stocks": {"title": "Material Stocks", "extensions": {"cost_units": 1}},
    "section.batches_summary": {"title": "Batches Summary", "extensions": {"cost_units": 2}},
    "section.flow_summary": {"title": "Flow Summary", "extensions": {"cost_units": 1}},
    "section.ag_progress": {"title": "Assembly Progress", "extensions": {"cost_units": 2}},
    "section.maintenance_backlog": {"title": "Maintenance Backlog", "extensions": {"cost_units": 1}},
    "section.failure_risk_summary": {"title": "Failure Risk Summary", "extensions": {"cost_units": 1}},
    "section.commitments_summary": {"title": "Commitments", "extensions": {"cost_units": 2}},
    "section.events_summary": {"title": "Events", "extensions": {"cost_units": 2}},
    "section.reenactment_link": {"title": "Reenactment", "extensions": {"cost_units": 1}},
    "section.micro_parts_summary": {"title": "Micro Parts Summary", "extensions": {"cost_units": 4}},
}


class InspectionError(ValueError):
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


def _quantize_map(values: object, *, step: int) -> dict:
    if not isinstance(values, dict):
        return {}
    quant = max(1, _as_int(step, 1))
    out = {}
    for key, value in sorted(values.items(), key=lambda item: str(item[0])):
        token = str(key).strip()
        if not token:
            continue
        raw = _as_int(value, 0)
        if quant > 1:
            raw = (raw // quant) * quant
        out[token] = int(raw)
    return out


def _target_kind_from_target_id(target_id: str) -> str:
    token = str(target_id or "").strip()
    if token.startswith("assembly.structure_instance."):
        return "structure"
    if token.startswith("project.construction."):
        return "project"
    if token.startswith("node.") or token.startswith("logistics.node."):
        return "node"
    if token.startswith("manifest."):
        return "manifest"
    if token.startswith("cohort."):
        return "cohort"
    if token.startswith("faction."):
        return "faction"
    return "structure"


def normalize_inspection_request_row(row: Mapping[str, object], *, current_tick: int) -> dict:
    payload = dict(row or {})
    target_id = str(payload.get("target_id", "")).strip()
    if not target_id:
        raise InspectionError(REFUSAL_INSPECT_TARGET_INVALID, "inspection target_id is required", {})
    desired_fidelity = str(payload.get("desired_fidelity", "macro")).strip() or "macro"
    if desired_fidelity not in _VALID_FIDELITY:
        desired_fidelity = "macro"
    target_kind = str(payload.get("target_kind", "")).strip() or _target_kind_from_target_id(target_id)
    if target_kind not in _VALID_TARGET_KINDS:
        target_kind = _target_kind_from_target_id(target_id)
    time_range = payload.get("time_range")
    normalized_time_range = None
    if isinstance(time_range, dict):
        start_tick = max(0, _as_int(time_range.get("start_tick", 0), 0))
        end_tick = max(start_tick, _as_int(time_range.get("end_tick", start_tick), start_tick))
        normalized_time_range = {"start_tick": int(start_tick), "end_tick": int(end_tick)}
    tick = max(0, _as_int(payload.get("tick", current_tick), current_tick))
    requester_subject_id = str(payload.get("requester_subject_id", "")).strip() or "subject.system"
    max_cost_units = max(0, _as_int(payload.get("max_cost_units", 0), 0))
    request_id = str(payload.get("request_id", "")).strip()
    if not request_id:
        request_id = "inspection.request.{}".format(
            canonical_sha256(
                {
                    "target_id": target_id,
                    "target_kind": target_kind,
                    "desired_fidelity": desired_fidelity,
                    "tick": int(tick),
                    "time_range": dict(normalized_time_range or {}),
                    "requester_subject_id": requester_subject_id,
                    "max_cost_units": int(max_cost_units),
                }
            )[:24]
        )
    return {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "requester_subject_id": requester_subject_id,
        "target_kind": target_kind,
        "target_id": target_id,
        "desired_fidelity": desired_fidelity,
        "tick": int(tick),
        "time_range": normalized_time_range,
        "max_cost_units": int(max_cost_units),
        "extensions": dict(payload.get("extensions") or {}),
    }


def inspection_section_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("sections")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("sections") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("section_id", ""))):
        section_id = str(row.get("section_id", "")).strip()
        if not section_id:
            continue
        ext = dict(row.get("extensions") or {})
        out[section_id] = {
            "schema_version": "1.0.0",
            "section_id": section_id,
            "title": str(row.get("title", "")).strip() or section_id,
            "extensions": {"cost_units": max(0, _as_int(ext.get("cost_units", 1), 1)), **ext},
        }
    for section_id, default in _DEFAULT_SECTION_ROWS.items():
        if section_id in out:
            continue
        out[section_id] = {
            "schema_version": "1.0.0",
            "section_id": section_id,
            "title": str(default.get("title", section_id)),
            "extensions": dict(default.get("extensions") or {}),
        }
    return out


def _section_cost(section_rows: Mapping[str, dict], section_ids: List[str]) -> int:
    return int(
        sum(
            max(0, _as_int((dict(section_rows.get(section_id) or {}).get("extensions") or {}).get("cost_units", 1), 1))
            for section_id in section_ids
        )
    )


def _resolve_fidelity(
    *,
    desired_fidelity: str,
    max_cost_units: int,
    section_rows: Mapping[str, dict],
    micro_allowed: bool,
    micro_available: bool,
    strict_budget: bool,
) -> Tuple[str, List[str], int, bool]:
    desired = str(desired_fidelity).strip() or "macro"
    if desired not in _VALID_FIDELITY:
        desired = "macro"
    candidates = [desired]
    if desired == "micro":
        candidates.extend(["meso", "macro"])
    elif desired == "meso":
        candidates.append("macro")
    if desired == "micro" and (not micro_allowed or not micro_available):
        candidates = ["meso", "macro"]
    seen = set()
    ordered = []
    for token in candidates:
        if token in seen:
            continue
        seen.add(token)
        ordered.append(token)

    budget = max(0, _as_int(max_cost_units, 0))
    fallback = "macro"
    fallback_sections = list(_SECTION_IDS_BY_FIDELITY["macro"])
    fallback_cost = _section_cost(section_rows, fallback_sections)
    for token in ordered:
        section_ids = list(_SECTION_IDS_BY_FIDELITY[token])
        cost = _section_cost(section_rows, section_ids)
        if budget <= 0 or cost <= budget:
            return token, section_ids, int(cost), bool(token != desired)
        fallback = token
        fallback_sections = section_ids
        fallback_cost = cost
    if strict_budget:
        raise InspectionError(
            REFUSAL_INSPECT_BUDGET_EXCEEDED,
            "inspection budget cannot satisfy requested fidelity",
            {
                "desired_fidelity": desired,
                "required_cost_units": int(fallback_cost),
                "max_cost_units": int(budget),
            },
        )
    return fallback, fallback_sections, int(fallback_cost), True


def _target_structure_id(target_payload: Mapping[str, object], target_id: str) -> str:
    collection = str(target_payload.get("collection", "")).strip()
    row = dict(target_payload.get("row") or {})
    if collection == "installed_structure_instances":
        return str(row.get("instance_id", "")).strip()
    if collection == "materialization_states":
        return str(row.get("structure_id", "")).strip()
    if collection == "distribution_aggregates":
        return str(row.get("structure_id", "")).strip()
    if collection == "micro_part_instances":
        return str(row.get("parent_structure_id", "")).strip()
    if str(target_id).startswith("assembly.structure_instance."):
        return str(target_id).strip()
    return ""


def _events_for_target(state: Mapping[str, object], target_id: str, time_range: Mapping[str, object] | None) -> List[dict]:
    token = str(target_id).strip()
    rows = []
    for key in ("logistics_provenance_events", "construction_provenance_events", "maintenance_provenance_events"):
        for row in list((dict(state or {})).get(key) or []):
            if not isinstance(row, dict):
                continue
            ext = dict(row.get("extensions") or {})
            candidates = {
                str(row.get("event_id", "")).strip(),
                str(row.get("commitment_id", "")).strip(),
                str(row.get("manifest_id", "")).strip(),
                str(row.get("linked_project_id", "")).strip(),
                str(row.get("linked_step_id", "")).strip(),
                str(row.get("asset_id", "")).strip(),
                str(ext.get("asset_id", "")).strip(),
                str(ext.get("project_id", "")).strip(),
                str(ext.get("manifest_id", "")).strip(),
            }
            if token not in candidates:
                continue
            rows.append(dict(row))
    if isinstance(time_range, dict):
        start_tick = max(0, _as_int(time_range.get("start_tick", 0), 0))
        end_tick = max(start_tick, _as_int(time_range.get("end_tick", start_tick), start_tick))
        rows = [row for row in rows if start_tick <= _as_int(row.get("tick", 0), 0) <= end_tick]
    return sorted(rows, key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("event_id", ""))))


def _build_section_data(section_id: str, *, state: Mapping[str, object], target_payload: Mapping[str, object], request: Mapping[str, object], quant_step: int, include_part_ids: bool) -> dict:
    row = dict(target_payload.get("row") or {})
    if section_id == "section.material_stocks":
        stocks = dict(row.get("material_stocks") or {})
        if not stocks:
            stocks = {}
            for inv in list((dict(state or {})).get("logistics_node_inventories") or []):
                if not isinstance(inv, dict):
                    continue
                for material_id, mass in sorted((dict(inv.get("material_stocks") or {})).items(), key=lambda item: str(item[0])):
                    token = str(material_id).strip()
                    if not token:
                        continue
                    stocks[token] = _as_int(stocks.get(token, 0), 0) + max(0, _as_int(mass, 0))
        return {"stocks": _quantize_map(stocks, step=quant_step), "material_count": len(stocks.keys())}
    if section_id == "section.batches_summary":
        batches = [dict(item) for item in list((dict(state or {})).get("material_batches") or []) if isinstance(item, dict)]
        return {"batch_count": len(batches), "sample_batch_ids": [str(item.get("batch_id", "")).strip() for item in batches[:16] if str(item.get("batch_id", "")).strip()]}
    if section_id == "section.flow_summary":
        manifests = [dict(item) for item in list((dict(state or {})).get("logistics_manifests") or []) if isinstance(item, dict)]
        status_counts: Dict[str, int] = {}
        for item in manifests:
            status = str(item.get("status", "planned")).strip() or "planned"
            status_counts[status] = _as_int(status_counts.get(status, 0), 0) + 1
        return {"manifest_count": len(manifests), "status_counts": dict((k, status_counts[k]) for k in sorted(status_counts.keys()))}
    if section_id == "section.ag_progress":
        projects = [dict(item) for item in list((dict(state or {})).get("construction_projects") or []) if isinstance(item, dict)]
        steps = [dict(item) for item in list((dict(state or {})).get("construction_steps") or []) if isinstance(item, dict)]
        completed = len([item for item in steps if str(item.get("status", "")).strip() == "completed"])
        total = max(1, len(steps))
        return {"project_count": len(projects), "step_total": len(steps), "step_completed": completed, "progress_permille": int((1000 * completed) // total)}
    if section_id == "section.maintenance_backlog":
        assets = [dict(item) for item in list((dict(state or {})).get("asset_health_states") or []) if isinstance(item, dict)]
        total = sum(max(0, _as_int(item.get("maintenance_backlog", 0), 0)) for item in assets)
        return {"asset_count": len(assets), "backlog_total": int(_quantize_map({"value": total}, step=quant_step).get("value", 0))}
    if section_id == "section.failure_risk_summary":
        payload_ext = dict(target_payload.get("extensions") or {})
        explicit = dict(payload_ext.get("failure_risk_summary") or {})
        if explicit:
            return {"risk_rows": [dict(item) for item in list(explicit.get("risk_rows") or [])[:16] if isinstance(item, dict)]}
        return {"risk_rows": []}
    if section_id == "section.commitments_summary":
        rows = []
        for key in ("material_commitments", "construction_commitments", "shipment_commitments", "maintenance_commitments"):
            rows.extend([dict(item) for item in list((dict(state or {})).get(key) or []) if isinstance(item, dict)])
        status_counts: Dict[str, int] = {}
        for item in rows:
            status = str(item.get("status", "planned")).strip() or "planned"
            status_counts[status] = _as_int(status_counts.get(status, 0), 0) + 1
        return {"commitment_count": len(rows), "status_counts": dict((k, status_counts[k]) for k in sorted(status_counts.keys()))}
    if section_id == "section.events_summary":
        rows = _events_for_target(state, str(request.get("target_id", "")), request.get("time_range") if isinstance(request.get("time_range"), dict) else None)
        return {"event_count": len(rows), "sample_event_ids": [str(item.get("event_id", "")).strip() for item in rows[:24] if str(item.get("event_id", "")).strip()]}
    if section_id == "section.reenactment_link":
        requests = [dict(item) for item in list((dict(state or {})).get("reenactment_requests") or []) if isinstance(item, dict)]
        request_ids = {str(item.get("request_id", "")).strip() for item in requests if str(item.get("target_id", "")).strip() == str(request.get("target_id", "")).strip()}
        artifacts = [dict(item) for item in list((dict(state or {})).get("reenactment_artifacts") or []) if isinstance(item, dict) and str(item.get("request_id", "")).strip() in request_ids]
        latest = sorted(artifacts, key=lambda item: str(item.get("reenactment_id", "")))[-1] if artifacts else {}
        return {"available": bool(latest), "artifact_count": len(artifacts), "latest_reenactment_id": str(latest.get("reenactment_id", "")).strip()}
    if section_id == "section.micro_parts_summary":
        structure_id = _target_structure_id(target_payload, str(request.get("target_id", "")))
        micro_rows = [dict(item) for item in list((dict(state or {})).get("micro_part_instances") or []) if isinstance(item, dict)]
        if structure_id:
            micro_rows = [item for item in micro_rows if str(item.get("parent_structure_id", "")).strip() == structure_id]
        return {
            "structure_id": structure_id,
            "part_count": len(micro_rows),
            "part_ids": [str(item.get("micro_part_id", "")).strip() for item in micro_rows[:128] if include_part_ids and str(item.get("micro_part_id", "")).strip()],
        }
    return {}


def build_inspection_snapshot_artifact(
    *,
    request_row: Mapping[str, object],
    target_payload: Mapping[str, object],
    state: Mapping[str, object],
    truth_hash_anchor: str,
    ledger_hash: str,
    section_registry_payload: Mapping[str, object] | None,
    policy_context: Mapping[str, object] | None,
    law_profile: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
    physics_profile_id: str,
    pack_lock_hash: str,
    cache_policy_id: str,
    strict_budget: bool,
) -> Tuple[dict, dict]:
    request = normalize_inspection_request_row(request_row, current_tick=_as_int(request_row.get("tick", 0), 0))
    payload = dict(target_payload or {})
    if not bool(payload.get("exists", False)):
        raise InspectionError(REFUSAL_INSPECT_TARGET_INVALID, "inspection target is unavailable", {"target_id": str(request.get("target_id", ""))})

    visibility_level = str((dict((dict(authority_context or {})).get("epistemic_scope") or {})).get("visibility_level", "")).strip() or "diegetic"
    entitlements = set(_sorted_unique_strings(list((dict(authority_context or {})).get("entitlements") or [])))
    allow_hidden_state = bool((dict(law_profile or {})).get("epistemic_limits", {}).get("allow_hidden_state_access", False))
    micro_allowed = visibility_level != "diegetic" and allow_hidden_state and "entitlement.inspect" in entitlements
    if str(request.get("desired_fidelity", "")) == "micro" and not micro_allowed and bool(strict_budget):
        raise InspectionError(REFUSAL_INSPECT_FORBIDDEN_BY_LAW, "micro inspection forbidden by law/epistemic scope", {})
    structure_id = _target_structure_id(payload, str(request.get("target_id", "")))
    micro_rows = [dict(item) for item in list((dict(state or {})).get("micro_part_instances") or []) if isinstance(item, dict)]
    micro_available = bool(micro_rows if not structure_id else [item for item in micro_rows if str(item.get("parent_structure_id", "")).strip() == structure_id])

    section_rows = inspection_section_rows_by_id(section_registry_payload)
    achieved_fidelity, section_ids, section_cost_units, degraded = _resolve_fidelity(
        desired_fidelity=str(request.get("desired_fidelity", "macro")),
        max_cost_units=_as_int(request.get("max_cost_units", 0), 0),
        section_rows=section_rows,
        micro_allowed=micro_allowed,
        micro_available=micro_available,
        strict_budget=bool(strict_budget),
    )

    quant_step = 100 if visibility_level == "diegetic" else (1 if allow_hidden_state else 10)
    include_part_ids = bool(micro_allowed and achieved_fidelity == "micro")
    redaction_level = "none" if include_part_ids else ("diegetic" if visibility_level == "diegetic" else "coarse")

    summary_sections: Dict[str, dict] = {}
    for section_id in section_ids:
        section_row = dict(section_rows.get(section_id) or {})
        summary_sections[section_id] = {
            "schema_version": "1.0.0",
            "section_id": section_id,
            "title": str(section_row.get("title", section_id)),
            "data": _build_section_data(
                section_id,
                state=state,
                target_payload=payload,
                request=request,
                quant_step=int(quant_step),
                include_part_ids=include_part_ids,
            ),
            "epistemic_redaction_level": redaction_level,
            "extensions": {
                "cost_units": max(0, _as_int((dict(section_row.get("extensions") or {})).get("cost_units", 1), 1)),
                "quantization_step": int(quant_step),
            },
        }

    epistemic_policy_id = str((dict(policy_context or {})).get("epistemic_policy_id", "")).strip() or str((dict(law_profile or {})).get("epistemic_policy_id", "")).strip() or "ep.policy.unknown"
    section_policy_id = str((dict(policy_context or {})).get("inspection_section_policy_id", "")).strip() or "section.policy.default"
    normalized_truth_hash = str(truth_hash_anchor).strip() or canonical_sha256({"truth": truth_hash_anchor})
    normalized_ledger_hash = str(ledger_hash).strip() or canonical_sha256({"ledger": ledger_hash, "target_id": request.get("target_id", "")})
    inputs_hash = canonical_sha256(
        {
            "request": dict(request),
            "truth_hash_anchor": normalized_truth_hash,
            "ledger_hash": normalized_ledger_hash,
            "target_payload_hash": canonical_sha256(payload),
            "section_ids": list(sorted(summary_sections.keys())),
            "achieved_fidelity": achieved_fidelity,
            "epistemic_policy_id": epistemic_policy_id,
            "section_policy_id": section_policy_id,
        }
    )
    snapshot_hash = canonical_sha256(
        {
            "request_id": str(request.get("request_id", "")),
            "target_id": str(request.get("target_id", "")),
            "achieved_fidelity": achieved_fidelity,
            "tick": int(_as_int(request.get("tick", 0), 0)),
            "inputs_hash": inputs_hash,
            "summary_sections": dict(summary_sections),
        }
    )
    snapshot_id = "inspect.snapshot.{}".format(snapshot_hash[:16])
    snapshot = {
        "schema_version": "1.0.0",
        "snapshot_id": snapshot_id,
        "request_id": str(request.get("request_id", "")),
        "target_id": str(request.get("target_id", "")),
        "achieved_fidelity": achieved_fidelity,
        "tick": int(_as_int(request.get("tick", 0), 0)),
        "physics_profile_id": str(physics_profile_id or ""),
        "pack_lock_hash": str(pack_lock_hash or ""),
        "cache_policy_id": str(cache_policy_id or ""),
        "truth_hash_anchor": normalized_truth_hash,
        "snapshot_hash": snapshot_hash,
        "ledger_hash": normalized_ledger_hash,
        "inputs_hash": inputs_hash,
        "summary_sections": dict(summary_sections),
        "detail_refs": ["inspection.section.{}".format(section_id) for section_id in sorted(summary_sections.keys())],
        "target_payload": payload,
        "deterministic_fingerprint": "",
        "extensions": {
            "derived_only": True,
            "requested_fidelity": str(request.get("desired_fidelity", "macro")),
            "degraded": bool(degraded or achieved_fidelity != str(request.get("desired_fidelity", "macro"))),
            "section_cost_units": int(section_cost_units),
            "max_cost_units": int(_as_int(request.get("max_cost_units", 0), 0)),
            "micro_detail_allowed": bool(micro_allowed),
            "micro_available": bool(micro_available),
            "epistemic_policy_id": epistemic_policy_id,
            "section_policy_id": section_policy_id,
            "visibility_level": visibility_level,
        },
    }
    snapshot["deterministic_fingerprint"] = canonical_sha256(dict(snapshot, deterministic_fingerprint=""))
    diagnostics = {
        "request_row": dict(request),
        "desired_fidelity": str(request.get("desired_fidelity", "macro")),
        "achieved_fidelity": achieved_fidelity,
        "degraded": bool(snapshot["extensions"].get("degraded", False)),
        "section_ids": list(sorted(summary_sections.keys())),
        "section_cost_units": int(section_cost_units),
        "micro_detail_allowed": bool(micro_allowed),
        "micro_available": bool(micro_available),
        "epistemic_policy_id": epistemic_policy_id,
        "section_policy_id": section_policy_id,
    }
    return snapshot, diagnostics
