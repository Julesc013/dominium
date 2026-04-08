Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: authoritative phased migration and rollback packet for later relayout execution prompts; downstream of stronger canon, the Omega0 constraint packet, the Omega1 topology reality map, the Omega2 coupling-risk packet, the Omega0 option packet, and the Omega1 preferred-target packet
Replacement Target: later explicit relayout-execution checkpoint or migration-plan replacement only after new baseline-hardening evidence and follow-up approval
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `data/repo/repo_non_negotiables_and_current_reality.json`, `docs/repo/REPO_TOPOLOGY_PATHS_AND_OWNERSHIP_REALITY_MAP.md`, `data/repo/repo_topology_paths_and_ownership_reality_map.json`, `docs/repo/REPO_COUPLING_DRIFT_AND_RELAYOUT_RISK_ANALYSIS.md`, `data/repo/repo_coupling_drift_and_relayout_risk_analysis.json`, `docs/repo/REPO_TARGET_TOPOLOGY_OPTIONS_AND_COMPARISON.md`, `data/repo/repo_target_topology_options_and_comparison.json`, `docs/repo/REPO_AUTHORITATIVE_BOUNDARY_MODEL_AND_PREFERRED_TARGET.md`, `data/repo/repo_authoritative_boundary_model_and_preferred_target.json`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `appshell/paths/virtual_paths.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/runner.py`, `tools/xstack/registry_compile/constants.py`, `tools/import_bridge.py`, `runtime/process_spawn.py`, `server/server_main.py`, `release/release_manifest_engine.py`

# Repo Phased Migration, Shims, Validation, And Rollback

## A. Purpose And Scope

This artifact defines the phased migration strategy from the current live repo topology to the preferred conceptual target while preserving the canonical playable-baseline path and keeping rollback possible at every serious step.

It exists because the series now has all prerequisite packets:

- Omega0 froze what must not break.
- Omega1 mapped the live roots, path contracts, and ownership reality.
- Omega2 ranked coupling strength, drift, shim need, and relayout risk.
- Omega0 design bounded the plausible topology options.
- Omega1 design selected the preferred target and froze the authoritative boundary model.

What remained undecided after those packets was the execution discipline:

- which phases later relayout prompts may actually use
- which shim classes are appropriate for which kinds of moves
- which migration slices are safe early versus late
- which validation gates and rollback thresholds must guard each phase

Its relationship to the canonical playable-baseline priority is direct:

- the baseline path remains the top migration-protection constraint
- any slice that threatens `verify`, `FAST`, launcher/setup shells, SessionX create/boot, local loopback authority, or `saves/<save_id>` assumptions must be sequenced late and behind strict rollback gates
- no physical relayout is authorized by this artifact

This is a migration design packet, not a relayout execution prompt and not a feature prompt.

For later repo-structure work, the direct answers are:

- What migration phases should be used:
  Section C.
- What shim classes are likely required:
  Section D.
- What the safest first migration slice is:
  Section F.
- What validation gates must pass after each phase:
  Section G.
- What rollback triggers and stop conditions must exist:
  Section H.
- What prompt this enables next:
  the final pre-relayout execution decision or an actual first-slice execution prompt, depending on human choice.

## B. Migration-Planning Method

The migration design is phase-first, shim-aware, and rollback-biased.

### How Phases Are Chosen

Phases are chosen by the strongest shared risk boundary rather than by desired neatness.

The ordering principle is:

1. no-move normalization before any physical change
2. no phase that touches baseline-critical seams before one repeatable repo-local playable baseline exists
3. low-coupling and wrapper-only movement before mixed or critical surfaces
4. shim-backed changes before shim retirement

### How Shim Need Is Judged

Shim need is judged from the Omega2 risk packet and the live seam files.

A shim is presumed necessary when:

- a slice changes a path that current code or scripts still resolve literally
- a slice changes command or entrypoint precedence while old invocations must remain valid
- a slice changes report, manifest, registry, or session artifact locations that existing consumers still read
- a slice touches a mixed host such as `tools/`, `docs/audit/`, `data/audit/`, or control-plane roots already consumed by launcher/setup shells

### How Validation Gates Are Selected

Validation gates are selected from Omega0 survival rules plus the audit-backed baseline path:

