# ULTRA REPO AUDIT PLAYTEST READINESS

| Question | Answer |
| --- | --- |
| Can a human boot anything now? | yes_but_not_a_polished_playable_product_loop |
| Recommended baseline | Playable Baseline v0 |
| Broader multiplayer ready? | no |
| Installed-mode ready? | not yet |

## Current Evidence

- verify binaries for client/server/launcher/setup/tools exist and help/smoke paths were exercised
- launcher and setup AppShell surfaces are live and enumerate packs/profiles/compatibility
- local loopback singleplayer handshake exists behind an internal controller path

## Missing Before Internal Playtesting

- One canonical repo-local start command that creates or reuses a session and boots the local authority path clearly.
- A fix or workaround for session_boot save-root coupling so repeatable session artifacts can boot where they are created.
- Confidence that launcher-supervised server/client startup does not exit early or fail attach.

## Missing Before Repeatable Playtesting

- Repeatable save/load/resume proof on the canonical baseline path.
- A completed FAST validation or narrowed baseline smoke gate that is actually green.
- Documented operator instructions that prefer the stronger Python/AppShell surfaces over stub-heavy native shells.

## Missing Before Broader Testing

- Non-loopback transport implementation.
- Installed-mode manifest/registry flows instead of repo_wrapper_shim-only discovery.
- Stronger native GUI/TUI completion for launcher/setup if non-technical users are expected.

## Playable Baseline v0

- Repo-local, single-machine, loopback-authoritative, TUI/headless-first baseline using bundle.mvp_default, pack_lock.mvp_default, the verify build outputs, and launcher/setup AppShell shells.
- Every major ingredient already exists in code, and the main missing work is path hardening and startup glue, not greenfield feature creation.

## Minimum Pass Criteria

1. cmake --preset verify completes and the verify binaries exist.
2. setup_cli.py and launch.py compat-status both report a live release manifest and pack/profile visibility.
3. session_create writes a complete session artifact bundle under the canonical or supported saves layout.
4. A local authority boot reaches accepted handshake/compat status and can be checked with a status command or equivalent log proof.
5. A save/load or resume cycle can be repeated at least once on the chosen baseline path.
6. FAST validation or a tighter agreed baseline smoke suite passes after assembly work.
