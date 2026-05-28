Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Part IX - Current High-Authority Docs


## Source: `README.md`

### Dominium / Domino

Dominium is a deterministic, contract-governed simulation game and operating
environment built on the Domino deterministic substrate.

The project is about invention, production, logistics, economics, settlement,
trust, communication, and institutional power emerging from lawful simulation
rather than scripted outcomes. Commands, processes, packs, capabilities,
diagnostics, evidence, and replay proof are first-class surfaces. Invalid action
must refuse explicitly; hidden fallback behavior is not part of the model.

#### Home Point

Use this README as the project home point. It orients the product, repository,
and common proof commands. It is not the highest authority.

Authority starts here:

- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- Agent governance: `AGENTS.md`
- Canon index: `docs/architecture/CANON_INDEX.md`
- Current queue: `.aide/queue/current.toml`
- Foundation status: `docs/repo/FOUNDATION_LOCK.md`
- Build guide: `docs/development/guides/BUILDING.md`
- Test tiers: `contracts/testing/test_tiers.contract.toml`
- Public surface registry: `contracts/public_surface/public_surface.contract.toml`

Repo artifacts outrank chat memory, generated echoes, convenience summaries, and
old planning notes.

#### Current State

Current committed program position:

- Foundation Lock: `PASS_WITH_WARNINGS`.
- Post-wave queue state: `post_wave_1_pass_with_warnings`.
- Completed narrow Workbench validation slice:
  `WORKBENCH-VALIDATION-SLICE-01`.
- Current next task: `COMMAND-RESULT-VIEW-SLICE-01`.
- Alternate next task: `PACKAGE-MOUNT-SLICE-01`.
- Secondary follow-up: `POINTER-WIDTH-SERIALIZATION-AUDIT-01`.

The current queue does not authorize broad feature work. Broad Workbench UI,
runtime module loading, provider runtime, package runtime, gameplay, renderer
implementation, native GUI, and release publication remain blocked until later
reviewed phases explicitly open them.

#### What This Is

Domino is the reusable deterministic substrate: execution, ordering, storage,
replay, ABI-facing boundaries, and other engine mechanisms.

Dominium is the official game, product, and domain layer on top of Domino. It
defines rules, process meaning, law targets, domain interpretation, authored
content use, and product composition.

Workbench is the richest operator environment for validation, evidence,
inspection, and later editing workflows. It consumes the same contracts and
services as other products; it is not an authority layer.

AIDE and Codex are repo/control-plane harnesses and bounded patch execution
surfaces. They help operate the repository; they do not replace canon,
contracts, validation, or evidence.

#### What This Is Not

Dominium is not a monolithic game executable, a renderer-owned simulation, a
traditional mode-flag game, a silent fallback system, or a place where generated
output becomes source truth by convenience.

It is also not currently release-ready. Full CTest and broader release/trust
proof remain visible debt outside the normal fast strict development gate.

#### Core Invariants

- Determinism first: identical canonical inputs produce identical authoritative
  outputs.
- Process-only mutation: authoritative truth changes only through lawful,
  deterministic Process execution.
- Truth / perceived / render separation: truth is authoritative; perception is
  law-filtered; rendering is presentation only.
- Profiles over mode flags: behavior composition comes from profiles, bundles,
  law surfaces, and constraints, not hardcoded runtime mode forks.
- Explicit refusal: unsupported or invalid transitions return deterministic,
  auditable refusal.
- Pack-driven integration: optional content and capabilities are declared by
  packs, contracts, registries, and compatibility law.
- Public identity is contractual: paths and implementations are not public
  surfaces unless registered as such.

#### Semantic Spine

The reusable truth is not a button, screen, renderer, or tool. The reusable truth
is the contract-governed surface:

```text
intent
-> command
-> capability/refusal check
-> service or deterministic process
-> result | document | snapshot
-> diagnostics/evidence
-> view/action model
-> projection
-> shell
```

CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench panels, CI,
and AIDE should project the same command/result/refusal/diagnostic/evidence
truth rather than inventing separate product behavior.

#### Product Shape

- `apps/client/`: client product composition, input, perception, and
  presentation shell.
- `apps/server/`: authoritative server product composition and admin/headless
  surfaces.
- `apps/launcher/`: profiles, instances, compatibility, and launch
  orchestration.
- `apps/setup/`: install, repair, rollback, and local product configuration.
- `apps/workbench/`: governed validation, evidence, inspection, and later
  authoring workflows.
- `tools/`: validators, migration tools, packaging helpers, codegen, audit, and
  developer machinery.

Apps compose. Runtime implements reusable behavior. Contracts define law.
Content supplies authored payload. Tools validate, generate, migrate, and audit.

#### Repository Map

- `apps/`: thin product entrypoints and product composition.
- `engine/`: Domino deterministic substrate and public engine-facing surfaces.
- `game/`: Dominium domain rules, process emission, and game interpretation.
- `runtime/`: AppShell, platform, shell, UI/projection adapters, diagnostics,
  storage, input, audio, network, and host integration.
- `contracts/`: machine-readable, version-pinned, compatibility-sensitive law.
- `content/`: authored packs, profiles, datasets, fixtures-as-content, assets,
  templates, and source content payloads.
- `docs/`: canon, architecture, development, reference, planning, release, and
  repo documentation.
- `tests/`: contract, invariant, smoke, integration, fixture, and proof suites.
- `tools/`: repo-only validation, packaging, migration, release, audit, and
  developer tooling.
- `archive/`: historical, superseded, quarantined, or provenance-retained
  material.

Ownership-sensitive split reminders:

- Do not infer ownership from similarly named roots.
- Follow `AGENTS.md` and scope-specific contract/planning artifacts before
  binding new work to transitional, projected, or quarantined roots.
- Generated outputs are evidence unless a stronger source promotes them.

#### Language And Platform Baseline

Mainline source uses:

- C17 for C code.
- C++17 for C++ code.
- C-compatible public ABI boundaries for stable binary-facing surfaces.

The active portability floor includes Windows 7 SP1, macOS 10.9.5, and Linux.
C++17 language mode is allowed, but public ABI surfaces do not expose C++
classes, STL types, exceptions, RTTI, allocator objects, or compiler object
layout.

See:

- `docs/development/LANGUAGE_BASELINE.md`
- `docs/development/C17_USAGE_POLICY.md`
- `docs/development/CPP17_USAGE_POLICY.md`
- `docs/development/MACOS_10_9_CPP17_LIBRARY_SUBSET.md`
- `contracts/abi/c_api.contract.toml`
- `contracts/abi/language_boundary.contract.toml`

#### Build And Verify

Configure and build the normal verify preset:

```powershell
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
```

Run the normal development proof gate:

```powershell
py -3 tools/test/run_fast_strict.py --repo-root .
```

Run AIDE local health checks:

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
```

Run targeted contract validators as needed:

```powershell
py -3 tools/validators/repo/check_dependency_directions.py --repo-root . --strict
py -3 tools/validators/contracts/check_command_surface.py --repo-root . --strict
py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
py -3 tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict
```

Fast strict is the normal development gate. Extended, release, and full proof
tiers are separate gates defined by `contracts/testing/test_tiers.contract.toml`.
A green fast strict result does not claim full certification.

#### Contracts And Public Surfaces

Public identity must be registered and versioned. A file path, implementation,
or generated artifact is not public merely because it exists.

Core contract entrypoints:

- Public surfaces: `contracts/public_surface/public_surface.contract.toml`
- Commands: `contracts/command/command_surface.contract.toml`
- Views: `contracts/view/view_surface.contract.toml`
- Diagnostics: `contracts/diagnostic/diagnostic_code.registry.json`
- Refusals: `contracts/refusal/refusal_code.registry.json`
- Capabilities: `contracts/capability/capability.registry.json`
- Modules: `contracts/module/module_surface.contract.toml`
- Providers: `contracts/provider/provider.contract.toml`
- Services: `contracts/service/service.contract.toml`
- Project graph: `contracts/project_graph/project_graph_model.contract.toml`
- Packages and packs: `contracts/package/`
- Replay proof: `contracts/replay/`

When behavior or compatibility meaning changes, update the relevant contract
surface and proof in the same task.

#### Content, Packs, And Modding

Content is authored data, not runtime law. Packs and registries describe optional
content, capabilities, compatibility, activation, and distribution surfaces.
Missing optional content must degrade or refuse explicitly.

Start with:

- `MODDING.md`
- `content/README.md`
- `content/packs/README.md`
- `contracts/package/packs/README.md`
- `contracts/capability/README.md`

Early pack tiers should remain data-first. Arbitrary executable code in packs is
not part of the current trust model.

#### Documentation Map

Use canon and contracts first, then architecture and development docs for
implementation guidance.

- Product overview: `DOMINIUM.md`
- Documentation root: `docs/README.md`
- Canonical system map: `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- Services and products: `docs/architecture/SERVICES_AND_PRODUCTS.md`
- Foundation status: `docs/repo/FOUNDATION_LOCK.md`
- Current queue: `.aide/queue/current.toml`
- Workbench validation slice: `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- Document/patch transactions: `docs/architecture/document_patch_transaction.md`
- Project graph service: `docs/architecture/project_graph_service.md`
- Build matrix: `docs/development/BUILD_MATRIX.md`
- Build guide: `docs/development/guides/BUILDING.md`

Old docs are retained for provenance, but canon, glossary, AGENTS, active
contracts, current queue state, and reviewed audits outrank stale references.

#### Contributing

Before substantive work, identify the governing class and authority documents.
Use the task invocation shape from `AGENTS.md`:

```text
Task:
Goal:
Touched Paths:
Relevant Invariants:
Contracts/Schemas:
Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

For ordinary bounded work:

1. Read the relevant canon, contract, and ownership documents.
2. Keep edits in the owning root.
3. Update contracts/schemas when behavior or compatibility meaning changes.
4. Run targeted validation plus `git diff --check`.
5. Run fast strict when scope warrants it or when claiming gate status.
6. Report what was run and what was not run.

See `CONTRIBUTING.md` for contributor workflow notes, but resolve conflicts
against canon, glossary, AGENTS, and active contracts.

#### License And Security

- License: `LICENSE.md`
- Security policy: `SECURITY.md`


## Source: `docs/README.md`

Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

### Dominium Documentation

#### Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/archive/audit/CANON_MAP.md` and `docs/archive/audit/DOC_DRIFT_MATRIX.md`.


Status: current.
Scope: high-level orientation and map.

Normative contracts live under `docs/architecture/` only. All other docs are
guidance, reference, or historical context.

#### Core mental model

- The simulation kernel is the source of truth; perception layers are derived.
- Objective snapshots record authoritative state; subjective snapshots record views.
- Packs provide capabilities, data, and assets; executables do not embed content.
- Determinism and replay-first design are mandatory.

#### Where to start

- `docs/architecture/WHAT_THIS_IS.md`
- `docs/architecture/WHAT_THIS_IS_NOT.md`
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/CONTRACTS_INDEX.md`

#### Documentation taxonomy

- `docs/architecture/` binding contracts and laws
- `docs/release/roadmap/` goals and coverage tests only
- `docs/content/` data and pack explanation only
- `docs/development/` developer how-to only
- `docs/modding/` modding how-to only
- `docs/archive/` historical and superseded docs only

#### Archival notes

Archived documents are kept for provenance only. Canonical contracts are in
`docs/architecture/`.


## Source: `AGENTS.md`

Status: CANONICAL
Last Reviewed: 2026-04-02
Supersedes: prior `AGENTS.md` v1.0.0 legacy control contract
Superseded By: none
Stability: stable
Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta
Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`

### Dominium Agent Governance

#### 1. Purpose And Scope

`AGENTS.md` is the single canonical governance source for how humans, GPT/Codex agents, Claude-style agents, Copilot-style agents, MCP-mediated tools, and future execution prompts are allowed to operate in this repository.

It governs:

- authority precedence for repo-grounded work
- current program-state orientation for post-`Lambda` execution
- core operating rules and non-negotiable execution constraints
- high-level work classes
- validation and reporting expectations
- review-gated and ownership-sensitive areas

It does not yet define:

- generated mirrors or vendor-specific instruction surfaces
- the natural-language task bridge
- the XStack task catalog
- MCP exposure contracts
- the final hardened agent safety policy

Those later surfaces must inherit from this file instead of inventing a parallel governance canon.

#### 2. Authority Model

When repo artifacts, mirrors, generated outputs, and chat memory differ, use the following rule:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. scope-specific canonical planning, semantic, schema, contract, release, and policy artifacts named by the active task
5. operational registries, projections, mirrors, manifests, and generated evidence with intact provenance
6. chat summaries, remembered transcript claims, and uncommitted planning notes

The governing consequences are:

- repo artifacts outrank chat memory
- canon and glossary outrank all lower-level prose
- mirrors are derived, not canonical
- generated outputs are evidence only unless a stronger source explicitly promotes them
- if repo artifacts conflict materially, resolve the conflict with `docs/planning/AUTHORITY_ORDER.md` and `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md` rather than by convenience
- chat summaries may orient work, but they may not override repo truth

#### 3. Current Program State

The current committed execution position is:

- `Omega`, `Xi`, and `Pi` complete
- `P-0` through `P-4` complete
- `0-0` planning hardening complete
- `Lambda-0` through `Lambda-6` complete
- current checkpoint: `post-Lambda / pre-Sigma-A`
- current executable prompt: `Sigma-0`
- current execution block: `Sigma-A`

Governance work must therefore consume the completed `Lambda` doctrine rather than invent a new semantic baseline.

Continuity note:

- some older planning artifacts still retain pre-`Sigma` or earlier `Sigma` ordering text
- for governance execution, treat the active executable prompt and this file as the canonical post-`Lambda` governance baseline until downstream planning mirrors are refreshed
- do not silently rewrite broader planning artifacts just to erase that drift unless a prompt explicitly targets them

#### 4. Core Operating Rules

All humans and agents operating in this repo must follow these rules:

- extend over replace unless stronger doctrine or explicit human direction says otherwise
- do not introduce silent semantic drift
- do not bypass authority ordering, gate logic, or review checkpoints
- do not infer canon from convenience, shared code, or generated output shape
- do not replace repo truth with chat summaries or remembered intent
- do not silently rebind work to projected, generated, transitional, or quarantined roots
- planning-only prompts do not authorize runtime, refactor, or implementation work
- implementation-facing prompts do not authorize doctrine rewrites unless they explicitly target doctrine

#### 5. Constitutional Execution Floor

The following inherited rules remain non-negotiable:

##### 5.1 No mode flags; profiles only

- do not add or preserve hardcoded runtime mode branches
- express behavior composition through profiles, bundles, law surfaces, and explicit constraints

##### 5.2 Process-only mutation

- authoritative truth mutation must occur through lawful deterministic Process execution
- UI, render, operator, tooling, or convenience layers must not mutate truth directly

##### 5.3 Truth / Perceived / Render separation

- truth is authoritative
- perception and observation are filtered views
- rendering is presentation only
- later governance and tool work must not collapse those layers

##### 5.4 Pack-driven integration

- optional content and capabilities must remain pack- and registry-driven
- missing packs require explicit refusal or degradation rather than hidden fallback magic

##### 5.5 Determinism discipline

- use named RNG streams for authoritative randomness
- preserve thread-count invariance, deterministic ordering, and deterministic reductions
- preserve replay-hash equivalence for canonical partitions where applicable

##### 5.6 Contract and compatibility discipline

- respect explicit schema identity, version, stability, migration, and refusal obligations
- do not perform silent migrations or compatibility reinterpretation
- update contract-facing docs when behavior or compatibility meaning changes

#### 6. Required Doctrine Inputs Before Acting

Before substantive work, agents must consult the relevant authoritative repo artifacts for the task. At minimum, the normal doctrine packet is:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/POST_PI_EXECUTION_PLAN.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- the relevant `Lambda` semantic constitution artifacts under `specs/reality/` and `data/reality/`
- `contracts/planning/final_prompt_inventory.json`
- `contracts/planning/dependency_graph_post_pi.json`

Task-specific additions are mandatory when scope expands:

- schema or compatibility work: `schema/**`, `docs/reference/contracts/**`, compat metadata
- release or control-plane work: `docs/release/**`, `contracts/repo/release_policy.toml`, release and update registries
- runtime extraction work: relevant runtime roots plus ownership review and bridge law
- bridge or ownership-sensitive work: `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md` before binding to overlapping roots

#### 7. Work Classes

The repository recognizes these high-level work classes:

- `planning`: sequencing, checkpoints, inventories, dependency maps, gates, and continuity work
- `doctrine_spec`: normative constitutional, contract, or specification work
- `governance`: agent, operator, instruction, refusal, and review-surface work
- `semantic_domain`: reality, domain, capability, representation, formalization, or bridge work
- `runtime_platform`: kernel, component, event, service, persistence, sandbox, or platform-boundary work
- `release_control_plane`: release, build, versioning, identity, trust, archive, publication, or control-plane work
- `packaging_checkpointing`: bundle, report, manifest, and checkpoint-curation work
- `validation_audit`: verification, consistency, evidence, audit, and proof work
- `refactor_convergence`: physical convergence, replacement, merge-later, or structure-normalization work

High-level task intent mapping is refined later. This file only defines the canonical class vocabulary and the minimum expectations attached to each class.

#### 8. Validation And Reporting Expectations

Before claiming success, agents must:

1. state the relevant invariant documents or IDs being upheld
2. state whether contract or schema impact changed
3. use `FAST` validation at minimum unless the task is docs-only and explicitly exempt from stronger checks
4. verify that the target artifacts required by the prompt exist
5. parse touched JSON or schema artifacts where relevant
6. check internal consistency between prose and machine-readable mirrors when both are produced
7. run `git diff --check`
8. report what was run and what was not run
9. avoid claiming implementation progress on planning-only prompts

Validation strength must increase when task scope increases. A docs-only task does not excuse false claims about unrun runtime or build checks.

#### 9. Review-Gated And Protected Areas

Explicit human review is required for work that:

- changes canon doctrine or glossary meaning
- reinterprets authority ordering, intake law, or this governance baseline
- touches replace-classified or do-not-replace surfaces in ways that exceed the prompt
- crosses unresolved or quarantined ownership areas
- changes release, publication, licensing, trust, or public policy meaning
- enters live-ops or `Zeta`-class territory
- alters foundational semantic meaning without an explicit doctrine-update prompt

Protected or caution-heavy zones include:

- `docs/canon/**`
- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `specs/reality/**`
- `schema/**`
- `docs/release/**`
- `release/**`, `repo/**`, `updates/**`, `security/**`
- generated echoes under `build/**`, `archive/generated/artifacts/**`, `.xstack_cache/**`, and `run_meta/**`

Protected does not mean untouchable. It means explicit scope, review awareness, and provenance discipline are required.

#### 10. Ownership And Projection Cautions

Agents must not assume the following ownership-sensitive roots are equivalent peers:

- `fields/` is canonical semantic field substrate; `field/` is a transitional compatibility facade
- `schema/` is canonical semantic contract law; `schemas/` is a validator-facing projection or advisory mirror
- `packs/` is canonical in runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/` remains authoritative within authored pack content and declaration scope, but stays transitional and residual-quarantined for any attempted single-root convergence
- `specs/reality/` is canonical over `data/reality/`
- `docs/planning/` is canonical over `data/planning/`

Agents may not:

- silently bind new governance, runtime, task, or bridge work to the wrong side of those splits
- treat projections as semantic owners because they are easier to consume
- collapse residual quarantine into certainty by naming preference

#### 11. Relation To Later Sigma Work

This file is intentionally canonical but not overloaded.

Later `Sigma` prompts refine derived surfaces only:

- `Sigma-1` generates governance mirrors from this canonical source
- `Sigma-2` formalizes high-level task intent and natural-language mapping
- `Sigma-3` freezes the XStack task catalog
- `Sigma-4` formalizes MCP and related interface exposure
- `Sigma-5` hardens the agent safety policy

No later `Sigma` prompt may create a competing governance canon. They must refine or project this layer.

#### 12. Commit Discipline

When tracked repository files change:

- make frequent commits at meaningful boundaries
- use explicit, verbose, audit-grade commit messages
- write commit messages that are sufficient to reconstruct a later changelog
- do not invent commits for ignored or untracked checkpoint outputs only

#### 13. Forbidden Moves

The following moves are forbidden unless a prompt explicitly authorizes them and the required review conditions are met:

- creating a parallel canonical governance file
- treating mirrors as canonical
- bypassing doctrine to "just get it done"
- replacing repo truth with prompt convenience or chat memory
- refactoring code during planning-only work
- binding runtime, governance, or release work to quarantined roots without review
- silently promoting generated outputs into semantic authority
- silently normalizing ownership drift because two roots look similar

<!-- AIDE-PORTABLE:BEGIN section=aide-lite-pack-v0 mode=managed -->
#### AIDE Lite Portable Guidance

- Use `.aide/context/latest-task-packet.md` as the default compact AIDE task brief when a task explicitly opts into AIDE Lite context.
- Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
- Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`; keep Dominium doctrine referenced by path instead of pasted into prompt memory.
- Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed Dominium task explicitly enables them.
<!-- AIDE-PORTABLE:END section=aide-lite-pack-v0 -->

#### 14. Task Invocation Template

Use this block when framing future work:

```text
Task:
Goal:
Touched Paths:
Relevant Invariants:
Contracts/Schemas:
Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

<!-- AIDE-GENERATED:BEGIN section=aide-token-survival-adapter target=codex_agents_md generator=aide-adapter-compiler-v0 version=q24.existing-tool-adapter-compiler.v0 source_template=.aide/adapters/templates/AGENTS.md.template mode=managed_section manual=outside-only fingerprint=sha256:634e820ddcf7d8251a9f42ddb51f7eab306ce2f0daf36bedbdae2df568663698 -->
#### AIDE Existing-Tool Adapter: Codex

- Use `.aide/context/latest-task-packet.md` as the default task brief.
- Use `.aide/context/latest-context-packet.md` for compact repo refs when the
  task packet points there.
- Do not paste long chat history, full repo dumps, raw prompts, raw responses,
  secrets, provider keys, or `.aide.local/` contents.
- Prefer exact repo refs and line refs over copied file bodies.
- Before substantive work, run `py -3 .aide/scripts/aide_lite.py doctor`,
  `validate`, and `pack --task "<bounded task>"` when available.
- For quality-sensitive work, run `verify`, `review-pack`, `eval run`, and
  evidence checks before review or promotion.
- For Q27-and-later work, use structured commits and run `commit check` when
  practical.
- Inspect `task status` or `task inspect` before repeated, partial, or
  out-of-order queue work.
- Run `git plan` before branch-sensitive work; do not mutate branches without
  an explicit helper plan, validation evidence, and operator approval.
- Treat routine git/worktree drift as a mechanical blocker, not a terminal
  stop: fetch or fast-forward when safe, preserve unrelated changes, continue
  path-disjoint work, and create or resume an AIDE blocker-resolution task for
  remaining drift.
- For validation, dependency, stale-generated-output, and dirty-tree blockers,
  create or resume a bounded AIDE task before reporting blocked; ask the user
  only for semantic authority conflicts, destructive ambiguity, missing
  external secrets, or required review gates.
- Treat Gateway and provider surfaces as no-call/report-only unless a future
  reviewed queue phase explicitly enables live execution.
- Write evidence, preserve manual content, stop at review gates, and report
  validation honestly.
<!-- AIDE-GENERATED:END section=aide-token-survival-adapter -->


## Source: `docs/canon/constitution_v1.md`

Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/glossary_v1.md` v1.0.0.
Stability: stable
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

### Dominium Constitutional Architecture & Execution Contract v1

#### 1) Purpose
This document is the binding constitutional contract for Dominium architecture and execution.
If any code, schema, tool, prompt, or documentation conflicts with this contract, this contract wins.

#### 2) Authority Order
Apply this order when interpreting requirements:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md` (repo root)
4. Schema law under `schema/` and contract docs under `docs/reference/contracts/`
5. Architecture docs under `docs/architecture/`
6. Roadmap and testing docs

#### 3) Constitutional Axioms (Non-Negotiable)

##### A1. Determinism is primary
- Authoritative simulation outcomes MUST be identical for identical inputs.
- Step-by-step and batched execution MUST remain equivalent.
- Thread count, scheduler interleavings, and backend choice MUST NOT change authoritative outputs.

##### A2. Process-only mutation
- Authoritative state mutation MUST occur only through deterministic Process execution.
- Direct writes outside Process commit boundaries are forbidden.
- Tooling MAY request mutation only through lawful intent/process paths.

##### A3. Law-gated authority
- Capability grants permission to attempt; law determines accept/refuse/transform.
- Authority does not bypass law.
- Refusals are lawful outcomes and MUST be explicit, deterministic, and auditable.

##### A4. No runtime mode flags
- Runtime behavior MUST resolve from profile data (`ExperienceProfile`, `LawProfile`, `ParameterBundle`, optional `MissionSpec` constraints).
- Hardcoded mode booleans/branches (for example `*_mode` runtime forks) are forbidden.

##### A5. Event-driven advancement
- Simulation advances via scheduled events and deterministic task execution.
- Hidden background mutation and global per-tick scans that mutate state are forbidden.

##### A6. Provenance is mandatory
- Creation, mutation, transfer, and destruction MUST have deterministic causal chains.
- Save/replay/audit artifacts MUST preserve that provenance.

##### A7. Observer-Renderer-Truth separation
- Truth is authoritative state.
- Perception is a law/authority/lens-filtered projection.
- Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions.

##### A8. Engine/Game/Client/Server boundaries
- Engine defines deterministic mechanisms.
- Game defines rule meaning through engine contracts.
- Client and renderer project data and issue intents; they do not author authoritative outcomes.
- Server is authoritative in multiplayer and validates law/authority context.

##### A9. Pack-driven integration
- New content and capability surfaces integrate through packs and registries.
- Packs are data-only and namespaced; executable code inside packs is forbidden.
- Missing optional packs MUST produce deterministic refusal or deterministic degradation.

##### A10. Explicit degradation and refusal
- Budget pressure MAY defer/degrade/refuse.
- Silent fallback is forbidden.
- Degradation and refusal outcomes MUST be inspectable and auditable.

##### A11. Absence is valid
- Systems MUST remain lawful with optional subsystems absent (for example: no AI, no economy, no war).
- Absence MUST produce explicit behavior, never hidden bypasses.

#### 4) Execution Contract (EXEC0 Family)

##### E1. Work IR and Access IR
- Authoritative work MUST be expressed as Work IR + Access IR contracts.
- Task ordering keys, read/write/reduce declarations, and commit points MUST be explicit.

##### E2. Deterministic ordering
- Canonical commit key: `(phase_id, task_id, sub_index)`.
- Ordering decisions MUST be independent of hash-map iteration, pointer order, or thread completion order.

##### E3. Deterministic reductions
- Reductions MUST use fixed-tree deterministic reduction.
- Float-based authoritative reductions are forbidden.

##### E4. Named RNG streams
- Authoritative randomness MUST use named streams.
- Anonymous/global RNG and time-seeded randomness are forbidden.
- Stream naming and derivation MUST follow deterministic RNG law.

##### E5. Thread-count invariance
- Authoritative outputs and partition hashes MUST remain invariant across allowed thread counts.

##### E6. Replay equivalence
- Replay from authoritative logs MUST reproduce canonical authoritative hashes.
- Replay drift is a contract failure.

##### E7. Hash-partition equivalence
- Canonical partitions (`HASH_SIM_CORE`, `HASH_SIM_ECON`, `HASH_SIM_INFO`, `HASH_SIM_TIME`, `HASH_SIM_WORLD`) MUST match across equivalent runs.
- Presentation hash divergence is non-authoritative unless explicitly promoted.

##### E8. SRZ contract
- Execution placement (server/delegated/dormant) changes where work runs, never what law permits.
- Delegated execution requires deterministic proof artifacts before commit.

##### E9. Commit legality
- Any state transition that cannot be expressed under deterministic ordering, legal authority context, and auditable commit semantics is invalid.

#### 5) Compatibility, Schema, and Migration Obligations

##### C1. Version semantics
- All runtime-impacting schemas MUST declare `schema_id`, `schema_version`, and `stability`.
- MAJOR changes require explicit migration routes or explicit refusal.

##### C2. Skip-unknown preservation
- Unknown fields MUST round-trip unchanged where contract says open-map/extension behavior.

##### C3. CompatX obligations
- Compatibility classes and migration links MUST be explicit and data-declared.
- Breaking transitions require deterministic migration specs and tests.

##### C4. No silent coercion
- Migration is explicit invoke-only.
- Best-effort guessing, silent dropping, and implicit semantic defaulting are forbidden.

#### 6) Testing and Invariant Obligations Per Task
Every non-trivial task MUST include:

1. Referenced invariants (by doc and section).
2. Contract impact statement (which schemas/contracts changed or confirmed unchanged).
3. Determinism impact statement (ordering, RNG, replay/hash partitions).
4. Validation execution (`FAST` at minimum, stricter when scope requires).
5. Document updates for any changed contractual behavior.

#### 7) Refusal and Enforcement
- Violations of constitutional invariants require refusal or rollback of the change request.
- Workarounds that bypass invariants are forbidden.
- Constitutional conflicts are resolved by this document, not by prompt convenience.

#### 8) Future Task Invocation Template
Use this prompt block for future work so tasks remain short and stable:

```text
Task ID:
Objective:
Touched Paths:
Relevant Invariants:
Required Contracts:
Required Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

#### 9) Primary Cross-References
- `docs/canon/glossary_v1.md`
- `docs/architecture/ARCH0_CONSTITUTION.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/EXECUTION_REORDERING_POLICY.md`
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/SRZ_MODEL.md`
- `docs/architecture/MODES_AS_PROFILES.md`
- `docs/architecture/RENDERER_RESPONSIBILITY.md`
- `docs/governance/COMPATX_MODEL.md`
- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_MIGRATION.md`

#### 10) TODO
- Add invariant ID tags for each constitutional clause to support machine traceability.
- Add formal contract map from each constitutional clause to enforcing RepoX/TestX checks.


## Source: `docs/canon/glossary_v1.md`

Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0 (Normative)
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0.
Scope: Dominium / Domino ecosystem vocabulary.
Stability: stable
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

### Dominium Canonical Glossary v1.0.0

This is the full canonical glossary v1.0.0.
If terminology conflicts with local or legacy docs, this glossary wins.

#### Glossary Invariants
- Terms in this document are canonical and binding for contracts, schemas, code comments, and prompts.
- Deprecated terms must not be introduced in new runtime logic.
- If a term is undefined here, it must not be treated as canonical until added through controlled update.

#### Example Usage
```text
Correct: "The Observation Kernel maps TruthModel through Lens and AuthorityContext."
Incorrect: "Renderer owns truth and can mutate state."
```

#### TODO
- Add a machine-readable term registry export format.
- Add change-control procedure for glossary term additions/deprecations.

#### Cross-References
- `docs/canon/constitution_v1.md`
- `AGENTS.md`

#### A

##### Account
A user identity external to the simulation ontology used for authentication, entitlements, and multiplayer coordination. An Account is not an Agent unless explicitly instantiated as one within the simulation.

##### Activation Policy
A deterministic rule set defining when a Domain, Solver, or Micro-simulation may activate within a region of interest.

