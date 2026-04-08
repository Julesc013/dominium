Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: authoritative target-topology option set for later preferred-target selection, shim-design, and migration-sequencing prompts; downstream of stronger canon, the Omega0 constraint packet, the Omega1 topology reality map, the Omega2 coupling-risk packet, audit evidence, and live implementation evidence
Replacement Target: later explicit preferred-target selection or topology checkpoint after baseline-hardening evidence and approval
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `data/repo/repo_non_negotiables_and_current_reality.json`, `docs/repo/REPO_TOPOLOGY_PATHS_AND_OWNERSHIP_REALITY_MAP.md`, `data/repo/repo_topology_paths_and_ownership_reality_map.json`, `docs/repo/REPO_COUPLING_DRIFT_AND_RELAYOUT_RISK_ANALYSIS.md`, `data/repo/repo_coupling_drift_and_relayout_risk_analysis.json`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `CMakePresets.json`, `appshell/paths/virtual_paths.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`, `schema/README.md`, `schemas/README.md`, `packs/README.md`

# Repo Target Topology Options And Comparison

## A. Purpose And Scope

This artifact generates and compares a bounded set of plausible future repository topology options for the live Dominium repo.

It exists because the series now has three different frozen inputs that later design work must consume together rather than implicitly recomputing:

- Omega0 froze the non-negotiable survival rules and current-reality status classes.
- Omega1 mapped the live roots, path contracts, ownership classes, and canonical-versus-derived facts.
- Omega2 measured coupling strength, path drift, shim burden, and baseline-critical relayout risks.

What later prompts still need is the option layer:

- which target topology families are actually plausible
- which ones preserve the canonical playable-baseline path best
- which ones create too much shim burden or false extraction pressure
- which ones should stay in play for preferred-target selection
- which ones should be rejected early

Its relationship to the canonical playable-baseline priority is central:

- every option is judged first on whether it preserves the repo-local session-plus-loopback authority path that the audit and Omega0 require to survive
- no option is allowed to assume that AppShell, the Python launcher/setup shells, SessionX create/boot flow, or the current `saves/<save_id>` assumptions can be casually relocated
- options that only look clean because they ignore baseline-critical couplings are treated as weak or rejected

This artifact does not choose the final topology, does not write migration phases, does not move files, and does not reopen `Ζ` or XStack/AIDE implementation work.

For later repo-structure work, the direct answers are:

- What are the best plausible future repo topology options:
  the four options in Section D.
- What are the strengths, weaknesses, and risks of each:
  Sections D, E, H, and I.
- Which options should be rejected early and why:
  Section F.
- Which options remain plausible and why:
  Section G.
- How does each option affect the canonical playable-baseline path:
  Section H.
- What prompt this enables next:
  preferred-target selection, with a stronger basis for choosing among the surviving option families.

## B. Option-Generation Method

The option set was generated conservatively from the frozen evidence packet rather than from aesthetics.

### How Candidate Topologies Were Generated

Each candidate was produced by changing one major organizing principle at a time while holding Omega0 survival rules constant.

The option families vary along these axes:

- how strongly they preserve the current top-level root federation
- whether they group by live surface type, by lifecycle, or by future modularity ambition
- whether they keep product-shell, substrate, control-plane, and data roots close to their current owners or redistribute them into new umbrellas
- how much they rely on later shims versus immediate physical convergence

### Constraints Every Option Must Satisfy

Every plausible option in this artifact had to satisfy all of the following:

- preserve the `verify` build lane and its role as the canonical compiled lane
- preserve the `FAST` validation lane plus `TestX` and `CTest` continuity
- keep the Python/AppShell launcher and setup shells on a survivable path
- preserve the current session create/boot pipeline, including honest treatment of the current save-root disagreement
- preserve the loopback-authoritative local baseline path
- keep canonical-versus-derived distinctions visible
- avoid silently choosing winners in ownership-sensitive splits such as `schema/` versus `schemas/` and `packs/` versus `data/packs/`
- remain compatible with post-`Ζ` closure and XStack/AIDE non-interference

### Evidence Used From Current Reality And Risk Analysis

The option comparison is grounded primarily in:

- Omega1 ownership and path-contract facts for `appshell/`, `client/`, `server/`, `tools/`, `release/`, `security/`, `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`, `schema/`, and `schemas/`
- Omega2 coupling findings for AppShell, launcher/setup shells, client-local-server loopback, server boot/spawn, session create/boot, validation/report paths, release/trust paths, and the `src` compatibility bridge
- audit guidance that the strongest near-term path is to harden one canonical repo-local playtest command around session creation plus local loopback authority
- governance law that live implementation evidence outranks stale docs and that extension-over-replacement remains binding

### What Makes An Option Plausible Versus Unrealistic

An option is treated as plausible when it:

- explains where today’s baseline-critical seams would live without pretending they are already fixed
- can preserve current build, validation, session, and playtest contracts with a bounded amount of shim or wrapper work
- reflects actual live ownership clusters rather than naming aesthetics alone
- does not require pre-baseline extraction, platformization, or a new competing architecture track

An option is treated as unrealistic or weak when it:

- assumes directory separation already means subsystem isolation
- moves baseline-critical mixed roots without acknowledging the required shims
- treats wrapper-only roots as if they were already canonical owners
- smuggles future AIDE extraction structure into the repo before the baseline exists

## C. Evaluation Criteria

Scores in Section E use a `1` to `5` scale where higher is better.

| Criterion ID | Criterion | Real meaning |
| --- | --- | --- |
| `baseline_path_preservation` | Preservation of canonical playable-baseline path | How well the option preserves the current repo-local session creation plus loopback-authoritative playable path without new fragility. |
| `ownership_fit` | Fit with current ownership reality | How closely the option matches the ownership clusters Omega1 recorded instead of inventing artificial ones. |
| `path_contract_tractability` | Path-contract simplicity | How manageable the current repo-root, save-root, manifest, validation-report, and generated-intermediate contracts would be under the option. |
| `migration_affordability` | Migration cost | How much physical churn, documentation churn, and coordination cost the option would likely impose later. |
| `shim_manageability` | Shim burden | How bounded the likely compatibility shim, alias, wrapper, and report-regeneration burden would be. |
| `flow_safety` | Risk to build, run, test, and session flows | How safely the option can protect the `verify`, validation, launcher/setup, session, and loopback flows during any future relayout. |
| `maintainability` | Maintainability | How well the option reduces mixed-root confusion and creates durable ownership boundaries for humans and tooling. |
| `long_term_modularity` | Long-term modularity | How well the option could support later structural clarity once the baseline is stable, without requiring a fresh redesign. |
| `codex_usability` | Codex usability | How easily a coding agent could locate product surfaces, control-plane surfaces, data inputs, and governance material without mistaking wrappers or mirrors for canon. |
| `xstack_aide_non_interference` | XStack/AIDE non-interference | How well the option avoids creating false pressure toward pre-baseline extraction, platformization, or AIDE-shaped churn. |

## D. Target Topology Options

### `TTO-001 - Stabilized Current-Root Federation`

- High-level directory or boundary model:
  keep the current top-level root family as the future target, but formalize it as an explicit federation of root families instead of treating the whole repo as an accidental sprawl.
- What major roots would conceptually become:
  `appshell/`, `client/`, and `server/` stay the main product-shell and authority roots; `tools/` stays a tool umbrella but with sharper internal ownership for `tools/launcher/`, `tools/setup/`, `tools/xstack/`, and `tools/validation/`; `release/`, `security/`, and `repo/` stay the control-plane cluster; `packs/`, `profiles/`, `locks/`, `data/session_templates/`, and `data/registries/` stay the authored data/config family; `docs/`, `specs/`, `schema/`, and `schemas/` stay governance/contract roots with their current split cautions still explicit.
- What would remain unchanged:
  the current top-level root family, the `verify` preset lane, the Python/AppShell operator shells, the SessionX path family, wrapper-only treatment of `launcher/` and `setup/`, and all current derived roots such as `build/`, `dist/`, `out/`, and `saves/`.
- Why it is plausible:
  it matches Omega0’s survival rules, Omega1’s ownership facts, and Omega2’s risk map most closely; it also aligns best with extend-over-replace doctrine.
