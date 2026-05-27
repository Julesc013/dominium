Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Domino_Dominium_Workbench/`
Promotion Status: not_reviewed

# Domino Dominium Workbench - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This conversation started as a practical plan to build a Windows-first internal UI Editor / Tool Editor to fix the Dominium launcher UI and visually author setup, launcher, game, and tool interfaces. It then evolved into a much larger and more durable architecture: **Dominium Workbench Platform**, a cross-platform rendered, TUI-capable, CLI/headless-compatible, modular production environment for building the entire Domino/Dominium ecosystem.

The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.

The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, setup_launcher, simulation, timekeeping, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `14` source files. The primary extracted source is `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md`.

## What Was Decided

- The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.
- The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.
- The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence.
- The user then rejected the old UI Editor / Tool Editor as final products. The user wanted cross-platform tools that use the same CLI, TUI, and rendered GUI systems as the client, not tools dependent on OS-native widgets. OS-native tools like Visual Studio and Xcode remain useful, but they are not the core presentation platform. This changed the plan from a UI editor to a **Workbench Platform**.
- The final major expansion connected Workbench to the actual game direction. Universe Explorer was framed as a lawful inspection/materialization/reference-frame proof surface, not a renderer/free-camera demo. It should prove scale continuity, no modal loading, reference frames, materialization, representation ladders, interest sets, fidelity, provenance, renderer purity, and evidence.
- Decision:** Old UI Editor and Tool Editor are superseded as final products.
- Decision:** Workbench is not authority.
- Reason:** If Workbench mutates files, truth, or product behavior directly, it will drift from CLI/headless/TUI/runtime semantics. Workbench must issue commands, produce patches, preview, validate, commit transactions, and record evidence.
- Decision:** CLI, TUI, rendered GUI, OS-native GUI, and headless are projections of the same command/result/refusal/document/view model.
- Decision:** OS-native GUI is optional projection, not the core architecture.
- Decision:** TUI is first-class.
- Reason:** It supports servers, SSH, recovery, setup fallback, CI, low-end systems, accessibility, and agent supervision. It must project the same commands and results as GUI/CLI.

## What Was Not Decided

- Reliability note:** This is a human-readable consolidation, not a live repository audit. Repo-current statements that came from pasted material or prior-chat excerpts remain **UNVERIFIED** until checked against the live `julesc013/dominium` repo and current AIDE/validator outputs.
- Verify current live repo status and task gate state.
- > Verify repo state, then generate `COMMAND-RESULT-VIEW-SLICE-01`.

## Ideas Rejected, Superseded, Or Deprioritised

- The original UI Editor / Tool Editor plan is now **superseded as a final product**. It is not lost: its useful parts become Workbench capabilities, especially Interface Studio, UI/HUD Sandbox, Theme Laboratory, TUI Studio, Rendered GUI Studio, Preview Matrix, validation panels, import/export tools, and document-patch workflows.
- The central decision is that Workbench must not become semantic authority. Workbench is a surface over contracts, commands, services, documents, patches, providers, packs, modules, apps, artifacts, diagnostics, evidence, tests, and replay/proof. It is the richest human/agent interface over the system, but it must not bypass command, capability, refusal, validation, document, patch, or proof law.
- That phase generated more Codex prompts: UI discovery/import/export, CLI validate/format/codegen, `ops.json` editing, launcher UI generation, setup UI generation, and hardening/CI. These are now **historical/superseded** but still useful as implementation material for future document/patch/CLI authoring workflows.
- The user then rejected the old UI Editor / Tool Editor as final products. The user wanted cross-platform tools that use the same CLI, TUI, and rendered GUI systems as the client, not tools dependent on OS-native widgets. OS-native tools like Visual Studio and Xcode remain useful, but they are not the core presentation platform. This changed the plan from a UI editor to a **Workbench Platform**.
- Decision:** Old UI Editor and Tool Editor are superseded as final products.
- If you want to continue this work, do not restart with UI Editor. Start from Workbench and the presentation spine.

## What Future Work Came From It

- The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence.
- The resulting old plan included canonical UI IR, deterministic TLV output, JSON mirrors, safe atomic saves, stable IDs, capability validation, layout engines, splitter/tabs/scroll widgets, action stubs, event dispatch, UI Editor GUI, Tool Editor bootstrap, import/export, CLI scripting, `ops.json`, and tests. Many Codex prompts were generated around those ideas.
- The plan was then extended so the UI Editor could import existing tool UIs, provide a CLI suitable for Codex automation, and use scripted `ops.json` changes to create logical "Minecraft-style" launcher and setup layouts. The user clarified that "Minecraft-style" referred to layout and flow, not visual skin. All controls were to remain native Win32 controls in that earlier phase.
- That phase generated more Codex prompts: UI discovery/import/export, CLI validate/format/codegen, `ops.json` editing, launcher UI generation, setup UI generation, and hardening/CI. These are now **historical/superseded** but still useful as implementation material for future document/patch/CLI authoring workflows.
- Reason:** The old plan risked becoming a separate one-off tool architecture. Workbench can instead prove and reuse the same systems as the client, launcher, setup, server, and future tools.
- The renderer does not know what a Validation Dashboard, Pack Browser, Windows XP theme, or Workbench module is. This keeps the renderer reusable by client, setup, launcher, server admin surfaces, Workbench, and future games.
- 7. Use validation dashboard to monitor future work.
- 1. Multiple old UI Editor Codex prompts and prompt plans.
- 2. UU1-UU6 prompt plans for UI import/CLI/ops/launcher/setup tests.
- 3. A VS/Xcode/Linux IDE live-editing prompt.
- 11. Robot seed-civilization Workbench module roadmap.
- Verify current live repo status and task gate state.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `3`
- `markdown`: `1`
- `primary_report`: `2`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`
- `zip`: `1`

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
