# Dominium Canonical Architecture and Repository Handoff

**Status date:** 2026-05-20  
**Context:** Dominium canonical repo/spine cleanup, reusable Domino substrate, C89 API/ABI discipline, Workbench/product development readiness.  
**Purpose:** Self-contained handoff for a new ChatGPT/Codex/AIDE conversation. It summarizes the architectural doctrine, completed cleanup, current state, remaining debt, prohibitions, next tasks, and long-term governance needed to make Dominium portable, modular, extensible, reusable, moddable, backward-compatible, and future-proof.

---

## 0. Executive verdict

Dominium has moved from a messy, root-sprawling repository toward a coherent ownership-root structure. The top-level structure is now close enough that the next maturity step is **not another large directory redesign**. The next step is to formalize and mechanically enforce the **public/private contract layer** that makes the codebase reusable across future games and engine projects.

The ultimate model is:

```text
Domino    = reusable deterministic substrate.
Dominium  = one game/product family built on Domino.
Workbench = production/editing/validation environment over the same contracts.
Packs     = governed authored content/extension units.
Contracts = machine-readable law.
Tests/replay/proof = truth system.
```

The strongest operating law is:

```text
Freeze contracts.
Replace implementations.
Preserve artifacts.
Verify behavior.
```

The best structure is not the largest tree. It is a small closed set of ownership roots plus strict module/API/file/schema/protocol/package governance.

The current root model should remain:

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

Allowed tooling/project roots:

```text
.aide/
.aide.local.example/
.github/
.vscode/
```

Generated/local roots must not be active tracked source:

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

The repo is now likely **feature-work capable in limited lanes** if these proof gates are green:

```text
RepoX STRICT
AIDE validate
root/layout validators
docs sanity
build boundary
include sanity
UI shell purity
ABI checks
CMake configure/build
smoke CTest
```

Full-gate work remains limited until:

```text
full CTest is run
remaining pack/FAB validation failures are resolved or explicitly classified
duplicate-symbol linker warnings are confirmed pre-existing and non-worsening
```

---

## 1. Latest reported repo/proof state

The latest explicit user report stated:

```text
Starting commit: e201f72d6825c5f815f3850692885ed185745b6b
Ending commit:   7e8879e6d0e6b13eebb181d3cd41cef3acb71dfa
Commit:          fix(repo): remediate canonical cleanup proof
Worktree:        clean after commit
```

Then another report stated:

```text
Starting commit: 7e8879e6d0e6b13eebb181d3cd41cef3acb71dfa
Ending commit:   17e35302327dff31141ae7541ac0d5fe7205ff3d
Commit:          fix(repo): repair repox strict debt
Worktree:        clean after commit
```

Proof reported after `17e3530...`:

```text
git diff --check / cached diff check: PASS
Python compile for touched tools/tests: PASS
AIDE doctor / validate: PASS, with existing review-packet warning
RepoX STRICT: PASS pre-commit and post-commit
Repo/root/docs/tools/content validators: PASS
Docs sanity, build boundary, include sanity, UI shell purity, ABI checks: PASS
TestX fast dry-run + survival invariants: PASS
Worldgen lock verify: PASS
Pack validator focused checks: PASS
cmake --preset verify: PASS
cmake --build --preset verify --target ALL_BUILD: PASS, with known duplicate-symbol linker warnings
ctest --preset verify -L smoke --output-on-failure: PASS, 57/57
Full CTest: Not run
```

Remaining non-blocking debt reported:

```text
docs/archive/audit/PACK_AUDIT.txt records 14 current pack-reference/FAB validation failures as package/content debt.
Full CTest has not been run.
Known duplicate-symbol linker warnings remain.
```

Interpretation:

```text
RepoX STRICT lanes: unblocked.
Canonical proof lanes: unblocked.
CMake verify build: unblocked.
Smoke CTest: unblocked.
Limited feature work: allowed.
Full-gate feature work: still limited until full CTest and pack/FAB debt are resolved or classified.
```

---

## 2. Completed cleanup themes

The following major refactor/canon waves were discussed, queued, or reported as completed/partially completed:

### 2.1 Root/spine cleanup

The old root chaos included many roots and second-level structures such as:

```text
app/
appshell/
client/
server/
setup/
launcher/
core/
control/
data/
packs/
profiles/
bundles/
schema/
schemas/
compat/
locks/
repo/
safety/
security/
specs/
updates/
validation/
meta/
governance/
performance/
net/
lib/
libs/
geo/
chem/
physics/
thermal/
materials/
worldgen/
```

The target root model became:

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

