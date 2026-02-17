Status: AUTHORITATIVE
Last Reviewed: 2026-02-16
Version: 1.0.0

# Territory and Claims

## Territory Model
- Territory is represented as `assembly.territory.*`.
- `region_scope` can be object-based and/or spatial bounds.
- `owner_faction_id` is nullable.
- `claim_status` is one of: `unclaimed`, `claimed`, `contested`.

## Claim Mechanics (Structural)
- Claims are process-only (`process.territory_claim`, `process.territory_release`).
- If unclaimed and valid: owner becomes claimant and status becomes `claimed`.
- If claimed by a different faction: status becomes `contested`.
- No war, occupation, or damage semantics are introduced in CIV-1.

## Deterministic Conflict Resolution
- Claim resolution order is deterministic:
  - `(tick, territory_id, faction_id, intent_id)`.
- Release operations are owner-validated and deterministic.
- Provenance events for claim/release operations are emitted in sorted order.

## Epistemic Constraint
- Territory knowledge visible to clients is still governed by LawProfile + EpistemicPolicy.
- CIV-1 does not grant omniscient map access.

