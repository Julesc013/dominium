Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Replacement Protocol Guidelines

Use a replacement packet when a change substitutes one implementation, provider,
schema, protocol, registry, artifact format, module, command surface, app
composition, or directory-owned surface for another.

## When A Packet Is Required

Create a packet when the change affects:

- public surface identity or compatibility;
- stable, locked, or published artifacts;
- schema/protocol/registry semantics;
- provider identity, capability behavior, or conformance;
- module, Workbench workspace, or app composition descriptors;
- command input/output/refusal behavior;
- ABI or dependency boundaries;
- broad directory ownership or root layout.

A small internal refactor can skip a formal packet only when public surfaces are
unchanged, durable artifacts are untouched, and targeted proof plus fast strict
remain sufficient.

## Packet Checklist

Every active packet should include:

- `replacement_id` using a lowercase dotted `dominium.replacement.*` or
  `domino.replacement.*` ID;
- `replacement_kind` and `status`;
- old and new surfaces by ID;
- affected public surfaces, artifacts, schemas, protocols, commands, providers,
  and modules;
- compatibility, ABI, and dependency impact;
- migration/refusal policy when compatibility can break;
- conformance and compatibility tests;
- rollback plan;
- diagnostics, refusal codes, and evidence references.

## Proof

Choose proof that matches the affected surface:

- public surface: public-surface validator and relevant contract validator;
- ABI: public header and ABI boundary validators;
- schema/protocol: schema/protocol validator and compatibility fixtures;
- artifact: artifact identity validator and migration/refusal proof;
- provider: provider validator plus capability/refusal proof;
- module/app/workbench: descriptor validators and command/view binding proof;
- directory restructure: root/layout/dependency/reference proof.

Fixture proof is useful for law scaffolds. It is not runtime conformance.

## Rollback

Rollback must say what to restore and how to verify it. Do not rely on informal
memory or broad destructive commands. If rollback is not executable, explain why
and keep the packet historical or deferred.

## Compatibility

Do not silently reinterpret old data. If a stable artifact, save, pack, replay,
schema, or command result changes shape, provide explicit migration or structured
refusal.

## Provider Replacement

Provider replacements must reference provider IDs and capabilities. If behavior
degrades, record degraded-from, degraded-to, diagnostics, evidence, and recovery
through capability/refusal law.

## Module Replacement

Module replacements must preserve module identity or declare transition policy.
Modules should depend on services, commands, views, providers, capabilities, and
documents rather than private paths.

## Schema Or Protocol Replacement

Schema/protocol replacements need version policy, unknown-field/default policy,
migration/refusal behavior, and negative fixtures where applicable.

## Invalid Patterns

Bad:

```json
{"replacement_id": "tools/validator.py", "status": "applied"}
```

Good:

```json
{
  "replacement_id": "dominium.replacement.validator.fast_strict.v1",
  "replacement_kind": "tooling",
  "old_surface": {"id": "dominium.testing.test_tiers.v1", "kind": "registry"},
  "new_surface": {"id": "dominium.testing.test_tiers.v1", "kind": "registry"},
  "rollback_plan": {"action": "revert_commit", "steps": ["Revert the patch"], "verification": ["python tools/test/run_fast_strict.py --repo-root ."]}
}
```
