Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# IDE Workflow

## Primary targets
- `dominium_client` (output: `client`)
- `dominium_server` (output: `server`)
- `launcher_cli` (output: `launcher`)
- `setup_cli` (output: `setup`)
- `dominium-tools` (output: `tools`)

## Entrypoints
- `client_main` in `client/app/main_client.c`
- `server_main` in `server/app/main_server.c`
- `launcher_main` in `launcher/cli/launcher_cli_main.c`
- `setup_main` in `setup/cli/setup_cli_main.c`
- `tools_main` in `tools/tools_host_main.c`

Individual tool executables continue to use `dom_tool_*_main` entrypoints.

## Working directory
Set the working directory to the repo root so relative resources resolve:
`data/registries/*`, `data/*`, and `docs/*` are referenced by default paths.

## Common debug args
- CLI smoke: `--smoke` (optionally with `--ui=none`)
- Build info: `--build-info`
- TUI: `--ui=tui` (client/tools)
- GUI: `--ui=gui` (client; others are stubs)

## Environment defaults
`DOM_UI` or `DOM_UI_MODE` can select a default UI mode when no CLI flag is
provided.