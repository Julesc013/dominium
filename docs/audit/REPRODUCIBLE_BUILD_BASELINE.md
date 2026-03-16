Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: stronger reproducible-build and signing enforcement after RELEASE-3

# Reproducible Build Baseline

## Reproducibility Checklist

- build_id derives only from deterministic build inputs
- manifest ordering is deterministic across repeated generation
- optional signatures do not perturb manifest identity fields
- offline verification succeeds without requiring a signature
- build_id can be recomputed from descriptor-emitted build metadata

## Known Platform Caveats

- bitwise-identical binaries across distinct toolchains are not guaranteed in RELEASE-2
- signature verification is additive and mock-channel releases may remain unsigned

## Signing Behavior Summary

- Signing is optional and external to the build pipeline.
- Optional signatures do not change `manifest_hash` or `deterministic_fingerprint`.
- Offline verification succeeds without signatures and reports `signature_missing` non-fatally for mock-channel releases.

## Readiness

- Ready for `RELEASE-3` final pre-DIST freeze.
- Current reproducible-build rule fingerprint: `4c1f62be31e0d81d54fa281ed3a2a04587d0f6a992c18bfda47075105190444e`
