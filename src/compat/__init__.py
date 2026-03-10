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
from .handshake import (
    REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
    REFUSAL_CONNECTION_NO_NEGOTIATION,
    build_compat_refusal,
    build_handshake_message,
    build_session_begin_payload,
)
from .negotiation import (
    negotiate_product_endpoints,
    verify_recorded_negotiation,
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
    "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH",
    "REFUSAL_CONNECTION_NO_NEGOTIATION",
    "READ_ONLY_LAW_PROFILE_ID",
    "build_compat_refusal",
    "build_default_endpoint_descriptor",
    "build_endpoint_descriptor",
    "build_handshake_message",
    "build_product_build_metadata",
    "build_product_descriptor",
    "build_session_begin_payload",
    "descriptor_json_text",
    "emit_product_descriptor",
    "negotiate_endpoint_descriptors",
    "negotiate_product_endpoints",
    "product_descriptor_bin_names",
    "verify_recorded_negotiation",
    "verify_negotiation_record",
    "write_descriptor_file",
]
