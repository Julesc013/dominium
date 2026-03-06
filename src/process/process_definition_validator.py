"""PROC-1 deterministic ProcessDefinition graph validation helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_PROCESS_INVALID_DEFINITION = "refusal.process.invalid_definition"

_STEP_KINDS = {"action", "transform", "measure", "verify", "wait"}
_INFO_OUTPUT_REF_TYPES = {"artifact", "observation", "report", "record"}


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


def _normalized_step_kind(value: object) -> str:
    token = str(value or "").strip().lower()
    if token.endswith("_step"):
        token = token[: -len("_step")]
    return token


def _normalize_io_refs(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: (str(item.get("name", "")), str(item.get("ref_id", "")))):
        normalized.append(
            {
                "name": str(row.get("name", "")).strip(),
                "ref_id": str(row.get("ref_id", "")).strip(),
                "ref_type": str(row.get("ref_type", "")).strip(),
                "io_tags": _sorted_tokens(row.get("io_tags")),
                "extensions": _as_map(row.get("extensions")),
            }
        )
    return normalized


def build_process_step_row(
    *,
    step_id: str,
    step_kind: str,
    action_template_id: str | None = None,
    domain_process_id: str | None = None,
    temporal_domain_id: str | None = None,
    inputs: object = None,
    outputs: object = None,
    cost_units: int = 0,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    token = str(step_id or "").strip()
    kind = _normalized_step_kind(step_kind)
    if (not token) or (kind not in _STEP_KINDS):
        return {}
    cost = int(max(0, _as_int(cost_units, 0)))
    payload = {
        "schema_version": "1.0.0",
        "step_id": token,
        "step_kind": kind,
        "action_template_id": str(action_template_id or "").strip() or None,
        "domain_process_id": str(domain_process_id or "").strip() or None,
        "temporal_domain_id": str(temporal_domain_id or "").strip() or None,
        "inputs": _normalize_io_refs(inputs),
        "outputs": _normalize_io_refs(outputs),
        "cost_units": cost,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_process_step_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("step_id", ""))):
        normalized = build_process_step_row(
            step_id=str(row.get("step_id", "")).strip(),
            step_kind=str(row.get("step_kind", "")).strip(),
            action_template_id=(None if row.get("action_template_id") is None else str(row.get("action_template_id", "")).strip() or None),
            domain_process_id=(None if row.get("domain_process_id") is None else str(row.get("domain_process_id", "")).strip() or None),
            temporal_domain_id=(None if row.get("temporal_domain_id") is None else str(row.get("temporal_domain_id", "")).strip() or None),
            inputs=row.get("inputs"),
            outputs=row.get("outputs"),
            cost_units=_as_int(row.get("cost_units", 0), 0),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions"),),
        )
        step_id = str(normalized.get("step_id", "")).strip()
        if step_id:
            out[step_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def process_step_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("step_id", "")).strip(), dict(row)) for row in normalize_process_step_rows(rows) if str(row.get("step_id", "")).strip())


def _normalize_step_graph_payload(step_graph: object) -> dict:
    graph = _as_map(step_graph)
    if not graph and isinstance(step_graph, list):
        graph = {"steps": step_graph, "edges": []}
    steps = normalize_process_step_rows(graph.get("steps"))
    if not steps and isinstance(step_graph, list):
        steps = normalize_process_step_rows(step_graph)
    edges_raw = _as_list(graph.get("edges"))
    normalized_edges: List[dict] = []
    for edge in sorted((dict(item) for item in edges_raw if isinstance(item, Mapping)), key=lambda item: (
        str(item.get("from_step_id", item.get("from", item.get("source_step_id", "")))),
        str(item.get("to_step_id", item.get("to", item.get("target_step_id", "")))),
    )):
        src = str(edge.get("from_step_id", edge.get("from", edge.get("source_step_id", ""))) or "").strip()
        dst = str(edge.get("to_step_id", edge.get("to", edge.get("target_step_id", ""))) or "").strip()
        if (not src) or (not dst):
            continue
        normalized_edges.append(
            {
                "from_step_id": src,
                "to_step_id": dst,
                "extensions": _as_map(edge.get("extensions")),
            }
        )
    return {"steps": steps, "edges": normalized_edges}


def build_process_definition_row(
    *,
    process_id: str,
    version: str,
    description: str,
    step_graph: object,
    input_signature: object,
    output_signature: object,
    required_tools: object,
    required_environment: object,
    tier_contract_id: str,
    coupling_budget_id: str | None = None,
    qc_policy_id: str | None = None,
    stabilization_policy_id: str | None = None,
    process_lifecycle_policy_id: str | None = None,
    process_cert_type_id: str | None = None,
    yield_model_id: str | None = None,
    defect_model_id: str | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = str(process_id or "").strip()
    version_token = str(version or "").strip() or "1.0.0"
    tier_token = str(tier_contract_id or "").strip()
    graph = _normalize_step_graph_payload(step_graph)
    if (not process_token) or (not tier_token) or (not list(graph.get("steps") or [])):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "process_id": process_token,
        "version": version_token,
        "description": str(description or "").strip(),
        "step_graph": graph,
        "input_signature": _normalize_io_refs(input_signature),
        "output_signature": _normalize_io_refs(output_signature),
        "required_tools": _sorted_tokens(required_tools),
        "required_environment": _sorted_tokens(required_environment),
        "tier_contract_id": tier_token,
        "coupling_budget_id": str(coupling_budget_id or "").strip() or None,
        "qc_policy_id": str(qc_policy_id or "").strip() or None,
        "stabilization_policy_id": str(stabilization_policy_id or "").strip() or None,
        "process_lifecycle_policy_id": str(process_lifecycle_policy_id or "").strip() or None,
        "process_cert_type_id": str(process_cert_type_id or "").strip() or None,
        "yield_model_id": str(yield_model_id or "").strip() or None,
        "defect_model_id": str(defect_model_id or "").strip() or None,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_process_definition_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: (str(item.get("process_id", "")), str(item.get("version", "")))):
        normalized = build_process_definition_row(
            process_id=str(row.get("process_id", "")).strip(),
            version=str(row.get("version", "")).strip() or "1.0.0",
            description=str(row.get("description", "")).strip(),
            step_graph=row.get("step_graph"),
            input_signature=row.get("input_signature"),
            output_signature=row.get("output_signature"),
            required_tools=row.get("required_tools"),
            required_environment=row.get("required_environment"),
            tier_contract_id=str(row.get("tier_contract_id", "")).strip(),
            coupling_budget_id=(None if row.get("coupling_budget_id") is None else str(row.get("coupling_budget_id", "")).strip() or None),
            qc_policy_id=(None if row.get("qc_policy_id") is None else str(row.get("qc_policy_id", "")).strip() or None),
            stabilization_policy_id=(None if row.get("stabilization_policy_id") is None else str(row.get("stabilization_policy_id", "")).strip() or None),
            process_lifecycle_policy_id=(None if row.get("process_lifecycle_policy_id") is None else str(row.get("process_lifecycle_policy_id", "")).strip() or None),
            process_cert_type_id=(None if row.get("process_cert_type_id") is None else str(row.get("process_cert_type_id", "")).strip() or None),
            yield_model_id=(None if row.get("yield_model_id") is None else str(row.get("yield_model_id", "")).strip() or None),
            defect_model_id=(None if row.get("defect_model_id") is None else str(row.get("defect_model_id", "")).strip() or None),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        process_id = str(normalized.get("process_id", "")).strip()
        version = str(normalized.get("version", "")).strip()
        if process_id and version:
            out["{}@{}".format(process_id, version)] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def process_definition_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_process_definition_rows(rows):
        process_id = str(row.get("process_id", "")).strip()
        version = str(row.get("version", "")).strip()
        if process_id and version:
            out["{}@{}".format(process_id, version)] = dict(row)
    return out


def _action_template_ids(payload: Mapping[str, object] | None) -> set[str]:
    body = _as_map(payload)
    record = _as_map(body.get("record"))
    rows = _as_list(record.get("templates"))
    out = set()
    for row in rows:
        item = _as_map(row)
        token = str(item.get("action_template_id", "")).strip()
        if token:
            out.add(token)
    return out


def _temporal_domain_ids(payload: Mapping[str, object] | None) -> set[str]:
    body = _as_map(payload)
    record = _as_map(body.get("record"))
    rows = _as_list(record.get("temporal_domains"))
    out = set()
    for row in rows:
        item = _as_map(row)
        token = str(item.get("temporal_domain_id", "")).strip()
        if token:
            out.add(token)
    return out


def _graph_adjacency(step_ids: Sequence[str], edges: Sequence[Mapping[str, object]]) -> Tuple[Dict[str, List[str]], Dict[str, int], List[str]]:
    adjacency = dict((step_id, []) for step_id in sorted(step_ids))
    indegree = dict((step_id, 0) for step_id in sorted(step_ids))
    violations: List[str] = []
    step_id_set = set(step_ids)
    for edge in list(edges or []):
        row = _as_map(edge)
        src = str(row.get("from_step_id", "")).strip()
        dst = str(row.get("to_step_id", "")).strip()
        if (src not in step_id_set) or (dst not in step_id_set):
            violations.append("edge references unknown step: {}->{}".format(src or "<missing>", dst or "<missing>"))
            continue
        adjacency[src].append(dst)
        indegree[dst] = int(max(0, _as_int(indegree.get(dst, 0), 0))) + 1
    for step_id in sorted(adjacency.keys()):
        adjacency[step_id] = sorted(set(adjacency[step_id]))
    return adjacency, indegree, violations


def stable_toposort(*, step_rows: Sequence[Mapping[str, object]], edge_rows: Sequence[Mapping[str, object]]) -> dict:
    step_ids = [str(_as_map(row).get("step_id", "")).strip() for row in list(step_rows or [])]
    step_ids = [step_id for step_id in sorted(set(step_ids)) if step_id]
    if not step_ids:
        return {"result": "refused", "reason_code": REFUSAL_PROCESS_INVALID_DEFINITION, "ordered_step_ids": [], "violations": ["step_graph missing steps"]}
    adjacency, indegree, violations = _graph_adjacency(step_ids, edge_rows)
    queue = sorted([step_id for step_id in step_ids if _as_int(indegree.get(step_id, 0), 0) == 0])
    ordered: List[str] = []
    while queue:
        step_id = queue.pop(0)
        ordered.append(step_id)
        for child in sorted(adjacency.get(step_id, [])):
            indegree[child] = int(max(0, _as_int(indegree.get(child, 0), 0) - 1))
            if indegree[child] == 0:
                queue.append(child)
        queue = sorted(set(queue))
    if len(ordered) != len(step_ids):
        unresolved = [step_id for step_id in step_ids if step_id not in set(ordered)]
        violations.append("step_graph contains cycle or unresolved dependency: {}".format(",".join(sorted(unresolved))))
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_INVALID_DEFINITION,
            "ordered_step_ids": list(ordered),
            "violations": violations,
        }
    return {
        "result": "complete",
        "reason_code": "",
        "ordered_step_ids": list(ordered),
        "violations": list(violations),
        "deterministic_fingerprint": canonical_sha256({"ordered_step_ids": ordered, "edge_count": len(list(edge_rows or []))}),
    }


def _step_info_output_ok(step_row: Mapping[str, object]) -> bool:
    kind = _normalized_step_kind(_as_map(step_row).get("step_kind"))
    outputs = _as_list(_as_map(step_row).get("outputs"))
    if kind not in {"measure", "verify"}:
        return True
    if not outputs:
        return False
    for output in outputs:
        row = _as_map(output)
        ref_type = str(row.get("ref_type", "")).strip().lower()
        if ref_type in _INFO_OUTPUT_REF_TYPES:
            continue
        ref_id = str(row.get("ref_id", "")).strip().lower()
        if ref_id.startswith("artifact."):
            continue
        return False
    return True


def validate_process_definition(
    *,
    process_definition_row: Mapping[str, object],
    action_template_registry_payload: Mapping[str, object] | None,
    temporal_domain_registry_payload: Mapping[str, object] | None,
    qc_policy_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    normalized = build_process_definition_row(
        process_id=str(_as_map(process_definition_row).get("process_id", "")).strip(),
        version=str(_as_map(process_definition_row).get("version", "")).strip() or "1.0.0",
        description=str(_as_map(process_definition_row).get("description", "")).strip(),
        step_graph=_as_map(process_definition_row).get("step_graph"),
        input_signature=_as_map(process_definition_row).get("input_signature"),
        output_signature=_as_map(process_definition_row).get("output_signature"),
        required_tools=_as_map(process_definition_row).get("required_tools"),
        required_environment=_as_map(process_definition_row).get("required_environment"),
        tier_contract_id=str(_as_map(process_definition_row).get("tier_contract_id", "")).strip(),
        coupling_budget_id=(None if _as_map(process_definition_row).get("coupling_budget_id") is None else str(_as_map(process_definition_row).get("coupling_budget_id", "")).strip() or None),
        qc_policy_id=(None if _as_map(process_definition_row).get("qc_policy_id") is None else str(_as_map(process_definition_row).get("qc_policy_id", "")).strip() or None),
        stabilization_policy_id=(None if _as_map(process_definition_row).get("stabilization_policy_id") is None else str(_as_map(process_definition_row).get("stabilization_policy_id", "")).strip() or None),
        process_lifecycle_policy_id=(None if _as_map(process_definition_row).get("process_lifecycle_policy_id") is None else str(_as_map(process_definition_row).get("process_lifecycle_policy_id", "")).strip() or None),
        process_cert_type_id=(None if _as_map(process_definition_row).get("process_cert_type_id") is None else str(_as_map(process_definition_row).get("process_cert_type_id", "")).strip() or None),
        yield_model_id=(None if _as_map(process_definition_row).get("yield_model_id") is None else str(_as_map(process_definition_row).get("yield_model_id", "")).strip() or None),
        defect_model_id=(None if _as_map(process_definition_row).get("defect_model_id") is None else str(_as_map(process_definition_row).get("defect_model_id", "")).strip() or None),
        deterministic_fingerprint=str(_as_map(process_definition_row).get("deterministic_fingerprint", "")).strip(),
        extensions=_as_map(_as_map(process_definition_row).get("extensions")),
    )
    if not normalized:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_INVALID_DEFINITION,
            "violations": ["invalid or incomplete process_definition row"],
            "ordered_step_ids": [],
        }

    graph = _as_map(normalized.get("step_graph"))
    step_rows = list(graph.get("steps") or [])
    edge_rows = list(graph.get("edges") or [])
    topo = stable_toposort(step_rows=step_rows, edge_rows=edge_rows)
    violations = list(topo.get("violations") or [])

    action_template_ids = _action_template_ids(action_template_registry_payload)
    temporal_domain_ids = _temporal_domain_ids(temporal_domain_registry_payload)
    qc_policy_ids = set()
    if isinstance(qc_policy_registry_payload, Mapping):
        qc_record = _as_map(_as_map(qc_policy_registry_payload).get("record"))
        for row in _as_list(qc_record.get("qc_policies")):
            entry = _as_map(row)
            token = str(entry.get("qc_policy_id", "")).strip()
            if token:
                qc_policy_ids.add(token)

    for step_row in step_rows:
        row = _as_map(step_row)
        step_id = str(row.get("step_id", "")).strip() or "<missing>"
        kind = _normalized_step_kind(row.get("step_kind"))
        if kind not in _STEP_KINDS:
            violations.append("step {} has unsupported step_kind".format(step_id))
            continue
        if _as_int(row.get("cost_units", -1), -1) < 0:
            violations.append("step {} has invalid cost_units".format(step_id))
        if kind == "action":
            action_template_id = str(row.get("action_template_id", "")).strip()
            if (not action_template_id) or (action_template_id not in action_template_ids):
                violations.append("action step {} missing valid action_template_id".format(step_id))
        if kind == "wait":
            temporal_domain_id = str(row.get("temporal_domain_id", "")).strip()
            if (not temporal_domain_id) or (temporal_domain_id not in temporal_domain_ids):
                violations.append("wait step {} missing valid temporal_domain_id".format(step_id))
        if not _step_info_output_ok(row):
            violations.append("step {} does not map outputs to META-INFO artifact refs".format(step_id))

    qc_policy_id = str(normalized.get("qc_policy_id", "")).strip()
    if qc_policy_id and qc_policy_ids and qc_policy_id not in qc_policy_ids:
        violations.append("process qc_policy_id is not registered: {}".format(qc_policy_id))

    if str(topo.get("result", "")).strip() != "complete":
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_INVALID_DEFINITION,
            "violations": sorted(set(violations)),
            "ordered_step_ids": list(topo.get("ordered_step_ids") or []),
            "deterministic_fingerprint": canonical_sha256({"process_id": normalized.get("process_id"), "violations": sorted(set(violations))}),
        }

    if violations:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_INVALID_DEFINITION,
            "violations": sorted(set(violations)),
            "ordered_step_ids": list(topo.get("ordered_step_ids") or []),
            "deterministic_fingerprint": canonical_sha256({"process_id": normalized.get("process_id"), "violations": sorted(set(violations))}),
        }

    return {
        "result": "complete",
        "reason_code": "",
        "violations": [],
        "ordered_step_ids": list(topo.get("ordered_step_ids") or []),
        "deterministic_fingerprint": canonical_sha256(
            {
                "process_id": str(normalized.get("process_id", "")).strip(),
                "version": str(normalized.get("version", "")).strip(),
                "ordered_step_ids": list(topo.get("ordered_step_ids") or []),
                "step_count": len(step_rows),
                "edge_count": len(edge_rows),
            }
        ),
    }


__all__ = [
    "REFUSAL_PROCESS_INVALID_DEFINITION",
    "build_process_step_row",
    "normalize_process_step_rows",
    "process_step_rows_by_id",
    "build_process_definition_row",
    "normalize_process_definition_rows",
    "process_definition_rows_by_id",
    "stable_toposort",
    "validate_process_definition",
]