Generated/local-only roots:

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

The major lesson:

```text
The top-level repo should contain durable ownership roots, not every topic, subsystem, era, product, renderer, platform, or future fantasy.
```

### 2.2 Runtime shell cleanup

Old concepts:

```text
runtime/app/
runtime/appshell/
runtime/shell/appcore/
tools/appshell/
libs/appcore/
apps/*/shell/
apps/*/core/
```

Canonical direction:

```text
runtime/shell/
```

`runtime/shell/` owns:

```text
product lifecycle
mode selection
command routing
view routing
event routing
refusal reporting
diagnostic shell state
CLI/TUI/native/rendered/headless binding
product capability negotiation
shared product startup/shutdown
```

Old terms to eliminate from active source:

```text
appcore
appshell as implementation name
runtime/app
runtime/shell/appcore
tools/appshell
apps/*/core
apps/*/shell unless tiny product binding
```

### 2.3 Runtime second-level names

Old active names to collapse:

```text
runtime/render/soft/
runtime/render/stub/
runtime/render/client/renderers/
runtime/shell/commands/
runtime/shell/ui_backends/
runtime/capability/capability/
runtime/ui/core/
```

Canonical routes:

```text
runtime/render/soft/             -> runtime/render/software/
runtime/render/stub/             -> runtime/render/null/
runtime/render/client/renderers/ -> runtime/render/backend/
runtime/shell/commands/          -> runtime/shell/command/
runtime/shell/ui_backends/       -> runtime/ui/backend/
runtime/capability/capability/   -> runtime/capability/core/
runtime/ui/core/                 -> runtime/ui/service/ or finer split
```

### 2.4 Game rule/domain cleanup

Old active paths:

```text
game/rules/
game/include/dominium/rules/
```

Canonical grammar:

```text
game/rule/       shared rule machinery
game/law/        authority/law/policy semantics
game/domain/     domain-specific game-world meaning
game/world/      world model abstractions
game/include/    public game headers matching canonical ownership
```

Likely routes:

```text
game/rules/economy        -> game/domain/economy
game/rules/logistics      -> game/domain/logistics
game/rules/war            -> game/domain/war
game/rules/technology     -> game/domain/technology
game/rules/population     -> game/domain/population
game/rules/infrastructure -> game/domain/infrastructure
game/rules/physical       -> game/domain/physics or game/domain/mechanics
game/rules/governance     -> game/law or game/domain/governance
game/rules/agents         -> game/domain/agent
game/rules/fab            -> game/domain/fabrication
game/rules/life           -> game/domain/life or game/domain/embodiment
```

### 2.5 Engine include boundary cleanup

Old engine include leaks:

```text
engine/include/domino/app/
engine/include/domino/cli/
engine/include/domino/gui/
engine/include/domino/input/
engine/include/domino/io/
engine/include/domino/pkg/
engine/include/domino/render/
engine/include/domino/tui/
engine/include/domino/world/
engine/include/render/
```

Canonical rule:

```text
engine/include/ exports deterministic engine substrate only.
runtime/include/ owns runtime-facing public headers.
game/include/ owns game/world/domain/law/rule headers.
apps/*/include/ owns product-specific app API only.
```

Allowed engine include concepts:

```text
kernel
determinism
execution
state
time
replay
proof
identity/ids if deterministic substrate
memory/order/schedule/event if engine-owned
concurrency only if engine substrate
math only if deterministic engine math
engine diagnostics, not runtime logging/UI
```

### 2.6 Pack authority cleanup

Problem:

```text
content/packs/<pack_id>/
contracts/package/packs/<pack_id>/
```

Correct ownership:

```text
content/packs/<pack_id>/       authored pack payload and pack-local manifest
contracts/package/             package schemas, policies, locks, contracts
contracts/registry/            package/pack registries if needed
tests/fixtures/package/        fixture/example packs
archive/generated/package/     generated package artifacts/evidence
archive/historical/package/    historical/superseded package material
```

Rule:

```text
Real authored pack payloads must not live under contracts/package/packs.
```

### 2.7 Content pack/domain cleanup

Current/old content issues:

```text
content/packs/ mixing category folders and flat org.dominium.* pack IDs
content/domains/game/core/
content/domains/worldgen/real/earth/content/
content/domains/worldgen/real/milky_way/content/
content/domains/worldgen/real/sol_system/content/
content/data/
content/domain-data/
```

Target content taxonomy:

```text
content/
  assets/
  bundles/
  defaults/
  domains/
  examples/
  fixtures/
  packs/
  profiles/
  templates/
  themes/
```

