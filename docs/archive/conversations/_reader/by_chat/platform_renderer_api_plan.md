Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/platform_renderer_api_plan/`
Promotion Status: not_reviewed

# Dominium Codex Platform Renderer API Plan - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning the user's Dominium/Domino engine work into a **high-quality Codex implementation plan**. The user wanted prompts for a coding agent, specifically "Codex CLI running GPT-5.2" or VS Code Codex, to work inside an existing C/CMake/C++ repository and implement missing or unfinished **platforms, renderers, APIs, and integration smoke tests**. The repository path used throughout the prompts was:

The central problem was not simply "write some code." The user wanted a carefully sequenced prompt pack that could guide Codex through a large, risky engine refactor without breaking the repository between steps. The plan had to respect strict constraints: Windows Codex runtime, approval policy `NEVER`, full filesystem access, no dependency downloads unless explicitly approved, and a buildable repo at the end of every prompt. The user also wanted the final prompts to be efficient for GPT-5.2 Codex: fewer, larger prompts rather than many tiny ones, because each Codex run can generate thousands of lines and take a long time.

The chat began with a questionnaire requirement. The user explicitly told the assistant not to assume what "platforms, renderers, APIs, and done" meant. A questionnaire was asked and the user supplied detailed answers: Tier-1 platforms such as Win32 and Win32 headless, Tier-2 platforms such as Linux X11, Wayland, and macOS Cocoa, Tier-1 renderers such as software and D3D9, and future renderers such as D3D11, GL2, Vulkan, Metal, and retro framebuffer backends. The user also explained that the repo has both `dsys_*` and `domino_sys_*` system surfaces, a `dgfx` renderer IR, C89/C++98 language constraints, and expected build targets such as `dominium_game`, `dominium-launcher`, `dominium-setup`, and `domino_numeric_test`.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__human_readable_chat_report.txt`.

## What Was Decided

- The chat ended by generating a maximum-fidelity transfer packet, then a downloadable report package, then an in-chat reader version. The main thing to remember is this: **the active artifact is the final 9-prompt post-master Codex plan, but it is a plan, not evidence that the code exists. The repo must be inspected before execution.
- These ideas became the architectural heart of the final plan.
- Stable ABI boundaries must use C ABI, POD structs, explicit function tables, and `u32 abi_version` plus `u32 struct_size` first.
- Every evolvable subsystem must use a facade/backend model.
- A central capability registry must drive deterministic selection.
- Determinism grades D0/D1/D2 must be formalized.
- Launcher profiles must select feature sets/backends, not language standards.
- Serialization/assets/saves/replays must be treated as ABI.
- Multiplayer handshake fields must include build ID, schema version, determinism profile, and content pack hashes.
- CI/build tooling must include baseline and modern presets, null platform/null renderer, conformance tests, and embedded build metadata.
- The assistant integrated these constraints into a more detailed plan. Then the user asked whether the plan covered everything and said they wanted the final product to be complete as far as platforms, renderers, APIs, and engine, including basic smoke tests in the game and launcher GUIs. The user also clarified a preference for fewer larger prompts.
- This final 9-prompt pack is the main actionable result of the chat.

## What Was Not Decided

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

## Ideas Rejected, Superseded, Or Deprioritised

- This is not a fatal problem for the prompt pack, because the prompts themselves repeatedly tell Codex to discover files with `rg`, `tree`, `type`, CMake commands, and target listing. But it is a major caveat for any future assistant: do not assume the actual repo matches every file path or API name unless checked.
- Runtime feature/backend selection is allowed, but runtime language-standard switching is rejected.
- The plan settled on one chunked/TLV container model with versioned chunks, skip-unknown behavior, deterministic ordering/hashing, and explicit migrations. Networking handshakes must include engine build ID, simulation schema ID/version, determinism profile, and content pack hashes. Mixed versions are rejected unless explicitly supported.
- This matters because the conversation was long and contained multiple plans, superseded options, caveats, and active artifacts. The report package and this plain-language report exist to prevent future assistants from restarting, re-asking, or losing distinctions between decisions, brainstorms, and uncertainties.
- Several earlier prompt plans existed, but the user's later preference for fewer larger prompts and git commit discipline produced the final 9-prompt pack. This is the active implementation plan. Earlier prompt packs are historical or superseded.
- This was explicitly rejected. It was considered only because the user wanted baseline and modern layers, but the user clarified that language standards are compile-time, not runtime-selectable. Runtime selection is allowed for feature profiles and backends only.
- The user prohibited adding dependencies that require downloads unless explicitly approved. This affects Vulkan, Wayland protocols, shader compilers, GLEW/GLAD, DXC, and any future audio/voice codecs. System-provided SDKs may be used when present, but the build system must not fetch dependencies.
- The idea of exposing C++ types or templates across module boundaries was rejected by the stable ABI policy. It might be acceptable inside private implementation code, but not across public/plugin/module boundaries.
- A monolithic platform layer was superseded by platform facets. The old API may remain as a compatibility shim, but the long-term architecture is facet-based.
- Unversioned serialization was rejected. Every save/asset/replay/config format should use a versioned TLV container with skip-unknown behavior and migration paths.

