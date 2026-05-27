# Dominium / Domino Canonical Structure — Accompanying Detailed Human Summary

**Generated:** 2026-05-27 21:03:35 AEST  
**Scope:** This conversation’s accessible content, the prior generated handoff package, visible user status reports, and uploaded/mounted summaries.  
**Purpose:** A human-readable companion report that explains what happened in the conversation, what was decided, what was done, what was deferred, and what the next continuation chat should preserve.

---

## 1. Executive Status

The conversation started as a directory-structure emergency and ended as a broader architecture-and-proof program for Dominium and the reusable Domino substrate.

The main outcome is:

```text
Domino Framework = contracts + public headers + service/provider law + conformance tests.
Dominium = the game/product family built on Domino.
Workbench = production/editing/validation/evidence environment.
AIDE = repo/control-plane harness.
```

The structure is no longer primarily a root-chaos problem. The canonical top-level root model has been established and repeatedly defended:

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

The most important current status from the conversation:

```text
Canonical structure: credible, PASS_WITH_WARNINGS.
Major old active path debt: mostly cleared.
Fast strict / CMake / smoke: reported passing in latest maintenance lanes.
Full CTest / T4 release gate: still not green.
Broad feature work: still blocked.
Narrow governed work: allowed only under the proof/queue model.
```

The single most important rule to preserve:

```text
Path is not identity.
Implementation is not contract.
UI is not authority.
Generated output is not source truth.
```

---

## 2. Conversation Narrative

### 2.1 Initial problem: repo structure blocked real work

The user began from the position that months of planning and refactoring had not produced a clean enough repo to continue development. The user was especially frustrated that prior attempts kept adding new root directories and reintroducing `src/` and `source/` folders, which had already been identified as a core failure mode.

The early goal was to determine the best future-proof directory layout for Dominium. The first answers proposed broad structures, routing maps, and distribution/install/media layouts. The user rejected proposals that reintroduced root sprawl, long ambiguous paths, source wrappers, vague folders, or status words in active paths.

That rejection hardened the core root doctrine:

```text
No root src/.
No root source/.
No nested first-party src/.
No generic common/shared/misc/lib/core/data junk drawers.
No new top-level roots without contract approval.
```

### 2.2 Source layout versus distribution/install layout

The conversation clarified that source repo layout is separate from:

```text
release dist output
.dompkg files
compressed archives
portable installs
installed desktop/server layouts
read-only media layouts
cache/staging/rollback layouts
save/instance/replay/diagnostic bundles
symbols/provenance layouts
```

The source repo should not contain install/runtime roots such as:

```text
store/
instances/
saves/
exports/
cache/
ops/
media/
```

Those are projections of virtual roots, not source ownership roots.

### 2.3 Canonical root model

The conversation converged on the durable root model:

```text
apps       thin product shells
engine     deterministic substrate
game       Dominium game meaning/law/domain
runtime    services, providers, projections, platform/render/storage/input/audio/package infrastructure
contracts  machine-readable law
content    authored payloads: packs, profiles, domains, themes, assets, templates
docs       explanation, not law
tests      proof and fixtures
tools      validators, codegen, migration, release, audit
scripts    thin automation wrappers
cmake      build-system support
external   third-party source/provenance
release    release definitions, profiles, packaging, signing, updates
archive    retained historical/generated/superseded material
```

This root model became the basis for all later architecture.

### 2.4 Massive cleanup prompts and status reports

Many Codex/AIDE prompts were generated to fix actual directories, not only document the ideal state. The prompts included cleanup of runtime names, game rules, engine include boundaries, schema taxonomy, content packs, Workbench naming, AIDE scan boundaries, tools taxonomy, docs taxonomy, RepoX/TestX stale paths, full remediation, and final canonical structure passes.

The user reported many task results and commits. Some important reported commits/statuses include:

```text
6e0dd93f263815667135bbf94b445c44cff6f733
  refactor(repo): finalize canonical structure

52ac5707e
  repo: enforce service-first provider structure

1406490bba4a8db617911f54cc85a8e939d29baa
  refactor(repo): finish canonical structure cleanup

3243fab7d7e4b9c32dc296a2583d4c5fa5ad8301
  tests: route full-gate legacy path expectations

ce9ca005f5922fd562f7f4c1aeb3240edd2d4823
  repo: define Domino framework boundary
```

