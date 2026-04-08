Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: authoritative preferred-target and boundary packet for later migration, shim, rollback, and ownership-reconciliation prompts; downstream of stronger canon, the Omega0 constraint packet, the Omega1 topology reality map, the Omega2 coupling-risk packet, and the Omega0 topology-option comparison
Replacement Target: later explicit migration-planning checkpoint or preferred-target replacement only after new baseline-hardening evidence and follow-up approval
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `data/repo/repo_non_negotiables_and_current_reality.json`, `docs/repo/REPO_TOPOLOGY_PATHS_AND_OWNERSHIP_REALITY_MAP.md`, `data/repo/repo_topology_paths_and_ownership_reality_map.json`, `docs/repo/REPO_COUPLING_DRIFT_AND_RELAYOUT_RISK_ANALYSIS.md`, `data/repo/repo_coupling_drift_and_relayout_risk_analysis.json`, `docs/repo/REPO_TARGET_TOPOLOGY_OPTIONS_AND_COMPARISON.md`, `data/repo/repo_target_topology_options_and_comparison.json`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `appshell/paths/virtual_paths.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `release/release_manifest_engine.py`

# Repo Authoritative Boundary Model And Preferred Target

## A. Purpose And Scope

This artifact selects the preferred conceptual target topology for the live Dominium repo and freezes the authoritative boundary model that later migration-planning prompts must follow.

It exists because the series has now completed four upstream steps:

- Omega0 froze the non-negotiable survival rules.
- Omega1 mapped the live roots, path contracts, and ownership reality.
- Omega2 measured coupling strength, drift, shim burden, and relayout risk.
- Omega0 design generated and compared the bounded topology option set.

What remained undecided after those packets was the commitment layer:

- which option actually becomes the preferred target
- which conceptual boundaries later migration prompts must preserve
- which parts of the model are firm now versus still conditional
- which tradeoffs the series is willing to accept in exchange for baseline safety

Its relationship to the canonical playable-baseline priority is explicit:

- the preferred target is selected by weighting baseline-path preservation, ownership truthfulness, flow safety, and XStack/AIDE non-interference above long-term cleanliness alone
- this artifact does not authorize file moves, renames, shims, or phased execution
- the selected target is conceptual, not migratory

Its relationship to the earlier repo packets is strict:

- Omega0 still governs what must not break
- Omega1 still governs what roots, contracts, and ownership facts exist now
- Omega2 still governs what is safe to move later, what likely needs shims, and what must not move yet
- Omega0 design still governs the bounded option set and comparison matrix

For later repo-structure work, the direct answers are:

- Which topology option is preferred:
  Section C.
- Why it is preferred over the alternatives:
  Sections B, C, and G.
- What the authoritative boundary model is:
  Sections D and E.
- How it preserves the canonical playable-baseline path:
  Section F.
- What remains undecided until migration planning:
  Section H.
- What prompt this enables next:
  phased migration, shim, and rollback planning against one frozen preferred target.

## B. Preferred-Target Selection Method

The preferred target is chosen from the bounded option set by using a dominance order rather than by averaging aesthetics.

### Dominant Criteria

The following criteria dominate the choice:

- preservation of the canonical playable-baseline path
- fit with current ownership reality
- path-contract tractability
- flow safety for build, run, test, session, and loopback-authoritative local execution
- XStack/AIDE non-interference

These dominate because Omega0 and Omega2 make clear that the current risk is not theoretical untidiness.
The current risk is breaking the repo-local playable-baseline path before one canonical playtest command is hardened.

### Secondary Criteria

The following criteria remain important, but they are secondary:

- maintainability
- long-term modularity
- Codex usability
- migration affordability after baseline hardening

These matter for the target model, but they do not outweigh current-reality and survival constraints.

### Current-Reality And Risk Findings That Constrain The Decision

The preferred-target choice is constrained by all of the following repo-grounded facts:

- `appshell/`, `tools/launcher/`, `tools/setup/`, SessionX create/boot, and the loopback-authoritative local path are Omega2 `do_not_move_yet` or high-shim surfaces
- `server/server_main.py` repo-root math, `sessionx/runner.py` save-root coupling, and supervision instability are still live blockers or fragilities
- wrapper-only native launcher/setup roots are not strong enough to anchor the preferred target
- `schema/` versus `schemas/` and `packs/` versus `data/packs/` remain explicit split-root cautions rather than resolved convergence winners
- XStack/AIDE closure forbids extraction-shaped pressure before the baseline exists

### Why This Is Still A Conceptual Commitment Rather Than A Migration Commitment

This artifact chooses the preferred target as a planning reference only.

It does not decide:

- exact physical moves
- exact root renames
- exact shim mechanisms
- exact staged ordering
- exact rollback boundaries

Those choices require later migration, shim, and rollback planning prompts that stay downstream of this packet.

## C. Selected Preferred Topology

### Preferred Target

- Preferred-target id:
  `PT-001`
- Selected option:
  `TTO-001 - Stabilized Current-Root Federation`
- Preferred-target name:
  `Preferred Target: Stabilized Current-Root Federation With Federated Boundary Model`

### Concise Description

The preferred conceptual target keeps the current top-level root federation as the future structural frame, but freezes a stricter conceptual boundary model across those roots so later migration planning can reduce mixed hosts and drift without destabilizing the baseline-critical path.

### Why It Wins

`TTO-001` wins because it clearly dominates on the criteria that matter most now:

- best preservation of the canonical playable-baseline path
- best fit with current ownership and path-contract reality
- best safety profile for `verify`, `FAST`, `TestX`, `CTest`, launcher/setup shells, SessionX create/boot, and the loopback-authoritative local path
- strongest alignment with extend-over-replace doctrine
- strongest alignment with XStack/AIDE non-interference

`TTO-002` remains the strongest non-selected alternative because it offers clearer long-term lattice boundaries, but it loses as the preferred target because it would require more shim design and more early conceptual distance from the current baseline-critical seams.

### What It Optimizes For

- preserving the current baseline-critical flows while future cleanup is designed
- staying truthful to the live ownership and coupling map
- creating a boundary model that later migration prompts can implement incrementally
- minimizing false canonicality and premature extraction pressure

### What Tradeoffs It Accepts

- the repo stays conceptually federated rather than physically simplified right away
- mixed roots such as `tools/`, `launcher/`, `setup/`, `docs/audit/`, and `data/audit/` remain visible as mixed hosts for longer
- long-term modularity and Codex ergonomics improve more slowly than they would under the lattice option

## D. Authoritative Boundary Model

The preferred target uses a federated boundary model.
That means the conceptual boundaries are authoritative even where the current physical roots still mix them.

### `product_shells_and_apps`

- What it owns:
  repo-local operator shells and product entry surfaces, including `appshell/`, `tools/launcher/`, `tools/setup/`, product-facing application wiring in `client/` and `server/`, local singleplayer orchestration under `client/local_server/`, and wrapper-only native launcher/setup leaves as wrappers.
- What it does not own:
  deep runtime/service substrate, release/trust policy, validation/report ownership, or canonical authored content roots.
- Legitimate cross-boundary dependencies:
  into runtime/substrate for authority services, process spawn, and loopback transport; into control-plane for install discovery, release resolution, and trust verification; into tooling for session assembly entry surfaces; into content roots for profiles, locks, templates, and registries.
- Boundary violations that would be unhealthy:
  treating `launcher/` or `setup/` wrapper leaves as canonical ownership centers, mutating release policy directly from shell code, or reading docs/audit mirrors as runtime truth.

### `runtime_substrate_and_engine`

- What it owns:
  authored simulation and authority substrate, including `engine/`, `game/`, shared runtime/service code, `net/`, `process/`, `server/runtime/`, `server/persistence/`, loopback implementation under `server/net/`, and the runtime side of authoritative client/server execution.
- What it does not own:
  product-shell policy, release/trust governance, session assembly CLI ownership, or planning/doctrine authority.
- Legitimate cross-boundary dependencies:
  into content roots for packs, profiles, locks, templates, registries, and schema-facing machine-readable contracts; into tooling for tests and validation harnesses; into control-plane at explicit manifest, compatibility, or trust boundaries.
- Boundary violations that would be unhealthy:
  using `runtime/` as the assumed whole-repo orchestrator home, deriving behavior from docs instead of code and machine-readable inputs, or mutating control-plane and planning surfaces directly.

### `control_plane_release_and_trust`

- What it owns:
  release, install, update, and trust policy surfaces, including `release/`, `security/trust/`, `updates/`, `repo/` release-policy law, install discovery, manifest resolution, and trust verification behavior consumed by the stronger launcher/setup shells.
- What it does not own:
  gameplay/runtime implementation, client/server product behavior, or authored content truth beyond reading governed inputs.
- Legitimate cross-boundary dependencies:
  into content roots for pack/profile/lock/registry inputs, into tooling and validation for proof/report generation, and into product shells for operator invocation and status presentation.
- Boundary violations that would be unhealthy:
  treating `dist/` outputs as canonical policy truth, turning release/trust roots into general product orchestration homes, or rebinding authored content ownership into release outputs.

### `tooling_validation_and_dev_workflows`

- What it owns:
  validation, session tooling, developer workflows, and proof/CI surfaces, including `tools/xstack/`, `tools/validation/`, `validation/`, `tests/`, `cmake/`, build scripts, workflow automation, and compatibility scaffolding such as `tools/import_bridge.py`.
- What it does not own:
  canonical product-shell ownership, semantic doctrine, release policy law, or authored content truth.
- Legitimate cross-boundary dependencies:
  into product-shell roots for operator entry surfaces, into runtime roots for proof targets, into content roots for compile and validation inputs, and into docs/audit roots for derived report emission.
- Boundary violations that would be unhealthy:
  promoting validation reports or compatibility bridges into canonical structural truth, treating `tools/` path location as proof of unified ownership, or letting tool wrappers redefine product or control-plane semantics.

### `content_profiles_locks_templates_registries_and_schema_contracts`

- What it owns:
  authored content, configuration, and machine-readable input families, including `packs/`, `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`, `schema/`, `schemas/`, and the explicitly unresolved `packs/` versus `data/packs/` caution zone.
- What it does not own:
  runtime/service logic, product-shell behavior, validation-report outputs, or release-generated manifests.
- Legitimate cross-boundary dependencies:
  into tooling for compilation and validation, into product/runtime roots as governed inputs, and into control-plane roots for install/release/trust planning where explicit registries or contracts are consumed.
- Boundary violations that would be unhealthy:
  silently collapsing `schema/` with `schemas/`, silently collapsing `packs/` with `data/packs/`, or treating generated outputs as replacements for the authored source roots.

### `docs_specs_planning_and_audit`

- What it owns:
  doctrine, specifications, planning packets, repo-structure packets, and audit/report surfaces, including `docs/`, `specs/`, `docs/planning/`, `docs/repo/`, `docs/xstack/`, `docs/audit/`, `data/planning/`, `data/xstack/`, and `data/audit/` as machine-readable mirrors and evidence.
- What it does not own:
  runtime structural truth when code and live machine-readable inputs disagree, product execution, or release policy implementation.
- Legitimate cross-boundary dependencies:
  references to every other boundary band for doctrine, inventories, evidence, and audit reporting; validation may emit derived evidence here.
- Boundary violations that would be unhealthy:
  treating audit reports as runtime truth, letting stale docs override live code or active registries, or using planning artifacts to choose ownership winners silently.

### Firm Boundaries Now

The following boundary commitments are firm now:

- product-shell and operator-shell ownership remains distinct from runtime/service ownership even where `client/`, `server/`, and `tools/` physically mix some of those concerns today
- control-plane and trust ownership remains distinct from product-shell and gameplay/runtime ownership
- authored content/config roots remain distinct from generated/intermediate roots
- documentation, planning, and audit roots remain distinct from runtime truth
- wrapper-only roots remain weaker than the stronger Python/AppShell shells

### Conditional Boundaries Pending Migration Planning

The following remain conditional until migration planning:

- exact physical separation of product-facing versus runtime-facing subtrees inside `client/` and `server/`
- exact internal ownership breakup of the `tools/` umbrella
- exact treatment of `launcher/` and `setup/` wrapper leaves
- exact physical handling of `schema/` versus `schemas/`
- exact physical handling of `packs/` versus `data/packs/`
- exact physical handling of `docs/audit/` and `data/audit/` as mixed doctrine-evidence families

## E. Canonical-Vs-Derived Boundary Model

### Canonical Source Roots The Preferred Target Must Preserve

- product and shell authority:
  `appshell/`, `client/`, `server/`, `tools/launcher/`, and `tools/setup/`
- runtime and service authority:
  `engine/`, `game/`, `net/`, `process/`, and runtime/service portions of `server/`
- control-plane authority:
  `release/`, `security/trust/`, `updates/`, and `repo/` policy surfaces
- authored content/config authority:
  `packs/`, `profiles/`, `locks/`, `data/session_templates/`, and `data/registries/`
- doctrine and planning authority:
  `docs/canon/`, `docs/planning/`, `docs/repo/`, `docs/xstack/`, and `specs/`

### Split-Truth And Bounded-Scope Canonicality That Must Stay Explicit

- `schema/` is canonical semantic contract law
- `schemas/` is the validator-facing machine-readable contract projection within its bounded tooling scope
- `docs/planning/` is canonical over `data/planning/`
- `docs/xstack/` and `docs/repo/` are canonical over their machine-readable mirrors
- `packs/` remains canonical in runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/` remains authoritative within authored pack-content declaration scope and must not be erased by convenience

