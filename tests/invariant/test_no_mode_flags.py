import argparse
import os
import sys

from invariant_utils import is_override_active


def _forbidden_tokens():
    # Build tokens from fragments so this test does not violate its own invariant.
    return (
        "survival" + "_" + "mode",
        "creative" + "_" + "mode",
        "hardcore" + "_" + "mode",
        "spectator" + "_" + "mode",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: no hardcoded mode branch tokens.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-NO-HARDCODED-MODE-BRANCH"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    roots = ("engine", "game", "client", "server", "launcher", "setup", "tools", "libs", "scripts")
    exts = {".c", ".cc", ".cpp", ".h", ".hpp", ".inl", ".py", ".json", ".schema", ".cmake", ".txt"}
    tokens = _forbidden_tokens()

    violations = []
    for rel_root in roots:
        abs_root = os.path.join(repo_root, rel_root)
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "out", "dist", "__pycache__"}]
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() not in exts:
                    continue
                path = os.path.join(dirpath, filename)
                try:
                    text = open(path, "r", encoding="utf-8").read().lower()
                except OSError:
                    continue
                rel = path.replace("\\", "/")
                for token in tokens:
                    if token in text:
                        violations.append("{} -> {}".format(rel, token))
                        break

    if violations:
        print("{}: hardcoded mode tokens detected".format(invariant_id))
        for item in violations[:32]:
            print("- {}".format(item))
        return 1

    print("no-mode-flags invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