## What Future Work Came From It

- Later, the user expanded the horizon: Dominium should start with simple early graphics and audio, but eventually support AAA-quality graphics, spatial audio, environmental acoustics, proximity chat, AI, navigation, terrain, vehicles, economy, combat, weather, modding, tools, and launcher/setup systems. Those ideas were preserved as a **future roadmap**, not current implementation scope.
- The chat ended by generating a maximum-fidelity transfer packet, then a downloadable report package, then an in-chat reader version. The main thing to remember is this: **the active artifact is the final 9-prompt post-master Codex plan, but it is a plan, not evidence that the code exists. The repo must be inspected before execution.
- The user opened with a precise role assignment: the assistant was to act as a staff software architect, technical program manager, and prompt engineer. The task was to generate **ready-to-run prompts** for Codex CLI running GPT-5.2 so that Codex could implement missing or unfinished platforms, renderers, and APIs in the existing Dominium repository.
- The first procedural rule was that the assistant had to ask a **minimal but complete questionnaire** before generating the prompt pack. The questionnaire had to cover platforms, renderers, APIs, definition of done, and repo/build context. The assistant did that.
- This is not a fatal problem for the prompt pack, because the prompts themselves repeatedly tell Codex to discover files with `rg`, `tree`, `type`, CMake commands, and target listing. But it is a major caveat for any future assistant: do not assume the actual repo matches every file path or API name unless checked.
- After the archive upload, an initial prompt plan was generated for platform and renderer work. It covered CMake platform/backend selection, Win32 and POSIX system backends, X11/Wayland/Cocoa gating, software/DX9/DX11/GL2/Metal/Vulkan renderers, sockets/dynlib, and integration. That plan was useful but did not remain active.
- The user then said they already had a set of pending prompts and pasted a **MASTER CODEX PROMPT PLAN**. This changed the sequence. The assistant was no longer planning from scratch; it had to generate a new plan that assumed this prior master plan had already been implemented.
- The user's master prompt plan was extensive. It covered deterministic simulation and engine-core architecture: invariants, packet ABI, scheduler, fields/events/messages, LOD, pose and anchors, TRANS corridors, STRUCT buildings and enclosures, DECOR signage and surface detail, agents/sensors/minds/actions, graph toolkit, domains/frames/propagators, knowledge/fog/visibility/comms, and determinism hardening.
- UNCERTAIN / UNVERIFIED:** The conversation did not prove that these prompts were actually applied to the repository. They are an assumed prerequisite, not verified code state.
- The user then asked whether the plan would support starting on a GUI launcher and game while allowing future advanced graphics and audio: bloom, ray tracing, spatial audio, proximity chat, environmental acoustics, hearing and seeing distant industry, and evolving from old-school RuneScape-like presentation to Unreal Engine 5-like quality.
- The assistant integrated these constraints into a more detailed plan. Then the user asked whether the plan covered everything and said they wanted the final product to be complete as far as platforms, renderers, APIs, and engine, including basic smoke tests in the game and launcher GUIs. The user also clarified a preference for fewer larger prompts.
- The assistant responded by saying the plan did not yet guarantee "fully complete" enough state, because it needed concrete Tier-1/Tier-2 backend completion gates, GUI smoke tests, and one consolidated verification script. It then produced an optimized prompt pack.

## Important Artifacts

- `manifest`: `1`
- `markdown`: `1`
- `primary_report`: `2`
- `reader_brief`: `1`
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
