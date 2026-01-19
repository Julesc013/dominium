# Canon Implementation Backlog (P1 Audit)

This file records P1 audit findings for canon alignment. Each entry lists a file
path, the finding, and the planned owner/phase.

## TODO / placeholder stubs
- `source/dominium/setup/os/win16/setup_win16_tui.c`: TODO Win16 TUI installer (install/repair/uninstall). Owner: Setup OS frontend (P10).
- `source/dominium/setup/os/cpm/setup_cpm86.c`: TODO CP/M-86 installer prompts/copy. Owner: Setup OS frontend (P10).
- `source/dominium/setup/os/cpm/setup_cpm80.c`: TODO CP/M-80 installer prompts/copy. Owner: Setup OS frontend (P10).
- `source/dominium/setup/os/carbon/setup_carbon.c`: TODO Carbon OS TUI installer. Owner: Setup OS frontend (P10).
- `source/dominium/launcher/core/tests/launcher_tools_registry_tests.cpp`: placeholder icon in test data. Owner: launcher tests (P11).
- `source/dominium/launcher/tests/launcher_control_plane_tests.cpp`: placeholder icon in test data. Owner: launcher tests (P11).

## Setup2 naming / legacy sandbox references
- `docs/setup2/IDE_WORKFLOWS.md`: "Setup2" naming and `tmp/setup2_sandbox` paths. Owner: Setup docs/tooling (P10).
- `source/dominium/setup/frontends/adapters/windows_exe/vs/README_VS.md`: `setup2_sandbox` paths. Owner: Setup tooling (P10).
- `source/dominium/setup/frontends/adapters/windows_exe/vs/launch.vs.json`: `setup2_sandbox` paths. Owner: Setup tooling (P10).

## Universe path / directory terminology (legacy)
- `docs/API/RUNTIME_CLI.md`: `--universe=<path>` and direct runtime launch guidance. Owner: docs alignment (P2/E1).
- `docs/API/LAUNCHER_CLI.md`: `--universe=PATH` in `instances start`. Owner: docs alignment (P2/E1).
- `source/dominium/game/cli/dom_cli_main.cpp`: `--universe` path and default `saves/default`; calls `engine_load_universe`/`engine_save`. Owner: game CLI + bundle integration (P5/P8).
- `source/domino/sim/api/engine_api.h`: public API uses `universe_path` and `universe_seed`. Owner: Domino sim API (P3/P5).
- `source/domino/sim/api/engine_api.c`: path-based load/save stubs for universe. Owner: Domino sim API (P3/P5).
- `source/domino/sim/replay/serialize/save_universe.h`: path-based universe save format and `universe_seed`. Owner: bundle/migration framework (P5/P6).
- `source/domino/sim/replay/serialize/save_universe.c`: universe save serializer. Owner: bundle/migration framework (P5/P6).
- `source/domino/sim/CMakeLists.txt`: builds `save_universe.c`. Owner: build integration (P5/P6).
- `source/domino/system/core/CMakeLists.txt`: builds `serialize/save_universe.c`. Owner: build integration (P5/P6).
- `include/dominium/_internal/dom_priv/launcher_internal/launcher_process.h`: stores `universe_path` on instance. Owner: launcher core (P7).
- `source/dominium/launcher/core/launcher_process.cpp`: passes `universe_path` at launch. Owner: launcher core (P7).
- `include/dominium/_internal/dom_priv/launcher_internal/launcher_plugin_api.h`: plugin API takes `universe_path`. Owner: launcher/plugin API (P7).
- `source/dominium/game/gui/runtime_app.h`: stores `universe_path` in runtime UI config. Owner: game UI (P8).
- `source/dominium/game/gui/runtime_display_cli.cpp`: displays `universe_path`. Owner: game UI (P8).
- `source/dominium/game/gui/runtime_display_gui.cpp`: displays `universe_path`. Owner: game UI (P8).
- `source/dominium/game/gui/runtime_display_headless.cpp`: displays `universe_path`. Owner: game UI (P8).
- `source/dominium/game/gui/runtime_display_tui.cpp`: displays `universe_path`. Owner: game UI (P8).
- `docs/DATA_FORMATS.md`: legacy `universe_seed`/universe metadata fields. Owner: docs/spec alignment (P2).
- `source/dominium/game/cli/dom_cli_main.cpp`: assigns `cfg.universe_seed`. Owner: game runtime scaffolding (P8).
- `source/dominium/game/gui/dom_sdl/dom_sdl_stub.cpp`: assigns `cfg.universe_seed`. Owner: game runtime scaffolding (P8).

