"""Deterministic MAT-6 decay/failure/maintenance helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.materials.dimension_engine import fixed_point_config_from_policy
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_MAINTENANCE_MATERIALS_MISSING = "refusal.maintenance.materials_missing"
REFUSAL_MAINTENANCE_FORBIDDEN_BY_LAW = "refusal.maintenance.forbidden_by_law"


class MaintenanceError(ValueError):
    """Deterministic maintenance refusal."""

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
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _registry_rows(payload: Mapping[str, object] | None, list_key: str) -> List[dict]:
    root = dict(payload or {})
    rows = root.get(list_key)
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get(list_key)
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, dict)]


def failure_mode_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _registry_rows(registry_payload, "failure_modes")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("failure_mode_id", ""))):
        mode_id = str(row.get("failure_mode_id", "")).strip()
        if not mode_id:
            continue
        out[mode_id] = {
            "failure_mode_id": mode_id,
            "description": str(row.get("description", "")).strip(),
            "applies_to_part_classes": _sorted_unique_strings(row.get("applies_to_part_classes")),
            "hazard_inputs": _sorted_unique_strings(row.get("hazard_inputs")),
            "base_hazard_rate_per_tick": max(0, _as_int(row.get("base_hazard_rate_per_tick", 0), 0)),
            "modifiers": dict(row.get("modifiers") or {}) if isinstance(row.get("modifiers"), dict) else {},
            "failure_event_type_id": str(row.get("failure_event_type_id", "")).strip() or "event.failure.triggered",
            "maintenance_effect_model_id": str(row.get("maintenance_effect_model_id", "")).strip() or "maint.effect.partial_reset",
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def maintenance_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _registry_rows(registry_payload, "policies")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("maintenance_policy_id", ""))):
        policy_id = str(row.get("maintenance_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "maintenance_policy_id": policy_id,
            "description": str(row.get("description", "")).strip(),
            "inspection_interval_ticks": max(0, _as_int(row.get("inspection_interval_ticks", 0), 0)),
            "maintenance_interval_ticks": max(0, _as_int(row.get("maintenance_interval_ticks", 0), 0)),
            "backlog_growth_rule_id": str(row.get("backlog_growth_rule_id", "")).strip() or "backlog.linear_stub",
            "max_backlog": max(0, _as_int(row.get("max_backlog", 0), 0)),
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def backlog_growth_rule_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _registry_rows(registry_payload, "rules")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("rule_id", ""))):
        rule_id = str(row.get("rule_id", "")).strip()
        if not rule_id:
            continue
        model_kind = str(row.get("model_kind", "linear")).strip() or "linear"
        if model_kind not in ("linear", "stepwise", "none"):
            model_kind = "linear"
        thresholds = sorted(
            [
                {
                    "at_backlog": max(0, _as_int(item.get("at_backlog", 0), 0)),
                    "increment_per_tick": max(0, _as_int(item.get("increment_per_tick", 0), 0)),
                }
                for item in list(row.get("thresholds") or [])
                if isinstance(item, dict)
            ],
            key=lambda item: (int(item.get("at_backlog", 0)), int(item.get("increment_per_tick", 0))),
        )
        out[rule_id] = {
            "rule_id": rule_id,
            "description": str(row.get("description", "")).strip(),
            "model_kind": model_kind,
            "base_increment_per_tick": max(0, _as_int(row.get("base_increment_per_tick", 0), 0)),
            "thresholds": thresholds,
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def normalize_asset_health_state(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    asset_id = str(payload.get("asset_id", "")).strip()
    if not asset_id:
        raise MaintenanceError("refusal.maintenance.asset_missing", "asset health state missing asset_id", {})
    wear = {}
    for key in sorted((dict(payload.get("accumulated_wear") or {})).keys()):
        mode_id = str(key).strip()
        if mode_id:
            wear[mode_id] = max(0, _as_int((dict(payload.get("accumulated_wear") or {})).get(key, 0), 0))
    return {
        "schema_version": "1.0.0",
        "asset_id": asset_id,
        "failure_mode_ids": _sorted_unique_strings(payload.get("failure_mode_ids")),
        "accumulated_wear": wear,
        "hazard_state": dict(payload.get("hazard_state") or {}) if isinstance(payload.get("hazard_state"), dict) else {},
        "maintenance_backlog": max(0, _as_int(payload.get("maintenance_backlog", 0), 0)),
        "last_inspection_tick": max(0, _as_int(payload.get("last_inspection_tick", 0), 0)),
        "last_maintenance_tick": max(0, _as_int(payload.get("last_maintenance_tick", 0), 0)),
        "extensions": dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), dict) else {},
    }


def _asset_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("asset_id", ""))):
        normalized = normalize_asset_health_state(row)
        out[str(normalized.get("asset_id", ""))] = normalized
    return out


def _commitment_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("commitment_id", ""))):
        commitment_id = str(row.get("commitment_id", "")).strip()
        if not commitment_id:
            continue
        out[commitment_id] = {
            "schema_version": "1.0.0",
            "commitment_id": commitment_id,
            "asset_id": str(row.get("asset_id", "")).strip(),
            "maintenance_policy_id": str(row.get("maintenance_policy_id", "")).strip(),
            "commitment_kind": str(row.get("commitment_kind", "")).strip(),
            "scheduled_tick": max(0, _as_int(row.get("scheduled_tick", 0), 0)),
            "status": str(row.get("status", "planned")).strip() or "planned",
            "actor_subject_id": str(row.get("actor_subject_id", "")).strip() or "subject.system",
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        }
    return out


def _provenance_event(*, event_type_id: str, tick: int, asset_id: str, actor_subject_id: str, sequence: int, extensions: Mapping[str, object] | None = None, ledger_deltas: Mapping[str, object] | None = None) -> dict:
    event_id = "provenance.event.{}".format(
        canonical_sha256(
            {
                "event_type_id": str(event_type_id),
                "tick": int(max(0, int(tick))),
                "asset_id": str(asset_id),
                "sequence": int(max(0, int(sequence))),
            }
        )[:24]
    )
    row = {
        "schema_version": "1.0.0",
        "event_id": event_id,
        "tick": int(max(0, int(tick))),
        "event_type_id": str(event_type_id),
        "actor_subject_id": str(actor_subject_id).strip() or "subject.system",
        "site_ref": "asset:{}".format(str(asset_id)),
        "inputs": [],
        "outputs": [],
        "ledger_deltas": dict((str(key).strip(), _as_int(value, 0)) for key, value in sorted((dict(ledger_deltas or {})).items(), key=lambda item: str(item[0])) if str(key).strip()),
        "linked_project_id": None,
        "linked_step_id": None,
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    seed = dict(row)
    seed["deterministic_fingerprint"] = ""
    row["deterministic_fingerprint"] = canonical_sha256(seed)
    return row


def _failure_event(*, tick: int, asset_id: str, failure_mode_id: str, severity: int, consequences: Mapping[str, object], provenance_event_id: str, sequence: int) -> dict:
    event_id = "failure.event.{}".format(
        canonical_sha256(
            {
                "tick": int(max(0, int(tick))),
                "asset_id": str(asset_id),
                "failure_mode_id": str(failure_mode_id),
                "severity": int(max(0, int(severity))),
                "sequence": int(max(0, int(sequence))),
            }
        )[:24]
    )
    row = {
        "schema_version": "1.0.0",
        "event_id": event_id,
        "tick": int(max(0, int(tick))),
        "asset_id": str(asset_id),
        "failure_mode_id": str(failure_mode_id),
        "severity": int(max(0, int(severity))),
        "consequences": dict(consequences or {}),
        "provenance_event_id": str(provenance_event_id),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    seed = dict(row)
    seed["deterministic_fingerprint"] = ""
    row["deterministic_fingerprint"] = canonical_sha256(seed)
    return row


def _growth_increment(rule_row: Mapping[str, object], backlog: int, dt_ticks: int) -> int:
    kind = str((dict(rule_row or {})).get("model_kind", "linear")).strip() or "linear"
    base = max(0, _as_int((dict(rule_row or {})).get("base_increment_per_tick", 0), 0))
    if kind == "none":
        return 0
    out = int(base * max(0, int(dt_ticks)))
    if kind != "stepwise":
        return out
    for threshold in sorted((item for item in list((dict(rule_row or {})).get("thresholds") or []) if isinstance(item, dict)), key=lambda item: _as_int(item.get("at_backlog", 0), 0)):
        if int(backlog) < int(max(0, _as_int(threshold.get("at_backlog", 0), 0))):
            continue
        out += int(max(0, _as_int(threshold.get("increment_per_tick", 0), 0)) * max(0, int(dt_ticks)))
    return int(max(0, out))


def _resolve_policy(policy_rows: Mapping[str, object], requested_policy_id: str) -> dict:
    token = str(requested_policy_id).strip()
    if token and token in set(policy_rows.keys()):
        return dict(policy_rows[token])
    if "maint.policy.default_realistic" in set(policy_rows.keys()):
        return dict(policy_rows["maint.policy.default_realistic"])
    if policy_rows:
        return dict(policy_rows[sorted(policy_rows.keys())[0]])
    return {"maintenance_policy_id": "maint.policy.default_realistic", "inspection_interval_ticks": 0, "maintenance_interval_ticks": 0, "backlog_growth_rule_id": "backlog.linear_stub", "max_backlog": 0, "extensions": {}}


def _commitment_id(asset_id: str, commitment_kind: str, scheduled_tick: int, maintenance_policy_id: str) -> str:
    return "commitment.maintenance.{}".format(
        canonical_sha256(
            {
                "asset_id": str(asset_id),
                "commitment_kind": str(commitment_kind),
                "scheduled_tick": int(max(0, int(scheduled_tick))),
                "maintenance_policy_id": str(maintenance_policy_id),
            }
        )[:20]
    )


def schedule_maintenance_commitments(*, asset_health_states: object, maintenance_commitments: object, current_tick: int, actor_subject_id: str, maintenance_policy_registry: Mapping[str, object] | None, backlog_growth_rule_registry: Mapping[str, object] | None, maintenance_policy_id: str = "", asset_id: str = "", event_sequence_start: int = 0) -> dict:
    del backlog_growth_rule_registry
    assets = _asset_rows_by_id(asset_health_states)
    commitments = _commitment_rows_by_id(maintenance_commitments)
    policies = maintenance_policy_rows_by_id(maintenance_policy_registry)
    sequence = int(max(0, _as_int(event_sequence_start, 0)))
    events: List[dict] = []
    target_assets = sorted(assets.keys())
    if str(asset_id).strip():
        token = str(asset_id).strip()
        target_assets = [token] if token in set(assets.keys()) else []
    for asset_key in target_assets:
        row = dict(assets[asset_key])
        policy = _resolve_policy(policies, str(maintenance_policy_id).strip() or str((dict(row.get("extensions") or {})).get("maintenance_policy_id", "")))
        policy_id = str(policy.get("maintenance_policy_id", "")).strip()
        for commitment_kind, interval, last_tick in (
            ("inspection_due", max(0, _as_int(policy.get("inspection_interval_ticks", 0), 0)), max(0, _as_int(row.get("last_inspection_tick", 0), 0))),
            ("maintenance_due", max(0, _as_int(policy.get("maintenance_interval_ticks", 0), 0)), max(0, _as_int(row.get("last_maintenance_tick", 0), 0))),
        ):
            if interval <= 0:
                continue
            scheduled_tick = int(last_tick + interval)
            if scheduled_tick > int(current_tick):
                continue
            commitment_id = _commitment_id(asset_key, commitment_kind, scheduled_tick, policy_id)
            if commitment_id in set(commitments.keys()):
                continue
            commitments[commitment_id] = {
                "schema_version": "1.0.0",
                "commitment_id": commitment_id,
                "asset_id": asset_key,
                "maintenance_policy_id": policy_id,
                "commitment_kind": commitment_kind,
                "scheduled_tick": int(scheduled_tick),
                "status": "planned",
                "actor_subject_id": str(actor_subject_id).strip() or "subject.system",
                "extensions": {},
            }
            events.append(_provenance_event(event_type_id="event.maintenance_scheduled", tick=int(current_tick), asset_id=asset_key, actor_subject_id=str(actor_subject_id), sequence=sequence, extensions={"commitment_id": commitment_id, "maintenance_policy_id": policy_id, "commitment_kind": commitment_kind}))
            sequence += 1
    return {"asset_health_states": [dict(assets[key]) for key in sorted(assets.keys())], "maintenance_commitments": [dict(commitments[key]) for key in sorted(commitments.keys())], "provenance_events": sorted(events, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", "")))), "next_event_sequence": int(sequence)}


def perform_inspection(*, asset_health_states: object, maintenance_commitments: object, current_tick: int, asset_id: str, actor_subject_id: str, event_sequence_start: int = 0) -> dict:
    assets = _asset_rows_by_id(asset_health_states)
    commitments = _commitment_rows_by_id(maintenance_commitments)
    token = str(asset_id).strip()
    if token not in set(assets.keys()):
        raise MaintenanceError("refusal.maintenance.asset_missing", "inspection target asset is missing", {"asset_id": token})
    row = dict(assets[token])
    row["last_inspection_tick"] = int(max(0, int(current_tick)))
    hazard_state = dict(row.get("hazard_state") or {})
    hazard_state["inspection_confidence_permille"] = 1000
    hazard_state["last_inspection_tick"] = int(max(0, int(current_tick)))
    row["hazard_state"] = hazard_state
    assets[token] = row
    for commitment_id in sorted(commitments.keys()):
        commitment = dict(commitments[commitment_id])
        if str(commitment.get("asset_id", "")).strip() != token:
            continue
        if str(commitment.get("commitment_kind", "")).strip() != "inspection_due":
            continue
        if int(_as_int(commitment.get("scheduled_tick", 0), 0)) > int(current_tick):
            continue
        if str(commitment.get("status", "")).strip() in ("completed", "failed"):
            continue
        commitment["status"] = "completed"
        commitments[commitment_id] = commitment
    event = _provenance_event(event_type_id="event.inspection_performed", tick=int(current_tick), asset_id=token, actor_subject_id=str(actor_subject_id), sequence=int(max(0, _as_int(event_sequence_start, 0))), extensions={"asset_id": token})
    return {"asset_health_states": [dict(assets[key]) for key in sorted(assets.keys())], "maintenance_commitments": [dict(commitments[key]) for key in sorted(commitments.keys())], "provenance_events": [event], "next_event_sequence": int(max(0, _as_int(event_sequence_start, 0)) + 1)}


def perform_maintenance(*, asset_health_states: object, maintenance_commitments: object, current_tick: int, asset_id: str, actor_subject_id: str, available_materials: Mapping[str, object] | None = None, required_materials: Mapping[str, object] | None = None, reset_fraction_numerator: int = 1, reset_fraction_denominator: int = 2, event_sequence_start: int = 0) -> dict:
    assets = _asset_rows_by_id(asset_health_states)
    commitments = _commitment_rows_by_id(maintenance_commitments)
    token = str(asset_id).strip()
    if token not in set(assets.keys()):
        raise MaintenanceError("refusal.maintenance.asset_missing", "maintenance target asset is missing", {"asset_id": token})
    required = dict(required_materials or {})
    available = dict(available_materials or {})
    for key in sorted(required.keys()):
        material_id = str(key).strip()
        if not material_id:
            continue
        required_mass = max(0, _as_int(required.get(key, 0), 0))
        available_mass = max(0, _as_int(available.get(material_id, 0), 0))
        if required_mass > available_mass:
            raise MaintenanceError(REFUSAL_MAINTENANCE_MATERIALS_MISSING, "maintenance materials are missing", {"asset_id": token, "material_id": material_id, "required_mass": required_mass, "available_mass": available_mass})
    row = dict(assets[token])
    backlog_before = int(max(0, _as_int(row.get("maintenance_backlog", 0), 0)))
    row["last_maintenance_tick"] = int(max(0, int(current_tick)))
    row["maintenance_backlog"] = 0
    numerator = max(0, int(reset_fraction_numerator))
    denominator = max(1, int(reset_fraction_denominator))
    wear = dict(row.get("accumulated_wear") or {})
    reduced_wear = {}
    for mode_id in sorted(wear.keys()):
        value = max(0, _as_int(wear.get(mode_id, 0), 0))
        reduced_wear[mode_id] = max(0, int(value - ((value * numerator) // denominator)))
    row["accumulated_wear"] = reduced_wear
    assets[token] = row
    for commitment_id in sorted(commitments.keys()):
        commitment = dict(commitments[commitment_id])
        if str(commitment.get("asset_id", "")).strip() != token:
            continue
        if str(commitment.get("commitment_kind", "")).strip() != "maintenance_due":
            continue
        if int(_as_int(commitment.get("scheduled_tick", 0), 0)) > int(current_tick):
            continue
        if str(commitment.get("status", "")).strip() in ("completed", "failed"):
            continue
        commitment["status"] = "completed"
        commitments[commitment_id] = commitment
    event = _provenance_event(event_type_id="event.maintenance_performed", tick=int(current_tick), asset_id=token, actor_subject_id=str(actor_subject_id), sequence=int(max(0, _as_int(event_sequence_start, 0))), ledger_deltas={"quantity.mass": 0}, extensions={"backlog_before": backlog_before, "backlog_after": 0})
    return {"asset_health_states": [dict(assets[key]) for key in sorted(assets.keys())], "maintenance_commitments": [dict(commitments[key]) for key in sorted(commitments.keys())], "provenance_events": [event], "next_event_sequence": int(max(0, _as_int(event_sequence_start, 0)) + 1), "backlog_before": int(backlog_before), "backlog_after": 0}


def tick_decay(*, asset_health_states: object, failure_mode_registry: Mapping[str, object] | None, maintenance_policy_registry: Mapping[str, object] | None, backlog_growth_rule_registry: Mapping[str, object] | None, current_tick: int, dt_ticks: int, actor_subject_id: str, numeric_policy: Mapping[str, object] | None = None, event_sequence_start: int = 0) -> dict:
    config = fixed_point_config_from_policy(numeric_policy)
    scale = int(config.scale)
    assets = _asset_rows_by_id(asset_health_states)
    modes = failure_mode_rows_by_id(failure_mode_registry)
    policies = maintenance_policy_rows_by_id(maintenance_policy_registry)
    growth_rules = backlog_growth_rule_rows_by_id(backlog_growth_rule_registry)
    dt_total = int(max(0, _as_int(dt_ticks, 0)))
    if dt_total <= 0:
        return {"asset_health_states": [dict(assets[key]) for key in sorted(assets.keys())], "failure_events": [], "provenance_events": [], "next_event_sequence": int(max(0, _as_int(event_sequence_start, 0))), "failure_count": 0}
    sequence = int(max(0, _as_int(event_sequence_start, 0)))
    failures: List[dict] = []
    provenance: List[dict] = []
    for asset_id in sorted(assets.keys()):
        row = dict(assets[asset_id])
        ext = dict(row.get("extensions") or {})
        policy = _resolve_policy(policies, str(ext.get("maintenance_policy_id", "")))
        growth_rule = dict(growth_rules.get(str(policy.get("backlog_growth_rule_id", "")).strip() or "backlog.linear_stub") or {})
        backlog = int(max(0, _as_int(row.get("maintenance_backlog", 0), 0)))
        max_backlog = int(max(0, _as_int(policy.get("max_backlog", backlog), backlog)))
        wear = dict(row.get("accumulated_wear") or {})
        hazard_state = dict(row.get("hazard_state") or {})
        failed_mode_ids = set(_sorted_unique_strings(hazard_state.get("failed_mode_ids")))
        step_sizes = []
        remaining = int(dt_total)
        while remaining > 0:
            step = int(min(1024, remaining))
            step_sizes.append(step)
            remaining -= step
        for step_dt in step_sizes:
            backlog += _growth_increment(growth_rule, backlog, step_dt)
            if max_backlog > 0:
                backlog = min(backlog, max_backlog)
            backlog_multiplier = max(1, 1 + (backlog // max(1, scale)))
            for mode_id in _sorted_unique_strings(row.get("failure_mode_ids")):
                mode = dict(modes.get(mode_id) or {})
                if not mode:
                    continue
                base_rate = int(max(0, _as_int(mode.get("base_hazard_rate_per_tick", 0), 0)))
                if base_rate <= 0:
                    continue
                wear_value = int(max(0, _as_int(wear.get(mode_id, 0), 0)))
                wear_value += int(base_rate * int(step_dt) * int(backlog_multiplier))
                wear[mode_id] = int(wear_value)
                if mode_id in failed_mode_ids:
                    continue
                threshold = max(1, _as_int((dict(mode.get("modifiers") or {})).get("failure_threshold", scale), scale))
                if wear_value < threshold:
                    continue
                failed_mode_ids.add(mode_id)
                severity = int(max(1, wear_value // threshold))
                consequence = {
                    "state_change": "failed",
                    "usable_material_loss_raw": int(max(0, _as_int(ext.get("failure_mass_loss_raw", 0), 0))),
                    "scrap_material_id": str(ext.get("scrap_material_id", "material.scrap.generic")).strip() or "material.scrap.generic",
                    "source_material_id": str(ext.get("material_id", "material.unknown")).strip() or "material.unknown",
                }
                prov = _provenance_event(event_type_id=str(mode.get("failure_event_type_id", "event.failure.triggered")), tick=int(max(0, int(current_tick))), asset_id=asset_id, actor_subject_id=str(actor_subject_id), sequence=sequence, ledger_deltas={"quantity.mass": 0, "quantity.entropy_metric": int(max(0, _as_int(ext.get("failure_entropy_delta_raw", 0), 0)))}, extensions={"failure_mode_id": mode_id, "severity": severity})
                sequence += 1
                fail = _failure_event(tick=int(max(0, int(current_tick))), asset_id=asset_id, failure_mode_id=mode_id, severity=severity, consequences=consequence, provenance_event_id=str(prov.get("event_id", "")), sequence=sequence)
                sequence += 1
                provenance.append(prov)
                failures.append(fail)
        row["accumulated_wear"] = dict((str(key), max(0, _as_int(value, 0))) for key, value in sorted(wear.items(), key=lambda item: str(item[0])))
        row["maintenance_backlog"] = int(max(0, backlog))
        hazard_state["failed_mode_ids"] = sorted(failed_mode_ids)
        hazard_state["last_decay_tick"] = int(max(0, int(current_tick)))
        row["hazard_state"] = hazard_state
        assets[asset_id] = row
    failure_rows = sorted((dict(row) for row in failures if isinstance(row, dict)), key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))))
    provenance_rows = sorted((dict(row) for row in provenance if isinstance(row, dict)), key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))))
    return {"asset_health_states": [dict(assets[key]) for key in sorted(assets.keys())], "failure_events": failure_rows, "provenance_events": provenance_rows, "next_event_sequence": int(sequence), "failure_count": int(len(failure_rows))}


def quantized_failure_risk_summary(*, asset_health_row: Mapping[str, object], failure_mode_registry: Mapping[str, object] | None, quantization_step: int) -> dict:
    asset = normalize_asset_health_state(asset_health_row)
    modes = failure_mode_rows_by_id(failure_mode_registry)
    failed_mode_ids = set(_sorted_unique_strings((dict(asset.get("hazard_state") or {})).get("failed_mode_ids")))
    step = max(1, int(quantization_step))
    rows = []
    for mode_id in _sorted_unique_strings(asset.get("failure_mode_ids")):
        wear = int(max(0, _as_int((dict(asset.get("accumulated_wear") or {})).get(mode_id, 0), 0)))
        threshold = max(1, _as_int((dict((dict(modes.get(mode_id) or {})).get("modifiers") or {})).get("failure_threshold", 1 << 24), 1 << 24))
        risk_permille = int(min(1000, (wear * 1000) // threshold))
        rows.append({"failure_mode_id": mode_id, "risk_permille_quantized": int(min(1000, (risk_permille // step) * step)), "failed": mode_id in failed_mode_ids})
    rows = sorted(rows, key=lambda row: str(row.get("failure_mode_id", "")))
    return {"asset_id": str(asset.get("asset_id", "")), "risk_rows": rows, "summary_hash": canonical_sha256(rows)}
