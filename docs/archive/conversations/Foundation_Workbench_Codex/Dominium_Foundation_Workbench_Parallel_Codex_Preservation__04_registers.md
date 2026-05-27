# Registers — Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Dominium / Domino / Workbench / AIDE master architecture | Preserve the final system model: Domino substrate, Dominium product family, Workbench environment, AIDE harness, contracts law, proof by tests/replay/evidence. | Foundation/governance spine mostly established; broad feature work blocked; narrow slices authorized after Foundation Lock. | A deterministic, contract-governed simulation platform with replaceable implementations and evidence-backed product slices. | active | P0 | High | FACT |
| WORKSTREAM-02 | Canonical repository skeleton and root cleanup | Keep the repo in the closed ownership-root model and avoid junk-root recurrence. | Root cleanup reportedly no longer the main issue; earlier router/move work replaced bad roots or quarantined unknowns. | No active old root junk drawers; canonical roots remain stable; generated/local roots stay out of source authority. | mostly-complete | P0 | Medium | FACT/UNCERTAIN |
| WORKSTREAM-03 | Foundation Lock and governance spine | Ensure public surfaces, ABI, dependency direction, commands, diagnostics, artifacts, schema/protocol, capability/refusal, providers, modules/apps, replacement, versioning, trust, and portability are validated. | Foundation Lock reportedly PASS_WITH_WARNINGS after dependency repair; fast strict passes; full CTest remains T4 debt. | Foundation Lock remains the baseline gate for narrow product work; full gate reserved for release/trust. | active | P0 | Medium-High | FACT |
| WORKSTREAM-04 | Fast strict proof loop | Use a fast, meaningful normal gate instead of full CTest for every task. | Fast strict reportedly passes 32 commands in ~272–315 seconds depending audit; full CTest remains T4 debt. | Normal changes use targeted validators + fast strict; release/trust changes use full gate. | active | P0 | High | FACT |
| WORKSTREAM-05 | Language and native architecture baseline | Use C17/C++17, 64-bit source-native, little-endian, C-compatible ABI, fixed-width persisted formats. | C17/C++17 reportedly live; 64-bit architecture policy prompted/in-flight or pending verification. | Mainline full native products are x86_64/arm64; 32-bit/vintage targets are constrained/projection/archive-runner. | active | P0 | Medium | FACT/UNCERTAIN |
| WORKSTREAM-06 | Parallel Codex/AIDE workflow | Run isolated Codex workers in parallel with strict path allowlists and coordinator merges. | Wave 1 prompts generated; later pasted state says Wave 1 effectively complete. | Multiple safe branches produce task-local evidence; coordinator serially merges and runs fast strict. | active | P0 | Medium | FACT/UNCERTAIN |
| WORKSTREAM-07 | Workbench validation and command/view spine | Build a narrow Workbench/product spine through registered commands, typed results, semantic views, projections, diagnostics, and evidence. | WORKBENCH-VALIDATION-SLICE-01 reportedly complete; next task is COMMAND-RESULT-VIEW-SLICE-01. | One command/result/view/projection path works across CLI/headless/text/Workbench without private bypass. | active | P0 | Medium | FACT/UNCERTAIN |
| WORKSTREAM-08 | Service conformance, document/patch, project graph, composition law | Define supporting laws needed before bigger Workbench/product work. | Prompts generated; pasted state says complete or pass-with-warnings. | Conformance, document/patch/transaction, graph, and composition models inform later runtime/product slices. | active | P1 | Medium | FACT/UNCERTAIN |
| WORKSTREAM-09 | Runtime/product spine slices | Build package mount, replay proof, and barebones client shell after command/result/view proof. | Planned; not yet executed in visible chat. | Package/profile/content mount proof; deterministic replay proof; minimal client status/refusal shell. | planned | P1 | High | FACT |
| WORKSTREAM-10 | Presentation/accessibility/localization spine | Define semantic presentation, projection conformance, accessibility, and text/localization before rich UI. | Planned after runtime/product checkpoint. | CLI/TUI/headless/rendered/native projections share semantics; accessibility and localization not late afterthoughts. | planned | P2 | High | FACT |
| WORKSTREAM-11 | Doctrine recovery and domain constitution | Preserve long-running design doctrine and instantiate it into domain constitutions. | Prompt generated; uploaded transcript says most doctrine preserved but deep primitives/failure/domain constitutions remain partial. | Doctrine recovery matrix guides deep primitives, failure ontology, representation proof, domain constitutions, playable baseline. | active/planned | P2 | Medium | FACT |
| WORKSTREAM-12 | Future game/product/domain expansion | Eventually build playable baseline and domain/game slices: survival, fabrication, maintenance, settlements, logistics/economy, institutions, knowledge, civilization, conflict, offworld. | Broad feature work currently blocked; future order planned. | Gameplay/features enter as domain constitutions, bridges, capabilities, representations, failure models, proofs, not ad hoc features. | future | P3 | Medium | INFERENCE/FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Dominium should be a deterministic contract-governed simulation platform, not merely a game repo. | final | Repeated synthesis accepted by user across conversation. | Enables modularity, replacement, proof-driven development. | Enables modularity, replacement, proof-driven development. | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Domino is the reusable substrate; Dominium is the product family; Workbench is production environment; AIDE is control-plane harness. | final | Repeated summaries and user acceptance. | Prevents Workbench/Dominium from becoming vague everything-platform. | Prevents Workbench/Dominium from becoming vague everything-platform. | WORKSTREAM-01 | High | FACT |
| DECISION-03 | Contracts are law; tests/replay/evidence are proof. | final | Core architectural mantra from conversation. | Docs explain, generated output is evidence unless promoted. | Docs explain, generated output is evidence unless promoted. | WORKSTREAM-01 | High | FACT |
| DECISION-04 | Path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. | final | Explicitly repeated and used in prompts. | Stable IDs/contracts/registries/manifests own identity; paths are replaceable. | Stable IDs/contracts/registries/manifests own identity; paths are replaceable. | WORKSTREAM-01 | High | FACT |
| DECISION-05 | Keep the closed canonical source-root set. | final-with-caveats | Root cleanup discussions and repo convergence. | No new top-level modules/plugins/services/sdk roots unless future contract introduces them. | No new top-level modules/plugins/services/sdk roots unless future contract introduces them. | WORKSTREAM-02 | High | FACT |
| DECISION-06 | Unknown files should not remain in bad roots; route to archive/quarantine rather than guess active ownership. | final for cleanup phase | MOVE-ROUTER discussion. | Prevents unknown files blocking cleanup or being wrongly active. | Prevents unknown files blocking cleanup or being wrongly active. | WORKSTREAM-02 | Medium | FACT |
| DECISION-07 | Mainline language baseline is C17 + C++17, not C89/C++98. | final/live per checks | Language baseline discussion and later repo state checks. | C-compatible public ABI remains; C89/C++98 becomes research/historical. | C-compatible public ABI remains; C89/C++98 becomes research/historical. | WORKSTREAM-05 | Medium | FACT/VERIFY |
| DECISION-08 | Full native products should be 64-bit source-native: x86_64 + arm64; 32-bit is constrained/projection/archive-runner. | decided, policy encoding pending/in-flight | 64-bit policy discussion. | Avoid old-toolchain/memory/matrix drag; keep pointer-width out of persisted law. | Avoid old-toolchain/memory/matrix drag; keep pointer-width out of persisted law. | WORKSTREAM-05 | Medium | FACT/UNCERTAIN |
| DECISION-09 | Little-endian mainline with explicit little-endian persisted/protocol encodings. | decided | 64-bit/platform discussion. | Avoid expensive big-endian support; formats are explicit. | Avoid expensive big-endian support; formats are explicit. | WORKSTREAM-05 | Medium | FACT |
| DECISION-10 | Fast strict is normal dev gate; full CTest is T4/full-gate debt. | final | Test-time frustration and Foundation Lock model. | Prompts use targeted validators; full CTest only release/trust or specific need. | Prompts use targeted validators; full CTest only release/trust or specific need. | WORKSTREAM-04 | High | FACT |
| DECISION-11 | Foundation Lock gates narrow product work; broad feature work remains blocked. | final for current phase | Foundation closeout state. | Narrow slices allowed; not gameplay/renderer/native GUI/release. | Narrow slices allowed; not gameplay/renderer/native GUI/release. | WORKSTREAM-03 | High | FACT |
| DECISION-12 | Workbench must use registered commands/services/evidence, not private validators/tools. | final | Workbench role discussions. | Prevents Workbench from becoming authority or bypass. | Prevents Workbench from becoming authority or bypass. | WORKSTREAM-07 | High | FACT |
| DECISION-13 | Use parallel Codex worktrees with strict worker rules. | active decision | User explicitly requested concurrent Codex chats. | Speed up setup while limiting merge conflicts. | Speed up setup while limiting merge conflicts. | WORKSTREAM-06 | High | FACT |
| DECISION-14 | Wave 1 prompt set: service conformance, document/patch/transaction, project graph, composition resolver, doctrine recovery. | executed in chat; completion user-reported | Prompts generated one by one. | Foundation hardening runs in parallel. | Foundation hardening runs in parallel. | WORKSTREAM-06 | High | FACT |
| DECISION-15 | Next task after Wave 1 is COMMAND-RESULT-VIEW-SLICE-01. | current plan | Latest pasted transcript. | Bridge command result to semantic view/projection before package mount. | Bridge command result to semantic view/projection before package mount. | WORKSTREAM-07 | Medium | FACT/UNCERTAIN |
| DECISION-16 | Do not start broad Workbench UI before command/result/view/projection law. | final for sequencing | Avoid duplicate CLI/Workbench/TUI/rendered logic. | Presentation spine first. | Presentation spine first. | WORKSTREAM-07 | High | FACT |
| DECISION-17 | Composition is the product. | architectural decision | Composition resolver discussion. | Apps compose profiles/packs/modules/providers/capabilities into lockfiles/evidence. | Apps compose profiles/packs/modules/providers/capabilities into lockfiles/evidence. | WORKSTREAM-08 | High | FACT |
| DECISION-18 | Doctrine recovery should map old doctrine to current canon rather than create a competing master doctrine. | final for doctrine phase | Uploaded transcript and doctrine prompt. | Preserve old requirements without overriding contracts. | Preserve old requirements without overriding contracts. | WORKSTREAM-11 | High | FACT |
| DECISION-19 | Major game features must enter as domain constitutions/bridges/capabilities/representation/failure/proof, not ad hoc features. | future design law | Domain and doctrine discussions. | Prevents shallow feature scripts and semantic drift. | Prevents shallow feature scripts and semantic drift. | WORKSTREAM-12 | Medium | FACT/INFERENCE |
| DECISION-20 | Do not put domino/dominium in every path; use project prefixes for public C symbols and fully qualified stable IDs. | final naming law | Naming discussion. | Short readable paths; collision-proof public symbols/IDs. | Short readable paths; collision-proof public symbols/IDs. | WORKSTREAM-01 | High | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify live repo state before issuing next prompt | P0 | U0 | assistant/new chat |  | GitHub connector or local git status | Confirm current main, queue, in-flight tasks. | Check latest commits and queue docs. | WORKSTREAM-06 | FACT |
| TASK-02 | Generate COMMAND-RESULT-VIEW-SLICE-01 prompt | P0 | U0 | assistant | Wave 1 complete or verified, Workbench validation slice complete | Current command/result/view contracts | Large continuous Codex prompt. | Use dominium.validation.run if possible. | WORKSTREAM-07 | FACT |
| TASK-03 | Run PHASE-REVIEW-02 after command/result/view slice | P0 | U1 | Codex/coordinator | COMMAND-RESULT-VIEW-SLICE-01 complete | Wave 1 audits and command-result-view audit | Review conflicts/regressions/readiness. | Compare tasks and validators. | WORKSTREAM-06 | FACT |
| TASK-04 | PACKAGE-MOUNT-SLICE-01 | P1 | U1 | Codex | PHASE-REVIEW-02 green, composition law, artifact identity, pack trust | One pack/profile/content artifact | Fixture-driven mount decision and lock/report. | Define narrow prompt after phase review. | WORKSTREAM-09 | FACT |
| TASK-05 | REPLAY-PROOF-SLICE-01 | P1 | U1 | Codex | command/evidence model | Simple deterministic command or validation command | One replay/proof/hash artifact. | Choose minimal deterministic path. | WORKSTREAM-09 | FACT |
| TASK-06 | BAREBONES-CLIENT-SHELL-01 | P1 | U1 | Codex | package/replay slices | Client app status surfaces | Minimal client shell status/refusal with no optional content. | Keep no gameplay/non-rendered. | WORKSTREAM-09 | FACT |
| TASK-07 | RUNTIME-SPINE-REVIEW-01 | P1 | U1 | coordinator | Package/replay/client slices | Slice audits | Runtime/product spine readiness decision. | Run fast strict and review docs. | WORKSTREAM-09 | FACT |
| TASK-08 | PRESENTATION-CONTRACT-01 | P2 | U2 | Codex | runtime spine review green | View/action/projection needs | Presentation contract and projection law. | Generate scoped prompt. | WORKSTREAM-10 | FACT |
| TASK-09 | PROJECTION-CONFORMANCE-01 | P2 | U2 | Codex | presentation contract | Projection fixtures | Projection conformance fixtures for CLI/TUI/headless/rendered/native placeholders. | Generate scoped prompt. | WORKSTREAM-10 | FACT |
| TASK-10 | ACCESSIBILITY-CONTRACT-01 | P2 | U2 | Codex | presentation contract | Accessibility requirements | Accessibility contract for labels/focus/keyboard/contrast/reduced motion. | Generate scoped prompt. | WORKSTREAM-10 | FACT |
| TASK-11 | TEXT-LOCALIZATION-CONTRACT-01 | P2 | U2 | Codex | presentation contract | Text/message catalogs | Localization/text ID policy. | Generate scoped prompt. | WORKSTREAM-10 | FACT |
| TASK-12 | WORKBENCH-SHELL-01 | P2 | U2 | Codex | presentation spine review | Workbench shell law and modules | Minimal non-rendered/text-first shell. | Do not build full rendered GUI. | WORKSTREAM-07 | FACT |
| TASK-13 | PROJECT-GRAPH-EXPLORER-01 | P2 | U2 | Codex | project graph law, Workbench shell | Graph query fixtures | Workbench graph summary/impact view. | Keep derived, not authority. | WORKSTREAM-07 | FACT |
| TASK-14 | PACK-BROWSER-01 | P2 | U2 | Codex | package mount proof, Workbench shell | Pack list/detail commands | Pack browser view over pack capabilities/trust/deps. | Scoped prompt later. | WORKSTREAM-07 | FACT |
| TASK-15 | AGENT-WORK-BOARD-01 | P2 | U2 | Codex | AIDE task docs, Workbench shell | AIDE work unit/evidence docs | Agent task/evidence board; no autonomous execution. | Scoped prompt later. | WORKSTREAM-07 | FACT |
| TASK-16 | COMPATIBILITY-CORPUS-01 | P2 | U2 | Codex | runtime/product spine | old artifacts/fixtures | Seed compatibility corpus. | Not complete corpus initially. | WORKSTREAM-03 | FACT |
| TASK-17 | PERFORMANCE-BUDGETS-01 | P2 | U2 | Codex | fast strict | budget categories | Performance budget contracts/validator. | Later hardening. | WORKSTREAM-04 | FACT |
| TASK-18 | ASSURANCE-PROFILE-00 | P2 | U2 | Codex | governance spine | DIL levels | Assurance levels and validator. | Before high-trust release/plugin work. | WORKSTREAM-03 | FACT |
| TASK-19 | RELEASE-PROMOTION-GATE-01 | P2 | U2 | Codex | release law | promotion states | Release promotion gate. | Before public release. | WORKSTREAM-03 | FACT |
| TASK-20 | FULL-GATE-DEBT-01 | P2 | U2 | Codex | full gate/hardening | Full CTest failures | Classify/fix full CTest debt. | Do not block narrow slices now. | WORKSTREAM-04 | FACT |
| TASK-21 | POINTER-WIDTH-SERIALIZATION-AUDIT-01 | P2 | U2 | Codex | PORTABILITY-ARCH-POLICY-02 complete | source inventory | Audit pointer-sized persisted truth hazards. | Inventory + targeted fixes only. | WORKSTREAM-05 | FACT |
| TASK-22 | SPEC-DEEP-PRIMITIVES-01 | P3 | U2 | Codex/planning | doctrine matrix | old doctrine/current docs | Master deep primitives doctrine. | After product spine starts moving. | WORKSTREAM-11 | FACT |
| TASK-23 | SPEC-FAILURE-ONTOLOGY-01 | P3 | U2 | Codex/planning | doctrine matrix | failure model gaps | Cross-domain failure ontology. | Later planning. | WORKSTREAM-11 | FACT |
| TASK-24 | DOMAIN-CONSTITUTION-WAVE-01 | P3 | U2 | Codex/planning | deep primitives/failure ontology | domain template | First domain constitutions. | Later planning. | WORKSTREAM-12 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | No broad feature work until authorized | project sequencing | hard | Foundation docs/plan | Blocks gameplay/render/native GUI/public release until proper slices/gates. | high | High | FACT |
| CONSTRAINT-02 | Full CTest is not routine gate | testing | hard/practical | User preference and Foundation model | Use targeted validators/fast strict; full CTest for T4/release/trust. | medium | High | FACT |
| CONSTRAINT-03 | Parallel workers must not push to main | workflow | hard | Parallel plan | Avoid race/merge corruption. | high | High | FACT |
| CONSTRAINT-04 | Parallel workers must not edit global AIDE latest files | workflow | hard | Parallel prompt rules | Prevents conflicts; coordinator updates latest state. | high | High | FACT |
| CONSTRAINT-05 | Contracts are law | architecture | hard | Core doctrine | Docs/generation cannot override contracts. | high | High | FACT |
| CONSTRAINT-06 | Workbench is not authority | architecture | hard | Workbench discussions | Workbench must use commands/services/evidence. | high | High | FACT |
| CONSTRAINT-07 | Public ABI is C-compatible | technical | hard | Language/ABI decision | No C++ ABI/STL/exceptions across stable boundary. | high | High | FACT |
| CONSTRAINT-08 | Persisted formats use fixed-width explicit little-endian fields | technical | hard | 64-bit/endian discussion | No pointer-sized truth. | high | High | FACT |
| CONSTRAINT-09 | Mainline full native is 64-bit x86_64/arm64 | technical | hard after policy | 64-bit decision | 32-bit is constrained/projection/research. | medium | Medium | FACT/UNCERTAIN |
| CONSTRAINT-10 | No silent fallback | runtime/capability | hard | Capability/refusal law | Missing capabilities produce typed refusal/degradation/evidence. | high | High | FACT |
| CONSTRAINT-11 | Generated output is not source truth | repo hygiene | hard | Core doctrine | Generated artifacts ignored/archive/evidence unless promoted. | medium | High | FACT |
| CONSTRAINT-12 | Do not reintroduce old junk roots | repo structure | hard | Root cleanup decision | Use canonical roots only. | medium | High | FACT |
| CONSTRAINT-13 | Use project prefixes for public symbols, not every directory/file | naming | preferred/hard for public API | Naming discussion | Paths stay readable; public symbols/IDs collision-proof. | low | High | FACT |
| CONSTRAINT-14 | Do not ask unnecessary clarifying questions | communication | soft/hard preference | User profile | Proceed with assumptions unless blocked. | medium | High | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, source-grounded, audit-ready answers | communication | explicit | strong | Use citations and labels; avoid vague reassurance. | high | FACT |
| PREF-02 | Start responses with model label and timestamp | format | explicit | strong | Use `GPT-5.5 Pro — YYYY-MM-DD HH:MM:SS TZ`. | medium | FACT |
| PREF-03 | Neutral, direct prose | tone | explicit/system | strong | Avoid excessive warmth/flattery. | low | FACT |
| PREF-04 | Distinguish FACT / INFERENCE / UNCERTAIN | epistemic | explicit | strong | Label uncertain repo state/live checks. | high | FACT |
| PREF-05 | Generate one large continuous txt/code block for Codex prompts | output format | explicit | strong | When asked for next prompt, produce a single block. | medium | FACT |
| PREF-06 | Prompts must do implementation/docs/targeted testing, not just reports | task style | explicit | strong | Include deliverables and validation. | high | FACT |
| PREF-07 | Rarely run full test suites | testing | explicit | strong | Prefer fast strict and targeted validators. | medium | FACT |
| PREF-08 | Do not stop at blockers without classification/repair attempts | task style | explicit | strong | Codex prompts should classify/repair/narrow blockers. | high | FACT |
| PREF-09 | Prioritize getting to Workbench/code soon | planning | explicit | strong | Avoid endless governance before useful slices. | medium | FACT |
| PREF-10 | Do not lose old doctrine/context | memory | explicit | strong | Use doctrine matrix and preservation packages. | high | FACT |
| PREF-11 | Challenge/correct framing when needed | epistemic | explicit profile | medium | If user’s framing conflicts with evidence, say so. | medium | FACT |
| PREF-12 | Use web/GitHub checks for live repo/current facts | evidence | explicit/system | strong | Verify before relying on current repo state. | high | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Is Wave 1 actually merged/live on origin/main? | Next task depends on true repo state. | User-pasted transcript says complete. | Final handoff did not verify after paste. | Check live repo commits/docs. | P0 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-02 | Has `PORTABILITY-ARCH-POLICY-02` completed and merged? | Determines if pointer-width audit can start and whether command/view prompt must account for it. | Prompt was issued and user said repo was working on it. | Completion not verified in final handoff. | Check latest commits/audits. | P0 | WORKSTREAM-05 | UNCERTAIN |
| QUESTION-03 | Has `COMMAND-RESULT-VIEW-SLICE-01` already been run? | Avoid duplicate prompt. | Latest visible instruction asks what's next before prompt generated. | No prompt generated in old chat after final state? | Check repo queue/user state. | P0 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-04 | Should next prompt be parallel worker or coordinator/main prompt? | Determines path rules and global AIDE edits. | Parallel workflow active. | Current next task likely product slice, may need worktree. | Ask only if live repo does not clarify. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-05 | How complete is the Workbench validation slice implementation? | Command/result/view slice should build on it. | Pasted transcript says it validates contract-schema target via typed command result. | Need actual files to know exact command/schemas. | Inspect audit/docs. | P0 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-06 | What specific current command/result schema should view slice use? | Avoid inventing new command if dominium.validation.run exists. | Transcript suggests use dominium.validation.run. | Need repo file names/paths. | Search contracts/command and workbench validation audit. | P0 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-07 | Which warnings remain acceptable? | Avoid treating warnings as blockers or ignoring real debt. | Known: dependency-direction warnings, stale AuditX, AIDE review refs, full CTest debt. | Exact latest warnings may differ. | Check latest warning disposition docs. | P1 | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-08 | Should doctrine matrix be merged into future spec book now or later? | Preservation/aggregation plan depends on it. | A doctrine matrix prompt was generated and reportedly complete. | No master spec book yet. | Ask when user requests aggregation. | P2 | WORKSTREAM-11 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | `Pasted markdown.md` / current uploaded preservation prompt | uploaded file | Contains the preservation/package instructions for this final handoff. | loaded/current | user upload | yes | Cited in final report. | FACT |
| ARTIFACT-02 | `Pasted text.txt` uploaded earlier in final context | uploaded file | Contained older audit/transcript about doctrine recovery and repo state. | partially represented | user upload | yes | The system indicated some previous uploads expired, but a current uploaded file was available. | UNCERTAIN |
| ARTIFACT-03 | `FOUNDATION_LOCK.md` | repo doc | Foundation status and allowed/blocked work. | live checked earlier | repo | yes | Reported PASS_WITH_WARNINGS after closeout. | FACT |
| ARTIFACT-04 | `FOUNDATION_CLOSEOUT_02.md` | repo audit | Foundation closeout result and warnings. | live checked earlier | repo | yes | Foundation closed with warnings; Workbench slice authorized. | FACT |
| ARTIFACT-05 | `LANGUAGE_BASELINE.md` | repo doc | C17/C++17 language baseline. | live checked earlier | repo | yes | Verify before language-sensitive work. | FACT/VERIFY |
| ARTIFACT-06 | `PORTABILITY-MATRIX-01` reports/docs | repo audit/contracts | Portability matrix and platform rows. | live checked earlier | repo | yes | 64-bit policy builds on it. | FACT |
| ARTIFACT-07 | `SERVICE-CONFORMANCE-LAW-01` prompt | generated prompt | Parallel worker prompt for service/provider conformance law. | generated in chat | assistant | yes | Likely run/completed per user paste. | FACT/UNCERTAIN |
| ARTIFACT-08 | `DOCUMENT-PATCH-TRANSACTION-RUNTIME-01` prompt | generated prompt | Parallel worker prompt for document/patch/transaction law. | generated in chat | assistant | yes | Likely run/completed per user paste. | FACT/UNCERTAIN |
| ARTIFACT-09 | `PROJECT-GRAPH-SERVICE-01` prompt | generated prompt | Parallel worker prompt for project graph law. | generated in chat | assistant | yes | Likely run/completed per user paste. | FACT/UNCERTAIN |
| ARTIFACT-10 | `COMPOSITION-RESOLVER-LAW-01` prompt | generated prompt | Parallel worker prompt for composition resolver/lockfile law. | generated in chat | assistant | yes | Likely run/completed per user paste. | FACT/UNCERTAIN |
| ARTIFACT-11 | `DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01` prompt | generated prompt | Parallel worker prompt for doctrine recovery matrix. | generated in chat | assistant | yes | Likely run/completed per user paste. | FACT/UNCERTAIN |
| ARTIFACT-12 | `COMMAND-RESULT-VIEW-SLICE-01` proposed task | planned prompt | Next task to generate. | not yet generated in visible old chat | assistant/user plan | yes | Immediate next step if live repo agrees. | FACT/UNCERTAIN |
| ARTIFACT-13 | Final handoff generated before current preservation request | in-chat handoff | Prior COMPLETE CHAT HANDOFF with continuity state. | generated in chat | assistant | yes | This current package supersedes and expands it. | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Manual drag/drop directory cleanup | Rejected | Too risky; breaks Git history/path refs/validators/proof | Final | Only as emergency followed by repair, not recommended | WORKSTREAM-02 | FACT |
| REJECTED-02 | Tiny sequential micro-moves forever | Superseded | Too slow; user frustration; easy candidates exhausted | Final for current phase | Use only for high-risk targeted repairs | WORKSTREAM-02 | FACT |
| REJECTED-03 | C89/C++98 as mainline | Superseded | Target floor now supports C17/C++17; old constraint too costly | Final unless new target floor changes | Retro/research lanes | WORKSTREAM-05 | FACT |
| REJECTED-04 | 32-bit full-native mainline | Deprioritized | Matrix/memory/toolchain cost; modern systems are 64-bit | Final for mainline | Constrained-native if real demand/evidence | WORKSTREAM-05 | FACT |
| REJECTED-05 | Literal OS framing | Refined | Dominium is not a hardware OS | Final wording | Use “simulation operating environment/platform” carefully | WORKSTREAM-01 | FACT |
| REJECTED-06 | Workbench as authority | Rejected | Would bypass contracts/commands/services | Final | None | WORKSTREAM-07 | FACT |
| REJECTED-07 | Top-level `modules/` or `plugins/` | Rejected for now | Module identity is contract/manifest, not root folder | Tentative | External SDK/module repo may alter later | WORKSTREAM-08 | FACT |
| REJECTED-08 | Full Workbench GUI before command/view spine | Rejected | Would create duplicate presentation logic | Final for sequencing | After presentation/projection conformance | WORKSTREAM-07 | FACT |
| REJECTED-09 | Full CTest as everyday gate | Rejected | Too slow/noisy; T4 debt | Final | Release/full-proof only | WORKSTREAM-04 | FACT |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future chat restarts old root cleanup debate | Wastes time, frustrates user, repeats settled work. | medium | high | Verify current repo; focus on next task unless validator shows root issue. | WORKSTREAM-02 | FACT |
| RISK-02 | Future chat treats Workbench as authority | Creates bypasses and private tool coupling. | medium | high | Force commands/services/evidence spine. | WORKSTREAM-07 | FACT |
| RISK-03 | Parallel workers edit shared AIDE latest files | Merge conflicts and stale status. | high | medium-high | Use parallel-worker rules; coordinator updates latest files. | WORKSTREAM-06 | FACT |
| RISK-04 | Prompt runs full CTest unnecessarily | Consumes time, may fail broad debt, slows progress. | medium | medium | Use targeted validators/fast strict. | WORKSTREAM-04 | FACT |
| RISK-05 | Assistant assumes user-pasted repo state is current | May duplicate or skip tasks incorrectly. | medium | high | Always verify live repo before next prompt. | WORKSTREAM-06 | FACT |
| RISK-06 | Governance expands forever before product work | Project stalls again. | medium | high | After minimal spine, do narrow product slices. | WORKSTREAM-07 | FACT |
| RISK-07 | Product work starts before view/projection spine | Duplicate CLI/Workbench/TUI/rendered systems emerge. | medium | high | Run COMMAND-RESULT-VIEW-SLICE-01 next. | WORKSTREAM-07 | FACT |
| RISK-08 | C++17 features break macOS 10.9.5 floor | Portability claims become false. | low-medium | medium | Maintain restricted C++17 library policy and validators. | WORKSTREAM-05 | FACT |
| RISK-09 | Pointer-width values leak into persisted formats | Breaks 32/64/portable/replay compatibility. | medium | high | Run pointer-width serialization audit after arch policy. | WORKSTREAM-05 | FACT |
| RISK-10 | Old doctrine gets forgotten during implementation | Long-term vision drifts into shallow features. | medium | high | Use doctrine recovery matrix and domain constitutions. | WORKSTREAM-11 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Latest `origin/main` commit and queue status | Needed before generating next prompt. | GitHub/local git | P0 | WORKSTREAM-06 | FACT |
| VERIFY-02 | Completion/merge state of `PORTABILITY-ARCH-POLICY-02` | Determines if pointer-width audit can run and if queue advanced. | GitHub/local git/audit docs | P0 | WORKSTREAM-05 | FACT |
| VERIFY-03 | Completion/merge state of Wave 1 tasks | User pasted complete, but verify before acting. | GitHub/local git/audit docs | P0 | WORKSTREAM-06 | FACT |
| VERIFY-04 | Exact command/result schemas from `WORKBENCH-VALIDATION-SLICE-01` | Needed for `COMMAND-RESULT-VIEW-SLICE-01` prompt. | Repo search/audit docs | P0 | WORKSTREAM-07 | FACT |
| VERIFY-05 | Current warning disposition | Avoid masking new vs known warnings. | AIDE latest warning docs | P1 | WORKSTREAM-03 | FACT |
| VERIFY-06 | Whether full CTest debt changed | May matter for release/full gate later. | CTest audit/queue docs | P2 | WORKSTREAM-04 | FACT |
| VERIFY-07 | Actual current CMake language standards if language-sensitive task arises | There was earlier contradiction. | CMakeLists/presets | P1 | WORKSTREAM-05 | FACT |
| VERIFY-08 | Availability of previously uploaded/expired files | Some previous uploads expired; ask user to re-upload if needed. | Chat file state | P2 | WORKSTREAM-11 | FACT |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Repo restructuring frustration | User wanted bad root folders gone and threatened manual moves | Forced move from slow cautious refactor to faster deterministic routing | Historical context and motivation | High |
| 2 | AIDE control plane | AIDE became repo/refactor/control harness | Enabled evidence-backed tasks and Codex prompts | Still central | High |
| 3 | Root routing | Unknown files route to quarantine; known files to canonical owners | Finished visible root cleanup path | Mostly historical | Medium |
| 4 | Foundation/governance pivot | Problem shifted from directories to public/private/stable/internal governance | Set up Foundation Lock | Active context | High |
| 5 | Language baseline pivot | C17/C++17 replaced C89/C++98 mainline | Modernizes code while retaining C ABI | Active | Medium |
| 6 | 64-bit policy | Full native products become x86_64/arm64 source-native | Avoids old platform constraints | Active/policy follow-up | Medium |
| 7 | Foundation blocker | Dependency direction blocked Foundation Lock | Protected architecture boundaries | Repaired per later state | Medium |
| 8 | Foundation closeout | Foundation Lock PASS_WITH_WARNINGS | Authorized narrow product slices | Active | Medium |
| 9 | Parallel Codex plan | Multiple worktrees/workers with strict rules | Accelerates setup | Active | High |
| 10 | Wave 1 prompts | Service conformance, docpatch, graph, composition, doctrine prompts generated | Parallel hardening | Reportedly complete | Medium |
| 11 | Workbench validation slice | First narrow Workbench command/result proof reportedly complete | Product slice begins | Active foundation for next task | Medium |
| 12 | Next task identified | COMMAND-RESULT-VIEW-SLICE-01 selected | Bridges command results to views/projections | Immediate | Medium |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| System Architecture | Domino/Dominium/Workbench/AIDE split | DECISION-01..04 | Requirement | High | Core framing |
| Repository Governance | Canonical roots and no bad roots | DECISION-05..06 | Requirement/context | Medium | Verify live repo |
| Language/ABI | C17/C++17, C-compatible ABI | DECISION-07 | Requirement | Medium | Verify actual build if needed |
| Portability | 64-bit source-native, legacy projections | DECISION-08..09 | Requirement/open issue | Medium | Architecture policy may be pending |
| Testing/Proof | Fast strict vs full gate | DECISION-10 | Requirement | High | Important for prompts |
| Workbench | Workbench as command/evidence surface | DECISION-12, TASK-02 | Requirement | High | Next slice |
| Parallel Workflow | Branch/worktree rules | DECISION-13 | Requirement/context | High | Operational spec |
| Composition | Composition is the product | DECISION-17 | Requirement | High | Product architecture |
| Doctrine | Doctrine recovery matrix | DECISION-18 | Context/open issue | Medium | Use for spec book |
| Domains | Domain constitutions and deep primitives | TASK-22..24 | Open issue | Medium | Future chapters |
