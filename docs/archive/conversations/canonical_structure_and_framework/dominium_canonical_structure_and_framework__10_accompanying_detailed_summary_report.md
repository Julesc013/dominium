# Accompanying Detailed Human-Readable Summary Report

**Project:** Dominium / Domino architecture, repository structure, framework boundary, provider model, Workbench, and proof gates  
**Generated:** 2026-05-27 21:02 AEST  
**Purpose:** This report accompanies the earlier preservation package. It gives a readable end-to-end summary of the entire visible conversation: what was discussed, what was decided, what was rejected, what was executed, what remains unresolved, and what a future chat should do next.

---

## 0. Scope, Method, and Reliability

This report summarizes the accessible conversation and the mounted artifacts available in `/mnt/data`. It incorporates the prior handoff/preservation files, user-reported commit statuses, repeated directory-structure reviews, and the architecture decisions made in the chat.

This is **not** a verbatim transcript. It is a synthesized, human-readable report intended for project continuity.

Reliability notes:

- The visible chat contained many user-provided summaries of Codex/AIDE runs. Those are treated as user-reported project state, not independently verified source control facts.
- Several uploaded files expired during the conversation. This report preserves the accessible substance, not every raw upload.
- Multiple structure bundles were found to be mixed or stale across commits. The conversation repeatedly identified report-bundle integrity as a required future proof check.
- Live repo state may have changed after the final status report. Verify the current branch, commit, validators, and CTest state before acting.

Recommended usage:

1. Read this report for human orientation.
2. Read `dominium_canonical_structure_and_framework__02_context_transfer_packet.md` before continuing in another chat.
3. Read `dominium_canonical_structure_and_framework__04_registers.md` for task/decision registers.
4. Verify the live repo before executing any task.

---

## 1. Executive Summary

This conversation started as an urgent attempt to fix Dominium’s directory structure after months of stalled development. It evolved into a complete architectural doctrine for turning Dominium from a messy game repository into a deterministic, contract-governed, provider-backed, pack-composed simulation platform.

The major outcome is that the project’s core structure is now understood as:

```text
Domino    = reusable deterministic/runtime substrate and framework contract surface
Dominium  = one game/product family built on Domino
Workbench = production, validation, editing, inspection, packaging, and evidence environment
AIDE      = repo/control-plane harness
Contracts = machine-readable law
Runtime   = services, projections, providers, and host/platform/render/package machinery
Apps      = thin product shells
Content   = authored payloads: packs, profiles, assets, domain data, themes, templates
Tests/replay/evidence = proof system
```

The central doctrine is:

```text
Freeze public contracts.
Replace private implementations.
Preserve artifacts.
Verify behavior.
```

The directory-structure doctrine is:

```text
Paths encode ownership, not identity.
Stable identities live in contracts, manifests, registries, IDs, public headers, and artifacts.
Private implementations live in folders and files.
Generated output is not source truth.
UI is not authority.
```

The repo’s top-level root model is settled and should not be redesigned casually:

```text
apps/
engine/
game/
runtime/
contracts/
content/
docs/
tests/
tools/
scripts/
cmake/
external/
release/
archive/
```

Allowed project/tooling roots:

```text
.aide/
.aide.local.example/
.github/
.vscode/
```

Generated/local roots must not become active tracked source:

```text
.aide.local/
.dominium.local/
build/
out/
dist/
artifacts/
reports/
tmp/
__pycache__/
```

The conversation’s final posture is: broad structure cleanup is largely resolved, but the project is not full-release-ready. Fast strict, canonical structure, CMake verify/build, smoke CTest, and targeted subsets were repeatedly reported passing or passing with warnings; full CTest/T4 remains debt; broad feature work remains blocked; narrow governed product-spine work can continue after proof hygiene is maintained.

---

## 2. The Problem We Were Solving

