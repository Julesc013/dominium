Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Trust Boundaries

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Boundary Summary

- `server_authority` is the authoritative trust root for intent validation and state acceptance.
- `engine_core` and `game_logic` are authoritative execution consumers, not policy mutators.
- `client_renderer` is projection-only and cannot access server-only truth without entitlement.
- `tools` are bounded operators with explicit invocation requirements.
- `packs` are untrusted until validated, hash-pinned, and signature-verified.
- `controlx` is bounded orchestration and cannot redefine canon or ontology.

## Enforcement Map

- Trust policy data: `data/registries/trust_policy.json`
- Privilege role data: `data/registries/security_roles.json`
- SecureX validator: `tools/securex/securex.py`
- RepoX checks: secure trust-policy, privilege, and supply-chain invariants
- TestX checks: signature, boundary, privilege, and reproducible-build tests
