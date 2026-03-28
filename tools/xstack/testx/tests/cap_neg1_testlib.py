"""Shared CAP-NEG-1 endpoint descriptor fixtures."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def product_bin_map(repo_root: str) -> dict[str, str]:
    ensure_repo_on_path(repo_root)
    from compat.descriptor import product_capability_default_rows_by_id
    from compat.capability_negotiation import load_product_registry

    payload, error = load_product_registry(repo_root)
    if error:
        return {}
    defaults, defaults_error = product_capability_default_rows_by_id(repo_root)
    if defaults_error:
        return {}
    record = dict(payload.get("record") or {})
    rows = list(record.get("products") or [])
    out: dict[str, str] = {}
    for row in rows:
        row_map = dict(row or {})
        product_id = str(row_map.get("product_id", "")).strip()
        if not product_id or product_id not in defaults:
            continue
        extensions = dict(row_map.get("extensions") or {})
        for name in sorted(set(str(item).strip() for item in list(extensions.get("official.dist_bin_names") or []) if str(item).strip())):
            out[name] = product_id
    return dict(sorted(out.items()))


def emit_descriptor_via_wrapper(repo_root: str, bin_name: str) -> dict:
    wrapper_path = os.path.join(repo_root, "dist", "bin", str(bin_name))
    result = subprocess.run(
        [sys.executable, wrapper_path, "--descriptor"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=repo_root,
    )
    if int(result.returncode or 0) != 0:
        raise ValueError("wrapper failed for {}".format(str(bin_name)))
    payload = json.loads(str(result.stdout or "").strip())
    if not isinstance(payload, dict):
        raise ValueError("descriptor output is not an object for {}".format(str(bin_name)))
    return payload


def emit_descriptor(repo_root: str, product_id: str) -> dict:
    ensure_repo_on_path(repo_root)
    from compat.descriptor import build_product_descriptor

    return build_product_descriptor(repo_root, product_id=str(product_id))


def generate_manifest(repo_root: str) -> tuple[dict, str]:
    build_root = os.path.join(repo_root, "build")
    os.makedirs(build_root, exist_ok=True)
    output_dir = tempfile.mkdtemp(prefix="cap_neg1_manifest_", dir=build_root)
    output_path = os.path.join(output_dir, "endpoint_descriptors.json")
    tool_path = os.path.join(repo_root, "tools", "compat", "tool_generate_descriptor_manifest.py")
    result = subprocess.run(
        [sys.executable, tool_path, "--repo-root", repo_root, "--output-path", output_path],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=repo_root,
    )
    if int(result.returncode or 0) != 0:
        raise ValueError("descriptor manifest tool failed")
    with open(output_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload, output_path
