#!/usr/bin/env python3
"""Verify a RELEASE-1 manifest offline against a distribution directory."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from release import infer_dist_root_from_manifest_path, verify_release_manifest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a RELEASE-1 manifest offline against a distribution directory.")
    parser.add_argument("--dist-root", default="")
    parser.add_argument("--manifest-path", required=True)
    parser.add_argument("--signature-path", default="")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--trust-policy-id", default="")
    parser.add_argument("--trust-policy-registry", default="")
    parser.add_argument("--trust-root-registry", default="")
    args = parser.parse_args(argv)

    manifest_path = os.path.normpath(os.path.abspath(str(args.manifest_path)))
    dist_root = str(args.dist_root).strip()
    if dist_root:
        dist_root = os.path.normpath(os.path.abspath(dist_root))
    else:
        dist_root = infer_dist_root_from_manifest_path(manifest_path)
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root))) if str(args.repo_root).strip() else ""

    report = verify_release_manifest(
        dist_root,
        manifest_path,
        repo_root=repo_root,
        signature_path=str(args.signature_path).strip(),
        trust_policy_id=str(args.trust_policy_id).strip(),
        trust_policy_registry_path=str(args.trust_policy_registry).strip(),
        trust_root_registry_path=str(args.trust_root_registry).strip(),
    )
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
