# Contradictions, Staleness, and Verification


> SOURCE PATH: `docs/archive/conversations/_audit/CONTRADICTION_MATRIX.md`


## Contradiction Matrix

Findings are review queues, not resolved doctrine.


> Dense table summarized for the reader edition. See the source file, HTML output, or reference appendix source for full detail.

| ID | Class | Source | Claim | Conflict Target | Severity | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| `CONTRA-0001` | `conversation_vs_current_queue` | `advanced_simulation_infrastructure` | Archived conversation discusses work related to blocked scope `gameplay`. | `.aide/queue/current.toml` | `medium` | preserve_as_history; require current queue authority before action |
| `CONTRA-0002` | `stale_external_claim` | `advanced_simulation_infrastructure` | Archived conversation contains potentially stale external or baseline claim: `C89`. | `README.md / current platform and language baseline` | `low` | quarantined until current repo and external facts are checked |
| `CONTRA-0003` | `stale_external_claim` | `advanced_simulation_infrastructure` | Archived conversation contains potentially stale external or baseline claim: `C++98`. | `README.md / current platform and language baseline` | `low` | quarantined until current repo and external facts are checked |
| `CONTRA-0004` | `stale_external_claim` | `advanced_simulation_infrastructure` | Archived conversation contains potentially stale external or baseline claim: `ISO C89`. | `README.md / current platform and language baseline` | `low` | quarantined until current repo and external facts are checked |
| `CONTRA-0005` | `conversation_vs_current_queue` | `app_runtime_platform_renderers` | Archived conversation discusses work related to blocked scope `runtime_module_loader`. | `.aide/queue/current.toml` | `medium` | preserve_as_history; require current queue authority before action |
| `CONTRA-0006` | `conversation_vs_current_queue` | `app_runtime_platform_renderers` | Archived conversation discusses work related to blocked scope `provider_runtime`. | `.aide/queue/current.toml` | `medium` | preserve_as_history; require current queue authority before action |
| ... | 221 additional rows omitted from reader view |



> SOURCE PATH: `docs/archive/conversations/_audit/STALENESS_AND_VERIFICATION.md`


## Staleness And Verification

External platform, SDK, release, language-baseline, and implementation claims are stale until verified.

### Packages With Explicit Uncertainty

#### `advanced_simulation_infrastructure`

- [UNCERTAIN / UNVERIFIED] No repository files were inspected in this chat. No code was implemented. Proposed paths, module names, command names, file names, VM concepts, and data schemas are design proposals until checked against the actual codebase.
- [UNCERTAIN / UNVERIFIED] Exact solvers, fixed-point formats, module paths, data schemas, and tick ordering remain to be verified and specified.
- [UNCERTAIN / UNVERIFIED] The exact gameplay rules runtime was not specified. The command examples were conceptual.
- [UNCERTAIN / UNVERIFIED] The exact cross-section schema, attachment schema, and packing rules remain unresolved.
- [UNCERTAIN / UNVERIFIED] Microsegment length, VM design, storage layout, budget values, and actual code integration remain open.
- [UNCERTAIN / UNVERIFIED] Actual standards packs, rule schema, semantic key format, localization, and AI interaction remain unresolved.
- Then it produced a prompt for another GPT-5.2 chat that already had a refactor/optimization plan. That prompt told the other chat to amend its existing plan instead of restarting, and to verify coverage of arbitrary placement, unified spatial primitives, co-location, signage, buildings, and determinism/performance.
- [UNCERTAIN / UNVERIFIED] The architecture has not been verified against the actual repository. The exact implementation details remain unresolved: Q formats, orientation math, command schemas, VM instruction set, microsegment length, carrier ownership, junction archetypes, facility modules, and DECOR/device promotion policy.

#### `app_runtime_platform_renderers`

- What remains uncertain is whether the current repository already enforces these boundaries mechanically. The actual code needs inspection.
- The unresolved issue is sharding semantics. APP0 requires sharding hooks, but the chat did not decide whether shards are spatial, logical, temporal, jurisdictional, or something else. The report preserved the idea that APP0 can provide sharding plumbing without inventing simulation semantics.
- The unresolved issue is the trust and integrity model for setup. The chat did not decide whether content verification should use hashes, signatures, local manifests, network verification, or another model.
- The unresolved issue is the exact elevation/audit model. The chat did not decide how tools authenticate, request write permissions, log actions, or interact with law enforcement modules.
- The unresolved issue is the exact renderer capability schema. The chat proposed ideas but did not finalize fields, priorities, or target matrices.
- The user asked to look at the old code snapshot in project attachments. A prior assistant claimed to inspect it, but later preservation documents marked that claim as **UNCERTAIN / UNVERIFIED**.
- This became one of the most important unresolved issues. Almost every implementation question depends on the real code: directory layout, build system, languages, existing platform/render layers, client/server dependencies, and engine/game public APIs. The next real step is repository verification.
- INFERENCE:** The user wants future assistants to be epistemically careful: not inventing repository facts, not treating proposals as decisions, and not losing uncertainty.

#### `app_testx_codehygiene`

- The main unresolved goal is practical execution: which prompts have actually been run, which files exist, and what implementation should happen next.
- Setup handles install, verify, repair, rollback, upgrade, downgrade, uninstall, and status. Launcher can invoke Setup, but must not replicate its mutation logic. This prevents two products from disagreeing about installation state.
- First, verify whether `libs/contracts` and `libs/appcore` already exist. Then implement the pure contract headers and appcore skeleton. This should include:
- Before implementing app RepoX integration, verify actual RepoX metadata paths, TestX invocation, VALIDATE-0 commands, and BUILD-ID-0 files. Without that, an implementation prompt would guess.
- Use labels like FACT, INFERENCE, UNCERTAIN, PROJECT-CONTEXT in reports.
- From the user profile and instructions, future assistants should verify time-sensitive/current facts with web where relevant. This chat itself is mostly internal project planning, so external citations are not central.
- EXEC, ECSX, KERN, ADOPT, DIST, HWCAPS, EXIST, DOMAIN, TRAVEL, TIME, OMNI, LIFE, CIV, WAR, AGENT, TOOL, MOD, FINAL prompt families were generated earlier. They are important as historical design artifacts, but actual repo execution is unverified.
- The chat produced downloadable handoff files and later an in-chat reader. Those files are useful for aggregation but are not themselves project source code. The package's main caveat is that it does not verify actual repository state.

#### `architecture_codex_prompts`

- UNCERTAIN / UNVERIFIED: No repository code was inspected or modified in this chat. The prompts and architecture are plans and artifacts, not proof that implementation exists. The actual repository state, build system, existing code quality, GUI backend availability, TLV schemas, and whether any prompts have been applied remain unverified.
- Uncertainty remains about actual repository code and build system, but the layering itself is a strong established principle.
- Unresolved issues include exact TLV schema field tags, exact registry implementation, base pack structure, and whether engine comments/docs may use examples with domain words.
- The main uncertainty is implementation: the prompts define it, but no code was verified.
- Unresolved details include exact process IO schemas, machine runtime state, and the relationship between autonomous machines and agent-operated jobs.
- Unresolved: exact nesting policy, allowed packing modes, and how far to model real packing constraints.
- Uncertainty remains about freeform geometry versus grid shell as the long-term building representation.
- The exact destruction and structural-load models remain unresolved and part of Path D.

#### `architecture_ui_providers`

- The exact first playable slice remains unresolved. The first provider wedge is clear, but exact sequence between client/workbench gameplay, Robot OS, and gameplay mechanics still needs a formal milestone. The exact Lua version, Linux baseline, current repo status, and external library/version support need verification. The exact degree of Unreal involvement remains unclear.
- 1. Verify and pin external library/toolchain facts.
- It remains uncertain how much the user wants Unreal in the near-term after raylib-first discussion. It also remains uncertain whether Lua 5.4 or 5.5 is preferred; the user appears to value pinning and stability more than "latest" for script ABI.

#### `Build_and_Future_Proofing`

- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- The unresolved goals are implementation goals: deciding which recommendations become canon, adding public-surface/dependency/build contracts, validating the current live repo state, and applying the proposed cleanup tasks. The preservation package is complete, but the engineering work it describes remains pending.
- 2. **Verify current repo state.** Confirm the actual current HEAD, build proof, smoke tests, and outstanding warnings before acting.
- 10. **Feed this report into the master spec book aggregator.** Preserve uncertainty labels and avoid merging suggestions as decisions.
- The preservation output must distinguish FACT, INFERENCE, UNCERTAIN/UNVERIFIED, and PROJECT-CONTEXT.
- A future assistant may rely on stale repo state. Mitigation: verify live HEAD, docs, and CI before implementation.
- What live repo facts should I verify before implementing these tasks?
- The final uploaded prompt asked for this preservation package. The key thing to preserve is that most architecture proposals are recommendations, not accepted user decisions yet. The next best action is to decide which recommendations become canon, then implement either `STRUCTURE-01: Public Surface Registry` or the build tuple contract work, after verifying the current live repo state.

#### `canonical_structure_and_framework`

- INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.
- A persistent uncertainty is the exact current repo state. The user supplied many status reports and directory exports, but several exports were internally inconsistent or stale at various points. The chat therefore repeatedly emphasized structure report integrity and verification before trusting tree analyses.
- 1. Verify fast-strict/RepoX/structure report status from a clean current export.
- The user dislikes vague reassurance and wants uncertainty labelled.
- UNCERTAIN: The final exact convention for `external/upstream` versus `external/vendor` should be checked against current repo policy.
- UNCERTAIN: Whether Lua should be pinned to 5.4 or 5.5 is not settled in this chat.
- UNCERTAIN: Whether pack-internal `content/` directories are legitimate pack law or legacy remains to be verified.
- User-reported commits and status summaries: these include commits like `6e0dd93`, `1406490`, `3243fab`, `ce9ca`, and others. Treat them as FACTs reported in the chat, but verify live repo state before acting.

#### `Chronology_Celestial_Systems`

- The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.
- What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data.
- The unresolved issue is exact fidelity. The chat specified what should exist conceptually, but not the final data schema, map resolution, object attributes, or implementation priority.
- What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one.
- The uncertainty is high relative to Earth. Many names and structures were assistant-generated and should be reviewed before implementation.
- The unresolved issue is implementation reality. The actual Plan G/The Game codebase was not visible here, so any implementation plan must be reconciled with real architecture.
- The only major unresolved part is the leap rule.
- The user wants rigorous, structured, fact-aware assistance. The user specifically requested preservation of uncertainty labels and does not want assistant suggestions treated as user decisions.

#### `development_routes`

- The first answer was assertive. It stated that Dominium must follow Route C and described the route as the only viable one for Dominium. Later parts of the chat corrected the status of that claim. FACT: the assistant made that recommendation. UNCERTAIN / UNVERIFIED: the recommendation was not validated with external sources in the chat and was not explicitly accepted by the user.
- The assistant produced a large Context Transfer Packet. It preserved the technical route proposal, the caveats around its uncertainty, the proposed phase order, the open questions, the risks, the artifacts, and the next actions.
- The assistant created those files and reported that the chat label was inferred as **Dominium Development Routes**. The package was said to be safe for aggregation **with caveats**. The main caveats were that the substantive project transcript was short, Route C was not user-confirmed, and Dominium's genre, core loop, stack, implementation state, files, platforms, team, and timeline were not established.
- UNCERTAIN / UNVERIFIED: Route C was not accepted by the user as final.
- UNCERTAIN / UNVERIFIED: the required level of determinism for Dominium was not established. It might need full cross-platform deterministic replay, or it might only need ordinary save/load correctness, or something between those extremes.
- The outputs included a Context Transfer Packet and a downloadable package with multiple files. The files are less important than the purpose: preserve the exact status of the discussion, including uncertainty and assistant-proposal status, so future assistants do not accidentally distort the project.
- The second explicit goal was to preserve the chat before retirement. The user did not want a normal summary. They wanted a maximum-fidelity transfer packet that would prevent loss of decisions, constraints, unresolved issues, rationale, and next actions. This was addressed by the Context Transfer Packet.
- Some goals changed over time. The chat began as architecture guidance, became a state-transfer task, became a packaging task, became an in-chat inspection task, and now becomes a plain-English briefing task. The underlying continuity goal stayed consistent: preserve the useful substance without losing uncertainty.

#### `documentation_standards_readme`

- The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- The chat began with the user asking how to have Codex generate documentation for every file in the project. The user wanted metadata, functions, definitions, dependencies, and other maintainability information documented. The core uncertainty was placement: should documentation live in separate sister files, or should it live in file headers and function headers?
- `UNCERTAIN / UNVERIFIED:` Whether the project has similarly named files or modules is unknown.
- What remains uncertain is how the actual project currently organizes public headers, internal headers, and docs. That must be verified from the repository.
- What remains unverified is the actual project name, supported platforms, license, maturity, and current repository layout. Those cannot be responsibly written without inspecting the repo.
- The decision depends on an assumption: that the project's public APIs are declared in headers. That is likely for a C/C++ codebase, but the actual public/private boundary is still unverified.
- What must happen first: verify source roots, exclusions, CMake structure, CI environment variables, and Python availability.
- What could go wrong: treating assistant suggestions as final requirements or merging contradictory chat claims without preserving uncertainty.

#### `Dominium_Architecture_I`

- What remains uncertain is the exact final scope of all simulation systems. Many systems were described in ambitious terms, but not all details are final or internally consistent. The systems layer especially needs canonicalisation before coding.
- What remains uncertain is the current real-world status and capabilities of "Codex 5.1 Max." That is an external tool fact and requires verification before future use.
- The key later decision was to skip top-level `.txt` devspec files because original Markdown files already existed in `/docs/...`. The visible chat does not show the full content of those docs. They should be preserved as referenced artifacts, but their exact content is **UNCERTAIN / UNVERIFIED**.
- This affects `dlocale`, font rendering, platform path handling, data locale JSON files, mod APIs, UI, and documentation. The unresolved part is exactly how much retro support is actually feasible. Claims about old OSes, toolchains, SDL2, OpenGL, Direct3D, and macOS versions require external verification.
- A large portion of the chat consisted of producing specs for those files. Each spec was meant to tell Codex how to implement that file. The conclusion is that the repository architecture is broad but structured. The unresolved issue is that many later files remain pending.
- The unresolved issue is API consistency. Generated specs for memory and serialization are inconsistent across files, and some platform/render specs contain outdated or unverified external assumptions.
- The most important unresolved issue is duplication and contradiction. `dweather`, `dhydro`, and `dai_core` were generated in more than one form. The package does not choose a final version. A future assistant should not implement any of those blindly.
- The user decided to skip the top-level `.txt` files because original Markdown docs already exist in `/docs/...`. This decision is final for the current workflow, but it depends on those docs actually existing and being current. That is **UNCERTAIN / UNVERIFIED** because the docs were not inspected in this chat.

#### `Dominium_Architecture_II`

- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- This is an important implementation detail, but some of it remains unverified. Lua 5.4.4 portability to old compilers needs testing. The exact Lua data schemas still need definition. The docs also still have JSON-oriented format sections, so the Lua-vs-JSON policy needs reconciliation.
- The biggest unresolved goals are practical:
- Verify DX9/Windows 2000, SDL2, Lua/toolchain compatibility.
- FACT: This was answered in response to Codex's clarifying questions. It is a concrete implementation direction, though Lua 5.4.4 portability remains unverified.
- 1. **Verify and apply V4 docs.
- The user repeatedly requested maximum-fidelity reports, registers, handoff packets, and human-readable summaries. The user wants labelled uncertainty and does not want future assistants to invent missing context.
- or forget that Lua-vs-JSON remains unresolved.

#### `Dominium_Architecture_III`

- The user then uploaded `dominium.7z`, saying it was the git repository as of that moment. **FACT:** The prior assistant said it could not open `.7z` archives in that environment. That means the actual repository state remained unverified at that stage. This became important later, because many implementation ideas were discussed without confirmed access to the repo contents.
- This created one of the main unresolved issues. DX12 was discussed earlier, but omitted from the latest renderer list. X11 and Wayland were discussed earlier, but the latest platform categories are POSIX, SDL1, SDL2, and Native. Therefore, the final status is:
- DX12 is **UNCERTAIN / UNVERIFIED** and should not be assumed.
- X11/Wayland placement is unresolved.
- The prior assistant summarized these files as containing two different launcher concepts: an engine-rendered launcher view and a native Win32 launcher. It also claimed the CMake file built the Win32 source for non-Windows targets. However, this report must preserve that as **UNCERTAIN / UNVERIFIED**, because the files were not re-inspected during final packaging.
- This is final as a user-stated product goal. Feasibility still requires verification.
- Those outputs are important artifacts, but they are not the substance of the design. Their purpose is to preserve this chat's decisions, uncertainty, and future work for later aggregation into a master Project Spec Book.
- What remains uncertain is not the constraint itself, but how existing repository code currently enforces it. That requires code inspection.

#### `Dominium_Architecture_IV`

- The conclusion was clear and accepted: **Domino is the reusable engine; Dominium is the game/product layer**. What remains uncertain is the actual repository state. The chat planned the split, but did not verify whether the repo already matches it.
- The unresolved issue is that the actual repo was not inspected in this chat. The planned structure may not match the current files.
- The unresolved issue is practical feasibility, especially for retro targets and Carbon OS. Their actual toolchains and system calls remain unverified.
- The unresolved issue is the exact IR payload layout and how far limited renderers should go. A CGA or MDA backend cannot realistically support modern 3D in the same way as Vulkan. The agreed approach is explicit capability flags and graceful fallback or no-op behaviour.
- The unresolved issue is the exact manifest/schema format. JSON, TOML, and INI-like examples appeared in prompts, but no final schema choice was made.
- The unresolved issue is that external packaging details require verification. WiX, macOS notarization, Linux packaging, and AppImage tooling are all external-world facts and may be stale.
- The package and this report should help future assistants continue without re-reading the whole chat. However, they must preserve uncertainty: actual repo state is unverified, some transcript sections were skipped, external tooling facts may be stale, and assistant suggestions are not user decisions unless accepted or built upon.
- It is also reasonable to infer that the user wants the future project spec book to preserve rationale, not just lists of decisions. The later handoff requests emphasised visible rationale, rejected options, uncertainty, and changes of direction.