The user’s core complaint was that Dominium had spent months in refactor/planning cycles without enabling real feature work. The repository had repeatedly accumulated new roots and redundant folder shapes. The user identified one recurring failure mode: assistants and tooling kept adding new root directories and `src/`/`source/` wrappers, directly violating the project’s own doctrine.

The specific problems included:

- Too many top-level roots.
- Product roots, runtime roots, domain roots, schemas, generated artifacts, packs, profiles, tools, and docs mixed at the same hierarchy level.
- Reintroduction of `src/`, `source/`, `core`, `lib`, `common`, `shared`, `misc`, `data`, and similar junk drawers.
- Duplicate or split concepts such as `appcore`, `appshell`, `shell`, `runtime/app`, `runtime/shell`, `tools/appshell`, and `libs/appcore`.
- Old schema buckets mirroring retired roots.
- Pack payloads mixed with package law.
- Workbench modules and general modules confused.
- Third-party libraries threatening to shape architecture.
- Generated reports and archived snapshots confusing active-source scans.
- Full-gate tests still expecting retired paths.

The goal became not merely to make folders tidy, but to create a system in which future development would not re-create the same structural drift.

---

## 3. Canonical Root Structure and Source Layout

The conversation converged on a small, closed top-level source-root model.

### 3.1 Final active roots

```text
apps/       product shells and product-specific composition
engine/     deterministic Domino substrate implementation
runtime/    reusable host/service/projection/provider machinery
game/       Dominium law, rule, world, and domain meaning
contracts/  machine-readable law, public surfaces, ABI/service/provider/package/schema law
content/    authored payloads: packs, profiles, assets, themes, templates, domain data
docs/       human explanation, not primary law
tests/      proof system
 tools/      validators, codegen, migration, repo/audit/release tooling
scripts/    thin command wrappers
cmake/      build-system support
external/   third-party source/provenance
release/    release definitions, profiles, packaging, provenance
archive/    historical/generated/quarantine/superseded retained material
```

### 3.2 Forbidden active roots

The conversation repeatedly rejected active roots such as:

```text
src/
source/
sources/
core/
control/
data/
lib/
libs/
packs/
profiles/
bundles/
compat/
locks/
repo/
safety/
security/
specs/
updates/
meta/
governance/
performance/
validation/
modding/
models/
templates/
net/
ide/
modules/
plugins/
services/
workspaces/
sdk/
framework/
labs/
```

Some words may still appear inside valid contexts, such as `archive/legacy`, `contracts/compatibility`, `docs/compatibility`, or third-party upstream source layouts.

### 3.3 No `src/` or `source/`

The user explicitly rejected `src/` and `source/` as a root or repeated module wrapper. The final rule is:

```text
No root src/.
No root source/.
No nested first-party module src/.
No source/ wrappers.
```

Implementation files live directly under ownership modules.

Correct:

```text
engine/time/
runtime/render/providers/software/
game/domain/geology/
tools/validators/repo/
```

Wrong:

```text
engine/src/time/
runtime/src/render/software/
game/src/domain/geology/
tools/source/validators/repo/
```

---

## 4. Source Layout versus Runtime/Install/Distribution Layout

A major conclusion was that source layout must not be confused with runtime/install/distribution layout.

The project needs many physical layouts:

- source repository layout;
- CI/build output layout;
- `.dompkg` internal logical export layout;
- downloadable compressed archive layout;
- portable uncompressed install layout;
- installed desktop/server layout;
- read-only media layout;
- save/instance/bundle/diagnostic/replay layouts;
- cache/staging/update/rollback layouts;
- symbol/provenance/release metadata layouts.

The source repo should not contain active install/runtime roots such as:

```text
store/
instances/
saves/
exports/
cache/
ops/
media/
```

These belong to generated runtime/install projections or release artifacts.

The clean model is:

```text
logical roots -> physical projection -> package export map -> install/store/runtime binding -> deterministic verification
```

---

## 5. Naming Doctrine

The conversation spent substantial time refining naming rules.

