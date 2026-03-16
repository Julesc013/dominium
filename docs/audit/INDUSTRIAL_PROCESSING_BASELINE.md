Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CHEM-2 Industrial Processing Baseline

Date: 2026-03-05  
Scope: CHEM-2 phases 8-11 completion (proof/replay, enforcement, TestX, final gate report).

## Invariants and Contracts Upheld

- `docs/canon/constitution_v1.md`:
  - A1 determinism
  - A2 process-only mutation
  - A6 provenance/event logging
- `docs/canon/glossary_v1.md` terminology discipline
- CHEM-2 enforcement invariants:
  - `INV-NO-RECIPE-HACKS-FOR-CHEM`
  - `INV-YIELD-MUST-BE-MODEL`
  - `INV-BATCH-QUALITY-DECLARED`
- Existing CHEM/PHYS/TOL/PROV discipline remains:
  - registered energy transforms only
  - ledgered energy mutation only
  - entropy contribution logging only through engine pathways

## Reaction Profiles and Processing Coverage

Registered CHEM-2 processing reactions (registry-driven):

- `reaction.smelting_stub`
- `reaction.refining_stub`
- `reaction.polymerization_stub`
- `reaction.distillation_stub`
- `reaction.cracking_stub`

Yield model policies:

- `yield.basic_windowed`
- `yield.entropy_penalty`
- `yield.catalyst_boost`

Process lifecycle pathways:

- `process.process_run_start`
- `process.process_run_tick`
- `process.process_run_end`

## Yield / Defect Model Summary

Yield and defect derivation remain constitutive-model driven through CHEM runtime evaluation.

Inputs used by model evaluation include:

- temperature (THERM surface)
- pressure head proxy (FLUID stub)
- entropy index
- catalyst presence
- spec score / compliance proxy
- contamination and equipment wear context

Outputs remain deterministic:

- `yield_factor_permille`
- defect flags
- contamination tags
- quality grade

## Provenance and Traceability

Output batch truth rows include deterministic process provenance links:

- `reaction_id`
- `run_id`
- `equipment_id`
- `input_batch_ids`
- `parent_batch_ids`

`artifact.batch_quality` remains classified as canonical gameplay truth.

## Proof and Replay Integration

CHEM-2 proof surfaces are now propagated into control proof bundles:

- `process_run_hash_chain`
- `batch_quality_hash_chain`
- `yield_model_hash_chain`

Replay verifier:

- `tools/chem/tool_replay_process_run.py`

Observed verifier status on generated CHEM-2 process-run state:

- result: `complete`
- violations: `[]`

## Enforcement Upgrades

RepoX hard-gate wiring added for:

- `INV-NO-RECIPE-HACKS-FOR-CHEM`
- `INV-YIELD-MUST-BE-MODEL`
- `INV-BATCH-QUALITY-DECLARED`

AuditX analyzers added:

- `E244_INLINE_YIELD_LOGIC_SMELL` (`InlineYieldLogicSmell`)
- `E245_RECIPE_BYPASS_SMELL` (`RecipeBypassSmell`)

XStack STRICT promotion map updated to escalate both new analyzers to fail.

## TestX Coverage Added

- `test_process_run_deterministic`
- `test_yield_factor_model_applied`
- `test_contamination_tags_propagate`
- `test_batch_provenance_links`
- `test_energy_and_entropy_logged`
- `test_cross_platform_hash_match`

Focused CHEM-2 subset run result:

- `pass` (6/6)

## Gate Runs

### RepoX STRICT

Command:

- `python tools/xstack/repox/check.py --repo-root . --profile STRICT`

Result:

- `refusal` due `INV-WORKTREE-HYGIENE` while final-report/topology artifacts were still uncommitted at run time.
- No CHEM-2-specific blocker was reported in strict blockers.

### AuditX STRICT

Command:

- `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`

Result:

- `fail`
- promoted blockers are pre-existing `E179_INLINE_RESPONSE_CURVE_SMELL` findings outside CHEM-2 scope.

### TestX

Command:

- `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_process_run_deterministic,test_yield_factor_model_applied,test_contamination_tags_propagate,test_batch_provenance_links,test_energy_and_entropy_logged,test_cross_platform_hash_match`

Result:

- `pass` (6/6)

### Stress/Replay Harness

Command:

- `python tools/chem/tool_replay_process_run.py --state-path <generated_fixture_state>`

Result:

- `complete`

### Strict Build Check

Command:

- `python -m py_compile` over all CHEM-2 touched runtime/proof/enforcement/test files

Result:

- `pass`

## Topology Map Update

Regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`

Topology fingerprint:

- `57843bce8ceb9906b3c1801de63506d3edcc075e645ab3f4feb743a50054e4c1`

## Readiness

CHEM-2 baseline is functionally ready for:

- CHEM-3 corrosion expansion
- POLL-0 pollutant simulation ingestion

Remaining global blockers are repository-wide strict-gate issues outside this CHEM-2 patch scope.