### Derived Or Generated Roots The Preferred Target Must Not Mistake For Authored Truth

- `build/`
- `out/`
- `.xstack_cache/`
- `artifacts/`
- `run_meta/`
- large assembled portions of `dist/`
- generated validation and audit outputs under `docs/audit/` and `data/audit/`

### Mixed Or Operationally Protected Roots

- `tools/` is a mixed host, not one clean owner
- `launcher/` and `setup/` are wrapper-only hosts, not primary product-shell owners
- `saves/` is not authored canon, but it is an operationally protected generated root because the current baseline path depends on it directly
- `docs/audit/` and `data/audit/` mix useful evidence with stale or derived mirrors and therefore require phased treatment rather than blanket cleanup

### Documentation And Report Roots Must Not Masquerade As Runtime Truth

The preferred target preserves the rule that:

- implementation evidence outranks stale docs where they conflict
- audit/report roots are evidence surfaces, not runtime owners
- stale `src/...` path mirrors remain drift to be cleaned later, not structural truth to design around now

## F. Baseline-Path Preservation Analysis

The preferred target preserves the canonical playable-baseline path by keeping the current live seam inside one protected federation rather than forcing it across newly invented containers.

### Verify Build Path

- `verify` remains the canonical compiled lane
- the preferred target does not require a new build-root abstraction before migration planning
- build and test discovery remain tied to current live product and tool roots

