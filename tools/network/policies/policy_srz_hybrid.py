"""Deterministic SRZ-hybrid replication policy module (single-process multi-shard)."""

from __future__ import annotations

from net.srz import (
    advance_hybrid_tick,
    build_client_intent_envelope,
    initialize_hybrid_runtime,
    join_client_hybrid,
    prepare_hybrid_baseline,
    queue_intent_envelope,
    request_hybrid_resync,
    run_hybrid_simulation,
)


POLICY_ID_SRZ_HYBRID = "policy.net.srz_hybrid"


__all__ = [
    "POLICY_ID_SRZ_HYBRID",
    "initialize_hybrid_runtime",
    "build_client_intent_envelope",
    "queue_intent_envelope",
    "advance_hybrid_tick",
    "run_hybrid_simulation",
    "prepare_hybrid_baseline",
    "request_hybrid_resync",
    "join_client_hybrid",
]