## Absolute-path allowances / contract mismatches
- `include/dominium/_internal/dom_priv/dom_shared/manifest_install.h`: `InstallInfo.root_path` documented as absolute. Owner: Setup/launcher contract alignment (P10).
- `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md`: `root_path` documented as absolute. Owner: docs/spec alignment (P2/P10).
- `docs/SPEC_GAME_CLI.md`: dev override permits absolute paths. Owner: CLI contract alignment (P2/P7).

## dt_s / float time in authoritative paths
- `include/domino/sim.h`: `dom_sim_state` exposes `double dt_s` and `sim_time_s`. Owner: Domino sim core (P3).
- `source/domino/core/sim.c`: `dt_s = 1.0 / ups`, `sim_time_s` advanced by `dt_s`. Owner: Domino sim core (P3).
- `source/domino/core/core_internal.h`: `double dt_s` in sim state. Owner: Domino sim core (P3).
- `include/dominium/game_api.h`: public `dom_game_sim_args` includes `double dt_s`. Owner: runtime API (P3/P8).
- `include/dominium/world.h`: `dom_world_sim_step(..., double dt_s)`. Owner: runtime API (P3/P8).
- `source/dominium/game/runtime/dom_game_runtime.cpp`: derives `dt_s` from `ups` using double. Owner: runtime loop (P3/P8).
- `source/dominium/game/rules/actors.c`: sim step signature includes `double dt_s`. Owner: rules layer (P3/P8).
- `source/dominium/game/rules/constructions.c`: sim step signature includes `double dt_s`. Owner: rules layer (P3/P8).
- `source/dominium/game/rules/game_api.c`: passes `double dt_s` through sim pipeline. Owner: rules layer (P3/P8).
- `source/dominium/game/rules/world.c`: sim step signature includes `double dt_s`. Owner: rules layer (P3/P8).
- `include/domino/dnumeric.h`: `g_domino_dt_s` fixed dt for `DOMINO_DEFAULT_UPS` (30 Hz). Owner: numeric/timebase alignment (P3/P2).
- `source/domino/dnumeric.c`: computes `g_domino_dt_s` from `DOMINO_DEFAULT_UPS` (30 Hz). Owner: numeric/timebase alignment (P3/P2).
- `docs/SPEC_DOMINO_SIM.md`: documents `dt_s`/`sim_time_s` in sim state. Owner: spec alignment (P2).
- `docs/REPORT_GAME_ARCH_DECISIONS.md`: notes `dt_s = 1/ups` in core. Owner: spec alignment (P2).
- `docs/SPEC_NUMERIC.md`: defines `g_domino_dt_s` and default 30 Hz. Owner: spec alignment (P2).
- `docs/SPEC_DOMINIUM_RULES.md`: references `dt_s` values in runtime APIs. Owner: spec alignment (P2).

## Wall-clock fields in handshake/contracts
- `source/dominium/launcher/core/include/launcher_handshake.h`: `timestamp_wall_us` field in handshake. Owner: launcher handshake alignment (P7/P2).
- `source/dominium/launcher/core/src/launch/launcher_handshake.cpp`: read/write `timestamp_wall_us`. Owner: launcher handshake alignment (P7/P2).
- `docs/launcher/ECOSYSTEM_INTEGRATION.md`: documents `timestamp_wall_us`. Owner: docs/spec alignment (P2).
