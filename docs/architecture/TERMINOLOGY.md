# Terminology

Status: canonical.
Scope: binding definitions for all documentation.
Authority: canonical. All other docs MUST defer to this file for terminology.

All terms in this file MUST be used with these meanings. Any definition change
SHALL be treated as an explicit breaking revision.

## Engine
Definition: The deterministic, content-agnostic runtime that enforces
invariants and executes authoritative state transitions.
Does NOT mean: game rules, content, or presentation logic.

## Game
Definition: The authoritative rules and meaning built on engine public APIs.
Does NOT mean: engine mechanisms or platform backends.

## Content
Definition: Data-only definitions supplied by packs; no executable logic.
Does NOT mean: code, embedded assets, or hard-coded rules.

## Pack
Definition: A versioned external content bundle resolved by UPS and declared by
capabilities and requirements.
Does NOT mean: a file path, directory layout, or embedded asset set.

## Mod
Definition: A pack that extends, replaces, or augments content within declared
compatibility bounds.
Does NOT mean: an unbounded override or an implicit patch.

## Capability
Definition: A named permission required to attempt an action or process.
Does NOT mean: a feature toggle or a file-path entitlement.

## Authority token
Definition: An explicit credential that grants a set of capabilities.
Does NOT mean: implicit admin status or hidden privilege.

## Process
Definition: A deterministic, declared rule that produces authoritative state
changes or authoritative knowledge changes.
Does NOT mean: ad-hoc code paths or background mutation.

## Transformative process
Definition: A process that changes authoritative state in a defined way.
Does NOT mean: derived presentation changes.

## Transactional process
Definition: A process that applies state changes atomically and enforces
conservation across declared quantities.
Does NOT mean: best-effort or partial updates.

## Epistemic process
Definition: A process that changes authoritative knowledge or visibility state.
Does NOT mean: physical state mutation.

## Topology node
Definition: A canonical identity in the world graph.
Does NOT mean: a transient render or UI object.

## Domain
Definition: A bounded jurisdiction where laws apply and authoritative
simulation is valid.
Does NOT mean: a visual region or a client-side partition.

## Domain volume
Definition: The explicit spatial volume that bounds a domain.
Does NOT mean: an implicit or unbounded extent.

## Field
Definition: An authoritative spatial dataset used by simulation.
Does NOT mean: a map layer or a rendered texture.

## Representation tier
Definition: The declared level of detail used to derive representation.
Does NOT mean: a change in authoritative identity.

## Representation tier: explicit
Definition: All required detail is explicitly provided by authoritative data.
Does NOT mean: procedural generation at runtime.

## Representation tier: hybrid
Definition: Authoritative data is combined with deterministic derivation.
Does NOT mean: ad-hoc or nondeterministic generation.

## Representation tier: procedural
Definition: Representation is derived deterministically from coarse data or
rules.
Does NOT mean: random or uncontrolled synthesis.

## Latent / unknown state
Definition: Authoritative state that exists but is intentionally unspecified or
unknown to an observer.
Does NOT mean: missing data or an error condition.

## Event
Definition: A scheduled invocation of a process at authoritative time.
Does NOT mean: a UI event or rendering callback.

## Snapshot
Definition: A recorded state at a specific authoritative time.
Does NOT mean: a derived visualization.

## Objective snapshot
Definition: A snapshot that records authoritative state.
Does NOT mean: an observer-specific view.

## Subjective snapshot
Definition: A snapshot derived for a specific observer or view.
Does NOT mean: authoritative truth.

## Save
Definition: A serialized objective snapshot with provenance and authority
scope.
Does NOT mean: a replay log or scripted behavior.

## Replay
Definition: A deterministic event log that reproduces authoritative outcomes.
Does NOT mean: a video recording or a save file.

## Derived data
Definition: Data computed from authoritative state for presentation or tooling.
Does NOT mean: authoritative inputs or sources of truth.

## Protocol
Definition: A wire or file-format contract.
Does NOT mean: a source-level API.

## API
Definition: A source-level contract.
Does NOT mean: an ABI or wire protocol.

## ABI
Definition: A binary-level contract.
Does NOT mean: a source API or a protocol definition.

## Zero-asset boot
Definition: A product startup path that succeeds with zero assets or packs and
provides CLI-level operation.
Does NOT mean: a minimal content pack.

## Deprecated aliases (DO NOT use)
- Feature (permission sense) -> Capability
- Map or layer (authoritative sense) -> Field
- Entity (canonical identity sense) -> Topology node
- Asset bundle (authoritative sense) -> Pack