#### `Dominium_Complete_Conversation`

- Uncertainty: the raw pasted prompt is not the current repo authority unless materialized in repo canon. The later audit found that it had in fact been materialized under `docs/canon/constitution_v1.md`.
- Uncertainty: during this preservation pass, a potential inconsistency appeared: some docs claim product roots moved under `apps/`, while an earlier inspected code path under root `client/` was available and `apps/client` was not fetched successfully. This must be verified against the current physical tree.
- Unresolved goals include verifying the latest physical repo tree, proving runtime implementation maturity, formalizing public ABI/API boundaries, completing layout/naming cleanup, and building a second Domino-based product to prove reuse.
- 1. Verify the current physical repo tree against layout docs and `contracts/repo/layout.contract.toml`.
- The user likely wants future assistants to challenge weak framing, preserve uncertainty, avoid shallow "best practice" lists, and focus on decisions that survive future rewrites.
- "Create a gated plan for verifying current repo layout and exceptions."

#### `dominium_domino_codex_planning`

- The most important things to remember are: the project's strict architecture constraints, the Milestone-0 prompt sequence, the later shared CLI/TUI/GUI/input/render prompt sequences, the missing pack-system prompt, the unified startup policy, the unresolved repo-verification issue, and the need to treat generated prompts as plans rather than proof of implementation.
- The assistant generated the first two prompts. The third was never produced because the conversation changed direction. That missing third prompt remains an important unresolved item.
- However, the later context transfer packet treated that inspection claim as **UNCERTAIN / UNVERIFIED**. This was careful and correct: within the visible chat, there was no reliable tool trace proving the repo had actually been inspected. Therefore, future assistants must verify `dominium.zip` or the active checkout before relying on the platform/render/API answer.
- What remains uncertain is how much of this architecture already exists in the current repo and how much is still planned. The chat produced prompts and plans, but it did not prove execution.
- The unresolved issue is whether those prompts were ever run and whether the generated code, if any, conforms to the project's strict C89/C++98 and determinism requirements.
- The unresolved complication is C89 portability. Standard C89 does not provide `long long`, but `u64`, `i64`, and `q48_16` require 64-bit representation. Future work must decide whether to allow compiler extensions, emulate 64-bit values for strict retro targets, or define platform tiers with conditional support.
- The unresolved issue is that the prompt's minimal manifest parser and hardcoded platform path are only a starting point. A real implementation must generalize product discovery, avoid duplicated path logic, and preserve compatibility/versioning rules.
- The unresolved issue is whether the prompts are too broad and whether the existing repo already has overlapping modules. Future work should inspect the repo before applying these prompts.

#### `dominium_full_conversation`

- Verify live repo state, then review/run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if the queue/status supports the maintenance lane.
- Preserve uncertainty labels.
- Future chats could easily misunderstand this conversation by treating Workbench as a GUI framework, treating raylib as the engine, resuming broad structure cleanup, skipping projection conformance, or assuming live repo status from stale pasted reports. The mitigation is to verify repo state first, preserve the contract/service/projection/provider distinctions, and follow the task queue.
- The best next action is to verify live repo state, then review or run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if status supports it.

#### `dominium_setup`

