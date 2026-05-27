# Reader Brief — Dominium README Ports Determinism

## What This Chat Was About

This chat refined the Dominium / Domino root README and produced a maximum-fidelity handoff for future continuation. Dominium / Domino is described as a deterministic, integer-math, multi-platform simulation game and engine. Domino is the deterministic engine core; Dominium is the official game/runtime/tooling layer. The user pasted README versions, requested critique, asked for Codex prompts, pasted Codex outputs, and refined the result.

The most important change came from the user’s direct requirement that ports should not be stored in a separate directory or system, should work within the same structure, and should degrade gracefully without flowing upstream. The final README now says all platforms build from one unified source hierarchy, platform-specific behavior is expressed through thin shims, compile-time flags, and capability tables, and `/ports` contains only optional metadata/build configurations/capability descriptors with no code or behavior. This metadata-only `/ports` interpretation should be verified before formalizing directory specs.

The chat also clarified determinism rules: no floats in `/engine` or engine-controlled formats; non-authoritative tools/renderers may use floats only if they never feed back; RNG streams advance only during deterministic tick phases; tick phases are immutable; parallel commits must be deterministic; lockstep is canonical networking; build numbers/timestamps are diagnostic only; content-lock mismatches are fatal; and disk versions are immutable contracts.

## Most Important Things to Know

- User explicitly rejected separate port directories/systems.
- All platforms must share one source hierarchy.
- Reduced functionality must degrade locally through capability descriptors and not flow upstream.
- Final README keeps `/ports` only as metadata/build config/capability descriptors, but this may need confirmation.
- No engine/runtime source code or behavior may live in `/ports` if retained.
- Section 9 is normative for platform/render targets.
- Intro mentions OS/2 strata, but Section 9 omits OS/2; this is an unresolved contradiction.
- Full Domino engine targets 286-class-and-newer systems.
- CP/M-80/86 is tooling/limited frontends only, not complete world simulation.
- Floats are banned in authoritative engine/format paths, not in all tools/renderers.
- Lockstep is canonical networking; rollback/prediction must converge to lockstep.
- README is descriptive; `/docs/spec` files are normative.
- Codex previously introduced duplicate README content, so prompts must be tightly scoped.

## Active Plans or Workstreams

- WORKSTREAM-01: README architecture.
- WORKSTREAM-02: unified ports and capability-based degradation.
- WORKSTREAM-03: determinism contract.
- WORKSTREAM-04: data formats and save/content-lock contract.
- WORKSTREAM-05: future normative specs.
- WORKSTREAM-06: Codex prompt workflow.

## Decisions Already Made

- Domino = engine core; Dominium = game/runtime/tooling layer.
- Specs are normative; README is descriptive.
- 286+ full engine target; CP/M limited only.
- Unified source hierarchy for all platforms.
- No divergent port implementations.
- Capability-based graceful degradation.
- Lockstep is canonical.
- Disk versions immutable.
- `content.lock` mismatch fatal until reconciled.

## Pending Tasks

- Verify actual repo README against final pasted README.
- Resolve OS/2 matrix inconsistency.
- Confirm metadata-only `/ports` vs no `/ports`.
- Update `DIRECTORY_CONTRACT.md`.
- Create capability-system spec.
- Create determinism and data-format specs.

## Open Questions

- Should OS/2 be added to Section 9 or removed/qualified in intro?
- Does the user accept metadata-only `/ports`?
- Where exactly do platform shims live?
- What is the capability descriptor schema?
- What are exact RNG/hash/TLV algorithms?

## Files / Artifacts / Prompts to Preserve

- Final README pasted by user.
- User port requirement quote.
- First Codex prompt for README fixes.
- Second Codex prompt for unified ports.
- Cleanup Codex prompt.
- Previous Context Transfer Packet.
- References to `README.md`, `/docs/spec/DIRECTORY_CONTRACT.md`, `/docs/spec/MILESTONES.md`, `content.lock`.

## What to Verify Before Acting

- Actual repository state.
- `/ports` interpretation.
- OS/2 target status.
- Existence/content of referenced spec files.
- That no source code lives under `/ports` if retained.

## Best Next Step

Verify the actual repository README, then patch the OS/2 inconsistency. If moving into specs, confirm `/ports` semantics before editing `DIRECTORY_CONTRACT.md`.
