Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: audit
Task: API-ABI-AIDE-SYNTHESIS-01

# API/ABI/AIDE Synthesis

## Verdict

The next maturity layer is not another directory move. It is public-surface
governance: a machine-readable answer to what is public, what is internal, what
is stable, what may be replaced, and which tests prove the promise.

The repository already contains most of the doctrine needed for a reusable
engine-grade platform, but the ideas are scattered across current docs,
superseded docs, archived audits, AIDE policy files, RepoX/TestX doctrine, and
naming/layout contracts.

The synthesis target should be:

```text
Domino is a reusable deterministic substrate with stable C89 contracts.
Dominium is a product/game layer built on top of Domino.
Every subsystem crosses boundaries through versioned, testable,
capability-negotiated interfaces.
```

That implies a formal public-surface and API/ABI/module governance layer
covering:

- public surface registry
- public/private API tiering
- C89/C++98 public-header discipline
- opaque handles, allocators, ownership, and lifetimes
- stable error and refusal payloads
- capability negotiation and explicit degradation
- deterministic serialization, replay, and migration
- dependency-direction and include-boundary enforcement
- schema/protocol/package compatibility
- compatibility corpora for old valid and invalid artifacts
- replacement protocol for swapping implementations behind the same contract
- assurance levels for trust-bearing surfaces only
- public-header consumer tests
- AIDE/RepoX/TestX/AuditX enforcement wiring

## Evidence Scope

This synthesis was grounded in the current tracked repo plus archived and
superseded docs.

- Starting commit: 729c0e6db27b67edb7b2825727d108188825252b
- Source scan: tracked `docs/` tree
- Docs files scanned: 4,206
- High-signal docs by filename/topic: 1,234
- Local evidence: `.dominium.local/api-abi-doc-synthesis-01/`
- AIDE preflight: `doctor` PASS, `validate` PASS with existing review-packet warning

Generated evidence is intentionally local and ignored. The evidence includes
tracked doc lists, high-signal doc lists, current/archived doctrine grep
extracts, AIDE policy hits, and enforcement-surface file inventories.

## Authority Reading

Current authority is not evenly distributed:

- `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md` are binding.
- `AGENTS.md` governs agent execution and validation discipline.
- Current `docs/architecture/**`, `docs/engine/**`, `docs/build/**`,
  `docs/compatibility/**`, `docs/governance/**`, `docs/repo/**`, and
  `contracts/**` provide live scoped doctrine where not superseded by stronger
  sources.
- `docs/archive/**` is useful evidence and history, not live authority.
- Generated reports are evidence unless explicitly promoted by a stronger
  contract.

The synthesis below promotes ideas only when they agree with current canon and
active structural authority.

## External Benchmarks As Advisory Patterns

External systems reinforce the same conclusion, but they are advisory examples,
not Dominium authority.