- `cmake --preset verify`, `cmake --build --preset verify`, and `ctest --preset verify` where build or wrapper surfaces are affected
- `python tools/validation/tool_run_validation.py --profile FAST` at minimum after every slice
- launcher/setup AppShell health whenever product shells, release/trust, or virtual-root behavior is touched
- SessionX create/boot, local loopback authority boot, and save/load smoke whenever session, local authority, or generated-intermediate contracts are touched
- selected `TestX` or `CTest` smoke whenever a phase changes proof surfaces or baseline-adjacent runtime seams

### How Rollback Boundaries Are Chosen

Rollback boundaries are chosen around any slice that could invalidate one of the following:

- the canonical build lane
- the canonical validation lane
- the Python/AppShell launcher/setup shells
- the SessionX create/boot path
- the local loopback-authoritative playable path
- the current save/load assumptions

Every slice must therefore be small enough that its compatibility shims and previous path behavior can be restored as one unit.

### How First-Slice Safety Is Judged

The safest first slice must:

- avoid moving files
- avoid changing imports, includes, or runtime path logic
- avoid touching Omega2 `do_not_move_yet` surfaces directly
- reduce ambiguity or drift in a way that later execution prompts can build on
- prove that the migration series can start without destabilizing the baseline path

## C. Migration Phase Model

### `MP-0 - Pre-Baseline No-Move Contract Hardening`

- What belongs here:
  authoritative path and wrapper-precedence normalization, drift reduction in derived docs and mirrors, migration slice manifests, boundary labels, and compatibility planning artifacts that do not change runtime behavior.
- What must not happen here:
  file moves, root renames, import changes, path-resolution changes, session semantics changes, or local authority changes.
- Entry requirements:
  the preferred-target packet exists and the current protected surfaces are known.

### `MP-1 - Post-Baseline Entrypoint And Path Normalization`

- What belongs here:
  wrapper-command shims, path-authority bridges, canonical entrypoint precedence cleanup, virtual-root alias planning, and other no-move compatibility mechanisms that make later movement survivable.
- What must not happen here:
  physical movement of `appshell/`, launcher/setup Python shells, SessionX create/boot surfaces, or the local authority cluster.
- Entry requirements:
  one repeatable repo-local playable baseline exists, `FAST` is green, and an agreed local smoke slice is passing.

### `MP-2 - Safe Low-Risk Structural Relayout`

- What belongs here:
  wrapper-only native GUI/TUI leaves, clearly low-coupling support leaves, and carefully scoped derived/report leaves whose consumers can be preserved easily.
- What must not happen here:
  movement of AppShell, SessionX, local authority, save-root contracts, or split-root ownership surfaces.
- Entry requirements:
  `MP-1` is green, the shims needed for affected callers are defined, and rollback has been rehearsed for the slice.

### `MP-3 - Shim-Backed Mixed-Root Migration`

- What belongs here:
  mixed proof and tooling hosts, validation/report path normalization, and control-plane boundary cleanup where launcher/setup and validation consumers still need compatibility aliases.
- What must not happen here:
  direct movement of baseline-critical product-shell or local-authority seams without already-proven shims.
- Entry requirements:
  `MP-2` is green, shim coverage exists, and the baseline remains repeatable after the earlier slices.

### `MP-4 - Late Baseline-Adjacent Structural Normalization`

- What belongs here:
  session artifact location bridges, generated-intermediate normalization, and only then any structural cleanup around baseline-adjacent product-shell or local-authority seams if still needed.
- What must not happen here:
  split-root convergence by convenience, extraction-shaped changes, or simultaneous movement of multiple critical path families.
- Entry requirements:
  repeatable local loopback boot, one save/load smoke, fresh `FAST`, and selected `TestX` or `CTest` smoke after earlier phases.

### `MP-5 - Shim Retirement And Cleanup`

- What belongs here:
  removing temporary path aliases, wrapper-command shims, import/include aliases, report redirects, and compatibility bridges once no surviving consumer depends on them.
- What must not happen here:
  bundling unrelated cleanup, feature work, or new topology experiments into shim removal.
- Entry requirements:
  all migrated consumers are proven on the new paths and at least one full validation cycle has passed without relying on the old shims.

### Deferred Outside The Canonical Phase Model

The following are not part of the normal early-to-mid migration path and must remain deferred until separate review:

- `schema/` versus `schemas/` convergence
- `packs/` versus `data/packs/` convergence
- any extraction-shaped change tied to future AIDE ambitions

