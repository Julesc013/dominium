# ULTRA REPO AUDIT WIRING MAP

## Nodes

| Node | Kind | State | Path |
| --- | --- | --- | --- |
| cmake.verify | build | verified | cmake --preset verify |
| verify.bin | build_artifact | verified | out/build/vs2026/verify/bin/ |
| appshell | shared_shell | implemented_and_used | appshell/ |
| launcher.py | entrypoint | verified | tools/launcher/launch.py |
| setup.py | entrypoint | verified | tools/setup/setup_cli.py |
| client.exe | entrypoint | verified | out/build/vs2026/verify/bin/client.exe |
| server.exe | entrypoint | verified | out/build/vs2026/verify/bin/server.exe |
| session_create | entrypoint | verified | tools/xstack/session_create.py |
| session_boot | entrypoint | blocked | tools/xstack/session_boot.py |
| sessionx.creator | tooling | implemented_and_used | tools/xstack/sessionx/creator.py |
| sessionx.runner | tooling | partial | tools/xstack/sessionx/runner.py |
| local_singleplayer | runtime_api | partial | client/local_server/local_server_controller.py |
| process_spawn | runtime_support | implemented_and_used | runtime/process_spawn.py |
| loopback_transport | runtime_support | implemented_and_used | server/net/loopback_transport.py |
| release_manifest | release_data | implemented_and_used | dist/manifests/release_manifest.json |
| release_engine | release_logic | implemented_and_used | release/release_manifest_engine.py |
| trust_verifier | security_logic | implemented_and_used | security/trust/trust_verifier.py |
| packs_profiles_locks | content_config | implemented_and_used | packs/, profiles/, locks/ |
| ctest | validation | verified | ctest --test-dir out/build/vs2026/verify |
| validation | validation | partial | tools/validation/tool_run_validation.py |
| semantic_python_domains | runtime_domain | implemented_but_isolated | geo/, logic/, materials/, process/, control/, worldgen/ |

## Dependency Edges

| From | Relationship | To | Status |
| --- | --- | --- | --- |
| cmake.verify | produces | verify.bin | verified |
| verify.bin | contains | client.exe | verified |
| verify.bin | contains | server.exe | verified |
| verify.bin | parallel_surface_to | launcher.py | implemented |
| launcher.py | boots_through | appshell | verified |
| setup.py | boots_through | appshell | verified |
| appshell | discovers | release_manifest | verified |
| appshell | consults_via_release_logic | trust_verifier | verified |
| release_engine | imports | trust_verifier | implemented |
| setup.py | enumerates_and_validates | packs_profiles_locks | verified |
| launcher.py | enumerates_and_validates | packs_profiles_locks | verified |
| session_create | delegates_to | sessionx.creator | verified |
| session_boot | delegates_to | sessionx.runner | verified |
| sessionx.creator | materializes_from | packs_profiles_locks | verified |
| sessionx.runner | expects_artifacts_from | packs_profiles_locks | blocked_by_save_root_coupling |
| local_singleplayer | uses_for_local_authority | process_spawn | implemented |
| local_singleplayer | handshakes_over | loopback_transport | verified |
| loopback_transport | runtime_protocol_surface_for | server.exe | verified |
| client.exe | consumes_content_and_compat_expectations | packs_profiles_locks | likely |
| ctest | tests | client.exe | verified_by_enumeration |
| ctest | tests | server.exe | verified_by_enumeration |
| validation | checks | schema_registry_support | implemented |

## Runpath Chains

- repo_local_boot: cmake --preset verify -> out/build/vs2026/verify/bin/{client,server,launcher,setup,tools}.exe -> --help / --smoke [verified]
- launcher_shell_flow: python tools/launcher/launch.py -> appshell bootstrap -> release manifest + pack/profile checks -> supervisor status / attach surface [verified_with_risk]
- setup_shell_flow: python tools/setup/setup_cli.py -> appshell bootstrap -> trust/release/install/pack/profile commands [verified]
- session_pipeline_flow: python tools/xstack/session_create.py -> session_spec + universe artifacts -> python tools/xstack/session_boot.py -> sessionx runner [partial]
- local_singleplayer_flow: client.local_server.local_server_controller.start_local_singleplayer -> runtime.process_spawn or in-proc stub -> server.net.loopback_transport -> compat handshake + control channel [partially_verified]
- validation_flow: python tools/validation/tool_run_validation.py -> python tools/xstack/testx_all.py -> ctest --test-dir out/build/vs2026/verify [verified_by_enumeration_not_full_execution]

## Disconnected Or Weakly Connected Clusters

- semantic_python_domains: geo/, logic/, materials/, process/, control/, worldgen/ - Large implementations exist, but the audit could not tie most of them to a verified public product runpath yet.
- external_multiplayer_transport: net/transport/tcp_stub.py, net/transport/udp_stub.py - Only deterministic loopback is implemented today.
- static_update_feed_data: updates/ - Channel JSON exists, but the directory itself is data-only rather than a runnable update service.
