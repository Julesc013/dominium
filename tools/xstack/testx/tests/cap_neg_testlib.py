"""Shared CAP-NEG-0 negotiation fixtures."""

from __future__ import annotations

import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def build_default_pair(repo_root: str) -> tuple[dict, dict]:
    ensure_repo_on_path(repo_root)
    from src.compat import build_default_endpoint_descriptor

    client = build_default_endpoint_descriptor(
        repo_root,
        product_id="client",
        product_version="0.0.0+test.client",
    )
    server = build_default_endpoint_descriptor(
        repo_root,
        product_id="server",
        product_version="0.0.0+test.server",
    )
    return dict(client), dict(server)


def negotiate(repo_root: str, client: dict, server: dict, *, allow_read_only: bool = False) -> dict:
    ensure_repo_on_path(repo_root)
    from src.compat import negotiate_endpoint_descriptors

    return negotiate_endpoint_descriptors(
        repo_root,
        dict(client),
        dict(server),
        allow_read_only=allow_read_only,
        chosen_contract_bundle_hash="hash.contract.bundle.test",
    )
