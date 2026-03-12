Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MVP Cross-Platform Gate

Purpose: define the deterministic cross-platform agreement gate that seals MVP release readiness after MVP-GATE-0 smoke and MVP-GATE-1 stress.

## Required Platforms

- `windows`
- `macos`
- `linux`

## Build Configurations

- `release` is required and treated as the strict gate lane.
- `debug` is optional and may be compared as an informational extension, but it does not change the release verdict.

## Required Inputs

The cross-platform gate consumes the governed outputs from:

- MVP-GATE-0 smoke
- MVP-GATE-1 stress
- LIB full regression lock
- deterministic negotiation-record surfaces
- deterministic repro-bundle surfaces

## Canonical Comparison Rule

- Compare canonical hashes only.
- Ignore host metadata such as timestamps, path separators, and absolute paths.
- No OS-native UI artifacts participate in the canonical comparison set.
- Platform wrappers, packaging shells, and install topology must not leak into truth-facing hashes.

## Artifacts Compared

The required comparison set is:

- proof anchors
- pack lock hashes
- negotiation record hashes
- bundle hashes
- repro bundle hashes
- MVP stress baseline hashes

## Portable vs Linked Parity

The gate must compare linked and portable installs under the same deterministic smoke scenario and require matching:

- proof anchors
- pack locks
- negotiation records
- repro bundles

## Acceptable Degrade Behavior

- deterministic degrade behavior only
- The default release lane must report zero cross-platform gate degrade events.
- No silent degradation is allowed.
- If a comparison excludes a host-specific field, that exclusion must be explicit and recorded in the gate report.

## Acceptance Thresholds

The gate passes only when all of the following are true:

- MVP-GATE-0 reports `complete`
- MVP-GATE-1 report and proof report both report `complete`
- `windows`, `macos`, and `linux` canonical artifact sets match exactly
- linked vs portable parity assertions all pass
- negotiation matrix records are deterministic and match the expected compatibility mode
- regression lock updates require `MVP-CROSS-PLATFORM-REGRESSION-UPDATE`

## Outputs

The gate writes deterministic artifacts to:

- `build/mvp/mvp_cross_platform_matrix.json`
- `build/mvp/mvp_cross_platform_hashes.json`
- `data/regression/mvp_cross_platform_baseline.json`
- `docs/audit/MVP_CROSS_PLATFORM_FINAL.md`
