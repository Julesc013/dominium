Status: CANONICAL
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Capability-Only Canon

## Binding Rule
- Capability and entitlement declarations are the only allowed gating mechanism in runtime code, schemas, manifests, validators, and tests.
- Planning vocabulary about historical periods is documentation-only and non-normative.

## Prohibited Outside Documentation
- Stage, era, progression, or completion identifiers.
- Runtime predicates that gate behavior using stage-derived values.
- Schema fields that encode stage requirements or stage-provided behavior.

## Required Runtime Contract
- Commands declare `required_capabilities`.
- Packs declare `requires_capabilities` and `provides_capabilities`.
- Tool-only privileged paths require explicit entitlements and refusal when absent.

## Enforcement
- RepoX fails on forbidden stage/progression identifiers in runtime, schema, manifest, validator, and test surfaces.
- TestX capability matrix is the authoritative gating test surface.
