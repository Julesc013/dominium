# ULTRA REPO AUDIT SYSTEM INVENTORY

Implementation-first ledger of the live repo state as inspected on 2026-04-06.

## Root Snapshot

| Root | Files | Approx Size | Top Extensions |
| --- | --- | --- | --- |
| engine | 669 | 4.6 MB | .h:338, .c:209, .cpp:87, .py:19 |
| game | 618 | 3.1 MB | .cpp:220, .h:214, .c:46, .toml:39 |
| client | 77 | 1.4 MB | .py:25, .h:24, .c:23, .cpp:3 |
| server | 52 | 505.9 KB | .cpp:23, .h:19, .py:8, .txt:1 |
| launcher | 42 | 170.4 KB | .h:25, .c:11, .cpp:2, .txt:1 |
| setup | 100 | 405.5 KB | .bat:20, .py:19, .sh:17, .in:12 |
| appshell | 31 | 368.5 KB | .py:31 |
| tools | 3693 | 26.7 MB | .py:2936, .json:132, .cpp:126, <no_ext>:121 |
| release | 6 | 169.0 KB | .py:6 |
| security | 4 | 40.3 KB | .py:4 |
| runtime | 2 | 6.6 KB | .py:2 |
| net | 17 | 306.2 KB | .py:17 |
| validation | 2 | 75.8 KB | .py:2 |
| packs | 256 | 392.3 KB | .json:248, .py:4, .md:1, .asc:1 |
| schema | 996 | 1.2 MB | .schema:824, .md:168, .json:4 |
| schemas | 587 | 1.4 MB | .json:586, .md:1 |
| docs/planning | 57 | 712.3 KB | .md:57 |
| specs/reality | 7 | 118.3 KB | .md:7 |

## Canon/Planning/Doctrine

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonical governance and planning packet | AGENTS.md<br>docs/canon/<br>docs/planning/<br>docs/runtime/<br>docs/release/<br>specs/reality/<br>data/planning/<br>data/runtime/<br>data/release/<br>data/reality/ | Markdown, JSON | doctrinal_only | authoritative_doctrine | - | infrastructure | Audit read the required doctrine packet before classifying implementation roots. |

## Client/Ui/Ux

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Client runtime, viewer shell, and compatibility-aware UI | client/ | C, C++, Python | implemented_and_used | wired_to_entrypoints | client_binary_verify, client_mvp_runtime_entry | product_facing | client.exe help and headless smoke both succeeded; client/app/main_client.c contains extensive compatibility and UI flow handling. |

## Content/Worldgen/Domain Surfaces

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Semantic domain, worldgen, and process engines | geo/<br>logic/<br>materials/<br>process/<br>control/<br>meta/<br>worldgen/ | Python | implemented_but_isolated | partially_wired | - | runtime_and_content | Many substantive engine files exist, but the audit did not verify a public product runpath that exercises most of them end to end. |
| Pack, profile, lock, and template baseline data | packs/<br>profiles/<br>locks/<br>data/session_templates/ | JSON | implemented_and_used | wired_to_entrypoints | launcher_python_appshell, setup_python_appshell, xstack_session_create | content_and_configuration | Audit verified profile.bundle.mvp_default, locks/pack_lock.mvp_default.json, data/session_templates/session.mvp_default.json, and live packs list output. |

## Editors/Inspectors/Tools

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Audit and repo-inspection tools | tools/audit/<br>tools/auditx/ | Python | partial | implemented_but_not_critical_to_boot | - | tooling | Repo contains substantial audit tooling and many generated reports, but some auditx analyzers still carry TODO markers and were not re-run during this audit. |

## Launcher/Setup

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Launcher Python/AppShell command surface | tools/launcher/launch.py | Python | implemented_and_used | wired_to_entrypoints | launcher_python_appshell | product_facing | compat-status, profiles list, packs list, and launcher status all ran during audit. |
| Compiled launcher shell | launcher/ | C, C++ | partial | wired_but_fragile | launcher_binary_verify | product_facing | launcher.exe help and smoke ran, but launcher_config_stub.c, launcher_profile_stub.c, launcher_process_stub.c, launcher_gui_stub.c, and launcher_tui_stub.c remain explicit stubs. |
| Setup Python/AppShell command surface | tools/setup/setup_cli.py<br>tools/setup/build.py | Python | implemented_and_used | wired_to_entrypoints | setup_python_appshell | product_and_release | setup_cli.py help, compat-status, profiles list, and packs list all succeeded during audit. |
| Compiled setup shell | setup/ | C, Python | partial | wired_but_fragile | setup_binary_verify | product_facing | setup.exe help worked and smoke returned `setup status: ok (stub)`; setup GUI/TUI frontends are thin wrappers rather than verified full products. |

