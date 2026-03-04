"""META-CONTRACT-0 deterministic explain artifact helpers (derived-only)."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


_DEFAULT_BOUND = 16


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _hash_payload(value: Mapping[str, object]) -> str:
    return canonical_sha256(dict(value))


def _stable_unique(values: Iterable[object], *, max_items: int) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in values:
        token = str(item or "").strip()
        if (not token) or token in seen:
            continue
        seen.add(token)
        out.append(token)
        if len(out) >= int(max(1, _as_int(max_items, _DEFAULT_BOUND))):
            break
    return out


def explain_cache_key(*, event_id: str, truth_hash_anchor: str, epistemic_policy_id: str) -> str:
    event_token = str(event_id or "").strip()
    truth_token = str(truth_hash_anchor or "").strip()
    policy_token = str(epistemic_policy_id or "").strip()
    if not event_token:
        return ""
    payload = {
        "event_id": event_token,
        "truth_hash_anchor": truth_token,
        "epistemic_policy_id": policy_token,
    }
    return "cache.explain.{}".format(canonical_sha256(payload)[:16])


def build_explain_artifact(
    *,
    explain_id: str,
    event_id: str = "",
    target_id: str = "",
    cause_chain: object = None,
    referenced_artifacts: object = None,
    remediation_hints: object = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    explain_token = str(explain_id or "").strip()
    event_token = str(event_id or "").strip()
    target_token = str(target_id or "").strip()
    if (not explain_token) or ((not event_token) and (not target_token)):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "explain_id": explain_token,
        "event_id": event_token or None,
        "target_id": target_token or None,
        "cause_chain": _stable_unique(list(cause_chain or []), max_items=_DEFAULT_BOUND),
        "referenced_artifacts": _stable_unique(list(referenced_artifacts or []), max_items=_DEFAULT_BOUND),
        "remediation_hints": _stable_unique(list(remediation_hints or []), max_items=_DEFAULT_BOUND),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_explain_artifact_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("event_id", "")),
            str(item.get("target_id", "")),
            str(item.get("explain_id", "")),
        ),
    ):
        normalized = build_explain_artifact(
            explain_id=str(row.get("explain_id", "")).strip(),
            event_id=str(row.get("event_id", "")).strip(),
            target_id=str(row.get("target_id", "")).strip(),
            cause_chain=list(row.get("cause_chain") or []),
            referenced_artifacts=list(row.get("referenced_artifacts") or []),
            remediation_hints=list(row.get("remediation_hints") or []),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("explain_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def explain_artifact_rows_by_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_explain_artifact_rows(rows)
    return dict(
        (str(row.get("explain_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("explain_id", "")).strip()
    )


def _cause_keys_from_rows(rows: object, *, row_kind: str, max_items: int) -> List[str]:
    if not isinstance(rows, list):
        rows = []
    out: List[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        row_map = dict(row)
        row_id = str(
            row_map.get("decision_id")
            or row_map.get("event_id")
            or row_map.get("result_id")
            or row_map.get("id")
            or ""
        ).strip()
        kind_id = str(row_map.get("kind_id") or row_map.get("event_kind_id") or row_kind).strip() or row_kind
        token = "{}.{}".format(kind_id, row_id or canonical_sha256(_canon(row_map))[:8])
        out.append("cause.{}".format(token))
        if len(out) >= int(max(1, _as_int(max_items, _DEFAULT_BOUND))):
            break
    return _stable_unique(out, max_items=max_items)


def _artifact_refs_from_rows(rows: object, *, artifact_kind: str, max_items: int) -> List[str]:
    if not isinstance(rows, list):
        rows = []
    out: List[str] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        row_map = dict(row)
        row_id = str(
            row_map.get("event_id")
            or row_map.get("decision_id")
            or row_map.get("result_id")
            or row_map.get("artifact_id")
            or ""
        ).strip()
        if not row_id:
            row_id = canonical_sha256(_canon(row_map))[:8]
        out.append("artifact.{}:{}".format(artifact_kind, row_id))
        if len(out) >= int(max(1, _as_int(max_items, _DEFAULT_BOUND))):
            break
    return _stable_unique(out, max_items=max_items)


def _sorted_mapping_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: List[dict] = []
    for row in rows:
        if isinstance(row, Mapping):
            out.append(dict(row))
    return sorted(
        out,
        key=lambda item: (
            str(item.get("event_id", "")),
            str(item.get("decision_id", "")),
            str(item.get("result_id", "")),
            canonical_sha256(_canon(item)),
        ),
    )


def _event_cause_tokens(
    *,
    rows: object,
    cause_prefix: str,
    key_candidates: Iterable[str],
    max_items: int,
) -> List[str]:
    bound = int(max(1, _as_int(max_items, _DEFAULT_BOUND)))
    out: List[str] = []
    for row in _sorted_mapping_rows(rows):
        for key in key_candidates:
            value = str(row.get(str(key), "")).strip()
            if not value:
                continue
            token_hash = canonical_sha256(
                {
                    "cause_prefix": str(cause_prefix),
                    "key": str(key),
                    "value": str(value),
                }
            )[:8]
            out.append("cause.{}.{}.{}".format(str(cause_prefix), str(key), str(token_hash)))
            if len(out) >= bound:
                return _stable_unique(out, max_items=bound)
    return _stable_unique(out, max_items=bound)


def _event_specific_cause_keys(
    *,
    event_kind_id: str,
    decision_log_rows: object,
    safety_event_rows: object,
    hazard_rows: object,
    compliance_rows: object,
    model_result_rows: object,
    max_items: int,
) -> List[str]:
    event_kind = str(event_kind_id or "").strip().lower()
    bound = int(max(1, _as_int(max_items, _DEFAULT_BOUND)))
    out: List[str] = []

    if event_kind.startswith("elec."):
        out.extend(
            _event_cause_tokens(
                rows=safety_event_rows,
                cause_prefix="elec_safety",
                key_candidates=(
                    "fault_state",
                    "fault_code",
                    "trip_reason",
                    "safety_pattern_id",
                    "protection_pattern_id",
                ),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=hazard_rows,
                cause_prefix="elec_fault",
                key_candidates=("fault_state", "fault_code", "overload_ratio", "hazard_id"),
                max_items=bound,
            )
        )

    if event_kind.startswith("therm."):
        out.extend(
            _event_cause_tokens(
                rows=hazard_rows,
                cause_prefix="therm_hazard",
                key_candidates=("temperature", "temperature_c", "overtemp", "fire_state", "heat_loss"),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=model_result_rows,
                cause_prefix="therm_model",
                key_candidates=("heat_loss", "heat_input", "phase_state", "runaway_index"),
                max_items=bound,
            )
        )

    if event_kind.startswith("fluid."):
        out.extend(
            _event_cause_tokens(
                rows=safety_event_rows,
                cause_prefix="fluid_safety",
                key_candidates=(
                    "pressure_head",
                    "current_head",
                    "relief_threshold",
                    "burst_threshold",
                    "spec_id",
                ),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=hazard_rows,
                cause_prefix="fluid_hazard",
                key_candidates=("pressure_head", "leak_rate", "cavitation_risk", "target_id"),
                max_items=bound,
            )
        )

    if event_kind.startswith("chem."):
        out.extend(
            _event_cause_tokens(
                rows=model_result_rows,
                cause_prefix="chem_model",
                key_candidates=(
                    "reaction_id",
                    "rate_model_id",
                    "efficiency_permille",
                    "mixture_ratio_permille",
                    "temperature",
                    "entropy_value",
                ),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=hazard_rows,
                cause_prefix="chem_hazard",
                key_candidates=("hazard_type_id", "overheat", "fire_state", "pollutant_emission"),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=compliance_rows,
                cause_prefix="chem_ledger",
                key_candidates=("transformation_id", "entry_id", "energy_total_delta"),
                max_items=bound,
            )
        )

    if event_kind.startswith("mob."):
        out.extend(
            _event_cause_tokens(
                rows=hazard_rows,
                cause_prefix="mob_hazard",
                key_candidates=("speed", "speed_mm_per_tick", "curvature", "wear", "signal_violation"),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=model_result_rows,
                cause_prefix="mob_model",
                key_candidates=("traction", "friction", "derailment_risk", "brake_state"),
                max_items=bound,
            )
        )

    if event_kind.startswith("sig."):
        out.extend(
            _event_cause_tokens(
                rows=decision_log_rows,
                cause_prefix="sig_decision",
                key_candidates=("belief_policy_id", "policy_id", "accepted", "reason_code"),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=model_result_rows,
                cause_prefix="sig_model",
                key_candidates=("attenuation", "loss_modifier", "jamming", "decrypt_denied"),
                max_items=bound,
            )
        )

    if event_kind.startswith("phys."):
        out.extend(
            _event_cause_tokens(
                rows=safety_event_rows,
                cause_prefix="phys_exception",
                key_candidates=("exception_kind", "reason_code", "quantity_id", "value"),
                max_items=bound,
            )
        )
        out.extend(
            _event_cause_tokens(
                rows=compliance_rows,
                cause_prefix="phys_ledger",
                key_candidates=("transformation_id", "entry_id", "energy_total_delta", "momentum_delta"),
                max_items=bound,
            )
        )

    return _stable_unique(out, max_items=bound)


def generate_explain_artifact(
    *,
    event_id: str,
    target_id: str,
    event_kind_id: str,
    truth_hash_anchor: str,
    epistemic_policy_id: str,
    explain_contract_row: Mapping[str, object] | None = None,
    decision_log_rows: object = None,
    safety_event_rows: object = None,
    hazard_rows: object = None,
    compliance_rows: object = None,
    model_result_rows: object = None,
    cause_chain_keys: object = None,
    remediation_hint_keys: object = None,
    referenced_artifacts: object = None,
    max_items: int = _DEFAULT_BOUND,
) -> dict:
    event_token = str(event_id or "").strip()
    target_token = str(target_id or "").strip()
    event_kind_token = str(event_kind_id or "").strip() or "event.unknown"
    if (not event_token) and (not target_token):
        return {}

    bound = int(max(1, _as_int(max_items, _DEFAULT_BOUND)))
    contract_row = dict(explain_contract_row or {})
    contract_hints = list(contract_row.get("remediation_hint_keys") or [])
    contract_required_inputs = list(contract_row.get("required_inputs") or [])

    derived_causes: List[str] = []
    derived_causes.extend(_cause_keys_from_rows(decision_log_rows, row_kind="decision", max_items=bound))
    derived_causes.extend(_cause_keys_from_rows(safety_event_rows, row_kind="safety", max_items=bound))
    derived_causes.extend(_cause_keys_from_rows(hazard_rows, row_kind="hazard", max_items=bound))
    derived_causes.extend(_cause_keys_from_rows(compliance_rows, row_kind="compliance", max_items=bound))
    derived_causes.extend(_cause_keys_from_rows(model_result_rows, row_kind="model", max_items=bound))
    derived_causes.extend(
        _event_specific_cause_keys(
            event_kind_id=event_kind_token,
            decision_log_rows=decision_log_rows,
            safety_event_rows=safety_event_rows,
            hazard_rows=hazard_rows,
            compliance_rows=compliance_rows,
            model_result_rows=model_result_rows,
            max_items=bound,
        )
    )
    derived_causes.extend(_stable_unique(list(cause_chain_keys or []), max_items=bound))
    cause_chain = _stable_unique(derived_causes, max_items=bound)

    refs: List[str] = []
    refs.extend(_artifact_refs_from_rows(decision_log_rows, artifact_kind="decision", max_items=bound))
    refs.extend(_artifact_refs_from_rows(safety_event_rows, artifact_kind="record", max_items=bound))
    refs.extend(_artifact_refs_from_rows(hazard_rows, artifact_kind="record", max_items=bound))
    refs.extend(_artifact_refs_from_rows(compliance_rows, artifact_kind="record", max_items=bound))
    refs.extend(_artifact_refs_from_rows(model_result_rows, artifact_kind="record", max_items=bound))
    refs.extend(_stable_unique(list(referenced_artifacts or []), max_items=bound))
    refs.extend(_stable_unique(list(contract_required_inputs), max_items=bound))
    referenced = _stable_unique(refs, max_items=bound)

    hints = _stable_unique(
        list(remediation_hint_keys or []) + list(contract_hints),
        max_items=bound,
    )

    explain_id = "explain.{}".format(
        canonical_sha256(
            {
                "event_id": event_token or None,
                "target_id": target_token or None,
                "event_kind_id": event_kind_token,
                "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
                "epistemic_policy_id": str(epistemic_policy_id or "").strip(),
                "cause_chain": list(cause_chain),
                "referenced_artifacts": list(referenced),
                "remediation_hints": list(hints),
            }
        )[:16]
    )
    return build_explain_artifact(
        explain_id=explain_id,
        event_id=event_token,
        target_id=target_token,
        cause_chain=cause_chain,
        referenced_artifacts=referenced,
        remediation_hints=hints,
        extensions={
            "event_kind_id": event_kind_token,
            "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
            "epistemic_policy_id": str(epistemic_policy_id or "").strip(),
            "cache_key": explain_cache_key(
                event_id=event_token or target_token,
                truth_hash_anchor=str(truth_hash_anchor or "").strip(),
                epistemic_policy_id=str(epistemic_policy_id or "").strip(),
            ),
            "explain_artifact_type_id": str(contract_row.get("explain_artifact_type_id", "")).strip() or "artifact.explain",
        },
    )


def cached_explain_artifact(
    *,
    cache_rows: object,
    event_id: str,
    truth_hash_anchor: str,
    epistemic_policy_id: str,
    build_inputs: Mapping[str, object],
) -> dict:
    rows = list(cache_rows) if isinstance(cache_rows, list) else []
    key = explain_cache_key(
        event_id=str(event_id or "").strip(),
        truth_hash_anchor=str(truth_hash_anchor or "").strip(),
        epistemic_policy_id=str(epistemic_policy_id or "").strip(),
    )
    existing = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        row_map = dict(row)
        if str(row_map.get("cache_key", "")).strip() != key:
            continue
        artifact = dict(row_map.get("artifact") or {}) if isinstance(row_map.get("artifact"), Mapping) else {}
        if artifact:
            existing = artifact
            break
    if existing:
        return {
            "cache_key": key,
            "cache_hit": True,
            "artifact": existing,
            "cache_rows": list(rows),
        }

    artifact = generate_explain_artifact(**dict(build_inputs or {}))
    if not artifact:
        return {
            "cache_key": key,
            "cache_hit": False,
            "artifact": {},
            "cache_rows": list(rows),
        }
    rows.append(
        {
            "cache_key": key,
            "event_id": str(event_id or "").strip(),
            "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
            "epistemic_policy_id": str(epistemic_policy_id or "").strip(),
            "artifact": dict(artifact),
        }
    )
    rows = sorted(
        [dict(item) for item in rows if isinstance(item, Mapping)],
        key=lambda item: (
            str(item.get("cache_key", "")),
            str(item.get("event_id", "")),
        ),
    )
    return {
        "cache_key": key,
        "cache_hit": False,
        "artifact": dict(artifact),
        "cache_rows": rows,
    }


def redact_explain_artifact(
    *,
    explain_artifact_row: Mapping[str, object],
    epistemic_policy_id: str,
    policy_row: Mapping[str, object] | None = None,
) -> dict:
    row = dict(explain_artifact_row or {})
    if not row:
        return {}
    policy_id = str(epistemic_policy_id or "").strip()
    policy = dict(policy_row or {})
    max_level = str(policy.get("max_inspection_level", "")).strip().lower()
    if not max_level:
        max_level = "micro" if ("observer" in policy_id or "admin" in policy_id) else "meso"

    cause_chain = list(row.get("cause_chain") or [])
    refs = list(row.get("referenced_artifacts") or [])
    hints = list(row.get("remediation_hints") or [])

    if max_level == "micro":
        redaction_mode = "none"
    elif max_level == "meso":
        cause_chain = _stable_unique(cause_chain, max_items=4)
        refs = _stable_unique(refs, max_items=4)
        hints = _stable_unique(hints, max_items=4)
        redaction_mode = "meso_truncate"
    else:
        cause_chain = ["cause.redacted"]
        refs = []
        hints = _stable_unique(hints, max_items=2)
        redaction_mode = "macro_mask"

    ext = _as_map(row.get("extensions"))
    ext["redaction_mode"] = redaction_mode
    ext["epistemic_policy_id"] = policy_id
    return build_explain_artifact(
        explain_id=str(row.get("explain_id", "")).strip(),
        event_id=str(row.get("event_id", "")).strip(),
        target_id=str(row.get("target_id", "")).strip(),
        cause_chain=cause_chain,
        referenced_artifacts=refs,
        remediation_hints=hints,
        extensions=ext,
    )


__all__ = [
    "build_explain_artifact",
    "cached_explain_artifact",
    "explain_artifact_rows_by_id",
    "explain_cache_key",
    "generate_explain_artifact",
    "normalize_explain_artifact_rows",
    "redact_explain_artifact",
]
