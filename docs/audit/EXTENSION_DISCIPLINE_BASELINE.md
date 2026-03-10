Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Extension Discipline Baseline

## Baseline
- Canonical doctrine: `docs/meta/EXTENSION_DISCIPLINE.md`
- Compatibility note: `docs/meta/EXTENSION_MIGRATION_NOTES.md`
- Registry of interpreted keys: `data/registries/extension_interpretation_registry.json`
- Runtime normalization and validation engine: `src/meta_extensions_engine.py`
- Canonical compatibility wrapper: `src/meta/extensions/extensions_engine.py`

## Rules Frozen By This Baseline
- Extension keys must be namespaced for new authoring.
- Unknown keys are inert by default.
- Strictness policy is explicit:
  - `extensions.default`
  - `extensions.warn`
  - `extensions.strict`
- Interpreted keys require registry declaration plus semantic-contract pin and profile gate metadata.
- Extension serialization and hashing now run through deterministic normalization.

## Compatibility Result
- Existing bare keys remain loadable in default mode through legacy alias handling.
- Existing data is not silently rewritten.
- No simulation, worldgen, or logic algorithm changed.

## Readiness
- Ready for `COMPAT-SEM-3` overlay conflict policy profiles.
- Ready for incremental migration of legacy bare keys to first-class namespaced authoring.
