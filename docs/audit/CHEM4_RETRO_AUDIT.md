Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# CHEM-4 Retro Consistency Audit

Date: 2026-03-05
Scope: Chemistry stress/proof/regression hardening preflight (CHEM-4).

## Inputs Audited
- `tools/xstack/sessionx/process_runtime.py`
- `src/chem/process_run_engine.py`
- `src/chem/degradation/degradation_engine.py`
- `src/control/proof/control_proof_bundle.py`
- `tools/chem/tool_replay_combustion_window.py`
- `tools/chem/tool_replay_process_run.py`
- `tools/chem/tool_replay_degradation_window.py`
- `data/registries/reaction_profile_registry.json`
- `data/registries/energy_transformation_registry.json`
- `data/registries/degradation_profile_registry.json`

## Findings
1. Reaction/process evaluation loops are budget-capped but stress-envelope tooling is missing.
- `process.process_run_tick` already enforces `chem_max_process_run_evaluations_per_tick` and logs deterministic degrade decisions (`degrade.chem.process_run_budget`).
- No CHEM-specific deterministic stress scenario generator or stress harness exists yet.

2. Energy ledger integration exists for combustion and process runs.
- Combustion and process-run pathways call `_record_energy_transformation_in_state(...)`.
- No evidence of direct CHEM energy mutation bypass in audited runtime paths.

3. Emission outputs are recorded, but envelope-level assertions are not centralized.
- Combustion and process runs emit deterministic emission rows and maintain `emission_hash_chain`.
- No dedicated CHEM stress harness currently verifies "all emissions logged" at scale.

4. Degradation updates are model/hazard-driven in current CHEM-3 runtime.
- `process.degradation_tick` routes through `evaluate_degradation_tick(...)` and hazard/effect pathways.
- No direct ad-hoc degradation bypass found in audited CHEM runtime files.

5. Proof chains exist but CHEM-4 aggregate replay verification is missing.
- Existing chains: combustion/process/batch-quality/yield/degradation.
- Missing CHEM-wide replay-window verifier that validates combined reaction+energy+emission+degradation hashes.

## Gap Classification
- Unbudgeted reaction loops: **partial coverage** (runtime capped, no CHEM stress tool).
- Missing energy ledger entries: **no direct gap found** in audited CHEM runtime paths.
- Emission outputs not logged: **no direct gap found**; CHEM-4 harness-level assertion needed.
- Degradation bypass hazard engine: **no direct gap found** in audited CHEM-3 runtime path.

## Migration Plan (CHEM-4)
1. Add deterministic `tool_generate_chem_stress` and `tool_run_chem_stress`.
2. Expose and assert deterministic degradation-order policy in CHEM stress reports.
3. Add CHEM conservation verifiers (mass, energy, entropy) for stress/replay outputs.
4. Add CHEM replay-window verifier combining reaction/ledger/emission/degradation chains.
5. Add `chem_full_baseline.json` regression lock with `CHEM-REGRESSION-UPDATE` tag requirement.
6. Promote CHEM envelope governance via RepoX/AuditX/TestX hard checks.

## Risk Notes
- Keep process-only mutation intact; no direct mass/energy/degradation writes.
- Keep deterministic ordering fixed by reaction/run/target IDs.
- Preserve existing CHEM semantics; CHEM-4 adds envelope and governance only.
