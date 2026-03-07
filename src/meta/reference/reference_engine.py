"""META-REF0 deterministic reference evaluators for critical runtime subsystems."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from src.meta.compile import compiled_model_rows_by_id, equivalence_proof_rows_by_id
from src.meta.numeric import tolerance_abs_for_quantity
from src.models import (
    evaluate_model_bindings,
    normalize_constitutive_model_rows,
    normalize_model_binding_rows,
)
from src.physics.energy.energy_ledger_engine import (
    evaluate_energy_balance,
    normalize_energy_ledger_entry_rows,
)
from src.system import validate_boundary_invariants
from tools.xstack.compatx.canonical_json import canonical_sha256


REFERENCE_STUB_STATUS = {"ref.proc_quality_baseline", "ref.logic_eval_engine"}

_ENERGY_QUANTITY_IDS = {
    "quantity.energy_total",
    "quantity.mass_energy_total",
}

_VALID_INVARIANT_KINDS = {"mass", "energy", "momentum", "pollution", "safety"}

_TIER_RANK = {"macro": 0, "meso": 1, "micro": 2}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _rows_from_registry_payload(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
    body = _as_map(payload)
    for key in keys:
        rows = body.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    for key in keys:
        rows = record.get(key)
        if isinstance(rows, list):
            return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _tick_window(*, tick_value: int, tick_start: int | None, tick_end: int | None) -> bool:
    if tick_start is not None and int(tick_value) < int(tick_start):
        return False
    if tick_end is not None and int(tick_value) > int(tick_end):
        return False
    return True


def _energy_total(values: Mapping[str, object] | None) -> int:
    payload = _as_map(values)
    total = 0
    for key, raw in sorted(payload.items(), key=lambda item: str(item[0])):
        quantity_id = str(key or "").strip()
        if quantity_id.startswith("quantity.energy_") or quantity_id in _ENERGY_QUANTITY_IDS:
            total += int(_as_int(raw, 0))
    return int(total)


def build_reference_run_record_row(
    *,
    run_id: str,
    evaluator_id: str,
    seed: int,
    tick_range: Mapping[str, object] | None,
    runtime_output_hash: str,
    reference_output_hash: str,
    match: bool,
    discrepancy_summary: str | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "run_id": str(run_id or "").strip(),
        "evaluator_id": str(evaluator_id or "").strip(),
        "seed": int(max(0, _as_int(seed, 0))),
        "tick_range": {
            "start": int(max(0, _as_int(_as_map(tick_range).get("start", 0), 0))),
            "end": int(max(0, _as_int(_as_map(tick_range).get("end", 0), 0))),
        },
        "runtime_output_hash": str(runtime_output_hash or "").strip(),
        "reference_output_hash": str(reference_output_hash or "").strip(),
        "match": bool(match),
        "discrepancy_summary": str(discrepancy_summary or "").strip() or None,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["run_id"]) or (not payload["evaluator_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_reference_run_record_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("run_id", ""))):
        payload = build_reference_run_record_row(
            run_id=str(row.get("run_id", "")).strip(),
            evaluator_id=str(row.get("evaluator_id", "")).strip(),
            seed=_as_int(row.get("seed", 0), 0),
            tick_range=_as_map(row.get("tick_range")),
            runtime_output_hash=str(row.get("runtime_output_hash", "")).strip(),
            reference_output_hash=str(row.get("reference_output_hash", "")).strip(),
            match=bool(row.get("match", False)),
            discrepancy_summary=(None if row.get("discrepancy_summary") is None else str(row.get("discrepancy_summary", "")).strip() or None),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("run_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def reference_evaluator_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry_payload(registry_payload, ("reference_evaluators",))
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("evaluator_id", ""))):
        evaluator_id = str(row.get("evaluator_id", "")).strip()
        if evaluator_id:
            out[evaluator_id] = dict(row)
    return out


def _energy_runtime_summary(
    *,
    energy_ledger_entry_rows: object,
    tick_start: int | None,
    tick_end: int | None,
) -> dict:
    tick_map: Dict[int, dict] = {}
    entry_delta_mismatch = 0
    filtered_entries: List[dict] = []
    for row in normalize_energy_ledger_entry_rows(energy_ledger_entry_rows):
        tick_value = int(max(0, _as_int(row.get("tick", 0), 0)))
        if not _tick_window(tick_value=tick_value, tick_start=tick_start, tick_end=tick_end):
            continue
        filtered_entries.append(dict(row))
    for row in sorted(filtered_entries, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("entry_id", "")))):
        tick_value = int(max(0, _as_int(row.get("tick", 0), 0)))
        runtime = evaluate_energy_balance(
            input_values=_as_map(row.get("input_values")),
            output_values=_as_map(row.get("output_values")),
        )
        recorded_delta = int(_as_int(row.get("energy_total_delta", 0), 0))
        runtime_delta = int(_as_int(runtime.get("energy_total_delta", 0), 0))
        if recorded_delta != runtime_delta:
            entry_delta_mismatch += 1
        bucket = tick_map.setdefault(
            tick_value,
            {
                "tick": tick_value,
                "entry_count": 0,
                "input_total": 0,
                "output_total": 0,
                "recorded_delta_total": 0,
                "runtime_delta_total": 0,
            },
        )
        bucket["entry_count"] = int(bucket["entry_count"]) + 1
        bucket["input_total"] = int(bucket["input_total"]) + int(_as_int(runtime.get("input_total", 0), 0))
        bucket["output_total"] = int(bucket["output_total"]) + int(_as_int(runtime.get("output_total", 0), 0))
        bucket["recorded_delta_total"] = int(bucket["recorded_delta_total"]) + int(recorded_delta)
        bucket["runtime_delta_total"] = int(bucket["runtime_delta_total"]) + int(runtime_delta)
    per_tick = [dict(tick_map[key]) for key in sorted(tick_map.keys())]
    output_hash = canonical_sha256(per_tick)
    return {
        "per_tick": per_tick,
        "entry_count": len(filtered_entries),
        "entry_delta_mismatch": int(entry_delta_mismatch),
        "output_hash": output_hash,
    }


def _energy_reference_summary(
    *,
    energy_ledger_entry_rows: object,
    tick_start: int | None,
    tick_end: int | None,
) -> dict:
    tick_map: Dict[int, dict] = {}
    entry_delta_mismatch = 0
    filtered_entries: List[dict] = []
    for row in normalize_energy_ledger_entry_rows(energy_ledger_entry_rows):
        tick_value = int(max(0, _as_int(row.get("tick", 0), 0)))
        if not _tick_window(tick_value=tick_value, tick_start=tick_start, tick_end=tick_end):
            continue
        filtered_entries.append(dict(row))

    for row in sorted(filtered_entries, key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("entry_id", "")))):
        tick_value = int(max(0, _as_int(row.get("tick", 0), 0)))
        input_total = _energy_total(_as_map(row.get("input_values")))
        output_total = _energy_total(_as_map(row.get("output_values")))
        reference_delta = int(output_total - input_total)
        recorded_delta = int(_as_int(row.get("energy_total_delta", 0), 0))
        if reference_delta != recorded_delta:
            entry_delta_mismatch += 1
        bucket = tick_map.setdefault(
            tick_value,
            {
                "tick": tick_value,
                "entry_count": 0,
                "input_total": 0,
                "output_total": 0,
                "recorded_delta_total": 0,
                "runtime_delta_total": 0,
            },
        )
        bucket["entry_count"] = int(bucket["entry_count"]) + 1
        bucket["input_total"] = int(bucket["input_total"]) + int(input_total)
        bucket["output_total"] = int(bucket["output_total"]) + int(output_total)
        bucket["recorded_delta_total"] = int(bucket["recorded_delta_total"]) + int(recorded_delta)
        bucket["runtime_delta_total"] = int(bucket["runtime_delta_total"]) + int(reference_delta)
    per_tick = [dict(tick_map[key]) for key in sorted(tick_map.keys())]
    output_hash = canonical_sha256(per_tick)
    return {
        "per_tick": per_tick,
        "entry_count": len(filtered_entries),
        "entry_delta_mismatch": int(entry_delta_mismatch),
        "output_hash": output_hash,
    }


def evaluate_reference_energy_ledger(
    *,
    energy_ledger_entry_rows: object,
    quantity_tolerance_registry_payload: Mapping[str, object] | None,
    tick_start: int | None,
    tick_end: int | None,
) -> dict:
    runtime = _energy_runtime_summary(
        energy_ledger_entry_rows=energy_ledger_entry_rows,
        tick_start=tick_start,
        tick_end=tick_end,
    )
    reference = _energy_reference_summary(
        energy_ledger_entry_rows=energy_ledger_entry_rows,
        tick_start=tick_start,
        tick_end=tick_end,
    )

    tolerance_abs = int(
        tolerance_abs_for_quantity(
            quantity_id="quantity.energy_total",
            quantity_tolerance_registry=quantity_tolerance_registry_payload,
            default_value=0,
        )
    )
    mismatch_rows: List[str] = []
    runtime_by_tick = {int(_as_int(row.get("tick", 0), 0)): dict(row) for row in list(runtime.get("per_tick") or [])}
    reference_by_tick = {int(_as_int(row.get("tick", 0), 0)): dict(row) for row in list(reference.get("per_tick") or [])}
    all_ticks = sorted(set(runtime_by_tick.keys()) | set(reference_by_tick.keys()))
    for tick_value in all_ticks:
        runtime_row = dict(runtime_by_tick.get(tick_value) or {})
        reference_row = dict(reference_by_tick.get(tick_value) or {})
        runtime_delta = int(_as_int(runtime_row.get("runtime_delta_total", 0), 0))
        reference_delta = int(_as_int(reference_row.get("runtime_delta_total", 0), 0))
        if abs(runtime_delta - reference_delta) > int(tolerance_abs):
            mismatch_rows.append("tick={} runtime_delta={} reference_delta={} tolerance={}".format(tick_value, runtime_delta, reference_delta, int(tolerance_abs)))

    match = (
        str(runtime.get("output_hash", "")).strip() == str(reference.get("output_hash", "")).strip()
        and int(_as_int(runtime.get("entry_delta_mismatch", 0), 0)) == int(_as_int(reference.get("entry_delta_mismatch", 0), 0))
        and not mismatch_rows
    )
    return {
        "runtime": dict(runtime),
        "reference": dict(reference),
        "match": bool(match),
        "tolerance_abs": int(tolerance_abs),
        "discrepancy_summary": "" if match else (mismatch_rows[0] if mismatch_rows else "energy ledger hash mismatch"),
    }


def _tier(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in _TIER_RANK:
        return token
    return "macro"


def _coupling_runtime_summary(
    *,
    current_tick: int,
    model_rows: object,
    binding_rows: object,
    model_type_rows: Mapping[str, dict] | None,
    cache_policy_rows: Mapping[str, dict] | None,
    max_cost_units: int,
    far_target_ids: object,
    far_tick_stride: int,
) -> dict:
    evaluation = evaluate_model_bindings(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        model_rows=model_rows,
        binding_rows=binding_rows,
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=None,
        max_cost_units=int(max(0, _as_int(max_cost_units, 0))),
        far_target_ids=far_target_ids,
        far_tick_stride=int(max(1, _as_int(far_tick_stride, 1))),
    )
    processed = _sorted_tokens(list(evaluation.get("processed_binding_ids") or []))
    deferred = sorted(
        (dict(row) for row in list(evaluation.get("deferred_rows") or []) if isinstance(row, Mapping)),
        key=lambda row: (str(row.get("binding_id", "")), str(row.get("reason", ""))),
    )
    payload = {
        "processed_binding_ids": processed,
        "deferred_rows": deferred,
        "cost_units": int(_as_int(evaluation.get("cost_units", 0), 0)),
        "budget_outcome": str(evaluation.get("budget_outcome", "")).strip(),
    }
    payload["output_hash"] = canonical_sha256(payload)
    return payload


def _coupling_reference_summary(
    *,
    current_tick: int,
    model_rows: object,
    binding_rows: object,
    model_type_rows: Mapping[str, dict] | None,
    max_cost_units: int,
    far_target_ids: object,
    far_tick_stride: int,
) -> dict:
    models_by_id = dict(
        (str(row.get("model_id", "")).strip(), dict(row))
        for row in normalize_constitutive_model_rows(model_rows)
        if str(row.get("model_id", "")).strip()
    )
    bindings = normalize_model_binding_rows(binding_rows)
    type_rows = dict(model_type_rows or {})
    budget = int(max(0, _as_int(max_cost_units, 0))) or 1_000_000_000
    far_targets = set(_sorted_tokens(list(far_target_ids or [])))
    stride = int(max(1, _as_int(far_tick_stride, 1)))

    processed: List[str] = []
    deferred: List[dict] = []
    spent = 0

    ordered_bindings = sorted(
        (dict(row) for row in bindings),
        key=lambda row: (
            int(_TIER_RANK.get(str(row.get("tier", "")), 999)),
            str(row.get("model_id", "")),
            str(row.get("binding_id", "")),
        ),
    )

    for binding in ordered_bindings:
        binding_id = str(binding.get("binding_id", "")).strip()
        model_id = str(binding.get("model_id", "")).strip()
        target_id = str(binding.get("target_id", "")).strip()
        tier = _tier(binding.get("tier"))
        if not bool(binding.get("enabled", True)):
            deferred.append({"binding_id": binding_id, "reason": "disabled"})
            continue
        model_row = dict(models_by_id.get(model_id) or {})
        if not model_row:
            deferred.append({"binding_id": binding_id, "reason": "missing_model"})
            continue
        model_type_id = str(model_row.get("model_type_id", "")).strip()
        if type_rows and model_type_id not in type_rows:
            deferred.append({"binding_id": binding_id, "reason": "missing_model_type"})
            continue
        supported_tiers = set(_sorted_tokens(model_row.get("supported_tiers") or []))
        if tier not in supported_tiers:
            deferred.append({"binding_id": binding_id, "reason": "tier_not_supported"})
            continue
        if target_id in far_targets and stride > 1 and (int(current_tick) % int(stride)) != 0:
            deferred.append({"binding_id": binding_id, "reason": "degrade.far_tick_bucket"})
            continue
        cost = int(max(1, _as_int(model_row.get("cost_units", 1), 1)))
        if (spent + cost) > budget:
            deferred.append({"binding_id": binding_id, "reason": "degrade.model_budget"})
            continue
        processed.append(binding_id)
        spent += cost

    processed_sorted = _sorted_tokens(processed)
    deferred_sorted = sorted(
        (dict(row) for row in deferred if isinstance(row, Mapping)),
        key=lambda row: (str(row.get("binding_id", "")), str(row.get("reason", ""))),
    )
    payload = {
        "processed_binding_ids": processed_sorted,
        "deferred_rows": deferred_sorted,
        "cost_units": int(max(0, spent)),
        "budget_outcome": "degraded" if deferred_sorted else "complete",
    }
    payload["output_hash"] = canonical_sha256(payload)
    return payload


def evaluate_reference_coupling_scheduler(
    *,
    current_tick: int,
    model_rows: object,
    binding_rows: object,
    model_type_rows: Mapping[str, dict] | None,
    cache_policy_rows: Mapping[str, dict] | None,
    max_cost_units: int,
    far_target_ids: object,
    far_tick_stride: int,
) -> dict:
    runtime = _coupling_runtime_summary(
        current_tick=current_tick,
        model_rows=model_rows,
        binding_rows=binding_rows,
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        max_cost_units=max_cost_units,
        far_target_ids=far_target_ids,
        far_tick_stride=far_tick_stride,
    )
    reference = _coupling_reference_summary(
        current_tick=current_tick,
        model_rows=model_rows,
        binding_rows=binding_rows,
        model_type_rows=model_type_rows,
        max_cost_units=max_cost_units,
        far_target_ids=far_target_ids,
        far_tick_stride=far_tick_stride,
    )
    mismatch = []
    for key in ("processed_binding_ids", "deferred_rows", "cost_units", "budget_outcome"):
        if runtime.get(key) != reference.get(key):
            mismatch.append(str(key))
    match = not mismatch
    return {
        "runtime": runtime,
        "reference": reference,
        "match": bool(match),
        "discrepancy_summary": "" if match else "coupling scheduler mismatch: {}".format(",".join(mismatch)),
    }


def _system_rows_by_id(rows: object) -> Dict[str, dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("system_id", ""))):
        system_id = str(row.get("system_id", "")).strip()
        if system_id:
            out[system_id] = dict(row)
    return out


def _invariant_rows_by_id(rows: object) -> Dict[str, dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("invariant_id", ""))):
        invariant_id = str(row.get("invariant_id", "")).strip()
        if invariant_id:
            out[invariant_id] = dict(row)
    return out


def _check_projection(checks: object) -> List[dict]:
    rows = [
        {
            "check_id": str(dict(item).get("check_id", "")).strip(),
            "status": str(dict(item).get("status", "")).strip(),
        }
        for item in list(checks or [])
        if isinstance(item, Mapping)
    ]
    return sorted(
        (row for row in rows if row["check_id"]),
        key=lambda row: str(row.get("check_id", "")),
    )


def _runtime_invariant_summary(
    *,
    system_id: str,
    system_rows: object,
    boundary_invariant_rows: object,
    boundary_invariant_template_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    safety_pattern_registry_payload: Mapping[str, object] | None,
) -> dict:
    result = validate_boundary_invariants(
        system_id=str(system_id or "").strip(),
        system_rows=system_rows,
        boundary_invariant_rows=boundary_invariant_rows,
        boundary_invariant_template_registry_payload=boundary_invariant_template_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        safety_pattern_registry_payload=safety_pattern_registry_payload,
    )
    projection = _check_projection(result.get("checks"))
    payload = {
        "result": str(result.get("result", "")).strip(),
        "reason_code": str(result.get("reason_code", "")).strip(),
        "checks": projection,
        "failed_check_ids": [
            str(row.get("check_id", "")).strip()
            for row in projection
            if str(row.get("status", "")).strip() != "pass"
        ],
    }
    payload["output_hash"] = canonical_sha256(payload)
    return payload


def _reference_invariant_summary(
    *,
    system_id: str,
    system_rows: object,
    boundary_invariant_rows: object,
    boundary_invariant_template_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    safety_pattern_registry_payload: Mapping[str, object] | None,
) -> dict:
    checks: List[dict] = []
    system_token = str(system_id or "").strip()
    systems = _system_rows_by_id(system_rows)
    system_row = dict(systems.get(system_token) or {})
    checks.append({"check_id": "invariant.system.present", "status": "pass" if bool(system_row) else "fail"})
    if not system_row:
        payload = {
            "result": "refused",
            "reason_code": "refusal.system.invariant_violation",
            "checks": _check_projection(checks),
        }
        payload["failed_check_ids"] = [
            str(row.get("check_id", "")).strip()
            for row in payload["checks"]
            if str(row.get("status", "")).strip() != "pass"
        ]
        payload["output_hash"] = canonical_sha256(payload)
        return payload

    tolerance_ids = set(
        _sorted_tokens(
            str(row.get("tolerance_policy_id", "")).strip()
            for row in _rows_from_registry_payload(tolerance_policy_registry_payload, ("tolerance_policies",))
        )
    )
    invariant_by_id = _invariant_rows_by_id(boundary_invariant_rows)
    invariant_ids = _sorted_tokens(system_row.get("boundary_invariant_ids") or [])
    checks.append({"check_id": "invariant.ids.present", "status": "pass" if bool(invariant_ids) else "fail"})
    for invariant_id in invariant_ids:
        row = dict(invariant_by_id.get(invariant_id) or {})
        kind = str(row.get("invariant_kind", "")).strip().lower()
        tolerance_policy_id = str(row.get("tolerance_policy_id", "")).strip()
        checks.append({"check_id": "invariant.row.present.{}".format(invariant_id), "status": "pass" if bool(row) else "fail"})
        checks.append({"check_id": "invariant.kind.valid.{}".format(invariant_id), "status": "pass" if kind in _VALID_INVARIANT_KINDS else "fail"})
        checks.append({"check_id": "invariant.tolerance.registered.{}".format(invariant_id), "status": "pass" if tolerance_policy_id in tolerance_ids else "fail"})
        checks.append({"check_id": "invariant.boundary_flux_allowed.typed.{}".format(invariant_id), "status": "pass" if isinstance(row.get("boundary_flux_allowed"), bool) else "fail"})
        checks.append({"check_id": "invariant.ledger_transform_required.typed.{}".format(invariant_id), "status": "pass" if isinstance(row.get("ledger_transform_required"), bool) else "fail"})
        if kind == "energy":
            checks.append(
                {
                    "check_id": "invariant.energy.requires_ledger.{}".format(invariant_id),
                    "status": "pass" if bool(row.get("ledger_transform_required", False)) else "fail",
                }
            )

    templates_by_id: Dict[str, dict] = {}
    for row in _rows_from_registry_payload(
        boundary_invariant_template_registry_payload,
        ("boundary_invariant_templates",),
    ):
        template_id = str(dict(row).get("boundary_invariant_template_id", "")).strip()
        if template_id:
            templates_by_id[template_id] = dict(row)
    template_ids = _sorted_tokens(_as_map(system_row.get("extensions")).get("boundary_invariant_template_ids") or [])
    checks.append({"check_id": "invariant.templates.declared", "status": "pass" if bool(template_ids) else "fail"})

    required_safety_pattern_ids: List[str] = []
    for template_id in template_ids:
        template_row = dict(templates_by_id.get(template_id) or {})
        checks.append({"check_id": "invariant.template.present.{}".format(template_id), "status": "pass" if bool(template_row) else "fail"})
        for required_invariant in _sorted_tokens(template_row.get("required_invariants") or []):
            checks.append(
                {
                    "check_id": "invariant.template.required.{}.{}".format(template_id, required_invariant),
                    "status": "pass" if required_invariant in set(invariant_ids) else "fail",
                }
            )
        required_safety_pattern_ids.extend(_sorted_tokens(template_row.get("required_safety_pattern_ids") or []))

    safety_ids = set(
        _sorted_tokens(
            str(row.get("pattern_id", "")).strip()
            for row in _rows_from_registry_payload(safety_pattern_registry_payload, ("safety_patterns",))
        )
    )
    safety_pattern_ids = _sorted_tokens(_as_map(system_row.get("extensions")).get("safety_pattern_ids") or [])
    for pattern_id in _sorted_tokens(required_safety_pattern_ids):
        checks.append(
            {
                "check_id": "invariant.required_safety_pattern.registered.{}".format(pattern_id),
                "status": "pass" if pattern_id in safety_ids else "fail",
            }
        )
        checks.append(
            {
                "check_id": "invariant.required_safety_pattern.present.{}".format(pattern_id),
                "status": "pass" if pattern_id in set(safety_pattern_ids) else "fail",
            }
        )

    system_ext = _as_map(system_row.get("extensions"))
    if bool(system_ext.get("emits_pollutants", False)):
        has_pollution = False
        for invariant_id in invariant_ids:
            row = dict(invariant_by_id.get(invariant_id) or {})
            if str(row.get("invariant_kind", "")).strip().lower() == "pollution" or invariant_id == "invariant.pollutant_accounted":
                has_pollution = True
                break
        checks.append(
            {
                "check_id": "invariant.pollution_accounting.required",
                "status": "pass" if has_pollution else "fail",
            }
        )

    projection = _check_projection(checks)
    failed = [row for row in projection if str(row.get("status", "")).strip() != "pass"]
    payload = {
        "result": "complete" if not failed else "refused",
        "reason_code": "" if not failed else "refusal.system.invariant_violation",
        "checks": projection,
        "failed_check_ids": [str(row.get("check_id", "")).strip() for row in failed],
    }
    payload["output_hash"] = canonical_sha256(payload)
    return payload


def evaluate_reference_system_invariant_check(
    *,
    system_id: str,
    system_rows: object,
    boundary_invariant_rows: object,
    boundary_invariant_template_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    safety_pattern_registry_payload: Mapping[str, object] | None,
) -> dict:
    runtime = _runtime_invariant_summary(
        system_id=system_id,
        system_rows=system_rows,
        boundary_invariant_rows=boundary_invariant_rows,
        boundary_invariant_template_registry_payload=boundary_invariant_template_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        safety_pattern_registry_payload=safety_pattern_registry_payload,
    )
    reference = _reference_invariant_summary(
        system_id=system_id,
        system_rows=system_rows,
        boundary_invariant_rows=boundary_invariant_rows,
        boundary_invariant_template_registry_payload=boundary_invariant_template_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        safety_pattern_registry_payload=safety_pattern_registry_payload,
    )
    mismatch = []
    for key in ("result", "reason_code", "checks", "failed_check_ids"):
        if runtime.get(key) != reference.get(key):
            mismatch.append(str(key))
    match = not mismatch
    return {
        "runtime": runtime,
        "reference": reference,
        "match": bool(match),
        "discrepancy_summary": "" if match else "system invariant mismatch: {}".format(",".join(mismatch)),
    }


def evaluate_reference_compiled_model_verify(
    *,
    compiled_model_id: str,
    compiled_model_rows: object,
    equivalence_proof_rows: object,
) -> dict:
    model_id = str(compiled_model_id or "").strip()
    model_row = dict(compiled_model_rows_by_id(compiled_model_rows).get(model_id) or {})
    proof_ref = str(model_row.get("equivalence_proof_ref", "")).strip()
    proof_row = dict(equivalence_proof_rows_by_id(equivalence_proof_rows).get(proof_ref) or {})

    runtime_hash = str(proof_row.get("proof_hash", "")).strip()
    payload_ref = _as_map(model_row.get("compiled_payload_ref"))
    payload_hash = str(payload_ref.get("payload_hash", "")).strip() or canonical_sha256(_as_map(payload_ref.get("payload")))
    source_hash = str(model_row.get("source_hash", "")).strip()
    proof_kind = str(proof_row.get("proof_kind", "")).strip()
    verifier = str(proof_row.get("verification_procedure_id", "")).strip()
    error_policy = (
        None if proof_row.get("error_bound_policy_id") is None else str(proof_row.get("error_bound_policy_id", "")).strip() or None
    )
    reference_hash = canonical_sha256(
        {
            "source_hash": source_hash,
            "compiled_payload_hash": payload_hash,
            "proof_kind": proof_kind,
            "verification_procedure_id": verifier,
            "error_bound_policy_id": error_policy,
        }
    )

    match = bool(runtime_hash and runtime_hash == reference_hash)
    discrepancy = "" if match else "compiled proof hash mismatch"
    return {
        "runtime": {
            "compiled_model_id": model_id,
            "equivalence_proof_ref": proof_ref,
            "proof_hash": runtime_hash,
            "output_hash": canonical_sha256({"proof_hash": runtime_hash, "proof_ref": proof_ref}),
        },
        "reference": {
            "compiled_model_id": model_id,
            "equivalence_proof_ref": proof_ref,
            "proof_hash": reference_hash,
            "output_hash": canonical_sha256({"proof_hash": reference_hash, "proof_ref": proof_ref}),
        },
        "match": bool(match),
        "discrepancy_summary": discrepancy,
    }


def evaluate_reference_evaluator(
    *,
    evaluator_id: str,
    state_payload: Mapping[str, object] | None,
    current_tick: int,
    seed: int,
    tick_start: int | None = None,
    tick_end: int | None = None,
    config: Mapping[str, object] | None = None,
) -> dict:
    state = _as_map(state_payload)
    cfg = _as_map(config)
    evaluator_token = str(evaluator_id or "").strip()

    runtime_output_hash = ""
    reference_output_hash = ""
    match = False
    discrepancy_summary = ""
    runtime_out = {}
    reference_out = {}

    if evaluator_token in REFERENCE_STUB_STATUS:
        runtime_output_hash = canonical_sha256({"evaluator_id": evaluator_token, "stub": True})
        reference_output_hash = str(runtime_output_hash)
        match = True
        discrepancy_summary = ""
        runtime_out = {"status": "stub", "evaluator_id": evaluator_token}
        reference_out = {"status": "stub", "evaluator_id": evaluator_token}
    elif evaluator_token == "ref.energy_ledger":
        report = evaluate_reference_energy_ledger(
            energy_ledger_entry_rows=state.get("energy_ledger_entries")
            or _as_map(state.get("record")).get("energy_ledger_entries")
            or [],
            quantity_tolerance_registry_payload=cfg.get("quantity_tolerance_registry_payload")
            or state.get("quantity_tolerance_registry_payload")
            or {},
            tick_start=tick_start,
            tick_end=tick_end,
        )
        runtime_out = dict(report.get("runtime") or {})
        reference_out = dict(report.get("reference") or {})
        runtime_output_hash = str(runtime_out.get("output_hash", "")).strip()
        reference_output_hash = str(reference_out.get("output_hash", "")).strip()
        match = bool(report.get("match", False))
        discrepancy_summary = str(report.get("discrepancy_summary", "")).strip()
    elif evaluator_token == "ref.coupling_scheduler":
        report = evaluate_reference_coupling_scheduler(
            current_tick=int(max(0, _as_int(current_tick, 0))),
            model_rows=cfg.get("model_rows")
            or state.get("model_rows")
            or state.get("constitutive_model_rows")
            or _as_map(state.get("record")).get("model_rows")
            or [],
            binding_rows=cfg.get("binding_rows")
            or state.get("model_binding_rows")
            or state.get("model_bindings")
            or _as_map(state.get("record")).get("model_binding_rows")
            or [],
            model_type_rows=_as_map(cfg.get("model_type_rows") or state.get("model_type_rows") or {}),
            cache_policy_rows=_as_map(cfg.get("cache_policy_rows") or state.get("cache_policy_rows") or {}),
            max_cost_units=int(max(0, _as_int(cfg.get("max_cost_units", state.get("max_cost_units", 0)), 0))),
            far_target_ids=cfg.get("far_target_ids") or state.get("far_target_ids") or [],
            far_tick_stride=int(max(1, _as_int(cfg.get("far_tick_stride", state.get("far_tick_stride", 1)), 1))),
        )
        runtime_out = dict(report.get("runtime") or {})
        reference_out = dict(report.get("reference") or {})
        runtime_output_hash = str(runtime_out.get("output_hash", "")).strip()
        reference_output_hash = str(reference_out.get("output_hash", "")).strip()
        match = bool(report.get("match", False))
        discrepancy_summary = str(report.get("discrepancy_summary", "")).strip()
    elif evaluator_token == "ref.system_invariant_check":
        system_id = str(cfg.get("system_id") or state.get("system_id") or "").strip()
        if not system_id:
            systems = _system_rows_by_id(state.get("system_rows") or [])
            if systems:
                system_id = sorted(systems.keys())[0]
        report = evaluate_reference_system_invariant_check(
            system_id=system_id,
            system_rows=state.get("system_rows") or [],
            boundary_invariant_rows=state.get("system_boundary_invariant_rows")
            or state.get("boundary_invariant_rows")
            or [],
            boundary_invariant_template_registry_payload=cfg.get("boundary_invariant_template_registry_payload")
            or state.get("boundary_invariant_template_registry_payload")
            or state.get("boundary_invariant_template_registry")
            or {},
            tolerance_policy_registry_payload=cfg.get("tolerance_policy_registry_payload")
            or state.get("tolerance_policy_registry_payload")
            or {},
            safety_pattern_registry_payload=cfg.get("safety_pattern_registry_payload")
            or state.get("safety_pattern_registry_payload")
            or {},
        )
        runtime_out = dict(report.get("runtime") or {})
        reference_out = dict(report.get("reference") or {})
        runtime_output_hash = str(runtime_out.get("output_hash", "")).strip()
        reference_output_hash = str(reference_out.get("output_hash", "")).strip()
        match = bool(report.get("match", False))
        discrepancy_summary = str(report.get("discrepancy_summary", "")).strip()
    elif evaluator_token == "ref.compiled_model_verify":
        model_id = str(cfg.get("compiled_model_id") or state.get("compiled_model_id") or "").strip()
        if not model_id:
            rows_by_id = compiled_model_rows_by_id(state.get("compiled_model_rows") or [])
            if rows_by_id:
                model_id = sorted(rows_by_id.keys())[0]
        report = evaluate_reference_compiled_model_verify(
            compiled_model_id=model_id,
            compiled_model_rows=state.get("compiled_model_rows") or [],
            equivalence_proof_rows=state.get("equivalence_proof_rows") or [],
        )
        runtime_out = dict(report.get("runtime") or {})
        reference_out = dict(report.get("reference") or {})
        runtime_output_hash = str(runtime_out.get("output_hash", "")).strip()
        reference_output_hash = str(reference_out.get("output_hash", "")).strip()
        match = bool(report.get("match", False))
        discrepancy_summary = str(report.get("discrepancy_summary", "")).strip()
    else:
        runtime_output_hash = canonical_sha256({"evaluator_id": evaluator_token, "runtime": "unknown"})
        reference_output_hash = canonical_sha256({"evaluator_id": evaluator_token, "reference": "unknown"})
        match = False
        discrepancy_summary = "unknown evaluator_id"
        runtime_out = {"reason_code": "refusal.reference.unknown_evaluator"}
        reference_out = {"reason_code": "refusal.reference.unknown_evaluator"}

    tick_min = int(max(0, _as_int(0 if tick_start is None else tick_start, 0)))
    tick_max = int(max(tick_min, _as_int(tick_min if tick_end is None else tick_end, tick_min)))
    run_id = "reference_run.{}".format(
        canonical_sha256(
            {
                "evaluator_id": evaluator_token,
                "seed": int(max(0, _as_int(seed, 0))),
                "tick_range": {"start": tick_min, "end": tick_max},
                "runtime_output_hash": runtime_output_hash,
                "reference_output_hash": reference_output_hash,
            }
        )[:16]
    )
    run_record = build_reference_run_record_row(
        run_id=run_id,
        evaluator_id=evaluator_token,
        seed=int(max(0, _as_int(seed, 0))),
        tick_range={"start": tick_min, "end": tick_max},
        runtime_output_hash=runtime_output_hash,
        reference_output_hash=reference_output_hash,
        match=bool(match),
        discrepancy_summary=discrepancy_summary or None,
        deterministic_fingerprint="",
        extensions={
            "runtime_output": runtime_out,
            "reference_output": reference_out,
            "current_tick": int(max(0, _as_int(current_tick, 0))),
        },
    )
    return {
        "result": "complete" if bool(match) else "violation",
        "evaluator_id": evaluator_token,
        "run_record": run_record,
        "runtime_output": runtime_out,
        "reference_output": reference_out,
        "match": bool(match),
        "discrepancy_summary": discrepancy_summary,
        "deterministic_fingerprint": str(run_record.get("deterministic_fingerprint", "")).strip(),
    }


def evaluate_reference_suite(
    *,
    evaluator_ids: Iterable[str],
    state_payload: Mapping[str, object] | None,
    current_tick: int,
    seed: int,
    tick_start: int | None,
    tick_end: int | None,
    configs_by_evaluator_id: Mapping[str, object] | None = None,
) -> dict:
    configs = _as_map(configs_by_evaluator_id)
    evaluations = []
    run_rows = []
    mismatches = []
    for evaluator_id in sorted(_sorted_tokens(evaluator_ids)):
        eval_row = evaluate_reference_evaluator(
            evaluator_id=evaluator_id,
            state_payload=state_payload,
            current_tick=int(max(0, _as_int(current_tick, 0))),
            seed=int(max(0, _as_int(seed, 0))),
            tick_start=tick_start,
            tick_end=tick_end,
            config=_as_map(configs.get(evaluator_id)),
        )
        evaluations.append(dict(eval_row))
        run_row = dict(eval_row.get("run_record") or {})
        if run_row:
            run_rows.append(run_row)
        if not bool(eval_row.get("match", False)):
            mismatches.append(
                {
                    "evaluator_id": evaluator_id,
                    "run_id": str(run_row.get("run_id", "")).strip(),
                    "discrepancy_summary": str(eval_row.get("discrepancy_summary", "")).strip(),
                }
            )
    run_rows = normalize_reference_run_record_rows(run_rows)
    return {
        "result": "complete" if not mismatches else "violation",
        "evaluations": evaluations,
        "reference_run_record_rows": run_rows,
        "mismatches": mismatches,
        "deterministic_fingerprint": canonical_sha256(
            {
                "reference_run_record_rows": run_rows,
                "mismatches": mismatches,
            }
        ),
    }


__all__ = [
    "REFERENCE_STUB_STATUS",
    "build_reference_run_record_row",
    "normalize_reference_run_record_rows",
    "reference_evaluator_rows_by_id",
    "evaluate_reference_energy_ledger",
    "evaluate_reference_coupling_scheduler",
    "evaluate_reference_system_invariant_check",
    "evaluate_reference_compiled_model_verify",
    "evaluate_reference_evaluator",
    "evaluate_reference_suite",
]
