Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Client Command Graph

## Scope

The canonical client command namespace is `client.*`.
The bridge translates canonical commands into existing CLI handlers or explicit refusals.

## Families

- Boot: `client.boot.*`
- Main menu: `client.menu.*`
- World manager: `client.world.*`
- Multiplayer: `client.server.*`
- Options: `client.options.*`
- About/diagnostics: `client.about.*`, `client.diag.*`
- Replay: `client.replay.*`

## Required Metadata

Each command descriptor declares:

- `command_id`
- `required_capabilities`
- `epistemic_scope`
- refusal code list
- mode mask (`cli|tui|gui`)

Definitions are in `client/core/client_commands_registry.c`.

## Bridge Rules

- Canonical command accepted:
  - rewritten to legacy command, or
  - synthetic deterministic success, or
  - deterministic refusal.
- Non-canonical command accepted as legacy path.

## Determinism Constraints

- Canonical command rewrite is a pure string transformation.
- No wall-clock, randomness, or I/O inside bridge routing.
- Same input command and capability set yields same output/refusal.

