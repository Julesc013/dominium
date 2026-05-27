Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/omega_xi_pi_architecture_future/`
Promotion Status: not_reviewed

# Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was a long-running architectural planning and continuity-preservation conversation for the user's Dominium project. Dominium began in the conversation as a game/engine project, but the user and assistant progressively reframed it as something larger: a deterministic simulation platform, reusable engine, runtime/service host, package ecosystem, product family, agent/human development environment, and release/archive/control plane. The engine layer was repeatedly referred to as Domino; Dominium is the game/product layer built on top of it.

The core user concern throughout the later parts of the chat was future-proofing. The user wanted to know how to make the code portable, modular, extensible, reusable for different games on the same engine, reusable for different engine projects, able to survive rewrites/refactors of entire directories, and engineered like a proper game or operating system rather than a one-off indie project. This led to a doctrine that became the spine of the chat: stable contracts, replaceable implementations, deterministic behavior, manifest-based identity, tool-agnostic development, XStack-enforced architecture, and human-readable plus machine-readable everything.

A huge amount of planning was produced. Earlier material covered MVP scope, Earth/Sol/Galaxy simulation stubs, CLI/TUI/GUI/AppShell concerns, capability negotiation, pack compatibility, library/install/save management, diagnostics and repro bundles, release/distribution, meta-stability, time anchors, architecture audits, universal identity, migration lifecycle, numeric discipline, concurrency, observability, store GC, governance, performance envelopes, archive policy, and final distribution. Later, those became grouped into Omega-series for ultimate MVP/runtime/distribution freezing, Xi-series for repository convergence and drift immunity, and Pi-series for future-series meta-blueprint planning.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `15` source files. The primary extracted source is `docs/archive/conversations/omega_xi_pi_architecture_future/dominium_omega_xi_pi_architecture_future_proofing_planning__01_human_readable_report.md`.

## What Was Decided

- The final strategic direction before this preservation request was to run a ?-series: snapshot intake, reality extraction, blueprint reconciliation, foundation readiness, and final prompt synthesis. This is needed because plans must now be mapped onto current repo reality rather than executed abstractly. The next chat should pick up there.
- The user later reported Xi completion. The enduring lesson is that prompt instructions are not enough; architecture must be machine-readable and enforced.
- 4. Preserve all plans, tasks, constraints, risks, decisions, artifacts, and future directions across chats.
- 1. Current repo reality must be reconciled with the blueprint.
- 2. Final Sigma/Phi/Upsilon/Z execution plans must be generated from current repo reality.
- 3. Exact runtime component boundaries must be mapped to existing code.
- 4. Agent governance and vendor mirrors must be implemented.
- 5. Build/release preset drift must be audited and consolidated.
- 9. **Treat documentation as unquestioned authority.** Rejected. Docs can drift; code/artifacts/XStack must reconcile reality.
- The agent-governance reasoning followed the same pattern. `AGENTS.md` is useful, but prompts and agent docs are not authoritative. They must point to machine-readable artifacts and executable XStack gates. This keeps the repo usable by GPT, Claude, Copilot, Codex, future agents, and humans without locking to any vendor.
- 5. **?-4 Final Prompt Synthesis
- 6. Then final Sigma/Phi/Upsilon/Z planning/execution in repo-specific order.

## What Was Not Decided

- Preserve FACT / INFERENCE / UNCERTAIN labels.
- Do not invent or flatten uncertainty.
- 7. "List all artifacts I should verify in GitHub main."
- 9. "What should I verify before starting Sigma?"

## Ideas Rejected, Superseded, Or Deprioritised

- The user later asked whether suite version should be removed. The answer was no: keep suite version as a human-facing tested baseline, but do not use it as runtime compatibility authority.
- 1. **Remove suite version entirely.** Rejected. Suite version remains useful as a curated snapshot, but not a compatibility authority.
- 2. **Per-product long-lived branches.** Rejected. Recommended single trunk/main with short-lived feature branches and independent product versioning.
- 3. **Create a new ArchX subsystem.** Rejected. Use existing RepoX/AuditX/ControlX/TestX with architecture graph artifact.
- 4. **Implement full materials/fluids/chemistry before MVP.** Rejected/deprioritised. Use proxy stubs for future-proofing.
- 5. **Implement Z hot-swap/live operations immediately.** Rejected/deprioritised. Requires Phi/Upsilon foundations.
- 6. **Build Workbench GUI first.** Rejected/deprioritised. Command/package/presentation floors first.
- 7. **Use `src/`/`source` as active code root.** Rejected for active code. Content provenance `source` pockets remain valid if policy-classified.
- 8. **Optimize for one AI vendor's instruction format.** Rejected. Use canonical governance + generated mirrors.
- 9. **Treat documentation as unquestioned authority.** Rejected. Docs can drift; code/artifacts/XStack must reconcile reality.

## What Future Work Came From It

- After Xi, the assistant planned Pi-series as a meta-blueprint: architecture diagrams, dependency maps, capability ladders, readiness matrices, prompt inventories, and snapshot mapping templates. The user reported Pi-0/Pi-1/Pi-2 were completed and restarted from Xi-8 ground truth, with fingerprints and prompt counts.
- The final strategic direction before this preservation request was to run a ?-series: snapshot intake, reality extraction, blueprint reconciliation, foundation readiness, and final prompt synthesis. This is needed because plans must now be mapped onto current repo reality rather than executed abstractly. The next chat should pick up there.
- The conclusion was that all products should boot through AppShell, use shared command registries, expose descriptors, validate packs/contracts before session start, and never have ad hoc boot paths. This matters for portability, setup/launcher integration, and future distribution.
- The user later reported Xi completion. The enduring lesson is that prompt instructions are not enough; architecture must be machine-readable and enforced.
- The user wanted agent support to work across vendors. The answer was to define a canonical vendor-neutral layer and generate vendor-specific mirrors. Canonical files include AGENTS.md, `.agentignore`, `data/agents/agent_context.json`, and `docs/agents/AGENT_TASKS.md`; mirrors may include Copilot instructions, Claude agent files, Codex skills/MCP wrappers. XStack, not agent prose, enforces truth.
- 4. Preserve all plans, tasks, constraints, risks, decisions, artifacts, and future directions across chats.
- 7. Support future live operations such as hot-swappable renderers and live mod activation, but only after foundations.
- 3. Make the repo robust to future tool/vendor changes.
- 6. Long-term live operations remain future work.
- 4. **Implement full materials/fluids/chemistry before MVP.** Rejected/deprioritised. Use proxy stubs for future-proofing.
- The agent-governance reasoning followed the same pattern. `AGENTS.md` is useful, but prompts and agent docs are not authoritative. They must point to machine-readable artifacts and executable XStack gates. This keeps the repo usable by GPT, Claude, Copilot, Codex, future agents, and humans without locking to any vendor.
- 5. **?-4 Final Prompt Synthesis

## Important Artifacts

- `handoff`: `1`
- `manifest`: `2`
- `markdown`: `1`
- `primary_report`: `2`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `source_input`: `1`
- `spec_sheet`: `1`
- `text`: `2`
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