- Linux is a useful boundary lesson: the user/kernel interface is treated as
  stable while in-kernel implementation interfaces remain free to change. For
  Dominium, this maps to stable public surfaces and replaceable internals.
  Source: [Linux stable API rationale](https://www.kernel.org/doc/Documentation/process/stable-api-nonsense.rst).
- SQLite is the artifact-compatibility lesson: the database file format is
  stable, cross-platform, and backwards-compatible across SQLite 3 releases.
  For Dominium, save/replay/pack/profile/lockfile compatibility must be proven
  by corpus, not asserted by intent. Source: [SQLite single-file database](https://sqlite.org/onefile.html).
- PostgreSQL extensions are the package-lifecycle lesson: related objects are
  collected under an extension with control files, install/update scripts,
  dependencies, ownership, and security considerations. For Dominium, packs,
  modules, and future plugins need governed manifests, created-object
  inventories, upgrade rules, rollback/uninstall semantics, and trust labels.
  Source: [PostgreSQL extension packaging](https://www.postgresql.org/docs/current/extend-extensions.html).
- Unreal modular game features are the optional-feature lesson: the core game
  can remain unaware of feature plugins and avoid direct dependencies on new
  content. For Dominium, product shells and core runtime must consume declared
  capabilities rather than hardcoding domain/module knowledge. Source:
  [Unreal modular game features](https://www.unrealengine.com/blog/modular-game-features-in-ue5-plug-n-play-the-unreal-way?lang=en-US).
- Godot GDExtension is the native-extension caution: native runtime extension
  uses shared libraries, a C function interface, an extension API descriptor,
  and a loadable extension file. For Dominium, native extension should come
  after ABI, trust, determinism, replay, and capability/refusal law are already
  proven. Source: [Godot GDExtension](https://docs.godotengine.org/en/stable/tutorials/scripting/gdextension/what_is_gdextension.html).
- .NET compatibility rules are the change-classification lesson: public-surface
  changes need explicit allowed/disallowed/judgment categories because source,
  binary, behavioral, and serialization compatibility differ. For Dominium,
  every public surface change needs a compatibility class before merge. Source:
  [.NET compatibility change rules](https://learn.microsoft.com/en-us/dotnet/core/compatibility/library-change-rules).
- Windows driver interfaces are the versioned-structure lesson: interface
  structures carry size/version/reference semantics and requesters query for a
  supported interface rather than assuming one. For Dominium, provider tables
  should use size/version fields, explicit lifetime hooks, and capability
  queries. Sources: [Windows versioned interfaces](https://learn.microsoft.com/en-us/windows-hardware/drivers/network/versioned-interfaces)
  and [driver-defined interfaces](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/using-driver-defined-interfaces).
- COM is the binary-boundary lesson: reusable components communicate through
  strongly typed interfaces with identity, lifetime, discovery, and deployment
  mechanisms. Dominium should borrow the discipline, not the full COM model.
  Source: [COM technical overview](https://learn.microsoft.com/en-us/windows/win32/com/com-technical-overview).

## Core Doctrine To Keep

### 0. Freeze Boundaries, Not Files

The strongest synthesis is:

```text
Freeze contracts.
Replace implementations.
Preserve data.
Verify behavior.
```

Do not promise that every file, private struct, private helper, directory, or
internal function is stable. Promise that released public surfaces are
registered, versioned, tested, and honestly migrated or refused.

This gives the project freedom to rewrite internals while preserving public
behavior and artifact identity.

### 1. Domino/Dominium Split

Current canon already says:

- Domino is the deterministic universe simulation core in C89.
- Dominium is the C++98 gameplay/product layer atop Domino.
- Engine mechanisms are deterministic and reusable.
- Game meaning, law, rules, and domains are product-specific unless explicitly
  lifted into reusable substrate.

The stronger operational rule is:

```text
engine/    = Domino substrate, product-agnostic, zero-asset boot
runtime/   = reusable host/service/backend adapters, no game truth
game/      = Dominium law, rule, process meaning, and domain implementation
apps/      = thin product composition shells
content/   = authored payloads, no executable truth mutation
contracts/ = machine-readable law, ABI/protocol/schema/package identities
tools/     = validators, generators, proof tooling, no runtime dependency
```

This should become machine-checkable, not just prose.

### 2. Public API Surfaces Are Contracts

Current docs already converge on:

- public engine headers under `engine/include/domino/**`
- public game headers under `game/include/dominium/**`
- public headers must be C89 and C++98 parseable
- public ABI is flat, versioned, C-only, and free of STL/templates/exceptions
- concrete layouts should stay private behind opaque handles
- public interfaces must define error handling, allocator, thread-safety,
  determinism, ownership, and lifetime constraints
- public headers must not include platform, renderer, OS, or private module
  headers unless they are explicitly runtime/platform public surfaces

This should be captured as a first-class API/ABI contract, not left spread
across `docs/engine/API_SPINE.md`, `SPEC_ABI_TEMPLATES.md`, style docs, and
build-boundary notes.

The broader rule is that public API is only one public surface class. Other
surface classes include ABI, schemas, protocols, commands, views, events,
refusals, package formats, save/replay formats, capability IDs, registry IDs,
release manifests, and compatibility corpora.

### 3. ABI Boundary Pattern

The archived/current ABI template material is still excellent:

```text
C ABI only
POD-only ABI-visible structs
versioned and size-stamped structs
opaque handles for non-trivial lifetime
function tables for plugin/backend boundaries
query_interface-style discovery where needed
no inline behavior required for ABI semantics
native handles only through explicit optional extensions
```

This should be retained and generalized for render, platform, package, storage,
network, UI, serialization, and future plugins.

### 4. Determinism As Kernel Law

The constitution, engine primitives, determinism policies, RNG docs, and XStack
doctrine agree:

- no wall-clock, filesystem order, pointer order, hash-map order, or thread
  completion order in authoritative outcomes
- named RNG streams only
- deterministic reductions only
- replay/hash partitions prove authoritative equivalence
- batching and parallelism must be equivalent to stepwise execution
- generated proof artifacts must have deterministic ordering and stable hashing

This belongs in the same API/ABI governance layer because every public boundary
must say whether it participates in authoritative determinism, presentation,
tooling, diagnostics, or non-authoritative host integration.

### 5. Capability Negotiation, Degrade Ladders, And Refusal

Current compatibility docs and RepoX rule descriptions already define the right
model:

- endpoint descriptors are deterministic and offline-emittable
- negotiation is mandatory before capability-bearing connections become active
- unknown capabilities are filtered or ignored deterministically
- degrade ladders are explicit, ordered, and recorded
- silent downgrade and silent feature hiding are forbidden
- refusal payloads are deterministic, replayable, and use stable codes

The platform should apply this model beyond client/server connections:

- render backend selection
- platform services
- storage and package loading
- save/replay compatibility
- UI/CLI/TUI/workbench command surfaces
- mod/content pack capabilities
- tooling and generated artifact contracts

### 6. Schema, Protocol, And Artifact Compatibility

The strongest current rule is:

```text
No authoritative format may rely on implicit interpretation.
```

Every persistent or protocol artifact should declare:

- schema id/version/stability
- format version where interpretation can change
- semantic contract bundle hash where applicable
- compatibility range
- migration policy
- unknown-field policy
- explicit default policy
- canonical serialization and hash policy
- refusal behavior when migration or compatibility cannot be proven

Old docs that say version numbers alone are insufficient should be kept as a
useful idea: compatibility is capability negotiation plus schema/protocol
contract compatibility, not semver comparison by itself.

### 7. AIDE, RepoX, TestX, AuditX Roles

The current governance stack has the right separation:

- AIDE: planning, context, evidence, review packets, controlled refactor maps,
  golden tasks, and no-call/no-apply policy surfaces.
- RepoX: static structural and policy enforcement.
- TestX: executable behavior proof and deterministic regression locks.
- AuditX: semantic drift/risk detection, non-gating until promoted.
- XStack: deterministic incremental gate planning, grouping, caching, and
  artifact classification.

This division should be preserved. Do not make AIDE a runtime oracle or an
autonomous source rewriter. Use AIDE to compile evidence and task packets, then
promote stable checks into RepoX/TestX.

### 8. Floors Before Features

The repo should grow from proofable floors, not UI-first feature piles:

```text
bare substrate floor
command/result/refusal floor
package/extension floor
presentation floor
Workbench production floor
```

Workbench should be treated as the visual and agentic production environment
for Domino/Dominium, not as authority. It should build on command, validation,
package, presentation, and evidence services that already work headlessly.

The first Workbench vertical slice should prove one command end to end:

```text
tool command -> service -> typed result/refusal -> CLI/headless output
-> TUI/status projection -> rendered dashboard -> evidence packet
```

Then Workbench modules can grow without bypassing command contracts.

The sequencing rule is:

```text
command spine first
Workbench GUI second
domain/product acceleration third
```

## Ideas To Improve

### 1. Public Surface Registry Is The Hard Mechanism

The highest-value missing mechanism is a machine-readable public surface
registry.

It should answer:

```text
what is public?
what is internal?
what is frozen?
what is stable?
what is provisional?
what is deprecated?
what is retired?
what test proves it?
who owns it?
```

Each public surface entry should declare:

```text
id
kind
path
owner
stability
version
api tier
allowed dependencies
forbidden dependencies
compatibility tests
conformance tests
deprecation state
replacement target
```

Surface classes should include:

```text
frozen_abi
stable_api
stable_data_contract
stable_command_contract
stable_protocol
stable_view_contract
stable_refusal_contract
provisional
internal
experimental
deprecated
retired
```

Without this registry, "stable API" remains social policy. With it, AIDE can
compile task context, RepoX can block static violations, TestX can require
behavioral proof, and AuditX can report drift before promotion.

### 2. Naming Prefixes Need A Single Current Rule

Docs disagree historically between:

- `d_*`, `dg_*`, `dom_*`, `dsys_*` style from older C code style docs
- `domino_*` and `dominium_*` as clearer substrate/product prefixes
- older `dom_*` APIs in archived interface inventories

Recommendation:

- keep existing prefixes where already ABI/public and stable
- define a forward rule:
  - `domino_*` for reusable substrate APIs
  - `dominium_*` for product/game APIs
  - `domino_runtime_*`, `domino_render_*`, `domino_platform_*`,
    `domino_package_*` for subsystem families
- create compatibility guidance for legacy `dom_*`, `d_*`, `dg_*`, and
  `dsys_*` symbols instead of mass-renaming them
- enforce no new unclassified public prefixes

Do not break ABI just to normalize names.

### 3. Public Header Checks Are Too Narrow

`scripts/verify_abi_boundaries.py` currently blocks obvious STL/C++ tokens in
public headers. That is valuable but incomplete.

Improve with a dedicated public-header validator that checks:

- C89 parse
- C++98 parse
- self-contained include
- no private-root includes
- no OS/platform headers outside runtime/platform public headers
- no STL/templates/exceptions in C-facing public headers
- no exposed mutable global variables
- no concrete public structs unless explicitly `layout_public=true`
- every ABI-visible struct has version/size fields where required
- every public function uses allowed result/ownership conventions
- every public header maps to an API tier and owner

### 4. Dependency Direction Needs A Contract

The docs already state dependency direction, but enforcement is split across
CMake, include sanity, ABI checks, RepoX, and historical tests.

Create a machine-readable dependency-direction contract that covers:

```text
apps -> runtime/game/engine as allowed by product role
game -> engine public API only
runtime -> engine public API, contracts, external adapters
engine -> contracts/abi/schema only where explicitly allowed, never game/apps
tools -> may inspect/generate/validate, never become runtime dependency
contracts/content/docs -> no executable dependency
```

Then make CMake, include, source import, and generated artifact checks consume
the same contract.

### 5. Module README/Manifest Contract Is Missing

The repo has module layout grammar, but reusable modules do not uniformly
declare:

- owner
- tier
- public API path
- private implementation path
- allowed dependencies
- deterministic posture
- allocator/error/refusal conventions
- capability IDs
- schemas/protocols consumed
- tests/proofs
- replacement/backends supported

Add a lightweight module manifest or README schema. Do not use it to block
everything immediately; start as AuditX advisory, promote to RepoX for new
modules, then ratchet existing modules.

### 6. Replacement Protocol Is Missing

If entire implementations and directories should be replaceable, the repo needs
a replacement protocol:

1. identify the public contract
2. build old and new implementations behind the same boundary
3. run conformance tests
4. run save/replay/pack/protocol compatibility tests where applicable
5. compare deterministic proof hashes where applicable
6. switch provider/implementation through a declared selection mechanism
7. retire old implementation only after evidence and deprecation conditions

This prevents rewrites from becoming semantic drift.

### 7. Compatibility Corpus Is Missing

Backward compatibility should be a permanent corpus, not intent. Retain fixtures
for:

- old valid saves
- old invalid saves
- old replays
- old packs
- old lockfiles
- old negotiation records
- old registry bundles
- old CLI outputs
- old bugreport bundles
- old generated manifests

Every release should prove:

```text
old valid artifacts load or migrate
old invalid artifacts still refuse with stable reason
old replays reproduce or refuse through declared incompatibility
```

### 8. Assurance Levels Should Be Project-Native

The standards-style docs and feedback are useful only if kept lightweight. Use
assurance levels for trust-bearing surfaces, not for every gameplay idea or UI
experiment.

Suggested internal levels:

| Level | Use | Examples |
| --- | --- | --- |
| DIL-0 | exploratory | prototypes, throwaway experiments |
| DIL-1 | ordinary | most gameplay/UI iteration |
| DIL-2 | product | shipped product behavior |
| DIL-3 | trust-bearing | save/load, deterministic state, law/capability checks, pack parsing |
| DIL-4 | authority/signing | release signing, updater, multiplayer authority, trust roots |
| DIL-5 | external-impacting | anything with legal/security/operator impact |

Do not turn this into certification cosplay. Use it to scale evidence and
review to risk.

### 9. Test Tiers Need A Performance Contract

The reconciliation full CTest run took about 54 minutes and failed broad
FULL-gate debt. Current `GATE_THROUGHPUT_POLICY.md` already says FAST is the
default and FULL/FULL_ALL are explicit. The practical improvement is to make
that policy enforceable:

- FAST: under 10 minutes, default for normal development
- STRICT: bounded, impact-driven, required for governance/API/ABI/schema changes
- FULL: rare, release/ultra-certainty only
- FULL_ALL: explicit environment variable or command only

Direct `ctest` use should be wrapped by AIDE/XStack gate policy unless the task
explicitly asks for exhaustive proof.

## Ideas To Abandon Or Quarantine

### 1. New Top-Level Roots

Do not add `sdk/`, `examples/`, `src/`, `source/`, `lib/`, `common/`, or
similar roots as part of API/ABI work. Existing naming doctrine allows only
future optional roots after contract update. API/ABI governance can live under
current roots:

- `contracts/abi/`
- `contracts/repo/`
- `docs/architecture/`
- `docs/development/`
- `tools/validators/abi/`
- `tests/contract/public_headers/`

### 2. Big-Bang Symbol Renames

Do not mass-rename public C symbols to match a preferred prefix. Public names
are identity/ABI surfaces. New naming rules should be forward-looking, with
explicit deprecation and compatibility ledgers for old symbols.

### 3. Silent Compatibility Shims

Archived shim policy has the right warning: shims must be deterministic,
explicit, warned, governed, and sunset-bound. Do not create broad compatibility
aliases for old roots, old symbols, old schema IDs, or old tool commands.

### 4. AIDE As Runtime Authority

AIDE should not mutate source automatically, choose architecture winners,
replace RepoX/TestX, call providers by default, or become runtime/product
dependency. Current AIDE policy is advisory/evidence/review oriented. Keep it
that way.

### 5. Version Numbers As Compatibility Truth

Semver alone is insufficient. Compatibility must be proven by declared
capabilities, schema/protocol constraints, migration policies, and deterministic
proof artifacts.

### 6. Full CTest As Default Gate

Full CTest is useful but too slow for normal work. Treat it as release/full
confidence proof only. The normal path should be AIDE doctor/validate, RepoX,
TestX impacted groups, focused validators, CMake build, and smoke tests.

### 7. Native Plugins Too Early

Do not make native third-party plugins the first extension target. Native
plugins complicate determinism, security, portability, replay, ABI support, and
operator trust.

Start with:

- data-only packs
- built-in providers behind registered interfaces
- external process adapters
- command contracts
- strict capability/refusal law

Native plugins can come later after ABI, sandbox, trust, replay, and
compatibility corpus rules are proven.

### 8. Ungoverned Mods As Arbitrary Files

Do not let mods become arbitrary directories of files with implicit authority.
Modding needs a trust ladder:

```text
data-only pack
schema-validated pack
scriptless rule pack
Workbench-authored module
external process adapter
trusted built-in provider
trusted native provider
signed native provider
```

Each rung must declare different permissions, capabilities, validation,
determinism obligations, replay impact, and install/update/removal rules.

## Recommended Canonical Artifacts

Create these across `PUBLIC-SURFACE-REGISTRY-01`, `API-ABI-CANON-01`,
`REPLACEMENT-PROTOCOL-01`, and `COMPATIBILITY-CORPUS-01`:

```text
contracts/public_surface/public_surface.contract.toml
contracts/public_surface/public_surface.schema.json
contracts/public_surface/abi_surface.contract.toml
contracts/public_surface/schema_surface.contract.toml
contracts/public_surface/protocol_surface.contract.toml
contracts/public_surface/command_surface.contract.toml
contracts/abi/c_api.contract.toml
contracts/repo/api_tiers.contract.toml
contracts/repo/dependency_directions.contract.toml
contracts/repo/symbol_prefixes.contract.toml
contracts/repo/module_contract.schema.json
contracts/replacement/replacement_protocol.contract.toml
contracts/assurance/integrity_level.schema.json
contracts/capability/capability_law.contract.toml
contracts/refusal/refusal_law.contract.toml
contracts/provider/provider_model.contract.toml
contracts/modding/trust_ladder.contract.toml
docs/architecture/api_abi_canon.md
docs/architecture/public_surface_registry.md
docs/architecture/replacement_protocol.md
docs/architecture/capability_refusal_law.md
docs/development/c89_coding_standard.md
docs/development/module_api_standard.md
docs/contracts/artifact_compatibility_policy.md
docs/contracts/provider_model.md
docs/assurance/assurance_profile.md
docs/modding/trust_model.md
docs/repo/symbol_naming.md
tools/validators/abi/check_public_headers.py
tools/validators/repo/check_public_surface.py
tools/validators/repo/check_dependency_directions.py
tools/validators/repo/check_symbol_prefixes.py
tools/validators/repo/check_module_contracts.py
tools/validators/compat/check_artifact_corpus.py
tools/validators/assurance/check_integrity_level.py
tools/validators/modding/check_mod_trust_ladder.py
tests/contract/public_headers/
tests/fixtures/compatibility_corpus/
```

Do not make these all hard blockers on day one. Use staged enforcement:

1. source contract and docs
2. advisory AuditX findings
3. RepoX for new code and public API surfaces
4. TestX public-header consumer tests
5. ratchet existing violations by owner
6. promote strict blockers only after evidence is stable

## Proposed API Tiers

| Tier | Meaning | Examples | Enforcement |
| --- | --- | --- | --- |
| Tier 0 | private product implementation | `apps/**`, product glue, Dominium content-specific flows | no external stability; boundary checks only |
| Tier 1 | reusable inside Dominium repo | selected `game/**`, runtime service internals | internal contract, may break with repo-wide migration |
| Tier 2 | reusable by another Domino game | `runtime/shell`, package/profile/session surfaces | documented API, compatibility policy |
| Tier 3 | reusable by another engine/tool project | `engine/time`, `engine/replay`, `runtime/render/software`, validators | stable public C/API or CLI contract |
| Tier 4 | external SDK/API | installed headers, plugins, public descriptors | ABI/version/deprecation strictness |

Every public header, product descriptor, schema family, protocol, command
surface, and package contract should declare its tier. Unknown tier defaults to
private, not public.

## C API/ABI Rules

Baseline rules:

- C ABI only across plugin/backend/module binary boundaries.
- Public C headers must be C89 and C++98 parseable.
- No STL, templates, exceptions, RTTI, C++ ownership types, or platform-native
  types in C public ABI.
- Use project integer/type aliases and compile probes for size assumptions.
- Prefer opaque handles for non-trivial lifetimes.
- Every ABI-visible struct crossing replaceable boundaries starts with
  `abi_version` and `struct_size` or an equivalent contract-approved header.
- Every public function documents ownership, lifetime, allocator, thread-safety,
  error/refusal behavior, and determinism posture.
- No hidden global mutable state in public API behavior.
- No raw struct serialization. Persistent formats use canonical serializers.
- Native handles are optional extensions, not baseline contract fields.

## Error, Refusal, And Diagnostics

Unify C result codes and product refusal codes:

- C APIs return stable `domino_result_t`-style codes.
- Rich diagnostics are explicit output objects or diagnostic sinks.
- Product/user refusals use canonical refusal payloads and stable code IDs.
- Errors/refusals must be deterministic where they affect proof or replay.
- Details must use stable identifiers where possible and avoid raw absolute
  paths unless the surface is explicitly local diagnostic output.

## Capability And Backend Pattern

For replaceable subsystems, use the same pattern:

```text
descriptor -> capability query -> negotiation -> selected backend/degrade/refusal -> proof record
```

Applicable subsystem families:

- render
- platform
- input
- audio
- network
- storage
- package/profile/save/replay
- UI backend
- command/view/event surfaces
- workbench modules
- mod/content pack features
- compression/hash/serialization providers

Backends should expose stable descriptors and function tables rather than
forcing callers to compile against implementation internals.

The provider table should be boring and ABI-governed: identifier, kind,
structure size, ABI/API version, capability query, create/destroy lifecycle,
diagnostics, conformance tests, and explicit refusal when a requested provider
or capability is unavailable.

## AIDE Enforcement Model

AIDE should enforce this through a compiler-style workflow:

### AIDE Context

- Add API/ABI doctrine to task packets when touched paths include
  `engine/include/**`, `runtime/include/**`, `game/include/**`,
  `contracts/abi/**`, `contracts/protocol/**`, CMake target files, or public
  schema/protocol/package surfaces.
- Keep context compact: link canonical docs and contracts, do not paste the
  full docs corpus.
- Add a short "public surface changed?" field to relevant task packets.

### AIDE Evidence

For API/ABI tasks, evidence packets should require:

- public header compile result
- ABI boundary validator result
- include boundary result
- dependency-direction result
- symbol-prefix result
- schema/protocol/package compatibility result where touched
- migration/refusal statement
- deterministic impact statement
- TestX proof group result

### AIDE Golden Tasks

Add golden tasks that check:

- API/ABI task packet includes required sections
- public header change without ABI evidence is flagged
- symbol prefix violation fixture fails deterministically
- hidden global state fixture is flagged
- missing allocator/lifetime docs in public API are flagged
- default/migration/refusal ambiguity in schema/protocol fixtures is flagged
- dependency-direction violation fixture is routed to RepoX/TestX
- mod trust ladder violation is flagged before native extension authority is
  granted

### AIDE Review Gates

Use AIDE review packets to stop:

- public ABI break without version/deprecation/migration plan
- schema/protocol meaning change without compatibility statement
- capability behavior change without negotiation/degrade/refusal proof
- engine depending on game/runtime/apps/product code
- tools/XStack/AIDE becoming runtime dependencies
- direct full-CTest as routine proof when FAST/STRICT scoped gates are enough

### AIDE Promotion Path

Use AuditX first for broad semantic smell detection:

- public/private ambiguity
- duplicate substrate implementations
- product logic in reusable substrate
- silent default or silent downgrade language
- stale superseded docs presented as current authority
- missing module contract docs

Promote mature checks to RepoX as static blockers. Promote behavior checks to
TestX when executable proof is needed.

## RepoX/TestX/AuditX Additions

### RepoX

Add or extend invariants:

- `INV-API-TIER-DECLARED`
- `INV-PUBLIC-HEADER-C89-CXX98`
- `INV-PUBLIC-HEADER-NO-PRIVATE-INCLUDES`
- `INV-PUBLIC-ABI-VERSIONED-SIZED`
- `INV-SYMBOL-PREFIX-STABLE`
- `INV-DEPENDENCY-DIRECTION`
- `INV-NO-HIDDEN-GLOBAL-STATE`
- `INV-NO-PRODUCT-LOGIC-IN-DOMINO`
- `INV-CAPABILITY-NEGOTIATION-REQUIRED`
- `INV-NO-SILENT-DEFAULTS-AT-BOUNDARY`
- `INV-MODULE-CONTRACT-PRESENT`

### TestX

Add focused groups:

- public-header external consumer build
- C89/C++98 public header compile
- plugin/backend ABI table fixture
- capability negotiation fixture
- explicit refusal/degrade fixture
- save/replay/schema migration fixture
- dependency-removability test for AIDE/XStack/tools from runtime build

### AuditX

Keep broad smell analysis non-gating by default:

- substrate/product leakage
- unclear module ownership
- duplicate concept implementations
- hidden singleton/service locator patterns
- product-specific identifiers inside engine/runtime reusable surfaces
- docs that present obsolete archive doctrine as current

## Programming Practices To Standardize

Use these as the "best practice" baseline:

1. Public APIs are contracts, not convenience headers.
2. Public C boundaries use opaque handles, explicit allocators, explicit result
   codes, and documented lifetimes.
3. Public ABI structs are versioned and size-stamped.
4. No public header includes private module headers.
5. No engine public header includes OS/render/platform headers unless it is a
   specifically approved runtime/platform public surface.
6. Every subsystem declares deterministic posture.
7. No authoritative path reads wall-clock, filesystem order, pointer order, or
   anonymous randomness.
8. Every schema/protocol/artifact declares version, compatibility, default,
   unknown-field, migration, and refusal policy.
9. Every optional subsystem participates in capability negotiation.
10. Every degradation or refusal is explicit, logged, and proofable.
11. Tools can inspect and generate; runtime cannot depend on tools.
12. AIDE generates evidence and review packets; it does not own runtime truth.
13. AuditX finds smells; RepoX blocks static policy violations; TestX proves
   runtime behavior.
14. FAST/STRICT gates are normal; FULL gates are rare.
15. Archived docs are evidence, not current truth.

## Immediate Next Prompt

```text
PUBLIC-SURFACE-REGISTRY-01

Task:
Create the first canonical public surface registry without broad code refactors.

Goal:
Define what is public, internal, stable, provisional, deprecated, retired, and
test-proven across APIs, ABIs, schemas, protocols, command/result/refusal
contracts, package/save/replay formats, capability IDs, registry IDs, and
release/build metadata.

Touched Paths:
contracts/public_surface/
contracts/abi/
contracts/repo/
docs/architecture/
docs/development/
docs/contracts/
docs/repo/
tools/validators/abi/
tools/validators/repo/
tests/contract/public_headers/
.aide/evals/golden-tasks/

Relevant Invariants:
docs/canon/constitution_v1.md
docs/canon/glossary_v1.md
docs/engine/API_SPINE.md
docs/engine/PRIMITIVES.md
docs/reference/specs/SPEC_ABI_TEMPLATES.md
docs/build/BOUNDARY_ENFORCEMENT.md
docs/governance/REPOX_RULESETS.md
docs/governance/TESTX_PROOF_MODEL.md
docs/governance/GATE_THROUGHPUT_POLICY.md

Contracts/Schemas:
Create contract surfaces only. Do not mutate existing ABI/schema IDs.

Validation Level:
STRICT scoped, not full CTest by default.

Expected Artifacts:
contracts/public_surface/public_surface.contract.toml
contracts/public_surface/public_surface.schema.json
contracts/public_surface/abi_surface.contract.toml
contracts/public_surface/schema_surface.contract.toml
contracts/public_surface/protocol_surface.contract.toml
contracts/public_surface/command_surface.contract.toml
contracts/abi/c_api.contract.toml
contracts/repo/api_tiers.contract.toml
contracts/repo/dependency_directions.contract.toml
contracts/repo/symbol_prefixes.contract.toml
docs/architecture/public_surface_registry.md
docs/architecture/api_abi_canon.md
docs/development/c89_coding_standard.md
docs/development/module_api_standard.md
docs/contracts/artifact_compatibility_policy.md
docs/repo/symbol_naming.md
tools/validators/repo/check_public_surface.py
tools/validators/abi/check_public_headers.py
tools/validators/repo/check_dependency_directions.py
tools/validators/repo/check_symbol_prefixes.py
tests/contract/public_headers/
.aide golden task fixtures for API/ABI task evidence

Non-Goals:
No broad symbol renames.
No directory restructure.
No ABI break.
No schema ID mutation.
No new top-level roots.
No full CTest unless explicitly requested.
```

Follow-up prompts:

```text
API-ABI-CANON-01
REPLACEMENT-PROTOCOL-01
COMPATIBILITY-CORPUS-01
PROVIDER-MODEL-01
CAPABILITY-REFUSAL-LAW-01
COMMAND-FLOOR-01
DDAP-00
```

## Recommended Sequence

### Phase 1: Public/Private Surface Law

```text
PUBLIC-SURFACE-REGISTRY-01
API-ABI-CANON-01
NAMING-CONTRACT-01
DEPENDENCY-DIRECTION-01
```

Goal: know what is public, what is private, what can break, and what proof is
required before a boundary promise is changed.

### Phase 2: Artifact Compatibility

```text
ARTIFACT-COMPATIBILITY-01
COMPATIBILITY-CORPUS-01
SCHEMA-PROTOCOL-LAW-01
NO-SILENT-DEFAULTS-HARDEN-01
```

Goal: make old saves, packs, replays, commands, and protocol artifacts load,
migrate, or refuse through declared compatibility law.

### Phase 3: Provider And Capability Model

```text
PROVIDER-MODEL-01
CAPABILITY-REFUSAL-LAW-01
PLATFORM-MATRIX-01
```

Goal: make implementations replaceable without product code knowing backend
details, and make absence/degradation explicit instead of silent.

### Phase 4: Command Floor Before Workbench Expansion

```text
COMMAND-FLOOR-01
VALIDATION-SERVICE-SLICE-01
WORKBENCH-VALIDATION-DASHBOARD-00
```

Goal: prove one command through service, refusal/result, CLI/headless, status
projection, rendered dashboard, and evidence packet before broad Workbench UI
growth.

### Phase 5: Assurance Where It Pays

```text
DDAP-00
PACK-MOD-TRUST-GATE-01
SAVE-STATE-MIGRATION-ASSURANCE-01
RELEASE-SIGNING-PROMOTION-GATE-01
```

Goal: apply high-rigor evidence only to trust-bearing surfaces such as save
state, law/capability checks, pack parsing, release signing, updater,
multiplayer authority, and external-impacting operations.

## Final Recommendation

Adopt the user's proposed framing, with one adjustment: do not define it as
only "portable modular C89 headers." Define it as public-surface governance
across code, contracts, schemas, protocols, package artifacts, command/view
surfaces, compatibility corpora, replacement protocols, assurance levels, and
proof tooling.

The directory cleanup has made the repo more legible. The next step is to make
reusability mechanically true by registering public surfaces first, then
enforcing API/ABI rules and behavioral compatibility through AIDE, RepoX,
TestX, and AuditX.
