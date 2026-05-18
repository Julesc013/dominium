# MOVE-ROUTER-02 Blockers

Status: OPEN
Generated: 2026-05-18

## Blocking Classes

1. RepoX ruleset discovery still expects `repo/repox/rulesets`.
   Current target is `contracts/repo/repox/rulesets`.

2. Registry and pack path consumers still expect old bad-root paths.
   Common stale forms include `data/registries/*`, `data/packs`, and `packs/*`.

3. Import fallout remains in deeper test/tool lanes.
   Observed examples include missing `compat`, missing
   `tools.libraries.install.install_discovery_engine`, and missing symbols from
   the old `contracts.capability.capability` package shape.

4. Frozen contract hashes and generated evidence still encode old path surfaces.
   These need reviewed refresh or explicit frozen-evidence preservation.

5. Known semantic lint debt is still visible in broader test lanes.
   `slice0_hardcoded_ids` remains a separate semantic lint blocker when invoked
   through the broader suite.

6. Some platform/renderer tests still expect old source locations such as
   `launcher/cli/launcher_cli_main.c` instead of `apps/launcher/cli/launcher_cli_main.c`.

## Non-Blockers For This Closeout

- Former bad-root tracked file count is 0.
- No target collision was introduced by this repair pass.
- No routed files were moved back to former bad roots.
- No generated build/projection/release outputs were intentionally staged.

## Required Follow-Up

`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`