### 5.1 Four-level naming model

```text
Paths encode ownership.
Public symbols encode namespace.
Stable IDs encode semantic identity.
Private names encode local role.
```

Examples:

```text
Path:          runtime/render/providers/direct3d11/
Public symbol: domino_render_backend_create()
Stable ID:     domino.provider.render.direct3d11.v1
Private file:  backend.c
Private static function: parse_header()
```

### 5.2 When to use `domino` / `dominium`

Use `domino_` and `dominium_` for public/global C symbols and stable IDs:

```text
domino_package_manifest_parse()
domino_replay_log_append()
dominium_world_tick()
dominium_law_validate_action()
```

Do not put `domino` or `dominium` in every directory and file.

Good paths:

```text
runtime/render/providers/raylib/
game/domain/economy/
contracts/schema/package/
```

Bad paths:

```text
runtime/domino_runtime_render/domino_raylib_renderer/
game/dominium_game_domain/dominium_economy/
```

### 5.3 Singular versus plural

Use singular for authority categories and subsystem planes; use plural for collections of peer artifacts.

Examples:

```text
contracts/schema/        category root
contracts/registry/      category root
contracts/package/       package law
contracts/profile/       profile law
game/domain/             implementation plane
runtime/render/          subsystem

content/packs/           many packs
content/domains/         many domain payloads
docs/domains/            many domain docs
tests/fixtures/          many fixtures
```

Some current repo choices may use plural for historical reasons; future assistants should follow the live contract if one is already enforced.

### 5.4 Provider naming

Use generic service roots and exact provider implementation folders:

```text
runtime/render/providers/direct3d11/
runtime/platform/providers/sdl2/
runtime/script/providers/lua54/
```

Use family metadata in manifests:

```toml
family = "direct3d"
version = "11"
```

```toml
family = "sdl"
major = 2
```

Provider directory choices established:

```text
sdl2 now, sdl as family
raylib for broad high-level provider
rlgl for lower-level raylib GL abstraction provider
rlsw for raylib software-render provider
win32 for native Windows API provider, windows as OS family
direct3d11 for Direct3D 11 provider, direct3d as family
opengl33 for first OpenGL 3.3 implementation, opengl as family
lua54 or lua55 for concrete Lua provider, lua as family
raygui for UI provider
raudio for audio provider when used directly
```

---

## 6. Domino Framework, Dominium Game, Workbench, and AIDE

### 6.1 Domino Framework

Domino Framework is not a top-level `framework/` root.

It is:

```text
contracts + public headers + public surface registry + ABI law + service/provider law + conformance tests
```

The public API homes are:

```text
engine/include/domino/     deterministic engine public surfaces
runtime/include/domino/    runtime/service/provider public surfaces
game/include/dominium/     game/product-specific public surfaces, if needed
```

### 6.2 Domino reference implementation

The current `engine/` and `runtime/` are the reference implementation of the Domino substrate and services. Do not rename to `engine/domino_reference/` unless there is a real second engine implementation.

### 6.3 Dominium Game

`game/`, `content/`, and product apps are Dominium’s game/product implementation.

### 6.4 Workbench

Workbench is the production/editing/validation/evidence environment over the same contracts, commands, services, providers, packs, modules, and artifacts. Workbench is not authority.

### 6.5 AIDE

AIDE is the repo/control-plane harness. It should be governed by `.aide/` policy/control-plane data, `.aide.local/` mutable local state, and `archive/generated/aide/` retained generated evidence. State-like AIDE dirs require classification.

---

## 7. API, ABI, and Language Baseline

The chat settled on:

```text
Mainline language baseline: C17 + C++17
Mainline architecture: 64-bit, little-endian, x86_64 + arm64 first
Boundary rule: C-compatible ABI, POD-only, versioned, no C++ ABI leakage
```

C17 owns:

```text
ABI-facing structs
packets
save/replay records
deterministic math
stable handles
renderer command IR
small low-level facades
```

