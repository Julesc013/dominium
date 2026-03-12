Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Boundary Enforcement

Status: Normative
Version: 1.0.0
Last Updated: 2026-02-28

## Purpose

This document defines hard architectural boundaries that make structural drift mechanically difficult.
The framework is governance/tooling-only and does not change runtime simulation semantics.

## Enforcement Layers

- Compile-time/build-time (CMake + deterministic boundary scanner)
  - Build configure fails if boundary scanner reports forbidden dependencies.
  - `check_build_boundaries` is included in `check_all`.
- RepoX scan-time
  - Hard-fail/refusal invariant checks for boundary violations.
- AuditX semantic-time
  - Boundary analyzers aggregate violation smells and produce actionable reports.
- TestX runtime-time
  - Boundary suite validates scanner behavior, platform isolation, tool isolation, and intent dispatch controls.

## Boundary Categories

1) Truth/Render isolation
- Renderer and render adapters consume Perceived/RenderModel only.
- Truth symbols and process mutation symbols are forbidden in render paths.
- Enforced by:
  - `INV-RENDER-TRUTH-ISOLATION`
  - existing renderer isolation invariants.

2) Core abstraction isolation
- Graph/flow/state/schedule logic must stay in core substrates.
- Domain modules consume core substrates; core modules must not depend on domain modules.
- Enforced by:
  - `INV-NO-DUPLICATE-GRAPH-SUBSTRATE`
  - `INV-NO-DUPLICATE-FLOW-SUBSTRATE`
  - `INV-NO-ADHOC-STATE-FLAG`
  - `INV-NO-ADHOC-SCHEDULER`.

3) Platform isolation
- OS/platform API headers/tokens are isolated to `src/platform`.
- Enforced by:
  - `INV-PLATFORM-ISOLATION`.

4) Tool suite isolation
- Runtime modules must not import/include tool-suite paths.
- Tools remain removable from authoritative runtime dependencies.
- Enforced by:
  - `INV-NO-TOOLS-IN-RUNTIME`.

5) Control pipeline isolation
- Direct intent envelope construction is restricted to explicit ingress/control paths.
- Allowed paths are declared in a deterministic whitelist registry:
  - `data/registries/intent_dispatch_whitelist.json`
- Enforced by:
  - `INV-NO-DIRECT-INTENT-ENVELOPE-CONSTRUCTION`
  - legacy direct-dispatch invariant checks.

## Severity Contract

- FAST profile: boundary violations are `fail`.
- STRICT/FULL profiles: boundary violations are `refusal`.

## Debug Assertions (Dev Builds Only)

Optional runtime assertions are enabled only in debug/dev assertion mode and are compile-time removable from release workflows:
- no render-to-truth pointer/channel leakage,
- mutation through commit phase only,
- ledger accounting completeness,
- schedule/state/hazard updates routed through component engines.

## Determinism and Runtime Cost

- All boundary checks are deterministic scans over canonical paths and sorted file order.
- Tooling checks do not alter simulation outcomes.
- Debug assertions are optional and disabled by default to avoid release overhead.
