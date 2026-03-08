#!/usr/bin/env python3
"""Replay a deterministic LOGIC-8 fault/noise/security window and summarize proof hashes."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.logic.tool_replay_logic_window import _load_json, _write_json, replay_logic_window_from_payload
from tools.xstack.compatx.canonical_json import canonical_sha256


def replay_fault_window_from_payload(*, repo_root: str, payload: dict) -> dict:
    report = replay_logic_window_from_payload(repo_root=repo_root, payload=payload)
    if str(report.get("result", "")).strip() != "complete":
        return dict(report)
    logic_eval_state = dict(report.get("final_logic_eval_state") or {})
    logic_fault_rows = [
        dict(row)
        for row in list(payload.get("logic_fault_state_rows") or [])
        if isinstance(row, dict)
    ]
    fault_report = {
        "result": "complete",
        "tick_reports": list(report.get("tick_reports") or []),
        "final_signal_hash": str(report.get("final_signal_hash", "")),
        "logic_fault_state_hash_chain": str(report.get("logic_fault_state_hash_chain", "")),
        "logic_noise_decision_hash_chain": str(report.get("logic_noise_decision_hash_chain", "")),
        "logic_security_fail_hash_chain": str(report.get("logic_security_fail_hash_chain", "")),
        "fault_state_count": int(len(logic_fault_rows)),
        "noise_decision_count": int(len(list(logic_eval_state.get("logic_noise_decision_rows") or []))),
        "security_fail_count": int(len(list(logic_eval_state.get("logic_security_fail_rows") or []))),
        "proof_surface": {
            "logic_fault_state_hash_chain": str(report.get("logic_fault_state_hash_chain", "")),
            "logic_noise_decision_hash_chain": str(report.get("logic_noise_decision_hash_chain", "")),
            "logic_security_fail_hash_chain": str(report.get("logic_security_fail_hash_chain", "")),
        },
        "final_logic_eval_state": logic_eval_state,
        "final_signal_store_state": dict(report.get("final_signal_store_state") or {}),
        "logic_fault_state_rows": logic_fault_rows,
    }
    fault_report["deterministic_fingerprint"] = canonical_sha256(
        {
            "tick_reports": fault_report["tick_reports"],
            "final_signal_hash": fault_report["final_signal_hash"],
            "logic_fault_state_hash_chain": fault_report["logic_fault_state_hash_chain"],
            "logic_noise_decision_hash_chain": fault_report["logic_noise_decision_hash_chain"],
            "logic_security_fail_hash_chain": fault_report["logic_security_fail_hash_chain"],
        }
    )
    return fault_report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--scenario-json", required=True)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = _load_json(os.path.join(args.repo_root, args.scenario_json.replace("/", os.sep)))
    report = replay_fault_window_from_payload(repo_root=args.repo_root, payload=payload)
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
