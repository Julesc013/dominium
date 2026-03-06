"""PROC-7 deterministic candidate inference helpers (derived-only artifacts)."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(_token(item) for item in list(values or []) if _token(item)))


def build_candidate_process_definition_row(
    *,
    candidate_id: str,
    inferred_from_artifact_ids: object,
    proposed_process_definition_ref: str,
    confidence_score: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "candidate_id": _token(candidate_id),
        "inferred_from_artifact_ids": _tokens(inferred_from_artifact_ids),
        "proposed_process_definition_ref": _token(proposed_process_definition_ref),
        "confidence_score": int(max(0, min(1000, _as_int(confidence_score, 0)))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (not payload["candidate_id"]) or (not payload["proposed_process_definition_ref"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_candidate_process_definition_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: _token(item.get("candidate_id")),
    ):
        normalized = build_candidate_process_definition_row(
            candidate_id=_token(row.get("candidate_id")),
            inferred_from_artifact_ids=row.get("inferred_from_artifact_ids"),
            proposed_process_definition_ref=_token(
                row.get("proposed_process_definition_ref")
            ),
            confidence_score=int(
                max(0, min(1000, _as_int(row.get("confidence_score", 0), 0)))
            ),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        candidate_id = _token(normalized.get("candidate_id"))
        if candidate_id:
            out[candidate_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def candidate_process_definition_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_candidate_process_definition_rows(rows):
        token = _token(row.get("candidate_id"))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_candidate_model_binding_row(
    *,
    candidate_binding_id: str,
    candidate_id: str,
    model_id: str | None,
    confidence_score: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "candidate_binding_id": _token(candidate_binding_id),
        "candidate_id": _token(candidate_id),
        "model_id": None if model_id is None else _token(model_id) or None,
        "confidence_score": int(max(0, min(1000, _as_int(confidence_score, 0)))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (not payload["candidate_binding_id"]) or (not payload["candidate_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_candidate_model_binding_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: _token(item.get("candidate_binding_id")),
    ):
        normalized = build_candidate_model_binding_row(
            candidate_binding_id=_token(row.get("candidate_binding_id")),
            candidate_id=_token(row.get("candidate_id")),
            model_id=(
                None if row.get("model_id") is None else _token(row.get("model_id")) or None
            ),
            confidence_score=int(
                max(0, min(1000, _as_int(row.get("confidence_score", 0), 0)))
            ),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        binding_id = _token(normalized.get("candidate_binding_id"))
        if binding_id:
            out[binding_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def infer_candidate_artifacts(
    *,
    current_tick: int,
    experiment_result_rows: object,
    reverse_engineering_record_rows: object,
    process_definition_ref_hint: str,
    model_id_hint: str | None = None,
    existing_candidate_rows: object = None,
    existing_candidate_model_binding_rows: object = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    experiment_rows = [
        dict(item)
        for item in _as_list(experiment_result_rows)
        if isinstance(item, Mapping)
        and _token(dict(item).get("result_id"))
    ]
    reverse_rows = [
        dict(item)
        for item in _as_list(reverse_engineering_record_rows)
        if isinstance(item, Mapping)
        and _token(dict(item).get("record_id"))
    ]
    artifact_ids = _tokens(
        list(_token(row.get("result_id")) for row in experiment_rows)
        + list(_token(row.get("record_id")) for row in reverse_rows)
    )
    if not artifact_ids:
        return {
            "result": "complete",
            "candidate_rows": normalize_candidate_process_definition_rows(
                existing_candidate_rows
            ),
            "candidate_model_binding_rows": normalize_candidate_model_binding_rows(
                existing_candidate_model_binding_rows
            ),
            "produced_candidate_ids": [],
            "deterministic_fingerprint": canonical_sha256(
                {
                    "result": "complete",
                    "tick": tick,
                    "artifact_ids": [],
                }
            ),
        }

    process_ref = _token(process_definition_ref_hint) or "process.unknown@1.0.0"
    evidence_count = int(len(artifact_ids))
    confidence_score = int(
        max(
            0,
            min(
                1000,
                120
                + min(500, evidence_count * 120)
                + min(200, len(experiment_rows) * 80)
                + min(180, len(reverse_rows) * 90),
            ),
        )
    )
    candidate_id = "candidate.process.{}".format(
        canonical_sha256(
            {
                "process_definition_ref": process_ref,
                "artifact_ids": list(artifact_ids),
            }
        )[:16]
    )
    candidate_row = build_candidate_process_definition_row(
        candidate_id=candidate_id,
        inferred_from_artifact_ids=artifact_ids,
        proposed_process_definition_ref=process_ref,
        confidence_score=confidence_score,
        deterministic_fingerprint="",
        extensions={
            "inference_source": "proc7.research",
            "inference_reason": "deterministic_evidence_merge",
            "experiment_result_count": int(len(experiment_rows)),
            "reverse_engineering_record_count": int(len(reverse_rows)),
            "tick": tick,
        },
    )

    model_id = _token(model_id_hint) or None
    candidate_binding_row = build_candidate_model_binding_row(
        candidate_binding_id="candidate.binding.{}".format(
            canonical_sha256(
                {
                    "candidate_id": candidate_id,
                    "model_id": model_id or "",
                    "tick": tick,
                }
            )[:16]
        ),
        candidate_id=candidate_id,
        model_id=model_id,
        confidence_score=int(max(0, min(1000, confidence_score - 80))),
        deterministic_fingerprint="",
        extensions={
            "inference_source": "proc7.research",
            "inference_reason": "deterministic_binding_hint",
            "tick": tick,
        },
    )

    candidate_rows_by_id = candidate_process_definition_rows_by_id(existing_candidate_rows)
    candidate_rows_by_id[candidate_id] = dict(candidate_row)
    candidate_rows = [dict(candidate_rows_by_id[key]) for key in sorted(candidate_rows_by_id.keys())]

    binding_rows = normalize_candidate_model_binding_rows(
        list(existing_candidate_model_binding_rows or [])
        + [dict(candidate_binding_row)]
    )
    return {
        "result": "complete",
        "candidate_rows": [dict(row) for row in candidate_rows],
        "candidate_model_binding_rows": [dict(row) for row in binding_rows],
        "produced_candidate_ids": [candidate_id],
        "deterministic_fingerprint": canonical_sha256(
            {
                "result": "complete",
                "candidate_id": candidate_id,
                "artifact_ids": list(artifact_ids),
                "confidence_score": confidence_score,
            }
        ),
    }
