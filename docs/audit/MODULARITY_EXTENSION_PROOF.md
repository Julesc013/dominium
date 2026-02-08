Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# IRC-0 Phase 2: Modularity & Extension Proof

## Representative Exercise

- Exercise type: capability-first extension probe plus command-surface trace.
- Goal under test:
  - capability can be added via data
  - command appears via CLI
  - UI derives command bindings automatically
  - no command-specific branching is required

## Step A: Data-only Capability Extension (PASS)

1. Created temporary probe pack manifest:
   - `tmp/irc0_extension/org.dominium.test.integration_probe/pack_manifest.json`
2. Added capability id:
   - `org.dominium.capability.integration.probe`
3. Validated with canonical validator:
   - `python tools/pack/pack_validate.py --repo-root . --pack-root tmp/irc0_extension/org.dominium.test.integration_probe --format json`
4. Result:
   - `{"issues":[],"ok":true}`

Conclusion: capability declarations can be introduced through manifest data and validated without runtime code edits.

## Step B: Command/CLI/UI Extension Trace (PARTIAL)

Observed command graph authority:
- Canonical command metadata exists in:
  - `libs/appcore/command/command_registry.h`
  - `libs/appcore/command/command_registry.c`
- UI bind generator consumes this registry:
  - `tools/ui_bind/ui_bind_main.cpp`

Observed runtime wiring:
- Shared dispatch surface remains stub:
  - `libs/appcore/command/command_dispatch.c`
- Runtime app CLIs keep local command surfaces (example):
  - `client/app/main_client.c`

Observed generated UI bindings:
- Derived from canonical UI docs and command ids:
  - `libs/appcore/ui_bind/ui_command_binding_table.c`

Result:
- UI derivation path is active for bound UI actions.
- Runtime CLI command surfaces are not fully sourced from `appcore` command registry today.

## Proof Outcome

- `PASS`: data-only capability extension.
- `PASS`: UI binding derivation mechanism is active and deterministic.
- `NOT PROVEN`: "new command appears in runtime CLI without additional wiring."

This is an integration gap, not a semantic failure.

## Rollback / Cleanup

- No committed source changes were made for the probe.
- Temporary probe artifact remains under `tmp/irc0_extension` and is removed in Phase 6 cleanup.
