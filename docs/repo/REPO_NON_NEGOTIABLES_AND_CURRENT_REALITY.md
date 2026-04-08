Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: canonical constraint packet for later repo-structure discovery, design, migration-planning, and decision prompts; downstream of stronger canon, planning law, audit evidence, and live implementation evidence
Replacement Target: later explicit repo-structure follow-up after new playable-baseline evidence or an approved redesign checkpoint
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `data/audit/ultra_repo_audit_system_inventory.json`, `data/audit/ultra_repo_audit_entrypoints.json`, `data/audit/ultra_repo_audit_product_assembly_plan.json`, `data/audit/ultra_repo_audit_gap_ledger.json`, `data/audit/ultra_repo_audit_build_run_test_matrix.json`, `data/audit/ultra_repo_audit_wiring_map.json`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `data/xstack/codex_repo_operating_contract.json`, `docs/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`, `data/xstack/xstack_to_aide_extraction_map.json`, `CMakePresets.json`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`, `tools/validation/tool_run_validation.py`, `tools/xstack/testx_all.py`, `tools/mvp/runtime_entry.py`, `server/server_main.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`, `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, `data/session_templates/session.mvp_default.json`

# Repo Non-Negotiables And Current Reality

## A. Purpose And Scope

This artifact freezes the constraint packet that later repo-structure prompts must consume before they propose topology changes, migration phases, shims, or ownership moves.

It exists to solve a real planning problem:

- the repo already has strong doctrine, closure, audit, and XStack/AIDE boundary packets
- the immediate product priority is still the canonical repo-local playable baseline
- future repo relayout work would be unsafe if it silently broke the current build, validation, session, or loopback-authority path while trying to make the tree look cleaner

This artifact is therefore baseline-first and redesign-limiting.
It is not a migration plan, not a topology decision, not a blocker-fix prompt, and not a feature prompt.

For later repo relayout work, the direct answers are:

- What must not break under any relayout:
  the `verify` build lane, the `FAST` plus `TestX` plus `CTest` validation chain, the Python/AppShell launcher and setup shells, the `session_create` and `session_boot` path contract, the current `saves/<save_id>/` boot assumption, the local loopback-authoritative path, authority-order and ownership doctrine, and the retained/deferred baseline-critical surfaces called out by the audit and XStack/AIDE closure.
- What current build, run, test, session, and playtest flows must survive:
  the flows listed in Section E.
- What is explicitly out of scope:
  the work listed in Section G.
- What this enables next:
  the next repo-structure discovery prompt class that maps current topology, path dependencies, and ownership boundaries under these frozen constraints before any topology design is chosen.

This packet is downstream of higher-order canon and live implementation evidence.
It does not replace `docs/canon/**`, `AGENTS.md`, or the post-`Ζ` and XStack/AIDE closure artifacts.

## B. Current-Reality Baseline

Later prompts must treat the following as the current reality baseline.

### Verified Now

- Post-`Ζ` doctrine and gating closure is complete, no further internal `Ζ` prompt is required, and the next broader mode is post-`Ζ` reconciliation and consolidation rather than more internal `Ζ` expansion.
- The XStack/AIDE narrowing-and-contract phase is complete, no further XStack/AIDE prompt is required before the playable baseline exists, and the existing X-series artifacts now act as a constraint packet rather than a competing implementation track.
- `CMakePresets.json` still defines aligned `verify` configure, build, and test presets, and the audit freezes that lane as the canonical compiled baseline.
- `tools/validation/tool_run_validation.py` exposes `FAST | STRICT | FULL` with `FAST` as the current default, and `tools/xstack/testx_all.py` exposes `FAST | STRICT | FULL` as the TestX entry surface.
- `tools/launcher/launch.py` and `tools/setup/setup_cli.py` are real repo-rooted AppShell shells, and the audit identifies them as the strongest repo-local operator surfaces now.
- `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, and `server/net/loopback_transport.py` together define a real session-plus-loopback authority path, even though parts of that path are still fragile.
- The authored MVP baseline asset trio exists and is live: `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, and `data/session_templates/session.mvp_default.json`.

### Likely But Not Fully Re-Verified In This Prompt

