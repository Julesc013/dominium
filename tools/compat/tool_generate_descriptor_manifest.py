#!/usr/bin/env python3
"""Generate deterministic offline descriptor manifest from dist/bin wrappers."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.compat.descriptor import product_descriptor_bin_names  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _candidate_bin_paths(dist_root: str, bin_names: List[str]) -> List[tuple[str, str]]:
    out: List[tuple[str, str]] = []
    for name in sorted(set(bin_names)):
        abs_path = os.path.join(dist_root, "bin", name)
        if os.path.isfile(abs_path):
            out.append((name, abs_path))
    return out


def _run_descriptor(wrapper_path: str) -> dict:
    result = subprocess.run(
        [sys.executable, wrapper_path, "--descriptor"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    stdout = str(result.stdout or "").strip()
    if int(result.returncode or 0) != 0:
        raise ValueError("descriptor wrapper failed: {}".format(os.path.basename(wrapper_path)))
    payload = json.loads(stdout)
    if not isinstance(payload, dict):
        raise ValueError("descriptor wrapper returned invalid JSON object")
    return payload


def _write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate offline endpoint descriptor manifest from dist/bin.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dist-root", default="dist")
    parser.add_argument("--output-path", default=os.path.join("dist", "manifests", "endpoint_descriptors.json"))
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    dist_root = os.path.normpath(os.path.abspath(os.path.join(repo_root, str(args.dist_root))))
    output_path = os.path.normpath(os.path.abspath(os.path.join(repo_root, str(args.output_path))))

    rows = []
    for bin_name, wrapper_path in _candidate_bin_paths(dist_root, product_descriptor_bin_names(repo_root)):
        descriptor = _run_descriptor(wrapper_path)
        rows.append(
            {
                "bin_name": str(bin_name),
                "product_id": str(descriptor.get("product_id", "")).strip(),
                "product_version": str(descriptor.get("product_version", "")).strip(),
                "descriptor_hash": canonical_sha256(descriptor),
                "descriptor": descriptor,
            }
        )

    rows = sorted(rows, key=lambda row: (str(row.get("bin_name", "")), str(row.get("product_id", ""))))
    payload = {
        "schema_version": "1.0.0",
        "manifest_id": "manifest.endpoint_descriptors.dist",
        "dist_root": dist_root.replace("\\", "/"),
        "descriptors": rows,
        "deterministic_fingerprint": "",
        "extensions": {
            "official.source": "CAP-NEG-1"
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    _write_json(output_path, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
