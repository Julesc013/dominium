# ULTRA REPO AUDIT PRODUCT ASSEMBLY PLAN

Recommended near-term product target: Repo-local TUI/headless baseline using the verify build, default profile bundle, default pack lock, loopback authority only, and AppShell launcher/setup control surfaces.

## Assembly Slices

| Slice | Required Subsystems | Missing Glue | Recommended Surface | Stop Conditions |
| --- | --- | --- | --- | --- |
| Repo-local bootstrap | build_verify_lane<br>appshell_bootstrap<br>release_control_plane | None if existing verify binaries are acceptable; otherwise run cmake --preset verify and build the preset. | Use verify preset plus repo_wrapper_shim dist/ manifest. | verify configure succeeds<br>verify binaries exist or are rebuilt |
| Setup and launcher shell | setup_python_surface<br>launcher_python_surface<br>packs_profiles_locks | Document Python/AppShell commands as canonical repo-local shells.<br>Keep compiled launcher/setup as wrappers only. | Use python tools/setup/setup_cli.py and python tools/launcher/launch.py. | compat-status works<br>profiles list works<br>packs list works |
| Session create/materialize | session_pipeline<br>packs_profiles_locks<br>schema_registry_support | Keep saves under canonical saves/ or fix session boot save-root coupling. | Use tools/xstack/session_create.py with bundle.mvp_default plus pack_lock.mvp_default. | session_spec.json exists<br>universe_identity/state exist |
| Local authoritative loopback runtime | local_singleplayer_loopback<br>server_authority_loopback<br>net_transports | Publish a single clear wrapper that calls the currently functional loopback controller path. | Use local singleplayer controller / launcher supervision, but limit transport expectations to loopback only. | handshake accepted<br>compat status emitted<br>server status reachable |
| Save/load/resume path | session_pipeline<br>release_control_plane | Fix session_boot saves-root coupling before relying on non-default save roots.<br>Confirm client-facing load/resume path after session boot is stable. | Prefer canonical saves/<save_id> layout for now. | session boot succeeds from a saved session<br>resume path can be repeated |
| Internal playtest v0 | client_runtime_ui<br>server_authority_loopback<br>launcher_python_surface<br>setup_python_surface<br>validation_ci_surface | Stabilize one canonical start/status/stop flow.<br>Capture a short repeatable smoke checklist. | Headless/TUI local authority only, default bundle/lock, repo-local manifest, FAST validation after boot smoke. | one repo-local session boots<br>client can attach or run loopback parity smoke<br>repeatable save/load check passes |

## Recommended Assembly Order

1. Lock onto the verify lane and confirm existing verify binaries or rebuild them.
2. Treat tools/setup/setup_cli.py and tools/launcher/launch.py as canonical repo-local shells.
3. Use profile.bundle.mvp_default plus locks/pack_lock.mvp_default.json as the baseline content/config pair.
4. Create session artifacts with tools/xstack/session_create.py using the canonical saves layout or a runner fix.
5. Boot local authority through the already functional loopback path, not external multiplayer.
6. Prove one short start -> status -> save/load/resume cycle before broadening scope.
7. Only after that, run FAST validation and selected playtest/CTest suites, then widen to installed-mode, updater, and broader multiplayer work.

## Defer Until After Baseline

- TCP/UDP or any non-loopback multiplayer transport.
- Native launcher/setup GUI completion.
- Broad semantic-domain wiring beyond what the baseline session actually needs.
- Large convergence, rename, or ownership-rebinding work.
