# Reader Brief — Dominium/Domino Engine Refactor Prompts

## What This Chat Was About

This chat designed and organized a major deterministic-engine refactor for Dominium/Domino. The user established that the Domino engine must remain ISO C89, deterministic, fixed-point where determinism matters, free of OS/UI/rendering/platform APIs, and free of hardcoded gameplay semantics. Dominium remains portable C++98 UI/tools only. The chat started with advanced simulation systems, moved into agents/life/ecology, generalized performance and extensibility methods across the whole engine, added heavy infrastructure/building optimization, generalized Interstellar/Wargames DLC needs into core primitives, integrated a sister-chat prompt requiring arbitrary 3D placement and TRANS/STRUCT/DECOR systems, and finally produced a 14-prompt Codex implementation roadmap plus a documentation validation prompt.

The most important architecture pattern is: generic engine primitives, not game semantics. Systems communicate through typed packets, fields, events, messages, observations, intents, actions, deltas, ports, probes, and canonical graphs. Mutation happens through sorted delta commit. Heavy work is budgeted and deferred deterministically. Large-scale simulation uses R0/R1/R2/R3 representations with interest volumes and accumulators. Placement uses fixed-point pose plus parametric anchors; grids are UI-only; baked geometry is never authoritative. TRANS uses corridors with cross-section slots for co-location. STRUCT uses parametric authoring and compiled occupancy/enclosure/surface/support/carrier artifacts. DECOR is host-agnostic rulepacks plus manual overrides. Space/war features are generalized as domains, frame graph, propagators, observer contexts, beliefs, visibility, and comms.

No repository was inspected and no code was implemented in this chat. The prompts are planning artifacts until executed or adapted against the actual repo.

## Most Important Things to Know

- Domino Engine = C89, deterministic, fixed-point, no platform/UI/rendering APIs.
- Dominium = portable C++98 UI/tools/visualization only.
- No hardcoded gameplay semantics.
- All data/commands are TLV-versioned.
- Mutation through sorted delta commit.
- Bounded work with deterministic carryover queues.
- R0/R1/R2/R3 representation ladder is engine-wide.
- Agents are composition, not inheritance.
- Behavior pipeline: sensors → observations → minds/controllers → intents → actions → deltas.
- Plants/wildlife can be fields/populations and promoted when relevant.
- No global grid dependency in engine logic.
- All placement uses pose + parametric anchor.
- No baked geometry as source of truth.
- TRANS co-location uses cross-section slots.
- STRUCT/DECOR are authoring-plus-derived-cache systems.
- Space/war needs are generalized into domains/knowledge/comms primitives.
- A 14-prompt Codex implementation roadmap exists.
- VM-only vs native plugin policy is unresolved.
- Exact Q-format table is unresolved.
- Repository structure/build system must be verified.

## Active Plans or Workstreams

- WORKSTREAM-01 — Dominium/Domino deterministic engine architecture
- WORKSTREAM-02 — Advanced physics and simulation stack
- WORKSTREAM-03 — Agents, actors, life, ecology, and behavior
- WORKSTREAM-04 — Engine-wide extensibility, modularity, and performance methodology
- WORKSTREAM-05 — Custom buildings and infrastructure at scale
- WORKSTREAM-06 — Generalized Interstellar/Wargames core primitives
- WORKSTREAM-07 — Arbitrary placement and TRANS/STRUCT/DECOR spatial primitives
- WORKSTREAM-08 — Master Codex prompt implementation roadmap
- WORKSTREAM-09 — Documentation validation and normalization

## Decisions Already Made

- Hard engine/layer constraints are non-negotiable.
- Use typed IO, delta commit, fields/events/messages, budgets, LOD, graphs, and replay hashes.
- Use pose+anchors and no baked geometry for placement.
- Use TRANS slots for corridor co-location.
- Use STRUCT/DECOR authoring vs compiled artifacts.
- Generalize DLC requirements into core primitives.

## Pending Tasks

- Inspect repository structure and build system.
- Run/adapt Codex Prompts 1–14 in sequence.
- Run the documentation validation prompt.
- Decide VM-only versus native plugins.
- Define exact Q-format table.
- Generate detailed physics subsystem prompts later.

## Open Questions

- VM-only vs native plugins?
- Exact Q formats?
- Actual repository/build layout?
- Existing TLV/scheduler/graph/BUILD/TRANS/STRUCT/DECOR state?
- Rotation representation for pose/frame transforms?
- How derived caches should be hashed?

## Files / Artifacts / Prompts to Preserve

- The 14 Codex prompts.
- Documentation validation prompt.
- Sister GPT-5.1 requirements prompt.
- Maximum-fidelity context transfer packet.
- This report package.

## What to Verify Before Acting

- Repository paths and build system.
- Existing TLV/res layer.
- Existing deterministic scheduler, if any.
- Existing BUILD/TRANS/STRUCT/DECOR assumptions.
- Whether any engine code uses floats, unordered containers, grid-locked logic, raw memory hashing, or platform APIs.

## Best Next Step

Inspect the repository, then run or adapt CODEX PROMPT 1. Do not execute later prompts until Prompt 1 establishes specs, invariants, and scaffolding or until repository reality is mapped.
