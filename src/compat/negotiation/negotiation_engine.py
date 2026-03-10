"""Reusable deterministic negotiation engine wrappers."""

from __future__ import annotations

from typing import Mapping

from src.compat.capability_negotiation import negotiate_endpoint_descriptors, verify_negotiation_record


def negotiate_product_endpoints(
    repo_root: str,
    endpoint_a: Mapping[str, object],
    endpoint_b: Mapping[str, object],
    *,
    allow_read_only: bool = False,
    chosen_contract_bundle_hash: str = "",
) -> dict:
    return negotiate_endpoint_descriptors(
        repo_root,
        dict(endpoint_a or {}),
        dict(endpoint_b or {}),
        allow_read_only=bool(allow_read_only),
        chosen_contract_bundle_hash=str(chosen_contract_bundle_hash or "").strip(),
    )


def verify_recorded_negotiation(
    repo_root: str,
    negotiation_record: Mapping[str, object],
    endpoint_a: Mapping[str, object],
    endpoint_b: Mapping[str, object],
    *,
    allow_read_only: bool = False,
    chosen_contract_bundle_hash: str = "",
) -> dict:
    return verify_negotiation_record(
        repo_root,
        dict(negotiation_record or {}),
        dict(endpoint_a or {}),
        dict(endpoint_b or {}),
        allow_read_only=bool(allow_read_only),
        chosen_contract_bundle_hash=str(chosen_contract_bundle_hash or "").strip(),
    )
