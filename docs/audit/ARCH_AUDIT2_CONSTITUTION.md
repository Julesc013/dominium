Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Final release/distribution audit baseline governed by ARCH-AUDIT-2

# ARCH Audit 2 Constitution

## Component Composition Purity

- Distribution bundle contents must derive from:
  - component graph
  - install profile
  - target matrix
  - trust policy
- Dist assembly must not embed alternate hardcoded bundle sets that bypass graph resolution.

## Update Purity

- Update planning must be:
  - release-index-driven
  - component-graph-resolved
  - trust-verified
- Core update logic must not implement direct `"download file X"` shortcuts outside the governed release-index/update-plan flow.

## Trust Enforcement Purity

- Hash verification is mandatory for all governed artifacts.
- Signature verification is enforced according to trust policy.
- Strict policy must not contain local-dev or unsigned bypass paths.

## Target Matrix Compliance

- Release indices must not publish Tier 3 targets as downloadable artifacts.
- Platform probes and endpoint descriptors must not claim unsupported capabilities or mismatched target identities.

## Manifest / Bundle Determinism

- Archive and bundle generation must preserve deterministic ordering.
- File lists must remain sorted.
- No timestamps, mtimes, or host metadata may perturb canonical bundle identity.
