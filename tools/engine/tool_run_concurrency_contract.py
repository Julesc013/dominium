#!/usr/bin/env python3
"""Generate deterministic CONCURRENCY-CONTRACT-0 baseline artifacts."""

from __future__ import annotations

import argparse
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.engine.concurrency_contract_common import write_concurrency_contract_outputs  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Write CONCURRENCY-CONTRACT-0 baseline artifacts.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    payload = write_concurrency_contract_outputs(os.path.abspath(str(args.repo_root or ".")))
    print(canonical_json_text(payload))
    return 0 if str(dict(payload.get("report") or {}).get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
