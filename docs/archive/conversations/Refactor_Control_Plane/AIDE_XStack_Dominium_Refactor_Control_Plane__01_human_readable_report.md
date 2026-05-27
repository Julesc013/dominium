# COMPLETE CHAT PRESERVATION REPORT — AIDE, XStack, and Dominium Refactor Control Plane

## 0. Coverage and Reliability Assessment

| Field | Assessment |
| --- | --- |
| Chat label | AIDE, XStack, and Dominium Refactor Control Plane |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only, except live GitHub checks explicitly labelled as current repo verification |
| Apparent access | Partial-to-broad visible chat context; not guaranteed full hidden transcript |
| Previously generated files available? | Canvas documents exist in this conversation but not as direct downloadable files until this package |
| Uploaded files or artifacts present? | Yes: current Pasted text.txt; earlier uploads expired |
| Contains future plans? | Yes |
| Contains decisions? | Yes |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium-High for external tools/repo state; mitigated by current GitHub checks |
| Extraction confidence | 4/5 for visible chat substance; lower for expired uploads |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | Some earlier uploaded files expired; exact raw re-analysis not available; live repos may advance after package creation |

### Limitations in plain language

FACT: This package is based on the visible chat context, the user-provided preservation prompt in `Pasted text.txt`, canvas summaries created in this chat, and live GitHub checks performed during this chat. FACT: several older uploaded files expired, including earlier PDFs and source ZIPs. Their contents are represented here only from the visible discussion and earlier extracted summaries, not from fresh reinspection. UNCERTAIN: the live AIDE and Dominium repositories may have advanced after the latest checks used in this package. For current implementation work, the first action should be to verify repository HEAD and relevant files again.

## 1. One-Page Orientation

This chat was a long-running architecture, workflow, and project-control discussion around how to use AI coding tools more effectively, how to evolve Dominium’s XStack governance system, and how to build AIDE as a portable repo-native operating layer. It began with practical questions about using Codex Pro, the Codex VS Code extension, ChatGPT project spaces, the ChatGPT/Codex apps, Visual Studio, and the API. The user wanted a better way to develop projects, perhaps concurrently and across tools, without manually handing prompts from ChatGPT to Codex.

The conversation quickly shifted from simple prompt engineering toward harness engineering. The central lesson became that high-quality agentic development depends less on one perfect prompt and more on the surrounding system: repo instructions, task contracts, memory, tool permissions, worktree isolation, evidence packets, validation, review gates, branch discipline, and deterministic run paths. This framing then became the lens for evaluating Codex, Claude Code, OpenHands, Continue, oh-my-codex, claw-code, claude-mem, Graphify, and other systems.

A major middle phase focused on XStack. XStack began as a Dominium-specific governance stack grown out of TestX, then expanded into RepoX, AuditX, and other concepts. We initially explored making XStack a general portable metaharness, but that proved too large and too Dominium-shaped. The accepted resolution was that XStack should remain Dominium’s strict local profile and proving ground, while AIDE becomes the new portable public layer.

AIDE itself also changed direction. It was first imagined broadly as an Automated Integrated Development Environment: perhaps a desktop app, extension family, multi-agent runtime, daemon, service, or control plane. Over time, the plan narrowed into something more practical: AIDE should first be Profiles + Harness + Compatibility + Dominium Bridge. That means AIDE defines repo contracts in `.aide/`, compiles those contracts into current tool-facing artifacts, validates and migrates them, produces compact task and evidence packets, and later may grow into Runtime, Gateway, Service, Commander, and IDE hosts only after its smaller layer proves useful.

The latest Dominium-specific thread reframed AIDE as the restructuring and execution control plane for the messy Dominium repo. Dominium had completed CONVERGE and POST-CONVERGE work that improved layout authority and build proof, but it remained physically messy, with root exceptions and CTest/RepoX blockers. The conclusion was that AIDE should now control refactors through root inventories, per-file classification, salvage maps, move maps, path aliases, migration ledgers, and validation gates. XStack/AuditX/RepoX/TestX should not be deleted; their useful checks should be wrapped, classified, migrated, and retired behind AIDE adapters.

