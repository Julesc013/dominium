import argparse
import os
import subprocess
import sys


def run(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, shell=False)
    return proc.returncode


def git_status(repo_root):
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return None
    return proc.stdout.splitlines()


def main():
    parser = argparse.ArgumentParser(description="Verify IDE projection regeneration is clean.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    parser.add_argument("--preset", action="append", dest="presets", help="CMake preset to run")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    presets = args.presets or []
    if not presets:
        sys.stderr.write("No presets provided. Use --preset.\n")
        return 2

    for preset in presets:
        ret = run(["cmake", "--preset", preset], cwd=repo_root)
        if ret != 0:
            sys.stderr.write(f"Preset failed: {preset}\n")
            return ret

    status = git_status(repo_root)
    if status is None:
        return 1

    violations = []
    for line in status:
        if not line:
            continue
        path = line[3:].strip()
        norm = path.replace("\\", "/")
        if not norm.startswith("ide/"):
            violations.append(norm)

    if violations:
        for path in violations:
            sys.stderr.write(f"{path}:1: projection regen modified authoritative path\n")
        return 1

    print("Projection regeneration clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