C++17 owns:

```text
runtime services
providers
game orchestration
Workbench
tools
resource ownership
composition/profile resolution
```

Public ABI rule:

```text
opaque handles
versioned structs
struct_size fields
explicit ownership/lifetime
explicit allocator/free path
result/refusal codes
no exceptions across boundary
no STL containers
no C++ classes
no native object layout serialization
no third-party types
```

The chat rejected pure C99, pure C17, pure C++11, pure C++17 at stable boundaries, and C++20/23/26 as mainline for now.

---

## 8. Public Surface Governance

The project needs machine-readable public surface law.

Surface kinds discussed:

```text
c_header
abi_table
schema
registry
protocol
command
view
event
refusal
diagnostic_code
package_format
profile_format
save_format
replay_format
provider_abi
capability_id
release_artifact
```

Stability classes:

```text
frozen_abi
stable_api
stable_data_contract
stable_command_contract
stable_protocol
provisional
internal
experimental
generated
fixture
historical
retired
```

Rule:

```text
Most things start internal or provisional.
Only proven surfaces become stable.
```

Every stable surface should have:

```text
owner
stable ID
path
version
stability class
compatibility policy
replacement policy
proof
deprecation policy
```

---

## 9. Dependency Direction and Boundary Law

Canonical dependency direction:

```text
apps    -> runtime, game, contracts
game    -> engine, contracts
runtime -> engine, contracts
engine  -> contracts only where necessary
tools   -> may inspect all, but runtime must not depend on tools
content -> no code dependency
contracts -> no implementation dependency
archive -> no active dependency
```

Forbidden:

```text
engine -> runtime
engine -> game
engine -> apps
runtime -> apps
runtime owns game truth
contracts import implementation
content imports code
active source imports archive
```

Third-party libraries are only allowed in provider/proof/tooling boundaries, not stable law or deterministic simulation.

---

## 10. Service-First Provider Architecture

The final provider doctrine:

```text
Service identity is first-party.
Provider implementation is replaceable.
Profiles select providers.
Third-party libraries are fenced.
Apps stay generic.
Contracts define the law.
```

Service roots should be generic:

```text
platform
input
render
audio
asset
script
ui
storage
diagnostics
command
view
projection
```

Provider implementations should live under:

```text
runtime/<service>/providers/<provider>/
```

Example:

```text
runtime/render/providers/raylib/
runtime/render/providers/rlgl/
runtime/render/providers/rlsw/
runtime/platform/providers/sdl2/
runtime/script/providers/lua54/
```

Third-party source belongs under:

```text
external/upstream/<third_party>/
```

or an explicitly chosen equivalent such as `external/vendor/`.

Provider choices belong under profiles:

```text
release/profiles/dev/client.raylib.toml
release/profiles/dev/client.sdl2_opengl33.toml
release/profiles/dev/workbench.raylib.toml
release/profiles/dev/server.null.toml
```

Not under app paths.

---

## 11. Raylib, SDL2, Lua, ImGui, and Third-Party Libraries

The chat accepted using raylib aggressively, but only as a provider suite.

Raylib ecosystem roles:

```text
raylib = broad seed provider suite
rlgl   = raylib low-level OpenGL abstraction provider
rlsw   = raylib software renderer provider
raygui = early Workbench/debug UI provider
raudio = audio provider if used directly
raymath = provider-local render/editor math helper
rtextures/rmodels = import/preview helpers
```

SDL2 role:

```text
platform/input/audio provider family
```

Lua role:

```text
pinned script provider behind dominium.script.v1 or domino.script.v1
not raw mod ABI
```

Dear ImGui role:

```text
optional Workbench/debug tooling UI provider
not UI law
```

Forbidden leakage:

```text
raylib.h
rlgl.h
raymath.h
SDL.h
lua.h
imgui.h
```

should not appear in:

```text
engine/
game/
contracts/
content/
saves/
replays/
public SDK headers
```

