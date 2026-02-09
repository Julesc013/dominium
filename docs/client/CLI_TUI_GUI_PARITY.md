Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# CLI TUI GUI Parity

## Contract

CLI is canonical for command semantics.
TUI and GUI dispatch through the same command execution path.

## Required Behavior

- identical command ids across modes
- deterministic refusal codes across modes
- no GUI-only command execution path
- no TUI-only command execution path

## Implemented Surfaces

- command bridge: `client/core/client_command_bridge.c`
- command descriptors: `client/core/client_commands_registry.c`
- state machine: `client/core/client_state_machine.c`
- mode adapters:
  - `client/modes/client_mode_cli.c`
  - `client/modes/client_mode_tui.c`
  - `client/modes/client_mode_gui.c`

## Validation

TestX parity checks:

- `tests/integration/client_flow_smoke_tests.py`
- `tests/integration/client_parity_tests.py`
- `tests/integration/server_discovery_tests.py`
- `tests/integration/world_manager_tests.py`
- `tests/integration/client_refusal_codes_tests.py`

