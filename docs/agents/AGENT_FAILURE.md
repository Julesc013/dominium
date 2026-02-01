Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# AGENT FAILURE





Failure MUST be modeled as normal: processes may fail, partially succeed, or cause side effects.


Failure MUST affect agent memory, future planning, and goal status (deferral/abandonment).


Failure MUST generate history artifacts with timestamps and provenance.


Failure MUST NOT be silently retried or erased.





Failure handling MUST NOT assume human judgment or player intervention.


Failure handling MUST NOT use "AI magic" to auto-correct outcomes.





References:


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