Pack layout must choose one:

```text
content/packs/<pack_id>/
```

or:

```text
content/packs/<category>/<pack_id>/
```

If using category model, categories must be finite and documented, such as:

```text
blueprint/
core/
derived/
domain/
example/
law/
official/
profile/
reality/
representation/
spec/
tool/
worldgen/
```

### 2.8 Schema taxonomy cleanup

Old schema buckets:

```text
contracts/schema/chem/
contracts/schema/civ/
contracts/schema/civilisation/
contracts/schema/compat/
contracts/schema/control/
contracts/schema/core/
contracts/schema/diag/
contracts/schema/fluid/
contracts/schema/geo/
contracts/schema/lib/
contracts/schema/models/
contracts/schema/mods/
contracts/schema/net/
contracts/schema/packs/
contracts/schema/render/
contracts/schema/specs/
contracts/schema/tool/
contracts/schema/tools/
contracts/schema/validator/
```

Canonical target:

```text
contracts/schema/
  app/
  engine/
  game/
  runtime/
  domain/
  package/
  profile/
  save/
  replay/
  release/
  repo/
  security/
  safety/
```

Additional categories only if justified:

```text
distribution/
install/
registry/
governance/
identity/
compatibility/
diagnostics/
policy/
protocol/
view/
validation/
tool/
```

Canonical domain schema names:

```text
contracts/schema/domain/chemistry/
contracts/schema/domain/geology/
contracts/schema/domain/fluids/
contracts/schema/domain/civilization/
```

### 2.9 Apps-thin cleanup

Suspicious app-local paths:

```text
apps/client/local_server/
apps/client/model/
apps/client/presentation/
apps/server/authority/
apps/server/persistence/
apps/server/shard/
apps/launcher/lifecycle/
apps/setup/lifecycle/
apps/*/include/_internal
```

Thin-app rule:

```text
apps/* may own:
  main entrypoints
  product descriptors
  product-specific command registration
  product-specific mode binding
  app-specific CLI/TUI/native/rendered binding
  small product lifecycle glue
  product-local resources
  app-specific public headers

apps/* must not own:
  shared runtime lifecycle
  renderer internals
  platform internals
  shared UI framework
  network core
  storage/persistence core
  package/update/profile/save/replay law
  game/domain/law semantics
  engine mechanisms
  reusable tooling
  content/data/packs
  schemas/contracts except product references
```

### 2.10 Workbench naming cleanup

Workbench root is correct:

```text
apps/workbench/
```

Old/narrow cleanup targets:

```text
apps/workbench/module/game/edit/
apps/workbench/module/tool/editor/
apps/workbench/module/ui/editor/gen/
apps/workbench/module/ui/native/
```

Recommended:

```text
apps/workbench/module/game/editor/
apps/workbench/module/tooling/editor/      # if user-facing tool-definition editor
tools/codegen/ui/                          # if generator implementation
runtime/ui/backend/ or runtime/platform/*  # if native UI substrate
```

Workbench modules should use noun roles:

```text
editor
viewer
inspector
analyzer
preview
registry
doc
panel
```

Avoid:

```text
edit
gen
misc
core
shared
common
native if actually backend/platform substrate
```

### 2.11 AIDE active/generated boundary cleanup

AIDE ownership:

```text
.aide/                    committed AIDE policy, contracts, prompts, adapters, commands, eval definitions, route rules, AI governance
.aide.local/              ignored mutable local state
.aide.local.example/      minimal committed example only
archive/generated/aide/   retained generated AIDE exports, evidence snapshots, generated adapters, queue evidence, historical tool outputs
archive/historical/aide/  old designs, if needed
```

Suspicious `.aide/` paths if live-state-like:

```text
.aide/cache/
.aide/queue/
.aide/reports/
.aide/evals/runs/
.aide/ledgers/
.aide/release/dist/
.aide/generated/
```

Scanners must not treat:

```text
archive/generated/aide/export/.../files/.aide/
archive/generated/aide/queue/*/evidence/
```

as active `.aide/`.

### 2.12 Tools taxonomy cleanup

Target taxonomy:

```text
tools/
  aide/
  audit/
  build/
  codegen/
  import/
  export/
  migration/
  package/
  release/
  repo/
  test/
  validators/
  xstack/
  domain/
```

Optional if justified:

```text
diagnostics/
performance/
```

Avoid broad mirrors:

```text
tools/core/
tools/lib/
tools/share/
tools/gui/
tools/render/
tools/net/
tools/network/
tools/server/
tools/setup/
tools/launcher/
tools/engine/
tools/runtime/
tools/validate/
tools/validation/
tools/validator/
tools/*_editor/
tools/*_viewer/
tools/*_inspector/
```

