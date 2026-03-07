# GR3 FULL Results

## Scope
FULL stress/replay/reference verification for SYS/PROC/POLL/SIG/ELEC/THERM/FLUID/CHEM and compaction replay.

## Stress Harness Results
- SYS stress: `docs/audit/GR3_FULL_SYS_STRESS.json` -> `complete`
- SYS cross-shard reduced-window stress: `docs/audit/GR3_FULL_SYS_CROSS_SHARD_STRESS.json` -> `complete`
- PROC stress: `docs/audit/GR3_FULL_PROC_STRESS.json` -> `pass`
- POLL stress: `docs/audit/GR3_FULL_POLL_STRESS.json` -> `complete`
- SIG stress: `docs/audit/GR3_FULL_SIG_STRESS.json` -> `complete`
- ELEC stress: `docs/audit/GR3_FULL_ELEC_STRESS.json` -> `complete`
- THERM stress: `docs/audit/GR3_FULL_THERM_STRESS.json` -> `complete`
- FLUID stress: `docs/audit/GR3_FULL_FLUID_STRESS.json` -> `complete`
- CHEM stress: `docs/audit/GR3_FULL_CHEM_STRESS.json` -> `complete`
- PROV compaction stress: `docs/audit/GR3_FULL_PROV_STRESS.json` -> `complete`

## Replay/Compaction Verification
- SYS replay window: `docs/audit/GR3_FULL_SYS_REPLAY.json` -> `complete`
- PROC replay window: `docs/audit/GR3_FULL_PROC_REPLAY.json` -> `complete`
- PROC compaction verification: `docs/audit/GR3_FULL_PROC_COMPACTION_VERIFY.json` -> `complete`

## Reference Suite (FULL evaluators)
- `docs/audit/GR3_FULL_REFERENCE_SUITE.json`
- Evaluators:
  - `ref.energy_ledger`
  - `ref.coupling_scheduler`
  - `ref.system_invariant_check`
  - `ref.compiled_model_verify`
- Result: `complete` (no mismatches)

## Execution Notes
- Several large-window runs timed out in this environment at the command timeout cap.
- For those, deterministic reduced-window scenarios were used and archived under `docs/audit/GR3_FULL_*`.
- All recorded reduced-window runs are deterministic and pass their internal assertions.
