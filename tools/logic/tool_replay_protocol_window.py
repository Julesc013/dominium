#!/usr/bin/env python3
"""Replay a deterministic LOGIC-9 protocol window and summarize protocol proof hashes."""

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


def replay_protocol_window_from_payload(*, repo_root: str, payload: dict) -> dict:
    return replay_logic_window_from_payload(repo_root=repo_root, payload=payload)


def protocol_proof_surface(report: dict) -> dict:
    payload = dict(report or {})
    transport_state = dict(payload.get("final_signal_transport_state") or {})
    return {
        "logic_protocol_frame_hash_chain": str(payload.get("logic_protocol_frame_hash_chain", "")),
        "logic_arbitration_state_hash_chain": str(payload.get("logic_arbitration_state_hash_chain", "")),
        "logic_protocol_event_hash_chain": str(payload.get("logic_protocol_event_hash_chain", "")),
        "logic_security_fail_hash_chain": str(payload.get("logic_security_fail_hash_chain", "")),
        "message_delivery_event_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(row.get("tick", 0) or 0),
                    "receipt_id": str(row.get("receipt_id", "")).strip(),
                    "status": str(row.get("status", "")).strip(),
                }
                for row in list(transport_state.get("message_delivery_event_rows") or [])
                if isinstance(row, dict)
            ]
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--scenario-json", required=True)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = _load_json(os.path.join(args.repo_root, args.scenario_json.replace("/", os.sep)))
    report = replay_protocol_window_from_payload(repo_root=args.repo_root, payload=payload)
    report["protocol_proof_surface"] = protocol_proof_surface(report)
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
