Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Refusal UX

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Contract
- Refusals are deterministic, structured outcomes from lawful validation.
- Interaction UX surfaces refusal details consistently across CLI/TUI/software renderer overlays.

## Required Fields
- `reason_code`
- `message`
- `remediation_hint`
- `relevant_ids` (target/process/affordance/envelope context when available)

## Display Rules
- Always display `reason_code`.
- Show a short human message and remediation hint.
- Keep deterministic ordering of `relevant_ids` keys.

## Ranked Server Behavior
- Sensitive context may be reduced by server policy.
- `reason_code` is still shown to support deterministic debugging/refusal parity.

## Common Interaction Refusals
- `refusal.preview.budget_exceeded`
- `refusal.preview.forbidden_by_epistemics`
- `refusal.net.authority_violation`
- `refusal.net.envelope_invalid`
- domain-specific refusal codes returned by process execution gates
