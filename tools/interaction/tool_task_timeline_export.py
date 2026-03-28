#!/usr/bin/env python3
"""Deterministic ACT-3 task timeline export tool."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from interaction.task.task_engine import build_task_timeline  # noqa: E402


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_export(args: argparse.Namespace) -> dict:
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    state_path = os.path.join(repo_root, str(args.state_file).replace("/", os.sep))
    state_payload = _read_json(state_path)
    if not state_payload:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.task.timeline.state_missing",
                    "message": "state file is missing or invalid JSON object",
                    "path": "$.state_file",
                }
            ],
        }

    rows = list(state_payload.get("tasks") or state_payload.get("task_rows") or state_payload.get("task_instances") or [])
    if not isinstance(rows, list):
        rows = []
    event_rows = list(state_payload.get("task_provenance_events") or state_payload.get("events") or [])
    if not isinstance(event_rows, list):
        event_rows = []

    timeline = build_task_timeline(
        task_rows=rows,
        event_rows=event_rows,
        task_id=str(args.task_id or ""),
    )
    out_dir = str(args.out_dir or os.path.join("build", "task_timeline")).replace("/", os.sep)
    out_abs = os.path.join(repo_root, out_dir)
    if not os.path.isdir(out_abs):
        os.makedirs(out_abs, exist_ok=True)
    suffix = str(args.task_id or "all").replace("/", "_")
    out_path = os.path.join(out_abs, "task_timeline.{}.json".format(suffix))
    _write_json(out_path, timeline)

    return {
        "result": "complete",
        "tool_id": "tool.interaction.tool_task_timeline_export",
        "task_id_filter": str(args.task_id or "") or None,
        "timeline_hash": str(timeline.get("timeline_hash", "")),
        "output_file": os.path.relpath(out_path, repo_root).replace("\\", "/"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic ACT-3 task timeline summaries.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--state-file", default=os.path.join("build", "task_state.json"))
    parser.add_argument("--task-id", default="")
    parser.add_argument("--out-dir", default=os.path.join("build", "task_timeline"))
    args = parser.parse_args()

    result = run_export(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