- The current strongest runnable compiled path is still the `out/build/vs2026/verify/` tree produced by the `verify` preset family; this comes from the ultra audit plus the still-present preset definitions, not from a fresh compiled run in this prompt.
- The current strongest repo-local product-shell path is still Python/AppShell-first rather than native wrapper-first; this is strongly evidenced by the audit and the live shell code, but the playtest wrapper itself is not yet fully hardened.
- The compiled verify tree still carries broad CTest coverage, including playtest-adjacent suites; that coverage was audited and enumerated, but not fully re-executed here.
- The shortest path to a playable baseline still looks like wrapper-hardening around existing session creation plus local loopback authority, not greenfield runtime or platform work.

### Blocked Or Fragile

- `server/server_main.py` remains an unsafe public Python server startup path because its `REPO_ROOT_HINT` still resolves two directories above the `server/` root, which is outside the repo root.
- `tools/xstack/session_boot.py` remains coupled to `tools/xstack/sessionx/runner.py`, and `runner.py` still resolves boot artifacts back through `repo_root/saves/<save_id>` instead of honoring alternate save roots end to end.
- `tools/mvp/runtime_entry.py --local-singleplayer` remains transitional; it does not yet qualify as the fully hardened public playtest command.
- Launcher-supervised attach and restart behavior remains fragile enough that the audit treats supervision stability as a real blocker for repeatable internal sessions.
- External multiplayer transport remains blocked because the non-loopback transport surfaces are still explicit stubs.
- Native launcher and setup shells remain wrapper-thin and stub-heavy relative to the Python/AppShell shells.

### Doctrinally Closed But Realization-Incomplete

- Post-`Ζ` frontier items remain unresolved realization territory; they are explicit frontier, not omitted work, and they are not reopened by this series.
- XStack/AIDE contract freezing is complete, but runtime extraction, platformization, daemon or scheduler work, and repo migration remain intentionally deferred until after the playable baseline exists.

### Implementation / Guidance Seams That Must Stay Visible

- The baseline recipe and XStack repo-operating guidance lean on the authored MVP asset trio, especially `profile.bundle.mvp_default`, `pack_lock.mvp_default`, and `session.mvp_default`.
- The live `tools/xstack/session_create.py` default `--bundle` still comes from `tools/xstack/registry_compile/constants.py`, where `DEFAULT_BUNDLE_ID` is `bundle.base.lab`.
- That means the repo currently contains a real implementation-vs-guidance seam around default bundle selection.
- Later prompts may design how to converge or normalize that seam, but they may not hide it by directory moves or by writing as if the seam is already resolved.

## C. Non-Negotiable Constraint Categories

| Category ID | Category | Real meaning |
| --- | --- | --- |
| `governance_authority` | Governance / authority constraints | Higher-order doctrine, authority ordering, protected-surface discipline, and extension-over-replacement rules that later topology work must remain downstream of. |
| `build_constraints` | Build constraints | The compiled lane, preset family, and build-artifact assumptions that future relayout must preserve or explicitly migrate. |
| `validation_constraints` | Validation constraints | The minimum honest validation surfaces, profile vocabulary, and status-language rules that later prompts must preserve. |
| `entrypoint_runpath_constraints` | Entrypoint / runpath constraints | Operator shells, public entrypoints, blocked startup paths, and live runpath contracts that must remain truthful under relayout. |
| `session_profile_save_constraints` | Session / profile / save constraints | Session materialization, boot semantics, save-root truth, and authored baseline asset contracts that later prompts must preserve. |
| `playtest_path_constraints` | Playtest-path constraints | The current canonical local playable-baseline target, including loopback authority and repo-local scope. |
| `canonical_vs_derived_constraints` | Canonical-vs-derived constraints | Distinctions between canon, implementation, mirrors, audit evidence, projections, and generated outputs. |
| `retained_vs_deferred_constraints` | Retained-vs-deferred constraints | Which surfaces must stay stable in Dominium until after baseline, and which work must remain deferred instead of becoming redesign pretext. |
| `xstack_aide_non_interference` | Non-interference constraints from XStack/AIDE closure | The rule that XStack/AIDE closure now constrains baseline work instead of competing with it. |

## D. Concrete Non-Negotiable Ledger

### `RNC-GOV-001 — Higher-Order Authority And Stronger-Source Precedence Remain Binding`