- FACT: The setup system was repeatedly defined as the only component allowed to install files, modify system/installation state, own installed-file metadata, repair installs, verify artifacts, uninstall, downgrade, upgrade, and roll back. This is the most important architectural rule from the chat.
- What remains uncertain is the actual current implementation state in the repository after the applied Codex prompts. The design is clear, but the repo must still be inspected.
- FACT: The final canonical setup layout uses `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- The unresolved part is whether the actual repository now matches this canonical layout.
- UNCERTAIN / UNVERIFIED: Exact Visual Studio 2026 behavior and toolchain details should be verified in the current environment before relying on them.
- UNCERTAIN / UNVERIFIED: The user stated the prompts were applied, but this chat did not show the final repository tree or build results.
- UNCERTAIN / UNVERIFIED: The actual schema files under `schema/setup/` need to be checked.
- Several goals remain unresolved because the actual repo was not inspected here. We do not know whether the applied Codex prompts fully succeeded, whether setup builds, whether schemas exist, whether `libs/contracts` is complete, or whether setup/launcher CLI smoke tests pass.

#### `Domino_Dominium_Workbench`

- Reliability note:** This is a human-readable consolidation, not a live repository audit. Repo-current statements that came from pasted material or prior-chat excerpts remain **UNVERIFIED** until checked against the live `julesc013/dominium` repo and current AIDE/validator outputs.
- Verify current live repo status and task gate state.
- > Verify repo state, then generate `COMMAND-RESULT-VIEW-SLICE-01`.

#### `domino_engine_refactor_prompts`

- The answer also introduced a deterministic bytecode VM as the preferred way to support modded behavior. A question was raised about whether native-code plugins should also be allowed, but the user did not answer. That remains unresolved.
- What remains uncertain is the actual repository state. The chat designed architecture and prompts, but did not inspect source code. Therefore the plan needs repo verification before implementation.
- The unresolved work is to generate detailed subsystem implementation prompts for heat, power, fluids, atmospheres, vehicles, and structural loads after the core engine spine is implemented.
- The remaining uncertainty is plugin policy. A deterministic VM was proposed, but whether native-code plugins are allowed remains unresolved.
- What remains uncertain is the exact thresholds and content policies for when things promote or demote.
- The unresolved issue is how much of STRUCT compilation should be implemented first. The prompt plan is broad; a real implementation may need a smaller first milestone.
- ignoring FACT/INFERENCE/UNCERTAIN labels;
- UNCERTAIN / UNVERIFIED:** The package files were generated in the sandbox during the prior step, but repository files were not created or inspected.

#### `engine_baseline_architecture`

- Uncertainty: the repo has many modules and some historical/legacy surfaces, so exact implementation maturity varies by subsystem. The distinction should remain a formal requirement in a master spec.
- Uncertainty: the full determinism envelope across all current modules was not independently re-run in this chat. User-supplied local validation results should be preserved but verified before being used as audit proof.
- Uncertainty: this remains strategic architecture, not an implemented decision.
- Unresolved goals include:
- User wants uncertainty labelled and framing corrected when evidence disagrees.
- UNCERTAIN: whether the user wants Unreal integration at all as a client/editor.
- UNCERTAIN: exact tolerance for using external geometry libraries.
- UNCERTAIN: whether broad repo restructuring will be desired after Milestone 0.

#### `Foundation_Workbench_Codex`

- What remains uncertain is how quickly this architecture will move from contracts and fixtures into runtime implementations and product slices. The next chat should not assume runtime provider resolvers, package runtime, or Workbench shell exist.
- verify latest live repo state after user-pasted Wave 1 completion;
- 1. Verify live repo state.
- The user wants direct, evidence-grounded, audit-ready answers; timestamps/model labels; explicit uncertainty; no repeated clarification unless necessary; large continuous Codex prompt blocks when generating prompts; targeted tests instead of full suites; and rapid progress toward Workbench/code.
- The user is likely to reject slow, report-only, overcautious process. Future assistants should produce executable next prompts quickly after verifying state.
- It is uncertain how many concurrent Codex workers the user will actually run at once and whether the user wants coordinator prompts or worker prompts next.
- The most important continuation is: verify current `origin/main`, confirm Wave 1 and Workbench validation state, then generate or run `COMMAND-RESULT-VIEW-SLICE-01`.

#### `Framework_Open_Source_Provider`

- The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.
- The exact first implementation branch, versions, and dependency pins are unresolved. The exact Domino Framework ABI is unresolved. The exact Lua version is unresolved. The current repository baseline must be verified. The formal policy for GPL/LGPL/unclear license material is unresolved. The sparse simulation and CAD systems need formal specs and prototypes.
- The raylib decision was also directionally accepted. The user repeatedly expressed enthusiasm for raylib and asked about using as much of raylib infrastructure as possible. The caveat is that raylib is a provider suite, not architecture. This affects rendering, audio, input, asset preview, and Workbench bootstrap.
- 1. Verify repo baseline and dependency versions.
- The user requires source-grounded, audit-ready, uncertainty-labelled responses. The preservation prompt explicitly requires FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT labels, no invented facts, no treating brainstorms as decisions, and no over-compression. The prompt also requires a human-readable report first and downloadable files if possible ?filecite?turn29file0?.
- The most blocking unresolved issues are repo baseline verification, exact dependency pins, minimal framework ABI, provider profile order, deterministic simulation spec, and license policy.
- Verify the current `julesc013/dominium` CMake language baseline.

#### `gui_binary_content`

- GPT-5.5 Pro - 2026-05-27 00:00:00 Australia/Melbourne; time UNVERIFIED
- whether knowledge systems should include uncertainty, false beliefs, or lost knowledge,
- This stage established a pattern that continues throughout the chat: the user does not want impressive-looking prompts that hide unresolved design choices. The user wants the assumptions exposed before anything is formalized.
- The assistant agreed with the general direction, but added caveats. The most important were:
- Those caveats were not final user decisions, but they are important warnings.
- The conclusion was not "run the prompt now." The conclusion was that CONTENT0 is a strong foundation but needs discussion before finalization. The assistant-generated rewrite is useful but not final. The unresolved issues need to be resolved before Codex or any implementation work touches the repository.
- What remains uncertain is how exactly to encode these ideas in schemas and data. For example, it is not yet decided how deterministic seed hierarchies work, how macro content refines into micro content, or how timeline causality should be represented.
- The unresolved issue is the shared backend/UI contract. Without that, the GUI plan is only a list of technologies.

#### `Language_Platform_Architecture`

- The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.
- Exact tolerance for exceptions/RTTI inside private C++17 code remains unsettled. Exact platform floors and raylib/SDL2 priority remain unresolved.
- Verify the Windows 7 and macOS 10.9 toolchain/library assumptions using official sources.

#### `launcher_app_layer`

- These prompts matter because they superseded earlier advice. They also created a new practical priority: verify that the applied prompts actually succeeded.
- This changed the correct future behavior. The next assistant must not redesign. It must implement, audit, maintain, document, verify, and harden.
- This matters because it prevents platform-specific drift. If CLI has `verify`, GUI must not implement a different hidden version of `verify`. If GUI has a pack enable flow, it should map to the same command/intent as CLI and TUI.
- The final purity prompt required those to be moved or quarantined. However, actual repo success remains unverified in this chat.
- The important change is that the conversation moved from "What architecture should we use?" to "Architecture is locked; how do we verify and harden the implementation?"
- The largest unresolved goal is verifying the actual repo. The user stated that two Codex prompts were applied, but this chat did not independently verify the filesystem, build, tests, scripts, or launcher docs.
- Another unresolved goal is confirming whether the launcher hardening prompt has been applied.
- A third unresolved goal is confirming whether command graph, UI IR, binding validation, zero-pack tests, RepoX changelog display, and BUILD-ID mismatch refusal are implemented.

#### `Launcher_Setup_Architecture`

- Uncertainty:** The exact repository layout and existing implementation were not inspected in this chat.
- Uncertainty:** The final language boundary for setup remains unresolved after the later C89/dsys/dgfx launcher direction.
- Uncertainty:** The exact mapping into runtime binaries remains unverified.
- Uncertainty:** Accounts/social/wiki/forum/direct messaging are future-facing and were not converted into the final five-tab implementation plan.
- Uncertainty:** Earlier setup designs used JSON manifests. Later dsys/dgfx architecture leaned toward TLV `.dmeta` files.
- Uncertainty:** Actual plugin ABI details and dynamic loading support depend on dsys/repo APIs.
- Uncertainty:** Actual dsys/dgfx APIs were not inspected.
- Conclusion reached:** This chat is now documented and can be merged later, but with caveats.

#### `Modularity_AIDE_Refactorability`

- The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.
- 1. **TASK-09** - Verify live repo baseline: current branch, root inventory, validators, CTest status, generated artifacts.
- The user prefers source-grounded, audit-ready decisions; bounded uncertainty; explicit task prompts; and reusable engineering doctrine. Future assistants should avoid shallow affirmation and should distinguish accepted user decisions from assistant recommendations.
- Important caveat: the only current uploaded file available for this task is `Pasted text.txt`, which contains the preservation-package prompt. Earlier generated handoff files, ZIP packages, or uploaded docs referenced in prior conversation are not available in this chat unless the user re-uploads them.
- The most serious risk is that a future assistant treats this chat as if it verified the live repo. It did not. The second serious risk is that it hardens every assistant suggestion into a requirement. Several items are strong recommendations aligned with user goals, but still require implementation review. Future chats must preserve labels and verify stale facts.
- Future assistants must verify live repo state before implementing cleanup.

#### `omega_xi_pi_architecture_future`

- Preserve FACT / INFERENCE / UNCERTAIN labels.
- Do not invent or flatten uncertainty.
- 7. "List all artifacts I should verify in GitHub main."
- 9. "What should I verify before starting Sigma?"

#### `OS_Interface_Repo_Architecture`

- The unresolved goals are implementation-level. The repo still needs command dispatch unification, product boot proof, portable projection proof, AppShell rendered-mode law update, Workbench module contracts, document/patch/result/refusal schemas, and a boot-to-replay MVP. It also needs continued exception retirement, CTest/RepoX remediation, and verification of current build status.
- 2. Repair canonical verify test discovery.
- The user wants uncertainty labels and correction of incorrect framing.
- This preservation task specifically required FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels, stable IDs, registers, spec sheets, an aggregator packet, self-audit, and downloadable files if tools are available.
- UNCERTAIN: Whether the user wants to rename `engine` conceptually to `kernel` in code, or only use kernel as a conceptual layer.
- UNCERTAIN: Whether the final public product name should be Dominium Workbench, Dominium Studio, Domino Workbench, or something else.
- UNCERTAIN: How aggressive the next actual code refactor should be versus staged adapters and codegen.

#### `platform_renderer_api_plan`

- This is not a fatal problem for the prompt pack, because the prompts themselves repeatedly tell Codex to discover files with `rg`, `tree`, `type`, CMake commands, and target listing. But it is a major caveat for any future assistant: do not assume the actual repo matches every file path or API name unless checked.
- UNCERTAIN / UNVERIFIED:** The conversation did not prove that these prompts were actually applied to the repository. They are an assumed prerequisite, not verified code state.
- Uncertainty remains about actual repo state. The prompts are designed to discover the repo state, but the chat itself did not inspect the archive.
- The final active prompt pack narrowed runtime completion to Tier-1 on Windows and compile-gated correctness for Tier-2. This is a practical compromise because Codex runs on Windows. But it also creates a caveat: if "fully complete" later means fully running X11/Wayland/Cocoa/Metal/Vulkan, more prompts or native CI validation will be required.
- This became one of the final "done" gates, along with `scripts\build_codex_verify.bat`.
- This matters because the conversation was long and contained multiple plans, superseded options, caveats, and active artifacts. The report package and this plain-language report exist to prevent future assistants from restarting, re-asking, or losing distinctions between decisions, brainstorms, and uncertainties.
- The user also seems to want future assistants to operate with high continuity and not lose subtle distinctions. This is inferred from the repeated requests for maximum-fidelity transfer, stable IDs, labels, uncertainty tracking, and report packaging.
- Another unresolved goal is whether the master engine prompts 1-14 are truly implemented. The later plan depends on them, but this chat did not verify the repo.

#### `platform_support`

- UNCERTAIN / UNVERIFIED: The name "Domino" was never confirmed by the user. Future work should treat "Domino" as an assistant-created placeholder unless the user explicitly accepts it. The useful idea is the distinction between full product support and reduced engine/core support, not necessarily the name.
- The main unresolved issue is the exact definition of support. Does Tier-0 mean identical feature parity, simultaneous release, identical save compatibility, identical UI, equal QA coverage, or some platform-specific differences? The assistant inferred that Tier-0 should mean feature parity, full QA, long-term support, and high release priority, but the exact contractual meaning still needs formal definition.
- What remains unresolved is the exact PC baseline. The chat did not decide whether Windows 10, Windows 11, or both are required. It did not decide whether Windows ARM64 matters. It did not decide whether macOS support includes Intel Macs, Apple Silicon Macs, or both. It did not define Linux distributions, glibc requirements, Flatpak/AppImage/deb/rpm packaging, X11/Wayland policy, or Steam Deck verification.
- UNCERTAIN / UNVERIFIED: The chat did not establish minimum Android API level, ABI list, target graphics APIs, Play Store rules, Android TV status, Android Go status, Automotive status, Chromebook status, or vendor ROM support. These need future decisions and current-source verification.
- The user also listed iPod Touch, Apple TV, Apple Watch, Mac, macOS, tvOS, watchOS, and Apple Vision Pro indirectly through AR. These were not classified in detail. INFERENCE: macOS belongs under PC. UNCERTAIN / UNVERIFIED: tvOS, watchOS, and visionOS remain undecided. Full Dominium on Apple Watch is not established and should not be assumed.
- The unresolved issues are substantial. The chat did not decide whether WebGPU is required, whether WebGL fallback is mandatory, whether the game must work offline as a PWA, whether WASM threading/SIMD is required, how browser storage will work, how asset loading will be handled, or what browser versions will be supported.
- UNCERTAIN / UNVERIFIED: Current console platform facts were not verified in this chat. Future work must verify official PlayStation, Xbox, and Nintendo developer requirements from current official sources before implementation planning.
- INFERENCE: PC handhelds should be subtargets under PC, with their own QA and UI profiles. UNCERTAIN / UNVERIFIED: Steam Deck's exact tier was not finally decided.

#### `Portability_Assurance_Future_Proof`

- The chat proposed using standards such as DO-178C, NIST SSDF, OWASP ASVS, SLSA, and SPDX as design inputs only. The proposed internal version is DDAP v0 with DIL levels. Uncertainty: user has not explicitly ratified DDAP.
- The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.
- Caveat: carry forward as `INFERENCE / assistant recommendation`.
- Caveat: carry forward as `FACT goal + INFERENCE architecture`.
- Caveat: carry forward as `assistant recommendation`.
- Implications: Safe for aggregation only with caveats.
- Caveat: carry forward as `FACT / UNCERTAIN scope`.
- 10. Feed this package into the master Project Spec Book with caveats.

#### `readme_ports_determinism`

- What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.
- The unresolved issue is whether a metadata-only `/ports` directory still violates the user's preference. The final README keeps `/ports` in a limited form, but the user's wording could mean no `/ports` directory at all. That should be clarified before writing the directory contract.
- The unresolved work is to define the actual network protocol, prediction model, rollback window, reconciliation logic, and state-hash validation.
- The major unresolved goal is deciding exactly what "no separate ports directory/system" means physically in the repository. The final README allows `/ports` as metadata-only. That may satisfy the user, but it is not confirmed. If the user meant no `/ports` directory at all, the README still needs another revision.
- Another unresolved goal is making the README and normative specs align. The README says specs are authoritative, but those specs were not inspected in this chat.
- UNCERTAIN / UNVERIFIED: `/ports` as metadata-only is the current README state, but may not be fully accepted.
- A related rejected idea was **retro build flows under `/ports/<target>` containing source or alternative implementations**. The final README superseded this with metadata-only `/ports`, assuming `/ports` is retained at all. This rejection is final for source code and behavior, but the existence of `/ports` itself remains uncertain.
- The first next step is to verify the actual repository `README.md` against the final pasted README. The chat only used pasted text. If the repository differs, future work should start from the actual file, not from memory.

#### `Refactor_Architecture`

- Reliability note: Repository state, Codex execution, exact version numbers, and actual file modifications are **UNCERTAIN / UNVERIFIED** unless explicitly stated otherwise.
- The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- UNCERTAIN / UNVERIFIED:** It did not establish that this system already exists in code.
- What remains uncertain is the exact degree to which existing code currently respects that boundary. The user provided a repo tree, but this chat did not inspect or modify code directly.
- Unresolved details include exact default DOMINIUM_HOME paths per OS and exact implementation of import/GC.
- Unresolved details include exact schemas, parser choice, tests, and actual code implementation.
- The key unresolved point is implementation timing. The report preserves this architecture, but the initial Codex refactor was not supposed to rewrite the entire UI system immediately.
- Actual implementation is unresolved. This chat generated architecture and prompts, not a verified changed codebase.

#### `Refactor_Control_Plane`

- Unresolved goals include finishing AIDE Q35-Q57, stabilizing Dominium CTest/RepoX blockers, defining final AIDE install/upgrade bundles, implementing root recycling machinery, deciding when product boot proof can proceed, and later deciding whether AIDE Runtime/Gateway/Hosts are truly needed.
- 1. Verify current Dominium HEAD and POST-CONVERGE status.
- The user values direct, source-grounded, audit-ready, detailed answers. The user asked for preservation packages that are human-readable and machine-aggregatable. The user repeatedly prefers not to lose nuance, rejected options, uncertainties, or artifacts. The user wants current facts verified when possible and wants future assistants to avoid re-asking answered questions.
- UNCERTAIN: Exact public-facing naming for AIDE Core/Kernel remains partly open. Exact threshold for accepting CTest-warning status remains a user/repo governance decision. Exact final AIDE installation packaging details remain pending.
- Future assistants must verify live repo state before implementing.
- "Merge this with another chat's preservation package without losing uncertainty labels."

#### `Release_Identity_and_Versioning`

- The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.
- GBN should identify CI/public/internal builds and appear as provenance, e.g. `+gbn.7137`, but it must not be used as SemVer precedence. BII should primarily be structured manifest metadata, because it may encode lane, target, kind, configuration, and other build identity fields. The exact BII schema remains unresolved.
- The main unresolved goals are to produce formal specs: Release Constitution, SemVer Component Inventory, Suite Release Policy, Build Identity Spec, Channel/Lifecycle Spec, Artifact Naming Spec, Manifest Schema, Target Taxonomy, and Capability Registry.
- It is still uncertain how strict the user wants suite `X.Y.Z` field meanings to be, whether capabilities should fully replace compatibility profiles or coexist with them, and how much old-platform support should be real versus aspirational.
- The most important unresolved issue is formal classification. Without knowing which entities are strict SemVer components, suite versions, product release IDs, build fields, or capabilities, the rest of the policy cannot be enforced safely.
- Platform targeting remains unresolved. The chat concluded that coarse families like WinNT5, WinNT10, MacOSX4, Linux5, or DOS5 are useful support labels, but exact binary compatibility needs target baselines and runtime/toolchain profiles. Linux kernel major alone is not enough. Windows 9x/NT/NT5/NT6/NT10 likely need separate build lanes or at least explicit tested baselines.

#### `testx_repox_governance`

- This topic remains unresolved in implementation because the repo snapshot showed `.dominium_build_number` and `update_build_number.cmake`, but the chat did not inspect their contents. Those files may still implement older build-number behavior. That must be verified.
- The unresolved part is implementation verification. The repo has Sol/Earth content in `data` and `game/content`; the engine must not assume those exist.
- The unresolved part is how much of TESTX is actually implemented in the repo. The repo contains many tests and scripts, but this chat did not inspect them. A rules-to-checks audit is needed.
- This remains conceptually accepted in the chat, but implementation is unverified.
- The unresolved goals are mostly implementation and verification:
- The repo already has UI IR/codegen infrastructure. The next step is to verify whether GUI/TUI truly bind to the CLI command graph and whether UI is data rather than logic.
- The user has Windows 10 + VS2022. The next step is to verify v141/v141_xp/SDK components and create isolated CMake presets for XP/Win7/Win8/Win10/Win11 builds.
- Acting before verifying repo state.

#### `Timekeeping_and_2038_Resilience`

- What remains uncertain is the current exact status of specific libc/OS/toolchain combinations, because those facts can change and were not reverified during this preservation turn.
- What remains uncertain is the precise target list of legacy machines/toolchains and how far compatibility must go, especially for 16-bit compilers with weak or absent 64-bit arithmetic.
- The main unresolved goals are backend audit, ACT serialization audit, civil/astronomical projection design, and verification of external platform facts.
- The main uncertainty is completeness of repo inspection. The assistant read key files, but not all serialization paths and not all platform backends.
- 6. Verify current platform/library facts before using them in formal public documentation.
- The preservation prompt explicitly requires a human-readable report first, not only a machine-readable handoff. It requires uncertainty labels, stable registers, preservation of artifacts, no invented facts, and downloadable files if tools are available. ?filecite?turn30file0?
- The user prefers source-grounded, audit-ready technical reasoning, direct structure, and careful distinction between facts, recommendations, and unresolved issues. PROJECT-CONTEXT indicates Dominium values C89/C++98 portability, deterministic architecture, CLI/TUI support, and clean platform/runtime separation.
- The strongest unresolved technical task is auditing actual backend timers and persistence formats.

#### `UE6_Domino_Deterministic_Universe`

- UNCERTAIN / UNVERIFIED: This is not a complete reconstruction of every Dominium conversation ever held. The project context shows that many other chats exist about platforms, renderers, setup, game architecture, ecology, ECS, launcher design, and development planning, but their full transcripts are not visible here. Those items are labelled PROJECT-CONTEXT when referenced.
- Uncertainty: public UE6 technical capabilities and requirements remain time-sensitive and need verification before any future hard commitment.
- The chat rejected the idea that clients can authoritatively simulate resource production, hidden state, enemy bases, combat, or persistent terrain changes in an MMO. Clients can assist, but the server must verify and commit.
- REJECTED-02: Waiting for UE6 before beginning serious work. Deprioritised because UE6 availability and capabilities remain uncertain.
- The user wants direct, source-grounded, audit-ready answers; explicit uncertainty; bounded estimates; and correction when framing is wrong. The preservation prompt explicitly requires human-readable explanation first, structured registers second, uncertainty labels, no invented facts, no hidden chain-of-thought, and downloadable files if tools are available.
- UNCERTAIN: The final intended role of Domino remains unclear in the visible transcript. It may be a custom engine, target runtime, renderer, or broader platform plan, but the current chat does not fully define it.

#### `ui_editor_tool_editor_planning`

- The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.
- What remains uncertain is the actual state of the code. The user named files, but the chat did not inspect the repository. A future assistant must verify exact paths, build targets, TLV parser implementation, and current launcher behavior.
- Unresolved details include the actual TLV wire format, migration strategy from `launcher_ui_v1.tlv`, and how much legacy data can be preserved during import.
- The unresolved risk is implementation complexity. Real native tab controls, splitter behavior, and scroll panels can be nontrivial in a child-HWND Win32 UI.
- This is a strong planned design, but some details remain assistant recommendations rather than explicit user-confirmed decisions. Future implementation should preserve that uncertainty if writing a formal spec.
- The unresolved issue is that the uploaded screenshot bundles were not inspected. The logical specs are accepted planning artifacts, not verified screenshot extractions.
- The exact scope of IDE-native live editing remains unresolved. The assistant proposed preview hosts, but it is not confirmed whether that fully satisfies the user's desire to use Visual Studio, Xcode, and Linux GUI tools.

#### `Universe_Explorer_Planning`

- Uncertain: whether all seven universal layers are now formally captured under exactly that naming. The repo has equivalent or related doctrine, but not every early phrase appears as a single artifact.
- Uncertain: the repo contains pieces of this through affordance/capability/domain docs, but the assistant did not find one single master Deep Primitives spec in the docs it read.
- The most important unresolved issue is that the Universe Explorer plan is still a proposed/recommended next strategy, not yet a completed repo task. The next best action is either to draft `PRESENTATION-CONTRACT-01` / `UNIVERSE-EXPLORER-CONTRACT-01`, or to preserve this chat and merge it with other old-chat reports into a master Project Spec Book.

#### `Workbench_AIDE_Product_Spine`

- The largest uncertainty is not the conceptual architecture; that has converged. The largest uncertainty is live execution state: whether prompts generated near the end of the chat have already been run locally, committed, or pushed. The next chat should first inspect `.aide/queue/current.toml`, recent commits, and relevant audit files.
- Remaining uncertainty: exact implementation of erosion/ecology/evolution proxies remains future domain work.
- 1. Verify current repo state.
- Explicitly label uncertainty.
- The next chat should verify repo state first.
- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Verify live repo state before acting.
- safe_for_aggregation: "Yes, with caveats"

#### `World_Architecture`

- The main unresolved issue is implementation detail. The design says Q16.16 and Q4.12, but the earlier prompt used signed types incorrectly. The future implementation must use unsigned local coordinates or a centered signed design.
- The unresolved parts are the exact meshing algorithm, the fixed-point scaling of `?`, and the sample resolution. A 32? sample grid per 16m chunk was recommended but not confirmed as final.
- The exact solvers remain unresolved. The architecture is clear, but formulas and resolutions are still future work.
- The save format remains conceptual in places. Exact binary headers, endian policy, compression, and migration strategy are unresolved.
- The crucial caveat is implementation: unsigned or centered representations are needed. The design intent is final, but the exact typedefs must be fixed. If the implementation uses signed types incorrectly, the whole coordinate system breaks.
- This is not yet an implementation-level final spec because solver formulas are unresolved.
- FACT:** Core target is C89. This is non-negotiable in principle, but exact portability mechanics are unresolved because strict C89 lacks standard fixed-width integer types.
- The user wants direct, detailed, rigorous, critical responses. The user prefers source labels, uncertainty preservation, and avoiding invented facts. The user does not want assistant suggestions silently upgraded to decisions.

#### `xstack_lab_galaxy`

- But this chat did not verify the repository. That became one of the most important unresolved issues.
- This is one of the most important outputs associated with this chat, but it is also one of the most uncertain because it is user-reported from another chat and not verified directly here. The user explicitly wanted it audited for completion and consistency.
- INFERENCE: The user also wanted to prevent future assistants from flattening nuance. They repeatedly asked for maximum fidelity, uncertainty labels, rejected options, contradictions, and rationale. This implies a strong preference for preserving complexity rather than oversimplifying.
- INFERENCE: The user likely wants to resume productive development after verifying the substrate. The next likely feature area is survival or Lab Galaxy refinement, but the user has not made a final decision in this visible chat.
- 4. From documentation to verifying a new 13-prompt substrate.
- The biggest unresolved goal is verifying the actual repository. The package says what was reported, but not what is proven. Another unresolved goal is deciding what comes next: survival, Lab Galaxy UX, distributed SRZ, or documentation polish.
- The main assumption behind all of this is that the repo can actually enforce these contracts. That remains unverified in this chat.
- The best next step is to verify the actual repository state. This matters because the long 13-prompt transcript is not proof. The user explicitly does not know whether everything was truly implemented.

### Stale Claim Findings

- `CONTRA-0002` `advanced_simulation_infrastructure`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0003` `advanced_simulation_infrastructure`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0004` `advanced_simulation_infrastructure`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0009` `app_runtime_platform_renderers`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0012` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0013` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0014` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0015` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0018` `architecture_codex_prompts`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0019` `architecture_codex_prompts`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0020` `architecture_codex_prompts`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0026` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0027` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0028` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0029` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0030` `Build_and_Future_Proofing`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0031` `Build_and_Future_Proofing`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0032` `Build_and_Future_Proofing`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0038` `canonical_structure_and_framework`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0039` `canonical_structure_and_framework`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0040` `canonical_structure_and_framework`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0043` `development_routes`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0044` `documentation_standards_readme`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0045` `documentation_standards_readme`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0046` `documentation_standards_readme`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0047` `documentation_standards_readme`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0050` `Dominium_Architecture_I`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0051` `Dominium_Architecture_I`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0054` `Dominium_Architecture_II`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0055` `Dominium_Architecture_II`: Archived conversation contains potentially stale external or baseline claim: `Windows 98`.
- `CONTRA-0056` `Dominium_Architecture_II`: Archived conversation contains potentially stale external or baseline claim: `Windows NT 2000`.
- `CONTRA-0057` `Dominium_Architecture_II`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0058` `Dominium_Architecture_II`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0061` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0062` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0063` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `Win98`.
- `CONTRA-0064` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `Windows 98`.
- `CONTRA-0065` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `Windows NT 2000`.
- `CONTRA-0066` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `Mac OS 9`.
- `CONTRA-0067` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `Mac OS 8`.
- `CONTRA-0068` `Dominium_Architecture_III`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0072` `Dominium_Architecture_IV`: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- `CONTRA-0073` `Dominium_Architecture_IV`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0074` `Dominium_Architecture_IV`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0076` `Dominium_Complete_Conversation`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0077` `Dominium_Complete_Conversation`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0078` `dominium_domino_codex_planning`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0079` `dominium_domino_codex_planning`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0080` `dominium_domino_codex_planning`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0081` `dominium_domino_codex_planning`: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- `CONTRA-0082` `dominium_domino_codex_planning`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0088` `dominium_full_conversation`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0091` `dominium_setup`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0096` `Domino_Dominium_Workbench`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0098` `domino_engine_refactor_prompts`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0099` `domino_engine_refactor_prompts`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0100` `domino_engine_refactor_prompts`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0111` `Foundation_Workbench_Codex`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0112` `Foundation_Workbench_Codex`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0113` `Foundation_Workbench_Codex`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0118` `Framework_Open_Source_Provider`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0119` `Framework_Open_Source_Provider`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0122` `gui_binary_content`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0123` `gui_binary_content`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0124` `gui_binary_content`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0129` `Language_Platform_Architecture`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0130` `Language_Platform_Architecture`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0131` `Language_Platform_Architecture`: Archived conversation contains potentially stale external or baseline claim: `Windows 98`.
- `CONTRA-0132` `Language_Platform_Architecture`: Archived conversation contains potentially stale external or baseline claim: `Mac OS 9`.
- `CONTRA-0133` `Language_Platform_Architecture`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0134` `Language_Platform_Architecture`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0135` `Language_Platform_Architecture`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0137` `launcher_app_layer`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0140` `Launcher_Setup_Architecture`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0141` `Launcher_Setup_Architecture`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0142` `Launcher_Setup_Architecture`: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- `CONTRA-0143` `Launcher_Setup_Architecture`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0146` `Modularity_AIDE_Refactorability`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0152` `OS_Interface_Repo_Architecture`: Archived conversation contains potentially stale external or baseline claim: `Mac OS 8`.
- `CONTRA-0153` `OS_Interface_Repo_Architecture`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0154` `OS_Interface_Repo_Architecture`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0158` `platform_renderer_api_plan`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0159` `platform_renderer_api_plan`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0160` `platform_renderer_api_plan`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0161` `platform_renderer_api_plan`: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- `CONTRA-0162` `platform_renderer_api_plan`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0163` `platform_renderer_api_plan`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0167` `platform_support`: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- `CONTRA-0168` `platform_support`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0169` `platform_support`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0170` `platform_support`: Archived conversation contains potentially stale external or baseline claim: `WebGPU`.
- `CONTRA-0171` `platform_support`: Archived conversation contains potentially stale external or baseline claim: `console program`.
- `CONTRA-0172` `platform_support`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0174` `Portability_Assurance_Future_Proof`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0175` `Portability_Assurance_Future_Proof`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0176` `readme_ports_determinism`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0177` `readme_ports_determinism`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0178` `readme_ports_determinism`: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- `CONTRA-0179` `readme_ports_determinism`: Archived conversation contains potentially stale external or baseline claim: `286`.
- `CONTRA-0180` `Refactor_Architecture`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0181` `Refactor_Architecture`: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- `CONTRA-0182` `Refactor_Architecture`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0183` `Refactor_Architecture`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0185` `Refactor_Control_Plane`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0187` `Release_Identity_and_Versioning`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0192` `testx_repox_governance`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0193` `testx_repox_governance`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0194` `testx_repox_governance`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0195` `testx_repox_governance`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0196` `Timekeeping_and_2038_Resilience`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0197` `Timekeeping_and_2038_Resilience`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0200` `UE6_Domino_Deterministic_Universe`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0201` `UE6_Domino_Deterministic_Universe`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0204` `ui_editor_tool_editor_planning`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0205` `ui_editor_tool_editor_planning`: Archived conversation contains potentially stale external or baseline claim: `Android`.
- `CONTRA-0216` `Workbench_AIDE_Product_Spine`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0217` `Workbench_AIDE_Product_Spine`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0219` `World_Architecture`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0220` `World_Architecture`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0221` `World_Architecture`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0222` `World_Architecture`: Archived conversation contains potentially stale external or baseline claim: `SDK`.



> SOURCE PATH: `docs/archive/conversations/_audit/UNCERTAINTY_REGISTER.md`


## Uncertainty Register

Uncertainty entries are extracted from archived reports and require current repo verification.