The future relevance of this chat is high. It defines the operating doctrine for AIDE, the relationship between AIDE and XStack, the immediate Dominium cleanup sequence, the longer AIDE Q35-Q57 roadmap, the branch/commit/workunit discipline, the versioning/capability model, and the anti-patterns to avoid. A future reader must understand one key idea: AIDE is not being built as another coding agent first. It is being built as the repo-native operating layer that lets humans, Codex, Claude Code, local tools, and future agents work through stable contracts, evidence, and validation.

## 2. The Story of the Conversation

### 2.1 From tool workflow to harness doctrine

The chat opened with the user describing a workflow: paying for Codex Pro, using the Codex VS Code extension on one project at a time, and using ChatGPT project spaces to generate prompts that were manually fed into Codex. The user had also installed the ChatGPT and Codex apps and Visual Studio Community. The initial question was whether there was a better, more professional, more integrated way to develop projects.

The first conclusion was that the user’s workflow worked but was not optimal. ChatGPT should be used for architecture, research, task design, documentation, review, and high-level reasoning. Codex should handle bounded repo-local implementation, testing, review, and worktree tasks. API/Responses/Agents-style systems could later support durable automation. This was the first move away from manual prompt relay and toward structured work.

The user then asked about optimizing prompts for GPT-5.3/GPT-5.4 and later supplied advice about harness engineering. That advice argued that teams succeed by engineering the environment around agents: tools, docs, linters, feedback loops, memory, and observability. The conversation accepted the core point: the model is not the whole system; the harness is the multiplier.

### 2.2 From harness ideas to XStack metaharness

The user proposed a rich stack: repo tree as topology, AGENTS.md as law, skills as procedures, MCP as integration bus, Responses as orchestration substrate, hosted shell as execution, evals as truth filter, CI/merge queue as integration governor, and recursive subagents working across branches and machines. The response refined this into bounded delegation: task graphs, evidence packets, branch leases, role separation, traces, eval layers, and privilege separation. The important correction was that unbounded recursive agents are not the goal; bounded tasks, contracts, evidence, and integration governance are.

The discussion then mapped these ideas onto Dominium’s XStack. We considered adding HarnessX, XPlan, XExec, MergeX, ContextX, SkillX, TaskX, BridgeX, SessionX, PermitX, DoctorX, TraceX, and more. Over time this became too many public concepts. We simplified toward higher-level planes and then eventually concluded that XStack should not be the general product at all.

### 2.3 External research inputs

The user supplied or referenced many external projects and reports: Claude Code leak mirrors, claw-code, oh-my-codex, claude-code-from-source, claude-mem, OpenHands, Continue, Graphify, prompt archives, and leak/resource guides. The repeated pattern was: use them for pattern mining, not as foundations. oh-my-codex looked like a useful Codex-facing workflow/runtime reference. claw-code looked useful as research/parity scaffolding, not a base. Claude Code leak analysis confirmed harness patterns: coordinator-worker, tool partitioning, memory, hooks, remote sessions, and multi-agent orchestration. Graphify looked useful as an optional graph-analysis backend, not a canonical memory layer. claude-mem contributed ideas for observer-driven typed memory and progressive disclosure.

The Grug Brained Developer became a design filter: avoid complexity, avoid premature abstraction, do small safe refactors, prefer integration tests, invest in logging, and respect existing structures before tearing them down. This influenced the decision to narrow AIDE and not overbuild runtime/hosts too early.

### 2.4 XStack becomes Dominium profile; AIDE becomes public layer

The user eventually named AIDE: Automated Integrated Development Environment. The accepted split became: XStack remains Dominium’s strict local governance/proof profile; AIDE becomes the portable public layer. AIDE would live in its own repo, be usable as a standalone repo pack, later as CLI/app/extensions, and eventually perhaps a runtime/service/host system.

But AIDE was narrowed again: AIDE v0 should not be a full coding agent. It should be a portable repo harness/profile standard plus compiler/adapters, validator, bakeoff kit, and Dominium bridge. Later, after more AIDE development, the plan matured into AIDE Core / Hosts / Bridges with internal Core bands: Contract, Harness, Runtime, Compatibility, Control, SDK. The first shipped stack remained Contract/Profile + Harness + Compatibility + Dominium Bridge.

