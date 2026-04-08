Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: authoritative pre-relayout validation, decision, and packaging checkpoint for the completed repo-structure series; downstream of stronger canon, the six repo-structure packets, post-Zeta closure, ultra audit evidence, XStack/AIDE closure, and selected live implementation evidence
Replacement Target: later first-slice execution checkpoint or explicit replacement review after RMS-001 execution or new baseline-hardening evidence
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `data/repo/repo_non_negotiables_and_current_reality.json`, `docs/repo/REPO_TOPOLOGY_PATHS_AND_OWNERSHIP_REALITY_MAP.md`, `data/repo/repo_topology_paths_and_ownership_reality_map.json`, `docs/repo/REPO_COUPLING_DRIFT_AND_RELAYOUT_RISK_ANALYSIS.md`, `data/repo/repo_coupling_drift_and_relayout_risk_analysis.json`, `docs/repo/REPO_TARGET_TOPOLOGY_OPTIONS_AND_COMPARISON.md`, `data/repo/repo_target_topology_options_and_comparison.json`, `docs/repo/REPO_AUTHORITATIVE_BOUNDARY_MODEL_AND_PREFERRED_TARGET.md`, `data/repo/repo_authoritative_boundary_model_and_preferred_target.json`, `docs/repo/REPO_PHASED_MIGRATION_SHIMS_VALIDATION_AND_ROLLBACK.md`, `data/repo/repo_phased_migration_shims_validation_and_rollback.json`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `appshell/paths/virtual_paths.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/runner.py`, `tools/import_bridge.py`, `tools/validation/tool_run_validation.py`, `validation/validation_engine.py`, `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`, `client/local_server/local_server_controller.py`, `release/release_manifest_engine.py`, `CMakePresets.json`

# Checkpoint C Repo Mega Structure Review

## A. Purpose And Scope

This checkpoint validates the entire repo-structure discovery, design, and migration-planning series end to end and decides whether the repo now has enough evidence to begin relayout execution.

It evaluates:

- whether the repo-structure series is complete and decision-grade
- whether the preferred target remains justified
- whether the migration packet is safe enough to begin execution
- what the exact first migration slice should be
- what residual risks still constrain later relayout work

It does not:

- move files
- rename roots
- implement shims
- execute the first migration slice
- implement the canonical playtest path
- reopen internal `Ζ` or XStack/AIDE implementation work

This is the pre-relayout validation and decision checkpoint for the full repo-structure series.

## B. Current Decision State

- Checkpoint state:
  `pre-relayout validation and decision`
- Candidate next work under review:
  `RMS-001 - No-Move Path Authority And Wrapper-Precedence Normalization`
- Candidate extra clarification artifact:
  `none required if RMS-001 remains doc-and-mirror-only`

The decision in this checkpoint must therefore separate three different things cleanly:

- the series being complete enough to make a decision
- the preferred target being justified as a conceptual commitment
- actual relayout execution approval, which may still be narrower than the conceptual target

## C. Series-Completion Review

| Series family | Verdict | Why the packet is decision-grade now | Active caution |
| --- | --- | --- | --- |
| `REPO-DISCOVERY-Ω0` constraints and current reality | `complete` | It freezes what must not break, preserves baseline-first priority, and keeps verified / likely / blocked distinct. | None beyond the already-frozen blocker set. |
| `REPO-DISCOVERY-Ω1` topology, paths, and ownership reality | `complete` | It maps the live root families, ownership classes, path contracts, and baseline-critical clusters with implementation evidence. | Mixed roots remain intentionally mixed in the map; that is a feature, not a gap. |
| `REPO-DISCOVERY-Ω2` coupling, drift, and relayout risk | `complete` | It ranks safe-to-move, needs-shim, and do-not-move-yet surfaces clearly enough to constrain design and migration. | The packet proves that physical movement beyond the lightest slice is still high risk pre-baseline. |
| `REPO-DESIGN-Ω0` topology option generation and comparison | `complete` | It generated materially distinct options and discriminated among them honestly instead of collapsing them into aesthetic ties. | `TTO-002` remains a useful long-term reference, but not the selected target. |
| `REPO-DESIGN-Ω1` preferred target and authoritative boundary model | `complete with cautions` | It selected `PT-001 / TTO-001` for repo-grounded reasons and froze a usable boundary model for later migration planning. | The selection is conceptual only and does not authorize physical relayout on its own. |
| `REPO-MIGRATION-Ω0` phased migration, shims, validation, and rollback | `complete with cautions` | It defines phases, shim classes, concrete slices, validation gates, rollback thresholds, and the safest first slice. | Only `RMS-001` is safe pre-baseline; later phases remain gated on playable-baseline proof. |

