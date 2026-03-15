Status: CANONICAL
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: release-pinned install profile, update model, and trust policy constitution

# Component Graph Constitution

## Purpose

The component graph defines Dominium distribution and installation as a deterministic dependency graph instead of a hardcoded folder recipe.

The graph is additive in MVP:

- existing dist trees remain valid,
- existing install/instance/save manifests remain loadable,
- release and dist tooling may resolve an install plan from the graph without changing simulation semantics.

## Component Model

A component is an immutable, content-addressed artifact unit that may be:

- required,
- optional,
- capability-gated,
- platform-filtered.

Supported component kinds:

- `binary`
- `pack`
- `profile`
- `lock`
- `docs`
- `sdk`
- `manifest`

## Edge Model

Supported edge kinds:

- `requires`
- `recommends`
- `suggests`
- `conflicts`
- `provides`

`requires` is mandatory.

`recommends` is included by default in MVP resolution unless policy disables it.

`suggests` is excluded by default in MVP resolution unless policy enables it.

`conflicts` refuses deterministic strict resolution when both components are selected.

`provides` exposes a `provides_id` and is resolved through the existing deterministic LIB provides resolver.

## Filters

Components and edges may be filtered by:

- `platform_id`
- `arch_id`
- `abi_id`
- `capability_id`
- semantic contract requirements

Filters only affect install/distribution planning and validation. They do not authorize runtime semantic bypasses.

## Resolution

Setup and launcher resolve an install plan deterministically:

1. select target platform, arch, and ABI
2. select requested install profile or explicit component roots
3. traverse the graph in stable lexical order by `component_id`
4. expand `requires`, then `recommends`, then optional provider bindings
5. resolve `provides` deterministically using policy-governed provider selection
6. refuse on unsatisfied requirements or strict conflicts
7. emit:
   - install plan
   - selected components
   - provider resolutions
   - verification steps

Traversal must be deterministic given:

- component graph
- requested roots
- target platform/arch/ABI
- capability set
- contract requirements
- installed state
- provides resolution policy

## Baseline MVP Graph

The baseline `v0.0.0-mock` graph is platform-agnostic.

Concrete platform-specific artifact availability remains bound later by release manifests and platform packaging outputs.

Because `contract.lib.manifest.v1` is not present in the current semantic contract registry, the component graph registry in MVP remains conservatively provisional even though it is designed to align with:

- `contract.pack.compat.v1`
- current LIB install/instance/save manifest behavior

## Integration Rules

- Setup uses the resolver to produce an install-plan summary for a resolved install root.
- Launcher uses the resolver to validate instance requirements against the resolved install plan.
- Release manifest generation includes the component graph hash.
- Dist assembly uses the resolved install plan to decide which products, packs, profiles, locks, and docs are included.

## Determinism

- ordering is lexical by `component_id`
- provider selection uses deterministic LIB provides resolution
- no wall-clock input
- no environment-dependent selection except explicit target/platform inputs
- install plan fingerprints are canonical hashes of the resolved plan body
