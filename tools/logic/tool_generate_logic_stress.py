#!/usr/bin/env python3
"""Generate deterministic LOGIC-10 stress scenario packs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.logic.logic10_stress_common import _as_int, _write_json, generate_logic_stress_scenario


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--seed", type=int, default=1010)
    parser.add_argument("--tick-count", type=int, default=8)
    parser.add_argument("--network-count", type=int, default=12)
    parser.add_argument("--mega-node-count", type=int, default=1_000_000)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = generate_logic_stress_scenario(
        repo_root=args.repo_root,
        seed=int(max(1, _as_int(args.seed, 1010))),
        tick_count=int(max(4, _as_int(args.tick_count, 8))),
        network_count=int(max(4, _as_int(args.network_count, 12))),
        mega_node_count=int(max(1, _as_int(args.mega_node_count, 1_000_000))),
    )
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