## D. Compatibility Shim Model

### `SHIM-PATH - Path Resolution Shim`

- What problem it solves:
  preserves callers that still resolve old relative or absolute paths when a path owner changes later.
- When it is appropriate:
  after a path move or re-rooting of a non-canonical surface where older callers still need a bounded transition window.
- When it is dangerous:
  when used to hide baseline-critical bugs such as `server/server_main.py` repo-root misresolution or to preserve two conflicting authorities silently.
- When it should be removed:
  once all known callers resolve the new path directly and old-path usage is proven absent.

### `SHIM-IMPORT - Import / Include Alias Shim`

- What problem it solves:
  preserves Python imports, C/C++ include lookups, or tool module references while files are rehomed later.
- When it is appropriate:
  for low-risk leaf moves or controlled mixed-root decomposition where callers can be migrated incrementally.
- When it is dangerous:
  when it hides ownership drift indefinitely or makes stale structure look canonical; `tools/import_bridge.py` is already a cautionary example.
- When it should be removed:
  once direct imports/includes have been updated and the old alias path no longer has consumers.

### `SHIM-CMD - Wrapper Command Shim`

- What problem it solves:
  preserves user or tool-facing commands while canonical entrypoint precedence changes under the hood.
- When it is appropriate:
  for launcher/setup/runtime/session wrappers and later canonical-entrypoint convergence.
- When it is dangerous:
  when it creates two “official” commands at once or deepens startup ambiguity.
- When it should be removed:
  once one canonical entrypoint is proven and old wrapper invocations are intentionally retired.

### `SHIM-LOCATION - Manifest / Profile / Session Location Bridge`

- What problem it solves:
  preserves pack/profile/lock/template/registry/session/generated-output lookup when a slice changes where these files live.
- When it is appropriate:
  for later movement of validation/report roots, release manifests, or session artifact locations after explicit mapping exists.
- When it is dangerous:
  when it writes to multiple authorities, hides save-root disagreement, or lets generated outputs become silent sources of truth.
- When it should be removed:
  after a single canonical location is proven by one repeatable start/save/load/resume cycle and no caller requires the old location.

### `SHIM-VROOT - Virtual-Root Alias Bridge`

- What problem it solves:
  preserves repo-local versus installed-mode discovery through `appshell/paths/virtual_paths.py` when supported roots move conceptually or physically later.
- When it is appropriate:
  for installed-versus-repo-local boundary cleanup where the current VROOT contract can absorb bounded aliasing.
- When it is dangerous:
  when new aliases are added without ownership review or when VROOTs start masking unresolved canonicality questions.
- When it should be removed:
  once the virtual-root registry and callers agree on one stable layout without compatibility overrides.

### `SHIM-DOC - Documentation Redirect And Report Regeneration Shim`

- What problem it solves:
  preserves external references, machine-readable evidence paths, and derived docs while stale path vocabulary is cleaned up.
- When it is appropriate:
  for `docs/audit/`, `data/audit/`, and other derived/report families where consumers still expect older locations or names.
- When it is dangerous:
  when redirects are used to excuse stale runtime claims or when report outputs start being treated as canonical runtime truth.
- When it should be removed:
  once docs, reports, and machine-readable mirrors are regenerated on the new vocabulary and no old references are required.

## E. Concrete Migration Slices

### `RMS-001 - No-Move Path Authority And Wrapper-Precedence Normalization`

- Conceptual goal:
  normalize authoritative path vocabulary, wrapper precedence, and preferred-target labels in docs and mirrors without moving files or changing runtime behavior.
- Likely affected roots:
  `docs/repo/`, `docs/audit/`, `data/repo/`, and later derived doc/report mirrors that still carry stale `src/...` vocabulary or wrapper overclaims.
- Safe to do early:
  yes
- Likely needs shims:
  no runtime shims; only documentation redirect planning if later report paths change
- Validation gates after it:
  JSON parse, markdown/JSON consistency, `git diff --check`, and `python tools/validation/tool_run_validation.py --profile FAST`
- Rollback trigger:
  any increase in source-of-truth ambiguity, contradictory canonical-path claims, or unexpected `FAST` regression
- Does it threaten the canonical baseline path:
  no; this slice is ambiguity-reducing only

### `RMS-002 - Canonical Entrypoint And Path Bridge Introduction`

