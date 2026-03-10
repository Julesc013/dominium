"""Shared APPSHELL-0 TestX helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Sequence


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def wrapper_map(repo_root: str) -> dict[str, str]:
    from tools.xstack.testx.tests.cap_neg1_testlib import product_bin_map

    return product_bin_map(repo_root)


def run_wrapper(repo_root: str, bin_name: str, args: Sequence[str]) -> dict:
    wrapper_path = os.path.join(repo_root, "dist", "bin", str(bin_name))
    result = subprocess.run(
        [sys.executable, wrapper_path] + list(args or []),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=repo_root,
    )
    return {
        "bin_name": str(bin_name),
        "returncode": int(result.returncode or 0),
        "stdout": str(result.stdout or ""),
        "stderr": str(result.stderr or ""),
    }


def parse_json_output(report: dict) -> dict:
    payload = json.loads(str(report.get("stdout", "")).strip())
    if not isinstance(payload, dict):
        raise ValueError("wrapper did not emit a JSON object")
    return payload


def appshell_surface_fingerprint(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.xstack.compatx.canonical_json import canonical_sha256

    rows = []
    for bin_name, product_id in sorted(wrapper_map(repo_root).items()):
        help_report = run_wrapper(repo_root, bin_name, ["--help"])
        version_report = run_wrapper(repo_root, bin_name, ["version"])
        descriptor_report = run_wrapper(repo_root, bin_name, ["descriptor"])
        rows.append(
            {
                "bin_name": str(bin_name),
                "product_id": str(product_id),
                "help_returncode": int(help_report.get("returncode", 0)),
                "help_text": str(help_report.get("stdout", "")).replace("\r\n", "\n"),
                "version_payload": parse_json_output(version_report),
                "descriptor_payload": parse_json_output(descriptor_report),
            }
        )
    payload = {"rows": rows}
    return {
        "rows": rows,
        "appshell_hash": canonical_sha256(payload),
    }

