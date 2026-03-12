"""LOGIC-6 equivalence proof helpers."""

from __future__ import annotations

from typing import Dict, Mapping

from src.meta.compile import build_equivalence_proof_row, verification_procedure_rows_by_id
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _canon(value: object) -> object:
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if isinstance(value, float):
        return int(round(float(value)))
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def logic_equivalence_proof_hash(
    *,
    source_hash: str,
    compiled_payload: Mapping[str, object],
    proof_kind: str,
    verification_procedure_id: str,
    error_bound_policy_id: str | None,
) -> str:
    return canonical_sha256(
        {
            "source_hash": _token(source_hash),
            "compiled_payload_hash": canonical_sha256(_canon(compiled_payload)),
            "proof_kind": _token(proof_kind),
            "verification_procedure_id": _token(verification_procedure_id),
            "error_bound_policy_id": None if error_bound_policy_id is None else _token(error_bound_policy_id) or None,
        }
    )


def _proof_extensions(*, compiled_type_id: str, compiled_payload: Mapping[str, object]) -> dict:
    payload = _as_map(compiled_payload)
    compiled_type = _token(compiled_type_id)
    if compiled_type == "compiled.lookup_table":
        table_rows = [dict(row) for row in _as_list(payload.get("table_rows")) if isinstance(row, Mapping)]
        return {
            "proof_method": "exhaustive_lookup_table",
            "table_hash": canonical_sha256(_canon(table_rows)),
            "enumerated_input_count": len(table_rows),
        }
    if compiled_type == "compiled.automaton":
        states = [dict(row) for row in _as_list(payload.get("states")) if isinstance(row, Mapping)]
        transitions = [dict(row) for row in _as_list(payload.get("transition_rows")) if isinstance(row, Mapping)]
        return {
            "proof_method": "explored_state_automaton",
            "state_hash": canonical_sha256(_canon(states)),
            "transition_hash": canonical_sha256(_canon(transitions)),
            "explored_state_count": len(states),
            "transition_count": len(transitions),
        }
    return {
        "proof_method": "structural_equivalence_hash",
        "element_program_hash": canonical_sha256(_canon(_as_list(payload.get("element_programs")))),
        "removed_node_hash": canonical_sha256(_canon(_as_list(payload.get("removed_node_ids")))),
    }


def build_logic_equivalence_proof_row(
    *,
    request_id: str,
    source_hash: str,
    compiled_type_id: str,
    compiled_payload: Mapping[str, object],
    verification_procedure_registry_payload: Mapping[str, object] | None,
    compile_policy_row: Mapping[str, object],
    error_bound_policy_id: str | None = None,
) -> dict:
    verifier_rows = verification_procedure_rows_by_id(verification_procedure_registry_payload)
    preferred = _token(_as_map(compile_policy_row).get("preferred_verification_procedure_id")) or "verify.exact_structural"
    verifier_id = preferred if preferred in verifier_rows else "verify.exact_structural"
    extensions = _proof_extensions(compiled_type_id=compiled_type_id, compiled_payload=compiled_payload)
    extensions.update(
        {
            "compiled_type_id": _token(compiled_type_id),
            "proof_scope": "logic_compile",
        }
    )
    return build_equivalence_proof_row(
        proof_id="proof.logic.equivalence.{}".format(
            canonical_sha256(
                {
                    "request_id": _token(request_id),
                    "compiled_type_id": _token(compiled_type_id),
                    "payload_hash": canonical_sha256(_canon(compiled_payload)),
                }
            )[:16]
        ),
        proof_kind="exact",
        verification_procedure_id=verifier_id,
        error_bound_policy_id=error_bound_policy_id,
        proof_hash=logic_equivalence_proof_hash(
            source_hash=source_hash,
            compiled_payload=compiled_payload,
            proof_kind="exact",
            verification_procedure_id=verifier_id,
            error_bound_policy_id=error_bound_policy_id,
        ),
        deterministic_fingerprint="",
        extensions=extensions,
    )


def verify_logic_equivalence_proof(
    *,
    compiled_model_row: Mapping[str, object],
    proof_row: Mapping[str, object],
) -> bool:
    model = _as_map(compiled_model_row)
    proof = _as_map(proof_row)
    compiled_payload = _as_map(_as_map(model.get("compiled_payload_ref")).get("payload"))
    expected_hash = logic_equivalence_proof_hash(
        source_hash=_token(model.get("source_hash")),
        compiled_payload=compiled_payload,
        proof_kind=_token(proof.get("proof_kind")),
        verification_procedure_id=_token(proof.get("verification_procedure_id")),
        error_bound_policy_id=None if proof.get("error_bound_policy_id") is None else _token(proof.get("error_bound_policy_id")) or None,
    )
    if _token(proof.get("proof_hash")) != expected_hash:
        return False
    expected_extensions = _proof_extensions(
        compiled_type_id=_token(model.get("compiled_type_id")),
        compiled_payload=compiled_payload,
    )
    actual_extensions = _as_map(proof.get("extensions"))
    for key, value in sorted(expected_extensions.items(), key=lambda item: str(item[0])):
        if _canon(actual_extensions.get(key)) != _canon(value):
            return False
    return True


__all__ = [
    "build_logic_equivalence_proof_row",
    "logic_equivalence_proof_hash",
    "verify_logic_equivalence_proof",
]