- Conceptual goal:
  introduce no-move wrapper-command and path-authority bridges so canonical launcher/setup/session entrypoints can survive later movement.
- Likely affected roots:
  `tools/launcher/`, `tools/setup/`, `tools/mvp/runtime_entry.py`, `appshell/paths/`, and selected session-facing wrapper surfaces
- Safe to do early:
  no; only after one repeatable repo-local playable baseline exists or as a tightly coordinated baseline-hardening follow-up
- Likely needs shims:
  yes
- Validation gates after it:
  `FAST`, launcher/setup AppShell health, SessionX create/boot health, and one local loopback boot smoke
- Rollback trigger:
  startup ambiguity increases, launcher/setup health regresses, session boot path behavior changes unexpectedly, or local loopback boot fails
- Does it threaten the canonical baseline path:
  yes, if executed too early or without one canonical precedence model

### `RMS-003 - Wrapper-Only Native Leaf Isolation`

- Conceptual goal:
  isolate or rehome low-risk native GUI/TUI wrapper leaves and related thin wrapper assets without altering the stronger Python/AppShell shells.
- Likely affected roots:
  `launcher/gui/`, `launcher/tui/`, `setup/gui/`, `setup/tui/`, and relevant wrapper-only build scaffolding
- Safe to do early:
  yes, but only after `RMS-001` and after canonical wrapper precedence is documented clearly
- Likely needs shims:
  minimal; at most bounded build or wrapper aliases
- Validation gates after it:
  `cmake --preset verify`, `cmake --build --preset verify`, selected launcher/setup wrapper smoke, and `FAST`
- Rollback trigger:
  verify build fails, wrapper targets disappear, or launcher/setup packaging expectations regress
- Does it threaten the canonical baseline path:
  low risk

### `RMS-004 - Validation And Audit Surface Normalization`

- Conceptual goal:
  separate proof tooling from emitted reports using compatibility aliases and report redirects so validation ownership becomes clearer without breaking consumers.
- Likely affected roots:
  `validation/`, `tools/validation/`, `tools/import_bridge.py`, `docs/audit/`, and `data/audit/`
- Safe to do early:
  no; it should follow the first low-risk slice because the proof surface is broad and heavily consumed
- Likely needs shims:
  yes
- Validation gates after it:
  `FAST`, `python tools/xstack/testx_all.py --profile FAST`, report-path integrity checks, and selected `ctest --preset verify` smoke if build or wrapper surfaces were touched
- Rollback trigger:
  report outputs move unexpectedly, proof consumers break, old-path compatibility fails, or `FAST` findings change unexpectedly
- Does it threaten the canonical baseline path:
  moderate risk because the baseline relies on honest proof and evidence surfaces

### `RMS-005 - Control-Plane Boundary Cleanup`

- Conceptual goal:
  align release, trust, install-discovery, and manifest-resolution surfaces to the preferred boundary model while keeping launcher/setup shells stable.
- Likely affected roots:
  `release/`, `security/trust/`, `repo/`, `tools/setup/`, `tools/launcher/`, `dist/`, and related registries or manifests
- Safe to do early:
  no
- Likely needs shims:
  yes
- Validation gates after it:
  `FAST`, launcher/setup AppShell health, release-manifest load smoke, trust verification smoke, and verify build/test if affected
- Rollback trigger:
  setup/launcher cannot discover installs or manifests, trust resolution regresses, or manifest path expectations diverge
- Does it threaten the canonical baseline path:
  moderate to high risk because the stronger shells already consume these surfaces directly

### `RMS-006 - Session Artifact And Generated-Output Bridge`

- Conceptual goal:
  bridge session create/boot/save/compile outputs so later structural normalization can happen without breaking `saves/`, `build/registries/`, or `build/lockfile.json` assumptions.
- Likely affected roots:
  `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`, `tools/xstack/registry_compile/constants.py`, `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`, `saves/`, `build/registries/`, and `build/lockfile.json`
- Safe to do early:
  no
- Likely needs shims:
  yes, critically
- Validation gates after it:
  `FAST`, SessionX create health, SessionX boot health, one local loopback authority boot, one save/load smoke, and selected `TestX` or `CTest` smoke
- Rollback trigger:
  save-root ambiguity persists or worsens, session boot cannot find artifacts, generated outputs drift, or local authority boot fails