Routing:

```text
validator -> tools/validators/<area>/
codegen -> tools/codegen/<area>/
repo/audit/migration -> tools/repo, tools/audit, tools/migration
build/release/package -> tools/build, tools/release, tools/package
domain noninteractive -> tools/domain/<domain> or validators/codegen/domain
user-facing editor/viewer/inspector -> apps/workbench/module/
runtime implementation -> runtime/
product implementation -> apps/
contract/schema/registry -> contracts/
test fixture -> tests/
historical/generated -> archive/
```

### 2.13 Docs taxonomy cleanup

Target docs taxonomy:

```text
docs/
  architecture/
  repo/
  runtime/
  apps/
  engine/
  game/
  domains/
  content/
  workbench/
  modding/
  distribution/
  release/
  build/
  development/
  testing/
  operations/
  performance/
  safety/
  security/
  reference/
  archive/
```

Optional if justified:

```text
compatibility/
validation/
governance/
```

Avoid old first-level roots:

```text
docs/app/
docs/appshell/
docs/client/
docs/server/
docs/setup/
docs/launcher/
docs/control/
docs/core/
docs/lib/
docs/net/
docs/render/
docs/platform/
docs/ui/
docs/tools/
docs/pack_format/
docs/packs/
docs/specs/
docs/refactor/
docs/restructure/
docs/audit/
docs/data/
docs/system/
docs/geo/
docs/fluid/
docs/electric/
docs/materials/
docs/mechanics/
docs/physical/
docs/worldgen/
```

### 2.14 RepoX/TestX proof cleanup

Known stale proof issues that were repaired or targeted:

```text
data/registries/law_profiles.json
tools/dist/runtime_compile_helper.py
old runtime paths
old game/rules paths
old engine include paths
old contracts/schema buckets
old contracts/package/packs payload expectations
archive/generated treated as active source
Windows encoding crash in RepoX output
NO_SILENT_DEFAULTS failures
worldgen lock/baseline stale paths
schema-version references
release/package proof artifacts
doc status headers
historical refs in current docs
```

Current reported status:

```text
RepoX STRICT: PASS
TestX fast dry-run + survival invariants: PASS
```

---

## 3. Absolute prohibitions

Do not reintroduce:

```text
root src/
root source/
nested src/ under first-party modules
source/
sources/
code/
impl/
common/
shared/
misc/
lib/
libs/
core as generic bucket
data as junk drawer
old
new
future
experimental
modern
legacy as active status path
compat as active status path
universal
v2/v3 directories as stable names
```

Allowed exceptions:

```text
archive/legacy/
archive/generated/
archive/historical/
docs/compatibility/
contracts/compatibility/
external/vendor or third-party source retaining upstream structure
finite documented compatibility shims
fixtures intentionally modeling old layouts
```

Do not:

```text
add new top-level roots casually
treat source layout as install/runtime/package layout
store generated build output as source
move real content payloads under contracts
move schemas/contracts under content
put user-facing editors under tools
let tools become a second source tree
let docs mirror old root chaos
let tests become a dumping ground
hand-edit generated artifacts when a generator owns them
hide failures by weakening validators
change semantic IDs/hashes/locks silently
let Workbench bypass command contracts
let engine depend on runtime/game/apps
let runtime own game truth
let apps own reusable runtime subsystems
```

---

## 4. Current conceptual target

### 4.1 Domino vs Dominium split

Hard conceptual distinction:

```text
Domino   = reusable engine/substrate/runtime/tool layer.
Dominium = this specific game/product/content/world/ruleset built on Domino.
```

Reusable across future games/projects:

```text
engine/
runtime/
contracts/abi/
contracts/protocol/
contracts/package/
contracts/view/
tools/build/
tools/codegen/
tools/validators/
cmake/
```

Dominium-specific:

```text
game/domain/economy
game/law/dominium-specific-law
content/packs/org.dominium.*
apps/client
apps/server
docs/domains/dominium-specific-worldgen
```

Mechanical future rule:

```text
Every module should declare whether it is Domino-reusable, Dominium-specific, test-only, generated, or historical.
```

### 4.2 Layer responsibilities

```text
contracts   define law
engine      executes deterministic substrate/truth
runtime     adapts host/platform/services/presentation
game        defines Dominium meaning
apps        expose thin product shells
content     mounts authored packs/assets/profiles
tools       validate/generate/migrate/audit, not runtime
release     packages projections/evidence/rollback
tests       prove contracts and behavior
docs        explain contracts and current architecture
archive     preserves history/evidence without active authority
```