- Category: `governance_authority`
- Why it exists:
  repo-structure work is downstream of canon and task law, and the authority model explicitly forbids resolving drift by convenience.
- Supporting evidence/source:
  `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`
- What must be preserved:
  canon and glossary precedence, `AGENTS.md` task discipline, live implementation as structural truth, and the rule that mirrors and generated outputs stay derived unless explicitly promoted by stronger law.
- What later prompts may vary:
  how the series restates or mirrors these rules, and how later redesign docs summarize supporting evidence.
- What later prompts may not vary:
  they may not let repo-structure docs, generated outputs, or chat memory outrank canon, `AGENTS.md`, or live structural evidence.
- Violation that breaks correctness or planning discipline:
  choosing topology from stale prose, mirrors, or convenience wrappers instead of higher-order canon plus the live repo.

### `RNC-GOV-002 — Extend-Over-Replace And Ownership-Sensitive Splits Stay Visible`

- Category: `governance_authority`
- Why it exists:
  the planning packet already freezes keep/extend/do-not-replace zones and quarantined ownership splits.
- Supporting evidence/source:
  `AGENTS.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `.agentignore`
- What must be preserved:
  stable product anchors, runtime substrate caution, and explicit ownership sensitivity around `field/` vs `fields/`, `schema/` vs `schemas/`, and `packs/` vs `data/packs/`.
- What later prompts may vary:
  later explicit convergence proposals, shim plans, or ownership review sequencing.
- What later prompts may not vary:
  they may not silently collapse the split roots or pivot the runtime plan around `runtime/` by convenience.
- Violation that breaks correctness or planning discipline:
  directory moves that choose ownership winners implicitly instead of through explicit later review.

### `RNC-ZET-001 — Internal Zeta Stays Closed`

- Category: `governance_authority`
- Why it exists:
  post-`Ζ` doctrine closure already states that the admissible `Ζ` program is complete and that the next broader mode is reconciliation and consolidation.
- Supporting evidence/source:
  `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`
- What must be preserved:
  no further internal `Ζ` prompt before post-`Ζ` reconciliation, and no silent widening of bounded-only, proof-only, guarded, blocked, or future-only frontier families.
- What later prompts may vary:
  how post-`Ζ` reconciliation is documented or sequenced after this series.
- What later prompts may not vary:
  they may not repurpose repo-structure work into live-ops frontier work or guarded-family promotion.
- Violation that breaks correctness or planning discipline:
  using relayout or cleanup work to smuggle blocked `Ζ` realization work back into near-term scope.

### `RNC-XA-001 — XStack/AIDE Remains A Constraint Packet, Not A Competing Workstream`

- Category: `xstack_aide_non_interference`
- Why it exists:
  the XStack/AIDE narrowing-and-contract phase is closed, and its own closure packet explicitly subordinates it to the playable-baseline priority.
- Supporting evidence/source:
  `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `docs/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`
- What must be preserved:
  no new XStack/AIDE prompt before the playable baseline exists, no pre-baseline platformization or migration, and no extraction of baseline-critical Dominium surfaces.
- What later prompts may vary:
  post-baseline AIDE roadmap details after the playable baseline is proven.
- What later prompts may not vary:
  they may not treat XStack/AIDE contract freezing as permission to start extraction, repo splits, or wrapper proliferation now.
- Violation that breaks correctness or planning discipline:
  using portability aspirations to justify pre-baseline repo churn or a second competing architecture track.

### `RNC-BLD-001 — The Verify Preset Family Remains The Canonical Compiled Lane`

- Category: `build_constraints`
- Why it exists:
  both the audit and the XStack repo-operating contract freeze the `verify` preset family as the current compiled baseline.
