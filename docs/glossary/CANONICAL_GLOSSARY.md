Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Canonical Glossary (CONS-0)

Status: binding.
Scope: canonical vocabulary for architecture, simulation, and planning.

## Engine
Definition: The deterministic substrate and runtime mechanisms that enforce
invariants and execute authoritative processes.
Not: Game rules, content, or presentation layers.
Common confusions: Engine vs game; the engine defines mechanisms, the game
defines meaning.

## Game
Definition: The authoritative rule set and meaning layered on engine public
APIs.
Not: The engine or its mechanisms.
Common confusions: Game vs content; content supplies data, the game defines
rules.

## Content
Definition: Data-only definitions delivered via packs.
Not: Executable logic or runtime code.
Common confusions: Content vs configuration; content is validated data, not
engine behavior.

## Pack
Definition: A versioned content bundle resolved by UPS and declaring
capabilities.
Not: A runtime module or executable.
Common confusions: Pack vs repository; packs are content artifacts, not source
trees.

## Capability
Definition: An explicit, additive permission required to attempt an action.
Not: Authority or a policy.
Common confusions: Capability vs authority; capability enables attempts,
authority results from law outcomes.

## Authority
Definition: Effective power derived from capabilities plus law outcomes and
authority tokens.
Not: Omnipotence or a bypass.
Common confusions: Authority vs capability; authority is contingent on law.

## Law
Definition: A rule governing existence or action, evaluated by the law kernel.
Not: A policy toggle or code shortcut.
Common confusions: Law vs policy; law admits or denies, policy constrains.

## Policy
Definition: A constraint on permitted action such as rate, scope, or window.
Not: Law and not a capability.
Common confusions: Policy vs mode; policy is a rule, mode selects policy sets.

## Mode
Definition: A declared operating context that selects which policies,
capabilities, and interfaces are active without changing law or invariants.
Not: A new law or a different simulation.
Common confusions: Mode vs policy; mode activates policies, policy constrains
actions.

## Process
Definition: A deterministic rule pipeline that produces authoritative outcomes
from admitted actions.
Not: A script, behavior tree, or ad hoc function.
Common confusions: Process vs action or event; actions are admitted, events are
scheduled effects.

## Field
Definition: An authoritative spatial dataset; maps and layers are derived
views.
Not: A texture, mesh, or UI overlay.
Common confusions: Field vs representation tier; fields are authoritative,
representations are derived.

## Agent
Definition: A persistent simulation entity that holds intent, acts through
processes under authority, and perceives via an epistemically bounded
projection.
Not: A behavior tree, script, or UI avatar.
Common confusions: Agent vs NPC; agents include non-human and institutional
actors.

## Institution
Definition: An agent representing a collective or organizational identity with
stable authority scope.
Not: A faction flag or UI-only grouping.
Common confusions: Institution vs group tag; institutions must have identity
and processes.

## Epistemic state
Definition: An agent's subjective knowledge state with explicit uncertainty,
provenance, and time scope.
Not: Objective truth.
Common confusions: Epistemic state vs world state; epistemics are observer
bounded.

## Knowledge artifact
Definition: An explicit data record of observation, inference, memory, or
measurement with provenance and confidence.
Not: Implied knowledge or objective state.
Common confusions: Knowledge artifact vs snapshot; artifacts feed subjective
views.

## WorldDefinition
Definition: A data artifact that declares foundational truth inputs and
constraints for refinement.
Not: A generator or runtime system.
Common confusions: WorldDefinition vs snapshot; definitions declare constraints,
snapshots record state.

## Template
Definition: A data pattern for parameterized content reuse that resolves to
concrete data.
Not: A process or executable logic.
Common confusions: Template vs process; templates produce data, processes
produce effects.

## Slice
Definition: A player-facing capability milestone.
Not: Coverage, era, or world fidelity.
Common confusions: Slice vs coverage; slices are about player capability.

## Coverage
Definition: A simulation representability goal describing what the engine can
model.
Not: A player mode or gameplay milestone.
Common confusions: Coverage vs slice; coverage is enforced by TESTX, not
runtime branching.

## Refusal
Definition: A law output that denies an action with explanation and audit.
Not: A silent failure or error.
Common confusions: Refusal vs error; refusal is a lawful outcome.

## Determinism
Definition: Authoritative simulation yields identical outcomes given identical
inputs and ordering rules.
Not: Realism or predictability in derived layers.
Common confusions: Determinism vs randomness; derived layers may vary without
affecting authority.

## Snapshot (objective)
Definition: The authoritative state record used for saves, replay, and audit.
Not: Observer-specific or derived.
Common confusions: Objective snapshot vs subjective snapshot.

## Snapshot (subjective)
Definition: A derived observer-specific view filtered by epistemic artifacts
and authority.
Not: Authoritative truth.
Common confusions: Subjective snapshot vs objective snapshot.

## Event
Definition: A scheduled state transition on ACT.
Not: A UI event or background tick.
Common confusions: Event vs process; processes emit events.

## History
Definition: The immutable, ordered record of authoritative events and outcomes
for a timeline.
Not: A mutable log or derived analytics.
Common confusions: History vs replay; replay is a view of history.

## Replay
Definition: A deterministic re-execution or view of history under defined replay
modes and permissions.
Not: A silent rewrite of history.
Common confusions: Replay vs fork; forks create new timelines.