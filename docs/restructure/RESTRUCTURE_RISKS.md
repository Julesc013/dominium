Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RESTRUCTURE
Replacement Target: executed move sequencing plan and shim retirement checklist after one stable release

# Restructure Risks

This document ranks the highest-risk move areas for the future repository restructure. It is derived from the current repository inventory and duplication reports and is intended to control move order, not to trigger immediate churn.

## Current Risk Signals

- Repository inventory entries: `5493`
- Validation entrypoints still distributed: `13`
- Direct path heuristic candidates: `2172`
- Platform-gated files by heuristic: `128`
- Legacy-classified entries: `166`
- Structural unknowns: `0`

## Highest-Risk Modules

### High

- `src/appshell/*`
  - Reason: owns bootstrap, command dispatch, IPC, supervisor, virtual paths, and install discovery.
  - Move risk: any partial move can break all products at once.
- `src/compat/*`
  - Reason: negotiation, descriptors, contract pinning, pack compatibility, and degrade ladders sit here.
  - Move risk: descriptor/hash drift or attach/read-only regressions.
- `src/lib/*`
  - Reason: install/store/instance/save resolution is path-sensitive and now mediated through vpaths.
  - Move risk: portable vs installed parity regressions.
- `src/core`, `src/runtime`, `src/time`, `src/meta`, `src/universe`, `src/field`, `src/fields`
  - Reason: foundational truth/determinism/time surfaces with wide fan-out.
  - Move risk: broad import fallout and accidental cycle creation.
- `src/system/*` and `src/process/*`
  - Reason: authoritative mutation and collapse/stabilization layers sit here.
  - Move risk: cross-domain import churn and process-only mutation invariant risk.
- `schema/*` plus `schemas/*`
  - Reason: dual schema trees are consumed by validators, compat tooling, and generated docs.
  - Move risk: broken validation/import paths across many tools.

### Medium

- `src/worldgen/earth/*`, `src/worldgen/mw/*`, `src/worldgen/galaxy/*`, `src/astro/*`
  - Reason: logical destination is the future `/src/astro/*` tree, but current code spans both `src/worldgen` and `src/astro`.
  - Move risk: package-boundary drift rather than semantic duplication.
- `src/client/ui/*`, `src/client/render/*`, `src/ui/*`
  - Reason: rendered UI and shared UI model are now harmonized but still physically split.
  - Move risk: adapter import regressions and accidental truth/view coupling.
- `src/server/*`
  - Reason: server product wrappers and runtime surfaces are still mixed.
  - Move risk: product-entry and headless boot regressions.
- `tools/xstack/*`
  - Reason: deep CI/test orchestration tree with many references.
  - Move risk: large merge-conflict surface rather than runtime risk.
- `dist/*` runtime data mirrors
  - Reason: packs, locks, and profiles are portable-install critical.
  - Move risk: install discovery and vpath parity regressions if moved too early.

### Low

- `tools/review/*`, `tools/audit/*`, `tools/release/*`
  - Reason: leaf tooling with limited runtime coupling.
  - Move risk: doc/report path churn only.
- `tools/launcher/*`, `tools/setup/*`, product wrapper scripts
  - Reason: now thin AppShell wrappers.
  - Move risk: manageable if entrypoint shims stay in place.
- `src/platform/*`
  - Reason: probe/adapters are isolated and capability-gated.
  - Move risk: mostly import and documentation cleanup.

## Duplication Clusters To Treat As Move Units

- Validation surface cluster
  - Evidence: `13` validation entrypoints remain distributed.
  - Recommendation: move under a single planned `/tools/compat` and `/tools/release` envelope only after wrapper commands remain stable.
- Path resolution cluster
  - Evidence: `2172` direct-path heuristic candidates.
  - Recommendation: do not physically move these until vpath shims and virtual roots cover the target area.
- UI surface cluster
  - Evidence: rendered UI, shared UI model, and native stubs are split across `src/client/*`, `src/ui/*`, and AppShell TUI surfaces.
  - Recommendation: move only after command-driven UI boundaries remain fully green.
- Astro/worldgen cluster
  - Evidence: Milky Way, Earth, galaxy stubs, and SOL surfaces are physically split even though they are now canon-linked.
  - Recommendation: move as bounded leaf packages after import shims exist.
- Product wrapper cluster
  - Evidence: product entries live across `src/server/*`, `tools/mvp/*`, `tools/launcher/*`, `tools/setup/*`, and `tools/appshell/*`.
  - Recommendation: converge wrappers before touching lower domain layers.

## Recommended Move Order

### 1. Documentation and Namespace Alias Prep

- Add package-level alias modules and include-path wrappers only.
- Publish the target mapping and move sequence first.
- No file moves yet.

### 2. Leaf Tooling and Review Surfaces

- `tools/review/*`
- `tools/release/*`
- selected `tools/audit/*` leaves

Reason: lowest runtime risk and immediate benefit for future navigation.

### 3. Product Wrappers and Adapter Leaves

- launcher/setup wrappers
- product stub wrappers
- rendered/native UI adapter leaves
- supervisor/product host leaves that are not truth engines

Reason: isolates executable entry surfaces before deeper package moves.

### 4. Platform and UI Boundaries

- `src/platform/*`
- `src/ui/*`
- `src/client/ui/*`
- `src/client/render/*`

Reason: these should become thin adapter zones before domain/core movement begins.

### 5. Compat and Lib

- `src/compat/*`
- `src/lib/*`
- related `tools/compat*` surfaces

Reason: once wrappers exist, moving these surfaces creates the biggest long-term clarity win, but only after path and install shims are already proven.

### 6. Astro and Worldgen Leaves

- `src/astro/*`
- `src/worldgen/mw/*`
- `src/worldgen/earth/*`
- `src/worldgen/galaxy/*`
- `src/pollution/*`

Reason: logical convergence into `/src/astro/*` can happen package by package.

### 7. System and Process Clusters

- `src/system/*`
- `src/process/*`

Reason: these have broad cross-domain reach and should move only after import boundaries are already tightened.

### 8. Core, Runtime, Time, and Schema Trees

- `src/core`
- `src/runtime`
- `src/time`
- `src/meta`
- `src/universe`
- `src/field`
- `src/fields`
- `schema/*`
- `schemas/*`

Reason: highest blast radius; reserve for the end when wrappers, tests, and gates are already mature.

## Move Rules

- One subsystem per pull request.
- Keep all old import paths working through wrappers until shim retirement.
- Keep build outputs, product ids, executable names, and virtual roots unchanged during moves.
- Do not co-mingle semantic edits with file moves.
- Re-run convergence gates after every move batch.

## Modules That Should Not Move Early

- `src/appshell/supervisor/*`
- `src/appshell/ipc/*`
- `src/appshell/paths/*`
- `src/lib/install/*`
- `src/compat/capability_negotiation.py`
- `src/compat/descriptor/*`
- `src/runtime/process_spawn.py`
- `schema/*` and `schemas/*`

These are late-phase or shim-first surfaces because they affect every product or gate.

## MVP Shipping Conclusion

The proposal does not require immediate physical moves to ship MVP. The current repo is already stabilized by:

- virtual paths
- install discovery
- AppShell-only entrypoints
- unified validation
- unified tool surface
- negotiated IPC
- supervisor hardening

Restructure work should therefore remain post-freeze, incremental, and gate-driven.
