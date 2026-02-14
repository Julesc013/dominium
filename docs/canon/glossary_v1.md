Status: CANONICAL
Version: 1.0.0 (Normative)
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0.
Scope: Dominium / Domino ecosystem vocabulary.

# Dominium Canonical Glossary v1.0.0

This is the full canonical glossary v1.0.0.
If terminology conflicts with local or legacy docs, this glossary wins.

## A

### Account
A user identity external to the simulation ontology used for authentication, entitlements, and multiplayer coordination. An Account is not an Agent unless explicitly instantiated as one within the simulation.

### Activation Policy
A deterministic rule set defining when a Domain, Solver, or Micro-simulation may activate within a region of interest.

### Agent
An Assembly capable of submitting Intents under AuthorityContext and LawProfile constraints.

### Architecture
The structural layering of Dominium systems including Engine, Game, Client, Server, and XStack governance components.

### Artifact
A produced output from a build, verification, simulation, or governance process.

### Artifact Class
The classification of artifacts into Canonical, Derived, or Run-meta categories.

### Authority
Permission to execute Processes under Law. Authority is not power; it is validated capability within constraints.

### AuthorityContext
The structured permission context required for all Process execution. Includes authority_origin, law_profile_id, entitlements, epistemic_scope, and privilege_level.

### AuthorityOrigin
The origin of authority: client, server, tool, replay, etc.

### Authority tick
The evaluation step where AuthorityContext is validated before Process execution.

### AuditX
The static analysis subsystem within XStack responsible for detecting drift, anti-patterns, and semantic violations.

## B

### Bad
Normatively incorrect or violating the Constitutional Architecture, invariants, or determinism.

### Binary
A compiled executable or library artifact.

### Budget Envelope
The deterministic compute constraints governing simulation cost per region, session, or tick.

### Budget Policy
A registry-driven configuration defining solver activation and fidelity under compute constraints.

### Bug
A deviation from deterministic, lawful, or architectural correctness.

### Build
The deterministic compilation and linking process producing Binaries.

### Bundle
A collection of Packs grouped for installation or activation.

### BundleProfile
A declarative definition of grouped Packs, tools, or experiences.

## C

### Cache store
Persistent content-addressed storage of verification or computation results keyed by input hash.

### Canon
The locked architectural truth of Dominium.

### Canonical
Conforming strictly to Canon and deterministic identity.

### Canonical artifact
A source-of-truth artifact that must not change without explicit migration.

### Canonical hash
A deterministic hash representing canonical state.

### Capability
A specific permission or affordance enabling a Process.

### CLI
Command Line Interface.

### Classroom-restricted
A SecureX trust category restricting certain Packs or features to educational environments.

### Client
The application responsible for rendering, input capture, and presentation of PerceivedModel.

### Collapse
Reduction of simulation detail into a Macro Capsule while preserving invariants.

### CompatX
The XStack subsystem enforcing compatibility and migration rules.

### Compatibility
The ability to maintain deterministic behavior across versions.

### Conservation guarantee
The requirement that physical and logical invariants are preserved across simulation tiers.

### Contract
A normative rule set defining allowed behaviors and invariants.

### ControlX
The orchestration and planning subsystem of XStack.

### Creative
An ExperienceProfile representing expanded construction authority governed by LawProfile.

## D

### Debug
An ExperienceProfile or entitlement allowing diagnostic access.

### Debug panel
A non-diegetic interface enabled only under explicit LawProfile.

### Deprecated
A term or pattern forbidden for use in code identifiers.

### Determinism
The property that identical inputs produce identical state hashes.

### Deterministic packaging
Packaging process producing bitwise identical artifacts given identical inputs.

### Derived artifact
An artifact deterministically generated from canonical artifacts.

### Dev
Developer environment context.

### Diegetic Lens
A Lens existing within simulation ontology and accessible to Agents.

### Diegetic UI
A UI representation existing as in-world instrument or Assembly.

### Distribution
A packaged form of Binaries and Packs for release.

### Domain
A modular simulation subsystem representing a coherent phenomenon (e.g., climate).

### Domain registry
A canonical registry listing all active Domains.

### Drift
Deviation from Canon or structural invariants.

## E

### Editor
An ExperienceProfile permitting scenario or blueprint modification.

### Engine
Domino, the deterministic universe simulation core (C89).

### Entitlement
A permission token within AuthorityContext.

### Epistemic scope
The boundary of information accessible to an Agent.

### Expand
Increase simulation detail from Macro Capsule to Micro-simulation.

### Execution plan
A deterministic sequence of verification or simulation actions.

### Execution Profile
FAST, STRICT, or FULL verification profile.

### ExperienceProfile
Defines presentation defaults, allowed lenses, and LawProfile bindings.

### Extensible
Capable of expansion via Domain packs without refactor.

## F

### Fake
A representation not grounded in simulation ontology.

### FAST
Incremental verification profile prioritizing speed.

### Feature
A declared addition conforming to Canon.

### Fidelity
Resolution level of solver approximation under conservation contract.

### Fidelity Boundary
The transition interface between solver tiers.

### Fidelity policy
Registry defining solver tier activation rules.

### Field
A deterministic property over space/time or Assembly.

### File
A stored data or code unit within the repository.

### Fixed-point math
Deterministic arithmetic representation used by Engine.

### Forwards compatible
Ability to run older saves in newer versions with migration.

### Forbidden
Explicitly disallowed by Canon or RepoX.

### Frame tick
Presentation update cycle distinct from simulation tick.

### Future proof
Architecturally designed to allow extension without refactor.

## G

### Game
Dominium, the C++98 gameplay layer atop Domino.

