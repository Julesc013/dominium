"""Deterministic compiler from verified Control IR to control-plane actions."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from ..control_plane_engine import build_control_intent, build_control_resolution
from .control_ir_verifier import (
    REFUSAL_CTRL_IR_COST_EXCEEDED,
    REFUSAL_CTRL_IR_INVALID,
    verify_control_ir,
)


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _refusal(
    reason_code: str,
    message: str,
    remediation_hint: str,
    relevant_ids: Mapping[str, object] | None = None,
    path: str = "$",
) -> dict:
    ids = {}
    for key, value in sorted((dict(relevant_ids or {})).items(), key=lambda item: str(item[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    refusal_row = {
        "reason_code": str(reason_code),
        "message": str(message),
        "remediation_hint": str(remediation_hint),
        "relevant_ids": ids,
        "path": str(path),
    }
    return {
        "result": "refused",
        "refusal": refusal_row,
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def _block_rows_by_id(ir_program: Mapping[str, object]) -> Dict[str, dict]:
    rows = (dict(ir_program or {})).get("blocks")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        block_id = str(row.get("block_id", "")).strip()
        if not block_id:
            continue
        out[block_id] = dict(row)
    return out


def _op_rows_by_id(ir_program: Mapping[str, object]) -> Dict[str, dict]:
    ext = _as_map((dict(ir_program or {})).get("extensions"))
    rows = ext.get("op_rows")
    if not isinstance(rows, list):
        rows = ext.get("ops")
    if not isinstance(rows, list):
        return {}
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        op_id = str(row.get("op_id", "")).strip()
        if not op_id:
            continue
        out[op_id] = dict(row)
    return out


def _ordered_block_ids(ir_program: Mapping[str, object]) -> List[str]:
    block_rows_by_id = _block_rows_by_id(ir_program)
    root_block = str((dict(ir_program or {})).get("root_block", "")).strip()
    if root_block not in block_rows_by_id:
        return []
    ordered: List[str] = []
    queued: List[str] = [root_block]
    seen: set = set()
    while queued:
        block_id = str(queued.pop(0)).strip()
        if not block_id or block_id in seen:
            continue
        if block_id not in block_rows_by_id:
            continue
        seen.add(block_id)
        ordered.append(block_id)
        row = dict(block_rows_by_id[block_id])
        for key in ("next_block_on_success", "next_block_on_failure"):
            value = row.get(key)
            next_block = "" if value is None else str(value).strip()
            if (not next_block) or next_block in seen or next_block in queued:
                continue
            queued.append(next_block)
    return ordered


def _ordered_ops(ir_program: Mapping[str, object]) -> List[Tuple[str, str, dict]]:
    out: List[Tuple[str, str, dict]] = []
    block_rows_by_id = _block_rows_by_id(ir_program)
    op_rows_by_id = _op_rows_by_id(ir_program)
    for block_id in _ordered_block_ids(ir_program):
        row = dict(block_rows_by_id.get(block_id) or {})
        op_sequence = row.get("op_sequence")
        if not isinstance(op_sequence, list):
            continue
        for op_id_raw in op_sequence:
            op_id = str(op_id_raw).strip()
            if not op_id:
                continue
            op_row = dict(op_rows_by_id.get(op_id) or {})
            if not op_row:
                continue
            out.append((block_id, op_id, op_row))
    return out


def _policy_rs5_budget_units(
    *,
    explicit_budget_units: int,
    control_policy: Mapping[str, object],
    policy_context: Mapping[str, object],
) -> int:
    explicit = int(max(0, _to_int(explicit_budget_units, 0)))
    if explicit > 0:
        return explicit
    context = dict(policy_context or {})
    control_ext = _as_map((dict(control_policy or {})).get("extensions"))
    for token in (
        context.get("rs5_budget_units"),
        context.get("max_control_cost_units"),
        control_ext.get("rs5_budget_units"),
        control_ext.get("max_control_cost_units"),
    ):
        value = int(max(0, _to_int(token, 0)))
        if value > 0:
            return value
    return 0


def _requester_subject_id(authority_context: Mapping[str, object]) -> str:
    authority = dict(authority_context or {})
    for token in (
        authority.get("subject_id"),
        authority.get("agent_id"),
        authority.get("controller_id"),
        authority.get("peer_id"),
    ):
        value = str(token or "").strip()
        if value:
            return value
    return "subject.unknown"


def _request_vector_defaults(
    *,
    control_policy: Mapping[str, object],
    policy_context: Mapping[str, object],
) -> Tuple[str, str, str]:
    context = dict(policy_context or {})
    abstraction = str(context.get("abstraction_level_requested", "")).strip()
    if not abstraction:
        allowed = _sorted_unique_strings((dict(control_policy or {})).get("allowed_abstraction_levels"))
        abstraction = allowed[0] if allowed else "AL0"
    fidelity = str(context.get("fidelity_requested", "")).strip() or "meso"
    view = str(context.get("view_requested", "")).strip() or "view.mode.first_person"
    return abstraction, fidelity, view


def _wait_condition(op_id: str, op_type: str, parameters: Mapping[str, object]) -> dict:
    seed = {"op_id": str(op_id), "op_type": str(op_type), "parameters": dict(parameters or {})}
    wait_id = "wait.condition.{}".format(canonical_sha256(seed)[:16])
    return {
        "wait_condition_id": wait_id,
        "op_id": str(op_id),
        "condition_type": "event" if op_type == "op.wait_event" else "predicate",
        "parameters": dict(parameters or {}),
    }


def _control_action_for_op(op_type: str) -> Tuple[str, str, str]:
    if op_type == "op.acquire_pose":
        return "action.pose.enter", "pose_slot", "process.pose_enter"
    if op_type == "op.release_pose":
        return "action.pose.exit", "pose_slot", "process.pose_exit"
    if op_type == "op.bind_tool":
        return "action.interaction.execute_process", "surface", "process.tool_bind"
    if op_type == "op.unbind_tool":
        return "action.interaction.execute_process", "surface", "process.tool_unbind"
    if op_type == "op.run_task":
        return "action.surface.execute_task", "surface", "process.task_create"
    if op_type == "op.emit_commitment":
        return "action.interaction.execute_process", "structure", "process.commitment_create"
    if op_type == "op.request_view_change":
        return "action.view.change", "none", "process.camera_set_view_mode"
    return "", "", ""


def _control_parameters(op_type: str, raw_parameters: Mapping[str, object], default_process_id: str) -> dict:
    params = dict(raw_parameters or {})
    if op_type in ("op.bind_tool", "op.unbind_tool", "op.emit_commitment"):
        if not str(params.get("process_id", "")).strip():
            params["process_id"] = str(default_process_id)
    if op_type == "op.run_task":
        process_id_to_execute = str(params.get("process_id_to_execute", "")).strip()
        if not process_id_to_execute:
            process_id_to_execute = str(params.get("process_id", "")).strip()
        if process_id_to_execute:
            params["process_id_to_execute"] = process_id_to_execute
        params.pop("process_id", None)
    if op_type == "op.request_view_change":
        if not str(params.get("view_mode_id", "")).strip():
            view_requested = str(params.get("view_requested", "")).strip()
            if view_requested:
                params["view_mode_id"] = view_requested
    return params


def compile_control_ir(
    *,
    ir_program: Mapping[str, object],
    verification_report: Mapping[str, object],
    law_profile: Mapping[str, object],
    authority_context: Mapping[str, object],
    control_policy: Mapping[str, object],
    control_action_registry: Mapping[str, object],
    control_policy_registry: Mapping[str, object],
    action_template_registry: Mapping[str, object] | None = None,
    policy_context: Mapping[str, object] | None = None,
    repo_root: str = "",
    rs5_budget_units: int = 0,
) -> dict:
    """Compile a verified Control IR program into ordered control-plane actions."""

    ir = dict(ir_program or {})
    report = dict(verification_report or {})
    if not bool(report.get("valid", False)):
        return _refusal(
            REFUSAL_CTRL_IR_INVALID,
            "Control IR verification report is invalid",
            "Run verify_control_ir and fix reported violations before compiling.",
            {"ir_id": str(ir.get("control_ir_id", "")).strip()},
            "$.verification_report",
        )

    expected_hash = str(report.get("deterministic_fingerprint", "")).strip()
    verification_seed = dict(report)
    verification_seed["deterministic_fingerprint"] = ""
    verification_hash = canonical_sha256(verification_seed)
    if expected_hash and expected_hash != verification_hash:
        return _refusal(
            REFUSAL_CTRL_IR_INVALID,
            "verification report fingerprint mismatch",
            "Use an untampered verification report generated from the same IR payload.",
            {"ir_id": str(ir.get("control_ir_id", "")).strip()},
            "$.verification_report.deterministic_fingerprint",
        )

    resolved_budget = _policy_rs5_budget_units(
        explicit_budget_units=int(rs5_budget_units),
        control_policy=control_policy,
        policy_context=dict(policy_context or {}),
    )
    max_cost_estimate = int(max(0, _to_int(report.get("max_cost_estimate", 0), 0)))
    if resolved_budget > 0 and max_cost_estimate > resolved_budget:
        return _refusal(
            REFUSAL_CTRL_IR_COST_EXCEEDED,
            "Control IR cost estimate exceeds RS-5 budget",
            "Reduce op cost_estimate totals or increase rs5_budget_units under policy.",
            {
                "ir_id": str(ir.get("control_ir_id", "")).strip(),
                "max_cost_estimate": str(max_cost_estimate),
                "rs5_budget_units": str(resolved_budget),
            },
            "$.verification_report.max_cost_estimate",
        )

    abstraction_default, fidelity_default, view_default = _request_vector_defaults(
        control_policy=control_policy,
        policy_context=dict(policy_context or {}),
    )
    created_tick_base = int(max(0, _to_int(_as_map(ir.get("metadata")).get("tick", 0), 0)))
    requester_subject_id = _requester_subject_id(authority_context)

    ir_id = str(ir.get("control_ir_id", "")).strip()
    op_execution_order: List[str] = []
    compiled_actions: List[dict] = []
    op_to_emitted: List[dict] = []
    wait_conditions: List[dict] = []
    task_starts: List[dict] = []
    commitment_creations: List[dict] = []
    downgrade_rows: List[dict] = []

    for op_index, (block_id, op_id, op_row) in enumerate(_ordered_ops(ir)):
        op_type = str(op_row.get("op_type", "")).strip()
        raw_parameters = _as_map(op_row.get("parameters"))
        op_execution_order.append(op_id)
        mapping_row = {
            "op_id": op_id,
            "block_id": str(block_id),
            "op_type": op_type,
            "control_intent_id": "",
            "resolution_id": "",
            "decision_log_ref": "",
            "emitted_intent_ids": [],
            "emitted_envelope_ids": [],
            "emitted_commitment_ids": [],
            "wait_condition_ids": [],
        }

        if op_type in ("op.wait_event", "op.check_condition"):
            wait_row = _wait_condition(op_id=op_id, op_type=op_type, parameters=raw_parameters)
            wait_conditions.append(wait_row)
            mapping_row["wait_condition_ids"] = [str(wait_row.get("wait_condition_id", ""))]
            op_to_emitted.append(mapping_row)
            continue
        if op_type in ("op.noop", "op.request_fidelity"):
            op_to_emitted.append(mapping_row)
            continue

        action_id, target_kind_default, default_process_id = _control_action_for_op(op_type)
        if not action_id:
            return _refusal(
                REFUSAL_CTRL_IR_INVALID,
                "op_type cannot be compiled to control-plane action",
                "Use only compile-supported op_type values in this compiler revision.",
                {"op_id": op_id, "op_type": op_type},
                "$.extensions.op_rows",
            )

        target_kind = str(raw_parameters.get("target_kind", "")).strip() or target_kind_default
        target_id = str(
            raw_parameters.get("target_id", "")
            or raw_parameters.get("target_semantic_id", "")
            or raw_parameters.get("pose_slot_id", "")
            or raw_parameters.get("asset_id", "")
        ).strip()
        if not target_id:
            target_id_value = None
        else:
            target_id_value = target_id

        op_abstraction = str(raw_parameters.get("abstraction_level_requested", "")).strip() or abstraction_default
        op_fidelity = str(raw_parameters.get("fidelity_requested", "")).strip() or fidelity_default
        op_view = str(raw_parameters.get("view_requested", "")).strip() or view_default
        control_parameters = _control_parameters(
            op_type=op_type,
            raw_parameters=raw_parameters,
            default_process_id=default_process_id,
        )
        control_intent = build_control_intent(
            requester_subject_id=requester_subject_id,
            requested_action_id=action_id,
            target_kind=target_kind,
            target_id=target_id_value,
            parameters=control_parameters,
            abstraction_level_requested=op_abstraction,
            fidelity_requested=op_fidelity,
            view_requested=op_view,
            inspection_requested=str(raw_parameters.get("inspection_requested", "none")),
            reenactment_requested=str(raw_parameters.get("reenactment_requested", "none")),
            created_tick=int(created_tick_base + op_index),
        )
        mapping_row["control_intent_id"] = str(control_intent.get("control_intent_id", ""))
        control_policy_context = dict(policy_context or {})
        control_policy_context.setdefault("submission_tick", int(created_tick_base + op_index))
        control_policy_context.setdefault("deterministic_sequence_number", int(op_index))
        control_policy_context["control_ir_execution"] = {
            "ir_id": ir_id,
            "verification_report_hash": verification_hash,
            "op_id": op_id,
            "op_type": op_type,
            "block_id": str(block_id),
            "op_index": int(op_index),
            "control_action_id": action_id,
        }

        resolved = build_control_resolution(
            control_intent=dict(control_intent),
            law_profile=dict(law_profile or {}),
            authority_context=dict(authority_context or {}),
            policy_context=control_policy_context,
            control_action_registry=dict(control_action_registry or {}),
            control_policy_registry=dict(control_policy_registry or {}),
            action_template_registry=dict(action_template_registry or {}),
            repo_root=str(repo_root or ""),
        )
        if str(resolved.get("result", "")) != "complete":
            refusal_row = dict(resolved.get("refusal") or {})
            if not refusal_row:
                refusal_row = {
                    "reason_code": REFUSAL_CTRL_IR_INVALID,
                    "message": "control-plane resolution refused compiled op",
                    "remediation_hint": "Adjust op parameters or authority/policy constraints.",
                    "relevant_ids": {"op_id": op_id},
                    "path": "$.extensions.op_rows",
                }
            out = dict(
                _refusal(
                    str(refusal_row.get("reason_code", REFUSAL_CTRL_IR_INVALID)),
                    str(refusal_row.get("message", "compiled op refused")),
                    str(refusal_row.get("remediation_hint", "Fix compiled op parameters and retry.")),
                    dict(refusal_row.get("relevant_ids") or {}),
                    str(refusal_row.get("path", "$")),
                )
            )
            out["control_intent"] = control_intent
            out["op_id"] = op_id
            return out

        resolution = dict(resolved.get("resolution") or {})
        mapping_row["resolution_id"] = str(resolution.get("resolution_id", ""))
        mapping_row["decision_log_ref"] = str(resolution.get("decision_log_ref", ""))
        emitted_intents = [dict(row) for row in list(resolution.get("emitted_intents") or []) if isinstance(row, Mapping)]
        emitted_envelopes = [
            dict(row) for row in list(resolution.get("emitted_intent_envelopes") or []) if isinstance(row, Mapping)
        ]
        emitted_commitment_ids = _sorted_unique_strings(resolution.get("emitted_commitment_ids"))

        mapping_row["emitted_intent_ids"] = sorted(
            str(row.get("intent_id", "")).strip() for row in emitted_intents if str(row.get("intent_id", "")).strip()
        )
        mapping_row["emitted_envelope_ids"] = sorted(
            str(row.get("envelope_id", "")).strip()
            for row in emitted_envelopes
            if str(row.get("envelope_id", "")).strip()
        )
        mapping_row["emitted_commitment_ids"] = emitted_commitment_ids

        for row in emitted_intents:
            process_id = str(row.get("process_id", "")).strip()
            if process_id == "process.task_create":
                task_starts.append(
                    {
                        "op_id": op_id,
                        "intent_id": str(row.get("intent_id", "")),
                        "process_id": process_id,
                        "inputs": dict(row.get("inputs") or {}),
                    }
                )
            if process_id == "process.commitment_create":
                commitment_creations.append(
                    {
                        "op_id": op_id,
                        "intent_id": str(row.get("intent_id", "")),
                        "process_id": process_id,
                        "inputs": dict(row.get("inputs") or {}),
                    }
                )
        for commitment_id in emitted_commitment_ids:
            commitment_creations.append(
                {
                    "op_id": op_id,
                    "intent_id": "",
                    "process_id": "process.commitment_create",
                    "commitment_id": commitment_id,
                    "inputs": {},
                }
            )

        downgrade_reasons = _sorted_unique_strings(resolution.get("downgrade_reasons"))
        for reason in downgrade_reasons:
            downgrade_rows.append(
                {
                    "op_id": op_id,
                    "reason_code": reason,
                }
            )
        compiled_actions.append(
            {
                "op_id": op_id,
                "block_id": str(block_id),
                "op_type": op_type,
                "control_intent": control_intent,
                "resolution": resolution,
            }
        )
        op_to_emitted.append(mapping_row)

    compiled = {
        "result": "complete",
        "control_ir_id": ir_id,
        "verification_report_hash": verification_hash,
        "rs5_budget_units": int(resolved_budget),
        "cost_estimate_used": int(max_cost_estimate),
        "op_execution_order": op_execution_order,
        "compiled_actions": compiled_actions,
        "op_to_emitted": op_to_emitted,
        "decision_log_refs": _sorted_unique_strings([row.get("decision_log_ref") for row in op_to_emitted]),
        "task_starts": task_starts,
        "commitment_creations": commitment_creations,
        "wait_conditions": wait_conditions,
        "downgrades": sorted(
            downgrade_rows,
            key=lambda row: (str(row.get("op_id", "")), str(row.get("reason_code", ""))),
        ),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    seed = dict(compiled)
    seed["deterministic_fingerprint"] = ""
    compiled["deterministic_fingerprint"] = canonical_sha256(seed)
    return compiled


def reconstruct_ir_action_sequence(
    *,
    decision_log_rows: Sequence[Mapping[str, object]],
    ir_id: str = "",
) -> dict:
    """Reconstruct deterministic IR action sequence from control decision-log rows."""

    requested_ir_id = str(ir_id or "").strip()
    sequence_rows: List[dict] = []
    resolved_ir_id = requested_ir_id
    for row in list(decision_log_rows or []):
        if not isinstance(row, Mapping):
            continue
        ext = _as_map((dict(row or {})).get("extensions"))
        ir_ext = _as_map(ext.get("control_ir_execution"))
        row_ir_id = str(ir_ext.get("ir_id", "")).strip()
        if not row_ir_id:
            continue
        if requested_ir_id and row_ir_id != requested_ir_id:
            continue
        if not resolved_ir_id:
            resolved_ir_id = row_ir_id
        if row_ir_id != resolved_ir_id:
            continue
        policy_ids_applied = _sorted_unique_strings((dict(row or {})).get("policy_ids_applied"))
        emitted_ids = _as_map((dict(row or {})).get("emitted_ids"))
        downgrade_entries = [
            dict(item)
            for item in list(ext.get("downgrade_entries") or [])
            if isinstance(item, Mapping)
        ]
        downgrade_reasons = _sorted_unique_strings([item.get("reason_code") for item in downgrade_entries])
        refusal_codes = _sorted_unique_strings((dict(row or {})).get("refusals"))

        # Backward compatibility with legacy CTRL-1/CTRL-2 decision-log rows.
        if not downgrade_reasons or not refusal_codes:
            reasons = _as_map((dict(row or {})).get("reasons"))
            if not downgrade_reasons:
                downgrade_reasons = _sorted_unique_strings(reasons.get("downgrade_reasons"))
            if not refusal_codes:
                legacy_refusal_row = _as_map(reasons.get("refusal"))
                legacy_code = str(legacy_refusal_row.get("reason_code", "")).strip()
                if legacy_code:
                    refusal_codes = [legacy_code]

        control_policy_id = str((dict(row or {})).get("control_policy_id", "")).strip()
        if not control_policy_id and policy_ids_applied:
            control_policy_id = str(policy_ids_applied[0])
        sequence_rows.append(
            {
                "op_index": int(max(0, _to_int(ir_ext.get("op_index", 0), 0))),
                "op_id": str(ir_ext.get("op_id", "")).strip(),
                "op_type": str(ir_ext.get("op_type", "")).strip(),
                "block_id": str(ir_ext.get("block_id", "")).strip(),
                "control_action_id": str(ir_ext.get("control_action_id", "")).strip(),
                "control_intent_id": str((dict(row or {})).get("control_intent_id", "")).strip(),
                "tick": int(max(0, _to_int((dict(row or {})).get("tick", 0), 0))),
                "control_policy_id": control_policy_id,
                "emitted_ids": {
                    "intent_ids": _sorted_unique_strings(emitted_ids.get("intent_ids")),
                    "commitment_ids": _sorted_unique_strings(emitted_ids.get("commitment_ids")),
                    "envelope_ids": _sorted_unique_strings(emitted_ids.get("envelope_ids")),
                },
                "downgrade_reasons": downgrade_reasons,
                "refusal_codes": refusal_codes,
                "refusal_code": str((refusal_codes or [""])[0]),
                "verification_report_hash": str(ir_ext.get("verification_report_hash", "")).strip(),
                "decision_id": str((dict(row or {})).get("decision_id", "")).strip(),
            }
        )
    ordered = sorted(
        sequence_rows,
        key=lambda row: (
            int(row.get("op_index", 0) or 0),
            int(row.get("tick", 0) or 0),
            str(row.get("control_intent_id", "")),
            str(row.get("decision_id", "")),
        ),
    )
    out = {
        "ir_id": resolved_ir_id or "control.ir.unknown",
        "action_sequence": ordered,
        "deterministic_fingerprint": "",
    }
    seed = dict(out)
    seed["deterministic_fingerprint"] = ""
    out["deterministic_fingerprint"] = canonical_sha256(seed)
    return out


def verify_and_compile_control_ir(
    *,
    ir_program: Mapping[str, object],
    control_policy: Mapping[str, object],
    authority_context: Mapping[str, object],
    capability_registry: Mapping[str, object] | None,
    law_profile: Mapping[str, object],
    control_action_registry: Mapping[str, object],
    control_policy_registry: Mapping[str, object],
    action_template_registry: Mapping[str, object] | None = None,
    policy_context: Mapping[str, object] | None = None,
    repo_root: str = "",
    rs5_budget_units: int = 0,
) -> dict:
    """Convenience entrypoint: verify then compile Control IR deterministically."""

    verification_report = verify_control_ir(
        ir_program=ir_program,
        control_policy=control_policy,
        authority_context=authority_context,
        capability_registry=capability_registry,
    )
    compiled = compile_control_ir(
        ir_program=ir_program,
        verification_report=verification_report,
        law_profile=law_profile,
        authority_context=authority_context,
        control_policy=control_policy,
        control_action_registry=control_action_registry,
        control_policy_registry=control_policy_registry,
        action_template_registry=action_template_registry,
        policy_context=policy_context,
        repo_root=repo_root,
        rs5_budget_units=rs5_budget_units,
    )
    compiled["verification_report"] = verification_report
    return compiled


__all__ = [
    "compile_control_ir",
    "reconstruct_ir_action_sequence",
    "verify_and_compile_control_ir",
]
