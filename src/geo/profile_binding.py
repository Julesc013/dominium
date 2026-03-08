"""GEO profile binding helpers layered on META-PROFILE."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.meta.profile import build_profile_exception_event_row, resolve_effective_profile_snapshot

from .kernel.geo_kernel import (
    _as_map,
    _dimension_from_topology,
    _projection_row,
    _topology_row,
    _metric_row,
    _partition_row,
)


REFUSAL_GEO_DIMENSION_CHANGE = "refusal.geo.dimension_change"
GEO_RULE_TO_PROFILE_KEY = {
    "rule.geo.topology_profile_id": "topology",
    "rule.geo.metric_profile_id": "metric",
    "rule.geo.partition_profile_id": "partition",
    "rule.geo.projection_profile_id": "projection",
}


def _baseline_geo_profile_set(universe_identity: Mapping[str, object] | None) -> dict:
    payload = _as_map(universe_identity)
    return {
        "topology_profile_id": str(payload.get("topology_profile_id", "geo.topology.r3_infinite")).strip() or "geo.topology.r3_infinite",
        "metric_profile_id": str(payload.get("metric_profile_id", "geo.metric.euclidean")).strip() or "geo.metric.euclidean",
        "partition_profile_id": str(payload.get("partition_profile_id", "geo.partition.grid_zd")).strip() or "geo.partition.grid_zd",
        "projection_profile_id": str(payload.get("projection_profile_id", "geo.projection.perspective_3d")).strip()
        or "geo.projection.perspective_3d",
    }


def _profile_dimension(profile_id: str, topology_registry_payload: Mapping[str, object] | None) -> int:
    row = _topology_row(str(profile_id), registry_payload=topology_registry_payload)
    if not row:
        return 0
    return _dimension_from_topology(row)


def _effective_geo_profile_set(
    baseline: Mapping[str, object],
    snapshot: Mapping[str, object],
) -> dict:
    snap = _as_map(snapshot)
    return {
        "topology_profile_id": str(snap.get("topology", "")).strip() or str(baseline.get("topology_profile_id", "")),
        "metric_profile_id": str(snap.get("metric", "")).strip() or str(baseline.get("metric_profile_id", "")),
        "partition_profile_id": str(snap.get("partition", "")).strip() or str(baseline.get("partition_profile_id", "")),
        "projection_profile_id": str(snap.get("projection", "")).strip() or str(baseline.get("projection_profile_id", "")),
    }


def _exception_event(
    *,
    rule_id: str,
    effective_profile_id: str,
    owner_id: str,
    tick: int,
    baseline_value: str,
    effective_value: str,
    details: Mapping[str, object] | None = None,
) -> dict:
    return build_profile_exception_event_row(
        profile_id=str(effective_profile_id),
        rule_id=str(rule_id),
        owner_id=str(owner_id),
        tick=int(max(0, int(tick))),
        details={
            "baseline_value": str(baseline_value),
            "effective_value": str(effective_value),
            **_as_map(details),
        },
        extensions={"source": "GEO0-5"},
    )


def resolve_geo_profile_set(
    *,
    universe_identity: Mapping[str, object] | None,
    owner_context: Mapping[str, object] | None,
    profile_registry_payload: Mapping[str, object] | None = None,
    profile_rows: object | None = None,
    profile_binding_rows: object | None = None,
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
    projection_registry_payload: Mapping[str, object] | None = None,
    tick: int = 0,
    owner_id: str = "",
) -> dict:
    baseline = _baseline_geo_profile_set(universe_identity)
    snapshot_payload = resolve_effective_profile_snapshot(
        owner_context=owner_context,
        profile_registry_payload=profile_registry_payload,
        profile_rows=profile_rows,
        profile_binding_rows=profile_binding_rows,
    )
    snapshot = _as_map(snapshot_payload.get("snapshot"))
    effective = _effective_geo_profile_set(baseline, snapshot)

    owner_token = str(owner_id).strip() or str(_as_map(owner_context).get("session_id", "")).strip() or "*"
    exception_events = []
    for rule_id, snapshot_key in GEO_RULE_TO_PROFILE_KEY.items():
        baseline_key = str(rule_id).split(".", 2)[-1]
        baseline_value = str(baseline.get(baseline_key, "")).strip()
        effective_value = str(
            effective.get(
                baseline_key,
                effective.get("{}_profile_id".format(snapshot_key), ""),
            )
        ).strip()
        if baseline_value and effective_value and baseline_value != effective_value:
            exception_events.append(
                _exception_event(
                    rule_id=rule_id,
                    effective_profile_id=effective_value,
                    owner_id=owner_token,
                    tick=tick,
                    baseline_value=baseline_value,
                    effective_value=effective_value,
                )
            )

    baseline_dimension = _profile_dimension(
        str(baseline.get("topology_profile_id", "")),
        topology_registry_payload=topology_registry_payload,
    )
    effective_dimension = _profile_dimension(
        str(effective.get("topology_profile_id", "")),
        topology_registry_payload=topology_registry_payload,
    )
    if (
        str(baseline.get("topology_profile_id", "")) != str(effective.get("topology_profile_id", ""))
        and baseline_dimension
        and effective_dimension
        and baseline_dimension != effective_dimension
    ):
        payload = {
            "result": "refused",
            "refusal_code": REFUSAL_GEO_DIMENSION_CHANGE,
            "message": "topology override changes dimension mid-session",
            "baseline": dict(baseline),
            "effective": dict(effective),
            "exception_events": [dict(row) for row in exception_events],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    topology_row = _topology_row(str(effective.get("topology_profile_id", "")), registry_payload=topology_registry_payload)
    metric_row = _metric_row(str(effective.get("metric_profile_id", "")), registry_payload=metric_registry_payload)
    partition_row = _partition_row(str(effective.get("partition_profile_id", "")), registry_payload=partition_registry_payload)
    projection_row = _projection_row(str(effective.get("projection_profile_id", "")), registry_payload=projection_registry_payload)
    payload = {
        "result": "complete",
        "baseline": dict(baseline),
        "effective": dict(effective),
        "effective_dimension_D": int(effective_dimension or baseline_dimension or 0),
        "override_active": bool(exception_events),
        "exception_events": [dict(row) for row in exception_events],
        "snapshot": dict(snapshot),
        "topology_row": dict(topology_row) if topology_row else None,
        "metric_row": dict(metric_row) if metric_row else None,
        "partition_row": dict(partition_row) if partition_row else None,
        "projection_row": dict(projection_row) if projection_row else None,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
