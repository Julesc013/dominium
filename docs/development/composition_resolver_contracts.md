Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Composition Resolver Contracts

Use `tools/validators/contracts/check_composition_plan.py` for the contract
surface added by COMPOSITION-RESOLVER-LAW-01.

## Commands

```text
python -m py_compile tools/validators/contracts/check_composition_plan.py
python tools/validators/contracts/check_composition_plan.py --repo-root . --strict
python tools/validators/contracts/check_composition_plan.py --repo-root . --json
python tools/validators/contracts/check_composition_plan.py --repo-root . --fixtures
python tools/validators/contracts/check_composition_plan.py --repo-root . --inventory
```

Strict mode validates schemas, registries, contract policy, and fixtures.
Inventory mode is descriptive and warning-only. The validator does not require
or call a runtime composition resolver.

## Contract Inputs

The validator reads:

- `contracts/composition/**`
- `contracts/lock/**`
- `contracts/profile/**`
- app, module, provider, capability, refusal, diagnostic, trust, and package
  registries used by fixture references

It validates that lock/report schemas are derived evidence and not source truth.
It also checks that the composition resolver contract forbids silent fallback,
silent overlay overwrite, path identity, and fixture-only support claims.

## Fixtures

Fixtures live under:

- `tests/contract/composition/fixtures`
- `tests/contract/lock/fixtures`
- `tests/contract/profile/fixtures`

Positive fixtures prove valid plans, decisions, lockfiles, provider selection,
module plans, capability reports, refusal reports, compatibility reports, trust
reports, and profile composition.

Negative fixtures prove unknown pack/module/provider/capability references,
silent overlay conflict, degraded fallback without fallback trace, selected
provider missing a required capability, path-as-identity, lockfile source-truth
claims, fixture-only support claims, and refusal reports without diagnostic or
refusal codes.

## Adding Fixtures

Use governed IDs from app, module, provider, capability, refusal, diagnostic,
trust, profile, and pack surfaces. Do not use file paths as stable IDs.
Fixture-only and planned rows must keep `support_claim = false` when that field
is present.

When adding a new valid reference type, update the source registry and add the
smallest fixture that proves both valid and invalid behavior. Do not expand this
validator into runtime composition resolution.