- Does it threaten the canonical baseline path:
  yes, critically

### `RMS-007 - Local Authority And Product-Shell Seam Normalization`

- Conceptual goal:
  only after earlier phases are green, align AppShell, product shells, and the local authority seam to the preferred boundary model without destabilizing canonical flows.
- Likely affected roots:
  `appshell/`, `tools/launcher/`, `tools/setup/`, `client/local_server/`, `runtime/process_spawn.py`, `server/server_main.py`, and `server/net/loopback_transport.py`
- Safe to do early:
  no
- Likely needs shims:
  yes, critically
- Validation gates after it:
  verify build lane, `FAST`, launcher/setup health, SessionX create/boot health, one local loopback boot, one save/load smoke, and a selected playtest or `CTest` smoke slice
- Rollback trigger:
  any baseline-flow regression, repo-root math regression, supervision regression, or renewed ambiguity about the canonical entrypoint
- Does it threaten the canonical baseline path:
  yes, critically

### `RMS-008 - Deferred Split-Root Ownership Execution`

- Conceptual goal:
  only after separate ownership review and later evidence, execute any convergence decisions around `schema/` versus `schemas/` and `packs/` versus `data/packs/`
- Likely affected roots:
  `schema/`, `schemas/`, `packs/`, `data/packs/`, and related contract/docs surfaces
- Safe to do early:
  no
- Likely needs shims:
  yes
- Validation gates after it:
  `FAST`, schema and compatibility checks, pack verification, and explicit review-gate satisfaction
- Rollback trigger:
  any canonicality conflict, pack/schema validation drift, or unresolved review-gate condition
- Does it threaten the canonical baseline path:
  governance-critical and high risk, even if not immediately runtime-breaking

## F. Safest First Migration Slice

### Selected First Slice

- Safest-first migration slice:
  `RMS-001 - No-Move Path Authority And Wrapper-Precedence Normalization`
- Safety class:
  pre-baseline documentation-and-mirror normalization only; no runtime, import, include, or file-location change is permitted inside this slice

### Why This Slice Is First

`RMS-001` is first because it has the lowest combined structural and rollback risk while still proving something meaningful.

It is the safest first slice because:

- it moves no files
- it changes no imports, includes, or runtime path logic
- it does not touch Omega2 `do_not_move_yet` surfaces directly
- it reduces the exact ambiguity that later physical slices would otherwise amplify

### What It Proves

It proves that the migration series can begin by:

- reducing stale path and wrapper ambiguity
- aligning docs and machine-readable mirrors to the preferred target
- creating a sharper contract for later execution prompts about which roots are canonical, mixed, wrapper-only, derived, or protected

### What It Does Not Yet Attempt

It does not yet attempt:

- canonical playtest-path implementation
- launcher/setup/runtime/session shim implementation
- any root movement
- any save-root or repo-root bug fix
- any ownership-split convergence

## G. Validation Model Per Phase

### `MP-0`

- mandatory gates:
  JSON parse for touched mirrors, prose/mirror consistency, `git diff --check`, and `python tools/validation/tool_run_validation.py --profile FAST`

### `MP-1`

- mandatory gates:
  all `MP-0` gates plus launcher/setup AppShell health
- additionally required when session or entrypoint surfaces are touched:
  SessionX create health, SessionX boot health, and one local loopback boot smoke

### `MP-2`

- mandatory gates:
  all relevant `MP-1` gates plus `cmake --preset verify`, `cmake --build --preset verify`, and selected `ctest --preset verify` smoke when build or wrapper surfaces are affected

### `MP-3`

- mandatory gates:
  all relevant `MP-2` gates plus `python tools/xstack/testx_all.py --profile FAST`, validation/report path integrity checks, and any targeted alias-parity checks required by the slice

### `MP-4`

- mandatory gates:
  all relevant `MP-3` gates plus one repeatable local loopback-authority boot, one save/load smoke, and one selected playtest or `CTest` smoke slice tied to the affected seam

### `MP-5`

- mandatory gates:
  the same gates required by the last affected phase, plus proof that no live caller still depends on the retiring shim

### Always-Protected Checks

Regardless of phase, later execution prompts must keep these checks available whenever the affected surface intersects them:

- verify build path
- launcher/setup AppShell health
- SessionX create/boot health
- local loopback authority boot
- save/load smoke
- `FAST` validation
- selected `TestX` or `CTest` smoke justified by the touched seam