### 4.3 Public/private philosophy

The best systems do not freeze everything. They freeze boundaries.

```text
Stable:
  public C ABI/API
  save/replay/pack formats
  command/view/event/refusal contracts
  schema/protocol IDs
  capability IDs
  package IDs
  provider ABI
  artifact identity

Replaceable:
  private folders
  implementation files
  algorithms behind same proof
  internal helper functions
  Workbench UI internals
  renderer backend internals
```

Condensed law:

```text
Stable outside.
Flexible inside.
```

---

## 5. What the best systems do

### 5.1 Stable public boundary, unstable internals

Mature systems choose public boundaries carefully and allow internals to evolve. For Dominium:

```text
Do not promise private APIs.
Do not freeze folder internals.
Do promise stable registered public surfaces.
```

### 5.2 Artifact compatibility is treated as a first-class API

Long-lived systems treat file formats and protocols as public surfaces. Dominium must treat these as compatibility surfaces:

```text
save files
replay logs
pack manifests
profiles
instance bundles
diagnostic bundles
package manifests
lockfiles
worldgen baselines
command transcripts
view snapshots
network/IPC protocols
```

### 5.3 Extension packages have identity and lifecycle

Mods/packs/modules must not be arbitrary file dumps. They need:

```text
manifest
ID
version
capability declarations
compatibility range
install/apply behavior
rollback/uninstall behavior
created object inventory
trust level
```

### 5.4 Core must be unaware of optional features

The engine should not know the economy pack. Runtime should not know Dominium law. Client should not hardcode every Workbench module. Mods declare capabilities, dependencies, and contracts.

### 5.5 Native extension boundaries must be deliberate

Native plugins should be late-stage. Start with:

```text
data-only packs
schema-validated packs
scriptless declarative modules
Workbench-authored modules
external process adapters
trusted built-in modules
```

Only later:

```text
native plugins with C ABI
capability sandbox
versioned provider table
determinism restrictions
trust policy
```

---

## 6. Missing governance systems

### 6.1 Public surface registry

Highest-value next concept.

Create:

```text
contracts/public_surface/
  public_surface.contract.toml
  surface.schema.json
  abi_surface.contract.toml
  schema_surface.contract.toml
  protocol_surface.contract.toml
  command_surface.contract.toml
```

Each public surface declares:

```text
id
kind
path
owner
stability
version
public/private/internal/generated
allowed dependencies
forbidden dependencies
compatibility test
deprecation state
replacement target
```

Surface classes:

```text
frozen_abi
stable_api
stable_data_contract
stable_command_contract
stable_protocol
provisional
internal
experimental
retired
```

This answers:

```text
What exactly are we promising not to break?
```

### 6.2 API/ABI canon

Create:

```text
contracts/abi/c_api.contract.toml
docs/architecture/api_abi_canon.md
docs/development/c89_coding_standard.md
docs/development/module_api_standard.md
tools/validators/abi/check_public_headers.py
tests/contract/public_headers/
```

Rules:

```text
opaque handles
versioned structs
size fields on ABI structs
explicit allocator
explicit ownership
explicit lifetime
explicit result/refusal codes
no C++ types across ABI
no STL across ABI
no platform headers in engine ABI
no direct struct serialization
no silent global state
callbacks include user pointer
```

### 6.3 Dependency direction validator

Create:

```text
contracts/repo/dependency_directions.contract.toml
tools/validators/repo/check_dependency_directions.py
```

Canonical dependency direction:

```text
apps    -> runtime, game, contracts
game    -> engine, contracts
runtime -> engine, contracts
engine  -> contracts only where necessary
tools   -> may inspect everything but must not become runtime dependency
content -> no code dependency
contracts -> no implementation dependency
```

Forbidden:

```text
engine -> runtime
engine -> game
engine -> apps
runtime -> apps
runtime owning game truth
apps owning reusable runtime subsystems
contracts importing implementation code
```

### 6.4 Compatibility corpus

Create:

```text
tests/compat/
  saves/
  replays/
  packs/
  profiles/
  schemas/
  protocols/
  commands/
  diagnostics/
  invalid/
```

Every release must prove:

```text
old valid artifacts still load or migrate
old invalid artifacts still refuse correctly
old replay still hashes or explicitly refuses
old pack still resolves or explicitly refuses
old command still maps or explicitly deprecates
```

Backward compatibility is a corpus plus tests, not intent.

### 6.5 Replacement protocol

Create:

