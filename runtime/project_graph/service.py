"""Deterministic loader, validator, sorter, and fingerprint helper for project graphs.

This helper treats project graph payloads as contract data. It never mutates
authoritative project truth and never infers runtime, UI, or release authority
from graph shape.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


PROJECT_GRAPH_SCHEMA_ID = "dominium.project_graph.payload.v1"
PROJECT_GRAPH_SCHEMA_VERSION = "1.0.0"

ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9][a-z0-9_-]*)+$")
GRAPH_ID_RE = re.compile(r"^dominium\.project_graph\.[a-z0-9][a-z0-9_.-]+$")
COMMAND_ID_RE = re.compile(r"^(domino|dominium)(\.[a-z0-9][a-z0-9_-]*)+$")

VALID_GRAPH_STABILITY = {"provisional", "stable", "experimental", "derived"}
VALID_NODE_KINDS = {
    "task",
    "contract",
    "schema",
    "runtime_helper",
    "validator",
    "fixture",
    "test",
    "document",
    "audit",
    "proof",
    "gate",
}
VALID_NODE_STATUSES = {
    "planned",
    "active",
    "blocked",
    "complete",
    "pass",
    "pass_with_warnings",
    "fail",
    "not_run",
    "refused",
}
VALID_EDGE_KINDS = {
    "depends_on",
    "proves",
    "validates",
    "documents",
    "materializes",
    "blocks",
    "references",
}
VALID_DEPENDENCY_KINDS = {
    "requires",
    "orders_after",
    "validates_against",
    "is_proven_by",
}
VALID_PROOF_KINDS = {
    "schema_parse",
    "validator",
    "fixture",
    "unit_test",
    "compile",
    "audit",
    "document",
}
VALID_EVIDENCE_STATUSES = {
    "pass",
    "pass_with_warnings",
    "fail",
    "blocked",
    "not_run",
    "partial",
    "ok",
    "warning",
    "refused",
    "error",
}
VALID_RESULT_STATUSES = {"ok", "warning", "refused", "error"}


@dataclass(frozen=True)
class ProjectGraphFinding:
    level: str
    code: str
    message: str
    path: str = ""

    def as_dict(self) -> Dict[str, str]:
        item = {"level": self.level, "code": self.code, "message": self.message}
        if self.path:
            item["path"] = self.path
        return item


@dataclass(frozen=True)
class ProjectGraphValidation:
    valid: bool
    findings: Tuple[ProjectGraphFinding, ...]

    @property
    def errors(self) -> Tuple[ProjectGraphFinding, ...]:
        return tuple(item for item in self.findings if item.level == "error")

    @property
    def warnings(self) -> Tuple[ProjectGraphFinding, ...]:
        return tuple(item for item in self.findings if item.level == "warning")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "findings": [item.as_dict() for item in self.findings],
        }


def _finding(level: str, code: str, message: str, path: str = "") -> ProjectGraphFinding:
    return ProjectGraphFinding(level=level, code=code, message=message, path=path)


def _token(value: Any) -> str:
    return str(value or "").strip()


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _is_id(value: Any) -> bool:
    return bool(ID_RE.match(_token(value)))


def _sorted_string_list(value: Any) -> List[str]:
    return sorted({_token(item) for item in _as_list(value) if _token(item)})


def _sort_evidence_refs(value: Any) -> List[Dict[str, Any]]:
    refs = [dict(item) for item in _as_list(value) if isinstance(item, Mapping)]
    return sorted(
        refs,
        key=lambda item: (
            _token(item.get("evidence_id")),
            _token(item.get("subject_id")),
            _token(item.get("path")),
            _token(item.get("status")),
        ),
    )


def _sort_result_refs(value: Any) -> List[Dict[str, Any]]:
    refs = [dict(item) for item in _as_list(value) if isinstance(item, Mapping)]
    return sorted(
        refs,
        key=lambda item: (
            _token(item.get("command_id")),
            _token(item.get("run_id")),
            _token(item.get("status")),
            _token(item.get("summary")),
        ),
    )


def _canonical_known_lists(item: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(item))
    for key in ("paths", "tags", "proof_refs"):
        if key in out:
            out[key] = _sorted_string_list(out.get(key))
    if "evidence_refs" in out:
        out["evidence_refs"] = _sort_evidence_refs(out.get("evidence_refs"))
    if "result_refs" in out:
        out["result_refs"] = _sort_result_refs(out.get("result_refs"))
    return out


def _canonical_tree(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical_tree(value[key]) for key in sorted(value.keys(), key=str)}
    if isinstance(value, list):
        return [_canonical_tree(item) for item in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def _canonical_json_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical_tree(payload), ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def load_project_graph_payload(path: str | Path) -> Dict[str, Any]:
    """Load a project graph JSON payload from disk as a root object."""

    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("project graph payload root must be a JSON object")
    return dict(payload)


def _validate_evidence_ref(value: Any, path: str) -> List[ProjectGraphFinding]:
    findings: List[ProjectGraphFinding] = []
    if not isinstance(value, Mapping):
        return [_finding("error", "evidence_ref_shape", "evidence_refs entries must be objects", path)]
    row = dict(value)
    for key in ("evidence_id", "path", "subject_id", "status"):
        if not _token(row.get(key)):
            findings.append(_finding("error", "evidence_ref_missing_field", f"evidence ref missing {key}", f"{path}.{key}"))
    status = _token(row.get("status"))
    if status and status not in VALID_EVIDENCE_STATUSES:
        findings.append(_finding("error", "evidence_ref_bad_status", f"unsupported evidence status: {status}", f"{path}.status"))
    return findings


def _validate_result_ref(value: Any, path: str) -> List[ProjectGraphFinding]:
    findings: List[ProjectGraphFinding] = []
    if not isinstance(value, Mapping):
        return [_finding("error", "result_ref_shape", "result_refs entries must be objects", path)]
    row = dict(value)
    for key in ("command_id", "status", "summary"):
        if not _token(row.get(key)):
            findings.append(_finding("error", "result_ref_missing_field", f"result ref missing {key}", f"{path}.{key}"))
    command_id = _token(row.get("command_id"))
    if command_id and not COMMAND_ID_RE.match(command_id):
        findings.append(_finding("error", "result_ref_bad_command_id", f"unsupported command_id: {command_id}", f"{path}.command_id"))
    status = _token(row.get("status"))
    if status and status not in VALID_RESULT_STATUSES:
        findings.append(_finding("error", "result_ref_bad_status", f"unsupported result status: {status}", f"{path}.status"))
    return findings


def _validate_node(row: Mapping[str, Any], index: int) -> List[ProjectGraphFinding]:
    path = f"nodes[{index}]"
    findings: List[ProjectGraphFinding] = []
    node_id = _token(row.get("node_id"))
    if not node_id:
        findings.append(_finding("error", "node_missing_id", "node_id is required", f"{path}.node_id"))
    elif not _is_id(node_id):
        findings.append(_finding("error", "node_bad_id", f"node_id is not a stable dotted id: {node_id}", f"{path}.node_id"))
    node_kind = _token(row.get("node_kind"))
    if node_kind not in VALID_NODE_KINDS:
        findings.append(_finding("error", "node_bad_kind", f"unsupported node_kind: {node_kind}", f"{path}.node_kind"))
    status = _token(row.get("status"))
    if status not in VALID_NODE_STATUSES:
        findings.append(_finding("error", "node_bad_status", f"unsupported node status: {status}", f"{path}.status"))
    if not _token(row.get("title")):
        findings.append(_finding("error", "node_missing_title", "title is required", f"{path}.title"))
    for ref_index, ref in enumerate(_as_list(row.get("evidence_refs"))):
        findings.extend(_validate_evidence_ref(ref, f"{path}.evidence_refs[{ref_index}]"))
    return findings


def _validate_edge(row: Mapping[str, Any], index: int) -> List[ProjectGraphFinding]:
    path = f"edges[{index}]"
    findings: List[ProjectGraphFinding] = []
    for key in ("edge_id", "source_node_id", "target_node_id", "edge_kind"):
        if not _token(row.get(key)):
            findings.append(_finding("error", "edge_missing_field", f"edge missing {key}", f"{path}.{key}"))
    for key in ("edge_id", "source_node_id", "target_node_id"):
        value = _token(row.get(key))
        if value and not _is_id(value):
            findings.append(_finding("error", "edge_bad_id", f"{key} is not a stable dotted id: {value}", f"{path}.{key}"))
    edge_kind = _token(row.get("edge_kind"))
    if edge_kind and edge_kind not in VALID_EDGE_KINDS:
        findings.append(_finding("error", "edge_bad_kind", f"unsupported edge_kind: {edge_kind}", f"{path}.edge_kind"))
    return findings


def _validate_dependency(row: Mapping[str, Any], index: int) -> List[ProjectGraphFinding]:
    path = f"dependencies[{index}]"
    findings: List[ProjectGraphFinding] = []
    for key in ("dependency_id", "node_id", "depends_on_node_id", "dependency_kind", "required"):
        if key not in row or (key != "required" and not _token(row.get(key))):
            findings.append(_finding("error", "dependency_missing_field", f"dependency missing {key}", f"{path}.{key}"))
    for key in ("dependency_id", "node_id", "depends_on_node_id"):
        value = _token(row.get(key))
        if value and not _is_id(value):
            findings.append(_finding("error", "dependency_bad_id", f"{key} is not a stable dotted id: {value}", f"{path}.{key}"))
    dependency_kind = _token(row.get("dependency_kind"))
    if dependency_kind and dependency_kind not in VALID_DEPENDENCY_KINDS:
        findings.append(
            _finding("error", "dependency_bad_kind", f"unsupported dependency_kind: {dependency_kind}", f"{path}.dependency_kind")
        )
    if "required" in row and not isinstance(row.get("required"), bool):
        findings.append(_finding("error", "dependency_required_not_bool", "required must be boolean", f"{path}.required"))
    return findings


def _validate_proof(row: Mapping[str, Any], index: int) -> List[ProjectGraphFinding]:
    path = f"proofs[{index}]"
    findings: List[ProjectGraphFinding] = []
    for key in ("proof_id", "subject_node_id", "proof_kind", "status", "summary"):
        if not _token(row.get(key)):
            findings.append(_finding("error", "proof_missing_field", f"proof missing {key}", f"{path}.{key}"))
    for key in ("proof_id", "subject_node_id"):
        value = _token(row.get(key))
        if value and not _is_id(value):
            findings.append(_finding("error", "proof_bad_id", f"{key} is not a stable dotted id: {value}", f"{path}.{key}"))
    proof_kind = _token(row.get("proof_kind"))
    if proof_kind and proof_kind not in VALID_PROOF_KINDS:
        findings.append(_finding("error", "proof_bad_kind", f"unsupported proof_kind: {proof_kind}", f"{path}.proof_kind"))
    status = _token(row.get("status"))
    if status and status not in VALID_EVIDENCE_STATUSES:
        findings.append(_finding("error", "proof_bad_status", f"unsupported proof status: {status}", f"{path}.status"))
    for ref_index, ref in enumerate(_as_list(row.get("evidence_refs"))):
        findings.extend(_validate_evidence_ref(ref, f"{path}.evidence_refs[{ref_index}]"))
    for ref_index, ref in enumerate(_as_list(row.get("result_refs"))):
        findings.extend(_validate_result_ref(ref, f"{path}.result_refs[{ref_index}]"))
    if status in {"pass", "pass_with_warnings", "ok"} and not _as_list(row.get("evidence_refs")) and not _as_list(row.get("result_refs")):
        findings.append(
            _finding("error", "proof_without_evidence", "passing proofs require evidence_refs or result_refs", path)
        )
    return findings


def _duplicates(values: Iterable[str]) -> List[str]:
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _topological_order(node_ids: Sequence[str], dependencies: Sequence[Mapping[str, Any]]) -> Tuple[List[str], List[str]]:
    ids = sorted(set(_token(item) for item in node_ids if _token(item)))
    adjacency: Dict[str, List[str]] = {node_id: [] for node_id in ids}
    indegree: Dict[str, int] = {node_id: 0 for node_id in ids}
    for dep in dependencies:
        node_id = _token(dep.get("node_id"))
        depends_on = _token(dep.get("depends_on_node_id"))
        if node_id not in indegree or depends_on not in indegree:
            continue
        adjacency[depends_on].append(node_id)
        indegree[node_id] += 1
    ready = sorted(node_id for node_id, count in indegree.items() if count == 0)
    ordered: List[str] = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for target in sorted(adjacency[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort()
    unresolved = sorted(node_id for node_id, count in indegree.items() if count > 0)
    return ordered, unresolved


def validate_project_graph_payload(payload: Mapping[str, Any]) -> ProjectGraphValidation:
    """Validate project graph shape, references, dependency DAG, and proof evidence."""

    findings: List[ProjectGraphFinding] = []
    if not isinstance(payload, Mapping):
        return ProjectGraphValidation(
            valid=False,
            findings=(_finding("error", "payload_shape", "project graph payload root must be an object", "$"),),
        )

    graph = dict(payload)
    for key in ("schema_id", "schema_version", "graph_id", "owner", "stability", "nodes", "edges", "dependencies", "proofs"):
        if key not in graph:
            findings.append(_finding("error", "payload_missing_field", f"payload missing {key}", key))

    if graph.get("schema_id") != PROJECT_GRAPH_SCHEMA_ID:
        findings.append(
            _finding("error", "payload_bad_schema_id", "schema_id must be dominium.project_graph.payload.v1", "schema_id")
        )
    if graph.get("schema_version") != PROJECT_GRAPH_SCHEMA_VERSION:
        findings.append(_finding("error", "payload_bad_schema_version", "schema_version must be 1.0.0", "schema_version"))
    graph_id = _token(graph.get("graph_id"))
    if graph_id and not GRAPH_ID_RE.match(graph_id):
        findings.append(_finding("error", "payload_bad_graph_id", f"graph_id is not governed: {graph_id}", "graph_id"))
    stability = _token(graph.get("stability"))
    if stability and stability not in VALID_GRAPH_STABILITY:
        findings.append(_finding("error", "payload_bad_stability", f"unsupported stability: {stability}", "stability"))

    arrays: Dict[str, List[Any]] = {}
    for key in ("nodes", "edges", "dependencies", "proofs"):
        value = graph.get(key)
        if not isinstance(value, list):
            findings.append(_finding("error", "payload_array_shape", f"{key} must be an array", key))
            arrays[key] = []
        else:
            arrays[key] = list(value)

    node_rows = [dict(row) for row in arrays["nodes"] if isinstance(row, Mapping)]
    edge_rows = [dict(row) for row in arrays["edges"] if isinstance(row, Mapping)]
    dependency_rows = [dict(row) for row in arrays["dependencies"] if isinstance(row, Mapping)]
    proof_rows = [dict(row) for row in arrays["proofs"] if isinstance(row, Mapping)]

    for key, rows in arrays.items():
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                findings.append(_finding("error", f"{key}_entry_shape", f"{key} entries must be objects", f"{key}[{index}]"))

    for index, row in enumerate(node_rows):
        findings.extend(_validate_node(row, index))
    for index, row in enumerate(edge_rows):
        findings.extend(_validate_edge(row, index))
    for index, row in enumerate(dependency_rows):
        findings.extend(_validate_dependency(row, index))
    for index, row in enumerate(proof_rows):
        findings.extend(_validate_proof(row, index))

    node_ids = [_token(row.get("node_id")) for row in node_rows if _token(row.get("node_id"))]
    proof_ids = [_token(row.get("proof_id")) for row in proof_rows if _token(row.get("proof_id"))]
    edge_ids = [_token(row.get("edge_id")) for row in edge_rows if _token(row.get("edge_id"))]
    dependency_ids = [_token(row.get("dependency_id")) for row in dependency_rows if _token(row.get("dependency_id"))]

    for duplicate in _duplicates(node_ids):
        findings.append(_finding("error", "node_duplicate_id", f"duplicate node_id: {duplicate}", "nodes"))
    for duplicate in _duplicates(proof_ids):
        findings.append(_finding("error", "proof_duplicate_id", f"duplicate proof_id: {duplicate}", "proofs"))
    for duplicate in _duplicates(edge_ids):
        findings.append(_finding("error", "edge_duplicate_id", f"duplicate edge_id: {duplicate}", "edges"))
    for duplicate in _duplicates(dependency_ids):
        findings.append(_finding("error", "dependency_duplicate_id", f"duplicate dependency_id: {duplicate}", "dependencies"))

    node_id_set = set(node_ids)
    proof_id_set = set(proof_ids)
    seen_dependency_pairs = set()
    for index, row in enumerate(dependency_rows):
        node_id = _token(row.get("node_id"))
        depends_on = _token(row.get("depends_on_node_id"))
        if node_id and node_id not in node_id_set:
            findings.append(_finding("error", "dependency_unknown_node", f"unknown dependency node: {node_id}", f"dependencies[{index}].node_id"))
        if depends_on and depends_on not in node_id_set:
            findings.append(
                _finding("error", "dependency_unknown_target", f"unknown depends_on_node_id: {depends_on}", f"dependencies[{index}].depends_on_node_id")
            )
        pair = (node_id, depends_on, _token(row.get("dependency_kind")))
        if node_id and depends_on and pair in seen_dependency_pairs:
            findings.append(_finding("error", "dependency_duplicate_relation", "duplicate dependency relation", f"dependencies[{index}]"))
        seen_dependency_pairs.add(pair)
        for ref_index, proof_ref in enumerate(_as_list(row.get("proof_refs"))):
            proof_id = _token(proof_ref)
            if proof_id and proof_id not in proof_id_set:
                findings.append(
                    _finding("error", "dependency_unknown_proof", f"unknown proof ref: {proof_id}", f"dependencies[{index}].proof_refs[{ref_index}]")
                )

    for index, row in enumerate(edge_rows):
        for key in ("source_node_id", "target_node_id"):
            node_id = _token(row.get(key))
            if node_id and node_id not in node_id_set:
                findings.append(_finding("error", "edge_unknown_node", f"unknown {key}: {node_id}", f"edges[{index}].{key}"))
    for index, row in enumerate(proof_rows):
        node_id = _token(row.get("subject_node_id"))
        if node_id and node_id not in node_id_set:
            findings.append(_finding("error", "proof_unknown_subject", f"unknown subject_node_id: {node_id}", f"proofs[{index}].subject_node_id"))

    if stability == "stable" and not proof_rows:
        findings.append(_finding("error", "stable_graph_without_proofs", "stable project graph payloads require proofs", "proofs"))

    if not any(item.code in {"dependency_unknown_node", "dependency_unknown_target"} for item in findings):
        _ordered, unresolved = _topological_order(node_ids, dependency_rows)
        if unresolved:
            findings.append(_finding("error", "dependency_cycle", f"dependency cycle includes: {', '.join(unresolved)}", "dependencies"))

    return ProjectGraphValidation(valid=not any(item.level == "error" for item in findings), findings=tuple(findings))


def topological_node_order(payload: Mapping[str, Any]) -> List[str]:
    """Return deterministic dependency order with prerequisites before dependents."""

    validation = validate_project_graph_payload(payload)
    if not validation.valid:
        codes = ", ".join(item.code for item in validation.errors)
        raise ValueError(f"project graph is invalid: {codes}")
    nodes = [dict(row) for row in _as_list(payload.get("nodes")) if isinstance(row, Mapping)]
    dependencies = [dict(row) for row in _as_list(payload.get("dependencies")) if isinstance(row, Mapping)]
    ordered, unresolved = _topological_order([_token(row.get("node_id")) for row in nodes], dependencies)
    if unresolved:
        raise ValueError("project graph dependency cycle: {}".format(", ".join(unresolved)))
    return ordered


def canonicalize_project_graph(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a deterministic copy of a graph payload with known rows sorted."""

    graph = copy.deepcopy(dict(payload or {}))
    graph["nodes"] = sorted(
        [_canonical_known_lists(dict(row)) for row in _as_list(graph.get("nodes")) if isinstance(row, Mapping)],
        key=lambda row: _token(row.get("node_id")),
    )
    graph["edges"] = sorted(
        [_canonical_known_lists(dict(row)) for row in _as_list(graph.get("edges")) if isinstance(row, Mapping)],
        key=lambda row: (
            _token(row.get("source_node_id")),
            _token(row.get("target_node_id")),
            _token(row.get("edge_kind")),
            _token(row.get("edge_id")),
        ),
    )
    graph["dependencies"] = sorted(
        [_canonical_known_lists(dict(row)) for row in _as_list(graph.get("dependencies")) if isinstance(row, Mapping)],
        key=lambda row: (
            _token(row.get("node_id")),
            _token(row.get("depends_on_node_id")),
            _token(row.get("dependency_kind")),
            _token(row.get("dependency_id")),
        ),
    )
    graph["proofs"] = sorted(
        [_canonical_known_lists(dict(row)) for row in _as_list(graph.get("proofs")) if isinstance(row, Mapping)],
        key=lambda row: _token(row.get("proof_id")),
    )
    return dict(_canonical_tree(graph))


