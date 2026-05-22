Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-CAPABILITY-REALITY-LEDGER-01
Stability: provisional
Binding Sources: `.aide/policy/workflow_law.md`, `.aide/policy/dev_main_policy.md`, `.aide/policy/checkpoint_loop_law.md`, `.aide/schema/capability_reality_record.schema.json`, `contracts/capability/capability.registry.json`, `contracts/public_surface/public_surface.contract.toml`

# AIDE Capability Reality Policy

## Purpose

This policy defines how AIDE records the real implementation status of
important capabilities and surfaces.

The ledger prevents documentation, queue files, audits, Workbench projections,
and future agents from claiming `implemented`, `tested`, `exposed`, or
`release_supported` when the repo only contains specifications, schemas,
fixtures, static projections, validators, generated reports, or stubs.

## Status Vocabulary

Use exactly these status values:

- `planned`: desired or queued; no binding contract yet and no implementation
  claim.
- `specified`: contract, schema, or doctrine exists; no fixture proof or
  implementation claim.
- `fixture_only`: fixtures, derived reports, static outputs, or validator
  examples exist; no runtime implementation claim.
- `stubbed`: code path or placeholder exists, but it is intentionally partial
  or non-functional for the real capability.
- `implemented`: runtime or product code path exists; it is not necessarily
  fully tested or exposed.
- `tested`: implementation or proof surface has targeted validation or
  conformance evidence.
- `exposed`: available through product, app, CLI, or runtime surface under
  capability negotiation; not necessarily release-supported.
- `release_supported`: included in a release or promotion claim with
  compatibility/support evidence.
- `retired`: no longer active; retained for compatibility, archive, or history.

`PASS_WITH_WARNINGS` does not automatically imply `implemented`, `tested`,
`exposed`, or `release_supported`.

## Allowed Transitions

A capability may move forward only when new evidence supports the move:

```text
planned -> specified -> fixture_only -> stubbed -> implemented -> tested -> exposed -> release_supported
```

Not every capability must pass through every state. For example, a
documentation-only AIDE policy may move from `specified` to `tested` when a
targeted validator proves the policy packet.

A capability may move backward when evidence is invalidated, support is
withdrawn, or a checkpoint rejects the claim.

`retired` may be reached from any state with explicit rationale and evidence.

## Evidence Requirements

Every record must include evidence refs and a verification method.

Minimum evidence by status:

- `planned`: queue, audit, roadmap, or policy reference.
- `specified`: contract, schema, policy, or doctrine reference.
- `fixture_only`: fixture paths, generated report paths, or validator examples.
- `stubbed`: code path plus explicit notes that the capability is partial or
  non-functional for real support.
- `implemented`: runtime or product code path plus evidence that the code path
  is wired for the declared capability.
- `tested`: targeted validator, conformance test, app test, or proof command.
- `exposed`: product/app/CLI/runtime surface plus negotiation/refusal evidence.
- `release_supported`: release/promotion evidence, compatibility evidence,
  warning disposition, and support scope.
- `retired`: retirement audit or compatibility/archive rationale.

Generated reports are evidence only. They do not promote status by themselves.

## Support Claim Rules

Allowed support claims:

- `none`
- `internal`
- `dev`
- `experimental`
- `release`

Rules:

- `planned`, `specified`, `fixture_only`, and `stubbed` must not use
  `support_claim = "release"`.
- `fixture_only` and `stubbed` must never be described as release-supported.
- `release_supported` requires `support_claim = "release"` and evidence refs.
- `exposed` may use `dev` or `experimental`, but not `release` without release
  evidence.
- A blocked runtime capability must not be marked `implemented`, `tested`,
  `exposed`, or `release_supported`.

## Relationship To Public Surface Registry

The public surface registry classifies surface identity, stability, and
visibility. It does not prove implementation reality by itself.

Capability reality records may reference public surfaces, but they must still
state capability status and evidence separately.

## Relationship To Component And Portability Matrices

Component and portability matrices can support a capability status when they
include relevant evidence. A matrix row alone is not a product support claim
unless the row, evidence, and warning disposition explicitly support that
claim.

## Relationship To Module, Provider, And App Descriptors

Module, provider, and app descriptors are specification evidence unless the
descriptor is paired with runtime wiring and validation.

Provider descriptors do not imply provider runtime. Module descriptors do not
imply runtime module loading. App descriptors do not imply release support.

## Relationship To Package And Pack Surfaces

Package mount planning, pack descriptors, composition plans, and fixture locks
are fixture or specification evidence unless runtime package mounting is
implemented and tested.

Pack-driven integration remains mandatory, but pack metadata must not be used
to claim runtime package loading by itself.

## Relationship To Workbench Status Surfaces

Workbench projections and validation modules may present evidence, but
Workbench is not authority. Workbench shell support requires a separate
implementation and exposure record.

Workbench validation projection proof must not be described as Workbench shell,
runtime module loader, rendered UI, or product gameplay support.

## Fixture-Only, Stubbed, And Planned Claims

Every fixture-only, stubbed, or planned record must include:

- status rationale
- blocking gaps
- non-goals
- next actions

A fixture-only or stubbed capability must refuse or degrade explicitly when a
runtime/product surface asks for real support.

## Ledger Update Rule

After each slice, the responsible task should update or append capability
reality records for surfaces it changes when the task:

- adds or changes a capability, provider, module, app, package, Workbench,
  renderer, replay, release, domain, command, view, or projection surface
- changes implementation status
- adds or invalidates validation evidence
- exposes a surface through product/app/CLI/runtime
- retires or supersedes a surface
- changes support claims

Do not rewrite unrelated ledger history. Append new records when preserving
history matters; update only when the ledger is explicitly treated as the
current-state file for the affected capability.

## Non-Goals

This policy does not implement capability runtime, provider runtime, runtime
module loading, package runtime, Workbench shell, renderer, native GUI,
gameplay, release publication, scheduler behavior, branch automation, or
promotion automation.
