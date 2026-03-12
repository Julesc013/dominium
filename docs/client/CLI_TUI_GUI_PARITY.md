Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CLI TUI GUI Parity

## Contract

CLI is canonical for command semantics.
TUI and GUI dispatch through the same command execution path.

Session pipeline parity commands:
- `tools/xstack/session_control client.session.stage ...`
- `tools/xstack/session_control client.session.abort ...`
- `tools/xstack/session_control client.session.resume ...`
- `tools/xstack/session_surface --surface cli|tui|gui client.session.stage ...`
- `tools/xstack/session_surface --surface cli|tui|gui client.session.abort ...`
- `tools/xstack/session_surface --surface cli|tui|gui client.session.resume ...`

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
- `tools/xstack/testx/tests/test_stage_parity_status_surfaces.py`
- `tools/xstack/testx/tests/test_stage_parity_transitions_surfaces.py`
- `tools/xstack/testx/tests/test_illegal_stage_skip_refusal.py`
