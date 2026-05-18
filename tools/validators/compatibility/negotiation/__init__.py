"""Reusable CAP-NEG negotiation engine surfaces."""

from .degrade_enforcer import (
    DEFAULT_UI_CAPABILITY_PREFERENCE,
    REFUSAL_COMPAT_FEATURE_DISABLED,
    build_compat_status_payload,
    build_degrade_runtime_state,
    enforce_negotiated_capability,
)
from .negotiation_engine import (
    negotiate_product_endpoints,
    verify_recorded_negotiation,
)

__all__ = [
    "DEFAULT_UI_CAPABILITY_PREFERENCE",
    "REFUSAL_COMPAT_FEATURE_DISABLED",
    "build_compat_status_payload",
    "build_degrade_runtime_state",
    "enforce_negotiated_capability",
    "negotiate_product_endpoints",
    "verify_recorded_negotiation",
]
