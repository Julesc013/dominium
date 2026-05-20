Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: MODULE-COMPOSITION-LAW, PROVIDER-MODEL, COMMAND-SURFACE, WORKBENCH-VALIDATION-SLICE
Binding Sources: `contracts/public_surface/public_surface.contract.toml`, `contracts/abi/c_api.contract.toml`, `docs/architecture/public_surface_registry.md`

# Module API Standard

## Scope

Modules, components, providers, and Workbench surfaces expose public contracts
only through registered surfaces. A path under `apps/workbench/module` or an
include directory is not automatically a stable module API.

## Rules

- Module identity is a stable ID, not a path.
- Stable module APIs require a public surface registry entry.
- Provider ABI requires registry classification, conformance tests, and
  replacement protocol coverage before stable promotion.
- Workbench modules call commands, services, or registered APIs rather than
  private implementation internals.
- Fixture and generated module surfaces are not product public contracts.
- Internal module headers may change until promoted by registry and proof.

## Promotion

Promotion from internal/provisional to stable requires:

- registry update;
- ABI/API validation;
- task-specific conformance tests;
- compatibility policy;
- replacement or deprecation policy;
- fast strict proof, with release/full proof when trust or compatibility is
  affected.
