#!/usr/bin/env python3
"""Plan deterministic migration lifecycle actions for a single artifact."""

from __future__ import annotations

import argparse
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.compat.migration_lifecycle_common import plan_artifact_migration  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print the deterministic migration decision for an artifact.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--artifact-kind-id", required=True)
    parser.add_argument("--artifact-path", required=True)
    parser.add_argument("--allow-read-only", action="store_true")
    parser.add_argument("--expected-contract-bundle-hash", default="")
    parser.add_argument("--output-path", default="")
    return parser


def main() -> int:
    args = _parser().parse_args()
    payload = plan_artifact_migration(
        os.path.abspath(str(args.repo_root)),
        artifact_kind_id=str(args.artifact_kind_id),
        artifact_path=str(args.artifact_path),
        allow_read_only=bool(args.allow_read_only),
        expected_contract_bundle_hash=str(args.expected_contract_bundle_hash or "").strip(),
    )
    text = canonical_json_text(payload)
    if str(args.output_path or "").strip():
        out_abs = os.path.abspath(str(args.output_path))
        os.makedirs(os.path.dirname(out_abs), exist_ok=True)
        with open(out_abs, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.write("\n")
    print(text)
    return 0 if str(payload.get("decision_action_id", "")).strip() != "decision.refuse" else 1


if __name__ == "__main__":
    raise SystemExit(main())
