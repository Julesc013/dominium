"""Reusable transport-agnostic handshake helpers."""

from .handshake_engine import (
    REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
    REFUSAL_CONNECTION_NO_NEGOTIATION,
    build_compat_refusal,
    build_handshake_message,
    build_session_begin_payload,
)

__all__ = [
    "REFUSAL_CONNECTION_NEGOTIATION_MISMATCH",
    "REFUSAL_CONNECTION_NO_NEGOTIATION",
    "build_compat_refusal",
    "build_handshake_message",
    "build_session_begin_payload",
]
