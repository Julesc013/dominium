# GLOBAL PERFORMANCE & BOUNDEDNESS REVIEW

Date: 2026-03-05
Scope: `GLOBAL-REVIEW-REFRACTOR-1 / Phase 7`

## Domains Audited
- SIG
- MOB
- ELEC
- THERM
- FLUID
- CHEM

## Tier/Cost Contract Coverage
- Verified `data/registries/tier_contract_registry.json` entries include:
  - `supported_tiers`
  - `deterministic_degradation_order`
  - `cost_model_id`
- This satisfies deterministic degrade-order declaration and budget policy linkage requirements for audited domains.

## Stress and Boundedness Evidence
- FLUID stress harness:
  - tool: `tools/fluid/tool_run_fluid_stress.py`
  - result: `complete`
  - fingerprint: `7397f47d458083167de95edeb345a4846072dccbc7eeb5751beecbc8298c50fb`
- CHEM stress harness:
  - tool: `tools/chem/tool_run_chem_stress.py`
  - result: `complete`
  - fingerprint: `c492e642561419a5de969fcde85652ac586b69fbe66cd7dade3ffb4e3e50522e`
  - assertions: bounded evaluation, deterministic ordering, degradation order deterministic, no silent mass/energy changes, outputs logged
- THERM stress harness:
  - tool: `tools/thermal/tool_run_therm_stress.py`
  - result: `complete`
  - fingerprint: `03b27c1daf370a2b4e307f07e3609086248d87670a691925447c3f47a563a4c1`
- ELEC stress harness (bounded configuration run):
  - tool: `tools/electric/tool_run_elec_stress.py`
  - scenario override: `generators=4, loads=16, storage=2, breakers=4, graphs=2, shards=2, ticks=16`
  - result: `complete`
  - fingerprint: `4687e8e407241e5e9c233d50a2fd3a9618afc479f5359cc040033f56cfdc2cdb`
- SIG stress harness (bounded configuration run):
  - tool: `tools/signals/tool_run_sig_stress.py`
  - override: `ticks=16`
  - result: `complete`
  - fingerprint: `c16779d6f9d3a532611756af5897b1d91766bdaadcd2a90a224627a1ccaf5100`
- MOB stress harness:
  - tool: `tools/mobility/tool_mobility_stress.py`
  - run: `ticks=16, dense_vehicles=64`
  - result: `complete`
  - report fingerprint: `32fa0f25a990e8fcfb743f5c29c638b22e6c4a8d771310d24419cccf3068ec3b`
  - mismatch_count: `0`

## Targeted Refactor Applied
- File: `tools/chem/tool_run_chem_stress.py`
- Change: deterministic-order assertion now validates ordering by deterministic execution keys (`tick`, `run_id`, domain identifiers) instead of hashed IDs.
- Reason: the previous checker compared insertion order against lexicographic hash IDs, producing false negatives while execution remained deterministic.
- Semantics impact: none (harness assertion fix only).

## Outcome
- Deterministic degradation and bounded-evaluation discipline verified across major domains.
- No unbounded cascade evidence found in validated harness runs.
- Phase 7 stop conditions not triggered.
