#!/usr/bin/env python3
"""Replay deterministic endpoint negotiation from recorded or default descriptors."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from compat import (  # noqa: E402
    build_default_endpoint_descriptor,
    negotiate_product_endpoints,
    verify_recorded_negotiation,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay CAP-NEG-2 deterministic negotiation from endpoint descriptors.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--product-a", default="client")
    parser.add_argument("--product-b", default="server")
    parser.add_argument("--allow-read-only", action="store_true")
    parser.add_argument("--contract-bundle-hash", default="hash.contract.bundle.replay")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    endpoint_a = build_default_endpoint_descriptor(
        repo_root,
        product_id=str(args.product_a or "client").strip() or "client",
        product_version="0.0.0+replay.{}".format(str(args.product_a or "client").strip() or "client"),
        allow_read_only=bool(args.allow_read_only),
    )
    endpoint_b = build_default_endpoint_descriptor(
        repo_root,
        product_id=str(args.product_b or "server").strip() or "server",
        product_version="0.0.0+replay.{}".format(str(args.product_b or "server").strip() or "server"),
        allow_read_only=bool(args.allow_read_only),
    )
    negotiation = negotiate_product_endpoints(
        repo_root,
        endpoint_a,
        endpoint_b,
        allow_read_only=bool(args.allow_read_only),
        chosen_contract_bundle_hash=str(args.contract_bundle_hash or "").strip(),
    )
    record = dict(negotiation.get("negotiation_record") or {})
    verification = verify_recorded_negotiation(
        repo_root,
        record,
        endpoint_a,
        endpoint_b,
        allow_read_only=bool(args.allow_read_only),
        chosen_contract_bundle_hash=str(args.contract_bundle_hash or "").strip(),
    )
    payload = {
        "result": "complete" if str(verification.get("result", "")).strip() == "complete" else "refused",
        "product_a": str(args.product_a or "client").strip() or "client",
        "product_b": str(args.product_b or "server").strip() or "server",
        "allow_read_only": bool(args.allow_read_only),
        "contract_bundle_hash": str(args.contract_bundle_hash or "").strip(),
        "negotiation_record_hash": str(negotiation.get("negotiation_record_hash", "")).strip(),
        "compatibility_mode_id": str(negotiation.get("compatibility_mode_id", "")).strip(),
        "endpoint_a_hash": str(negotiation.get("endpoint_a_hash", "")).strip(),
        "endpoint_b_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
        "verification": dict(verification),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))

    output_path = str(args.output_path or "").strip()
    if output_path:
        output_abs = os.path.normpath(os.path.abspath(os.path.join(repo_root, output_path)))
        _write_json(output_abs, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(payload.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
