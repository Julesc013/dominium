#!/usr/bin/env python3
"""Deterministic developer acceleration CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.dev.impact_graph import (  # noqa: E402
    build_graph_and_write,
    compute_impacted_sets,
    detect_changed_files,
)


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _resolve_changed(repo_root: str, changed_files: str, base_ref: str):
    if str(changed_files).strip():
        out = sorted(set(token.strip().replace("\\", "/") for token in changed_files.split(",") if token.strip()))
        return {"result": "complete", "changed_files": out}
    return detect_changed_files(repo_root=repo_root, base_ref=base_ref)


def _print(payload: Dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _cmd_impact_graph(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    changed = _resolve_changed(repo_root=repo_root, changed_files=args.changed_files, base_ref=args.base_ref)
    if changed.get("result") != "complete":
        _print(changed)
        return 2
    built = build_graph_and_write(
        repo_root=repo_root,
        changed_files=list(changed.get("changed_files") or []),
        out_path=str(args.out),
    )
    payload = {
        "result": "complete",
        "graph_path": built.get("graph_path"),
        "graph_hash": built.get("graph_hash"),
        "node_count": built.get("node_count"),
        "edge_count": built.get("edge_count"),
        "changed_files": list(changed.get("changed_files") or []),
    }
    _print(payload)
    return 0


def _impacted(repo_root: str, changed_files: List[str], out_path: str) -> Dict[str, object]:
    built = build_graph_and_write(repo_root=repo_root, changed_files=changed_files, out_path=out_path)
    payload = dict(built.get("payload") or {})
    impacted = compute_impacted_sets(graph_payload=payload, changed_files=changed_files)
    return {
        "result": "complete",
        "graph_path": built.get("graph_path"),
        "graph_hash": built.get("graph_hash"),
        "node_count": built.get("node_count"),
        "edge_count": built.get("edge_count"),
        "changed_files": changed_files,
        "impacted": impacted,
    }


def _cmd_impacted_tests(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    changed = _resolve_changed(repo_root=repo_root, changed_files=args.changed_files, base_ref=args.base_ref)
    if changed.get("result") != "complete":
        _print(changed)
        return 2
    payload = _impacted(
        repo_root=repo_root,
        changed_files=list(changed.get("changed_files") or []),
        out_path=str(args.out),
    )
    _print(
        {
            "result": "complete",
            "graph_path": payload.get("graph_path"),
            "changed_files": payload.get("changed_files"),
            "impacted_test_ids": ((payload.get("impacted") or {}).get("impacted_test_ids") or []),
            "complete_coverage": bool(((payload.get("impacted") or {}).get("complete_coverage", False))),
            "missing_changed_files": ((payload.get("impacted") or {}).get("missing_changed_files") or []),
        }
    )
    return 0


def _cmd_impacted_build_targets(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    changed = _resolve_changed(repo_root=repo_root, changed_files=args.changed_files, base_ref=args.base_ref)
    if changed.get("result") != "complete":
        _print(changed)
        return 2
    payload = _impacted(
        repo_root=repo_root,
        changed_files=list(changed.get("changed_files") or []),
        out_path=str(args.out),
    )
    _print(
        {
            "result": "complete",
            "graph_path": payload.get("graph_path"),
            "changed_files": payload.get("changed_files"),
            "impacted_build_targets": ((payload.get("impacted") or {}).get("impacted_build_targets") or []),
            "complete_coverage": bool(((payload.get("impacted") or {}).get("complete_coverage", False))),
            "missing_changed_files": ((payload.get("impacted") or {}).get("missing_changed_files") or []),
        }
    )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Developer acceleration command wrapper.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    for command in ("impact-graph", "impacted-tests", "impacted-build-targets"):
        node = sub.add_parser(command)
        node.add_argument("--base-ref", default="origin/main")
        node.add_argument("--changed-files", default="", help="comma-separated changed file list override")
        node.add_argument("--out", default="build/impact_graph.json")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "impact-graph":
        return _cmd_impact_graph(args)
    if args.command == "impacted-tests":
        return _cmd_impacted_tests(args)
    if args.command == "impacted-build-targets":
        return _cmd_impacted_build_targets(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
