# MVP Gameplay 0 Retro Audit

## Scope

- Objective: freeze the minimal deterministic gameplay loop for `v0.0.0-mock`.
- Baseline dependency: `DOMINIUM_MVP_BASELINE_SEED_0`
- Frozen baseline universe: `instance.baseline_universe_0`
- Delivery target: CLI/TUI harness, not GUI-only interaction.

## Embodiment Controls Available

- Launch/bootstrap:
  - `tools/mvp/runtime_entry.py client --repo-root . --seed "DOMINIUM_MVP_BASELINE_SEED_0" --profile_bundle data/baselines/universe/baseline_profile_bundle.json --pack_lock data/baselines/universe/baseline_pack_lock.json --ui cli`
- Teleport controls:
  - `tool tp /tp sol`
  - `tool tp /tp earth`
  - `tool tp /tp chart.surface.8d9723595c7f.north:0,0,0`
- Inspection control:
  - `tool scan`
- Terrain mutation control:
  - `tool mine`
- Logic interaction controls:
  - `tool probe`
  - `process.logic_compile_request`
  - `tool trace`

## Terrain Edit Commands

- Authoritative edit surface resolves through `process.geometry_remove`.
- Frozen target:
  - `chart_id = chart.surface.8d9723595c7f.north`
  - `cell = 0,0`
  - `volume_amount = 16`
- Result: one baseline surface tile is mined deterministically with no GUI mediator.

## Teleport And Inspect Commands

- Teleport planning is deterministic through `src/embodiment/tools/teleport_tool.py::build_teleport_tool_surface`.
- Inspect output is deterministic through `src/embodiment/tools/scanner_tool.py::build_scan_result`.
- Frozen inspect readout at the baseline tile:
  - elevation proxy `2158`
  - temperature `226`
  - daylight `32`
  - tide height proxy `31`
  - biome `biome.stub.polar`
  - material `material.stone_basic`

## Save/Load Commands

- Save surface: `save_snapshot`
- Reload surface: `load_versioned_artifact`
- Frozen committed save hash: `6717f843285193a0b261aadd424b963502f41fce66755fb18deab2f64c1011dc`

## Proof Anchor Capture

- Anchor builder: `tools/mvp/baseline_universe_common.py::_proof_anchor_row`
- Epoch anchor authority: `src/time/epoch_anchor_engine.py::build_epoch_anchor_record`
- Frozen checkpoints reused by Ω-3:
  - `T0` initialization
  - `T1` post-refinement
  - `T2` after first terrain edit
  - `T3` after save-reload

## Replay Mechanism

- Gameplay verification surface:
  - `python tools/mvp/tool_verify_gameplay_loop.py --repo-root . --seed-text "DOMINIUM_MVP_BASELINE_SEED_0" --snapshot-path data/baselines/gameplay/gameplay_loop_snapshot.json`
- Replay baseline regeneration reuses `tools/mvp/baseline_universe_common.py::generate_baseline_universe`.
- Replay requirement: final `T3` anchor must match both the gameplay reload anchor and the frozen Ω-2 baseline anchor.

## CLI/TUI Scriptability Result

- All required actions in the minimal loop are callable through CLI/TUI surfaces.
- No step requires renderer-only state or a GUI event path.
- The frozen gameplay loop can therefore serve as both the human demo path and the deterministic smoke harness.
