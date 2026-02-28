"""Deterministic static verifier for restricted Control IR programs."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_CTRL_IR_INVALID = "refusal.ctrl.ir_invalid"
REFUSAL_CTRL_IR_FORBIDDEN_OP = "refusal.ctrl.ir_forbidden_op"
REFUSAL_CTRL_IR_COST_EXCEEDED = "refusal.ctrl.ir_cost_exceeded"

ALLOWED_CONTROL_IR_OP_TYPES = (
    "op.acquire_pose",
    "op.release_pose",
    "op.bind_tool",
    "op.unbind_tool",
    "op.run_task",
    "op.emit_commitment",
    "op.wait_event",
    "op.check_condition",
    "op.request_view_change",
    "op.request_fidelity",
    "op.noop",
)
_ALLOWED_OP_TYPES_SET = set(ALLOWED_CONTROL_IR_OP_TYPES)

_ABSTRACTION_LEVELS = ("AL0", "AL1", "AL2", "AL3", "AL4")
_ABSTRACTION_RANK = dict((token, idx) for idx, token in enumerate(_ABSTRACTION_LEVELS))
_OP_MIN_ABSTRACTION = {
    "op.acquire_pose": "AL0",
    "op.release_pose": "AL0",
    "op.bind_tool": "AL0",
    "op.unbind_tool": "AL0",
    "op.run_task": "AL0",
    "op.emit_commitment": "AL2",
    "op.wait_event": "AL1",
    "op.check_condition": "AL1",
    "op.request_view_change": "AL0",
    "op.request_fidelity": "AL1",
    "op.noop": "AL0",
}

_FORBIDDEN_DYNAMIC_PARAMETER_KEYS = {
    "eval",
    "script",
    "python",
    "code",
    "compile",
    "exec",
    "goto",
    "jump",
    "jump_block",
    "next_block",
    "branch_expr",
}


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _control_ir_id(ir_program: Mapping[str, object]) -> str:
    return str((dict(ir_program or {})).get("control_ir_id", "")).strip()


def _block_rows(ir_program: Mapping[str, object]) -> List[dict]:
    rows = (dict(ir_program or {})).get("blocks")
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _op_rows(ir_program: Mapping[str, object]) -> List[dict]:
    ext = _as_map((dict(ir_program or {})).get("extensions"))
    for key in ("op_rows", "ops"):
        rows = ext.get(key)
        if isinstance(rows, list):
            return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _op_rows_by_id(ir_program: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(_op_rows(ir_program), key=lambda item: str(item.get("op_id", ""))):
        op_id = str(row.get("op_id", "")).strip()
        if not op_id:
            continue
        out[op_id] = row
    return out


def _block_rows_by_id(ir_program: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _block_rows(ir_program):
        block_id = str(row.get("block_id", "")).strip()
        if not block_id:
            continue
        out[block_id] = row
    return out


def _known_capabilities(capability_registry: Mapping[str, object] | None) -> List[str]:
    payload = dict(capability_registry or {})
    rows = payload.get("capabilities")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("capabilities")
    if not isinstance(rows, list):
        return []
    out = set()
    for row in rows:
        if isinstance(row, Mapping):
            token = str(row.get("capability_id", "")).strip() or str(row.get("id", "")).strip()
        else:
            token = str(row).strip()
        if token:
            out.add(token)
    return sorted(out)


def _allowed_op_types(control_policy: Mapping[str, object]) -> List[str]:
    ext = _as_map((dict(control_policy or {})).get("extensions"))
    configured = _sorted_unique_strings(ext.get("allowed_ir_op_types"))
    if configured:
        return configured
    return list(ALLOWED_CONTROL_IR_OP_TYPES)


def _allowed_max_abstraction_rank(control_policy: Mapping[str, object]) -> int:
    allowed = _sorted_unique_strings((dict(control_policy or {})).get("allowed_abstraction_levels"))
    ranks = [int(_ABSTRACTION_RANK[token]) for token in allowed if token in _ABSTRACTION_RANK]
    if not ranks:
        return int(_ABSTRACTION_RANK["AL4"])
    return int(max(ranks))


def _bounded_cycle_nodes(ir_program: Mapping[str, object], cycle_nodes: Sequence[str]) -> bool:
    ext = _as_map((dict(ir_program or {})).get("extensions"))
    bounds = _as_map(ext.get("block_visit_bounds"))
    if not bounds and int(_to_int(ext.get("max_cycle_visits", 0), 0)) > 0:
        return True
    for block_id in cycle_nodes:
        if int(_to_int(bounds.get(str(block_id), 0), 0)) <= 0:
            return False
    return bool(cycle_nodes)


def _graph_edges(block_rows_by_id: Mapping[str, dict]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for block_id in sorted(block_rows_by_id.keys()):
        row = dict(block_rows_by_id[block_id])
        edges: List[str] = []
        for key in ("next_block_on_success", "next_block_on_failure"):
            value = row.get(key)
            token = "" if value is None else str(value).strip()
            if token:
                edges.append(token)
        out[block_id] = sorted(set(edges))
    return out


def _cycle_nodes(graph: Mapping[str, List[str]]) -> List[str]:
    visited: set = set()
    stack: set = set()
    cycles: set = set()

    def dfs(node_id: str) -> None:
        visited.add(node_id)
        stack.add(node_id)
        for next_id in list(graph.get(node_id, [])):
            if next_id not in graph:
                continue
            if next_id not in visited:
                dfs(next_id)
                continue
            if next_id in stack:
                cycles.add(node_id)
                cycles.add(next_id)
        stack.remove(node_id)

    for node_id in sorted(graph.keys()):
        if node_id in visited:
            continue
        dfs(node_id)
    return sorted(cycles)


def _violation(code: str, message: str, path: str, relevant_ids: Mapping[str, object] | None = None) -> dict:
    ids = {}
    for key, value in sorted((dict(relevant_ids or {})).items(), key=lambda item: str(item[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "code": str(code),
        "message": str(message),
        "path": str(path),
        "relevant_ids": ids,
    }


def _sorted_violations(rows: Iterable[Mapping[str, object]]) -> List[dict]:
    out = [dict(row) for row in rows if isinstance(row, Mapping)]
    return sorted(
        out,
        key=lambda row: (
            str(row.get("path", "")),
            str(row.get("code", "")),
            str(row.get("message", "")),
            canonical_sha256(dict(row.get("relevant_ids") or {})),
        ),
    )


def verify_control_ir(
    *,
    ir_program: Mapping[str, object],
    control_policy: Mapping[str, object],
    authority_context: Mapping[str, object],
    capability_registry: Mapping[str, object] | None = None,
) -> dict:
    """Return deterministic static verification report for a Control IR payload."""

    ir = dict(ir_program or {})
    policy = dict(control_policy or {})
    authority = dict(authority_context or {})
    ir_id = _control_ir_id(ir)
    block_rows_by_id = _block_rows_by_id(ir)
    op_rows_by_id = _op_rows_by_id(ir)
    violations: List[dict] = []

    if not ir_id:
        violations.append(
            _violation(
                REFUSAL_CTRL_IR_INVALID,
                "control_ir_id is required",
                "$.control_ir_id",
            )
        )
    root_block = str(ir.get("root_block", "")).strip()
    if not root_block:
        violations.append(_violation(REFUSAL_CTRL_IR_INVALID, "root_block is required", "$.root_block"))
    elif root_block not in block_rows_by_id:
        violations.append(
            _violation(
                REFUSAL_CTRL_IR_INVALID,
                "root_block must reference an existing block",
                "$.root_block",
                {"root_block": root_block},
            )
        )
    if not block_rows_by_id:
        violations.append(_violation(REFUSAL_CTRL_IR_INVALID, "at least one block is required", "$.blocks"))
    if not op_rows_by_id:
        violations.append(_violation(REFUSAL_CTRL_IR_INVALID, "extensions.op_rows is required", "$.extensions.op_rows"))

    allowed_op_types = set(_allowed_op_types(policy))
    allowed_max_rank = _allowed_max_abstraction_rank(policy)
    requester_entitlements = set(_sorted_unique_strings(authority.get("entitlements")))
    policy_ext = _as_map(policy.get("extensions"))
    forbidden_entitlements = set(_sorted_unique_strings(policy_ext.get("forbidden_entitlements")))
    forbidden_capabilities = set(_sorted_unique_strings(policy_ext.get("forbidden_capabilities")))
    known_capabilities = set(_known_capabilities(capability_registry))

    required_entitlements: set = set()
    required_capabilities: set = set()
    max_cost_estimate = 0

    for block_id in sorted(block_rows_by_id.keys()):
        row = dict(block_rows_by_id[block_id])
        for key in ("next_block_on_success", "next_block_on_failure"):
            value = row.get(key)
            token = "" if value is None else str(value).strip()
            if token and token not in block_rows_by_id:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_INVALID,
                        "{} references unknown block".format(key),
                        "$.blocks[{}].{}".format(block_id, key),
                        {"block_id": block_id, "next_block_id": token},
                    )
                )
        op_sequence = row.get("op_sequence")
        if not isinstance(op_sequence, list):
            violations.append(
                _violation(
                    REFUSAL_CTRL_IR_INVALID,
                    "op_sequence must be an ordered list of op_id",
                    "$.blocks[{}].op_sequence".format(block_id),
                    {"block_id": block_id},
                )
            )
            continue
        for op_index, op_id_raw in enumerate(op_sequence):
            op_id = str(op_id_raw).strip()
            if not op_id:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_INVALID,
                        "op_sequence entries must be non-empty op_id",
                        "$.blocks[{}].op_sequence[{}]".format(block_id, int(op_index)),
                        {"block_id": block_id},
                    )
                )
                continue
            op_row = dict(op_rows_by_id.get(op_id) or {})
            if not op_row:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_INVALID,
                        "op_sequence references unknown op_id",
                        "$.blocks[{}].op_sequence[{}]".format(block_id, int(op_index)),
                        {"block_id": block_id, "op_id": op_id},
                    )
                )
                continue
            op_type = str(op_row.get("op_type", "")).strip()
            if op_type not in _ALLOWED_OP_TYPES_SET:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_FORBIDDEN_OP,
                        "op_type is not permitted by restricted Control IR",
                        "$.extensions.op_rows[{}].op_type".format(op_id),
                        {"op_id": op_id, "op_type": op_type},
                    )
                )
            elif op_type not in allowed_op_types:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_FORBIDDEN_OP,
                        "op_type is forbidden by control policy",
                        "$.extensions.op_rows[{}].op_type".format(op_id),
                        {"op_id": op_id, "op_type": op_type},
                    )
                )

            min_al = str(_OP_MIN_ABSTRACTION.get(op_type, "AL4"))
            if int(_ABSTRACTION_RANK.get(min_al, 4)) > int(allowed_max_rank):
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_FORBIDDEN_OP,
                        "op_type requires higher abstraction than policy allows",
                        "$.extensions.op_rows[{}].op_type".format(op_id),
                        {"op_id": op_id, "op_type": op_type, "min_abstraction": min_al},
                    )
                )

            parameters = _as_map(op_row.get("parameters"))
            for key in sorted(parameters.keys()):
                if str(key).strip().lower() not in _FORBIDDEN_DYNAMIC_PARAMETER_KEYS:
                    continue
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_INVALID,
                        "dynamic evaluation/branch parameter is forbidden",
                        "$.extensions.op_rows[{}].parameters.{}".format(op_id, str(key)),
                        {"op_id": op_id, "parameter": str(key)},
                    )
                )

            static_requirements = _as_map(op_row.get("static_requirements"))
            entitlements = set(_sorted_unique_strings(static_requirements.get("entitlements")))
            capabilities = set(_sorted_unique_strings(static_requirements.get("capabilities")))
            required_entitlements |= entitlements
            required_capabilities |= capabilities

            missing_entitlements = sorted(entitlements - requester_entitlements)
            if missing_entitlements:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_INVALID,
                        "op static_requirements includes entitlements missing from requester authority",
                        "$.extensions.op_rows[{}].static_requirements.entitlements".format(op_id),
                        {"op_id": op_id, "missing_entitlements": ",".join(missing_entitlements)},
                    )
                )
            forbidden_req_entitlements = sorted(entitlements.intersection(forbidden_entitlements))
            if forbidden_req_entitlements:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_INVALID,
                        "op static_requirements includes entitlements forbidden by policy",
                        "$.extensions.op_rows[{}].static_requirements.entitlements".format(op_id),
                        {"op_id": op_id, "forbidden_entitlements": ",".join(forbidden_req_entitlements)},
                    )
                )
            forbidden_req_capabilities = sorted(capabilities.intersection(forbidden_capabilities))
            if forbidden_req_capabilities:
                violations.append(
                    _violation(
                        REFUSAL_CTRL_IR_INVALID,
                        "op static_requirements includes capabilities forbidden by policy",
                        "$.extensions.op_rows[{}].static_requirements.capabilities".format(op_id),
                        {"op_id": op_id, "forbidden_capabilities": ",".join(forbidden_req_capabilities)},
                    )
                )
            if known_capabilities:
                unknown_capabilities = sorted(capabilities - known_capabilities)
                if unknown_capabilities:
                    violations.append(
                        _violation(
                            REFUSAL_CTRL_IR_INVALID,
                            "op static_requirements includes unknown capabilities",
                            "$.extensions.op_rows[{}].static_requirements.capabilities".format(op_id),
                            {"op_id": op_id, "unknown_capabilities": ",".join(unknown_capabilities)},
                        )
                    )

            cost_estimate = int(max(0, _to_int(op_row.get("cost_estimate", 0), 0)))
            max_cost_estimate += cost_estimate

    graph = _graph_edges(block_rows_by_id)
    cycle_nodes = _cycle_nodes(graph)
    if cycle_nodes and not _bounded_cycle_nodes(ir, cycle_nodes):
        violations.append(
            _violation(
                REFUSAL_CTRL_IR_INVALID,
                "Control IR block graph contains an unbounded cycle",
                "$.blocks",
                {"cycle_nodes": ",".join(cycle_nodes)},
            )
        )

    report = {
        "schema_version": "1.0.0",
        "ir_id": ir_id or "control.ir.unknown",
        "valid": len(violations) == 0,
        "violations": _sorted_violations(violations),
        "required_entitlements": sorted(required_entitlements),
        "required_capabilities": sorted(required_capabilities),
        "max_cost_estimate": int(max(0, max_cost_estimate)),
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    return report


__all__ = [
    "ALLOWED_CONTROL_IR_OP_TYPES",
    "REFUSAL_CTRL_IR_COST_EXCEEDED",
    "REFUSAL_CTRL_IR_FORBIDDEN_OP",
    "REFUSAL_CTRL_IR_INVALID",
    "verify_control_ir",
]
