Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MAT-2 material taxonomy and composition baseline.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Material Taxonomy Baseline

## 1) Ontology Layers
MAT-2 defines canonical layers:
- `Element`: atomic identity with optional atomic number and fixed-point molar mass.
- `Compound`: explicit stoichiometric composition over element IDs.
- `Mixture`: fixed-point mass-fraction composition over compounds and/or materials.
- `Material Class`: typed material definition bound to `element|compound|mixture` base references plus dimensional properties.
- `Fuel Class`: represented via `material_class` tagging and `specific_energy` property (no solver behavior in MAT-2).

Primary doctrine: `docs/materials/MATERIAL_TAXONOMY.md`.

## 2) Baseline Elements, Compounds, Mixtures, Materials
Source registries:
- `data/registries/element_registry.json`
- `data/registries/compound_registry.json`
- `data/registries/mixture_registry.json`
- `data/registries/material_class_registry.json`
- `data/registries/quality_distribution_registry.json`

Baseline entries:
- Elements: `element.H`, `element.O`, `element.C`, `element.Fe`, `element.Si`
- Compounds: `compound.H2O`, `compound.CO2`, `compound.Fe2O3`
- Materials: `material.water`, `material.iron`, `material.steel_basic`, `material.wood_basic`, `material.stone_basic`, `material.air`
- Quality models: `quality.uniform_stub`, `quality.basic_defect_stub`

Null-universe compatibility:
- Material taxonomy registries are optional at runtime with deterministic null fallbacks in `tools/xstack/sessionx/universe_physics.py`.

## 3) Composition + Validation Contracts
Deterministic composition validation implementation:
- `src/materials/composition_engine.py`

Coverage:
- validates element registry shape/values
- validates compound composition references and deterministic molar-mass derivation
- validates mixture fixed-point mass-fraction sums
- validates material dimensional property compatibility (`density`, `specific_energy`, optional typed fields)
- deterministic material batch construction via stable hash identity

Refusal codes:
- `refusal.material.invalid_composition`
- `refusal.material.mass_fraction_mismatch`
- `refusal.material.dimension_mismatch`

## 4) Ledger Integration
RS-2 integration updates:
- conservation contract sets include `quantity.mass` tracking channel
- ledger runtime accepts optional `material_id` on mass deltas
- finalize output includes deterministic `extensions.material_mass_totals`
- dimensional checks remain enforced (`refusal.dimension.mismatch`)

Constraints:
- material mass is tracked directly by `material_id`
- no implicit mass->energy conversion is introduced by MAT-2
- `quantity.mass_energy_total` only changes when declared conversion processes emit it

## 5) Schema + CompatX Integration
New schemas (v1.0.0 strict):
- `element`, `compound`, `mixture`, `material_class`, `material_property_override`, `quality_distribution`, `material_batch`

Registry schemas and compile outputs are integrated into:
- `tools/xstack/compatx/version_registry.json`
- `tools/xstack/registry_compile/*`
- `schemas/bundle_lockfile.schema.json`
- session runtime registry loaders (`tools/xstack/sessionx/runner.py`, `script_runner.py`)

## 6) Guardrails
RepoX rules:
- `INV-MATERIAL-DEFINITIONS-DATA-ONLY`
- `INV-NO-HARDCODED-ELEMENTS`
- `INV-COMPOSITION-VALIDATED`

AuditX analyzers:
- `HardcodedPeriodicTableSmell` (`E58_HARDCODED_PERIODIC_TABLE_SMELL`)
- `MaterialMassDriftSmell` (`E59_MATERIAL_MASS_DRIFT_SMELL`)

TestX coverage:
- `testx.materials.element_registry_valid`
- `testx.materials.compound_mass_fraction_sum`
- `testx.materials.mixture_mass_fraction_sum`
- `testx.materials.material_batch_creation_deterministic`
- `testx.materials.ledger_mass_tracking_by_material`

## 7) Extension Guidance
Full periodic table packs:
1. Add element entries through pack registries only; avoid runtime hardcoded IDs.
2. Keep `molar_mass_raw` fixed-point and deterministic across pack versions.
3. Layer compounds/mixtures/material classes by IDs without changing engine code.

Fictional elements/materials:
1. `atomic_number` may be null for fictional elements.
2. Introduce fictional IDs under pack namespace and provide explicit composition/property declarations.
3. Bind conservation semantics through `quantity_id` channels in RS-2 contract sets, not by display names.

## 8) Gate Execution Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=0
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=1629 (warn-level findings present)
3. TestX PASS
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.materials.element_registry_valid,testx.materials.compound_mass_fraction_sum,testx.materials.mixture_mass_fraction_sum,testx.materials.material_batch_creation_deterministic,testx.materials.ledger_mass_tracking_by_material`
   - result: `status=pass`, selected_tests=5
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mat2 --cache on --format json`
   - result: `result=complete`
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`, checked_windows=21
