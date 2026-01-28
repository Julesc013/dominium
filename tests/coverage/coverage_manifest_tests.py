import argparse
import os
import sys

from coverage_lib import (
    ALLOWED_STATUSES,
    SCENARIO_HEADER,
    coverage_paths,
    ensure_sorted,
    ensure_unique,
    first_content_line,
    is_reverse_dns,
    list_level_dirs,
    load_json,
    parse_refusal_codes,
)


REQUIRED_FIELDS = [
    "level_id",
    "level_name",
    "status",
    "required_schemas",
    "required_process_families",
    "required_capabilities",
    "required_refusals",
    "allow_in_principle",
    "determinism_assertions",
]


def validate_schema_paths(repo_root, schemas):
    missing = []
    for entry in schemas:
        path = os.path.join(repo_root, entry)
        if not os.path.isfile(path):
            missing.append(entry)
    return missing


def main():
    parser = argparse.ArgumentParser(description="Coverage manifest validation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    refusal_codes = parse_refusal_codes(
        os.path.join(repo_root, "docs", "arch", "REFUSAL_SEMANTICS.md")
    )

    ok = True
    for level_dir, expected_level in list_level_dirs(repo_root):
        paths = coverage_paths(repo_root, level_dir)
        if not os.path.isdir(paths["dir"]):
            sys.stderr.write("FAIL: missing coverage directory {}\n".format(paths["dir"]))
            ok = False
            continue
        if not os.path.isfile(paths["coverage"]):
            sys.stderr.write("FAIL: missing coverage.json in {}\n".format(level_dir))
            ok = False
            continue
        if not os.path.isfile(paths["scenario"]):
            sys.stderr.write("FAIL: missing scenario.scenario in {}\n".format(level_dir))
            ok = False
            continue

        coverage = load_json(paths["coverage"])
        for field in REQUIRED_FIELDS:
            if field not in coverage:
                sys.stderr.write(
                    "FAIL: coverage.json missing field '{}' in {}\n".format(field, level_dir)
                )
                ok = False

        level_id = coverage.get("level_id", "")
        if level_id != expected_level:
            sys.stderr.write(
                "FAIL: level_id mismatch in {} (expected {})\n".format(level_dir, expected_level)
            )
            ok = False

        status = coverage.get("status", "")
        if status not in ALLOWED_STATUSES:
            sys.stderr.write(
                "FAIL: invalid status '{}' in {}\n".format(status, level_dir)
            )
            ok = False

        schemas = coverage.get("required_schemas", [])
        if not schemas or not ensure_sorted(schemas):
            sys.stderr.write("FAIL: required_schemas must be non-empty and sorted in {}\n".format(level_dir))
            ok = False
        missing_schemas = validate_schema_paths(repo_root, schemas)
        if missing_schemas:
            sys.stderr.write(
                "FAIL: required_schemas missing files in {}: {}\n".format(
                    level_dir, ", ".join(missing_schemas)
                )
            )
            ok = False

        process_families = coverage.get("required_process_families", [])
        if not process_families or not ensure_sorted(process_families):
            sys.stderr.write(
                "FAIL: required_process_families must be non-empty and sorted in {}\n".format(level_dir)
            )
            ok = False
        if not ensure_unique(process_families):
            sys.stderr.write(
                "FAIL: required_process_families must be unique in {}\n".format(level_dir)
            )
            ok = False
        for entry in process_families:
            if not is_reverse_dns(entry):
                sys.stderr.write(
                    "FAIL: process_family id '{}' not reverse-DNS in {}\n".format(entry, level_dir)
                )
                ok = False

        capabilities = coverage.get("required_capabilities", [])
        if not capabilities or not ensure_sorted(capabilities):
            sys.stderr.write(
                "FAIL: required_capabilities must be non-empty and sorted in {}\n".format(level_dir)
            )
            ok = False
        if not ensure_unique(capabilities):
            sys.stderr.write(
                "FAIL: required_capabilities must be unique in {}\n".format(level_dir)
            )
            ok = False
        for entry in capabilities:
            if not is_reverse_dns(entry):
                sys.stderr.write(
                    "FAIL: capability id '{}' not reverse-DNS in {}\n".format(entry, level_dir)
                )
                ok = False

        refusals = coverage.get("required_refusals", [])
        if not refusals or not ensure_sorted(refusals):
            sys.stderr.write(
                "FAIL: required_refusals must be non-empty and sorted in {}\n".format(level_dir)
            )
            ok = False
        if not ensure_unique(refusals):
            sys.stderr.write("FAIL: required_refusals must be unique in {}\n".format(level_dir))
            ok = False
        for entry in refusals:
            if entry not in refusal_codes:
                sys.stderr.write(
                    "FAIL: refusal code '{}' not in canonical table ({})\n".format(entry, level_dir)
                )
                ok = False

        allow_flag = coverage.get("allow_in_principle")
        if not isinstance(allow_flag, bool):
            sys.stderr.write(
                "FAIL: allow_in_principle must be boolean in {}\n".format(level_dir)
            )
            ok = False

        determinism = coverage.get("determinism_assertions", [])
        if not determinism or not ensure_sorted(determinism):
            sys.stderr.write(
                "FAIL: determinism_assertions must be non-empty and sorted in {}\n".format(level_dir)
            )
            ok = False
        if not ensure_unique(determinism):
            sys.stderr.write(
                "FAIL: determinism_assertions must be unique in {}\n".format(level_dir)
            )
            ok = False

        scenario_header = first_content_line(paths["scenario"])
        if scenario_header != SCENARIO_HEADER:
            sys.stderr.write(
                "FAIL: scenario header mismatch in {} (expected {})\n".format(
                    level_dir, SCENARIO_HEADER
                )
            )
            ok = False

    if ok:
        print("coverage manifest validation OK")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
