# ULTRA REPO AUDIT EXECUTIVE SUMMARY

## What The Repo Appears To Be Today

- The live repo is already a broad deterministic simulation platform with real product-shell code, large engine/game/test surfaces, AppShell control flows, release/trust infrastructure, and pack/profile/session data.
- The strongest live product surfaces are the verify build binaries plus the Python/AppShell launcher and setup shells.
- The repo is not feature-empty. It is integration-fragile: several key pieces exist but the public startup path for a first playtest is still spread across multiple entrypoints.

## Strongest Implemented Surfaces

- Verify build lane and existing verify binaries for client, server, launcher, setup, and tools.
- AppShell bootstrap, compatibility negotiation, install discovery shim, IPC/supervisor, and pack/profile enumeration.
- Release manifest, update resolver, and trust verification surfaces.
- Loopback authority/server/client handshake path and a direct local singleplayer controller.
- Large validation and test surface, including 493 registered CTest entries and dedicated playtest suites.

## Most Reusable Right Now

| Reusable Unit | Paths | Why It Matters |
| --- | --- | --- |
| Verify build preset and existing verify binaries | CMakeLists.txt<br>CMakePresets.json<br>out/build/vs2026/verify/bin/ | This is the fastest verified path to runnable client/server/tools shells. |
| Launcher and setup AppShell command surfaces | tools/launcher/launch.py<br>tools/setup/setup_cli.py<br>appshell/ | These are the strongest live repo-local command surfaces for packs, profiles, compat, trust, and supervision. |
| Default profile bundle, pack lock, and session template | profiles/bundles/bundle.mvp_default.json<br>locks/pack_lock.mvp_default.json<br>data/session_templates/session.mvp_default.json | They already define a coherent baseline configuration for a near-term playable slice. |
| Loopback authority and local singleplayer controller | client/local_server/local_server_controller.py<br>server/net/loopback_transport.py<br>runtime/process_spawn.py | This is the most evidence-backed way to get a local authoritative playtest loop before real network transport exists. |
| Release manifest, update resolver, and trust verifier | release/release_manifest_engine.py<br>release/update_resolver.py<br>security/trust/trust_verifier.py | These surfaces are already wired into setup/launcher compatibility and should be reused rather than replaced. |
| CTest/TestX/validation surface | tools/validation/<br>tools/xstack/testx_all.py<br>tests/playtest/ | The repo already has broad coverage scaffolding; it should gate baseline assembly rather than be rebuilt. |

## Most Incomplete

- A single canonical playtest startup command.
- Direct Python server startup.
- Session boot when session artifacts live outside the default saves/ root.
- Native launcher/setup GUI/TUI completion.
- Any multiplayer transport beyond loopback.

## Shortest Path To A Playable Baseline

1. Lock onto the verify lane and confirm existing verify binaries or rebuild them.
2. Treat tools/setup/setup_cli.py and tools/launcher/launch.py as canonical repo-local shells.
3. Use profile.bundle.mvp_default plus locks/pack_lock.mvp_default.json as the baseline content/config pair.
4. Create session artifacts with tools/xstack/session_create.py using the canonical saves layout or a runner fix.
5. Boot local authority through the already functional loopback path, not external multiplayer.
6. Prove one short start -> status -> save/load/resume cycle before broadening scope.
7. Only after that, run FAST validation and selected playtest/CTest suites, then widen to installed-mode, updater, and broader multiplayer work.

## Biggest Risks

- Startup ambiguity: too many overlapping entrypoints still lead to different levels of readiness.
- Path coupling: server_main.py repo-root math and session_boot saves-root assumptions both break practical flows.
- Supervision stability: launcher status shows evidence of prior exited child/attach failure.
- Doc drift: several derived docs still overstate portability or reference stale src/ paths.

## Recommended Integration Order

1. Lock onto the verify lane and confirm existing verify binaries or rebuild them.
2. Treat tools/setup/setup_cli.py and tools/launcher/launch.py as canonical repo-local shells.
3. Use profile.bundle.mvp_default plus locks/pack_lock.mvp_default.json as the baseline content/config pair.
4. Create session artifacts with tools/xstack/session_create.py using the canonical saves layout or a runner fix.
5. Boot local authority through the already functional loopback path, not external multiplayer.
6. Prove one short start -> status -> save/load/resume cycle before broadening scope.
7. Only after that, run FAST validation and selected playtest/CTest suites, then widen to installed-mode, updater, and broader multiplayer work.
