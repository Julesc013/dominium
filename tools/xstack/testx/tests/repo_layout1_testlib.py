"""Helpers for REPO-LAYOUT-1 TestX coverage."""

from __future__ import annotations

import os
import sys


def ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def build_context(repo_root: str, product_id: str, raw_args: list[str], *, executable_path: str = "") -> dict:
    ensure_repo_root(repo_root)
    from tools.release.entrypoint_unify_common import bootstrap_context_for_product

    return bootstrap_context_for_product(
        repo_root,
        product_id,
        raw_args,
        executable_path=executable_path,
    )


def redirect_legacy(repo_root: str, raw_path: str) -> dict:
    ensure_repo_root(repo_root)
    from compat.shims import redirect_legacy_path

    return redirect_legacy_path(
        raw_path,
        repo_root=repo_root,
        executable_path=os.path.join(repo_root, "dist", "bin", "dom"),
        emit_warning=False,
    )


def run_legacy_validator(repo_root: str, *, strict: bool = False) -> dict:
    ensure_repo_root(repo_root)
    from compat.shims import run_legacy_validate_all

    return run_legacy_validate_all(
        repo_root=repo_root,
        strict=bool(strict),
        profile="STRICT" if bool(strict) else "FAST",
    )


def warning_payload() -> dict:
    from compat.shims.common import build_deprecation_warning

    return build_deprecation_warning(
        shim_id="shim.test.warning",
        warning_code="deprecated_test_usage",
        message_key="warn.deprecated_test_usage",
        original_surface="legacy.surface",
        replacement_surface="canonical.surface",
        details={"alpha": "1", "beta": "2"},
    )
