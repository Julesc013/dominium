Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# PLAYER INTENT MODEL

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






Player input MUST be modeled as intent proposals, goal updates, plan confirmations, or process requests.


Intent MUST NOT mutate state directly.


All intent MUST be validated against authority, epistemics, and physical constraints.


Intent refusal MUST be explicit and recorded.





Intent handling MUST be deterministic and headless-safe.


Intent handling MUST NOT assume UI presence or direct manipulation.





References:


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
