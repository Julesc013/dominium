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
from .descriptor import (
    build_product_build_metadata,
    build_product_descriptor,
    descriptor_json_text,
    emit_product_descriptor,
    product_descriptor_bin_names,
    write_descriptor_file,
)

__all__ = [
    "COMPAT_MODE_DEGRADED",
    "COMPAT_MODE_FULL",
    "COMPAT_MODE_READ_ONLY",
    "COMPAT_MODE_REFUSE",
    "READ_ONLY_LAW_PROFILE_ID",
    "build_default_endpoint_descriptor",
    "build_endpoint_descriptor",
    "build_product_build_metadata",
    "build_product_descriptor",
    "descriptor_json_text",
    "emit_product_descriptor",
    "negotiate_endpoint_descriptors",
    "product_descriptor_bin_names",
    "verify_negotiation_record",
    "write_descriptor_file",
]
