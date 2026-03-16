Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to pack manifest signature metadata, lockfile contract, SecureX policy registry, and handshake compatibility gates.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# SecureX Trust Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic trust policy evaluation for pack acceptance at setup-time and handshake-time.

## Signature Status Categories

1. `official`
   - Vendor-published and signature-verified.
2. `signed`
   - Signed and verified under accepted trust root.
3. `unsigned`
   - No signature proof.
4. `classroom-restricted`
   - Valid only for classroom policy contexts.
5. `verified`
   - Legacy-compatible verified status.
6. `revoked`
   - Explicitly forbidden.

## Trust Policy Inputs

1. `securex_policy_id`
2. resolved pack list from lockfile
3. per-pack `signature_status`
4. optional publisher allow-list
5. signature verification requirement bit

## Deterministic Verification Steps

1. Load SecureX policy by ID from compiled registry.
2. Normalize and sort lockfile pack rows by `pack_id`.
3. Evaluate each pack against policy rules:
   - required statuses
   - unsigned allowance
   - classroom restriction allowance
   - publisher allow-list (when present)
4. Emit deterministic refusal on first disallowed row.

## Enforcement Points

1. Setup/install validation:
   - verifies lockfile pack set satisfies requested SecureX policy.
2. Server handshake validation:
   - ensures client posture satisfies server profile SecureX requirement.

No silent downgrade is allowed for ranked requirements.

## Ranked vs Private

1. Ranked (`securex.policy.rank_strict`)
   - unsigned disallowed
   - signature verification required
2. Casual/Public (`securex.policy.casual_default`)
   - unsigned allowed with warnings
3. Private (`securex.policy.private_relaxed`)
   - unsigned allowed by explicit policy

## Refusal Codes

1. `refusal.net.handshake_securex_denied`
2. `refusal.ac.policy_violation`
3. `LOCKFILE_MISMATCH`
4. `PACK_INCOMPATIBLE`

## Cross-References

- `docs/net/RANKED_SERVER_GOVERNANCE.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `schemas/pack_manifest.schema.json`
- `schemas/securex_policy_registry.schema.json`
- `data/registries/securex_policy_registry.json`
