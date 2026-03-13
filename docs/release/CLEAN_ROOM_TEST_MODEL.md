Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-4 platform clean-room matrix and archive validation

# Clean Room Test Model

## Purpose

DIST-3 proves that an assembled Dominium portable bundle can be copied to a new location and run without:

- the source repository
- XStack tooling outside the shipped runtime subset
- pre-existing install registry entries
- `DOMINIUM_*` environment variables
- cached store data outside the copied bundle

The clean-room gate is an acceptance test, not a packaging step.

## Clean Room Definition

A clean-room run executes from a copied portable bundle under an isolated temporary root.

Allowed:

- documented OS runtime libraries
- the system Python runtime required by the portable MVP bundle
- local filesystem access inside the copied bundle root

Disallowed:

- repo-root imports outside the copied bundle
- install discovery through external registry state
- external store, saves, logs, IPC, or export paths
- `DOMINIUM_*` environment overrides
- network services

## Isolation Rules

The harness must:

1. Copy the source bundle into a temporary working directory.
2. Launch products only from the copied `bin/` wrappers.
3. Clear all `DOMINIUM_*` variables before subprocess launch.
4. Provide isolated `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `TEMP`, and `TMP` directories inside the copied bundle.
5. Avoid `--install-id` and any other installed-mode selector.
6. Require portable adjacency to resolve the install root.

## Determinism Rules

- Step order is fixed and versioned by the harness.
- All retries are bounded by explicit iteration counts; no wall-clock timeouts are used.
- Reports sanitize copied-bundle absolute paths to logical placeholders before hashing.
- Any absolute path that escapes the copied bundle root is a hard failure.

## Required Assertions

The clean-room run must prove:

- portable install discovery resolves by adjacency
- virtual roots resolve only inside the copied bundle
- offline pack verification succeeds
- negotiated launcher attachments are present
- no external absolute path leaks are emitted
- repro bundle replay validates deterministically
- all required commands exit successfully

## Mode Policy

The harness accepts `prefer gui|tui|cli`.

- `gui` requests `--mode rendered` and accepts deterministic degrade through the AppShell ladder
- `tui` requests `--mode tui`
- `cli` requests `--mode cli`

Mode policy affects only UI selection. It must not affect simulation truth.

## Required Flow

The clean-room harness executes this end-to-end flow in deterministic order:

1. `setup install status`
2. `setup verify`
3. `launcher instances list`
4. `launcher start --seed S`
5. `launcher status`
6. `launcher attach --all`
7. teleport chain `sol -> earth -> random_star -> earth`
8. tool scan + terrain edit + logic probe/trace checks
9. DIAG bundle capture
10. replay bundle verification
11. `launcher stop`

The launcher uses the bundled default instance manifest. No repo-time instance selection is required.
