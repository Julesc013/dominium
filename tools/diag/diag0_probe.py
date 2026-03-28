"""Deterministic DIAG-0 capture/replay probe helpers."""

from __future__ import annotations

import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from compat import emit_product_descriptor  # noqa: E402
from diag import verify_repro_bundle, write_repro_bundle  # noqa: E402
from tools.mvp.runtime_bundle import MVP_PACK_LOCK_REL  # noqa: E402


def capture_diag0_bundle(
    repo_root: str = REPO_ROOT_HINT,
    *,
    out_dir: str = "",
    tick_window: int = 16,
    include_views: bool = False,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))
    descriptor = emit_product_descriptor(repo_root_abs, product_id="client")
    bundle_dir = out_dir or os.path.join(repo_root_abs, "build", "diag0", "fixture")
    return write_repro_bundle(
        repo_root=repo_root_abs,
        created_by_product_id="client",
        build_id=str(dict(descriptor.get("version") or {}).get("build_id", "")).strip(),
        out_dir=bundle_dir,
        window=tick_window,
        include_views=include_views,
        descriptor_payloads=[descriptor],
        pack_lock_path=MVP_PACK_LOCK_REL,
        semantic_contract_registry_hash=str(
            dict(dict(descriptor.get("descriptor") or {}).get("extensions", {}) or {}).get(
                "official.semantic_contract_registry_hash",
                "",
            )
        ).strip(),
        seed="0",
        session_template_id="session.mvp_default",
        proof_anchor_rows=[],
        canonical_event_rows=[
            {"event_id": "event.capture.0001", "tick": 1, "kind": "diag.capture", "product_id": "client"},
            {"event_id": "event.capture.0002", "tick": 2, "kind": "diag.capture", "product_id": "client"},
        ],
        log_events=[
            {"event_id": "log.0000000000000001", "tick": 1, "category": "diag", "message_key": "diag.capture.written", "severity": "info"},
            {"event_id": "log.0000000000000002", "tick": 2, "category": "compat", "message_key": "compat.negotiation.result", "severity": "info"},
        ],
        view_fingerprints=[{"view_id": "view.fixture.0001", "fingerprint": "fixture.view.hash"}] if include_views else [],
    )


def replay_diag0_bundle(repo_root: str = REPO_ROOT_HINT, *, bundle_path: str, tick_window: int = 16) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))
    return verify_repro_bundle(repo_root=repo_root_abs, bundle_path=bundle_path, tick_window=tick_window)


__all__ = [
    "capture_diag0_bundle",
    "replay_diag0_bundle",
]
