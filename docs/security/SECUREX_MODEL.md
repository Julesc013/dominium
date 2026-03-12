Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# SecureX Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


SecureX is the trust and integrity enforcement layer for Dominium development and runtime packaging flows.

## Scope

- Trust boundary validation across engine, game, client, server, tools, packs, and orchestration.
- Pack signature generation and verification for supply-chain integrity checks.
- Deterministic integrity manifests for canonical artifacts and tool outputs.
- Least-privilege role enforcement through law profile bindings and entitlements.
- Reproducible build checks based on canonical artifact hashes.

## Non-Goals

- SecureX does not define new simulation semantics.
- SecureX does not grant authority outside law profiles.
- SecureX does not bypass RepoX/TestX/ControlX gate contracts.

## Integration

- RepoX enforces trust-policy and privilege-model registry validity plus supply-chain invariants.
- TestX validates boundary, privilege, pack signature, and reproducible-build behaviors.
- CompatX remains responsible for schema compatibility and migration routing.
- ControlX remains the orchestration control plane and routes execution through `scripts/dev/gate.py`.
