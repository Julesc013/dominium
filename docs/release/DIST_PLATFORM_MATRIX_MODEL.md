Status: CANONICAL
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: release-pinned platform support and archive verification contract

# Distribution Platform Matrix Model

DIST-4 defines the deterministic distribution-platform validation matrix for `v0.0.0-mock`.

## Purpose

The platform matrix proves that the assembled distribution surfaces:

- resolve UI mode through the single AppShell selector,
- advertise platform capabilities consistently through endpoint descriptors,
- degrade through the declared fallback chains,
- remain usable as standalone products in the contexts supported by the current bundle.

The matrix is a validation harness and support statement only. It does not claim parity for platforms that do not have a built bundle in the current run.

## Platforms

Platforms are recorded from the formal platform capability registry and validated when a bundle is available for the platform tag.

- Windows NT
- Windows 9x, if built
- macOS Cocoa, if built
- macOS Classic, if built
- Linux GTK, if built
- POSIX minimal, if built

Unbuilt platforms remain documented but are not marked as validated in the DIST-4 report.

## Contexts

The matrix evaluates these presentation contexts:

- GUI invocation: no TTY, GUI-capable host
- TTY interactive: interactive shell attached
- Headless: no TTY and no GUI surface

Context simulation is presentation-only. It must not affect truth, replay, or negotiation semantics.

## Products

The matrix covers these standalone products:

- engine
- game
- client
- server
- setup
- launcher

## Expected Mode Rules

- GUI context:
  - `client` prefers `rendered`, then `os_native`, then `tui`, then `cli`
  - `setup` prefers `os_native`, then `tui`, then `cli`
  - `launcher` prefers `os_native`, then `tui`, then `cli`
  - `server` prefers `tui` only when interactive; otherwise `cli`
  - `engine` and `game` remain console-first and follow their product policy registry
- TTY interactive:
  - `client` prefers `tui`, then `cli`
  - `setup`, `launcher`, `server`, `game` prefer `tui`, then `cli`
  - `engine` prefers `cli`, then `tui`
- Headless:
  - all products must remain usable in `cli`

## Required Observations

For each validated bundle and product, DIST-4 records:

- descriptor success and descriptor hash
- claimed `platform_id`
- claimed UI capability set
- simulated default selection in GUI, TTY, and headless contexts
- forced fallback behavior for the product's primary GUI or interactive mode
- observed degrade logging when a forced mode is unavailable
- refusal codes, if any

## Reporting

DIST-4 generates:

- `docs/audit/DIST_PLATFORM_MATRIX_REPORT.md`
- `data/audit/dist_platform_matrix.json`
- `docs/release/SUPPORTED_PLATFORMS_v0_0_0_mock.md`
- `docs/audit/DIST4_FINAL.md`

All outputs must use deterministic ordering and canonical serialization.
