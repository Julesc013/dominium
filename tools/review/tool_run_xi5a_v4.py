#!/usr/bin/env python3
"""Run deterministic XI-5a-v4 dangerous-shadow execution."""

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


from tools.review.xi5a_v4_execute_common import (  # noqa: E402
    Xi5aV4ExecutionFailure,
    Xi5aV4InputsMissing,
    build_xi5a_v4_plan,
    execute_xi5a_v4,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-5a-v4 dangerous-shadow execution.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.plan_only:
            plan_first = build_xi5a_v4_plan(args.repo_root)
            plan_second = build_xi5a_v4_plan(args.repo_root)
            if json.dumps(plan_first, sort_keys=True) != json.dumps(plan_second, sort_keys=True):
                sys.stdout.write(
                    json.dumps(
                        {
                            "code": "refusal.xi5a.plan_nondeterministic",
                            "result": "refused",
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
                sys.stdout.write("\n")
                return 3
            sys.stdout.write(
                json.dumps(
                    {
                        "approved_rows": len(list(dict(plan_first.get("move_map") or {}).get("rows") or [])),
                        "preview_changed_file_count": int(plan_first.get("preview_changed_file_count", 0) or 0),
                        "result": "planned",
                        "unexpected_paths": list(dict(plan_first.get("surprises") or {}).get("unexpected") or []),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            sys.stdout.write("\n")
            return 0

        result = execute_xi5a_v4(args.repo_root)
    except Xi5aV4InputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4
    except Xi5aV4ExecutionFailure as exc:
        sys.stdout.write(json.dumps({"code": exc.code, **dict(exc.details or {})}, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 2

    execution_log = dict(result.get("execution_log") or {})
    residual = dict(result.get("residual_report") or {})
    payload = {
        "approved_rows_executed": len(list(dict(result.get("move_map") or {}).get("rows") or [])),
        "attic_rows_routed": len(list(dict(result.get("attic_map") or {}).get("rows") or [])),
        "deferred_runtime_src_remaining": len(list(residual.get("deferred_to_xi5b_remaining") or [])),
        "ready_for_xi6": bool(execution_log.get("ready_for_xi6")),
        "result": "complete",
        "unexpected_runtime_src_paths": list(residual.get("unexpected_remaining_src_paths") or []),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
