Status: CANONICAL
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Architecture Glossary

This document binds architecture-level terminology used by canonical specs and invariants.
For broader cross-product definitions, see `docs/GLOSSARY.md`.

## Core Terms

- **Engine**: Deterministic mechanism substrate and runtime systems.
- **Game**: Authoritative meaning layer built on engine public APIs.
- **Law**: Rule set that admits or refuses intents before mutation.
- **Capability**: Explicit permission required to attempt an intent.
- **AuthorityContext**: Runtime authority envelope carrying origin, law profile, and entitlements.
- **Process**: The only legal mutation path for authoritative state.
- **Refusal**: Deterministic denial with reason code and audit evidence.
- **TruthModel**: Canonical simulation state.
- **PerceivedModel**: Lens-filtered observable projection of truth.
- **RenderModel**: Renderer-target projection consumed by CLI/TUI/GUI.
- **Lens**: Controlled transform from truth to perception under law and authority constraints.
- **ExperienceProfile**: Presentation and discovery defaults bound to a `LawProfile`.
- **LawProfile**: Declarative capability and entitlement policy.
- **ParameterBundle**: Tunable numeric inputs; no semantic branching.
- **SessionSpec**: Canonical launch contract for an executable session.
- **UniverseIdentity**: Immutable root identity and seed context.
- **UniverseState**: Mutable runtime state tied to identity.

## Governance Terms

- **RepoX**: Static invariant and policy enforcement.
- **TestX**: Behavioral and determinism verification.
- **AuditX**: Semantic drift and structural smell detection.
- **XStack**: Coordinated governance execution model.
- **FAST / STRICT / FULL**: Gate profiles for incremental, deep, and exhaustive validation.

## Constraints

- Runtime code must not use hardcoded mode flags.
- UI must dispatch commands through the canonical command graph.
- Engine and game must not read user settings directly.
- All authoritative changes must be deterministic and reproducible.