- Major strengths:
  lowest baseline-path risk, best fit to current ownership reality, lowest migration cost, and the smallest shim burden.
- Major weaknesses:
  preserves a broad top-level repo, leaves `tools/` and `docs/` mixed longer, and does not deliver the cleanest long-term physical simplification.
- Major risks:
  if later follow-up is weak, mixed-root confusion may persist and stale path narratives may survive longer than necessary.
- What it optimizes for:
  safe baseline preservation, honest current-reality alignment, and incremental convergence after blocker fixes.
- What it sacrifices:
  immediate aesthetic cleanup, strong physical consolidation, and a dramatic reduction in top-level root count.

### `TTO-002 - Surface / Substrate / Control / Content / Governance Lattice`

- High-level directory or boundary model:
  reorganize the future repo around five explicit responsibility zones: surface-facing roots, runtime substrate, control-plane and proof tooling, content/config inputs, and governance/contract material.
- What major roots would conceptually become:
  `surfaces/` would conceptually host AppShell, launcher/setup entry shells, and user-facing orchestration; `substrate/` would conceptually host `client/`, `server/`, `runtime/`, `net/`, and the strongest shared runtime/engine adjacency; `control_plane/` would conceptually host `release/`, `security/`, `updates/`, validation, and XStack/session assembly tooling; `content/` would conceptually host `packs/`, `profiles/`, `locks/`, `data/session_templates/`, and `data/registries/`; `governance/` would conceptually host `docs/`, `specs/`, `repo/`, `schema/`, and `schemas/`.
- What would remain unchanged:
  the `verify` preset family, the requirement for explicit wrapper treatment of native launcher/setup leaves, the current derived roots, and the split cautions around `schema/` versus `schemas/` and `packs/` versus `data/packs/`.
- Why it is plausible:
  it follows the real functional families recorded by Omega1 and Omega2 better than a simple product-versus-libs split, and it offers a coherent long-term owner model without depending on AIDE extraction.
- Major strengths:
  strongest long-term conceptual clarity, best long-term modularity, and the clearest improvement to Codex navigability.
- Major weaknesses:
  requires substantial future shim design because many baseline-critical flows would cross new boundaries; `appshell/`, session tooling, validation, and release/trust would all need very careful protection.
- Major risks:
  if implemented too early or too literally, it would destabilize the launcher/setup shells, session pipeline, and report/manifest path contracts.
- What it optimizes for:
  clearer long-term boundaries and a more legible repo for both humans and tools once the baseline is stable.
- What it sacrifices:
  short-term safety, migration affordability, and immediate simplicity.

### `TTO-003 - Product Shells / Runtime Services / Repo Ops / Content Catalog`

- High-level directory or boundary model:
  group the repo by execution lifecycle: end-user product shells, shared runtime/service machinery, repo-operations and proof tooling, a content/config catalog, and governance material.
- What major roots would conceptually become:
  `products/` would conceptually host `client/`, `server/`, `appshell/`, `launcher/`, and `setup/`; `runtime_services/` would conceptually host `runtime/`, `net/`, `process/`, and distributed runtime/service substrate; `repo_ops/` would conceptually host `release/`, `security/`, `validation/`, and tool surfaces such as `tools/validation/` and `tools/xstack/`; `catalog/` would conceptually host `packs/`, `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`, `schema/`, and `schemas/`; `governance/` would conceptually host `docs/`, `specs/`, and `repo/`.
- What would remain unchanged:
  the `verify` lane, derived roots, and the rule that wrapper-only native launcher/setup leaves remain weaker than the Python/AppShell shells.
- Why it is plausible:
  it respects the fact that `client`, `server`, `launcher`, and `setup` are stable product anchors and that `release`, `security`, and validation already act like repo-operations surfaces.
- Major strengths:
  strong product discoverability, a clearer home for repo-operations and proof tooling, and a workable long-term mental model if the cross-zone seams are handled carefully.
- Major weaknesses:
  the current playable-baseline path would cross too many conceptual zones at once, and the option risks overstating `launcher/`, `setup/`, and `appshell/` as peer product owners.