def project_graph_fingerprint(payload: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 fingerprint over the canonical graph payload."""

    canonical = canonicalize_project_graph(payload)
    return hashlib.sha256(_canonical_json_text(canonical).encode("utf-8")).hexdigest()


def build_validation_result(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Build a result-schema-compatible validation summary for a graph payload."""

    validation = validate_project_graph_payload(payload)
    graph_id = _token(dict(payload or {}).get("graph_id"))
    details: Dict[str, Any] = {
        "graph_id": graph_id,
        "valid": validation.valid,
        "graph_hash": "",
        "topological_node_order": [],
    }
    if validation.valid:
        details["graph_hash"] = project_graph_fingerprint(payload)
        details["topological_node_order"] = topological_node_order(payload)
    status = "ok" if validation.valid else "error"
    summary = "project graph payload valid" if validation.valid else "project graph payload invalid"
    return {
        "command_id": "dominium.project_graph.validate",
        "status": status,
        "summary": summary,
        "diagnostics": [item.as_dict() for item in validation.findings],
        "evidence": [],
        "payload": details,
    }


__all__ = [
    "PROJECT_GRAPH_SCHEMA_ID",
    "PROJECT_GRAPH_SCHEMA_VERSION",
    "ProjectGraphFinding",
    "ProjectGraphValidation",
    "build_validation_result",
    "canonicalize_project_graph",
    "load_project_graph_payload",
    "project_graph_fingerprint",
    "topological_node_order",
    "validate_project_graph_payload",
]
