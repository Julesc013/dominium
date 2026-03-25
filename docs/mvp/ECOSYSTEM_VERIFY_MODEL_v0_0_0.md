Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen ecosystem verification baseline for v0.0.0-mock distribution gating.

# Ecosystem Verify Model v0.0.0

## Scope

This verifier freezes ecosystem-integrity checks for the mock MVP distribution.

It validates:

- deterministic component-graph resolution
- install-profile coverage for the intended product sets
- identity coverage for the frozen ecosystem surfaces
- migration-policy coverage for all governed artifact kinds
- trust-policy binding and refusal behavior
- deterministic latest-compatible update planning with yanked exclusion

It does not add new runtime behavior, identity semantics, or update semantics.

## Verification Domains

### A) Graph Resolution

- `install.profile.full` MUST resolve deterministically for the Tier 1 target.
- `install.profile.server` MUST resolve deterministically for the Tier 1 target.
- `install.profile.tools` MUST resolve deterministically for the Tier 1 target.
- Resolution MUST flow through the component graph and install-profile registries only.
- No hardcoded bundle composition is permitted in the verifier.

### B) Identity Coverage

- Universal identity validation MUST pass for distributed install, instance, release index, release manifest, pack lock, and profile bundle surfaces.
- Universal identity validation MUST pass for the pack-compat manifests that feed the selected frozen pack set.
- Save identity validation MUST pass through a deterministic local `save.manifest.json` fixture.
- Binary identity coverage for the current MVP packaging model is verified through release-manifest/build identity rather than embedded `universal_identity_block` on every descriptor JSON.

### C) Migration Coverage

- Every governed artifact kind MUST have a migration lifecycle policy.
- Read-only fallback behavior MUST remain defined where forward-open is permitted.
- Missing migration coverage is a hard failure.

### D) Trust Coverage

- Governance-selected trust policy MUST be present and applied.
- `trust.default_mock` behavior MUST remain consistent with the frozen trust model.
- Strict trust verification MUST refuse unsigned release-manifest verification.

### E) Update Coverage

- `policy.latest_compatible` MUST compute deterministically.
- Yanked candidates MUST be excluded from latest-compatible selection.
- Skipped yanked candidates MUST remain explicitly recorded.

## Stability

- `ecosystem_verify_version = 0`
- `stability_class = stable`
