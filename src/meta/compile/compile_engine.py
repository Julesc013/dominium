"""COMPILE-0 deterministic compiled-model skeleton engine."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256
from src.meta.compute import request_compute
from src.system.statevec import (
    build_state_vector_definition_row,
    deserialize_state,
    serialize_state,
    state_vector_definition_for_owner,
    state_vector_snapshot_rows_by_owner,
)


REFUSAL_COMPILE_INVALID = "refusal.compile.invalid"
REFUSAL_COMPILE_SOURCE_MISSING = "refusal.compile.source_missing"
REFUSAL_COMPILE_UNSUPPORTED_TYPE = "refusal.compile.unsupported_type"
REFUSAL_COMPILE_MISSING_PROOF = "refusal.compile.missing_proof"

_PROOF_KINDS = {"exact", "bounded_error"}


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


def _rows_from_registry_payload(payload: Mapping[str, object] | None, keys: Sequence[str]) -> List[dict]:
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


def build_validity_domain_row(
    *,
    domain_id: str,
    input_ranges: object,
    timing_constraints: Mapping[str, object] | None = None,
    environmental_constraints: Mapping[str, object] | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    domain_token = str(domain_id or "").strip()
    if not domain_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "domain_id": domain_token,
        "input_ranges": _as_map(input_ranges),
        "timing_constraints": _as_map(timing_constraints) or None,
        "environmental_constraints": _as_map(environmental_constraints) or None,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_validity_domain_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("domain_id", ""))):
        payload = build_validity_domain_row(
            domain_id=str(row.get("domain_id", "")).strip(),
            input_ranges=row.get("input_ranges"),
            timing_constraints=_as_map(row.get("timing_constraints")) or None,
            environmental_constraints=_as_map(row.get("environmental_constraints")) or None,
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("domain_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def validity_domain_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("domain_id", "")).strip(), dict(row)) for row in normalize_validity_domain_rows(rows) if str(row.get("domain_id", "")).strip())


def build_equivalence_proof_row(
    *,
    proof_id: str,
    proof_kind: str,
    verification_procedure_id: str,
    error_bound_policy_id: str | None,
    proof_hash: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    proof_token = str(proof_id or "").strip()
    kind_token = str(proof_kind or "").strip().lower()
    verifier_token = str(verification_procedure_id or "").strip()
    if (not proof_token) or (kind_token not in _PROOF_KINDS) or (not verifier_token):
        return {}
    error_token = str(error_bound_policy_id or "").strip() or None
    if (kind_token == "bounded_error") and (error_token is None):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "proof_id": proof_token,
        "proof_kind": kind_token,
        "verification_procedure_id": verifier_token,
        "error_bound_policy_id": error_token,
        "proof_hash": str(proof_hash or "").strip(),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["proof_hash"]:
        payload["proof_hash"] = canonical_sha256(dict(payload, proof_hash=""))
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_equivalence_proof_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("proof_id", ""))):
        payload = build_equivalence_proof_row(
            proof_id=str(row.get("proof_id", "")).strip(),
            proof_kind=str(row.get("proof_kind", "")).strip().lower(),
            verification_procedure_id=str(row.get("verification_procedure_id", "")).strip(),
            error_bound_policy_id=(None if row.get("error_bound_policy_id") is None else str(row.get("error_bound_policy_id", "")).strip() or None),
            proof_hash=str(row.get("proof_hash", "")).strip(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("proof_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def equivalence_proof_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("proof_id", "")).strip(), dict(row)) for row in normalize_equivalence_proof_rows(rows) if str(row.get("proof_id", "")).strip())


def build_compiled_model_row(
    *,
    compiled_model_id: str,
    source_kind: str,
    source_hash: str,
    compiled_type_id: str,
    compiled_payload_ref: Mapping[str, object] | None,
    input_signature_ref: str,
    output_signature_ref: str,
    validity_domain_ref: str,
    equivalence_proof_ref: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "compiled_model_id": str(compiled_model_id or "").strip(),
        "source_kind": str(source_kind or "").strip(),
        "source_hash": str(source_hash or "").strip(),
        "compiled_type_id": str(compiled_type_id or "").strip(),
        "compiled_payload_ref": _as_map(compiled_payload_ref),
        "input_signature_ref": str(input_signature_ref or "").strip(),
        "output_signature_ref": str(output_signature_ref or "").strip(),
        "validity_domain_ref": str(validity_domain_ref or "").strip(),
        "equivalence_proof_ref": str(equivalence_proof_ref or "").strip(),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not all(
        (
            payload["compiled_model_id"],
            payload["source_kind"],
            payload["source_hash"],
            payload["compiled_type_id"],
            payload["input_signature_ref"],
            payload["output_signature_ref"],
            payload["validity_domain_ref"],
            payload["equivalence_proof_ref"],
        )
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_compiled_model_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("compiled_model_id", ""))):
        payload = build_compiled_model_row(
            compiled_model_id=str(row.get("compiled_model_id", "")).strip(),
            source_kind=str(row.get("source_kind", "")).strip(),
            source_hash=str(row.get("source_hash", "")).strip(),
            compiled_type_id=str(row.get("compiled_type_id", "")).strip(),
            compiled_payload_ref=_as_map(row.get("compiled_payload_ref")),
            input_signature_ref=str(row.get("input_signature_ref", "")).strip(),
            output_signature_ref=str(row.get("output_signature_ref", "")).strip(),
            validity_domain_ref=str(row.get("validity_domain_ref", "")).strip(),
            equivalence_proof_ref=str(row.get("equivalence_proof_ref", "")).strip(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("compiled_model_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def compiled_model_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("compiled_model_id", "")).strip(), dict(row)) for row in normalize_compiled_model_rows(rows) if str(row.get("compiled_model_id", "")).strip())


def build_compile_request_row(
    *,
    request_id: str,
    source_kind: str,
    source_ref: Mapping[str, object] | None,
    target_compiled_type_id: str,
    error_bound_policy_id: str | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "request_id": str(request_id or "").strip(),
        "source_kind": str(source_kind or "").strip(),
        "source_ref": _as_map(source_ref),
        "target_compiled_type_id": str(target_compiled_type_id or "").strip(),
        "error_bound_policy_id": str(error_bound_policy_id or "").strip() or None,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not all((payload["request_id"], payload["source_kind"], payload["target_compiled_type_id"])):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_compile_request_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("request_id", ""))):
        payload = build_compile_request_row(
            request_id=str(row.get("request_id", "")).strip(),
            source_kind=str(row.get("source_kind", "")).strip(),
            source_ref=_as_map(row.get("source_ref")),
            target_compiled_type_id=str(row.get("target_compiled_type_id", "")).strip(),
            error_bound_policy_id=(None if row.get("error_bound_policy_id") is None else str(row.get("error_bound_policy_id", "")).strip() or None),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("request_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def compile_request_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("request_id", "")).strip(), dict(row)) for row in normalize_compile_request_rows(rows) if str(row.get("request_id", "")).strip())


def build_compile_result_row(
    *,
    result_id: str,
    compiled_model_id: str | None,
    success: bool,
    refusal: str | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "result_id": str(result_id or "").strip(),
        "compiled_model_id": str(compiled_model_id or "").strip() or None,
        "success": bool(success),
        "refusal": str(refusal or "").strip() or None,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["result_id"]:
        return {}
    if payload["success"] and (payload["compiled_model_id"] is None):
        return {}
    if (not payload["success"]) and (payload["refusal"] is None):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_compile_result_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("result_id", ""))):
        payload = build_compile_result_row(
            result_id=str(row.get("result_id", "")).strip(),
            compiled_model_id=(None if row.get("compiled_model_id") is None else str(row.get("compiled_model_id", "")).strip() or None),
            success=bool(row.get("success", False)),
            refusal=(None if row.get("refusal") is None else str(row.get("refusal", "")).strip() or None),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(payload.get("result_id", "")).strip()
        if token:
            out[token] = dict(payload)
    return [dict(out[key]) for key in sorted(out.keys())]


def compile_result_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("result_id", "")).strip(), dict(row)) for row in normalize_compile_result_rows(rows) if str(row.get("result_id", "")).strip())


def compiled_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry_payload(registry_payload, ("compiled_types",))
    return dict(
        (str(row.get("compiled_type_id", "")).strip(), dict(row))
        for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("compiled_type_id", "")))
        if str(row.get("compiled_type_id", "")).strip()
    )


def verification_procedure_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry_payload(registry_payload, ("verification_procedures",))
    return dict(
        (str(row.get("verification_procedure_id", "")).strip(), dict(row))
        for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("verification_procedure_id", "")))
        if str(row.get("verification_procedure_id", "")).strip()
    )


def compile_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry_payload(registry_payload, ("compile_policies",))
    return dict(
        (str(row.get("compile_policy_id", "")).strip(), dict(row))
        for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("compile_policy_id", "")))
        if str(row.get("compile_policy_id", "")).strip()
    )


def _source_hash(*, source_kind: str, source_ref: Mapping[str, object]) -> str:
    return canonical_sha256({"source_kind": str(source_kind or "").strip(), "source_ref": _as_map(source_ref)})


def _compiled_state_owner_id(compiled_model_id: str) -> str:
    token = str(compiled_model_id or "").strip()
    if not token:
        return ""
    return "compiled.{}".format(token)


def _compiled_state_definition(
    *,
    owner_id: str,
) -> dict:
    return build_state_vector_definition_row(
        owner_id=owner_id,
        version="1.0.0",
        state_fields=[
            {"field_id": "execution_count", "path": "execution_count", "field_kind": "u64", "default": 0},
            {"field_id": "last_input_hash", "path": "last_input_hash", "field_kind": "sha256", "default": ""},
            {"field_id": "last_output_hash", "path": "last_output_hash", "field_kind": "sha256", "default": ""},
        ],
        deterministic_fingerprint="",
        extensions={"source": "COMPILE0"},
    )


def _compile_reduced_graph(source_ref: Mapping[str, object]) -> dict:
    nodes = [
        {
            "node_id": str(row.get("node_id", "")).strip() or "node.{}".format(canonical_sha256(row)[:12]),
            "op": str(row.get("op", "")).strip() or "passthrough",
            "constant_value": row.get("constant_value"),
            "prunable": bool(row.get("prunable", False)),
            "extensions": _as_map(row.get("extensions")),
        }
        for row in sorted((dict(item) for item in _as_list(_as_map(source_ref).get("nodes")) if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", "")))
    ]
    keep_nodes = set(_sorted_tokens(_as_map(source_ref).get("keep_node_ids") or []))
    for node in nodes:
        node_id = str(node.get("node_id", "")).strip()
        if str(node.get("op", "")).strip().lower() == "const" or node.get("constant_value") is not None:
            keep_nodes.add(node_id)

    reduced_nodes: List[dict] = []
    removed: List[str] = []
    constants: Dict[str, object] = {}
    for node in nodes:
        node_id = str(node.get("node_id", "")).strip()
        if (node_id not in keep_nodes) and bool(node.get("prunable", False)):
            removed.append(node_id)
            continue
        reduced_nodes.append(dict(node))
        if node.get("constant_value") is not None:
            constants[node_id] = node.get("constant_value")

    payload = {
        "schema_version": "1.0.0",
        "nodes": sorted(reduced_nodes, key=lambda row: str(row.get("node_id", ""))),
        "edges": [],  # COMPILE-0 skeleton: reduced-graph node compile only.
        "constant_bindings": dict((key, constants[key]) for key in sorted(constants.keys())),
        "removed_node_ids": _sorted_tokens(removed),
        "optimization_summary": {
            "source_node_count": len(nodes),
            "reduced_node_count": len(reduced_nodes),
            "removed_node_count": len(removed),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def evaluate_compile_request(
    *,
    current_tick: int,
    compile_request: Mapping[str, object],
    compiled_type_registry_payload: Mapping[str, object] | None,
    verification_procedure_registry_payload: Mapping[str, object] | None,
    compile_policy_registry_payload: Mapping[str, object] | None,
    compile_policy_id: str = "compile.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request_row = build_compile_request_row(
        request_id=str(compile_request.get("request_id", "")).strip() or "compile_request.{}".format(canonical_sha256({"tick": tick, "compile_request": _as_map(compile_request)})[:16]),
        source_kind=str(compile_request.get("source_kind", "")).strip(),
        source_ref=_as_map(compile_request.get("source_ref")),
        target_compiled_type_id=str(compile_request.get("target_compiled_type_id", "")).strip(),
        error_bound_policy_id=(None if compile_request.get("error_bound_policy_id") is None else str(compile_request.get("error_bound_policy_id", "")).strip() or None),
        deterministic_fingerprint=str(compile_request.get("deterministic_fingerprint", "")).strip(),
        extensions=dict(_as_map(compile_request.get("extensions")), current_tick=tick, source_tick=tick),
    )
    if not request_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_INVALID,
            "compile_request_row": {},
            "compile_result_row": build_compile_result_row(result_id="compile_result.{}".format(canonical_sha256({"tick": tick, "reason": REFUSAL_COMPILE_INVALID})[:16]), compiled_model_id=None, success=False, refusal=REFUSAL_COMPILE_INVALID, deterministic_fingerprint="", extensions={}),
        }

    source_ref = _as_map(request_row.get("source_ref"))
    if not source_ref:
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_SOURCE_MISSING,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(result_id="compile_result.{}".format(canonical_sha256({"request_id": request_row.get("request_id"), "reason": REFUSAL_COMPILE_SOURCE_MISSING})[:16]), compiled_model_id=None, success=False, refusal=REFUSAL_COMPILE_SOURCE_MISSING, deterministic_fingerprint="", extensions={"request_id": request_row.get("request_id")}),
        }

    target_type = str(request_row.get("target_compiled_type_id", "")).strip()
    if target_type not in compiled_type_rows_by_id(compiled_type_registry_payload) or target_type != "compiled.reduced_graph":
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_UNSUPPORTED_TYPE,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(result_id="compile_result.{}".format(canonical_sha256({"request_id": request_row.get("request_id"), "reason": REFUSAL_COMPILE_UNSUPPORTED_TYPE, "target": target_type})[:16]), compiled_model_id=None, success=False, refusal=REFUSAL_COMPILE_UNSUPPORTED_TYPE, deterministic_fingerprint="", extensions={"request_id": request_row.get("request_id"), "target_compiled_type_id": target_type}),
        }

    reduced_payload = _compile_reduced_graph(source_ref)
    source_hash = _source_hash(source_kind=str(request_row.get("source_kind", "")).strip(), source_ref=source_ref)

    policy_row = dict(compile_policy_rows_by_id(compile_policy_registry_payload).get(str(compile_policy_id or "").strip()) or compile_policy_rows_by_id(compile_policy_registry_payload).get("compile.default") or {})
    removed_count = int(max(0, _as_int(_as_map(reduced_payload.get("optimization_summary")).get("removed_node_count", 0), 0)))
    proof_kind = "bounded_error" if (removed_count > 0 and bool(policy_row.get("allow_bounded_error", True))) else "exact"
    verifier_rows = verification_procedure_rows_by_id(verification_procedure_registry_payload)
    preferred = str(policy_row.get("preferred_verification_procedure_id", "")).strip()
    verifier_id = preferred if (preferred and proof_kind in set(_sorted_tokens(_as_map(verifier_rows.get(preferred)).get("proof_kind_supported") or []))) else ""
    if not verifier_id:
        for candidate in sorted(verifier_rows.keys()):
            if proof_kind in set(_sorted_tokens(_as_map(verifier_rows.get(candidate)).get("proof_kind_supported") or [])):
                verifier_id = candidate
                break
    if not verifier_id:
        verifier_id = "verify.exact_structural" if proof_kind == "exact" else "verify.bounded_sampling"

    error_policy = None if proof_kind == "exact" else (str(request_row.get("error_bound_policy_id", "")).strip() or "tol.default")
    proof_row = build_equivalence_proof_row(
        proof_id="proof.equivalence.{}".format(canonical_sha256({"request_id": request_row.get("request_id"), "source_hash": source_hash, "payload_hash": canonical_sha256(reduced_payload), "proof_kind": proof_kind, "verifier_id": verifier_id})[:16]),
        proof_kind=proof_kind,
        verification_procedure_id=verifier_id,
        error_bound_policy_id=error_policy,
        proof_hash=canonical_sha256({"source_hash": source_hash, "compiled_payload_hash": canonical_sha256(reduced_payload), "proof_kind": proof_kind, "verification_procedure_id": verifier_id, "error_bound_policy_id": error_policy}),
        deterministic_fingerprint="",
        extensions={"source_tick": tick},
    )
    if not proof_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_MISSING_PROOF,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(result_id="compile_result.{}".format(canonical_sha256({"request_id": request_row.get("request_id"), "reason": REFUSAL_COMPILE_MISSING_PROOF})[:16]), compiled_model_id=None, success=False, refusal=REFUSAL_COMPILE_MISSING_PROOF, deterministic_fingerprint="", extensions={"request_id": request_row.get("request_id")}),
        }

    validity_row = build_validity_domain_row(
        domain_id=str(_as_map(source_ref.get("validity_domain")).get("domain_id", "")).strip() or "validity_domain.{}".format(source_hash[:16]),
        input_ranges=_as_map(_as_map(source_ref.get("validity_domain")).get("input_ranges")) or _as_map(source_ref.get("input_ranges")),
        timing_constraints=_as_map(_as_map(source_ref.get("validity_domain")).get("timing_constraints")) or None,
        environmental_constraints=_as_map(_as_map(source_ref.get("validity_domain")).get("environmental_constraints")) or None,
        deterministic_fingerprint="",
        extensions={"source_hash": source_hash, "source_tick": tick},
    )
    payload_hash = canonical_sha256(reduced_payload)
    compiled_model_id = "compiled_model.{}".format(
        canonical_sha256(
            {
                "request_id": request_row.get("request_id"),
                "source_hash": source_hash,
                "target_type": target_type,
                "payload_hash": payload_hash,
                "proof_id": proof_row.get("proof_id"),
            }
        )[:16]
    )
    state_owner_id = _compiled_state_owner_id(compiled_model_id)
    state_vector_definition_row = _compiled_state_definition(owner_id=state_owner_id)
    initial_state_serialization = serialize_state(
        owner_id=state_owner_id,
        source_state={"execution_count": 0, "last_input_hash": "", "last_output_hash": ""},
        state_vector_definition_rows=[state_vector_definition_row] if state_vector_definition_row else [],
        current_tick=tick,
        expected_version="1.0.0",
        extensions={"source": "compile_engine.initial_state"},
    )
    if str(initial_state_serialization.get("result", "")).strip() != "complete":
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_INVALID,
            "compile_request_row": request_row,
            "compile_result_row": build_compile_result_row(
                result_id="compile_result.{}".format(
                    canonical_sha256(
                        {
                            "request_id": request_row.get("request_id"),
                            "reason": REFUSAL_COMPILE_INVALID,
                        }
                    )[:16]
                ),
                compiled_model_id=None,
                success=False,
                refusal=REFUSAL_COMPILE_INVALID,
                deterministic_fingerprint="",
                extensions={"request_id": request_row.get("request_id")},
            ),
        }
    initial_state_snapshot_row = dict(initial_state_serialization.get("snapshot_row") or {})
    model_row = build_compiled_model_row(
        compiled_model_id=compiled_model_id,
        source_kind=str(request_row.get("source_kind", "")).strip(),
        source_hash=source_hash,
        compiled_type_id=target_type,
        compiled_payload_ref={"payload_format": "inline.reduced_graph.v1", "payload_hash": payload_hash, "payload": reduced_payload},
        input_signature_ref=str(source_ref.get("input_signature_ref", "")).strip() or "signature.input.{}".format(source_hash[:12]),
        output_signature_ref=str(source_ref.get("output_signature_ref", "")).strip() or "signature.output.{}".format(source_hash[:12]),
        validity_domain_ref=str(validity_row.get("domain_id", "")).strip(),
        equivalence_proof_ref=str(proof_row.get("proof_id", "")).strip(),
        deterministic_fingerprint="",
        extensions={
            "source_ref_snapshot": source_ref,
            "compile_policy_id": str(policy_row.get("compile_policy_id", "")).strip() or "compile.default",
            "source_tick": tick,
            "state_vector_owner_id": state_owner_id,
            "state_vector_version": "1.0.0",
            "state_vector_snapshot_id": str(initial_state_snapshot_row.get("snapshot_id", "")).strip(),
            "state_vector_anchor_hash": str(initial_state_serialization.get("anchor_hash", "")).strip(),
        },
    )
    result_row = build_compile_result_row(
        result_id="compile_result.{}".format(canonical_sha256({"request_id": request_row.get("request_id"), "compiled_model_id": model_row.get("compiled_model_id")})[:16]),
        compiled_model_id=str(model_row.get("compiled_model_id", "")).strip(),
        success=True,
        refusal=None,
        deterministic_fingerprint="",
        extensions={"request_id": request_row.get("request_id"), "proof_id": proof_row.get("proof_id"), "source_tick": tick},
    )
    return {
        "result": "complete",
        "reason_code": "",
        "compile_request_row": request_row,
        "compile_result_row": result_row,
        "compiled_model_row": model_row,
        "equivalence_proof_row": proof_row,
        "validity_domain_row": validity_row,
        "state_vector_definition_row": state_vector_definition_row,
        "state_vector_snapshot_row": initial_state_snapshot_row,
        "source_hash": source_hash,
        "deterministic_fingerprint": canonical_sha256(
            {
                "compile_request_row": request_row,
                "compile_result_row": result_row,
                "compiled_model_row": model_row,
                "equivalence_proof_row": proof_row,
                "validity_domain_row": validity_row,
                "state_vector_definition_row": state_vector_definition_row,
                "state_vector_snapshot_row": initial_state_snapshot_row,
            }
        ),
    }


def compiled_model_is_valid(
    *,
    compiled_model_id: str,
    current_inputs: Mapping[str, object] | None,
    compiled_model_rows: object,
    validity_domain_rows: object,
    state_vector_definition_rows: object | None = None,
) -> dict:
    model_id = str(compiled_model_id or "").strip()
    model_row = dict(compiled_model_rows_by_id(compiled_model_rows).get(model_id) or {})
    if not model_row:
        return {"valid": False, "reason_code": REFUSAL_COMPILE_INVALID, "violations": ["missing_compiled_model"]}
    validity_id = str(model_row.get("validity_domain_ref", "")).strip()
    validity_row = dict(validity_domain_rows_by_id(validity_domain_rows).get(validity_id) or {})
    if not validity_row:
        return {"valid": False, "reason_code": REFUSAL_COMPILE_INVALID, "violations": ["missing_validity_domain"]}
    state_owner_id = str(_as_map(model_row.get("extensions")).get("state_vector_owner_id", "")).strip()
    if state_owner_id and state_vector_definition_rows is not None:
        definition = state_vector_definition_for_owner(
            owner_id=state_owner_id,
            state_vector_definition_rows=state_vector_definition_rows,
        )
        if not definition:
            return {
                "valid": False,
                "reason_code": REFUSAL_COMPILE_INVALID,
                "violations": ["missing_state_vector_definition"],
                "state_vector_owner_id": state_owner_id,
            }
    inputs = _as_map(current_inputs)
    violations: List[str] = []
    for key, rule in sorted(_as_map(validity_row.get("input_ranges")).items()):
        token = str(key or "").strip()
        if (not token) or (token not in inputs):
            continue
        row = _as_map(rule)
        value = _as_int(inputs.get(token), 0)
        if ("min" in row) and value < _as_int(row.get("min"), value):
            violations.append("input_range_low:{}".format(token))
        if ("max" in row) and value > _as_int(row.get("max"), value):
            violations.append("input_range_high:{}".format(token))
    return {"valid": not violations, "reason_code": "" if not violations else REFUSAL_COMPILE_INVALID, "violations": violations, "validity_domain_id": validity_id}


def compiled_model_execute(
    *,
    compiled_model_id: str,
    inputs: Mapping[str, object] | None,
    compiled_model_rows: object,
    validity_domain_rows: object,
    state_vector_definition_rows: object | None = None,
    state_vector_snapshot_rows: object | None = None,
    current_tick: int = 0,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
    owner_priority: int = 100,
) -> dict:
    validity = compiled_model_is_valid(
        compiled_model_id=compiled_model_id,
        current_inputs=inputs,
        compiled_model_rows=compiled_model_rows,
        validity_domain_rows=validity_domain_rows,
        state_vector_definition_rows=state_vector_definition_rows,
    )
    if not bool(validity.get("valid", False)):
        return {"result": "refused", "reason_code": REFUSAL_COMPILE_INVALID, "outputs": {}, "validity": validity}
    model_row = dict(compiled_model_rows_by_id(compiled_model_rows).get(str(compiled_model_id or "").strip()) or {})
    payload_ref = _as_map(model_row.get("compiled_payload_ref"))
    payload = _as_map(payload_ref.get("payload"))
    compute_request = request_compute(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        owner_kind="controller",
        owner_id="compiled_model.{}".format(str(model_row.get("compiled_model_id", "")).strip() or str(compiled_model_id or "").strip()),
        instruction_units=int(
            max(
                1,
                min(
                    4096,
                    (len(_as_map(inputs)) * 8)
                    + (len(payload) * 4)
                    + (len(_as_map(payload.get("optimization_summary"))) * 2)
                    + 12,
                ),
            )
        ),
        memory_units=int(max(1, (len(_as_map(payload.get("constant_bindings"))) * 8) + 8)),
        owner_priority=int(max(0, _as_int(owner_priority, 100))),
        critical=False,
        compute_runtime_state=compute_runtime_state,
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=str(compute_budget_profile_id or "compute.default"),
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    compute_result = str(compute_request.get("result", "")).strip().lower()
    if compute_result in {"refused", "deferred", "shutdown"}:
        return {
            "result": "refused",
            "reason_code": str(compute_request.get("reason_code", "")).strip() or REFUSAL_COMPILE_INVALID,
            "outputs": {},
            "validity": validity,
            "violations": ["compute_budget_{}".format(compute_result)],
            "compute_consumption_record_row": dict(compute_request.get("consumption_record_row") or {}),
            "compute_decision_log_row": dict(compute_request.get("decision_log_row") or {}),
            "compute_explain_artifact_row": dict(compute_request.get("explain_artifact_row") or {}),
            "compute_runtime_state": dict(compute_request.get("runtime_state") or {}),
        }
    compute_energy_transform_row = {}
    if bool(_as_map(compute_request.get("compute_profile_row")).get("power_coupling_enabled", False)):
        instruction_used = int(
            max(
                0,
                _as_int(
                    _as_map(compute_request.get("consumption_record_row")).get("instruction_units_used", 0),
                    0,
                ),
            )
        )
        if instruction_used > 0:
            compute_energy_transform_row = {
                "transformation_id": "transform.electrical_to_thermal",
                "source_id": str(model_row.get("compiled_model_id", "")).strip()
                or str(compiled_model_id or "").strip(),
                "input_values": {"quantity.energy.electrical": int(instruction_used)},
                "output_values": {"quantity.energy.thermal": int(instruction_used)},
                "extensions": {
                    "source": "META-COMPUTE0-5",
                    "reason_code": "compute_power_coupling",
                },
            }
    outputs = {
        "compiled_model_id": str(model_row.get("compiled_model_id", "")).strip(),
        "compiled_type_id": str(model_row.get("compiled_type_id", "")).strip(),
        "input_hash": canonical_sha256(_as_map(inputs)),
        "payload_hash": str(payload_ref.get("payload_hash", "")).strip() or canonical_sha256(payload),
        "optimization_summary": _as_map(payload.get("optimization_summary")),
        "constant_bindings": _as_map(payload.get("constant_bindings")),
    }
    state_owner_id = str(_as_map(model_row.get("extensions")).get("state_vector_owner_id", "")).strip() or _compiled_state_owner_id(
        str(model_row.get("compiled_model_id", "")).strip()
    )
    state_vector_definitions = list(state_vector_definition_rows or [])
    owner_definition = state_vector_definition_for_owner(
        owner_id=state_owner_id,
        state_vector_definition_rows=state_vector_definitions,
    )
    if not owner_definition:
        fallback_definition = _compiled_state_definition(owner_id=state_owner_id)
        if fallback_definition:
            state_vector_definitions = list(state_vector_definitions) + [fallback_definition]
            owner_definition = dict(fallback_definition)
    if not owner_definition:
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_INVALID,
            "outputs": {},
            "validity": dict(validity),
            "violations": ["missing_state_vector_definition"],
        }
    previous_state = {"execution_count": 0, "last_input_hash": "", "last_output_hash": ""}
    previous_snapshot_by_owner = state_vector_snapshot_rows_by_owner(state_vector_snapshot_rows)
    previous_snapshot = dict(previous_snapshot_by_owner.get(state_owner_id) or {})
    if previous_snapshot:
        restored = deserialize_state(
            snapshot_row=previous_snapshot,
            state_vector_definition_rows=state_vector_definitions,
            expected_version=str(owner_definition.get("version", "")).strip() or "1.0.0",
        )
        if str(restored.get("result", "")).strip() != "complete":
            return {
                "result": "refused",
                "reason_code": REFUSAL_COMPILE_INVALID,
                "outputs": {},
                "validity": dict(validity),
                "violations": ["state_vector_deserialize_failed"],
                "statevec_reason_code": str(restored.get("reason_code", "")).strip(),
            }
        previous_state = _as_map(restored.get("restored_state"))
    next_state = {
        "execution_count": int(max(0, _as_int(previous_state.get("execution_count", 0), 0))) + 1,
        "last_input_hash": str(outputs.get("input_hash", "")).strip(),
        "last_output_hash": str(outputs.get("payload_hash", "")).strip(),
    }
    state_serialization = serialize_state(
        owner_id=state_owner_id,
        source_state=next_state,
        state_vector_definition_rows=state_vector_definitions,
        current_tick=int(max(0, _as_int(current_tick, 0))),
        expected_version=str(owner_definition.get("version", "")).strip() or "1.0.0",
        extensions={"source": "compiled_model_execute"},
    )
    if str(state_serialization.get("result", "")).strip() != "complete":
        return {
            "result": "refused",
            "reason_code": REFUSAL_COMPILE_INVALID,
            "outputs": {},
            "validity": dict(validity),
            "violations": ["state_vector_serialize_failed"],
            "statevec_reason_code": str(state_serialization.get("reason_code", "")).strip(),
        }
    snapshot_row = dict(state_serialization.get("snapshot_row") or {})
    outputs["state_vector_anchor_hash"] = str(state_serialization.get("anchor_hash", "")).strip()
    outputs["state_vector_snapshot_id"] = str(snapshot_row.get("snapshot_id", "")).strip()
    outputs["compute_throttled"] = bool(compute_request.get("throttled", False))
    outputs["compute_action_taken"] = str(compute_request.get("action_taken", "")).strip() or "none"
    outputs["compute_consumption_record_id"] = str(
        _as_map(compute_request.get("consumption_record_row")).get("record_id", "")
    ).strip()
    outputs["deterministic_fingerprint"] = canonical_sha256(dict(outputs, deterministic_fingerprint=""))
    return {
        "result": "complete",
        "reason_code": "",
        "outputs": outputs,
        "state_vector_owner_id": state_owner_id,
        "state_vector_snapshot_row": snapshot_row,
        "state_vector_definition_row": owner_definition,
        "compute_energy_transform_row": dict(compute_energy_transform_row),
        "compute_consumption_record_row": dict(compute_request.get("consumption_record_row") or {}),
        "compute_decision_log_row": dict(compute_request.get("decision_log_row") or {}),
        "compute_explain_artifact_row": dict(compute_request.get("explain_artifact_row") or {}),
        "compute_runtime_state": dict(compute_request.get("runtime_state") or {}),
    }


__all__ = [
    "REFUSAL_COMPILE_INVALID",
    "REFUSAL_COMPILE_SOURCE_MISSING",
    "REFUSAL_COMPILE_UNSUPPORTED_TYPE",
    "REFUSAL_COMPILE_MISSING_PROOF",
    "build_validity_domain_row",
    "normalize_validity_domain_rows",
    "validity_domain_rows_by_id",
    "build_equivalence_proof_row",
    "normalize_equivalence_proof_rows",
    "equivalence_proof_rows_by_id",
    "build_compiled_model_row",
    "normalize_compiled_model_rows",
    "compiled_model_rows_by_id",
    "build_compile_request_row",
    "normalize_compile_request_rows",
    "compile_request_rows_by_id",
    "build_compile_result_row",
    "normalize_compile_result_rows",
    "compile_result_rows_by_id",
    "compiled_type_rows_by_id",
    "verification_procedure_rows_by_id",
    "compile_policy_rows_by_id",
    "evaluate_compile_request",
    "compiled_model_is_valid",
    "compiled_model_execute",
]