## H. Rollback Model

### Rollback Triggers

Rollback must trigger immediately when a slice causes any of the following:

- verify configure, build, or test regression
- `FAST` not returning `complete`
- launcher/setup AppShell health regression
- session create or boot regression
- local loopback authority boot failure
- save/load smoke failure
- canonical path ambiguity increasing rather than decreasing
- shims shadowing canonical roots or creating two simultaneous authorities

### Rollback Decision Thresholds

- For `MP-0` and low-risk `MP-2` slices:
  one blocking validation failure or one clear source-of-truth contradiction is enough to roll back the slice.
- For `MP-1`, `MP-3`, and `MP-4`:
  any regression in a baseline-critical flow is an immediate rollback condition, not a “fix forward” invitation inside the same slice.
- For repeated failures:
  two consecutive rollbacks on the same boundary band stop the migration series until the plan is reassessed.

### Rollback Evidence Required

Rollback decisions must preserve:

- before-and-after command outputs
- validation report identifiers or fingerprints
- smoke-test evidence for launcher/setup/session/loopback if run
- list of touched roots and touched path contracts
- explicit record of which shim or alias class was involved

### What Must Be Restorable

Every serious slice must leave the following restorable:

- previous canonical command lines
- previous path resolution behavior or the shims that preserve it
- report output locations
- session artifact discovery behavior
- manifest and trust lookup behavior
- build preset and wrapper behavior

### Stop Conditions For The Migration Series

Stop the migration series entirely and reassess if:

- the baseline path is no longer repeatable even after rollback
- the same protected seam rolls back twice
- a new same-tier authority conflict appears around split roots or canonicality
- a migration slice begins to pressure XStack/AIDE extraction or post-`Ζ` frontier work back into scope
- rollback cannot restore pre-slice behavior quickly and unambiguously

## I. Boundaries On Migration Freedom

### What Later Execution Prompts May Do

- execute one bounded migration slice at a time
- introduce the minimum shim class required by that slice
- perform only the validation gates required by the touched seam plus the minimum always-on gates
- roll back immediately when the thresholds in Section H are met

### What Later Execution Prompts Must Not Do

- combine migration with unrelated feature work
- move multiple high-risk boundary bands in one slice
- remove old paths or commands before the replacement plus shim is validated
- treat the preferred target as permission to migrate split-root ownership surfaces by convenience
- reopen XStack/AIDE extraction or internal `Ζ` realization work under migration language

### What Later Execution Prompts Must Validate First

Before any slice beyond `MP-0`, later prompts must confirm:

- the protected baseline path is still the governing priority
- the slice does not outrun the preferred-target boundary model
- rollback can restore the old behavior for the touched seam

### Surfaces That Remain Protected Until Later

- `appshell/`
- `tools/launcher/` and `tools/setup/`
- `client/local_server/`
- `runtime/process_spawn.py`
- `server/server_main.py`
- `server/net/loopback_transport.py`
- `tools/xstack/session_create.py`
- `tools/xstack/session_boot.py`
- `tools/xstack/sessionx/creator.py`
- `tools/xstack/sessionx/runner.py`
- repo-local `saves/`
- `build/registries/`
- `build/lockfile.json`
- `schema/` versus `schemas/`
- `packs/` versus `data/packs/`

## J. Anti-Patterns / Forbidden Migration Shapes

- moving baseline-critical roots in the first slice
- eliminating old paths before shims exist and are validated
- coupling structural movement with unrelated feature work
- using migration phases to reopen XStack/AIDE extraction or post-`Ζ` frontier work
- claiming “cleanup” while invalidating build, validation, session, or playtest flows
- treating compatibility bridges as permanent substitutes for real ownership cleanup
- letting doc/report movement outrun proof-consumer compatibility
- collapsing low-risk and high-risk slices into one generic “restructure” step

## K. Stability And Evolution

- Stability class:
  stable until a later prompt either executes the first slice or new baseline evidence changes the safe ordering materially.
- Later prompts expected to consume this artifact:
  final pre-relayout validation decision prompts, first-slice execution prompts, shim-implementation prompts, and rollback-aware relayout prompts.
- What must not change without explicit follow-up:
  the migration phase order, the designation of `RMS-001` as the safest first slice, the protected-surface list, and the rollback thresholds around baseline-critical flows.
