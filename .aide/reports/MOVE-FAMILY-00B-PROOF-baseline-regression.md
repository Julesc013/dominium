Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00B-PROOF Baseline Regression

## Baseline

- Baseline source: BASELINE-00 / RELEASE-00 structural regression baseline.
- Baseline requirement source: `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`.
- Move family: MOVE-FAMILY-00B within MOVE-FAMILY-00.

## Required Tier

The proof used Tier 0 plus focused RepoX, manifest JSON parsing, stale-reference classification, strict root/layout checks, and generated-output ignored/staging checks.

## Result

PASS_WITH_WARNINGS.

## Preserved Baseline Posture

- RELEASE-00 local release/projection outputs were not regenerated or committed.
- `.dominium.local/**` and `.aide.local/**` remain ignored and untracked.
- Strict repo/root/distribution/component validators passed.
- AIDE doctor/validate/test/selftest/tools/roots/repo/latest commit checks passed.
- Docs sanity, build target boundaries, UI shell purity, and ABI boundary checks passed.
- Focused RepoX passed through `ctest --preset verify -R inv_repox_rules --output-on-failure`.
- Full CTest and full eval remain out of scope, matching the accepted proof posture for this move family proof.

## Known Warnings

- TOML fallback-parser warnings from strict validators.
- Historical/audit/planning/AIDE references to old IDE manifest paths remain by design.
- Generated-output references to `ide/manifests/*.projection.json` remain by design.
- Full CTest, full eval, CMake configure/build, product binaries, package/release generation, portable projection regeneration, and internal pilot release regeneration were not run.

## Regression Decision

No baseline regression was detected. The retired `ide` source root does not weaken the RELEASE-00 baseline, root layout authority, RepoX posture, projection contract location, or AIDE evidence posture.
