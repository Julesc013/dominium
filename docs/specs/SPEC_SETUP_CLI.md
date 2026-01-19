--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `setup/`.

GAME:
- None. This spec is implemented under `setup/`.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_SETUP_CLI

## Purpose
Define the legacy setup CLI frontend that routes commands to Setup Core and
emits text or JSON output for tooling and user workflows.

## Internal layering
- CLI entrypoint: argument parsing, command dispatch, and output formatting live
  in `source/dominium/setup/cli/dominium_setup_main.c`.
- Core boundary: all setup behavior is executed via public Setup Core APIs
  (`source/dominium/setup/core/include/dsu/**`); CLI does not access core
  internals.

## Extension mechanisms
- External GUI entrypoint `dom_setup_ui_run_gui` is resolved at link time for
  the `gui` command.
- No plugin interface; new commands require modifying the CLI source.

## Invariants
- JSON output uses a fixed envelope with `schema_version`, `command`, `status`,
  `status_code`, and `details` fields.
- Deterministic mode defaults to enabled and is propagated to Setup Core via
  `DSU_CONFIG_FLAG_DETERMINISTIC`.
- CLI identity strings are sourced from `DSU_CLI_NAME` and `DSU_CLI_VERSION`.

## Versioning rules
- `DSU_CLI_JSON_SCHEMA_VERSION` increments only when the JSON envelope schema
  changes.
- `DSU_CLI_VERSION` is the CLI's declared version string.

## Determinism guarantees
- When deterministic mode is enabled, Setup Core is configured for deterministic
  behavior by the CLI.
- JSON output ordering is fixed by the CLI emission order.
