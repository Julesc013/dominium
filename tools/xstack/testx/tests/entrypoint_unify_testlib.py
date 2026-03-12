"""Helpers for ENTRYPOINT-UNIFY-0 TestX coverage."""

from __future__ import annotations

from tools.release.entrypoint_unify_common import (
    SAMPLE_ARGS,
    bootstrap_context_for_product,
    build_entrypoint_unify_report,
    entrypoint_unify_violations,
)
from tools.xstack.compatx.canonical_json import canonical_json_text


def build_report(repo_root: str) -> dict:
    return build_entrypoint_unify_report(repo_root)


def canonical_report_text(repo_root: str) -> str:
    return canonical_json_text(build_report(repo_root))


def violations(repo_root: str) -> list[dict]:
    return entrypoint_unify_violations(repo_root)


def context_for_product(repo_root: str, product_id: str, raw_args: list[str] | None = None) -> dict:
    return bootstrap_context_for_product(repo_root, product_id, raw_args)


def sample_args_for(product_id: str) -> list[str]:
    return list(SAMPLE_ARGS.get(str(product_id).strip(), []))
