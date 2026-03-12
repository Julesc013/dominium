Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PROC-0 Retro-Consistency Audit

Date: 2026-03-06  
Scope: Process constitution baseline before PROC runtime/schema expansion.

## Inputs Audited
- `data/registries/process_registry.json`
- `data/registries/process_requirements.json`
- `tools/xstack/sessionx/process_runtime.py`
- `src/chem/process_run_engine.py`
- `src/system/templates/template_compiler.py`
- `src/system/certification/system_cert_engine.py`
- `tools/materials/tool_blueprint_compile.py`

## Existing Recipe/Craft Constructs
1. Generic craft workflow
- `process.craft.execute` exists as a process entry and remains process-governed.
- Craft references still use recipe-like terms, but mutation is process-bound.

2. Domain process runs (CHEM)
- CHEM industrial flow already uses process lifecycle IDs:
  - `process.process_run_start`
  - `process.process_run_tick`
  - `process.process_run_end`
- Yield/defect paths are model-driven and logged.

3. Template/system workflows (SYS)
- Template instantiation is process-governed (`process.template_instantiate`).
- System collapse/expand/certification are explicit processes with canonical records.

4. Build/compile-like workflows
- Blueprint and compiled-model tooling exist as deterministic build/derive flows.
- Compilation path is now framework-governed (`process.compile_request_submit`).

## Repeated Workflow Logic Candidates For ProcessDefinition
The following repeated deterministic workflows should be represented as explicit `ProcessDefinition` lifecycle entities in PROC-1+:

1. CHEM process runs
- Current run triplet maps directly to process step-graph formalization, stabilization metrics, and capsule readiness.

2. SYS template instantiation plans
- Current plan/commit workflow maps to process definitions with environment/tool requirements and quality/compliance gates.

3. Certification evaluations
- Current deterministic evaluation flows map to process definitions with report/credential outputs and explicit policy modes.

4. Software/firmware build stubs
- Existing deterministic build/compile paths are candidates for process formalization with artifact signatures and validity domains.

## Gaps Identified
1. No dedicated process lifecycle policy registry (exploration/defined/stabilized/certified/capsule/drifted) yet.
2. No process-specific stabilization/drift policy registries yet.
3. No explicit PROC-tier/coupling/explain template rows yet.
4. No PROC-specific enforcement invariants in RepoX/AuditX naming yet.

## Migration Notes To PROC
1. Keep existing domain behavior unchanged; PROC-0 is constitutional/governance only.
2. Introduce policy registries and contract templates first.
3. Require new domain workflows to reference PROC policy IDs instead of ad hoc lifecycle flags.
4. Preserve null-boot by keeping PROC policy registries optional defaults with deterministic refusal/degrade behavior.
