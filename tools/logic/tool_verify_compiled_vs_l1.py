#!/usr/bin/env python3
"""Verify deterministic compiled-vs-L1 parity for bounded LOGIC fixtures."""

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

from tools.logic.tool_replay_compiled_logic_window import _load_json, _write_json, replay_compiled_logic_window_from_payload
from tools.logic.tool_run_logic_eval_stress import build_logic_eval_stress_scenario
from tools.xstack.compatx.canonical_json import canonical_sha256


def _token(value: object) -> str:
    return str(value or "").strip()


def verify_compiled_vs_l1(
    *,
    repo_root: str,
    scenario_payload: dict | None = None,
    element_pairs: int = 6,
    tick_count: int = 4,
) -> dict:
    payload = (
        dict(scenario_payload)
        if isinstance(scenario_payload, dict) and scenario_payload
        else build_logic_eval_stress_scenario(
            repo_root=repo_root,
            element_pairs=int(max(1, int(element_pairs))),
            tick_count=int(max(2, int(tick_count))),
        )
    )
    report = replay_compiled_logic_window_from_payload(repo_root=repo_root, payload=payload)
    if _token(report.get("result")) != "complete":
        return dict(report)
    proof_surface = {
        "compile_result_hash_chain": _token(report.get("compile_result_hash_chain")),
        "compiled_model_hash_chain": _token(report.get("compiled_model_hash_chain")),
        "equivalence_proof_hash_chain": _token(report.get("equivalence_proof_hash_chain")),
        "logic_compile_policy_hash_chain": _token(report.get("logic_compile_policy_hash_chain")),
        "forced_expand_event_hash_chain": _token(report.get("forced_expand_event_hash_chain")),
    }
    verification = {
        "result": "complete" if bool(report.get("signals_match", False) and report.get("states_match", False) and report.get("tick_signal_match", False)) else "mismatch",
        "scenario_id": _token(payload.get("scenario_id")),
        "compiled_model_ids": list(report.get("compiled_model_ids") or []),
        "compiled_type_ids": list(report.get("compiled_type_ids") or []),
        "compiled_path_observed": bool(report.get("compiled_path_observed", False)),
        "signals_match": bool(report.get("signals_match", False)),
        "states_match": bool(report.get("states_match", False)),
        "tick_signal_match": bool(report.get("tick_signal_match", False)),
        "proof_surface": proof_surface,
    }
    verification["deterministic_fingerprint"] = canonical_sha256(
        {
            "scenario_id": verification["scenario_id"],
            "compiled_model_ids": verification["compiled_model_ids"],
            "compiled_type_ids": verification["compiled_type_ids"],
            "compiled_path_observed": verification["compiled_path_observed"],
            "signals_match": verification["signals_match"],
            "states_match": verification["states_match"],
            "tick_signal_match": verification["tick_signal_match"],
            "proof_surface": verification["proof_surface"],
        }
    )
    return verification


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--scenario-json", default="")
    parser.add_argument("--element-pairs", type=int, default=6)
    parser.add_argument("--tick-count", type=int, default=4)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    scenario_payload = {}
    if args.scenario_json:
        scenario_payload = _load_json(os.path.join(args.repo_root, args.scenario_json.replace("/", os.sep)))
    report = verify_compiled_vs_l1(
        repo_root=args.repo_root,
        scenario_payload=scenario_payload,
        element_pairs=int(args.element_pairs),
        tick_count=int(args.tick_count),
    )
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if _token(report.get("result")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
