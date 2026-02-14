Status: DRAFT
Version: 1.0.0-draft
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Compatibility: Constrained by `docs/canon/constitution_v1.md` v1.0.0 and `docs/canon/glossary_v1.md` v1.0.0.

# Milestone: Lab Galaxy Navigation Build

## Purpose
Define the first lab-facing milestone for galaxy-scale navigation primitives without implementing runtime features yet.
This milestone is documentation and substrate focused.

## Scope (In)
- Canonical contracts and architecture stubs required for future Lab Galaxy work.
- Session/profile/lens/refusal contract shaping for navigation-centric flows.
- Determinism, SRZ, and compatibility guardrails for future navigation features.
- Skill templates that keep later implementation tasks constrained to canon.

## Out of Scope
- Runtime movement systems, pathfinding, UI rendering, or simulation logic changes.
- New executable components in `engine/`, `game/`, `client/`, or `server/`.
- Non-deterministic experimentation paths, mode flags, or bypass switches.
- One-off prototype branches not tied to pack/profile/contract systems.

## Non-Negotiable Invariants
- No mode flags; profile-driven composition only.
- Process-only mutation for any future state change.
- Observer/Renderer/Truth separation.
- Pack-driven integration and registry-declared capability resolution.
- Deterministic replay/hash equivalence and thread-count invariance.
- Schema evolution through CompatX-compatible migration/refusal contracts.

## Success Criteria
1. Canonical substrate docs exist and are cross-referenced.
2. Required contract and architecture skeletons define field shape, invariants, examples, and TODOs.
3. Root `AGENTS.md` encodes binding development behavior.
4. Skill templates exist for repeatable repo-safe execution patterns.
5. `tools/xstack/run fast` executes without control-substrate refusal.

## Done Criteria
1. All required directories and files exist at requested paths.
2. Every new doc includes:
   - version identifier
   - compatibility notice
   - explicit invariants
   - short example
   - TODO markers
   - cross-reference to canon/glossary
3. No runtime feature implementation is introduced.
4. Output includes a created-file summary with residual TODOs.

## Future Task Invocation
Use the following prompt frame for subsequent milestone tasks:

```text
Milestone: Lab Galaxy Navigation Build
Subtask:
Goal:
Touched Paths:
Must-Respect Invariants:
Required Contracts:
Required Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Out-of-Scope:
```

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/MODES_AS_PROFILES.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SRZ_MODEL.md`
- `docs/governance/COMPATX_MODEL.md`

## TODO
- Replace draft deliverable sequencing with dated release checkpoints.
- Add explicit fixture IDs once TestX navigation fixtures are proposed.
- Link acceptance gates to concrete `tests/` paths when they exist.

