# Industrial Processing Model

Status: CANONICAL  
Last Updated: 2026-03-05  
Scope: CHEM-2 deterministic industrial processing contract (materials processing, refining, catalysts, batch quality).

## 1) Purpose

Define CHEM processing as deterministic reaction-driven transformation, not recipe scripting, while preserving:

- process-only mutation,
- stoichiometric mass discipline,
- PHYS-3 energy-ledger discipline,
- PHYS-4 entropy linkage,
- MAT provenance continuity.

## 2) Processing Is Chemistry

A processing run is modeled as:

- `ReactionProfile` (stoichiometric + energy transform declaration),
- `ProcessEquipmentProfile` (supported reactions + catalyst slots + spec),
- condition window (temperature/pressure/entropy/spec-compliance inputs).

Runtime must never bypass this with ad-hoc recipe branches.

## 3) Catalysts

Catalysts are deterministic modifiers, expressed through constitutive model inputs.

Catalyst behavior in CHEM-2:

- does not create mass or energy,
- can increase/decrease rate and yield deterministically,
- must be represented in run metadata and provenance.

## 4) Yield and Defects

Yield is model-driven:

`yield_factor = f(temperature, pressure_head_stub, entropy_index, catalyst_present, spec_compliance_state)`

Defect flags are deterministic outputs of model evaluation:

- `contamination_present`
- `underprocessed`
- `overprocessed`
- `out_of_spec`

No silent quality penalties are allowed.

## 5) Contamination Discipline

Contamination is model-driven from:

- equipment condition (wear/corrosion proxies),
- input batch contamination tags,
- process compliance conditions.

Output contamination tags must be logged and attached to output batch quality rows.

## 6) Traceability Contract

Each output batch produced by processing must include traceability metadata:

- `input_batch_ids`
- `reaction_id`
- `equipment_id`
- `start_tick` / `end_tick`

This enables future QA, recall, and compliance gameplay without reconstructive heuristics.

Provenance classification policy for CHEM-2:

- process-run lifecycle events are canonical (`process_run_start`, `process_run_tick`, `process_run_end`),
- batch quality is canonical because it affects downstream gameplay acceptance and QA gating,
- compaction may summarize derived inspection overlays only, never canonical process-run or quality truth rows.

## 7) Tier Contract

CHEM processing tiers:

- `C0`: bookkeeping transform (instant deterministic completion),
- `C1`: deterministic rate-based progression,
- `C2`: ROI lab-micro reserved (future).

Budget degradation must be explicit and logged.

## 8) Coupling Contract

CHEM couplings are explicit only:

- CHEM -> THERM: `transform.chemical_to_thermal`
- CHEM -> POLL: pollutant-tagged emission quantities
- CHEM -> MECH: corrosion/degradation via constitutive model outputs
- CHEM -> FLUID: species transport via fluid-carried inventory/material pathways

Direct cross-domain mutation is forbidden.

## 9) Canonical Invariants

- A1 Determinism is primary
- A2 Process-only mutation
- A6 Provenance is mandatory
- PHYS-3: registered energy transformation + ledger entry required
- PHYS-4: entropy contribution is explicit for irreversible transforms
- META-CONTRACT: declared coupling/explain contracts required

## 10) Non-Goals

- full kinetics/equilibrium solvers,
- molecule simulation,
- mandatory POLL runtime solver in CHEM-2 baseline.

## 11) Explain and Inspection Surfaces

CHEM-2 inspection sections:

- `section.chem.process_runs`
- `section.batch.quality_summary`
- `section.chem.yield_factors`

CHEM-2 explain contracts:

- `explain.low_yield`
- `explain.contamination`
- `explain.out_of_spec_batch`

Diegetic presentation guidance:

- show an out-of-spec warning marker for affected output batches,
- show contamination marker when contamination tags are present.

## 12) Proof and Replay Hooks

CHEM-2 process-run truth integrates deterministic proof surfaces:

- `process_run_hash_chain`
- `batch_quality_hash_chain`
- `yield_model_hash_chain`

Control proof bundles must carry these chains when CHEM process-run rows are present in the tick window.

Replay verification tool:

- `python tools/chem/tool_replay_process_run.py --state-path <state.json> --expected-state-path <baseline.json>`

The verifier checks:

- recorded vs replayed process-run/quality/yield hash chains,
- deterministic yield stability for equivalent input contexts,
- process-run ledger linkage to `transform.chemical_to_thermal`,
- batch mass and quality sanity constraints.