- Supporting evidence/source:
  `CMakePresets.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- What must be preserved:
  `cmake --preset verify`, `cmake --build --preset verify`, `ctest --preset verify`, and the current verify-aligned build/test relationship.
- What later prompts may vary:
  internal CMake helper placement, wrapper scripts, or a future explicitly admitted replacement lane.
- What later prompts may not vary:
  they may not silently demote `verify`, break the aligned preset family, or pretend another lane is now canonical during this series.
- Violation that breaks correctness or planning discipline:
  relayout breaks the canonical preset family or strands the repo without one explicit proveable compiled lane.

### `RNC-VAL-001 — FAST, TestX, CTest, And Honest Status Language Must Survive`

- Category: `validation_constraints`
- Why it exists:
  later prompts need one honest validation spine and one stable way to report `verified`, `likely`, `partial`, and `blocked` instead of flattening them.
- Supporting evidence/source:
  `AGENTS.md`, `tools/validation/tool_run_validation.py`, `tools/xstack/testx_all.py`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- What must be preserved:
  `python tools/validation/tool_run_validation.py --profile FAST` as the minimum canonical validation path, `python tools/xstack/testx_all.py --profile FAST` as the XStack/TestX companion when relevant, `ctest --preset verify` as the compiled companion when the compiled lane is implicated, and explicit status-class language.
- What later prompts may vary:
  stronger validation, narrower smoke slices, helper wrappers, or post-baseline validation reshaping after explicit proof.
- What later prompts may not vary:
  they may not replace the honest status classes with one flattened success label, and they may not claim green validation without real execution.
- Violation that breaks correctness or planning discipline:
  relayout breaks the validation surfaces, hides them behind unproven wrappers, or makes blocked flows look verified.

### `RNC-RUN-001 — Python/AppShell Launcher And Setup Shells Remain The Canonical Repo-Local Operator Surfaces`

- Category: `entrypoint_runpath_constraints`
- Why it exists:
  the audit identifies these shells as the strongest operator surfaces now, and the canonical playable-baseline recipe depends on them.
- Supporting evidence/source:
  `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- What must be preserved:
  `python tools/launcher/launch.py` and `python tools/setup/setup_cli.py` as the canonical repo-local shells for compat, profile, pack, install-discovery, and status/reporting work.
- What later prompts may vary:
  future wrapper or façade strategy, internal module layout, or later native parity work after the baseline exists.
- What later prompts may not vary:
  they may not treat compiled launcher/setup wrappers as the canonical operator path just because those binaries look cleaner or shorter.
- Violation that breaks correctness or planning discipline:
  relayout hides or degrades the Python/AppShell shells before a stronger proved replacement exists.

### `RNC-RUN-002 — Direct Python Server Startup Remains Blocked Truth Until Explicitly Fixed`

- Category: `entrypoint_runpath_constraints`
- Why it exists:
  later prompts must not use path moves to pretend that a blocked startup entrypoint is already ready.
- Supporting evidence/source:
  `server/server_main.py`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `data/audit/ultra_repo_audit_entrypoints.json`, `data/audit/ultra_repo_audit_gap_ledger.json`
- What must be preserved:
  the current reality that `python server/server_main.py` and `python -m server.server_main` are not safe baseline commands today.
- What later prompts may vary:
  an explicit later fix to repo-root math, import bootstrapping, or path resolution.
- What later prompts may not vary:
  they may not promote these paths to canonical status through documentation, path aliases, or relayout alone.
- Violation that breaks correctness or planning discipline:
  redesign prose starts telling operators to use a server startup path that is still blocked in live code.

### `RNC-SES-001 — Session Materialization And Boot Semantics Stay Anchored In SessionX`

- Category: `session_profile_save_constraints`
- Why it exists:
  the playable-baseline path already depends on `session_create` and `session_boot`, and the save-root coupling is a real current constraint.
- Supporting evidence/source:
  `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- What must be preserved:
  `tools/xstack/session_create.py` as the canonical materialization entrypoint, `tools/xstack/session_boot.py` as the canonical boot entrypoint, `save_id` as required identity, and `saves/<save_id>/session_spec.json` as the current honest bootable layout.
- What later prompts may vary:
  later explicit fixes to save-root handling, later wrapper naming, or later internal module grouping after explicit prompt approval.
- What later prompts may not vary:
  they may not break the canonical `saves/<save_id>/` boot path before a proved replacement exists.
- Violation that breaks correctness or planning discipline:
  relayout strands session artifacts from their boot path or advertises alternate save roots as supported without code proof.

### `RNC-SES-002 — The Authored MVP Asset Trio And The Current Bundle-Default Seam Must Stay Explicit`

- Category: `session_profile_save_constraints`
- Why it exists:
  the repo contains real authored MVP baseline assets, but the live session-create default still points at a different bundle id.
- Supporting evidence/source:
  `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, `data/session_templates/session.mvp_default.json`, `tools/mvp/runtime_bundle.py`, `tools/xstack/session_create.py`, `tools/xstack/registry_compile/constants.py`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- What must be preserved:
  the existence and path stability of the authored MVP bundle, pack lock, and session template; the ability to target them explicitly; and the explicit note that `session_create.py` defaults `--bundle` to `bundle.base.lab` while the baseline recipe leans on `profile.bundle.mvp_default`.
