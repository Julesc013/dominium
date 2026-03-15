Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/SUPERVISOR_MODEL.md`, `docs/appshell/IPC_DISCOVERY.md`, `docs/appshell/LOGGING_AND_TRACING.md`, and `docs/diag/REPRO_BUNDLE.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Supervisor Hardening Final

Fingerprint: `354fac9b3d1ace550667c518ea6d0271e3f3d6b94a901de6cc19f18968fbbb66`

## Removed Wall-Clock Usage

- No `sleep`, `time`, `datetime`, or timeout-driven readiness loops remain in the hardened supervisor surfaces.
- Readiness now relies on deterministic ready handshakes plus bounded negotiated attach/status checks.

## Canonical Arg Rules

- Long flags are serialized in stable lexical order through `src/appshell/supervisor/args_canonicalizer.py`.
- Canonical argv text uses deterministic JSON quoting for whitespace and escape-sensitive tokens.
- Each supervised process row records `args_hash` and `argv_text_hash` in the run manifest.

## Crash Handling

- `supervisor.policy.default`: no restart; crash captures a diag bundle and leaves the child exited.
- `supervisor.policy.lab`: bounded restart with deterministic iteration backoff before respawn.
- `explain.supervisor_restart` and `explain.supervisor_stop` are emitted through the shared log engine.

## Runtime Verification

- Runtime probe result: `complete`
- Replay probe result: `complete`
- Crash policy probe result: `complete`
- Portable/installed parity fingerprint: `04749a43ff16ad354964cdaf301a5c491a0f3d0bb48db31f500dc274f386697e`

## Violations

- Count: `0`
- Remaining items: none

## Readiness

- Ready for `RESTRUCTURE-PREP-0` and `CONVERGENCE-GATE-0` once full-repo strict lanes are rerun.
