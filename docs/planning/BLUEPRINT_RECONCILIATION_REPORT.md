Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Ρ, Λ, Σ, Φ, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`, `docs/planning/AUTHORITY_ORDER.md`, `data/planning/snapshot_intake_policy.json`, `docs/planning/REALITY_EXTRACTION_REPORT.md`, `data/planning/reality/module_map.json`, `data/planning/reality/product_entrypoints.json`, `data/planning/reality/runtime_surfaces.json`, `data/planning/reality/control_plane_surfaces.json`, `data/planning/reality/content_domain_surfaces.json`, `data/planning/reality/toolchain_and_preset_map.json`, `data/planning/reality/agent_instruction_surfaces.json`, `data/planning/reality/schema_registry_inventory.json`

# Blueprint Reconciliation Report

## 1. Purpose and Basis

This report reconciles the live repository as a post-Ω/Ξ/Π snapshot against the currently frozen blueprint and doctrinal expectations. Its purpose is not to refactor the repository, but to convert extracted repo reality into an explicit decision layer that later prompts can use safely.

The reconciliation baseline is:

- Ω expectations: runtime and ecosystem freeze, MVP canonicalization, deterministic truth discipline, and pack-driven compatibility boundaries.
- Ξ expectations: convergence pressure, anti-drift governance, architecture graph direction, and explicit ownership boundaries.
- Π expectations: planning structure, dependency-aware sequencing, and audit-grade prompt discipline.
- Semantic and reality doctrine expectations: Assemblies / Fields / Processes / Law ontology, Truth / Perceived / Render separation, total truth with sparse materialization, epistemic and diegetic refinement, and first-class civilization / institution / knowledge modeling.

The governing rule for this report is simple: blueprint is not allowed to erase live repo evidence, and repo reality is not allowed to erase frozen doctrine.

## 2. Classification Logic

The classification buckets are used in the strict P-2 sense:

- `keep`: the surface already matches blueprint direction strongly enough to preserve as-is and build on.
- `extend`: the surface is directionally correct but underformalized, partial, or missing connective tissue.
- `merge`: multiple surfaces appear to split a single conceptual responsibility and should later be reconciled without discarding useful work.
- `replace`: the current shape is misleading or structurally wrong enough that later work should derive a different canonical surface.
- `quarantine`: evidence is insufficient, conflict risk is high, or human review is required before later prompts may depend on it.

These judgments follow the P-0 authority rules and the repo-reality-first guidance in `docs/blueprint/REPO_REALITY_RECONCILIATION_GUIDE.md`. The machine-readable registries are sorted deterministically by subsystem family and surface name.

## 3. Blueprint Families Reconciled

### 3.1 Runtime and Ecosystem Freeze Expectations

The strongest existing alignment remains the engine and game baseline, the compiled product roots, deterministic contract surfaces, and the pack/registry-backed release spine. The repo already contains substantial runtime-adjacent substrate, but not yet the single explicit orchestrator and service layer imagined by the runtime diagram.

### 3.2 Repo Convergence and Anti-Drift Expectations

The repository already embodies strong anti-drift direction through `AGENTS.md`, `docs/planning`, `tools/xstack`, `data/architecture`, `data/registries`, and the release/update policy stack. The biggest convergence gaps are not missing governance, but split ownership zones such as `schema` versus `schemas`, `packs` versus `data/packs`, and `field` versus `fields`.

### 3.3 Meta-Blueprint and Dependency Expectations

Π assumed later series would formalize many surfaces that the repo now already partially embodies. That does not eliminate later work, but it does change the work from invention to disciplined extraction, extension, and merge planning.

### 3.4 Semantic and Reality Doctrine Expectations

The semantic/domain side is materially embodied already. The repo contains broad reality, world, material, signal, logic, diegetic, epistemic, and pack-backed domain roots. Later Λ work should formalize and connect these surfaces, not imagine them from nothing.

## 4. Family-by-Family Reconciliation

### 4.1 Products and Applications

Keep:

- `client`
- `server`
- `launcher`
- `setup`

These compiled roots align with the engine/game/client/server boundary discipline and already act like stable product surfaces.

Extend:

- `tools`
- `appshell`

The repo already has operator and utility application surfaces, but their product boundaries and relationship to later Σ operator-facing planning are still underformalized.

### 4.2 Runtime, Service, and Component Candidates

Keep:

- `engine`
- `game`

These are the strongest existing embodiment of the runtime blueprint and should be preserved as foundation surfaces.

Extend:

- `app`
- `compat`
- `control`
- `core`
- `net`
- `process`
- `libs/appcore`
- `libs/contracts`
- `server/runtime`
- `server/net`
- `server/persistence`
- `tools/inspect`
- `tools/observability`

These surfaces already contain runtime, service, contract, orchestration, and observability precursors. Later Φ should formalize them into clearer component and service boundaries rather than replace them wholesale.

Replace:

- `runtime`

The thin `runtime` root does not currently function as the obvious canonical orchestrator anchor implied by some blueprint sketches. Later Φ should derive the orchestrator layer from the distributed substrate that already exists instead of pretending this root is already the right canonical center.

### 4.3 Release, Update, Trust, and Control Plane

Keep:

- `release`
- `repo`
- `updates`
- `data/architecture`
- `data/registries`
- `tools/xstack`

This cluster strongly matches the Ξ and Π anti-drift and control-plane direction. It is already useful enough that later Υ should consolidate and extend it rather than reinvent the control plane.

Extend:

- `governance`
- `security/trust`
- `tools/release`
- `tools/distribution`
- `tools/compatx`
- `tools/controlx`
- `tools/securex`

These surfaces show that release, trust, compatibility, and operator policy ideas are not theoretical anymore, but they are not yet reduced to a single clean operational model.

Quarantine:

- `run_meta`
- `artifacts`
- `build`
- `.xstack_cache`

These are valuable evidence and projection surfaces, but not safe canonical control-plane ownership surfaces on their own.

### 4.4 Semantic, Domain, World, and Civilization Roots

Extend:

- `worldgen`
- `geo`
- `reality`
- `materials`
- `logic`
- `signals`
- `system`
- `universe`
- `game/content/core`
- `packs/domain`
- `packs/experience`
- `packs/law`
- `epistemics`
- `diegetics`
- `infrastructure`
- `machines`
- `mobility`
- `embodiment`
- `astro`
- `physics`
- `pollution`
- `chem`
- `electric`

These surfaces demonstrate substantial semantic embodiment already. Later Λ should formalize cross-surface semantics, truth ladders, and institutional/world modeling around this material instead of replacing it.

Merge:

- `field`
- `fields`

The repo shows duplicate-shadow ownership around field-like concepts. This is a merge target, not a safe silent canonicalization target.

### 4.5 Schemas, Registries, Manifests, and Policy Surfaces

Keep:

- `schema`
- `data/architecture`
- `data/registries`
- `repo/release_policy.toml`
- `packs`

These surfaces already look like the strongest machine-readable law, registry, and compatibility backbone in the current repo.

Extend:

- `ide/manifests`

This surface appears useful and directionally aligned, but secondary to the core law and registry roots.

Merge:

- `packs`
- `data/packs`

The repo appears to split pack ownership between a canonical runtime-facing pack root and a transitional data-facing mirror. Later reconciliation should unify ownership intentionally rather than let both drift.

Quarantine:

- `schemas`

The repo clearly contains both `schema` and `schemas`. Under P-0 authority rules, `schema` retains semantic authority while `schemas` cannot be treated as independently canonical until mapping and disagreement status are explicitly resolved.

### 4.6 Toolchain, Presets, and Automation

Keep:

- `CMakeLists.txt`
- `CMakePresets.json`
- `cmake`
- `scripts`
- `setup/packages/scripts`
- `.github/workflows/ci.yml`

The repo already has a broad build and automation backbone. Later Υ should reduce ambiguity and projection clutter, but it should start from this spine rather than imagine a new one.

Extend:

- `cmake/toolchains`
- `cmake/ide`
- `ide/manifests`

These surfaces are directionally correct and valuable, but later toolchain consolidation should formalize how they relate to the canonical build graph and distribution policy.

Quarantine:

- `tools/xstack/out`

This is a derived output surface and should not silently become the authoritative build graph.

### 4.7 Agent, Governance, and Instruction Surfaces

Keep:

- `AGENTS.md`
- `docs/planning`

These are already acting as the live governance and planning authority stack for post-Π work.

Extend:

- `docs/blueprint`

The blueprint archive is still valuable, but P-2 shows several of its implicit assumptions now need reconciliation guards before later prompts consume it directly.

Merge:

- `docs/agents`
- `docs/governance`
- `docs/xstack`
- `DOMINIUM.md`
- `GOVERNANCE.md`
- `README.md`
- `SECURITY.md`

These guidance surfaces contain value, but they split operator, contributor, and governance narratives across multiple documents. Later Σ should harmonize them rather than add yet another parallel instruction layer.

### 4.8 Legacy, Duplicate-Shadow, and Quarantine Zones

Quarantine:

- `legacy`
- `attic/src_quarantine`
- `quarantine`

These roots remain visible and potentially useful for later human review, but they cannot be treated as canonical ownership evidence.

Merge:

- `field`
- `fields`
- `packs`
- `data/packs`

These are the highest-confidence split-ownership zones visible in the live tree.

Quarantine:

- `schema`
- `schemas`

This pair is a special-case conflict zone: `schema` remains the stronger law surface, but the pair as a relationship is not safe to collapse automatically.

## 5. Major Mismatches Between Blueprint and Repo Reality

The largest mismatches are not failures of architecture, but failures of simplification:

- The blueprint often speaks as if runtime/service foundations are mostly future work, but the repo already contains a broad substrate of runtime-adjacent roots and tooling.
- The blueprint often speaks as if control-plane and governance structure are still largely to be built, but the repo already contains strong release, registry, update, trust, and XStack-backed governance surfaces.
- The blueprint sometimes assumes a cleaner single-root model than the repo actually has. Real ownership is split in several places and must be reconciled deliberately.
- The blueprint correctly predicted the need for runtime orchestration, service boundaries, and semantic formalization, but the repo already contains precursor surfaces that later work should extend rather than replace.

## 6. Assumptions Invalidated or Weakened

The strongest invalidations are:

- the repo can no longer be reasoned about as if only a tiny number of source-like roots matter
- runtime/service precursor surfaces are not absent
- release and control-plane structure is not purely theoretical
- semantic/domain embodiment is not absent
- schema and pack ownership are not single-root and unambiguous
- duplicate-shadow risk is not confined to explicit legacy roots

See `data/planning/reconciliation/assumption_invalidations.json` for the operational registry.

## 7. What Later Prompts Must Not Overwrite

Later prompts should not overwrite or bypass:

- the engine/game/client/server boundary foundations already present
- the `release` / `repo` / `updates` / `data/architecture` / `data/registries` / `tools/xstack` control spine
- the `schema` law root and explicit compatibility metadata doctrine
- the pack-driven integration backbone in `packs`
- the live semantic/domain roots that later Λ work must formalize
- the P-0 intake and authority rules

Later prompts must also avoid silently collapsing any of the known split-ownership zones.

## 8. Priority Extension-Over-Replacement Surfaces

The highest-value extension surfaces are:

- `app`, `compat`, `control`, `core`, `net`, `process`, `libs/appcore`, `libs/contracts`, and `server/runtime` for later Φ work
- `release`, `repo`, `updates`, `data/architecture`, `data/registries`, and `tools/xstack` for later Υ work
- `worldgen`, `geo`, `reality`, `materials`, `logic`, `signals`, `system`, `universe`, `packs/domain`, `packs/experience`, `packs/law`, `epistemics`, and `diegetics` for later Λ work
- `tools`, `appshell`, and the merged governance doc stack for later Σ work

## 9. Human Review Requirements

Human review is required before later execution depends on:

- the `schema` versus `schemas` relationship whenever semantic ownership is materially disputed
- the `packs` versus `data/packs` ownership split
- the `field` versus `fields` split
- any attempt to treat `legacy`, `attic/src_quarantine`, or `quarantine` as live canonical evidence
- any attempt to promote derived output roots such as `build`, `artifacts`, `.xstack_cache`, or `tools/xstack/out` into canonical ownership surfaces

## 10. Direct Answers to the Mandatory Reconciliation Questions

1. The areas that already embody the Ω/Ξ/Π direction strongly enough to preserve are the compiled product roots, the engine/game baseline, the schema/registry/release spine, the pack root, and the AGENTS plus planning plus XStack governance stack.
2. The clearest transitional coexistence zones are `packs` with `data/packs`, `schema` with `schemas`, `field` with `fields`, and the live repo with `legacy` or quarantine roots.
3. Later Σ should use `tools`, `appshell`, `AGENTS.md`, `docs/planning`, `tools/xstack`, and the existing governance and operator tooling instead of inventing a new operator surface from scratch.
4. Later Φ should extract and formalize the `app` / `compat` / `control` / `core` / `net` / `process` / `libs/appcore` / `libs/contracts` / `server/runtime` substrate rather than replace it wholesale.
5. Later Υ should consolidate `release`, `repo`, `updates`, `data/architecture`, `data/registries`, `tools/xstack`, and the compatibility and trust tooling cluster rather than reinvent them.
6. Later Λ should formalize the already-visible reality and domain roots, especially `worldgen`, `geo`, `reality`, `materials`, `logic`, `signals`, `system`, `universe`, `packs/domain`, `packs/experience`, `packs/law`, `epistemics`, and `diegetics`.
7. The most visible duplicate ownership risks are `schema` versus `schemas`, `packs` versus `data/packs`, `field` versus `fields`, and the generated evidence echoes under `build`, `artifacts`, `.xstack_cache`, and `tools/xstack/out`.
8. The most important stale planning assumptions are that runtime/service surfaces are mostly absent, control-plane structure is mostly theoretical, semantic/domain embodiment is mostly future-only, and the repo can still be reasoned about through a small-root simplification.
9. The later series most blocked on quarantine items are Φ and Υ for schema and pack ownership, and Λ for field-like semantic ownership and any disputed schema semantics.
10. The strongest extension-over-replacement priorities are the distributed runtime substrate, the release and registry spine, and the existing semantic/domain roots.