- Major risks:
  higher shim burden across product, runtime, repo-ops, and catalog seams; greater risk of path confusion around session creation, boot, and save-root ownership.
- What it optimizes for:
  a product-centric navigation model and clearer separation between gameplay surfaces and repo operations.
- What it sacrifices:
  path-contract simplicity, baseline-path compactness, and some ownership truthfulness around AppShell and SessionX.

### `TTO-004 - Extraction-Oriented Platformization Topology`

- High-level directory or boundary model:
  reshape the repo as if a near-term AIDE-style extraction or platform split were already the target, using portability-oriented umbrellas such as platform core, adapters, product surfaces, portable data, and bridge layers.
- What major roots would conceptually become:
  `appshell/`, `tools/`, `runtime/`, `net/`, `release/`, `security/`, and validation would be re-expressed as extraction-friendly platform or adapter layers; Dominium-owned data/config roots would be repackaged as portability-oriented catalogs and bridge inputs.
- What would remain unchanged:
  very little beyond formal doctrine and the requirement that `verify`, `FAST`, and the baseline path still somehow survive.
- Why it is plausible:
  it is a recognizable long-term architectural instinct, and some repo surfaces really are extraction-adjacent.
- Major strengths:
  strongest future-portability story on paper and the highest nominal modularity score if baseline reality is ignored.
- Major weaknesses:
  worst fit to current ownership reality, highest collision with Omega0 and Omega2 risk findings, and the strongest false-alignment pressure toward pre-baseline AIDE work.
- Major risks:
  destabilizes baseline-critical mixed roots, silently reinterprets XStack/AIDE closure as permission to restructure, and invites wrapper or bridge proliferation before the canonical playtest path exists.
- What it optimizes for:
  future extraction readiness and abstraction cleanliness.
- What it sacrifices:
  current-reality truthfulness, baseline safety, migration affordability, and XStack/AIDE non-interference.

## E. Comparison Matrix

Scores use the `1` to `5` scale from Section C, where higher is better.

| Criterion | `TTO-001` | `TTO-002` | `TTO-003` | `TTO-004` |
| --- | --- | --- | --- | --- |
| Preservation of canonical playable-baseline path | `5` | `3` | `2` | `1` |
| Fit with current ownership reality | `5` | `4` | `3` | `1` |
| Path-contract simplicity | `4` | `3` | `2` | `1` |
| Migration affordability | `5` | `3` | `2` | `1` |
| Shim manageability | `4` | `2` | `2` | `1` |
| Flow safety for build/run/test/session | `5` | `3` | `2` | `1` |
| Maintainability | `3` | `5` | `4` | `2` |
| Long-term modularity | `2` | `5` | `4` | `5` |
| Codex usability | `3` | `5` | `4` | `2` |
| XStack/AIDE non-interference | `5` | `4` | `3` | `1` |

### Matrix Reading Notes

- `TTO-001` wins clearly on survivability, migration affordability, and low-risk fit with the current repo.
- `TTO-002` wins clearly on long-term clarity and tool usability, but only if later prompts can absorb the higher shim burden safely.
- `TTO-003` is more coherent than an extraction-first redesign, but it scores worse than `TTO-002` on the current baseline path because it cuts the existing playtest path across more conceptual seams.
- `TTO-004` only looks strong in abstract modularity; it loses badly on every repo-grounded near- and mid-term criterion that matters now.

## F. Early Eliminations / Weak Options

### Reject Early: `TTO-004 - Extraction-Oriented Platformization Topology`

This option should be rejected early for the current series.

Reasons:

- it optimizes for future extraction rather than the current playable-baseline priority
- it conflicts directly with the XStack/AIDE closure rule that existing X-series artifacts act as a constraint packet, not a competing implementation track
- it requires moving or reinterpreting too many Omega2 `do_not_move_yet` surfaces at once
- it would create false pressure to redesign around aspirations rather than around live Dominium ownership and path contracts

### Weak But Not Fully Rejected: `TTO-003 - Product Shells / Runtime Services / Repo Ops / Content Catalog`

This option remains structurally possible, but it is a weaker candidate than `TTO-001` and `TTO-002`.

Reasons:

