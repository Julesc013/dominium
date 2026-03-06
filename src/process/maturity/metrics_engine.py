"""PROC-4 deterministic process metrics aggregation helpers."""

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


def _rows_from_registry(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    body = _as_map(payload)
    if isinstance(body.get(key), list):
        return [dict(item) for item in _as_list(body.get(key)) if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    if isinstance(record.get(key), list):
        return [dict(item) for item in _as_list(record.get(key)) if isinstance(item, Mapping)]
    return []


def _metric_key(process_id: object, version: object) -> str:
    pid = _token(process_id)
    ver = _token(version) or "1.0.0"
    return "{}@{}".format(pid, ver) if pid else ""


def _hash_deviation(prev_hash: str, current_hash: str) -> int:
    prev = _token(prev_hash).lower()
    cur = _token(current_hash).lower()
    if (not prev) or (not cur) or prev == cur:
        return 0
    marker = int(canonical_sha256({"prev": prev, "cur": cur})[:8], 16)
    return int(max(0, min(1000, 50 + (marker % 251))))


def _id_deviation(prev_id: str, current_id: str) -> int:
    prev = _token(prev_id).lower()
    cur = _token(current_id).lower()
    if (not prev) or (not cur) or prev == cur:
        return 0
    marker = int(canonical_sha256({"prev": prev, "cur": cur, "kind": "calibration"})[:8], 16)
    return int(max(0, min(1000, 75 + (marker % 201))))


def build_process_metrics_state_row(
    *,
    process_id: str,
    version: str,
    runs_count: int,
    yield_mean: int,
    yield_variance: int,
    defect_rate: int,
    qc_pass_rate: int,
    env_deviation_score: int,
    calibration_deviation_score: int,
    last_update_tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    if not process_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "process_id": process_token,
        "version": version_token,
        "runs_count": int(max(0, _as_int(runs_count, 0))),
        "yield_mean": int(max(0, min(1000, _as_int(yield_mean, 0)))),
        "yield_variance": int(max(0, _as_int(yield_variance, 0))),
        "defect_rate": int(max(0, min(1000, _as_int(defect_rate, 0)))),
        "qc_pass_rate": int(max(0, min(1000, _as_int(qc_pass_rate, 0)))),
        "env_deviation_score": int(max(0, min(1000, _as_int(env_deviation_score, 0)))),
        "calibration_deviation_score": int(
            max(0, min(1000, _as_int(calibration_deviation_score, 0)))
        ),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_process_metrics_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            _token(item.get("process_id")),
            _token(item.get("version")) or "1.0.0",
            int(max(0, _as_int(item.get("last_update_tick", 0), 0))),
        ),
    ):
        normalized = build_process_metrics_state_row(
            process_id=_token(row.get("process_id")),
            version=_token(row.get("version")) or "1.0.0",
            runs_count=int(max(0, _as_int(row.get("runs_count", 0), 0))),
            yield_mean=int(max(0, min(1000, _as_int(row.get("yield_mean", 0), 0)))),
            yield_variance=int(max(0, _as_int(row.get("yield_variance", 0), 0))),
            defect_rate=int(max(0, min(1000, _as_int(row.get("defect_rate", 0), 0)))),
            qc_pass_rate=int(max(0, min(1000, _as_int(row.get("qc_pass_rate", 0), 0)))),
            env_deviation_score=int(
                max(0, min(1000, _as_int(row.get("env_deviation_score", 0), 0)))
            ),
            calibration_deviation_score=int(
                max(0, min(1000, _as_int(row.get("calibration_deviation_score", 0), 0)))
            ),
            last_update_tick=int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        key = _metric_key(normalized.get("process_id"), normalized.get("version"))
        if key:
            out[key] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def process_metrics_rows_by_key(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_process_metrics_state_rows(rows):
        key = _metric_key(row.get("process_id"), row.get("version"))
        if key:
            out[key] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def stabilization_policy_rows_by_id(
    registry_payload: Mapping[str, object] | None,
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(registry_payload, "stabilization_policies"):
        policy_id = _token(row.get("policy_id"))
        if not policy_id:
            continue
        weights = dict(
            (str(key).strip(), int(max(0, _as_int(value, 0))))
            for key, value in sorted(_as_map(row.get("weights")).items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
        thresholds = dict(
            (str(key).strip(), int(max(0, _as_int(value, 0))))
            for key, value in sorted(_as_map(row.get("thresholds")).items(), key=lambda item: str(item[0]))
            if str(key).strip()
        )
        payload = {
            "schema_version": "1.0.0",
            "policy_id": policy_id,
            "weights": weights,
            "thresholds": thresholds,
            "min_runs": int(max(0, _as_int(row.get("min_runs", 0), 0))),
            "stability_horizon_ticks": int(
                max(0, _as_int(row.get("stability_horizon_ticks", 0), 0))
            ),
            "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
            "extensions": _as_map(row.get("extensions")),
        }
        if not payload["deterministic_fingerprint"]:
            payload["deterministic_fingerprint"] = canonical_sha256(
                dict(payload, deterministic_fingerprint="")
            )
        out[policy_id] = payload
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def update_process_metrics_for_run(
    *,
    current_tick: int,
    process_id: str,
    version: str,
    previous_metrics_row: Mapping[str, object] | None,
    process_quality_row: Mapping[str, object] | None,
    qc_result_rows: object,
    environment_snapshot_hash: str | None,
    calibration_cert_id: str | None,
    update_stride: int = 1,
    force_update: bool = False,
    policy_id: str = "stab.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    stride = int(max(1, _as_int(update_stride, 1)))
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    prev_row = dict(previous_metrics_row or {})
    prev_ext = _as_map(prev_row.get("extensions"))

    if (not bool(force_update)) and stride > 1 and (tick % stride != 0):
        deferred = {
            "result": "deferred",
            "reason_code": "degrade.process.metrics_stride",
            "metrics_row": (
                dict(prev_row)
                if prev_row
                else build_process_metrics_state_row(
                    process_id=process_token,
                    version=version_token,
                    runs_count=0,
                    yield_mean=0,
                    yield_variance=0,
                    defect_rate=0,
                    qc_pass_rate=1000,
                    env_deviation_score=0,
                    calibration_deviation_score=0,
                    last_update_tick=0,
                    extensions={
                        "source": "PROC4-3",
                        "policy_id": _token(policy_id) or "stab.default",
                    },
                )
            ),
            "decision_log_row": {
                "tick": int(tick),
                "process_id": process_token,
                "version": version_token,
                "reason": "metrics_update_deferred",
                "reason_code": "degrade.process.metrics_stride",
                "update_stride": int(stride),
            },
        }
        deferred["deterministic_fingerprint"] = canonical_sha256(
            dict(deferred, deterministic_fingerprint="")
        )
        return deferred

    yield_sum = int(max(0, _as_int(prev_ext.get("yield_sum", 0), 0)))
    yield_sq_sum = int(max(0, _as_int(prev_ext.get("yield_sq_sum", 0), 0)))
    quality_samples = int(max(0, _as_int(prev_ext.get("quality_samples", 0), 0)))
    defect_sum = int(max(0, _as_int(prev_ext.get("defect_sum", 0), 0)))
    sampled_count = int(max(0, _as_int(prev_ext.get("sampled_count", 0), 0)))
    pass_count = int(max(0, _as_int(prev_ext.get("pass_count", 0), 0)))
    env_sum = int(max(0, _as_int(prev_ext.get("env_deviation_sum", 0), 0)))
    env_samples = int(max(0, _as_int(prev_ext.get("env_samples", 0), 0)))
    cal_sum = int(max(0, _as_int(prev_ext.get("calibration_deviation_sum", 0), 0)))
    cal_samples = int(max(0, _as_int(prev_ext.get("calibration_samples", 0), 0)))
    runs_count = int(max(0, _as_int(prev_row.get("runs_count", 0), 0)))

    quality = _as_map(process_quality_row)
    if quality:
        runs_count += 1
        quality_samples += 1
        yield_sample = int(max(0, min(1000, _as_int(quality.get("yield_factor", 0), 0))))
        defect_severity = int(
            max(
                0,
                min(
                    1000,
                    _as_int(_as_map(quality.get("extensions")).get("defect_severity", 0), 0),
                ),
            )
        )
        if defect_severity <= 0:
            defect_severity = int(max(0, min(1000, len(_as_list(quality.get("defect_flags"))) * 250)))
        yield_sum += yield_sample
        yield_sq_sum += yield_sample * yield_sample
        defect_sum += defect_severity

    for row in sorted(
        (dict(item) for item in _as_list(qc_result_rows) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("run_id")), _token(item.get("batch_id"))),
    ):
        if not bool(row.get("sampled", False)):
            continue
        sampled_count += 1
        if bool(row.get("passed", False)):
            pass_count += 1

    env_hash = _token(environment_snapshot_hash).lower()
    if env_hash:
        env_sum += _hash_deviation(_token(prev_ext.get("last_env_snapshot_hash")), env_hash)
        env_samples += 1
    cal_id = _token(calibration_cert_id).lower()
    if cal_id:
        cal_sum += _id_deviation(_token(prev_ext.get("last_calibration_cert_id")), cal_id)
        cal_samples += 1

    yield_mean = int((yield_sum // quality_samples) if quality_samples > 0 else 0)
    yield_variance = (
        int(max(0, (yield_sq_sum // quality_samples) - (yield_mean * yield_mean)))
        if quality_samples > 0
        else 0
    )
    defect_rate = int((defect_sum // quality_samples) if quality_samples > 0 else 0)
    qc_pass_rate = int((pass_count * 1000 // sampled_count) if sampled_count > 0 else 1000)
    env_deviation = int((env_sum // env_samples) if env_samples > 0 else 0)
    cal_deviation = int((cal_sum // cal_samples) if cal_samples > 0 else 0)

    row = build_process_metrics_state_row(
        process_id=process_token,
        version=version_token,
        runs_count=runs_count,
        yield_mean=yield_mean,
        yield_variance=yield_variance,
        defect_rate=defect_rate,
        qc_pass_rate=qc_pass_rate,
        env_deviation_score=env_deviation,
        calibration_deviation_score=cal_deviation,
        last_update_tick=tick,
        extensions={
            "source": "PROC4-3",
            "policy_id": _token(policy_id) or "stab.default",
            "yield_sum": int(yield_sum),
            "yield_sq_sum": int(yield_sq_sum),
            "quality_samples": int(quality_samples),
            "defect_sum": int(defect_sum),
            "sampled_count": int(sampled_count),
            "pass_count": int(pass_count),
            "env_deviation_sum": int(env_sum),
            "env_samples": int(env_samples),
            "calibration_deviation_sum": int(cal_sum),
            "calibration_samples": int(cal_samples),
            "last_env_snapshot_hash": env_hash,
            "last_calibration_cert_id": cal_id,
        },
    )
    result = {
        "result": "complete",
        "reason_code": "",
        "metrics_row": row,
        "decision_log_row": {
            "tick": int(tick),
            "process_id": process_token,
            "version": version_token,
            "reason": "metrics_updated",
            "runs_count": int(runs_count),
            "qc_pass_rate": int(qc_pass_rate),
            "yield_mean": int(yield_mean),
            "yield_variance": int(yield_variance),
        },
    }
    result["deterministic_fingerprint"] = canonical_sha256(
        dict(result, deterministic_fingerprint="")
    )
    return result


__all__ = [
    "build_process_metrics_state_row",
    "normalize_process_metrics_state_rows",
    "process_metrics_rows_by_key",
    "stabilization_policy_rows_by_id",
    "update_process_metrics_for_run",
]
