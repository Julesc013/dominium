#!/usr/bin/env python3
"""Run the deterministic Omega offline update simulation and write the committed audit outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402
install_src_aliases(REPO_ROOT_HINT)

from tools.mvp.update_sim_common import (  # noqa: E402
    UPDATE_SIM_RUN_DOC_REL,
    UPDATE_SIM_RUN_JSON_REL,
    build_update_sim_baseline,
    run_update_sim,
)


def _token(value: object) -> str:
    return str(value or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--output-root-rel", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = run_update_sim(
        repo_root,
        output_root_rel=str(args.output_root_rel or ""),
        write_outputs=True,
    )
    written = dict(report.get("written") or {})
    payload = {
        "result": _token(report.get("result")),
        "json_output_rel": os.path.relpath(str(written.get("json_path", "")), repo_root).replace("\\", "/") if _token(written.get("json_path")) else UPDATE_SIM_RUN_JSON_REL,
        "doc_output_rel": os.path.relpath(str(written.get("doc_path", "")), repo_root).replace("\\", "/") if _token(written.get("doc_path")) else UPDATE_SIM_RUN_DOC_REL,
        "expected_baseline_fingerprint": _token(build_update_sim_baseline(report).get("deterministic_fingerprint")),
        "scenario_order": list(report.get("scenario_order") or []),
        "report": report,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if _token(report.get("result")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
