#!/usr/bin/env python3
import argparse
import json
import os
import sys

from dompkg_lib import DomPkgError, refusal_payload, verify_package


def _iter_packages(path: str):
    if os.path.isfile(path):
        yield os.path.abspath(path)
        return
    for dirpath, _dirs, files in os.walk(path):
        files.sort()
        for name in files:
            if name.lower().endswith(".dompkg"):
                yield os.path.abspath(os.path.join(dirpath, name))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic dompkg artifacts.")
    parser.add_argument("--pkg", default="")
    parser.add_argument("--pkg-dir", default="")
    parser.add_argument("--trust-policy", default="")
    args = parser.parse_args()

    roots = []
    if args.pkg:
        roots.append(args.pkg)
    if args.pkg_dir:
        roots.append(args.pkg_dir)
    if not roots:
        print(json.dumps(refusal_payload("refuse.invalid_input", "package path is required"), indent=2))
        return 3

    failures = []
    verified = []
    for root in roots:
        if not os.path.exists(root):
            print(json.dumps(refusal_payload("refuse.invalid_input", "path does not exist", {"path": root}), indent=2))
            return 3
        for pkg in _iter_packages(root):
            try:
                verified.append(verify_package(pkg, trust_policy_path=args.trust_policy))
            except DomPkgError as exc:
                failures.append({
                    "pkg_path": pkg.replace("\\", "/"),
                    "refusal": refusal_payload(exc.code, exc.message, exc.details)["refusal"],
                })

    if failures:
        print(json.dumps({"result": "refused", "failures": failures}, indent=2))
        return 3
    print(json.dumps({"result": "ok", "verified": verified}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
