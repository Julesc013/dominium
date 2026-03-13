#!/usr/bin/env python3
"""Generate deterministic PROD-GATE-0 audit outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.prod_gate0_common import build_product_boot_matrix_report, write_product_boot_matrix_outputs  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate PROD-GATE-0 standalone product boot matrix outputs.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--install-root", default="")
    parser.add_argument("--simulate-tty", default="auto", choices=("auto", "yes", "no"))
    parser.add_argument("--simulate-gui", default="auto", choices=("auto", "yes", "no"))
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    report = build_product_boot_matrix_report(
        repo_root,
        simulate_tty=str(args.simulate_tty),
        simulate_gui=str(args.simulate_gui),
        install_root=str(args.install_root),
    )
    written = write_product_boot_matrix_outputs(repo_root, report)
    payload = {
        "result": str(report.get("result", "")).strip() or "complete",
        "report_id": str(report.get("report_id", "")).strip(),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "failure_count": int(len(list(report.get("failures") or []))),
        "written_outputs": dict(written),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
