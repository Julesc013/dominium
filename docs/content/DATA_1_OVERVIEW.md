# DATA-1 Overview (Expanded Fabrication Libraries)

Status: binding.
Scope: data-only packs that stress FAB-0/1 without adding code.

## Pack List and Maturity

- org.dominium.core.materials.extended — PARAMETRIC  
  Stress: wide trait ranges, conflicts, sensitivity, degradation parameters.
- org.dominium.core.parts.extended — STRUCTURAL  
  Stress: multiple interfaces, asymmetry, capacity mismatches, tolerances.
- org.dominium.core.assemblies.extended — STRUCTURAL  
  Stress: deep nesting, shared subassemblies, cycles, multiple hosted processes.
- org.dominium.core.processes.extended — PARAMETRIC  
  Stress: multi-input/output chains, losses, parameter sensitivity, failures.
- org.dominium.core.quality.extended — PARAMETRIC  
  Stress: tolerance classes, inspection methods, degradation effects, batch lots.
- org.dominium.core.standards.extended — STRUCTURAL  
  Stress: competing standards and overlapping scopes.
- org.dominium.core.instruments.extended — STRUCTURAL  
  Stress: limited accuracy/precision, calibration drift, standards dependencies.
- org.dominium.core.hazards.extended — INCOMPLETE  
  Stress: trigger conditions, cascading effects, mitigation references.

## What Works Today

- Packs validate via `tools/fab/fab_validate.py` when merged with dependencies.
- Capability discovery and compat checks are deterministic via pack manifests.
- Assemblies, processes, qualities, and hazards are expressible as data-only
  records without new engine/game code.

## Awkward or Impossible (DATA-1 Findings)

- Unitless numeric values are not supported, so yield/failure maps use proxy
  units (for example mass or time) even when a true unitless ratio is desired.
- No pressure unit exists in UNIT_SYSTEM_POLICY; pressure-like fields are
  encoded using energy units as placeholders.
- `fab_inspect` does not compare endpoint interfaces on edges; it only validates
  the referenced interface record, so capacity mismatch refusals are not
  observable in the tool output.
- Assembly cycles can be expressed but there is no schema-level way to mark
  allowed vs forbidden cycles, nor to document cycle constraints.
- Process families cannot encode distribution types (only scalar maps), so
  probabilistic envelopes are represented as flat numeric maps.

These gaps are documented to inform CODE-1 decisions.

## Expected Refusals

- Missing dependencies (capabilities) must yield `REFUSE_CAPABILITY_MISSING`
  in compatibility checks.
- Invalid cross-references within a merged FAB pack must yield
  `REFUSE_INTEGRITY_VIOLATION` from `fab_validate`.

## Notes

All packs are optional and content-agnostic. They exist to pressure-test the
ontology and interpreters without adding any runtime semantics.