### 2.5 Dominium repo convergence and root recycling

The user then integrated live Dominium repo state. CONVERGE had improved layout authority but not finished physical cleanup. Later POST-CONVERGE tasks improved native build proof: VS2022/v143 configure and build pass, native binaries are produced, but full CTest remains blocked by `invariant_units_present`, `inv_repox_rules`, and wall-time. The repo is governed and build-configurable but still messy and not feature-expansion-ready.

The plan changed from “clean folders” to “AIDE-controlled root recycling.” The remaining bad top-level roots are mixed strata, not junk. Every file must be inventoried and assigned a fate: Keep, Adapt, Extract, Convert, Archive, or Drop. Moves require salvage maps, move maps, path aliases, migration ledgers, validators, build/test proof, and rollback notes. XStack/AuditX/RepoX/TestX should be wrapped and recycled behind AIDE before renaming or deletion.

### 2.6 Current final state

By the end of the chat, AIDE had become the staged, compatibility-preserving repo operating system. For AIDE itself, the authoritative development path runs from Q35 through Q57: GitHub/CI advisory, governance audit, intent compiler, repo intelligence index, file quality ledger, refactor control, root recycling, tool absorption, install/repair/upgrade/rollback, stable release bundle, Dominium/Eureka installs, and only later runtime/gateway/hosts. For Dominium, the next sequence is CTest/RepoX blocker remediation/classification, then AIDE-STRUCTURE-00, tool recycling, root recycling framework, inventory waves, move waves, product boot proof, portable projection proof, and only then feature work.

## 3. Main Topics Discussed

### Topic 1 — Personal AI development workflow

This topic began the chat. The user wanted to know whether their Codex Pro, ChatGPT, VS Code, and app workflow could be improved. The conclusion was to stop using ChatGPT mainly as a prompt generator for Codex and instead use each tool for its proper layer. ChatGPT should be the architecture/spec/review/documentation environment. Codex should do bounded repo implementation and tests. AIDE later becomes the portable harness layer that reduces prompt relay entirely.

### Topic 2 — Harness engineering

Harness engineering became the major doctrine. The visible rationale was that agents perform better when the repo provides stable context, reliable commands, test recipes, permission models, worktree isolation, memory, and evidence. This moved the discussion away from “best prompts” and toward “best environment.” The future implication is that AIDE should create the repo-native structure that existing agent tools consume.

### Topic 3 — XStack

XStack was first considered as the central metaharness, but that became too broad. The final decision is that XStack remains Dominium-specific and strict. It should be narrowed, modularized, and eventually wrapped behind AIDE. It should not be deleted immediately because its checks and evidence are valuable. It should not remain public mythology forever because the names and structure are too Dominium-era and too complex.

### Topic 4 — AIDE

AIDE was introduced as the new general system. It evolved from a broad Automated Integrated Development Environment into a more staged repo-native operating layer. The first real product is Profiles + Harness + Compatibility + Dominium Bridge. Later AIDE may include Runtime, Gateway, Service, Commander, mobile, and IDE hosts, but those are deferred until the stable control plane proves itself.

### Topic 5 — Existing tool ecosystem

The chat studied or referenced Codex, Claude Code, OpenHands, Continue, oh-my-codex, claw-code, claude-code-from-source, claude-mem, Graphify, and other projects. The conclusion was that tools already have agents, subagents, skills, hooks, project files, and config surfaces. The gap is a portable repo-owned harness/profile standard that can compile into those dialects. AIDE should fill that gap.

### Topic 6 — Dominium repo convergence and root recycling

The current Dominium repo has improved governance and build proof but still contains many messy roots. The final plan is AIDE-controlled root recycling: inventory, classify, salvage, move, rewrite references, validate, shim, and retire exceptions. No broad feature work or root moving should occur before CTest/RepoX blockers are classified and AIDE refactor machinery exists.

### Topic 7 — Versioning and compatibility

