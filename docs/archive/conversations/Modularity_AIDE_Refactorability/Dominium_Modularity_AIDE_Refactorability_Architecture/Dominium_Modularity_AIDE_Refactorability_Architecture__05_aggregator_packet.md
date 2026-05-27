# Aggregator Packet — Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture

## Packet Metadata

* Chat label: Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial-to-good for visible current chat; no live repo inspection
* Confidence: 4/5 visible substance; 2/5 live repo facts
* Staleness risk: Medium
* Merge priority: High for architecture doctrine
* Main limitations: Prior generated files unavailable; live repo status unverified; some claims are pasted from earlier assistant outputs.

## Ultra-Condensed Carry-Forward Capsule

This chat should be merged as a major Dominium architecture/refactorability doctrine source. It establishes that Dominium should not be treated as a one-off indie project. It should be developed like a long-lived game/engine platform with stable contracts, replaceable implementations, portable data, deterministic proof, and AIDE-governed refactorability. The core user concern is avoiding another painful restructuring and making code reusable across Dominium products, future games on the same domino/Dominium engine, and potentially unrelated engine or game projects.

The source layout target is a stable constitutional root set: `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, with `dist/` generated or strictly governed. New top-level roots should be refused by default. Future work should occur inside ownership slots. Root names like `core/`, `lib/`, `libs/`, `packs/`, `profiles/`, `models/`, `modding/`, `security/`, `safety/`, `governance/`, `validation/`, `meta/`, `compat/`, `updates/`, and `performance/` should generally be split into existing roots rather than kept as top-level owners.

A central correction is the user’s rejection of XStack/AuditX/RepoX/TestX-style framing. The merged spec should not preserve those as durable architecture names. Instead, AIDE should be the repo-native control plane for restructuring: inventory, policies, queues, work units, move maps, salvage maps, path aliases, validators, evidence ledgers, and refactor history. Existing old tools and docs should be recycled, not ignored. They should be classified as keep/adapt/extract/convert/archive/drop, wrapped before rename, and migrated only with evidence.

The most important engineering doctrine is: paths are not identity. Contracts and manifests define identity. Durable artifacts need stable IDs, versions, schemas, content hashes where applicable, capability declarations, compatibility ranges, and migration/refusal policy. Apps should be thin. Runtime adapts host/platform/render/audio/input/network/storage/UI. Engine owns deterministic reusable substrate. Game owns Dominium-specific rules. Content is authored data, not runtime cache. Release contains recipes, not generated build products. Tools may inspect everything but must not become runtime dependencies.

For portability and modularity, stable C89-compatible ABI seams should be used where durable external boundaries are needed, with opaque handles, explicit allocators, versioned structs, stable error codes, and no C++/implementation structs in public ABI. Internals should remain flexible. Public APIs need stability levels: experimental, provisional, stable, frozen, deprecated, removed. Schemas and protocols should be versioned, negotiation-capable, and migration-tested. Capability negotiation should replace platform-era assumptions. Generated artifacts must be quarantined. Tests should cover ABI/header compilation, schema round trips, migrations, determinism, replay, save/load, package verification, renderer parity, and command/TUI/GUI parity.

The best next action is to verify live repo state, then implement AIDE-STRUCTURE-00 and AIDE-ARCH-00 non-invasively. Do not move implementation code first. Do not delete old tools. Do not trust pasted repo-status claims without verification. Do not treat every assistant recommendation as user-adopted doctrine until reviewed.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | AIDE as restructuring control plane | Decision | DECISION-02 | Central user correction and future refactor system | FACT | high |
| P0 | Stable root constitution | Decision | DECISION-01 | Prevents root sprawl and repeat cleanup | FACT/INFERENCE | high |
| P0 | Paths are not identity | Doctrine | DECISION-04 | Makes rewrites/refactors portable and cheap | INFERENCE | high |
| P0 | Product-line architecture | Doctrine | DECISION-05 | Supports reuse across products/games/projects | FACT | high |
| P0 | Recycle old tooling/docs/tests | Constraint | DECISION-03 | Avoids losing useful validators and policies | FACT | high |

## Workstream Summaries

* ID: WORKSTREAM-01
  * Name: Stable repo constitution
  * Objective: Define stable top-level ownership roots and refuse future root sprawl.
  * Current state: Conceptually defined in chat; needs implementation.
  * Desired end state: Contracts, docs, validators, and root admission policy exist and are enforced.
  * Priority: P0
  * Next action: see task register.

* ID: WORKSTREAM-02
  * Name: Distribution and install projection
  * Objective: Unify package, portable, installed, media, cache, rollback, bundle, save, and diagnostics layouts through logical roots.
  * Current state: Strongly described in pasted prior analysis; not verified against live repo.
  * Desired end state: One logical-root projection contract drives all physical layouts.
  * Priority: P0
  * Next action: see task register.

* ID: WORKSTREAM-03
  * Name: AIDE control plane
  * Objective: Use AIDE for migration, validation, evidence, queues, move maps, salvage maps, and refactor history.
  * Current state: User explicitly preferred AIDE over XStack-style framing.
  * Desired end state: AIDE owns restructuring workflow; old tools are wrapped and recycled.
  * Priority: P0
  * Next action: see task register.

* ID: WORKSTREAM-04
  * Name: Old tool/code/doc recycling
  * Objective: Inventory and classify XStack/AuditX/RepoX/TestX-style material instead of discarding it.
  * Current state: Conceptual plan only.
  * Desired end state: Useful assets kept/adapted/extracted/converted; bad names retired.
  * Priority: P1
  * Next action: see task register.

* ID: WORKSTREAM-05
  * Name: Reusable engine/product-line architecture
  * Objective: Separate code by reuse level across Dominium products, future games, and unrelated engine projects.
  * Current state: Outlined in final architecture response.
  * Desired end state: Reusable layers isolated from Dominium-specific game rules.
  * Priority: P0
  * Next action: see task register.

* ID: WORKSTREAM-06
  * Name: Contracts/API/ABI/schema/protocol discipline
  * Objective: Make public seams versioned, stable where promised, and negotiable.
  * Current state: Outlined as doctrine; implementation pending.
  * Desired end state: Contracts define identity and compatibility; public ABI seams are durable.
  * Priority: P0
  * Next action: see task register.

* ID: WORKSTREAM-07
  * Name: Naming and matrix cleanup
  * Objective: Use clean component names with version/status/format fields separated.
  * Current state: Discussed in pasted component-naming analysis.
  * Desired end state: No durable names like legacy/modern/compat/XStack/gl2/vk1/dx11-as-primary.
  * Priority: P1
  * Next action: see task register.

* ID: WORKSTREAM-08
  * Name: Determinism, testing, and proof matrix
  * Objective: Create deterministic, hermetic, replayable proof systems for engine, packages, saves, protocols, and renderers.
  * Current state: Discussed as best practice.
  * Desired end state: Refactors and releases have reproducible proof outputs.
  * Priority: P1
  * Next action: see task register.

* ID: WORKSTREAM-09
  * Name: Spec-book aggregation
  * Objective: Preserve this chat for later merging into a master Project Spec Book.
  * Current state: Activated by uploaded prompt.
  * Desired end state: Human report, registers, YAML spec, aggregator packet, and ZIP exist.
  * Priority: P0
  * Next action: see task register.

## Compact Registers for Merge

### Decisions

| ID | Decision | Status | Workstream | Label |
| --- | --- | --- | --- | --- |
| DECISION-01 | Use a stable top-level root constitution rather than ad hoc root growth. | accepted direction | WORKSTREAM-01 | FACT/INFERENCE |
| DECISION-02 | Treat AIDE as the restructuring control plane. | accepted by user framing | WORKSTREAM-03 | FACT |
| DECISION-03 | Recycle old tools/docs/tests rather than ignore or discard them. | accepted direction | WORKSTREAM-04 | FACT |
| DECISION-04 | Paths are not identity; contracts and manifests define identity. | strong recommendation | WORKSTREAM-05 | INFERENCE |
| DECISION-05 | Design Dominium as a product-line architecture, not a one-off game. | accepted objective | WORKSTREAM-05 | FACT |
| DECISION-06 | Use C89-compatible stable ABI seams, without forcing all internals to be C89. | recommendation | WORKSTREAM-06 | INFERENCE |
| DECISION-07 | Avoid durable architecture names based on temporary tooling or status labels. | accepted direction | WORKSTREAM-07 | FACT/INFERENCE |
| DECISION-08 | Future refactors should be AIDE work units with move maps and salvage maps. | recommendation aligned with user goal | WORKSTREAM-03 | INFERENCE |
| DECISION-09 | Apps should be thin; runtime adapts host; engine/game own truth. | strong recommendation | WORKSTREAM-05 | INFERENCE |
| DECISION-10 | Do not promise compatibility for every internal interface. | recommendation | WORKSTREAM-06 | INFERENCE |

### Tasks

| ID | Task | Priority | Urgency | Workstream | Label |
| --- | --- | --- | --- | --- | --- |
| TASK-01 | Implement AIDE-STRUCTURE-00 / repo constitution and refactorability framework. | P0 | U0 | WORKSTREAM-01 | FACT/INFERENCE |
| TASK-02 | Implement AIDE-ARCH-00 / modularity and reuse constitution. | P0 | U1 | WORKSTREAM-05 | FACT/INFERENCE |
| TASK-03 | Inventory existing XStack/AuditX/RepoX/TestX-style tooling and classify it. | P0 | U1 | WORKSTREAM-04 | FACT |
| TASK-04 | Wrap old checks behind AIDE before renaming them. | P1 | U1 | WORKSTREAM-03 | INFERENCE |
| TASK-05 | Define logical-root projection contracts for distribution/install/media/bundles. | P0 | U1 | WORKSTREAM-02 | INFERENCE |
| TASK-06 | Add boundary validators for apps/engine/game/runtime/contracts/content/tools. | P1 | U2 | WORKSTREAM-06 | INFERENCE |
| TASK-07 | Create component/module manifest pattern. | P1 | U2 | WORKSTREAM-07 | INFERENCE |
| TASK-08 | Define portability threat checks. | P1 | U2 | WORKSTREAM-08 | INFERENCE |
| TASK-09 | Verify live repo status before executing any concrete cleanup. | P0 | U0 | WORKSTREAM-01 | UNCERTAIN |
| TASK-10 | Merge this package into future master Project Spec Book. | P1 | U2 | WORKSTREAM-09 | FACT |

### Constraints

| ID | Constraint | Type | Hard/soft | Label |
| --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Source scope is this chat only unless Project-context is explicitly labelled. | reporting | hard | FACT |
| CONSTRAINT-02 | Do not treat assistant suggestions as user decisions unless accepted. | epistemic | hard | FACT |
| CONSTRAINT-03 | Future architecture should avoid root sprawl. | architecture | hard-ish | FACT/INFERENCE |
| CONSTRAINT-04 | Existing code/docs/tests should be recycled rather than ignored. | migration | hard | FACT |
| CONSTRAINT-05 | AIDE names must not contaminate product/runtime/game architecture. | architecture | soft-to-hard | INFERENCE |
| CONSTRAINT-06 | Portability and modularity are primary design goals. | technical | hard | FACT |
| CONSTRAINT-07 | Durable data and protocols need versioning and migration/refusal policy. | compatibility | hard-ish | INFERENCE |
| CONSTRAINT-08 | Generated outputs must be quarantined. | repo hygiene | hard-ish | INFERENCE |

### Open Questions

| ID | Question | Priority | Workstream | Label |
| --- | --- | --- | --- | --- |
| QUESTION-01 | What is the current live repo state and which of the pasted commit/status claims remain true? | P0 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-02 | What exact parts of old XStack/AuditX/RepoX/TestX tooling are useful? | P0 | WORKSTREAM-04 | FACT/UNCERTAIN |
| QUESTION-03 | Which APIs deserve stable/frozen compatibility promises? | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-04 | Where should domino-engine reusable code stop and Dominium-specific game code begin? | P0 | WORKSTREAM-05 | INFERENCE |
| QUESTION-05 | What generated artifacts are intentionally tracked versus accidental? | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-06 | What should become formal Project Spec Book requirements versus background context? | P1 | WORKSTREAM-09 | INFERENCE |

### Artifacts

| ID | Artifact | Type | Status | Carry forward? | Label |
| --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Pasted text.txt | uploaded prompt | available in this chat | yes | FACT |
| ARTIFACT-02 | Prior distribution/install layout analysis pasted by user | pasted assistant output | visible in chat, not independently verified | yes | FACT/UNCERTAIN |
| ARTIFACT-03 | Prior convergence/root cleanup analysis pasted by user | pasted assistant output | visible in chat, not independently verified | yes | FACT/UNCERTAIN |
| ARTIFACT-04 | Prior component naming/matrix analysis pasted by user | pasted assistant output | visible in chat | yes | FACT |
| ARTIFACT-05 | AIDE transition prompt/task proposal | assistant-generated prompt | visible in chat | yes, with user review | INFERENCE |
| ARTIFACT-06 | AIDE-STRUCTURE-00 prompt | assistant-generated prompt | visible in chat | yes | INFERENCE |
| ARTIFACT-07 | AIDE-ARCH-00 prompt | assistant-generated prompt | visible in chat | yes | INFERENCE |
| ARTIFACT-08 | This preservation package | generated files + ZIP | created in this turn | yes | FACT |

### Risks

| ID | Risk | Likelihood | Severity | Label |
| --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats assistant recommendations as user decisions. | medium | high | FACT |
| RISK-02 | Live repo claims from pasted text are stale or wrong. | medium | high | UNCERTAIN |
| RISK-03 | AIDE becomes another mythology instead of a control plane. | medium | medium-high | INFERENCE |
| RISK-04 | Old validators are renamed before being wrapped. | medium | high | INFERENCE |
| RISK-05 | Root constitution becomes too rigid. | low-medium | medium | INFERENCE |
| RISK-06 | Compatibility promises are too broad. | medium | medium-high | INFERENCE |
| RISK-07 | Reusable code remains tangled with Dominium-specific game rules. | medium-high | high | FACT/INFERENCE |
| RISK-08 | Generated artifacts leak into source roots. | medium | medium | INFERENCE |

### Verification Queue

| ID | Item | Suggested source/type | Priority | Label |
| --- | --- | --- | --- | --- |
| VERIFY-01 | Current live repo head, branch, validator status, and CTest status. | GitHub/Codex live repo inspection. | P0 | UNCERTAIN |
| VERIFY-02 | Existence and contents of docs referenced in pasted analyses, such as VIRTUAL_PATHS, INSTALL_MODEL, DIST_TREE_CONTRACT, PKG_FORMAT. | Live repo or uploaded docs snapshot. | P0 | UNCERTAIN |
| VERIFY-03 | Actual XStack/AuditX/RepoX/TestX paths and behavior. | Repo inventory and test runs. | P0 | UNCERTAIN |
| VERIFY-04 | Current component matrix names and statuses. | Repo search. | P1 | UNCERTAIN |
| VERIFY-05 | External best-practice references used in prior answer. | Official docs for CMake, Bazel, Chromium, Linux, SemVer, Google Testing. | P2 | UNCERTAIN |
| VERIFY-06 | Which prior generated files or old uploads are unavailable/expired. | Conversation file list / user re-upload. | P1 | UNCERTAIN |

## Possible Cross-Chat Duplicates

Repo layout convergence, distribution layout, component matrices, renderer/platform naming, AppShell virtual roots, `.dompkg` semantics, AIDE governance, Codex task prompts, previous old-chat handoff packages.

## Possible Cross-Chat Conflicts

Earlier chats may preserve XStack/AuditX/RepoX/TestX terms more strongly. Earlier directory layouts may have different root names. Earlier platform/render priorities may be more implementation-specific. Some previous repo-status claims may conflict with current live repo.

## Spec Book Integration Guidance

Feed this into chapters on repository architecture, AIDE governance, engine modularity, API/ABI/contracts, distribution/install layout, testing/determinism, compatibility, and refactorability. Formalize root constitution, AIDE refactor process, path-is-not-identity doctrine, public API stability levels, and generated-output policy. Keep pasted repo status as background until verified. Do not merge unverified commit IDs or CTest status as current facts.

## Aggregator Warnings

Do not treat this as live repo verification. Do not flatten assistant recommendations into decisions. Do not resurrect XStack as a desired architecture name. Do not ignore the user’s explicit requirement to recycle existing code/docs/tests. Do not compress away the product-line reuse framing.