### `advanced_simulation_infrastructure`

- Source file: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__human_readable_chat_report.txt`
- [UNCERTAIN / UNVERIFIED] No repository files were inspected in this chat. No code was implemented. Proposed paths, module names, command names, file names, VM concepts, and data schemas are design proposals until checked against the actual codebase.
- [UNCERTAIN / UNVERIFIED] Exact solvers, fixed-point formats, module paths, data schemas, and tick ordering remain to be verified and specified.
- [UNCERTAIN / UNVERIFIED] The exact gameplay rules runtime was not specified. The command examples were conceptual.
- [UNCERTAIN / UNVERIFIED] The exact cross-section schema, attachment schema, and packing rules remain unresolved.
- [UNCERTAIN / UNVERIFIED] Microsegment length, VM design, storage layout, budget values, and actual code integration remain open.
- [UNCERTAIN / UNVERIFIED] Actual standards packs, rule schema, semantic key format, localization, and AI interaction remain unresolved.
- Then it produced a prompt for another GPT-5.2 chat that already had a refactor/optimization plan. That prompt told the other chat to amend its existing plan instead of restarting, and to verify coverage of arbitrary placement, unified spatial primitives, co-location, signage, buildings, and determinism/performance.
- [UNCERTAIN / UNVERIFIED] The architecture has not been verified against the actual repository. The exact implementation details remain unresolved: Q formats, orientation math, command schemas, VM instruction set, microsegment length, carrier ownership, junction archetypes, facility modules, and DECOR/device promotion policy.
- [UNCERTAIN / UNVERIFIED] Exact Q formats were not finalized.
- [UNCERTAIN / UNVERIFIED] The exact VM is unresolved.
- The most important practical next step is to inspect the current repository. This chat proposed module names and file paths, but did not verify them.
- [FACT] The user asked later reports to preserve uncertainty labels: FACT, INFERENCE, UNCERTAIN / UNVERIFIED, and PROJECT-CONTEXT.

### `app_runtime_platform_renderers`

- Source file: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`
- What remains uncertain is whether the current repository already enforces these boundaries mechanically. The actual code needs inspection.
- The unresolved issue is sharding semantics. APP0 requires sharding hooks, but the chat did not decide whether shards are spatial, logical, temporal, jurisdictional, or something else. The report preserved the idea that APP0 can provide sharding plumbing without inventing simulation semantics.
- The unresolved issue is the trust and integrity model for setup. The chat did not decide whether content verification should use hashes, signatures, local manifests, network verification, or another model.
- The unresolved issue is the exact elevation/audit model. The chat did not decide how tools authenticate, request write permissions, log actions, or interact with law enforcement modules.
- The unresolved issue is the exact renderer capability schema. The chat proposed ideas but did not finalize fields, priorities, or target matrices.
- The user asked to look at the old code snapshot in project attachments. A prior assistant claimed to inspect it, but later preservation documents marked that claim as **UNCERTAIN / UNVERIFIED**.
- This became one of the most important unresolved issues. Almost every implementation question depends on the real code: directory layout, build system, languages, existing platform/render layers, client/server dependencies, and engine/game public APIs. The next real step is repository verification.
- INFERENCE:** The user wants future assistants to be epistemically careful: not inventing repository facts, not treating proposals as decisions, and not losing uncertainty.
- The exact module architecture remains unresolved. The exact platform/renderer support matrix remains unresolved. The exact relationship to the current repository remains unresolved because the old snapshot has not been verified. The exact setup trust model, tool audit model, sharding semantics, and client prediction policy remain unresolved.
- This affects the client, server, launcher, setup, and tools. The client can display and interact; the server can host authority; the launcher can start sessions; setup can install and verify; tools can inspect and audit. But none of them should invent unauthorized simulation outcomes.
- The assumption behind this decision is that engine/game code can be hosted through stable public APIs. Whether the current repo already supports that is **UNCERTAIN / UNVERIFIED**.
- The unresolved caveat is prediction. If client-side prediction is later needed, it must be designed carefully as non-authoritative and probably separated from authority-committing simulation code.

### `app_testx_codehygiene`

- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- The main unresolved goal is practical execution: which prompts have actually been run, which files exist, and what implementation should happen next.
- Setup handles install, verify, repair, rollback, upgrade, downgrade, uninstall, and status. Launcher can invoke Setup, but must not replicate its mutation logic. This prevents two products from disagreeing about installation state.
- First, verify whether `libs/contracts` and `libs/appcore` already exist. Then implement the pure contract headers and appcore skeleton. This should include:
- Before implementing app RepoX integration, verify actual RepoX metadata paths, TestX invocation, VALIDATE-0 commands, and BUILD-ID-0 files. Without that, an implementation prompt would guess.
- Use labels like FACT, INFERENCE, UNCERTAIN, PROJECT-CONTEXT in reports.
- From the user profile and instructions, future assistants should verify time-sensitive/current facts with web where relevant. This chat itself is mostly internal project planning, so external citations are not central.
- EXEC, ECSX, KERN, ADOPT, DIST, HWCAPS, EXIST, DOMAIN, TRAVEL, TIME, OMNI, LIFE, CIV, WAR, AGENT, TOOL, MOD, FINAL prompt families were generated earlier. They are important as historical design artifacts, but actual repo execution is unverified.
- The chat produced downloadable handoff files and later an in-chat reader. Those files are useful for aggregation but are not themselves project source code. The package's main caveat is that it does not verify actual repository state.
- The most important unresolved issue is actual repository state. We do not know which prompts were run, which files exist, or which systems are implemented.
- The latest project-context says `CANON_INDEX.md` is the single source of truth. The package does not verify its existence. This should be checked before using docs as canon.
- The versioning model is stated as canon, but actual implementation is unverified.
- The project is too complex for vague summaries. Future assistants should preserve IDs, artifacts, and caveats.

### `architecture_codex_prompts`

