"""Shared COMPILE-0 fixtures/helpers."""

from __future__ import annotations

import copy
import json
import os
from typing import Mapping


def _read_registry_payload(*, repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(str(repo_root), str(rel_path).replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, Mapping):
        return {}
    if isinstance(payload.get("record"), Mapping):
        return dict(payload.get("record") or {})
    return dict(payload)


def law_profile() -> dict:
    return {
        "law_profile_id": "law.compile0.test",
        "allowed_processes": ["process.compile_request_submit"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.compile_request_submit": "entitlement.inspect",
        },
        "process_privilege_requirements": {
            "process.compile_request_submit": "observer",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.compile0.test",
        "entitlements": ["entitlement.inspect"],
        "privilege_level": "observer",
    }


def base_state() -> dict:
    return {
        "tick": 0,
        "compile_request_rows": [],
        "compile_result_rows": [],
        "compiled_model_rows": [],
        "equivalence_proof_rows": [],
        "validity_domain_rows": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
        "control_decision_log": [],
    }


def compile_request_fixture(*, request_id: str = "compile_request.test.default") -> dict:
    return {
        "request_id": str(request_id),
        "source_kind": "model_set",
        "target_compiled_type_id": "compiled.reduced_graph",
        "error_bound_policy_id": "tol.default",
        "source_ref": {
            "input_signature_ref": "signature.input.compile0",
            "output_signature_ref": "signature.output.compile0",
            "validity_domain": {
                "domain_id": "validity_domain.compile0",
                "input_ranges": {
                    "x": {"min": 0, "max": 100},
                    "y": {"min": 0, "max": 100},
                },
            },
            "nodes": [
                {"node_id": "node.input", "op": "input"},
                {"node_id": "node.const", "op": "const", "constant_value": 7},
                {"node_id": "node.dead", "op": "noop", "prunable": True},
            ],
            "keep_node_ids": ["node.input"],
        },
        "extensions": {"source": "testx.compile0"},
    }


def policy_context(repo_root: str) -> dict:
    return {
        "compiled_type_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/compiled_type_registry.json",
        ),
        "verification_procedure_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/verification_procedure_registry.json",
        ),
        "compile_policy_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/compile_policy_registry.json",
        ),
    }


def execute_compile_request(
    *,
    repo_root: str,
    state: dict,
    compile_request: Mapping[str, object],
    inputs: Mapping[str, object] | None = None,
    policy_ctx: Mapping[str, object] | None = None,
) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    intent_inputs = dict(inputs or {})
    intent_inputs["compile_request"] = dict(compile_request or {})
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.compile0.submit.{}".format(
                str(dict(compile_request or {}).get("request_id", "default"))
            ),
            "process_id": "process.compile_request_submit",
            "inputs": intent_inputs,
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_ctx or policy_context(repo_root)),
    )


def cloned_state() -> dict:
    return copy.deepcopy(base_state())
