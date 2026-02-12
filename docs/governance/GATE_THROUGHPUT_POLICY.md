Status: DERIVED
Last Reviewed: 2026-02-12
Supersedes: none
Superseded By: none

# Gate Throughput Policy

## Purpose

This policy hardens throughput for automation and queued prompts by making `scripts/dev/gate.py` fast by default while preserving strict/final validation paths.

## Default Modes

- `gate.py verify` defaults to `FAST`.
- `gate.py exitcheck` defaults to `FAST`.
- `gate.py precheck` remains ultra-minimal.
- `gate.py strict` runs targeted strict validation.
- `gate.py full` runs exhaustive validation.
- `gate.py dist` always runs full distribution checks.

## Escalation Rules

`gate.py` evaluates changed paths and escalates mode safely:

- `FAST`:
  - docs-only changes
  - UI-only IR/layout changes
  - client/game-only code changes
- `STRICT`:
  - any change under `schema/`
  - any change under `data/registries/`
  - changes under `repo/repox/` or `tests/`
  - packaging-related changes when not in dist lane
- `FULL`:
  - explicit `--full`
  - `gate.py full`
  - `gate.py dist`

Packaging changes do not auto-upgrade to `FULL` unless explicitly requested or dist lane is invoked.

## Heavy Operation Defaults

In `FAST` mode, `gate.py` does not run full heavy suites by default:

- full TestX
- full AuditX
- full PerformX
- full CompatX
- full SecureX
- packaging

`FAST` emits warnings that strict/full checks were skipped and points to `gate.py strict` / `gate.py full`.

## State-Hash Short-Circuit

To prevent repeated prompt abuse overhead, `gate.py` short-circuits identical successful runs:

- state hash inputs:
  - `git HEAD`
  - working tree diff hash
  - gate policy version
- cache file:
  - `dist/ws/<WS_ID>/tmp/gate_last_ok.json`
- cache key:
  - `<gate_command>:<mode>`

If state hash and key match the last successful run, `gate.py` returns success immediately.

## Safety Guarantees

- No invariants are weakened; only default lane work volume is reduced.
- strict/full lanes remain available and enforce stronger checks.
- full lane is never selected implicitly except in dist lane.
