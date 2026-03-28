#!/usr/bin/env python3
"""Run deterministic NetworkGraph route queries for debugging and migration checks."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from core.graph.network_graph_engine import normalize_network_graph  # noqa: E402
from core.graph.routing_engine import (  # noqa: E402
    RoutingError,
    normalize_route_query_row,
    query_route_result,
)


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


def _routing_policy_from_registry(repo_root: str, policy_id: str) -> dict:
    registry = _read_json(os.path.join(repo_root, "data", "registries", "core_routing_policy_registry.json"))
    record = dict(registry.get("record") or {})
    rows = list(record.get("routing_policies") or registry.get("routing_policies") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {}


def _constraints_payload(args: argparse.Namespace, repo_root: str) -> dict:
    if str(args.constraints_file).strip():
        return dict(_read_json(os.path.join(repo_root, str(args.constraints_file).replace("/", os.sep))))
    if str(args.constraints_json).strip():
        try:
            payload = json.loads(str(args.constraints_json))
        except ValueError:
            return {}
        return dict(payload) if isinstance(payload, dict) else {}
    return {}


def run_route_query(args: argparse.Namespace) -> dict:
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    graph_payload_raw = _read_json(os.path.join(repo_root, str(args.graph_file).replace("/", os.sep)))
    graph_payload = _extract_graph_payload(graph_payload_raw)
    if not graph_payload:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.route_query.graph_missing",
                    "message": "graph file is missing or does not contain a network_graph payload",
                    "path": "$.graph_file",
                }
            ],
        }
    graph_payload = normalize_network_graph(graph_payload)
    policy_row = {}
    if str(args.policy_file).strip():
        policy_row = dict(_read_json(os.path.join(repo_root, str(args.policy_file).replace("/", os.sep))))
    if not policy_row:
        policy_row = _routing_policy_from_registry(repo_root, str(args.route_policy_id).strip())
    if not policy_row:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.route_query.policy_missing",
                    "message": "routing policy could not be resolved",
                    "path": "$.route_policy_id",
                }
            ],
        }
    query_row = normalize_route_query_row(
        {
            "schema_version": "1.0.0",
            "graph_id": str(graph_payload.get("graph_id", "")),
            "from_node_id": str(args.from_node_id).strip(),
            "to_node_id": str(args.to_node_id).strip(),
            "route_policy_id": str(policy_row.get("policy_id", "")),
            "constraints": _constraints_payload(args, repo_root),
            "extensions": {},
        }
    )
    partition_row = {}
    if str(args.partition_file).strip():
        partition_row = _read_json(os.path.join(repo_root, str(args.partition_file).replace("/", os.sep)))
    cache_state = {"entries_by_key": {}, "next_sequence": 0}
    try:
        first = query_route_result(
            graph_row=graph_payload,
            routing_policy_row=policy_row,
            from_node_id=str(query_row.get("from_node_id", "")),
            to_node_id=str(query_row.get("to_node_id", "")),
            constraints_row=dict(query_row.get("constraints") or {}),
            partition_row=partition_row if partition_row else None,
            cache_state=dict(cache_state),
            max_cache_entries=max(0, int(args.max_cache_entries)),
            cost_units_per_query=max(1, int(args.cost_units_per_query)),
        )
    except RoutingError as exc:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": str(exc.reason_code),
                    "message": str(exc),
                    "path": "$.route_query",
                    "details": dict(exc.details),
                }
            ],
        }

    repeat = None
    if str(args.cache).strip().lower() != "off":
        repeat = query_route_result(
            graph_row=graph_payload,
            routing_policy_row=policy_row,
            from_node_id=str(query_row.get("from_node_id", "")),
            to_node_id=str(query_row.get("to_node_id", "")),
            constraints_row=dict(query_row.get("constraints") or {}),
            partition_row=partition_row if partition_row else None,
            cache_state=dict(first.get("cache_state") or {}),
            max_cache_entries=max(0, int(args.max_cache_entries)),
            cost_units_per_query=max(1, int(args.cost_units_per_query)),
        )

    return {
        "result": "complete",
        "tool_id": "tool.core.tool_route_query",
        "query": dict(query_row),
        "first": dict(first),
        "second": dict(repeat or {}),
        "cache_reused": bool(repeat and bool(repeat.get("cache_hit", False))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic NetworkGraph route queries.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--graph-file", required=True)
    parser.add_argument("--from-node-id", required=True)
    parser.add_argument("--to-node-id", required=True)
    parser.add_argument("--route-policy-id", default="route.shortest_delay")
    parser.add_argument("--policy-file", default="")
    parser.add_argument("--constraints-file", default="")
    parser.add_argument("--constraints-json", default="")
    parser.add_argument("--partition-file", default="")
    parser.add_argument("--cache", choices=("on", "off"), default="on")
    parser.add_argument("--max-cache-entries", type=int, default=64)
    parser.add_argument("--cost-units-per-query", type=int, default=1)
    args = parser.parse_args()
    result = run_route_query(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
