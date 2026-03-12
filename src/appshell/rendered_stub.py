"""Deterministic APPSHELL-0 rendered-mode stub surface."""

from __future__ import annotations

import os

import hashlib
import json

def build_rendered_stub(product_id: str) -> dict:
    product_token = str(product_id).strip()
    if product_token == "client":
        from src.client.ui.main_menu_surface import build_client_main_menu_surface

        repo_root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
        payload = build_client_main_menu_surface(repo_root=repo_root)
        payload["mode"] = "rendered"
        payload["status"] = "ready"
        payload["deterministic_fingerprint"] = hashlib.sha256(
            json.dumps(dict(payload, deterministic_fingerprint=""), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        return payload
    return {
        "result": "complete",
        "product_id": product_token,
        "mode": "rendered",
        "status": "stub",
        "renderer_backends": ["null", "software"],
        "message": "APPSHELL-0 rendered stub is active.",
    }


__all__ = ["build_rendered_stub"]
