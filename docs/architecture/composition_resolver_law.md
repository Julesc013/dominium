Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Composition Resolver Law

COMPOSITION-RESOLVER-LAW-01 defines the narrow contract surface for deterministic
composition resolver plans across app, module, Workbench, and package
descriptors.

This law extends:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/app_composition_model.md`
- `docs/architecture/module_composition_law.md`
- `docs/architecture/workbench_workspace_model.md`
- package and pack contract law under `contracts/package/**` and
  `contracts/schema/package/**`

It does not replace those surfaces and does not promote a generated resolver
plan into semantic authority.

## Scope

A resolver plan is an auditable, deterministic projection over declared
descriptors. It may name:

- `app_composition` inputs from app composition descriptors
- `module_composition` inputs from module composition descriptors
- `workbench_workspace` inputs from Workbench workspace descriptors
- `package_descriptor` inputs from pack, package, bundle, or package-adjacent
  descriptor law

The resolver plan may state which governed IDs are included, required, selected,
refused, degraded, or deferred for review. It may not mount packs, load modules,
dispatch apps, mutate truth, call private tools, or perform compatibility
migration.

## Deterministic Ordering

Resolver plans use `canonical_layered_stable_sort`.

The canonical descriptor-kind order is:

1. `package_descriptor`
2. `module_composition`
3. `workbench_workspace`
4. `app_composition`

This is a comparison key for stable resolver output. It is not runtime load
order and not dependency execution order.

Within each descriptor kind, steps sort by:

1. descriptor kind rank
2. `descriptor_id` case-folded ascending
3. `step_id` case-folded ascending
4. `source_ref` case-folded ascending

Resolver output must not depend on filesystem discovery order, hash-map order,
thread completion order, or process timing.

## Conflict Law

The resolver must expose conflicts instead of hiding them.

The following subjects require explicit conflict records:

- duplicate descriptor IDs
- duplicate provided governed references
- missing required governed references
- version conflicts
- capability conflicts
- ordering ambiguity
- private path binding attempts

Allowed decisions are:

- `refused`
- `degraded`
- `selected_by_policy`
- `deferred_for_review`

Silent fallback, ignored conflicts, and best-effort guessing are forbidden.

## Authority Boundaries

Descriptor IDs, not paths, define identity. `source_ref` is provenance and
evidence, not semantic authority.

The resolver inherits the existing ownership cautions:

- `schema/` remains semantic contract law; validator-facing projections do not
  redefine it.
- `packs/` and `data/packs/` retain scoped ownership and residual quarantine;
  this law does not pick a single pack root winner.
- Workbench consumes registered commands, services, modules, diagnostics,
  evidence, documents, and views; Workbench is not semantic authority.

## Non-Goals

This law does not implement:

- runtime loader behavior
- module loading
- package mounting
- app composer UI or runtime dispatch
- Workbench workspace runtime
- release publication
- migration of existing app, module, Workbench, package, pack, or schema
  contracts

## Contract Surface

The machine-readable law lives under `contracts/composition/`:

- `composition_resolver.contract.toml`
- `composition_resolver_plan.schema.json`
- `composition_source_kind.registry.json`

The validator is:

```text
python tools/validators/contracts/check_composition_resolver.py --repo-root . --strict --fixtures
```
