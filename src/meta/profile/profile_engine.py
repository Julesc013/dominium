"""META-PROFILE0 deterministic unified profile resolution and override helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_PROFILE_INVALID = "refusal.profile.invalid"
REFUSAL_PROFILE_MISSING = "refusal.profile.missing"
REFUSAL_PROFILE_OVERRIDE_NOT_ALLOWED = "refusal.profile.override_not_allowed"

_PROFILE_TYPES = {
    "physics",
    "law",
    "process",
    "safety",
    "epistemic",
    "coupling",
    "compute",
    "topology",
    "metric",
    "partition",
    "projection",
}
_BINDING_SCOPES = ("universe", "session", "authority", "system")


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


def _rows_from_registry(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
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


def build_profile_row(
    *,
    profile_id: str,
    profile_type: str,
    version: str,
    overrides: Mapping[str, object] | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    profile_token = str(profile_id or "").strip()
    type_token = str(profile_type or "").strip().lower()
    version_token = str(version or "").strip()
    payload = {
        "schema_version": "1.0.0",
        "profile_id": profile_token,
        "profile_type": type_token,
        "version": version_token or "1.0.0",
        "overrides": dict(sorted(_as_map(overrides).items(), key=lambda item: str(item[0]))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not profile_token) or (type_token not in _PROFILE_TYPES):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_profile_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("profile_id", ""))):
        payload = build_profile_row(
            profile_id=str(row.get("profile_id", "")).strip(),
            profile_type=str(row.get("profile_type", "")).strip().lower(),
            version=str(row.get("version", "1.0.0")).strip() or "1.0.0",
            overrides=_as_map(row.get("overrides")),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("profile_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def profile_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("profile_id", "")).strip(), dict(row)) for row in normalize_profile_rows(rows) if str(row.get("profile_id", "")).strip())


def profile_rows_by_id_from_registry(profile_registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(profile_registry_payload, ("profiles",))
    return profile_rows_by_id(rows)


def build_profile_binding_row(
    *,
    binding_id: str,
    scope: str,
    target_id: str,
    profile_id: str,
    tick_applied: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    scope_token = str(scope or "").strip().lower()
    payload = {
        "schema_version": "1.0.0",
        "binding_id": str(binding_id or "").strip(),
        "scope": scope_token,
        "target_id": str(target_id or "").strip(),
        "profile_id": str(profile_id or "").strip(),
        "tick_applied": int(max(0, _as_int(tick_applied, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["binding_id"]) or (scope_token not in _BINDING_SCOPES) or (not payload["target_id"]) or (not payload["profile_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_profile_binding_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("scope", "")),
            str(item.get("target_id", "")),
            int(max(0, _as_int(item.get("tick_applied", 0), 0))),
            str(item.get("binding_id", "")),
        ),
    ):
        payload = build_profile_binding_row(
            binding_id=str(row.get("binding_id", "")).strip(),
            scope=str(row.get("scope", "")).strip().lower(),
            target_id=str(row.get("target_id", "")).strip(),
            profile_id=str(row.get("profile_id", "")).strip(),
            tick_applied=int(max(0, _as_int(row.get("tick_applied", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("binding_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def build_profile_exception_event_row(
    *,
    profile_id: str,
    rule_id: str,
    owner_id: str,
    tick: int,
    details: Mapping[str, object] | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    profile_token = str(profile_id or "").strip()
    rule_token = str(rule_id or "").strip()
    owner_token = str(owner_id or "").strip()
    tick_value = int(max(0, _as_int(tick, 0)))
    payload = {
        "schema_version": "1.0.0",
        "event_id": "event.profile.override.{}".format(
            canonical_sha256(
                {
                    "profile_id": profile_token,
                    "rule_id": rule_token,
                    "owner_id": owner_token,
                    "tick": tick_value,
                    "details": _as_map(details),
                }
            )[:16]
        ),
        "profile_id": profile_token,
        "rule_id": rule_token,
        "owner_id": owner_token,
        "tick": tick_value,
        "details": _as_map(details),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not profile_token) or (not rule_token) or (not owner_token):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _context_target(scope: str, owner_context: Mapping[str, object] | None) -> str:
    ctx = _as_map(owner_context)
    session_spec = _as_map(ctx.get("session_spec"))
    authority_context = _as_map(ctx.get("authority_context")) or _as_map(session_spec.get("authority_context"))
    universe_identity = _as_map(ctx.get("universe_identity"))
    if scope == "universe":
        return (
            str(ctx.get("universe_id", "")).strip()
            or str(universe_identity.get("universe_id", "")).strip()
            or str(session_spec.get("universe_id", "")).strip()
            or "*"
        )
    if scope == "session":
        return (
            str(ctx.get("session_id", "")).strip()
            or str(session_spec.get("session_id", "")).strip()
            or str(session_spec.get("save_id", "")).strip()
            or "*"
        )
    if scope == "authority":
        return (
            str(ctx.get("authority_id", "")).strip()
            or str(authority_context.get("authority_context_id", "")).strip()
            or str(authority_context.get("authority_origin", "")).strip()
            or "*"
        )
    if scope == "system":
        return str(ctx.get("system_id", "")).strip() or str(ctx.get("owner_id", "")).strip() or "*"
    return "*"


def _binding_rows_from_context(owner_context: Mapping[str, object] | None, explicit_rows: object) -> List[dict]:
    ctx = _as_map(owner_context)
    session_spec = _as_map(ctx.get("session_spec"))
    authority_context = _as_map(ctx.get("authority_context")) or _as_map(session_spec.get("authority_context"))
    system_template = _as_map(ctx.get("system_template"))
    rows = []
    for source in (
        explicit_rows,
        ctx.get("profile_binding_rows"),
        session_spec.get("profile_bindings"),
        authority_context.get("profile_bindings"),
        system_template.get("profile_bindings"),
    ):
        rows.extend([dict(item) for item in _as_list(source) if isinstance(item, Mapping)])
    return normalize_profile_binding_rows(rows)


def _profiles_by_id_from_inputs(
    *,
    owner_context: Mapping[str, object] | None,
    profile_rows: object,
    profile_registry_payload: Mapping[str, object] | None,
) -> Dict[str, dict]:
    ctx = _as_map(owner_context)
    rows: List[dict] = [dict(item) for item in _as_list(profile_rows) if isinstance(item, Mapping)]
    rows.extend(_rows_from_registry(profile_registry_payload, ("profiles",)))
    rows.extend(_rows_from_registry(_as_map(ctx.get("profile_registry_payload")), ("profiles",)))
    return profile_rows_by_id(rows)


def _trace_row(*, scope: str, target_id: str, profile_id: str, applied: bool, reason: str, value: object = None) -> dict:
    payload = {
        "scope": str(scope),
        "target_id": str(target_id),
        "profile_id": str(profile_id),
        "applied": bool(applied),
        "reason": str(reason),
        "value": value,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def resolve_profile(
    *,
    rule_id: str,
    owner_context: Mapping[str, object] | None,
    profile_registry_payload: Mapping[str, object] | None = None,
    profile_rows: object | None = None,
    profile_binding_rows: object | None = None,
) -> dict:
    rule_token = str(rule_id or "").strip()
    if not rule_token:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_PROFILE_INVALID,
            "message": "rule_id is required",
            "deterministic_fingerprint": canonical_sha256({"result": "refused", "refusal_code": REFUSAL_PROFILE_INVALID, "rule_id": ""}),
        }

    ctx = _as_map(owner_context)
    defaults = _as_map(ctx.get("rule_defaults"))
    baseline_value = defaults.get(rule_token)
    baseline_profile_id = ""
    effective_value = baseline_value
    effective_profile_id = ""
    effective_scope = "default"
    baseline_known = rule_token in defaults
    trace_rows: List[dict] = []

    profiles_by_id = _profiles_by_id_from_inputs(
        owner_context=ctx,
        profile_rows=profile_rows,
        profile_registry_payload=profile_registry_payload,
    )
    bindings = _binding_rows_from_context(ctx, profile_binding_rows)

    for scope in _BINDING_SCOPES:
        target_id = _context_target(scope, ctx)
        scope_rows = [
            dict(row)
            for row in bindings
            if str(row.get("scope", "")).strip().lower() == scope
            and str(row.get("target_id", "")).strip() in {"*", target_id}
        ]
        scope_rows = sorted(
            scope_rows,
            key=lambda row: (
                int(max(0, _as_int(row.get("tick_applied", 0), 0))),
                str(row.get("binding_id", "")),
                str(row.get("profile_id", "")),
            ),
        )
        for row in scope_rows:
            profile_id = str(row.get("profile_id", "")).strip()
            profile_row = dict(profiles_by_id.get(profile_id) or {})
            if not profile_row:
                trace_rows.append(
                    _trace_row(
                        scope=scope,
                        target_id=str(row.get("target_id", "")).strip(),
                        profile_id=profile_id,
                        applied=False,
                        reason="profile_missing",
                    )
                )
                continue
            overrides = _as_map(profile_row.get("overrides"))
            if rule_token not in overrides:
                trace_rows.append(
                    _trace_row(
                        scope=scope,
                        target_id=str(row.get("target_id", "")).strip(),
                        profile_id=profile_id,
                        applied=False,
                        reason="rule_not_declared",
                    )
                )
                continue
            value = overrides.get(rule_token)
            if scope == "universe":
                baseline_value = value
                baseline_profile_id = profile_id
                baseline_known = True
            effective_value = value
            effective_profile_id = profile_id
            effective_scope = scope
            trace_rows.append(
                _trace_row(
                    scope=scope,
                    target_id=str(row.get("target_id", "")).strip(),
                    profile_id=profile_id,
                    applied=True,
                    reason="rule_override_applied",
                    value=value,
                )
            )

    override_active = False
    if effective_scope in {"session", "authority", "system"}:
        override_active = (not baseline_known) or (effective_value != baseline_value)

    payload = {
        "result": "complete",
        "rule_id": rule_token,
        "baseline_value": baseline_value,
        "baseline_profile_id": baseline_profile_id,
        "effective_value": effective_value,
        "effective_profile_id": effective_profile_id,
        "effective_scope": effective_scope,
        "override_active": bool(override_active),
        "resolution_trace": trace_rows,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def apply_override(
    *,
    rule_id: str,
    owner_id: str,
    tick: int,
    owner_context: Mapping[str, object] | None,
    profile_registry_payload: Mapping[str, object] | None = None,
    profile_rows: object | None = None,
    profile_binding_rows: object | None = None,
    law_profile_row: Mapping[str, object] | None = None,
    details: Mapping[str, object] | None = None,
) -> dict:
    resolution = resolve_profile(
        rule_id=rule_id,
        owner_context=owner_context,
        profile_registry_payload=profile_registry_payload,
        profile_rows=profile_rows,
        profile_binding_rows=profile_binding_rows,
    )
    if str(resolution.get("result", "")).strip() != "complete":
        return dict(resolution)

    override_active = bool(resolution.get("override_active", False))
    allowed_rule_ids = _tokens(
        _as_map(law_profile_row).get("profile_override_allowed_rule_ids")
        or _as_map(_as_map(law_profile_row).get("extensions")).get("profile_override_allowed_rule_ids")
    )
    if override_active and allowed_rule_ids and ("*" not in allowed_rule_ids) and (str(rule_id or "").strip() not in set(allowed_rule_ids)):
        payload = {
            "result": "refused",
            "refusal_code": REFUSAL_PROFILE_OVERRIDE_NOT_ALLOWED,
            "rule_id": str(rule_id or "").strip(),
            "owner_id": str(owner_id or "").strip(),
            "allowed_rule_ids": allowed_rule_ids,
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    event_row = {}
    if override_active:
        event_row = build_profile_exception_event_row(
            profile_id=str(resolution.get("effective_profile_id", "")).strip(),
            rule_id=str(rule_id or "").strip(),
            owner_id=str(owner_id or "").strip(),
            tick=int(max(0, _as_int(tick, 0))),
            details={
                "baseline_value": resolution.get("baseline_value"),
                "effective_value": resolution.get("effective_value"),
                "effective_scope": str(resolution.get("effective_scope", "")).strip(),
                **_as_map(details),
            },
            extensions={"source": "META-PROFILE0"},
        )

    payload = {
        "result": "complete",
        "rule_id": str(rule_id or "").strip(),
        "owner_id": str(owner_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "resolution": dict(resolution),
        "override_active": bool(override_active),
        "exception_event": dict(event_row) if event_row else None,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def resolve_effective_profile_snapshot(
    *,
    owner_context: Mapping[str, object] | None,
    profile_registry_payload: Mapping[str, object] | None = None,
    profile_rows: object | None = None,
    profile_binding_rows: object | None = None,
) -> dict:
    ctx = _as_map(owner_context)
    profiles_by_id = _profiles_by_id_from_inputs(
        owner_context=ctx,
        profile_rows=profile_rows,
        profile_registry_payload=profile_registry_payload,
    )
    bindings = _binding_rows_from_context(ctx, profile_binding_rows)
    snapshot: Dict[str, str] = {}
    provenance_rows: List[dict] = []

    for scope in _BINDING_SCOPES:
        target_id = _context_target(scope, ctx)
        scope_rows = [
            dict(row)
            for row in bindings
            if str(row.get("scope", "")).strip().lower() == scope
            and str(row.get("target_id", "")).strip() in {"*", target_id}
        ]
        scope_rows = sorted(
            scope_rows,
            key=lambda row: (
                int(max(0, _as_int(row.get("tick_applied", 0), 0))),
                str(row.get("binding_id", "")),
                str(row.get("profile_id", "")),
            ),
        )
        for row in scope_rows:
            profile_id = str(row.get("profile_id", "")).strip()
            profile_row = dict(profiles_by_id.get(profile_id) or {})
            profile_type = str(profile_row.get("profile_type", "")).strip().lower()
            if not profile_row or profile_type not in _PROFILE_TYPES:
                continue
            snapshot[profile_type] = profile_id
            provenance_rows.append(
                {
                    "scope": scope,
                    "target_id": str(row.get("target_id", "")).strip(),
                    "profile_type": profile_type,
                    "profile_id": profile_id,
                    "binding_id": str(row.get("binding_id", "")).strip(),
                }
            )

    payload = {
        "snapshot": dict((key, snapshot[key]) for key in sorted(snapshot.keys())),
        "provenance": sorted(
            [dict(row) for row in provenance_rows],
            key=lambda row: (
                str(row.get("profile_type", "")),
                str(row.get("scope", "")),
                str(row.get("target_id", "")),
                str(row.get("binding_id", "")),
            ),
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
