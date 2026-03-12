Status: DERIVED
Last Reviewed: 2026-03-12
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MVP Smoke Suite

This document defines the deterministic end-to-end smoke gate for Dominium v0.0.0.
It is subordinate to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

## Purpose

The MVP smoke suite is the minimum release gate proving that v0.0.0 operates as one lawful, deterministic system.

The gate does not add features. It composes existing AppShell, setup, launcher, EARTH, LOGIC, SERVER-MVP-0, and DIAG surfaces into one repeatable smoke envelope:

- launch and pack verification
- session bootstrap
- teleport chain
- Earth traversal and edit checks
- logic compile, probe, and trace checks
- bounded time warp checks
- repro bundle replay verification

The suite is release-blocking. Dist and release packaging are not considered ready unless the smoke suite passes.

## Seed Policy

- The suite uses one explicit canonical smoke seed.
- All subordinate seeds are derived from the canonical smoke seed through named deterministic streams.
- No wall-clock source, timeout-derived seed, or ambient entropy source may affect scenario generation or harness assertions.
- The default smoke seed is `456`.
- The harness records:
  - top-level smoke seed
  - derived EARTH seed
  - derived SERVER-MVP-0 seed
  - deterministic scenario fingerprint

## Required Products

The smoke gate spans these existing product surfaces:

- `setup`
- `launcher`
- AppShell supervisor and IPC attach path
- `client`
- `server`
- EARTH-9 deterministic stress helpers
- LOGIC replay, compile, and debug helpers
- DIAG repro bundle capture and replay verification

## Command Surface Mapping

The prompt shorthand `launcher start --instance mvp_default --seed S` is implemented without adding a new launcher flag.

The current canonical smoke command is:

`launcher launcher start --seed S --session-template-path <smoke-session-template> --profile-bundle-path <smoke-profile-bundle> --pack-lock-path <smoke-pack-lock>`

This preserves the existing AppShell command surface and keeps smoke gating out of feature work.

The smoke harness records two deterministic lock identities on purpose:

- the curated verification `pack_lock_hash` produced by `setup verify` and `launcher packs build-lock`
- the smoke runtime `pack_lock_hash` used for AppShell and SERVER-MVP-0 boot

Both hashes must be explicit in the smoke report. Neither may be inferred silently.

## Success Criteria

The smoke suite passes only if all of the following are true:

- `setup verify` completes on the curated MVP smoke verification root.
- `launcher compat-status` completes and emits the expected negotiation hash.
- `launcher packs build-lock` completes and reproduces the expected `pack_lock_hash`.
- `launcher launcher start`, `launcher launcher status`, and `launcher launcher stop` complete.
- launcher-supervised IPC attach records are explicit about any degraded compatibility mode.
- the deterministic teleport chain is generated from the smoke seed.
- EARTH replay verifies deterministic traversal, local edit, hydrology, collision, daylight, climate, and tide behavior.
- LOGIC compile parity, probe, and bounded trace checks complete.
- SERVER-MVP-0 proof anchors match their recorded expected hashes.
- DIAG repro bundle capture completes and replay verification reports hash equivalence.
- refusal count is zero in the default smoke lane.
- no silent degradation is observed.

## Deterministic Outputs

The smoke suite writes these canonical outputs:

- `build/mvp/mvp_smoke_scenario.json`
- `build/mvp/mvp_smoke_hashes.json`
- `build/mvp/mvp_smoke_report.json`
- `data/regression/mvp_smoke_baseline.json`
- `docs/audit/MVP_SMOKE_FINAL.md`

The smoke harness also writes deterministic working artifacts under `build/mvp/`:

- curated verification root
- setup and build-lock reports
- smoke profile bundle
- smoke pack lock
- smoke session template
- DIAG repro bundle

## Deterministic Hash Lock

The smoke suite records and compares these hashes:

- setup verification report fingerprint
- launcher compatibility negotiation hash
- curated `pack_lock_hash`
- smoke runtime `pack_lock_hash`
- launcher build-lock report fingerprint
- scenario fingerprint
- key EARTH view and climate and tide fingerprints
- LOGIC compiled model hash and trace proof hashes
- SERVER-MVP-0 proof anchor hashes keyed by tick
- DIAG bundle hash and proof-window hash

Regression lock updates require the explicit tag:

`MVP-SMOKE-REGRESSION-UPDATE`

Baseline changes without that tag are treated as a gate violation, not as an automatic refresh.
