#!/usr/bin/env python3
"""Replay a deterministic LOGIC-5 timing window and summarize timing hashes."""

from __future__ import annotations

import argparse
import json
import os
from typing import Iterable

from tools.logic.tool_replay_logic_window import _load_json, _write_json, replay_logic_window_from_payload
from tools.xstack.compatx.canonical_json import canonical_sha256


def replay_timing_window_from_payload(*, repo_root: str, payload: dict) -> dict:
    report = replay_logic_window_from_payload(repo_root=repo_root, payload=payload)
    if str(report.get("result", "")).strip() != "complete":
        return dict(report)
    logic_eval_state = dict(report.get("final_logic_eval_state") or {})
    timing_report = {
        "result": "complete",
        "tick_reports": list(report.get("tick_reports") or []),
        "final_signal_hash": str(report.get("final_signal_hash", "")),
        "logic_oscillation_record_hash_chain": str(report.get("logic_oscillation_record_hash_chain", "")),
        "logic_timing_violation_hash_chain": str(report.get("logic_timing_violation_hash_chain", "")),
        "logic_watchdog_timeout_hash_chain": str(report.get("logic_watchdog_timeout_hash_chain", "")),
        "oscillation_record_count": int(len(list(logic_eval_state.get("logic_oscillation_record_rows") or []))),
        "timing_violation_count": int(len(list(logic_eval_state.get("logic_timing_violation_event_rows") or []))),
        "watchdog_timeout_count": int(len(list(logic_eval_state.get("logic_watchdog_timeout_event_rows") or []))),
        "proof_surface": {
            "logic_oscillation_record_hash_chain": str(report.get("logic_oscillation_record_hash_chain", "")),
            "logic_timing_violation_hash_chain": str(report.get("logic_timing_violation_hash_chain", "")),
            "logic_watchdog_timeout_hash_chain": str(report.get("logic_watchdog_timeout_hash_chain", "")),
        },
        "final_logic_eval_state": logic_eval_state,
        "final_signal_store_state": dict(report.get("final_signal_store_state") or {}),
        "final_state_vector_snapshot_rows": list(report.get("final_state_vector_snapshot_rows") or []),
    }
    timing_report["deterministic_fingerprint"] = canonical_sha256(
        {
            "tick_reports": timing_report["tick_reports"],
            "final_signal_hash": timing_report["final_signal_hash"],
            "logic_oscillation_record_hash_chain": timing_report["logic_oscillation_record_hash_chain"],
            "logic_timing_violation_hash_chain": timing_report["logic_timing_violation_hash_chain"],
            "logic_watchdog_timeout_hash_chain": timing_report["logic_watchdog_timeout_hash_chain"],
        }
    )
    return timing_report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--scenario-json", required=True)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = _load_json(os.path.join(args.repo_root, args.scenario_json.replace("/", os.sep)))
    report = replay_timing_window_from_payload(repo_root=args.repo_root, payload=payload)
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