```text
contracts/replacement/replacement.contract.toml
docs/architecture/replacement_protocol.md
tools/validators/repo/check_replacement_packet.py
```

A rewrite/replacement must provide:

```text
old implementation
new implementation
same public surface
conformance tests
compatibility corpus result
replay/proof result
performance notes
migration notes
rollback plan
```

This is what makes whole-folder rewrites safe.

### 6.6 Capability/refusal law

Create:

```text
contracts/capability/
contracts/refusal/
docs/architecture/capability_refusal_law.md
```

Every optional provider supports:

```text
requested capability
available capability
selected provider
degraded mode
refusal code
recovery path
diagnostic evidence
```

Applies to:

```text
renderers
platforms
storage
network
audio
input
package loaders
profiles
mods
Workbench modules
server authority
setup/update
old-platform support
```

### 6.7 Provider model

Create a provider table model for replaceable backends:

```c
typedef struct domino_provider_desc {
    domino_u32 size;
    domino_u32 abi_version;
    const char *id;
    const char *kind;
    domino_result_t (*query)(void *out_caps);
    domino_result_t (*create)(const void *config, void **out_provider);
    void (*destroy)(void *provider);
} domino_provider_desc_t;
```

Use for:

```text
render backend
platform backend
storage backend
audio backend
input backend
package backend
UI backend
network transport
```

### 6.8 Schema/protocol evolution law

Every schema/protocol needs:

```text
stable ID
version
compatibility range
unknown-field policy
required-field policy
default policy
canonical serialization
migration policy
refusal behavior
fixtures
negative tests
```

No silent defaults. Missing values must be:

```text
explicit default
explicit migration
explicit refusal
```

### 6.9 Assurance profile

Use integrity levels. Do not apply heavy process everywhere.

Suggested:

```text
DIL-0 scratch/prototype
DIL-1 normal code
DIL-2 product feature
DIL-3 trust-bearing state
DIL-4 signing/update/authority
DIL-5 external/security-critical boundary
```

High levels apply to:

```text
save state
replay/proof
package parsing
release signing
update/rollback
server authority
law/capability checks
mod trust
network protocol
```

Low levels apply to:

```text
UI experiments
Workbench mockups
tools prototypes
lore/content drafts
visual effects
```

### 6.10 Mod trust ladder

Modding needs levels:

```text
data-only pack
schema-validated pack
scriptless rule pack
Workbench-authored module
external process adapter
trusted native provider
signed native provider
```

Each level gets different permissions.

---

## 7. C89 public API/ABI rules

### 7.1 Public headers

Public headers should be boring, explicit, conservative.

Rules:

```text
C89-compatible where possible
no C++ types
extern "C" guard for C++
opaque handles
explicit result codes
explicit allocator
explicit ownership/lifetime
no platform-specific types in engine ABI
no hidden globals
no struct serialization
```

Example:

```c
#ifndef DOMINO_ENGINE_H
#define DOMINO_ENGINE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef unsigned char domino_u8;
typedef unsigned short domino_u16;
typedef unsigned long domino_u32;

typedef struct domino_engine domino_engine_t;

typedef enum domino_result {
    DOMINO_OK = 0,
    DOMINO_ERR_INVALID_ARG = 1,
    DOMINO_ERR_OUT_OF_MEMORY = 2,
    DOMINO_ERR_UNSUPPORTED = 3,
    DOMINO_ERR_CAPABILITY_MISSING = 4,
    DOMINO_ERR_CONTRACT_MISMATCH = 5
} domino_result_t;

typedef struct domino_api_version {
    domino_u32 major;
    domino_u32 minor;
    domino_u32 patch;
} domino_api_version_t;

domino_result_t domino_engine_get_api_version(domino_api_version_t *out_version);

#ifdef __cplusplus
}
#endif

#endif
```

### 7.2 Opaque handles

Good:

```c
typedef struct domino_world domino_world_t;
typedef struct domino_replay domino_replay_t;
```

Bad:

```c
typedef struct domino_world {
    int tick;
    void *internal_state;
} domino_world_t;
```

### 7.3 Allocator model

```c
typedef void *(*domino_alloc_fn)(void *user, domino_u32 size);
typedef void (*domino_free_fn)(void *user, void *ptr);

typedef struct domino_allocator {
    void *user;
    domino_alloc_fn alloc;
    domino_free_fn free;
} domino_allocator_t;
```

Major systems take allocator explicitly.

### 7.4 ABI struct versioning

Every ABI-facing struct:

```text
size field
version field if needed
reserved fields if long-lived
explicit ownership
no raw platform types
```

