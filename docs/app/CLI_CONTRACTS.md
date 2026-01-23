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
- `--deterministic`: fixed timestep (no wall-clock sleep)
- `--interactive`: variable timestep (wall-clock)
- `--ui=none|tui|gui`: select CLI/TUI/GUI shells
- `--tui`: legacy alias for `--ui=tui`

## Build-info output (all products)
Key/value lines include:
- `product`, `product_version`
- `engine_version`, `game_version`
- `build_number`, `build_id`, `git_hash`, `toolchain_id`
- protocol lines: `protocol_law_targets`, `protocol_control_caps`,
  `protocol_authority_tokens`
- API/ABI lines: `abi_dom_build_info`, `abi_dom_caps`, `api_dsys`, `api_dgfx`
- Platform extension API lines: `platform_ext_window_ex_api`, `platform_ext_error_api`,
  `platform_ext_cliptext_api`, `platform_ext_cursor_api`, `platform_ext_dragdrop_api`,
  `platform_ext_gamepad_api`, `platform_ext_power_api`, `platform_ext_text_input_api`,
  `platform_ext_window_mode_api`, `platform_ext_dpi_api`
- Products may append platform capability lines (e.g. `platform_*`,
  `window_default_*`, `dpi_scale_default`).

## Client (`client`)
- `--renderer <name>`: explicit renderer selection; fails loudly if unavailable
- `--ui=none|tui|gui`: select GUI/TUI/CLI-only shell
- `--windowed`: start a windowed shell (not used by CLI tests)
- `--tui`: start a terminal UI shell (not used by CLI tests)
- `--borderless`: start a borderless window
- `--fullscreen`: start a fullscreen window (best-effort)
- `--width <px>`, `--height <px>`: window size override
- `--frame-cap-ms <ms>`: frame cap for interactive loops
- `--mp0-connect=local`: MP0 local demo (deterministic)
- `--topology`: report packages tree summary (read-only)
- `--snapshot`: snapshot metadata (unsupported in APR4; fails loudly)
- `--events`: event stream summary (unsupported in APR4; fails loudly)
- `--format <text|json>`: output format for observability commands
- `--expect-engine-version`, `--expect-game-version`, `--expect-build-id`,
  `--expect-sim-schema`, `--expect-build-info-abi`, `--expect-caps-abi`,
  `--expect-gfx-api`: compatibility enforcement for read-only access

## Server (`server`)
- `--mp0-loopback`: MP0 loopback (deterministic)
- `--mp0-server-auth`: MP0 server-auth demo (deterministic)
- `--ui=none|tui|gui`: optional UI selection (TUI/GUI are stubs in APR3)

## Launcher (`launcher`)
- Commands: `version`, `list-profiles`, `capabilities`
- `--status`/`--smoke`: prints control capability status
- `--ui=none|tui|gui`: optional UI selection (TUI/GUI are stubs in APR3)

## Setup (`setup`)
- Commands: `version`, `status`, `prepare`
- `status` prints `setup status: ok (stub)` and control capability status
- `prepare` creates an empty install layout (uses `--root` when provided)
- `--ui=none|tui|gui`: optional UI selection (TUI/GUI are stubs in APR3)

## Tools (`tools`)
- Commands: `inspect`, `validate`, `replay` (stubs)
- `--status`/`--smoke`: prints `tools_status=ok` or `tools_smoke=ok`
- `--ui=none|tui|gui`: select CLI/TUI/GUI shells
- `--tui`: legacy alias for `--ui=tui` (not used by CLI tests)
- `--frame-cap-ms <ms>`: frame cap for interactive loops
- `--format <text|json>`: output format for `inspect`/`validate`
- `--expect-engine-version`, `--expect-game-version`, `--expect-build-id`,
  `--expect-sim-schema`, `--expect-build-info-abi`, `--expect-caps-abi`,
  `--expect-gfx-api`: compatibility enforcement for read-only access
