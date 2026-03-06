# PROC-1 Retro-Consistency Audit

Date: 2026-03-06  
Scope: ProcessDefinition schemas and deterministic step-graph execution baseline.

## Inputs Audited
- `tools/xstack/sessionx/process_runtime.py`
- `src/chem/process_run_engine.py`
- `src/system/templates/template_compiler.py`
- `src/system/certification/system_cert_engine.py`
- `data/registries/process_registry.json`
- `data/registries/action_template_registry.json`
- `data/registries/temporal_domain_registry.json`

## Implicit Workflow Audit

1. Template instantiation workflow
- Current path is process-governed (`process.template_instantiate`) with plan + commitment semantics.
- Can be represented as a ProcessDefinition DAG: verify preconditions -> transform instantiate -> verify compliance.

2. Certification workflow
- Current system certification already follows deterministic process entry points.
- Can be expressed as step graph: verify signature/invariants -> verify spec -> issue/report.

3. Maintenance/degradation workflow
- Existing degradation and maintenance paths are deterministic and logged.
- Candidate fit for process step graph with explicit verify and wait steps.

4. CHEM process run lifecycle
- Existing run triplet (`process.process_run_start|tick|end`) is deterministic and canonical.
- Maps cleanly to explicit ProcessDefinition + ProcessRun record model.

## Step-Graph Expressibility Check

All audited workflow categories can be represented as deterministic DAG step graphs using:
- `action_step` for human/agent task surfaces,
- `transform_step` for domain process calls,
- `measure_step` for observation artifacts,
- `verify_step` for spec/safety checks,
- `wait_step` for temporal-domain gated progression.

No audited workflow requires nondeterministic ordering or wall-clock semantics.

## Candidate First ProcessDefinitions (Examples)
- `proc.archetype.cast_part`
- `proc.archetype.machine_part`
- `proc.archetype.assemble_system`
- `proc.archetype.test_and_calibrate`
- `proc.archetype.compile_firmware`

## Migration Notes
1. Keep CHEM runtime semantics intact; PROC-1 adds generic step-graph infrastructure.
2. Map ad hoc workflow descriptors to registered process archetype IDs.
3. Enforce DAG/toposort validation before any run start.
4. Keep canonical run/step records authoritative; intermediate observations stay derived/compactable.
