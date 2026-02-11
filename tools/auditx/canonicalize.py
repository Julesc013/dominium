#!/usr/bin/env python3
"""Canonical JSON normalization helpers for AuditX artifacts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from typing import Any, Iterable, Set


DEFAULT_FORBIDDEN_FIELDS = {
    "created_utc",
    "generated_utc",
    "host_name",
    "last_reviewed",
    "machine_name",
    "run_id",
    "scan_id",
    "timestamp",
    "timestamps",
}


def _strip_forbidden(node: Any, forbidden: Set[str]) -> Any:
    if isinstance(node, dict):
        cleaned = {}
        for key in sorted(node.keys()):
            if key in forbidden:
                continue
            cleaned[key] = _strip_forbidden(node[key], forbidden)
        return cleaned
    if isinstance(node, list):
        return [_strip_forbidden(item, forbidden) for item in node]
    return node


def canonicalize_json_payload(payload: Any, forbidden_fields: Iterable[str] | None = None) -> Any:
    forbidden = set(DEFAULT_FORBIDDEN_FIELDS)
    if forbidden_fields:
        forbidden.update(str(item) for item in forbidden_fields)
    return _strip_forbidden(copy.deepcopy(payload), forbidden)


def canonical_json_string(payload: Any, forbidden_fields: Iterable[str] | None = None) -> str:
    canonical = canonicalize_json_payload(payload, forbidden_fields=forbidden_fields)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_json_hash(payload: Any, forbidden_fields: Iterable[str] | None = None) -> str:
    blob = canonical_json_string(payload, forbidden_fields=forbidden_fields).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="AuditX canonical JSON utility.")
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument("--output", default="", help="Optional canonical JSON output path.")
    parser.add_argument("--print-hash", action="store_true", help="Print canonical SHA-256 hash.")
    args = parser.parse_args()

    payload = _load_json(args.input)
    canonical_text = canonical_json_string(payload)
    if args.output:
        _write_text(args.output, canonical_text)
    else:
        print(canonical_text)
    if args.print_hash:
        print(canonical_json_hash(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

