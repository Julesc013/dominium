#!/usr/bin/env python3
import argparse
import json
import os

from dompkg_lib import DomPkgError, refusal_payload, verify_package


def _iter_packages(root: str):
    for dirpath, _dirs, files in os.walk(root):
        files.sort()
        for name in files:
            if name.lower().endswith(".dompkg"):
                yield os.path.abspath(os.path.join(dirpath, name))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify all dompkg artifacts in a directory tree.")
    parser.add_argument("--pkg-dir", required=True)
    parser.add_argument("--trust-policy", default="")
    args = parser.parse_args()

    pkg_dir = os.path.abspath(args.pkg_dir)
    if not os.path.isdir(pkg_dir):
        print(json.dumps(refusal_payload("refuse.invalid_input", "pkg-dir missing", {"pkg_dir": pkg_dir}), indent=2))
        return 3

    packages = list(_iter_packages(pkg_dir))
    results = []
    try:
        for pkg_path in packages:
            result = verify_package(pkg_path, args.trust_policy)
            results.append({
                "pkg_path": pkg_path.replace("\\", "/"),
                "content_hash": result.get("content_hash"),
                "file_count": int(result.get("file_count", 0)),
            })
    except DomPkgError as exc:
        print(json.dumps(refusal_payload(exc.code, exc.message, exc.details), indent=2))
        return 3
    except Exception as exc:  # pragma: no cover
        print(json.dumps(refusal_payload("refuse.internal_error", "pkg verify failed", {"error": str(exc)}), indent=2))
        return 1

    print(json.dumps({
        "result": "ok",
        "pkg_dir": pkg_dir.replace("\\", "/"),
        "package_count": len(results),
        "packages": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
