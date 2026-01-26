import argparse
import os
import sys


REQUIRED_COMMON_TOKENS = [
    "json.dumps",
    "sort_keys=True",
    'separators=(",", ":")',
]

REQUIRED_WD_TOKENS = [
    "round_trip_json",
    "sort_keys=True",
    'separators=(",", ":")',
    "ensure_ascii=True",
]


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser(description="Deterministic hash checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    common_path = os.path.join(repo_root, "tools", "worldgen_offline", "_common.py")
    wd_path = os.path.join(repo_root, "tools", "worldgen_offline", "world_definition_lib.py")

    if not os.path.isfile(common_path):
        print("missing _common.py")
        return 1
    if not os.path.isfile(wd_path):
        print("missing world_definition_lib.py")
        return 1

    common_text = read_text(common_path)
    for token in REQUIRED_COMMON_TOKENS:
        if token not in common_text:
            print("common hash missing token: {}".format(token))
            return 1

    wd_text = read_text(wd_path)
    for token in REQUIRED_WD_TOKENS:
        if token not in wd_text:
            print("worlddef hash missing token: {}".format(token))
            return 1

    print("Deterministic hash checks OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
