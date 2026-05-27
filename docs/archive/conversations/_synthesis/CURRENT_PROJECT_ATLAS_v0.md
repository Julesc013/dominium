Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: current_project_atlas_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis


# Current Project Atlas v0

This atlas is a reader map. It is not canon and does not promote archived conversation claims.

## Read Order

1. [README.md](../../../../README.md) for current project orientation.
2. [constitution_v1.md](../../../canon/constitution_v1.md) and [glossary_v1.md](../../../canon/glossary_v1.md) for binding meaning.
3. [AGENTS.md](../../../../AGENTS.md) and [AUTHORITY_ORDER.md](../../../planning/AUTHORITY_ORDER.md) for repo/agent authority rules.
4. [.aide/queue/current.toml](../../../../.aide/queue/current.toml) for current scope gates.
5. [DECISION_DOCKET_v0.md](../_decision/DECISION_DOCKET_v0.md) and [PROMOTION_REVIEW_BOARD_v0.md](../_promotion/PROMOTION_REVIEW_BOARD_v0.md) for archive-derived adjudication.

## What Dominium Is

Current repo truth: Dominium is a deterministic, contract-governed simulation game and operating environment built on the Domino deterministic substrate. It is about lawful simulation of invention, production, logistics, economics, settlement, trust, communication, and institutional power.

Conversation-derived context: the archive expands that picture into a long-horizon product ecosystem: engine substrate, official game/domain layer, Workbench, setup/launcher, content packs, portability, release identity, and repo-governed assistant workflows. That context is historical and advisory.

## What Domino Is

Domino is the reusable deterministic substrate: execution ordering, storage, replay, ABI-facing boundaries, and engine mechanisms. Archived conversations consistently treat Domino as reusable infrastructure rather than a one-off game binary.

## Active Surfaces

| Surface | Current Meaning | Archive Context |
| --- | --- | --- |
| `engine/` | deterministic substrate | reusable Domino foundation |
| `game/` | Dominium domain rules and interpretation | official game/product layer |
| `runtime/` | shell/platform/adapters/diagnostics/storage host integration | platform and projection glue, not truth owner |
| `apps/` | thin product composition | client/server/launcher/setup/workbench entrypoints |
| `contracts/` and `schema/` | machine-readable law and compatibility meaning | promotion candidates need high review |
| `docs/archive/conversations/` | derived conversation evidence | source layer for synthesis, not authority |
| `tools/` | validators and repo tooling | repeatable audit/generation/control surfaces |

## Current Work Gates

- Foundation lock status signal: `PASS_WITH_WARNINGS`.
- Current blocked queue scopes: `broad_workbench_ui`, `gameplay`, `native_gui`, `package_runtime`, `provider_runtime`, `release_publication`, `renderer_implementation`, `runtime_module_loader`.
- Safe now: archive reading, decision review, promotion review, reconciliation crosswalks, docs-only microtask preparation, and validators.
- Not safe now: implementation work in blocked scopes, canon/schema/contract rewrites from archive claims, release publication, renderer implementation, gameplay, provider/package runtime, broad Workbench UI, native GUI.

## Unresolved Decisions

- Decision docket items: `30`.
- `Workbench/AIDE/Codex/tooling`: `6`.
- `architecture/boundaries`: `12`.
- `provider/content/packs`: `5`.
- `release/setup/launcher`: `2`.
- `renderer/UI/platform`: `3`.
- `world/time/civilization simulation`: `2`.

## Promotion State

- Raw promotion candidates: `135`.
- Wave 1 docs-only candidates: `18`.
- `architecture_doc_candidate`: `16`.
- `archive_only`: `9`.
- `blocked_by_queue`: `10`.
- `contract_candidate`: `11`.
- `docs_clarification_candidate`: `1`.
- `insufficient_evidence`: `53`.
- `needs_user_decision`: `12`.
- `planning_doc_candidate`: `1`.
- `reject_as_noise`: `19`.
- `schema_candidate`: `3`.

## What Requires Review Before Promotion

- Any claim touching canon, glossary, authority order, contracts, schema law, current queue, release, implementation, or blocked scope.
- Any old language/platform/baseline claim.
- Any claim whose target path is only a wildcard such as `docs/architecture/**` or `contracts/**`.
- Any Wave 1 candidate before source text and target docs are inspected together.

## Recommended Next Steps

1. Manually review the decision docket and choose defer/preserve/promote-later dispositions.
2. Select a small subset of Wave 1 candidates for docs-only microtasks.
3. For each microtask, name the source claim ID, exact target doc, authority support, non-goals, validation, and promotion status update.
4. Keep implementation blocked unless the current queue opens it.