### Validation / TestX / CTest Paths

- `python tools/validation/tool_run_validation.py --profile FAST` remains the minimum validation spine
- `python tools/xstack/testx_all.py --profile FAST` remains the XStack/TestX companion
- `ctest --preset verify` remains the compiled companion
- report roots remain derived proof surfaces rather than canonical owners

### Launcher / Setup AppShell Flows

- `appshell/`, `tools/launcher/`, and `tools/setup/` remain inside the same preferred target family
- wrapper-only native `launcher/` and `setup/` roots remain explicitly weaker than the Python/AppShell shells
- release/trust/install-discovery dependencies remain legitimate cross-band dependencies rather than excuses to move the shells

### Session Create / Boot Path

- SessionX create/boot remains protected as one boundary-crossing path instead of being split into new topology buckets
- the save-root disagreement is preserved as a real blocker, not hidden by conceptual cleanup
- generated intermediates such as `build/registries/` and `build/lockfile.json` remain protected transition contracts

### Local Loopback Authority Path

- `client/local_server/`, `runtime/process_spawn.py`, `server/server_main.py`, and `server/net/loopback_transport.py` remain on a protected path family
- the preferred target does not reinterpret the loopback path as an extraction-oriented adapter seam
- direct Python server startup remains blocked truth until fixed explicitly

