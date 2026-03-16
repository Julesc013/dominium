Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: release-pinned standalone shell and product UI bootstrap contract

# UI Mode Resolution Baseline

Fingerprint: `e8272bf85ae80a1a0d4f4a8e708cba9503b48c2b08e93bf78c7399eded76aa25`

## Decision Tree Lock

- explicit override -> explicit mode or deterministic fallback
- attached TTY -> product TTY policy order
- GUI without TTY -> product GUI policy order
- no TTY and no GUI -> product headless policy order

## Sample Outcomes

| Scenario | Product | Requested | Context | Selected | Compat | Degrade Steps |
| --- | --- | --- | --- | --- | --- | --- |
| `client_gui` | `client` | `default` | `gui` | `rendered` | `compat.full` | `0` |
| `client_tty` | `client` | `default` | `tty` | `tui` | `compat.full` | `0` |
| `launcher_gui_no_native` | `launcher` | `default` | `gui` | `cli` | `compat.degraded` | `2` |
| `server_headless_explicit` | `server` | `headless` | `headless` | `headless` | `compat.full` | `0` |
| `server_tty` | `server` | `default` | `tty` | `tui` | `compat.full` | `0` |
| `setup_gui_native` | `setup` | `default` | `gui` | `os_native` | `compat.full` | `0` |

## Enforcement Status

- No selector-surface violations were detected.

## Readiness

- The governed selector is centralized in `src/appshell/ui_mode_selector.py`.
- The presentation-only probe is isolated in `src/platform/platform_probe.py`.
- The selector is ready for UI-RECONCILE-0 and PLATFORM-FORMALIZE-0 without changing simulation truth.
