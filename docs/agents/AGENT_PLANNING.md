Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

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


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
