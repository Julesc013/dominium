#!/usr/bin/env python3
"""Validate the Dominium project graph contract model and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


CONTRACT_DIR = Path("contracts/project_graph")
FIXTURE_DIR = Path("tests/contract/project_graph/fixtures")

MODEL_CONTRACT = CONTRACT_DIR / "project_graph_model.contract.toml"
DERIVATION_POLICY = CONTRACT_DIR / "project_graph_derivation_policy.contract.toml"
NODE_SCHEMA = CONTRACT_DIR / "node.schema.json"
EDGE_SCHEMA = CONTRACT_DIR / "edge.schema.json"
SNAPSHOT_SCHEMA = CONTRACT_DIR / "snapshot.schema.json"
QUERY_SCHEMA = CONTRACT_DIR / "impact_query.schema.json"
NODE_KIND_REGISTRY = CONTRACT_DIR / "node_kind.registry.json"
EDGE_KIND_REGISTRY = CONTRACT_DIR / "edge_kind.registry.json"
CONFIDENCE_REGISTRY = CONTRACT_DIR / "confidence.registry.json"
COMPLETENESS_REGISTRY = CONTRACT_DIR / "completeness_level.registry.json"
QUERY_KIND_REGISTRY = CONTRACT_DIR / "query_kind.registry.json"

EXPECTED_NODE_KINDS = {
    "file", "source_root", "component", "public_surface", "contract", "schema", "registry", "protocol",
    "command", "result", "refusal", "diagnostic", "service", "provider", "capability", "module",
    "workspace", "app", "pack", "profile", "artifact", "test", "validator", "evidence_packet",
    "release_artifact", "replacement_packet", "version_surface", "portability_row", "aide_task",
    "domain", "document_type", "patch_type", "transaction_type",
}
EXPECTED_EDGE_KINDS = {
    "owns", "contains", "declares", "implements", "consumes", "invokes", "produces", "emits",
    "validates", "tests", "packages", "mounts", "depends_on", "supersedes", "replaces", "deprecates",
    "refuses_with", "requires_capability", "provides_capability", "selected_by", "displayed_by",
    "generated_by", "documented_by", "proven_by", "affected_by", "blocks", "unblocks",
}
EXPECTED_CONFIDENCE = {"asserted", "derived", "inferred", "observed"}
EXPECTED_COMPLETENESS = {"fixture_only", "partial_inventory", "contract_index", "proof_index", "release_index"}
EXPECTED_QUERY_KINDS = {
    "what_depends_on", "what_does_this_command_use", "which_apps_expose", "which_tests_prove",
    "which_modules_display", "which_packs_provide", "which_release_artifacts_include",
    "which_public_surfaces_are_affected_by", "which_tasks_touched",
}
EXPECTED_FIXTURES = {
    "valid_node.json": True,
    "valid_edge.json": True,
    "valid_snapshot.json": True,
    "valid_impact_query.json": True,
    "invalid_node_unknown_kind.json": False,
    "invalid_edge_unknown_kind.json": False,
    "invalid_edge_missing_node.json": False,
    "invalid_node_path_identity.json": False,
    "invalid_snapshot_proof_index_missing_evidence.json": False,
    "invalid_node_missing_source_ref.json": False,
    "invalid_snapshot_source_truth_authority.json": False,
}

ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._:-][a-z0-9][a-z0-9_-]*)+$")
PATH_ID_RE = re.compile(r"(^[A-Za-z]:)|[/\\]|(\.(json|toml|py|md|hpp|cpp|h|c)$)", re.IGNORECASE)


class Result(object):
    def __init__(self):
        self.findings = []
        self.info = {}

    @property
    def errors(self):
        return [item for item in self.findings if item["level"] == "error"]

    @property
    def warnings(self):
        return [item for item in self.findings if item["level"] == "warning"]

    def add(self, level, code, message, path=None, **fields):
        finding = {"level": level, "code": code, "message": message}
        if path is not None:
            finding["path"] = str(path).replace("\\", "/")
        finding.update({key: value for key, value in fields.items() if value is not None})
        self.findings.append(finding)

    def error(self, code, message, path=None, **fields):
        self.add("error", code, message, path, **fields)

    def warn(self, code, message, path=None, **fields):
        self.add("warning", code, message, path, **fields)


def load_json(repo_root, rel, result=None):
    try:
        value = json.loads((repo_root / rel).read_text(encoding="utf-8-sig"))
    except Exception as exc:
        if result is not None:
            result.error("graph.json_parse", "JSON file does not parse: {}".format(exc), rel)
        return {}
    if not isinstance(value, dict):
        if result is not None:
            result.error("graph.json_root", "JSON root must be an object", rel)
        return {}
    return value


def registry_ids(payload, key):
    rows = payload.get(key)
    if not isinstance(rows, list):
        return set()
    return {row.get("id") for row in rows if isinstance(row, dict) and isinstance(row.get("id"), str)}


def is_string_list(value):
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value) and len(set(value)) == len(value)


def repo_relative(value):
    if not isinstance(value, str) or not value:
        return False
    parts = value.replace("\\", "/").split("/")
    return not Path(value).is_absolute() and ".." not in parts and not value.startswith("/")


def require_fields(payload, fields, result, rel, subject):
    missing = sorted(set(fields) - set(payload))
    if missing:
        result.error("graph.{}.required_missing".format(subject), "{} is missing required fields".format(subject), rel, missing=missing)


def check_source_ref(payload, result, rel):
    ref = payload.get("source_ref")
    if ref is None:
        result.error("graph.source_ref_missing", "graph fact is missing required source_ref", rel)
        return
    if not isinstance(ref, dict):
        result.error("graph.source_ref_invalid", "source_ref must be an object", rel)
        return
    if not ref.get("source_kind"):
        result.error("graph.source_ref_invalid", "source_ref.source_kind must be non-empty", rel)
    if not repo_relative(ref.get("path")):
        result.error("graph.source_ref_missing", "source_ref.path must be repo-relative and non-empty", rel, source_ref=ref.get("path"))


def check_id(value, field, result, rel):
    if not isinstance(value, str) or not ID_RE.match(value):
        result.error("graph.id.invalid", "{} must be a stable graph identifier".format(field), rel, field=field, value=value)


def check_node(node, result, rel, node_kinds):
    if not isinstance(node, dict):
        result.error("graph.node.invalid", "node must be an object", rel)
        return None
    require_fields(node, [
        "node_id", "node_kind", "label", "owner", "stability", "source_ref", "path_refs",
        "public_surface_refs", "artifact_refs", "capability_refs", "version_refs", "evidence_refs",
        "tags", "status", "generated", "derived_from",
    ], result, rel, "node")
    check_id(node.get("node_id"), "node_id", result, rel)
    if node.get("node_kind") not in node_kinds:
        result.error("graph.node_kind.unknown", "node_kind is not registered", rel, node_kind=node.get("node_kind"))
    check_source_ref(node, result, rel)
    for field in ["path_refs", "public_surface_refs", "artifact_refs", "capability_refs", "version_refs", "evidence_refs", "tags", "derived_from"]:
        if not is_string_list(node.get(field)):
            result.error("graph.list.invalid", "{} must be unique non-empty strings".format(field), rel, field=field)
    if not isinstance(node.get("generated"), bool):
        result.error("graph.node.generated_invalid", "node.generated must be boolean", rel)
    if node.get("generated") is True and not node.get("derived_from"):
        result.error("graph.derived_from_missing", "generated node must identify derived_from", rel)
    if node.get("stability") == "stable" and isinstance(node.get("node_id"), str) and PATH_ID_RE.search(node.get("node_id")):
        result.error("graph.path_identity_violation", "stable graph node_id must not be a raw path", rel, node_id=node.get("node_id"))
    return node.get("node_id") if isinstance(node.get("node_id"), str) else None


def check_edge(edge, result, rel, edge_kinds, confidence, node_ids):
    if not isinstance(edge, dict):
        result.error("graph.edge.invalid", "edge must be an object", rel)
        return None
    require_fields(edge, [
        "edge_id", "edge_kind", "from_node", "to_node", "source_ref", "stability",
        "confidence", "required", "direction", "diagnostic_refs", "tags",
    ], result, rel, "edge")
    check_id(edge.get("edge_id"), "edge_id", result, rel)
    check_id(edge.get("from_node"), "from_node", result, rel)
    check_id(edge.get("to_node"), "to_node", result, rel)
    if edge.get("edge_kind") not in edge_kinds:
        result.error("graph.edge_kind.unknown", "edge_kind is not registered", rel, edge_kind=edge.get("edge_kind"))
    if edge.get("confidence") not in confidence:
        result.error("graph.edge.confidence_invalid", "edge confidence is not registered", rel, confidence=edge.get("confidence"))
    if not isinstance(edge.get("required"), bool):
        result.error("graph.edge.required_invalid", "edge.required must be boolean", rel)
    check_source_ref(edge, result, rel)
    for field in ["diagnostic_refs", "tags"]:
        if not is_string_list(edge.get(field)):
            result.error("graph.list.invalid", "{} must be unique non-empty strings".format(field), rel, field=field)
    if node_ids is not None:
        for field in ["from_node", "to_node"]:
            if isinstance(edge.get(field), str) and edge.get(field) not in node_ids:
                result.error("graph.edge_target_missing", "{} does not reference a known fixture node".format(field), rel, node_id=edge.get(field))
    return edge.get("edge_id") if isinstance(edge.get("edge_id"), str) else None


def check_snapshot(snapshot, result, rel, registries):
    if not isinstance(snapshot, dict):
        result.error("graph.snapshot.invalid", "snapshot must be an object", rel)
        return
    require_fields(snapshot, [
        "snapshot_id", "repo_ref", "source_commit", "generator_id", "generator_version",
        "graph_schema_version", "node_count", "edge_count", "diagnostics", "evidence_ref",
        "completeness_level", "known_gaps",
    ], result, rel, "snapshot")
    check_id(snapshot.get("snapshot_id"), "snapshot_id", result, rel)
    if snapshot.get("completeness_level") not in registries["completeness"]:
        result.error("graph.snapshot.completeness_unknown", "snapshot completeness_level is not registered", rel)
    if snapshot.get("completeness_level") in {"proof_index", "release_index"} and not snapshot.get("evidence_ref"):
        result.error("graph.evidence_required_missing", "proof_index and release_index snapshots require evidence_ref", rel)
    if snapshot.get("authority_class", "derived_index") != "derived_index" or snapshot.get("graph_is_source_truth") is True:
        result.error("graph.authority_violation", "project graph snapshot must be a derived index, not source truth", rel)
    for field in ["diagnostics", "known_gaps"]:
        if not is_string_list(snapshot.get(field)):
            result.error("graph.list.invalid", "{} must be unique non-empty strings".format(field), rel, field=field)
    nodes = snapshot.get("nodes")
    node_ids = set()
    if nodes is not None:
        if not isinstance(nodes, list):
            result.error("graph.snapshot.nodes_invalid", "snapshot.nodes must be an array", rel)
        else:
            for node in nodes:
                node_id = check_node(node, result, rel, registries["node_kinds"])
                if node_id:
                    node_ids.add(node_id)
    edges = snapshot.get("edges")
    edge_ids = set()
    if edges is not None:
        if not isinstance(edges, list):
            result.error("graph.snapshot.edges_invalid", "snapshot.edges must be an array", rel)
        else:
            for edge in edges:
                edge_id = check_edge(edge, result, rel, registries["edge_kinds"], registries["confidence"], node_ids)
                if edge_id:
                    edge_ids.add(edge_id)
    if isinstance(snapshot.get("node_count"), int) and nodes is not None and snapshot.get("node_count") != len(node_ids):
        result.error("graph.snapshot.node_count_mismatch", "node_count must match embedded nodes", rel)
    if isinstance(snapshot.get("edge_count"), int) and edges is not None and snapshot.get("edge_count") != len(edge_ids):
        result.error("graph.snapshot.edge_count_mismatch", "edge_count must match embedded edges", rel)


def check_query(query, result, rel, registries):
    if not isinstance(query, dict):
        result.error("graph.query.invalid", "impact query must be an object", rel)
        return
    require_fields(query, ["query_id", "query_kind", "input_nodes", "result_nodes", "result_edges", "confidence", "diagnostics", "evidence_ref"], result, rel, "query")
    check_id(query.get("query_id"), "query_id", result, rel)
    if query.get("query_kind") not in registries["query_kinds"]:
        result.error("graph.query.kind_unknown", "query_kind is not registered", rel)
    if query.get("confidence") not in registries["confidence"]:
        result.error("graph.query.confidence_invalid", "query confidence is not registered", rel)
    if not query.get("evidence_ref"):
        result.error("graph.evidence_required_missing", "impact query requires evidence_ref", rel)
    for field in ["input_nodes", "result_nodes", "result_edges", "diagnostics"]:
        if not is_string_list(query.get(field)):
            result.error("graph.list.invalid", "{} must be unique non-empty strings".format(field), rel, field=field)


def check_contract_files(repo_root, result):
    required = [
        MODEL_CONTRACT, DERIVATION_POLICY, NODE_SCHEMA, EDGE_SCHEMA, SNAPSHOT_SCHEMA, QUERY_SCHEMA,
        NODE_KIND_REGISTRY, EDGE_KIND_REGISTRY, CONFIDENCE_REGISTRY, COMPLETENESS_REGISTRY, QUERY_KIND_REGISTRY,
    ]
    for rel in required:
        if not (repo_root / rel).exists():
            result.error("graph.file_missing", "required project graph file is missing", rel)

    registries = {
        "node_kinds": registry_ids(load_json(repo_root, NODE_KIND_REGISTRY, result), "kinds"),
        "edge_kinds": registry_ids(load_json(repo_root, EDGE_KIND_REGISTRY, result), "kinds"),
        "confidence": registry_ids(load_json(repo_root, CONFIDENCE_REGISTRY, result), "levels"),
        "completeness": registry_ids(load_json(repo_root, COMPLETENESS_REGISTRY, result), "levels"),
        "query_kinds": registry_ids(load_json(repo_root, QUERY_KIND_REGISTRY, result), "kinds"),
    }
    expected = {
        "node_kinds": EXPECTED_NODE_KINDS,
        "edge_kinds": EXPECTED_EDGE_KINDS,
        "confidence": EXPECTED_CONFIDENCE,
        "completeness": EXPECTED_COMPLETENESS,
        "query_kinds": EXPECTED_QUERY_KINDS,
    }
    for key in expected:
        missing = sorted(expected[key] - registries[key])
        if missing:
            result.error("graph.registry_missing_expected", "{} registry is missing expected values".format(key), missing=missing)

    schema_expectations = [
        (NODE_SCHEMA, "dominium.project_graph.node.v1", {"node_id", "node_kind", "source_ref"}),
        (EDGE_SCHEMA, "dominium.project_graph.edge.v1", {"edge_id", "edge_kind", "from_node", "to_node", "source_ref"}),
        (SNAPSHOT_SCHEMA, "dominium.project_graph.snapshot.v1", {"snapshot_id", "repo_ref", "source_commit", "completeness_level"}),
        (QUERY_SCHEMA, "dominium.project_graph.impact_query.v1", {"query_id", "query_kind", "input_nodes", "result_nodes", "result_edges"}),
    ]
    for rel, schema_id, required_fields in schema_expectations:
        payload = load_json(repo_root, rel, result)
        if payload.get("$id") != schema_id:
            result.error("graph.schema_id_invalid", "schema $id is incorrect", rel, expected=schema_id, actual=payload.get("$id"))
        missing = sorted(required_fields - set(payload.get("required") or []))
        if missing:
            result.error("graph.schema_required_missing", "schema is missing required fields", rel, missing=missing)

    model_text = (repo_root / MODEL_CONTRACT).read_text(encoding="utf-8-sig") if (repo_root / MODEL_CONTRACT).exists() else ""
    policy_text = (repo_root / DERIVATION_POLICY).read_text(encoding="utf-8-sig") if (repo_root / DERIVATION_POLICY).exists() else ""
    if 'id = "dominium.project_graph.model.v1"' not in model_text:
        result.error("graph.contract_id_invalid", "project graph model contract id is incorrect", MODEL_CONTRACT)
    for needle in ["graph_is_source_truth = false", "graph_is_derived_index = true", "workbench_may_override_authority = false", "aide_may_override_allowed_paths = false"]:
        if needle not in model_text:
            result.error("graph.authority_violation", "model contract is missing authority rule: {}".format(needle), MODEL_CONTRACT)
    for needle in ["graph_output_is_source_truth = false", "facts_must_cite_source_ref = true", "cache_invalid_when_source_commit_changes = true", "cache_invalid_when_generator_version_changes = true"]:
        if needle not in policy_text:
            result.error("graph.policy_missing", "derivation policy is missing rule: {}".format(needle), DERIVATION_POLICY)
    return registries


def validate_fixture(repo_root, rel, registries):
    sub = Result()
    payload = load_json(repo_root, rel, sub)
    kind = payload.get("fixture_kind")
    if kind == "node":
        check_node(payload.get("node"), sub, rel, registries["node_kinds"])
    elif kind == "edge":
        node_ids = set()
        for node in payload.get("nodes") or []:
            node_id = check_node(node, sub, rel, registries["node_kinds"])
            if node_id:
                node_ids.add(node_id)
        check_edge(payload.get("edge"), sub, rel, registries["edge_kinds"], registries["confidence"], node_ids)
    elif kind == "snapshot":
        check_snapshot(payload.get("snapshot"), sub, rel, registries)
    elif kind == "impact_query":
        check_query(payload.get("query"), sub, rel, registries)
    else:
        sub.error("graph.fixture_kind_unknown", "fixture_kind is not recognized", rel, fixture_kind=kind)
    return not sub.errors, sub.findings


def check_fixtures(repo_root, result, registries):
    rows = []
    for filename, expected_valid in sorted(EXPECTED_FIXTURES.items()):
        rel = FIXTURE_DIR / filename
        if not (repo_root / rel).exists():
            result.error("graph.fixture_missing", "expected fixture is missing", rel)
            rows.append({"path": rel.as_posix(), "expected_valid": expected_valid, "actual_valid": False, "status": "missing"})
            continue
        actual_valid, findings = validate_fixture(repo_root, rel, registries)
        if actual_valid != expected_valid:
            result.error("graph.fixture_expectation_failed", "fixture did not match expected validity", rel, expected_valid=expected_valid, actual_valid=actual_valid, fixture_findings=findings)
        rows.append({"path": rel.as_posix(), "expected_valid": expected_valid, "actual_valid": actual_valid, "finding_count": len(findings), "status": "pass" if actual_valid == expected_valid else "fail"})
    result.info["fixtures"] = rows


def run_inventory(repo_root, result):
    roots = ["contracts", "tools/validators", "tests/contract", "docs", ".aide/reports"]
    try:
        proc = subprocess.run(["git", "ls-files"] + roots, cwd=str(repo_root), check=False, text=True, capture_output=True)
        files = [line for line in proc.stdout.splitlines() if line]
    except Exception:
        files = []
    result.info["inventory"] = {"tracked_total": len(files), "roots": {root: sum(1 for item in files if item == root or item.startswith(root + "/")) for root in roots}}
    result.warn("graph.inventory_warning_only", "inventory mode is descriptive only and does not prove graph completeness", FIXTURE_DIR)


def run(repo_root, include_fixtures, inventory):
    result = Result()
    registries = check_contract_files(repo_root, result)
    if include_fixtures:
        check_fixtures(repo_root, result, registries)
    if inventory:
        run_inventory(repo_root, result)
    result.info["summary"] = {"errors": len(result.errors), "warnings": len(result.warnings), "fixtures_checked": len(result.info.get("fixtures", []))}
    return result


def emit_text(result):
    print("project graph contract: {}".format("PASS" if not result.errors else "FAIL"))
    print("errors: {}".format(len(result.errors)))
    print("warnings: {}".format(len(result.warnings)))
    if "fixtures" in result.info:
        print("fixtures: {} checked".format(len(result.info["fixtures"])))
    for finding in result.findings:
        path = " " + finding["path"] if finding.get("path") else ""
        print("{}: {}:{} {}".format(finding["level"].upper(), finding["code"], path, finding["message"]))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--inventory", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    inventory_only = args.inventory and not args.strict and not args.fixtures and not args.json
    result = run(repo_root, include_fixtures=not inventory_only, inventory=args.inventory)
    if args.json:
        print(json.dumps({"status": "PASS" if not result.errors else "FAIL", "findings": result.findings, "info": result.info}, indent=2, sort_keys=True))
    else:
        emit_text(result)
    if (args.strict or args.fixtures) and result.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
