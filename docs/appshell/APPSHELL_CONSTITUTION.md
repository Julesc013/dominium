Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, and `docs/packs/PACK_VERIFICATION_PIPELINE.md`.

# AppShell Constitution

## Purpose

APPSHELL-0 defines the portable product shell for Dominium products outside the
authoritative simulation.

Products covered:

- engine
- game
- client
- server
- setup
- launcher
- tool surfaces

The AppShell is the universal out-of-simulation spine for:

- CLI execution
- TUI hosting
- rendered-mode dispatch for the client
- direct console access
- deterministic logging
- offline operation
- offline verification and boot

## Normative Lifecycle

Every AppShell product lifecycle follows this order:

1. parse args
2. resolve product descriptor
3. load config and profile bundle inputs
4. verify packs and locks when required
5. negotiate compatibility mode if connecting to another endpoint
6. initialize console and logging sinks
7. enter the selected shell mode
8. perform graceful shutdown with deterministic exit code

This lifecycle is bound to `contract.appshell.lifecycle.v1`.

## Modes

The canonical AppShell modes are:

- `mode.cli`
- `mode.tui`
- `mode.rendered`
- `mode.headless`

Rules:

- all products support `mode.cli`
- all products support `mode.tui` through at least a deterministic stub
- `mode.rendered` is client-only
- `mode.headless` is valid for server and engine surfaces and may be used by other
  products only if their product contract declares it

Mode selection is an AppShell concern. It must not mutate authoritative truth or
introduce hidden runtime mode flags into simulation code.

## Root Commands

Every product shares the following root command surface:

- `help`
- `version`
- `descriptor`
- `compat-status`
- `profiles`
- `packs`
- `verify`
- `diag`

Product-specific subtrees remain valid:

- `engine.*`
- `game.*`
- `client.*`
- `server.*`
- `setup.*`
- `launcher.*`
- `tool.*`

APPSHELL-0 only standardizes the shared root surface and bootstrap behavior.
It does not require every product-specific subtree to be implemented yet.

## Console Sessions

Every product exposes a console session surface.

For APPSHELL-0 this means:

- a deterministic CLI command surface is always present
- a REPL console abstraction exists in the shared shell layer
- attach/detach semantics are defined but may remain stubbed until later IPC work

Future IPC attach flows must reuse the AppShell console session model rather than
introducing product-specific consoles.

## Logging

AppShell logging is structured and deterministic.

Required logging rules:

- logs are structured records, not truth mutations
- simulation tick is included where relevant
- host timestamps may appear only as host-meta and must not affect truth, proofs,
  negotiation, or command outcomes
- log ordering must remain deterministic for identical command sequences

## Refusals and Exit Codes

AppShell refusals are explicit and deterministic.

The AppShell must expose:

- a refusal code registry
- a stable exit code registry
- deterministic remediation hints for shell-level refusals

Representative refusal families:

- `refusal.compat.*`
- `refusal.pack.*`
- `refusal.contract.*`
- `refusal.law.*`
- `refusal.debug.*`
- `refusal.io.*`

## Runtime Independence

AppShell is a runtime surface, not a dev-only surface.

Required properties:

- AppShell must work offline
- AppShell must not require repo-only mutable state for normal execution
- appshell must not depend on repo or XStack at runtime
- AppShell shell mechanics must not depend on XStack internals at runtime
- XStack remains a development and governance tool surface

Adapters may bridge to compatibility and pack-verification libraries already
present in runtime code, but the shell core must remain product- and transport-
agnostic.

## What APPSHELL-0 Does Not Do

APPSHELL-0 does not:

- add gameplay features
- add OS widget GUIs
- replace simulation law or process semantics
- require networking or IPC transports
- require repository tooling for normal shell lifecycle logic

## Readiness

APPSHELL-0 establishes:

- a unified bootstrap lifecycle
- shared root commands
- deterministic shell-mode normalization
- portable product-shell adoption

This is the required baseline for:

- APPSHELL-1 command/refusal refinement
- APPSHELL-2 structured logging
- APPSHELL-3 TUI panels
- APPSHELL-4 attach/detach multiplexing
