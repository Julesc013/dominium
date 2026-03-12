Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Content Portability

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






Status: draft (implementation gaps noted).


Scope: pack, save, and replay portability rules.


Authority: canonical for required contract; blockers listed below.





## Required contract


- Saves and replays MUST reference pack IDs and version constraints only.


- No file paths or platform-specific locations may appear in saves or replays.


- Unknown fields and tags MUST be preserved for forward compatibility.


- Missing capabilities MUST trigger explicit degradation or refusal.





## Current state (as-is)


- Schema contracts define forward-compatible records.


- Save/replay portability enforcement is not yet audited in engine/game code.





## Blockers to resolve in Phase 6


- Enforce pathless references in save/replay serialization.


- Ensure refusal semantics are explicit and testable.





## References


- `docs/architecture/EXECUTION_MODEL.md`


- `docs/schema/FORWARD_COMPATIBILITY.md`