Allowed only in provider/proof/experiment boundaries.

---

## 12. Workbench, Modules, Packs, Apps, and Composition

Vocabulary:

```text
Component = source/build ownership unit
Service   = callable runtime capability
Provider  = replaceable implementation
Pack      = distributable authored payload
Module    = declared functional extension unit
Workspace = large user-facing Workbench composition
App       = shipped product composition
Artifact  = persisted versioned thing
```

Rules:

```text
A folder can contain a component.
A manifest defines a module.
A pack can provide modules.
An app composes modules, providers, services, and packs.
A workspace presents workflows.
```

Workbench structure:

```text
apps/workbench/shell/
apps/workbench/module/
apps/workbench/workspace/
```

Reusable modules should not live under `apps/workbench/module/`; Workbench modules are UI modules only.

General module law:

```text
contracts/module/
```

Pack-delivered module payload:

```text
content/packs/<category>/<pack_id>/modules/
```

---

## 13. Presentation / Projection Model

The final semantic spine:

```text
intent
→ command
→ capability/refusal check
→ service
→ result | document | snapshot
→ diagnostics/evidence
→ view
→ action model
→ projection
→ shell
```

Definitions:

```text
command    = behavior request
result     = command output
refusal    = typed failure
document   = persistent/editable logical object
snapshot   = read-only state projection
patch      = lawful proposed mutation
view       = semantic presentation model
action     = operation available from a view
projection = CLI/text/rendered/native/headless realization
shell      = product host
```

Do not create separate semantic contract worlds for CLI/TUI/rendered/native. These are projections:

```text
runtime/projection/cli/
runtime/projection/text/
runtime/projection/rendered/
runtime/projection/native/
runtime/projection/headless/
```

Contracts should define semantic surfaces:

```text
contracts/command/
contracts/action/
contracts/result/
contracts/refusal/
contracts/diagnostic/
contracts/document/
contracts/patch/
contracts/view/
contracts/presentation/
contracts/projection/
```

---

## 14. Content, Packs, Saves, Replays, and Artifacts

Preferred pack layout:

```text
content/packs/<category>/<pack_id>/
  pack.manifest.json
  data/
  assets/
  docs/
  ui/
  scenarios/
  locks/      # only if authored, not generated
```

Pack IDs do not depend on path.

Pack composition should be deterministic:

```text
base pack
→ official extension pack
→ mod pack
→ theme pack
→ user profile pack
→ workspace override pack
```

Rules:

```text
no silent overwrite
ordered overlays
declared conflicts
schema validation
hash/provenance tracking
capability negotiation
lockfile output
```

Save/replay law:

```text
stable IDs
schema IDs
explicit little-endian encoding
fixed-width values
canonical serialization
migration/refusal behavior
no native layout serialization
```

---

## 15. Proof Gates and Current Project State

The conversation distinguished between normal development gates and full release gates.

Normal fast strict gate:

```text
AIDE doctor/validate
RepoX strict
root/layout/no-src/forbidden-name validators
canonical structure validator
public surface / ABI / dependency direction checks
CMake verify/build
smoke CTest
focused capability/provider/package/schema checks
```

Full/T4 gate:

```text
full CTest
compatibility corpus
public header consumer tests
replay determinism tests
save migration tests
pack/mod trust tests
provider conformance tests
release promotion checks
```

As of the latest user-reported state:

```text
canonical structure: credible / pass with warnings
fast strict: not fully clean if stale evidence/marker debt persists
smoke CTest: reported passing in several runs
full CTest: not green
feature readiness: limited
broad feature work: blocked
```

---

## 16. Major Reported Commits and Statuses

The user reported several task results. Important ones include:

- `refactor(repo): finish canonical structure cleanup` — actual structure cleanup, schema routing, CompatX cleanup, DomUI routing, test taxonomy moves, provider/profile guardrails, Workbench/projection boundaries, validators, fresh structure export. Status: PASS_WITH_WARNINGS.
- `tests: route full-gate legacy path expectations` — routed full-gate tests away from retired paths such as `game/rules`, `contracts/schemas`, `data/profiles`, `libs/appcore`, old docs roots, old tools roots. Status: PASS_WITH_WARNINGS; targeted subset 9/9 passed.
- `repo: define Domino framework boundary` — defined Domino Framework as contracts + public headers + service/provider law, not top-level `framework/`. Added validator and doc. Status: PASS_WITH_WARNINGS.
- `repo: enforce service-first provider structure` — moved null/software render providers under `runtime/render/providers`, added provider structure law, release profiles, external roots, validators. Status: PASS_WITH_WARNINGS.

These statuses are user-reported and should be verified against the live repository if used operationally.

---

## 17. What We Put Off for Later

Deferred or still pending:

```text
FULL-GATE-GENERATED-EVIDENCE-REFRESH-01
FAST-STRICT-EVIDENCE-MARKER-REPAIR-01
PROJECTION-CONFORMANCE-01
PRESENTATION-CONTRACT-01
PACK-INTERNAL-LAYOUT-CANON-01
RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01
AIDE-STATE-CLASSIFICATION-01
PUBLIC-HEADER-ABI-PROMOTION-01
STORAGE-PACKAGE-PROVIDER-SPLIT-01
FULL-CTEST-AUDIT-NONPATH-01
PROVIDER-WEDGE-01 / RAYLIB-SEED-PROVIDER-01
SDL2-PROVIDER-01
LUA-PROVIDER-PIN-01
```

Broad feature work remains blocked until proof gates improve:

```text
large Workbench UI
runtime module loader
provider runtime
package runtime
gameplay expansion
renderer implementation
native GUI
release publication
```

Narrow governed slices are acceptable if gates are green.

---

## 18. Things Future Assistants Must Not Do

Do not:

```text
add top-level framework/
add top-level modules/
add top-level plugins/
add top-level services/
add top-level profiles/
add top-level labs/
add top-level sdk/
reintroduce src/ or source/
make raylib/SDL/Lua architecture law
put provider choices in app paths
treat Workbench as authority
move authored pack payloads under contracts/package
let tools become a second source tree
treat generated reports as source truth
overclaim PASS_WITH_WARNINGS as full green
restart broad structure cleanup unless a hard validator fails
```

---

## 19. What a New Chat Should Do First

A new chat should ask for the latest current repo status or inspect the live repository. Then:

1. Verify current branch/commit.
2. Verify AIDE doctor/validate.
3. Verify fast strict / RepoX strict.
4. Verify canonical structure validators.
5. Verify current queue/current.toml.
6. Do not run broad restructure by default.
7. Pick the next task based on actual gate state.

Likely next tasks:

```text
If fast-strict/RepoX blocked:
  FAST-STRICT-EVIDENCE-MARKER-REPAIR-01

If proof gates are clean:
  PROJECTION-CONFORMANCE-01

If provider implementation is now allowed:
  PROVIDER-WEDGE-01 / RAYLIB-SEED-PROVIDER-01
```

---

## 20. Final Synthesis

The ultimate design is:

```text
Dominium is a deterministic, contract-governed, provider-backed, pack-composed simulation platform built on reusable Domino surfaces.
```

The key architectural formula is:

```text
contracts define semantic surfaces
runtime implements services and providers
engine preserves deterministic substrate
game defines Dominium meaning
content supplies authored payloads
apps compose products
Workbench operates the system
tools validate/generate/migrate
tests and evidence prove behavior
```

The most important preserved decision is:

```text
Domino Framework is not a top-level framework/ root.
It is public surfaces, contracts, ABI law, service/provider law, public headers, conformance tests, and profiles.
```

The most important operational status is:

```text
Structure is credible.
Full proof is not complete.
Feature readiness is limited.
Continue with targeted proof and governed slices, not broad refactors.
```
