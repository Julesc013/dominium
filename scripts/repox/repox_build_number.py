#!/usr/bin/env python3
import argparse
import os
import sys


def read_build_number(path: str) -> int:
    if not os.path.isfile(path):
        return 0
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read().strip()
    if not text:
        return 0
    try:
        return int(text)
    except ValueError:
        return 0


def write_build_number(path: str, value: int) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(value))
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX build number helper.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--bump", action="store_true")
    parser.add_argument("--read", action="store_true")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    path = os.path.join(repo_root, ".dominium_build_number")

    if args.read or (not args.read and not args.bump):
        value = read_build_number(path)
        sys.stdout.write(str(value))
        sys.stdout.write("\n")
        return 0

    if args.bump:
        value = read_build_number(path) + 1
        write_build_number(path, value)
        sys.stdout.write(str(value))
        sys.stdout.write("\n")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