The chat developed a layered identity model: versions identify releases, capability contracts determine compatibility, and GBN/BII/hash identify exact build provenance. This matters to Dominium and AIDE because they handle products, suites, components, packs, schemas, protocols, plugins, and runtime targets. Capabilities such as `save.schema@5` or `net.protocol.session@3` are better compatibility truth than release version numbers alone.

### Topic 8 — Git workflow and WorkUnit recovery

The user supplied AIDE advice around dev branches, structured commits, and WorkUnit recovery. The accepted model is `main` as canonical truth, `dev` as governed integration, `task/*` as bounded work, and release/hotfix branches as needed. AIDE should enforce commit trailers, branch roles, safe sync/land/promote/prune, and repo-state-first recovery when prompts are repeated or out of order.

### Topic 9 — Knowledge preservation

The user asked to preserve this chat as a static knowledge base. This package is the result. Earlier canvas documents captured intermediate summaries. This report supersedes them as the most complete current package but should not be treated as perfect raw transcript extraction, especially because earlier uploads expired.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to improve AI-assisted development, design a better harness, decide XStack’s role, create AIDE, align Dominium cleanup with AIDE, use AIDE in Dominium safely, and generate a complete preservation package. These goals mattered because the user is managing long-running complex projects and wants future chats, Codex sessions, and repos to stop losing context or repeating mistakes.

### 4.2 Inferred Goals

INFERENCE: The user also wants a durable personal/team development operating system that can survive tool churn, support local and remote agents, avoid vendor lock-in, and make repo cleanup mechanical. This was inferred from repeated interest in Codex, Claude Code, open-source harnesses, local models, multi-repo AIDE adoption, and Dominium/Eureka integration.

### 4.3 Goals That Changed Over Time

AIDE changed most. It began as a possible full development environment and became a portable repo operating layer. XStack changed from a candidate universal system to a Dominium strict profile. Repo cleanup changed from moving folders to root recycling under AIDE. AI workflow changed from prompt optimization to harness engineering.

### 4.4 Goals Still Unresolved

Unresolved goals include finishing AIDE Q35-Q57, stabilizing Dominium CTest/RepoX blockers, defining final AIDE install/upgrade bundles, implementing root recycling machinery, deciding when product boot proof can proceed, and later deciding whether AIDE Runtime/Gateway/Hosts are truly needed.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use harness engineering as central frame | Accepted | Models/prompts alone do not solve reliability; environment/contracts/evidence do | 5 | FACT |
| DECISION-02 | Keep ChatGPT/Codex roles distinct | Accepted | ChatGPT for architecture/spec/review; Codex for repo-local implementation | 4 | INFERENCE |
| DECISION-03 | XStack remains Dominium-specific strict profile | Accepted | XStack grew from Dominium and carries local law; universalizing it causes bloat | 5 | FACT |
| DECISION-04 | AIDE becomes new portable repo-native operating layer | Accepted | New clean identity avoids XStack baggage | 5 | FACT |
| DECISION-05 | AIDE v0 is Profiles + Harness + Compatibility + Dominium Bridge, not full runtime | Accepted | Existing tools already provide runtimes; missing layer is portable repo contract | 5 | FACT |
| DECISION-06 | Profile and Harness are distinct | Accepted | Declarative truth and executable machinery must not blur | 5 | FACT |
| DECISION-07 | AIDE must self-host from a small seed, not zero magic | Accepted | Honest bootstrap requires repo kind/commands/policy seed | 4 | FACT |
| DECISION-08 | Use AIDE in Dominium as subordinate pack/control layer first | Accepted | Dominium AGENTS/XStack authority must not be overwritten | 5 | FACT |
| DECISION-09 | Do not delete XStack checks; wrap/classify/migrate/retire | Accepted | Old names are bad, checks are valuable | 5 | FACT |
| DECISION-10 | Dominium cleanup must be file-by-file root recycling, not wholesale moves | Accepted | Mixed roots contain source/docs/policy/tests/generated/history | 5 | FACT |
| DECISION-11 | Do not start broad feature work until build/CTest/product/projection proof is acceptable | Accepted | Feature expansion amplifies disorder while proof gaps remain | 5 | FACT |
| DECISION-12 | Use versions for release identity, capabilities/contracts for compatibility, GBN/BII for provenance | Accepted as strong refinement | Multi-dimensional compatibility cannot be encoded in one version string | 4 | FACT/INFERENCE |
| DECISION-13 | Use dev as integration branch, not source of truth | Accepted from AIDE Git plan | main remains accepted canonical truth | 4 | FACT/INFERENCE |
| DECISION-14 | Structured commits and WorkUnit recovery should become AIDE policy | Accepted | Future automation needs task IDs, branch roles, evidence, trailers | 4 | FACT/INFERENCE |
| DECISION-15 | External leak-derived projects are research inputs, not foundations | Accepted | Legal/supply-chain risk and vendor-specific semantics | 5 | FACT/INFERENCE |
| DECISION-16 | Graphify-like tools are optional analysis backends, not canon | Accepted | Graph outputs are derived and may be noisy/stale | 4 | FACT/INFERENCE |
| DECISION-17 | AIDE must support template, managed product, and release bundle adoption | Accepted | Different repos need different adoption modes | 4 | FACT |
| DECISION-18 | Generated outputs are evidence unless promoted | Accepted | Prevents generated files from competing with canon | 5 | FACT |
| DECISION-19 | Use documentation/contract first before runtime/app/extension expansion | Accepted | Avoids overbuilding and premature abstraction | 5 | FACT |
| DECISION-20 | This chat should be preserved as a high-fidelity handoff package | Accepted by current user request | Creates persistent artifact for future aggregation | 5 | FACT |