The reported outcomes moved the repo from obvious active root chaos to `PASS_WITH_WARNINGS` structure credibility.

### 2.5 Shift from folders to public-surface governance

The user asked how to make code portable, modular, extensible, and reusable across not just Dominium but other games and engine projects. The conversation moved from folders to public surface governance:

```text
public surface registry
C-compatible ABI rules
dependency-direction validation
compatibility corpus
replacement protocol
capability/refusal law
provider model
schema/protocol evolution law
assurance profiles
fast strict and full release gates
```

The key doctrine became:

```text
Freeze public contracts.
Replace private implementations.
Preserve artifacts.
Verify behavior.
```

### 2.6 Domino Framework versus Dominium Game

The conversation then clarified that Domino is the reusable substrate/framework and Dominium is one game/product family. The user considered a new `framework/` root, but the final decision rejected it.

Accepted doctrine:

```text
Domino Framework is not a top-level framework/ source root.
Domino Framework = contracts + public headers + service/provider law + conformance tests.
```

The public API homes are:

```text
engine/include/domino/     deterministic substrate public headers
runtime/include/domino/    runtime/service/provider public headers
game/include/dominium/     game/product-specific public headers where needed
```

A future SDK can be generated from registered public surfaces, likely under `release/sdk/` or equivalent, but not as a new active root unless explicitly contracted.

### 2.7 Language baseline

The conversation moved from old C89/C++98 ideas to:

```text
Mainline language baseline: C17 + C++17
Public ABI boundary: C-compatible, POD-only, versioned, no C++ ABI leakage
Architecture: 64-bit first, little-endian first, x86_64 + arm64 first
```

C17 should own boring stable law:

```text
ABI-facing structs
packets
save/replay records
fixed-point math
stable IDs/handles
renderer command IR
low-level facades
```

C++17 should own machinery:

```text
game orchestration
runtime services
providers
renderer/platform backends
apps
Workbench
tools
resource ownership
composition/profile resolution
```

The important carry-forward is not to expose C++ classes, STL containers, exceptions, templates, or compiler object layout across stable ABI/data boundaries.

### 2.8 Workbench, modules, packs, and composition

The user brought in Workbench brainstorming around Project Editor, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, and related modules. The conversation clarified the vocabulary:

```text
component = source/build ownership unit
service   = callable runtime capability
provider  = replaceable implementation
pack      = distributable authored payload
module    = declared functional extension unit
workspace = large Workbench composition
app       = shipped product composition
artifact  = persisted/versioned object
```

The key rule:

```text
A folder can contain a component implementation.
A manifest defines a module.
A pack can provide modules.
An app composes modules, providers, services, and packs.
A workspace presents workflows over modules and services.
```

Reusable modules do not live under `apps/workbench`. Workbench modules are Workbench UI/presentation modules only. General module law lives under `contracts/module/`, and module payloads may be delivered through `content/packs/.../modules/`.

### 2.9 Presentation and projection model

The chat refined the UI architecture so CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench, CI, server/admin, and AIDE project the same semantic truth.

Final spine:

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

Projection modes belong under runtime implementation, not semantic contract roots:

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

Do not create separate contract worlds for `contracts/tui`, `contracts/rendered`, or `contracts/native`.

### 2.10 Raylib, SDL2, Lua, ImGui and provider architecture

The user asked how raylib, SDL2, Lua, and other libraries should fit. The final doctrine:

```text
Dominium owns service contracts.
Providers satisfy service contracts.
Profiles select providers.
Third-party libraries are fenced.
Apps stay generic.
```

Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and ImGui are providers, not architecture. Correct structure:

```text
external/upstream/<third_party>/
runtime/<service>/providers/<provider>/
contracts/provider/
contracts/capability/
contracts/schema/runtime/<service>/
release/profiles/<profile>.toml
content/profiles/<runtime_profile>.toml
apps/<product>/
```

Use names like:

```text
sdl2 now, sdl as family
raylib for broad provider
rlgl for low-level raylib GL abstraction
rlsw for raylib software renderer provider
win32 for Windows API provider, windows as OS family
direct3d11 for renderer provider, direct3d as family
opengl33 for direct OpenGL 3.3 provider, opengl as family
lua54 or lua55 for concrete script provider, lua as family
```

Third-party headers and types are forbidden in:

```text
engine/
game/
contracts/
content/
saves/replays/packs/public ABI/stable data law
```

### 2.11 Framework boundary

The user then considered whether the framework approach implied `framework/`, `engine/domino_reference/`, and `game/dominium/` roots. The final answer was no.

Corrected model:

```text
Domino Framework = public-surface package generated from contracts and public headers.
Domino Reference Implementation = current engine/ + runtime/.
Dominium Game = current game/ + content/ + apps/.
Providers = runtime/<service>/providers/<provider>.
Profiles = release/content profile descriptors.
```

The user later reported a commit defining the Domino framework boundary and adding a validator that guards against top-level `framework/` and `sdk/`.

### 2.12 Current proof posture

The latest visible statuses indicate:

```text
Canonical structure: PASS_WITH_WARNINGS
Provider structure: PASS_WITH_WARNINGS
Domino framework boundary: PASS
Full-gate legacy path subset: PASS
Fast strict / AIDE / CMake / smoke: mostly PASS by report
RepoX/fast-strict stale evidence/launcher marker debt: still blocking in a later status
Full CTest/T4: still not green
Feature readiness: LIMITED
Broad feature/release readiness: NO
```

A future assistant must verify latest live repo state before acting.

---

## 3. What Was Done

The conversation produced both reasoning and executable task prompts. The user reported actual maintenance runs and commits. The main completed categories were:

1. **Canonical structure cleanup** — major old active paths routed away; top-level roots normalized.
2. **Runtime/game/engine include cleanup** — old runtime names, `game/rules`, and engine include leakage were reportedly removed in active paths.
3. **Schema residual routing** — 130+ residual schema paths reportedly moved into canonical categories in one major cleanup pass.
4. **Test taxonomy and full-gate retired-root routing** — stale tests expecting retired roots were updated, and a `check_full_gate_legacy_paths.py` validator was added.
5. **Provider structure** — service-first provider structure, release provider profiles, provider policy/docs, and validators were added.
6. **Domino framework boundary** — framework defined as contracts/public headers/provider-service law, not a root; guards added against `framework/` and `sdk/`.
7. **Structure report integrity** — validators and reports were discussed/added to prevent mixed stale tree exports.
8. **Handoff package** — prior preservation files were generated, and this companion report now extends them.

---

## 4. What Was Put Off for Later

The following were not finished or intentionally deferred:

```text
Full CTest/T4 release proof.
Stale AuditX/identity evidence refresh.
Launcher pack-verification marker debt.
Storage/package provider split.
Actual raylib/SDL2/Lua provider implementations.
Provider conformance suites beyond skeleton/planned warnings.
Projection conformance.
Presentation contract completion if not already done.
Public header ABI promotion warnings.
Pack internal layout content/ vs data/ final law.
AIDE state-like directory classification.
Runtime/engine residual session/serialization/foundation taxonomy.
Broad Workbench UI.
Runtime module loader.
Provider runtime implementation beyond planned structure.
Package runtime.
Gameplay expansion.
Renderer implementation beyond provider planning.
Native GUI.
Release publication.
```

The deliberate policy was to stop broad structure churn once the active tree became credible and then move to targeted maintenance and narrow governed product slices.

---

## 5. Final Canonical Root Doctrine

Active roots:

```text
.aide/
.aide.local.example/
.github/
.vscode/
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

Forbidden active roots:

```text
src/
source/
sources/
framework/
sdk/
modules/
plugins/
services/
profiles/
labs/
core/
control/
data/
lib/
libs/
packs/
profiles/
bundles/
meta/
validation/
governance/
performance/
models/
templates/
net/
ide/
```

Allowed exceptions:

```text
archive/legacy/
archive/generated/
archive/historical/
archive/quarantine/
docs/compatibility/
contracts/compatibility/
external/upstream or external/vendor third-party source preserving upstream layout
tests/fixtures intentionally modeling old layouts
finite documented compatibility shims
```

---

## 6. Final Architectural Laws

```text
Path is not identity.
Implementation is not contract.
UI is not authority.
Generated output is not source truth.
Module identity is not path.
Pack identity is not path.
Provider identity is not implementation directory.
App identity is not executable filename.
Workspace identity is not layout file.
Commands are behavioral boundaries.
Documents/snapshots/results/patches are data boundaries.
Diagnostics/evidence are audit boundaries.
Contracts and tests decide stability.
```

---

## 7. Final Provider Directory Doctrine

Best pattern:

```text
external/upstream/<third_party>/
runtime/<service>/providers/<provider>/
contracts/provider/
contracts/capability/
contracts/schema/runtime/<service>/
release/profiles/<profile>.toml
content/profiles/<runtime_profile>.toml
apps/<product>/
```

Example runtime layout:

```text
runtime/platform/providers/sdl2/
runtime/platform/providers/raylib/
runtime/input/providers/sdl2/
runtime/input/providers/raylib/
runtime/render/providers/null/
runtime/render/providers/software/
runtime/render/providers/rlsw/
runtime/render/providers/raylib/
runtime/render/providers/rlgl/
runtime/render/providers/opengl33/
runtime/render/providers/direct3d11/
runtime/audio/providers/raudio/
runtime/script/providers/lua54/
runtime/ui/providers/raygui/
```

Do not use app paths like:

```text
apps/client/rendered/raylib/
apps/workbench/raylib/
```

Provider choices live in profiles.

---

## 8. Current Status in Plain Language

The repo is much healthier. The broad directory crisis appears to be over. The structure is not perfect, and the proof pipeline is not full green. But the project now has a credible canonical root model, structure validators, provider structure doctrine, framework boundary, and a path toward actual Workbench/client/engine/game implementation.

The correct next mindset is no longer:

```text
We need one more giant directory refactor.
```

It is:

```text
We need targeted proof hygiene and governed implementation slices.
```

---

## 9. Recommended Immediate Next Tasks

Depending on current live state:

### If fast-strict/RepoX is blocked

```text
FAST-STRICT-EVIDENCE-MARKER-REPAIR-01
```

Scope:

```text
Refresh/retire stale AuditX/identity evidence.
Fix launcher pack-verification marker debt.
Do not modify directory structure broadly.
Rerun AIDE, RepoX, fast strict, CMake, smoke.
```

### If fast-strict is green

```text
PROJECTION-CONFORMANCE-01
```

Scope:

```text
Prove CLI/text/rendered/native/headless projections over command/result/view/evidence contracts.
```

### Maintenance after that

```text
FULL-CTEST-AUDIT-NONPATH-01
PACK-INTERNAL-LAYOUT-CANON-01
STORAGE-PACKAGE-PROVIDER-SPLIT-01
PUBLIC-HEADER-ABI-PROMOTION-01
AIDE-STATE-CLASSIFICATION-01
```

---

## 10. Things Future Assistants Must Not Do

```text
Do not add framework/ as a source root.
Do not add top-level modules/, plugins/, services/, profiles/, labs/, or sdk/.
Do not reintroduce src/ or source/.
Do not treat raylib, SDL2, Lua, ImGui, raygui, rlgl, rlsw, or raudio as architecture law.
Do not put reusable modules under apps/workbench.
Do not make Workbench authority.
Do not encode provider choices into app directory names.
Do not declare PASS_WITH_WARNINGS as full green.
Do not start broad feature work while full proof and current queue say it is blocked.
```

---

## 11. Verification Checklist for a New Chat

Before doing any work, verify:

```text
Current HEAD and branch.
Worktree clean/dirty state.
AIDE doctor/validate.
RepoX strict / fast strict.
Canonical structure validator.
Dependency-direction validator.
Provider structure validator.
Third-party include validator.
CMake verify/build.
Smoke CTest.
Full CTest status or last full-gate audit.
Current .aide/queue/current.toml.
Whether stale AuditX/identity evidence remains.
Whether launcher pack-verification marker debt remains.
```

Do not rely on old uploaded `dir_tree.json` files without checking report integrity.

---

## 12. Package Contents

This updated bundle includes the prior preservation package files plus this companion report and a bundle inventory with SHA-256 hashes.
