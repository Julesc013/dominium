# Process Constitution Baseline

Status: BASELINE
Last Updated: 2026-03-06
Scope: PROC-0 constitutional layer only (no concrete process engine implementations).

## 1) Lifecycle Model

PROC-0 establishes a canonical lifecycle for all process abstractions:

- `exploration`
- `defined`
- `stabilized`
- `certified`
- `capsule`
- `drifted`

The constitution requires deterministic process semantics, process-only mutation, provenance-first run artifacts, and explicit drift/revalidation pathways.

## 2) Contract Requirements

PROC-0 contract surface implemented:

- Constitution: `docs/process/PROCESS_CONSTITUTION.md`
- Grammar alignment:
  - RWAM coverage includes PROC process/manufacturing/workflow affordances
  - META-ACTION includes process-step action mappings
  - META-INFO includes process run/QC/capsule artifact-family mappings
- META-CONTRACT templates:
  - Tier: `tier.proc.default`
  - Coupling: `coupling.proc.capsule_to_chem.outputs`, `coupling.proc.qc_to_sig.report`, `coupling.proc.drift_to_sys.fidelity`
  - Explain: `explain.qc_failure`, `explain.drift_detected`, `explain.yield_drop`, `explain.process_refusal`
- Policy registries:
  - `data/registries/process_lifecycle_policy_registry.json`
  - `data/registries/process_stabilization_policy_registry.json`
  - `data/registries/process_drift_policy_registry.json`
- Enforcement scaffolding:
  - RepoX invariants: `INV-NO-RECIPE-HACKS`, `INV-PROCESS-OUTPUTS-LEDGERED`, `INV-PROCESS-CAPSULE-REQUIRES-STABILIZED`
  - AuditX analyzers: `RecipeBypassSmell` (`E245`), `UnregisteredWorkflowSmell` (`E281`)

## 3) Process-Output Ledger Wiring

To satisfy `INV-PROCESS-OUTPUTS-LEDGERED`, `process_registry` now includes canonical lifecycle process IDs:

- `process.process_run_start`
- `process.process_run_tick`
- `process.process_run_end`

`PROCESS_CONSTITUTION.md` now includes explicit stabilization prerequisite text:

- `Every ProcessCapsule must be derived from stabilized ProcessDefinition.`

## 4) Validation Summary

Relevant invariants/docs upheld in this pass:

- Canon: `docs/canon/constitution_v1.md`
- Canon glossary: `docs/canon/glossary_v1.md`
- AGENTS constraints (determinism, process-only mutation, pack-driven integration)
- RepoX PROC invariants listed above

Contract/schema impact:

- Changed (data/contracts/registries): process governance registries + process registry entries.
- Unchanged (simulation semantics): no new process solver/executor semantics introduced by PROC-0.

Validation runs:

- RepoX STRICT: `REFUSAL` (repository-wide pre-existing blockers remain), PROC-specific invariants pass.
  - Command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Latest: `files=1679`, `findings=27`, status `refusal`
- AuditX STRICT: `FAIL` (pre-existing promoted blocker)
  - Command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - Latest: `findings=1343`, `promoted_blockers=1` (`E240_UNCLASSIFIED_ARTIFACT_SMELL`)
- TestX:
  - Full strict-lane TestX from xstack strict: `FAIL` (repository-wide pre-existing failures)
  - PROC subset: `PASS`
    - Command: `python tools/xstack/testx_all.py --repo-root . --profile FAST --cache on --subset test_process_policies_registry_valid,test_proc_contract_templates_present,test_proc_grammar_mappings_present,test_null_boot_proc_optional`
- Strict build profile: `REFUSAL` (pre-existing global CompatX/AuditX/TestX/packaging blockers)
  - Command: `python tools/xstack/run.py strict --repo-root . --cache on`

## 5) Topology Map

Topology map regenerated:

- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`
- fingerprint: `963cdc6c9ef232c86474afbda063491be97fc6d5dbd112fb134e26e32302a346`

## 6) Readiness Checklist for PROC-1

PROC-1 readiness status:

- [x] Lifecycle constitution frozen
- [x] PROC grammar mappings declared
- [x] PROC contract templates declared
- [x] Lifecycle/stabilization/drift policy registries present
- [x] RepoX/AuditX scaffolding present
- [x] FAST TestX coverage for PROC-0 constitution present
- [ ] Repository-wide strict gates fully green (blocked by pre-existing non-PROC findings)