- What later prompts may vary:
  a later explicit convergence strategy for bundle defaults, a shim, or a revised baseline recipe after proof.
- What later prompts may not vary:
  they may not write as if the seam is already solved, and they may not use directory moves to hide it.
- Violation that breaks correctness or planning discipline:
  topology work silently turns an open guidance-vs-implementation seam into a fake closure story.

### `RNC-PLT-001 — The Canonical Local Playtest Target Remains Repo-Local, Single-Machine, And Loopback-Authoritative`

- Category: `playtest_path_constraints`
- Why it exists:
  the ultra audit and XStack repo-operating contract both freeze the same immediate product priority: harden one canonical repo-local playable baseline around session creation plus local loopback authority.
- Supporting evidence/source:
  `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- What must be preserved:
  repo-local scope, single-machine posture, loopback authority only, Python/AppShell-first operator surfaces, canonical `saves/<save_id>/` materialization, and the truth that the current path is a target recipe rather than a finished one-command flow.
- What later prompts may vary:
  which explicit wrapper later hardens the one canonical command, provided it composes these existing surfaces honestly.
- What later prompts may not vary:
  they may not broaden the baseline to non-loopback multiplayer, installed-mode assumptions, or native-shell-first assumptions by convenience.
- Violation that breaks correctness or planning discipline:
  choosing a cleaner-but-less-proven runtime direction and calling it the new canonical playtest path without proof.

### `RNC-PLT-002 — The Local Loopback Runtime Bridge Remains Baseline-Critical Dominium-Owned Substrate`

- Category: `playtest_path_constraints`
- Why it exists:
  the local authority path is both the strongest evidence-backed runtime direction and a retained Dominium surface in the extraction map.
- Supporting evidence/source:
  `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `docs/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`
- What must be preserved:
  the connection between `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`, and the current server boot/runtime path.
- What later prompts may vary:
  later post-baseline wrappers, shims, or provider interfaces after explicit review.
- What later prompts may not vary:
  they may not extract, migrate, or de-own this bridge before the playable baseline exists and later review admits it.
- Violation that breaks correctness or planning discipline:
  moving the current local authority bridge into a portability track and breaking the shortest proven playtest direction.

### `RNC-DRV-001 — Canonical, Derived, Audit-Evidence, And Implementation Statuses Must Not Be Flattened`

- Category: `canonical_vs_derived_constraints`
- Why it exists:
  the repo already has canonical doctrine, derived mirrors, audit evidence, generated outputs, and live code; later prompts need those classes to stay distinguishable.