##### Agent
An Assembly capable of submitting Intents under AuthorityContext and LawProfile constraints.

##### Architecture
The structural layering of Dominium systems including Engine, Game, Client, Server, and XStack governance components.

##### Artifact
A produced output from a build, verification, simulation, or governance process.

##### Artifact Class
The classification of artifacts into Canonical, Derived, or Run-meta categories.

##### Authority
Permission to execute Processes under Law. Authority is not power; it is validated capability within constraints.

##### AuthorityContext
The structured permission context required for all Process execution. Includes authority_origin, law_profile_id, entitlements, epistemic_scope, and privilege_level.

##### AuthorityOrigin
The origin of authority: client, server, tool, replay, etc.

##### Authority tick
The evaluation step where AuthorityContext is validated before Process execution.

##### AuditX
The static analysis subsystem within XStack responsible for detecting drift, anti-patterns, and semantic violations.

#### B

##### Bad
Normatively incorrect or violating the Constitutional Architecture, invariants, or determinism.

##### Binary
A compiled executable or library artifact.

##### Budget Envelope
The deterministic compute constraints governing simulation cost per region, session, or tick.

##### Budget Policy
A registry-driven configuration defining solver activation and fidelity under compute constraints.

##### Bug
A deviation from deterministic, lawful, or architectural correctness.

##### Build
The deterministic compilation and linking process producing Binaries.

##### Bundle
A collection of Packs grouped for installation or activation.

##### BundleProfile
A declarative definition of grouped Packs, tools, or experiences.

#### C

##### Cache store
Persistent content-addressed storage of verification or computation results keyed by input hash.

##### Canon
The locked architectural truth of Dominium.

##### Canonical
Conforming strictly to Canon and deterministic identity.

##### Canonical artifact
A source-of-truth artifact that must not change without explicit migration.

##### Canonical hash
A deterministic hash representing canonical state.

##### Capability
A specific permission or affordance enabling a Process.

##### CLI
Command Line Interface.

##### Classroom-restricted
A SecureX trust category restricting certain Packs or features to educational environments.

##### Client
The application responsible for rendering, input capture, and presentation of PerceivedModel.

##### Collapse
Reduction of simulation detail into a Macro Capsule while preserving invariants.

##### CompatX
The XStack subsystem enforcing compatibility and migration rules.

##### Compatibility
The ability to maintain deterministic behavior across versions.

##### Conservation guarantee
The requirement that physical and logical invariants are preserved across simulation tiers.

##### Contract
A normative rule set defining allowed behaviors and invariants.

##### ControlX
The orchestration and planning subsystem of XStack.

##### Creative
An ExperienceProfile representing expanded construction authority governed by LawProfile.

#### D

##### Debug
An ExperienceProfile or entitlement allowing diagnostic access.

##### Debug panel
A non-diegetic interface enabled only under explicit LawProfile.

##### Deprecated
A term or pattern forbidden for use in code identifiers.

##### Determinism
The property that identical inputs produce identical state hashes.

##### Deterministic packaging
Packaging process producing bitwise identical artifacts given identical inputs.

##### Derived artifact
An artifact deterministically generated from canonical artifacts.

##### Dev
Developer environment context.

##### Diegetic Lens
A Lens existing within simulation ontology and accessible to Agents.

##### Diegetic UI
A UI representation existing as in-world instrument or Assembly.

##### Distribution
A packaged form of Binaries and Packs for release.

##### Domain
A modular simulation subsystem representing a coherent phenomenon (e.g., climate).

##### Domain registry
A canonical registry listing all active Domains.

##### Drift
Deviation from Canon or structural invariants.

#### E

##### Editor
An ExperienceProfile permitting scenario or blueprint modification.

##### Engine
Domino, the deterministic universe simulation core (C17 mainline with C-compatible public ABI).

##### Entitlement
A permission token within AuthorityContext.

##### Epistemic scope
The boundary of information accessible to an Agent.

##### Expand
Increase simulation detail from Macro Capsule to Micro-simulation.

##### Execution plan
A deterministic sequence of verification or simulation actions.

##### Execution Profile
FAST, STRICT, or FULL verification profile.

##### ExperienceProfile
Defines presentation defaults, allowed lenses, and LawProfile bindings.

##### Extensible
Capable of expansion via Domain packs without refactor.

#### F

##### Fake
A representation not grounded in simulation ontology.

##### FAST
Incremental verification profile prioritizing speed.

##### Feature
A declared addition conforming to Canon.

##### Fidelity
Resolution level of solver approximation under conservation contract.

##### Fidelity Boundary
The transition interface between solver tiers.

##### Fidelity policy
Registry defining solver tier activation rules.

##### Field
A deterministic property over space/time or Assembly.

##### File
A stored data or code unit within the repository.

##### Fixed-point math
Deterministic arithmetic representation used by Engine.

##### Forwards compatible
Ability to run older saves in newer versions with migration.

##### Forbidden
Explicitly disallowed by Canon or RepoX.

##### Frame tick
Presentation update cycle distinct from simulation tick.

##### Future proof
Architecturally designed to allow extension without refactor.

#### G

##### Game
Dominium, the C++17 gameplay layer atop Domino.

##### GBN
Global Build Number for release tracking.

##### Glossary
This authoritative normative definition set.

##### Good
Conforming to Canon and invariants.

##### GUI
Graphical User Interface.

#### H

##### Hardcore
LawProfile with stricter constraints and no respawn.

##### HUD
Heads-up display; non-diegetic unless explicitly diegetic via instrument.

#### I

##### Identity
Stable deterministic identifier for Universe or Assembly.

##### Identity fingerprint
Canonical hash representing identity invariants.

##### Impact graph
Dependency mapping from file changes to verification scope.

##### Instance
A running SessionSpec execution context.

##### Interest radius
Spatial boundary determining Micro-simulation activation.

##### Interest region
Region under detailed simulation.

##### Invariant
A rule that must always hold.

##### Issue
Tracked deviation or defect.

#### L

##### Lab
An ExperienceProfile for experimentation.

##### Law
Constraint system governing Process execution.

##### LawProfile
Declarative rule set enabling/disabling Processes and lenses.

##### Lens
Transformation from TruthModel to PerceivedModel.

##### LOD
Level of Detail; fidelity level in presentation or simulation.

#### M

##### Macro
Aggregate simulation layer.

##### Macro Capsule
Aggregate representation preserving invariants.

##### Macro-simulation
High-level simulation of aggregates.

##### Merkle hash tree
Content-addressed hashing system for subtree change detection.

##### Metric
A quantitative measurement within simulation or verification.

##### Micro
Detailed simulation layer.

##### Micro-simulation
Fine-grained simulation of Assemblies and Fields.

##### MissionSpec
Declarative mission definition with predicates.

##### Mod
Third-party Pack extending Domain or content.

##### Modular
Composed of replaceable independent components.

#### N

##### Named RNG Stream
Deterministic pseudo-random sequence identified by name.

##### Non-diegetic Lens
Lens external to simulation ontology.

##### Non-diegetic UI
UI not existing within ontology.

#### O

##### Observation artifact
Deterministic output of Observation Kernel.

##### Observation Kernel
Function mapping `TruthModel x Lens x LawProfile x AuthorityContext -> PerceivedModel`.

##### Official
Pack signed and verified by SecureX.

##### Observer
ExperienceProfile allowing non-mutating observation.

##### Overlay
Presentation layer component rendered over scene.

#### P

##### Pack
Modular content or Domain extension unit.

##### Package
Bundled distribution artifact.

##### ParameterBundle
Numeric tuning configuration.

##### Parity
Consistency across CLI, TUI, GUI.

##### PerformX
Performance enforcement subsystem.

##### Pipe dream
Speculative future feature not yet implemented.

##### Platform
Target operating environment.

##### Process
The sole mutation mechanism.

##### Process-only mutation
Invariant prohibiting mutation outside Process.

##### Profile
Generic term referring to LawProfile or ExperienceProfile.

##### Program
Executable binary.

##### Privilege level
AuthorityContext permission tier.

#### R

##### Reality
Simulation ontology truth.

##### Refusal
Deterministic denial of Process execution.

##### Refusal Contract
Normative structure requiring reason code and remediation hint.

##### Reliable
Deterministic and invariant-preserving.

##### Renderer
Presentation subsystem consuming PerceivedModel.

##### Replay
Deterministic re-execution of Process log.

##### RepoX
Static governance enforcement subsystem.

##### Retro
Legacy or historical pack context.

##### Robust
Resilient to malformed input or bad prompts.

##### Run-meta artifact
Non-canonical execution metadata.

##### Rule
Normative invariant.

#### S

##### Safe mode
Restricted execution profile.

##### Save
Persisted UniverseState snapshot.

##### ScenarioSpec
Initial condition declaration for SessionSpec.

##### SecureX
Security enforcement subsystem.

##### Server
Authoritative multiplayer runtime.

##### Session boundary
Explicit restart boundary between ExperienceProfiles.

##### SessionSpec
Runnable configuration of universe and experience.

##### Shard
SRZ partition.

##### Shard boundary
SRZ demarcation.

##### Simulation tick
Deterministic simulation update cycle.

##### Softcore
Default survival LawProfile.

##### Space
Spatial domain of simulation.

##### Spectator
ExperienceProfile allowing non-mutating view in multiplayer.

##### SRZ
Simulation Responsibility Zone.

##### STRICT
Structural verification profile.

##### Suite
Test grouping.

##### Supported
Actively maintained and compatible.

#### T

##### Tag
Version control marker.

##### Target
Build or execution objective.

##### Test
Verification case.

##### TestX
Deterministic runtime verification subsystem.

##### Thread-count invariance
Deterministic behavior independent of thread count.

##### Time
Simulation temporal dimension.

##### Tool
Non-runtime utility under `tools/`.

##### Toy
Non-production experimental artifact.

##### Transition Contract
Explicit rule governing ExperienceProfile switching.

##### Truth
Authoritative simulation state.

##### TruthModel
Canonical state representation.

##### TUI
Text User Interface.

#### U

##### UI
User Interface.

##### Unit
Standardized measurement.

##### Universe
Complete causal graph governed by UniverseIdentity.

##### UniverseIdentity
Immutable root identity configuration.

##### UniverseState
Mutable state at given simulation time.

##### Unsupported
Not guaranteed compatible.

##### Unsigned
Pack lacking SecureX signature.

##### UX
User Experience.

#### V

##### Version
Semantic identifier for compatibility.

##### Vintage
Historical content pack context.

#### Deprecated Terms
- Legacy mode-flag identifiers (`*_mode`) in runtime code.
- Ad hoc privilege flags outside `AuthorityContext`.
- Non-registry "sandbox" or "god" labels.

#### Reserved Words
Deterministic, Law, Authority, Lens, Canonical, Identity, Collapse, Expand, Macro, Micro, Process, Refusal.

End of Glossary v1.0.0.


## Source: `docs/repo/FOUNDATION_LOCK.md`

Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

### Foundation Lock

Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.

Current closeout result: PASS_WITH_WARNINGS.

`FOUNDATION-CLOSEOUT-02` reran the Foundation Lock gate after `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01` and closed the lock with warnings. `PORTABILITY-ARCH-POLICY-02` has since completed the first post-closeout hardening follow-up.

#### What It Means

Foundation Lock means the governance spine exists, validates in required scope, is documented, and is integrated with the normal fast strict proof gate. It allows only narrow product slices that obey the public surface, command, diagnostics, artifact, capability, provider, module, replacement, versioning, trust, and portability laws.

Foundation Lock does not mean full CTest is green, every compatibility corpus exists, every provider is implemented, every runtime trust rule is enforced, Workbench UI exists, or broad feature work is open.

#### Required Layers

- Fast strict test tier.
- Public surface registry.
- API/ABI canon.
- Dependency direction law.
- Command/refusal/result surface law.
- Diagnostic and evidence registry.
- Artifact identity law.
- Schema/protocol evolution law.
- Capability/refusal law.
- Provider model.
- Module/workspace/app composition law.
- Replacement protocol.
- Version/deprecation law.
- Mod/pack trust model.
- Portability matrix.

#### Closeout Decision

All required files for the 15 Foundation Lock layers are present.

`FOUNDATION-CLOSEOUT-01` was blocked because dependency-direction strict reported `358` violations and `38` warnings.

`FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01` reports dependency-direction strict PASS with `0` violations and `68` warnings.

`FOUNDATION-CLOSEOUT-02` reports:

- dependency-direction strict: PASS with `0` violations and `68` warnings.
- Foundation validator matrix: PASS.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- RepoX STRICT: PASS with stale AuditX warning.
- fast strict: PASS, `32` commands, `272.607` seconds.
- CMake configure/build and smoke CTest: PASS through fast strict.
- full CTest: T4/full-gate debt, not run.

Foundation Lock is PASS_WITH_WARNINGS.

`PORTABILITY-ARCH-POLICY-02` reports:

- architecture policy validator: PASS.
- portability matrix validator: PASS.
- fast strict: PASS, `33` commands, `296.553` seconds.
- CMake configure/build and smoke CTest: PASS through fast strict.
- full CTest: T4/full-gate debt, not run.

#### Allowed Work

- Continue narrow governed product-spine slices recorded by `.aide/queue/current.toml`.
- Run `AIDE-WORKFLOW-LAW-01` next if the queue remains reconciled after
  `PRODUCT-SPINE-REVIEW-01`.
- Run `POINTER-WIDTH-SERIALIZATION-AUDIT-01` only if the descriptive pointer-width inventory should be promoted into a focused audit.
- Continue documentation and evidence updates that do not bypass Foundation laws.
- Continue documentation and evidence updates that keep remaining warnings and full-gate debt visible.
- Keep Queue B hardening planned but not a substitute for the blocker repair.

#### Blocked Work

- Broad feature work remains blocked.
- Workbench UI, runtime module loading, provider runtime, package runtime, gameplay, renderer, native GUI, release publication, and broad rewrites remain blocked.

#### Feature Rules After Lock

When the lock eventually passes, future narrow slices must register public surfaces, expose typed commands, use diagnostic and refusal codes, preserve artifact identity, declare capabilities and providers, use module descriptors where applicable, and use the replacement protocol for rewrites.

#### Authorized Narrow Product-Spine Slices

`FOUNDATION-CLOSEOUT-02` authorized narrow product-spine work. Completed
narrow slices include `WORKBENCH-VALIDATION-SLICE-01`,
`COMMAND-RESULT-VIEW-SLICE-01`, `PACKAGE-MOUNT-SLICE-01`,
`REPLAY-PROOF-SLICE-01`, and `BAREBONES-CLIENT-SHELL-01`.

This authorization remains narrow. It does not authorize broad Workbench UI,
gameplay, renderer, native GUI, runtime provider expansion, package runtime,
release publication, or domain feature work.

Next recommended tasks:

1. `AIDE-WORKFLOW-LAW-01`
2. `PRESENTATION-CONTRACT-01`
3. `POINTER-WIDTH-SERIALIZATION-AUDIT-01`


## Source: `docs/architecture/WHAT_THIS_IS.md`

Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

### What This Project Is (CANON0)





Status: binding.


Scope: canonical statement of identity and intent.





Dominium/Domino is a deterministic world runtime and law-governed simulation OS.


It is built to host multi-scale universes with explicit existence, travel,


authority, and time perception.





#### Core identity


- A deterministic simulation runtime with reproducible outcomes.


- A truth/perception split where views are derived and authoritative state is


  explicit.


- A law-governed simulation OS where authority is data-defined.


- A multi-scale reality model with explicit existence/refinement and visitability.


- A product stack (engine + game + client/server + launcher/setup + tools) that


  separates runtime, control plane, and tooling.


- Content-agnostic executables: all meaning comes from packs resolved by UPS.


- Zero-asset boot paths for all products.





#### It can host


- player-only worlds


- AI-only autorun universes


- mixed civilizations


- spectator museums and replays


- anarchy servers


- god-mode admin tools (law-gated and audited)





#### Invariants


- Engine/game separation is preserved.


- Determinism and provenance are enforced.


- Absence and refusal are valid outcomes, not errors.


- There are no game modes; behavior is law + capability + policy.





#### Forbidden assumptions


- It is not acceptable to bypass law or audit for convenience.


- It is not acceptable to fabricate existence or resources.





#### Dependencies


- Canon and invariants: `docs/architecture/INVARIANTS.md`


- Reality layer: `docs/architecture/REALITY_LAYER.md`





#### See also


- `docs/architecture/CANONICAL_SYSTEM_MAP.md`


- `docs/architecture/INVARIANTS.md`


- `docs/architecture/REALITY_MODEL.md`


- `docs/architecture/AUTHORITY_MODEL.md`


## Source: `docs/architecture/WHAT_THIS_IS_NOT.md`

Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

### What This Project Is Not (CANON0)





Status: binding.


Scope: guardrails against common misunderstandings.





#### Not a traditional game engine


It is not a generic rendering or physics framework; rendering is derived and


authoritative logic is deterministic and law-gated.





#### Not an asset-dependent runtime


Executables do not embed content; packs are external and optional.





#### Not a step-everything sandbox


No global scans or per-ACT AI loops; simulation advances via scheduled events.





#### Not a physics-everywhere simulator


Micro detail is refined only when required; macro existence is valid.





#### Not a modes-based game


There are no hard-coded modes; laws and capabilities define behavior.





#### Not a cheat-based admin system


Admin power is capability- and law-gated, audited, and fork-aware.





#### Not a single-scale simulation


It supports macro-only, meso, and micro refinement with explicit contracts.





#### Invariants


- Deterministic, law-gated authority is mandatory.


- Global iteration and implicit background simulation are forbidden.


- No hard-coded modes exist.





#### Forbidden assumptions


- "Convenient" implicit behavior is not allowed.


- Authority cannot bypass audit or law gates.





#### Dependencies


- Canon and invariants: `docs/architecture/INVARIANTS.md`


- Reality layer: `docs/architecture/REALITY_LAYER.md`





#### See also


- `docs/architecture/WHAT_THIS_IS.md`


- `docs/architecture/INVARIANTS.md`


- `docs/architecture/REALITY_MODEL.md`


- `docs/architecture/AUTHORITY_MODEL.md`


## Source: `docs/architecture/INVARIANTS.md`

Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

### Invariants (CANON0)





Status: binding.


Scope: hard invariants for all systems, documentation, and data.





Canonical summary: this document.





Each invariant includes why it exists, what breaks if violated, and which


systems enforce it.





#### Invariant: Deterministic authoritative simulation (batch == step)


Why:


- Reproducibility, auditability, and cross-platform agreement depend on it.


Breaks if violated:


- Replays diverge, cross-shard reconciliation fails, and saves become invalid.


Enforced by:


- Work IR + Access IR (`schema/execution/README.md`)


- `docs/architecture/EXECUTION_REORDERING_POLICY.md`


- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`


- CI: EXEC0b-REORDER-001, EXEC0b-COMMIT-001





#### Invariant: Simulation advances only via explicit events (no global scans)


Why:


- Event scheduling keeps costs bounded and deterministic.


Breaks if violated:


- Hidden background work, O(N) scans, and per-tick AI loops cause drift and


  unpredictable budgets.


Enforced by:


- ARCH0 A2 (`docs/architecture/ARCH0_CONSTITUTION.md`)


- Event-driven scheduling specs (e.g., `docs/reference/specs/SPEC_EVENT_DRIVEN_STEPPING.md`)


- Guides: `docs/development/guides/NO_GLOBAL_ITERATION_GUIDE.md`


- CI: CIV5-WAR3-NOGLOB-005, CIV5-WAR4-NOGLOB-004





#### Invariant: ACT is monotonic and never warped


Why:


- ACT is the authoritative time axis for determinism and ordering.


Breaks if violated:


- Travel scheduling, replay, and law decisions become nondeterministic.


Enforced by:


- `docs/architecture/TIME_DILATION_WITHOUT_TIME_WARP.md`


- `schema/time/README.md`


- CI: TIME2-NO-ACT-WARP-001





#### Invariant: No implicit existence


Why:


- Existence must be auditable and lawful.


Breaks if violated:


- Pop-in creation, silent erasure, and unverifiable provenance.


Enforced by:


- `docs/architecture/EXISTENCE_AND_REALITY.md`


- `schema/existence/README.md`


- CI: EXIST0-STATE-001, EXIST0-NOPOP-002





#### Invariant: No refinement without a contract


Why:


- Refinement must be deterministic and provenance-preserving.


Breaks if violated:


- Fake worlds, fabricated history, and nondeterministic detail.


Enforced by:


- `docs/architecture/REFINEMENT_CONTRACTS.md`


- `docs/architecture/VISITABILITY_CONSISTENCY.md`


- CI: EXIST1-CONTRACT-001, DOMAIN4-NOFAKE-002





#### Invariant: No teleport without a TravelEdge


Why:


- Movement must be schedulable, law-gated, and auditable.


Breaks if violated:


- Reachability lies, bypassed costs, and broken domain law.


Enforced by:


- `docs/architecture/TRAVEL_AND_MOVEMENT.md`


- `docs/architecture/NO_MAGIC_TELEPORTS.md`


- CI: TRAVEL0-NO-TELEPORT-001, TRAVEL2-NO-MAGIC-001





#### Invariant: Reachability implies visitability


Why:


- If something can be reached, it must be real and refinable.


Breaks if violated:


- Players can arrive at non-real or non-refinable destinations.


Enforced by:


- `docs/architecture/VISITABILITY_AND_REALITY.md`


- `schema/domain/SPEC_VISITABILITY.md`


- CI: DOMAIN4-VISIT-001, DOMAIN4-NOFAKE-002





#### Invariant: No authority without capability and law


Why:


- Authority must be explicit, scoped, and auditable.


Breaks if violated:


- Hidden admin bypass, cheat-only paths, and unverifiable outcomes.


Enforced by:


- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md`


- `docs/architecture/LAW_ENFORCEMENT_POINTS.md`


- `schema/authority/README.md`


- CI: OMNI0-NO-ISADMIN-001, OMNI0-NOBYPASS-003





#### Invariant: Authority gates actions only, never visibility (AUTH3-AUTH-001)


Why:


- Visibility is epistemic; authority is action gating only.


Breaks if violated:


- Hidden enforcement, nondeterministic views, and un-auditable censorship.


Enforced by:


- `docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md`


- `docs/architecture/DEMO_AND_TOURIST_MODEL.md`


- Tests: `tests/authority/`, `tests/integration/tourist/`





#### Invariant: Entitlements gate authority issuance only (AUTH3-ENT-002)


Why:


- Entitlements are platform-facing; engine/game must stay neutral.


Breaks if violated:


- Platform lock-in and hidden enforcement in simulation logic.


Enforced by:


- `docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md`


- Tests: `tests/entitlement/`





#### Invariant: Demo is an authority profile, not a build (AUTH3-DEMO-003)


Why:


- One distribution prevents paywalled forks and drift.


Breaks if violated:


- Divergent code paths and inconsistent determinism.


Enforced by:


- `docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md`


- `docs/architecture/DEMO_AND_TOURIST_MODEL.md`


- Tests: `tests/demo/`, `tests/distribution/`





#### Invariant: Tourists never mutate authoritative state (AUTH3-TOURIST-004)


Why:


- Observation must not become hidden authority.


Breaks if violated:


- Untracked mutations and integrity drift.


Enforced by:


- `docs/architecture/DEMO_AND_TOURIST_MODEL.md`


- Tests: `tests/integration/tourist/`





#### Invariant: Services affect access only (AUTH3-SERVICE-005)


Why:


- Services are optional and external to determinism.


Breaks if violated:


- Altered outcomes and invalidated replays.


Enforced by:


- `docs/architecture/SERVICES_AND_PRODUCTS.md`


- Tests: `tests/contract/service/services_expiry/`





#### Invariant: Piracy contained by authority, not DRM (AUTH3-PIRACY-006)


Why:


- Copying is allowed; durable value is authority-bound.


Breaks if violated:


- Hidden penalties, degraded simulation, and non-archival behavior.


Enforced by:


- `docs/architecture/PIRACY_CONTAINMENT.md`


- Tests: `tests/piracy_containment/`





#### Invariant: Authority upgrades/downgrades do not mutate state (AUTH3-UPGRADE-007)


Why:


- Authority changes are administrative, not simulation events.


Breaks if violated:


- Hidden state mutation and replay divergence.


Enforced by:


- `docs/architecture/UPGRADE_AND_CONVERSION.md`


- Tests: `tests/authority/`, `tests/contract/service/services_expiry/`





#### Invariant: Saves are tagged by authority scope (AUTH3-SAVE-008)


Why:


- Save provenance must remain explicit and auditable.


Breaks if violated:


- Silent promotion of non-authoritative saves.


Enforced by:


- `docs/architecture/UPGRADE_AND_CONVERSION.md`


- Tests: `tests/authority/`





#### Invariant: Control layers never interfere with authoritative simulation


Why:


- Control layers are optional and external; they must not change outcomes.


Breaks if violated:


- Replays diverge, archival verification fails, and law enforcement becomes


  untrustworthy.


Enforced by:


- `docs/architecture/NON_INTERFERENCE.md`


- `docs/architecture/CONTROL_LAYERS.md`


- Tests: `tests/runtime/control/interference/`





#### Invariant: No secrets in engine or game


Why:


- Engine/game are portable, public, and replay-verifiable; secrets break trust.


Breaks if violated:


- Credential exposure, covert policy enforcement, and irreproducible builds.


Enforced by:


- `docs/architecture/CONTROL_LAYERS.md`


- `docs/architecture/THREAT_MODEL.md`


- Tests: `tests/runtime/control/audit/`





#### Invariant: Refusal and absence are first-class outcomes


Why:


- Systems must fail deterministically and explainably.


Breaks if violated:


- Silent fallbacks, undefined behavior, or forced workarounds.


Enforced by:


- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md`


- ARCH0 A7 (`docs/architecture/ARCH0_CONSTITUTION.md`)


- CI: EXEC0-ABSENCE-001





#### Invariant: Authoritative mutation only through Work IR + law gates


Why:


- Ensures auditability and enforcement consistency.


Breaks if violated:


- Untracked state changes and law bypass paths.


Enforced by:


- `docs/architecture/EXECUTION_SUBSTRATE_AUDIT.md`


- `docs/architecture/LAW_ENFORCEMENT_POINTS.md`


- CI: EXEC0-IR-001, EXEC0c-LAW-REQ-001





#### Invariant: Deterministic reductions and commit ordering


Why:


- Parallelism must not change outcomes.


Breaks if violated:


- Nondeterministic totals, inconsistent ledgers, and diverging replicas.


Enforced by:


- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`


- `docs/architecture/EXECUTION_REORDERING_POLICY.md`


- CI: EXEC0b-REDUCE-001, EXEC0b-COMMIT-001





#### Invariant: Distribution and sharding are deterministic


Why:


- Cross-shard outcomes must be reproducible and auditable.


Breaks if violated:


- Divergent shard ownership, nondeterministic message ordering.


Enforced by:


- `schema/distribution/README.md`


- `docs/architecture/DOMAIN_SHARDING_AND_STREAMING.md`


- CI: DOMAIN3-SHARD-001, CIV5-WAR4-SHARD-005





#### Invariant: Archived history is immutable (fork to change it)


Why:


- Historical integrity and auditability depend on immutability.


Breaks if violated:


- Silent history edits and unverifiable replays.


Enforced by:


- `docs/architecture/ARCHIVAL_AND_PERMANENCE.md`


- `docs/architecture/TIMELINE_FORKS_AND_HISTORY.md`


- CI: EXIST2-FREEZE-001, EXIST2-FORK-002





#### Invariant: Tools cannot bypass law (read-only by default)


Why:


- Tooling must not become a hidden admin channel.


Breaks if violated:


- Untracked mutations, integrity drift, and replay divergence.


Enforced by:


- `docs/architecture/TOOLS_AS_CAPABILITIES.md`


- `schema/tool/README.md`


- CI: OMNI1-NOTOOLBYPASS-001, TOOL0-NOMUT-004





#### Invariant: Scaling is a semantics-preserving projection (SCALE0-PROJECTION-001)


Why:


- Macro state must not contradict micro truth.


Breaks if violated:


- Expanding a domain changes outcomes or fabricates history.


Enforced by:


- `docs/architecture/SCALING_MODEL.md`


- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: Conservation across collapse/expand (SCALE0-CONSERVE-002)


Why:


- Totals and obligations must remain exact across fidelity tiers.


Breaks if violated:


- Resource/energy/population drift, broken contracts, authority inconsistencies.


Enforced by:


- `docs/architecture/INVARIANTS_AND_TOLERANCES.md`


- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: Collapse/expand only at commit boundaries (SCALE0-COMMIT-003)


Why:


- Commit boundaries are the only safe points for deterministic transitions.


Breaks if violated:


- Mid-commit state changes create nondeterministic outcomes.


Enforced by:


- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`


- `docs/architecture/EXECUTION_MODEL.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: Deterministic macro time ordering (SCALE0-DETERMINISM-004)


Why:


- Cross-thread determinism and replay depend on stable ordering.


Breaks if violated:


- Divergent replays, shard disagreements, and audit failure.


Enforced by:


- `docs/architecture/MACRO_TIME_MODEL.md`


- `docs/architecture/EXECUTION_REORDERING_POLICY.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: Sufficient statistics within declared tolerances (SCALE0-TOLERANCE-005)


Why:


- Bounded approximation prevents drift and invalid refinements.


Breaks if violated:


- Unbounded error accumulation and invalid expansions.


Enforced by:


- `docs/architecture/INVARIANTS_AND_TOLERANCES.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: Interest drives activation (SCALE0-INTEREST-006)


Why:


- Activation must be explicit, deterministic, and auditable.


Breaks if violated:


- View-driven activation, hidden work, and nondeterministic scaling.


Enforced by:


- `docs/architecture/INTEREST_MODEL.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: No ex nihilo expansion (SCALE0-NO-EXNIHILO-007)


Why:


- Expansion must reconstruct, not invent.


Breaks if violated:


- Fabricated entities/resources and broken conservation.


Enforced by:


- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: Replay equivalence across collapse/expand (SCALE0-REPLAY-008)


Why:


- Save/replay integrity depends on identical macro transitions.


Breaks if violated:


- Replays diverge when collapse/expand occurs.


Enforced by:


- `docs/architecture/MACRO_TIME_MODEL.md`


- `docs/architecture/REPLAY_FORMAT.md`


- Tests: `tests/apps/scale0_contract_tests.py`





#### Invariant: Scaling work is budget-gated (SCALE3-BUDGET-009)


Why:


- Budgets are the only lawful way to bound work without changing semantics.


Breaks if violated:


- Hidden scaling paths bypass policy and destroy auditability.


Enforced by:


- `docs/architecture/BUDGET_POLICY.md`


- `docs/architecture/CONSTANT_COST_GUARANTEE.md`


- Tests: `tests/apps/scale3_budget_tests.py`





#### Invariant: Admission control is explicit and non-mutating on refusal (SCALE3-ADMISSION-010)


Why:


- Refusal and defer semantics are part of determinism and replay guarantees.


Breaks if violated:


- Budget pressure silently changes outcomes or corrupts state.


Enforced by:


- `docs/architecture/BUDGET_POLICY.md`


- `docs/architecture/REFUSAL_SEMANTICS.md`


- Tests: `tests/apps/scale3_budget_tests.py`





#### Invariant: Per-commit cost is bounded by active fidelity (SCALE3-CONSTCOST-011)


Why:


- Large worlds and deep history must not change active simulation cost.


Breaks if violated:


- Cost scales with world size, time span, or collapsed-domain count.


Enforced by:


- `docs/architecture/CONSTANT_COST_GUARANTEE.md`


- `docs/architecture/MACRO_TIME_MODEL.md`


- Tests: `tests/apps/scale3_budget_tests.py`





#### Invariant: The universe is logically single under distribution (MMO0-UNIVERSE-012)


Why:


- Distribution must not create alternate histories or outcomes.


Breaks if violated:


- Multiplayer outcomes diverge from single-shard truth.


Enforced by:


- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`


