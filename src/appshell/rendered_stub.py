"""Deterministic APPSHELL-0 rendered-mode stub surface."""

from __future__ import annotations


def build_rendered_stub(product_id: str) -> dict:
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "mode": "rendered",
        "status": "stub",
        "renderer_backends": ["null", "software"],
        "message": "APPSHELL-0 rendered stub is active.",
    }


__all__ = ["build_rendered_stub"]
