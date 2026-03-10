#!/usr/bin/env python3
"""Generate the deterministic CAP-NEG-4 synthetic interoperability matrix."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.compat.cap_neg4_common import DEFAULT_CAP_NEG4_SEED, DEFAULT_MATRIX_REL, generate_interop_matrix, write_json  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the CAP-NEG-4 synthetic interoperability matrix.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", default=str(DEFAULT_CAP_NEG4_SEED))
    parser.add_argument("--output-path", default=DEFAULT_MATRIX_REL.replace("\\", "/"))
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    seed_value = int(str(args.seed or DEFAULT_CAP_NEG4_SEED).strip() or DEFAULT_CAP_NEG4_SEED)
    payload = generate_interop_matrix(repo_root=repo_root, seed=seed_value)

    output_path = str(args.output_path or "").strip()
    if output_path:
        abs_path = os.path.normpath(os.path.abspath(os.path.join(repo_root, output_path)))
        write_json(abs_path, payload)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
