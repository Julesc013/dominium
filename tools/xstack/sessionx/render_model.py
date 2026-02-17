"""SessionX wrapper for the canonical RenderModel adapter."""

from __future__ import annotations

from typing import Dict

from src.client.render import build_render_model as _build_render_model


def build_render_model(
    perceived_model: dict,
    registry_payloads: dict | None = None,
    pack_lock_hash: str = "",
    physics_profile_id: str = "",
) -> Dict[str, object]:
    return _build_render_model(
        perceived_model=dict(perceived_model or {}),
        registry_payloads=dict(registry_payloads or {}),
        pack_lock_hash=str(pack_lock_hash or ""),
        physics_profile_id=str(physics_profile_id or ""),
    )
