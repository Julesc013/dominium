Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Task: COMPOSITION-RESOLVER-LAW-01
Worker: 4
Validation Level: FAST targeted
Result: PASS

# COMPOSITION-RESOLVER-LAW-01 Audit

## Scope

Worker 4 added a narrow composition resolver contract surface for deterministic
resolver plans across app, module, Workbench, and package descriptors.

Touched scope:

- `contracts/composition/**`
- `tools/validators/contracts/check_composition_resolver.py`
- `tests/contract/composition_resolver/**`
- `docs/architecture/composition_resolver_law.md`
- `docs/repo/audits/COMPOSITION_RESOLVER_LAW_01.md`

## Invariants Upheld

- `docs/canon/constitution_v1.md` A1/E2: deterministic ordering is primary.
- `docs/canon/constitution_v1.md` A2: resolver plans do not mutate truth.
- `docs/canon/constitution_v1.md` A3/A10: refusal and degradation are explicit.
- `docs/canon/constitution_v1.md` A7: resolver plans do not collapse truth,
  perception, or render responsibilities.
- `docs/canon/constitution_v1.md` A9: pack-driven integration remains declared
  and explicit.
- `AGENTS.md` sections 4, 5, 8, and 10: extend-over-replace, no silent drift,
  contract discipline, validation honesty, and ownership cautions.

## Contract And Schema Impact

Added new composition contract/schema artifacts only. Existing app, module,
Workbench, package, pack, and schema contracts were not modified.

New artifacts:

- `contracts/composition/composition_resolver.contract.toml`
- `contracts/composition/composition_resolver_plan.schema.json`
- `contracts/composition/composition_source_kind.registry.json`

## Determinism Impact

The resolver law defines a canonical layered stable sort:

1. `package_descriptor`
2. `module_composition`
3. `workbench_workspace`
4. `app_composition`

The validator checks stable step order by descriptor kind rank,
case-folded descriptor ID, case-folded step ID, and case-folded source
reference. This is contract validation only and does not implement runtime
loading or execution.

## Conflict Handling

The validator detects duplicate descriptors, duplicate provided governed
references, missing required governed references, forbidden conflict decisions,
unsorted participants, and private path bindings. Required conflicts must be
explicitly recorded with a lawful decision.

## Non-Goals Confirmed

No runtime loader, module loader, package mount, app composer runtime,
Workbench runtime, release publication, or existing descriptor-schema migration
was implemented.

## Validation Results

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing AIDE
  review-packet warnings.
- `py -3 tools/validators/contracts/check_composition_resolver.py --repo-root . --strict --fixtures --inventory`:
  PASS, 6 fixtures, 0 errors, 0 warnings.
- `py -3 -m py_compile tools/validators/contracts/check_composition_resolver.py tests/contract/composition_resolver/composition_resolver_contract_tests.py`:
  PASS.
- `py -3 tests/contract/composition_resolver/composition_resolver_contract_tests.py`:
  PASS, 1 test.
- `py -3 -c "<json parse for composition schema, registry, and fixtures>"`:
  PASS, 8 JSON files.
- `py -3 tools/validators/contracts/check_composition_resolver.py --repo-root . --strict --json --fixtures`:
  PASS, fixture expectations satisfied.

`git diff --check` is recorded in the final worker response because the
workspace contains unrelated parallel-worker edits outside this task scope.
