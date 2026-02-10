#!/usr/bin/env python3
"""Generate deterministic identity fingerprint artifacts."""

import argparse
import json
import os
import sys


def _load_lib(repo_root):
    dev_root = os.path.join(repo_root, "scripts", "dev")
    if dev_root not in sys.path:
        sys.path.insert(0, dev_root)
    import identity_fingerprint_lib

    return identity_fingerprint_lib


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Generate Dominium identity fingerprint artifact.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--output",
        default=os.path.join("docs", "audit", "identity_fingerprint.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    lib = _load_lib(repo_root)
    payload = lib.build_identity_payload(repo_root)
    out_path = os.path.join(repo_root, args.output)
    if args.check:
        if not os.path.isfile(out_path):
            print("refuse.identity_fingerprint_missing")
            return 2
        try:
            with open(out_path, "r", encoding="utf-8") as handle:
                existing = json.load(handle)
        except (OSError, ValueError):
            print("refuse.identity_fingerprint_invalid")
            return 2
        if existing != payload:
            print("refuse.identity_fingerprint_stale")
            return 2
        print("identity_fingerprint=ok")
        return 0

    _write_json(out_path, payload)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
