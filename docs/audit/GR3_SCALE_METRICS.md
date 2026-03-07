# GR3 Scale Metrics

## SYS
Source: `GR3_FULL_SYS_STRESS_MANIFEST.json`
- assertions: all pass
- proof hash summary recorded for collapse/expand, macro outputs, forced expand, certification, health

Source: `GR3_FULL_SYS_CROSS_SHARD_STRESS_MANIFEST.json`
- assertions: all pass
- cross-shard reduced-window deterministic pass

## PROC
Source: `GR3_FULL_PROC_STRESS.json`
- assertions:
  - deterministic ordering: pass
  - bounded micro execution: pass
  - no silent capsule execution: pass
  - no hidden state drift: pass
  - compaction replay anchor match: pass
- key metrics:
  - forced_expand_count: 101
  - compaction_marker_count: 0

## POLL
Source: `GR3_FULL_POLL_STRESS.json`
- assertions: all pass
- proof hash chains present (emission, field, exposure, compliance, decision/degrade)

## SIG
Source: `GR3_FULL_SIG_STRESS.json`
- report assertions:
  - deterministic ordering: pass
  - no silent drop: pass
  - trust updates logged: pass
  - budget applied: pass

## ELEC
Source: `GR3_FULL_ELEC_STRESS.json`
- assertions:
  - deterministic ordering: pass
  - no infinite loops: pass
  - no silent flow mutation: pass
  - no unlogged trips: pass

## THERM
Source: `GR3_FULL_THERM_STRESS.json`
- assertions:
  - deterministic ordering: pass
  - bounded evaluation: pass
  - no silent downgrades: pass
  - no unlogged heat inputs: pass

## FLUID
Source: `GR3_FULL_FLUID_STRESS.json`
- assertions:
  - deterministic ordering: pass
  - bounded evaluation: pass
  - degradation order deterministic: pass
  - all failures logged: pass
  - no silent mass changes: pass

## CHEM
Source: `GR3_FULL_CHEM_STRESS.json`
- assertions: all pass
- key metrics:
  - total_reactions_evaluated: 428
  - max_cost_units_observed: 60
  - emission_total_mass: 386
  - entropy_increment_total: 318

## PROV/Compaction
Source: `GR3_FULL_PROV_STRESS.json`
- result: complete
- key metrics:
  - generated_derived_rows: 3,840,000
  - removed_derived_rows: 3,839,952
  - replay_cost_units: 728

## Hotspots
- Large-window SYS/FLUID/PROV stress invocations exceeded environment timeout cap.
- Reduced deterministic windows were used for completed evidence runs.
- SYS raw archives are now represented by committed manifests because the original raw JSON blobs exceeded hosted Git size limits.