- it splits the current playable-baseline path across too many conceptual zones
- it risks overstating wrapper and shell roots as peer product owners when Omega1 and Omega2 say some of them are wrapper-only or mixed
- it does not improve baseline-path protection enough to justify its extra coordination burden

Later prompts may still compare against it, but it should enter preferred-target selection as a second-tier option rather than a lead candidate.

## G. Promising Options

### `TTO-001 - Stabilized Current-Root Federation`

This remains promising because:

- it preserves the baseline-critical flows most directly
- it aligns best with current ownership truth and extend-over-replace doctrine
- it creates the least migration pressure while still giving later prompts a real target model

### `TTO-002 - Surface / Substrate / Control / Content / Governance Lattice`

This remains promising because:

- it is the clearest long-term topology family that still respects the current repo’s actual functional clusters
- it reduces mixed-root confusion more than `TTO-001`
- it improves Codex usability and maintainability substantially if it is sequenced after baseline hardening rather than before

### `TTO-003 - Product Shells / Runtime Services / Repo Ops / Content Catalog`

This remains plausible but not leading because:

- it fits some live anchor families well
- it gives a readable lifecycle story
- but it underperforms on baseline-path compactness and seam control compared with `TTO-001` and `TTO-002`

## H. Baseline-Path Impact Analysis

### `TTO-001 - Stabilized Current-Root Federation`

- Build path:
  strongest preservation; the `verify` preset family can remain the canonical compiled lane without major build-path reindexing.
- Validation path:
  preserves `tools/validation/`, `validation/`, `TestX`, `CTest`, and current report roots with the least mirror churn.
