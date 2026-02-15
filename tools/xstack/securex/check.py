#!/usr/bin/env python3
"""SecureX minimal signature status verification for pack manifests."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.pack_loader.loader import load_pack_set  # noqa: E402


ALLOWED_SIGNATURE_STATUS = {
    "official",
    "unsigned",
    "classroom-restricted",
    "signed",
    "verified",
    "revoked",
}


def run_securex_check(repo_root: str, profile: str) -> Dict[str, object]:
    _ = profile
    loaded = load_pack_set(repo_root=repo_root)
    findings: List[Dict[str, object]] = []

    if loaded.get("result") != "complete":
        for row in loaded.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.securex.pack_load_failed")),
                    "message": str(row.get("message", "")),
                }
            )
        return {
            "status": "refusal",
            "message": "securex refused because pack loading failed",
            "findings": sorted(findings, key=lambda item: (str(item.get("severity", "")), str(item.get("code", "")), str(item.get("message", "")))),
        }

    unsigned_count = 0
    for row in sorted(loaded.get("packs") or [], key=lambda item: str(item.get("pack_id", ""))):
        pack_id = str(row.get("pack_id", ""))
        signature_status = str(row.get("signature_status", "")).strip()
        if signature_status not in ALLOWED_SIGNATURE_STATUS:
            findings.append(
                {
                    "severity": "refusal",
                    "code": "refuse.securex.unknown_signature_status",
                    "message": "pack '{}' uses unknown signature_status '{}'".format(pack_id, signature_status or "<empty>"),
                }
            )
            continue
        if signature_status == "revoked":
            findings.append(
                {
                    "severity": "refusal",
                    "code": "refuse.securex.revoked_pack",
                    "message": "pack '{}' is marked revoked".format(pack_id),
                }
            )
        elif signature_status == "unsigned":
            unsigned_count += 1
            findings.append(
                {
                    "severity": "warn",
                    "code": "warn.securex.unsigned_pack_allowed_dev",
                    "message": "pack '{}' is unsigned (allowed in developer runs)".format(pack_id),
                }
            )

    ordered = sorted(findings, key=lambda item: (str(item.get("severity", "")), str(item.get("code", "")), str(item.get("message", ""))))
    status = "refusal" if any(str(row.get("severity", "")) == "refusal" for row in ordered) else "pass"
    message = "securex check {} (packs={}, unsigned={})".format(
        "passed" if status == "pass" else "completed_with_findings",
        int(loaded.get("pack_count", 0)),
        unsigned_count,
    )
    return {
        "status": status,
        "message": message,
        "findings": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SecureX signature status checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()
    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_securex_check(repo_root=repo_root, profile=str(args.profile))
    print(json.dumps(result, indent=2, sort_keys=True))
    status = str(result.get("status", "error"))
    if status == "pass":
        return 0
    if status == "refusal":
        return 2
    if status == "fail":
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

