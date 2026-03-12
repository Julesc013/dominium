Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-03-01
Scope: SPEC-1 SpecSheet substrate baseline
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SpecSheet Baseline

## Canon/Invariant Mapping
- A1 Determinism is primary (`docs/canon/constitution_v1.md`)
- A2 Process-only mutation (`docs/canon/constitution_v1.md`)
- A3 Law-gated authority (`docs/canon/constitution_v1.md`)
- A9 Pack-driven integration (`docs/canon/constitution_v1.md`)
- A10 Explicit degradation/refusal (`docs/canon/constitution_v1.md`)
- RepoX:
  - `INV-NO-HARDCODED-GAUGE-WIDTH-SPECS`
  - `INV-SPECSHEET-OPTIONAL`

## Schemas
- `schema/specs/spec_sheet.schema`
- `schema/specs/spec_type.schema`
- `schema/specs/tolerance_policy.schema`
- `schema/specs/compliance_check.schema`
- `schema/specs/compliance_result.schema`

CompatX JSON mirrors:
- `schemas/spec_sheet.schema.json`
- `schemas/spec_type.schema.json`
- `schemas/tolerance_policy.schema.json`
- `schemas/compliance_check.schema.json`
- `schemas/compliance_result.schema.json`
- `schemas/spec_type_registry.schema.json`
- `schemas/tolerance_policy_registry.schema.json`
- `schemas/compliance_check_registry.schema.json`

## Registries and Optional Pack
Registries:
- `data/registries/spec_type_registry.json`
- `data/registries/tolerance_policy_registry.json`
- `data/registries/compliance_check_registry.json`

Optional default pack:
- `packs/specs/specs.default.realistic.m1/data/spec_sheets.json`

Baseline spec types:
- `spec.track`
- `spec.road`
- `spec.tunnel`
- `spec.bridge`
- `spec.vehicle_interface`
- `spec.docking_interface`

Baseline tolerance policies:
- `tol.default`
- `tol.strict`
- `tol.relaxed`

Baseline compliance checks:
- `check.geometry.clearance`
- `check.geometry.curvature_limit`
- `check.structure.load_rating_stub`
- `check.interface.compatibility`
- `check.operation.max_speed_policy`

## Example Spec Sheets
From `packs/specs/specs.default.realistic.m1/data/spec_sheets.json`:
- `spec.track.standard_gauge.v1`
- `spec.track.narrow_gauge_example.v1`
- `spec.road.basic_lane_width.v1`
- `spec.tunnel.basic_clearance.v1`

These remain optional content and are not required for boot/runtime validity.

## Engine and Process Workflow
Engine:
- `src/specs/spec_engine.py`
  - deterministic loading/validation of spec sheets from registries and packs
  - strict parameter validation by `parameter_schema_id`
  - deterministic compliance evaluation with fingerprinted `compliance_result`

Authoritative process family:
- `process.spec_apply_to_target`
  - binds `spec_id` to `target_kind`/`target_id`
  - persists binding through process-only mutation
  - emits provenance event
- `process.spec_check_compliance`
  - gathers required inputs from inspection snapshots and derived summaries
  - evaluates checks deterministically
  - emits/stores fingerprinted compliance result
  - strict contexts may refuse with `refusal.spec.noncompliant`

## Integration Summary
MAT:
- Spec bindings annotate structure instances and assembly-graph targets.
- Inspection snapshots expose `section.spec_compliance_summary`.

ABS:
- Compliance checks can consume hazard/state-derived summaries through required input keys.
- Deterministic check outcomes can be used by policy and scheduling layers.

CTRL:
- Plan execution may enforce or relax spec compliance by policy context.
- Decision logs capture `spec_compliance` context and enforced refusals/downgrades.

RND:
- Construction overlay renders pass/warn/fail spec compliance glyphs.
- Rendering remains presentation-only and does not mutate truth.

## MOB-1 Extension Points
- GuideGeometry integration should map geometry summaries (clearance/curvature/interface envelopes) into SpecSheet `required_inputs`.
- Mobility control outputs should consume spec-driven limits via control/process paths, not direct domain mutation.
- Spec enforcement policy should remain profile/law-driven (ranked enforce, private optional), logged in DecisionLog.

## Enforcement and Tests
RepoX:
- `INV-NO-HARDCODED-GAUGE-WIDTH-SPECS`
- `INV-SPECSHEET-OPTIONAL`

AuditX:
- `E133_SPEC_HARDCODE_SMELL`
- `E134_SPEC_BYPASS_SMELL`

TestX (SPEC-1):
- `testx.specs.registry_valid`
- `testx.specs.apply_deterministic`
- `testx.specs.compliance_result_deterministic`
- `testx.specs.no_spec_packs_null_boot_ok`
- `testx.specs.hardcoded_spec_constant_smoke`

## Gate Snapshot (2026-03-01)
1. RepoX PASS
   - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass` (warn finding retained from pre-existing AuditX threshold)
2. AuditX run
   - command: `python tools/auditx/auditx.py scan --repo-root . --changed-only --format json --output-root run_meta/auditx_spec1_final`
   - result: `result=scan_complete`
3. TestX PASS (SPEC-1 subset)
   - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.specs.registry_valid --subset testx.specs.apply_deterministic --subset testx.specs.compliance_result_deterministic --subset testx.specs.no_spec_packs_null_boot_ok --subset testx.specs.hardcoded_spec_constant_smoke`
   - result: `status=pass`, `selected_tests=5`
4. strict build PASS
   - command: `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: build completed successfully
5. topology map updated
   - command: `python tools/governance/tool_topology_generate.py --repo-root .`
   - result: `result=complete`
