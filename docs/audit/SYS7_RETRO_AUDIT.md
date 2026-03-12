Status: BASELINE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-7 retro-consistency audit for system-level forensics and explain coverage.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SYS7 Retro Audit

## Existing Explain Coverage (System Domain)
- Existing system explain contracts already cover:
  - `system.forced_expand`
  - `system.warning`
  - `system.failure`
  - `system.safety_shutdown`
  - `system.output_degradation`
  - `system.tier_transition_refusal`
  - `system.certification_failure`
  - `system.certificate_revocation`
- Runtime already auto-generates explain artifacts for:
  - macro forced expand requests,
  - reliability warning/failure outputs,
  - certification failure/revocation pathways.

## Gap Audit Against SYS-7 Targets
- Forced expand: covered.
- Capsule error-bound exceeded: not explicitly declared as dedicated explain contract/event kind.
- Certificate revoked: covered (`system.certificate_revocation`).
- Reliability failure_event: covered (`system.failure`).
- System invariant violation: no dedicated explicit contract for direct invariant-violation explain event.
- Compliance failure (system-level): no dedicated explicit contract/event kind separate from certification failure.

## Missing Contracts Added (Registry-Only for Phase 0)
- Added explain contracts for:
  - `system.capsule_error_bound_exceeded`
  - `system.invariant_violation`
  - `system.compliance_failure`

These are declarations only in this phase; runtime integration is completed in later SYS-7 phases.

## Migration Notes
- Consolidate ad hoc system explain generation behind a dedicated deterministic forensics process.
- Ensure bounded cause-chain selection is shared across forced expand/failure/certification pathways.
- Ensure epistemic redaction policy is explicit by requester role (diegetic vs inspector vs admin).
- Keep all explain outputs derived/compactable and anchored to canonical event rows.