- Launcher/setup AppShell flows:
  keeps `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, and `appshell/` on the same protected path family.
- Session create/boot path:
  keeps SessionX surfaces close to today’s contracts, which makes the save-root disagreement easier to harden without topology churn.
- Loopback-authoritative local path:
  preserves the current `client/local_server/` plus `runtime/process_spawn.py` plus `server/server_main.py` plus `server/net/loopback_transport.py` seam directly.
- Save/load baseline assumptions:
  keeps repo-local `saves/<save_id>` and generated intermediates visible as current truth instead of relocating them behind abstraction layers.

### `TTO-002 - Surface / Substrate / Control / Content / Governance Lattice`

- Build path:
  viable later, but only with explicit façade or alias planning so the `verify` lane still locates the same build owners during transition.
- Validation path:
  could simplify long term by giving validation a clearer control-plane home, but immediate report-path and tool-path shims would be required.
- Launcher/setup AppShell flows:
  conceptually clearer because shells live together, but moving `appshell/` and the Python launcher/setup shells too early would be high risk.
- Session create/boot path:
  introduces a hard seam between surface orchestration, substrate runtime, and control-plane session assembly, which is manageable only after the current save-root blocker is resolved.
- Loopback-authoritative local path:
  still workable, but the current local-controller seam would cross more conceptual boundaries and therefore need careful protection.
- Save/load baseline assumptions:
  requires explicit treatment of repo-local `saves/`, `build/registries/`, and `build/lockfile.json` as protected transition contracts.

### `TTO-003 - Product Shells / Runtime Services / Repo Ops / Content Catalog`

- Build path:
  more build-graph churn than `TTO-002`, because product, runtime-service, and repo-ops surfaces all participate in current verification flows.
- Validation path:
  centralizes repo-ops and proof tooling, but risks separating validation too aggressively from the surfaces it proves.
- Launcher/setup AppShell flows:
  puts the launcher/setup/AppShell family in a product bucket, which is attractive for discoverability but can make wrapper-only roots look more canonical than they are.
- Session create/boot path:
  splits session orchestration across product, runtime-service, repo-ops, and catalog zones, which is a poor match to the current fragile path contracts.
- Loopback-authoritative local path:
  weaker than `TTO-001` and `TTO-002` because the current client-local-server seam would cross more boundaries.
- Save/load baseline assumptions:
  risks confusion about whether `saves/` and generated intermediates belong with product runtime, catalog inputs, or repo-ops materialization.

### `TTO-004 - Extraction-Oriented Platformization Topology`

- Build path:
  highest break risk because it would reframe too many live root owners at once.
- Validation path:
  highest report-path and mirror churn, with the added risk of presenting new abstractions as if they were already proved.
- Launcher/setup AppShell flows:
  worst risk of replacing the strongest live shells with architecture-shaped wrappers or bridge layers.
- Session create/boot path:
  highly destabilizing because it pushes session and startup seams toward portability abstractions before current blockers are removed.
- Loopback-authoritative local path:
  weakest fit because it turns the most useful current path into a bridge or adapter story.
- Save/load baseline assumptions:
  most likely to misclassify current `saves/` and generated-intermediate contracts as temporary portability details instead of current baseline truth.

## I. XStack/AIDE Non-Interference Analysis

### `TTO-001`

Strongly compatible with XStack/AIDE non-interference.
It keeps Dominium-owned baseline work centered on the live repo and does not create pressure to restructure around extraction.

### `TTO-002`

Compatible if handled carefully.
It can remain Dominium-internal and baseline-safe if later prompts treat it as a long-term owner lattice rather than as a pre-baseline extraction rehearsal.

### `TTO-003`

Mixed.
It does not explicitly mirror AIDE, but its product-versus-runtime-versus-ops vocabulary could create false pressure toward extraction-style boundaries if later prompts are not disciplined.

### `TTO-004`

Not compatible for the current series.
It bakes future extraction pressure into the topology itself and therefore conflicts directly with the frozen XStack/AIDE closure posture.

## J. Boundaries On Later Prompt Freedom

### What Later Prompts May Choose Among

- a preferred target drawn from `TTO-001`, `TTO-002`, or `TTO-003`
- a constrained hybrid that is explicitly described as a hybrid of `TTO-001` and `TTO-002`, provided it preserves Omega0 survival rules and inherits the documented risks from both families honestly
- a sequencing decision that keeps `TTO-001` as the near-term stabilization shape while using `TTO-002` as the longer-term owner model

### What Later Prompts Must Preserve Regardless Of Option

- the `verify` build lane
- the `FAST` plus `TestX` plus `CTest` proof spine
- the Python/AppShell launcher and setup shells as the strongest current operator surfaces until a stronger proved replacement exists
- the SessionX create/boot path and honest treatment of the current save-root blocker
- the loopback-authoritative local path
- canonical-versus-derived distinctions
- explicit split-root caution around `schema/` versus `schemas/` and `packs/` versus `data/packs/`
- post-`Ζ` closure and XStack/AIDE non-interference

### What Later Prompts Must Not Reinterpret

- wrapper-only roots as if they were already canonical owners
- stale docs or old `src/...` mirrors as structural truth
- XStack/AIDE closure as permission for extraction-first topology work
- Omega2 `do_not_move_yet` findings as if they were only cosmetic annoyances
- long-term modularity as a sufficient reason to weaken baseline-path survival

## K. Anti-Patterns / Forbidden Option Shapes

- options optimized for aesthetics or root-count reduction over baseline-flow survival
- options that relocate `appshell/`, Python launcher/setup shells, SessionX create/boot surfaces, or the local loopback path without acknowledging shim burden and blocker timing
- options that treat `launcher/` and `setup/` native leaves as canonical ownership centers because they look like product roots
- options that silently collapse `schema/` with `schemas/` or `packs/` with `data/packs/`
- options that hide generated-intermediate contracts such as `build/registries/` and `build/lockfile.json`
- options that assume a new container such as `platform/`, `src/`, or `products/` automatically simplifies current path contracts
- options that bake future AIDE extraction into the target shape before the canonical playable baseline exists

## L. Stability And Evolution

- Stability class:
  stable until a later prompt either selects a preferred target or new baseline-hardening evidence changes the relative risk profile of the options.
- Later prompts expected to consume this artifact:
  preferred-target selection, shim-strategy design, migration-sequencing design, and ownership-reconciliation prompts in this repo-structure series.
- What must not change without explicit follow-up:
  the option identities, the comparison criteria meanings, the early rejection of `TTO-004`, the second-tier posture of `TTO-003`, and the promising status of `TTO-001` and `TTO-002` unless new repo evidence materially changes the tradeoffs.