### Decision explanations

The most important decisions were DECISION-03 through DECISION-10. The user accepted that XStack should remain Dominium’s strict profile, not the public general system. AIDE should become the portable repo-native operating layer. AIDE’s first product should be Profiles + Harness + Compatibility + Dominium Bridge. XStack checks should be wrapped and migrated, not deleted. Dominium root cleanup must be file-by-file root recycling, not wholesale moves. These decisions all manage the same risk: losing hard-won validation and project knowledge while trying to clean up complexity.

Several decisions are strategic rather than fully implemented. The version/capability model, Git workflow model, install/repair/upgrade model, and tool absorption model are accepted directions but require schemas and code. Future assistants must not mistake them for already completed implementations.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

The biggest rejected idea was building AIDE as a full coding-agent competitor first. That was superseded by the smaller Profiles + Harness + Compatibility + Bridge wedge. Another rejected idea was keeping XStack forever as public mythology; it should be wrapped and retired. Conversely, deleting XStack outright was also rejected because its checks matter. Wholesale folder moves were rejected because roots are mixed strata. Feature work in Dominium was deferred until proof improves. Leak-derived code and graph tools were limited to pattern research or optional backends.

## 7. Important Reasoning, Rationale, and Tradeoffs

The visible rationale was consistent: preserve value while reducing complexity. The chat repeatedly balanced ambition against proof. AIDE should be powerful but start small. XStack should be replaced as public ontology but not discarded functionally. Dominium should become cleaner but not by moving files blindly. External projects should inform AIDE but not become dependencies. Versions should remain useful but not be abused as compatibility truth. Dev branches should help multi-agent work but not become uncontrolled truth.

The main managed risks were drift, over-abstraction, lost validation, hidden path assumptions, bad agent memory, and premature feature work. The dominant tradeoff was speed versus safety: moving folders or deleting old tools would look faster but would likely break build/test/proof paths and lose semantics. Root recycling is slower but safer.

## 8. Plans, Future Work, and Next Steps

The current plan splits into AIDE work and Dominium work.

For AIDE, finish Q35, run QCHECK-03, then implement Q36-Q42 for intent/repo intelligence/refactor/tool absorption, then Q43-Q48 for install/repair/upgrade/rollback/release bundle, then Q49-Q57 for Dominium/Eureka stable install and absorption. Runtime/Gateway/Hosts wait until QCHECK-04.

For Dominium, handle the current CTest/RepoX blockers, then establish AIDE-STRUCTURE-00, inventory old tooling, wrap tools through AIDE, build root recycling framework, inventory roots, and only later perform move waves. Product boot proof, portable projection proof, and first test release lane follow. Feature systems wait.

