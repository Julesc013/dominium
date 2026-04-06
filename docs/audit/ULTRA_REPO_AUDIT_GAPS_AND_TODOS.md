# ULTRA REPO AUDIT GAPS AND TODOS

## Gap Ledger

| Gap | Category | Severity | Scope | Blocker Status | Recommended Action | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| GAP-001 | entrypoint | high | server startup | hard_blocker_for_public_python_server_entry | Fix REPO_ROOT_HINT so direct script or module invocation resolves appshell and data/registries from the live repo root. | python server/server_main.py --help and python -m server.server_main --help both failed during audit. |
| GAP-002 | integration | high | session boot | hard_blocker_for_alt_save_roots | Make session_boot honor the save root/session artifact location already supported by session_create. | runner.py hard-codes repo_root/saves/<save_id>; alternate saves-root boot failed. |
| GAP-003 | startup_ergonomics | high | local playtest bootstrap | hard_blocker_for_single_command_playtest_boot | Publish one canonical repo-local command that wraps session creation, local authority boot, and attach/status reporting. | MVP runtime_entry local-singleplayer launch did not yield a clear gameplay boot. |
| GAP-004 | supervision | high | launcher supervised sessions | soft_blocker_for_repeatable_playtests | Resolve the server child exit_code 3 / attach refusal path before relying on launcher supervision for internal sessions. | launcher status surfaced a prior exited server child and failed local attach attempt. |
| GAP-005 | ui_shell | medium | launcher native shell | non_blocker_for_headless_tui_baseline | Keep using the Python launcher/AppShell for baseline work; defer native launcher GUI/TUI completion. | launcher_config/profile/process and GUI/TUI entrypoints remain explicit stubs. |
| GAP-006 | ui_shell | medium | setup native shell | non_blocker_for_repo_local_setup | Treat tools/setup/setup_cli.py as canonical for now and defer native setup shell completion. | setup.exe smoke reports stub status while setup_cli.py exposes richer real commands. |
| GAP-007 | networking | high | multiplayer transport | hard_blocker_for_non_loopback_multiplayer | Defer broader multiplayer until TCP/UDP or another external transport is implemented beyond loopback stubs. | tcp_stub.py and udp_stub.py explicitly refuse not_implemented. |
| GAP-008 | validation | medium | green gate confidence | soft_blocker_for_claiming_repo_green | Run FAST validation to completion after audit artifacts are in place and capture a fresh report. | FAST validation attempt timed out during the audit. |
| GAP-009 | packaging | medium | installed-mode flows | soft_blocker_for_installed_playtest_distribution | Materialize or register a real install manifest/registry when moving from repo-local playtests to installed builds. | Launcher/setup compat-status use repo_wrapper_shim because install discovery refuses normal installed-mode discovery. |
| GAP-010 | runtime_wiring | medium | semantic subsystems | non_blocker_for_minimal_playtest | Integrate these subsystems incrementally after the baseline boot/session loop is stable. | Large substantive implementations exist, but most are not visibly exercised by the verified public playtest path yet. |
| GAP-011 | runtime | medium | game runtime shell | soft_blocker_for_broader_product_realization | Keep reusing engine/game libraries already wired into client/server, but treat remaining stub-tagged library shells as incomplete until proven otherwise. | game/dominium_game_stub.c still marks the game library shell as a stub. |
| GAP-012 | documentation | low | repo orientation | non_blocker | Refresh stale src/ path mirrors and maturity claims so docs stop overstating GUI portability or direct server startup readiness. | Multiple docs still point at src/... paths or stronger portability/readiness than the live code warrants. |

## Hard Blockers

- GAP-001: server startup - Fix REPO_ROOT_HINT so direct script or module invocation resolves appshell and data/registries from the live repo root.
- GAP-002: session boot - Make session_boot honor the save root/session artifact location already supported by session_create.
- GAP-003: local playtest bootstrap - Publish one canonical repo-local command that wraps session creation, local authority boot, and attach/status reporting.
- GAP-004: launcher supervised sessions - Resolve the server child exit_code 3 / attach refusal path before relying on launcher supervision for internal sessions.
- GAP-007: multiplayer transport - Defer broader multiplayer until TCP/UDP or another external transport is implemented beyond loopback stubs.

## Near-Term TODOs

- GAP-005: launcher native shell - Keep using the Python launcher/AppShell for baseline work; defer native launcher GUI/TUI completion.
- GAP-006: setup native shell - Treat tools/setup/setup_cli.py as canonical for now and defer native setup shell completion.
- GAP-008: green gate confidence - Run FAST validation to completion after audit artifacts are in place and capture a fresh report.
- GAP-009: installed-mode flows - Materialize or register a real install manifest/registry when moving from repo-local playtests to installed builds.
- GAP-010: semantic subsystems - Integrate these subsystems incrementally after the baseline boot/session loop is stable.
- GAP-011: game runtime shell - Keep reusing engine/game libraries already wired into client/server, but treat remaining stub-tagged library shells as incomplete until proven otherwise.

## Low-Priority TODOs

- GAP-012: repo orientation - Refresh stale src/ path mirrors and maturity claims so docs stop overstating GUI portability or direct server startup readiness.
