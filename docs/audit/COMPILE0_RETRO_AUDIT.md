Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# COMPILE-0 Retro-Consistency Audit

Date: 2026-03-06  
Scope: Universal CompiledModel framework baseline for SYS/PROC/LOGIC integration.

## Inputs Audited
- `src/control/ir/control_ir_compiler.py`
- `tools/materials/tool_blueprint_compile.py`
- `tools/xstack/registry_compile/compiler.py`
- `src/system/templates/template_compiler.py`
- `src/meta/provenance/compaction_engine.py`

## Existing Optimization / Minimization Paths
1. Control IR compiler (`src/control/ir/control_ir_compiler.py`)
- Deterministic IR-to-action lowering with verification gate.
- Domain-specific to control-plane IR; no reusable compiled-model proof contract.

2. Blueprint compiler tool (`tools/materials/tool_blueprint_compile.py`)
- Deterministic artifact compilation for materials/blueprints.
- Produces reproducible outputs and cache keys, but not expressed as universal compiled model type.

3. Registry compile pipeline (`tools/xstack/registry_compile/compiler.py`)
- Deterministic pack+registry composition/validation.
- Build-time data compiler; not runtime compiled equivalence.

4. System template compiler (`src/system/templates/template_compiler.py`)
- Deterministic template expansion/compilation and fingerprinting.
- Structural template compilation, not equivalence-verified behavioral compilation.

## Findings
1. No single universal runtime compiled-model schema exists for:
- compiled payload typing
- equivalence proof contract
- validity domain contract
- deterministic recompile verification

2. Compile-like logic exists in separate subsystems, each with local contracts and no shared proof schema.

3. Current architecture already has deterministic and provenance discipline required to host a universal framework.

## Candidate Targets For Universal Compilation
1. SYS macro capsule model sets
- Compile model-set graphs into reduced deterministic representations with explicit validity bounds.

2. LOGIC networks (future)
- Compile logic graphs to automata/IR/lookup-table forms under equivalence contracts.

3. PROC process step graphs (future)
- Compile stabilized process networks into reduced execution graphs/capsules.

4. Generic model sets
- Compile declared constitutive model wiring into reduced graph/IR where exact or bounded-error proof exists.

## Migration Direction
1. Add `compiled_model`, `equivalence_proof`, `validity_domain`, `compile_request`, `compile_result` schemas.
2. Add canonical compiled-type/proof-procedure/policy registries.
3. Add deterministic compile engine skeleton in `src/meta/compile/`.
4. Add runtime hooks:
- `compiled_model_is_valid`
- `compiled_model_execute`
5. Keep all compiled outputs derived + compactable, with proof/replay verification tooling.

## Risk Notes
- Avoid semantic drift: compiled execution is optional optimization and must fall back to uncompiled path.
- Avoid bespoke compilers per domain: framework governance and RepoX/AuditX checks must enforce one path.
