# ULTRA REPO AUDIT BUILD RUN TEST MATRIX

Conservative status matrix based on direct audit execution or concrete tree evidence.

| Subsystem / Entrypoint | Path | Build | Run | Test | Evidence | Blockers |
| --- | --- | --- | --- | --- | --- | --- |
| cmake verify preset | cmake --preset verify | verified | verified | unknown | Configure completed successfully on 2026-04-06. | - |
| client binary | out/build/vs2026/verify/bin/client.exe | verified | verified | likely | Help and headless smoke both passed; CTest tree contains client_flow_smoke and client_parity. | - |
| server binary | out/build/vs2026/verify/bin/server.exe | verified | verified | likely | Help and headless smoke both passed; CTest tree includes server_discovery and shard tests. | Public Python server entrypoint is still broken outside the compiled binary path. |
| launcher binary | out/build/vs2026/verify/bin/launcher.exe | verified | likely | likely | Help passed; smoke only showed shell-level hooks; CTest registers launcher_help and launcher_cli_tests. | Compiled launcher core remains stub-heavy and public session start was not fully verified. |
| setup binary | out/build/vs2026/verify/bin/setup.exe | verified | likely | likely | Help passed; smoke returned stub status; CTest registers setup_help and setup_install_tests. | Compiled setup wrapper is thinner than the Python/AppShell setup surface. |
| tools binary | out/build/vs2026/verify/bin/tools.exe | verified | verified | likely | Help and smoke passed; CTest registers tools_pack_validate, tools_capability_inspect, tools_auditx. | tools_host_main.c still self-identifies as a stub host. |
| launcher AppShell | python tools/launcher/launch.py | verified | verified | likely | compat-status, profiles list, packs list, and launcher status all ran successfully. | launcher status exposed a prior server child exit_code 3 and attach refusal, so supervision stability is not fully green. |
| setup AppShell | python tools/setup/setup_cli.py | verified | verified | likely | help, compat-status, profiles list, and packs list all ran successfully. | Audit did not execute install apply/update apply against a real install root. |
| server Python script | python server/server_main.py | verified | blocked | unknown | Direct invocation failed due repo-root/import path errors. | server/server_main.py REPO_ROOT_HINT points two directories up instead of to the repo root. |
| session_create | python tools/xstack/session_create.py | verified | verified | likely | Audit successfully created a full session artifact bundle. | - |
| session_boot | python tools/xstack/session_boot.py | verified | blocked | likely | Help works, but alt-root boot failed because runner expects repo_root/saves/<save_id>. | Honor session_spec saves-root metadata or keep using canonical saves/ layout. |
| local singleplayer controller | client.local_server.local_server_controller.start_local_singleplayer | verified | likely | unknown | Direct invocation produced accepted handshake payloads and compat state. | Public CLI wrapper is still ambiguous and no short canonical user-facing command was verified end to end. |
| TestX all-suite | python tools/xstack/testx_all.py | verified | verified | verified | Help works and exposes test profile/shard arguments. | Audit did not execute a full suite run. |
| Unified validation | python tools/validation/tool_run_validation.py | verified | likely | likely | Help works and validator sources exist. | FAST run attempt timed out, so audit cannot mark the lane green. |
| CTest verify tree | ctest --test-dir out/build/vs2026/verify | verified | verified | verified | CTest enumerated 493 tests, including playtest suites and product smoke. | Audit enumerated but did not execute the full test tree. |
| TCP/UDP transport | net/transport/tcp_stub.py and net/transport/udp_stub.py | verified | blocked | unknown | Both transport modules exist as explicit not_implemented stubs. | No external multiplayer transport beyond loopback is implemented. |
