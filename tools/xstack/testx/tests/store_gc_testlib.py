"""Shared STORE-GC-0 TestX helpers."""

from __future__ import annotations

import os

from lib.store import DEFAULT_GC_POLICY_ID, REFUSAL_GC_EXPLICIT_FLAG, build_store_reachability_report, run_store_gc
from tools.lib.store_gc_common import BASELINE_DOC_REL, GC_REPORT_JSON_REL, VERIFY_REPORT_JSON_REL, build_store_gc_fixture, build_store_gc_report, write_store_gc_outputs


def ensure_assets(repo_root: str) -> dict:
    root = os.path.abspath(repo_root)
    required = (
        os.path.join(root, BASELINE_DOC_REL.replace("/", os.sep)),
        os.path.join(root, VERIFY_REPORT_JSON_REL.replace("/", os.sep)),
        os.path.join(root, GC_REPORT_JSON_REL.replace("/", os.sep)),
    )
    if all(os.path.isfile(path) for path in required):
        return build_store_gc_report(repo_root)
    return write_store_gc_outputs(repo_root)


def build_fixture(repo_root: str, name: str) -> dict:
    fixture_root = os.path.join(repo_root, "build", "tmp", "store_gc_tests", str(name or "fixture"))
    return build_store_gc_fixture(repo_root, fixture_root=fixture_root)


def reachability_fingerprint(repo_root: str) -> str:
    fixture = build_fixture(repo_root, "reachability")
    report = build_store_reachability_report(
        str(fixture.get("store_root", "")).strip(),
        repo_root=repo_root,
        install_roots=[str(fixture.get("install_root", "")).strip()],
        registry_path=str(fixture.get("registry_path", "")).strip(),
    )
    return str(report.get("deterministic_fingerprint", "")).strip()


def gc_none_result(repo_root: str) -> dict:
    fixture = build_fixture(repo_root, "gc_none")
    return run_store_gc(
        str(fixture.get("store_root", "")).strip(),
        repo_root=repo_root,
        gc_policy_id=DEFAULT_GC_POLICY_ID,
        install_roots=[str(fixture.get("install_root", "")).strip()],
        registry_path=str(fixture.get("registry_path", "")).strip(),
    )


def gc_safe_result(repo_root: str) -> tuple[dict, dict]:
    fixture = build_fixture(repo_root, "gc_safe")
    result = run_store_gc(
        str(fixture.get("store_root", "")).strip(),
        repo_root=repo_root,
        gc_policy_id="gc.safe",
        install_roots=[str(fixture.get("install_root", "")).strip()],
        registry_path=str(fixture.get("registry_path", "")).strip(),
    )
    return fixture, result


def gc_aggressive_refusal(repo_root: str) -> dict:
    fixture = build_fixture(repo_root, "gc_aggressive")
    return run_store_gc(
        str(fixture.get("store_root", "")).strip(),
        repo_root=repo_root,
        gc_policy_id="gc.aggressive",
        install_roots=[str(fixture.get("install_root", "")).strip()],
        registry_path=str(fixture.get("registry_path", "")).strip(),
        allow_aggressive=False,
    )


def gc_cross_root_fingerprints(repo_root: str) -> tuple[str, str]:
    left_fixture = build_fixture(repo_root, "cross_root_a")
    right_fixture = build_fixture(repo_root, "cross_root_b")
    left = run_store_gc(
        str(left_fixture.get("store_root", "")).strip(),
        repo_root=repo_root,
        gc_policy_id=DEFAULT_GC_POLICY_ID,
        install_roots=[str(left_fixture.get("install_root", "")).strip()],
        registry_path=str(left_fixture.get("registry_path", "")).strip(),
    )
    right = run_store_gc(
        str(right_fixture.get("store_root", "")).strip(),
        repo_root=repo_root,
        gc_policy_id=DEFAULT_GC_POLICY_ID,
        install_roots=[str(right_fixture.get("install_root", "")).strip()],
        registry_path=str(right_fixture.get("registry_path", "")).strip(),
    )
    return (
        str(dict(left.get("gc_report") or {}).get("deterministic_fingerprint", "")).strip(),
        str(dict(right.get("gc_report") or {}).get("deterministic_fingerprint", "")).strip(),
    )


__all__ = [
    "REFUSAL_GC_EXPLICIT_FLAG",
    "build_fixture",
    "ensure_assets",
    "gc_aggressive_refusal",
    "gc_cross_root_fingerprints",
    "gc_none_result",
    "gc_safe_result",
    "reachability_fingerprint",
]
