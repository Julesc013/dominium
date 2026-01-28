import argparse
import json
import os
import sys


def repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def load_manifest(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive/quarantine presence guard.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    manifest_path = os.path.join(repo_root, "tests", "contract", "archive_manifest.json")
    if not os.path.isfile(manifest_path):
        print("missing archive manifest: {}".format(repo_rel(repo_root, manifest_path)))
        return 1

    manifest = load_manifest(manifest_path)
    violations = []
    for entry in manifest.get("archives", []):
        path = os.path.join(repo_root, entry.get("path", ""))
        readme = os.path.join(repo_root, entry.get("readme", ""))
        if not os.path.isdir(path):
            violations.append("missing archived path: {}".format(repo_rel(repo_root, path)))
        if not os.path.isfile(readme):
            violations.append("missing archive README: {}".format(repo_rel(repo_root, readme)))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Archive/quarantine presence guard OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
