"""APPSHELL-1 TestX helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Sequence


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def run_wrapper_json(repo_root: str, bin_name: str, args: Sequence[str]) -> tuple[dict, dict]:
    from tools.xstack.testx.tests.appshell0_testlib import parse_json_output, run_wrapper

    report = run_wrapper(repo_root, bin_name, args)
    return report, parse_json_output(report)


def load_refusal_to_exit_registry(repo_root: str) -> dict:
    path = os.path.join(repo_root, "data", "registries", "refusal_to_exit_registry.json")
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("refusal_to_exit_registry root must be an object")
    return payload


def generate_cli_reference_text(repo_root: str) -> str:
    ensure_repo_on_path(repo_root)
    from tools.appshell.tool_generate_command_docs import generate_cli_reference

    return str(generate_cli_reference(repo_root))
