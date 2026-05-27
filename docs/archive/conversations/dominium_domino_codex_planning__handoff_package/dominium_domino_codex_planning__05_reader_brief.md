# Reader Brief — Dominium Domino Codex Planning

## What This Chat Was About

This chat was about preserving and extending planning state for the Dominium + Domino project. The user first supplied a detailed master architecture prompt: Domino is a deterministic ISO C89 fixed-point engine; Dominium is a portable C++98 product suite; platform access goes through dsys; rendering goes through dgfx; GUI/TUI/CLI must share logic; old saves/mods/packs/tools must not silently break. The assistant generated a forward plan and then multiple Codex prompts to implement the architecture in stages.

The first major output was a six-prompt Milestone-0 sequence: specs, repo/CMake skeleton, deterministic numeric core, DOMINIUM_HOME manifest/launcher enumeration, minimal deterministic sim/headless game/TLV save, and launcher-to-game process spawning. The second major output was three prompts for universal CLI, TUI, and GUI layers across launcher, game, setup, and tools. The third output branch generated prompts for shared input/state/IME and multi-window GUI/dgfx pipelines/GPU backend detection. A requested third prompt for pack-system integration was not generated and remains a carry-forward task.

The chat also developed a startup policy: product executables should use CLI when run from a terminal, and when double-clicked/no terminal should try GUI, then TUI, then CLI. Explicit --mode flags should override auto mode; game server/headless flags should force headless. A Codex prompt was generated for this, but it needs design repair before implementation because a shared C startup module directly referencing product-specific C++ wrappers may create link failures.

The user later asked for platform/render/API questionnaire filling based on dominium.zip. The answer given in the prior chat must be treated as unverified until the repo is inspected in a new chat.

## Most Important Things to Know

- Domino must remain ISO C89.
- Dominium product/UI code must remain portable C++98.
- dsys is the only platform abstraction boundary.
- dgfx is the only rendering boundary.
- Simulation must be deterministic and fixed-point.
- Old saves/mods/packs/tools must not silently break.
- Vector-only UI fallback must always work.
- Six Milestone-0 Codex prompts were generated.
- Universal CLI/TUI/GUI prompts were generated.
- Shared input/state/IME and multi-window/dgfx/backend prompts were generated.
- Pack-system integration prompt was requested but not generated.
- Startup policy was designed and prompted.
- Startup prompt has a linker-risk caveat.
- Repo-specific questionnaire facts require verification.

## Active Plans or Workstreams

- WORKSTREAM-01 — Dominium + Domino Core Architecture Continuity
- WORKSTREAM-02 — Milestone-0 Vertical Slice via Six Codex Prompts
- WORKSTREAM-03 — Shared CLI, TUI, and GUI Layers Across Products
- WORKSTREAM-04 — Shared Input System, State Machines, and Cross-Platform IME
- WORKSTREAM-05 — Multi-Window GUI, dgfx Pipelines, and GPU Backend Detection
- WORKSTREAM-06 — Pack System Integration Prompt
- WORKSTREAM-07 — Unified Startup and Mode Dispatcher
- WORKSTREAM-08 — Platform, Renderer, API Questionnaire and Repo-State Answer
- WORKSTREAM-09 — Chat Handoff and Report Package

## Decisions Already Made

- DECISION-01 — Domino engine is ISO C89. (FACT)
- DECISION-02 — Dominium product/UI code may use portable C++98 subset where needed. (FACT)
- DECISION-03 — All platform interaction must go through dsys. (FACT)
- DECISION-04 — All rendering must go through dgfx IR/backends. (FACT)
- DECISION-05 — Software renderer is mandatory baseline. (FACT)
- DECISION-06 — Vector-only fallback UI/pack path must always function. (FACT)
- DECISION-07 — DOMINIUM_HOME repository model is canonical for products, mods, packs, and instances. (FACT)
- DECISION-08 — Backward/forward compatibility is mandatory for saves, packs, mods, tools where possible. (FACT)
- DECISION-10 — Codex prompts should be self-contained implementation packages. (FACT)
- DECISION-11 — CLI/TUI/GUI should be common/shared across launcher, game, setup, and tools. (FACT)
- DECISION-12 — TUI and GUI must use dsys/dgfx abstractions, not direct platform drawing. (FACT)
- DECISION-13 — Input/IME/state machine systems should be shared and deterministic. (FACT)
- DECISION-14 — GPU backend detection must always include software fallback. (FACT)
- DECISION-15 — Terminal invocation with no explicit mode defaults to CLI. (FACT)
- DECISION-16 — Double-click/no-terminal launch defaults to GUI, then TUI, then CLI fallback. (FACT)
- DECISION-21 — This old chat should be exported as a downloadable multi-file report package. (FACT)

