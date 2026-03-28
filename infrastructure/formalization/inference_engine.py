"""Deterministic FORM-1 inference engine (derived-only)."""

from __future__ import annotations

import hashlib
from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_TARGET_KINDS = {"track", "road", "path", "canal", "tunnel", "custom"}
_VALID_CANDIDATE_KINDS = {"spline", "corridor", "volume", "graph_stub"}


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


def _token_hash_int(token: str) -> int:
    digest = hashlib.sha256(str(token).encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def _candidate_kind_token(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_CANDIDATE_KINDS:
        return token
    return "corridor"


def _target_kind_token(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_TARGET_KINDS:
        return token
    return "custom"


def _regularity_score(source_ids: List[str]) -> int:
    if len(source_ids) < 3:
        return 500
    samples = sorted(_token_hash_int(token) for token in source_ids)
    deltas = [abs(samples[i + 1] - samples[i]) for i in range(len(samples) - 1)]
    if not deltas:
        return 500
    avg = sum(deltas) // len(deltas)
    variance = sum(abs(delta - avg) for delta in deltas) // len(deltas)
    if avg <= 0:
        return 250
    noise_permille = min(1000, int((variance * 1000) // avg))
    return int(max(0, 1000 - noise_permille))


def _confidence_score(*, source_ids: List[str], candidate_kind: str) -> int:
    regularity = _regularity_score(source_ids)
    coverage = min(1000, 200 + len(source_ids) * 80)
    kind_bonus = {
        "corridor": 120,
        "spline": 180,
        "graph_stub": 90,
        "volume": 70,
    }.get(candidate_kind, 80)
    score = int((regularity * 6 + coverage * 3 + kind_bonus * 10) // 10)
    return int(max(0, min(1000, score)))


def _resource_estimate(*, source_ids: List[str], candidate_kind: str) -> dict:
    base = max(1, len(source_ids))
    multiplier = {
        "corridor": 4,
        "spline": 5,
        "graph_stub": 3,
        "volume": 6,
    }.get(candidate_kind, 4)
    return {
        "labor_units": int(base * multiplier),
        "material_units": int(base * max(1, multiplier - 1)),
    }


def build_inference_candidate(
    *,
    formalization_id: str,
    candidate_kind: str,
    geometry_preview_ref: str,
    confidence_score: int,
    required_resources_estimate: Mapping[str, object] | None = None,
    suggested_spec_ids: object = None,
    candidate_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    formalization_token = str(formalization_id).strip()
    kind_token = _candidate_kind_token(candidate_kind)
    preview_token = str(geometry_preview_ref).strip()
    ext = _canon(dict(extensions or {}))
    spec_ids = _sorted_unique_strings(suggested_spec_ids)
    resources = _canon(dict(required_resources_estimate or {})) if isinstance(required_resources_estimate, Mapping) else None
    confidence = int(max(0, min(1000, _as_int(confidence_score, 0))))

    normalized_candidate_id = str(candidate_id).strip()
    if not normalized_candidate_id:
        normalized_candidate_id = "candidate.{}".format(
            canonical_sha256(
                {
                    "formalization_id": formalization_token,
                    "candidate_kind": kind_token,
                    "geometry_preview_ref": preview_token,
                    "confidence_score": int(confidence),
                    "required_resources_estimate": resources,
                    "suggested_spec_ids": list(spec_ids),
                    "extensions": ext,
                }
            )[:16]
        )

    payload = {
        "schema_version": "1.0.0",
        "candidate_id": normalized_candidate_id,
        "formalization_id": formalization_token,
        "candidate_kind": kind_token,
        "geometry_preview_ref": preview_token,
        "confidence_score": int(confidence),
        "required_resources_estimate": resources,
        "suggested_spec_ids": list(spec_ids) if spec_ids else None,
        "deterministic_fingerprint": "",
        "extensions": ext,
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_inference_candidate_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    by_id: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("formalization_id", "")),
            str(item.get("candidate_kind", "")),
            str(item.get("candidate_id", "")),
        ),
    ):
        formalization_id = str(row.get("formalization_id", "")).strip()
        geometry_preview_ref = str(row.get("geometry_preview_ref", "")).strip()
        if (not formalization_id) or (not geometry_preview_ref):
            continue
        candidate = build_inference_candidate(
            candidate_id=str(row.get("candidate_id", "")).strip(),
            formalization_id=formalization_id,
            candidate_kind=str(row.get("candidate_kind", "")).strip(),
            geometry_preview_ref=geometry_preview_ref,
            confidence_score=_as_int(row.get("confidence_score", 0), 0),
            required_resources_estimate=_as_map(row.get("required_resources_estimate")),
            suggested_spec_ids=row.get("suggested_spec_ids"),
            extensions=_as_map(row.get("extensions")),
        )
        candidate_id = str(candidate.get("candidate_id", "")).strip()
        if candidate_id:
            by_id[candidate_id] = candidate
    return sorted(
        (dict(by_id[key]) for key in sorted(by_id.keys())),
        key=lambda row: (
            str(row.get("formalization_id", "")),
            str(row.get("candidate_kind", "")),
            str(row.get("candidate_id", "")),
        ),
    )


def infer_candidates(
    *,
    formalization_id: str,
    target_kind: str,
    target_context_id: str,
    raw_sources: object,
    current_tick: int,
    max_search_cost_units: int,
    cost_units_per_candidate: int = 1,
    max_candidates_cap: int = 64,
    suggested_spec_ids: object = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    formalization_token = str(formalization_id).strip()
    target_kind_token = _target_kind_token(target_kind)
    context_token = str(target_context_id).strip()
    source_ids = _sorted_unique_strings(raw_sources)
    unit_cost = max(1, _as_int(cost_units_per_candidate, 1))
    budget = max(0, _as_int(max_search_cost_units, 0))
    cap = max(0, _as_int(max_candidates_cap, 64))
    current = max(0, _as_int(current_tick, 0))

    seed_rows: List[dict] = []
    if len(source_ids) >= 2:
        seed_rows.append(
            {
                "candidate_kind": "corridor",
                "source_subset": [source_ids[0], source_ids[-1]],
            }
        )
        seed_rows.append(
            {
                "candidate_kind": "graph_stub",
                "source_subset": list(source_ids),
            }
        )
        for index in range(len(source_ids) - 1):
            seed_rows.append(
                {
                    "candidate_kind": "corridor",
                    "source_subset": [source_ids[index], source_ids[index + 1]],
                }
            )
    if len(source_ids) >= 3:
        middle = source_ids[len(source_ids) // 2]
        seed_rows.append(
            {
                "candidate_kind": "spline",
                "source_subset": [source_ids[0], middle, source_ids[-1]],
            }
        )

    normalized_seed_rows = sorted(
        [dict(item) for item in seed_rows if isinstance(item, dict)],
        key=lambda item: (
            str(item.get("candidate_kind", "")),
            ":".join(_sorted_unique_strings(item.get("source_subset"))),
        ),
    )

    candidates: List[dict] = []
    for seed in normalized_seed_rows:
        kind = _candidate_kind_token(seed.get("candidate_kind"))
        subset = _sorted_unique_strings(seed.get("source_subset"))
        if not subset:
            continue
        preview_ref = "preview.formalization.{}".format(
            canonical_sha256(
                {
                    "formalization_id": formalization_token,
                    "target_kind": target_kind_token,
                    "target_context_id": context_token,
                    "candidate_kind": kind,
                    "source_subset": list(subset),
                    "tick": int(current),
                }
            )[:16]
        )
        candidate = build_inference_candidate(
            formalization_id=formalization_token,
            candidate_kind=kind,
            geometry_preview_ref=preview_ref,
            confidence_score=_confidence_score(source_ids=subset, candidate_kind=kind),
            required_resources_estimate=_resource_estimate(source_ids=subset, candidate_kind=kind),
            suggested_spec_ids=suggested_spec_ids,
            extensions={
                "target_kind": target_kind_token,
                "target_context_id": context_token,
                "source_subset": list(subset),
                **dict(extensions or {}),
            },
        )
        candidates.append(candidate)

    candidates = normalize_inference_candidate_rows(candidates)
    max_candidates_from_budget = min(cap, (budget // unit_cost) if unit_cost > 0 else 0)
    if budget <= 0:
        max_candidates_from_budget = 0
    selected = list(candidates[:max_candidates_from_budget]) if max_candidates_from_budget > 0 else []

    possible_count = len(candidates)
    selected_count = len(selected)
    query_cost_units = int(selected_count * unit_cost)
    degraded = bool(selected_count < possible_count)
    degrade_reason = ""
    if degraded:
        degrade_reason = "degrade.formalization.inference_budget"

    result = {
        "formalization_id": formalization_token,
        "target_kind": target_kind_token,
        "target_context_id": context_token,
        "current_tick": int(current),
        "raw_source_count": int(len(source_ids)),
        "possible_candidate_count": int(possible_count),
        "candidate_count": int(selected_count),
        "query_cost_units": int(query_cost_units),
        "degraded": bool(degraded),
        "degrade_reason": degrade_reason or None,
        "candidates": [dict(row) for row in selected],
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


__all__ = [
    "build_inference_candidate",
    "infer_candidates",
    "normalize_inference_candidate_rows",
]