- Supporting evidence/source:
  `docs/planning/AUTHORITY_ORDER.md`, `AGENTS.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `docs/audit/ULTRA_REPO_AUDIT_*.md`, `data/audit/*.json`
- What must be preserved:
  canon over mirrors, live implementation over stale docs for structure, audit docs and JSON as evidence rather than law, generated outputs as non-canonical unless explicitly promoted, and explicit `verified` vs `likely` vs `blocked` reporting.
- What later prompts may vary:
  doc refreshes, mirror improvements, or evidence packaging.
- What later prompts may not vary:
  they may not let audit reports, generated outputs, or stale docs become stronger than live implementation or canon where those sources disagree.
- Violation that breaks correctness or planning discipline:
  a redesign packet turns evidence into doctrine or turns blocked paths into verified ones by writing style.

### `RNC-DEF-001 — Baseline-Critical Retained And Deferred Surfaces Must Stay Stable Until After The Playable Baseline Exists`

- Category: `retained_vs_deferred_constraints`
- Why it exists:
  the audit and XStack/AIDE extraction map both freeze a retained-vs-deferred posture specifically so the baseline path is not destabilized by broad repo churn.
- Supporting evidence/source:
  `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `docs/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- What must be preserved:
  the retained status of SessionX runtime/control, AppShell and operator shells, local loopback runtime glue, pack and distribution pipelines, release/trust consumers, and repo-local operating law surfaces until after the baseline exists.
- What later prompts may vary:
  later post-baseline extraction-review sequencing, convergence proposals, or explicit migration plans.
- What later prompts may not vary:
  they may not use the repo-structure series to do broad renames, extraction, ownership rebinding, or migration across these surfaces before the baseline exists.
- Violation that breaks correctness or planning discipline:
  repo-structure work becomes a stealth migration or platformization pass that increases baseline risk instead of containing it.

## E. Build / Validation / Runpath Survival Rules

Any future relayout must preserve the following flows, either literally or through an explicitly proved equivalent that is introduced by a later approved prompt.

| Survival Rule ID | Current anchor | Current status | Survival rule |
| --- | --- | --- | --- |
| `survive.build.verify` | `cmake --preset verify`, `cmake --build --preset verify`, `ctest --preset verify` | canonical lane frozen by audit and presets; not re-executed here | Preserve one verify-aligned configure/build/test lane and do not silently demote `verify` during this series. |
| `survive.validation.fast` | `python tools/validation/tool_run_validation.py --profile FAST` | live entrypoint verified; full green status remains task-dependent | Preserve the `FAST` validation entry surface and its report semantics. |
| `survive.validation.testx_fast` | `python tools/xstack/testx_all.py --profile FAST` | live entrypoint verified; full suite not re-run here | Preserve TestX as the XStack validation companion when tooling, session, compat, or validation surfaces are touched. |
| `survive.validation.ctest_verify` | `ctest --preset verify` | audited compiled harness; broad tree enumerated, not fully rerun here | Preserve a compiled-test companion aligned with the verify lane. |
| `survive.shell.launcher_appshell` | `python tools/launcher/launch.py compat-status|profiles list|packs list|launcher status` | strongest current launcher/operator shell | Preserve the launcher AppShell flow as a canonical repo-local operator surface until a stronger proved replacement exists. |
| `survive.shell.setup_appshell` | `python tools/setup/setup_cli.py compat-status|profiles list|packs list` | strongest current setup/operator shell | Preserve the setup AppShell flow as a canonical repo-local operator surface until a stronger proved replacement exists. |
| `survive.session.create` | `python tools/xstack/session_create.py --save-id <save_id>` | canonical materialization path; default bundle seam remains open | Preserve the ability to create session artifacts through SessionX, and keep baseline-oriented bundle/lock/template expectations explicit. |
| `survive.session.boot` | `python tools/xstack/session_boot.py saves/<save_id>/session_spec.json` | canonical boot surface, but save-root fragile | Preserve the current honest boot contract around `saves/<save_id>/session_spec.json` until explicit save-root support changes. |
| `survive.runtime.loopback_local` | `client.local_server.local_server_controller.start_local_singleplayer` plus `runtime/process_spawn.py` plus `server/net/loopback_transport.py` | partially verified internal runtime anchor | Preserve the local singleplayer loopback bridge and its retained in-repo ownership. |
| `survive.playtest.baseline_recipe` | verify lane plus Python/AppShell shells plus session materialization plus local loopback authority | target recipe, not yet one finished command | Preserve the current baseline recipe as the top redesign constraint and do not invent a second official playtest path. |
| `survive.save_resume.baseline` | canonical `saves/<save_id>/` layout and repeatable boot/resume expectation | fragile and not fully green yet | Preserve the current save/load/resume assumptions or change them only through an explicit later fix with honest proof. |

## F. Boundaries On Redesign Freedom

### Later Prompts Are Free To Redesign Conceptually

- future topology options and grouping proposals
- later migration phase ordering and shim strategy proposals
- documentation packaging and evidence presentation
- explicit wrapper strategy for a later one-command playtest flow
- later convergence proposals for mixed or legacy roots, after they are analyzed under this packet

### Later Prompts Are Not Free To Break

- the authority order, extension-over-replacement discipline, and ownership-sensitive split cautions
- the `verify` build lane and the `FAST` plus `TestX` plus `CTest` validation spine
- the current canonical repo-local operator shells
- the current SessionX create and boot path contracts
- the repo-local, loopback-authoritative, single-machine playable-baseline target
- the truth that some paths are verified, some only likely, and some still blocked or fragile
- the retained-vs-deferred baseline-critical posture from the XStack/AIDE closure packet

### Must Remain Stable Until After The Playable Baseline Exists

- `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, and `appshell/**` as the current operator-shell center
- `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, and the current canonical `saves/<save_id>/` boot layout
- the local loopback runtime bridge rooted in `client/local_server/**`, `runtime/process_spawn.py`, and `server/net/loopback_transport.py`
- the post-`Ζ` closure boundary and the XStack/AIDE non-interference boundary
- the retained status of pack/distribution, release/trust, and repo-local validation/control surfaces that the extraction map keeps in Dominium for now

## G. Explicit Out-Of-Scope List

This repo-structure series must not do the following unless a later explicit prompt changes scope:

- implement the one-command canonical playtest path
- patch `server/server_main.py` repo-root logic directly
- patch `tools/xstack/sessionx/runner.py` save-root coupling directly
- move files or rename roots in this prompt
- redesign the final repo topology in this prompt
- broaden into feature expansion
- reopen internal `Ζ` work
- broaden into post-`Ζ` live-ops frontier realization
- implement a full AIDE runtime, daemon, scheduler, compiler, adapter runtime, or separate AIDE repo
- perform broad extraction or migration because a surface looks portable
- perform large convergence or ownership-rebinding work driven by XStack concerns
- broaden into non-loopback multiplayer, installed-mode distribution, or native launcher/setup completion work

## H. Open Questions That Must Remain Open For Now

- What the final preferred repo topology actually is.
- What the exact migration phases and rollback points should be.
- What the exact shim or alias strategy should be for any future path changes.
- Which future wrapper, if any, should become the one canonical playtest command after baseline hardening.
- How `session_create.py` default `bundle.base.lab` behavior should converge, if at all, with the baseline recipe that leans on the authored MVP bundle, pack lock, and session template.
- Which mixed surfaces later belong in portable substrate, retained Dominium wrappers, or later retirement work.
- Whether `out/build/vs2026/verify/` remains the literal future artifact root or is later abstracted behind another stable equivalent.
- What the exact target ownership moves are, if any, across `field/` vs `fields/`, `schema/` vs `schemas/`, and `packs/` vs `data/packs/`.

## I. Anti-Patterns / Forbidden Shapes

- Choosing a topology that breaks the `verify` preset family.
- Treating compiled launcher or setup wrappers as canonical just because they look cleaner on paper.
- Moving baseline-critical SessionX, AppShell, launcher/setup, or loopback runtime surfaces too early.
- Using XStack/AIDE portability aspirations to justify repo churn before the playable baseline exists.
- Promoting `server/server_main.py` or `tools/mvp/runtime_entry.py` into the canonical public playtest path through documentation only.
- Using stale docs, mirrors, or generated outputs as stronger truth than live implementation where structural reality disagrees.
- Flattening `verified`, `likely`, `partial`, and `blocked` into one status class.
- Assuming alternate save roots or non-loopback transport are baseline-ready because flags or stubs exist.
- Solving ownership-sensitive split questions by directory preference instead of explicit later review.
- Reopening internal `Ζ` or pre-baseline XStack/AIDE platform work through repo-structure language.

## J. Stability And Evolution

- Stability class:
  stable derived constraint packet for the repo-structure series.
- Later prompts that consume this artifact:
  every later repo-structure discovery prompt, topology-option prompt, ownership-mapping prompt, migration-planning prompt, and redesign decision prompt.
- Immediate next prompt class enabled by this artifact:
  topology, path, and ownership mapping under frozen constraints before any topology design is chosen.
- What must not change without explicit follow-up:
  the canonical compiled lane, the canonical validation lane, the current local playtest target, the current session/save-root truth, the retained-vs-deferred baseline posture, the post-`Ζ` closure boundary, and the rule that XStack/AIDE stays behind baseline work rather than in front of it.

This artifact is intentionally conservative.
Its job is to keep later repo-structure work honest about what must survive, what is still blocked, what is already closed, and what must not be "solved" prematurely by moving directories around.