Recommended immediate sequence:

1. Verify current Dominium HEAD and POST-CONVERGE status.
2. Remediate/classify `invariant_units_present`.
3. Remediate/classify `inv_repox_rules`.
4. Decide if POST-CONVERGE-11 can proceed with CTest-warning status.
5. Finish AIDE Q35 and QCHECK-03 if not already done.
6. Start AIDE Q36-Q42 in AIDE repo.
7. In Dominium, start AIDE-STRUCTURE-00 only after current blocker status is understood.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user values direct, source-grounded, audit-ready, detailed answers. The user asked for preservation packages that are human-readable and machine-aggregatable. The user repeatedly prefers not to lose nuance, rejected options, uncertainties, or artifacts. The user wants current facts verified when possible and wants future assistants to avoid re-asking answered questions.

### 9.2 Inferred Constraints and Preferences

INFERENCE: The user strongly prefers systems that make future agent work less dependent on long chats. The user also prefers evidence-backed engineering over vibes, and wants repo state to dominate memory. The user appears willing to invest in infrastructure if it reduces future chaos.

### 9.3 Uncertain or Unestablished Preferences

UNCERTAIN: Exact public-facing naming for AIDE Core/Kernel remains partly open. Exact threshold for accepting CTest-warning status remains a user/repo governance decision. Exact final AIDE installation packaging details remain pending.

## 10. Files, Artifacts, Outputs, and Prompts

Important artifacts include the canvas documents created earlier, this generated handoff package, live repo files fetched from GitHub, and many external references discussed. The earlier uploaded PDFs/ZIPs have expired, so they cannot be freshly audited. The newly uploaded `Pasted text.txt` provided the preservation-task prompt and drove the package structure.

The most important live repo artifacts are AIDE README/profile/Harness/AIDE Lite files and Dominium AGENTS/POST_CONVERGE_NEXT_STEPS. The most important generated artifacts are this report package, the context transfer packet, the spec sheet, the registers, the aggregator packet, and the future-chat bootstrap prompt.

## 11. Open Questions and Unresolved Issues

The main unresolved issues are whether Dominium’s current CTest blockers will be fixed or explicitly accepted; what exact AIDE schema and stable release bundle will be used for target repos; how strict AIDE validation will be; when AIDE Runtime becomes necessary; and how each remaining Dominium root family should be classified. These are not philosophical issues anymore. They are implementation and verification tasks.

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

Future chats may incorrectly assume AIDE is already a full runtime, delete old XStack tools prematurely, move roots wholesale, start features before proof, treat generated files as canon, or forget that expired uploads limit raw-source certainty. The mitigation is to use the task register and verification queue, check live repo state first, preserve authority hierarchy, and require evidence for every cleanup/migration.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes the architectural doctrine for AIDE, the migration strategy from XStack to AIDE, the Dominium root-recycling plan, the AIDE Q35-Q57 roadmap, the version/capability compatibility model, the Git/WorkUnit recovery model, and the anti-patterns to avoid. It should feed future spec-book chapters on AIDE doctrine, repo harness architecture, Dominium cleanup, migration/compatibility, agent workflow, and evidence governance.

It should not be merged prematurely as final implementation law where items remain planning-level. In particular, Q35-Q57, root recycling, install/upgrade, and capability contracts require current verification and implementation.

## 14. What I Should Remember

- AIDE is the portable repo operating layer; XStack is Dominium’s strict local profile.
- AIDE first ships Profiles + Harness + Compatibility + Dominium Bridge.
- AIDE Runtime/Gateway/Hosts are later, not now.
- Dominium is build-producing but not CTest-clean or feature-ready.
- Current Dominium cleanup must be AIDE-controlled root recycling, not folder dragging.
- XStack/AuditX/RepoX/TestX checks are valuable; names are not.
- Every mixed-root file gets one fate: Keep, Adapt, Extract, Convert, Archive, or Drop.
- Versions identify releases; capabilities/contracts decide compatibility; build IDs prove provenance.
- AIDE should support install/repair/upgrade/rollback before wide target-repo adoption.
- Future assistants must verify live repo state before implementing.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

