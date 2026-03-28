"""Shared SYS-5 certification TestX fixtures/helpers."""

from __future__ import annotations

import copy
import sys
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.testx.tests.sys0_testlib import cloned_state as sys0_cloned_state


def _configured_system_rows(state: dict, *, spec_target_kind: str, spec_target_id: str) -> list[dict]:
    rows = [dict(row) for row in list(state.get("system_rows") or []) if isinstance(row, Mapping)]
    out = []
    for row in rows:
        ext = dict(dict(row.get("extensions") or {}))
        ext["spec_target_kind"] = str(spec_target_kind)
        ext["spec_target_id"] = str(spec_target_id)
        row["extensions"] = ext
        out.append(row)
    return out


def base_state(*, compliance_grade: str = "pass") -> dict:
    if "." not in sys.path:
        sys.path.insert(0, ".")
    from specs import build_spec_binding

    state = copy.deepcopy(sys0_cloned_state())
    system_id = "system.engine.alpha"
    spec_target_kind = "vehicle"
    spec_target_id = "vehicle.engine.alpha"
    spec_id = "spec.track.standard_gauge.v1"

    state["system_rows"] = _configured_system_rows(
        state,
        spec_target_kind=spec_target_kind,
        spec_target_id=spec_target_id,
    )
    state["spec_bindings"] = [
        build_spec_binding(
            spec_id=spec_id,
            target_kind=spec_target_kind,
            target_id=spec_target_id,
            applied_tick=0,
            source_event_id="event.spec.bind.sys5",
        )
    ]
    state["spec_compliance_results"] = [
        {
            "schema_version": "1.0.0",
            "result_id": "result.spec.sys5.{}".format(
                canonical_sha256({"system_id": system_id, "grade": str(compliance_grade).strip().lower()})[:12]
            ),
            "spec_id": spec_id,
            "target_kind": spec_target_kind,
            "target_id": spec_target_id,
            "overall_grade": str(compliance_grade).strip().lower() or "fail",
            "tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["safety_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.sys5.001",
            "pattern_id": "safety.graceful_degrade_basic",
            "target_ids": [system_id],
            "active": True,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state.setdefault("system_certification_result_rows", [])
    state.setdefault("system_certificate_artifact_rows", [])
    state.setdefault("system_certificate_revocation_rows", [])
    state.setdefault("explain_artifact_rows", [])
    return state


def law_profile() -> dict:
    return {
        "law_profile_id": "law.sys5.test",
        "allowed_processes": [
            "process.system_evaluate_certification",
            "process.system_collapse",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.system_evaluate_certification": "entitlement.inspect",
            "process.system_collapse": "session.boot",
        },
        "process_privilege_requirements": {
            "process.system_evaluate_certification": "observer",
            "process.system_collapse": "observer",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys5.test",
        "entitlements": ["entitlement.inspect", "session.boot"],
        "privilege_level": "observer",
    }


def execute_process(
    *,
    repo_root: str,
    state: dict,
    process_id: str,
    inputs: Mapping[str, object] | None = None,
    policy_context: Mapping[str, object] | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys5.{}.{}".format(
                str(process_id).replace(".", "_"),
                canonical_sha256(dict(inputs or {}))[:12],
            ),
            "process_id": str(process_id),
            "inputs": dict(inputs or {}),
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_context or {}),
    )


def execute_system_certification(
    *,
    repo_root: str,
    state: dict,
    system_id: str = "system.engine.alpha",
    cert_type_id: str = "cert.environmental_stub",
) -> dict:
    return execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.system_evaluate_certification",
        inputs={
            "system_id": str(system_id),
            "cert_type_id": str(cert_type_id),
        },
    )


def execute_system_collapse(
    *,
    repo_root: str,
    state: dict,
    system_id: str = "system.engine.alpha",
) -> dict:
    return execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.system_collapse",
        inputs={"system_id": str(system_id)},
    )

