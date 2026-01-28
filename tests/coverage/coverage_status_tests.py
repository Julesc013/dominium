import argparse
import os
import sys

from coverage_lib import (
    ALLOWED_STATUSES,
    coverage_paths,
    ensure_sorted,
    list_level_dirs,
    load_json,
)


MISSING_CAP_REFUSALS = {"REFUSE_CAPABILITY_MISSING", "WD-REFUSAL-CAPABILITY"}


def load_list(path):
    data = load_json(path)
    if isinstance(data, list):
        return data
    return []


def compute_status(required_caps, required_procs, present_caps, present_procs):
    caps_missing = sorted(set(required_caps) - set(present_caps))
    procs_missing = sorted(set(required_procs) - set(present_procs))
    if not caps_missing and not procs_missing:
        return "COMPLETE"
    if present_caps or present_procs:
        return "PARTIAL"
    return "UNSUPPORTED"


def main():
    parser = argparse.ArgumentParser(description="Coverage status tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    ok = True
    summary = []

    for level_dir, expected_level in list_level_dirs(repo_root):
        paths = coverage_paths(repo_root, level_dir)
        coverage = load_json(paths["coverage"])
        if coverage.get("level_id") != expected_level:
            sys.stderr.write("FAIL: level id mismatch in {}\n".format(level_dir))
            ok = False
            continue

        required_caps = coverage.get("required_capabilities", [])
        required_procs = coverage.get("required_process_families", [])
        required_refusals = set(coverage.get("required_refusals", []))
        declared_status = coverage.get("status", "")
        allow_flag = coverage.get("allow_in_principle", False)

        present_caps = load_list(paths["cap_present"])
        missing_caps = load_list(paths["cap_missing"])
        present_procs = load_list(paths["proc_present"])
        missing_procs = load_list(paths["proc_missing"])

        expected_missing_caps = sorted(set(required_caps) - set(present_caps))
        expected_missing_procs = sorted(set(required_procs) - set(present_procs))

        if missing_caps != expected_missing_caps:
            sys.stderr.write("FAIL: capabilities_missing mismatch in {}\n".format(level_dir))
            ok = False
        if missing_procs != expected_missing_procs:
            sys.stderr.write("FAIL: process_families_missing mismatch in {}\n".format(level_dir))
            ok = False

        if not ensure_sorted(present_caps) or not ensure_sorted(missing_caps):
            sys.stderr.write("FAIL: capability fixture lists must be sorted in {}\n".format(level_dir))
            ok = False
        if not ensure_sorted(present_procs) or not ensure_sorted(missing_procs):
            sys.stderr.write("FAIL: process fixture lists must be sorted in {}\n".format(level_dir))
            ok = False

        computed_status = compute_status(required_caps, required_procs, present_caps, present_procs)
        if computed_status not in ALLOWED_STATUSES:
            sys.stderr.write("FAIL: computed status invalid in {}\n".format(level_dir))
            ok = False
        if declared_status != computed_status:
            sys.stderr.write(
                "FAIL: declared status {} != computed {} in {}\n".format(
                    declared_status, computed_status, level_dir
                )
            )
            ok = False

        if expected_missing_caps or expected_missing_procs:
            if not (required_refusals & MISSING_CAP_REFUSALS):
                sys.stderr.write(
                    "FAIL: missing capability refusal not declared in {}\n".format(level_dir)
                )
                ok = False
        else:
            if not allow_flag:
                sys.stderr.write("FAIL: allow_in_principle false with full capabilities in {}\n".format(level_dir))
                ok = False

        summary.append("{}={}".format(expected_level, declared_status))

    if ok:
        print("coverage status:", ", ".join(summary))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
