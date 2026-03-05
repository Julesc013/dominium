"""SYS-7 deterministic system forensics engine."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_SYSTEM_EXPLAIN_INVALID = "refusal.system.explain.invalid"
REFUSAL_SYSTEM_EXPLAIN_SYSTEM_UNKNOWN = "refusal.system.explain.system_unknown"

_DEFAULT_CAUSE_BOUND = 16
_EXPLAIN_LEVEL_BOUNDS = {
    "L1": 6,
    "L2": 12,
    "L3": 16,
}

_ENTRY_KIND_HINTS = {
    "hazard": [
        "hint.reduce.system_load",
        "hint.inspect.system_micro",
    ],
    "fault": [
        "hint.apply.safety_isolation",
        "hint.inspect.system_micro",
    ],
    "ledger": [
        "hint.review.boundary_flux",
        "hint.review.energy_transform",
    ],
    "spec": [
        "hint.review.spec_and_safety",
        "hint.request.recertification",
    ],
    "safety": [
        "hint.reset.safety_pattern",
        "hint.inspect.system_micro",
    ],
    "model": [
        "hint.review.macro_model_set",
        "hint.raise.ctrl.fidelity_request",
    ],
    "signal": [
        "hint.verify.signal_path",
        "hint.review.control_channels",
    ],
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _stable_unique(values: Iterable[object], *, max_items: int) -> List[str]:
    seen = set()
    out: List[str] = []
    bound = int(max(1, _as_int(max_items, _DEFAULT_CAUSE_BOUND)))
    for item in values:
        token = str(item or "").strip()
        if (not token) or (token in seen):
            continue
        seen.add(token)
        out.append(token)
        if len(out) >= bound:
            break
    return out


def _explain_bound(explain_level: str, max_items: int) -> int:
    level = str(explain_level or "").strip().upper() or "L1"
    declared = int(max(1, _as_int(_EXPLAIN_LEVEL_BOUNDS.get(level, _DEFAULT_CAUSE_BOUND), _DEFAULT_CAUSE_BOUND)))
    requested = int(max(1, _as_int(max_items, _DEFAULT_CAUSE_BOUND)))
    return int(min(declared, requested))


def _tick_from_row(row: Mapping[str, object], fallback_tick: int) -> int:
    for key in ("tick", "last_update_tick", "issued_tick"):
        if key in row:
            return int(max(0, _as_int(row.get(key, fallback_tick), fallback_tick)))
    return int(max(0, _as_int(fallback_tick, 0)))


def _entry_id_from_row(row: Mapping[str, object]) -> str:
    for key in (
        "event_id",
        "warning_id",
        "result_id",
        "record_id",
        "entry_id",
        "decision_id",
        "cert_id",
        "capsule_id",
    ):
        token = str(row.get(key, "")).strip()
        if token:
            return token
    return "entry.{}".format(canonical_sha256(dict(row))[:16])


def _event_id_from_row(row: Mapping[str, object]) -> str:
    for key in ("event_id", "warning_id", "result_id", "record_id"):
        token = str(row.get(key, "")).strip()
        if token:
            return token
    return ""


def _severity_from_row(row: Mapping[str, object], base_severity: int) -> int:
    ext = _as_map(row.get("extensions"))
    for key in ("severity", "severity_rank"):
        if key in row:
            return int(max(0, _as_int(row.get(key, base_severity), base_severity)))
        if key in ext:
            return int(max(0, _as_int(ext.get(key, base_severity), base_severity)))
    return int(max(0, _as_int(base_severity, 0)))


def _row_matches_targets(row: Mapping[str, object], target_ids: Sequence[str]) -> bool:
    targets = set(_sorted_tokens(target_ids))
    if not targets:
        return False
    for key in ("system_id", "target_id", "subject_id", "capsule_id", "source_id", "region_id"):
        token = str(row.get(key, "")).strip()
        if token and token in targets:
            return True
    ext = _as_map(row.get("extensions"))
    for key in ("system_id", "target_id", "capsule_id"):
        token = str(ext.get(key, "")).strip()
        if token and token in targets:
            return True
    return False


def build_cause_entry_row(
    *,
    entry_kind: str,
    entry_id: str,
    severity: int,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind_token = str(entry_kind or "").strip().lower()
    entry_token = str(entry_id or "").strip()
    if (not kind_token) or (not entry_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "entry_kind": kind_token,
        "entry_id": entry_token,
        "severity": int(max(0, _as_int(severity, 0))),
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_cause_entry_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            -int(max(0, _as_int(item.get("severity", 0), 0))),
            -int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("entry_id", "")),
        ),
    ):
        normalized = build_cause_entry_row(
            entry_kind=str(row.get("entry_kind", "")).strip(),
            entry_id=str(row.get("entry_id", "")).strip(),
            severity=int(max(0, _as_int(row.get("severity", 0), 0))),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        entry_key = "{}::{}".format(
            str(normalized.get("entry_kind", "")).strip(),
            str(normalized.get("entry_id", "")).strip(),
        )
        if entry_key != "::":
            out[entry_key] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_system_explain_request_row(
    *,
    request_id: str,
    system_id: str,
    event_id: str | None,
    explain_level: str,
    requester_subject_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    request_token = str(request_id or "").strip()
    system_token = str(system_id or "").strip()
    requester_token = str(requester_subject_id or "").strip()
    explain_level_token = str(explain_level or "").strip().upper() or "L1"
    if (not request_token) or (not system_token) or (not requester_token):
        return {}
    if explain_level_token not in {"L1", "L2", "L3"}:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "request_id": request_token,
        "system_id": system_token,
        "event_id": None if not str(event_id or "").strip() else str(event_id).strip(),
        "explain_level": explain_level_token,
        "requester_subject_id": requester_token,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_system_explain_request_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("system_id", "")),
            str(item.get("event_id", "")),
            str(item.get("request_id", "")),
        ),
    ):
        normalized = build_system_explain_request_row(
            request_id=str(row.get("request_id", "")).strip(),
            system_id=str(row.get("system_id", "")).strip(),
            event_id=(None if row.get("event_id") is None else str(row.get("event_id", "")).strip()),
            explain_level=str(row.get("explain_level", "")).strip().upper(),
            requester_subject_id=str(row.get("requester_subject_id", "")).strip(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        request_id = str(normalized.get("request_id", "")).strip()
        if request_id:
            out[request_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_system_explain_artifact_row(
    *,
    explain_id: str,
    system_id: str,
    explain_level: str,
    primary_cause: str,
    cause_chain: object,
    referenced_event_ids: object,
    referenced_specs: object,
    remediation_hints: object,
    epistemic_redaction_level: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    explain_token = str(explain_id or "").strip()
    system_token = str(system_id or "").strip()
    level_token = str(explain_level or "").strip().upper() or "L1"
    primary = str(primary_cause or "").strip() or "cause.none"
    redaction = str(epistemic_redaction_level or "").strip().lower() or "diegetic"
    if (not explain_token) or (not system_token) or level_token not in {"L1", "L2", "L3"}:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "explain_id": explain_token,
        "system_id": system_token,
        "explain_level": level_token,
        "primary_cause": primary,
        "cause_chain": normalize_cause_entry_rows(cause_chain),
        "referenced_event_ids": _stable_unique(referenced_event_ids or [], max_items=_DEFAULT_CAUSE_BOUND),
        "referenced_specs": _stable_unique(referenced_specs or [], max_items=_DEFAULT_CAUSE_BOUND),
        "remediation_hints": _stable_unique(remediation_hints or [], max_items=_DEFAULT_CAUSE_BOUND),
        "epistemic_redaction_level": redaction,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_system_explain_artifact_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("system_id", "")),
            str(item.get("explain_level", "")),
            str(item.get("explain_id", "")),
        ),
    ):
        normalized = build_system_explain_artifact_row(
            explain_id=str(row.get("explain_id", "")).strip(),
            system_id=str(row.get("system_id", "")).strip(),
            explain_level=str(row.get("explain_level", "")).strip().upper(),
            primary_cause=str(row.get("primary_cause", "")).strip(),
            cause_chain=list(row.get("cause_chain") or []),
            referenced_event_ids=list(row.get("referenced_event_ids") or []),
            referenced_specs=list(row.get("referenced_specs") or []),
            remediation_hints=list(row.get("remediation_hints") or []),
            epistemic_redaction_level=str(row.get("epistemic_redaction_level", "")).strip().lower(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        explain_id = str(normalized.get("explain_id", "")).strip()
        if explain_id:
            out[explain_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _cause_row(
    *,
    entry_kind: str,
    row: Mapping[str, object],
    base_severity: int,
    default_tick: int,
) -> dict:
    entry_id = _entry_id_from_row(row)
    event_id = _event_id_from_row(row)
    tick = _tick_from_row(row, default_tick)
    severity = _severity_from_row(row, base_severity)
    spec_refs = _sorted_tokens(
        [
            row.get("spec_id"),
            row.get("spec_type_id"),
            _as_map(row.get("extensions")).get("spec_id"),
            _as_map(row.get("extensions")).get("spec_type_id"),
        ]
    )
    return {
        "cause_entry": build_cause_entry_row(
            entry_kind=entry_kind,
            entry_id=entry_id,
            severity=severity,
            tick=tick,
            extensions={
                "event_id": event_id or None,
                "spec_refs": list(spec_refs),
            },
        ),
        "event_id": event_id,
        "spec_refs": list(spec_refs),
    }


def _collect_causes(
    *,
    default_tick: int,
    target_ids: Sequence[str],
    rows: object,
    entry_kind: str,
    base_severity: int,
) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: List[dict] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        row_map = dict(row)
        if not _row_matches_targets(row_map, target_ids):
            continue
        cause_row = _cause_row(
            entry_kind=entry_kind,
            row=row_map,
            base_severity=base_severity,
            default_tick=default_tick,
        )
        if cause_row.get("cause_entry"):
            out.append(cause_row)
    return out


def _policy_redaction_level(policy_id: str) -> str:
    token = str(policy_id or "").strip().lower()
    if ("admin" in token) or ("operator" in token):
        return "admin"
    if ("inspector" in token) or ("inspect" in token):
        return "inspector"
    return "diegetic"


def _redact_cause_chain(cause_chain: List[dict], redaction_level: str) -> List[dict]:
    level = str(redaction_level or "").strip().lower()
    if level == "admin":
        return normalize_cause_entry_rows(cause_chain)
    if level == "inspector":
        return normalize_cause_entry_rows(cause_chain)[:8]
    redacted: List[dict] = []
    for row in normalize_cause_entry_rows(cause_chain)[:3]:
        redacted.append(
            build_cause_entry_row(
                entry_kind=str(row.get("entry_kind", "")).strip(),
                entry_id="coarse.{}".format(str(row.get("entry_kind", "")).strip() or "cause"),
                severity=int(max(0, _as_int(row.get("severity", 0), 0))),
                tick=int(max(0, _as_int(row.get("tick", 0), 0))),
                extensions={
                    "coarse": True,
                },
            )
        )
    return normalize_cause_entry_rows(redacted)


def _cache_key(*, system_id: str, event_id: str, truth_hash_anchor: str, requester_policy_id: str) -> str:
    return "cache.system.explain.{}".format(
        canonical_sha256(
            {
                "system_id": str(system_id or "").strip(),
                "event_id": str(event_id or "").strip(),
                "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
                "requester_policy_id": str(requester_policy_id or "").strip(),
            }
        )[:16]
    )


def evaluate_system_explain_request(
    *,
    current_tick: int,
    system_explain_request: Mapping[str, object],
    system_rows: object,
    system_macro_capsule_rows: object,
    system_failure_event_rows: object = None,
    system_forced_expand_event_rows: object = None,
    system_certificate_revocation_rows: object = None,
    system_certification_result_rows: object = None,
    safety_event_rows: object = None,
    energy_ledger_entry_rows: object = None,
    model_hazard_rows: object = None,
    spec_compliance_result_rows: object = None,
    system_macro_output_record_rows: object = None,
    system_macro_runtime_state_rows: object = None,
    domain_fault_rows: object = None,
    existing_cache_rows: object = None,
    truth_hash_anchor: str = "",
    requester_policy_id: str = "policy.epistemic.diegetic",
    max_cause_entries: int = _DEFAULT_CAUSE_BOUND,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = build_system_explain_request_row(
        request_id=str(system_explain_request.get("request_id", "")).strip(),
        system_id=str(system_explain_request.get("system_id", "")).strip(),
        event_id=(
            None
            if system_explain_request.get("event_id") is None
            else str(system_explain_request.get("event_id", "")).strip()
        ),
        explain_level=str(system_explain_request.get("explain_level", "L1")).strip().upper(),
        requester_subject_id=str(system_explain_request.get("requester_subject_id", "")).strip(),
        deterministic_fingerprint=str(system_explain_request.get("deterministic_fingerprint", "")).strip(),
        extensions=_as_map(system_explain_request.get("extensions")),
    )
    if not request:
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SYSTEM_EXPLAIN_INVALID,
            "artifact_row": {},
            "cache_rows": list(existing_cache_rows or []),
            "cache_hit": False,
        }

    system_id = str(request.get("system_id", "")).strip()
    system_by_id = dict(
        (
            str(row.get("system_id", "")).strip(),
            dict(row),
        )
        for row in list(system_rows or [])
        if isinstance(row, Mapping) and str(row.get("system_id", "")).strip()
    )
    if system_id not in system_by_id:
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SYSTEM_EXPLAIN_SYSTEM_UNKNOWN,
            "artifact_row": {},
            "cache_rows": list(existing_cache_rows or []),
            "cache_hit": False,
        }

    capsule_ids = _sorted_tokens(
        str(row.get("capsule_id", "")).strip()
        for row in list(system_macro_capsule_rows or [])
        if isinstance(row, Mapping) and str(row.get("system_id", "")).strip() == system_id
    )
    target_ids = [system_id] + list(capsule_ids)

    event_id = str(request.get("event_id", "") or "").strip()
    policy_id = str(requester_policy_id or "").strip() or "policy.epistemic.diegetic"
    cache_rows = [dict(item) for item in list(existing_cache_rows or []) if isinstance(item, Mapping)]
    cache_key = _cache_key(
        system_id=system_id,
        event_id=event_id or "request.{}".format(str(request.get("request_id", ""))),
        truth_hash_anchor=str(truth_hash_anchor or "").strip(),
        requester_policy_id=policy_id,
    )

    for row in sorted(cache_rows, key=lambda item: str(item.get("cache_key", ""))):
        if str(row.get("cache_key", "")).strip() != cache_key:
            continue
        artifact = dict(row.get("artifact") or {}) if isinstance(row.get("artifact"), Mapping) else {}
        if artifact:
            return {
                "result": "complete",
                "reason_code": "",
                "artifact_row": artifact,
                "cache_rows": cache_rows,
                "cache_hit": True,
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "cache_key": cache_key,
                        "artifact": artifact,
                        "cache_hit": True,
                    }
                ),
            }

    causes: List[dict] = []
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=system_failure_event_rows,
            entry_kind="fault",
            base_severity=100,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=system_forced_expand_event_rows,
            entry_kind="model",
            base_severity=90,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=system_certificate_revocation_rows,
            entry_kind="spec",
            base_severity=88,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=system_certification_result_rows,
            entry_kind="spec",
            base_severity=82,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=safety_event_rows,
            entry_kind="safety",
            base_severity=80,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=spec_compliance_result_rows,
            entry_kind="spec",
            base_severity=78,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=energy_ledger_entry_rows,
            entry_kind="ledger",
            base_severity=70,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=model_hazard_rows,
            entry_kind="hazard",
            base_severity=66,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=system_macro_output_record_rows,
            entry_kind="model",
            base_severity=62,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=system_macro_runtime_state_rows,
            entry_kind="model",
            base_severity=58,
        )
    )
    causes.extend(
        _collect_causes(
            default_tick=tick,
            target_ids=target_ids,
            rows=domain_fault_rows,
            entry_kind="signal",
            base_severity=55,
        )
    )

    cause_rows = [dict(item.get("cause_entry") or {}) for item in causes if isinstance(item, Mapping)]
    cause_rows = [row for row in cause_rows if row]
    sorted_causes = sorted(
        cause_rows,
        key=lambda item: (
            -int(max(0, _as_int(item.get("severity", 0), 0))),
            -int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("entry_id", "")),
        ),
    )
    bound = _explain_bound(str(request.get("explain_level", "L1")), int(max_cause_entries))
    bounded_causes = normalize_cause_entry_rows(sorted_causes[:bound])
    if not bounded_causes:
        bounded_causes = [
            build_cause_entry_row(
                entry_kind="model",
                entry_id="cause.none",
                severity=0,
                tick=tick,
                extensions={"empty": True},
            )
        ]

    primary_row = dict(bounded_causes[0])
    primary_cause = "{}.{}".format(
        str(primary_row.get("entry_kind", "")).strip() or "model",
        str(primary_row.get("entry_id", "")).strip() or "cause.none",
    )

    referenced_event_ids = _stable_unique(
        (
            item.get("event_id")
            for item in causes
            if isinstance(item, Mapping) and str(item.get("event_id", "")).strip()
        ),
        max_items=bound,
    )
    referenced_specs = _stable_unique(
        (
            spec_id
            for item in causes
            if isinstance(item, Mapping)
            for spec_id in list(item.get("spec_refs") or [])
        ),
        max_items=bound,
    )
    remediation_hints = _stable_unique(
        (
            hint
            for row in bounded_causes
            for hint in list(_ENTRY_KIND_HINTS.get(str(row.get("entry_kind", "")).strip(), []))
        ),
        max_items=bound,
    )

    redaction_level = _policy_redaction_level(policy_id)
    redacted_causes = _redact_cause_chain(bounded_causes, redaction_level)
    if redaction_level == "diegetic":
        referenced_event_ids = []
        referenced_specs = []
        remediation_hints = remediation_hints[:2]
    elif redaction_level == "inspector":
        referenced_event_ids = referenced_event_ids[:8]
        referenced_specs = referenced_specs[:6]

    explain_id = "system.explain.{}".format(
        canonical_sha256(
            {
                "request_id": str(request.get("request_id", "")).strip(),
                "system_id": system_id,
                "event_id": event_id or None,
                "explain_level": str(request.get("explain_level", "")).strip(),
                "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
                "requester_policy_id": policy_id,
                "cause_chain": redacted_causes,
                "referenced_event_ids": referenced_event_ids,
                "referenced_specs": referenced_specs,
                "remediation_hints": remediation_hints,
                "epistemic_redaction_level": redaction_level,
            }
        )[:16]
    )
    artifact_row = build_system_explain_artifact_row(
        explain_id=explain_id,
        system_id=system_id,
        explain_level=str(request.get("explain_level", "")).strip(),
        primary_cause=primary_cause,
        cause_chain=redacted_causes,
        referenced_event_ids=referenced_event_ids,
        referenced_specs=referenced_specs,
        remediation_hints=remediation_hints,
        epistemic_redaction_level=redaction_level,
        extensions={
            "request_id": str(request.get("request_id", "")).strip(),
            "event_id": event_id or None,
            "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
            "requester_policy_id": policy_id,
            "cache_key": cache_key,
        },
    )

    updated_cache_rows = [dict(row) for row in cache_rows if str(row.get("cache_key", "")).strip() != cache_key]
    updated_cache_rows.append(
        {
            "cache_key": cache_key,
            "system_id": system_id,
            "event_id": event_id or None,
            "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
            "requester_policy_id": policy_id,
            "artifact": dict(artifact_row),
        }
    )
    updated_cache_rows = sorted(
        [dict(row) for row in updated_cache_rows if isinstance(row, Mapping)],
        key=lambda item: (
            str(item.get("cache_key", "")),
            str(item.get("system_id", "")),
            str(item.get("event_id", "")),
        ),
    )

    return {
        "result": "complete",
        "reason_code": "",
        "artifact_row": dict(artifact_row),
        "cache_rows": updated_cache_rows,
        "cache_hit": False,
        "deterministic_fingerprint": canonical_sha256(
            {
                "artifact": artifact_row,
                "cache_key": cache_key,
                "cache_hit": False,
            }
        ),
    }


__all__ = [
    "REFUSAL_SYSTEM_EXPLAIN_INVALID",
    "REFUSAL_SYSTEM_EXPLAIN_SYSTEM_UNKNOWN",
    "build_cause_entry_row",
    "normalize_cause_entry_rows",
    "build_system_explain_request_row",
    "normalize_system_explain_request_rows",
    "build_system_explain_artifact_row",
    "normalize_system_explain_artifact_rows",
    "evaluate_system_explain_request",
]
