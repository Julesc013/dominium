#!/usr/bin/env python3
"""Plan an intentional Xi-6 architecture graph change without mutating artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi6_common import ARCH_UPDATE_TAG, evaluate_architecture_drift  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    report = evaluate_architecture_drift(args.repo_root)
    requires_update = bool(report.get("drifted"))
    payload = {
        "result": "complete",
        "tool_id": "controlx.tool_plan_arch_change.v1",
        "requires_arch_graph_update": requires_update,
        "required_tags": [ARCH_UPDATE_TAG] if requires_update else [],
        "frozen_content_hash": report.get("frozen_content_hash"),
        "live_content_hash": report.get("live_content_hash"),
        "module_delta_preview": list(report.get("module_delta_preview") or []),
        "next_steps": (
            [
                "prepare a ControlX-reviewed architecture change plan",
                "attach ARCH-GRAPH-UPDATE to the change request",
                "refresh architecture graph/module registry from live repo reality",
                "rerun Xi-6 gate suite before Xi-7",
            ]
            if requires_update
            else ["no architecture graph drift detected; no Xi-6 update plan is required"]
        ),
        "update_tag_template": {
            "report_id": "architecture_graph_update_request.v1",
            "required_tags": [ARCH_UPDATE_TAG],
            "reason": "describe the intentional architecture graph delta before replacing architecture_graph.v1",
        },
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