- “Give me the shortest possible explanation of why AIDE should not replace XStack by deletion.”
- “Explain the difference between AIDE Profile, Harness, Compatibility, and Runtime.”

### 15.2 Decisions

- “Which decisions here are final, and which are still tentative?”
- “Which decisions should become formal AIDE requirements?”

### 15.3 Tasks and Next Actions

- “Generate the next Codex prompt for POST-CONVERGE-10F.”
- “Generate AIDE-STRUCTURE-00 as an implementation prompt.”
- “Generate Q36 Intent Compiler v0 as a precise AIDE WorkUnit.”

### 15.4 Artifacts and Files

- “Which files from this package should I paste into a future chat?”
- “Which live repo files should be checked before continuing Dominium work?”

### 15.5 Risks and Verification

- “What are the top risks if we import AIDE into Dominium too early?”
- “What must be verified before root moves begin?”

### 15.6 Future Spec Book / Aggregation

- “Convert this package into a chapter outline for the master spec book.”
- “Merge this with another chat’s preservation package without losing uncertainty labels.”

### 15.7 Deep-Dive Questions Specific to This Chat

- “Design the root recycling schema in detail.”
- “Design the AIDE install/upgrade/rollback model.”
- “Design the capability contract registry for Dominium packs/plugins/protocols.”

## 16. Compact Human Summary

This chat produced the current strategic architecture for AIDE, XStack, and Dominium cleanup. It began with a practical question about getting more out of Codex Pro and ChatGPT. The answer evolved into a much deeper conclusion: the core leverage is not better prompts but better harnesses. Agents need repo contracts, stable context, reliable commands, validation, permissions, evidence, and structured tasks. This led to the idea that AIDE should be a repo-native operating layer rather than another coding agent.

XStack was originally considered as the broader metaharness, but that was rejected. XStack grew from Dominium-specific needs and carries too much local vocabulary. It should remain Dominium’s strict local governance/proof profile, but it should not become the public universal system. AIDE should become the portable public layer.

AIDE’s first real product is not Runtime, Gateway, Service, Commander, desktop app, or IDE extension. It is Profiles + Harness + Compatibility + Dominium Bridge. AIDE Profiles declare repo truth. AIDE Harness compiles, validates, doctors, migrates, and eventually installs/repairs/upgrades. Compatibility preserves schema, migration, replay, shim, and upgrade rules. Dominium Bridge maps Dominium’s XStack strictness into AIDE without overwriting Dominium authority.

The current AIDE development plan runs through Q35-Q57. Q35/QCHECK-03 finish governance/Git/release readiness. Q36-Q38 build intent compilation, repo intelligence, and file quality. Q39-Q42 build refactor/root recycling/tool absorption/move-map mechanics. Q43-Q48 build install/repair/upgrade/rollback/release bundle support. Q49-Q53 prove Dominium stable install and absorption. Q54-Q57 do the same for Eureka and a product vertical slice. Only after QCHECK-04 should AIDE return to Gateway/provider/Service/Commander/IDE host work.

Dominium is not clean yet. The repo has improved: POST-CONVERGE work made layout authority machine-visible, strict validators pass, VS2022/v143 configure/build pass, and native binaries are produced. But full CTest is still blocked by unit/RepoX issues and wall-time, product boot proof is partial, portable projection proof is partial, and many root exceptions remain. So Dominium should not start major features yet.

The next Dominium strategy is root recycling. Remaining bad roots are not simply junk. They contain mixed useful source, docs, policy, tests, generated evidence, obsolete scaffolding, and stale agent-era machinery. Every file must be classified as Keep, Adapt, Extract, Convert, Archive, or Drop. AIDE should create inventories, salvage maps, move maps, path aliases, migration ledgers, reference rewrites, validators, shims, and exception retirement. XStack/AuditX/RepoX/TestX tools should first be wrapped behind AIDE, then inventoried, adapted, migrated, and retired from public ontology. Do not delete them first.

The final operating rule is simple: AIDE should make Dominium refactors mechanical, validated, reversible, and evidence-backed before feature work resumes.
