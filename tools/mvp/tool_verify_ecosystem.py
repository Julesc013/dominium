#!/usr/bin/env python3
"""Run the deterministic Omega ecosystem verifier and write the committed audit outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.ecosystem_verify_common import (  # noqa: E402
    DEFAULT_PLATFORM_TAG,
    ECOSYSTEM_VERIFY_RUN_DOC_REL,
    ECOSYSTEM_VERIFY_RUN_JSON_REL,
    build_ecosystem_verify_baseline,
    verify_ecosystem,
    write_ecosystem_verify_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--release-index-path", default="")
    parser.add_argument("--component-graph-path", default="")
    parser.add_argument("--install-profile-registry-path", default="")
    parser.add_argument("--governance-profile-path", default="")
    parser.add_argument("--trust-policy-id", default="")
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    parser.add_argument("--output-path", default="")
    parser.add_argument("--doc-path", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = verify_ecosystem(
        repo_root,
        release_index_path=str(args.release_index_path or ""),
        component_graph_path=str(args.component_graph_path or ""),
        install_profile_registry_path=str(args.install_profile_registry_path or ""),
        governance_profile_path=str(args.governance_profile_path or ""),
        trust_policy_id=str(args.trust_policy_id or ""),
        platform_tag=str(args.platform_tag or DEFAULT_PLATFORM_TAG),
    )
    written = write_ecosystem_verify_outputs(
        repo_root,
        report,
        json_path=str(args.output_path or ""),
        doc_path=str(args.doc_path or ""),
    )
    payload = {
        "result": str(report.get("result", "")).strip(),
        "json_output_rel": os.path.relpath(str(written.get("json_path", "")), repo_root).replace("\\", "/") if str(written.get("json_path", "")).strip() else ECOSYSTEM_VERIFY_RUN_JSON_REL,
        "doc_output_rel": os.path.relpath(str(written.get("doc_path", "")), repo_root).replace("\\", "/") if str(written.get("doc_path", "")).strip() else ECOSYSTEM_VERIFY_RUN_DOC_REL,
        "baseline_fingerprint": str(build_ecosystem_verify_baseline(report).get("deterministic_fingerprint", "")).strip(),
        "report": report,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
