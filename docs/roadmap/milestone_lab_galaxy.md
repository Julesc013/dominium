Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
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
- Bootable out-of-game session path (SessionSpec create -> lock -> boot -> run-meta -> shutdown).
- Lab profile packs load through registries (`profile.lab.developer`, `law.lab.unrestricted`).
- Process-driven free camera + time control intent path with deterministic replay anchors.
- Pack-driven astronomy/site indices for Milky Way -> Sol -> Earth navigation targets.
- Deterministic teleport-by-`object_id` and teleport-by-`site_id` path with replay checks.
- In-game lab tool UI windows (navigator, go-to, site browser, inspector, time control, process/refusal log).
- Continuous traversal with deterministic interest-region activation and macro/micro switching under explicit budget/fidelity policies.
- SRZ-ready deterministic scheduling (`read -> propose -> resolve -> commit`) with intent envelopes and hash anchors.
- Deterministic dist packaging and launcher lockfile enforcement for reproducible lab builds.

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
6. Deterministic SessionSpec creator and minimal headless boot/shutdown path execute for `bundle.base.lab`.
7. Process-driven freecam + time control works deterministically in headless script replay.
8. Teleport to all compiled astronomy objects/sites replays with identical deterministic hash anchors.
9. Descriptor-driven tool UI loads from `ui.registry` and emits deterministic process intents from PerceivedModel bindings.
10. Region management tick yields deterministic ROI/fidelity transitions with budget enforcement and conservation checks.
11. SRZ scheduler emits deterministic per-tick/checkpoint/composite hashes and remains worker-count invariant in STRICT.
12. Deterministic setup/launcher pipeline reproduces identical dist content hashes and final composite hash anchors.

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
5. Boot checkpoint complete:
   - `tools/xstack/session_create` generates schema-valid canonical save artifacts.
   - `tools/xstack/session_boot` emits deterministic run-meta under `saves/<save_id>/run_meta/`.
6. Lab interaction checkpoint complete:
   - `tools/xstack/session_script_run` replays camera/time intents with deterministic state hash anchors.
   - authority/law gating refusals are deterministic and contract-compliant.
7. Astronomy checkpoint complete:
   - `astronomy.catalog.index` and `site.registry.index` compile deterministically from packs only.
   - teleport by `target_object_id` and `target_site_id` is deterministic and refusal-contract compliant.
8. Tool UI checkpoint complete:
   - navigator/go-to/site browser/time/log/inspector windows compile from pack descriptors.
   - UI action dispatch mutates state only via process runtime and surfaces deterministic refusal logs.
9. Continuous traversal checkpoint complete:
   - `process.region_management_tick` deterministically updates `interest_regions`, `macro_capsules`, and `micro_regions`.
   - policy-driven degrade/cap or refusal behavior is reproducible across runs.
   - conservation checks and traversal hash anchors are replay-stable.
10. SRZ checkpoint complete:
   - `schemas/srz_shard.schema.json` and `schemas/intent_envelope.schema.json` validate in CompatX.
   - `tools/xstack/session_script_run` executes via SRZ phase pipeline and emits deterministic hash anchors.
   - `tools/xstack/srz_status` reports `shard.0` ownership and last hash anchor deterministically.
11. Packaging checkpoint complete:
   - `tools/setup/build --bundle bundle.base.lab --out dist` produces deterministic `manifest.json` and `lockfile.json`.
   - `tools/launcher/launch run --dist dist --session ...` enforces lockfile compatibility.
   - repeated build + launch traversal yields identical final composite hash anchors.

## Milestone Completion Checklist
- [x] Boot path
- [x] Lab profile
- [x] Astronomy packs
- [x] Tool UI
- [x] ROI/macro capsules
- [x] SRZ-ready scheduling
- [x] Deterministic packaging
- [x] Reproducible composite hash

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
- `docs/architecture/deterministic_packaging.md`
- `docs/architecture/setup_and_launcher.md`
- `docs/governance/COMPATX_MODEL.md`

## TODO
- Replace draft deliverable sequencing with dated release checkpoints.
- Add explicit fixture IDs once TestX navigation fixtures are proposed.
- Link acceptance gates to concrete `tests/` paths when they exist.