## Pending Tasks

- TASK-01 — Verify actual repo state from dominium.zip or current checkout.
- TASK-02 — Determine which generated Codex prompts were executed.
- TASK-03 — Build and run golden target set.
- TASK-04 — Audit generated numeric core for strict C89 and deterministic overflow behavior.
- TASK-05 — Define endian-stable TLV IO helpers if not already present.
- TASK-06 — Verify launcher→game process spawn path and manifest path handling.
- TASK-07 — Keep docs/specs aligned with generated code.
- TASK-08 — Implement or refine common CLI framework.
- TASK-09 — Implement or refine common TUI framework.
- TASK-10 — Implement or refine common GUI framework.
- TASK-11 — Implement shared input/state/IME after inspecting existing modules.
- TASK-12 — Implement or rewrite multi-window/dgfx pipeline/backend detection prompt against actual renderer API.

## Open Questions

- QUESTION-01 — Which generated Codex prompts have actually been applied to the repo?
- QUESTION-02 — What is the actual current repo structure and target list in dominium.zip/current checkout?
- QUESTION-03 — Does the repo already contain files from prompts 1-6?
- QUESTION-04 — How should strict C89 support exact 64-bit types and q48_16 across retro compilers?
- QUESTION-05 — Should TLV save format be native-endian temporarily or endian-stable immediately?
- QUESTION-06 — Where should startup mode dispatch live to avoid C/C++ linker issues?
- QUESTION-07 — Should Windows products be console-subsystem, windows-subsystem, or dual wrapper binaries?
- QUESTION-08 — Should future startup mode overrides via env/config be supported?
- QUESTION-09 — What are final Tier 1/2/3 platform priorities?
- QUESTION-10 — Should common CLI/TUI/GUI prompts be applied as broad prompts or split into smaller implementation prompts?

## Files / Artifacts / Prompts to Preserve

- ARTIFACT-01 — Extended Master Starter Prompt — Dominium + Domino
- ARTIFACT-03 — Forward plan phases 0-12
- ARTIFACT-04 — Codex Prompt 1 — SPEC_IDENTITY + SPEC_PRODUCTS
- ARTIFACT-05 — Codex Prompt 2 — Repo layout, CMake skeleton, core/product targets
- ARTIFACT-06 — Codex Prompt 3 — Deterministic numeric core + test harness
- ARTIFACT-07 — Codex Prompt 4 — DOMINIUM_HOME repo model + launcher enumeration
- ARTIFACT-08 — Codex Prompt 5 — Deterministic sim + headless game + TLV save
- ARTIFACT-09 — Codex Prompt 6 — Launcher to game process spawn via dsys
- ARTIFACT-10 — Prompt A — Universal CLI Layer
- ARTIFACT-11 — Prompt B — Universal TUI Layer
- ARTIFACT-12 — Prompt C — Universal GUI Layer
- ARTIFACT-13 — Prompt — Shared Input System + State Machines + Cross-Platform IME
- ARTIFACT-14 — Prompt — Multi-window GUI + dgfx Pipelines + GPU Backend Detection
- ARTIFACT-15 — Missing Prompt — Pack system integration
- ARTIFACT-16 — Prompt — Unified Startup / Mode Dispatcher
- ARTIFACT-17 — User questionnaire: Platforms, Renderers, APIs, Completion, Repo/build context
- ARTIFACT-18 — User-pasted Codex-in-repo questionnaire answer
- ARTIFACT-19 — Assistant refined questionnaire answer
- ARTIFACT-20 — User-pasted root CMakeLists.txt
- ARTIFACT-21 — User-pasted source/CMakeLists.txt

## What to Verify Before Acting

- VERIFY-01 — Open/extract dominium.zip or current checkout.
- VERIFY-02 — Inspect root CMakeLists.txt, source CMake files, and CMakePresets.json.
- VERIFY-03 — Search for files specified by prompts 1-6.
- VERIFY-04 — Build golden target set and run numeric/headless tests.
- VERIFY-05 — Inspect numeric typedef/fixed-point implementation for C89 compliance.
- VERIFY-06 — Inspect existing CLI/TUI/GUI/input/state modules before applying common-framework prompts.
- VERIFY-07 — Inspect dgfx/render headers and backend implementation names.
- VERIFY-08 — Inspect content/pack/data format docs before generating pack-system prompt.
- VERIFY-09 — Inspect CMake target graph before implementing startup dispatcher.
- VERIFY-10 — Verify platform tier/render backend claims in docs/source.

## Best Next Step

Verify the current repo from `dominium.zip` or the active checkout. Then determine which generated Codex prompts were actually applied. After that, either generate the missing pack-system integration prompt or repair the startup dispatcher implementation design, depending on the user's next instruction.
