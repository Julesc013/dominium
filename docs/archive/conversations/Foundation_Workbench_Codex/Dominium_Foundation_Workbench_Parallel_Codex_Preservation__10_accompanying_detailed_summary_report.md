# Accompanying Human-Readable Detailed Summary and Continuity Report

**Chat label:** Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff  
**Date anchor:** 2026-05-27 Australia/Melbourne  
**Source scope:** This chat only, except where marked as project context or live-repo status previously checked during the conversation.  
**Reliability note:** This report is a human-readable companion to the preservation package. It summarizes the visible conversation and the previously generated package. Some earlier uploads or skipped transcript portions were unavailable at generation time, so live repo details should be rechecked before acting.

---

## 1. What this conversation was really about

This conversation captured a major transition in the Dominium project. Earlier project work had been dominated by repository cleanup, root-folder consolidation, AIDE installation, Codex task generation, build proof, internal pilot packaging, and repeated attempts to make the repository structurally safe. The user was frustrated because this phase had taken months and still seemed to block work on the actual game, Workbench, and product code.

The conversation gradually shifted away from “how do we move every bad folder?” toward a more durable model: **make the project contract-governed so folders and implementations can be replaced without breaking identity, saved artifacts, packs, modules, Workbench surfaces, or downstream games**.

The final architecture that emerged was:

```text
Domino    = reusable deterministic/runtime substrate
Dominium  = game/product family built on Domino
Workbench = production, validation, editing, inspection, packaging, evidence, and agent-control environment
AIDE      = repo/control-plane harness
Codex     = bounded patch executor
Contracts = law
Tests, replay, diagnostics, and evidence = proof
```

The most important rules were:

```text
Path is not identity.
Implementation is not contract.
UI is not authority.
Generated output is not source truth.
```

This matters because Dominium’s future depends on stable IDs, contracts, schemas, commands, capabilities, providers, modules, packs, artifacts, diagnostics, and proof. The private implementation can move or be replaced, but public identity and compatibility cannot drift silently.

---

## 2. The emotional and practical context

The user was not calmly asking for abstract architecture. The user was trying to stop a long-running refactor from consuming the project indefinitely.

A recurring theme was urgency. The user repeatedly expressed that the directory and root-structure cleanup had taken too long, and at points threatened to manually drag/drop folders if the assistant and Codex process failed to produce real progress. That context matters for future assistants: the user does not want more gentle open-ended planning when the project already has a decided path.

The correct future posture is:

- verify live repo state;
- identify the current next task;
- generate concrete Codex prompts with strict scope;
- keep prompts implementation/documentation/test focused;
- avoid full CTest unless necessary;
- avoid restarting solved debates;
- avoid asking for clarification unless genuinely blocking.

---

## 3. The repository cleanup arc

The early and middle parts of this chat dealt with the repo’s ugly historical roots. The project had accumulated top-level roots such as:

```text
core/
control/
data/
packs/
profiles/
bundles/
compat/
lib/
libs/
locks/
repo/
safety/
security/
specs/
updates/
meta/
governance/
ide/
performance/
validation/
modding/
models/
templates/
net/
```

The initial cleanup model was very cautious:

```text
inventory
→ classify
→ salvage map
→ move map
→ gate
→ apply
→ proof
```

This proved safe but slow. The user became impatient because the visible folder mess remained. The process then evolved into deterministic routing:

- semantically known files move to canonical owners;
- unknown or ambiguous files go to `archive/quarantine/<root>/`;
- bad roots should not remain as active source;
- active exceptions require owners and retirement plans.

Later live-state checks suggested that the visible root problem was largely resolved and that the project had moved to the next problem: **semantic governance inside the approved roots**.

The canonical source-root model became:

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

Generated/local only:

```text
.aide.local/
.dominium.local/
build/
out/
dist/
tmp/
__pycache__/
```

Future assistants should not restart root cleanup unless a live validator shows an active old-root violation.

---

## 4. The governance phase and Foundation Lock

Once the folder skeleton became acceptable, the focus shifted to the governance platform. The user and assistant converged on the need for a **Foundation Lock**: a proof gate showing that core repo law exists and validates before narrow product work resumes.

The Foundation layers included:

1. fast strict test tier;
2. public surface registry;
3. API/ABI canon;
4. dependency direction law;
5. command/refusal/result surface law;
6. diagnostic and evidence registry;
7. artifact identity law;
8. schema/protocol evolution law;
9. capability/refusal law;
10. provider model;
11. module/workbench/app composition law;
12. replacement protocol;
13. version/deprecation law;
14. mod/pack trust model;
15. portability matrix.

A live repo check during the conversation found Foundation Lock initially blocked by dependency-direction strict validation:

```text
358 violations
38 warnings
```

A later live check found that `FOUNDATION-CLOSEOUT-02` had closed Foundation Lock with warnings:

```text
dependency-direction strict: PASS, 0 violations, 68 warnings
fast strict: PASS
RepoX STRICT: PASS with stale AuditX warning
CMake configure/build: PASS through fast strict
smoke CTest: PASS through fast strict
full CTest: T4/full-gate debt
```

This was a major threshold. It meant narrow product slices could begin, but broad feature work remained blocked.

---

## 5. The technical baseline

The project moved away from C89/C++98 as the mainline rule.

The final baseline discussed was:

```text
Language:        C17 + C++17
Architecture:    64-bit source-native: x86_64 + arm64
Endian:          little-endian mainline only
ABI:             C-compatible, POD-only, versioned, no C++ ABI leakage
Data formats:    fixed-width, explicit little-endian, no padding, no pointer-sized fields
Simulation:      deterministic, fixed-point where authoritative, stable IDs, canonical ordering
Runtime:         provider/capability/refusal model
Renderer:        null + software baseline; GPU backends are replaceable providers
UI:              CLI/headless always; TUI/rendered/native shells are capability layers
Legacy targets:  constrained_native or contract_projection, not mainline constraints
```

C17 owns the stable deterministic and ABI-adjacent surfaces:

- fixed-width math and IDs;
- save/replay/wire records;
- renderer command IR;
- provider facades;
- canonical hashing.

C++17 owns higher-level implementation:

- game orchestration;
- domain systems;
- runtime services;
- providers;
- apps;
- Workbench;
- resource ownership;
- job systems;
- compiled tooling where useful.

The public ABI remains C-compatible. Stable formats must not use `size_t`, `long`, pointer values, native padding, object layout, address ordering, or pointer-derived identity.

---

## 6. Workbench’s role

Workbench became a major focus, but the critical decision was that **Workbench is not authority**.

Workbench is the richest human/agent interface over the system, but it must use the same command/result/refusal/diagnostic/evidence spine as CLI, TUI, headless, server/admin, tests, and future UI projections.

The conversation distinguished:

```text
component = source/build ownership unit
service   = callable runtime capability
provider  = replaceable implementation
pack      = distributable authored payload
module    = declared functional extension unit
workspace = large Workbench composition
app       = shipped product composition
artifact  = persisted versioned result
```

Workbench has:

```text
apps/workbench/shell/
apps/workbench/module/
apps/workbench/workspace/
```

Workbench modules include:

```text
validation/
pack_browser/
agent_board/
replay_trace/
renderer_lab/
package_planner/
evidence_viewer/
```

Workbench workspaces include:

```text
project_graph/
interface_studio/
module_foundry/
app_composer/
release_forge/
```

The first Workbench slice was `WORKBENCH-VALIDATION-SLICE-01`, which was reported as complete but narrow. It did not implement a broad Workbench shell, rendered GUI, native UI, runtime module loader, provider runtime, package runtime, gameplay, or release publication.

---

## 7. The transition to parallel Codex work

After Foundation Lock closed with warnings, the user wanted to stop queueing prompts one at a time. The assistant proposed a parallel worktree system.

Parallel workers must:

- use dedicated branches/worktrees;
- not push to `main`;
- not edit global AIDE latest files;
- write task-local evidence only;
- stay within allowed path lists;
- run targeted validators;
- avoid full CTest;
- commit locally;
- leave final merge to a coordinator.

Files parallel workers must not edit:

```text
.aide/context/latest-task-packet.md
.aide/context/latest-review-packet.md
.aide/reports/latest-dominium-status.md
.aide/reports/latest-warning-disposition.md
.aide/queue/current.toml
.aide/ledgers/migration_ledger.jsonl
docs/repo/POST_CONVERGE_NEXT_STEPS.md
docs/repo/FOUNDATION_LOCK.md
```

This enabled Wave 1 prompts.

---

## 8. Wave 1 parallel prompts

The assistant generated five major parallel Codex prompts:

1. `SERVICE-CONFORMANCE-LAW-01`
2. `DOCUMENT-PATCH-TRANSACTION-RUNTIME-01`
3. `PROJECT-GRAPH-SERVICE-01`
4. `COMPOSITION-RESOLVER-LAW-01`
5. `DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01`

A later pasted transcript reported these as complete, with `PASS` or `PASS_WITH_WARNINGS`.

### 8.1 Service conformance

Purpose: a provider/service/module is not available merely because it compiles or has a descriptor. It must pass a conformance kit.

### 8.2 Document/patch/transaction

Purpose: Workbench, AIDE, CLI, and tools must mutate structured state through:

```text
document
→ patch
→ dry run
→ validation
→ transaction apply
→ evidence packet
→ rollback handle
```

not ad hoc edits.

### 8.3 Project graph

Purpose: typed relationship graph across files, components, public surfaces, contracts, commands, services, providers, modules, packs, apps, tests, artifacts, evidence, and releases.

Project Graph is derived evidence, not authority.

### 8.4 Composition resolver

Purpose: composition is the product.

The chain:

```text
app descriptor
+ profile
+ packs
+ modules
+ providers
+ platform
+ renderer
+ trust policy
+ capabilities
→ composition resolver
→ selected providers
→ mounted packs
→ enabled modules
→ capability set
→ refusals/degradations
→ lockfile
→ evidence packet
```

### 8.5 Doctrine recovery matrix

Purpose: preserve long-running Dominium doctrine by mapping old ideas to current canon, without creating a competing master doctrine.

---

## 9. Doctrine preserved and still missing

The uploaded transcript/audit said most major old Dominium ideas were preserved in the repo:

- truth totality;
- sparse materialization;
- Truth / Perceived / Render separation;
- representation ladders;
- semantic ascent/descent;
- formalization chains;
- process-only mutation;
- cross-domain bridge law;
- ordinary life;
- institutions and civilization;
- pack-driven integration;
- explicit refusal/degradation.

Partial or missing areas include:

- deep primitives master doctrine;
- failure ontology master taxonomy;
- player-facing formalization workflows;
- ordinary-life grounding;
- domain constitutions;
- playable-baseline hardening;
- domain-by-domain verification.

The doctrine recovery matrix was generated to preserve those threads for later spec work.

---

## 10. Current next task

The latest pasted planning state said the next correct task is:

```text
COMMAND-RESULT-VIEW-SLICE-01
```

Why this comes next:

`WORKBENCH-VALIDATION-SLICE-01` proved a narrow command/result/diagnostic/evidence path, but the next missing bridge is:

```text
command result
→ semantic view
→ projection
→ CLI / headless / Workbench
```

This task should use `dominium.validation.run` if possible and prove that one command result can produce a semantic view projected consistently across multiple surfaces.

It must not implement:

```text
full Workbench shell
rendered GUI
native GUI
runtime view engine
package runtime
provider runtime
module loader
gameplay
renderer implementation
release publication
```

After it, the next checkpoint should be:

```text
PHASE-REVIEW-02
```

Then the runtime/product spine:

```text
PACKAGE-MOUNT-SLICE-01
REPLAY-PROOF-SLICE-01
BAREBONES-CLIENT-SHELL-01
RUNTIME-SPINE-REVIEW-01
```

---

## 11. What remains to do

### Immediate

- Verify current `origin/main`.
- Confirm whether `COMMAND-RESULT-VIEW-SLICE-01` has already run.
- Generate or execute `COMMAND-RESULT-VIEW-SLICE-01`.

### Next checkpoint

- Run `PHASE-REVIEW-02` after command-result-view.

### Product/runtime spine

- `PACKAGE-MOUNT-SLICE-01`
- `REPLAY-PROOF-SLICE-01`
- `BAREBONES-CLIENT-SHELL-01`
- `RUNTIME-SPINE-REVIEW-01`

### Presentation and UI law

- `PRESENTATION-CONTRACT-01`
- `PROJECTION-CONFORMANCE-01`
- `ACCESSIBILITY-CONTRACT-01`
- `TEXT-LOCALIZATION-CONTRACT-01`

### Workbench expansion

- `WORKBENCH-SHELL-01`
- `PROJECT-GRAPH-EXPLORER-01`
- `PACK-BROWSER-01`
- `AGENT-WORK-BOARD-01`

### Hardening

- `COMPATIBILITY-CORPUS-01`
- `PERFORMANCE-BUDGETS-01`
- `ASSURANCE-PROFILE-00`
- `RELEASE-PROMOTION-GATE-01`
- `FULL-GATE-DEBT-01`
- `POINTER-WIDTH-SERIALIZATION-AUDIT-01`
- `GENERATED-SOURCE-LAW-01`

### Doctrine/domain

- `SPEC-DEEP-PRIMITIVES-01`
- `SPEC-FAILURE-ONTOLOGY-01`
- `SPEC-PLAYER-FORMALIZATION-WORKFLOWS-01`
- `SPEC-REPRESENTATION-PROOF-01`
- `DOMAIN-CONSTITUTION-WAVE-01`

---

## 12. What a future assistant should do first

A future assistant should:

1. Verify live repo state.
2. Inspect the current AIDE queue/status/audit docs.
3. Confirm whether `COMMAND-RESULT-VIEW-SLICE-01` is still the next task.
4. If yes, generate the Codex prompt for that task as one large continuous text block.
5. Keep it narrow and targeted.
6. Do not launch broad Workbench UI or gameplay.
7. Avoid full CTest unless required.
8. Preserve the parallel-worker rules if using concurrent Codex chats.

---

## 13. Final package check summary

This companion report should be used alongside the original preservation package files. The original package already contains:

- manifest;
- full human-readable preservation report;
- context transfer packet;
- YAML spec sheet;
- registers;
- aggregator packet;
- reader brief;
- verification/audit;
- future chat bootstrap prompt;
- in-chat reader guide.

This new report gives a more narrative explanation of the entire conversation and is intended for human reading before diving into the registers.

