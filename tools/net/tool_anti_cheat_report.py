#!/usr/bin/env python3
"""Generate deterministic anti-cheat proof summaries for administrators."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, read_json_object, write_canonical_json


def _repo_root(raw: str) -> str:
    token = str(raw).strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def _load_json(abs_path: str) -> Tuple[dict, str]:
    payload, err = read_json_object(abs_path)
    if err:
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sort_events(rows: List[dict]) -> List[dict]:
    return sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=lambda row: (
            _as_int(row.get("tick", 0), 0),
            str(row.get("peer_id", "")),
            str(row.get("module_id", "")),
            str(row.get("event_id", "")),
        ),
    )


def _sort_actions(rows: List[dict]) -> List[dict]:
    return sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=lambda row: (
            _as_int(row.get("tick", 0), 0),
            str(row.get("peer_id", "")),
            str(row.get("module_id", "")),
            str(row.get("action", "")),
            str(row.get("action_id", "")),
        ),
    )


def _sort_refusals(rows: List[dict]) -> List[dict]:
    return sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=lambda row: (
            _as_int(row.get("tick", 0), 0),
            str(row.get("peer_id", "")),
            str(row.get("module_id", "")),
            str(row.get("reason_code", "")),
            str(row.get("action", "")),
        ),
    )


def _sort_anchor_mismatches(rows: List[dict]) -> List[dict]:
    return sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=lambda row: (
            _as_int(row.get("tick", 0), 0),
            str(row.get("peer_id", "")),
            str(row.get("expected_hash", "")),
            str(row.get("actual_hash", "")),
        ),
    )


def _latest_file(abs_dir: str, prefix: str) -> str:
    if not os.path.isdir(abs_dir):
        return ""
    matches = []
    for name in sorted(os.listdir(abs_dir)):
        if not str(name).startswith(prefix):
            continue
        if not str(name).lower().endswith(".json"):
            continue
        matches.append(os.path.join(abs_dir, name))
    return sorted(matches)[-1] if matches else ""


def _from_runtime_payload(runtime_payload: dict) -> dict:
    server = dict(runtime_payload.get("server") or {})
    anti = dict(runtime_payload.get("anti_cheat") or {})
    lock_payload = dict(runtime_payload.get("lock_payload") or {})
    registry_hashes = dict(server.get("registry_hashes") or {})
    pack_lock_hash = str(server.get("pack_lock_hash", "")) or str(lock_payload.get("pack_lock_hash", ""))
    return {
        "policy_id": str(anti.get("policy_id", "")),
        "pack_lock_hash": str(pack_lock_hash),
        "registry_hashes": dict((key, registry_hashes[key]) for key in sorted(registry_hashes.keys())),
        "bii": str(lock_payload.get("compatibility_version", "")),
        "events": _sort_events(list(server.get("anti_cheat_events") or [])),
        "actions": _sort_actions(list(server.get("anti_cheat_enforcement_actions") or [])),
        "refusal_injections": _sort_refusals(list(server.get("anti_cheat_refusal_injections") or [])),
        "anchor_mismatches": _sort_anchor_mismatches(list(server.get("anti_cheat_anchor_mismatches") or [])),
        "terminated_peers": sorted(set(str(item).strip() for item in (server.get("terminated_peers") or []) if str(item).strip())),
    }


def _load_from_run_meta_dir(abs_dir: str) -> Tuple[dict, str]:
    events_path = _latest_file(abs_dir, "anti_cheat.events.")
    actions_path = _latest_file(abs_dir, "anti_cheat.actions.")
    refusals_path = _latest_file(abs_dir, "anti_cheat.refusal_injections.")
    mismatches_path = _latest_file(abs_dir, "anti_cheat.anchor_mismatches.")
    if not events_path:
        return {}, "anti-cheat event artifact missing"

    events_payload, events_err = _load_json(events_path)
    if events_err:
        return {}, "invalid events artifact"
    actions_payload, _ = _load_json(actions_path) if actions_path else ({}, "")
    refusals_payload, _ = _load_json(refusals_path) if refusals_path else ({}, "")
    mismatches_payload, _ = _load_json(mismatches_path) if mismatches_path else ({}, "")

    return {
        "policy_id": str(events_payload.get("policy_id", "")),
        "pack_lock_hash": str(events_payload.get("pack_lock_hash", "")),
        "registry_hashes": dict(events_payload.get("registry_hashes") or {}),
        "bii": str(events_payload.get("bii", "")),
        "events": _sort_events(list(events_payload.get("rows") or [])),
        "actions": _sort_actions(list(actions_payload.get("rows") or [])),
        "refusal_injections": _sort_refusals(list(refusals_payload.get("rows") or [])),
        "anchor_mismatches": _sort_anchor_mismatches(list(mismatches_payload.get("rows") or [])),
        "terminated_peers": sorted(
            set(
                str((row or {}).get("peer_id", "")).strip()
                for row in list(refusals_payload.get("rows") or [])
                if str((row or {}).get("action", "")).strip() == "terminate"
            )
        ),
    }, ""


def _count_map(rows: List[dict], key: str) -> dict:
    counts: Dict[str, int] = {}
    for row in rows:
        token = str((row or {}).get(key, "")).strip() or "<empty>"
        counts[token] = _as_int(counts.get(token, 0), 0) + 1
    return dict((name, counts[name]) for name in sorted(counts.keys()))


def _markdown(summary: dict) -> str:
    counts = dict(summary.get("counts") or {})
    severity_counts = dict(summary.get("severity_counts") or {})
    module_counts = dict(summary.get("module_counts") or {})
    action_counts = dict(summary.get("action_counts") or {})
    lines = [
        "# Anti-Cheat Report",
        "",
        "- Status: `DERIVED`",
        "- Policy: `{}`".format(str(summary.get("policy_id", ""))),
        "- Pack Lock Hash: `{}`".format(str(summary.get("pack_lock_hash", ""))),
        "- Events: `{}`".format(int(counts.get("events", 0))),
        "- Enforcement Actions: `{}`".format(int(counts.get("actions", 0))),
        "- Refusal Injections: `{}`".format(int(counts.get("refusal_injections", 0))),
        "- Anchor Mismatches: `{}`".format(int(counts.get("anchor_mismatches", 0))),
        "- Terminated Peers: `{}`".format(", ".join(list(summary.get("terminated_peers") or [])) or "<none>"),
        "",
        "## Severity Counts",
    ]
    for key in sorted(severity_counts.keys()):
        lines.append("- `{}`: `{}`".format(str(key), int(severity_counts.get(key, 0))))
    lines.append("")
    lines.append("## Module Counts")
    for key in sorted(module_counts.keys()):
        lines.append("- `{}`: `{}`".format(str(key), int(module_counts.get(key, 0))))
    lines.append("")
    lines.append("## Action Counts")
    for key in sorted(action_counts.keys()):
        lines.append("- `{}`: `{}`".format(str(key), int(action_counts.get(key, 0))))
    lines.append("")
    lines.append("## Deterministic Hashes")
    lines.append("- `events_hash`: `{}`".format(str(summary.get("events_hash", ""))))
    lines.append("- `actions_hash`: `{}`".format(str(summary.get("actions_hash", ""))))
    lines.append("- `proof_hash`: `{}`".format(str(summary.get("proof_hash", ""))))
    return "\n".join(lines) + "\n"


def build_summary(payload: dict) -> dict:
    events = _sort_events(list(payload.get("events") or []))
    actions = _sort_actions(list(payload.get("actions") or []))
    refusals = _sort_refusals(list(payload.get("refusal_injections") or []))
    mismatches = _sort_anchor_mismatches(list(payload.get("anchor_mismatches") or []))
    summary = {
        "schema_version": "1.0.0",
        "policy_id": str(payload.get("policy_id", "")),
        "pack_lock_hash": str(payload.get("pack_lock_hash", "")),
        "registry_hashes": dict((key, payload.get("registry_hashes", {}).get(key)) for key in sorted(dict(payload.get("registry_hashes") or {}).keys())),
        "bii": str(payload.get("bii", "")),
        "counts": {
            "events": int(len(events)),
            "actions": int(len(actions)),
            "refusal_injections": int(len(refusals)),
            "anchor_mismatches": int(len(mismatches)),
        },
        "severity_counts": _count_map(events, "severity"),
        "module_counts": _count_map(events, "module_id"),
        "action_counts": _count_map(actions, "action"),
        "terminated_peers": sorted(set(str(item).strip() for item in (payload.get("terminated_peers") or []) if str(item).strip())),
        "events_hash": canonical_sha256(events),
        "actions_hash": canonical_sha256(actions),
        "refusal_injections_hash": canonical_sha256(refusals),
        "anchor_mismatches_hash": canonical_sha256(mismatches),
        "proof_hash": canonical_sha256(
            {
                "events_hash": canonical_sha256(events),
                "actions_hash": canonical_sha256(actions),
                "refusal_injections_hash": canonical_sha256(refusals),
                "anchor_mismatches_hash": canonical_sha256(mismatches),
            }
        ),
        "extensions": {},
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic anti-cheat JSON/Markdown admin report.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--runtime-json", default="", help="Runtime JSON path containing anti-cheat server logs.")
    parser.add_argument("--run-meta-dir", default="", help="Directory containing anti_cheat.*.json artifacts.")
    parser.add_argument("--out-dir", default="build/net/reports")
    parser.add_argument("--out-prefix", default="anti_cheat_report")
    args = parser.parse_args()

    repo_root = _repo_root(str(args.repo_root))
    runtime_path = str(args.runtime_json).strip()
    run_meta_dir = str(args.run_meta_dir).strip()

    payload = {}
    err = ""
    if runtime_path:
        runtime_abs = os.path.normpath(os.path.abspath(runtime_path))
        runtime_payload, runtime_err = _load_json(runtime_abs)
        if runtime_err:
            err = "runtime json is invalid"
        else:
            payload = _from_runtime_payload(runtime_payload)
    elif run_meta_dir:
        run_meta_abs = os.path.normpath(os.path.abspath(run_meta_dir))
        payload, err = _load_from_run_meta_dir(run_meta_abs)
    else:
        print(
            json.dumps(
                {
                    "result": "refused",
                    "refusal": {
                        "reason_code": "refusal.net.envelope_invalid",
                        "message": "tool_anti_cheat_report requires --runtime-json or --run-meta-dir",
                        "remediation_hint": "Provide runtime payload or run_meta directory path.",
                        "relevant_ids": {"command_id": "tool_anti_cheat_report"},
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    if err:
        print(
            json.dumps(
                {
                    "result": "refused",
                    "refusal": {
                        "reason_code": "refusal.net.envelope_invalid",
                        "message": "failed to load anti-cheat inputs for reporting",
                        "remediation_hint": "Provide valid runtime JSON or run_meta anti-cheat artifact directory.",
                        "relevant_ids": {"error": err},
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    summary = build_summary(payload)
    out_dir_abs = os.path.join(repo_root, str(args.out_dir).strip().replace("/", os.sep))
    if not os.path.isdir(out_dir_abs):
        os.makedirs(out_dir_abs, exist_ok=True)
    out_prefix = str(args.out_prefix).strip() or "anti_cheat_report"
    json_abs = os.path.join(out_dir_abs, "{}.json".format(out_prefix))
    md_abs = os.path.join(out_dir_abs, "{}.md".format(out_prefix))
    write_canonical_json(json_abs, summary)
    with open(md_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_markdown(summary))

    response = {
        "result": "complete",
        "json_path": norm(os.path.relpath(json_abs, repo_root)),
        "markdown_path": norm(os.path.relpath(md_abs, repo_root)),
        "proof_hash": str(summary.get("proof_hash", "")),
        "counts": dict(summary.get("counts") or {}),
    }
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