- Source file: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__human_readable_chat_report.txt`
- UNCERTAIN / UNVERIFIED: No repository code was inspected or modified in this chat. The prompts and architecture are plans and artifacts, not proof that implementation exists. The actual repository state, build system, existing code quality, GUI backend availability, TLV schemas, and whether any prompts have been applied remain unverified.
- Uncertainty remains about actual repository code and build system, but the layering itself is a strong established principle.
- Unresolved issues include exact TLV schema field tags, exact registry implementation, base pack structure, and whether engine comments/docs may use examples with domain words.
- The main uncertainty is implementation: the prompts define it, but no code was verified.
- Unresolved details include exact process IO schemas, machine runtime state, and the relationship between autonomous machines and agent-operated jobs.
- Unresolved: exact nesting policy, allowed packing modes, and how far to model real packing constraints.
- Uncertainty remains about freeform geometry versus grid shell as the long-term building representation.
- The exact destruction and structural-load models remain unresolved and part of Path D.
- Unverified: actual save file format and current repo serialization code.
- The most important caveat is that actual repo state is unknown.
- Unverified: actual hash design and validators have not been implemented in this chat.
- UNCERTAIN / UNVERIFIED: Actual implementation remains unresolved. The prompts are ready, but no code was verified.

### `architecture_ui_providers`

- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- The exact first playable slice remains unresolved. The first provider wedge is clear, but exact sequence between client/workbench gameplay, Robot OS, and gameplay mechanics still needs a formal milestone. The exact Lua version, Linux baseline, current repo status, and external library/version support need verification. The exact degree of Unreal involvement remains unclear.
- 1. Verify and pin external library/toolchain facts.
- It remains uncertain how much the user wants Unreal in the near-term after raylib-first discussion. It also remains uncertain whether Lua 5.4 or 5.5 is preferred; the user appears to value pinning and stability more than "latest" for script ABI.

### `Build_and_Future_Proofing`

- Source file: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- The unresolved goals are implementation goals: deciding which recommendations become canon, adding public-surface/dependency/build contracts, validating the current live repo state, and applying the proposed cleanup tasks. The preservation package is complete, but the engineering work it describes remains pending.
- 2. **Verify current repo state.** Confirm the actual current HEAD, build proof, smoke tests, and outstanding warnings before acting.
- 10. **Feed this report into the master spec book aggregator.** Preserve uncertainty labels and avoid merging suggestions as decisions.
- The preservation output must distinguish FACT, INFERENCE, UNCERTAIN/UNVERIFIED, and PROJECT-CONTEXT.
- A future assistant may rely on stale repo state. Mitigation: verify live HEAD, docs, and CI before implementation.
- What live repo facts should I verify before implementing these tasks?
- The final uploaded prompt asked for this preservation package. The key thing to preserve is that most architecture proposals are recommendations, not accepted user decisions yet. The next best action is to decide which recommendations become canon, then implement either `STRUCTURE-01: Public Surface Registry` or the build tuple contract work, after verifying the current live repo state.

### `canonical_structure_and_framework`

- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.
- A persistent uncertainty is the exact current repo state. The user supplied many status reports and directory exports, but several exports were internally inconsistent or stale at various points. The chat therefore repeatedly emphasized structure report integrity and verification before trusting tree analyses.
- 1. Verify fast-strict/RepoX/structure report status from a clean current export.
- The user dislikes vague reassurance and wants uncertainty labelled.
- UNCERTAIN: The final exact convention for `external/upstream` versus `external/vendor` should be checked against current repo policy.
- UNCERTAIN: Whether Lua should be pinned to 5.4 or 5.5 is not settled in this chat.
- UNCERTAIN: Whether pack-internal `content/` directories are legitimate pack law or legacy remains to be verified.
- User-reported commits and status summaries: these include commits like `6e0dd93`, `1406490`, `3243fab`, `ce9ca`, and others. Treat them as FACTs reported in the chat, but verify live repo state before acting.
- Is full CTest currently green? The chat repeatedly says no or not run; verify before any release/trust claim.
- Are stale AuditX/identity evidence and launcher marker debt still blocking fast strict? User reports changed over time; verify live.
- Is the final live queue pointing to `PROJECTION-CONFORMANCE-01`, `PRESENTATION-CONTRACT-01`, or a maintenance task? Verify current `.aide/queue/current.toml`.
- Should `external/upstream` or `external/vendor` be canonical? Verify current repo convention.

### `Chronology_Celestial_Systems`

- Source file: `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__human_readable_chat_report.txt`
- The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.
- What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data.
- The unresolved issue is exact fidelity. The chat specified what should exist conceptually, but not the final data schema, map resolution, object attributes, or implementation priority.
- What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one.
- The uncertainty is high relative to Earth. Many names and structures were assistant-generated and should be reviewed before implementation.
- The unresolved issue is implementation reality. The actual Plan G/The Game codebase was not visible here, so any implementation plan must be reconciled with real architecture.
- The only major unresolved part is the leap rule.
- The user wants rigorous, structured, fact-aware assistance. The user specifically requested preservation of uncertainty labels and does not want assistant suggestions treated as user decisions.
- Future assistants should not invent Plan G details, assume codebase language constraints, hardcode unverified astronomy, treat all assistant-generated calendars as final, flatten tentative items into decisions, or reveal time/date in UI without in-world justification.
- The most important unresolved issue is the real Plan G/The Game architecture. This chat could not inspect it. Any implementation plan must first compare this design to the actual project.
- The second major unresolved issue is the exact HPC-E leap rule. The calendar structure is set, but the leap cadence is not. This must be decided before implementation.
- The third unresolved issue is the exact time-scale mapping for Gregorian January 1, 2000 AD. The user specified the civil date, but not the exact technical instant. This affects deterministic world start.

### `development_routes`

- Source file: `docs/archive/conversations/development_routes/dominium_development_routes__human_readable_chat_report.txt`
- The first answer was assertive. It stated that Dominium must follow Route C and described the route as the only viable one for Dominium. Later parts of the chat corrected the status of that claim. FACT: the assistant made that recommendation. UNCERTAIN / UNVERIFIED: the recommendation was not validated with external sources in the chat and was not explicitly accepted by the user.
- The assistant produced a large Context Transfer Packet. It preserved the technical route proposal, the caveats around its uncertainty, the proposed phase order, the open questions, the risks, the artifacts, and the next actions.
- The assistant created those files and reported that the chat label was inferred as **Dominium Development Routes**. The package was said to be safe for aggregation **with caveats**. The main caveats were that the substantive project transcript was short, Route C was not user-confirmed, and Dominium's genre, core loop, stack, implementation state, files, platforms, team, and timeline were not established.
- UNCERTAIN / UNVERIFIED: Route C was not accepted by the user as final.
- UNCERTAIN / UNVERIFIED: the required level of determinism for Dominium was not established. It might need full cross-platform deterministic replay, or it might only need ordinary save/load correctness, or something between those extremes.
- The outputs included a Context Transfer Packet and a downloadable package with multiple files. The files are less important than the purpose: preserve the exact status of the discussion, including uncertainty and assistant-proposal status, so future assistants do not accidentally distort the project.
- The second explicit goal was to preserve the chat before retirement. The user did not want a normal summary. They wanted a maximum-fidelity transfer packet that would prevent loss of decisions, constraints, unresolved issues, rationale, and next actions. This was addressed by the Context Transfer Packet.
- Some goals changed over time. The chat began as architecture guidance, became a state-transfer task, became a packaging task, became an in-chat inspection task, and now becomes a plain-English briefing task. The underlying continuity goal stayed consistent: preserve the useful substance without losing uncertainty.
- The chat-specific reporting decisions were more settled. The user explicitly required that the package be limited to this chat, use labels for fact/inference/uncertainty, preserve assistant suggestions as suggestions, and avoid inventing facts. These are firm process decisions because they came directly from the user.
- The user's strongest visible concern is epistemic discipline: do not invent, do not silently infer, do not promote suggestions into decisions, and do not erase uncertainty.
- Before building anything, the project needs a clearer definition of Dominium. The first unresolved technical step is to define the genre and core player loop. This matters because a grand strategy game, colony sim, city-builder, RTS, political simulator, and economic simulation all imply different state models and time scales.
- The largest unresolved issue is whether Dominium is actually simulation-heavy enough to justify the proposed kernel-first deterministic route. The assistant assumed that kind of complexity, but the visible conversation does not prove it. The user needs to confirm or correct that assumption.

### `documentation_standards_readme`

- Source file: `docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__human_readable_chat_report.txt`
- The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions.
- The chat began with the user asking how to have Codex generate documentation for every file in the project. The user wanted metadata, functions, definitions, dependencies, and other maintainability information documented. The core uncertainty was placement: should documentation live in separate sister files, or should it live in file headers and function headers?
- `UNCERTAIN / UNVERIFIED:` Whether the project has similarly named files or modules is unknown.
- What remains uncertain is how the actual project currently organizes public headers, internal headers, and docs. That must be verified from the repository.
- What remains unverified is the actual project name, supported platforms, license, maturity, and current repository layout. Those cannot be responsibly written without inspecting the repo.
- The decision depends on an assumption: that the project's public APIs are declared in headers. That is likely for a C/C++ codebase, but the actual public/private boundary is still unverified.
- What must happen first: verify source roots, exclusions, CMake structure, CI environment variables, and Python availability.
- What could go wrong: treating assistant suggestions as final requirements or merging contradictory chat claims without preserving uncertainty.
- `FACT:` The user wants facts checked and uncertainty preserved.
- `INFERENCE:` The user values preserving rejected options and uncertainty because they expect to aggregate many old chats later.
- `UNCERTAIN / UNVERIFIED:` Actual repository language standards, compiler settings, source roots, and assembly presence still need verification.
- This is one of the most concrete artifacts. It describes how Codex should create a Python checker, integrate it into CMake, document it, and verify behavior.

### `Dominium_Architecture_I`

- Source file: `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__human_readable_chat_report.txt`
- What remains uncertain is the exact final scope of all simulation systems. Many systems were described in ambitious terms, but not all details are final or internally consistent. The systems layer especially needs canonicalisation before coding.
- What remains uncertain is the current real-world status and capabilities of "Codex 5.1 Max." That is an external tool fact and requires verification before future use.
- The key later decision was to skip top-level `.txt` devspec files because original Markdown files already existed in `/docs/...`. The visible chat does not show the full content of those docs. They should be preserved as referenced artifacts, but their exact content is **UNCERTAIN / UNVERIFIED**.
- This affects `dlocale`, font rendering, platform path handling, data locale JSON files, mod APIs, UI, and documentation. The unresolved part is exactly how much retro support is actually feasible. Claims about old OSes, toolchains, SDL2, OpenGL, Direct3D, and macOS versions require external verification.
- A large portion of the chat consisted of producing specs for those files. Each spec was meant to tell Codex how to implement that file. The conclusion is that the repository architecture is broad but structured. The unresolved issue is that many later files remain pending.
- The unresolved issue is API consistency. Generated specs for memory and serialization are inconsistent across files, and some platform/render specs contain outdated or unverified external assumptions.
- The most important unresolved issue is duplication and contradiction. `dweather`, `dhydro`, and `dai_core` were generated in more than one form. The package does not choose a final version. A future assistant should not implement any of those blindly.
- The user decided to skip the top-level `.txt` files because original Markdown docs already exist in `/docs/...`. This decision is final for the current workflow, but it depends on those docs actually existing and being current. That is **UNCERTAIN / UNVERIFIED** because the docs were not inspected in this chat.
- The user explicitly required that the final handoff/report preserve facts, decisions, preferences, rejected options, unresolved issues, artifacts, and rationale. The user required labels for FACT, INFERENCE, UNCERTAIN / UNVERIFIED, and PROJECT-CONTEXT. The user required that assistant suggestions not be treated as user decisions unless accepted.
- All artifacts should feed into the future Project Spec Book only after uncertainty and contradictions are handled. The file-spec prompts are especially important, but they require API cleanup before implementation.
- The most important unresolved issue is canonicalisation. `dweather`, `dhydro`, and `dai_core` each have duplicate conflicting specs. A future assistant needs to compare the versions and either select one or merge them carefully.
- The next unresolved issue is core API consistency. `dmem` and `dserialize` are used inconsistently across generated specs. This must be fixed before coding.

### `Dominium_Architecture_II`

- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- What remains uncertain is the exact code-level API and component layouts. The chat produced specs and prompts, not final source code.
- This is an important implementation detail, but some of it remains unverified. Lua 5.4.4 portability to old compilers needs testing. The exact Lua data schemas still need definition. The docs also still have JSON-oriented format sections, so the Lua-vs-JSON policy needs reconciliation.
- The biggest unresolved goals are practical:
- Verify DX9/Windows 2000, SDL2, Lua/toolchain compatibility.
- FACT: This was answered in response to Codex's clarifying questions. It is a concrete implementation direction, though Lua 5.4.4 portability remains unverified.
- 1. **Verify and apply V4 docs.
- The user repeatedly requested maximum-fidelity reports, registers, handoff packets, and human-readable summaries. The user wants labelled uncertainty and does not want future assistants to invent missing context.
- or forget that Lua-vs-JSON remains unresolved.
- The most important unresolved issue is **actual repo state**. The chat generated many documents, but it is unknown whether they were applied to disk. Before Codex implements anything, the repo must be inspected.
- Another major unresolved issue is **Lua data versus JSON formats**. The user explicitly wants Lua for all MVP data, but generated `DATA_FORMATS.md` and data specs include JSON-style formats. This may be acceptable if JSON is long-term and Lua is MVP, but the docs must say that clearly.
- The exact MVP component set is also unresolved. The chat implies Transform, occupancy, power node, fluid node, data node, worker/agent, building/device, prefab IDs, inventory/job state, and possibly simple vehicle/path components, but exact fields are not final.
- Major unresolved issues are actual repo state, Lua-vs-JSON policy, render command/camera API, external compatibility, MVP component fields, and licence validity.

### `Dominium_Architecture_III`

- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- The user then uploaded `dominium.7z`, saying it was the git repository as of that moment. **FACT:** The prior assistant said it could not open `.7z` archives in that environment. That means the actual repository state remained unverified at that stage. This became important later, because many implementation ideas were discussed without confirmed access to the repo contents.
- This created one of the main unresolved issues. DX12 was discussed earlier, but omitted from the latest renderer list. X11 and Wayland were discussed earlier, but the latest platform categories are POSIX, SDL1, SDL2, and Native. Therefore, the final status is:
- DX12 is **UNCERTAIN / UNVERIFIED** and should not be assumed.
- X11/Wayland placement is unresolved.
- The prior assistant summarized these files as containing two different launcher concepts: an engine-rendered launcher view and a native Win32 launcher. It also claimed the CMake file built the Win32 source for non-Windows targets. However, this report must preserve that as **UNCERTAIN / UNVERIFIED**, because the files were not re-inspected during final packaging.
- This is final as a user-stated product goal. Feasibility still requires verification.
- Those outputs are important artifacts, but they are not the substance of the design. Their purpose is to preserve this chat's decisions, uncertainty, and future work for later aggregation into a master Project Spec Book.
- What remains uncertain is not the constraint itself, but how existing repository code currently enforces it. That requires code inspection.
- Uncertainty remains around how the uploaded launcher code currently maps to this desired UI. The prior assistant said the uploaded native launcher had different tabs, including Console and missing Accounts, but this must be verified.
- Uncertainty remains around aliases. Earlier names such as `dom-launcher` and `dom-setup` might be kept as aliases, but that was not finalized.
- The major unresolved issue is taxonomy: how exactly POSIX, SDL1, SDL2, and Native map to Win32, Cocoa, Carbon, X11, Wayland, headless, and retro platforms.
- The unresolved part is feasibility. Supporting Linux 2.4, Mac OS 8.5, Windows 3, and MS-DOS requires separate toolchain research. The chat did not verify that every target can be built.

### `Dominium_Architecture_IV`

- Source file: `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`
- The conclusion was clear and accepted: **Domino is the reusable engine; Dominium is the game/product layer**. What remains uncertain is the actual repository state. The chat planned the split, but did not verify whether the repo already matches it.
- The unresolved issue is that the actual repo was not inspected in this chat. The planned structure may not match the current files.
- The unresolved issue is practical feasibility, especially for retro targets and Carbon OS. Their actual toolchains and system calls remain unverified.
- The unresolved issue is the exact IR payload layout and how far limited renderers should go. A CGA or MDA backend cannot realistically support modern 3D in the same way as Vulkan. The agreed approach is explicit capability flags and graceful fallback or no-op behaviour.
- The unresolved issue is the exact manifest/schema format. JSON, TOML, and INI-like examples appeared in prompts, but no final schema choice was made.
- The unresolved issue is that external packaging details require verification. WiX, macOS notarization, Linux packaging, and AppImage tooling are all external-world facts and may be stale.
- The package and this report should help future assistants continue without re-reading the whole chat. However, they must preserve uncertainty: actual repo state is unverified, some transcript sections were skipped, external tooling facts may be stale, and assistant suggestions are not user decisions unless accepted or built upon.
- It is also reasonable to infer that the user wants the future project spec book to preserve rationale, not just lists of decisions. The later handoff requests emphasised visible rationale, rejected options, uncertainty, and changes of direction.
- Before doing it, verify the repo state. The generated prompts assume specific directories and may need adaptation.
- Important items labelled as fact, inference, or uncertainty.
- The **Phase 4 setup prompts** describe setup core and wrappers for Windows, macOS, Linux, and retro targets. They should be used only after verifying current external packaging tool details.
- The chat also created downloadable report files and handoff packages. For understanding the substance of the chat, the important thing is not the files themselves but the information they preserved: roadmap, decisions, tasks, constraints, risks, and unresolved issues.

### `Dominium_Complete_Conversation`

- Source file: `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`
- Uncertainty: the raw pasted prompt is not the current repo authority unless materialized in repo canon. The later audit found that it had in fact been materialized under `docs/canon/constitution_v1.md`.
- Uncertainty: during this preservation pass, a potential inconsistency appeared: some docs claim product roots moved under `apps/`, while an earlier inspected code path under root `client/` was available and `apps/client` was not fetched successfully. This must be verified against the current physical tree.
- Unresolved goals include verifying the latest physical repo tree, proving runtime implementation maturity, formalizing public ABI/API boundaries, completing layout/naming cleanup, and building a second Domino-based product to prove reuse.
- 1. Verify the current physical repo tree against layout docs and `contracts/repo/layout.contract.toml`.
- The user likely wants future assistants to challenge weak framing, preserve uncertainty, avoid shallow "best practice" lists, and focus on decisions that survive future rewrites.
- "Create a gated plan for verifying current repo layout and exceptions."

### `dominium_domino_codex_planning`

- Source file: `docs/archive/conversations/dominium_domino_codex_planning/dominium_domino_codex_planning__human_readable_chat_report.txt`
- The most important things to remember are: the project's strict architecture constraints, the Milestone-0 prompt sequence, the later shared CLI/TUI/GUI/input/render prompt sequences, the missing pack-system prompt, the unified startup policy, the unresolved repo-verification issue, and the need to treat generated prompts as plans rather than proof of implementation.
- The assistant generated the first two prompts. The third was never produced because the conversation changed direction. That missing third prompt remains an important unresolved item.
- However, the later context transfer packet treated that inspection claim as **UNCERTAIN / UNVERIFIED**. This was careful and correct: within the visible chat, there was no reliable tool trace proving the repo had actually been inspected. Therefore, future assistants must verify `dominium.zip` or the active checkout before relying on the platform/render/API answer.
- What remains uncertain is how much of this architecture already exists in the current repo and how much is still planned. The chat produced prompts and plans, but it did not prove execution.
- The unresolved issue is whether those prompts were ever run and whether the generated code, if any, conforms to the project's strict C89/C++98 and determinism requirements.
- The unresolved complication is C89 portability. Standard C89 does not provide `long long`, but `u64`, `i64`, and `q48_16` require 64-bit representation. Future work must decide whether to allow compiler extensions, emulate 64-bit values for strict retro targets, or define platform tiers with conditional support.
- The unresolved issue is that the prompt's minimal manifest parser and hardcoded platform path are only a starting point. A real implementation must generalize product discovery, avoid duplicated path logic, and preserve compatibility/versioning rules.
- The unresolved issue is whether the prompts are too broad and whether the existing repo already has overlapping modules. Future work should inspect the repo before applying these prompts.
- What remains uncertain is how much of this already exists in the repo and how realistic cross-platform IME is for early implementation. IME is often platform-specific and complex, so the generated prompt should probably be applied carefully or split.
- The unresolved issue is API alignment. The prompt proposed new APIs, but the actual repo's dgfx API may already differ. The final report therefore recommends verifying current render headers and backend code before applying the prompt.
- The unresolved work is to generate this prompt, ideally after inspecting actual content/pack docs and source files. The prompt should probably be staged, because pack integration touches content loading, dependency resolution, audio, rendering, shader compilation, GUI themes, vector icons, and streaming.
- This topic remains important but unresolved in implementation. The policy is strong, but the implementation prompt needs repair to avoid linking problems. The safer approach is to keep the generic mode-selection algorithm independent of product-specific symbols, likely through callback tables or product-local dispatchers.

### `dominium_full_conversation`

- Source file: `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`
- Verify live repo state, then review/run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if the queue/status supports the maintenance lane.
- Preserve uncertainty labels.
- Future chats could easily misunderstand this conversation by treating Workbench as a GUI framework, treating raylib as the engine, resuming broad structure cleanup, skipping projection conformance, or assuming live repo status from stale pasted reports. The mitigation is to verify repo state first, preserve the contract/service/projection/provider distinctions, and follow the task queue.
- The best next action is to verify live repo state, then review or run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if status supports it.

### `dominium_setup`

- Source file: `docs/archive/conversations/dominium_setup/dominium_setup_handoff__human_readable_chat_report.txt`
- FACT: The setup system was repeatedly defined as the only component allowed to install files, modify system/installation state, own installed-file metadata, repair installs, verify artifacts, uninstall, downgrade, upgrade, and roll back. This is the most important architectural rule from the chat.
- What remains uncertain is the actual current implementation state in the repository after the applied Codex prompts. The design is clear, but the repo must still be inspected.
- FACT: The final canonical setup layout uses `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- The unresolved part is whether the actual repository now matches this canonical layout.
- UNCERTAIN / UNVERIFIED: Exact Visual Studio 2026 behavior and toolchain details should be verified in the current environment before relying on them.
- UNCERTAIN / UNVERIFIED: The user stated the prompts were applied, but this chat did not show the final repository tree or build results.
- UNCERTAIN / UNVERIFIED: The actual schema files under `schema/setup/` need to be checked.
- Several goals remain unresolved because the actual repo was not inspected here. We do not know whether the applied Codex prompts fully succeeded, whether setup builds, whether schemas exist, whether `libs/contracts` is complete, or whether setup/launcher CLI smoke tests pass.
- FACT: The chat repeatedly established that setup is the only component allowed to install, upgrade, downgrade, repair, verify, uninstall, roll back, and own installed-file metadata.
- FACT: The final setup layout is `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- This affects future application work, but some exact implementation paths remain unverified.
- Another tradeoff was between broad future support and current implementation scope. The architecture allows legacy platforms, storefronts, and offline/online acquisition, but many implementation details remain unverified. The chat preserved those as goals without pretending they are already implemented.

### `Domino_Dominium_Workbench`

- Source file: `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md`
- Reliability note:** This is a human-readable consolidation, not a live repository audit. Repo-current statements that came from pasted material or prior-chat excerpts remain **UNVERIFIED** until checked against the live `julesc013/dominium` repo and current AIDE/validator outputs.
- Verify current live repo status and task gate state.
- > Verify repo state, then generate `COMMAND-RESULT-VIEW-SLICE-01`.

### `domino_engine_refactor_prompts`

- Source file: `docs/archive/conversations/domino_engine_refactor_prompts/dominium_domino_engine_refactor_prompts__human_readable_chat_report.txt`
- The answer also introduced a deterministic bytecode VM as the preferred way to support modded behavior. A question was raised about whether native-code plugins should also be allowed, but the user did not answer. That remains unresolved.
- What remains uncertain is the actual repository state. The chat designed architecture and prompts, but did not inspect source code. Therefore the plan needs repo verification before implementation.
- The unresolved work is to generate detailed subsystem implementation prompts for heat, power, fluids, atmospheres, vehicles, and structural loads after the core engine spine is implemented.
- The remaining uncertainty is plugin policy. A deterministic VM was proposed, but whether native-code plugins are allowed remains unresolved.
- What remains uncertain is the exact thresholds and content policies for when things promote or demote.
- The unresolved issue is how much of STRUCT compilation should be implemented first. The prompt plan is broad; a real implementation may need a smaller first milestone.
- ignoring FACT/INFERENCE/UNCERTAIN labels;
- UNCERTAIN / UNVERIFIED:** The package files were generated in the sandbox during the prior step, but repository files were not created or inspected.
- The prompts are detailed, but repository state is unverified. Blindly applying them could create duplicate systems or wrong paths.
- Before merging this into a master spec, preserve uncertainty labels and verify against repository state and later decisions.
- The most important unresolved issues are VM/native plugin policy, exact Q formats, repository structure, existing TLV/scheduler state, and derived cache hash policy.
- 9. "What should I verify in the repository before running Codex Prompt 1?"

### `engine_baseline_architecture`

- Source file: `docs/archive/conversations/engine_baseline_architecture/domino_dominium_engine_baseline_architecture__01_human_readable_report.md`
- Uncertainty: the repo has many modules and some historical/legacy surfaces, so exact implementation maturity varies by subsystem. The distinction should remain a formal requirement in a master spec.
- Uncertainty: the full determinism envelope across all current modules was not independently re-run in this chat. User-supplied local validation results should be preserved but verified before being used as audit proof.
- Uncertainty: this remains strategic architecture, not an implemented decision.
- Unresolved goals include:
- User wants uncertainty labelled and framing corrected when evidence disagrees.
- UNCERTAIN: whether the user wants Unreal integration at all as a client/editor.
- UNCERTAIN: exact tolerance for using external geometry libraries.
- UNCERTAIN: whether broad repo restructuring will be desired after Milestone 0.
- UNCERTAIN: exact visual style, UI stack, or programming language evolution.

### `Foundation_Workbench_Codex`

- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- What remains uncertain is how quickly this architecture will move from contracts and fixtures into runtime implementations and product slices. The next chat should not assume runtime provider resolvers, package runtime, or Workbench shell exist.
- verify latest live repo state after user-pasted Wave 1 completion;
- 1. Verify live repo state.
- The user wants direct, evidence-grounded, audit-ready answers; timestamps/model labels; explicit uncertainty; no repeated clarification unless necessary; large continuous Codex prompt blocks when generating prompts; targeted tests instead of full suites; and rapid progress toward Workbench/code.
- The user is likely to reject slow, report-only, overcautious process. Future assistants should produce executable next prompts quickly after verifying state.
- It is uncertain how many concurrent Codex workers the user will actually run at once and whether the user wants coordinator prompts or worker prompts next.
- The most important continuation is: verify current `origin/main`, confirm Wave 1 and Workbench validation state, then generate or run `COMMAND-RESULT-VIEW-SLICE-01`.

### `Framework_Open_Source_Provider`

- Source file: `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`
- The chat inspected `julesc013/dominium` and found evidence of existing abstractions such as system and graphics layers, stubs, and soft-backed backends. The finding was that raylib could fill concrete provider gaps without replacing the architecture. However, current repo facts are stale/uncertain and must be verified, especially the C17/C++17 vs C90/C++98 baseline contradiction.
- The exact first implementation branch, versions, and dependency pins are unresolved. The exact Domino Framework ABI is unresolved. The exact Lua version is unresolved. The current repository baseline must be verified. The formal policy for GPL/LGPL/unclear license material is unresolved. The sparse simulation and CAD systems need formal specs and prototypes.
- The raylib decision was also directionally accepted. The user repeatedly expressed enthusiasm for raylib and asked about using as much of raylib infrastructure as possible. The caveat is that raylib is a provider suite, not architecture. This affects rendering, audio, input, asset preview, and Workbench bootstrap.
- 1. Verify repo baseline and dependency versions.
- The user requires source-grounded, audit-ready, uncertainty-labelled responses. The preservation prompt explicitly requires FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT labels, no invented facts, no treating brainstorms as decisions, and no over-compression. The prompt also requires a human-readable report first and downloadable files if possible ?filecite?turn29file0?.
- The most blocking unresolved issues are repo baseline verification, exact dependency pins, minimal framework ABI, provider profile order, deterministic simulation spec, and license policy.
- Verify the current `julesc013/dominium` CMake language baseline.

### `gui_binary_content`

- Source file: `docs/archive/conversations/gui_binary_content/dominium_gui_binary_content_handoff__human_readable_chat_report.txt`
- GPT-5.5 Pro - 2026-05-27 00:00:00 Australia/Melbourne; time UNVERIFIED
- whether knowledge systems should include uncertainty, false beliefs, or lost knowledge,
- This stage established a pattern that continues throughout the chat: the user does not want impressive-looking prompts that hide unresolved design choices. The user wants the assumptions exposed before anything is formalized.
- The assistant agreed with the general direction, but added caveats. The most important were:
- Those caveats were not final user decisions, but they are important warnings.
- The conclusion was not "run the prompt now." The conclusion was that CONTENT0 is a strong foundation but needs discussion before finalization. The assistant-generated rewrite is useful but not final. The unresolved issues need to be resolved before Codex or any implementation work touches the repository.
- What remains uncertain is how exactly to encode these ideas in schemas and data. For example, it is not yet decided how deterministic seed hierarchies work, how macro content refines into micro content, or how timeline causality should be represented.
- The unresolved issue is the shared backend/UI contract. Without that, the GUI plan is only a list of technologies.
- The conversation did not yet define how those product backends are exposed. That remains the most important unresolved design issue.
- The assistant caveat was that old .NET support must not be faked. Supporting .NET 4.0-era machines is not the same as targeting .NET 4.8. This remains a technical verification item, not a fully resolved decision.
- The assistant caveat was that old macOS support requires serious toolchain planning. A current Xcode version may not target macOS 10.9. AppKit also does not necessarily need to be Intel-only. These are important but not fully verified within this chat.
- The unresolved question is whether macOS 10.9 is a hard requirement or an aspirational compatibility goal.

### `Language_Platform_Architecture`

- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.
- Exact tolerance for exceptions/RTTI inside private C++17 code remains unsettled. Exact platform floors and raylib/SDL2 priority remain unresolved.
- Verify the Windows 7 and macOS 10.9 toolchain/library assumptions using official sources.

### `launcher_app_layer`

- Source file: `docs/archive/conversations/launcher_app_layer/dominium_launcher_app_layer_handoff__human_readable_chat_report.txt`
- These prompts matter because they superseded earlier advice. They also created a new practical priority: verify that the applied prompts actually succeeded.
- This changed the correct future behavior. The next assistant must not redesign. It must implement, audit, maintain, document, verify, and harden.
- This matters because it prevents platform-specific drift. If CLI has `verify`, GUI must not implement a different hidden version of `verify`. If GUI has a pack enable flow, it should map to the same command/intent as CLI and TUI.
- The final purity prompt required those to be moved or quarantined. However, actual repo success remains unverified in this chat.
- The important change is that the conversation moved from "What architecture should we use?" to "Architecture is locked; how do we verify and harden the implementation?"
- The largest unresolved goal is verifying the actual repo. The user stated that two Codex prompts were applied, but this chat did not independently verify the filesystem, build, tests, scripts, or launcher docs.
- Another unresolved goal is confirming whether the launcher hardening prompt has been applied.
- A third unresolved goal is confirming whether command graph, UI IR, binding validation, zero-pack tests, RepoX changelog display, and BUILD-ID mismatch refusal are implemented.
- This decision depends on CMake and script enforcement. It remains operationally unverified until the current repo is checked.
- The launcher may expose repair or verify entry points in the sense that it can invoke setup through a contract, but it must not perform install mutation itself. This separation protects auditability and prevents hidden mutation.
- This decision reflects the state of the project: after major refactors and applied prompts, the next risk is planning on assumptions. The correct move is to audit, document, verify, and harden the current launcher implementation.
- stale or unverified repository assumptions,

### `Launcher_Setup_Architecture`

- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Uncertainty:** The exact repository layout and existing implementation were not inspected in this chat.
- Uncertainty:** The final language boundary for setup remains unresolved after the later C89/dsys/dgfx launcher direction.
- Uncertainty:** The exact mapping into runtime binaries remains unverified.
- Uncertainty:** Accounts/social/wiki/forum/direct messaging are future-facing and were not converted into the final five-tab implementation plan.
- Uncertainty:** Earlier setup designs used JSON manifests. Later dsys/dgfx architecture leaned toward TLV `.dmeta` files.
- Uncertainty:** Actual plugin ABI details and dynamic loading support depend on dsys/repo APIs.
- Uncertainty:** Actual dsys/dgfx APIs were not inspected.
- Conclusion reached:** This chat is now documented and can be merged later, but with caveats.
- INFERENCE:** The user wanted to avoid later assistant confusion by preserving rejected options, uncertainties, and changes of direction.
- The unresolved goals are mostly implementation-definition questions:
- The main assumption throughout is that the underlying project either already has, or will have, the shared libraries and platform abstractions described. That assumption is unverified in this chat.
- The user wants strict engineering tone, detailed reasoning, and preservation of uncertainty. In this specific request, the user asked for prose rather than a register dump.

### `Modularity_AIDE_Refactorability`

- Source file: `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__01_human_readable_report.md`
- The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.
- 1. **TASK-09** - Verify live repo baseline: current branch, root inventory, validators, CTest status, generated artifacts.
- The user prefers source-grounded, audit-ready decisions; bounded uncertainty; explicit task prompts; and reusable engineering doctrine. Future assistants should avoid shallow affirmation and should distinguish accepted user decisions from assistant recommendations.
- Important caveat: the only current uploaded file available for this task is `Pasted text.txt`, which contains the preservation-package prompt. Earlier generated handoff files, ZIP packages, or uploaded docs referenced in prior conversation are not available in this chat unless the user re-uploads them.
- The most serious risk is that a future assistant treats this chat as if it verified the live repo. It did not. The second serious risk is that it hardens every assistant suggestion into a requirement. Several items are strong recommendations aligned with user goals, but still require implementation review. Future chats must preserve labels and verify stale facts.
- Future assistants must verify live repo state before implementing cleanup.

### `omega_xi_pi_architecture_future`

- Source file: `docs/archive/conversations/omega_xi_pi_architecture_future/dominium_omega_xi_pi_architecture_future_proofing_planning__01_human_readable_report.md`
- Preserve FACT / INFERENCE / UNCERTAIN labels.
- Do not invent or flatten uncertainty.
- 7. "List all artifacts I should verify in GitHub main."
- 9. "What should I verify before starting Sigma?"

### `OS_Interface_Repo_Architecture`

- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- The unresolved goals are implementation-level. The repo still needs command dispatch unification, product boot proof, portable projection proof, AppShell rendered-mode law update, Workbench module contracts, document/patch/result/refusal schemas, and a boot-to-replay MVP. It also needs continued exception retirement, CTest/RepoX remediation, and verification of current build status.
- 2. Repair canonical verify test discovery.
- The user wants uncertainty labels and correction of incorrect framing.
- This preservation task specifically required FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels, stable IDs, registers, spec sheets, an aggregator packet, self-audit, and downloadable files if tools are available.
- UNCERTAIN: Whether the user wants to rename `engine` conceptually to `kernel` in code, or only use kernel as a conceptual layer.
- UNCERTAIN: Whether the final public product name should be Dominium Workbench, Dominium Studio, Domino Workbench, or something else.
- UNCERTAIN: How aggressive the next actual code refactor should be versus staged adapters and codegen.

### `platform_renderer_api_plan`

- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- This is not a fatal problem for the prompt pack, because the prompts themselves repeatedly tell Codex to discover files with `rg`, `tree`, `type`, CMake commands, and target listing. But it is a major caveat for any future assistant: do not assume the actual repo matches every file path or API name unless checked.
- UNCERTAIN / UNVERIFIED:** The conversation did not prove that these prompts were actually applied to the repository. They are an assumed prerequisite, not verified code state.
- Uncertainty remains about actual repo state. The prompts are designed to discover the repo state, but the chat itself did not inspect the archive.
- The final active prompt pack narrowed runtime completion to Tier-1 on Windows and compile-gated correctness for Tier-2. This is a practical compromise because Codex runs on Windows. But it also creates a caveat: if "fully complete" later means fully running X11/Wayland/Cocoa/Metal/Vulkan, more prompts or native CI validation will be required.
- This became one of the final "done" gates, along with `scripts\build_codex_verify.bat`.
- This matters because the conversation was long and contained multiple plans, superseded options, caveats, and active artifacts. The report package and this plain-language report exist to prevent future assistants from restarting, re-asking, or losing distinctions between decisions, brainstorms, and uncertainties.
- The user also seems to want future assistants to operate with high continuity and not lose subtle distinctions. This is inferred from the repeated requests for maximum-fidelity transfer, stable IDs, labels, uncertainty tracking, and report packaging.
- Another unresolved goal is whether the master engine prompts 1-14 are truly implemented. The later plan depends on them, but this chat did not verify the repo.
- This is a decision with a caveat. Because Codex runs on Windows, the final prompt pack treats non-Windows Tier-2 platforms as host-gated and compile-correct when built on their native hosts, not fully runtime-validated on Windows. This makes practical sense, but it may not satisfy a stronger interpretation of "fully complete" if the user later demands runtime Tier-2 validation.
- Fifth, the user wanted **future spec-book construction**. That means uncertainty and provenance matter. The chat repeatedly preserved labels such as FACT, INFERENCE, and UNCERTAIN / UNVERIFIED. This prevents future aggregation from treating assistant suggestions or brainstorms as binding decisions.
- cmake -S . -B build\verify_initial -G Ninja -DCMAKE_BUILD_TYPE=Debug
- cmake --build build\verify_initial --target help

### `platform_support`

- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- UNCERTAIN / UNVERIFIED: The name "Domino" was never confirmed by the user. Future work should treat "Domino" as an assistant-created placeholder unless the user explicitly accepts it. The useful idea is the distinction between full product support and reduced engine/core support, not necessarily the name.
- The main unresolved issue is the exact definition of support. Does Tier-0 mean identical feature parity, simultaneous release, identical save compatibility, identical UI, equal QA coverage, or some platform-specific differences? The assistant inferred that Tier-0 should mean feature parity, full QA, long-term support, and high release priority, but the exact contractual meaning still needs formal definition.
- What remains unresolved is the exact PC baseline. The chat did not decide whether Windows 10, Windows 11, or both are required. It did not decide whether Windows ARM64 matters. It did not decide whether macOS support includes Intel Macs, Apple Silicon Macs, or both. It did not define Linux distributions, glibc requirements, Flatpak/AppImage/deb/rpm packaging, X11/Wayland policy, or Steam Deck verification.
- UNCERTAIN / UNVERIFIED: The chat did not establish minimum Android API level, ABI list, target graphics APIs, Play Store rules, Android TV status, Android Go status, Automotive status, Chromebook status, or vendor ROM support. These need future decisions and current-source verification.
- The user also listed iPod Touch, Apple TV, Apple Watch, Mac, macOS, tvOS, watchOS, and Apple Vision Pro indirectly through AR. These were not classified in detail. INFERENCE: macOS belongs under PC. UNCERTAIN / UNVERIFIED: tvOS, watchOS, and visionOS remain undecided. Full Dominium on Apple Watch is not established and should not be assumed.
- The unresolved issues are substantial. The chat did not decide whether WebGPU is required, whether WebGL fallback is mandatory, whether the game must work offline as a PWA, whether WASM threading/SIMD is required, how browser storage will work, how asset loading will be handled, or what browser versions will be supported.
- UNCERTAIN / UNVERIFIED: Current console platform facts were not verified in this chat. Future work must verify official PlayStation, Xbox, and Nintendo developer requirements from current official sources before implementation planning.
- INFERENCE: PC handhelds should be subtargets under PC, with their own QA and UI profiles. UNCERTAIN / UNVERIFIED: Steam Deck's exact tier was not finally decided.
- UNCERTAIN / UNVERIFIED: XR was never promoted to top-tier. Its priority remains unresolved. Future work should not let XR quietly expand the scope of the main product unless the user explicitly elevates it.
- INFERENCE: The user was also trying to prevent vague "support everything" language from hiding real engineering constraints. The repeated requests for decisions, constraints, unresolved issues, verification items, and future actions imply that the user wanted a plan that could later become part of a formal project specification.
- The biggest unresolved goal is turning the platform direction into a real, implementable matrix. The chat did not define exact minimum versions, APIs, architectures, release timelines, engine/toolchain, build system, store strategy, or QA device list.
- The decision depends on an unresolved assumption: that the engine/toolchain can support Android well enough for the intended Dominium experience. That assumption needs verification after engine/toolchain choice.

### `Portability_Assurance_Future_Proof`

- Source file: `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md`
- The chat proposed using standards such as DO-178C, NIST SSDF, OWASP ASVS, SLSA, and SPDX as design inputs only. The proposed internal version is DDAP v0 with DIL levels. Uncertainty: user has not explicitly ratified DDAP.
- The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.
- Caveat: carry forward as `INFERENCE / assistant recommendation`.
- Caveat: carry forward as `FACT goal + INFERENCE architecture`.
- Caveat: carry forward as `assistant recommendation`.
- Implications: Safe for aggregation only with caveats.
- Caveat: carry forward as `FACT / UNCERTAIN scope`.
- 10. Feed this package into the master Project Spec Book with caveats.
- The user explicitly required human-readable preservation, uncertainty labels, no invented facts, no silent inference, and no treating assistant recommendations as user decisions. The user explicitly values portability, modularity, extensibility, reuse, replaceability, future-proofing, and proper long-lived engineering.
- Resolution path: Verify against official/current sources before normative text.
- The uploaded prompt requested this preservation package. The main caveat is that the package preserves visible chat context and the uploaded prompt, not a guaranteed hidden full transcript or inspected repository. The best next action is to inspect the actual repo and turn the strongest recommendations into a small set of enforceable policies and one conformance-test pilot.

### `readme_ports_determinism`

- Source file: `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__human_readable_chat_report.txt`
- What remains uncertain is whether the actual repository `README.md` matches the final pasted version. The chat only saw pasted text and generated prompts; it did not inspect a Git repository.
- The unresolved issue is whether a metadata-only `/ports` directory still violates the user's preference. The final README keeps `/ports` in a limited form, but the user's wording could mean no `/ports` directory at all. That should be clarified before writing the directory contract.
- The unresolved work is to define the actual network protocol, prediction model, rollback window, reconciliation logic, and state-hash validation.
- The major unresolved goal is deciding exactly what "no separate ports directory/system" means physically in the repository. The final README allows `/ports` as metadata-only. That may satisfy the user, but it is not confirmed. If the user meant no `/ports` directory at all, the README still needs another revision.
- Another unresolved goal is making the README and normative specs align. The README says specs are authoritative, but those specs were not inspected in this chat.
- UNCERTAIN / UNVERIFIED: `/ports` as metadata-only is the current README state, but may not be fully accepted.
- A related rejected idea was **retro build flows under `/ports/<target>` containing source or alternative implementations**. The final README superseded this with metadata-only `/ports`, assuming `/ports` is retained at all. This rejection is final for source code and behavior, but the existence of `/ports` itself remains uncertain.
- The first next step is to verify the actual repository `README.md` against the final pasted README. The chat only used pasted text. If the repository differs, future work should start from the actual file, not from memory.
- Possible blockers include the unresolved `/ports` question, missing access to actual repository files, and unspecified algorithms for RNG, state hashing, CRCs, and content hashing.
- The reporting constraints later in the chat were also explicit: preserve facts, inferences, uncertainty, rejected options, contradictions, artifacts, prompts, and rationale. Do not invent. Do not silently infer. Do not treat assistant suggestions as user decisions unless accepted.
- The user's profile and instructions emphasize bluntness, rigor, directness, and fact-checking. In this chat, they repeatedly asked for high-fidelity state preservation and explicitly rejected over-compressed summaries. Future assistants should avoid vague reassurance and instead give concrete analysis, caveats, and next actions.
- The ninth artifact was the final README pasted by the user. It is the current textual baseline, but it is unverified against the actual repository.

### `Refactor_Architecture`

- Source file: `docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__human_readable_chat_report.txt`
- Reliability note: Repository state, Codex execution, exact version numbers, and actual file modifications are **UNCERTAIN / UNVERIFIED** unless explicitly stated otherwise.
- The most important thing to remember is that this chat did not implement the refactor. It designed the architecture and generated prompts and handoff material. Any future assistant must verify actual repository state before assuming files were moved, prompts were applied, or code was updated.
- UNCERTAIN / UNVERIFIED:** It did not establish that this system already exists in code.
- What remains uncertain is the exact degree to which existing code currently respects that boundary. The user provided a repo tree, but this chat did not inspect or modify code directly.
- Unresolved details include exact default DOMINIUM_HOME paths per OS and exact implementation of import/GC.
- Unresolved details include exact schemas, parser choice, tests, and actual code implementation.
- The key unresolved point is implementation timing. The report preserves this architecture, but the initial Codex refactor was not supposed to rewrite the entire UI system immediately.
- Actual implementation is unresolved. This chat generated architecture and prompts, not a verified changed codebase.
- Specific unresolved goals include:
- The immediate plan is not to redesign everything again. The immediate plan is to verify current repo state and then implement the structural refactor in a controlled way.
- This matters because the chat produced prompts, but did not verify that they were applied. If Codex has not run, the next step is to run or refine the master refactor prompt. If Codex has run, the next step is the consistency pass.
- Preserve FACT / INFERENCE / UNCERTAIN labels in transfer/report contexts.

### `Refactor_Control_Plane`

- Source file: `docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__01_human_readable_report.md`
- Unresolved goals include finishing AIDE Q35-Q57, stabilizing Dominium CTest/RepoX blockers, defining final AIDE install/upgrade bundles, implementing root recycling machinery, deciding when product boot proof can proceed, and later deciding whether AIDE Runtime/Gateway/Hosts are truly needed.
- 1. Verify current Dominium HEAD and POST-CONVERGE status.
- The user values direct, source-grounded, audit-ready, detailed answers. The user asked for preservation packages that are human-readable and machine-aggregatable. The user repeatedly prefers not to lose nuance, rejected options, uncertainties, or artifacts. The user wants current facts verified when possible and wants future assistants to avoid re-asking answered questions.
- UNCERTAIN: Exact public-facing naming for AIDE Core/Kernel remains partly open. Exact threshold for accepting CTest-warning status remains a user/repo governance decision. Exact final AIDE installation packaging details remain pending.
- Future assistants must verify live repo state before implementing.
- "Merge this with another chat's preservation package without losing uncertainty labels."

### `Release_Identity_and_Versioning`

- Source file: `docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__01_human_readable_report.md`
- The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.
- GBN should identify CI/public/internal builds and appear as provenance, e.g. `+gbn.7137`, but it must not be used as SemVer precedence. BII should primarily be structured manifest metadata, because it may encode lane, target, kind, configuration, and other build identity fields. The exact BII schema remains unresolved.
- The main unresolved goals are to produce formal specs: Release Constitution, SemVer Component Inventory, Suite Release Policy, Build Identity Spec, Channel/Lifecycle Spec, Artifact Naming Spec, Manifest Schema, Target Taxonomy, and Capability Registry.
- It is still uncertain how strict the user wants suite `X.Y.Z` field meanings to be, whether capabilities should fully replace compatibility profiles or coexist with them, and how much old-platform support should be real versus aspirational.
- The most important unresolved issue is formal classification. Without knowing which entities are strict SemVer components, suite versions, product release IDs, build fields, or capabilities, the rest of the policy cannot be enforced safely.
- Platform targeting remains unresolved. The chat concluded that coarse families like WinNT5, WinNT10, MacOSX4, Linux5, or DOS5 are useful support labels, but exact binary compatibility needs target baselines and runtime/toolchain profiles. Linux kernel major alone is not enough. Windows 9x/NT/NT5/NT6/NT10 likely need separate build lanes or at least explicit tested baselines.

### `testx_repox_governance`

- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- This topic remains unresolved in implementation because the repo snapshot showed `.dominium_build_number` and `update_build_number.cmake`, but the chat did not inspect their contents. Those files may still implement older build-number behavior. That must be verified.
- The unresolved part is implementation verification. The repo has Sol/Earth content in `data` and `game/content`; the engine must not assume those exist.
- The unresolved part is how much of TESTX is actually implemented in the repo. The repo contains many tests and scripts, but this chat did not inspect them. A rules-to-checks audit is needed.
- This remains conceptually accepted in the chat, but implementation is unverified.
- The unresolved goals are mostly implementation and verification:
- The repo already has UI IR/codegen infrastructure. The next step is to verify whether GUI/TUI truly bind to the CLI command graph and whether UI is data rather than logic.
- The user has Windows 10 + VS2022. The next step is to verify v141/v141_xp/SDK components and create isolated CMake presets for XP/Win7/Win8/Win10/Win11 builds.
- Acting before verifying repo state.
- The user also explicitly required the report style to preserve facts, inferences, uncertainties, rejected options, artifacts, timelines, risks, and visible rationale.
- This recommendation is useful for immediate practical builds but requires verification of installed components and current toolchain facts.
- Manual product SemVer is required, but the actual file layout is unverified.
- The repo has UI tooling, but this chat did not verify that GUI/TUI bind to CLI command graph or that tools are read-only by default.

### `Timekeeping_and_2038_Resilience`

- Source file: `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`
- What remains uncertain is the current exact status of specific libc/OS/toolchain combinations, because those facts can change and were not reverified during this preservation turn.
- What remains uncertain is the precise target list of legacy machines/toolchains and how far compatibility must go, especially for 16-bit compilers with weak or absent 64-bit arithmetic.
- The main unresolved goals are backend audit, ACT serialization audit, civil/astronomical projection design, and verification of external platform facts.
- The main uncertainty is completeness of repo inspection. The assistant read key files, but not all serialization paths and not all platform backends.
- 6. Verify current platform/library facts before using them in formal public documentation.
- The preservation prompt explicitly requires a human-readable report first, not only a machine-readable handoff. It requires uncertainty labels, stable registers, preservation of artifacts, no invented facts, and downloadable files if tools are available. ?filecite?turn30file0?
- The user prefers source-grounded, audit-ready technical reasoning, direct structure, and careful distinction between facts, recommendations, and unresolved issues. PROJECT-CONTEXT indicates Dominium values C89/C++98 portability, deterministic architecture, CLI/TUI support, and clean platform/runtime separation.
- The strongest unresolved technical task is auditing actual backend timers and persistence formats.
- The main conclusion is that Dominium does not need a conceptual rewrite for time. It needs boundary hardening. Future work should audit all DSYS backends, freeze ACT units and serialization, ban wall-clock time from authority paths, make civil/astronomical time a derived projection layer, and verify any external platform facts before making them formal documentation.

### `UE6_Domino_Deterministic_Universe`

- Source file: `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md`
- UNCERTAIN / UNVERIFIED: This is not a complete reconstruction of every Dominium conversation ever held. The project context shows that many other chats exist about platforms, renderers, setup, game architecture, ecology, ECS, launcher design, and development planning, but their full transcripts are not visible here. Those items are labelled PROJECT-CONTEXT when referenced.
- Uncertainty: public UE6 technical capabilities and requirements remain time-sensitive and need verification before any future hard commitment.
- The chat rejected the idea that clients can authoritatively simulate resource production, hidden state, enemy bases, combat, or persistent terrain changes in an MMO. Clients can assist, but the server must verify and commit.
- REJECTED-02: Waiting for UE6 before beginning serious work. Deprioritised because UE6 availability and capabilities remain uncertain.
- The user wants direct, source-grounded, audit-ready answers; explicit uncertainty; bounded estimates; and correction when framing is wrong. The preservation prompt explicitly requires human-readable explanation first, structured registers second, uncertainty labels, no invented facts, no hidden chain-of-thought, and downloadable files if tools are available.
- UNCERTAIN: The final intended role of Domino remains unclear in the visible transcript. It may be a custom engine, target runtime, renderer, or broader platform plan, but the current chat does not fully define it.

### `ui_editor_tool_editor_planning`

- Source file: `docs/archive/conversations/ui_editor_tool_editor_planning/dominium_ui_editor_tool_editor_planning__human_readable_chat_report.txt`
- The most important thing to remember is that this chat was a planning and prompt-generation chat, not proof of implementation. **UNCERTAIN / UNVERIFIED:** No generated prompt is evidence that repository code was actually changed. The next assistant must first verify whether the prompts were executed, inspect the repo/source bundle if available, and avoid treating planned files as existing files.
- The user uploaded screenshot bundles for setup and launcher. **UNCERTAIN / UNVERIFIED:** The screenshots were not inspected in this chat. The assistant still produced a logical layout description, and the user accepted it as useful. Future work should inspect the bundles before claiming exact screenshot fidelity.
- What remains uncertain is the actual state of the code. The user named files, but the chat did not inspect the repository. A future assistant must verify exact paths, build targets, TLV parser implementation, and current launcher behavior.
- Unresolved details include the actual TLV wire format, migration strategy from `launcher_ui_v1.tlv`, and how much legacy data can be preserved during import.
- The unresolved risk is implementation complexity. Real native tab controls, splitter behavior, and scroll panels can be nontrivial in a child-HWND Win32 UI.
- This is a strong planned design, but some details remain assistant recommendations rather than explicit user-confirmed decisions. Future implementation should preserve that uncertainty if writing a formal spec.
- The unresolved issue is that the uploaded screenshot bundles were not inspected. The logical specs are accepted planning artifacts, not verified screenshot extractions.
- The exact scope of IDE-native live editing remains unresolved. The assistant proposed preview hosts, but it is not confirmed whether that fully satisfies the user's desire to use Visual Studio, Xcode, and Linux GUI tools.
- The exact first implementation status is unresolved. The chat generated prompts but did not show Codex execution results.
- UNCERTAIN / INFERENCE:** The assistant generated a preview-host strategy. It was a reasonable way to integrate Visual Studio, Xcode, and Linux tools while preserving DUI TLV as canonical. But the user did not confirm whether this satisfies "utilising all GUI tools available in each IDE."
- The sixth tradeoff was IDE-native editing. Visual Studio and Xcode have their own native designer ecosystems, but those do not naturally edit DUI TLV. The preview-host proposal preserves DUI as canonical while using IDE build/run/watch loops. This is practical but may not fully satisfy a desire for direct IDE designer manipulation. That is why it remains unresolved.
- What must happen before it: verify launcher/setup build targets and loader integration points.

### `Universe_Explorer_Planning`

- Source file: `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__01_human_readable_report.md`
- Uncertain: whether all seven universal layers are now formally captured under exactly that naming. The repo has equivalent or related doctrine, but not every early phrase appears as a single artifact.
- Uncertain: the repo contains pieces of this through affordance/capability/domain docs, but the assistant did not find one single master Deep Primitives spec in the docs it read.
- The most important unresolved issue is that the Universe Explorer plan is still a proposed/recommended next strategy, not yet a completed repo task. The next best action is either to draft `PRESENTATION-CONTRACT-01` / `UNIVERSE-EXPLORER-CONTRACT-01`, or to preserve this chat and merge it with other old-chat reports into a master Project Spec Book.

### `Workbench_AIDE_Product_Spine`

- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- The largest uncertainty is not the conceptual architecture; that has converged. The largest uncertainty is live execution state: whether prompts generated near the end of the chat have already been run locally, committed, or pushed. The next chat should first inspect `.aide/queue/current.toml`, recent commits, and relevant audit files.
- Remaining uncertainty: exact implementation of erosion/ecology/evolution proxies remains future domain work.
- 1. Verify current repo state.
- Explicitly label uncertainty.
- The next chat should verify repo state first.
- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Verify live repo state before acting.
- safe_for_aggregation: "Yes, with caveats"
- "UNCERTAIN / UNVERIFIED"
- "Verify current queue and commits before acting."
- "Preserve uncertainty and rejected options."
- uncertain_or_not_established:

### `World_Architecture`

- Source file: `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__human_readable_chat_report.txt`
- The main unresolved issue is implementation detail. The design says Q16.16 and Q4.12, but the earlier prompt used signed types incorrectly. The future implementation must use unsigned local coordinates or a centered signed design.
- The unresolved parts are the exact meshing algorithm, the fixed-point scaling of `?`, and the sample resolution. A 32? sample grid per 16m chunk was recommended but not confirmed as final.
- The exact solvers remain unresolved. The architecture is clear, but formulas and resolutions are still future work.
- The save format remains conceptual in places. Exact binary headers, endian policy, compression, and migration strategy are unresolved.
- The crucial caveat is implementation: unsigned or centered representations are needed. The design intent is final, but the exact typedefs must be fixed. If the implementation uses signed types incorrectly, the whole coordinate system breaks.
- This is not yet an implementation-level final spec because solver formulas are unresolved.
- FACT:** Core target is C89. This is non-negotiable in principle, but exact portability mechanics are unresolved because strict C89 lacks standard fixed-width integer types.
- The user wants direct, detailed, rigorous, critical responses. The user prefers source labels, uncertainty preservation, and avoiding invented facts. The user does not want assistant suggestions silently upgraded to decisions.
- The most important unresolved issue is the fixed-point implementation detail. The user chose Q16.16 runtime and Q4.12 save-local, but the implementation must choose the exact signed/unsigned representation. The prior prompt's signed version is invalid. This must be resolved before code.
- The second major unresolved issue is C89 portability. The user wants C89, but the architecture needs 64-bit IDs, RNG states, and accumulators. Strict ISO C89 does not standardize `stdint.h` or 64-bit integer types. A portability layer or compiler-extension policy is required.
- The third unresolved issue is exact save encoding. TLV, Region files, content locks, and sparse saves were designed conceptually, but endian policy, padding, alignment, compression, and path grammar still need specification.
- The fourth unresolved issue is solver math. FluidSpaces, weather, hydrology, oil pressure, ruptures, hydraulics, thermal systems, and electrical networks were designed architecturally, but formulas and fixed-point scales are not final. These do not block v0 core implementation but must be resolved before those systems are coded.

### `xstack_lab_galaxy`

- Source file: `docs/archive/conversations/xstack_lab_galaxy/dominium_xstack_lab_galaxy_handoff__human_readable_chat_report.txt`
- But this chat did not verify the repository. That became one of the most important unresolved issues.
- This is one of the most important outputs associated with this chat, but it is also one of the most uncertain because it is user-reported from another chat and not verified directly here. The user explicitly wanted it audited for completion and consistency.
- INFERENCE: The user also wanted to prevent future assistants from flattening nuance. They repeatedly asked for maximum fidelity, uncertainty labels, rejected options, contradictions, and rationale. This implies a strong preference for preserving complexity rather than oversimplifying.
- INFERENCE: The user likely wants to resume productive development after verifying the substrate. The next likely feature area is survival or Lab Galaxy refinement, but the user has not made a final decision in this visible chat.
- 4. From documentation to verifying a new 13-prompt substrate.
- The biggest unresolved goal is verifying the actual repository. The package says what was reported, but not what is proven. Another unresolved goal is deciding what comes next: survival, Lab Galaxy UX, distributed SRZ, or documentation polish.
- The main assumption behind all of this is that the repo can actually enforce these contracts. That remains unverified in this chat.
- The best next step is to verify the actual repository state. This matters because the long 13-prompt transcript is not proof. The user explicitly does not know whether everything was truly implemented.
- Because the user cares about XStack portability, the new assistant should verify that runtime can build/run without `tools/xstack` and that engine/game/client/server do not import or depend on it.
- FACT: The user asked for FACT / INFERENCE / UNCERTAIN labels.
- This matters because future work depends on whether the 13-prompt changes are committed, pushed, or still local. The transcript reports a clean branch ahead by 10 commits, but this chat did not verify it.
- Before merging into a master spec, the aggregator should preserve uncertainty and verify the actual repository.



> SOURCE PATH: `docs/archive/conversations/_audit/DOC_DRIFT_REPORT.md`


## Document Drift Report

This report flags archived claims that may drift from current README, queue, language baseline, or authority order.

### `CONTRA-0001` - `conversation_vs_current_queue`

- Source conversation: `advanced_simulation_infrastructure`
- Source file: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0002` - `stale_external_claim`

