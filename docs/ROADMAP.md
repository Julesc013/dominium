Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived public roadmap derived from queue, status, contracts, and reviewed audits

# Dominium Roadmap

This roadmap is the public sequencing guide for Dominium. It explains the order
of work without turning planned or blocked features into implementation claims.

This file is derived. If it conflicts with `.aide/queue/current.toml`, canon,
glossary, `AGENTS.md`, active contracts, or reviewed audits, the higher-authority
artifact wins.

## Roadmap Rule

Roadmap entries are permission boundaries, not marketing promises.

```text
Implemented means committed and evidenced.
Planned means intended but not necessarily authorized now.
Blocked means not open until a reviewed phase explicitly opens it.
Experimental means present but subject to change.
```

A completed narrow slice does not automatically open broad product work.

## Current Phase

Dominium is in a narrow governed product-spine phase after Foundation Lock.
Current queue status is `post_presentation_contract_pass_with_warnings`.

Current queue pointer:

| Field | Value |
|---|---|
| Current task | `PRESENTATION-CONTRACT-01` |
| Current result | `PASS_WITH_WARNINGS` |
| Next task | `PROJECTION-CONFORMANCE-01` |
| Alternate next task | `WORKBENCH-SHELL-READONLY-01` |
| Secondary follow-up | `UNIVERSE-EXPLORER-CONTRACT-01` |
| Tertiary follow-up | `POINTER-WIDTH-SERIALIZATION-AUDIT-01` |
| Maintenance follow-up | `FULL-GATE-LEGACY-TEST-ROUTE-01` |

## Near-Term Work

Near-term work should remain narrow, contract-first, and evidence-backed.

| Work item | Public intent | Boundary |
|---|---|---|
| `PROJECTION-CONFORMANCE-01` | Check that projection surfaces conform to current contracts. | Does not open renderer or native GUI implementation. |
| `WORKBENCH-SHELL-READONLY-01` | Establish a read-only Workbench shell direction. | Does not open broad Workbench UI or authoring workflows. |
| `UNIVERSE-EXPLORER-CONTRACT-01` | Define or harden contract surfaces for universe-explorer concepts. | Does not implement broad gameplay. |
| `POINTER-WIDTH-SERIALIZATION-AUDIT-01` | Audit pointer-width and serialization assumptions. | Audit/fix scope only. |
| `FULL-GATE-LEGACY-TEST-ROUTE-01` | Route visible full-gate legacy test debt. | Does not imply full CTest is already passing. |

## Medium-Term Direction

After near-term conformance and audit work, the project can continue widening
only through reviewed phases that preserve the contract spine.

Expected medium-term themes:

- projection conformance and view/action model hardening
- read-only Workbench inspection flows
- command/result/refusal surfaces that remain stable across shells
- pack/package compatibility and mount semantics, within the current trust model
- replay proof and evidence improvements
- AIDE workflow, workunit, checkpoint, and dev/main policy integration
- full-gate debt routing and release-proof preparation

## Later Product Direction

Later phases may include broader product surfaces, but they remain blocked until
explicitly authorized.

Potential later themes:

- broader Workbench UI and authoring workflows
- renderer implementation
- native GUI surfaces
- runtime module loading
- provider runtime expansion
- package runtime expansion
- gameplay/domain feature implementation
- public release publication

These should be described as future direction, not as implemented capability.

## Blocked Until Explicitly Opened

| Area | Status |
|---|---|
| Broad Workbench UI | `BLOCKED` |
| Runtime module loader | `BLOCKED` |
| Provider runtime | `BLOCKED` |
| Package runtime | `BLOCKED` |
| Gameplay | `BLOCKED` |
| Renderer implementation | `BLOCKED` |
| Native GUI | `BLOCKED` |
| Release publication | `BLOCKED` |

Public docs must keep these boundaries visible.

## Claim Ledger

Use this ledger when editing public docs.

| Claim | Allowed wording | Evidence source | Status |
|---|---|---|---|
| Dominium has passed Foundation Lock with warnings | "Foundation Lock is `PASS_WITH_WARNINGS`." | `docs/repo/FOUNDATION_LOCK.md`, `.aide/queue/current.toml` | Implemented/evidenced |
| Fast strict currently passes | "Fast strict is recorded as `PASS`." | `.aide/queue/current.toml` | Implemented/evidenced |
| Full CTest is complete | Do not claim. | `.aide/queue/current.toml` says `NOT_RUN_T4_DEBT`. | Blocked/debt |
| Workbench exists as broad UI/editor | Do not claim. | `.aide/queue/current.toml` blocks broad Workbench UI. | Blocked |
| Workbench validation slice completed | "A narrow Workbench validation slice is recorded as completed." | `.aide/queue/current.toml`, `docs/repo/FOUNDATION_LOCK.md` | Implemented/evidenced |
| Gameplay is playable | Do not claim. | `.aide/queue/current.toml` blocks gameplay. | Blocked |
| Packs/mods can include arbitrary executable code | Do not claim. | `MODDING.md`, canon pack rules. | Not current trust model |
| Public surfaces are contractual | "Public identity must be registered and versioned." | `contracts/public_surface/public_surface.contract.toml`, README. | Implemented policy |

## Release Readiness Boundary

Dominium is not release-ready while release publication is blocked and full
release/trust proof remains debt. Public docs may describe architecture,
contracts, validation, and governed progress, but they must not imply an SDK,
game release, public alpha, production service, or completed mod platform.

## Maintenance Rule

When roadmap state changes:

1. Update the governing queue, audit, or contract first.
2. Update `docs/STATUS.md`.
3. Update this roadmap as a derived summary.
4. Update `README.md` only if the public front-door story changes materially.
5. Leave blocked work visible until a reviewed phase explicitly opens it.