### 7.5 Function naming

Use prefix namespaces:

```text
domino_engine_*
domino_runtime_*
domino_render_*
domino_platform_*
domino_package_*
domino_ui_*
dominium_game_*
dominium_domain_*
```

Avoid:

```text
init()
update()
load()
save()
run()
process()
manager()
helper()
common()
```

Better:

```text
domino_render_backend_create()
domino_package_manifest_parse()
dominium_economy_tick()
domino_replay_event_append()
domino_platform_file_open()
```

---

## 8. Determinism rules

Hard rules:

```text
No direct wall-clock access in engine/game truth.
No random without named deterministic RNG stream.
No unordered iteration where order affects results.
No floating-point in deterministic truth unless policy defines exact behavior.
No platform locale/timezone dependency.
No filesystem order dependency.
No pointer address ordering.
No thread-schedule-dependent output.
No silent fallback defaults.
```

Instead:

```text
engine/time = deterministic tick/time source
engine/replay = event log and replay proof
engine/proof = hashes, digests, invariants
runtime/platform = wall-clock, files, OS services
```

Deterministic truth surfaces should emit:

```text
proof hash
state hash
event log
replay transcript
deterministic diagnostic packet
```

---

## 9. Serialization and artifact compatibility

Do not serialize raw structs.

Use canonical serialization:

```text
stable field order
explicit endian
explicit integer widths
explicit string encoding
explicit unknown-field policy
explicit hash/canonicalization rule
explicit schema ID and version
```

Binary formats should include:

```text
magic
version
header size
flags
section table
content hash
schema ID
compatibility mode
signature/trust section if needed
```

Applies to:

```text
save files
replay logs
pack files
package files
snapshots
indexes
cache records
diagnostic bundles
```

---

## 10. Module contract pattern

Every reusable module should state:

```text
what it owns
what it does not own
public API, if any
private implementation boundaries
contracts obeyed
replaceability promise
determinism impact
tests/proofs
```

Minimal structure:

```text
module/
  README.md
  include/      if public API exists
  implementation files directly under module or submodules
  tests/        if module-local tests are useful
  fixtures/     only if justified
```

No repeated `src/`.

---

## 11. Build-system hygiene

CMake target names should reflect ownership:

```text
domino_engine_state
domino_runtime_render_software
domino_runtime_platform_win32
dominium_game_domain_economy
dominium_app_client
dominium_app_workbench
```

Avoid stale target names:

```text
appcore
shared_ui
legacy_lib
soft
stub
core
common
```

Rules:

```text
One target = one ownership module.
Target names follow directory ownership.
Apps link downward.
Engine does not link upward.
Runtime must not depend on apps.
Engine must not depend on runtime/game/apps.
```

---

## 12. Testing architecture

Required test families:

```text
boundary tests
ABI/public header compile tests
C89 compile tests
determinism tests
replay tests
serialization tests
schema tests
pack tests
migration tests
platform tests
renderer tests
fuzz/parser tests
golden tests
compatibility corpus tests
negative/refusal tests
```

Crucial missing family:

```text
public-header consumer tests
```

A small external consumer should include only installed/public headers and link only documented libraries. If it cannot build, the stable C API is not real.

---

## 13. Validation/proof gate ladder

Suggested gates:

### Local fast gate

```text
format/lint where applicable
python compile
strict root/layout validators
bad-root absence
no-src/source validator
forbidden-name validator
docs sanity
build boundary
include sanity
UI shell purity
ABI checks
```

### Build gate

```text
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
```

### Smoke gate

```text
ctest --preset verify -L smoke --output-on-failure
```

### Canon proof gate

```text
RepoX STRICT
TestX fast/survival invariants
worldgen lock verify
pack validator focused checks
schema validators
content validators
tools/docs taxonomy validators
```

### Full gate

```text
full CTest
compatibility corpus
public header consumer tests
artifact migration tests
pack/FAB validation
release/package proof
```

Feature work is:

```text
allowed for narrow lanes after canon proof + smoke
limited until full gate
blocked for release/trust-bearing surfaces until full gate + assurance criteria
```

---

## 14. Immediate recommended next strategic tasks

The next tasks should not be more broad directory reshuffling unless reconciliation finds active old paths.

### Highest-value next task

```text
PUBLIC-SURFACE-REGISTRY-01
```

Purpose:

```text
Declare every public surface and its stability, version, owner, dependency rules, and compatibility tests.
```

Deliverables:

```text
contracts/public_surface/public_surface.contract.toml
contracts/public_surface/surface.schema.json
docs/architecture/public_surface_registry.md
tools/validators/repo/check_public_surface.py
tests/contract/public_surface/
```

