# Context Transfer Packet for a Future Chat

## Ultra-Condensed Bootstrap Brief

This old chat concerned Dominium’s transition from a messy, root-sprawling game repository into a deterministic, contract-governed, provider-backed, pack-composed simulation platform built on a reusable Domino substrate. The user’s core need was to stop months of structure churn and establish an architecture that supports real development of engine, game, Workbench, apps, modules, packs, providers, and future games without another large refactor.

The major accepted root model is: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, plus `.aide/`, `.aide.local.example/`, `.github/`, `.vscode/`. Do not add top-level `framework/`, `modules/`, `plugins/`, `services/`, `profiles/`, `labs/`, `sdk/`, `src/`, or `source/` unless explicitly contracted.

The key doctrine is: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. Domino Framework is not a source root; it is the public-surface package made of contracts, ABI law, service/provider law, public headers under `engine/include/domino` and `runtime/include/domino`, and conformance tests. Dominium is the game/product family. Workbench is the production/editor/evidence environment. AIDE is the control-plane harness.

The system vocabulary is: component = source/build unit; service = callable runtime capability; provider = replaceable implementation; pack = authored distributable payload; module = declared functional extension unit; workspace = Workbench composition; app = product composition; artifact = persisted versioned object. Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and similar libraries are providers, not architecture. Provider implementations live under `runtime/<service>/providers/<provider>/`; provider selections live in `release/profiles/` or `content/profiles/`; apps stay generic.

The presentation model is: intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view/action model → projection → shell. CLI, text/TUI, rendered GUI, native GUI, headless, Workbench, CI, and AIDE should be projections of the same semantic surfaces.

Current repo status per user reports: broad structure chaos is mostly resolved; canonical structure and fast strict pass or pass with warnings; full CTest/T4 release proof remains debt; broad feature work remains blocked; narrow governed tasks continue. Recent reported work included final canonical structure cleanup, full-gate legacy path routing, provider-structure enforcement, and Domino framework boundary definition.

Recommended next action depends on latest repo status: if fast-strict/RepoX still fail on stale AuditX/identity or launcher marker debt, repair that first. Otherwise proceed with `PROJECTION-CONFORMANCE-01` and/or `PRESENTATION-CONTRACT-01`, then provider wedge tasks for raylib/SDL/Lua.

## Source Hierarchy

1. Direct user statements in this chat.
2. Explicit user-accepted decisions and user-reported commits/statuses.
3. Task and constraint registers in this preservation package.
4. Uploaded directory tree/status artifacts, with caveats for stale/mixed runs.
5. Earlier generated handoff files in `/mnt/data`.
6. Inferences clearly marked.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat. Do not re-ask questions already answered. Verify stale facts before relying on them. Do not treat tentative brainstorms as decisions. Do not repeat rejected options such as adding top-level `framework/`, `modules/`, or `profiles/`. Preserve artifacts and use structured outputs when continuing. Do not restart broad structure cleanup unless a validator finds a hard blocker.

## Active Workstreams

- Canonical structure and root policy.
- Domino Framework boundary and public surface governance.
- C17/C++17 and C-compatible ABI policy.
- Service-first provider architecture and third-party fencing.
- Presentation/projection spine.
- Workbench module/workspace development.
- Full-gate proof repair.
- AIDE workflow/evidence classification.

## Current Priorities

1. Repair stale proof/evidence/marker debt if fast-strict is blocked.
2. Proceed to `PROJECTION-CONFORMANCE-01` / `PRESENTATION-CONTRACT-01` when gates allow.
3. Implement provider wedge for raylib/SDL/Lua only through service/provider contracts.
4. Continue full CTest/T4 audit.

## Current Open Questions

- Is full CTest green in the live repo?
- Which Lua version is pinned?
- Is `external/upstream` or `external/vendor` canonical?
- Are AIDE cache/queue/reports canonical control-plane data or local/generated state?
- Is pack-internal `content/` canonical or legacy?

## Recommended First Action

Check the latest live repo gate status. If fast-strict or RepoX still fails due stale evidence/marker debt, run a focused proof-hygiene repair. If normal gates are clean, run `PROJECTION-CONFORMANCE-01` next.