## Launcher/Setup/Client Shell

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AppShell bootstrap, compatibility, IPC, and supervisor | appshell/ | Python | implemented_and_used | wired_to_entrypoints | launcher_python_appshell, setup_python_appshell, client_mvp_runtime_entry, server_python_module | product_and_infrastructure | Launcher and setup compat-status/status flows completed and surfaced manifest, compatibility, and supervisor state. |

## Registries/Schemas/Data Support

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonical schemas and registries | schema/<br>schemas/<br>data/registries/ | JSON, Markdown | implemented_and_used | wired_to_entrypoints | xstack_session_create, xstack_session_boot, setup_python_appshell, validation_python | infrastructure | SessionX, release, and trust code all import schema or registry loaders; doctrine marks schema/ over schemas/ as canonical. |

## Release/Trust/Packaging

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Release manifest and update resolution control plane | release/<br>updates/<br>dist/manifests/release_manifest.json<br>repo/release_policy.toml | Python, JSON, TOML | implemented_and_used | wired_to_entrypoints | setup_python_appshell, launcher_python_appshell | infrastructure_and_release | Launcher and setup compat-status both found dist/manifests/release_manifest.json and reported repo_wrapper_shim install discovery. |
| Offline-first trust verification | security/ | Python | implemented_and_used | wired_to_entrypoints | setup_python_appshell, launcher_python_appshell | infrastructure_and_release | security/trust/trust_verifier.py defines offline trust policy and signature verification helpers used by release_manifest_engine.py and update_resolver.py. |
| Static update feed artifacts | updates/ | JSON, Markdown | implemented_but_isolated | support_data_only | setup_python_appshell | release_support | updates/ contains stable.json, beta.json, nightly.json, pinned.json, changelog.json, and README.md, but no update runtime code lives there. |

## Runtime/Engine/Core

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Engine and game core libraries | engine/<br>game/ | C, C++ | partial | wired_to_entrypoints | client_binary_verify, server_binary_verify, ctest_verify | runtime | Engine and game roots are large and heavily tested, but game/dominium_game_stub.c still marks part of the runtime library shell as a stub. |

## Server/Net/Shard

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Authoritative server boot and deterministic loopback transport | server/ | C, C++, Python | implemented_and_used | wired_to_entrypoints | server_binary_verify, server_python_script, server_python_module | product_facing | server.exe help and smoke succeeded; server/net/loopback_transport.py and server/server_boot.py implement negotiation, ack handling, and read-only refusal. |
| Transport layer | net/<br>server/net/ | Python | partial | wired_for_loopback_only | server_binary_verify, local_singleplayer_internal_api | runtime | Loopback transport is real and used; net/transport/tcp_stub.py and udp_stub.py explicitly refuse with not_implemented errors. |

## Session/Gameplay

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Local singleplayer controller and loopback attach | client/local_server/<br>runtime/process_spawn.py<br>server/net/loopback_transport.py | Python | partial | wired_internal_only | local_singleplayer_internal_api, client_mvp_runtime_entry | product_facing | Direct start_local_singleplayer invocation produced accepted handshake and compat payloads, but the public CLI bootstrap is still unclear. |

## Session/Save/Load/Replay

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| XStack session create and boot pipeline | tools/xstack/session_create.py<br>tools/xstack/session_boot.py<br>tools/xstack/sessionx/ | Python | partial | wired_but_fragile | xstack_session_create, xstack_session_boot | product_and_tooling | session_create completed successfully, but runner.py hard-codes repo_root/saves/<save_id> and blocked alternate saves-root boot. |

## Tests/Validation/Ci

| Subsystem | Roots | Languages | Maturity | Usage | Entrypoints | Surface | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CMake verify lane and build boundary checks | CMakeLists.txt<br>CMakePresets.json<br>scripts/ | CMake, Python | implemented_and_used | wired_to_entrypoints | cmake_preset_verify | infrastructure | cmake --preset verify completed successfully on 2026-04-06 and wrote out/build/vs2026/verify. |
| Validation, TestX, CTest, and playtest suites | tools/validation/<br>tools/xstack/testx_all.py<br>tests/<br>validation/ | Python, C++ | implemented_and_used | wired_to_entrypoints | validation_python, testx_all_python, ctest_verify | tooling_and_infrastructure | tool_run_validation.py and testx_all.py exist; ctest -N enumerated 493 tests including playtest_scenario_parity, playtest_variant_replay, playtest_replay_regression, and playtest_mode_parity. |
