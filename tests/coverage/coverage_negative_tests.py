import argparse
import os
import sys


def load_banlist(path):
    tokens = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            tokens.append(stripped.lower())
    return tokens


def iter_source_files(repo_root):
    for base in ("engine", "game"):
        root = os.path.join(repo_root, base)
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                if not (name.endswith(".c") or name.endswith(".h") or name.endswith(".cpp") or name.endswith(".hpp")):
                    continue
                yield os.path.join(dirpath, name)


def main():
    parser = argparse.ArgumentParser(description="No era/tech gating in runtime code.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    banlist_path = os.path.join(repo_root, "tests", "coverage", "era_banlist.txt")
    tokens = load_banlist(banlist_path)
    if not tokens:
        sys.stderr.write("FAIL: empty banlist\n")
        return 1

    hits = []
    for path in iter_source_files(repo_root):
        try:
            data = open(path, "rb").read().lower()
        except Exception:
            continue
        for token in tokens:
            if token.encode("ascii") in data:
                hits.append((path, token))

    if hits:
        sys.stderr.write("FAIL: era/tech gating tokens found:\n")
        for path, token in hits:
            sys.stderr.write("  {} -> {}\n".format(path, token))
        return 1

    print("coverage negative tests OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
