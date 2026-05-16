Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Core / Control / Net Ownership

## Status

- Status: PROVISIONAL
- Phase: POST-CONVERGE-05

## Purpose

`core/`, `control/`, and `net/` are protected roots because they sit on the boundary between deterministic substrate, process admission, authority gates, server policy, transport, SRZ/shard behavior, anti-cheat, replay, and proof artifacts. A root name is not enough evidence to move material wholesale.

This note documents the ownership result from POST-CONVERGE-05. It does not change behavior and does not promote these roots to permanent source-root authority.

## Ownership Rules

- Engine owns universal deterministic substrate and primitives.
- Game owns Dominium-specific domain logic under `game/` or `game/domains/<domain>/`.
- Runtime owns host-facing adapters and runtime transport/control surfaces.
- `apps/server` owns product entrypoint and server composition only.
- Contracts own machine-readable protocols, capabilities, control definitions, and network definitions.
- Docs own human explanation.
- Tools own developer tooling.
- Tests own verification inputs and test harness helpers.

## Invariants

- Process-only mutation remains binding: control and network ingress may create or admit intents, but authoritative truth changes only through lawful Process execution and commit gates.
- Authority gates remain explicit and deterministic.
- Deterministic replay must remain stable across local, server-authoritative, lockstep, and SRZ-hybrid paths.
- Truth, perceived, and render surfaces remain separated.
- Network transport does not equal authority.
- Anti-cheat and integrity semantics require protected review.
- SRZ, shard routing, join, resync, and replay semantics require protected review.

## Current Result

POST-CONVERGE-05 performed no physical moves.

- `core/` remains an active exception because deterministic substrate helpers are imported by game domains, tools, and XStack session runtime.
- `control/` remains an active exception because the deterministic control gateway, Control IR, negotiation, fidelity, planning, capability, view, effects, and proof engines are process- and authority-sensitive.
- `net/` remains an active exception because transport, server-authoritative, lockstep, SRZ hybrid, anti-cheat, shard coordination, and deterministic network test-harness modules are live.

Future movement must split by file role and update references only under an explicit protected ownership task.