- `docs/architecture/MMO_COMPATIBILITY.md`


- Tests: `tests/apps/mmo0_distributed_contract_tests.py`





#### Invariant: Domain ownership is exclusive and commit-boundary only (MMO0-OWNERSHIP-013)


Why:


- Double ownership destroys authority, auditability, and determinism.


Breaks if violated:


- Conflicting writes, nondeterministic outcomes, and replay failure.


Enforced by:


- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`


- `docs/architecture/CROSS_SHARD_LOG.md`


- Tests: `tests/apps/mmo0_distributed_contract_tests.py`





#### Invariant: Global identifiers are deterministic and collision-free (MMO0-ID-014)


Why:


- Identity must survive distribution, replay, and ownership transfer.


Breaks if violated:


- Collisions, identity drift, and nondeterministic reconciliation.


Enforced by:


- `docs/architecture/GLOBAL_ID_MODEL.md`


- Tests: `tests/apps/mmo0_distributed_contract_tests.py`





#### Invariant: Cross-shard interaction is append-only, ordered, and idempotent (MMO0-LOG-015)


Why:


- Logs are the only lawful way to couple shards without hidden mutation.


Breaks if violated:


- Hidden cross-shard state changes and unreplayable outcomes.


Enforced by:


- `docs/architecture/CROSS_SHARD_LOG.md`


- `schema/cross_shard_message.schema`


- Tests: `tests/apps/mmo0_distributed_contract_tests.py`





#### Invariant: Distributed time and ordering preserve outcomes (MMO0-TIME-016)


Why:


- Physical execution order must not change authoritative results.


Breaks if violated:


- Cross-thread and cross-shard divergence in final world state.


Enforced by:


- `docs/architecture/DISTRIBUTED_TIME_MODEL.md`


- `docs/architecture/CROSS_SHARD_LOG.md`


- Tests: `tests/apps/mmo0_distributed_contract_tests.py`





#### Invariant: Join/resync is deterministic and capability-safe (MMO0-RESYNC-017)


Why:


- Joining and resyncing must not introduce hidden or partial authority.


Breaks if violated:


- Inconsistent clients, shard drift, and audit failure.


Enforced by:


- `docs/architecture/JOIN_RESYNC_CONTRACT.md`


- `docs/architecture/REFUSAL_SEMANTICS.md`


- Tests: `tests/apps/mmo0_distributed_contract_tests.py`





#### Invariant: Singleplayer and multiplayer semantics are unified (MMO0-COMPAT-018)


Why:


- Divergent logic across modes invalidates determinism guarantees.


Breaks if violated:


- SP and MP produce different outcomes for the same intent streams.


Enforced by:


- `docs/architecture/MMO_COMPATIBILITY.md`


- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`


- Tests: `tests/apps/mmo0_distributed_contract_tests.py`





#### Forbidden assumptions


- Invariants are optional or "guidelines" rather than binding rules.


- Convenience exceptions are acceptable without a canon update.





#### Dependencies


- `docs/architecture/ARCH0_CONSTITUTION.md`


- `docs/architecture/CHANGE_PROTOCOL.md`





#### See also


- `docs/architecture/CANONICAL_SYSTEM_MAP.md`


- `docs/architecture/REALITY_MODEL.md`


- `docs/architecture/AUTHORITY_MODEL.md`


- `docs/architecture/EXECUTION_MODEL.md`


## Source: `docs/architecture/CANONICAL_SYSTEM_MAP.md`

Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

### Canonical System Map (CANON0)





Status: binding.


Scope: single-source dependency map and forbidden edges for Dominium/Domino.





This map locks the project into one mental model. It is written for humans and


is the authoritative dependency direction statement. "A -> B" means A depends


on B and must not be inverted.





#### Canonical system stack (textual diagram)


This stack is a navigation and integration view. Dependency direction remains


authoritative in the sections below.





ENGINE -> GAME -> SERVER/CLIENT -> LAUNCHER/SETUP -> TOOLS





#### Invariants


- Dependency direction is authoritative and must not be inverted.


- Engine and game responsibilities remain separated.


- Law gates and audit are mandatory for authoritative effects.


- Engine and game are content-agnostic executables; content lives in data.


- Launcher and setup are orchestration surfaces only.


- Tools are read-only by default and mutate state only via ToolIntents.





#### Responsibilities and forbidden dependencies (quick map)


Responsibilities:


- engine: mechanisms, determinism, storage, execution substrate, law gates


- game: meaning, rules, process emission, law targets, content interpretation


- server/client: product shells that compose engine + game


- launcher/setup: orchestration, installation, profiles, compatibility


- tools: validation, inspection, authoring, and audit-friendly workflows





Forbidden dependencies (summary):


- engine -> game, launcher, setup, tools, libs contracts


- game -> launcher, setup, tools, libs contracts


- launcher/setup/tools -> game rule mutation paths


- client/server -> launcher, setup, tools


- tools -> authoritative mutation outside ToolIntents





#### 1) Engine vs Game Boundary


Engine defines mechanisms; game defines meaning; data defines configuration.


Tools are read-only observers unless they emit explicit ToolIntents that are


law-gated and audited.





Dependency direction:


ENGINE: platform + syscaps -> execution substrate -> ECS storage -> world services


(domains, travel, time, law gates)


GAME: rules -> intents -> Work IR -> engine execution substrate


PRODUCTS: client/server -> engine + game


CONTROL PLANE: launcher/setup -> libs/contracts


TOOLS: tools -> libs/contracts (+ engine public API only, read-only)


SCHEMA: schema -> data formats only (no runtime logic)





Forbidden dependencies:


- engine -> game/launcher/setup/tools/libs


- game -> launcher/setup/tools/libs


- launcher/setup/tools -> game (no rule mutation)


- client/server -> tools/package/launcher/setup


- tools -> authoritative mutation outside ToolIntents





#### 2) Execution Substrate


All authoritative work is expressed as Work IR with Access IR declarations.


Law admission gates sit before scheduling, before execution, and before commit.





Dependency direction:


game systems -> Work IR + Access IR -> scheduler backends -> deterministic commit


law kernel -> admission gates -> task/effect execution


budgets + SysCaps -> execution policy -> backend selection





Forbidden dependencies:


- gameplay code bypassing Work IR or spawning threads


- derived/presentation tasks writing authoritative state


- scheduler policy encoded inside game rules





#### 3) Storage (ECS)


ECS schemas define component meaning; storage layout is an engine backend choice.


Game code depends on logical components, not layout or memory order.





Dependency direction:


schema/ecs -> engine storage -> game rules -> Work IR tasks





Forbidden dependencies:


- gameplay logic depending on physical storage layout


- storage backends altering component semantics or determinism





#### 4) Space & Domains
Domain volumes define where reality exists and which laws apply. Domain queries
are deterministic, budgeted, and SDF-based.

Dependency direction:
domain volumes -> reachability + law jurisdictions -> travel + refinement

Forbidden dependencies:
- implicit world bounds or rectangular assumptions
- domain checks bypassing domain query API

Terrain truth (TERRAIN0) is field-defined and provider-resolved.

Dependency direction:
domain volumes -> terrain field stack -> provider chain -> overlays -> queries

Forbidden dependencies:
- meshes treated as authoritative truth
- per-tick global erosion
- planet/station special casing in terrain truth



#### 5) Existence & Refinement


Existence states are explicit; transitions are effects. Refinement contracts


deterministically realize micro state; collapse preserves truth and provenance.





Dependency direction:


existence state -> refinement contract -> visitability -> travel arrival


law kernel + Work IR -> existence transitions





Forbidden dependencies:


- implicit existence creation/destruction


- refinement without a contract


- history edits without archival fork





#### 6) Travel & Reachability


All movement is scheduled travel over explicit edges with cost/capacity rules.


Visitability gates arrival.





Dependency direction:


travel graph -> ACT scheduling -> law/capability checks -> arrival effects


domain permissions + existence/refinement -> visitability decision





Forbidden dependencies:


- teleportation without a TravelEdge


- arrival into non-refinable or archived targets


- bypassing law or visitability gates





#### 7) Time & Perception


ACT is authoritative and monotonic. Observer clocks derive perception without


changing schedules. Replay uses the same model.





Dependency direction:


ACT -> scheduler -> authoritative effects


observer clocks -> presentation/replay views





Forbidden dependencies:


- ACT warping for gameplay pacing


- perception clocks affecting authoritative scheduling


- future leakage beyond allowed buffers





#### 8) Authority, Law & Integrity


Capabilities grant power; laws decide outcomes; policy constrains behavior.


Integrity signals inform law but never mutate state.





Dependency direction:


capabilities + law targets + policy -> law kernel -> accept/refuse/transform


law outcomes -> effects + audit + refusal explanations





Forbidden dependencies:


- isAdmin/mode checks in code


- admin/cheat bypass without law + audit


- silent fallbacks in the face of denial





#### 9) Distribution & Sharding


Shard ownership is deterministic and domain-driven. Cross-shard messages are


ordered deterministically; no synchronous cross-shard reads.





Dependency direction:


domain partition -> shard ownership -> message ordering -> commit





Forbidden dependencies:


- nondeterministic shard placement


- state teleportation or silent migration


- synchronous cross-shard reads





#### 10) Tooling & Omnipotence


Tooling is capability-gated. Omnipotence is the union of capabilities and is


still law-gated, audited, and constrained by archival rules.





Dependency direction:


ToolIntents -> law kernel -> effects -> audit


omnipotent intent -> same path





Forbidden dependencies:


- tool-side mutation outside ToolIntents


- history edits without archival fork + audit


- bypassing law or integrity gates





#### Forbidden assumptions


- Dependency inversion is acceptable for convenience.


- Tooling can mutate authoritative state directly.





#### Dependencies


- `docs/architecture/ARCH0_CONSTITUTION.md`


- `docs/architecture/INVARIANTS.md`





#### See also


- `docs/architecture/ARCH0_CONSTITUTION.md`


- `docs/architecture/EXECUTION_MODEL.md`


- `docs/architecture/REALITY_MODEL.md`


- `docs/architecture/REALITY_LAYER.md`


- `docs/architecture/REALITY_FLOW.md`


- `docs/architecture/AUTHORITY_MODEL.md`


- `schema/execution/README.md`


- `schema/existence/README.md`


- `schema/domain/README.md`


- `schema/travel/README.md`


- `schema/time/README.md`


- `schema/authority/README.md`


- `schema/distribution/README.md`


## Source: `docs/architecture/CONTRACTS_INDEX.md`

Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

### Contracts Index (CONST0)





Status: binding.


Scope: index of frozen and evolving constitutional surfaces.





This index is the navigation hub for stability surfaces. "FROZEN" means the


document defines a contract that must not change lightly. "EVOLVING" means the


document is binding but still expected to grow or sharpen.





#### Frozen constitutional surfaces


| Contract | Stability | Notes |


| --- | --- | --- |


| `docs/architecture/ARCH0_CONSTITUTION.md` | FROZEN | Top-level architecture law |


| `docs/architecture/INVARIANTS.md` | FROZEN | Canonical invariant registry |


| `docs/architecture/CANONICAL_SYSTEM_MAP.md` | FROZEN | Dependency direction and forbidden edges |
| `docs/architecture/CANON_INDEX.md` | FROZEN | Canonical contract entry point |


| `docs/architecture/REPO_NAV.md` | FROZEN | Where work belongs in the repo |
| `docs/architecture/REPO_INTENT.md` | FROZEN | Repository intent and allowed change classes |


| `docs/architecture/ID_AND_NAMESPACE_RULES.md` | FROZEN | ID shape, stability, and reservations |


| `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md` | FROZEN | Global ordering rules |


| `docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md` | FROZEN | Mechanism vs meaning boundary |


| `docs/architecture/PROCESS_ONLY_MUTATION.md` | FROZEN | Only lawful state mutation path |


| `docs/architecture/LAW_AND_META_LAW.md` | FROZEN | Historical law vs operational law |


| `docs/architecture/REFUSAL_SEMANTICS.md` | FROZEN | Canonical refusal codes and payload |


| `docs/architecture/UNIT_SYSTEM_POLICY.md` | FROZEN | Units, fixed-point, and numeric policy |


| `docs/architecture/FABRICATION_MODEL.md` | FROZEN | Fabrication ontology and schema rules |
| `docs/architecture/SCHEMA_STABILITY.md` | FROZEN | Schema stability classifications |


| `docs/architecture/EXECUTION_MODEL.md` | FROZEN | Work IR and deterministic execution |


| `docs/architecture/EXECUTION_REORDERING_POLICY.md` | FROZEN | Canonical commit ordering |


| `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md` | FROZEN | Deterministic reduction operators |
| `docs/architecture/RNG_MODEL.md` | FROZEN | Named RNG streams and derivation |
| `docs/architecture/REDUCTION_MODEL.md` | FROZEN | Deterministic reduction merge order |
| `docs/architecture/FLOAT_POLICY.md` | FROZEN | Floating point quarantine zones |
| `docs/architecture/SIGNAL_MODEL.md` | FROZEN | Signal fields, interfaces, and computation rules |


| `docs/architecture/LAW_ENFORCEMENT_POINTS.md` | FROZEN | Mandatory law gates |


| `docs/architecture/GLOBAL_ID_MODEL.md` | FROZEN | Deterministic global ID rules |


| `docs/architecture/CROSS_SHARD_LOG.md` | FROZEN | Cross-shard ordering and idempotence |


| `docs/architecture/BUDGET_POLICY.md` | FROZEN | Budget admission and refusal mapping |
| `docs/architecture/PERFORMANCE_METRICS.md` | FROZEN | Derived metrics for PERF fixtures |
| `docs/architecture/CODE_DATA_BOUNDARY.md` | FROZEN | Code vs data ownership rules |
| `docs/architecture/SEMANTIC_STABILITY_POLICY.md` | FROZEN | No reuse and no silent reinterpretation |
| `docs/reference/contracts/SEMANTIC_CONTRACT_MODEL.md` | FROZEN | Semantic behavior versioning and migration rules |
| `docs/governance/meta/EXTENSION_DISCIPLINE.md` | FROZEN | Namespaced extension discipline and deterministic ignore/refusal policy |
| `docs/domains/geology/OVERLAY_CONFLICT_POLICIES.md` | FROZEN | Deterministic overlay conflict-policy modes and refusal semantics |
| `docs/reference/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md` | FROZEN | Deterministic endpoint capability negotiation, degrade plans, and negotiation records |
| `docs/modding/MOD_TRUST_AND_CAPABILITIES.md` | FROZEN | Deterministic mod trust levels, capability declarations, and refusal policy |


| `docs/architecture/ANTI_ENTROPY_RULES.md` | FROZEN | Anti-entropy requirements |


| `docs/architecture/CAPABILITY_BASELINES.md` | FROZEN | Capability baselines and refusals |
| `docs/architecture/AI_INTENT_MODEL.md` | FROZEN | AI intent production and modes |
| `docs/architecture/AI_BUDGET_MODEL.md` | FROZEN | AI budget classes and fairness |
| `docs/architecture/BUNDLE_MODEL.md` | FROZEN | Shareable bundle container and rules |
| `docs/architecture/BUGREPORT_MODEL.md` | FROZEN | Bugreport bundle contents and rules |


| `docs/distribution/PACK_TAXONOMY.md` | FROZEN | Canonical pack classes |


| `docs/distribution/LAUNCHER_SETUP_CONTRACT.md` | FROZEN | Distribution and launcher/setup rules |


| `docs/distribution/LEGACY_COMPATIBILITY.md` | FROZEN | Legacy compatibility modes |





| `docs/architecture/INSTALL_MODEL.md` | FROZEN | Install manifest and install root contract |
| `docs/architecture/INSTANCE_MODEL.md` | FROZEN | Instance manifest and data root contract |
| `docs/architecture/OPS_TRANSACTION_MODEL.md` | FROZEN | Transactional ops model and ops log |
| `docs/architecture/UPDATE_MODEL.md` | FROZEN | Update channels and rollback guarantees |
| `docs/architecture/SANDBOX_MODEL.md` | FROZEN | Sandbox meta-law policy |
| `docs/architecture/COMPATIBILITY_MODEL.md` | FROZEN | Compat report and mode selection |
| `docs/architecture/LIVE_EVOLUTION_MODEL.md` | FROZEN | Rolling updates and rollback safety |
| `docs/architecture/LEGACY_SUPPORT_MODEL.md` | FROZEN | Legacy binaries and degraded modes |
| `docs/distribution/PACK_SOURCES.md` | FROZEN | Pack sources and mirrors |
| `docs/architecture/LOCKLIST.md` | FROZEN | Frozen seams, reserved surfaces, and override policy |
| `docs/architecture/PLATFORM_RESPONSIBILITY.md` | FROZEN | Platform runtime scope and invariants |
| `docs/architecture/RENDERER_RESPONSIBILITY.md` | FROZEN | Renderer scope and determinism invariants |
#### Evolving but binding surfaces


| Contract | Stability | Notes |


| --- | --- | --- |


| `docs/architecture/ARCH_REPO_LAYOUT.md` | EVOLVING | Layout is binding but may refine |


| `docs/architecture/DIRECTORY_STRUCTURE.md` | EVOLVING | Canonical tree and runtime root |
| `docs/architecture/SETUP_TRANSACTION_MODEL.md` | EVOLVING | Setup transactional model |
| `docs/distribution/SETUP_GUARANTEES.md` | EVOLVING | Setup guarantees |
| `docs/distribution/SETUP_GUIDE.md` | EVOLVING | Setup CLI guide |
| `docs/distribution/OFFLINE_INSTALL.md` | EVOLVING | Offline install policy |
| `docs/distribution/UNINSTALL_AND_REPAIR.md` | EVOLVING | Uninstall, repair, rollback rules |
| `docs/distribution/LAUNCHER_SCOPE.md` | EVOLVING | Launcher scope and prohibitions |
| `docs/distribution/LAUNCHER_GUIDE.md` | EVOLVING | Launcher CLI guide |
| `docs/architecture/PRODUCT_SHELL_CONTRACT.md` | EVOLVING | Product shell acceptance contract |
| `docs/architecture/CHECKPOINTS.md` | EVOLVING | Acceptance checkpoints |
| `docs/runtime/ui/UX_RULES.md` | EVOLVING | Global UX rules (CLI/TUI/GUI) |
| `docs/runtime/ui/LAUNCHER_WALKTHROUGH.md` | EVOLVING | Launcher walkthrough and parity |
| `docs/runtime/ui/CLIENT_OUT_OF_GAME_SCOPE.md` | EVOLVING | Client out-of-game scope (zero-asset) |
| `docs/runtime/ui/CLIENT_MENU_GUIDE.md` | EVOLVING | Client menu behavior and rules |
| `docs/runtime/ui/WORLD_CREATION_FLOW.md` | EVOLVING | World creation flow contract |
| `docs/runtime/ui/SETTINGS_GUIDE.md` | EVOLVING | Settings contract and constraints |
| `docs/runtime/ui/DEBUG_AND_INSPECT.md` | EVOLVING | Debug/inspect access contract |
| `docs/development/DEBUG_AND_DIAGNOSTICS_MODEL.md` | EVOLVING | Debug and diagnostics model |
| `docs/compatibility/ENDPOINT_DESCRIPTORS.md` | EVOLVING | Deterministic per-product endpoint descriptor emission and offline manifest surfaces |
| `docs/compatibility/NEGOTIATION_HANDSHAKES.md` | EVOLVING | Deterministic client/server and IPC attach negotiation handshake flow |
| `docs/compatibility/DEGRADE_LADDERS.md` | EVOLVING | Deterministic per-product degrade ladders and explicit fallback mapping |
| `docs/compatibility/DATA_FORMAT_VERSIONING.md` | EVOLVING | Deterministic persistent artifact format versioning, migration hooks, and read-only fallback rules |
| `docs/runtime/diagnostics/REPRO_BUNDLE_MODEL.md` | EVOLVING | Deterministic offline repro bundle contents, privacy stripping, and replay verification workflow |
| `docs/operations/SERVER_SCOPE.md` | EVOLVING | Server scope and guarantees |
| `docs/operations/LOGGING_MODEL.md` | EVOLVING | Server logging format and rotation |
| `docs/operations/LONG_RUN_EXPECTATIONS.md` | EVOLVING | Long-run stability expectations |
| `docs/operations/SERVER_OPERATIONS.md` | EVOLVING | Server CLI operations |
| `docs/operations/MMO_SCALING_PLAYBOOK.md` | EVOLVING | SRZ scaling operations playbook |
| `docs/development/REPLAY_WORKFLOW.md` | EVOLVING | Replay-first workflow |
| `docs/development/TOOLS_GUIDE.md` | EVOLVING | Read-only tooling guide |
| `docs/development/REPLAY_DEBUGGING.md` | EVOLVING | Replay debugging process |


| `docs/architecture/MACRO_TIME_MODEL.md` | EVOLVING | Macro stepping rules |

| `docs/architecture/TERRAIN_TRUTH_MODEL.md` | EVOLVING | Terrain truth model (SDF + fields) |
| `docs/architecture/TERRAIN_FIELDS.md` | EVOLVING | Canonical terrain field stack |
| `docs/architecture/TERRAIN_PROVIDER_CHAIN.md` | EVOLVING | Provider chain order and composition |
| `docs/architecture/TERRAIN_OVERLAYS.md` | EVOLVING | Process-only terrain overlays |
| `docs/architecture/STRUCTURAL_STABILITY_MODEL.md` | EVOLVING | Structural stability and collapse |
| `docs/architecture/DECAY_EROSION_REGEN.md` | EVOLVING | Event-driven decay/erosion/regeneration |
| `docs/architecture/TERRAIN_COORDINATES.md` | EVOLVING | Terrain coordinate frames and precision |
| `docs/architecture/TERRAIN_MACRO_CAPSULE.md` | EVOLVING | Terrain macro capsule contract |


| `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md` | EVOLVING | SRZ-aware distributed execution model |
| `docs/architecture/SRZ_MODEL.md` | EVOLVING | Simulation responsibility zones and verification |
| `docs/architecture/EPISTEMICS_MODEL.md` | EVOLVING | Epistemic constraints and knowledge limits |
| `docs/architecture/EPISTEMICS_AND_SCALED_MMO.md` | EVOLVING | Fog-of-war preservation at scale |


| `docs/architecture/DISTRIBUTED_TIME_MODEL.md` | EVOLVING | Distributed time details |


| `docs/architecture/JOIN_RESYNC_CONTRACT.md` | EVOLVING | Join and resync rules |


| `docs/architecture/SHARD_LIFECYCLE.md` | EVOLVING | Shard lifecycle rules |


| `docs/architecture/CHECKPOINTING_MODEL.md` | EVOLVING | Checkpointing and snapshots |


| `docs/architecture/CRASH_RECOVERY.md` | EVOLVING | Recovery contracts |


| `docs/architecture/ROLLING_UPDATES.md` | EVOLVING | Rolling update contracts |
| `docs/architecture/ARCHIVE_MANIFEST.md` | EVOLVING | Archive and quarantine manifest |
| `docs/architecture/CHANGELOG_ARCH.md` | EVOLVING | Architecture changelog and pointers |
| `docs/architecture/PERFORMANCE_PROOF.md` | EVOLVING | PERF stress evidence and regression proof |
| `docs/engine/FAB_INTERPRETERS.md` | EVOLVING | Minimal FAB interpreter contract |
| `docs/game/FAB_EXECUTION_FLOW.md` | EVOLVING | FAB execution flow and guardrails |





#### Schema and contract anchors

AppShell shell-lifecycle anchor:

- `docs/runtime/shell/APPSHELL_CONSTITUTION.md`

Schemas are the authoritative data-shape contracts. Start here:


- `schema/SCHEMA_GOVERNANCE.md`


- `schema/SCHEMA_VERSIONING.md`


- `schema/SCHEMA_VALIDATION.md`


- `schema/world_definition.schema`


- `schema/process.schema`


- `schema/save_and_replay.schema`


- `schema/server_protocol.schema`


- `schema/material.schema`


- `schema/part.schema`


- `schema/assembly.schema`


- `schema/interface.schema`


- `schema/process_family.schema`


- `schema/instrument.schema`


- `schema/standard.schema`


- `schema/quality.schema`


- `schema/batch_lot.schema`


- `schema/hazard.schema`


- `schema/substance.schema`


- `schema/profile.schema`
- `schema/universe/universe_contract_bundle.schema`
- `schema/appshell/app_mode.schema`
- `schema/appshell/exit_code_registry.schema`
- `schema/appshell/refusal_code_registry.schema`
- `schema/appshell/command_descriptor.schema`
- `schema/appshell/tui_panel_descriptor.schema`
- `schema/runtime/diagnostics/repro_bundle_manifest.schema`
- `schema/runtime/diagnostics/repro_bundle_index.schema`
- `schema/runtime/diagnostics/replay_request.schema`
- `schema/runtime/diagnostics/replay_result.schema`





- `schema/install.manifest.schema`
- `schema/instance.manifest.schema`
- `schema/runtime.descriptor.schema`
- `schema/pack.sources.schema`
- `schema/sandbox.policy.schema`
- `schema/compat.report.schema`
- `schema/ai.profile.schema`
- `schema/bundle.container.schema`
- `schema/bugreport.bundle.schema`
- `schema/signal.field.schema`
- `schema/signal.interface.schema`
Refusal code anchors:


- `docs/architecture/REFUSAL_SEMANTICS.md`


- `schema/integrity/SPEC_REFUSAL_CODES.md`





Ordering anchors:


- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`

- `docs/architecture/REDUCTION_MODEL.md`

- `docs/architecture/EXECUTION_REORDERING_POLICY.md`


- `docs/architecture/CROSS_SHARD_LOG.md`





#### Enforcement


Contract enforcement lives under:


- `tests/contract/`
 - `tests/invariant/`


- `tests/apps/` (legacy and adjacent contract checks)


## Source: `docs/architecture/CANON_INDEX.md`

Status: CANONICAL
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

### Canon Index (CLEAN-2)

If it is not listed here as CANONICAL, it is not binding.
All binding prompts MUST be materialized as exactly one
canonical document listed here. Prompts themselves are
execution artifacts and are not authoritative.

#### CONVERGE-12 Layout Authority Note

This canon index remains a legacy reference surface for broad documentation discovery. It is not the current physical source repository layout authority. Current layout authority is `contracts/repo/layout.contract.toml`, `contracts/repo/root_allowlist.toml`, `contracts/repo/layout_exceptions.toml`, and `docs/repo/REPO_LAYOUT_TARGET.md`; release/component support posture is governed by `contracts/release/component_matrix.contract.toml` and `docs/release/COMPONENT_MATRIX.md`.

#### CANONICAL
- `docs/domains/processes/PROCESS_REGISTRY.md`
- `docs/game/agents/AGENT_IDENTITY.md`
- `docs/game/agents/AGENT_LIFECYCLE.md`
- `docs/game/agents/AGENT_MODEL.md`
- `docs/game/agents/AGENT_NON_GOALS.md`
- `docs/runtime/shell/APPSHELL_CONSTITUTION.md`
- `docs/runtime/shell/COMMANDS_AND_REFUSALS.md`
- `docs/runtime/shell/FLAG_MIGRATION.md`
- `docs/runtime/shell/IPC_ATTACH_CONSOLES.md`
- `docs/runtime/shell/IPC_DISCOVERY.md`
- `docs/runtime/shell/LOGGING_AND_TRACING.md`
- `docs/runtime/shell/LOG_MERGE_RULES.md`
- `docs/runtime/shell/SUPERVISOR_MODEL.md`
- `docs/runtime/shell/TUI_FRAMEWORK.md`
- `docs/runtime/shell/UI_MODE_RESOLUTION.md`
- `docs/runtime/shell/VIRTUAL_PATHS.md`
- `docs/architecture/ADOPTION_PROTOCOL.md`
- `docs/architecture/AI_BUDGET_MODEL.md`
- `docs/architecture/AI_INTENT_MODEL.md`
- `docs/architecture/ANTI_CHEAT_AND_INTEGRITY.md`
- `docs/architecture/ANTI_CHEAT_AS_LAW.md`
- `docs/architecture/ANTI_ENTROPY_RULES.md`
- `docs/architecture/APP_AUTOMATION_MODEL.md`
- `docs/architecture/APP_CANON0.md`
- `docs/architecture/APP_CANON1.md`
- `docs/architecture/ARCH0_CONSTITUTION.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/ARCHITECTURE_LAYERS.md`
- `docs/architecture/ARCHIVAL_AND_PERMANENCE.md`
- `docs/architecture/ARCHIVE_MANIFEST.md`
- `docs/architecture/ARCH_BUILD_ENFORCEMENT.md`
- `docs/architecture/ARCH_CHANGE_PROCESS.md`
- `docs/architecture/ARCH_ENFORCEMENT.md`
- `docs/architecture/ARCH_REPO_LAYOUT.md`
- `docs/architecture/ARCH_SPEC_OWNERSHIP.md`
- `docs/architecture/ARTIFACT_MODEL.md`
- `docs/architecture/AUDITABILITY_AND_DISCLOSURE.md`
- `docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md`
- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md`
- `docs/architecture/AUTHORITY_IN_REALITY.md`
- `docs/architecture/AUTHORITY_MODEL.md`
- `docs/architecture/BUGREPORT_MODEL.md`
- `docs/architecture/BUILD_IDENTITY_MODEL.md`
- `docs/architecture/BUNDLE_MODEL.md`
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/CANON_CUT_LINE.md`
- `docs/architecture/CANON_INDEX.md`
- `docs/architecture/CAPABILITY_BASELINES.md`
- `docs/architecture/CAPABILITY_ONLY_CANON.md`
- `docs/architecture/CHANGELOG_ARCH.md`
- `docs/architecture/CHANGE_PROTOCOL.md`
- `docs/architecture/CHEATS_ARE_JUST_LAWS.md`
- `docs/architecture/CHECKPOINTING_MODEL.md`
- `docs/architecture/CHECKPOINTS.md`
- `docs/architecture/CIVILIZATION_MODEL.md`
- `docs/architecture/CODE_DATA_BOUNDARY.md`
- `docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md`
- `docs/architecture/COLLAPSE_AND_DECAY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/COMPATIBILITY_MODEL.md`
- `docs/architecture/COMPONENTS.md`
- `docs/architecture/CONFLICT_AND_WAR_MODEL.md`
- `docs/architecture/CONSTANT_COST_GUARANTEE.md`
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/CONTRACTS_INDEX.md`
- `docs/architecture/CONTROL_LAYERS.md`
- `docs/architecture/CRASH_RECOVERY.md`
- `docs/architecture/CROSS_SHARD_LOG.md`
- `docs/architecture/DEATH_AND_CONTINUITY.md`
- `docs/architecture/DECAY_EROSION_REGEN.md`
- `docs/architecture/DEMO_AND_TOURIST_MODEL.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`
- `docs/architecture/DEV_OPS_MODEL.md`
- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md`
- `docs/architecture/DISTRIBUTED_TIME_MODEL.md`
- `docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md`
- `docs/architecture/DISTRIBUTION_LAYOUT.md`
- `docs/architecture/DISTRIBUTION_PROFILES.md`
- `docs/architecture/domino_framework_boundary.md`
- `docs/architecture/DOMAIN_JURISDICTIONS_AND_LAW.md`
- `docs/architecture/DOMAIN_SHARDING_AND_STREAMING.md`
- `docs/architecture/DOMAIN_VOLUMES.md`
- `docs/architecture/ECONOMIC_MODEL.md`
- `docs/architecture/ECONOMY_AND_LOGISTICS.md`
- `docs/architecture/ENERGY_MODEL.md`
- `docs/architecture/ENFORCEMENT_ESCALATION.md`
- `docs/architecture/EPISTEMICS_AND_SCALED_MMO.md`
- `docs/architecture/EPISTEMICS_MODEL.md`
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/EXECUTION_REORDERING_POLICY.md`
- `docs/architecture/EXECUTION_SUBSTRATE_AUDIT.md`
- `docs/architecture/EXISTENCE_AND_REALITY.md`
- `docs/architecture/EXISTENCE_LIFECYCLE.md`
- `docs/architecture/EXOTIC_TRAVEL_AND_REALITY.md`
- `docs/architecture/EXPLORATION_METRICS.md`
- `docs/architecture/EXPLORATION_SCALING_PROOF.md`
- `docs/architecture/EXTEND_VS_CREATE.md`
- `docs/architecture/EXTENSION_RULES.md`
- `docs/architecture/FABRICATION_MODEL.md`
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/FLUIDS_MODEL.md`
- `docs/architecture/FORKING_AND_PROVIDES_MODEL.md`
- `docs/architecture/FUTURE_COMPATIBILITY_AND_ARCH.md`
- `docs/architecture/FUTURE_PROOFING.md`
- `docs/architecture/GENERATED_CODE_POLICY.md`
- `docs/architecture/GLOBAL_ID_MODEL.md`
- `docs/architecture/GLOSSARY.md`
- `docs/architecture/GOVERNANCE_AND_INSTITUTIONS.md`
- `docs/architecture/GUI_BASELINE.md`
- `docs/architecture/HARDWARE_EVOLUTION_STRATEGY.md`
- `docs/architecture/HAZARDS_MODEL.md`
- `docs/architecture/IDENTITY_ACROSS_TIME.md`
- `docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md`
- `docs/architecture/ID_AND_NAMESPACE_RULES.md`
- `docs/architecture/INDEXING_POLICY.md`
- `docs/architecture/INFORMATION_MODEL.md`
- `docs/architecture/INSTALLER_CONTRACT.md`
- `docs/architecture/INSTALL_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
- `docs/architecture/INSTITUTIONS_AND_GOVERNANCE_MODEL.md`
- `docs/architecture/INTEREST_MODEL.md`
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/INVARIANTS_AND_TOLERANCES.md`
- `docs/architecture/INVARIANT_REGISTRY.md`
- `docs/architecture/JOIN_RESYNC_CONTRACT.md`
- `docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md`
- `docs/architecture/KNOWN_BLOCKERS.md`
- `docs/architecture/LANGUAGE_STRATEGY.md`
- `docs/architecture/LAUNCHER_CONTRACT.md`
- `docs/architecture/LAW_AND_META_LAW.md`
- `docs/architecture/LAW_ENFORCEMENT_POINTS.md`
- `docs/architecture/LEGACY_SUPPORT_MODEL.md`
- `docs/architecture/LEGACY_SUPPORT_STRATEGY.md`
- `docs/architecture/LIFE_AND_POPULATION.md`
- `docs/architecture/LIVE_EVOLUTION_MODEL.md`
- `docs/architecture/LOCKFILES.md`
- `docs/architecture/LOCKLIST.md`
- `docs/architecture/MACRO_TIME_MODEL.md`
- `docs/architecture/MMO_COMPATIBILITY.md`
- `docs/architecture/MMO_SAFETY_MODEL.md`
- `docs/architecture/MODPACK_FORMAT.md`
- `docs/architecture/MOD_ECOSYSTEM_RULES.md`
- `docs/architecture/mod_pack_trust_model.md`
- `docs/architecture/MOVEMENT_AS_LOGISTICS.md`
- `docs/architecture/NAMESPACING_RULES.md`
- `docs/architecture/NON_INTERFERENCE.md`
- `docs/architecture/NO_MAGIC_TELEPORTS.md`
- `docs/architecture/NO_TELEPORTATION_EXCEPT_BY_CONTRACT.md`
- `docs/architecture/OPS_TRANSACTION_MODEL.md`
- `docs/architecture/OVERVIEW_ARCHITECTURE.md`
- `docs/architecture/PACK_FORMAT.md`
- `docs/architecture/PERFORMANCE_METRICS.md`
- `docs/architecture/PERFORMANCE_PROOF.md`
- `docs/architecture/PIRACY_CONTAINMENT.md`
- `docs/architecture/PLATFORM_RESPONSIBILITY.md`
- `docs/architecture/portability_matrix.md`
- `docs/architecture/native_architecture_policy.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/PRODUCT_SHELL_CONTRACT.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/PROJECT_EXECUTION_BASELINE.md`
- `docs/architecture/REALITY_FLOW.md`
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/REALITY_MODEL.md`
- `docs/architecture/REDUCTION_MODEL.md`
- `docs/architecture/REFINEMENT_CONTRACTS.md`
- `docs/architecture/REFRACTOR_STAGE.md`
- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/REGISTRY_PATTERN.md`
- `docs/architecture/RENDERER_RESPONSIBILITY.md`
- `docs/architecture/REPLAY_AND_TIME_ASYMMETRY.md`
- `docs/architecture/REPLAY_FORMAT.md`
- `docs/architecture/REPORT_GAME_ARCH_DECISIONS.md`
- `docs/architecture/REPOX_AUTOMATION_MODEL.md`
- `docs/architecture/REPO_INTENT.md`
- `docs/architecture/REPO_NAV.md`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/architecture/RISK_AND_LIABILITY_MODEL.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/ROLLING_UPDATES.md`
- `docs/architecture/SANDBOX_MODEL.md`
- `docs/architecture/SAVE_FORMAT.md`
- `docs/architecture/SAVE_MODEL.md`
- `docs/architecture/SAVE_PIPELINE.md`
- `docs/architecture/SCALE_AND_COMPLEXITY.md`
- `docs/architecture/SCALING_COMPATIBILITY.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/SCHEMA_CHANGE_NOTES.md`
- `docs/architecture/SCHEMA_STABILITY.md`
- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`
- `docs/architecture/SERVICES_AND_PRODUCTS.md`
- `docs/architecture/service_conformance_law.md`
- `docs/architecture/provider_conformance_law.md`
- `docs/architecture/SETUP_TRANSACTION_MODEL.md`
- `docs/architecture/SHARD_LIFECYCLE.md`
- `docs/architecture/SIGNAL_MODEL.md`
- `docs/architecture/SKU_MATRIX.md`
- `docs/architecture/SLICE_0_CONTRACT.md`
- `docs/architecture/SLICE_1_CONTRACT.md`
- `docs/architecture/SLICE_2_CONTRACT.md`
- `docs/architecture/SPACE_AND_BOUNDS.md`
- `docs/architecture/SPACE_TIME_EXISTENCE.md`
- `docs/architecture/SPECTATOR_AND_AUDIT_MODES.md`
- `docs/architecture/SPECTATOR_TO_GODMODE.md`
- `docs/architecture/SRZ_MODEL.md`
- `docs/architecture/STRUCTURAL_STABILITY_MODEL.md`
- `docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md`
- `docs/architecture/TERRAIN_COORDINATES.md`
- `docs/architecture/TERRAIN_FIELDS.md`
- `docs/architecture/TERRAIN_MACRO_CAPSULE.md`
- `docs/architecture/TERRAIN_OVERLAYS.md`
- `docs/architecture/TERRAIN_PROVIDER_CHAIN.md`
- `docs/architecture/TERRAIN_TRUTH_MODEL.md`
- `docs/architecture/THERMAL_MODEL.md`
- `docs/architecture/THREAT_MODEL.md`
- `docs/architecture/TIMELINE_FORKS_AND_HISTORY.md`
- `docs/architecture/TIME_DILATION_WITHOUT_TIME_WARP.md`
- `docs/architecture/TIME_PERCEPTION_VS_SIMULATION.md`
- `docs/architecture/TOOLS_AS_CAPABILITIES.md`
- `docs/architecture/TRANSITION_PLAYBOOK.md`
- `docs/architecture/TRAVEL_AND_MOVEMENT.md`
- `docs/architecture/TRAVEL_CAPACITY_AND_COST.md`
- `docs/architecture/TRUST_AND_LEGITIMACY_MODEL.md`
- `docs/architecture/UI_BINDING_MODEL.md`
- `docs/architecture/UNIT_SYSTEM_POLICY.md`
- `docs/architecture/UNKNOWN_UNKNOWNS.md`
- `docs/architecture/UPDATE_MODEL.md`
- `docs/architecture/UPGRADE_AND_CONVERSION.md`
- `docs/architecture/VALIDATION_RULES.md`
- `docs/architecture/versioning_and_deprecation.md`
- `docs/architecture/VISITABILITY_AND_REFINEMENT.md`
- `docs/architecture/VISITABILITY_CONSISTENCY.md`
- `docs/architecture/WHAT_THIS_IS.md`
- `docs/architecture/WHAT_THIS_IS_NOT.md`
- `docs/architecture/WHY_ECONOMIES_DONT_FAKE.md`
- `docs/architecture/WHY_NPCS_DONT_POP.md`
- `docs/architecture/WORKSPACES.md`
- `docs/architecture/WORLDDEFINITION.md`
- `docs/architecture/WORLDDEFINITION_CONTRACT.md`
- `docs/archive/audit/ARCH_AUDIT_CONSTITUTION.md`
- `docs/archive/audit/ARTIFACT_MANIFEST_BASELINE.md`
- `docs/archive/audit/FORKING_PROVIDES_BASELINE.md`
- `docs/archive/audit/INSTALL_MANIFEST_BASELINE.md`
- `docs/archive/audit/INSTANCE_MANIFEST_BASELINE.md`
- `docs/archive/audit/INSTITUTIONAL_COMMS_BASELINE.md`
- `docs/archive/audit/MACROCAPSULE_BEHAVIOR_BASELINE.md`
- `docs/archive/audit/SAVE_MANIFEST_BASELINE.md`
- `docs/archive/audit/SIG7_RETRO_AUDIT.md`
- `docs/archive/audit/SUPERVISOR_HARDENING_FINAL.md`
- `docs/archive/audit/SUPERVISOR_SURFACE_MAP.md`
- `docs/archive/audit/SYSTEM_TIER_ROI_BASELINE.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/domains/civilization/COHORT_MODEL.md`
- `docs/domains/civilization/DEMOGRAPHY_OPTIONALITY.md`
- `docs/domains/civilization/DIPLOMACY_STUBS.md`
- `docs/domains/civilization/FACTIONS_AND_AFFILIATION.md`
- `docs/domains/civilization/INSTITUTIONS_AND_ROLES.md`
- `docs/domains/civilization/MIGRATION_AND_ASSIMILATION.md`
- `docs/domains/civilization/ORDER_LANGUAGE.md`
- `docs/domains/civilization/TERRITORY_AND_CLAIMS.md`
- `docs/apps/client/CLIENT_SETTINGS.md`
- `docs/apps/client/CLIENT_UI_AND_FLOW.md`
- `docs/compatibility/DATA_FORMAT_VERSIONING.md`
- `docs/compatibility/DEGRADE_LADDERS.md`
- `docs/compatibility/ENDPOINT_DESCRIPTORS.md`
- `docs/compatibility/NEGOTIATION_HANDSHAKES.md`
- `docs/reference/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`
- `docs/reference/contracts/SEMANTIC_CONTRACT_MODEL.md`
- `docs/governance/control/CONTROL_EXTENSION_CONTRACT.md`
- `docs/governance/control/CONTROL_PLANE_CONSTITUTION.md`
- `docs/build/toolchain_portability.md`
- `docs/development/NOW_SOON_LATER_ROADMAP.md`
- `docs/development/portability_guidelines.md`
- `docs/development/pointer_width_and_serialization.md`
- `docs/runtime/diagnostics/REPRO_BUNDLE_MODEL.md`
- `docs/domains/embodiment/EMBODIMENT_BASELINE.md`
- `docs/domains/embodiment/LOCOMOTION_POLISH_MODEL.md`
- `docs/domains/embodiment/MVP_TOOLBELT_MODEL.md`
- `docs/domains/embodiment/TERRAIN_COLLISION_MODEL.md`
- `docs/engine/CONCURRENCY_DETERMINISM_CONTRACT.md`
- `docs/domains/geology/OVERLAY_CONFLICT_POLICIES.md`
- `docs/governance/AUDITX_PROMOTION_POLICY.md`
- `docs/governance/COMPATX_MODEL.md`
- `docs/governance/CONTROLX_MODEL.md`
- `docs/governance/GATE_THROUGHPUT_POLICY.md`
- `docs/governance/PERFORMX_MODEL.md`
- `docs/governance/PROMPT_FIREWALL_POLICY.md`
- `docs/governance/REMEDIATION_STATE_MACHINE.md`
- `docs/governance/SEMANTIC_ESCALATION_POLICY.md`
- `docs/governance/TESTX_ARCHITECTURE.md`
- `docs/governance/UNBOUNDED_AGENTIC_DEVELOPMENT.md`
- `docs/governance/XSTACK_EXTENSION_MODEL.md`
- `docs/governance/XSTACK_INCREMENTAL_MODEL.md`
- `docs/governance/XSTACK_PORTABILITY.md`
- `docs/governance/XSTACK_PRODUCTION_CRITERIA.md`
- `docs/governance/XSTACK_TEMPLATE_CHECKLIST.md`
- `docs/governance/XSTACK_TRACK_IGNORE_POLICY.md`
- `docs/development/guides/TOOLING_OVERVIEW.md`
- `docs/development/guides/ui_editor/README.md`
- `docs/domains/interiors/COMPARTMENT_FLOWS.md`
- `docs/domains/interiors/INTERIOR_INSPECTION_AND_DIEGETICS.md`
- `docs/apps/launcher/LAUNCHER_SETTINGS.md`
- `docs/runtime/storage/EXPORT_IMPORT_FORMAT.md`
- `docs/domains/logic/LOGIC_CONSTITUTION.md`
- `docs/domains/logic/LOGIC_ELEMENT_MODEL.md`
- `docs/domains/logic/LOGIC_EVALUATION_ENGINE.md`
- `docs/domains/logic/SIGNAL_AND_BUS_MODEL.md`
- `docs/governance/meta/EXTENSION_DISCIPLINE.md`
- `docs/governance/meta/PROVENANCE_AND_COMPACTION_CONSTITUTION.md`
- `docs/governance/meta/UNIVERSE_CONTRACT_BUNDLE.md`
- `docs/domains/mobility/MAINTENANCE_AND_WEAR.md`
- `docs/domains/mobility/SIGNALING_AND_INTERLOCKING.md`
- `docs/modding/MOD_TRUST_AND_CAPABILITIES.md`
- `docs/release/mvp/PRODUCT_BOOT_MATRIX.md`
- `docs/content/packs/PACK_COMPATIBILITY_MANIFEST.md`
- `docs/content/packs/PACK_VERIFICATION_PIPELINE.md`
- `docs/content/packs/sol/PACK_SOL_PIN_MINIMAL.md`
- `docs/governance/policies/COMPATIBILITY_PROMISES.md`
- `docs/governance/policies/DEPRECATION_POLICY.md`
- `docs/governance/policies/DETERMINISM_REGRESSION_RULES.md`
- `docs/governance/policies/FEATURE_EPOCH_POLICY.md`
- `docs/governance/policies/LONG_TERM_SUPPORT_POLICY.md`
- `docs/governance/policies/RENDER_BACKEND_LIFECYCLE.md`
- `docs/release/ARTIFACT_NAMING_RULES.md`
- `docs/release/COMPONENT_GRAPH_CONSTITUTION.md`
- `docs/release/DISTRIBUTION_MODEL.md`
- `docs/release/DIST_BUNDLE_ASSEMBLY.md`
- `docs/release/DIST_PLATFORM_MATRIX_MODEL.md`
- `docs/release/DIST_VERIFICATION_RULES.md`
- `docs/release/FROZEN_INVARIANTS_v0_0_0.md`
- `docs/release/INTEROP_MATRIX_v0_0_0_mock.md`
- `docs/release/MVP_SCOPE_LOCK.md`
- `docs/release/PROVISIONAL_FEATURE_LIST.md`
- `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`
- `docs/release/RELEASE_MANIFEST_MODEL.md`
- `docs/release/RELEASE_NOTES_v0_0_0_mock.md`
- `docs/release/architecture_support_policy.md`
- `docs/release/platform_support_policy.md`
- `docs/release/REPRODUCIBLE_BUILD_RULES.md`
- `docs/release/SIGNING_POLICY.md`
- `docs/archive/restructure/FUTURE_LAYOUT_PROPOSAL.md`
- `docs/archive/restructure/RESTRUCTURE_RISKS.md`
- `docs/archive/restructure/SHIM_POLICY.md`
- `docs/domains/scale/GALAXY_SCALE_READINESS.md`
- `docs/security/TRUST_AND_SIGNING_MODEL.md`
- `docs/apps/server/LOCAL_SINGLEPLAYER_MODEL.md`
- `docs/apps/server/SERVER_MVP_BASELINE.md`
- `docs/apps/server/SERVER_SETTINGS.md`
- `docs/runtime/settings/SETTINGS_OWNERSHIP_MODEL.md`
- `docs/apps/setup/SETUP_SETTINGS.md`
- `docs/domains/signals/INSTITUTIONAL_COMMS_MODEL.md`
- `docs/domains/signals/MESSAGE_SEMANTICS.md`
- `docs/domains/signals/SIGNALS_CONSTITUTION.md`
- `docs/domains/signals/SIGNAL_NETWORKGRAPH.md`
- `docs/domains/signals/SIGNAL_QUALITY_MODEL.md`
- `docs/domains/signals/TRUST_AND_BELIEF_MODEL.md`
- `docs/reference/specs/CIV0_POPULATION_GENESIS.md`
- `docs/reference/specs/CIV0a_SURVIVAL_LOOP.md`
- `docs/reference/specs/CIV1_CITIES_INFRA.md`
- `docs/reference/specs/CIV2_GOVERNANCE.md`
- `docs/reference/specs/CIV3_KNOWLEDGE_TECH.md`
- `docs/reference/specs/CIV4_SCALE_AND_LOGISTICS.md`
- `docs/reference/specs/CONTRACTS.md`
- `docs/reference/specs/DATA_FORMATS.md`
- `docs/reference/specs/SPEC_ABI_TEMPLATES.md`
- `docs/reference/specs/SPEC_ACTIONS.md`
- `docs/reference/specs/SPEC_CONTAINER_TLV.md`
- `docs/reference/specs/SPEC_CORE.md`
- `docs/reference/specs/SPEC_DETERMINISM.md`
- `docs/reference/specs/SPEC_DETERMINISM_GRADES.md`
- `docs/reference/specs/SPEC_DOMAINS_FRAMES_PROP.md`
- `docs/reference/specs/SPEC_DUI.md`
- `docs/reference/specs/SPEC_LANGUAGE_BASELINES.md`
- `docs/reference/specs/SPEC_LOD.md`
- `docs/reference/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/reference/specs/SPEC_NUMERIC.md`
- `docs/reference/specs/SPEC_PACKETS.md`
- `docs/reference/specs/SPEC_POSE_AND_ANCHORS.md`
- `docs/reference/specs/SPEC_SIM_SCHEDULER.md`
- `docs/reference/specs/SPEC_TRANS_STRUCT_DECOR.md`
- `docs/reference/specs/setup/INVARIANTS.md`
- `docs/reference/specs/setup/JOB_ENGINE.md`
- `docs/reference/specs/setup/PARITY_LOCK_MATRIX.md`
- `docs/reference/specs/setup/SPLAT_SELECTION_RULES.md`
- `docs/architecture/system/EXPLICIT_STATE_VECTOR_RULE.md`
- `docs/architecture/system/SYSTEM_FORENSICS_MODEL.md`
- `docs/architecture/system/SYSTEM_RELIABILITY_MODEL.md`
- `docs/architecture/system/SYS_SHARD_BOUNDARY_RULES.md`
- `docs/development/tools/TOOLS_SETTINGS.md`
- `docs/runtime/ui/UI_ADAPTER_CONTRACT.md`
- `docs/runtime/ui/UI_IR_SCHEMA_AND_LAYOUTS.md`
- `docs/runtime/ui/UI_MODDING_AND_THEMES.md`
- `docs/runtime/ui/UI_SYSTEM_DOCTRINE.md`
- `docs/runtime/ui/ux/MVP_VIEWER_SHELL.md`
- `docs/testing/validation/VALIDATION_PIPELINE.md`
- `docs/domains/worldgen/EARTH_HYDROLOGY_MODEL.md`
- `docs/domains/worldgen/EARTH_ILLUMINATION_SHADOW_MODEL.md`
- `docs/domains/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`
- `docs/domains/worldgen/EARTH_SEASONAL_CLIMATE_MODEL.md`
- `docs/domains/worldgen/EARTH_SKY_STARFIELD_MODEL.md`
- `docs/domains/worldgen/EARTH_TIDE_PROXY_MODEL.md`
- `docs/domains/worldgen/EARTH_WATER_VISUAL_MODEL.md`
- `docs/domains/worldgen/EARTH_WIND_PROXY_MODEL.md`
- `docs/domains/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/domains/worldgen/PLANET_SURFACE_MACRO_MODEL.md`
- `docs/domains/worldgen/REAL_DATA_IMPORT_PIPELINE.md`
- `docs/domains/worldgen/REFINEMENT_PIPELINE_MODEL.md`
- `docs/domains/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md`
- `docs/domains/worldgen/STAR_SYSTEM_SEED_MODEL.md`
- `docs/domains/worldgen/UNIVERSE_SCALE_STRATEGY.md`
- `docs/domains/worldgen/WORLDGEN_CONSTRAINTS.md`
- `docs/domains/worldgen/WORLDGEN_PIPELINE.md`
- `docs/domains/worldgen/WORLDGEN_PREVIEW_AND_OPTIMIZATION.md`

<!-- POST-CONVERGE-10H: canonical header/index drift repair -->
- `docs/game/agents/AGENT_MIRROR_POLICY.md`
- `docs/game/agents/AGENT_SAFETY_POLICY.md`
- `docs/game/agents/MCP_INTERFACE_MODEL.md`
- `docs/game/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`
- `docs/game/agents/XSTACK_TASK_CATALOG.md`
- `docs/planning/CHECKPOINT_C_LATER_WAVE_ZETA_ADMISSION_REVIEW.md`
- `docs/planning/CHECKPOINT_C_PHIB3_YB_SAFE_REVIEW.md`
- `docs/planning/CHECKPOINT_C_PHIB5_ADMISSION_REVIEW.md`
- `docs/planning/CHECKPOINT_C_POST_ZETA_A_FIRST_WAVE_REVIEW.md`
- `docs/planning/CHECKPOINT_C_POST_ZETA_B3_REVIEW.md`
- `docs/planning/CHECKPOINT_C_PRE_ZETA_ADMISSION.md`
- `docs/planning/CHECKPOINT_C_YA_SAFE_REVIEW.md`
- `docs/planning/CHECKPOINT_C_YC_SAFE_REVIEW.md`
- `docs/planning/CHECKPOINT_C_ZETA_A_ADMISSION_REVIEW.md`
- `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`
- `docs/planning/CROSS_DOMAIN_BRIDGE_TEMPLATE.md`
- `docs/planning/DOMAIN_CONSTITUTION_EXECUTION_PLAN.md`
- `docs/planning/LATER_WAVE_BOUNDARY_RECONCILIATION.md`
- `docs/planning/LATER_WAVE_EXECUTION_GATES.md`
- `docs/planning/LATER_WAVE_PREREQUISITE_MATRIX.md`
- `docs/planning/LIVE_OPERATIONS_PREREQUISITE_MATRIX.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB3_YB.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB4.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_PHIB5.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_YA.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_YC.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_YD.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_ZA_FIRST_WAVE.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_ZB.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_ZB3.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`
- `docs/planning/NEXT_EXECUTION_ORDER_POST_ZP.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MATRIX.md`
- `docs/planning/POST_ZETA_FRONTIER_RECONCILIATION_AND_HANDOFF.md`
- `docs/planning/TRUST_AWARE_REFUSAL_AND_CONTAINMENT_RECONCILIATION.md`
- `docs/planning/UNIVERSAL_DOMAIN_CONSTITUTION_TEMPLATE.md`
- `docs/planning/UNIVERSAL_REALITY_FRAMEWORK_RECONCILIATION.md`
- `docs/planning/VERIFICATION_AND_EQUIVALENCE_DOCTRINE_RECONCILIATION.md`
- `docs/planning/ZETA_BLOCKER_RECONCILIATION.md`
- `docs/planning/ZETA_EXECUTION_GATES.md`
- `docs/planning/ZETA_FINAL_ADMISSIBLE_SCOPE.md`
- `docs/planning/ZETA_REMAINING_FRONTIER_AND_CLOSURE_BASELINE.md`
- `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`
- `docs/release/ARTIFACT_NAMING_CHANGELOG_TARGET_POLICY.md`
- `docs/release/CANARY_AND_DETERMINISTIC_DOWNGRADE_EXECUTION.md`
- `docs/release/LIVE_CUTOVER_RECEIPTS_AND_PROVENANCE_GENERALIZATION.md`
- `docs/release/LIVE_CUTOVER_RECEIPT_PIPELINE_ANCHORIZATION.md`
- `docs/release/LIVE_TRUST_ROTATION_AND_REVOCATION_PROPAGATION_PREREQUISITES.md`
- `docs/release/MANUAL_AUTOMATION_PARITY_AND_REHEARSAL.md`
- `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`
- `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`
- `docs/release/PRESET_AND_TOOLCHAIN_CONSOLIDATION.md`
- `docs/release/PUBLICATION_AND_TRUST_EXECUTION_OPERATIONALIZATION_GATES.md`
- `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`
- `docs/release/RELEASE_CONTRACT_PROFILE.md`
- `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`
- `docs/release/RELEASE_OPS_EXECUTION_ENVELOPE.md`
- `docs/release/RELEASE_REHEARSAL_SANDBOX_AND_PROOF_BACKED_ROLLBACK_ALIGNMENT.md`
- `docs/release/TRUST_EXECUTION_AND_REVOCATION_CONTINUITY.md`
- `docs/release/VERSIONING_CONSTITUTION.md`
- `docs/runtime/BOUNDED_RUNTIME_CUTOVER_PROOF_REHEARSAL.md`
- `docs/runtime/COMPONENT_MODEL.md`
- `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`
- `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`
- `docs/runtime/HOTSWAP_BOUNDARIES.md`
- `docs/runtime/LIFECYCLE_MANAGER.md`
- `docs/runtime/MULTI_VERSION_COEXISTENCE.md`
- `docs/runtime/ROLLBACK_BEARING_STAGED_TRANSITION_VALIDATION.md`
- `docs/runtime/RUNTIME_KERNEL_MODEL.md`
- `docs/runtime/RUNTIME_SERVICES.md`
- `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`
- `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`
- `docs/security/TRUST_STRICT_MODEL_v0_0_0.md`
- `docs/development/xstack/AIDE_ADAPTER_CONTRACT.md`
- `docs/development/xstack/AIDE_CAPABILITY_PROFILE_SHAPE.md`
- `docs/development/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`
- `docs/development/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`
- `docs/development/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`
- `docs/development/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`
- `docs/development/xstack/CODEX_REPO_OPERATING_CONTRACT.md`
- `docs/development/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`
- `docs/development/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`
- `docs/development/xstack/XSTACK_SCOPE_FREEZE.md`
- `docs/development/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`
- `docs/repo/provider_structure_canon.md`

#### DERIVED
- `docs/repo/final_repository_structure.md`
- `docs/architecture/ROOT_ARCHITECTURE.md`
- `docs/game/CAPABILITY_STAGES.md`
- `docs/development/CODE_CHANGE_JUSTIFICATION.md`
- `docs/development/CONTRIBUTING.md`
- `docs/reference/FAQ.md`
- `docs/reference/GLOSSARY.md`
- `docs/modding/MODDER_GUIDE.md`
- `docs/reference/PHILOSOPHY.md`
- `docs/README.md`
- `docs/reference/schema/SCHEMA_CANON_ALIGNMENT.md`
- `docs/reference/schema/SCHEMA_EVOLUTION.md`
- `docs/archive/STATUS_NOW.md`
- `docs/archive/SURVIVAL_SLICE.md`
- `docs/testing/TESTX_STAGE_MATRIX.md`
- `docs/game/player/WHAT_PLAYERS_CAN_DO.md`
- `docs/development/xstack/XSTACK.md`
- `docs/runtime/ui/accessibility/ACCESSIBILITY_MODEL.md`
- `docs/game/agents/AGENT_CONFLICT.md`
- `docs/game/agents/AGENT_CONTRACTS.md`
- `docs/game/agents/AGENT_FAILURE.md`
- `docs/game/agents/AGENT_GOALS.md`
- `docs/game/agents/AGENT_HISTORY.md`
- `docs/game/agents/AGENT_HISTORY_MACRO.md`
- `docs/game/agents/AGENT_INSTITUTIONS.md`
- `docs/game/agents/AGENT_KNOWLEDGE.md`
- `docs/game/agents/AGENT_MEMORY.md`
- `docs/game/agents/AGENT_PLANNING.md`
- `docs/game/agents/AGENT_POWER.md`
- `docs/apps/ARTIFACT_IDENTITY.md`
- `docs/apps/CLIENT_IDE_START_POINTS.md`
- `docs/apps/CLIENT_READONLY_INTEGRATION.md`
- `docs/apps/CLIENT_RENDERER_UI.md`
- `docs/apps/CLIENT_UI_LAYER.md`
- `docs/apps/CLI_CONTRACTS.md`
- `docs/apps/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md`
- `docs/apps/COMPATIBILITY_ENFORCEMENT.md`
- `docs/apps/ENGINE_GAME_DIAGNOSTICS.md`
- `docs/apps/GUI_MODE.md`
- `docs/apps/HEADLESS_AND_ZERO_PACK.md`
- `docs/apps/IDE_WORKFLOW.md`
- `docs/apps/NATIVE_UI_POLICY.md`
- `docs/apps/OBSERVABILITY_PIPELINES.md`
- `docs/apps/PRODUCT_BOUNDARIES.md`
- `docs/apps/README.md`
- `docs/apps/READONLY_ADAPTER.md`
- `docs/apps/RUNTIME_LOOP.md`
- `docs/apps/TESTX_COMPLIANCE.md`
- `docs/apps/TESTX_INVENTORY.md`
- `docs/apps/TIMING_AND_CLOCKS.md`
- `docs/apps/TOOLS_OBSERVABILITY.md`
- `docs/apps/TOOLS_UI_POLICY.md`
- `docs/apps/TUI_MODE.md`
- `docs/apps/UI_MODES.md`
- `docs/runtime/shell/CLI_REFERENCE.md`
- `docs/runtime/shell/TOOL_REFERENCE.md`
- `docs/architecture/ADAPTER_PATTERN.md`
- `docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md`
- `docs/architecture/api_abi_canon.md`
- `docs/architecture/APPLICATION_CONTRACTS.md`
- `docs/architecture/artifact_identity_law.md`
- `docs/architecture/ARCHITECTURE_GRAPH_SPEC_v1.md`
- `docs/architecture/ARTIFACT_LIFECYCLE.md`
- `docs/architecture/BEHAVIORAL_COMPONENTS_STANDARD.md`
- `docs/architecture/BOUNDARY_ENFORCEMENT.md`
- `docs/architecture/BUDGET_POLICY.md`
- `docs/architecture/C_COMPATIBLE_ABI_BOUNDARY.md`
- `docs/architecture/capability_refusal_law.md`
- `docs/architecture/command_result_view_slice.md`
- `docs/architecture/command_view_event_refusal.md`
- `docs/architecture/COLLAPSE_EXPAND_SOLVERS.md`
- `docs/architecture/composition_resolver_law.md`
- `docs/architecture/COMPLEXITY_AND_SCALE.md`
- `docs/architecture/CORE_ABSTRACTIONS.md`
- `docs/architecture/dependency_direction_law.md`
- `docs/architecture/diagnostics_and_evidence.md`
- `docs/architecture/document_patch_transaction_runtime.md`
- `docs/architecture/document_patch_transaction.md`
- `docs/architecture/lockfile_law.md`
- `docs/architecture/module_composition_law.md`
- `docs/architecture/package_mount_slice.md`
- `docs/architecture/pack_mount_model.md`
- `docs/architecture/project_graph_service.md`
- `docs/architecture/project_graph_impact_model.md`
- `docs/architecture/provider_model.md`
- `docs/architecture/provider_selection_model.md`
- `docs/architecture/replay_proof_law.md`
- `docs/architecture/replay_proof_slice.md`
- `docs/architecture/replacement_protocol.md`
- `docs/architecture/schema_protocol_evolution.md`
- `docs/architecture/view_action_projection_model.md`
- `docs/architecture/workbench_workspace_model.md`
- `docs/architecture/app_composition_model.md`
- `docs/architecture/barebones_client_shell.md`
- `docs/architecture/DEPRECATION_AND_QUARANTINE.md`
- `docs/architecture/DEPRECATION_LIFECYCLE.md`
- `docs/architecture/DIRECTORY_CONTEXT.md`
- `docs/architecture/DIRECTORY_STRUCTURE.md`
- `docs/architecture/DUPLICATION_DETECTION_RULES.md`
- `docs/architecture/EXTENSION_MAP.md`
- `docs/architecture/FLOWSYSTEM_STANDARD.md`
- `docs/architecture/HISTORY_AND_CIVILIZATION_MODEL.md`
- `docs/architecture/IDE_PROJECTIONS.md`
- `docs/architecture/KNOWN_WARNINGS.md`
- `docs/architecture/MIGRATION_TEMPLATE.md`
- `docs/architecture/MODES_AS_PROFILES.md`
- `docs/architecture/MODULE_BOUNDARIES_v1.md`
- `docs/architecture/MODULE_INDEX_v1.md`
- `docs/architecture/NETWORKGRAPH_STANDARD.md`
- `docs/architecture/POST_CLEAN_2_STATUS.md`
- `docs/architecture/public_surface_registry.md`
- `docs/architecture/QUANTITY_BUNDLES.md`
- `docs/architecture/REPOSITORY_STRUCTURE_v1.md`
- `docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md`
- `docs/architecture/SHIM_SUNSET_PLAN.md`
- `docs/architecture/SOURCE_POCKET_POLICY_v1.md`
- `docs/architecture/STANDARDS_AND_META_SYSTEMS_MODEL.md`
- `docs/architecture/SYSTEM_TOPOLOGY_MAP.md`
- `docs/architecture/TERMINOLOGY_GLOSSARY.md`
- `docs/architecture/astronomy_catalogs.md`
- `docs/architecture/camera_and_navigation.md`
- `docs/architecture/coordinate_model.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/architecture/deterministic_parallelism.md`
- `docs/architecture/fidelity_policy.md`
- `docs/architecture/hash_anchors.md`
- `docs/architecture/interest_regions.md`
- `docs/architecture/lens_system.md`
- `docs/architecture/lockfile.md`
- `docs/architecture/macro_capsules.md`
- `docs/architecture/observation_kernel.md`
- `docs/architecture/pack_system.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/setup_and_launcher.md`
- `docs/architecture/site_registry.md`
- `docs/architecture/srz_contract.md`
- `docs/architecture/time_model.md`
- `docs/architecture/truth_model.md`
- `docs/architecture/truth_perceived_render.md`
- `docs/architecture/ui_registry.md`
- `docs/archive/audit/ACTION_SURFACE_BASELINE.md`
- `docs/archive/audit/AG1_MVP_VALIDATION.md`
- `docs/archive/audit/AG2_MVP_COMPLETION.md`
- `docs/archive/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md`
- `docs/archive/audit/APPSHELL0_RETRO_AUDIT.md`
- `docs/archive/audit/APPSHELL1_RETRO_AUDIT.md`
- `docs/archive/audit/APPSHELL2_RETRO_AUDIT.md`
- `docs/archive/audit/APPSHELL3_RETRO_AUDIT.md`
- `docs/archive/audit/APPSHELL4_RETRO_AUDIT.md`
- `docs/archive/audit/APPSHELL6_RETRO_AUDIT.md`
- `docs/archive/audit/APPSHELL_BOOTSTRAP_BASELINE.md`
- `docs/archive/audit/APPSHELL_COMMANDS_BASELINE.md`
- `docs/archive/audit/APPSHELL_IPC_BASELINE.md`
- `docs/archive/audit/APPSHELL_LOGGING_BASELINE.md`
- `docs/archive/audit/APPSHELL_TUI_BASELINE.md`
- `docs/archive/audit/ARCHITECTURE_HEALTH.md`
- `docs/archive/audit/ARCHITECTURE_HEALTH_REPORT.md`
- `docs/archive/audit/ARCHIVE_POLICY0_RETRO_AUDIT.md`
- `docs/archive/audit/ARCHIVE_POLICY_BASELINE.md`
- `docs/archive/audit/ARCH_AUDIT0_RETRO_AUDIT.md`
- `docs/archive/audit/ARCH_AUDIT1_FINAL_REPORT.md`
- `docs/archive/audit/ARCH_AUDIT2_CONSTITUTION.md`
- `docs/archive/audit/ARCH_AUDIT2_FINAL.md`
- `docs/archive/audit/ARCH_AUDIT2_REPORT.md`
- `docs/archive/audit/ARCH_AUDIT2_RETRO_AUDIT.md`
- `docs/archive/audit/ARCH_AUDIT_BASELINE.md`
- `docs/archive/audit/ARCH_AUDIT_FIX_PLAN.md`
- `docs/archive/audit/ARCH_AUDIT_REPORT.md`
- `docs/archive/audit/ARCH_MATRIX0_RETRO_AUDIT.md`
- `docs/archive/audit/ARCH_MATRIX_FINAL.md`
- `docs/archive/audit/AUDITX_BASELINE_REPORT.md`
- `docs/archive/audit/AUDITX_OVERHAUL_REPORT.md`
- `docs/archive/audit/BEHAVIORAL_COMPONENTS_BASELINE.md`
- `docs/archive/audit/BINARY_BUILD_MATRIX.md`
- `docs/archive/audit/BODY_COLLISION_BASELINE.md`
- `docs/archive/audit/BOM_AG_BASELINE.md`
- `docs/archive/audit/BOUNDARY_AUDIT.md`
- `docs/archive/audit/BOUNDARY_BLOCKERS_BASELINE.md`
- `docs/archive/audit/BR0_BASELINE.md`
- `docs/archive/audit/BR0_COMPLETION_REPORT.md`
- `docs/archive/audit/BR0_PUBLIC_HEADER_FAILS.md`
- `docs/archive/audit/BR0_RERUN_SEQUENCE.md`
- `docs/archive/audit/BR0_STUB_RESOLUTION.md`
- `docs/archive/audit/BUILD_PRESET_AND_WORKFLOW_REPORT.md`
- `docs/archive/audit/CAMERA_VIEW_BASELINE.md`
- `docs/archive/audit/CANON_CONFORMANCE_REPORT.md`
- `docs/archive/audit/CANON_MAP.md`
- `docs/archive/audit/CAPABILITY_REGISTRY_BASELINE.md`
- `docs/archive/audit/CAP_NEG1_RETRO_AUDIT.md`
- `docs/archive/audit/CAP_NEG2_RETRO_AUDIT.md`
- `docs/archive/audit/CAP_NEG3_RETRO_AUDIT.md`
- `docs/archive/audit/CAP_NEG4_RETRO_AUDIT.md`
- `docs/archive/audit/CAP_NEGOTIATION_BASELINE.md`
- `docs/archive/audit/CAP_NEG_FINAL_BASELINE.md`
- `docs/archive/audit/CHEM1_COUPLING_VALIDATION.md`
- `docs/archive/audit/CHEM1_RETRO_AUDIT.md`
- `docs/archive/audit/CHEM2_RETRO_AUDIT.md`
- `docs/archive/audit/CHEM3_RETRO_AUDIT.md`
- `docs/archive/audit/CHEM4_RETRO_AUDIT.md`
- `docs/archive/audit/CHEMISTRY_FINAL_BASELINE.md`
- `docs/archive/audit/CHEM_DEGRADATION_BASELINE.md`
- `docs/archive/audit/CIVILISATION_SUBSTRATE_BASELINE.md`
- `docs/archive/audit/CLEAN_ROOM_win64.md`
- `docs/archive/audit/CODE_DATA_SEPARATION_REPORT.md`
- `docs/archive/audit/COHORT_REFINEMENT_BASELINE.md`
- `docs/archive/audit/COMBUSTION_BASELINE.md`
- `docs/archive/audit/COMMITMENTS_AND_REENACTMENT_BASELINE.md`
- `docs/archive/audit/COMPARTMENT_FLOWS_BASELINE.md`
- `docs/archive/audit/COMPAT_SEM1_RETRO_AUDIT.md`
- `docs/archive/audit/COMPAT_SEM2_RETRO_AUDIT.md`
- `docs/archive/audit/COMPAT_SEM3_RETRO_AUDIT.md`
- `docs/archive/audit/COMPILE0_RETRO_AUDIT.md`
- `docs/archive/audit/COMPILED_MODEL_BASELINE.md`
- `docs/archive/audit/COMPONENT_GRAPH0_RETRO_AUDIT.md`
- `docs/archive/audit/COMPONENT_GRAPH_BASELINE.md`
- `docs/archive/audit/COMPUTE_BUDGET_BASELINE.md`
- `docs/archive/audit/CONCURRENCY0_RETRO_AUDIT.md`
- `docs/archive/audit/CONCURRENCY_CONTRACT_BASELINE.md`
- `docs/archive/audit/CONCURRENCY_SCAN_REPORT.md`
- `docs/archive/audit/CONFIDENCE_STATEMENT.md`
- `docs/archive/audit/CONSERVATION_LEDGER_BASELINE.md`
- `docs/archive/audit/CONSISTENCY_AUDIT_REPORT.md`
- `docs/archive/audit/CONSOLIDATION_REPORT.md`
- `docs/archive/audit/CONSTITUTIVE_MODEL_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/CONSTITUTIVE_MODEL_ENGINE_BASELINE.md`
- `docs/archive/audit/CONSTRUCTION_BASELINE.md`
- `docs/archive/audit/CONTENT_STORE_BASELINE.md`
- `docs/archive/audit/CONTROL_IR_BASELINE.md`
- `docs/archive/audit/CONTROL_NEGOTIATION_BASELINE.md`
- `docs/archive/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md`
- `docs/archive/audit/CONTROL_PLANE_ENGINE_BASELINE.md`
- `docs/archive/audit/CONTROL_PLANE_FINAL_BASELINE.md`
- `docs/archive/audit/CONTROL_SUBSTRATE_BASELINE.md`
- `docs/archive/audit/CONVERGENCE_FINAL.md`
- `docs/archive/audit/CORE_ABSTRACTIONS_BASELINE.md`
- `docs/archive/audit/COUPLE0_RETRO_AUDIT.md`
- `docs/archive/audit/CROSS_SYSTEM_CONSISTENCY_MATRIX.md`
- `docs/archive/audit/CTRL0_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL10_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL1_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL2_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL3_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL4_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL5_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL6_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL7_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL8_RETRO_AUDIT.md`
- `docs/archive/audit/CTRL9_RETRO_AUDIT.md`
- `docs/archive/audit/DATA_FORMAT_COMPAT_BASELINE.md`
- `docs/archive/audit/DECAY_MAINTENANCE_BASELINE.md`
- `docs/archive/audit/DEGRADE_LADDER_BASELINE.md`
- `docs/archive/audit/DEMOGRAPHY_OPTIONALITY_BASELINE.md`
- `docs/archive/audit/DEPRECATION_FRAMEWORK_BASELINE.md`
- `docs/archive/audit/DETERMINISM_AND_PERFORMANCE_BASELINE.md`
- `docs/archive/audit/DETERMINISM_ENVELOPE_REPORT.md`
- `docs/archive/audit/DEVELOPER_ACCELERATION_BASELINE.md`
- `docs/archive/audit/DIAG0_RETRO_AUDIT.md`
- `docs/archive/audit/DIEGETIC_FIRST_BASELINE.md`
- `docs/archive/audit/DIEGETIC_INSTRUMENTS_BASELINE.md`
- `docs/archive/audit/DIST1_RETRO_AUDIT.md`
- `docs/archive/audit/DIST2_FINAL.md`
- `docs/archive/audit/DIST2_RETRO_AUDIT.md`
- `docs/archive/audit/DIST3_FINAL.md`
- `docs/archive/audit/DIST4_FINAL.md`
- `docs/archive/audit/DIST5_UX_POLISH_FINAL.md`
- `docs/archive/audit/DIST5_UX_SMOKE.md`
- `docs/archive/audit/DIST6_FINAL.md`
- `docs/archive/audit/DIST6_INTEROP_contract_mismatch_read_only.md`
- `docs/archive/audit/DIST6_INTEROP_contract_mismatch_strict.md`
- `docs/archive/audit/DIST6_INTEROP_minor_protocol_drift.md`
- `docs/archive/audit/DIST6_INTEROP_pack_lock_mismatch.md`
- `docs/archive/audit/DIST6_INTEROP_same_build_identical_rebuild.md`
- `docs/archive/audit/DIST6_INTEROP_same_build_same_build.md`
- `docs/archive/audit/DIST6_INTEROP_same_version_cross_platform.md`
- `docs/archive/audit/DISTRIBUTION_ARCHITECTURE_FREEZE.md`
- `docs/archive/audit/DIST_CONTENT_AUDIT.md`
- `docs/archive/audit/DIST_PLATFORM_MATRIX_REPORT.md`
- `docs/archive/audit/DIST_REFINE1_RETRO_AUDIT.md`
- `docs/archive/audit/DIST_TREE_ASSEMBLY_FINAL.md`
- `docs/archive/audit/DIST_VERIFY_win64.md`
- `docs/archive/audit/DOCS_AUDIT_PROMPT0.md`
- `docs/archive/audit/DOC_CANON_ALIGNMENT_REPORT.md`
- `docs/archive/audit/DOC_DRIFT.md`
- `docs/archive/audit/DOC_DRIFT_MATRIX.md`
- `docs/archive/audit/DOC_GAPS.md`
- `docs/archive/audit/DOC_INDEX.md`
- `docs/archive/audit/DOMAIN_FOUNDATION_REPORT.md`
- `docs/archive/audit/DOMAIN_REGISTRY_REPORT.md`
- `docs/archive/audit/DRIFT_REVALIDATION_BASELINE.md`
- `docs/archive/audit/EARTH0_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH10_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH1_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH2_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH3_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH4_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH5_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH6_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH7_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH8_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH9_RETRO_AUDIT.md`
- `docs/archive/audit/EARTH_HYDROLOGY_BASELINE.md`
- `docs/archive/audit/EARTH_LIGHTING_BASELINE.md`
- `docs/archive/audit/EARTH_MATERIAL_PROXY_BASELINE.md`
- `docs/archive/audit/EARTH_MVP_FINAL_BASELINE.md`
- `docs/archive/audit/EARTH_PROCEDURAL_BASELINE.md`
- `docs/archive/audit/EARTH_SEASONAL_CLIMATE_BASELINE.md`
- `docs/archive/audit/EARTH_SKY_STARFIELD_BASELINE.md`
- `docs/archive/audit/EARTH_TERRAIN_COLLISION_BASELINE.md`
- `docs/archive/audit/EARTH_TIDE_PROXY_BASELINE.md`
- `docs/archive/audit/EARTH_WATER_VISUAL_BASELINE.md`
- `docs/archive/audit/EARTH_WIND_PROXY_BASELINE.md`
- `docs/archive/audit/EFFECT_SYSTEM_BASELINE.md`
- `docs/archive/audit/EG_H_REPO_AUDIT.md`
- `docs/archive/audit/ELEC0_RETRO_AUDIT.md`
- `docs/archive/audit/ELEC1_RETRO_AUDIT.md`
- `docs/archive/audit/ELEC2_RETRO_AUDIT.md`
- `docs/archive/audit/ELEC3_RETRO_AUDIT.md`
- `docs/archive/audit/ELEC4_RETRO_AUDIT.md`
- `docs/archive/audit/ELEC5_RETRO_AUDIT.md`
- `docs/archive/audit/ELECTRICAL_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/ELECTRICAL_FINAL_BASELINE.md`
- `docs/archive/audit/ELECTRICAL_PROTECTION_BASELINE.md`
- `docs/archive/audit/EMB0_RETRO_AUDIT.md`
- `docs/archive/audit/EMB1_RETRO_AUDIT.md`
- `docs/archive/audit/EMB2_RETRO_AUDIT.md`
- `docs/archive/audit/EMBODIED_MOVEMENT_BASELINE.md`
- `docs/archive/audit/EMBODIMENT_BASELINE_REPORT.md`
- `docs/archive/audit/EMB_LOCOMOTION_POLISH_BASELINE.md`
- `docs/archive/audit/ENDPOINT_DESCRIPTOR_BASELINE.md`
- `docs/archive/audit/END_TO_END_FLOW.md`
- `docs/archive/audit/ENERGY_LEDGER_BASELINE.md`
- `docs/archive/audit/ENERGY_MOMENTUM_INTEGRITY_REPORT.md`
- `docs/archive/audit/ENTROPY_POLICY_BASELINE.md`
- `docs/archive/audit/ENTRYPOINT_MAP.md`
- `docs/archive/audit/ENTRYPOINT_UNIFY_FINAL.md`
- `docs/archive/audit/ENTRYPOINT_UNIFY_MAP.md`
- `docs/archive/audit/EPISTEMICS_OVER_NETWORK_BASELINE.md`
- `docs/archive/audit/EPISTEMIC_MEMORY_BASELINE.md`
- `docs/archive/audit/EXECUTION_LOG.md`
- `docs/archive/audit/EXPORT_IMPORT_BASELINE.md`
- `docs/archive/audit/EXTENSION_DISCIPLINE_BASELINE.md`
- `docs/archive/audit/FAILURE_MODE_CATALOG.md`
- `docs/archive/audit/FIDELITY_ARBITRATION_BASELINE.md`
- `docs/archive/audit/FIELD1_RETRO_AUDIT.md`
- `docs/archive/audit/FIELD_DISCIPLINE_REPORT.md`
- `docs/archive/audit/FIELD_GENERALIZATION_BASELINE.md`
- `docs/archive/audit/FIELD_LAYER_BASELINE.md`
- `docs/archive/audit/FINAL_SYSTEM_BASELINE.md`
- `docs/archive/audit/FIRE_RUNAWAY_BASELINE.md`
- `docs/archive/audit/FLOWSYSTEM_STANDARD_BASELINE.md`
- `docs/archive/audit/FLUID0_RETRO_AUDIT.md`
- `docs/archive/audit/FLUID1_RETRO_AUDIT.md`
- `docs/archive/audit/FLUID2_RETRO_AUDIT.md`
- `docs/archive/audit/FLUID3_RETRO_AUDIT.md`
- `docs/archive/audit/FLUID_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/FLUID_CONTAINMENT_BASELINE.md`
- `docs/archive/audit/FLUID_FINAL_BASELINE.md`
- `docs/archive/audit/FORCE_MOMENTUM_BASELINE.md`
- `docs/archive/audit/FORM1_RETRO_AUDIT.md`
- `docs/archive/audit/FORMALIZATION_BASELINE.md`
- `docs/archive/audit/FUTURE_CASE_STRESS_REPORT.md`
- `docs/archive/audit/FUTURE_PRESSURE_ANALYSIS.md`
- `docs/archive/audit/GAL0_RETRO_AUDIT.md`
- `docs/archive/audit/GAL1_RETRO_AUDIT.md`
- `docs/archive/audit/GALAXY_OBJECT_STUBS_BASELINE.md`
- `docs/archive/audit/GALAXY_PROXY_BASELINE.md`
- `docs/archive/audit/GAP_REPORT.md`
- `docs/archive/audit/GEO0_RETRO_AUDIT.md`
- `docs/archive/audit/GEO10_RETRO_AUDIT.md`
- `docs/archive/audit/GEO1_RETRO_AUDIT.md`
- `docs/archive/audit/GEO2_RETRO_AUDIT.md`
- `docs/archive/audit/GEO3_RETRO_AUDIT.md`
- `docs/archive/audit/GEO4_RETRO_AUDIT.md`
- `docs/archive/audit/GEO5_RETRO_AUDIT.md`
- `docs/archive/audit/GEO6_RETRO_AUDIT.md`
- `docs/archive/audit/GEO7_RETRO_AUDIT.md`
- `docs/archive/audit/GEO8_RETRO_AUDIT.md`
- `docs/archive/audit/GEO9_RETRO_AUDIT.md`
- `docs/archive/audit/GEO_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/GEO_FIELD_BINDING_BASELINE.md`
- `docs/archive/audit/GEO_FINAL_BASELINE.md`
- `docs/archive/audit/GEO_FRAMES_BASELINE.md`
- `docs/archive/audit/GEO_GEOMETRY_EDIT_BASELINE.md`
- `docs/archive/audit/GEO_IDENTITY_BASELINE.md`
- `docs/archive/audit/GEO_METRIC_BASELINE.md`
- `docs/archive/audit/GEO_PATHING_BASELINE.md`
- `docs/archive/audit/GEO_PROJECTION_LENS_BASELINE.md`
- `docs/archive/audit/GLOBAL_CONSERVATION_REPORT.md`
- `docs/archive/audit/GLOBAL_CONTRACT_COVERAGE.md`
- `docs/archive/audit/GLOBAL_COUPLING_GRAPH.md`
- `docs/archive/audit/GLOBAL_EXPLAINABILITY_REPORT.md`
- `docs/archive/audit/GLOBAL_FIELD_TIME_CAUSALITY.md`
- `docs/archive/audit/GLOBAL_PERFORMANCE_ENVELOPE.md`
- `docs/archive/audit/GLOBAL_PROVENANCE_COMPACTION.md`
- `docs/archive/audit/GLOBAL_REGRESSION_STATUS.md`
- `docs/archive/audit/GLOBAL_REVIEW_FINAL.md`
- `docs/archive/audit/GLOBAL_SUBSTRATE_PURITY.md`
- `docs/archive/audit/GLOBAL_TOPOLOGY_REVIEW.md`
- `docs/archive/audit/GOVERNANCE0_RETRO_AUDIT.md`
- `docs/archive/audit/GOVERNANCE_POLICY_BASELINE.md`
- `docs/archive/audit/GOVERNANCE_READINESS_REPORT.md`
- `docs/archive/audit/GR3_CONTRACT_GRAPH.md`
- `docs/archive/audit/GR3_DEMAND_COVERAGE_SUMMARY.md`
- `docs/archive/audit/GR3_DEMAND_GAP_REPORT.md`
- `docs/archive/audit/GR3_FAST_RESULTS.md`
- `docs/archive/audit/GR3_FINAL_REPORT.md`
- `docs/archive/audit/GR3_FULL_RESULTS.md`
- `docs/archive/audit/GR3_PERFORMANCE_TUNING.md`
- `docs/archive/audit/GR3_REFERENCE_MISMATCHES.md`
- `docs/archive/audit/GR3_REGRESSION_STATUS.md`
- `docs/archive/audit/GR3_SCALE_METRICS.md`
- `docs/archive/audit/GR3_STRICT_REFACTOR_NOTES.md`
- `docs/archive/audit/GR3_STRICT_RESULTS.md`
- `docs/archive/audit/GR3_TOPOLOGY_MASTER.md`
- `docs/archive/audit/GUIDE_GEOMETRY_BASELINE.md`
- `docs/archive/audit/HANDSHAKE_COMPAT_MATRIX.md`
- `docs/archive/audit/ILLUMINATION_GEOMETRY_BASELINE.md`
- `docs/archive/audit/INDUSTRIAL_PROCESSING_BASELINE.md`
- `docs/archive/audit/INSPECTION_SYSTEM_BASELINE.md`
- `docs/archive/audit/INSTALL_DISCOVERY_BASELINE.md`
- `docs/archive/audit/INSTALL_PROFILE_BASELINE.md`
- `docs/archive/audit/INSTRUMENTATION_SURFACE_BASELINE.md`
- `docs/archive/audit/INTEGRATION_READINESS_REPORT.md`
- `docs/archive/audit/INTERACTION_UX_BASELINE.md`
- `docs/archive/audit/INTERFACE_LAUNCH_REPORT.md`
- `docs/archive/audit/INTERIOR_DIEGETIC_INSPECTION_BASELINE.md`
- `docs/archive/audit/INTERIOR_VOLUME_BASELINE.md`
- `docs/archive/audit/INVENTORY.md`
- `docs/archive/audit/IPC_DUPLICATION_FIXES.md`
- `docs/archive/audit/IPC_SURFACE_MAP.md`
- `docs/archive/audit/IPC_UNIFY_FINAL.md`
- `docs/archive/audit/LEGACY_PLATFORM_READINESS.md`
- `docs/archive/audit/LIB6_RETRO_AUDIT.md`
- `docs/archive/audit/LIB7_RETRO_AUDIT.md`
- `docs/archive/audit/LIB_FINAL_BASELINE.md`
- `docs/archive/audit/LOCAL_SINGLEPLAYER_BASELINE.md`
- `docs/archive/audit/LOD_EPISTEMIC_INVARIANCE_BASELINE.md`
- `docs/archive/audit/LOGIC0_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC10_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC1_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC2_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC3_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC4_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC5_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC6_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC7_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC8_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC9_RETRO_AUDIT.md`
- `docs/archive/audit/LOGIC_COMPILATION_BASELINE.md`
- `docs/archive/audit/LOGIC_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/LOGIC_DEBUG_BASELINE.md`
- `docs/archive/audit/LOGIC_ELEMENTS_BASELINE.md`
- `docs/archive/audit/LOGIC_EVAL_BASELINE.md`
- `docs/archive/audit/LOGIC_FAULT_NOISE_BASELINE.md`
- `docs/archive/audit/LOGIC_FINAL_BASELINE.md`
- `docs/archive/audit/LOGIC_NETWORKGRAPH_BASELINE.md`
- `docs/archive/audit/LOGIC_PROTOCOL_BASELINE.md`
- `docs/archive/audit/LOGIC_TIMING_BASELINE.md`
- `docs/archive/audit/LOGISTICS_BASELINE.md`
- `docs/archive/audit/MACHINE_PORTS_BASELINE.md`
- `docs/archive/audit/MACRO_MICRO_MAPPING_BASELINE.md`
- `docs/archive/audit/MACRO_TRAVEL_BASELINE.md`
- `docs/archive/audit/MAINTENANCE_WEAR_BASELINE.md`
- `docs/archive/audit/MARKER_SCAN.txt`
- `docs/archive/audit/MATERIALS_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/MATERIAL_TAXONOMY_BASELINE.md`
- `docs/archive/audit/MAT_SCALE_BASELINE_FINAL.md`
- `docs/archive/audit/MECH1_RETRO_AUDIT.md`
- `docs/archive/audit/MECHANICS_SUBSTRATE_BASELINE.md`
- `docs/archive/audit/MESO_TRAFFIC_BASELINE.md`
- `docs/archive/audit/MESSAGE_LAYER_BASELINE.md`
- `docs/archive/audit/META_ACTION0_RETRO_AUDIT.md`
- `docs/archive/audit/META_COMPUTE0_RETRO_AUDIT.md`
- `docs/archive/audit/META_CONTRACT0_RETRO_AUDIT.md`
- `docs/archive/audit/META_CONTRACT1_RETRO_AUDIT.md`
- `docs/archive/audit/META_CONTRACT_HARDENING_REPORT.md`
- `docs/archive/audit/META_GENRE0_RETRO_AUDIT.md`
- `docs/archive/audit/META_INSTR0_RETRO_AUDIT.md`
- `docs/archive/audit/META_MODEL0_RETRO_AUDIT.md`
- `docs/archive/audit/META_MODEL1_RETRO_AUDIT.md`
- `docs/archive/audit/META_MODEL2_RETRO_AUDIT.md`
- `docs/archive/audit/META_PROFILE0_RETRO_AUDIT.md`
- `docs/archive/audit/META_REF0_RETRO_AUDIT.md`
- `docs/archive/audit/META_STABILITY0_RETRO_AUDIT.md`
- `docs/archive/audit/META_STABILITY1_FIX_PLAN.md`
- `docs/archive/audit/META_STABILITY1_RETRO_AUDIT.md`
- `docs/archive/audit/MICRO_CONSTRAINED_MOTION_BASELINE.md`
- `docs/archive/audit/MICRO_FREE_MOTION_BASELINE.md`
- `docs/archive/audit/MIGRATION_LIFECYCLE0_RETRO_AUDIT.md`
- `docs/archive/audit/MIGRATION_LIFECYCLE_BASELINE.md`
- `docs/archive/audit/MIGRATION_STATUS.md`
- `docs/archive/audit/MILKY_WAY_BASELINE.md`
- `docs/archive/audit/MOB0_RETRO_AUDIT.md`
- `docs/archive/audit/MOB10_RETRO_AUDIT.md`
- `docs/archive/audit/MOB11_RETRO_AUDIT.md`
- `docs/archive/audit/MOB1_RETRO_AUDIT.md`
- `docs/archive/audit/MOB2_RETRO_AUDIT.md`
- `docs/archive/audit/MOB3_RETRO_AUDIT.md`
- `docs/archive/audit/MOB4_RETRO_AUDIT.md`
- `docs/archive/audit/MOB5_RETRO_AUDIT.md`
- `docs/archive/audit/MOB6_RETRO_AUDIT.md`
- `docs/archive/audit/MOB7_RETRO_AUDIT.md`
- `docs/archive/audit/MOB8_RETRO_AUDIT.md`
- `docs/archive/audit/MOB9_RETRO_AUDIT.md`
- `docs/archive/audit/MOBILITY_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/MOBILITY_NETWORK_BASELINE.md`
- `docs/archive/audit/MODE_REFACTOR_REPORT.md`
- `docs/archive/audit/MODE_REFACTOR_V2_REPORT.md`
- `docs/archive/audit/MODULARITY_EXTENSION_PROOF.md`
- `docs/archive/audit/MODULE_DUPLICATION_REPORT.md`
- `docs/archive/audit/MOD_POLICY0_RETRO_AUDIT.md`
- `docs/archive/audit/MOD_POLICY_BASELINE.md`
- `docs/archive/audit/MULTIPLAYER_BASELINE_FINAL.md`
- `docs/archive/audit/MULTIPLAYER_CONTRACT_FOUNDATION_REPORT.md`
- `docs/archive/audit/MULTIPLAYER_DETERMINISM_ENVELOPE.md`
- `docs/archive/audit/MULTIPLAYER_SECURITY_BASELINE.md`
- `docs/archive/audit/MVP1_RETRO_AUDIT.md`
- `docs/archive/audit/MVP_CROSS_PLATFORM_FINAL.md`
- `docs/archive/audit/MVP_RUNTIME_BASELINE.md`
- `docs/archive/audit/MVP_SMOKE_FINAL.md`
- `docs/archive/audit/MVP_STRESS_FINAL.md`
- `docs/archive/audit/MVP_TOOLBELT_BASELINE.md`
- `docs/archive/audit/MVP_VIEWER_BASELINE.md`
- `docs/archive/audit/MW0_RETRO_AUDIT.md`
- `docs/archive/audit/MW1_RETRO_AUDIT.md`
- `docs/archive/audit/MW2_RETRO_AUDIT.md`
- `docs/archive/audit/MW3_RETRO_AUDIT.md`
- `docs/archive/audit/MW4_RETRO_AUDIT.md`
- `docs/archive/audit/MW_SYSTEM_L2_BASELINE.md`
- `docs/archive/audit/NAMING_TAXONOMY_CHECK.md`
- `docs/archive/audit/NEGOTIATION_HANDSHAKE_BASELINE.md`
- `docs/archive/audit/NETWORKGRAPH_STANDARD_BASELINE.md`
- `docs/archive/audit/NET_HANDSHAKE_COMPATIBILITY_REPORT.md`
- `docs/archive/audit/NEXT_PROMPTS.md`
- `docs/archive/audit/NORMALIZATION_REPORT.md`
- `docs/archive/audit/NUMERICAL_TOLERANCE_BASELINE.md`
- `docs/archive/audit/NUMERIC_DISCIPLINE0_RETRO_AUDIT.md`
- `docs/archive/audit/NUMERIC_DISCIPLINE_BASELINE.md`
- `docs/archive/audit/NUMERIC_SCAN_REPORT.md`
- `docs/archive/audit/OBSERVABILITY0_RETRO_AUDIT.md`
- `docs/archive/audit/OBSERVABILITY_BASELINE.md`
- `docs/archive/audit/ORBIT_VISUALIZATION_BASELINE.md`
- `docs/archive/audit/ORDER_LANGUAGE_BASELINE.md`
- `docs/archive/audit/OVERLAY_CONFLICT_BASELINE.md`
- `docs/archive/audit/OVERLAY_MERGE_BASELINE.md`
- `docs/archive/audit/PACK_AUDIT.txt`
- `docs/archive/audit/PACK_COMPAT0_RETRO_AUDIT.md`
- `docs/archive/audit/PACK_COMPAT1_RETRO_AUDIT.md`
- `docs/archive/audit/PACK_COMPAT2_RETRO_AUDIT.md`
- `docs/archive/audit/PACK_COMPAT_BASELINE.md`
- `docs/archive/audit/PACK_VERIFICATION_BASELINE.md`
- `docs/archive/audit/PATCH_A2_RETRO_AUDIT.md`
- `docs/archive/audit/PATCH_A3_RETRO_AUDIT.md`
- `docs/archive/audit/PEP0_BASELINE.md`
- `docs/archive/audit/PERFORMANCE_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/PERFORMANCE_ENVELOPE0_RETRO_AUDIT.md`
- `docs/archive/audit/PERFORMANCE_ENVELOPE_BASELINE.md`
- `docs/archive/audit/PERFORMANCE_REPORT_win64.md`
- `docs/archive/audit/PHYS0_RETRO_AUDIT.md`
- `docs/archive/audit/PHYS1_RETRO_AUDIT.md`
- `docs/archive/audit/PHYS2_RETRO_AUDIT.md`
- `docs/archive/audit/PHYS3_RETRO_AUDIT.md`
- `docs/archive/audit/PHYS4_RETRO_AUDIT.md`
- `docs/archive/audit/PHYSICS_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/PKG_IMPLEMENTATION_REPORT.md`
- `docs/archive/audit/PLANET_SURFACE_L3_BASELINE.md`
- `docs/archive/audit/PLANNING_EXECUTION_BASELINE.md`
- `docs/archive/audit/PLATFORM_AND_PORTABILITY_CONSISTENCY_REPORT.md`
- `docs/archive/audit/PLATFORM_FORMALIZE_FINAL.md`
- `docs/archive/audit/PLATFORM_RENDERER_BACKENDS_BASELINE.md`
- `docs/archive/audit/PLATFORM_RENDERER_MATRIX.md`
- `docs/archive/audit/PLATFORM_RENDERER_SURFACE.md`
- `docs/archive/audit/PLAYER2_VALIDATION.md`
- `docs/archive/audit/PLAYER_DEMAND_GAPS.md`
- `docs/archive/audit/PLAYER_DEMAND_MATRIX_BASELINE.md`
- `docs/archive/audit/POLL0_RETRO_AUDIT.md`
- `docs/archive/audit/POLL1_RETRO_AUDIT.md`
- `docs/archive/audit/POLL2_RETRO_AUDIT.md`
- `docs/archive/audit/POLL3_RETRO_AUDIT.md`
- `docs/archive/audit/POLLUTION_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/POLLUTION_DISPERSION_BASELINE.md`
- `docs/archive/audit/POLLUTION_EXPOSURE_BASELINE.md`
- `docs/archive/audit/POLLUTION_FINAL_BASELINE.md`
- `docs/archive/audit/POSE_MOUNT_BASELINE.md`
- `docs/archive/audit/POWER_NETWORK_BASELINE.md`
- `docs/archive/audit/PREALPHA_PACK_STRATEGY.md`
- `docs/archive/audit/PROC0_RETRO_AUDIT.md`
- `docs/archive/audit/PROC1_RETRO_AUDIT.md`
- `docs/archive/audit/PROC2_RETRO_AUDIT.md`
- `docs/archive/audit/PROC3_RETRO_AUDIT.md`
- `docs/archive/audit/PROC4_RETRO_AUDIT.md`
- `docs/archive/audit/PROC5_RETRO_AUDIT.md`
- `docs/archive/audit/PROC6_RETRO_AUDIT.md`
- `docs/archive/audit/PROC7_RETRO_AUDIT.md`
- `docs/archive/audit/PROC8_RETRO_AUDIT.md`
- `docs/archive/audit/PROC9_RETRO_AUDIT.md`
- `docs/archive/audit/PROCESS_CAPSULE_BASELINE.md`
- `docs/archive/audit/PROCESS_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/PROCESS_DEFINITION_BASELINE.md`
- `docs/archive/audit/PROCESS_MATURITY_BASELINE.md`
- `docs/archive/audit/PROC_FINAL_BASELINE.md`
- `docs/archive/audit/PRODUCT_BOOT_MATRIX_REPORT.md`
- `docs/archive/audit/PROD_GATE_FINAL.md`
- `docs/archive/audit/PROFILE_OVERRIDE_BASELINE.md`
- `docs/archive/audit/PROMPT_EXECUTION_MODEL.md`
- `docs/archive/audit/PROMPT_G_REPORT.md`
- `docs/archive/audit/PROV0_RETRO_AUDIT.md`
- `docs/archive/audit/PROVENANCE_BASELINE.md`
- `docs/archive/audit/QC_SAMPLING_BASELINE.md`
- `docs/archive/audit/QUANTITY_BUNDLE_BASELINE.md`
- `docs/archive/audit/RANKED_SERVER_GOVERNANCE_BASELINE.md`
- `docs/archive/audit/REAL_DATA_INTEGRATION_REPORT.md`
- `docs/archive/audit/RECOMMENDED_NEXT_FIXES.md`
- `docs/archive/audit/RED_FLAGS.md`
- `docs/archive/audit/REFERENCE_INTERPRETER_BASELINE.md`
- `docs/archive/audit/REFINEMENT_PIPELINE_BASELINE.md`
- `docs/archive/audit/RELEASE0_RETRO_AUDIT.md`
- `docs/archive/audit/RELEASE1_RETRO_AUDIT.md`
- `docs/archive/audit/RELEASE2_RETRO_AUDIT.md`
- `docs/archive/audit/RELEASE_IDENTITY_BASELINE.md`
- `docs/archive/audit/RELEASE_INDEX_POLICY0_RETRO_AUDIT.md`
- `docs/archive/audit/RELEASE_INDEX_POLICY_BASELINE.md`
- `docs/archive/audit/RELEASE_MANIFEST_BASELINE.md`
- `docs/archive/audit/RENDERER_BASELINE_REPORT.md`
- `docs/archive/audit/RENDERMODEL_CONTRACT_BASELINE.md`
- `docs/archive/audit/REPO_INVENTORY_SUMMARY.md`
- `docs/archive/audit/REPO_REVIEW_2_FINAL.md`
- `docs/archive/audit/REPO_REVIEW_3_FINAL.md`
- `docs/archive/audit/REPO_STRUCTURE_AUDIT.md`
- `docs/archive/audit/REPO_TREE_INDEX.md`
- `docs/archive/audit/REPRESENTATION_BASELINE.md`
- `docs/archive/audit/REPRODUCIBLE_BUILD_BASELINE.md`
- `docs/archive/audit/REPRO_BUNDLE_BASELINE.md`
- `docs/archive/audit/RESEARCH_REVERSE_ENGINEERING_BASELINE.md`
- `docs/archive/audit/RETRO_CONSISTENCY_FRAMEWORK_BASELINE.md`
- `docs/archive/audit/RWAM_BASELINE.md`
- `docs/archive/audit/SAFETY_PATTERN_BASELINE.md`
- `docs/archive/audit/SAFE_TO_PROCEED.md`
- `docs/archive/audit/SCHEMA_CANON_ALIGNMENT.md`
- `docs/archive/audit/SDK_READINESS.md`
- `docs/archive/audit/SEMANTIC_CONTRACT_BASELINE.md`
- `docs/archive/audit/SERVER_AUTHORITATIVE_BASELINE_REPORT.md`
- `docs/archive/audit/SERVER_MVP0_RETRO_AUDIT.md`
- `docs/archive/audit/SERVER_MVP1_RETRO_AUDIT.md`
- `docs/archive/audit/SERVER_MVP_BASELINE_REPORT.md`
- `docs/archive/audit/SESSION_PIPELINE_CONTRACT_REPORT.md`
- `docs/archive/audit/SETTINGS_AND_UX_CONSISTENCY_REPORT.md`
- `docs/archive/audit/SHIM_COVERAGE_REPORT.md`
- `docs/archive/audit/SIG0_RETRO_AUDIT.md`
- `docs/archive/audit/SIG1_RETRO_AUDIT.md`
- `docs/archive/audit/SIG2_RETRO_AUDIT.md`
- `docs/archive/audit/SIG3_RETRO_AUDIT.md`
- `docs/archive/audit/SIG5_RETRO_AUDIT.md`
- `docs/archive/audit/SIG6_RETRO_AUDIT.md`
- `docs/archive/audit/SIGNALING_INTERLOCKING_BASELINE.md`
- `docs/archive/audit/SIGNALS_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/SIGNAL_BUS_BASELINE.md`
- `docs/archive/audit/SIGNAL_NETWORK_BASELINE.md`
- `docs/archive/audit/SIGNAL_QUALITY_BASELINE.md`
- `docs/archive/audit/SOFTWARE_PIPELINE_BASELINE.md`
- `docs/archive/audit/SOL0_RETRO_AUDIT.md`
- `docs/archive/audit/SOL1_RETRO_AUDIT.md`
- `docs/archive/audit/SOL2_RETRO_AUDIT.md`
- `docs/archive/audit/SOL_PIN_PACK_BASELINE.md`
- `docs/archive/audit/SPEC1_RETRO_AUDIT.md`
- `docs/archive/audit/SPECSHEET_BASELINE.md`
- `docs/archive/audit/SRZ_HYBRID_BASELINE_REPORT.md`
- `docs/archive/audit/STABILITY_CLASSIFICATION_BASELINE.md`
- `docs/archive/audit/STABILITY_COVERAGE_REPORT.md`
- `docs/archive/audit/STABILITY_TAGGING_FINAL.md`
- `docs/archive/audit/STAGE_RIPOUT_REPORT.md`
- `docs/archive/audit/STAR_SYSTEM_SEED_BASELINE.md`
- `docs/archive/audit/STATEVEC0_RETRO_AUDIT.md`
- `docs/archive/audit/STATE_VECTOR_BASELINE.md`
- `docs/archive/audit/STORE_GC0_RETRO_AUDIT.md`
- `docs/archive/audit/STORE_GC_BASELINE.md`
- `docs/archive/audit/STORE_VERIFY_REPORT.md`
- `docs/archive/audit/STRUCTURAL_INTEGRITY_REPORT.md`
- `docs/archive/audit/STRUCTURAL_TOPOLOGY_SCAN.md`
- `docs/archive/audit/STUB_REPORT.md`
- `docs/archive/audit/SUPERVISOR_BASELINE.md`
- `docs/archive/audit/SYS0_RETRO_AUDIT.md`
- `docs/archive/audit/SYS1_RETRO_AUDIT.md`
- `docs/archive/audit/SYS2_RETRO_AUDIT.md`
- `docs/archive/audit/SYS3_RETRO_AUDIT.md`
- `docs/archive/audit/SYS4_RETRO_AUDIT.md`
- `docs/archive/audit/SYS5_RETRO_AUDIT.md`
- `docs/archive/audit/SYS6_RETRO_AUDIT.md`
- `docs/archive/audit/SYS7_RETRO_AUDIT.md`
- `docs/archive/audit/SYS8_RETRO_AUDIT.md`
- `docs/archive/audit/SYSTEM_CERTIFICATION_BASELINE.md`
- `docs/archive/audit/SYSTEM_COMPOSITION_BASELINE.md`
- `docs/archive/audit/SYSTEM_FORENSICS_BASELINE.md`
- `docs/archive/audit/SYSTEM_INTERFACE_INVARIANT_BASELINE.md`
- `docs/archive/audit/SYSTEM_RELIABILITY_BASELINE.md`
- `docs/archive/audit/SYSTEM_TEMPLATES_BASELINE.md`
- `docs/archive/audit/SYS_FINAL_BASELINE.md`
- `docs/archive/audit/TASK_WORK_BASELINE.md`
- `docs/archive/audit/TEMP0_RETRO_AUDIT.md`
- `docs/archive/audit/TEMP1_RETRO_AUDIT.md`
- `docs/archive/audit/TEMP2_RETRO_AUDIT.md`
- `docs/archive/audit/TEMPORAL_SEMANTICS_BASELINE.md`
- `docs/archive/audit/TESTX_OVERHAUL_REPORT.md`
- `docs/archive/audit/TEST_COVERAGE_MATRIX.md`
- `docs/archive/audit/THERM0_RETRO_AUDIT.md`
- `docs/archive/audit/THERM1_RETRO_AUDIT.md`
- `docs/archive/audit/THERM2_RETRO_AUDIT.md`
- `docs/archive/audit/THERM3_RETRO_AUDIT.md`
- `docs/archive/audit/THERM4_RETRO_AUDIT.md`
- `docs/archive/audit/THERM5_RETRO_AUDIT.md`
- `docs/archive/audit/THERMAL_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/THERMAL_COOLING_BASELINE.md`
- `docs/archive/audit/THERMAL_FINAL_BASELINE.md`
- `docs/archive/audit/THERMAL_NETWORK_BASELINE.md`
- `docs/archive/audit/THERM_PHASE_CURE_BASELINE.md`
- `docs/archive/audit/TIER_COUPLING_EXPLAIN_BASELINE.md`
- `docs/archive/audit/TIER_TRANSITION_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/TIME_ANCHOR0_RETRO_AUDIT.md`
- `docs/archive/audit/TIME_ANCHOR_BASELINE.md`
- `docs/archive/audit/TIME_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/TIME_MAPPING_BASELINE.md`
- `docs/archive/audit/TIME_SYNC_BASELINE.md`
- `docs/archive/audit/TOL0_RETRO_AUDIT.md`
- `docs/archive/audit/TOOLING_BASELINE.md`
- `docs/archive/audit/TOOLS_EFFECTS_BASELINE.md`
- `docs/archive/audit/TOOL_AUTONOMY_VALIDATION.md`
- `docs/archive/audit/TOOL_SURFACE_FINAL.md`
- `docs/archive/audit/TOOL_SURFACE_MAP.md`
- `docs/archive/audit/TOPOLOGY_MAP.md`
- `docs/archive/audit/TOPOLOGY_MAP_BASELINE.md`
- `docs/archive/audit/TRUST_BELIEF_BASELINE.md`
- `docs/archive/audit/TRUST_MODEL0_RETRO_AUDIT.md`
- `docs/archive/audit/TRUST_MODEL_BASELINE.md`
- `docs/archive/audit/UI_AND_WORLDGEN_CONSISTENCY_REPORT.md`
- `docs/archive/audit/UI_MODE_RESOLUTION_BASELINE.md`
- `docs/archive/audit/UI_RECONCILE_FINAL.md`
- `docs/archive/audit/UI_SURFACE_MAP.md`
- `docs/archive/audit/UNITS_AND_DIMENSIONS_BASELINE.md`
- `docs/archive/audit/UNIVERSAL_IDENTITY0_RETRO_AUDIT.md`
- `docs/archive/audit/UNIVERSAL_IDENTITY_BASELINE.md`
- `docs/archive/audit/UNIVERSE_CONTRACT_ENFORCEMENT_BASELINE.md`
- `docs/archive/audit/UNIVERSE_PHYSICS_PROFILE_BASELINE.md`
- `docs/archive/audit/UPDATE_MODEL0_RETRO_AUDIT.md`
- `docs/archive/audit/UPDATE_MODEL_BASELINE.md`
- `docs/archive/audit/UX0_RETRO_AUDIT.md`
- `docs/archive/audit/VALIDATION_INVENTORY.md`
- `docs/archive/audit/VALIDATION_REPORT_FAST.md`
- `docs/archive/audit/VALIDATION_REPORT_STRICT.md`
- `docs/archive/audit/VALIDATION_STACK_MAP.md`
- `docs/archive/audit/VALIDATION_UNIFY_FINAL.md`
- `docs/archive/audit/VEHICLE_INTERIORS_BASELINE.md`
- `docs/archive/audit/VEHICLE_MODEL_BASELINE.md`
- `docs/archive/audit/VIEW_EPISTEMIC_CONTROL_BASELINE.md`
- `docs/archive/audit/VIRTUAL_PATHS_BASELINE.md`
- `docs/archive/audit/VIS3_VALIDATION.md`
- `docs/archive/audit/WG_E_VALIDATION_REPORT.md`
- `docs/archive/audit/WORKTREE_LEFTOVERS.md`
- `docs/archive/audit/WORLDGEN_COMPATIBILITY.md`
- `docs/archive/audit/WORLDGEN_CONSTITUTION_BASELINE.md`
- `docs/archive/audit/WORLDGEN_CONSTRAINT_SOLVER_REPORT.md`
- `docs/archive/audit/YIELD_DEFECT_BASELINE.md`
- `docs/archive/audit/auditx/FINDINGS.md`
- `docs/archive/audit/auditx/README.md`
- `docs/archive/audit/auditx/SUMMARY.md`
- `docs/archive/audit/compat/COMPAT_BASELINE.md`
- `docs/archive/audit/compat/README.md`
- `docs/archive/audit/controlx/README.md`
- `docs/archive/audit/convergence_steps/arch_audit.md`
- `docs/archive/audit/convergence_steps/cap_neg_interop.md`
- `docs/archive/audit/convergence_steps/dist_verify.md`
- `docs/archive/audit/convergence_steps/ipc_attach_smoke.md`
- `docs/archive/audit/convergence_steps/lib_stress.md`
- `docs/archive/audit/convergence_steps/meta_stability.md`
- `docs/archive/audit/convergence_steps/mvp_cross_platform.md`
- `docs/archive/audit/convergence_steps/mvp_smoke.md`
- `docs/archive/audit/convergence_steps/mvp_stress.md`
- `docs/archive/audit/convergence_steps/pack_compat_stress.md`
- `docs/archive/audit/convergence_steps/product_boot_matrix.md`
- `docs/archive/audit/convergence_steps/supervisor_hardening.md`
- `docs/archive/audit/convergence_steps/time_anchor.md`
- `docs/archive/audit/convergence_steps/validation_strict.md`
- `docs/archive/audit/identity_fingerprint_explanation.md`
- `docs/archive/audit/performance/PERFORMX_BASELINE.md`
- `docs/archive/audit/performance/README.md`
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T215035Z_precheck_ok/diff_summary.txt`
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T215035Z_precheck_ok/failure.md`
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T220047Z_precheck_OTHER/diff_summary.txt`
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T220047Z_precheck_OTHER/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T080631Z_verify_DERIVED_ARTIFACT_STALE/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T080631Z_verify_DERIVED_ARTIFACT_STALE/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T080838Z_verify_OTHER/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T080838Z_verify_OTHER/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T081813Z_verify_ok/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T081813Z_verify_ok/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T083343Z_verify_DERIVED_ARTIFACT_STALE/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T083343Z_verify_DERIVED_ARTIFACT_STALE/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T090841Z_verify_OTHER/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T090841Z_verify_OTHER/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T111036Z_verify_OTHER/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T111036Z_verify_OTHER/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T121513Z_verify_ok/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T121513Z_verify_ok/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T130308Z_verify_ok/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T130308Z_verify_ok/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T163146Z_verify_OTHER/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T163146Z_verify_OTHER/failure.md`
- `docs/archive/audit/remediation/vs2026/20260211T233128Z_verify_ok/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260211T233128Z_verify_ok/failure.md`
- `docs/archive/audit/remediation/vs2026/20260212T143108Z_verify_ok/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260212T143108Z_verify_ok/failure.md`
- `docs/archive/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/failure.md`
- `docs/archive/audit/remediation/vs2026/20260213T054938Z_exitcheck_OTHER/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260213T054938Z_exitcheck_OTHER/failure.md`
- `docs/archive/audit/remediation/vs2026/20260213T055921Z_exitcheck_OTHER/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260213T055921Z_exitcheck_OTHER/failure.md`
- `docs/archive/audit/remediation/vs2026/20260213T063945Z_verify_DERIVED_ARTIFACT_STALE/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260213T063945Z_verify_DERIVED_ARTIFACT_STALE/failure.md`
- `docs/archive/audit/remediation/vs2026/20260213T075116Z_strict_ok/diff_summary.txt`
- `docs/archive/audit/remediation/vs2026/20260213T075116Z_strict_ok/failure.md`
- `docs/archive/audit/remediation/ws-426fb129fc29daec/20260226T070322Z_verify_DERIVED_ARTIFACT_STALE/diff_summary.txt`
- `docs/archive/audit/remediation/ws-426fb129fc29daec/20260226T070322Z_verify_DERIVED_ARTIFACT_STALE/failure.md`
- `docs/archive/audit/remediation/ws-426fb129fc29daec/20260226T070425Z_strict_BUILD_OUTPUT_MISSING/diff_summary.txt`
- `docs/archive/audit/remediation/ws-426fb129fc29daec/20260226T070425Z_strict_BUILD_OUTPUT_MISSING/failure.md`
- `docs/archive/audit/repox/REPOX_SCOPE_ANALYSIS.md`
- `docs/archive/audit/security/README.md`
- `docs/archive/audit/system/ANB_OMEGA_REPORT.md`
- `docs/archive/audit/system/FAILURE_CLASSES.md`
- `docs/archive/audit/system/GOVERNANCE_FINAL_REPORT.md`
- `docs/archive/audit/system/PORTABILITY_REPORT.md`
- `docs/archive/audit/system/REPO_HEALTH_SNAPSHOT.md`
- `docs/archive/audit/system/XSTACK_FINAL_POLISH_REPORT.md`
- `docs/archive/audit/system/XSTACK_PRODUCTION_FINAL_REPORT.md`
- `docs/archive/audit/testx/TESTX_SUMMARY.md`
- `docs/archive/audit/xstack/BOTTLENECK_ANALYSIS.md`
- `docs/archive/audit/xstack/FINAL_PERFORMANCE_VALIDATION.md`
- `docs/archive/audit/xstack/OPTIMIZATION_SUMMARY.md`
- `docs/archive/audit/xstack/REPOX_SCOPE_FINAL_REPORT.md`
- `docs/archive/audit/xstack/XSTACK_SPEED_REPORT.md`
- `docs/build/ARTIFACT_IDENTITY_AND_METADATA.md`
- `docs/build/BOUNDARY_ENFORCEMENT.md`
- `docs/build/BUILD_LANES.md`
- `docs/build/CI_MATRIX.md`
- `docs/build/OS_FLOOR_POLICY.md`
- `docs/build/SKU_MODEL.md`
- `docs/build/TOOLCHAIN_MODEL.md`
- `docs/build/TRANSITION_DO_NOTS.md`
- `docs/domains/chemistry/CHEM_STRESS_DEGRADATION_POLICY.md`
- `docs/domains/chemistry/COMBUSTION_AND_FUEL_CHAINS.md`
- `docs/domains/chemistry/DEGRADATION_MODEL.md`
- `docs/domains/chemistry/INDUSTRIAL_PROCESSING_MODEL.md`
- `docs/testing/ci/BUILD_MATRIX.md`
- `docs/testing/ci/CI_ENFORCEMENT_MATRIX.md`
- `docs/testing/ci/CODEHYGIENE_RULES.md`
- `docs/testing/ci/DETERMINISM_TEST_MATRIX.md`
- `docs/testing/ci/DIST_PKG_PIPELINE.md`
- `docs/testing/ci/EXECUTION_ENFORCEMENT_CHECKS.md`
- `docs/testing/ci/FUTURE_ENFORCEMENT.md`
- `docs/testing/ci/HYGIENE_QUEUE.md`
- `docs/testing/ci/KNOWN_BLOCKERS.md`
- `docs/testing/ci/REGRESSION_SUITES.md`
- `docs/testing/ci/TESTX_GATE_CONTRACT.md`
- `docs/testing/ci/TESTX_TIMEOUT_ANALYSIS.md`
- `docs/testing/ci/VERIFY_FAST_VS_FULL.md`
- `docs/apps/client/CLIENT_COMMAND_GRAPH.md`
- `docs/apps/client/CLIENT_FLOW.md`
- `docs/apps/client/CLIENT_LIFECYCLE_PIPELINE.md`
- `docs/apps/client/CLI_TUI_GUI_PARITY.md`
- `docs/apps/client/SERVER_DISCOVERY.md`
- `docs/apps/client/SESSION_READY_AND_RUNNING.md`
- `docs/apps/client/SESSION_SPEC_AND_AUTHORITY_CONTEXT.md`
- `docs/apps/client/SESSION_TRANSITION_WORKSPACE.md`
- `docs/apps/client/WORLD_MANAGER.md`
- `docs/compatibility/MIGRATION_LIFECYCLE_MODEL.md`
- `docs/content/BASE_PACKS.md`
- `docs/content/CONTENTLIB_OVERVIEW.md`
- `docs/content/CONTENT_OVERVIEW.md`
- `docs/content/DATA_1_OVERVIEW.md`
- `docs/content/DATA_2_GOVERNANCE_OVERVIEW.md`
- `docs/content/DATA_3_WORLD_OVERVIEW.md`
- `docs/content/FALLBACK_MATRIX.md`
- `docs/content/IMPORTANCE_INDEX.md`
- `docs/content/INFINITE_DETAIL.md`
- `docs/content/PACK_CAPABILITIES.md`
- `docs/content/PORTABILITY.md`
- `docs/content/README.md`
- `docs/content/REALITY_OVERLAYS.md`
- `docs/content/REFINEMENT_MODEL.md`
- `docs/content/SIGNALS_AND_COMPUTATION.md`
- `docs/content/UPS.md`
- `docs/content/UPS_OVERVIEW.md`
- `docs/content/WORLDGEN_PACKS.md`
- `docs/reference/contracts/authority_context.md`
- `docs/reference/contracts/experience_profile.md`
- `docs/reference/contracts/law_profile.md`
- `docs/reference/contracts/lens_contract.md`
- `docs/reference/contracts/refusal_contract.md`
- `docs/reference/contracts/session_spec.md`
- `docs/reference/contracts/versioning_and_migration.md`
- `docs/development/BUILD_MATRIX.md`
- `docs/development/C17_USAGE_POLICY.md`
- `docs/development/CLIP_DRIVEN_DEVELOPMENT.md`
- `docs/development/CPP17_USAGE_POLICY.md`
- `docs/development/DEBUG_AND_DIAGNOSTICS_MODEL.md`
- `docs/development/DEVELOPER_ACCELERATION_MODEL.md`
- `docs/development/DEV_COMMANDS.md`
- `docs/development/EXPLORATION_SCALING_TESTS.md`
- `docs/development/GUI_TO_COMMAND_WORKFLOW.md`
- `docs/development/IDE_BUILD_DEFAULTS.md`
- `docs/development/IDE_SETUP.md`
- `docs/development/IMPACT_GRAPH.md`
- `docs/development/LANGUAGE_BASELINE.md`
- `docs/development/LOCAL_BUILD_RULES.md`
- `docs/development/MACOS_10_9_CPP17_LIBRARY_SUBSET.md`
- `docs/development/ONE_BINARY_THREE_MODES.md`
- `docs/development/PLAYTESTING_GUIDE.md`
- `docs/development/PORTABLE_TESTING.md`
- `docs/development/README.md`
- `docs/development/REPLAY_DEBUGGING.md`
- `docs/development/REPLAY_WORKFLOW.md`
- `docs/development/TOOLS_GUIDE.md`
- `docs/development/TOOLS_OVERVIEW.md`
- `docs/development/TOOL_INVOCATION_POLICY.md`
- `docs/development/UI_BINDING_PIPELINE.md`
- `docs/development/UI_BINDING_RULES.md`
- `docs/development/UI_GUIDELINES.md`
- `docs/development/UI_NAMING_CONVENTIONS.md`
- `docs/game/diegetics/COMMUNICATION_CHANNELS_OVERVIEW.md`
- `docs/game/diegetics/DIEGETIC_FIRST_ENFORCEMENT.md`
- `docs/game/diegetics/DIEGETIC_INSTRUMENT_DOCTRINE.md`
- `docs/game/diegetics/MAP_AND_NOTEBOOK_MODEL.md`
- `docs/distribution/DIST_PLATFORM_DOCTRINE.md`
- `docs/distribution/DIST_TREE_CONTRACT.md`
- `docs/distribution/LAUNCHER_GUIDE.md`
- `docs/distribution/LAUNCHER_SCOPE.md`
- `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`
- `docs/distribution/LEGACY_COMPATIBILITY.md`
- `docs/distribution/OFFLINE_AND_STEAM_MAPPING.md`
- `docs/distribution/OFFLINE_INSTALL.md`
- `docs/distribution/PACK_SOURCES.md`
- `docs/distribution/PACK_TAXONOMY.md`
- `docs/distribution/PKG_FORMAT.md`
- `docs/distribution/PKG_INSTALL_AND_ROLLBACK.md`
- `docs/distribution/PKG_MANIFEST.md`
- `docs/distribution/PLATFORM_ID_CANON.md`
- `docs/distribution/PRODUCT_GRAPH_AND_MODES.md`
- `docs/distribution/SETUP_GUARANTEES.md`
- `docs/distribution/SETUP_GUIDE.md`
- `docs/distribution/UNINSTALL_AND_REPAIR.md`
- `docs/domains/electricity/CASCADE_MODEL.md`
- `docs/domains/electricity/DEVICE_MODELS.md`
- `docs/domains/electricity/ELECTRICAL_CONSTITUTION.md`
- `docs/domains/electricity/ELECTRICAL_UX_MODEL.md`
- `docs/domains/electricity/PROTECTION_AND_FAULT_MODEL.md`
- `docs/domains/electricity/SHARD_BOUNDARY_RULES.md`
- `docs/domains/embodiment/BODY_PRIMITIVES_AND_COLLISION.md`
- `docs/domains/embodiment/CAMERA_AND_VIEW_LENSES.md`
- `docs/domains/embodiment/CONTROL_SUBSTRATE_DOCTRINE.md`
- `docs/domains/embodiment/MOVEMENT_PROCESSES.md`
- `docs/domains/embodiment/REPRESENTATION_LAYER.md`
- `docs/engine/API_SPINE.md`
- `docs/engine/CODE_1_CHANGELOG.md`
- `docs/engine/FAB_INTERPRETERS.md`
- `docs/engine/NUMERIC_DISCIPLINE_MODEL.md`
- `docs/engine/PRIMITIVES.md`
- `docs/engine/README.md`
- `docs/engine/UPS_RUNTIME.md`
- `docs/game/epistemics/LOD_EPISTEMIC_INVARIANCE.md`
- `docs/game/epistemics/MEMORY_AND_FOG_OF_WAR.md`
- `docs/reference/examples/EXPLORATION_BASELINE.md`
- `docs/reference/examples/GEOLOGY_FIXTURE_EXAMPLE.md`
- `docs/reference/examples/INTERACTION_BASELINE.md`
- `docs/reference/examples/SIGNALS_BASELINE.md`
- `docs/reference/examples/SLICE_1_WALKTHROUGH.md`
- `docs/reference/examples/SLICE_2_WALKTHROUGH.md`
- `docs/reference/examples/TERRAIN_FIXTURE_EXAMPLE.md`
- `docs/reference/examples/false_science/README.md`
- `docs/reference/examples/lost_civilization/README.md`
- `docs/reference/examples/magic_earth/README.md`
- `docs/reference/examples/multicosmology/README.md`
- `docs/reference/examples/realistic_earth/README.md`
- `docs/domains/fields/FIELD_LAYER_MODEL.md`
- `docs/domains/fluids/CONTAINMENT_AND_FAILURE.md`
- `docs/domains/fluids/FLUID_CONSTITUTION.md`
- `docs/domains/fluids/SHARD_BOUNDARY_RULES.md`
- `docs/game/FAB_EXECUTION_FLOW.md`
- `docs/game/INTERFACE_CONTRACT.md`
- `docs/game/PRIMITIVES.md`
- `docs/game/README.md`
- `docs/game/gameplay/CONSTRUCTION_MODEL.md`
- `docs/game/gameplay/FAILURE_AND_MAINTENANCE.md`
- `docs/game/gameplay/ITERATION_MODEL.md`
- `docs/game/gameplay/NETWORKS.md`
- `docs/game/gameplay/ON_PLANET_ACTIONS.md`
- `docs/game/gameplay/TERRAFORMING.md`
- `docs/domains/geology/FIELD_BINDING_TO_GEO.md`
- `docs/domains/geology/GEOMETRY_EDIT_CONTRACT.md`
- `docs/domains/geology/GEO_CONSTITUTION.md`
- `docs/domains/geology/METRIC_QUERY_ENGINE.md`
- `docs/domains/geology/OVERLAY_MERGE_CONSTITUTION.md`
- `docs/domains/geology/PATHING_AND_TRAVERSAL_MODEL.md`
- `docs/domains/geology/PROJECTION_AND_LENS_MODEL.md`
- `docs/domains/geology/REFERENCE_FRAMES_AND_PRECISION.md`
- `docs/domains/geology/SPATIAL_INDEX_AND_IDENTITY.md`
- `docs/domains/geology/WORLDGEN_CONSTITUTION.md`
- `docs/reference/glossary/CANONICAL_GLOSSARY.md`
- `docs/governance/AUDITX_MODEL.md`
- `docs/governance/DATA_FIRST_DOCTRINE.md`
- `docs/governance/GATE_AUTONOMY_POLICY.md`
- `docs/governance/GOVERNANCE_MODEL.md`
- `docs/governance/LICENSING_STRATEGY.md`
- `docs/governance/MODE_GOVERNANCE_POLICY.md`
- `docs/governance/PROMPT_GATE_CONTRACT.md`
- `docs/governance/REPOX_RULESETS.md`
- `docs/governance/REPOX_TOOL_RULES.md`
- `docs/governance/TESTX_PROOF_MODEL.md`
- `docs/governance/TRUST_ROOT_GOVERNANCE.md`
- `docs/development/guides/AGENT_WORK_IR.md`
- `docs/development/guides/BUILDING.md`
- `docs/development/guides/BUILD_DIST.md`
- `docs/development/guides/BUILD_OVERVIEW.md`
- `docs/development/guides/CORE_DATA_GUIDE.md`
- `docs/development/guides/DATA_VALIDATION_GUIDE.md`
- `docs/development/guides/DEPENDENCIES.md`
- `docs/development/guides/DOMAIN_QUERY_AND_BUDGETS.md`
- `docs/development/guides/ECONOMY_WORK_IR.md`
- `docs/development/guides/EDITOR_BACKENDS.md`
- `docs/development/guides/FUTURE_PHASE_GUIDELINES.md`
- `docs/development/guides/GOVERNANCE_WORK_IR.md`
- `docs/development/guides/IMPLEMENTATION_BACKLOG_CANON.md`
- `docs/development/guides/IMPLEMENTATION_BACKLOG_NO_MODAL_LOADING.md`
- `docs/development/guides/IMPLEMENTATION_BACKLOG_UNIVERSE.md`
- `docs/development/guides/INTEGRITY_AND_DISPUTE_REPLAYS.md`
- `docs/development/guides/INTEREST_SYSTEM_WORK_IR.md`
- `docs/development/guides/KERNEL_BACKEND_SELECTION.md`
- `docs/development/guides/MILESTONES.md`
- `docs/development/guides/MODDING_GUIDE.md`
- `docs/development/guides/NO_GLOBAL_ITERATION_GUIDE.md`
- `docs/development/guides/NO_MODAL_LOADING.md`
- `docs/development/guides/OFFLINE_AND_LOCAL_MP.md`
- `docs/development/guides/PROFILES_AND_BUDGETS.md`
- `docs/development/guides/PROFILING_GUIDE.md`
- `docs/development/guides/README.md`
- `docs/development/guides/RELEASE_NOTES_PROCESS.md`
- `docs/development/guides/RELEASE_READINESS_CHECKLIST.md`
- `docs/development/guides/RENDER_PREP_MIGRATION_GUIDE.md`
- `docs/development/guides/SETUP_GAPS.md`
- `docs/development/guides/STREAMING_MIGRATION_GUIDE.md`
- `docs/development/guides/STYLE.md`
- `docs/development/guides/WAR_WORK_IR.md`
- `docs/development/guides/WORK_IR_EMISSION_GUIDE.md`
- `docs/development/guides/WORLD_CONTENT_GUIDE.md`
- `docs/development/guides/api/LAUNCHER_CLI.md`
- `docs/development/guides/api/RUNTIME_CLI.md`
- `docs/development/guides/api/SETUP_CLI.md`
- `docs/development/guides/build_output.md`
- `docs/development/guides/context/dominium_newcontext.txt`
- `docs/development/guides/dev/dominium_new_addendum.txt`
- `docs/development/guides/dev/dominium_new_build.txt`
- `docs/development/guides/dev/dominium_new_data.txt`
- `docs/development/guides/dev/dominium_new_data_base.txt`
- `docs/development/guides/dev/dominium_new_data_dlc.txt`
- `docs/development/guides/dev/dominium_new_data_packs.txt`
- `docs/development/guides/dev/dominium_new_data_templates.txt`
- `docs/development/guides/dev/dominium_new_engine_audio.txt`
- `docs/development/guides/dev/dominium_new_engine_core.txt`
- `docs/development/guides/dev/dominium_new_engine_ecs.txt`
- `docs/development/guides/dev/dominium_new_engine_net.txt`
- `docs/development/guides/dev/dominium_new_engine_path.txt`
- `docs/development/guides/dev/dominium_new_engine_physics.txt`
- `docs/development/guides/dev/dominium_new_engine_platform.txt`
- `docs/development/guides/dev/dominium_new_engine_render.txt`
- `docs/development/guides/dev/dominium_new_engine_sim.txt`
- `docs/development/guides/dev/dominium_new_engine_spatial.txt`
- `docs/development/guides/dev/dominium_new_engine_ui.txt`
- `docs/development/guides/dev/dominium_new_external.txt`
- `docs/development/guides/dev/dominium_new_game_client.txt`
- `docs/development/guides/dev/dominium_new_game_launcher.txt`
- `docs/development/guides/dev/dominium_new_game_server.txt`
- `docs/development/guides/dev/dominium_new_mods.txt`
- `docs/development/guides/dev/dominium_new_package.txt`
- `docs/development/guides/dev/dominium_new_ports.txt`
- `docs/development/guides/dev/dominium_new_root.txt`
- `docs/development/guides/dev/dominium_new_scripts.txt`
- `docs/development/guides/dev/dominium_new_tests.txt`
- `docs/development/guides/dev/dominium_new_tools.txt`
- `docs/development/guides/release/BUILD_AND_PACKAGE.md`
- `docs/development/guides/release/RECOVERY_PLAYBOOK.md`
- `docs/development/guides/release/RELEASE_READINESS_CHECKLIST.md`
- `docs/development/guides/release/SETUP_RELEASE_NOTES.md`
- `docs/development/guides/ui_editor/CAPABILITY_TEST.md`
- `docs/development/guides/ui_editor/CLI.md`
- `docs/development/guides/ui_editor/FLICKER_NOTES.md`
- `docs/development/guides/ui_editor/IDE_LIVE_EDITING.md`
- `docs/development/guides/ui_editor/IMPORT_EXPORT.md`
- `docs/development/guides/ui_editor/OPS_FORMAT.md`
- `docs/development/guides/ui_editor/PHASE_A_DONE_CHECKLIST.md`
- `docs/development/guides/ui_editor/REPO_MAP_UI_SYSTEM.md`
- `docs/development/guides/ui_editor/SPEC_ACTIONS_AND_EVENTS.md`
- `docs/development/guides/ui_editor/SPEC_CAPABILITIES.md`
- `docs/development/guides/ui_editor/SPEC_CODEGEN_ACTIONS.md`
- `docs/development/guides/ui_editor/SPEC_UI_DOC_TLV.md`
- `docs/development/guides/ui_editor/TEST_MINECRAFT_LAUNCHER.md`
- `docs/development/guides/ui_editor/TEST_MINECRAFT_SETUP.md`
- `docs/development/guides/ui_editor/TOOL_EDITOR_BOOTSTRAP_CHECKLIST.md`
- `docs/development/guides/ui_editor/WORKFLOW_END_TO_END.md`
- `docs/development/guides/ui_editor/ide/xcode/README.md`
- `docs/archive/impact/GEO4_FIELD_BINDING.md`
- `docs/archive/impact/GEO8_WORLDGEN_CONTRACT.md`
- `docs/archive/impact/GR3_FAST.md`
- `docs/archive/impact/GR3_NO_STOPS_HARDENING.md`
- `docs/archive/impact/GR3_STRICT.md`
- `docs/archive/impact/LIB1_INSTALL_MANIFEST.md`
- `docs/archive/impact/LIB2_INSTANCE_MANIFEST.md`
- `docs/archive/impact/LIB3_SAVE_MANIFEST.md`
- `docs/archive/impact/LIB4_ARTIFACT_MANIFEST.md`
- `docs/archive/impact/LIB5_FORKING_PROVIDES.md`
- `docs/archive/impact/LIB7_LIBRARY_ENVELOPE.md`
- `docs/archive/impact/LOGIC4_EVAL_ENGINE.md`
- `docs/archive/impact/LOGIC8_FAULT_NOISE_SECURITY.md`
- `docs/archive/impact/LOGIC9_PROTOCOL_LAYER.md`
- `docs/archive/impact/META_COMPUTE0.md`
- `docs/archive/impact/META_GENRE0.md`
- `docs/archive/impact/OMEGA_PREP_RUNTIME_HARDENING.md`
- `docs/archive/impact/README.md`
- `docs/archive/impact/RELEASE_RUNTIME_MVP_READINESS.md`
- `docs/domains/infrastructure/FORMALIZATION_MODEL.md`
- `docs/game/interaction/ACTION_SURFACE_MODEL.md`
- `docs/game/interaction/INSPECTION_OVERLAYS.md`
- `docs/game/interaction/INTERACTION_MODEL.md`
- `docs/game/interaction/MACHINE_PORTS.md`
- `docs/game/interaction/POSE_AND_MOUNT_MODEL.md`
- `docs/game/interaction/REFUSAL_UX.md`
- `docs/game/interaction/TASK_AND_WORK_MODEL.md`
- `docs/game/interaction/TOOLS_AND_EFFECTS.md`
- `docs/domains/interiors/INTERIOR_VOLUME_MODEL.md`
- `docs/domains/knowledge/BLUEPRINTS_AND_RESEARCH.md`
- `docs/domains/knowledge/DISCOVERY_AND_MEASUREMENT.md`
- `docs/domains/knowledge/EPISTEMICS_OVERVIEW.md`
- `docs/domains/knowledge/MISINFORMATION.md`
- `docs/domains/knowledge/README.md`
- `docs/runtime/storage/STORE_INTEGRITY_AND_GC.md`
- `docs/domains/logic/DEBUG_AND_INSTRUMENTATION.md`
- `docs/domains/logic/FAULT_NOISE_SECURITY_MODEL.md`
- `docs/domains/logic/LOGIC_COMPILATION_MODEL.md`
- `docs/domains/logic/LOGIC_NETWORKGRAPH.md`
- `docs/domains/logic/LOGIC_SHARD_BOUNDARY_RULES.md`
- `docs/domains/logic/PROTOCOL_LAYER_MODEL.md`
- `docs/domains/logic/PROTOCOL_SHARD_RULES.md`
- `docs/domains/logic/TIMING_AND_OSCILLATION_MODEL.md`
- `docs/domains/materials/BOM_AND_ASSEMBLY_GRAPH.md`
- `docs/domains/materials/CONSTRUCTION_AND_INSTALLATION.md`
- `docs/domains/materials/DECAY_FAILURE_MAINTENANCE.md`
- `docs/domains/materials/FAILURE_AND_MAINTENANCE_MODEL.md`
- `docs/domains/materials/GUARDRAIL_DECLARATIONS.md`
- `docs/domains/materials/INSPECTION_SYSTEM.md`
- `docs/domains/materials/LOGISTICS_GRAPH.md`
- `docs/domains/materials/MACRO_MICRO_MAPPING.md`
- `docs/domains/materials/MANIFESTS_AND_SHIPMENTS.md`
- `docs/domains/materials/MATERIALS_CONSTITUTION.md`
- `docs/domains/materials/MATERIAL_INVARIANTS.md`
- `docs/domains/materials/MATERIAL_TAXONOMY.md`
- `docs/domains/materials/NOTHING_JUST_HAPPENS.md`
- `docs/domains/materials/PERFORMANCE_AND_SCALE_STRATEGY.md`
- `docs/domains/materials/PROVENANCE_AND_COMMITMENTS.md`
- `docs/domains/materials/PROVENANCE_EVENTS.md`
- `docs/domains/materials/REENACTMENT_MODEL.md`
- `docs/domains/materials/TIERED_MATERIAL_REPRESENTATION.md`
- `docs/domains/materials/UNITS_AND_DIMENSIONS.md`
- `docs/domains/mechanics/MECHANICS_SUBSTRATE_MODEL.md`
- `docs/governance/meta/ACTION_GRAMMAR_CONSTITUTION.md`
- `docs/governance/meta/AFFORDANCE_EXTENSION_CONTRACT.md`
- `docs/governance/meta/COMPILED_MODEL_CONSTITUTION.md`
- `docs/governance/meta/COMPUTE_BUDGET_CONSTITUTION.md`
- `docs/governance/meta/CONSTITUTIVE_MODEL_CATALOG.md`
- `docs/governance/meta/CONSTITUTIVE_MODEL_CONSTITUTION.md`
- `docs/governance/meta/COUPLING_BUDGET_AND_RELEVANCE.md`
- `docs/governance/meta/EXTENSION_MIGRATION_NOTES.md`
- `docs/governance/meta/IDENTITY_INTEGRATION_MAP.md`
- `docs/governance/meta/INFORMATION_GRAMMAR_CONSTITUTION.md`
- `docs/governance/meta/INSTRUMENTATION_SURFACE_STANDARD.md`
- `docs/governance/meta/NUMERICAL_TOLERANCE_CONSTITUTION.md`
- `docs/governance/meta/OBSERVABILITY_CONTRACT.md`
- `docs/governance/meta/PLAYER_DEMAND_COVERAGE_MATRIX.md`
- `docs/governance/meta/PROFILE_OVERRIDE_ARCHITECTURE.md`
- `docs/governance/meta/REAL_WORLD_AFFORDANCE_MATRIX.md`
- `docs/governance/meta/REFERENCE_INTERPRETER_CONSTITUTION.md`
- `docs/governance/meta/STABILITY_CLASSIFICATION.md`
- `docs/governance/meta/STABILITY_REGISTRY_CONVENTION.md`
- `docs/governance/meta/TIER_COUPLING_EXPLAIN_CONTRACTS.md`
- `docs/governance/meta/UNIVERSAL_IDENTITY_MODEL.md`
- `docs/domains/mobility/GUIDE_GEOMETRY.md`
- `docs/domains/mobility/MACRO_TRAVEL_MODEL.md`
- `docs/domains/mobility/MESO_TRAFFIC_MODEL.md`
- `docs/domains/mobility/MICRO_CONSTRAINED_MOTION.md`
- `docs/domains/mobility/MICRO_FREE_MOTION.md`
- `docs/domains/mobility/MOBILITY_CONSTITUTION.md`
- `docs/domains/mobility/MOBILITY_EXTENSION_CONTRACT.md`
- `docs/domains/mobility/MOBILITY_NETWORKGRAPH.md`
- `docs/domains/mobility/VEHICLE_INTERIORS.md`
- `docs/domains/mobility/VEHICLE_MODEL.md`
- `docs/modding/DEBUGGING_DATA.md`
- `docs/modding/FABRICATION_AUTHORING_GUIDE.md`
- `docs/modding/FORBIDDEN_MOD_PATTERNS.md`
- `docs/modding/LOCALIZATION_PACKS.md`
- `docs/modding/MOD_AUTHORING_OVERVIEW.md`
- `docs/modding/MOD_COMPATIBILITY_CHECKLIST.md`
- `docs/modding/MOD_ECOSYSTEM.md`
- `docs/modding/README.md`
- `docs/modding/SAFE_MOD_PATTERNS.md`
- `docs/release/mvp/MVP_CROSS_PLATFORM_GATE.md`
- `docs/release/mvp/MVP_INSTALL_LAYOUT.md`
- `docs/release/mvp/MVP_RUNTIME_BUNDLE.md`
- `docs/release/mvp/MVP_SMOKE_SUITE.md`
- `docs/release/mvp/MVP_STRESS_GATE.md`
- `docs/runtime/network/ANTI_CHEAT_ENFORCEMENT_ACTIONS.md`
- `docs/runtime/network/ANTI_CHEAT_MODULES.md`
- `docs/runtime/network/ANTI_CHEAT_POLICY_FRAMEWORK.md`
- `docs/runtime/network/DIEGETIC_CHANNELS_OVER_NETWORK.md`
- `docs/runtime/network/EPISTEMICS_OVER_NETWORK.md`
- `docs/runtime/network/EPISTEMIC_SCOPE_AND_FOG_OF_WAR.md`
- `docs/runtime/network/ESPORTS_PROOF_ARTIFACTS.md`
- `docs/runtime/network/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/runtime/network/MULTIPLAYER_MODEL_OVERVIEW.md`
- `docs/runtime/network/RANKED_SERVER_GOVERNANCE.md`
- `docs/runtime/network/REPLICATION_POLICIES.md`
- `docs/runtime/network/SERVER_AUTHORITATIVE_POLICY.md`
- `docs/runtime/network/SRZ_HYBRID_POLICY.md`
- `docs/runtime/network/TRANSPORT_ABSTRACTION.md`
- `docs/operations/COMMIT_CONVENTIONS.md`
- `docs/operations/FAILURE_SCENARIOS.md`
- `docs/operations/INSTANCE_LIFECYCLE.md`
- `docs/operations/LOGGING_MODEL.md`
- `docs/operations/LONG_RUN_EXPECTATIONS.md`
- `docs/operations/MMO_RUNBOOK.md`
- `docs/operations/MMO_SCALING_PLAYBOOK.md`
- `docs/operations/OFFLINE_AND_AIRGAPPED.md`
- `docs/operations/RELEASE_AND_CHANNELS.md`
- `docs/operations/RELEASE_PIPELINE.md`
- `docs/operations/SERVER_OPERATIONS.md`
- `docs/operations/SERVER_SCOPE.md`
- `docs/operations/UPDATE_AND_ROLLBACK.md`
- `docs/distribution/package-format/PACK_MANIFEST.md`
- `docs/performance/PERFORMANCE_ENVELOPE_v0_0_0_mock.md`
- `docs/domains/physics/physical/CONSTRUCTION_MODEL.md`
- `docs/domains/physics/physical/FAILURE_AND_MAINTENANCE.md`
- `docs/domains/physics/physical/NETWORKS_AND_INFRASTRUCTURE.md`
- `docs/domains/physics/physical/PARTS_AND_ASSEMBLIES.md`
- `docs/domains/physics/physical/TERRAIN_MODEL.md`
- `docs/domains/physics/ENERGY_LEDGER_AND_TRANSFORMATIONS.md`
- `docs/domains/physics/ENTROPY_POLICY.md`
- `docs/domains/physics/FIELD_GENERALIZATION.md`
- `docs/domains/physics/FIELD_SHARD_BOUNDARY_ENFORCEMENT.md`
- `docs/domains/physics/FIELD_SHARD_RULES.md`
- `docs/domains/physics/PHYSICS_CONSTITUTION.md`
- `docs/domains/physics/PHYSICS_PROOF_REPLAY_HOOKS.md`
- `docs/runtime/platform/EVENT_QUEUE.md`
- `docs/runtime/platform/EXTENSIONS.md`
- `docs/runtime/platform/LIFECYCLE_AND_SIGNALS.md`
- `docs/runtime/platform/MULTI_WINDOW.md`
- `docs/runtime/platform/PLATFORM_RUNTIME.md`
- `docs/runtime/platform/README.md`
- `docs/runtime/platform/WINDOW_MODES_DPI_INPUT.md`
- `docs/game/player/EXPERIENCES_AND_DEFAULTS.md`
- `docs/game/player/PLAYER_AS_AGENT.md`
- `docs/game/player/PLAYER_AUTHORITY.md`
- `docs/game/player/PLAYER_FAILURE.md`
- `docs/game/player/PLAYER_INTENT_MODEL.md`
- `docs/game/player/PLAYER_NON_GOALS.md`
- `docs/governance/policies/CODE_OF_CONDUCT.md`
- `docs/governance/policies/COMMIT_CONVENTIONS.md`
- `docs/governance/policies/COMPAT_TERMS.md`
- `docs/governance/policies/DETERMINISM_ENFORCEMENT.md`
- `docs/governance/policies/DETERMINISM_GATES.md`
- `docs/governance/policies/DETERMINISM_HASH_PARTITIONS.md`
- `docs/governance/policies/DETERMINISTIC_MATH.md`
- `docs/governance/policies/DETERMINISTIC_ORDERING.md`
- `docs/governance/policies/DETERMINISTIC_RNG.md`
- `docs/governance/policies/DOCUMENTATION_STANDARDS.md`
- `docs/governance/policies/IDE_CONTRIBUTION_RULES.md`
- `docs/governance/policies/LANGUAGE_POLICY.md`
- `docs/governance/policies/PERFORMANCE_ENFORCEMENT.md`
- `docs/governance/policies/PERF_BUDGETS.md`
- `docs/governance/policies/README.md`
- `docs/governance/policies/VALIDATION_AND_GOVERNANCE.md`
- `docs/domains/pollution/DISPERSION_MODEL.md`
- `docs/domains/pollution/EXPOSURE_AND_COMPLIANCE_MODEL.md`
- `docs/domains/pollution/POLLUTION_CONSTITUTION.md`
- `docs/archive/post-canon/IVRH_LOOP.md`
- `docs/archive/post-canon/L1_PROCESS_REGISTRY.md`
- `docs/archive/post-canon/L2_SCHEMA_EVOLUTION.md`
- `docs/archive/post-canon/L3_CAPABILITY_STAGES.md`
- `docs/archive/post-canon/L4_STAGE_MATRIX.md`
- `docs/domains/processes/DRIFT_AND_REVALIDATION_MODEL.md`
- `docs/domains/processes/PROCESS_CAPSULE_MODEL.md`
- `docs/domains/processes/PROCESS_CONSTITUTION.md`
- `docs/domains/processes/PROCESS_DEFINITION_MODEL.md`
- `docs/domains/processes/QC_SAMPLING_MODEL.md`
- `docs/domains/processes/RESEARCH_AND_REVERSE_ENGINEERING_MODEL.md`
- `docs/domains/processes/SOFTWARE_PIPELINE_MODEL.md`
- `docs/domains/processes/STABILIZATION_AND_MATURITY_MODEL.md`
- `docs/domains/processes/YIELD_DEFECT_MODEL.md`
- `docs/archive/prompts/PROMPT_SLICE_4.md`
- `docs/game/realities/FALSE_SCIENCE.md`
- `docs/game/realities/MAGIC_IS_DATA.md`
- `docs/game/realities/REALITY_DOMAINS.md`
- `docs/domains/reality/CONSERVATION_AND_EXCEPTIONS.md`
- `docs/domains/reality/PERFORMANCE_CONSTITUTION.md`
- `docs/domains/reality/TIER_TAXONOMY_AND_TRANSITIONS.md`
- `docs/domains/reality/TIME_CONSTITUTION.md`
- `docs/domains/reality/UNIVERSE_PHYSICS_PROFILE.md`
- `docs/release/ARCHIVE_AND_RETENTION_POLICY.md`
- `docs/release/CLEAN_ROOM_TEST_MODEL.md`
- `docs/release/GIT_TAGGING_AND_RELEASE_POLICY.md`
- `docs/release/INSTALL_PROFILES.md`
- `docs/release/RELEASE_INDEX_MODEL.md`
- `docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md`
- `docs/release/SETUP_SELF_UPDATE.md`
- `docs/release/SUPPORTED_PLATFORMS_v0_0_0_mock.md`
- `docs/release/TARGET_CAPABILITY_RULES.md`
- `docs/release/TARGET_MATRIX_v0_0_0_mock.md`
- `docs/release/UX_POLISH_CRITERIA.md`
- `docs/runtime/render/BACKENDS.md`
- `docs/runtime/render/NULL_RENDERER.md`
- `docs/runtime/render/PLATFORM_AND_BACKENDS.md`
- `docs/runtime/render/PROCEDURAL_RENDERING_DEFAULTS.md`
- `docs/runtime/render/README.md`
- `docs/runtime/render/RENDERMODEL_CONTRACT.md`
- `docs/runtime/render/RENDER_INTERFACE.md`
- `docs/runtime/render/RENDER_SNAPSHOT_ARTIFACTS.md`
- `docs/runtime/render/SOFTWARE_RENDERER.md`
- `docs/runtime/render/SWAPCHAINS_AND_SURFACES.md`
- `docs/repo/repox/APRX_INTEGRATION_HOOKS.md`
- `docs/release/roadmap/FAILURE_PREMORTEM.md`
- `docs/release/roadmap/MMO_OPS_ACCEPTANCE.md`
- `docs/release/roadmap/NOT_IN_MVP.md`
- `docs/release/roadmap/README.md`
- `docs/release/roadmap/ROADMAP_OVERVIEW.md`
- `docs/release/roadmap/SIMULATION_COVERAGE_LADDER.md`
- `docs/release/roadmap/SLICE_0_ACCEPTANCE.md`
- `docs/release/roadmap/SLICE_1_ACCEPTANCE.md`
- `docs/release/roadmap/SLICE_2_ACCEPTANCE.md`
- `docs/release/roadmap/SLICE_VS_COVERAGE.md`
- `docs/release/roadmap/WORLD_CREATION_FLOW.md`
- `docs/release/roadmap/milestone_lab_galaxy.md`
- `docs/safety/SAFETY_PATTERN_LIBRARY.md`
- `docs/domains/scale/CONTRACTS_AND_CONSERVATION.md`
- `docs/domains/scale/DOMAIN_MODEL.md`
- `docs/domains/scale/DOMAIN_REGISTRY.md`
- `docs/domains/scale/SOLVER_DOMAIN_BINDINGS.md`
- `docs/reference/schema/FORWARD_COMPATIBILITY.md`
- `docs/reference/schema/SCHEMA_INDEX.md`
- `docs/security/CHEATING_AND_VERIFICATION.md`
- `docs/security/CHEAT_THREAT_MODEL.md`
- `docs/security/README.md`
- `docs/security/SECUREX_MODEL.md`
- `docs/security/SECUREX_TRUST_MODEL.md`
- `docs/security/THREAT_MODEL.md`
- `docs/security/TRUST_BOUNDARIES.md`
- `docs/domains/astronomy/sol/ILLUMINATION_GEOMETRY_MODEL.md`
- `docs/domains/astronomy/sol/ORBIT_VISUALIZATION_MODEL.md`
- `docs/reference/specs/AGENT_AGGREGATION_AND_SCALE.md`
- `docs/reference/specs/AGENT_DOCTRINE_AND_ROLES.md`
- `docs/reference/specs/AGENT_GOALS_AND_PLANNING.md`
- `docs/reference/specs/CIV5_WAR_ENGAGEMENTS.md`
- `docs/reference/specs/CIV5_WAR_INTERPLANETARY.md`
- `docs/reference/specs/CIV5_WAR_OCCUPATION.md`
- `docs/reference/specs/CIV5_WAR_SECURITY_FORCES.md`
- `docs/reference/specs/CONTENT_BASE_EXAMPLE.md`
- `docs/reference/specs/COREDATA_BUILD.md`
- `docs/reference/specs/FIDELITY_DEGRADATION.md`
- `docs/reference/specs/FIDELITY_PROJECTION_IMPLEMENTATION.md`
- `docs/reference/specs/FORMAT_INSTALL_MANIFEST.md`
- `docs/reference/specs/INTEREST_SET_IMPLEMENTATION.md`
- `docs/reference/specs/LIFE_BIRTH_PIPELINE.md`
- `docs/reference/specs/LIFE_DEATH_PIPELINE.md`
- `docs/reference/specs/LIFE_REMAINS_SALVAGE.md`
- `docs/reference/specs/README.md`
- `docs/reference/specs/SPECSHEET_CONSTITUTION.md`
- `docs/reference/specs/SPEC_ACTORS.md`
- `docs/reference/specs/SPEC_AGENT.md`
- `docs/reference/specs/SPEC_AGGREGATES.md`
- `docs/reference/specs/SPEC_AI_DECISION_TRACES.md`
- `docs/reference/specs/SPEC_AI_DETERMINISM.md`
- `docs/reference/specs/SPEC_ARTIFACT_STORE.md`
- `docs/reference/specs/SPEC_ASSETS_INSTRUMENTS.md`
- `docs/reference/specs/SPEC_ATMOSPHERE.md`
- `docs/reference/specs/SPEC_BACKEND_CONFORMANCE.md`
- `docs/reference/specs/SPEC_BIOMES.md`
- `docs/reference/specs/SPEC_BLUEPRINTS.md`
- `docs/reference/specs/SPEC_BUILD.md`
- `docs/reference/specs/SPEC_CALENDARS.md`
- `docs/reference/specs/SPEC_CAPABILITIES.md`
- `docs/reference/specs/SPEC_CAPABILITY_REGISTRY.md`
- `docs/reference/specs/SPEC_CLIMATE_WEATHER.md`
- `docs/reference/specs/SPEC_COMMAND_MODEL.md`
- `docs/reference/specs/SPEC_COMMUNICATION.md`
- `docs/reference/specs/SPEC_CONSTRUCTIONS_V0.md`
- `docs/reference/specs/SPEC_CONTENT.md`
- `docs/reference/specs/SPEC_CONTRACTS.md`
- `docs/reference/specs/SPEC_CORE_DATA.md`
- `docs/reference/specs/SPEC_CORE_DATA_PIPELINE.md`
- `docs/reference/specs/SPEC_CORE_DATA_VALIDATION.md`
- `docs/reference/specs/SPEC_COSMO_CORE_DATA.md`
- `docs/reference/specs/SPEC_COSMO_ECONOMY_EVENTS.md`
- `docs/reference/specs/SPEC_COSMO_LANE.md`
- `docs/reference/specs/SPEC_CROSS_SHARD_MESSAGES.md`
- `docs/reference/specs/SPEC_DEBUG_UI.md`
- `docs/reference/specs/SPEC_DGFX_IR_VERSIONING.md`
- `docs/reference/specs/SPEC_DOCTRINE_AUTONOMY.md`
- `docs/reference/specs/SPEC_DOMINIUM_LAYER.md`
- `docs/reference/specs/SPEC_DOMINIUM_RULES.md`
- `docs/reference/specs/SPEC_DOMINO_AUDIO_UI_INPUT.md`
- `docs/reference/specs/SPEC_DOMINO_GFX.md`
- `docs/reference/specs/SPEC_DOMINO_MOD.md`
- `docs/reference/specs/SPEC_DOMINO_SIM.md`
- `docs/reference/specs/SPEC_DOMINO_SUBSYSTEMS.md`
- `docs/reference/specs/SPEC_DOMINO_SYS.md`
- `docs/reference/specs/SPEC_ECONOMY.md`
- `docs/reference/specs/SPEC_EDITOR_GUI.md`
- `docs/reference/specs/SPEC_EFFECT_FIELDS.md`
- `docs/reference/specs/SPEC_ENERGY.md`
- `docs/reference/specs/SPEC_ENV.md`
- `docs/reference/specs/SPEC_EPISTEMIC_GATING.md`
- `docs/reference/specs/SPEC_EPISTEMIC_INTERFACE.md`
- `docs/reference/specs/SPEC_EVENT_DRIVEN_STEPPING.md`
- `docs/reference/specs/SPEC_FACADES_BACKENDS.md`
- `docs/reference/specs/SPEC_FACTIONS.md`
- `docs/reference/specs/SPEC_FEATURE_EPOCH.md`
- `docs/reference/specs/SPEC_FIDELITY_DEGRADATION.md`
- `docs/reference/specs/SPEC_FIDELITY_PROJECTION.md`
- `docs/reference/specs/SPEC_FIELDS.md`
- `docs/reference/specs/SPEC_FIELDS_EVENTS.md`
- `docs/reference/specs/SPEC_FS_CONTRACT.md`
- `docs/reference/specs/SPEC_GAME_CLI.md`
- `docs/reference/specs/SPEC_GAME_CONTENT_API.md`
- `docs/reference/specs/SPEC_GAME_PRODUCT.md`
- `docs/reference/specs/SPEC_GRAPH_TOOLKIT.md`
- `docs/reference/specs/SPEC_HYDROLOGY.md`
- `docs/reference/specs/SPEC_IDENTITY.md`
- `docs/reference/specs/SPEC_INDEX.md`
- `docs/reference/specs/SPEC_INFORMATION_MODEL.md`
- `docs/reference/specs/SPEC_INPUT.md`
- `docs/reference/specs/SPEC_INSTANCE_LAYOUT.md`
- `docs/reference/specs/SPEC_INTEREST_SETS.md`
- `docs/reference/specs/SPEC_JOBS.md`
- `docs/reference/specs/SPEC_JOB_AI.md`
- `docs/reference/specs/SPEC_KNOWLEDGE.md`
- `docs/reference/specs/SPEC_KNOWLEDGE_VIS_COMMS.md`
- `docs/reference/specs/SPEC_LANES_AND_BUBBLES.md`
- `docs/reference/specs/SPEC_LEDGER.md`
- `docs/reference/specs/SPEC_LOGICAL_TRAVEL.md`
- `docs/reference/specs/SPEC_MACHINES.md`
- `docs/reference/specs/SPEC_MARKETS.md`
- `docs/reference/specs/SPEC_MATTER.md`
- `docs/reference/specs/SPEC_MECHANICS_PROFILES.md`
- `docs/reference/specs/SPEC_MEDIA_FRAMEWORK.md`
- `docs/reference/specs/SPEC_MIGRATIONS.md`
- `docs/reference/specs/SPEC_MODELS.md`
- `docs/reference/specs/SPEC_MONEY_STANDARDS.md`
- `docs/reference/specs/SPEC_NET.md`
- `docs/reference/specs/SPEC_NETCODE.md`
- `docs/reference/specs/SPEC_NETWORKS.md`
- `docs/reference/specs/SPEC_NET_HANDSHAKE.md`
- `docs/reference/specs/SPEC_NO_MODAL_LOADING.md`
- `docs/reference/specs/SPEC_ORBITS.md`
- `docs/reference/specs/SPEC_ORBITS_TIMEWARP.md`
- `docs/reference/specs/SPEC_PACKAGES.md`
- `docs/reference/specs/SPEC_PERF_BUDGETS.md`
- `docs/reference/specs/SPEC_PLAYER_CONTINUITY.md`
- `docs/reference/specs/SPEC_PLAY_FLOW.md`
- `docs/reference/specs/SPEC_PRODUCTS.md`
- `docs/reference/specs/SPEC_PROFILING.md`
- `docs/reference/specs/SPEC_PROPERTY_RIGHTS.md`
- `docs/reference/specs/SPEC_PROVENANCE.md`
- `docs/reference/specs/SPEC_QOS_ASSISTANCE.md`
- `docs/reference/specs/SPEC_RECIPES.md`
- `docs/reference/specs/SPEC_REENTRY_THERMAL.md`
- `docs/reference/specs/SPEC_REFERENCE_FRAMES.md`
- `docs/reference/specs/SPEC_RENDERING_CANON.md`
- `docs/reference/specs/SPEC_RENDER_CAPS.md`
- `docs/reference/specs/SPEC_RENDER_FEATURES.md`
- `docs/reference/specs/SPEC_RENDER_GRAPH.md`
- `docs/reference/specs/SPEC_REPLAY.md`
- `docs/reference/specs/SPEC_RES.md`
- `docs/reference/specs/SPEC_RESEARCH.md`
- `docs/reference/specs/SPEC_SCHEDULING.md`
- `docs/reference/specs/SPEC_SENSORS.md`
- `docs/reference/specs/SPEC_SESSIONS.md`
- `docs/reference/specs/SPEC_SETUP_CLI.md`
- `docs/reference/specs/SPEC_SETUP_CORE.md`
- `docs/reference/specs/SPEC_SHADER_IR.md`
- `docs/reference/specs/SPEC_SHARDING_AUTHORITY.md`
- `docs/reference/specs/SPEC_SIM.md`
- `docs/reference/specs/SPEC_SMOKE_TESTS.md`
- `docs/reference/specs/SPEC_SPACETIME.md`
- `docs/reference/specs/SPEC_SPACE_GRAPH.md`
- `docs/reference/specs/SPEC_STANDARDS_AND_RENDERERS.md`
- `docs/reference/specs/SPEC_STANDARD_RESOLUTION.md`
- `docs/reference/specs/SPEC_STREAMING_BUDGETS.md`
- `docs/reference/specs/SPEC_STRUCT.md`
- `docs/reference/specs/SPEC_SURFACE_STREAMING.md`
- `docs/reference/specs/SPEC_SURFACE_TOPOLOGY.md`
- `docs/reference/specs/SPEC_SYSTEMS_BODIES.md`
- `docs/reference/specs/SPEC_SYSTEM_LOGISTICS.md`
- `docs/reference/specs/SPEC_TIERS.md`
- `docs/reference/specs/SPEC_TIME_CORE.md`
- `docs/reference/specs/SPEC_TIME_FRAMES.md`
- `docs/reference/specs/SPEC_TIME_KNOWLEDGE.md`
- `docs/reference/specs/SPEC_TIME_STANDARDS.md`
- `docs/reference/specs/SPEC_TIME_WARP.md`
- `docs/reference/specs/SPEC_TOOLS_AS_INSTANCES.md`
- `docs/reference/specs/SPEC_TOOLS_CORE.md`
- `docs/reference/specs/SPEC_TOOL_IO.md`
- `docs/reference/specs/SPEC_TRANS.md`
- `docs/reference/specs/SPEC_TRANSPORT_NETWORKS.md`
- `docs/reference/specs/SPEC_UI_CAPABILITIES.md`
- `docs/reference/specs/SPEC_UI_PROJECTIONS.md`
- `docs/reference/specs/SPEC_UI_WIDGETS.md`
- `docs/reference/specs/SPEC_UNIVERSE_BUNDLE.md`
- `docs/reference/specs/SPEC_UNIVERSE_MODEL.md`
- `docs/reference/specs/SPEC_VALIDATION.md`
- `docs/reference/specs/SPEC_VEHICLE.md`
- `docs/reference/specs/SPEC_VEHICLES.md`
- `docs/reference/specs/SPEC_VIEW_UI.md`
- `docs/reference/specs/SPEC_VM.md`
- `docs/reference/specs/SPEC_WEATHER_CLIMATE_HOOKS.md`
- `docs/reference/specs/SPEC_WORLD_COORDS.md`
- `docs/reference/specs/SPEC_WORLD_SOURCE_STACK.md`
- `docs/reference/specs/SPEC_ZONES.md`
- `docs/reference/specs/STREAMING_BUDGETS.md`
- `docs/reference/specs/TOOL_ASSETC.md`
- `docs/reference/specs/TOOL_REPLAY.md`
- `docs/reference/specs/TOOL_TEST.md`
- `docs/reference/specs/UI_EPISTEMIC_BOUNDARY.md`
- `docs/reference/specs/UI_HANDOFF.md`
- `docs/reference/specs/core/CAPABILITIES_AND_SOLVER.md`
- `docs/reference/specs/core/CORE_LIBRARIES.md`
- `docs/reference/specs/core/INSTALLED_STATE_CONTRACT.md`
- `docs/reference/specs/core/JOB_ENGINE.md`
- `docs/reference/specs/core/LOGGING_EVENTS.md`
- `docs/reference/specs/core/PROVIDERS.md`
- `docs/reference/specs/core/TLV_SCHEMA_GOVERNANCE.md`
- `docs/reference/specs/launcher/ARCHITECTURE.md`
- `docs/reference/specs/launcher/ARTIFACT_STORE.md`
- `docs/reference/specs/launcher/BUILD_AND_PACKAGING.md`
- `docs/reference/specs/launcher/CAPS.md`
- `docs/reference/specs/launcher/CLI.md`
- `docs/reference/specs/launcher/DEV_UI.md`
- `docs/reference/specs/launcher/DIAGNOSTICS_AND_SUPPORT.md`
- `docs/reference/specs/launcher/DIAGNOSTICS_BUNDLES.md`
- `docs/reference/specs/launcher/ECOSYSTEM_INTEGRATION.md`
- `docs/reference/specs/launcher/INSTALLED_STATE_CONTRACT.md`
- `docs/reference/specs/launcher/INSTANCE_MODEL.md`
- `docs/reference/specs/launcher/LAUNCHER_SETUP_OVERVIEW.md`
- `docs/reference/specs/launcher/PACK_SYSTEM.md`
- `docs/reference/specs/launcher/RECOVERY_AND_SAFE_MODE.md`
- `docs/reference/specs/launcher/SECURITY_AND_TRUST.md`
- `docs/reference/specs/launcher/SETUP_HANDOFF.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_CLI.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_CORE.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_EXT.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_GUI.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_NET.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_PACKS.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_PRELAUNCH_CONFIG.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_PROFILES.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_PROTOCOL.md`
- `docs/reference/specs/launcher/SPEC_LAUNCHER_TUI.md`
- `docs/reference/specs/launcher/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/reference/specs/launcher/TESTING.md`
- `docs/reference/specs/launcher/TUI.md`
- `docs/reference/specs/launcher/UI_SYSTEM.md`
- `docs/reference/specs/launcher/news.txt`
- `docs/reference/specs/setup/ADAPTERS.md`
- `docs/reference/specs/setup/ADAPTER_MATRIX.md`
- `docs/reference/specs/setup/ADDING_FEATURES.md`
- `docs/reference/specs/setup/ARCHIVAL_AND_HANDOFF.md`
- `docs/reference/specs/setup/AUDIT_MODEL.md`
- `docs/reference/specs/setup/BUILD_RULES.md`
- `docs/reference/specs/setup/CLI_JSON_SCHEMAS.md`
- `docs/reference/specs/setup/CLI_REFERENCE.md`
- `docs/reference/specs/setup/CONFORMANCE.md`
- `docs/reference/specs/setup/DEFAULTS_AND_FLAGS.md`
- `docs/reference/specs/setup/DEPRECATION_PLAN.md`
- `docs/reference/specs/setup/ERROR_TAXONOMY.md`
- `docs/reference/specs/setup/EXTENSION_POLICY.md`
- `docs/reference/specs/setup/FAILPOINTS.md`
- `docs/reference/specs/setup/FRONTEND_CONTRACT.md`
- `docs/reference/specs/setup/FUTURE_BACKLOG.md`
- `docs/reference/specs/setup/HANDOFF_SNAPSHOT.md`
- `docs/reference/specs/setup/IDE_WORKFLOWS.md`
- `docs/reference/specs/setup/LEGACY_STATE_IMPORT.md`
- `docs/reference/specs/setup/LINUX_DEB_WRAPPER.md`
- `docs/reference/specs/setup/LINUX_RPM_WRAPPER.md`
- `docs/reference/specs/setup/MACOS_PKG_WRAPPER.md`
- `docs/reference/specs/setup/OPERATIONS_QUICKSTART.md`
- `docs/reference/specs/setup/OPERATOR_TOOLS.md`
- `docs/reference/specs/setup/OWNERSHIP_MODEL.md`
- `docs/reference/specs/setup/PACKAGING_DEFAULTS.md`
- `docs/reference/specs/setup/PARITY_WITH_LAUNCHER.md`
- `docs/reference/specs/setup/PLANNING_RULES.md`
- `docs/reference/specs/setup/README.md`
- `docs/reference/specs/setup/READ_ONLY_LOCK.md`
- `docs/reference/specs/setup/RECOVERY_PLAYBOOK.md`
- `docs/reference/specs/setup/REPRODUCIBILITY_GUARANTEES.md`
- `docs/reference/specs/setup/REPRODUCIBLE_BUILDS.md`
- `docs/reference/specs/setup/SCHEMA_FREEZE_V1.md`
- `docs/reference/specs/setup/SECURITY_MODEL.md`
- `docs/reference/specs/setup/SERVICES_ERRORS.md`
- `docs/reference/specs/setup/SERVICES_FACADES.md`
- `docs/reference/specs/setup/SETUP_LINUX.md`
- `docs/reference/specs/setup/SETUP_MACOS.md`
- `docs/reference/specs/setup/SETUP_RETRO.md`
- `docs/reference/specs/setup/SETUP_WINDOWS.md`
- `docs/reference/specs/setup/SPLAT_LIFECYCLE.md`
- `docs/reference/specs/setup/SPLAT_REGISTRY.md`
- `docs/reference/specs/setup/STATE_EVOLUTION.md`
- `docs/reference/specs/setup/STATUS_SR1.md`
- `docs/reference/specs/setup/STATUS_SR10.md`
- `docs/reference/specs/setup/STATUS_SR11.md`
- `docs/reference/specs/setup/STATUS_SR2.md`
- `docs/reference/specs/setup/STATUS_SR3.md`
- `docs/reference/specs/setup/STATUS_SR4.md`
- `docs/reference/specs/setup/STATUS_SR5.md`
- `docs/reference/specs/setup/STATUS_SR6.md`
- `docs/reference/specs/setup/STATUS_SR7.md`
- `docs/reference/specs/setup/STATUS_SR8.md`
- `docs/reference/specs/setup/STATUS_SR9.md`
- `docs/reference/specs/setup/STEAM_PROVIDER.md`
- `docs/reference/specs/setup/TLV_INSTALLED_STATE.md`
- `docs/reference/specs/setup/TLV_INSTALL_MANIFEST.md`
- `docs/reference/specs/setup/TLV_INSTALL_PLAN.md`
- `docs/reference/specs/setup/TLV_INSTALL_REQUEST.md`
- `docs/reference/specs/setup/TLV_JOB_JOURNAL.md`
- `docs/reference/specs/setup/TLV_SETUP_AUDIT.md`
- `docs/reference/specs/setup/TLV_TXN_JOURNAL.md`
- `docs/reference/specs/setup/TRANSACTIONS.md`
- `docs/reference/specs/setup/TROUBLESHOOTING.md`
- `docs/reference/specs/setup/TUI_REFERENCE.md`
- `docs/reference/specs/setup/UI_CONTRACT_MAPPING.md`
- `docs/reference/specs/setup/WINDOWS_MSI_WRAPPER.md`
- `docs/architecture/system/INTERFACE_AND_INVARIANT_RULES.md`
- `docs/architecture/system/MACROCAPSULE_BEHAVIOR_MODEL.md`
- `docs/architecture/system/SYSTEM_CERTIFICATION_MODEL.md`
- `docs/architecture/system/SYSTEM_COMPOSITION_CONSTITUTION.md`
- `docs/architecture/system/SYSTEM_TEMPLATES.md`
- `docs/architecture/system/SYSTEM_TIER_AND_ROI_POLICY.md`
- `docs/testing/README.md`
- `docs/testing/xstack_profiles.md`
- `docs/domains/thermal/COOLING_AND_AMBIENT_MODEL.md`
- `docs/domains/thermal/FIRE_AND_RUNAWAY_MODEL.md`
- `docs/domains/thermal/LOSS_TO_HEAT_CONVENTION.md`
- `docs/domains/thermal/PHASE_CHANGE_AND_CURING.md`
- `docs/domains/thermal/THERMAL_CONSTITUTION.md`
- `docs/engine/time/BATCHING_AND_SUBSTEPPING.md`
- `docs/engine/time/BRANCHING_TIMELINES.md`
- `docs/engine/time/DRIFT_AND_SYNC_POLICY.md`
- `docs/engine/time/SHARD_TIME_ALIGNMENT.md`
- `docs/engine/time/TEMPORAL_SEMANTICS_CONSTITUTION.md`
- `docs/engine/time/TIME_ANCHOR_MODEL.md`
- `docs/development/tools/AGENT_INSPECTOR.md`
- `docs/development/tools/CACHE_POLICY.md`
- `docs/development/tools/DETERMINISM_TOOLS.md`
- `docs/development/tools/HISTORY_VIEWER.md`
- `docs/development/tools/REFINEMENT_RUNNER.md`
- `docs/development/tools/REPLAY_SYSTEM.md`
- `docs/development/tools/TOOLING_OVERVIEW.md`
- `docs/development/tools/TOOL_UI_GUIDELINES.md`
- `docs/development/tools/VALIDATION.md`
- `docs/development/tools/WORLDGEN_TOOLING.md`
- `docs/development/tools/WORLD_INSPECTOR.md`
- `docs/runtime/ui/CLIENT_MENU_GUIDE.md`
- `docs/runtime/ui/CLIENT_OUT_OF_GAME_SCOPE.md`
- `docs/runtime/ui/CLI_CANON.md`
- `docs/runtime/ui/CLI_TUI_GUI_PARITY.md`
- `docs/runtime/ui/CONSOLE_AND_DEBUG.md`
- `docs/runtime/ui/DEBUG_AND_INSPECT.md`
- `docs/runtime/ui/FREECAM_MODES.md`
- `docs/runtime/ui/HUD_COMPOSITION.md`
- `docs/runtime/ui/LAUNCHER_WALKTHROUGH.md`
- `docs/runtime/ui/LOCALIZATION_MODEL.md`
- `docs/runtime/ui/OBSERVATION_AND_INSPECTION.md`
- `docs/runtime/ui/ONBOARDING_GUIDE.md`
- `docs/runtime/ui/PRODUCT_SHELL_OVERVIEW.md`
- `docs/runtime/ui/README.md`
- `docs/runtime/ui/RENDERING_EPISTEMICS.md`
- `docs/runtime/ui/SETTINGS_GUIDE.md`
- `docs/runtime/ui/SHARING_UX.md`
- `docs/runtime/ui/UI_FORBIDDEN_BEHAVIORS.md`
- `docs/runtime/ui/UI_PHILOSOPHY.md`
- `docs/runtime/ui/UI_PIPELINE_AND_WORKSPACES.md`
- `docs/runtime/ui/UX_OVERVIEW.md`
- `docs/runtime/ui/UX_RULES.md`
- `docs/runtime/ui/WORLD_CREATION_FLOW.md`
- `docs/runtime/ui/WORLD_CREATION_UI.md`
- `docs/runtime/ui/ZERO_ASSET_GUI.md`
- `docs/domains/universe/UNIVERSE_IDENTITY_STATE.md`
- `docs/runtime/render/visualization/OBSERVATION_MODEL.md`
- `docs/runtime/render/visualization/VISUALIZATION_CONTRACT.md`
- `docs/domains/worldgen/AI_AUTONOMY_BASELINE.md`
- `docs/domains/worldgen/ANIMALS_BASELINE.md`
- `docs/domains/worldgen/BUILDING_AND_DESTRUCTION_BASELINE.md`
- `docs/domains/worldgen/BUILTIN_TEMPLATES.md`
- `docs/domains/worldgen/CIVILIZATIONS_AND_HISTORY_BASELINE.md`
- `docs/domains/worldgen/CLIMATE_AND_BIOMES_BASELINE.md`
- `docs/domains/worldgen/CLIMATE_BODY_SHAPES.md`
- `docs/domains/worldgen/CONFLICT_BASELINE.md`
- `docs/domains/worldgen/CRAFTING_BASELINE.md`
- `docs/domains/worldgen/EARTH_MATERIAL_SURFACE_PROXY.md`
- `docs/domains/worldgen/EDUCATION_AND_LEARNING_BASELINE.md`
- `docs/domains/worldgen/ENERGY_BASELINE.md`
- `docs/domains/worldgen/FLUIDS_AND_CONTAINMENT_BASELINE.md`
- `docs/domains/worldgen/GALAXY_COMPACT_OBJECT_STUBS.md`
- `docs/domains/worldgen/GALAXY_METADATA_PROXIES.md`
- `docs/domains/worldgen/GEOLOGY_AND_RESOURCES_BASELINE.md`
- `docs/domains/worldgen/GEOLOGY_STORAGE.md`
- `docs/domains/worldgen/HAZARDS_AND_SAFETY_BASELINE.md`
- `docs/domains/worldgen/HEAT_AND_FAILURE_BASELINE.md`
- `docs/domains/worldgen/INSURANCE_AND_ACCOUNTABILITY_BASELINE.md`
- `docs/domains/worldgen/LAW_AND_GOVERNANCE_BASELINE.md`
- `docs/domains/worldgen/LOGISTICS_AND_MARKETS_BASELINE.md`
- `docs/domains/worldgen/MICRO_DETAIL_GUARANTEE.md`
- `docs/domains/worldgen/MINING_AND_EXTRACTION_BASELINE.md`
- `docs/domains/worldgen/MODEL_REGISTRY.md`
- `docs/domains/worldgen/NETWORKS_AND_DATA_BASELINE.md`
- `docs/domains/worldgen/OBJECTIVE_VS_SUBJECTIVE_REALITY.md`
- `docs/domains/worldgen/REALISM_IS_CONTENT.md`
- `docs/domains/worldgen/REFINEMENT_CONTRACT.md`
- `docs/domains/worldgen/REFINEMENT_LATTICE.md`
- `docs/domains/worldgen/STANDARDS_AND_TOOLCHAINS_BASELINE.md`
- `docs/domains/worldgen/TEMPLATE_REGISTRY.md`
- `docs/domains/worldgen/TERRAIN_GEOMETRY_BASELINE.md`
- `docs/domains/worldgen/TERRAIN_STORAGE_STRATEGY.md`
- `docs/domains/worldgen/TRAVEL_AND_TRANSPORT_BASELINE.md`
- `docs/domains/worldgen/TRUST_AND_REPUTATION_BASELINE.md`
- `docs/domains/worldgen/VEGETATION_BASELINE.md`
- `docs/domains/worldgen/WEATHER_BASELINE.md`
- `docs/domains/worldgen/WORLDGEN_OVERVIEW.md`

#### HISTORICAL
- `docs/archive/README.md`
- `docs/archive/app/APR1_RUNTIME_AUDIT.md`
- `docs/archive/app/APR1_TESTX_COMPLIANCE.md`
- `docs/archive/app/APR2_TESTX_COMPLIANCE.md`
- `docs/archive/app/APR3_TESTX_COMPLIANCE.md`
- `docs/archive/app/APR3_UI_MODE_AUDIT.md`
- `docs/archive/app/APR4_ENGINE_GAME_INTERFACE_INVENTORY.md`
- `docs/archive/app/APR4_TESTX_COMPLIANCE.md`
- `docs/archive/architecture/ARCH_GLOSSARY.md`
- `docs/archive/architecture/COMPATIBILITY_PHILOSOPHY.md`
- `docs/archive/architecture/DISTRIBUTED_SIM_MODEL.md`
- `docs/archive/architecture/INVARIANTS.md`
- `docs/archive/architecture/MENTAL_MODEL.md`
- `docs/archive/architecture/NON_GOALS.md`
- `docs/archive/architecture/TERMINOLOGY.md`
- `docs/archive/architecture/VISITABILITY_AND_REALITY.md`
- `docs/archive/build/APR5_BUILD_INVENTORY.md`
- `docs/archive/ci/COREDATA_CONSISTENCY_REPORT.md`
- `docs/archive/ci/DOCS_VALIDATION_REPORT.md`
- `docs/archive/ci/PHASE1_AUDIT_REPORT.md`
- `docs/archive/ci/PHASE1_ENFORCEMENT_SUMMARY.md`
- `docs/archive/ci/PHASE2_5_AUDIT_REPORT.md`
- `docs/archive/ci/PHASE2_5_FIXLIST.md`
- `docs/archive/ci/PHASE6_AUDIT_REPORT.md`
- `docs/archive/ci/PHASE6_READINESS.md`
- `docs/archive/ci/PHASE6_SEALED.md`
- `docs/archive/guides/LAUNCHER_AUDIT.md`
- `docs/archive/platform/APR2_EXTENSION_AUDIT.md`
- `docs/archive/prompts/post_canon_sequence_L1_L4_IVRH.txt`
- `docs/archive/repox/APRX_INTEGRATION_HOOKS.md`
- `docs/archive/repox/APRX_INVENTORY.md`
- `docs/archive/specs/TOOL_PACK.md`
- `docs/archive/stray_root_docs/CIV0_POPULATION_GENESIS.md`
- `docs/archive/stray_root_docs/CIV0a_SURVIVAL_LOOP.md`
- `docs/archive/stray_root_docs/CIV1_CITIES_INFRA.md`
- `docs/archive/stray_root_docs/CIV2_GOVERNANCE.md`
- `docs/archive/stray_root_docs/CIV3_KNOWLEDGE_TECH.md`
- `docs/archive/stray_root_docs/CIV4_SCALE_AND_LOGISTICS.md`
- `docs/archive/stray_root_docs/CI_ENFORCEMENT_MATRIX.md`
- `docs/archive/stray_root_docs/DETERMINISM_TEST_MATRIX.md`
- `docs/archive/stray_root_docs/GOVERNANCE.md`
- `docs/archive/stray_root_docs/MODDING.md`
- `docs/archive/stray_root_docs/OFFLINE_AND_LOCAL_MP.md`
- `docs/archive/stray_root_docs/PERF_BUDGETS.md`
- `docs/archive/stray_root_docs/VALIDATION_AND_GOVERNANCE.md`