- Source conversation: `advanced_simulation_infrastructure`
- Source file: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0003` - `stale_external_claim`

- Source conversation: `advanced_simulation_infrastructure`
- Source file: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0004` - `stale_external_claim`

- Source conversation: `advanced_simulation_infrastructure`
- Source file: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0005` - `conversation_vs_current_queue`

- Source conversation: `app_runtime_platform_renderers`
- Source file: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `runtime_module_loader`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0006` - `conversation_vs_current_queue`

- Source conversation: `app_runtime_platform_renderers`
- Source file: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0007` - `conversation_vs_current_queue`

- Source conversation: `app_runtime_platform_renderers`
- Source file: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0008` - `conversation_vs_current_queue`

- Source conversation: `app_runtime_platform_renderers`
- Source file: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0009` - `stale_external_claim`

- Source conversation: `app_runtime_platform_renderers`
- Source file: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0010` - `conversation_vs_current_queue`

- Source conversation: `app_testx_codehygiene`
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0011` - `conversation_vs_current_queue`

- Source conversation: `app_testx_codehygiene`
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0012` - `stale_external_claim`

- Source conversation: `app_testx_codehygiene`
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0013` - `stale_external_claim`

- Source conversation: `app_testx_codehygiene`
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0014` - `stale_external_claim`

