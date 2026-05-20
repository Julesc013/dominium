Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Command Surface Contract Fixtures

These fixtures document the first validation expectations for
`tools/validators/contracts/check_command_surface.py`.

The fixture suite is contract-only. It does not implement command dispatch,
Workbench behavior, product CLI behavior, or runtime services.

Expected behavior:

- `valid_command_surface.toml` passes validator fixture mode.
- `invalid_missing_result_schema.toml` fails because a required result schema
  path is absent.
- `invalid_stable_without_refusal_policy.toml` fails because stable command
  contracts require refusal policy and proof.
- JSON fixtures parse as command result, refusal, and evidence examples.

Future tasks may add JSON Schema validation and CTest integration. This task
keeps the fixture lane small and focused on the command-surface law.
