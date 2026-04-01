Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Ρ, Λ
Replacement Target: revised only after Ρ-2 and Ρ-3 reconcile current reality against blueprint intent
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`, `docs/planning/AUTHORITY_ORDER.md`, `data/planning/snapshot_intake_policy.json`

# Reality Extraction Report

## 1. Basis

This report treats the repository as a live post-Ω/Ξ/Π snapshot.
It is the first evidence-gathering pass for Ρ-series planning and is intentionally classification-only.

The extraction follows the P-0 intake rules:

- canon, glossary, and `AGENTS.md` remain the semantic and repository-execution floor
- live repo structure is structurally authoritative for existence, location, and wiring claims
- schema law in `schema/**` outranks validator projections in `schemas/**` if they disagree
- generated or build-output echoes are recorded as evidence surfaces, not silently treated as canonical truth
- transitional, duplicate-shadow, and quarantine-candidate areas remain visible rather than flattened away

## 2. Current Architectural Character

The repo is not a clean single-language tree.
It is a mixed but intentional architecture with several strong existing centers:

- a CMake-driven product surface with concrete executable roots in `client`, `server`, `launcher`, `setup`, and `tools`
- a shared runtime spine across `engine`, `game`, `app`, `libs`, `compat`, `control`, `core`, `net`, and `process`
- a large Python governance/control/tooling ecosystem spanning `appshell`, `release`, `repo`, `tools`, `scripts`, `worldgen`, and many semantic roots
- heavy machine-readable contract surfaces in `schema`, `schemas`, `data/registries`, `data/architecture`, `packs`, `data/packs`, `updates`, and `repo`
- explicit mixed-state residue in `legacy`, `attic/src_quarantine`, `quarantine`, `build`, `artifacts`, `out`, `run_meta`, and `.xstack_cache`

This means later prompts should plan for convergence and extension, not pretend the repo has only one implementation lineage.

## 3. Major Families

| Family | Major Roots | Character |
| --- | --- | --- |
| Products | `client`, `server`, `launcher`, `setup`, `tools`, `appshell` | Concrete app/operator surfaces already exist; most C/C++ products are registered in CMake and `appshell` adds a Python orchestration shell. |
| Shared runtime and platform | `engine`, `game`, `app`, `runtime`, `compat`, `control`, `core`, `net`, `process`, `lib`, `libs` | Mixed runtime backbone with both compiled and Python surfaces. |
| Control-plane and release | `release`, `repo`, `updates`, `security`, `governance`, `data/architecture`, `data/registries`, `tools/xstack`, `tools/release`, `tools/distribution`, `tools/compatx`, `tools/controlx`, `tools/securex` | Strong evidence that release, compat, update, archive, and governance directions are already embodied. |
| Semantic and world domains | `game/content/core`, `worldgen`, `geo`, `reality`, `materials`, `machines`, `logic`, `signals`, `system`, `universe`, `astro`, `embodiment`, `epistemics`, `diegetics`, `mobility`, `physics`, `pollution` | Broad domain surface already exists in raw form and is not confined to one root. |
| Schemas, registries, and manifests | `schema`, `schemas`, `data/registries`, `data/architecture`, `packs`, `data/packs`, `updates`, `repo` | Extensive machine-readable declaration layer, but with visible dual-structure coexistence. |
| Toolchain and automation | `CMakeLists.txt`, `CMakePresets.json`, `cmake`, `scripts`, `tools/ci`, `setup/packages/scripts`, `.github/workflows/ci.yml` | Strong automation surface spanning build, validation, IDE projection, packaging, and CI profiles. |
| Governance and planning | `AGENTS.md`, `docs/planning`, `docs/blueprint`, `docs/agents`, `docs/xstack`, `docs/governance`, `GOVERNANCE.md` | Repo contains multiple instruction layers; only some are planning-authoritative. |
| Transitional, legacy, and generated residue | `legacy`, `attic/src_quarantine`, `quarantine`, `build`, `artifacts`, `.xstack_cache`, `dist`, `run_meta` | Explicit archaeology and generated-output zones that must remain non-canonical unless separately promoted. |

## 4. Product and Application Roots

The compiled product family is concrete rather than hypothetical:

- `client` defines `dominium_client` from `client/app/main_client.c` and related app, input, UI, presentation, and observability sources, then registers the product through `dom_register_product(client dominium_client)`.
- `server` defines `dominium_server` from `server/app/main_server.c` plus authority, net, shard, persistence, and runtime code, then registers the product through `dom_register_product(server dominium_server)`.
- `launcher` provides a shared `launcher_core` plus CLI, GUI, TUI, and Win32 entrypoints, with `launcher_cli` registered as the product entry.
- `setup` mirrors that pattern with `setup_core`, CLI, GUI, TUI, and Win32 entrypoints, with `setup_cli` registered as the product entry.
- `tools` is a real product root, not just incidental utilities. `tools/CMakeLists.txt` defines `dominium-tools`, registers it as `tools`, and also builds many specialized domain/operator executables.
- `appshell` is not wired through the same CMake product registration path, but it is a real operator shell surface with bootstrap, mode dispatch, supervisor, IPC, diagnostics, and TUI modules.

`app` is a strong shared support layer rather than a standalone user-facing product.
Its `app::runtime` library is linked into `client`, `server`, and `tools`, which makes it an extension-over-replacement candidate later.

## 5. Runtime, Service, and Component Surfaces

Several existing roots already point toward a kernel/service/component direction:

- `engine` is the strongest compiled runtime anchor, with `include`, `modules`, `platform`, `render`, `time`, concurrency, and tests.
- `game` is the content/rules companion runtime with `content`, `mods`, `rules`, and tests.
- `core` contains schedule, graph, state, spatial, and hazard subdomains that look like runtime substrate rather than mere docs.
- `compat` and `control` are explicit live roots for negotiation, lifecycle, proof, fidelity, capability, and planning concerns.
- `net` contains transport, anti-cheat, policies, and serialization-related surfaces.
- `server/runtime`, `server/net`, and `server/persistence` show server-side orchestration, network, and state retention already separated at least at the directory level.
- `runtime` itself is present but currently thin, so it is real but lower-confidence as a canonical ownership root than `engine`, `app`, or `server/runtime`.
- `libs/contracts` and `libs/appcore` provide cross-product contract and application-core surfaces that later prompts should prefer extending over re-inventing.
- `tools/inspect` and `tools/observability` already form concrete inspection and replay-facing service/tool surfaces.

The repo therefore already embodies service and component ideas in multiple places.
Later prompts should reconcile these surfaces instead of inventing them from scratch.

## 6. Control-Plane, Release, Update, and Trust Surfaces

The control-plane direction is already materially present:

- `release` contains `archive_policy.py`, `build_id_engine.py`, `component_graph_resolver.py`, `release_manifest_engine.py`, and `update_resolver.py`.
- `repo` contains `release_policy.toml`, `canon_state.json`, and `repox` rulesets, which directly signal repository governance and release control.
- `updates` contains channel manifests for `stable`, `beta`, `nightly`, `pinned`, plus `changelog.json`.
- `data/architecture` holds architecture and module graph artifacts such as `architecture_graph.json`, `module_dependency_graph.json`, `module_registry.json`, and `repository_structure_lock.json`.
- `data/registries` is a very large machine-readable control surface including component graph, compat, process, and many policy registries.
- `tools/xstack` is a major automation and control umbrella with `ci`, `compatx`, `controlx`, `packagingx`, `repox`, `securex`, `sessionx`, `testx`, and `auditx`.
- `tools/release`, `tools/distribution`, `tools/compatx`, `tools/controlx`, and `tools/securex` provide concrete operator/tooling implementations for those control concerns.
- `security/trust` provides a live trust-verification surface.
- `docs/release` and `docs/governance` provide scoped doctrine that later prompts can use conditionally, not blindly.

This area looks like one of the strongest extension-over-replacement zones in the entire repo.

## 7. Semantic, Content, and World Surfaces

The semantic/domain landscape is already broad and non-trivial:

- `game/content/core` provides a clear baseline content surface with `astro`, `cosmo`, and `mechanics` data.
- `worldgen` is a strong domain root with `core`, `earth`, `galaxy`, `mw`, and refinement surfaces.
- `geo`, `reality`, `materials`, `machines`, `logic`, `signals`, `system`, and `universe` are all live top-level semantic roots with engine-like files, not empty placeholders.
- `astro`, `chem`, `electric`, `embodiment`, `epistemics`, `diegetics`, `mobility`, `physics`, and `pollution` expand the domain model rather than merely documenting it.
- `packs/domain`, `packs/experience`, and `packs/law` show that semantic content is also expressed through pack manifests and data assets, not only code roots.

This matters for later Λ-series work: semantic roots already exist across both code and pack surfaces, so future semantic planning should bridge them instead of replacing them wholesale.

## 8. Schemas, Registries, Manifests, and Machine-Readable Contracts

The repo contains a dense declaration layer with several coexisting surfaces:

- `schema/**` appears to hold schema law, governance prose, and semantic/compatibility doctrine.
- `schemas/**` appears to hold machine-readable schema projections and validator-facing exports.
- `data/registries/**` is the largest registry surface and includes control, compat, component graph, and domain registries.
- `data/architecture/**` is a smaller but high-signal graph and module-registry surface.
- `packs/**` contains pack descriptors such as `pack.json`, `pack.compat.json`, `pack.capabilities.json`, and `pack.trust.json`.
- `data/packs/**` contains another pack declaration family with `pack.toml`, `pack.manifest`, and `pack_manifest.json`.
- `updates/*.json` and `repo/release_policy.toml` are machine-readable control artifacts for release/update behavior.

The most important coexistence risk here is not hypothetical:

- `schema/**` and `schemas/**` both exist
- `packs/**` and `data/packs/**` both exist
- build outputs also echo schemas under generated trees such as `build/**/schemas`

P-0 authority rules therefore matter immediately for Ρ-2.

## 9. Toolchain, Preset, and CI Surfaces

The toolchain surface is large and active:

- root `CMakeLists.txt` orchestrates the suite and defines multi-product, verification, and distribution targets
- `CMakePresets.json` contains modern dev, verify, release, platform-specific, and legacy projection families
- `cmake/toolchains/**` and `cmake/ide/**` show explicit multi-target and IDE projection support
- `.github/workflows/ci.yml` runs repo sanity, xstack FAST/STRICT/FULL profiles, projection sanity, docs sanity, and matrix build/test jobs
- `scripts/**` and `tools/ci/**` contain a wide set of verification scripts
- `setup/packages/scripts/**` contains packaging, staging, schema freeze, layer-check, and launcher invariant automation
- `tools/xstack/out/**`, `artifacts/toolchain_runs/**`, and many `build/**` subtrees show generated output and audit residue

This repo already behaves like a governed toolchain and distribution workspace, not just a code tree.

## 10. Agent and Governance Surfaces

The repo has a visible guidance stack:

- root `AGENTS.md` is the strongest repo-execution instruction surface after canon/glossary
- `docs/planning/**` now contains P-0 intake doctrine and, after this prompt, P-1 extraction output
- `docs/blueprint/**` contains the current blueprint/planning archive that later Ρ prompts must reconcile against reality
- `docs/agents/**` contains a substantial doctrine set for agent concepts and lifecycle
- `docs/xstack/**` and `docs/governance/**` provide process, guardrail, and prompt-firewall style policy surfaces
- `GOVERNANCE.md`, `SECURITY.md`, `CONTRIBUTING.md`, `README.md`, and `DOMINIUM.md` add collaborator-facing guidance

No `CLAUDE.md` or Copilot instruction file was observed in the live snapshot.

## 11. Transitional, Legacy, and Quarantine Candidates

Several areas are explicitly risky for silent planning errors:

- `legacy/**` contains multiple mirrored product/core families such as `engine_core_dominium`, `launcher_core_launcher`, and `setup_core_setup`
- `attic/src_quarantine/**` is an explicit quarantine root and must stay non-canonical without manual review
- `quarantine/README.md` signals an explicit quarantine surface even though the root is currently small
- `build/**`, `artifacts/**`, `out/**`, `run_meta/**`, and `.xstack_cache/**` contain large generated or cached evidence surfaces
- `field/**` and `fields/**` both exist with overlapping `field_engine.py` naming, which is a duplicate-shadow risk
- `schema/**` versus `schemas/**` is an explicit P-0 quarantine trigger if material disagreements appear
- `packs/**` versus `data/packs/**` is not automatically a conflict, but it is a clear coexistence zone that later prompts must classify carefully

## 12. Old/New Coexistence Patterns

The strongest coexistence patterns visible now are:

- compiled product roots plus Python orchestration and policy/tooling roots
- live runtime roots plus mirrored legacy product/core trees
- schema-law prose plus machine schema projections
- pack descriptors in `packs/**` plus separate pack declarations in `data/packs/**`
- current source roots plus generated evidence copies under build and artifact trees

This is a converging repo, not yet a single fully normalized one.

## 13. Questions Later Prompts Should Be Careful About

### 13.1 Where does the repo already embody a kernel/service/component direction?

Primarily in `engine`, `app`, `core`, `compat`, `control`, `net`, `server/runtime`, `libs/contracts`, and the data/registry/component-graph surfaces under `data/architecture` and `data/registries`.

### 13.2 Where do product/application roots already align with component graph and install-profile ideas?

In the registered products `client`, `server`, `launcher`, `setup`, and `tools`, plus the release/update/component graph surfaces in `release`, `repo`, `updates`, `data/architecture`, and `data/registries`.

### 13.3 Where does the repo already embody release/update/trust/control-plane ideas?

Most strongly in `release`, `repo`, `updates`, `security/trust`, `tools/xstack`, `tools/release`, `tools/distribution`, `tools/compatx`, `tools/controlx`, `tools/securex`, and scoped docs under `docs/release` and `docs/governance`.

### 13.4 Where do semantic/world/domain roots already exist in raw form?

Across `game/content/core`, `worldgen`, `geo`, `reality`, `materials`, `machines`, `logic`, `signals`, `system`, `universe`, `astro`, `embodiment`, `epistemics`, `diegetics`, `mobility`, `physics`, and pack families under `packs/domain`, `packs/experience`, and `packs/law`.

### 13.5 Where do old and new structures appear to coexist?

Most clearly in `legacy/**` versus live roots, `schema/**` versus `schemas/**`, `packs/**` versus `data/packs/**`, and the presence of build/output echoes beside current source trees.

### 13.6 Where are the biggest duplication or shadow-ownership risks?

`field` versus `fields`, `schema` versus `schemas`, `legacy` product mirrors versus live product roots, and any generated `build/**/schemas` copies being mistaken for source-of-truth material.

### 13.7 Which areas look most promising for extension rather than replacement later?

- registered product roots in `client`, `server`, `launcher`, `setup`, and `tools`
- shared support surfaces in `app`, `engine`, `game`, `libs/contracts`, and `libs/appcore`
- release/control surfaces in `release`, `repo`, `updates`, `data/architecture`, `data/registries`, and `tools/xstack`
- semantic pack and domain roots in `packs/**`, `game/content/core`, `worldgen`, `geo`, and related domain roots

## 14. Care Rules For Ρ-2 And Ρ-3

Later prompts should not:

- infer canonical ownership from naming alone
- treat generated outputs as live authority without provenance
- silently resolve `schema/**` versus `schemas/**`
- silently collapse `legacy/**` mirrors into live ownership
- assume every present domain root is already canonical just because it is outside `legacy/**`

Later prompts may assume:

- the post-Ω/Ξ/Π repo already has concrete product, control-plane, schema, pack, and domain surfaces
- the repo is mixed-state and must be reconciled, not reimagined
- future work should prefer extension-over-replacement where existing roots are already strong and wired into build, release, or registry flow