Series-completion judgment:

- `yes`

The repo-structure series is complete and decision-grade.
It does not need another clarification packet before the first approved slice, because the safest first slice is itself a bounded clarification-and-normalization slice.

## D. Preferred-Target Review

Preferred-target under review:

- `PT-001`
- selected option: `TTO-001 - Stabilized Current-Root Federation`

Assessment:

- Does it preserve the baseline path:
  `yes`
- Is it grounded in repo reality:
  `yes`
- Is it compatible with the migration and risk findings:
  `yes`
- Is it still the best available target:
  `yes`

Why the preferred target remains justified:

- it best preserves the `verify` lane, `FAST` validation path, Python/AppShell launcher and setup shells, SessionX create/boot path, current `saves/<save_id>` assumptions, and the loopback-authoritative local path
- it matches the current live root federation and does not invent new physical owners that the code does not actually honor today
- it is the only option that aligns strongly with both extend-over-replace doctrine and XStack/AIDE non-interference
- it leaves mixed or split ownership surfaces visible instead of pretending they are already settled

Critical uncertainties that remain unresolved:

- one canonical repo-local playtest command still does not exist
- `server/server_main.py` repo-root resolution remains blocked truth
- `session_boot` and `sessionx/runner.py` still disagree about save-root generality
- launcher supervision remains fragile
- `schema/` versus `schemas/` and `packs/` versus `data/packs/` remain deferred ownership splits
- the authored MVP baseline trio and the live default bundle id still form an implementation-versus-guidance seam

Those uncertainties do not defeat the preferred target.
They only restrict what kind of execution can be approved next.

## E. First Migration-Slice Review

Proposed first slice:

- `RMS-001 - No-Move Path Authority And Wrapper-Precedence Normalization`

Decision:

- Is it really the safest first slice:
  `yes`
- Does it avoid baseline-critical breakage:
  `yes, if kept strictly doc-and-mirror-only`
- Does it require shims first:
  `no runtime shims`

Why `RMS-001` is the safest first slice:

- it moves no files
- it changes no imports, includes, or runtime path logic
- it does not touch Omega2 `do_not_move_yet` surfaces directly
- it targets exactly the drift that the audit and Omega2 packet identified: stale `src/...` path vocabulary, wrapper overclaims, and ambiguous path-authority narratives
- rollback is trivial compared with any slice that would touch AppShell, SessionX, loopback authority, release/trust, or build-path ownership

Immediate validation that must follow `RMS-001`:

1. parse all touched JSON mirrors
2. confirm prose and machine-readable mirrors still align
3. run `git diff --check`
4. run `python tools/validation/tool_run_validation.py --profile FAST`
5. confirm that the slice did not touch runtime, entrypoint, or path-resolution code; if it did, stop and reclassify the work

Immediate rollback triggers for `RMS-001`:

- source-of-truth ambiguity increases instead of decreasing
- any doc or mirror starts claiming a different canonical entrypoint than the live shells and audit evidence support
- `FAST` regresses unexpectedly
- scope expands into runtime behavior, imports, includes, manifests, session semantics, or real path logic
- report or audit regeneration begins to misstate runtime truth

## F. Residual Risk Ledger

| Risk ID | Residual risk | Why it still matters before later relayout | Effect on `RMS-001` |
| --- | --- | --- | --- |
| `RR-001` | canonical playable-baseline path is still not hardened | Blocks `MP-1` and all later slices that touch entrypoints or product-shell seams. | Does not block `RMS-001`, but forbids using `RMS-001` as proof that broader relayout is now safe. |
| `RR-002` | `server/server_main.py` repo-root misresolution | Keeps direct Python server startup blocked and makes local-authority seam movement unsafe. | Must stay documented truth; `RMS-001` must not overclaim readiness. |
| `RR-003` | `session_boot` / `sessionx/runner.py` save-root coupling | Keeps session-location movement and generated-output rebinding unsafe. | `RMS-001` may document the constraint, not fix it. |
| `RR-004` | launcher supervision instability | Keeps AppShell and operator-shell relayout high risk. | `RMS-001` must not describe supervision as solved. |
| `RR-005` | native launcher/setup and non-loopback surfaces remain stub-heavy | Prevents wrappers from being treated as canonical owners. | `RMS-001` should narrow wrapper readiness claims, not widen them. |
| `RR-006` | stale `src/...` mirrors plus `tools/import_bridge.py` still coexist | Drift is real and is exactly why the first slice exists, but bridge retirement remains later work. | This is the main risk addressed by `RMS-001`. |
| `RR-007` | default bundle seam between authored MVP guidance and `bundle.base.lab` | Silent normalization would create false truth during later movement or path cleanup. | `RMS-001` must keep the seam visible. |
| `RR-008` | split-root ambiguity in `schema/` / `schemas/` and `packs/` / `data/packs/` | Keeps ownership convergence explicitly deferred. | `RMS-001` must not pick winners by wording. |
| `RR-009` | validation strength after a doc-only slice is necessarily narrow | `FAST` proves consistency and non-regression in the repo’s audit pipeline, but not playable-baseline readiness. | Requires an explicit stop after `RMS-001`; no automatic progression to `RMS-002`. |

