#!/usr/bin/env python3
"""AuditX CLI entrypoint."""

import argparse
import json
import os
import shutil
import subprocess
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from analyzers import run_analyzers
from graph import build_analysis_graph
from model.serialization import compute_fingerprint, finding_to_dict, sort_findings
from output import write_reports


def _repo_root(path):
    if path:
        return os.path.abspath(path)
    return os.path.abspath(os.getcwd())


def _created_utc():
    return os.environ.get("AUDITX_CREATED_UTC", "1970-01-01T00:00:00Z")


def _normalize_paths(paths):
    return sorted({item.replace("\\", "/").strip() for item in paths if item and item.strip()})


def _collect_changed_paths(repo_root):
    git_exe = shutil.which("git")
    if not git_exe:
        return None, {
            "result": "refused",
            "refusal_code": "refuse.git_unavailable",
            "reason": "Git executable not found for --changed-only scan.",
        }

    commands = (
        [git_exe, "-C", repo_root, "diff", "--name-only", "--relative", "HEAD"],
        [git_exe, "-C", repo_root, "ls-files", "--others", "--exclude-standard"],
    )
    paths = []
    for command in commands:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            return None, {
                "result": "refused",
                "refusal_code": "refuse.git_unavailable",
                "reason": "Git command failed for --changed-only scan.",
                "command": " ".join(command),
                "stderr": (proc.stderr or "").strip(),
            }
        lines = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
        paths.extend(lines)

    return _normalize_paths(paths), None


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


def _run_scan(args):
    root = _repo_root(args.repo_root)
    changed_paths = None
    if args.changed_only:
        changed_paths, refusal = _collect_changed_paths(root)
        if refusal is not None:
            return refusal, 2

    graph = build_analysis_graph(root, changed_only_paths=changed_paths)
    findings = _finalize_findings(run_analyzers(graph, root, changed_files=changed_paths))
    output_info = write_reports(
        repo_root=root,
        findings=findings,
        graph_hash=graph.stable_hash(),
        changed_only=bool(args.changed_only),
        output_format=args.format,
        scan_result="scan_complete",
    )
    payload = {
        "result": "scan_complete",
        "repo_root": root,
        "changed_only": bool(args.changed_only),
        "format": args.format,
        "graph": {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "graph_hash": graph.stable_hash(),
        },
        "findings_count": len(findings),
        "outputs": output_info,
    }
    return payload, 0


def _print_scan_payload(payload, output_format):
    if output_format == "md":
        lines = [
            "# AuditX Scan",
            "",
            "- Result: `{}`".format(payload.get("result", "")),
            "- Repo Root: `{}`".format(payload.get("repo_root", "")),
            "- Changed Only: `{}`".format(payload.get("changed_only", False)),
            "- Findings: `{}`".format(payload.get("findings_count", 0)),
            "- Output Dir: `{}`".format(payload.get("outputs", {}).get("output_dir", "")),
        ]
        print("\n".join(lines))
        return
    print(json.dumps(payload, indent=2, sort_keys=True))


def _cmd_scan(args):
    payload, code = _run_scan(args)
    _print_scan_payload(payload, args.format)
    return code


def _cmd_verify(args):
    payload, code = _run_scan(args)
    _print_scan_payload(payload, args.format)
    if code == 0:
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

