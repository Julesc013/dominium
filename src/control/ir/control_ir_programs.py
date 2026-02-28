"""Canonical Control IR program builders for blueprint/autopilot/AI stubs."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from .control_ir_compiler import verify_and_compile_control_ir


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _op_row(
    *,
    op_id: str,
    op_type: str,
    parameters: Mapping[str, object] | None,
    entitlements: Sequence[str] | None = None,
    capabilities: Sequence[str] | None = None,
    cost_estimate: int = 1,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "op_id": str(op_id),
        "op_type": str(op_type),
        "parameters": dict(parameters or {}),
        "static_requirements": {
            "entitlements": _sorted_unique_strings(list(entitlements or [])),
            "capabilities": _sorted_unique_strings(list(capabilities or [])),
        },
        "cost_estimate": int(max(0, int(cost_estimate))),
        "extensions": {},
    }


def _block_row(*, block_id: str, op_ids: Sequence[str], next_success: str | None = None, next_failure: str | None = None) -> dict:
    return {
        "schema_version": "1.0.0",
        "block_id": str(block_id),
        "op_sequence": [str(token) for token in list(op_ids or []) if str(token).strip()],
        "next_block_on_success": None if next_success is None else str(next_success).strip() or None,
        "next_block_on_failure": None if next_failure is None else str(next_failure).strip() or None,
        "extensions": {},
    }


def _finalize_ir(
    *,
    control_ir_id: str,
    root_block: str,
    blocks: Sequence[Mapping[str, object]],
    op_rows: Sequence[Mapping[str, object]],
    creator: str,
    tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    ir = {
        "schema_version": "1.0.0",
        "control_ir_id": str(control_ir_id),
        "root_block": str(root_block),
        "blocks": [dict(row) for row in list(blocks or []) if isinstance(row, Mapping)],
        "metadata": {
            "creator": str(creator or "controller.unknown"),
            "tick": int(max(0, int(tick))),
        },
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    ir_extensions = dict(ir.get("extensions") or {})
    ir_extensions["op_rows"] = [dict(row) for row in list(op_rows or []) if isinstance(row, Mapping)]
    ir["extensions"] = ir_extensions
    seed = dict(ir)
    seed["deterministic_fingerprint"] = ""
    ir["deterministic_fingerprint"] = canonical_sha256(seed)
    return ir


def build_autopilot_stub_ir(
    *,
    controller_id: str,
    driver_pose_slot_id: str = "pose.driver",
    throttle_task_type_id: str = "task.vehicle.set_throttle",
    reached_target_event_id: str = "event.autopilot.reached_target",
    tick: int = 0,
) -> dict:
    """Build AL1 autopilot stub IR: acquire_pose -> run_task -> wait_event -> release_pose."""

    control_ir_id = "control.ir.autopilot.{}".format(canonical_sha256({"controller_id": str(controller_id)})[:16])
    op_rows = [
        _op_row(
            op_id="op.0001",
            op_type="op.acquire_pose",
            parameters={"pose_slot_id": str(driver_pose_slot_id), "target_kind": "pose_slot", "target_id": str(driver_pose_slot_id)},
            entitlements=["entitlement.tool.operating"],
            capabilities=["capability.pose.enter"],
            cost_estimate=1,
        ),
        _op_row(
            op_id="op.0002",
            op_type="op.run_task",
            parameters={
                "task_type_id": str(throttle_task_type_id),
                "target_semantic_id": str(controller_id),
                "target_kind": "surface",
                "target_id": str(controller_id),
            },
            entitlements=["entitlement.tool.use"],
            capabilities=["capability.surface.execute"],
            cost_estimate=2,
        ),
        _op_row(
            op_id="op.0003",
            op_type="op.wait_event",
            parameters={"event_id": str(reached_target_event_id), "target_semantic_id": str(controller_id)},
            entitlements=[],
            capabilities=[],
            cost_estimate=1,
        ),
        _op_row(
            op_id="op.0004",
            op_type="op.release_pose",
            parameters={"pose_slot_id": str(driver_pose_slot_id), "target_kind": "pose_slot", "target_id": str(driver_pose_slot_id)},
            entitlements=["entitlement.tool.operating"],
            capabilities=["capability.pose.exit"],
            cost_estimate=1,
        ),
    ]
    blocks = [_block_row(block_id="block.main", op_ids=["op.0001", "op.0002", "op.0003", "op.0004"])]
    return _finalize_ir(
        control_ir_id=control_ir_id,
        root_block="block.main",
        blocks=blocks,
        op_rows=op_rows,
        creator="controller.autopilot.stub",
        tick=int(max(0, int(tick))),
        extensions={"stub_kind": "autopilot"},
    )


def build_ai_controller_stub_ir(
    *,
    controller_id: str,
    high_level_order: Mapping[str, object],
    tick: int = 0,
) -> dict:
    """Build deterministic AI-controller stub IR from a high-level order object."""

    order = dict(high_level_order or {})
    order_id = str(order.get("order_id", "")).strip() or "order.ai.default"
    task_sequence = list(order.get("task_sequence") or [])
    if not task_sequence:
        task_sequence = [{"task_type_id": "task.ai.idle", "target_semantic_id": str(controller_id)}]

    op_rows: List[dict] = []
    op_ids: List[str] = []
    op_index = 0
    for row in task_sequence:
        payload = dict(row or {}) if isinstance(row, Mapping) else {"task_type_id": str(row)}
        task_type_id = str(payload.get("task_type_id", "")).strip() or "task.ai.idle"
        target_semantic_id = str(payload.get("target_semantic_id", "")).strip() or str(controller_id)
        run_op_id = "op.{}".format(str(op_index + 1).zfill(4))
        op_rows.append(
            _op_row(
                op_id=run_op_id,
                op_type="op.run_task",
                parameters={
                    "task_type_id": task_type_id,
                    "target_semantic_id": target_semantic_id,
                    "target_kind": str(payload.get("target_kind", "surface")).strip() or "surface",
                    "target_id": str(payload.get("target_id", target_semantic_id)).strip() or target_semantic_id,
                },
                entitlements=["entitlement.tool.use"],
                capabilities=["capability.surface.execute"],
                cost_estimate=int(max(1, int(payload.get("cost_estimate", 2) or 2))),
            )
        )
        op_ids.append(run_op_id)
        op_index += 1

        wait_event_id = str(payload.get("wait_event_id", "")).strip()
        if wait_event_id:
            wait_op_id = "op.{}".format(str(op_index + 1).zfill(4))
            op_rows.append(
                _op_row(
                    op_id=wait_op_id,
                    op_type="op.wait_event",
                    parameters={"event_id": wait_event_id, "target_semantic_id": target_semantic_id},
                    entitlements=[],
                    capabilities=[],
                    cost_estimate=1,
                )
            )
            op_ids.append(wait_op_id)
            op_index += 1

    control_ir_id = "control.ir.ai.{}".format(canonical_sha256({"controller_id": str(controller_id), "order_id": order_id})[:16])
    blocks = [_block_row(block_id="block.main", op_ids=op_ids)]
    return _finalize_ir(
        control_ir_id=control_ir_id,
        root_block="block.main",
        blocks=blocks,
        op_rows=op_rows,
        creator="controller.ai.stub",
        tick=int(max(0, int(tick))),
        extensions={"stub_kind": "ai_controller", "order_id": order_id},
    )


def build_blueprint_execution_ir(
    *,
    project_id: str,
    blueprint_id: str,
    site_ref: str,
    ag_node_ids: Sequence[str],
    actor_subject_id: str,
    tick: int = 0,
) -> dict:
    """Build deterministic blueprint execution IR with stepwise commitment emission."""

    node_ids = _sorted_unique_strings(list(ag_node_ids or []))
    if not node_ids:
        node_ids = ["ag.node.root"]
    op_rows: List[dict] = []
    op_ids: List[str] = []
    op_index = 0
    for ag_node_id in node_ids:
        start_op_id = "op.{}".format(str(op_index + 1).zfill(4))
        op_rows.append(
            _op_row(
                op_id=start_op_id,
                op_type="op.emit_commitment",
                parameters={
                    "project_id": str(project_id),
                    "blueprint_id": str(blueprint_id),
                    "site_ref": str(site_ref),
                    "ag_node_id": str(ag_node_id),
                    "commitment_kind": "construction.step_start",
                    "actor_subject_id": str(actor_subject_id),
                },
                entitlements=["entitlement.control.admin"],
                capabilities=[],
                cost_estimate=1,
            )
        )
        op_ids.append(start_op_id)
        op_index += 1

        task_op_id = "op.{}".format(str(op_index + 1).zfill(4))
        op_rows.append(
            _op_row(
                op_id=task_op_id,
                op_type="op.run_task",
                parameters={
                    "task_type_id": "task.surface.construct_step",
                    "target_semantic_id": str(site_ref),
                    "target_kind": "surface",
                    "target_id": str(site_ref),
                    "project_id": str(project_id),
                    "ag_node_id": str(ag_node_id),
                },
                entitlements=["entitlement.tool.use"],
                capabilities=["capability.surface.execute"],
                cost_estimate=2,
            )
        )
        op_ids.append(task_op_id)
        op_index += 1

        wait_op_id = "op.{}".format(str(op_index + 1).zfill(4))
        op_rows.append(
            _op_row(
                op_id=wait_op_id,
                op_type="op.wait_event",
                parameters={
                    "event_id": "event.construction.step.completed",
                    "project_id": str(project_id),
                    "ag_node_id": str(ag_node_id),
                },
                entitlements=[],
                capabilities=[],
                cost_estimate=1,
            )
        )
        op_ids.append(wait_op_id)
        op_index += 1

        end_op_id = "op.{}".format(str(op_index + 1).zfill(4))
        op_rows.append(
            _op_row(
                op_id=end_op_id,
                op_type="op.emit_commitment",
                parameters={
                    "project_id": str(project_id),
                    "blueprint_id": str(blueprint_id),
                    "site_ref": str(site_ref),
                    "ag_node_id": str(ag_node_id),
                    "commitment_kind": "construction.step_end",
                    "actor_subject_id": str(actor_subject_id),
                },
                entitlements=["entitlement.control.admin"],
                capabilities=[],
                cost_estimate=1,
            )
        )
        op_ids.append(end_op_id)
        op_index += 1

    control_ir_id = "control.ir.blueprint.{}".format(
        canonical_sha256({"project_id": str(project_id), "blueprint_id": str(blueprint_id), "site_ref": str(site_ref)})[:16]
    )
    blocks = [_block_row(block_id="block.main", op_ids=op_ids)]
    return _finalize_ir(
        control_ir_id=control_ir_id,
        root_block="block.main",
        blocks=blocks,
        op_rows=op_rows,
        creator="planner.blueprint.execution",
        tick=int(max(0, int(tick))),
        extensions={"stub_kind": "blueprint_execution", "project_id": str(project_id), "blueprint_id": str(blueprint_id)},
    )


def compile_ir_program(
    *,
    ir_program: Mapping[str, object],
    control_policy: Mapping[str, object],
    authority_context: Mapping[str, object],
    capability_registry: Mapping[str, object] | None,
    law_profile: Mapping[str, object],
    control_action_registry: Mapping[str, object],
    control_policy_registry: Mapping[str, object],
    policy_context: Mapping[str, object] | None = None,
    repo_root: str = "",
    rs5_budget_units: int = 0,
) -> dict:
    """Compile a generated Control IR program through verifier + control-plane compiler."""

    return verify_and_compile_control_ir(
        ir_program=dict(ir_program or {}),
        control_policy=dict(control_policy or {}),
        authority_context=dict(authority_context or {}),
        capability_registry=capability_registry,
        law_profile=dict(law_profile or {}),
        control_action_registry=dict(control_action_registry or {}),
        control_policy_registry=dict(control_policy_registry or {}),
        policy_context=policy_context,
        repo_root=repo_root,
        rs5_budget_units=int(max(0, int(rs5_budget_units))),
    )


__all__ = [
    "build_ai_controller_stub_ir",
    "build_autopilot_stub_ir",
    "build_blueprint_execution_ir",
    "compile_ir_program",
]
