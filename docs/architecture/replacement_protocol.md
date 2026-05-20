Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Replacement Protocol

`REPLACEMENT-PROTOCOL-01` defines how Dominium replaces implementation,
provider, module, schema, protocol, registry, artifact, command, app, Workbench,
tooling, and directory surfaces without silent breakage.

Replacement is allowed. Silent breakage is not.

## Model

A replacement packet is a contract-backed plan and evidence record. It names the
old surface, the new surface, affected public surfaces, artifacts, schemas,
protocols, commands, providers, modules, dependency impact, ABI impact,
compatibility impact, migration/refusal policy, conformance proof, rollback, and
diagnostics.

Implementation paths may appear as evidence, but they are not identity. Surface,
artifact, provider, module, schema, protocol, and command IDs are the authority.

## Replacement, Refactor, Migration, Deprecation

A private refactor can remain lightweight when public surfaces and durable
artifacts are unchanged and normal proof passes. It still needs enough evidence
to show the public surface was known.

A replacement changes the implementation or declared surface behind an identity.
If the public or durable contract changes, it needs a replacement packet.

A migration transforms old artifacts or formats through explicit policy. No
replacement may perform silent migration or silent defaulting.

A deprecation is a compatibility policy decision. Version/deprecation law will
deepen lifecycle rules, but replacement packets already need to record the
transition path.

## Surface Impact

Public surface replacements must reference
`contracts/public_surface/public_surface.contract.toml`. Stable or frozen
surfaces require conformance proof, compatibility proof, or a declared
deprecation/refusal path.

Private implementation replacements may use a lighter packet when:

- old and new public surface IDs are the same;
- compatibility impact is compatible;
- rollback is documented;
- fast strict proof or equivalent targeted proof passes.

## Artifact And Schema Impact

Stable, locked, or published artifacts must be preserved, migrated, or refused.
Artifact references use artifact IDs and kinds, not paths.

Schema and protocol replacements must obey schema/protocol evolution law:
unknown-field behavior, required-field behavior, defaults, canonical
serialization, migration, and refusal are explicit.

## Provider And Module Impact

Provider replacement must preserve provider ID semantics or declare a transition
policy. Capabilities must remain equivalent or explicitly degrade/refuse.

Module, Workbench workspace, and app composition replacements must preserve
module/app/workspace IDs or declare new IDs with transition policy. Command,
view, document, service, provider, and capability bindings must remain
compatible or be migrated/refused.

## ABI And Dependency Impact

API/ABI replacement must obey API-ABI-CANON. Native and C ABI surfaces require
header/boundary proof before promotion.

Directory restructuring and dependency boundary replacement require path
reference repair, dependency-direction proof, root allowlist proof, and rollback.

## Rollback

Active replacements need rollback plans. A rollback plan states the action,
steps, and verification commands. Historical and deferred records may explain why
rollback is not executable.

## Diagnostics And Evidence

Failed replacement validation emits stable diagnostics such as
`DOM-REPLACEMENT-MISSING-PROOF` or
`DOM-REPLACEMENT-COMPATIBILITY-BREAK`. Refusals use structured refusal codes
under `dominium.refusal.replacement.*`.

Evidence packets and release proof should cite replacement packet IDs, command
results, validator output, and compatibility proof.

## Release Relationship

Release promotion must know whether a replacement affects public surfaces,
artifacts, schemas, protocols, ABI, providers, modules, or app composition. The
compatibility corpus and version/deprecation law will deepen proof obligations.

## Examples

- Renderer backend rewrite: provider replacement with capability equivalence,
  degradation/refusal behavior, provider conformance, and rollback.
- Schema v2 change: schema replacement with explicit migration or refusal for old
  artifacts.
- Workbench module rewrite: module replacement with descriptor compatibility and
  command/view binding proof.
- Directory move: directory restructure with reference repair, dependency proof,
  and rollback evidence.
