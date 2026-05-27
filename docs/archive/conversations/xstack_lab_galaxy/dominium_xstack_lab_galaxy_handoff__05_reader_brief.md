# Reader Brief — Dominium XStack Lab Galaxy Handoff

## What This Chat Was About

This chat was about preserving and continuing work on Dominium / Domino, a deterministic universe simulation/game project, and XStack, a portable agentic development/governance suite. The chat began from a long history of planning and frustration with agentic development failures, especially gates that stopped work instead of fixing mechanical problems. It produced a robust doctrine: no hardcoded modes, process-only mutation, deterministic replay, TruthModel → PerceivedModel → RenderModel separation, pack-driven integration, and XStack as removable development tooling rather than runtime dependency.

A later uploaded transcript records a 13-prompt run in a new chat that reportedly implemented a Lab Galaxy deterministic substrate: canonical docs/schemas, pack system, registry compile/lockfile/cache, modular tools/xstack runner, session boot, observation kernel, lab camera/time processes, astronomy/Earth packs, descriptor-driven tool UI, interest regions, SRZ scheduling, deterministic packaging, setup/launcher, and 10 thematic commits. The user explicitly said they are not sure what was actually done and need completion/accuracy/consistency verification.

The future assistant should treat this report as continuity context, not as verified repo truth.

## Most Important Things to Know

- Verify the repository before trusting the transcript.
- XStack must be portable and removable.
- Runtime must not depend on tools/xstack.
- No mode flags: use LawProfile / ExperienceProfile / ParameterBundle.
- All mutation must happen through Processes.
- Renderer/UI must not access TruthModel.
- Packs must be data-only.
- Registry compile and lockfile enforce deterministic integration.
- Local verification should be fast, cached, sharded.
- Run-meta should not dirty tracked files except explicit snapshots.
- Lab Galaxy milestone is reported complete but must be audited.
- Survival is planned but not implemented as the main 13-prompt result.
- Survival default should be diegetic-only: no non-diegetic HUD/freecam/console.
- Future realism should be packs/solvers/budgets, not global micro-sim.

## Active Plans or Workstreams

- Verify 13-prompt Lab Galaxy implementation.
- Reconcile XStack entrypoints and artifact policy.
- Preserve runtime/XStack boundary.
- Possibly proceed to Survival Vertical Slice after audit.
- Preserve future domain/realism extensibility.

## Decisions Already Made

- Profiles, not modes.
- Process-only mutation.
- Truth/Perceived/Render separation.
- XStack removable.
- Mechanical failures remediated.
- Packs data-only and compiled into registries.
- Deterministic packaging and lockfile enforcement.

## Pending Tasks

- Run git status/log.
- Run tools/xstack/run fast.
- Audit 13 prompt deliverables.
- Verify XStack removability.
- Inspect .gitignore and docs/audit tracking.
- Decide push/rebase status.
- Decide next feature focus.

## Open Questions

- Is tools/xstack/run now canonical over gate.py?
- Are docs/audit artifacts tracked intentionally?
- Are all 13 prompts truly complete?
- Is Lab Galaxy interactive or mainly headless?
- Is survival next?

## Files / Artifacts / Prompts to Preserve

- transcript.txt
- AGENTS.md
- docs/canon/constitution_v1.md
- docs/canon/glossary_v1.md
- docs/roadmap/milestone_lab_galaxy.md
- tools/xstack/run
- tools/setup/build
- tools/launcher/launch
- packs/
- bundles/bundle.base.lab
- schemas/
- tools/xstack/sessionx
- docs/architecture/
- 10 reported commits

## What to Verify Before Acting

- Actual git state.
- Commit list and push status.
- XStack command path.
- Runtime no-XStack imports.
- Run-meta tracked files.
- Fast/strict validation.
- Prompt-by-prompt file existence.

## Best Next Step

Run a repository verification and completion audit against the 13-prompt transcript before writing any new feature prompt.
