#!/usr/bin/env python3
"""AuditX CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Dict, Iterable, List, Optional, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

DEV_SCRIPT_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "scripts", "dev"))
if DEV_SCRIPT_DIR not in sys.path:
    sys.path.insert(0, DEV_SCRIPT_DIR)

from analyzers import ANALYZERS
from cache_engine import AuditXCache, build_cache_context, changed_paths_from_state
from canonicalize import canonicalize_json_payload
from env_tools_lib import (
    WORKSPACE_ID_ENV_KEY,
    canonical_workspace_id,
    canonicalize_env_for_workspace,
    detect_repo_root,
)
from graph import build_analysis_graph
from model.serialization import compute_fingerprint, finding_to_dict, sort_findings
from output import write_reports


ANALYZER_API_VERSION = "2.0.0"


def _repo_root(path):
    if path:
        return os.path.abspath(path)
    return detect_repo_root(os.getcwd(), __file__)


def _canonicalize_env(repo_root: str) -> Tuple[str, Dict[str, str]]:
    ws_id = os.environ.get(WORKSPACE_ID_ENV_KEY, "").strip() or canonical_workspace_id(repo_root, env=os.environ)
    env, _ = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=ws_id)
    os.environ.update(env)
    return ws_id, env


def _normalize_paths(paths: Iterable[str]) -> List[str]:
    return sorted({str(item).replace("\\", "/").strip() for item in paths if str(item).strip()})


def _collect_changed_paths(repo_root: str):
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
        paths.extend(line.strip() for line in (proc.stdout or "").splitlines() if line.strip())
    return _normalize_paths(paths), None


def _normalize_finding_record(record: Dict[str, object]) -> Dict[str, object]:
    item = dict(record)
    item.pop("finding_id", None)
    item.pop("fingerprint", None)
    item.pop("created_utc", None)
    item["analyzer_id"] = str(item.get("analyzer_id", "")).strip()
    item["category"] = str(item.get("category", "general")).strip() or "general"
    item["severity"] = str(item.get("severity", "INFO")).strip() or "INFO"
    item["status"] = str(item.get("status", "OPEN")).strip() or "OPEN"
    try:
        item["confidence"] = float(item.get("confidence", 0.0))
    except (TypeError, ValueError):
        item["confidence"] = 0.0
    location = item.get("location")
    if not isinstance(location, dict):
        location = {"file": ""}
    location = {
        "file": str(location.get("file", "")).replace("\\", "/"),
        "line": int(location.get("line", 0) or 0),
        "end_line": int(location.get("end_line", 0) or 0),
    }
    if not location["line"]:
        location.pop("line", None)
    if not location["end_line"]:
        location.pop("end_line", None)
    item["location"] = location
    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        evidence = []
    item["evidence"] = [str(entry).strip() for entry in evidence if str(entry).strip()]
    item["suggested_classification"] = str(item.get("suggested_classification", "TODO-BLOCKED")).strip() or "TODO-BLOCKED"
    item["recommended_action"] = str(item.get("recommended_action", "DOC_FIX")).strip() or "DOC_FIX"
    item["related_invariants"] = sorted({str(entry).strip() for entry in item.get("related_invariants", []) if str(entry).strip()})
    item["related_paths"] = sorted({str(entry).replace("\\", "/").strip() for entry in item.get("related_paths", []) if str(entry).strip()})
    return item


def _finding_obj_to_raw(finding_obj) -> Dict[str, object]:
    if isinstance(finding_obj, dict):
        return _normalize_finding_record(finding_obj)
    return _normalize_finding_record(finding_to_dict(finding_obj))


def _finalize_findings(raw_finding_records: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    records = [_normalize_finding_record(item) for item in raw_finding_records]
    records = sort_findings(records)
    counters: Dict[str, int] = {}
    out: List[Dict[str, object]] = []
    for item in records:
        analyzer_id = item.get("analyzer_id", "A0")
        counters[analyzer_id] = counters.get(analyzer_id, 0) + 1
        finalized = dict(item)
        finalized["finding_id"] = "{}:{:04d}".format(analyzer_id, counters[analyzer_id])
        finalized["fingerprint"] = compute_fingerprint(finalized)
        out.append(canonicalize_json_payload(finalized))
    return out


def _module_id(module) -> str:
    analyzer_id = getattr(module, "ANALYZER_ID", "")
    if analyzer_id:
        return str(analyzer_id)
    return str(module.__name__)


def _module_watch_prefixes(module) -> Tuple[str, ...]:
    prefixes = getattr(module, "WATCH_PREFIXES", None)
    if not isinstance(prefixes, (list, tuple)):
        return ("*",)
    cleaned = [str(item).replace("\\", "/").strip() for item in prefixes if str(item).strip()]
    return tuple(cleaned or ["*"])


def _is_analyzer_affected(changed_paths: List[str], watch_prefixes: Tuple[str, ...]) -> bool:
    if not changed_paths:
        return False
    if "*" in watch_prefixes:
        return True
    for rel in changed_paths:
        rel_norm = rel.replace("\\", "/")
        for prefix in watch_prefixes:
            if rel_norm.startswith(prefix):
                return True
    return False


def _load_previous_findings_by_analyzer(entry_payload) -> Dict[str, List[Dict[str, object]]]:
    if not isinstance(entry_payload, dict):
        return {}
    by_analyzer = entry_payload.get("analyzer_findings")
    if not isinstance(by_analyzer, dict):
        return {}
    out: Dict[str, List[Dict[str, object]]] = {}
    for analyzer_id, rows in sorted(by_analyzer.items()):
        if not isinstance(rows, list):
            continue
        out[str(analyzer_id)] = [_normalize_finding_record(row) for row in rows if isinstance(row, dict)]
    return out


def _run_incremental_analyzers(
    graph,
    repo_root: str,
    changed_files: Optional[List[str]],
    changed_paths_since_last: List[str],
    previous_by_analyzer: Dict[str, List[Dict[str, object]]],
):
    analyzer_findings: Dict[str, List[Dict[str, object]]] = {}
    recomputed: List[str] = []
    reused: List[str] = []
    for module in ANALYZERS:
        analyzer_id = _module_id(module)
        watch_prefixes = _module_watch_prefixes(module)
        should_recompute = analyzer_id not in previous_by_analyzer or _is_analyzer_affected(changed_paths_since_last, watch_prefixes)
        if should_recompute:
            raw_rows = module.run(graph, repo_root, changed_files=changed_files)
            analyzer_findings[analyzer_id] = [_finding_obj_to_raw(item) for item in raw_rows]
            recomputed.append(analyzer_id)
        else:
            analyzer_findings[analyzer_id] = [_normalize_finding_record(item) for item in previous_by_analyzer[analyzer_id]]
            reused.append(analyzer_id)
    return analyzer_findings, sorted(recomputed), sorted(reused)


def _flatten_analyzer_findings(by_analyzer: Dict[str, List[Dict[str, object]]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for analyzer_id in sorted(by_analyzer.keys()):
        rows = by_analyzer.get(analyzer_id) or []
        out.extend(rows)
    return out


def _scan_config(args) -> Dict[str, object]:
    return {
        "analyzer_api_version": ANALYZER_API_VERSION,
        "changed_only": bool(args.changed_only),
        "format": str(args.format),
    }


def _run_scan(args):
    root = _repo_root(args.repo_root)
    ws_id, _ = _canonicalize_env(root)
    changed_paths = None
    if args.changed_only:
        changed_paths, refusal = _collect_changed_paths(root)
        if refusal is not None:
            return refusal, 2

    cache = AuditXCache(root, ws_id)
    scan_scope = changed_paths or []
    cache_ctx = build_cache_context(
        repo_root=root,
        changed_only=bool(args.changed_only),
        scan_scope_paths=scan_scope,
        config_payload=_scan_config(args),
    )
    state = cache.load_state()
    changed_since_state = changed_paths_from_state(state, cache_ctx["file_hashes"])

    cache_entry = cache.load_entry(cache_ctx["cache_key"])
    if cache_entry and isinstance(cache_entry.get("findings"), list):
        findings = [_normalize_finding_record(item) for item in cache_entry.get("findings", []) if isinstance(item, dict)]
        findings = _finalize_findings(findings)
        graph_hash = str(cache_entry.get("graph_hash", ""))
        output_info = write_reports(
            repo_root=root,
            findings=findings,
            graph_hash=graph_hash,
            changed_only=bool(args.changed_only),
            output_format=args.format,
            scan_result="scan_complete",
            run_meta={
                "cache_mode": "full_reuse",
                "workspace_id": ws_id,
            },
            cache=cache,
        )
        cache.save_state(
            {
                "last_cache_key": cache_ctx["cache_key"],
                "file_hashes": cache_ctx["file_hashes"],
            }
        )
        payload = {
            "result": "scan_complete",
            "repo_root": root,
            "changed_only": bool(args.changed_only),
            "format": args.format,
            "graph": {
                "node_count": int(cache_entry.get("graph_node_count", 0)),
                "edge_count": int(cache_entry.get("graph_edge_count", 0)),
                "graph_hash": graph_hash,
            },
            "findings_count": len(findings),
            "cache": {
                "cache_hit": True,
                "cache_mode": "full_reuse",
                "workspace_id": ws_id,
            },
            "outputs": output_info,
        }
        return payload, 0

    graph = build_analysis_graph(root, changed_only_paths=changed_paths)
    previous_entry = cache.load_entry(str(state.get("last_cache_key", "")))
    previous_by_analyzer = _load_previous_findings_by_analyzer(previous_entry)
    analyzer_findings, recomputed, reused = _run_incremental_analyzers(
        graph=graph,
        repo_root=root,
        changed_files=changed_paths,
        changed_paths_since_last=changed_since_state,
        previous_by_analyzer=previous_by_analyzer,
    )
    findings = _finalize_findings(_flatten_analyzer_findings(analyzer_findings))
    graph_hash = graph.stable_hash()
    cache_mode = "incremental" if reused else "full_scan"
    output_info = write_reports(
        repo_root=root,
        findings=findings,
        graph_hash=graph_hash,
        changed_only=bool(args.changed_only),
        output_format=args.format,
        scan_result="scan_complete",
        run_meta={
            "cache_mode": cache_mode,
            "workspace_id": ws_id,
            "recomputed_analyzers": recomputed,
            "reused_analyzers": reused,
            "changed_paths_since_last": len(changed_since_state),
        },
        cache=cache,
    )
    cache.save_entry(
        cache_ctx["cache_key"],
        {
            "cache_key": cache_ctx["cache_key"],
            "graph_hash": graph_hash,
            "graph_node_count": len(graph.nodes),
            "graph_edge_count": len(graph.edges),
            "findings": findings,
            "analyzer_findings": analyzer_findings,
        },
    )
    cache.save_state(
        {
            "last_cache_key": cache_ctx["cache_key"],
            "file_hashes": cache_ctx["file_hashes"],
        }
    )
    payload = {
        "result": "scan_complete",
        "repo_root": root,
        "changed_only": bool(args.changed_only),
        "format": args.format,
        "graph": {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "graph_hash": graph_hash,
        },
        "findings_count": len(findings),
        "cache": {
            "cache_hit": False,
            "cache_mode": cache_mode,
            "workspace_id": ws_id,
            "recomputed_analyzers": recomputed,
            "reused_analyzers": reused,
        },
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
            "- Cache Mode: `{}`".format(payload.get("cache", {}).get("cache_mode", "")),
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
