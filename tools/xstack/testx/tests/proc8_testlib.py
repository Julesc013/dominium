"""Shared PROC-8 software pipeline TestX fixtures."""

from __future__ import annotations

import copy
import sys
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def base_state() -> dict:
    return {"tick": 0}


def law_profile() -> dict:
    return {
        "law_profile_id": "law.proc8.test",
        "allowed_processes": ["process.software_pipeline_execute"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.software_pipeline_execute": "entitlement.tool.operating",
        },
        "process_privilege_requirements": {
            "process.software_pipeline_execute": "operator",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.proc8.test",
        "entitlements": ["entitlement.tool.operating"],
        "privilege_level": "operator",
        "subject_id": "subject.proc8.operator",
    }


def default_inputs() -> dict:
    source_hash = canonical_sha256({"source": "proc8.test.source"})
    config_hash = canonical_sha256({"config": "proc8.test.config"})
    return {
        "pipeline_id": "pipeline.build_test_package_sign_deploy",
        "source_artifact_id": "artifact.software.source.{}".format(source_hash[:16]),
        "source_hash": source_hash,
        "toolchain_id": "toolchain.stub_c89",
        "config_hash": config_hash,
        "compile_policy_id": "compile.default",
        "signing_key_artifact_id": "cred.signing.proc8",
        "deploy_to_address": "sig://station.proc8",
        "available_test_ids": [
            "test.unit.alpha",
            "test.integration.beta",
            "test.signature.gamma",
            "test.performance.delta",
        ],
        "test_subset_rate_permille": 500,
        "qc_policy_id": "qc.basic_sampling",
    }


def execute_pipeline(
    *,
    repo_root: str,
    state: dict,
    inputs: Mapping[str, object] | None = None,
    policy_context: Mapping[str, object] | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.sessionx.process_runtime import execute_intent

    payload = dict(default_inputs())
    if isinstance(inputs, Mapping):
        payload.update(dict(inputs))
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.proc8.{}".format(
                canonical_sha256(payload)[:12]
            ),
            "process_id": "process.software_pipeline_execute",
            "inputs": payload,
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_context or {}),
    )


def cloned_state() -> dict:
    return copy.deepcopy(base_state())
