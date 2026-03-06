"""PROC-7 deterministic experiment execution helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_EXPERIMENT_INVALID = "refusal.process.experiment.invalid"
REFUSAL_EXPERIMENT_UNKNOWN = "refusal.process.experiment.unknown"
REFUSAL_EXPERIMENT_PROCESS_UNKNOWN = "refusal.process.experiment.process_unknown"


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


def _split_process_definition_ref(ref_token: str) -> Tuple[str, str]:
    token = _token(ref_token)
    if not token:
        return "", "1.0.0"
    if "@" in token:
        process_id, version = token.split("@", 1)
        return _token(process_id), _token(version) or "1.0.0"
    return token, "1.0.0"


def build_experiment_definition_row(
    *,
    experiment_id: str,
    process_definition_ref: str,
    hypothesis_text_ref: str | None,
    variable_defs: object,
    measurement_plan_ref: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "experiment_id": _token(experiment_id),
        "process_definition_ref": _token(process_definition_ref),
        "hypothesis_text_ref": (
            None if hypothesis_text_ref is None else _token(hypothesis_text_ref) or None
        ),
        "variable_defs": [dict(row) for row in _as_list(variable_defs) if isinstance(row, Mapping)],
        "measurement_plan_ref": _token(measurement_plan_ref),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (
        (not payload["experiment_id"])
        or (not payload["process_definition_ref"])
        or (not payload["measurement_plan_ref"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_experiment_definition_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: _token(item.get("experiment_id")),
    ):
        normalized = build_experiment_definition_row(
            experiment_id=_token(row.get("experiment_id")),
            process_definition_ref=_token(row.get("process_definition_ref")),
            hypothesis_text_ref=(
                None
                if row.get("hypothesis_text_ref") is None
                else _token(row.get("hypothesis_text_ref")) or None
            ),
            variable_defs=row.get("variable_defs"),
            measurement_plan_ref=_token(row.get("measurement_plan_ref")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        experiment_id = _token(normalized.get("experiment_id"))
        if experiment_id:
            out[experiment_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def experiment_definition_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_experiment_definition_rows(rows):
        token = _token(row.get("experiment_id"))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_experiment_result_row(
    *,
    result_id: str,
    experiment_id: str,
    run_id: str,
    measured_values: Mapping[str, object] | None,
    confidence_bounds: Mapping[str, object] | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "result_id": _token(result_id),
        "experiment_id": _token(experiment_id),
        "run_id": _token(run_id),
        "measured_values": dict(sorted(_as_map(measured_values).items(), key=lambda item: str(item[0]))),
        "confidence_bounds": dict(
            sorted(_as_map(confidence_bounds).items(), key=lambda item: str(item[0]))
        ),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (not payload["experiment_id"]) or (not payload["run_id"]):
        return {}
    if not payload["result_id"]:
        payload["result_id"] = "result.experiment.{}".format(
            canonical_sha256(
                {
                    "experiment_id": payload["experiment_id"],
                    "run_id": payload["run_id"],
                    "measured_values": dict(payload["measured_values"]),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_experiment_result_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("experiment_id")), _token(item.get("result_id"))),
    ):
        normalized = build_experiment_result_row(
            result_id=_token(row.get("result_id")),
            experiment_id=_token(row.get("experiment_id")),
            run_id=_token(row.get("run_id")),
            measured_values=_as_map(row.get("measured_values")),
            confidence_bounds=_as_map(row.get("confidence_bounds")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        result_id = _token(normalized.get("result_id"))
        if result_id:
            out[result_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def evaluate_experiment_run_start(
    *,
    current_tick: int,
    experiment_id: str,
    run_id: str | None,
    experiment_definition_rows: object,
    process_definition_rows: object,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    experiment_token = _token(experiment_id)
    experiment_map = experiment_definition_rows_by_id(experiment_definition_rows)
    experiment_row = dict(experiment_map.get(experiment_token) or {})
    if not experiment_row:
        return {
            "result": "refusal",
            "refusal_code": REFUSAL_EXPERIMENT_UNKNOWN,
            "deterministic_fingerprint": canonical_sha256(
                {
                    "result": "refusal",
                    "refusal_code": REFUSAL_EXPERIMENT_UNKNOWN,
                    "experiment_id": experiment_token,
                    "tick": tick,
                }
            ),
        }

    process_id, version = _split_process_definition_ref(
        _token(experiment_row.get("process_definition_ref"))
    )
    process_exists = False
    for row in sorted(
        (dict(item) for item in _as_list(process_definition_rows) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("process_id")), _token(item.get("version"))),
    ):
        if _token(row.get("process_id")) != process_id:
            continue
        if (_token(row.get("version")) or "1.0.0") != version:
            continue
        process_exists = True
        break
    if not process_exists:
        return {
            "result": "refusal",
            "refusal_code": REFUSAL_EXPERIMENT_PROCESS_UNKNOWN,
            "deterministic_fingerprint": canonical_sha256(
                {
                    "result": "refusal",
                    "refusal_code": REFUSAL_EXPERIMENT_PROCESS_UNKNOWN,
                    "experiment_id": experiment_token,
                    "process_definition_ref": _token(experiment_row.get("process_definition_ref")),
                    "tick": tick,
                }
            ),
        }

    run_token = _token(run_id) or "run.experiment.{}".format(
        canonical_sha256(
            {
                "experiment_id": experiment_token,
                "tick": tick,
            }
        )[:16]
    )
    binding_row = {
        "schema_version": "1.0.0",
        "experiment_id": experiment_token,
        "run_id": run_token,
        "process_id": process_id,
        "version": version,
        "start_tick": tick,
        "status": "running",
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    binding_row["deterministic_fingerprint"] = canonical_sha256(
        dict(binding_row, deterministic_fingerprint="")
    )
    return {
        "result": "complete",
        "experiment_definition_row": dict(experiment_row),
        "binding_row": dict(binding_row),
        "deterministic_fingerprint": canonical_sha256(
            {
                "result": "complete",
                "experiment_id": experiment_token,
                "run_id": run_token,
                "tick": tick,
            }
        ),
    }


def evaluate_experiment_run_complete(
    *,
    current_tick: int,
    experiment_id: str,
    run_id: str,
    measurement_rows: object,
    confidence_floor_permille: int = 250,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    experiment_token = _token(experiment_id)
    run_token = _token(run_id)
    if (not experiment_token) or (not run_token):
        return {
            "result": "refusal",
            "refusal_code": REFUSAL_EXPERIMENT_INVALID,
            "deterministic_fingerprint": canonical_sha256(
                {
                    "result": "refusal",
                    "refusal_code": REFUSAL_EXPERIMENT_INVALID,
                    "experiment_id": experiment_token,
                    "run_id": run_token,
                    "tick": tick,
                }
            ),
        }

    measured_values: Dict[str, object] = {}
    confidence_bounds: Dict[str, object] = {}
    for row in sorted(
        (dict(item) for item in _as_list(measurement_rows) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("measurement_id")), _token(item.get("pollutant_id"))),
    ):
        measurement_id = _token(row.get("measurement_id"))
        if not measurement_id:
            continue
        measured_value = int(max(0, _as_int(row.get("measured_concentration", row.get("value", 0)), 0)))
        measured_values[measurement_id] = measured_value
        spread = int(
            max(
                0,
                min(
                    measured_value,
                    (_token(row.get("calibration_cert_id")) and 0)
                    or max(1, measured_value // 20),
                ),
            )
        )
        confidence_bounds[measurement_id] = {
            "lower": int(max(0, measured_value - spread)),
            "upper": int(max(0, measured_value + spread)),
            "confidence_permille": int(
                max(
                    0,
                    min(
                        1000,
                        max(
                            int(max(0, min(1000, _as_int(confidence_floor_permille, 250)))),
                            1000 - min(750, spread),
                        ),
                    ),
                )
            ),
        }

    result_row = build_experiment_result_row(
        result_id="result.experiment.{}".format(
            canonical_sha256(
                {
                    "experiment_id": experiment_token,
                    "run_id": run_token,
                    "tick": tick,
                    "measurement_ids": _tokens(measured_values.keys()),
                }
            )[:16]
        ),
        experiment_id=experiment_token,
        run_id=run_token,
        measured_values=measured_values,
        confidence_bounds=confidence_bounds,
        deterministic_fingerprint="",
        extensions=dict(
            _as_map(extensions),
            measurement_count=int(len(measured_values)),
            tick=int(tick),
        ),
    )
    return {
        "result": "complete",
        "experiment_result_row": dict(result_row),
        "deterministic_fingerprint": canonical_sha256(
            {
                "result": "complete",
                "experiment_id": experiment_token,
                "run_id": run_token,
                "result_id": _token(result_row.get("result_id")),
            }
        ),
    }