## G. Go / Hold Decision

Decision:

- `proceed with first migration slice`

Scope of approval:

- approved now:
  `MP-0 / RMS-001` only
- not approved now:
  any physical relayout, any shim-backed slice, any path-logic change, any file move, any root rename, and any `MP-1` or later slice

Why this is the correct verdict:

- the series is complete and decision-grade
- the preferred target is justified
- `RMS-001` is a real execution slice with meaningful value, not a redundant extra clarification artifact
- `RMS-001` does not compete with the baseline-first priority because it is no-move, no-shim, and no-runtime-change
- broader relayout execution is still not safe because the canonical playable-baseline path is not yet hardened

This is therefore a narrow go, not a broad go.

## H. Exact Next Execution Order

1. Execute:
   `REPO-MIGRATION-Ω1 — RMS-001_NO_MOVE_PATH_AUTHORITY_AND_WRAPPER_PRECEDENCE_NORMALIZATION-0`
2. Immediately validate the slice with:
   JSON parse for touched mirrors, prose/mirror consistency, `git diff --check`, and `python tools/validation/tool_run_validation.py --profile FAST`
3. Stop after the slice and record the result as:
   `MP-0 complete, broader relayout still gated`
4. Return the broader product priority to:
   canonical playable-baseline hardening, including startup-path clarification, server repo-root correction, session save-root correction, supervision stability, and one repeatable repo-local playtest path
5. Do not attempt yet:
   `RMS-002`, `MP-1`, any physical relayout, any shim introduction, split-root convergence, or any XStack/AIDE-shaped extraction work

## I. Boundaries And Anti-Patterns

Execution after this checkpoint must preserve:

- the `verify` configure/build/test lane
- `FAST` validation honesty
- the Python/AppShell launcher and setup shells as canonical repo-local operator surfaces
- current SessionX create/boot and `saves/<save_id>` truth
- the loopback-authoritative local path
- authority order, canonical-versus-derived discipline, and XStack/AIDE non-interference

Execution must validate first:

- that the slice is still doc-and-mirror-only
- that touched JSON mirrors parse
- that prose and machine-readable claims still match live roots
- that `FAST` remains complete

The first slice must not bundle:

- feature work
- `server_main.py` fixes
- session save-root fixes
- launcher or setup behavior changes
- trust or release-path changes
- path shims
- import/include alias work
- split-root convergence
- playtest-path hardening itself

Unsafe or scope-creeping relayout shapes include:

- treating `RMS-001` as permission to start physical relayout immediately after merge
- slipping runtime, entrypoint, manifest, or path-resolution edits into a doc-normalization slice
- using stale audit/doc cleanup to overstate readiness
- bundling RMS-001 with baseline-blocker fixes and calling the combined work “cleanup”
- treating the preferred conceptual target as if the repo had already migrated

## J. Final Verdict

- Is the repo-structure series complete and decision-grade:
  `yes`
- Is the preferred target justified:
  `yes`
- Is the repo ready to begin phased relayout:
  `yes, but only at MP-0 / RMS-001`
- Is the repo ready for physical relayout or shim-backed relayout:
  `no`
- What exact first migration slice should execute next:
  `RMS-001 - No-Move Path Authority And Wrapper-Precedence Normalization`
- What bundle should be used for review here:
  `tmp/dominium_repo_structure_decision_bundle_20260408.zip` together with its report and manifest

The authoritative decision is therefore:

- approve only the bounded no-move first slice
- keep all broader relayout work gated behind playable-baseline hardening
- use the bundle emitted with this checkpoint as the human-review and planning packet before execution
