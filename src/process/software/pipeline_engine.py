"""PROC-8 deterministic software pipeline helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.meta.compile import evaluate_compile_request
from src.process.process_run_engine import (
    build_process_quality_record_row,
    build_process_run_record_row,
    build_process_step_record_row,
)
from src.process.qc.qc_engine import evaluate_qc_for_run


REFUSAL_SOFTWARE_PIPELINE_INVALID = "refusal.software_pipeline.invalid_inputs"
REFUSAL_SOFTWARE_PIPELINE_TOOLCHAIN_UNKNOWN = "refusal.software_pipeline.toolchain_unknown"
REFUSAL_SOFTWARE_PIPELINE_TEMPLATE_UNKNOWN = "refusal.software_pipeline.template_unknown"
REFUSAL_SOFTWARE_PIPELINE_COMPILE_FAILED = "refusal.software_pipeline.compile_failed"
REFUSAL_SOFTWARE_PIPELINE_TEST_FAILED = "refusal.software_pipeline.test_failed"
REFUSAL_SOFTWARE_PIPELINE_SIGNING_KEY_REQUIRED = "refusal.software_pipeline.signing_key_required"
REFUSAL_SOFTWARE_PIPELINE_SIGNATURE_REQUIRED_FOR_DEPLOY = (
    "refusal.software_pipeline.signature_required_for_deploy"
)
REFUSAL_SOFTWARE_PIPELINE_SIGNATURE_INVALID = "refusal.software_pipeline.signature_invalid"


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


def _rows_from_registry(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    body = _as_map(payload)
    if isinstance(body.get(key), list):
        return [dict(row) for row in _as_list(body.get(key)) if isinstance(row, Mapping)]
    record = _as_map(body.get("record"))
    if isinstance(record.get(key), list):
        return [dict(row) for row in _as_list(record.get(key)) if isinstance(row, Mapping)]
    return []


def build_software_pipeline_profile_row(
    *,
    pipeline_id: str,
    toolchain_id: str,
    toolchain_version: str,
    config_hash: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "pipeline_id": _token(pipeline_id),
        "toolchain_id": _token(toolchain_id),
        "toolchain_version": _token(toolchain_version),
        "config_hash": _token(config_hash).lower(),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (
        (not payload["pipeline_id"])
        or (not payload["toolchain_id"])
        or (not payload["toolchain_version"])
        or (not payload["config_hash"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_software_pipeline_profile_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            _token(item.get("pipeline_id")),
            _token(item.get("toolchain_id")),
            _token(item.get("config_hash")),
        ),
    ):
        payload = build_software_pipeline_profile_row(
            pipeline_id=_token(row.get("pipeline_id")),
            toolchain_id=_token(row.get("toolchain_id")),
            toolchain_version=_token(row.get("toolchain_version")),
            config_hash=_token(row.get("config_hash")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        if not payload:
            continue
        key = "{}|{}|{}".format(
            _token(payload.get("pipeline_id")),
            _token(payload.get("toolchain_id")),
            _token(payload.get("config_hash")),
        )
        out[key] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def build_software_artifact_row(
    *,
    artifact_id: str,
    kind: str,
    content_hash: str,
    produced_by_run_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind_token = _token(kind).lower()
    if kind_token not in {"source", "binary", "package", "signature", "test_report"}:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "artifact_id": _token(artifact_id),
        "kind": kind_token,
        "content_hash": _token(content_hash).lower(),
        "produced_by_run_id": _token(produced_by_run_id),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (
        (not payload["artifact_id"])
        or (not payload["content_hash"])
        or (not payload["produced_by_run_id"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_software_artifact_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("artifact_id")), _token(item.get("kind"))),
    ):
        payload = build_software_artifact_row(
            artifact_id=_token(row.get("artifact_id")),
            kind=_token(row.get("kind")),
            content_hash=_token(row.get("content_hash")),
            produced_by_run_id=_token(row.get("produced_by_run_id")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        artifact_id = _token(payload.get("artifact_id"))
        if artifact_id:
            out[artifact_id] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def build_deployment_record_row(
    *,
    deploy_id: str,
    artifact_id: str,
    from_subject_id: str,
    to_address: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "deploy_id": _token(deploy_id),
        "artifact_id": _token(artifact_id),
        "from_subject_id": _token(from_subject_id),
        "to_address": _token(to_address),
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if (
        (not payload["deploy_id"])
        or (not payload["artifact_id"])
        or (not payload["from_subject_id"])
        or (not payload["to_address"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_deployment_record_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            _token(item.get("deploy_id")),
        ),
    ):
        payload = build_deployment_record_row(
            deploy_id=_token(row.get("deploy_id")),
            artifact_id=_token(row.get("artifact_id")),
            from_subject_id=_token(row.get("from_subject_id")),
            to_address=_token(row.get("to_address")),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        deploy_id = _token(payload.get("deploy_id"))
        if deploy_id:
            out[deploy_id] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


def _toolchain_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(registry_payload, "toolchains"):
        token = _token(row.get("toolchain_id"))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _pipeline_template_rows_by_id(
    registry_payload: Mapping[str, object] | None,
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(registry_payload, "pipeline_templates"):
        token = _token(row.get("pipeline_id"))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _selected_test_ids(
    *,
    run_id: str,
    source_hash: str,
    qc_policy_id: str,
    available_test_ids: Sequence[str],
    sample_rate_permille: int,
) -> List[str]:
    candidates = _tokens(available_test_ids)
    if not candidates:
        return []
    rate = int(max(0, min(1000, _as_int(sample_rate_permille, 500))))
    if rate >= 1000:
        return list(candidates)
    selected: List[str] = []
    for test_id in candidates:
        marker = int(
            canonical_sha256(
                {
                    "stream": "process.software_pipeline.qc_subset",
                    "run_id": _token(run_id),
                    "source_hash": _token(source_hash),
                    "qc_policy_id": _token(qc_policy_id),
                    "test_id": _token(test_id),
                }
            )[:8],
            16,
        ) % 1000
        if marker < rate:
            selected.append(test_id)
    if selected:
        return _tokens(selected)
    return [candidates[0]]


def _build_step_row(*, run_id: str, step_id: str, tick: int, status: str) -> dict:
    return build_process_step_record_row(
        run_id=run_id,
        step_id=step_id,
        tick=tick,
        status=status,
        deterministic_fingerprint="",
        extensions={"source": "PROC8-6"},
    )


def _grade_for_quality(yield_factor: int, defect_flags: Sequence[str]) -> str:
    token_flags = _tokens(defect_flags)
    if yield_factor >= 920 and not token_flags:
        return "grade.A"
    if yield_factor >= 700 and len(token_flags) <= 1:
        return "grade.B"
    return "grade.C"


def evaluate_software_pipeline_execution(
    *,
    current_tick: int,
    pipeline_id: str,
    source_artifact_id: str,
    source_hash: str,
    toolchain_id: str,
    toolchain_version: str,
    config_hash: str,
    compile_policy_id: str,
    software_toolchain_registry_payload: Mapping[str, object] | None,
    software_pipeline_template_registry_payload: Mapping[str, object] | None,
    compiled_type_registry_payload: Mapping[str, object] | None,
    verification_procedure_registry_payload: Mapping[str, object] | None,
    compile_policy_registry_payload: Mapping[str, object] | None,
    existing_build_cache_rows: Sequence[Mapping[str, object]] | None,
    signing_key_artifact_id: str | None,
    deploy_to_address: str | None,
    requester_subject_id: str | None,
    run_id: str | None = None,
    available_test_ids: Sequence[str] | None = None,
    qc_policy_id: str = "qc.basic_sampling",
    qc_policy_registry_payload: Mapping[str, object] | None = None,
    sampling_strategy_registry_payload: Mapping[str, object] | None = None,
    test_procedure_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    runtime_bug_risk_permille: int = 0,
    force_test_failure: bool = False,
    force_signature_invalid: bool = False,
    allow_deploy_without_signature: bool = False,
    test_subset_rate_permille: int = 500,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    pipeline_token = _token(pipeline_id)
    source_artifact_token = _token(source_artifact_id)
    source_hash_token = _token(source_hash).lower()
    toolchain_token = _token(toolchain_id)
    toolchain_version_token = _token(toolchain_version)
    config_hash_token = _token(config_hash).lower()
    signer_token = _token(signing_key_artifact_id)
    deploy_target = _token(deploy_to_address)
    subject_token = _token(requester_subject_id) or "subject.unknown"
    compile_policy_token = _token(compile_policy_id) or "compile.default"
    qc_policy_token = _token(qc_policy_id) or "qc.basic_sampling"

    if (
        (not pipeline_token)
        or (not source_artifact_token)
        or (not source_hash_token)
        or (not toolchain_token)
        or (not toolchain_version_token)
        or (not config_hash_token)
    ):
        return {"result": "refusal", "reason_code": REFUSAL_SOFTWARE_PIPELINE_INVALID}

    toolchain_rows = _toolchain_rows_by_id(software_toolchain_registry_payload)
    if toolchain_token not in toolchain_rows:
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SOFTWARE_PIPELINE_TOOLCHAIN_UNKNOWN,
            "toolchain_id": toolchain_token,
        }
    template_rows = _pipeline_template_rows_by_id(
        software_pipeline_template_registry_payload
    )
    if pipeline_token not in template_rows:
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SOFTWARE_PIPELINE_TEMPLATE_UNKNOWN,
            "pipeline_id": pipeline_token,
        }

    run_token = _token(run_id) or "run.software.pipeline.{}".format(
        canonical_sha256(
            {
                "pipeline_id": pipeline_token,
                "source_hash": source_hash_token,
                "toolchain_id": toolchain_token,
                "toolchain_version": toolchain_version_token,
                "config_hash": config_hash_token,
                "tick": tick,
            }
        )[:16]
    )
    compile_cache_key = canonical_sha256(
        {
            "pipeline_id": pipeline_token,
            "source_hash": source_hash_token,
            "toolchain_version": toolchain_version_token,
            "config_hash": config_hash_token,
        }
    )

    cache_by_key = dict(
        (
            _token(row.get("cache_key")),
            dict(row),
        )
        for row in _as_list(existing_build_cache_rows)
        if isinstance(row, Mapping) and _token(row.get("cache_key"))
    )
    cache_row = dict(cache_by_key.get(compile_cache_key) or {})
    compile_cache_hit = bool(cache_row)

    compile_request_row = {}
    compile_result_row = {}
    compiled_model_row = {}
    equivalence_proof_row = {}
    validity_domain_row = {}
    if not compile_cache_hit:
        compile_request = {
            "request_id": "compile_request.pipeline.{}".format(
                canonical_sha256({"cache_key": compile_cache_key})[:16]
            ),
            "source_kind": "process_graph",
            "source_ref": {
                "input_signature_ref": "{}.input".format(pipeline_token),
                "output_signature_ref": "{}.output".format(pipeline_token),
                "validity_domain": {
                    "domain_id": "validity.pipeline.{}".format(compile_cache_key[:16]),
                    "input_ranges": {
                        "source_hash_stability_permille": {"min": 1000, "max": 1000},
                        "config_hash_stability_permille": {"min": 1000, "max": 1000},
                    },
                    "environmental_constraints": {
                        "toolchain_id": toolchain_token,
                        "toolchain_version": toolchain_version_token,
                    },
                },
                "nodes": [
                    {"node_id": "verify_inputs", "op": "input"},
                    {"node_id": "compile", "op": "transform"},
                    {"node_id": "run_tests", "op": "measure"},
                    {"node_id": "package", "op": "transform"},
                    {"node_id": "sign", "op": "verify"},
                    {"node_id": "deploy", "op": "action"},
                ],
                "keep_node_ids": [
                    "verify_inputs",
                    "compile",
                    "run_tests",
                    "package",
                    "sign",
                    "deploy",
                ],
                "source_hash": source_hash_token,
                "toolchain_version": toolchain_version_token,
                "config_hash": config_hash_token,
            },
            "target_compiled_type_id": "compiled.reduced_graph",
            "error_bound_policy_id": "tol.default",
            "extensions": {
                "source": "PROC8-4",
                "pipeline_id": pipeline_token,
                "toolchain_id": toolchain_token,
            },
        }
        compile_eval = evaluate_compile_request(
            current_tick=tick,
            compile_request=compile_request,
            compiled_type_registry_payload=compiled_type_registry_payload,
            verification_procedure_registry_payload=verification_procedure_registry_payload,
            compile_policy_registry_payload=compile_policy_registry_payload,
            compile_policy_id=compile_policy_token,
        )
        compile_request_row = dict(compile_eval.get("compile_request_row") or {})
        compile_result_row = dict(compile_eval.get("compile_result_row") or {})
        compiled_model_row = dict(compile_eval.get("compiled_model_row") or {})
        equivalence_proof_row = dict(compile_eval.get("equivalence_proof_row") or {})
        validity_domain_row = dict(compile_eval.get("validity_domain_row") or {})
        if not bool(compile_result_row.get("success", False)):
            return {
                "result": "refusal",
                "reason_code": REFUSAL_SOFTWARE_PIPELINE_COMPILE_FAILED,
                "compile_request_row": compile_request_row,
                "compile_result_row": compile_result_row,
                "compiled_model_row": compiled_model_row,
                "equivalence_proof_row": equivalence_proof_row,
                "validity_domain_row": validity_domain_row,
            }
        cache_by_key[compile_cache_key] = {
            "cache_key": compile_cache_key,
            "compiled_model_id": _token(compile_result_row.get("compiled_model_id")),
            "source_hash": source_hash_token,
            "toolchain_version": toolchain_version_token,
            "config_hash": config_hash_token,
            "tick_cached": int(tick),
            "deterministic_fingerprint": canonical_sha256(
                {
                    "cache_key": compile_cache_key,
                    "compiled_model_id": _token(compile_result_row.get("compiled_model_id")),
                    "source_hash": source_hash_token,
                    "toolchain_version": toolchain_version_token,
                    "config_hash": config_hash_token,
                }
            ),
            "extensions": {"source": "PROC8-4"},
        }
    cache_row = dict(cache_by_key.get(compile_cache_key) or {})
    compiled_model_id = _token(cache_row.get("compiled_model_id"))
    binary_hash = canonical_sha256(
        {
            "cache_key": compile_cache_key,
            "compiled_model_id": compiled_model_id,
            "source_hash": source_hash_token,
            "toolchain_id": toolchain_token,
            "toolchain_version": toolchain_version_token,
            "config_hash": config_hash_token,
        }
    )
    selected_tests = _selected_test_ids(
        run_id=run_token,
        source_hash=source_hash_token,
        qc_policy_id=qc_policy_token,
        available_test_ids=list(
            available_test_ids or ["test.unit", "test.integration", "test.signature"]
        ),
        sample_rate_permille=int(max(0, min(1000, _as_int(test_subset_rate_permille, 500)))),
    )
    if force_test_failure:
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SOFTWARE_PIPELINE_TEST_FAILED,
            "selected_tests": list(selected_tests),
            "compile_cache_hit": bool(compile_cache_hit),
            "build_cache_key": compile_cache_key,
            "software_build_cache_rows": [
                dict(cache_by_key[key]) for key in sorted(cache_by_key.keys())
            ],
        }

    package_hash = canonical_sha256(
        {"binary_hash": binary_hash, "pipeline_id": pipeline_token, "config_hash": config_hash_token}
    )
    if (not signer_token) and deploy_target:
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SOFTWARE_PIPELINE_SIGNING_KEY_REQUIRED,
            "selected_tests": list(selected_tests),
            "compile_cache_hit": bool(compile_cache_hit),
            "build_cache_key": compile_cache_key,
            "software_build_cache_rows": [
                dict(cache_by_key[key]) for key in sorted(cache_by_key.keys())
            ],
        }
    signature_hash = (
        canonical_sha256({"package_hash": package_hash, "signing_key_artifact_id": signer_token})
        if signer_token
        else ""
    )
    if force_signature_invalid and deploy_target:
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SOFTWARE_PIPELINE_SIGNATURE_INVALID,
            "signature_hash": canonical_sha256({"invalid_signature": signature_hash}) if signature_hash else "",
            "compile_cache_hit": bool(compile_cache_hit),
            "build_cache_key": compile_cache_key,
            "software_build_cache_rows": [
                dict(cache_by_key[key]) for key in sorted(cache_by_key.keys())
            ],
        }
    if deploy_target and (not signature_hash) and (not allow_deploy_without_signature):
        return {
            "result": "refusal",
            "reason_code": REFUSAL_SOFTWARE_PIPELINE_SIGNATURE_REQUIRED_FOR_DEPLOY,
            "selected_tests": list(selected_tests),
            "compile_cache_hit": bool(compile_cache_hit),
            "build_cache_key": compile_cache_key,
            "software_build_cache_rows": [
                dict(cache_by_key[key]) for key in sorted(cache_by_key.keys())
            ],
        }

    runtime_bug_risk = int(max(0, min(1000, _as_int(runtime_bug_risk_permille, 0))))
    defect_flags: List[str] = []
    if runtime_bug_risk >= 500:
        defect_flags.append("software_bug")
    yield_factor = int(max(0, min(1000, 1000 - (runtime_bug_risk // 2))))
    quality_grade = _grade_for_quality(yield_factor=yield_factor, defect_flags=defect_flags)
    process_quality_row = build_process_quality_record_row(
        run_id=run_token,
        yield_factor=yield_factor,
        defect_flags=defect_flags,
        quality_grade=quality_grade,
        deterministic_fingerprint="",
        extensions={
            "source": "PROC8-6",
            "runtime_bug_risk_permille": runtime_bug_risk,
            "pipeline_id": pipeline_token,
            "selected_tests": list(selected_tests),
        },
    )
    process_run_record_row = build_process_run_record_row(
        run_id=run_token,
        process_id="proc.pipeline.build_test_package_sign_deploy",
        version="1.0.0",
        start_tick=tick,
        end_tick=tick,
        status="completed",
        input_refs=[
            {"ref_id": source_artifact_token, "ref_type": "artifact"},
            {"ref_id": toolchain_token, "ref_type": "toolchain"},
            {"ref_id": config_hash_token, "ref_type": "hash"},
        ],
        output_refs=[
            {"ref_id": "artifact.software.binary.{}".format(binary_hash[:16]), "ref_type": "artifact"},
            {"ref_id": "artifact.software.package.{}".format(package_hash[:16]), "ref_type": "artifact"},
        ],
        deterministic_fingerprint="",
        extensions={"source": "PROC8-6", "capsule_eligible_hint": True},
    )
    process_step_record_rows = [
        _build_step_row(run_id=run_token, step_id=step_id, tick=tick, status="completed")
        for step_id in (
            "step.verify_inputs",
            "step.compile",
            "step.run_tests",
            "step.package",
            "step.sign",
            "step.deploy",
        )
    ]
    software_artifact_rows = normalize_software_artifact_rows(
        [
            build_software_artifact_row(
                artifact_id="artifact.software.source.{}".format(source_hash_token[:16]),
                kind="source",
                content_hash=source_hash_token,
                produced_by_run_id=run_token,
                deterministic_fingerprint="",
                extensions={"source": "PROC8-6"},
            ),
            build_software_artifact_row(
                artifact_id="artifact.software.binary.{}".format(binary_hash[:16]),
                kind="binary",
                content_hash=binary_hash,
                produced_by_run_id=run_token,
                deterministic_fingerprint="",
                extensions={"source": "PROC8-4", "cache_key": compile_cache_key},
            ),
            build_software_artifact_row(
                artifact_id="artifact.software.package.{}".format(package_hash[:16]),
                kind="package",
                content_hash=package_hash,
                produced_by_run_id=run_token,
                deterministic_fingerprint="",
                extensions={"source": "PROC8-6"},
            ),
            build_software_artifact_row(
                artifact_id="artifact.software.test_report.{}".format(
                    canonical_sha256({"run_id": run_token, "tests": list(selected_tests)})[:16]
                ),
                kind="test_report",
                content_hash=canonical_sha256(
                    {"run_id": run_token, "tests": list(selected_tests), "status": "passed"}
                ),
                produced_by_run_id=run_token,
                deterministic_fingerprint="",
                extensions={"source": "PROC8-6", "selected_tests": list(selected_tests)},
            ),
        ]
        + (
            [
                build_software_artifact_row(
                    artifact_id="artifact.software.signature.{}".format(signature_hash[:16]),
                    kind="signature",
                    content_hash=signature_hash,
                    produced_by_run_id=run_token,
                    deterministic_fingerprint="",
                    extensions={
                        "source": "PROC8-5",
                        "signing_key_artifact_id": signer_token or None,
                    },
                )
            ]
            if signature_hash
            else []
        )
    )
    deployment_record_rows = (
        normalize_deployment_record_rows(
            [
                build_deployment_record_row(
                    deploy_id="deploy.software.{}".format(
                        canonical_sha256(
                            {"run_id": run_token, "to_address": deploy_target, "tick": tick}
                        )[:16]
                    ),
                    artifact_id="artifact.software.package.{}".format(package_hash[:16]),
                    from_subject_id=subject_token,
                    to_address=deploy_target,
                    tick=tick,
                    deterministic_fingerprint="",
                    extensions={"source": "PROC8-5", "pipeline_id": pipeline_token},
                )
            ]
        )
        if deploy_target
        else []
    )
    sig_outbound_row = (
        {
            "envelope_id": "env.software.deploy.{}".format(
                canonical_sha256({"run_id": run_token, "to_address": deploy_target, "tick": tick})[
                    :16
                ]
            ),
            "from_subject_id": subject_token,
            "to_address": deploy_target,
            "artifact_ids": _tokens(
                [
                    "artifact.software.package.{}".format(package_hash[:16]),
                    "artifact.software.signature.{}".format(signature_hash[:16]),
                ]
            ),
            "tick": tick,
            "delivery_mode": "sig_channel",
            "deterministic_fingerprint": canonical_sha256(
                {
                    "from_subject_id": subject_token,
                    "to_address": deploy_target,
                    "artifact_ids": _tokens(
                        [
                            "artifact.software.package.{}".format(package_hash[:16]),
                            "artifact.software.signature.{}".format(signature_hash[:16]),
                        ]
                    ),
                    "tick": tick,
                }
            ),
            "extensions": {"source": "PROC8-5"},
        }
        if deploy_target
        else {}
    )

    qc_eval = evaluate_qc_for_run(
        current_tick=tick,
        run_id=run_token,
        qc_policy_id=qc_policy_token,
        batch_quality_rows=[
            {
                "batch_id": "batch.software.binary.{}".format(binary_hash[:16]),
                "yield_factor": yield_factor,
                "defect_flags": _tokens(defect_flags),
                "contamination_tags": [],
                "quality_grade": quality_grade,
            }
        ],
        process_quality_record_rows=[process_quality_row] if process_quality_row else [],
        qc_policy_registry_payload=qc_policy_registry_payload,
        sampling_strategy_registry_payload=sampling_strategy_registry_payload,
        test_procedure_registry_payload=test_procedure_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        instrument_id="instrument.software.ci",
        calibration_cert_id=None,
        requester_subject_id=subject_token,
    )
    pipeline_profile_row = build_software_pipeline_profile_row(
        pipeline_id=pipeline_token,
        toolchain_id=toolchain_token,
        toolchain_version=toolchain_version_token,
        config_hash=config_hash_token,
        deterministic_fingerprint="",
        extensions={"source": "PROC8-4", "compile_policy_id": compile_policy_token},
    )
    return {
        "result": "complete",
        "reason_code": "",
        "pipeline_profile_row": pipeline_profile_row,
        "software_artifact_rows": [dict(row) for row in software_artifact_rows],
        "deployment_record_rows": [dict(row) for row in deployment_record_rows],
        "process_run_record_row": dict(process_run_record_row),
        "process_step_record_rows": [dict(row) for row in process_step_record_rows if row],
        "process_quality_record_row": dict(process_quality_row),
        "qc_result_rows": [dict(row) for row in list(qc_eval.get("qc_result_rows") or [])],
        "qc_measurement_rows": [dict(row) for row in list(qc_eval.get("measurement_rows") or [])],
        "sampling_decision_rows": [
            dict(row) for row in list(qc_eval.get("sampling_decision_rows") or [])
        ],
        "compile_request_row": dict(compile_request_row),
        "compile_result_row": dict(compile_result_row),
        "compiled_model_row": dict(compiled_model_row),
        "equivalence_proof_row": dict(equivalence_proof_row),
        "validity_domain_row": dict(validity_domain_row),
        "software_build_cache_rows": [dict(cache_by_key[key]) for key in sorted(cache_by_key.keys())],
        "sig_outbound_row": dict(sig_outbound_row),
        "compile_cache_hit": bool(compile_cache_hit),
        "build_cache_key": compile_cache_key,
        "compiled_model_id": compiled_model_id or None,
        "binary_hash": binary_hash,
        "package_hash": package_hash,
        "signature_hash": signature_hash or None,
        "selected_tests": list(selected_tests),
        "deterministic_fingerprint": canonical_sha256(
            {
                "run_id": run_token,
                "pipeline_id": pipeline_token,
                "compile_cache_key": compile_cache_key,
                "compiled_model_id": compiled_model_id,
                "binary_hash": binary_hash,
                "package_hash": package_hash,
                "signature_hash": signature_hash or None,
                "selected_tests": list(selected_tests),
            }
        ),
    }


__all__ = [
    "REFUSAL_SOFTWARE_PIPELINE_INVALID",
    "REFUSAL_SOFTWARE_PIPELINE_TOOLCHAIN_UNKNOWN",
    "REFUSAL_SOFTWARE_PIPELINE_TEMPLATE_UNKNOWN",
    "REFUSAL_SOFTWARE_PIPELINE_COMPILE_FAILED",
    "REFUSAL_SOFTWARE_PIPELINE_TEST_FAILED",
    "REFUSAL_SOFTWARE_PIPELINE_SIGNING_KEY_REQUIRED",
    "REFUSAL_SOFTWARE_PIPELINE_SIGNATURE_REQUIRED_FOR_DEPLOY",
    "REFUSAL_SOFTWARE_PIPELINE_SIGNATURE_INVALID",
    "build_software_pipeline_profile_row",
    "normalize_software_pipeline_profile_rows",
    "build_software_artifact_row",
    "normalize_software_artifact_rows",
    "build_deployment_record_row",
    "normalize_deployment_record_rows",
    "evaluate_software_pipeline_execution",
]
