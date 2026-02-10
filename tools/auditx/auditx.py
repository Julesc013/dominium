#!/usr/bin/env python3
"""AuditX CLI entrypoint."""

import argparse
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from analyzers import run_analyzers
from graph import build_analysis_graph
from model.serialization import compute_fingerprint, finding_to_dict, sort_findings


def _repo_root(path):
    if path:
        return os.path.abspath(path)
    return os.path.abspath(os.getcwd())


def _created_utc():
    return os.environ.get("AUDITX_CREATED_UTC", "1970-01-01T00:00:00Z")


def _finalize_findings(finding_objects):
    records = []
    for finding in finding_objects:
        finding.created_utc = _created_utc()
        records.append(finding_to_dict(finding))
    records = sort_findings(records)
    counters = {}
    for item in records:
        analyzer_id = item.get("analyzer_id", "A0")
        counters[analyzer_id] = counters.get(analyzer_id, 0) + 1
        item["finding_id"] = "{}:{:04d}".format(analyzer_id, counters[analyzer_id])
        item["fingerprint"] = compute_fingerprint(item)
    return records


def _cmd_scan(args):
    root = _repo_root(args.repo_root)
    graph = build_analysis_graph(root)
    findings = _finalize_findings(run_analyzers(graph, root))
    payload = {
        "result": "scan_partial_ready",
        "reason_code": "refuse.not_fully_implemented",
        "repo_root": root,
        "changed_only": bool(args.changed_only),
        "format": args.format,
        "graph": {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "graph_hash": graph.stable_hash(),
        },
        "findings_count": len(findings),
        "findings_preview": findings[: min(len(findings), 20)],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _cmd_verify(args):
    result = _cmd_scan(args)
    if result == 0:
        return 0
    return 1


def _cmd_enforce(_args):
    payload = {
        "result": "refused",
        "refusal_code": "refuse.not_enabled",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="AuditX semantic audit CLI.")

    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Run semantic scan.")
    scan.add_argument("--repo-root", default=".", help="Repository root path.")
    scan.add_argument("--changed-only", action="store_true", help="Limit to changed files.")
    scan.add_argument(
        "--format",
        choices=("json", "md", "both"),
        default="both",
        help="Report output format.",
    )
    scan.set_defaults(func=_cmd_scan)

    verify = sub.add_parser("verify", help="Run scan in non-gating verify mode.")
    verify.add_argument("--repo-root", default=".", help="Repository root path.")
    verify.add_argument("--changed-only", action="store_true", help="Limit to changed files.")
    verify.add_argument(
        "--format",
        choices=("json", "md", "both"),
        default="both",
        help="Report output format.",
    )
    verify.set_defaults(func=_cmd_verify)

    enforce = sub.add_parser("enforce", help="Reserved enforcement entrypoint.")
    enforce.add_argument("--repo-root", default=".", help="Repository root path.")
    enforce.set_defaults(func=_cmd_enforce)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
