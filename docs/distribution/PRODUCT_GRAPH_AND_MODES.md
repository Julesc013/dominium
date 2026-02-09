Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Product Graph And Modes

## Scope

This document defines the distribution-time product graph and runtime mode backend
selection contract used by packaging, setup, launcher, RepoX, and TestX.

## Product Graph Contract

- Product graph source of truth: `data/registries/product_graph.json`.
- Schema contract: `schema/distribution/product_graph.schema`.
- Nodes declare provided exports and capabilities.
- Node requirements must be explicit and resolved before run/install.
- SDK nodes must not depend on setup or launcher products.

## Initial Product Nodes

- `dominium.product.engine` provides `export:lib.engine`.
- `dominium.product.game` provides `export:lib.game`, requires `export:lib.engine`.
- `dominium.product.client` provides `export:bin.client`, requires engine + game exports.
- `dominium.product.server` provides `export:bin.server`, requires engine + game exports and `capability.render.null`.
- `dominium.product.launcher` provides `export:bin.launcher`, requires `export:bin.client`.
- `dominium.product.setup` provides `export:bin.setup`, requires `export:tool.pkg.verify`.
- `dominium.product.sdk.engine` and `dominium.product.sdk.game` are SDK-only and restricted from setup/launcher deps.

## One Binary Three Modes

- Runtime mode selection source of truth: `data/registries/mode_backend.json`.
- Schema contract: `schema/ui/mode_backend.schema`.
- Modes are `cli`, `tui`, `gui`.
- A single executable may expose all modes if backend and entitlement checks pass.
- Deterministic fallback order must be declared and data-driven.

## Mode Backend Rules

- `cli` is always available.
- `tui` requires tty detection + backend availability.
- `gui` requires declared backend package capability.
- Backend selection must not be hardcoded in runtime logic.
- Refusal must use stable reason codes and include missing backend/capability details.

## Access And Dispatch

- GUI and TUI command entry points must dispatch through canonical command graph.
- AccessSet and EntitlementSet checks apply before command execution.
- No mode may bypass capability checks or epistemic rules.