- Source conversation: `app_testx_codehygiene`
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0015` - `stale_external_claim`

- Source conversation: `app_testx_codehygiene`
- Source file: `docs/archive/conversations/app_testx_codehygiene/dominium_app_testx_codehygiene_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0016` - `conversation_vs_current_queue`

- Source conversation: `architecture_codex_prompts`
- Source file: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0017` - `conversation_vs_current_queue`

- Source conversation: `architecture_codex_prompts`
- Source file: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0018` - `stale_external_claim`

- Source conversation: `architecture_codex_prompts`
- Source file: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0019` - `stale_external_claim`

- Source conversation: `architecture_codex_prompts`
- Source file: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0020` - `stale_external_claim`

- Source conversation: `architecture_codex_prompts`
- Source file: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0021` - `conversation_vs_current_queue`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0022` - `conversation_vs_current_queue`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0023` - `conversation_vs_current_queue`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0024` - `conversation_vs_current_queue`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0025` - `conversation_vs_current_queue`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0026` - `stale_external_claim`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0027` - `stale_external_claim`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0028` - `stale_external_claim`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0029` - `stale_external_claim`

- Source conversation: `architecture_ui_providers`
- Source file: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0030` - `stale_external_claim`

- Source conversation: `Build_and_Future_Proofing`
- Source file: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0031` - `stale_external_claim`

- Source conversation: `Build_and_Future_Proofing`
- Source file: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0032` - `stale_external_claim`

- Source conversation: `Build_and_Future_Proofing`
- Source file: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0033` - `conversation_vs_current_queue`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0034` - `conversation_vs_current_queue`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `package_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0035` - `conversation_vs_current_queue`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0036` - `conversation_vs_current_queue`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0037` - `conversation_vs_current_queue`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0038` - `stale_external_claim`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0039` - `stale_external_claim`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0040` - `stale_external_claim`

- Source conversation: `canonical_structure_and_framework`
- Source file: `docs/archive/conversations/canonical_structure_and_framework/dominium_canonical_architecture_repo_foundation__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0041` - `conversation_vs_current_queue`

- Source conversation: `Chronology_Celestial_Systems`
- Source file: `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0042` - `conversation_vs_current_queue`

- Source conversation: `development_routes`
- Source file: `docs/archive/conversations/development_routes/dominium_development_routes__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0043` - `stale_external_claim`

- Source conversation: `development_routes`
- Source file: `docs/archive/conversations/development_routes/dominium_development_routes__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0044` - `stale_external_claim`

- Source conversation: `documentation_standards_readme`
- Source file: `docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0045` - `stale_external_claim`

- Source conversation: `documentation_standards_readme`
- Source file: `docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0046` - `stale_external_claim`

- Source conversation: `documentation_standards_readme`
- Source file: `docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0047` - `stale_external_claim`

- Source conversation: `documentation_standards_readme`
- Source file: `docs/archive/conversations/documentation_standards_readme/documentation_standards_readme_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0048` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_I`
- Source file: `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0049` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_I`
- Source file: `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0050` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_I`
- Source file: `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0051` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_I`
- Source file: `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0052` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_II`
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0053` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_II`
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0054` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_II`
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0055` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_II`
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Windows 98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0056` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_II`
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Windows NT 2000`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0057` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_II`
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0058` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_II`
- Source file: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0059` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0060` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0061` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0062` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0063` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Win98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0064` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Windows 98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0065` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Windows NT 2000`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0066` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Mac OS 9`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0067` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Mac OS 8`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0068` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_III`
- Source file: `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0069` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_IV`
- Source file: `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0070` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_IV`
- Source file: `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0071` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Architecture_IV`
- Source file: `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0072` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_IV`
- Source file: `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0073` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_IV`
- Source file: `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0074` - `stale_external_claim`

- Source conversation: `Dominium_Architecture_IV`
- Source file: `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0075` - `conversation_vs_current_queue`

- Source conversation: `Dominium_Complete_Conversation`
- Source file: `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0076` - `stale_external_claim`

- Source conversation: `Dominium_Complete_Conversation`
- Source file: `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0077` - `stale_external_claim`

- Source conversation: `Dominium_Complete_Conversation`
- Source file: `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0078` - `stale_external_claim`

- Source conversation: `dominium_domino_codex_planning`
- Source file: `docs/archive/conversations/dominium_domino_codex_planning/dominium_domino_codex_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0079` - `stale_external_claim`

- Source conversation: `dominium_domino_codex_planning`
- Source file: `docs/archive/conversations/dominium_domino_codex_planning/dominium_domino_codex_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0080` - `stale_external_claim`

- Source conversation: `dominium_domino_codex_planning`
- Source file: `docs/archive/conversations/dominium_domino_codex_planning/dominium_domino_codex_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0081` - `stale_external_claim`

- Source conversation: `dominium_domino_codex_planning`
- Source file: `docs/archive/conversations/dominium_domino_codex_planning/dominium_domino_codex_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0082` - `stale_external_claim`

- Source conversation: `dominium_domino_codex_planning`
- Source file: `docs/archive/conversations/dominium_domino_codex_planning/dominium_domino_codex_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0083` - `conversation_vs_current_queue`

- Source conversation: `dominium_full_conversation`
- Source file: `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`
- Claim: Archived conversation discusses work related to blocked scope `runtime_module_loader`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0084` - `conversation_vs_current_queue`

