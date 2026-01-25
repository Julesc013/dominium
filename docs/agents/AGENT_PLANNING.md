# AGENT PLANNING

Planning MUST select and order processes based on goals, constraints, and subjective knowledge.
Planning MUST consume a bounded compute budget, respect time horizons, and be deterministic.
Planning MUST be interruptible and resumable without changing results for identical inputs.

Plans MUST include ordered/partial process attempts, required capabilities/authority,
expected resource usage, expected epistemic gaps, confidence estimates, and explicit failure points.
Plans MUST NOT assume omniscience, unbounded search, or guaranteed success.

Planning MUST NOT assume human cognition, player agency, or UI-driven intent.
Planning MUST NOT depend on "AI magic" or opaque intelligence.

References:
- docs/arch/INVARIANTS.md
- docs/arch/REALITY_LAYER.md