### GBN
Global Build Number for release tracking.

### Glossary
This authoritative normative definition set.

### Good
Conforming to Canon and invariants.

### GUI
Graphical User Interface.

## H

### Hardcore
LawProfile with stricter constraints and no respawn.

### HUD
Heads-up display; non-diegetic unless explicitly diegetic via instrument.

## I

### Identity
Stable deterministic identifier for Universe or Assembly.

### Identity fingerprint
Canonical hash representing identity invariants.

### Impact graph
Dependency mapping from file changes to verification scope.

### Instance
A running SessionSpec execution context.

### Interest radius
Spatial boundary determining Micro-simulation activation.

### Interest region
Region under detailed simulation.

### Invariant
A rule that must always hold.

### Issue
Tracked deviation or defect.

## L

### Lab
An ExperienceProfile for experimentation.

### Law
Constraint system governing Process execution.

### LawProfile
Declarative rule set enabling/disabling Processes and lenses.

### Lens
Transformation from TruthModel to PerceivedModel.

### LOD
Level of Detail; fidelity level in presentation or simulation.

## M

### Macro
Aggregate simulation layer.

### Macro Capsule
Aggregate representation preserving invariants.

### Macro-simulation
High-level simulation of aggregates.

### Merkle hash tree
Content-addressed hashing system for subtree change detection.

### Metric
A quantitative measurement within simulation or verification.

### Micro
Detailed simulation layer.

### Micro-simulation
Fine-grained simulation of Assemblies and Fields.

### MissionSpec
Declarative mission definition with predicates.

### Mod
Third-party Pack extending Domain or content.

### Modular
Composed of replaceable independent components.

## N

### Named RNG Stream
Deterministic pseudo-random sequence identified by name.

### Non-diegetic Lens
Lens external to simulation ontology.

### Non-diegetic UI
UI not existing within ontology.

## O

### Observation artifact
Deterministic output of Observation Kernel.

### Observation Kernel
Function mapping `TruthModel x Lens x LawProfile x AuthorityContext -> PerceivedModel`.

### Official
Pack signed and verified by SecureX.

### Observer
ExperienceProfile allowing non-mutating observation.

### Overlay
Presentation layer component rendered over scene.

## P

### Pack
Modular content or Domain extension unit.

### Package
Bundled distribution artifact.

### ParameterBundle
Numeric tuning configuration.

### Parity
Consistency across CLI, TUI, GUI.

### PerformX
Performance enforcement subsystem.

### Pipe dream
Speculative future feature not yet implemented.

### Platform
Target operating environment.

### Process
The sole mutation mechanism.

### Process-only mutation
Invariant prohibiting mutation outside Process.

### Profile
Generic term referring to LawProfile or ExperienceProfile.

### Program
Executable binary.

### Privilege level
AuthorityContext permission tier.

## R

### Reality
Simulation ontology truth.

### Refusal
Deterministic denial of Process execution.

### Refusal Contract
Normative structure requiring reason code and remediation hint.

### Reliable
Deterministic and invariant-preserving.

### Renderer
Presentation subsystem consuming PerceivedModel.

### Replay
Deterministic re-execution of Process log.

### RepoX
Static governance enforcement subsystem.

### Retro
Legacy or historical pack context.

### Robust
Resilient to malformed input or bad prompts.

### Run-meta artifact
Non-canonical execution metadata.

### Rule
Normative invariant.

## S

### Safe mode
Restricted execution profile.

### Save
Persisted UniverseState snapshot.

### ScenarioSpec
Initial condition declaration for SessionSpec.

### SecureX
Security enforcement subsystem.

### Server
Authoritative multiplayer runtime.

### Session boundary
Explicit restart boundary between ExperienceProfiles.

### SessionSpec
Runnable configuration of universe and experience.

### Shard
SRZ partition.

### Shard boundary
SRZ demarcation.

### Simulation tick
Deterministic simulation update cycle.

### Softcore
Default survival LawProfile.

### Space
Spatial domain of simulation.

### Spectator
ExperienceProfile allowing non-mutating view in multiplayer.

### SRZ
Simulation Responsibility Zone.

### STRICT
Structural verification profile.

### Suite
Test grouping.

### Supported
Actively maintained and compatible.

## T

### Tag
Version control marker.

### Target
Build or execution objective.

### Test
Verification case.

### TestX
Deterministic runtime verification subsystem.

### Thread-count invariance
Deterministic behavior independent of thread count.

### Time
Simulation temporal dimension.

### Tool
Non-runtime utility under `tools/`.

### Toy
Non-production experimental artifact.

### Transition Contract
Explicit rule governing ExperienceProfile switching.

### Truth
Authoritative simulation state.

### TruthModel
Canonical state representation.

### TUI
Text User Interface.

## U

### UI
User Interface.

### Unit
Standardized measurement.

### Universe
Complete causal graph governed by UniverseIdentity.

### UniverseIdentity
Immutable root identity configuration.

### UniverseState
Mutable state at given simulation time.

### Unsupported
Not guaranteed compatible.

### Unsigned
Pack lacking SecureX signature.

### UX
User Experience.

## V

### Version
Semantic identifier for compatibility.

### Vintage
Historical content pack context.

## Deprecated Terms
- Legacy mode-flag identifiers (`*_mode`) in runtime code.
- Ad hoc privilege flags outside `AuthorityContext`.
- Non-registry "sandbox" or "god" labels.

## Reserved Words
Deterministic, Law, Authority, Lens, Canonical, Identity, Collapse, Expand, Macro, Micro, Process, Refusal.

End of Glossary v1.0.0.

