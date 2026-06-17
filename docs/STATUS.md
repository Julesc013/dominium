Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived public status surface derived from canon, queue, contracts, and reviewed audits

# Dominium Status

This page is the public status surface for Dominium. It explains what is real in
the repository today, what remains blocked, and which artifacts should be used
to verify claims.

This file is derived. If it conflicts with canon, glossary, `AGENTS.md`, active
contracts, `.aide/queue/current.toml`, or reviewed audits, the higher-authority
artifact wins.

## Summary

Dominium is **not release-ready**. The project has passed Foundation Lock with
warnings and is proceeding through narrow governed product-spine slices. Public
documentation should present it as a deterministic, contract-governed simulation
engine and game platform under active development, not as a finished playable
game or released engine SDK.

## Current Operational Snapshot

| Area | Current value | Meaning |
|---|---|---|
| Foundation Lock | `PASS_WITH_WARNINGS` | Required governance and validation layers exist, but warnings and debt remain visible. |
| Queue status | `post_presentation_contract_pass_with_warnings` | The current queue has advanced through presentation-contract work. |
| Current task | `PRESENTATION-CONTRACT-01` | Recorded as `PASS_WITH_WARNINGS`. |
| Next task | `PROJECTION-CONFORMANCE-01` | Recommended next narrow task. |
| Alternate next task | `WORKBENCH-SHELL-READONLY-01` | Read-only Workbench shell direction only. |
| Secondary follow-up | `UNIVERSE-EXPLORER-CONTRACT-01` | Contract work, not broad gameplay implementation. |
| Tertiary follow-up | `POINTER-WIDTH-SERIALIZATION-AUDIT-01` | Audit follow-up. |
| Maintenance follow-up | `FULL-GATE-LEGACY-TEST-ROUTE-01` | Full-gate debt routing. |
| Large parallel execution | `false` | Broad parallel implementation is not authorized. |
| Broad feature work | `false` | Broad product work remains blocked. |

Source of truth for this table: `.aide/queue/current.toml`.

## Validation Snapshot

| Validation area | Current value | Notes |
|---|---|---|
| Architecture policy | `PASS` | Architecture policy validator passes. |
| Portability matrix | `PASS` | Portability matrix validator passes. |
| Component matrix | `PASS` | Component matrix validator passes. |
| Dependency direction strict | `PASS` | Dependency direction strict passes. |
| Fast strict | `PASS` | Normal development proof gate passes. |
| Presentation contract | `PASS` | Presentation-contract validator passes. |
| AIDE | `PASS_WITH_WARNINGS` | AIDE local validation passes with warnings. |
| AIDE workunit schemas | `PASS` | Workunit schema validation passes. |
| AIDE dev/main policy | `PASS` | Dev/main policy validation passes. |
| AIDE checkpoint loop policy | `PASS` | Checkpoint loop policy validation passes. |
| AIDE capability reality | `PASS` | Capability reality validation passes. |
| RepoX strict | `PASS_WITH_WARNINGS` | RepoX strict passes with warnings. |
| CMake configure/build | `PASS_THROUGH_FAST_STRICT` | Covered through fast strict. |
| Smoke CTest | `PASS_THROUGH_FAST_STRICT` | Covered through fast strict. |
| Full CTest | `NOT_RUN_T4_DEBT` | Full release/trust proof remains debt. |

Do not convert a green fast strict result into a claim of full certification.

## Completed Narrow Slices

Completed work recorded in the current queue includes:

- `FOUNDATION-CLOSEOUT-02`
- `PORTABILITY-ARCH-POLICY-02`
- `MATRIX-CLEANUP-00`
- `SERVICE-CONFORMANCE-LAW-01`
- `DOCUMENT-PATCH-TRANSACTION-RUNTIME-01`
- `PROJECT-GRAPH-SERVICE-01`
- `COMPOSITION-RESOLVER-LAW-01`
- `DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01`
- `WORKBENCH-VALIDATION-SLICE-01`
- `COMMAND-RESULT-VIEW-SLICE-01`
- `PHASE-REVIEW-02`
- `PACKAGE-MOUNT-SLICE-01`
- `QUEUE-RECONCILE-01`
- `REPLAY-PROOF-SLICE-01`
- `BAREBONES-CLIENT-SHELL-01`
- `PRODUCT-SPINE-REVIEW-01`
- `AIDE-WORKFLOW-LAW-01`
- `STATUS-RECONCILE-02`
- `AIDE-WORKUNIT-SCHEMA-01`
- `AIDE-DEV-MAIN-POLICY-01`
- `AIDE-CHECKPOINT-LOOP-01`
- `AIDE-CAPABILITY-REALITY-LEDGER-01`
- `PRESENTATION-CONTRACT-01`

These slices indicate governed progress. They do not authorize broad gameplay,
renderer, runtime-provider, package-runtime, native-GUI, or release-publication
claims.

## Blocked Areas

| Area | Status | Public wording |
|---|---|---|
| Broad Workbench UI | `BLOCKED` | Workbench UI is not broadly open; only reviewed narrow slices may proceed. |
| Runtime module loader | `BLOCKED` | Runtime module loading is not implemented/open as a broad feature. |
| Provider runtime | `BLOCKED` | Provider runtime expansion remains blocked. |
| Package runtime | `BLOCKED` | Package runtime is not open beyond reviewed contract/slice work. |
| Gameplay | `BLOCKED` | Do not present Dominium as a playable gameplay release. |
| Renderer implementation | `BLOCKED` | Renderer implementation is not open as a broad feature. |
| Native GUI | `BLOCKED` | Native GUI work is not open as a broad feature. |
| Release publication | `BLOCKED` | No public release/publication status should be claimed. |

## Implemented / Planned / Blocked Claim Boundary

| Claim class | Allowed public language | Disallowed public language |
|---|---|---|
| Implemented contracts and validators | "The repository contains contract and validation surfaces for commands, diagnostics, refusals, modules, providers, public surfaces, packages, and replay proof." | "The runtime implements every contracted system end to end." |
| Narrow completed slices | "Several narrow product-spine slices are recorded as completed with warnings." | "The product spine is complete." |
| Build and fast strict gate | "The normal fast strict gate is recorded as passing in the current status." | "The project is fully certified or release-ready." |
| Workbench | "Workbench is the governed validation/inspection direction, with narrow slices completed." | "Workbench is a complete editor or production UI." |
| Modding and packs | "Pack and modding policy is data-first and contract-governed." | "Arbitrary executable mods are supported." |
| Gameplay | "Gameplay remains blocked as broad feature work." | "Dominium is currently playable as a game release." |

## Evidence Sources

Use these artifacts before changing public status language:

- `.aide/queue/current.toml`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `contracts/testing/test_tiers.contract.toml`
- `contracts/public_surface/public_surface.contract.toml`
- `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- `docs/development/guides/BUILDING.md`

## Maintenance Rule

When any current-task, validation, or authorization status changes:

1. Update `.aide/queue/current.toml` or the governing source first.
2. Update this page only as a derived public summary.
3. Update `README.md` if the public front-door status changes materially.
4. Keep blocked areas visible until a higher-authority artifact explicitly opens
them.
5. Do not describe planned or blocked systems as implemented.
