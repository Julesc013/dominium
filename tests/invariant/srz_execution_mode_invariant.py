import argparse
import os
import re
import sys


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: SRZ modes are fixed to server/delegated/dormant.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    header_path = os.path.join(repo_root, "engine", "include", "domino", "world", "srz_fields.h")
    if not os.path.isfile(header_path):
        sys.stderr.write("FAIL: missing srz_fields.h\n")
        return 1

    with open(header_path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()

    start_idx = None
    end_idx = None
    for idx, line in enumerate(lines):
        if "enum dom_srz_mode" in line:
            start_idx = idx
            continue
        if start_idx is not None and "};" in line:
            end_idx = idx
            break

    ok = True
    ok = ok and require(start_idx is not None, "dom_srz_mode enum not found")
    ok = ok and require(end_idx is not None, "dom_srz_mode enum end not found")
    if not ok:
        return 1

    mode_lines = lines[start_idx:end_idx + 1]
    token_re = re.compile(r"\bDOM_SRZ_MODE_[A-Z0-9_]+")
    tokens = set()
    for line in mode_lines:
        for match in token_re.findall(line):
            tokens.add(match)

    expected = {
        "DOM_SRZ_MODE_UNSET",
        "DOM_SRZ_MODE_SERVER",
        "DOM_SRZ_MODE_DELEGATED",
        "DOM_SRZ_MODE_DORMANT",
    }
    ok = ok and require(tokens == expected, "SRZ modes must be exactly {}".format(sorted(expected)))

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
