# ULTRA REPO AUDIT ENTRYPOINTS AND RUNPATHS

Live entrypoints identified from the current repository plus direct audit execution.

## Entrypoint Table

| ID | Path | Type | Canonicality | Likely Runnable | Prerequisites | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| cmake_preset_verify | cmake --preset verify | configure_preset | canonical | yes | CMake, configured verify toolchain, Python | Best starting point for repo-local build verification. |
| client_binary_verify | out/build/vs2026/verify/bin/client.exe | compiled_binary | canonical | yes | verify build outputs, Windows/MSVC verify bin tree | Current easiest verified client path is headless or minimal UI smoke. |
| server_binary_verify | out/build/vs2026/verify/bin/server.exe | compiled_binary | canonical | yes | verify build outputs, Windows/MSVC verify bin tree | Verified surface today is deterministic loopback/headless smoke, not external multiplayer. |
| launcher_binary_verify | out/build/vs2026/verify/bin/launcher.exe | compiled_binary | wrapper | yes | verify build outputs | Practical repo-local launcher control is currently stronger through tools/launcher/launch.py. |
| setup_binary_verify | out/build/vs2026/verify/bin/setup.exe | compiled_binary | wrapper | yes | verify build outputs | Practical repo-local setup flow is stronger through tools/setup/setup_cli.py. |
| tools_binary_verify | out/build/vs2026/verify/bin/tools.exe | compiled_binary | canonical | yes | verify build outputs | tools_host_main.c still identifies the host as a stub to be replaced by a tool router. |
| launcher_python_appshell | python tools/launcher/launch.py | python_cli | canonical | yes | Python, repo root, dist/manifests/release_manifest.json | Best launcher surface for repo-local audit and likely baseline assembly. |
| setup_python_appshell | python tools/setup/setup_cli.py | python_cli | canonical | yes | Python, repo root, dist/manifests/release_manifest.json | This is the strongest live setup surface in the repo today. |
| server_python_script | python server/server_main.py | python_cli | documented_canonical | no | Python, correct repo-root resolution | Do not recommend as a baseline command until repo_root_hint is fixed. |
| server_python_module | python -m server.server_main | python_cli | experimental | no | Python, correct repo-root resolution | Slightly farther than direct script mode, but still blocked. |
| client_mvp_runtime_entry | python tools/mvp/runtime_entry.py client | python_cli | experimental | yes | Python, repo root, selected mode/profile arguments | Useful as a compatibility wrapper, not yet a dependable playtest command. |
| xstack_run | python tools/xstack/run.py | python_cli | canonical | yes | Python, repo root | Useful for governance/test orchestration rather than direct product play. |
| xstack_session_create | python tools/xstack/session_create.py | python_cli | canonical | yes | Python, repo root, pack/profile/template inputs | Works now and is part of the shortest path to a baseline session. |
| xstack_session_boot | python tools/xstack/session_boot.py | python_cli | canonical | yes | Python, repo root, session artifacts in expected saves layout | Recommend using canonical saves/<save_id> until the coupling bug is fixed. |
| validation_python | python tools/validation/tool_run_validation.py | python_cli | canonical | yes | Python, repo root | Exists and is wired, but audit did not finish a full FAST run. |
| testx_all_python | python tools/xstack/testx_all.py | python_cli | canonical | yes | Python, repo root | Best fit for large validation sweeps once baseline boot is stable. |
| ctest_verify | ctest --test-dir out/build/vs2026/verify | test_harness | canonical | yes | verify build tree | Includes playtest, capability, distribution, trust, and performance suites. |
| local_singleplayer_internal_api | client.local_server.local_server_controller.start_local_singleplayer | internal_api | internal | yes | Python, repo root, profile bundle, pack lock, server config | Internal path is more functional today than the public CLI wrapper. |

## Verified or Partially Verified Runpaths

1. Repo-local binary smoke: `cmake --preset verify` -> `out/build/vs2026/verify/bin/{client,server,launcher,setup,tools}.exe --help/--smoke`.
2. Launcher shell: `python tools/launcher/launch.py compat-status|profiles list|packs list|launcher status` -> AppShell -> release manifest + compatibility + supervisor surfaces.
3. Setup shell: `python tools/setup/setup_cli.py compat-status|profiles list|packs list` -> AppShell -> release/trust/install/pack surfaces.
4. Session materialization: `python tools/xstack/session_create.py ...` -> session_spec + universe_identity + universe_state + contract bundle.
5. Internal local singleplayer: `client.local_server.local_server_controller.start_local_singleplayer(...)` -> loopback handshake + compat status.

## Blocked or Fragile Paths

1. `python server/server_main.py --help` is blocked by repo-root resolution.
2. `python -m server.server_main --help` is also blocked by repo-root/data path resolution.
3. `python tools/xstack/session_boot.py <session_spec>` is only reliable when artifacts live under the expected canonical `saves/<save_id>` layout.
4. `python tools/mvp/runtime_entry.py client --local-singleplayer ...` is still a transitional wrapper rather than a clean playtest launcher.

## Canonical vs Experimental

Canonical today for repo-local work: `cmake --preset verify`, verify binaries, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/testx_all.py`, `tools/validation/tool_run_validation.py`.
Experimental or blocked today: direct `server/server_main.py`, `python -m server.server_main`, `tools/mvp/runtime_entry.py` as a user-facing gameplay bootstrap, any TCP/UDP multiplayer transport path.
