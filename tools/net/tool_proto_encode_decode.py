#!/usr/bin/env python3
"""Deterministic encode/decode utility for net_proto_message artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.net_protocol import decode_proto_message, encode_proto_message


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _hex_encode(raw: bytes) -> str:
    return bytes(raw or b"").hex()


def _hex_decode(raw: str) -> bytes:
    return bytes.fromhex(str(raw).strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Encode/decode deterministic net_proto_message payloads.")
    sub = parser.add_subparsers(dest="command")

    enc = sub.add_parser("encode")
    enc.add_argument("--repo-root", default="")
    enc.add_argument("--in", dest="in_path", required=True, help="input JSON proto_message path")

    dec = sub.add_parser("decode")
    dec.add_argument("--repo-root", default="")
    dec.add_argument("--hex", dest="hex_blob", required=True, help="hex-encoded proto_message bytes")

    args = parser.parse_args()
    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(getattr(args, "repo_root", "")).strip() else REPO_ROOT_HINT
    command = str(getattr(args, "command", "")).strip()

    if command == "encode":
        payload = _read_json(str(args.in_path))
        if not isinstance(payload, dict):
            print(json.dumps({"result": "refused", "message": "input must be object JSON"}, indent=2, sort_keys=True))
            return 2
        encoded = encode_proto_message(payload)
        out = {
            "result": "complete",
            "bytes_hex": _hex_encode(encoded),
            "bytes_sha256": canonical_sha256({"blob_hex": _hex_encode(encoded)}),
            "size_bytes": len(encoded),
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0

    if command == "decode":
        decoded = decode_proto_message(repo_root=repo_root, message_bytes=_hex_decode(str(args.hex_blob)))
        if decoded.get("result") != "complete":
            print(json.dumps(decoded, indent=2, sort_keys=True))
            return 2
        out = {
            "result": "complete",
            "proto_message": decoded.get("proto_message"),
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
