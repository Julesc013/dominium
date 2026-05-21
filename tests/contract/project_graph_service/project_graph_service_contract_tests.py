#!/usr/bin/env python3
"""Contract tests for the narrow project graph service helper."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.project_graph import (  # noqa: E402
    build_validation_result,
    canonicalize_project_graph,
    load_project_graph_payload,
    project_graph_fingerprint,
    topological_node_order,
    validate_project_graph_payload,
)
from tools.validators.contracts.check_project_graph_service import run_checks  # noqa: E402


FIXTURE_DIR = REPO_ROOT / "tests/contract/project_graph_service/fixtures"
EXPECTED_ORDER = [
    "task.foundation-lock",
    "task.portability-arch-policy",
    "task.project-graph-service",
    "contract.project-graph-service",
    "runtime.project-graph-helper",
    "validator.project-graph-service",
    "proof.project-graph-validation",
]
INVALID_FIXTURES = [
    "invalid_dependency_cycle.json",
    "invalid_duplicate_node.json",
    "invalid_missing_dependency_target.json",
    "invalid_proof_without_evidence.json",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fixture(name: str) -> dict:
    return load_project_graph_payload(FIXTURE_DIR / name)


def main() -> int:
    required_paths = [
        "contracts/project_graph/project_graph.schema.json",
        "contracts/project_graph/project_graph_service.contract.toml",
        "runtime/project_graph/service.py",
        "tools/validators/contracts/check_project_graph_service.py",
        "docs/architecture/project_graph_service.md",
        "docs/repo/audits/PROJECT_GRAPH_SERVICE_01.md",
    ]
    for rel in required_paths:
        require((REPO_ROOT / rel).exists(), f"missing required artifact: {rel}")

    valid = fixture("valid_project_graph.json")
    shuffled = fixture("valid_project_graph_shuffled.json")
    valid_result = validate_project_graph_payload(valid)
    shuffled_result = validate_project_graph_payload(shuffled)
    require(valid_result.valid, f"valid fixture failed: {valid_result.as_dict()}")
    require(shuffled_result.valid, f"shuffled valid fixture failed: {shuffled_result.as_dict()}")

    require(topological_node_order(valid) == EXPECTED_ORDER, "unexpected topological order for valid fixture")
    require(topological_node_order(shuffled) == EXPECTED_ORDER, "unexpected topological order for shuffled fixture")
    require(project_graph_fingerprint(valid) == project_graph_fingerprint(shuffled), "shuffled fixture changed graph fingerprint")

    canonical = canonicalize_project_graph(shuffled)
    require(
        [row["node_id"] for row in canonical["nodes"]] == sorted(row["node_id"] for row in canonical["nodes"]),
        "canonical node order is not deterministic",
    )

    service_result = build_validation_result(valid)
    require(service_result["status"] == "ok", "valid graph service result should be ok")
    require(service_result["payload"]["topological_node_order"] == EXPECTED_ORDER, "service result order mismatch")
    require(service_result["payload"]["graph_hash"] == project_graph_fingerprint(valid), "service result hash mismatch")

    for name in INVALID_FIXTURES:
        invalid = fixture(name)
        validation = validate_project_graph_payload(invalid)
        require(not validation.valid, f"invalid fixture unexpectedly passed: {name}")
        invalid_result = build_validation_result(invalid)
        require(invalid_result["status"] == "error", f"invalid fixture result should be error: {name}")

    validator_result = run_checks(REPO_ROOT, include_fixtures=True)
    require(not validator_result.errors, f"project graph validator errors: {validator_result.findings}")

    print("project graph service contract tests OK")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"project graph service contract tests FAIL: {exc}")
        sys.exit(1)
