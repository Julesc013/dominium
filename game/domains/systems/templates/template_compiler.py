"""SYS-4 deterministic system template compiler."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence, Set

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_TEMPLATE_INVALID = "refusal.template.invalid"
REFUSAL_TEMPLATE_NOT_FOUND = "refusal.template.not_found"
REFUSAL_TEMPLATE_MISSING_REFERENCE = "refusal.template.missing_reference"
REFUSAL_TEMPLATE_MISSING_DOMAIN = "refusal.template.missing_domain"
REFUSAL_TEMPLATE_CYCLE = "refusal.template.cycle"
REFUSAL_TEMPLATE_FORBIDDEN_MODE = "refusal.template.forbidden_mode"
REFUSAL_TEMPLATE_SPEC_NONCOMPLIANT = "refusal.template.spec_noncompliant"

_INSTANTIATION_MODES = {"micro", "macro", "hybrid"}


class SystemTemplateCompileError(RuntimeError):
    """Raised when template compilation inputs are invalid."""

    def __init__(self, message: str, *, reason_code: str, details: Mapping[str, object] | None = None) -> None:
        super().__init__(str(message))
        self.reason_code = str(reason_code or REFUSAL_TEMPLATE_INVALID)
        self.details = dict(details or {})


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


def build_system_template_row(
    *,
    template_id: str,
    version: str,
    description: str,
    required_domains: object,
    assembly_graph_spec_ref: str,
    interface_signature_template_id: str,
    boundary_invariant_template_ids: object,
    macro_model_set_id: str,
    tier_contract_id: str,
    safety_pattern_instance_templates: object,
    spec_bindings: object,
    nested_template_refs: object,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    template_token = str(template_id or "").strip()
    if not template_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "template_id": template_token,
        "version": str(version or "").strip() or "1.0.0",
        "description": str(description or "").strip(),
        "required_domains": _sorted_tokens(required_domains),
        "assembly_graph_spec_ref": str(assembly_graph_spec_ref or "").strip(),
        "interface_signature_template_id": str(interface_signature_template_id or "").strip(),
        "boundary_invariant_template_ids": _sorted_tokens(boundary_invariant_template_ids),
        "macro_model_set_id": str(macro_model_set_id or "").strip(),
        "tier_contract_id": str(tier_contract_id or "").strip(),
        "safety_pattern_instance_templates": [
            dict(item)
            for item in sorted(
                (dict(row) for row in _as_list(safety_pattern_instance_templates) if isinstance(row, Mapping)),
                key=lambda row: (
                    str(row.get("pattern_id", "")),
                    str(row.get("instance_id", "")),
                ),
            )
        ],
        "spec_bindings": [
            dict(item)
            for item in sorted(
                (dict(row) for row in _as_list(spec_bindings) if isinstance(row, Mapping)),
                key=lambda row: (
                    str(row.get("spec_type_id", "")),
                    str(row.get("binding_id", "")),
                ),
            )
        ],
        "nested_template_refs": _sorted_tokens(nested_template_refs),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_system_template_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("template_id", ""))):
        normalized = build_system_template_row(
            template_id=str(row.get("template_id", "")).strip(),
            version=str(row.get("version", "1.0.0")).strip() or "1.0.0",
            description=str(row.get("description", "")).strip(),
            required_domains=row.get("required_domains"),
            assembly_graph_spec_ref=str(row.get("assembly_graph_spec_ref", "")).strip(),
            interface_signature_template_id=str(row.get("interface_signature_template_id", "")).strip(),
            boundary_invariant_template_ids=row.get("boundary_invariant_template_ids"),
            macro_model_set_id=str(row.get("macro_model_set_id", "")).strip(),
            tier_contract_id=str(row.get("tier_contract_id", "")).strip(),
            safety_pattern_instance_templates=row.get("safety_pattern_instance_templates"),
            spec_bindings=row.get("spec_bindings"),
            nested_template_refs=row.get("nested_template_refs"),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        template_id = str(normalized.get("template_id", "")).strip()
        if template_id:
            out[template_id] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def system_template_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_system_template_rows(rows):
        template_id = str(row.get("template_id", "")).strip()
        if template_id:
            out[template_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _template_rows_from_registry(payload: Mapping[str, object] | None) -> List[dict]:
    return _rows_from_registry_payload(payload, ("system_templates",))


def _interface_template_ids(payload: Mapping[str, object] | None) -> Set[str]:
    rows = _rows_from_registry_payload(payload, ("interface_signature_templates",))
    return set(
        _sorted_tokens(str(row.get("interface_signature_template_id", "")).strip() for row in rows)
    )


def _boundary_template_ids(payload: Mapping[str, object] | None) -> Set[str]:
    rows = _rows_from_registry_payload(payload, ("boundary_invariant_templates",))
    return set(
        _sorted_tokens(str(row.get("boundary_invariant_template_id", "")).strip() for row in rows)
    )


def _macro_model_set_ids(payload: Mapping[str, object] | None) -> Set[str]:
    rows = _rows_from_registry_payload(payload, ("macro_model_sets",))
    return set(
        _sorted_tokens(str(row.get("macro_model_set_id", "")).strip() for row in rows)
    )


def _tier_contract_ids(payload: Mapping[str, object] | None) -> Set[str]:
    rows = _rows_from_registry_payload(payload, ("tier_contracts",))
    return set(_sorted_tokens(str(row.get("contract_id", "")).strip() for row in rows))


def _domain_ids(payload: Mapping[str, object] | None) -> Set[str]:
    rows = _rows_from_registry_payload(payload, ("records", "domains"))
    return set(_sorted_tokens(str(row.get("domain_id", "")).strip() for row in rows))


def _collect_reachable_templates(*, template_id: str, by_id: Mapping[str, dict]) -> Dict[str, dict]:
    root_token = str(template_id or "").strip()
    if root_token not in by_id:
        raise SystemTemplateCompileError(
            "template_id '{}' is not registered".format(root_token),
            reason_code=REFUSAL_TEMPLATE_NOT_FOUND,
            details={"template_id": root_token},
        )
    out: Dict[str, dict] = {}
    stack = [root_token]
    while stack:
        token = str(stack.pop()).strip()
        if (not token) or token in out:
            continue
        row = dict(by_id.get(token) or {})
        if not row:
            raise SystemTemplateCompileError(
                "nested template '{}' is not registered".format(token),
                reason_code=REFUSAL_TEMPLATE_MISSING_REFERENCE,
                details={"template_id": root_token, "missing_template_id": token},
            )
        out[token] = row
        nested = _sorted_tokens(row.get("nested_template_refs") or [])
        for nested_id in reversed(nested):
            if nested_id not in by_id:
                raise SystemTemplateCompileError(
                    "nested template '{}' is not registered".format(nested_id),
                    reason_code=REFUSAL_TEMPLATE_MISSING_REFERENCE,
                    details={"template_id": root_token, "missing_template_id": nested_id},
                )
            if nested_id not in out:
                stack.append(nested_id)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _topological_template_order(*, root_template_id: str, template_rows_by_id: Mapping[str, dict]) -> List[str]:
    rows_by_id = dict((str(key).strip(), dict(value)) for key, value in template_rows_by_id.items() if str(key).strip())
    reachable = _collect_reachable_templates(template_id=root_template_id, by_id=rows_by_id)
    deps_by_id: Dict[str, Set[str]] = {}
    reverse_edges: Dict[str, Set[str]] = {}
    indegree: Dict[str, int] = {}
    for template_id in sorted(reachable.keys()):
        row = dict(reachable.get(template_id) or {})
        deps = set(_sorted_tokens(row.get("nested_template_refs") or []))
        deps = set(token for token in deps if token in reachable)
        deps_by_id[template_id] = set(sorted(deps))
        indegree[template_id] = int(len(deps))
        reverse_edges.setdefault(template_id, set())
        for dep_id in sorted(deps):
            reverse_edges.setdefault(dep_id, set()).add(template_id)

    frontier = sorted(template_id for template_id, degree in indegree.items() if int(degree) == 0)
    ordered: List[str] = []
    while frontier:
        current = str(frontier.pop(0)).strip()
        if not current:
            continue
        ordered.append(current)
        for dependent in sorted(reverse_edges.get(current, set())):
            indegree[dependent] = int(max(0, _as_int(indegree.get(dependent, 0), 0) - 1))
            if int(indegree[dependent]) == 0:
                frontier.append(dependent)
        frontier = sorted(set(frontier))

    if len(ordered) != len(reachable):
        unresolved = sorted(
            template_id for template_id in reachable.keys() if template_id not in set(ordered)
        )
        raise SystemTemplateCompileError(
            "template dependency cycle detected",
            reason_code=REFUSAL_TEMPLATE_CYCLE,
            details={
                "root_template_id": str(root_template_id or "").strip(),
                "unresolved_template_ids": unresolved,
            },
        )
    return list(ordered)


def _validation_row(*, check_id: str, status: str, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "check_id": str(check_id).strip(),
        "status": str(status).strip(),
        "message": str(message).strip(),
        "details": _as_map(details),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _aggregate_template_ports(template_rows: Sequence[Mapping[str, object]]) -> List[str]:
    ports: List[str] = []
    for row in list(template_rows or []):
        ext = _as_map(_as_map(row).get("extensions"))
        interface_summary = _as_map(ext.get("interface_summary"))
        for port in _sorted_tokens(interface_summary.get("ports") or []):
            ports.append(port)
    return _sorted_tokens(ports)


def _aggregate_spec_bindings(template_rows: Sequence[Mapping[str, object]]) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in list(template_rows or []):
        for binding in [dict(item) for item in _as_list(_as_map(row).get("spec_bindings")) if isinstance(item, Mapping)]:
            spec_type_id = str(binding.get("spec_type_id", "")).strip()
            binding_id = str(binding.get("binding_id", "")).strip() or "binding.{}".format(
                canonical_sha256(binding)[:12]
            )
            if not spec_type_id:
                continue
            key = "{}::{}".format(spec_type_id, binding_id)
            out[key] = {
                "spec_type_id": spec_type_id,
                "binding_id": binding_id,
                "target": str(binding.get("target", "")).strip() or "system",
                "extensions": _as_map(binding.get("extensions")),
            }
    return [dict(out[key]) for key in sorted(out.keys())]


def compile_system_template(
    *,
    template_id: str,
    instantiation_mode: str,
    system_template_registry_payload: Mapping[str, object] | None,
    interface_signature_template_registry_payload: Mapping[str, object] | None,
    boundary_invariant_template_registry_payload: Mapping[str, object] | None,
    macro_model_set_registry_payload: Mapping[str, object] | None,
    tier_contract_registry_payload: Mapping[str, object] | None,
    domain_registry_payload: Mapping[str, object] | None,
) -> dict:
    template_token = str(template_id or "").strip()
    mode_token = str(instantiation_mode or "").strip().lower() or "micro"
    if not template_token:
        raise SystemTemplateCompileError(
            "template_id is required",
            reason_code=REFUSAL_TEMPLATE_INVALID,
            details={},
        )
    if mode_token not in _INSTANTIATION_MODES:
        raise SystemTemplateCompileError(
            "instantiation_mode '{}' is invalid".format(mode_token),
            reason_code=REFUSAL_TEMPLATE_FORBIDDEN_MODE,
            details={"instantiation_mode": mode_token},
        )

    template_rows = normalize_system_template_rows(
        _template_rows_from_registry(system_template_registry_payload)
    )
    templates_by_id = system_template_rows_by_id(template_rows)
    if template_token not in templates_by_id:
        raise SystemTemplateCompileError(
            "template_id '{}' is not registered".format(template_token),
            reason_code=REFUSAL_TEMPLATE_NOT_FOUND,
            details={"template_id": template_token},
        )

    ordered_ids = _topological_template_order(
        root_template_id=template_token,
        template_rows_by_id=templates_by_id,
    )
    ordered_rows = [dict(templates_by_id[item]) for item in ordered_ids]
    root_row = dict(templates_by_id.get(template_token) or {})

    interface_template_ids = _interface_template_ids(interface_signature_template_registry_payload)
    boundary_template_ids = _boundary_template_ids(boundary_invariant_template_registry_payload)
    macro_model_set_ids = _macro_model_set_ids(macro_model_set_registry_payload)
    tier_contract_ids = _tier_contract_ids(tier_contract_registry_payload)
    domain_ids = _domain_ids(domain_registry_payload)

    validation_rows: List[dict] = []
    missing_domains = [
        token
        for token in _sorted_tokens(root_row.get("required_domains") or [])
        if token not in domain_ids
    ]
    validation_rows.append(
        _validation_row(
            check_id="template.required_domains.registered",
            status="pass" if not missing_domains else "fail",
            message="required domain ids registered",
            details={"missing_domain_ids": missing_domains},
        )
    )
    interface_template_id = str(root_row.get("interface_signature_template_id", "")).strip()
    validation_rows.append(
        _validation_row(
            check_id="template.interface_signature_template.registered",
            status="pass" if interface_template_id in interface_template_ids else "fail",
            message="interface signature template reference is registered",
            details={"interface_signature_template_id": interface_template_id},
        )
    )
    for boundary_template_id in _sorted_tokens(root_row.get("boundary_invariant_template_ids") or []):
        validation_rows.append(
            _validation_row(
                check_id="template.boundary_invariant_template.registered.{}".format(boundary_template_id),
                status="pass" if boundary_template_id in boundary_template_ids else "fail",
                message="boundary invariant template reference is registered",
                details={"boundary_invariant_template_id": boundary_template_id},
            )
        )
    macro_model_set_id = str(root_row.get("macro_model_set_id", "")).strip()
    validation_rows.append(
        _validation_row(
            check_id="template.macro_model_set.registered",
            status="pass" if macro_model_set_id in macro_model_set_ids else "fail",
            message="macro model set reference is registered",
            details={"macro_model_set_id": macro_model_set_id},
        )
    )
    tier_contract_id = str(root_row.get("tier_contract_id", "")).strip()
    validation_rows.append(
        _validation_row(
            check_id="template.tier_contract.registered",
            status="pass" if tier_contract_id in tier_contract_ids else "fail",
            message="tier contract reference is registered",
            details={"tier_contract_id": tier_contract_id},
        )
    )

    failed_rows = [
        dict(row)
        for row in list(validation_rows or [])
        if str(row.get("status", "")).strip() != "pass"
    ]
    if missing_domains:
        raise SystemTemplateCompileError(
            "template required domain is unavailable",
            reason_code=REFUSAL_TEMPLATE_MISSING_DOMAIN,
            details={
                "template_id": template_token,
                "missing_domain_ids": list(missing_domains),
                "failed_checks": failed_rows,
            },
        )
    if failed_rows:
        raise SystemTemplateCompileError(
            "template validation failed",
            reason_code=REFUSAL_TEMPLATE_INVALID,
            details={
                "template_id": template_token,
                "failed_checks": failed_rows,
            },
        )

    assembly_graph_spec_refs: List[str] = []
    assembly_nodes: List[dict] = []
    for index, row in enumerate(ordered_rows):
        spec_ref = str(row.get("assembly_graph_spec_ref", "")).strip()
        if spec_ref:
            assembly_graph_spec_refs.append(spec_ref)
        ext = _as_map(row.get("extensions"))
        node_ids = _sorted_tokens(_as_map(ext.get("assembly_graph_spec")).get("node_ids") or [])
        if not node_ids:
            node_ids = [
                "assembly.template.{}.{}".format(
                    str(row.get("template_id", "")).strip().replace(".", "_"),
                    str(index + 1).zfill(2),
                )
            ]
        for node_id in node_ids:
            assembly_nodes.append(
                {
                    "node_id": str(node_id).strip(),
                    "template_id": str(row.get("template_id", "")).strip(),
                    "spec_ref": spec_ref or None,
                }
            )
    assembly_nodes = sorted(
        (
            dict(row)
            for row in list(assembly_nodes or [])
            if isinstance(row, Mapping) and str(row.get("node_id", "")).strip()
        ),
        key=lambda row: (str(row.get("template_id", "")), str(row.get("node_id", ""))),
    )

    aggregated_boundary_templates: List[str] = []
    aggregated_safety_patterns: List[dict] = []
    for row in ordered_rows:
        aggregated_boundary_templates.extend(_sorted_tokens(row.get("boundary_invariant_template_ids") or []))
        aggregated_safety_patterns.extend(
            [
                dict(item)
                for item in _as_list(row.get("safety_pattern_instance_templates"))
                if isinstance(item, Mapping)
            ]
        )
    aggregated_safety_patterns = sorted(
        (
            dict(row)
            for row in list(aggregated_safety_patterns or [])
            if isinstance(row, Mapping)
        ),
        key=lambda row: (
            str(row.get("pattern_id", "")),
            str(row.get("instance_id", "")),
        ),
    )

    compiled_assembly_graph_spec = {
        "root_template_id": template_token,
        "resolved_template_ids": list(ordered_ids),
        "assembly_graph_spec_refs": _sorted_tokens(assembly_graph_spec_refs),
        "assembly_nodes": [dict(row) for row in assembly_nodes],
        "deterministic_fingerprint": "",
    }
    compiled_assembly_graph_spec["deterministic_fingerprint"] = canonical_sha256(
        dict(compiled_assembly_graph_spec, deterministic_fingerprint="")
    )

    compiled_macro_capsule = {
        "template_id": template_token,
        "resolved_template_ids": list(ordered_ids),
        "interface_signature_template_id": interface_template_id,
        "boundary_invariant_template_ids": _sorted_tokens(aggregated_boundary_templates),
        "macro_model_set_id": macro_model_set_id,
        "tier_contract_id": tier_contract_id,
        "safety_pattern_instance_templates": [dict(row) for row in aggregated_safety_patterns],
        "spec_bindings": _aggregate_spec_bindings(ordered_rows),
        "expected_ports": _aggregate_template_ports(ordered_rows),
        "deterministic_fingerprint": "",
    }
    compiled_macro_capsule["deterministic_fingerprint"] = canonical_sha256(
        dict(compiled_macro_capsule, deterministic_fingerprint="")
    )

    root_ext = _as_map(root_row.get("extensions"))
    expanded_template_ids = _sorted_tokens(root_ext.get("hybrid_default_expanded_template_ids") or [])
    if not expanded_template_ids:
        expanded_template_ids = [token for token in ordered_ids if token != template_token][:1]
    hybrid_decomposition_plan = {
        "template_id": template_token,
        "resolved_template_ids": list(ordered_ids),
        "capsule_template_id": template_token,
        "expanded_template_ids": _sorted_tokens(expanded_template_ids),
        "deterministic_fingerprint": "",
    }
    hybrid_decomposition_plan["deterministic_fingerprint"] = canonical_sha256(
        dict(hybrid_decomposition_plan, deterministic_fingerprint="")
    )

    result = {
        "result": "complete",
        "template_id": template_token,
        "instantiation_mode": mode_token,
        "resolved_template_order": list(ordered_ids),
        "validation_rows": [dict(row) for row in sorted(validation_rows, key=lambda row: str(row.get("check_id", "")))],
        "compiled_assembly_graph_spec": dict(compiled_assembly_graph_spec) if mode_token in {"micro", "hybrid"} else {},
        "compiled_macro_capsule": dict(compiled_macro_capsule) if mode_token in {"macro", "hybrid"} else {},
        "hybrid_decomposition_plan": dict(hybrid_decomposition_plan) if mode_token == "hybrid" else {},
        "compiled_template_fingerprint": "",
        "deterministic_fingerprint": "",
    }
    result["compiled_template_fingerprint"] = canonical_sha256(
        {
            "template_id": template_token,
            "instantiation_mode": mode_token,
            "resolved_template_order": list(ordered_ids),
            "compiled_assembly_graph_spec": result.get("compiled_assembly_graph_spec") or {},
            "compiled_macro_capsule": result.get("compiled_macro_capsule") or {},
            "hybrid_decomposition_plan": result.get("hybrid_decomposition_plan") or {},
        }
    )
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def resolve_nested_template_order(
    *,
    template_id: str,
    system_template_registry_payload: Mapping[str, object] | None,
) -> List[str]:
    template_rows = normalize_system_template_rows(
        _template_rows_from_registry(system_template_registry_payload)
    )
    return _topological_template_order(
        root_template_id=str(template_id or "").strip(),
        template_rows_by_id=system_template_rows_by_id(template_rows),
    )


__all__ = [
    "REFUSAL_TEMPLATE_INVALID",
    "REFUSAL_TEMPLATE_NOT_FOUND",
    "REFUSAL_TEMPLATE_MISSING_REFERENCE",
    "REFUSAL_TEMPLATE_MISSING_DOMAIN",
    "REFUSAL_TEMPLATE_CYCLE",
    "REFUSAL_TEMPLATE_FORBIDDEN_MODE",
    "REFUSAL_TEMPLATE_SPEC_NONCOMPLIANT",
    "SystemTemplateCompileError",
    "build_system_template_row",
    "normalize_system_template_rows",
    "system_template_rows_by_id",
    "resolve_nested_template_order",
    "compile_system_template",
]
