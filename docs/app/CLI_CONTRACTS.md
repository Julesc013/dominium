# CLI Contracts

All product CLIs provide deterministic, CLI-only modes. No GUI/TUI is required
for tests, and no packs are required for `--help`, `--version`, `--build-info`,
`--status`, or `--smoke`.

## Common flags
- `--help` (or `-h`): usage and options
- `--version`: product version string
- `--build-info`: key/value build metadata
- `--status`: deterministic status output
- `--smoke`: deterministic CLI smoke run
- `--selftest`: alias for `--smoke`

## Build-info output (all products)
Key/value lines include:
- `product`, `product_version`
- `engine_version`, `game_version`
- `build_number`, `build_id`, `git_hash`, `toolchain_id`
- protocol lines: `protocol_law_targets`, `protocol_control_caps`,
  `protocol_authority_tokens`
- API/ABI lines: `abi_dom_build_info`, `abi_dom_caps`, `api_dsys`, `api_dgfx`

## Client (`client`)
- `--renderer <name>`: explicit renderer selection; fails loudly if unavailable
- `--windowed`: start a windowed shell (not used by CLI tests)
- `--borderless`: start a borderless window
- `--fullscreen`: start a fullscreen window (best-effort)
- `--width <px>`, `--height <px>`: window size override
- `--mp0-connect=local`: MP0 local demo (deterministic)

## Server (`server`)
- `--mp0-loopback`: MP0 loopback (deterministic)
- `--mp0-server-auth`: MP0 server-auth demo (deterministic)

## Launcher (`launcher`)
- Commands: `version`, `list-profiles`, `capabilities`
- `--status`/`--smoke`: prints control capability status

## Setup (`setup`)
- Commands: `version`, `status`, `prepare`
- `status` prints `setup status: ok (stub)` and control capability status
- `prepare` creates an empty install layout (uses `--root` when provided)

## Tools (`tools`)
- Commands: `inspect`, `validate`, `replay` (stubs)
- `--status`/`--smoke`: prints `tools_status=ok` or `tools_smoke=ok`
