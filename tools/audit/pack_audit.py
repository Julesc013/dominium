import os
import subprocess
import sys
from datetime import date


def main():
    repo_root = "."
    packs_root = os.path.join(repo_root, "data", "packs")
    report_path = os.path.join("docs", "audit", "PACK_AUDIT.txt")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    pack_dirs = [
        os.path.join(packs_root, d)
        for d in sorted(os.listdir(packs_root))
        if os.path.isdir(os.path.join(packs_root, d))
    ]

    failures = 0
    with open(report_path, "w", encoding="utf-8") as report:
        report.write("Status: DERIVED\n")
        report.write("Last Reviewed: {}\n".format(date.today().isoformat()))
        report.write("Supersedes: none\n")
        report.write("Superseded By: none\n\n")
        report.write(
            "Note: This document may reference archived or historical files\n"
            "for descriptive purposes only. Such references do not confer\n"
            "authority and are not normative.\n\n"
        )
        report.write("Pack audit report\n")
        report.write("Repo root: {}\n".format(os.path.abspath(repo_root)))
        report.write("Pack root: {}\n\n".format(os.path.abspath(packs_root)))
        for pack_dir in pack_dirs:
            rel = os.path.relpath(pack_dir, repo_root)
            cmd = [
                sys.executable,
                os.path.join("tools", "pack", "pack_validate.py"),
                "--repo-root",
                repo_root,
                "--pack-root",
                pack_dir,
                "--format",
                "text",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            report.write("== {} ==\n".format(rel))
            if proc.stdout:
                report.write(proc.stdout)
            if proc.stderr:
                report.write(proc.stderr)
            if proc.returncode != 0:
                failures += 1
                report.write("status: FAIL\n")
            else:
                report.write("status: PASS\n")
            report.write("\n")

        report.write("Summary: {} packs, {} failures\n".format(len(pack_dirs), failures))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
