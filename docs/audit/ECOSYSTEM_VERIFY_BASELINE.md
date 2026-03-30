Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen ecosystem integrity baseline for v0.0.0-mock distribution gating.

# Ecosystem Verify Baseline

- result: `complete`
- platform_tag: `win64`
- deterministic_fingerprint: `2237a437f4e575aa3c4058be1a0c0490102ad2081b57d76f3640ece02570eb61`

## Resolved Component Sets

- `install.profile.full` -> `binary.client, binary.engine, binary.game, binary.launcher, binary.server, binary.setup, docs.release_notes, lock.pack_lock.mvp_default, manifest.appshell.runtime, manifest.compat.negotiation, manifest.instance.default, manifest.lib.runtime, manifest.pack_compat.runtime, manifest.release_manifest, pack.base.procedural, pack.earth.procedural, pack.sol.pin_minimal, profile.bundle.mvp_default`
- `install.profile.server` -> `binary.engine, binary.server, lock.pack_lock.mvp_default, manifest.appshell.runtime, manifest.compat.negotiation, manifest.instance.default, manifest.release_manifest, pack.base.procedural, pack.earth.procedural, pack.sol.pin_minimal, profile.bundle.mvp_default`
- `install.profile.tools` -> `binary.setup, manifest.appshell.runtime, manifest.lib.runtime, manifest.pack_compat.runtime, manifest.release_manifest`

## Identity Coverage Summary

- result: `complete`
- invalid_identity_paths: `none`

## Migration Coverage Summary

- result: `complete`
- missing_policy_ids: `none`

## Update Plan Summary

- latest_compatible_plan_fingerprint: `3abfe57f79b0e2c4d29eb59d3185820ac7d1ab51bc4d67a7dc2634b2c53848e3`
- selected_yanked_component_ids: `none`
- skipped_yanked_count: `1`

## Readiness

- Ready for Ω-6 update channel simulation once this baseline stays green under RepoX, AuditX, TestX, and strict build gates.