- Source conversation: `dominium_full_conversation`
- Source file: `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0085` - `conversation_vs_current_queue`

- Source conversation: `dominium_full_conversation`
- Source file: `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`
- Claim: Archived conversation discusses work related to blocked scope `package_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0086` - `conversation_vs_current_queue`

- Source conversation: `dominium_full_conversation`
- Source file: `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0087` - `conversation_vs_current_queue`

- Source conversation: `dominium_full_conversation`
- Source file: `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0088` - `stale_external_claim`

- Source conversation: `dominium_full_conversation`
- Source file: `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0089` - `conversation_vs_current_queue`

- Source conversation: `dominium_setup`
- Source file: `docs/archive/conversations/dominium_setup/dominium_setup_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0090` - `conversation_vs_current_queue`

- Source conversation: `dominium_setup`
- Source file: `docs/archive/conversations/dominium_setup/dominium_setup_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0091` - `stale_external_claim`

- Source conversation: `dominium_setup`
- Source file: `docs/archive/conversations/dominium_setup/dominium_setup_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0092` - `conversation_vs_current_queue`

- Source conversation: `Domino_Dominium_Workbench`
- Source file: `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md`
- Claim: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0093` - `conversation_vs_current_queue`

- Source conversation: `Domino_Dominium_Workbench`
- Source file: `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0094` - `conversation_vs_current_queue`

- Source conversation: `Domino_Dominium_Workbench`
- Source file: `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0095` - `conversation_vs_current_queue`

- Source conversation: `Domino_Dominium_Workbench`
- Source file: `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0096` - `stale_external_claim`

- Source conversation: `Domino_Dominium_Workbench`
- Source file: `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0097` - `conversation_vs_current_queue`

- Source conversation: `domino_engine_refactor_prompts`
- Source file: `docs/archive/conversations/domino_engine_refactor_prompts/dominium_domino_engine_refactor_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0098` - `stale_external_claim`

- Source conversation: `domino_engine_refactor_prompts`
- Source file: `docs/archive/conversations/domino_engine_refactor_prompts/dominium_domino_engine_refactor_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0099` - `stale_external_claim`

- Source conversation: `domino_engine_refactor_prompts`
- Source file: `docs/archive/conversations/domino_engine_refactor_prompts/dominium_domino_engine_refactor_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0100` - `stale_external_claim`

- Source conversation: `domino_engine_refactor_prompts`
- Source file: `docs/archive/conversations/domino_engine_refactor_prompts/dominium_domino_engine_refactor_prompts__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0101` - `conversation_vs_current_queue`

- Source conversation: `engine_baseline_architecture`
- Source file: `docs/archive/conversations/engine_baseline_architecture/domino_dominium_engine_baseline_architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0102` - `conversation_vs_current_queue`

- Source conversation: `engine_baseline_architecture`
- Source file: `docs/archive/conversations/engine_baseline_architecture/domino_dominium_engine_baseline_architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0103` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0104` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `runtime_module_loader`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0105` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0106` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `package_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0107` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0108` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0109` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0110` - `conversation_vs_current_queue`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0111` - `stale_external_claim`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0112` - `stale_external_claim`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0113` - `stale_external_claim`

- Source conversation: `Foundation_Workbench_Codex`
- Source file: `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0114` - `conversation_vs_current_queue`

- Source conversation: `Framework_Open_Source_Provider`
- Source file: `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0115` - `conversation_vs_current_queue`

- Source conversation: `Framework_Open_Source_Provider`
- Source file: `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0116` - `conversation_vs_current_queue`

- Source conversation: `Framework_Open_Source_Provider`
- Source file: `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0117` - `conversation_vs_current_queue`

- Source conversation: `Framework_Open_Source_Provider`
- Source file: `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0118` - `stale_external_claim`

- Source conversation: `Framework_Open_Source_Provider`
- Source file: `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0119` - `stale_external_claim`

- Source conversation: `Framework_Open_Source_Provider`
- Source file: `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0120` - `conversation_vs_current_queue`

- Source conversation: `gui_binary_content`
- Source file: `docs/archive/conversations/gui_binary_content/dominium_gui_binary_content_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0121` - `conversation_vs_current_queue`

- Source conversation: `gui_binary_content`
- Source file: `docs/archive/conversations/gui_binary_content/dominium_gui_binary_content_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0122` - `stale_external_claim`

- Source conversation: `gui_binary_content`
- Source file: `docs/archive/conversations/gui_binary_content/dominium_gui_binary_content_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0123` - `stale_external_claim`

- Source conversation: `gui_binary_content`
- Source file: `docs/archive/conversations/gui_binary_content/dominium_gui_binary_content_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0124` - `stale_external_claim`

- Source conversation: `gui_binary_content`
- Source file: `docs/archive/conversations/gui_binary_content/dominium_gui_binary_content_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0125` - `conversation_vs_current_queue`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0126` - `conversation_vs_current_queue`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0127` - `conversation_vs_current_queue`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0128` - `conversation_vs_current_queue`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0129` - `stale_external_claim`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0130` - `stale_external_claim`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0131` - `stale_external_claim`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Windows 98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0132` - `stale_external_claim`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Mac OS 9`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0133` - `stale_external_claim`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0134` - `stale_external_claim`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0135` - `stale_external_claim`

- Source conversation: `Language_Platform_Architecture`
- Source file: `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0136` - `conversation_vs_current_queue`

- Source conversation: `launcher_app_layer`
- Source file: `docs/archive/conversations/launcher_app_layer/dominium_launcher_app_layer_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0137` - `stale_external_claim`

- Source conversation: `launcher_app_layer`
- Source file: `docs/archive/conversations/launcher_app_layer/dominium_launcher_app_layer_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0138` - `conversation_vs_current_queue`

- Source conversation: `Launcher_Setup_Architecture`
- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0139` - `conversation_vs_current_queue`

- Source conversation: `Launcher_Setup_Architecture`
- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0140` - `stale_external_claim`

- Source conversation: `Launcher_Setup_Architecture`
- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0141` - `stale_external_claim`

- Source conversation: `Launcher_Setup_Architecture`
- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0142` - `stale_external_claim`

- Source conversation: `Launcher_Setup_Architecture`
- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0143` - `stale_external_claim`

- Source conversation: `Launcher_Setup_Architecture`
- Source file: `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0144` - `conversation_vs_current_queue`

- Source conversation: `Modularity_AIDE_Refactorability`
- Source file: `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0145` - `conversation_vs_current_queue`

- Source conversation: `Modularity_AIDE_Refactorability`
- Source file: `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0146` - `stale_external_claim`

- Source conversation: `Modularity_AIDE_Refactorability`
- Source file: `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0147` - `conversation_vs_current_queue`

- Source conversation: `omega_xi_pi_architecture_future`
- Source file: `docs/archive/conversations/omega_xi_pi_architecture_future/dominium_omega_xi_pi_architecture_future_proofing_planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `runtime_module_loader`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0148` - `conversation_vs_current_queue`

- Source conversation: `omega_xi_pi_architecture_future`
- Source file: `docs/archive/conversations/omega_xi_pi_architecture_future/dominium_omega_xi_pi_architecture_future_proofing_planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0149` - `conversation_vs_current_queue`

- Source conversation: `OS_Interface_Repo_Architecture`
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0150` - `conversation_vs_current_queue`

- Source conversation: `OS_Interface_Repo_Architecture`
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0151` - `conversation_vs_current_queue`

- Source conversation: `OS_Interface_Repo_Architecture`
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0152` - `stale_external_claim`

- Source conversation: `OS_Interface_Repo_Architecture`
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Mac OS 8`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0153` - `stale_external_claim`

- Source conversation: `OS_Interface_Repo_Architecture`
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0154` - `stale_external_claim`

- Source conversation: `OS_Interface_Repo_Architecture`
- Source file: `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0155` - `conversation_vs_current_queue`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0156` - `conversation_vs_current_queue`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0157` - `conversation_vs_current_queue`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0158` - `stale_external_claim`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0159` - `stale_external_claim`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0160` - `stale_external_claim`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0161` - `stale_external_claim`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0162` - `stale_external_claim`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0163` - `stale_external_claim`

- Source conversation: `platform_renderer_api_plan`
- Source file: `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0164` - `conversation_vs_current_queue`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0165` - `conversation_vs_current_queue`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0166` - `conversation_vs_current_queue`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0167` - `stale_external_claim`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0168` - `stale_external_claim`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0169` - `stale_external_claim`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0170` - `stale_external_claim`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `WebGPU`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0171` - `stale_external_claim`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `console program`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0172` - `stale_external_claim`

- Source conversation: `platform_support`
- Source file: `docs/archive/conversations/platform_support/dominium_platform_support_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0173` - `conversation_vs_current_queue`

- Source conversation: `Portability_Assurance_Future_Proof`
- Source file: `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0174` - `stale_external_claim`

- Source conversation: `Portability_Assurance_Future_Proof`
- Source file: `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0175` - `stale_external_claim`

- Source conversation: `Portability_Assurance_Future_Proof`
- Source file: `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0176` - `stale_external_claim`

- Source conversation: `readme_ports_determinism`
- Source file: `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0177` - `stale_external_claim`

- Source conversation: `readme_ports_determinism`
- Source file: `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0178` - `stale_external_claim`

- Source conversation: `readme_ports_determinism`
- Source file: `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0179` - `stale_external_claim`

- Source conversation: `readme_ports_determinism`
- Source file: `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `286`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0180` - `stale_external_claim`

- Source conversation: `Refactor_Architecture`
- Source file: `docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0181` - `stale_external_claim`

- Source conversation: `Refactor_Architecture`
- Source file: `docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `CP/M`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0182` - `stale_external_claim`

- Source conversation: `Refactor_Architecture`
- Source file: `docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0183` - `stale_external_claim`

- Source conversation: `Refactor_Architecture`
- Source file: `docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0184` - `conversation_vs_current_queue`

- Source conversation: `Refactor_Control_Plane`
- Source file: `docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0185` - `stale_external_claim`

- Source conversation: `Refactor_Control_Plane`
- Source file: `docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0186` - `conversation_vs_current_queue`

- Source conversation: `Release_Identity_and_Versioning`
- Source file: `docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0187` - `stale_external_claim`

- Source conversation: `Release_Identity_and_Versioning`
- Source file: `docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0188` - `conversation_vs_current_queue`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0189` - `conversation_vs_current_queue`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0190` - `conversation_vs_current_queue`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0191` - `conversation_vs_current_queue`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0192` - `stale_external_claim`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0193` - `stale_external_claim`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0194` - `stale_external_claim`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0195` - `stale_external_claim`

- Source conversation: `testx_repox_governance`
- Source file: `docs/archive/conversations/testx_repox_governance/dominium_testx_repox_governance_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0196` - `stale_external_claim`

- Source conversation: `Timekeeping_and_2038_Resilience`
- Source file: `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0197` - `stale_external_claim`

- Source conversation: `Timekeeping_and_2038_Resilience`
- Source file: `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0198` - `conversation_vs_current_queue`

- Source conversation: `UE6_Domino_Deterministic_Universe`
- Source file: `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0199` - `conversation_vs_current_queue`

- Source conversation: `UE6_Domino_Deterministic_Universe`
- Source file: `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0200` - `stale_external_claim`

- Source conversation: `UE6_Domino_Deterministic_Universe`
- Source file: `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0201` - `stale_external_claim`

- Source conversation: `UE6_Domino_Deterministic_Universe`
- Source file: `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0202` - `conversation_vs_current_queue`

- Source conversation: `ui_editor_tool_editor_planning`
- Source file: `docs/archive/conversations/ui_editor_tool_editor_planning/dominium_ui_editor_tool_editor_planning__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0203` - `conversation_vs_current_queue`

- Source conversation: `ui_editor_tool_editor_planning`
- Source file: `docs/archive/conversations/ui_editor_tool_editor_planning/dominium_ui_editor_tool_editor_planning__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0204` - `stale_external_claim`

- Source conversation: `ui_editor_tool_editor_planning`
- Source file: `docs/archive/conversations/ui_editor_tool_editor_planning/dominium_ui_editor_tool_editor_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0205` - `stale_external_claim`

- Source conversation: `ui_editor_tool_editor_planning`
- Source file: `docs/archive/conversations/ui_editor_tool_editor_planning/dominium_ui_editor_tool_editor_planning__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `Android`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0206` - `conversation_vs_current_queue`

- Source conversation: `Universe_Explorer_Planning`
- Source file: `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0207` - `conversation_vs_current_queue`

- Source conversation: `Universe_Explorer_Planning`
- Source file: `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0208` - `conversation_vs_current_queue`

- Source conversation: `Universe_Explorer_Planning`
- Source file: `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0209` - `conversation_vs_current_queue`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `runtime_module_loader`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0210` - `conversation_vs_current_queue`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `provider_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0211` - `conversation_vs_current_queue`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `package_runtime`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0212` - `conversation_vs_current_queue`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0213` - `conversation_vs_current_queue`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0214` - `conversation_vs_current_queue`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `native_gui`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0215` - `conversation_vs_current_queue`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation discusses work related to blocked scope `release_publication`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0216` - `stale_external_claim`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0217` - `stale_external_claim`

- Source conversation: `Workbench_AIDE_Product_Spine`
- Source file: `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0218` - `conversation_vs_current_queue`

- Source conversation: `World_Architecture`
- Source file: `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0219` - `stale_external_claim`

- Source conversation: `World_Architecture`
- Source file: `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0220` - `stale_external_claim`

- Source conversation: `World_Architecture`
- Source file: `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0221` - `stale_external_claim`

- Source conversation: `World_Architecture`
- Source file: `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0222` - `stale_external_claim`

- Source conversation: `World_Architecture`
- Source file: `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__human_readable_chat_report.txt`
- Claim: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- Conflict target: `README.md / current platform and language baseline`
- Recommended disposition: quarantined until current repo and external facts are checked

### `CONTRA-0223` - `conversation_vs_current_queue`

- Source conversation: `xstack_lab_galaxy`
- Source file: `docs/archive/conversations/xstack_lab_galaxy/dominium_xstack_lab_galaxy_handoff__human_readable_chat_report.txt`
- Claim: Archived conversation discusses work related to blocked scope `gameplay`.
- Conflict target: `.aide/queue/current.toml`
- Recommended disposition: preserve_as_history; require current queue authority before action

### `CONTRA-0224` - `conversation_vs_docs`

- Source conversation: `advanced_simulation_infrastructure, app_testx_codehygiene, architecture_codex_prompts, architecture_ui_providers, Build_and_Future_Proofing, canonical_structure_and_framework, documentation_standards_readme, Dominium_Architecture_I`
- Source file: `multiple primary sources`
- Claim: Corpus contains both `C89` and `C17` claims.
- Conflict target: `current repo authority and conversation cross-check`
- Recommended disposition: quarantined until reviewed

### `CONTRA-0225` - `conversation_vs_docs`

- Source conversation: `advanced_simulation_infrastructure, app_testx_codehygiene, architecture_codex_prompts, architecture_ui_providers, Build_and_Future_Proofing, canonical_structure_and_framework, documentation_standards_readme, Dominium_Architecture_I`
- Source file: `multiple primary sources`
- Claim: Corpus contains both `C++98` and `C++17` claims.
- Conflict target: `current repo authority and conversation cross-check`
- Recommended disposition: quarantined until reviewed



> SOURCE PATH: `docs/archive/conversations/_audit/COVERAGE_GAPS.md`


## Coverage Gaps

Coverage gaps identify incomplete or structurally unclear archived packages.

| Folder | Status | Warnings | Missing Expected Kinds |
| --- | --- | --- | --- |



> SOURCE PATH: `docs/archive/conversations/_audit/INTAKE_ACCEPTANCE_REVIEW.md`


## Intake Acceptance Review

Result: `PASS_WITH_WARNINGS`

This review assesses whether the generated conversation-corpus intake is complete and useful enough to support derived synthesis. It does not promote conversation claims.

### Summary

| Check | Result |
| --- | --- |
| Conversation folders represented | `45` |
| Source files represented | `604` |
| Source files re-counted from disk | `604` |
| SHA-256 lines | `604` |
| Complete packages | `45` |
| Partial packages | `0` |
| Unclear packages | `0` |
| Source file warnings | `0` |
| Reader pages expected / actual | `45` / `45` |
| Promotion candidates | `135` |
| Contradiction findings | `227` |
| Generated Markdown files reviewed | `112` |
| Link issues | `0` |

### Acceptance Findings

- All top-level source packages represented: `True`.
- All source files hashed: `True`.
- Manifest re-scan matches committed manifest: `True`.
- Reader pages are present and advisory-scoped: `True`.
- Wiki topic pages cover manifest topics: `True`.
- Link integrity is clean for generated Markdown: `True`.
- Promotion queue is useful as raw intake, but not clean enough for direct promotion: `True`.
- Contradiction findings are actionable as a review backlog, but remain heuristic and need triage before use as doctrine evidence.

### Warnings Before Synthesis

- Noisy or archival-process promotion candidates: `17`.
- Overlong promotion candidates: `44`.
- Promotion candidates with repo conflict still `not_checked`: `135`.
- Reader placeholder counts: `{'no_stable_decision_lines': 0, 'no_explicit_uncertainty_lines': 0, 'no_explicit_future_work_lines': 0, 'no_rejected_or_superseded_lines': 1}`.
- Contradiction findings are broad and keyword-assisted; use them as review triggers, not resolved conclusions.

### Decision

`PASS_WITH_WARNINGS`

The corpus is ready for derived synthesis if synthesis cites reader/wiki/audit sources directly, keeps repo truth separate from conversation-derived intent, and treats the promotion queue as raw review material. It is not ready for direct live-doc promotion.

### Recommended Fixes Before Promotion

- Triage promotion candidates into serious, historical, stale, noisy, and needs-user-decision buckets.
- Reconcile high-value claims against canon, current queue, contracts, schema law, and implementation only in a separate task.
- Keep the current acceptance result visible in the synthesis book front matter.

### Recommended Next Task

`CONVERSATION-SYNTHESIS-BOOK-01`