Acceptance:

```text
Every public header, schema, protocol, command, pack/save/replay format, and provider ABI has:
  owner
  stability
  version
  compatibility test
  allowed dependencies
  deprecation policy
```

### Then

```text
API-ABI-CANON-01
DEPENDENCY-DIRECTION-01
COMPATIBILITY-CORPUS-01
REPLACEMENT-PROTOCOL-01
CAPABILITY-REFUSAL-LAW-01
PROVIDER-MODEL-01
SCHEMA-PROTOCOL-LAW-01
ASSURANCE-PROFILE-00
```

---

## 15. Suggested prompt: PUBLIC-SURFACE-REGISTRY-01

Use this as the next major prompt if continuing the project:

```text
PUBLIC-SURFACE-REGISTRY-01

You are Codex working in the Dominium repository.

Task:
Create the public surface registry for Domino/Dominium so stable public contracts are explicitly declared, versioned, owned, and testable.

Goal:
Distinguish public, internal, private, generated, fixture, and historical surfaces. The registry must make it clear what the project promises to preserve and what implementations may freely replace.

Do not perform broad directory moves. Do not change public APIs unless required to register them. Do not invent stability promises for surfaces that are not ready.

Create:
contracts/public_surface/public_surface.contract.toml
contracts/public_surface/surface.schema.json
docs/architecture/public_surface_registry.md
tools/validators/repo/check_public_surface.py
tests/contract/public_surface/

Surface kinds:
c_header
abi_table
schema
registry
protocol
command
view
event
refusal
package_format
save_format
replay_format
profile_format
provider_abi
capability_id
diagnostic_code
release_artifact

Stability classes:
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

Each surface entry must declare:
id
kind
path
owner
stability
version
public_name
allowed_dependencies
forbidden_dependencies
compatibility_tests
conformance_tests
deprecation_state
replacement_target
notes

Initial registry should include only surfaces that can be confidently classified. Mark uncertain surfaces as provisional or internal. Do not overpromise.

Validator must:
- ensure registered public paths exist
- ensure public paths do not depend on forbidden layers
- ensure every stable public surface has at least one test/proof reference
- ensure generated/historical/fixture surfaces are not treated as stable public APIs
- report exact missing/stale entries

Run:
git status --short
AIDE validate
RepoX STRICT
public surface validator
include sanity
ABI checks
CMake verify build
smoke CTest

Commit:
feat(contracts): add public surface registry
```

---

## 16. What the next chat must understand

The next chat should not restart the directory debate. It should continue from these conclusions:

```text
Top-level roots are essentially settled.
No new top-level roots.
No src/source wrappers.
No generic junk drawers.
Contracts are law.
Docs explain law.
Runtime adapts.
Engine is deterministic substrate.
Game is Dominium meaning.
Apps are thin product shells.
Workbench is a production environment.
Tools validate/generate/migrate/audit.
Content is authored packs/assets/profiles/templates.
Archive preserves history/evidence only.
```

The remaining strategic work is:

```text
public surface registry
C89 ABI canon
dependency direction enforcement
compatibility corpus
replacement protocol
capability/refusal law
provider model
schema/protocol evolution law
assurance profile
full proof gate
```

---

## 17. Final one-page summary for the next chat

Dominium’s goal is not merely to be a game. It is to become a reusable Domino substrate with Dominium as one game/product family. The repo has undergone major canonical cleanup and is moving toward an OS-grade modular architecture. The top-level root model is now basically settled: apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, archive. Do not add roots or reintroduce src/source/common/shared/core/lib/data junk drawers.

The key doctrine is: freeze contracts, replace implementations, preserve artifacts, verify behavior. Stable public surfaces must include C89 APIs, ABI tables, schemas, protocols, command/view/event/refusal contracts, package/save/replay formats, capability IDs, provider ABIs, and artifact IDs. Private implementation files and directories should remain replaceable.

The next major maturity step is not more folder moves. It is a public surface registry and API/ABI governance: identify every public surface, classify stability, assign owner/version, enforce allowed dependencies, require compatibility/conformance tests, and document deprecation/replacement. Add C89 public header standards, dependency direction validator, compatibility corpus, replacement protocol, capability/refusal law, provider model, schema/protocol evolution law, and assurance levels.

Feature work is allowed only in limited lanes while full CTest and pack/FAB validation debt remain unresolved. Trust-bearing features need stronger gates. The next best task is PUBLIC-SURFACE-REGISTRY-01.

---

End of handoff.
