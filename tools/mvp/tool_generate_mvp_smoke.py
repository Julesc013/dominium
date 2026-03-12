#!/usr/bin/env python3
"""Generate deterministic MVP smoke scenario and expected hashes."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.mvp_smoke_common import (  # noqa: E402
    DEFAULT_HASHES_REL,
    DEFAULT_MVP_SMOKE_SEED,
    DEFAULT_SCENARIO_REL,
    write_generated_mvp_smoke_inputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", type=int, default=DEFAULT_MVP_SMOKE_SEED)
    parser.add_argument("--scenario-path", default=DEFAULT_SCENARIO_REL)
    parser.add_argument("--hashes-path", default=DEFAULT_HASHES_REL)
    args = parser.parse_args(argv)

    result = write_generated_mvp_smoke_inputs(
        args.repo_root,
        seed=int(args.seed),
        scenario_path=str(args.scenario_path),
        hashes_path=str(args.hashes_path),
    )
    payload = {
        "result": "complete",
        "scenario_path": str(result.get("scenario_path", "")),
        "hashes_path": str(result.get("hashes_path", "")),
        "scenario_fingerprint": str((dict(result.get("scenario") or {})).get("deterministic_fingerprint", "")),
        "hashes_fingerprint": str((dict(result.get("expected_hashes") or {})).get("deterministic_fingerprint", "")),
        "deterministic_fingerprint": str(result.get("deterministic_fingerprint", "")),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
