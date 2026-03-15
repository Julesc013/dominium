"""Shared ARCH-AUDIT-2 TestX helpers."""

from __future__ import annotations

import os

from tools.audit.arch_audit_common import (
    build_arch_audit2_report,
    run_arch_audit,
    scan_dist_bundle_composition,
    scan_trust_bypass,
)


def build_report(repo_root: str) -> dict:
    return build_arch_audit2_report(run_arch_audit(repo_root))


def _fixture_rel(name: str) -> str:
    return "build/tmp/testx_arch_audit2/{}".format(str(name).strip())


def _write_fixture(repo_root: str, name: str, text: str) -> str:
    rel_path = _fixture_rel(name)
    abs_path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text).replace("\r\n", "\n"))
    return rel_path


def hardcoded_bundle_scan(repo_root: str) -> dict:
    rel_path = _write_fixture(
        repo_root,
        "fixture_hardcoded_bundle.py",
        "\n".join(
            [
                "def build_bundle():",
                "    selected_components = ['binary.client', 'binary.server', 'pack.earth.procedural']",
                "    return selected_components",
                "",
            ]
        ),
    )
    return scan_dist_bundle_composition(repo_root, override_paths=[rel_path])


def trust_bypass_scan(repo_root: str) -> dict:
    rel_path = _write_fixture(
        repo_root,
        "fixture_trust_bypass.py",
        "\n".join(
            [
                "def verify(content_hash, trust_policy_id):",
                "    local_dev_bypass = True",
                "    if trust_policy_id:",
                "        return {'result': 'complete', 'content_hash': content_hash}",
                "    return {'result': 'complete'}",
                "",
            ]
        ),
    )
    return scan_trust_bypass(repo_root, override_paths=[rel_path])


__all__ = [
    "build_report",
    "hardcoded_bundle_scan",
    "trust_bypass_scan",
]
