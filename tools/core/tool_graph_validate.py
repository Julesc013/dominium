#!/usr/bin/env python3
"""Validate NetworkGraph and optional partition artifacts deterministically."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.core.graph.network_graph_engine import NetworkGraphError, normalize_network_graph  # noqa: E402
from src.core.graph.routing_engine import RoutingError, normalize_graph_partition_row  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _extract_graph_payload(payload: dict) -> dict:
    if str(payload.get("graph_id", "")).strip():
        return dict(payload)
    for key in ("graph", "network_graph"):
        row = payload.get(key)
        if isinstance(row, dict) and str(row.get("graph_id", "")).strip():
            return dict(row)
    return {}


def run_validate(args: argparse.Namespace) -> dict:
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    graph_abs = os.path.join(repo_root, str(args.graph_file).replace("/", os.sep))
    graph_payload_raw = _read_json(graph_abs)
    graph_payload = _extract_graph_payload(graph_payload_raw)
    if not graph_payload:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.graph.validate.graph_missing",
                    "message": "graph file is missing or does not contain a network_graph payload",
                    "path": "$.graph_file",
                }
            ],
        }

    if str(args.validation_mode).strip():
        graph_payload["validation_mode"] = str(args.validation_mode).strip()

    try:
        normalized_graph = normalize_network_graph(graph_payload)
    except NetworkGraphError as exc:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": str(exc.reason_code),
                    "message": str(exc),
                    "path": "$.graph",
                    "details": dict(exc.details),
                }
            ],
        }

    schema_versions = dict(normalized_graph.get("payload_schema_versions") or {})
    node_schema_id = str(normalized_graph.get("node_type_schema_id", "")).strip()
    edge_schema_id = str(normalized_graph.get("edge_type_schema_id", "")).strip()
    missing_schema_ids = [
        schema_id
        for schema_id in (node_schema_id, edge_schema_id)
        if schema_id and schema_id not in schema_versions
    ]
    if missing_schema_ids:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.graph.validate.payload_schema_missing",
                    "message": "graph payload schema ids are not declared in payload_schema_versions",
                    "path": "$.payload_schema_versions",
                    "details": {"missing_schema_ids": list(missing_schema_ids)},
                }
            ],
        }

    partition_out = {}
    if str(args.partition_file).strip():
        partition_abs = os.path.join(repo_root, str(args.partition_file).replace("/", os.sep))
        partition_raw = _read_json(partition_abs)
        if not partition_raw:
            return {
                "result": "refused",
                "errors": [
                    {
                        "code": "refusal.graph.validate.partition_missing",
                        "message": "partition file is missing or invalid JSON object",
                        "path": "$.partition_file",
                    }
                ],
            }
        try:
            partition_out = normalize_graph_partition_row(partition_raw, graph_row=normalized_graph)
        except RoutingError as exc:
            return {
                "result": "refused",
                "errors": [
                    {
                        "code": str(exc.reason_code),
                        "message": str(exc),
                        "path": "$.partition",
                        "details": dict(exc.details),
                    }
                ],
            }

    graph_hash = canonical_sha256(normalized_graph)
    out = {
        "result": "complete",
        "tool_id": "tool.core.tool_graph_validate",
        "graph_id": str(normalized_graph.get("graph_id", "")),
        "graph_hash": graph_hash,
        "validation_mode": str(normalized_graph.get("validation_mode", "strict")),
        "node_count": len(list(normalized_graph.get("nodes") or [])),
        "edge_count": len(list(normalized_graph.get("edges") or [])),
        "payload_schema_versions": dict(schema_versions),
    }
    if partition_out:
        out["partition"] = {
            "partition_id": str(partition_out.get("partition_id", "")),
            "graph_id": str(partition_out.get("graph_id", "")),
            "cross_shard_boundary_count": len(list(partition_out.get("cross_shard_boundary_nodes") or [])),
            "deterministic_fingerprint": canonical_sha256(partition_out),
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate deterministic NetworkGraph and partition payloads.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--graph-file", required=True)
    parser.add_argument("--partition-file", default="")
    parser.add_argument("--validation-mode", default="")
    args = parser.parse_args()
    result = run_validate(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
