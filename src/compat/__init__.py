"""Compatibility helpers."""

from .capability_negotiation import (
    COMPAT_MODE_DEGRADED,
    COMPAT_MODE_FULL,
    COMPAT_MODE_READ_ONLY,
    COMPAT_MODE_REFUSE,
    READ_ONLY_LAW_PROFILE_ID,
    build_default_endpoint_descriptor,
    build_endpoint_descriptor,
    negotiate_endpoint_descriptors,
    verify_negotiation_record,
)

__all__ = [
    "COMPAT_MODE_DEGRADED",
    "COMPAT_MODE_FULL",
    "COMPAT_MODE_READ_ONLY",
    "COMPAT_MODE_REFUSE",
    "READ_ONLY_LAW_PROFILE_ID",
    "build_default_endpoint_descriptor",
    "build_endpoint_descriptor",
    "negotiate_endpoint_descriptors",
    "verify_negotiation_record",
]
