# CLI, TUI, GUI Parity

CLI, TUI, and GUI are three presentations of a single interface contract. The
CLI is authoritative for commands, flags, and error semantics. TUI and GUI are
thin shells over CLI-equivalent actions.

## Contract
- Every GUI control and TUI action maps to exactly one CLI command.
- No GUI-only or TUI-only features are permitted.
- Failure handling is identical across CLI, TUI, and GUI:
  - same error codes
  - same refusal reasons
  - same output semantics

## Implementation rules
- Define the CLI command first.
- Implement a shared command handler used by CLI, TUI, and GUI.
- Maintain a one-to-one mapping table (command -> action -> control).
- Emit identical event streams for identical actions.

## Regression checks
Parity MUST be enforced with tests:
- CLI <-> GUI event log equivalence for matching commands.
- TUI actions must hit the same command handlers.

## References
- docs/app/CLI_CONTRACTS.md
- docs/ui/UI_PHILOSOPHY.md
- docs/architecture/GUI_BASELINE.md
