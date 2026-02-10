Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Client UI And Flow

Client UI flow is command-driven and mode-parity safe.

## Canonical States

- BootProgress
- MainMenu
- SingleplayerWorldManager
- MultiplayerServerBrowser
- Options
- About
- SessionLaunching
- SessionRunning
- RefusalError

## Navigation Contract

- Transitions occur only through registered client commands.
- CLI, TUI, and GUI consume the same state snapshots.
- UI shells do not implement behavior directly.

## Session Entry Contract

- Session setup runs through declared lifecycle stages.
- Time advancement starts only after explicit begin.
- World and pack compatibility checks occur before session entry.

## Diagnostics

- Refusal messages include deterministic refusal codes.
- Build identity and lock hash are surfaced in About/Details views.
- Replay and bugreport surfaces are read-only by default.

