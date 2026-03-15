Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: RELEASE-INDEX
Replacement Target: signed suite and product evolution policy with explicit yanking and rollback governance

# Release Index Policy Baseline

## Resolution Policies Summary

- default policy: `policy.exact_suite`
- latest-compatible fixture selected client version: `0.0.1`
- exact-suite fixture selected client version: `0.0.0+build.8166d8e67e934a11`

## Yanking Behavior

- latest-compatible skipped yanked candidates: `1`
- exact-suite selected yanked components: `binary.client`
- exact-suite warning codes: `warn.update.yanked_component`

## Rollback Guarantees

- recorded `resolution_policy_id`: `policy.latest_compatible`
- recorded `install_plan_hash`: `3333333333333333333333333333333333333333333333333333333333333333`
- recorded `prior_component_set_hash`: `4444444444444444444444444444444444444444444444444444444444444444`

## Git Tagging Rules

- suite tags follow `suite/vX.Y.Z-<channel>`
- product tags are optional and product-specific
- no tag rewriting
- current repo tags observed during retro audit: `canon-clean-2, safety/mega-13cb8ca7`

## Changelog Layering

- discovered changelog files: `CHANGELOG.md, docs/architecture/CHANGELOG_ARCH.md, docs/engine/CODE_1_CHANGELOG.md`
- suite changelog remains `CHANGELOG.md`
- release manifest remains the machine-readable version map

## Readiness

- long-term suite evolution: ready
- yanked build governance: ready
- deterministic rollback recording: ready

## Report Fingerprints

- policy registry hash: `5c7df3d88913321fe827bf1ceba5f765d0c7f0ae7ca07048714a1842b96f0788`
- report fingerprint: `75237ebe50f48215717b34dcc84353dfe57934def932b9dd376fbba9e1062fbb`
