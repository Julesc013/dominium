# Reader Brief — Dominium Codex Platform Renderer API Plan

## What This Chat Was About

This chat built a continuity-safe implementation plan for the Dominium/Domino engine. The user wanted ready-to-run prompts for Codex CLI / VS Code Codex running GPT-5.2 on Windows at `c:\Inbox\Git Repos\dominium`, with no interactive approvals and no dependency downloads unless approved. The work evolved from a broad platforms/renderers/APIs prompt request into a final nine-prompt post-master implementation pack. The pack assumes a previous master engine-core prompt plan (prompts 1-14) exists and is implemented for planning purposes, but this is unverified.

The active nine-prompt pack focuses on C89/C++98 baseline enforcement, stable ABI/vtable facades, central capability registry, determinism grades, launcher profiles, CMake presets, null backends, Win32/win32-headless Tier-1 platform completion, software/DX9 Tier-1 renderer completion, Tier-2 gating, TLV-as-ABI, net handshakes, launcher/game GUI smoke tests, end-to-end verification, and changelog tooling. Each prompt requires Codex to make detailed git commits suitable for later changelog generation.

The chat also captured a future AAA roadmap: advanced graphics, audio, input, AI, navigation, terrain, vehicles, economy, combat, weather, networking, setup/download, tools, modding, and scripting. These are future architectural slots, not current implementation scope.

## Most Important Things to Know

- Final active plan is the 9-prompt pack, not earlier superseded plans.
- Domino core must remain ISO C89.
- Dominium layer must remain C++98.
- C99/C11/C++11+ are optional acceleration only.
- No runtime language-standard switching.
- ABI boundaries use C ABI, POD structs, function tables.
- Every interface starts with `u32 abi_version` and `u32 struct_size`.
- Systems use facade + backend architecture.
- Central capability registry chooses backends deterministically.
- Determinism grades are D0/D1/D2.
- Lockstep strict requires D0.
- Serialization is ABI: one chunked/TLV format, skip-unknown, migrations.
- Net handshake includes build ID, schema ID/version, determinism profile, content hashes.
- Codex must commit throughout with detailed messages.
- Repo archive was uploaded but not inspected in this chat.
- Prompt plans are not evidence of implemented code.

## Active Plans or Workstreams

- WORKSTREAM-01: Master deterministic engine-core prompts 1-14.
- WORKSTREAM-02: Active post-master platform/render/API/product completion pack.
- WORKSTREAM-03: Stable API architecture model.
- WORKSTREAM-04: Future AAA roadmap.
- WORKSTREAM-05: This chat report package.

## Decisions Already Made

- Use final 9-prompt pack as active plan.
- Use fewer larger prompts.
- Enforce C89/C++98 baseline.
- Use C ABI/POD/vtable interfaces.
- Use central caps registry and D0/D1/D2 determinism.
- Add launcher/game GUI smoke tests.
- Add changelog-ready commit discipline.

## Pending Tasks

- Verify repo/archive contents.
- Run Prompt 1, then prompts 2-9 in order.
- Resolve DSYS vs `domino_sys_*` if conflict appears.
- Confirm target names.
- Confirm UI text strategy if needed.
- Confirm legacy format migration scope.

## Open Questions

- Were master prompts 1-14 actually implemented?
- Which system API is authoritative?
- What are exact launcher/game targets?
- Is full Tier-2 runtime completion required later?
- What old save/replay/pack formats must be migrated?

## Files / Artifacts / Prompts to Preserve

- `/mnt/data/dominium.zip`
- MASTER prompt plan 1-14
- Final prompts 1-9
- Previous Context Transfer Packet
- This report package and ZIP

## What to Verify Before Acting

- Repo build state.
- CMake target list.
- DSYS/DGFX headers and callsites.
- Public header baseline violations.
- Existing serialization formats.
- Existing UI/text rendering support.

## Best Next Step

Download this package, then if continuing implementation, inspect the repo/archive and run Final Prompt 1 in Codex.
