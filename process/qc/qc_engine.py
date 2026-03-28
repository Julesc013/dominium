"""PROC-3 deterministic QC sampling and inspection helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_float(value: object, default_value: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def build_qc_result_record_row(
    *,
    run_id: str,
    batch_id: str,
    sampled: bool,
    passed: bool,
    fail_reason: str | None,
    action_taken: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "run_id": str(run_id or "").strip(),
        "batch_id": str(batch_id or "").strip(),
        "sampled": bool(sampled),
        "passed": bool(passed),
        "fail_reason": (None if fail_reason is None else str(fail_reason).strip() or None),
        "action_taken": str(action_taken or "").strip() or "none",
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["run_id"]) or (not payload["batch_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _rows_from_registry(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    body = _as_map(payload)
    if isinstance(body.get(key), list):
        return [dict(row) for row in _as_list(body.get(key)) if isinstance(row, Mapping)]
    record = _as_map(body.get("record"))
    if isinstance(record.get(key), list):
        return [dict(row) for row in _as_list(record.get(key)) if isinstance(row, Mapping)]
    return []


def qc_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(payload, "qc_policies"):
        token = str(row.get("qc_policy_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def sampling_strategy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(payload, "sampling_strategies"):
        token = str(row.get("sampling_strategy_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def test_procedure_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(payload, "test_procedures"):
        token = str(row.get("test_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def tolerance_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(payload, "tolerance_policies"):
        token = str(row.get("tolerance_policy_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _rate_permille(raw_value: object) -> int:
    raw = _as_float(raw_value, 0.0)
    if raw <= 1.0:
        return int(max(0, min(1000, round(raw * 1000.0))))
    return int(max(0, min(1000, round(raw))))


def _hash_marker(*, run_id: str, batch_id: str, qc_policy_id: str, strategy_id: str) -> int:
    seed = canonical_sha256(
        {
            "stream": "process.qc.sample",
            "run_id": str(run_id),
            "batch_id": str(batch_id),
            "qc_policy_id": str(qc_policy_id),
            "strategy_id": str(strategy_id),
        }
    )
    return int(seed[:8], 16) % 1000


def _risk_severity(batch_row: Mapping[str, object], process_quality_row: Mapping[str, object] | None) -> int:
    ext = _as_map(_as_map(process_quality_row).get("extensions"))
    from_quality = int(max(0, min(1000, _as_int(ext.get("defect_severity", 0), 0))))
    if from_quality > 0:
        return from_quality
    defect_count = len(_tokens(_as_map(batch_row).get("defect_flags")))
    contamination_count = len(_tokens(_as_map(batch_row).get("contamination_tags")))
    return int(max(0, min(1000, defect_count * 220 + contamination_count * 260)))


def _sampling_decision(
    *,
    run_id: str,
    batch_id: str,
    index: int,
    policy_row: Mapping[str, object],
    strategy_row: Mapping[str, object],
    process_quality_row: Mapping[str, object] | None,
    batch_row: Mapping[str, object],
) -> Tuple[bool, dict]:
    qc_policy_id = str(_as_map(policy_row).get("qc_policy_id", "")).strip()
    strategy_id = str(_as_map(strategy_row).get("sampling_strategy_id", "")).strip()
    ext = _as_map(_as_map(policy_row).get("extensions"))
    base_rate = _rate_permille(_as_map(policy_row).get("sampling_rate", 0))
    if base_rate <= 0:
        return False, {
            "strategy_id": strategy_id,
            "base_rate_permille": int(base_rate),
            "effective_rate_permille": 0,
            "reason": "rate_zero",
            "marker": 0,
        }

    marker = _hash_marker(
        run_id=str(run_id),
        batch_id=str(batch_id),
        qc_policy_id=str(qc_policy_id),
        strategy_id=str(strategy_id),
    )

    if strategy_id == "sample.every_n":
        every_n = int(max(1, _as_int(ext.get("every_n", 0), 0)))
        if every_n <= 1:
            derived_n = int(max(1, round(1000.0 / float(max(1, base_rate)))))
            every_n = int(max(1, derived_n))
        sampled = int(max(0, _as_int(index, 0))) % int(every_n) == 0
        return sampled, {
            "strategy_id": strategy_id,
            "base_rate_permille": int(base_rate),
            "effective_rate_permille": int(base_rate),
            "reason": "every_n",
            "every_n": int(every_n),
            "marker": int(marker),
        }

    if strategy_id == "sample.risk_weighted":
        risk_value = _risk_severity(batch_row=batch_row, process_quality_row=process_quality_row)
        uplift_factor = int(max(0, min(1000, _as_int(ext.get("risk_uplift_scale_permille", 500), 500))))
        uplift = int((risk_value * uplift_factor) // 1000)
        effective_rate = int(max(0, min(1000, base_rate + uplift)))
        sampled = int(marker) < int(effective_rate)
        return sampled, {
            "strategy_id": strategy_id,
            "base_rate_permille": int(base_rate),
            "effective_rate_permille": int(effective_rate),
            "reason": "risk_weighted",
            "risk_severity": int(risk_value),
            "risk_uplift_permille": int(uplift),
            "marker": int(marker),
        }

    sampled = int(marker) < int(base_rate)
    return sampled, {
        "strategy_id": strategy_id,
        "base_rate_permille": int(base_rate),
        "effective_rate_permille": int(base_rate),
        "reason": "hash_threshold",
        "marker": int(marker),
    }


def _measure_quantity(
    *,
    quantity_id: str,
    batch_row: Mapping[str, object],
    process_quality_row: Mapping[str, object] | None,
) -> int:
    token = str(quantity_id or "").strip()
    row = _as_map(batch_row)
    ext = _as_map(_as_map(process_quality_row).get("extensions"))

    if token == "quality.yield_factor":
        return int(max(0, min(1000, _as_int(row.get("yield_factor", 0), 0))))
    if token == "quality.contamination_present":
        return 1000 if _tokens(row.get("contamination_tags")) else 0
    if token == "quality.defect_count":
        return int(max(0, min(1000, len(_tokens(row.get("defect_flags"))))))
    if token == "quality.defect_severity":
        severity = int(max(0, min(1000, _as_int(ext.get("defect_severity", 0), 0))))
        if severity > 0:
            return severity
        return int(max(0, min(1000, len(_tokens(row.get("defect_flags")) * 250))))
    return int(max(0, _as_int(_as_map(ext.get("measurement_values")).get(token, 0), 0)))


def _threshold_ok(value: int, rule_row: Mapping[str, object], tolerance: int) -> bool:
    rule = _as_map(rule_row)
    minimum = rule.get("min")
    maximum = rule.get("max")
    equal_to = rule.get("eq")
    measured = int(max(0, _as_int(value, 0)))
    tol = int(max(0, _as_int(tolerance, 0)))

    if equal_to is not None:
        return abs(int(max(0, _as_int(equal_to, 0))) - measured) <= tol
    if minimum is not None and measured < int(max(0, _as_int(minimum, 0))) - tol:
        return False
    if maximum is not None and measured > int(max(0, _as_int(maximum, 0))) + tol:
        return False
    return True


def _test_tolerance(policy_row: Mapping[str, object] | None) -> int:
    numeric = _as_map(_as_map(policy_row).get("numeric_tolerances"))
    return int(max(0, _as_int(numeric.get("interface_offset_mm", 0), 0)))


def _fail_action_token(raw_token: object) -> str:
    token = str(raw_token or "").strip()
    if token in {"reject_batch", "quarantine"}:
        return "reject"
    if token == "rework_batch":
        return "rework"
    if token == "accept_with_warning":
        return "accept_warning"
    return "none"


def evaluate_qc_for_run(
    *,
    current_tick: int,
    run_id: str,
    qc_policy_id: str,
    batch_quality_rows: Sequence[Mapping[str, object]],
    process_quality_record_rows: Sequence[Mapping[str, object]] | None,
    qc_policy_registry_payload: Mapping[str, object] | None,
    sampling_strategy_registry_payload: Mapping[str, object] | None,
    test_procedure_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    instrument_id: str | None = None,
    calibration_cert_id: str | None = None,
    requester_subject_id: str | None = None,
) -> dict:
    run_token = str(run_id or "").strip()
    policy_token = str(qc_policy_id or "").strip() or "qc.none"
    tick = int(max(0, _as_int(current_tick, 0)))

    policy_rows = qc_policy_rows_by_id(qc_policy_registry_payload)
    strategy_rows = sampling_strategy_rows_by_id(sampling_strategy_registry_payload)
    test_rows = test_procedure_rows_by_id(test_procedure_registry_payload)
    tolerance_rows = tolerance_policy_rows_by_id(tolerance_policy_registry_payload)

    policy_row = dict(policy_rows.get(policy_token) or {})
    if not policy_row:
        policy_row = {
            "qc_policy_id": "qc.none",
            "sampling_rate": 0,
            "sampling_strategy_id": "sample.hash_based",
            "test_procedure_refs": [],
            "fail_action": "accept_with_warning",
            "extensions": {"fallback": "missing_policy_row"},
        }
    strategy_id = str(policy_row.get("sampling_strategy_id", "sample.hash_based")).strip() or "sample.hash_based"
    strategy_row = dict(strategy_rows.get(strategy_id) or {"sampling_strategy_id": strategy_id})

    process_quality_map = {
        str(_as_map(row).get("run_id", "")).strip(): dict(row)
        for row in list(process_quality_record_rows or [])
        if isinstance(row, Mapping) and str(_as_map(row).get("run_id", "")).strip()
    }
    quality_row = dict(process_quality_map.get(run_token) or {})

    batch_rows = sorted(
        [dict(row) for row in list(batch_quality_rows or []) if isinstance(row, Mapping)],
        key=lambda row: str(row.get("batch_id", "")),
    )

    qc_rows: List[dict] = []
    measurement_rows: List[dict] = []
    decision_rows: List[dict] = []
    rejected_ids: List[str] = []
    rework_ids: List[str] = []
    warning_ids: List[str] = []
    quarantine_ids: List[str] = []

    fail_action = str(policy_row.get("fail_action", "accept_with_warning")).strip() or "accept_with_warning"
    requested_tests = _tokens(policy_row.get("test_procedure_refs"))

    for index, row in enumerate(batch_rows):
        batch_token = str(row.get("batch_id", "")).strip()
        if not batch_token:
            continue

        sampled, decision_meta = _sampling_decision(
            run_id=run_token,
            batch_id=batch_token,
            index=int(index),
            policy_row=policy_row,
            strategy_row=strategy_row,
            process_quality_row=quality_row,
            batch_row=row,
        )
        decision_rows.append(
            {
                "run_id": run_token,
                "batch_id": batch_token,
                "tick": int(tick),
                "sampled": bool(sampled),
                "sampling_strategy_id": str(strategy_id),
                "sampling_details": dict(decision_meta),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "run_id": run_token,
                        "batch_id": batch_token,
                        "sampled": bool(sampled),
                        "sampling_details": dict(decision_meta),
                    }
                ),
            }
        )

        if not sampled:
            qc_row = build_qc_result_record_row(
                run_id=run_token,
                batch_id=batch_token,
                sampled=False,
                passed=True,
                fail_reason=None,
                action_taken="none",
                tick=int(tick),
                extensions={
                    "qc_policy_id": str(policy_row.get("qc_policy_id", "qc.none")).strip() or "qc.none",
                    "sampling_strategy_id": str(strategy_id),
                    "visibility_policy": "policy.epistemic.inspector",
                    "requester_subject_id": str(requester_subject_id or "").strip() or None,
                },
            )
            if qc_row:
                qc_rows.append(dict(qc_row))
            continue

        failures: List[str] = []
        for test_id in sorted(requested_tests):
            test_row = dict(test_rows.get(test_id) or {})
            if not test_row:
                failures.append("missing_test:{}".format(test_id))
                continue
            tol_id = str(test_row.get("tolerance_policy_id", "tol.default")).strip() or "tol.default"
            tol_value = _test_tolerance(tolerance_rows.get(tol_id))
            thresholds = _as_map(test_row.get("thresholds"))
            measured_values: Dict[str, int] = {}
            for quantity_id in _tokens(test_row.get("measured_quantity_ids")):
                measured_values[quantity_id] = int(
                    _measure_quantity(
                        quantity_id=quantity_id,
                        batch_row=row,
                        process_quality_row=quality_row,
                    )
                )
                if not _threshold_ok(measured_values[quantity_id], thresholds.get(quantity_id), tol_value):
                    failures.append("{}:{}".format(test_id, quantity_id))

            measurement_rows.append(
                {
                    "artifact_type_id": "artifact.process.measurement",
                    "run_id": run_token,
                    "batch_id": batch_token,
                    "test_id": str(test_id),
                    "tick": int(tick),
                    "instrument_id": str(instrument_id or "").strip() or None,
                    "calibration_cert_id": str(calibration_cert_id or "").strip() or None,
                    "measured_quantities": dict((key, int(measured_values[key])) for key in sorted(measured_values.keys())),
                    "tolerance_policy_id": str(tol_id),
                    "deterministic_fingerprint": canonical_sha256(
                        {
                            "run_id": run_token,
                            "batch_id": batch_token,
                            "test_id": str(test_id),
                            "measured_quantities": dict((key, int(measured_values[key])) for key in sorted(measured_values.keys())),
                            "tolerance_policy_id": str(tol_id),
                            "tick": int(tick),
                        }
                    ),
                }
            )

        passed = not failures
        action_token = "none" if passed else _fail_action_token(fail_action)
        if action_token == "reject":
            rejected_ids.append(batch_token)
            if fail_action == "quarantine":
                quarantine_ids.append(batch_token)
        elif action_token == "rework":
            rework_ids.append(batch_token)
        elif action_token == "accept_warning":
            warning_ids.append(batch_token)

        qc_row = build_qc_result_record_row(
            run_id=run_token,
            batch_id=batch_token,
            sampled=True,
            passed=bool(passed),
            fail_reason=(None if passed else "|".join(sorted(failures))),
            action_taken=str(action_token),
            tick=int(tick),
            extensions={
                "qc_policy_id": str(policy_row.get("qc_policy_id", "qc.none")).strip() or "qc.none",
                "sampling_strategy_id": str(strategy_id),
                "test_ids": sorted(requested_tests),
                "fail_action_policy": str(fail_action),
                "visibility_policy": "policy.epistemic.inspector",
                "requester_subject_id": str(requester_subject_id or "").strip() or None,
                "explain_contract_id": "explain.qc_failure" if not passed else "explain.qc_sampling_decision",
            },
        )
        if qc_row:
            qc_rows.append(dict(qc_row))

    qc_rows = sorted(
        qc_rows,
        key=lambda row: (str(row.get("run_id", "")), str(row.get("batch_id", ""))),
    )
    measurement_rows = sorted(
        measurement_rows,
        key=lambda row: (str(row.get("batch_id", "")), str(row.get("test_id", ""))),
    )
    decision_rows = sorted(
        decision_rows,
        key=lambda row: (str(row.get("batch_id", "")), str(row.get("sampling_strategy_id", ""))),
    )

    sampled_true_count = int(sum(1 for row in qc_rows if bool(row.get("sampled", False))))
    sampled_fail_count = int(
        sum(
            1
            for row in qc_rows
            if bool(row.get("sampled", False)) and (not bool(row.get("passed", False)))
        )
    )
    pass_rate = 1000 if sampled_true_count <= 0 else int(max(0, min(1000, round(((sampled_true_count - sampled_fail_count) * 1000.0) / float(sampled_true_count)))))
    fail_rate = 0 if sampled_true_count <= 0 else int(max(0, min(1000, round((sampled_fail_count * 1000.0) / float(sampled_true_count)))))

    qc_hash = canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "batch_id": str(row.get("batch_id", "")).strip(),
                "sampled": bool(row.get("sampled", False)),
                "passed": bool(row.get("passed", False)),
                "action_taken": str(row.get("action_taken", "")).strip(),
                "fail_reason": (None if row.get("fail_reason") is None else str(row.get("fail_reason", "")).strip()),
            }
            for row in qc_rows
        ]
    )
    sampling_hash = canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "batch_id": str(row.get("batch_id", "")).strip(),
                "sampled": bool(row.get("sampled", False)),
                "sampling_strategy_id": str(row.get("sampling_strategy_id", "")).strip(),
                "sampling_details": _as_map(row.get("sampling_details")),
            }
            for row in decision_rows
        ]
    )

    return {
        "result": "complete",
        "reason": "",
        "qc_result_rows": qc_rows,
        "measurement_rows": measurement_rows,
        "decision_rows": decision_rows,
        "rejected_batch_ids": _tokens(rejected_ids),
        "rework_batch_ids": _tokens(rework_ids),
        "warning_batch_ids": _tokens(warning_ids),
        "quarantine_batch_ids": _tokens(quarantine_ids),
        "sampled_count": int(sampled_true_count),
        "failed_count": int(sampled_fail_count),
        "pass_rate_permille": int(pass_rate),
        "fail_rate_permille": int(fail_rate),
        "qc_result_hash_chain": str(qc_hash),
        "sampling_decision_hash_chain": str(sampling_hash),
        "deterministic_fingerprint": canonical_sha256(
            {
                "run_id": run_token,
                "qc_policy_id": str(policy_row.get("qc_policy_id", "qc.none")).strip() or "qc.none",
                "qc_result_hash_chain": str(qc_hash),
                "sampling_decision_hash_chain": str(sampling_hash),
            }
        ),
    }


__all__ = [
    "build_qc_result_record_row",
    "qc_policy_rows_by_id",
    "sampling_strategy_rows_by_id",
    "test_procedure_rows_by_id",
    "tolerance_policy_rows_by_id",
    "evaluate_qc_for_run",
]
