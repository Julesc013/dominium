#!/usr/bin/env python3
"""Run the deterministic DIST-5 UX smoke suite."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.appshell.tool_generate_command_docs import main as generate_command_docs_main  # noqa: E402
from tools.dist.ux_smoke_common import (  # noqa: E402
    DIST5_FINAL_PATH,
    build_ux_smoke_report,
    write_ux_smoke_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--doc-path", default="")
    parser.add_argument("--json-path", default="")
    parser.add_argument("--final-doc-path", default=DIST5_FINAL_PATH)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    generate_command_docs_main(["--repo-root", repo_root])
    report = build_ux_smoke_report(repo_root)
    write_ux_smoke_outputs(
        repo_root,
        report,
        doc_path=str(args.doc_path).strip(),
        json_path=str(args.json_path).strip(),
        final_doc_path=str(args.final_doc_path).strip() or DIST5_FINAL_PATH,
    )
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