### Save / Load Baseline Assumptions

- repo-local `saves/<save_id>` remains an operationally protected assumption
- the preferred target does not relocate `saves/` conceptually into a generic derived bucket that later prompts could discard
- current save/load semantics remain visible as fragile but binding current-reality contracts

## G. Why Rejected Options Lost

### Why `TTO-002` Lost The Final Selection

`TTO-002` lost not because it is weak, but because it is too early to make it the preferred target.

It lost on these grounds:

- higher shim burden across `appshell/`, launcher/setup shells, validation, release/trust, and SessionX create/boot
- weaker baseline-path preservation than `TTO-001`
- more conceptual distance from the current live ownership map at the exact moment when the baseline path still has real blockers
- greater risk that later prompts would treat conceptual bands as permission for early physical separation

It remains the strongest non-selected reference model for long-term clarity, but it is not the authoritative preferred target for migration planning.

### Why `TTO-003` Was Not Preferred

`TTO-003` lost because:

- it cuts the current playable-baseline path across too many conceptual seams
- it creates more ownership mismatch around AppShell, launcher/setup, and SessionX than `TTO-001`
- it brings more conceptual churn than protection value
- its Codex ergonomics improve somewhat, but not enough to offset the extra risk and shim burden

### Why `TTO-004` Was Rejected

