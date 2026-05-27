Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Refactor_Control_Plane/`
Promotion Status: not_reviewed

# AIDE, XStack, and Dominium Refactor Control Plane - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was a long-running architecture, workflow, and project-control discussion around how to use AI coding tools more effectively, how to evolve Dominium's XStack governance system, and how to build AIDE as a portable repo-native operating layer. It began with practical questions about using Codex Pro, the Codex VS Code extension, ChatGPT project spaces, the ChatGPT/Codex apps, Visual Studio, and the API. The user wanted a better way to develop projects, perhaps concurrently and across tools, without manually handing prompts from ChatGPT to Codex.

The conversation quickly shifted from simple prompt engineering toward harness engineering. The central lesson became that high-quality agentic development depends less on one perfect prompt and more on the surrounding system: repo instructions, task contracts, memory, tool permissions, worktree isolation, evidence packets, validation, review gates, branch discipline, and deterministic run paths. This framing then became the lens for evaluating Codex, Claude Code, OpenHands, Continue, oh-my-codex, claw-code, claude-mem, Graphify, and other systems.

A major middle phase focused on XStack. XStack began as a Dominium-specific governance stack grown out of TestX, then expanded into RepoX, AuditX, and other concepts. We initially explored making XStack a general portable metaharness, but that proved too large and too Dominium-shaped. The accepted resolution was that XStack should remain Dominium's strict local profile and proving ground, while AIDE becomes the new portable public layer.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, governance, release, simulation, timekeeping, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `10` source files. The primary extracted source is `docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__01_human_readable_report.md`.

## What Was Decided

- The user then asked about optimizing prompts for GPT-5.3/GPT-5.4 and later supplied advice about harness engineering. That advice argued that teams succeed by engineering the environment around agents: tools, docs, linters, feedback loops, memory, and observability. The conversation accepted the core point: the model is not the whole system; the harness is the multiplier.
- The Grug Brained Developer became a design filter: avoid complexity, avoid premature abstraction, do small safe refactors, prefer integration tests, invest in logging, and respect existing structures before tearing them down. This influenced the decision to narrow AIDE and not overbuild runtime/hosts too early.
- The user eventually named AIDE: Automated Integrated Development Environment. The accepted split became: XStack remains Dominium's strict local governance/proof profile; AIDE becomes the portable public layer. AIDE would live in its own repo, be usable as a standalone repo pack, later as CLI/app/extensions, and eventually perhaps a runtime/service/host system.
- The current Dominium repo has improved governance and build proof but still contains many messy roots. The final plan is AIDE-controlled root recycling: inventory, classify, salvage, move, rewrite references, validate, shim, and retire exceptions. No broad feature work or root moving should occur before CTest/RepoX blockers are classified and AIDE refactor machinery exists.
- The user supplied AIDE advice around dev branches, structured commits, and WorkUnit recovery. The accepted model is `main` as canonical truth, `dev` as governed integration, `task/*` as bounded work, and release/hotfix branches as needed. AIDE should enforce commit trailers, branch roles, safe sync/land/promote/prune, and repo-state-first recovery when prompts are repeated or out of order.
- Unresolved goals include finishing AIDE Q35-Q57, stabilizing Dominium CTest/RepoX blockers, defining final AIDE install/upgrade bundles, implementing root recycling machinery, deciding when product boot proof can proceed, and later deciding whether AIDE Runtime/Gateway/Hosts are truly needed.
- Several decisions are strategic rather than fully implemented. The version/capability model, Git workflow model, install/repair/upgrade model, and tool absorption model are accepted directions but require schemas and code. Future assistants must not mistake them for already completed implementations.
- UNCERTAIN: Exact public-facing naming for AIDE Core/Kernel remains partly open. Exact threshold for accepting CTest-warning status remains a user/repo governance decision. Exact final AIDE installation packaging details remain pending.
- It should not be merged prematurely as final implementation law where items remain planning-level. In particular, Q35-Q57, root recycling, install/upgrade, and capability contracts require current verification and implementation.
- Current Dominium cleanup must be AIDE-controlled root recycling, not folder dragging.
- Future assistants must verify live repo state before implementing.
- "Which decisions here are final, and which are still tentative?"

## What Was Not Decided

- Unresolved goals include finishing AIDE Q35-Q57, stabilizing Dominium CTest/RepoX blockers, defining final AIDE install/upgrade bundles, implementing root recycling machinery, deciding when product boot proof can proceed, and later deciding whether AIDE Runtime/Gateway/Hosts are truly needed.
- 1. Verify current Dominium HEAD and POST-CONVERGE status.
- The user values direct, source-grounded, audit-ready, detailed answers. The user asked for preservation packages that are human-readable and machine-aggregatable. The user repeatedly prefers not to lose nuance, rejected options, uncertainties, or artifacts. The user wants current facts verified when possible and wants future assistants to avoid re-asking answered questions.
- UNCERTAIN: Exact public-facing naming for AIDE Core/Kernel remains partly open. Exact threshold for accepting CTest-warning status remains a user/repo governance decision. Exact final AIDE installation packaging details remain pending.
- Future assistants must verify live repo state before implementing.
- "Merge this with another chat's preservation package without losing uncertainty labels."

## Ideas Rejected, Superseded, Or Deprioritised

- Several decisions are strategic rather than fully implemented. The version/capability model, Git workflow model, install/repair/upgrade model, and tool absorption model are accepted directions but require schemas and code. Future assistants must not mistake them for already completed implementations.
- The user values direct, source-grounded, audit-ready, detailed answers. The user asked for preservation packages that are human-readable and machine-aggregatable. The user repeatedly prefers not to lose nuance, rejected options, uncertainties, or artifacts. The user wants current facts verified when possible and wants future assistants to avoid re-asking answered questions.
- XStack was originally considered as the broader metaharness, but that was rejected. XStack grew from Dominium-specific needs and carries too much local vocabulary. It should remain Dominium's strict local governance/proof profile, but it should not become the public universal system. AIDE should become the portable public layer.
- Dominium is not clean yet. The repo has improved: POST-CONVERGE work made layout authority machine-visible, strict validators pass, VS2022/v143 configure/build pass, and native binaries are produced. But full CTest is still blocked by unit/RepoX issues and wall-time, product boot proof is partial, portable projection proof is partial, and many root exceptions remain. So Dominium should not start major features yet.

## What Future Work Came From It

- The chat opened with the user describing a workflow: paying for Codex Pro, using the Codex VS Code extension on one project at a time, and using ChatGPT project spaces to generate prompts that were manually fed into Codex. The user had also installed the ChatGPT and Codex apps and Visual Studio Community. The initial question was whether there was a better, more professional, more integrated way to develop projects.
- The user then asked about optimizing prompts for GPT-5.3/GPT-5.4 and later supplied advice about harness engineering. That advice argued that teams succeed by engineering the environment around agents: tools, docs, linters, feedback loops, memory, and observability. The conversation accepted the core point: the model is not the whole system; the harness is the multiplier.
- The discussion then mapped these ideas onto Dominium's XStack. We considered adding HarnessX, XPlan, XExec, MergeX, ContextX, SkillX, TaskX, BridgeX, SessionX, PermitX, DoctorX, TraceX, and more. Over time this became too many public concepts. We simplified toward higher-level planes and then eventually concluded that XStack should not be the general product at all.
- The user supplied AIDE advice around dev branches, structured commits, and WorkUnit recovery. The accepted model is `main` as canonical truth, `dev` as governed integration, `task/*` as bounded work, and release/hotfix branches as needed. AIDE should enforce commit trailers, branch roles, safe sync/land/promote/prune, and repo-state-first recovery when prompts are repeated or out of order.
- The user explicitly wanted to improve AI-assisted development, design a better harness, decide XStack's role, create AIDE, align Dominium cleanup with AIDE, use AIDE in Dominium safely, and generate a complete preservation package. These goals mattered because the user is managing long-running complex projects and wants future chats, Codex sessions, and repos to stop losing context or repeating mistakes.
- AIDE changed most. It began as a possible full development environment and became a portable repo operating layer. XStack changed from a candidate universal system to a Dominium strict profile. Repo cleanup changed from moving folders to root recycling under AIDE. AI workflow changed from prompt optimization to harness engineering.
- Several decisions are strategic rather than fully implemented. The version/capability model, Git workflow model, install/repair/upgrade model, and tool absorption model are accepted directions but require schemas and code. Future assistants must not mistake them for already completed implementations.
- The user values direct, source-grounded, audit-ready, detailed answers. The user asked for preservation packages that are human-readable and machine-aggregatable. The user repeatedly prefers not to lose nuance, rejected options, uncertainties, or artifacts. The user wants current facts verified when possible and wants future assistants to avoid re-asking answered questions.
- INFERENCE: The user strongly prefers systems that make future agent work less dependent on long chats. The user also prefers evidence-backed engineering over vibes, and wants repo state to dominate memory. The user appears willing to invest in infrastructure if it reduces future chaos.
- Important artifacts include the canvas documents created earlier, this generated handoff package, live repo files fetched from GitHub, and many external references discussed. The earlier uploaded PDFs/ZIPs have expired, so they cannot be freshly audited. The newly uploaded `Pasted text.txt` provided the preservation-task prompt and drove the package structure.
- The most important live repo artifacts are AIDE README/profile/Harness/AIDE Lite files and Dominium AGENTS/POST_CONVERGE_NEXT_STEPS. The most important generated artifacts are this report package, the context transfer packet, the spec sheet, the registers, the aggregator packet, and the future-chat bootstrap prompt.
- Future assistants must verify live repo state before implementing.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `markdown`: `1`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
