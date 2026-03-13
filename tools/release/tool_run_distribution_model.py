"""Generate the DIST-0 distribution architecture report."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.distribution_model_common import write_distribution_model_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the DIST-0 distribution architecture report.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--dist-root", default="dist", help="Distribution staging root.")
    parser.add_argument("--report-path", default="data/audit/distribution_architecture_report.json", help="Machine-readable output path.")
    parser.add_argument("--doc-path", default="docs/audit/DISTRIBUTION_ARCHITECTURE_FREEZE.md", help="Markdown output path.")
    args = parser.parse_args(argv)

    report = write_distribution_model_outputs(
        args.repo_root,
        dist_root=args.dist_root,
        report_path=args.report_path,
        doc_path=args.doc_path,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