`TTO-004` remains rejected because:

- it optimizes for extraction-style modularity rather than baseline survival
- it conflicts directly with XStack/AIDE non-interference
- it would normalize platformization and bridge proliferation before the canonical playable baseline exists
- it is the least truthful option about current mixed-root and path-contract reality

## H. Conditional / Not-Yet-Decided Areas

The following remain intentionally open until the migration-plan prompt:

- exact file moves
- exact root renames, if any
- exact shim mechanisms and alias surfaces
- exact staged ordering and rollback points
- exact cleanup timing for stale `src/...` mirrors in docs and reports
- exact breakup of the `tools/` umbrella into sub-ownerships
- exact physical separation inside `client/` and `server/`
- exact future treatment of `launcher/` and `setup/` wrapper leaves
- exact future treatment of `docs/audit/` and `data/audit/`
- exact convergence strategy for `schema/` versus `schemas/`
- exact convergence strategy for `packs/` versus `data/packs/`
- exact resolution of the default bundle seam between authored MVP assets and `bundle.base.lab`
- exact future use of any TTO-002-style boundary names as physical directory names versus conceptual-only documentation bands

## I. Boundaries On Later Prompt Freedom

### What Later Prompts Must Now Treat As The Preferred Target

- the repo’s preferred conceptual target is `PT-001`, which selects `TTO-001 - Stabilized Current-Root Federation`
- later migration planning must assume the current root federation is the protected structural frame
- later prompts may use boundary bands from this packet, but they may not replace the preferred target with a different topology family silently

### What Later Prompts Are Still Free To Choose Within Migration Planning

- exact phased ordering
- exact shim and alias mechanisms
- exact rollback checkpoints
- exact treatment of second-tier mixed roots
- whether some TTO-002-style vocabulary is used as documentation scaffolding during migration, as long as `PT-001` remains the chosen target

### What Later Prompts Must Not Reinterpret

- preferred-target selection as permission to move files immediately
- TTO-002 as secretly co-equal with the selected target
- wrapper-only roots as canonical ownership centers
- split-root cautions as already resolved
- XStack/AIDE closure as permission for extraction-first migration

## J. Anti-Patterns / Forbidden Shapes

- treating preferred-target selection as if the migration plan has already been approved
- using conceptual cleanliness to ignore Omega2 mixed-root and `do_not_move_yet` findings
- treating `launcher/` or `setup/` wrappers as the new product-shell authority center
- hiding `saves/`, `build/registries/`, or `build/lockfile.json` because they are generated rather than authored
- allowing future AIDE extraction aspirations to redefine Dominium-owned boundaries before the baseline exists
- treating the authoritative boundary model as license to collapse `schema/` with `schemas/` or `packs/` with `data/packs/`

## K. Stability And Evolution

- Stability class:
  stable until a later prompt either produces the migration plan for `PT-001` or new baseline-hardening evidence materially changes the selection criteria.
- Later prompts expected to consume this artifact:
  phased migration planning, shim-strategy design, rollback planning, ownership-reconciliation follow-up, and later cleanup checkpoints in this repo-structure series.
- What must not change without explicit follow-up:
  selection of `TTO-001` as the preferred target, the federated boundary-band model, the non-selection of `TTO-002` as the preferred target, the rejection of `TTO-004`, and the list of intentionally undecided areas that must stay open until migration planning.
