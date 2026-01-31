import argparse
import os
import subprocess
import sys

from invariant_utils import is_override_active


AUTHORITATIVE_DIRS = [
    os.path.join("engine", "modules", "core"),
    os.path.join("engine", "modules", "sim"),
    os.path.join("engine", "modules", "world"),
    os.path.join("game", "core"),
    os.path.join("game", "rules"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: no enum values named OTHER/CUSTOM/UNKNOWN/MISC/UNSPECIFIED.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-ENUM-NO-OTHER"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    script = os.path.join(repo_root, "scripts", "ci", "check_forbidden_enums.py")
    cmd = [sys.executable, script, "--mode", "fail"]
    for root in AUTHORITATIVE_DIRS:
        cmd.extend(["--roots", os.path.join(repo_root, root)])
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("{}: forbidden enum tokens detected".format(invariant_id))
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode

    if result.stdout:
        print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
