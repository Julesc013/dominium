# Reader Brief — Dominium Architecture I

## What This Chat Was About

This chat was a long architecture/specification-generation session for the Dominium Game project. It focused on turning a broad v3 game architecture into concrete, file-by-file `.txt` implementation specs for Codex automation. The user decided that Codex cannot read the entire full conversation at once, so the workflow changed from a single complete spec book to modular prompt files: one `.txt` per repo file.

The visible chat generated many implementation-spec prompts across engine, platform, render, audio, systems, and the start of game. It also preserved important decisions: UTF-8 internal text, retro fallbacks, semantic versioning, build metadata policy, deterministic simulation, strict layering, fixed-pool/no tick allocation, and lockstep/save/replay safety. The visible generation reached `game/g_world.h.txt`; the next file is `game/g_world.cpp.txt` if continuing in strict order.

The chat is partial: many earlier messages are skipped. Top-level docs, legal docs, context MDs, cross-dependencies, volume specs, and possibly early engine files are referenced but not fully visible.

## Most Important Things to Know

- The chat label is **Dominium Architecture I**.
- Scope is this chat only, not the whole Project.
- The current package date anchor is 2026-05-27 Australia/Melbourne.
- Codex per-file devspecs are the active implementation-prep strategy.
- Top-level `.txt` files were skipped because `/docs/...` originals exist.
- If continuing, resume at `game/g_world.cpp.txt`.
- Determinism is mandatory.
- UTF-8 is canonical internally.
- Retro fallbacks are required where feasible.
- Semantic versioning is major.minor.patch.
- Build numbers/dates do not belong in filenames.
- Build metadata should include build numbers/dates.
- Many generated specs are drafts and need audit.
- Duplicate dweather/dhydro/dai_core specs are unresolved.
- dmem and dserialize APIs are inconsistent across drafts.
- C89/C++98 compliance is intended but violated by some generated text.
- External platform/tool/legal claims must be verified.

## Active Plans or Workstreams

- Finish final handoff/report package.
- Continue devspec generation from `game/g_world.cpp.txt`.
- Canonicalise conflicting APIs before coding.
- Finish game/UI/launcher/mods/tools/data/tests/scripts specs.
- Convert specs into actual files.
- Use Codex to implement after canonicalisation.

## Decisions Already Made

- Per-file `.txt` specs for Codex.
- Skip top-level `.txt` specs.
- Strict file order.
- UTF-8 canonical text.
- Semantic versioning and metadata build policy.
- Deterministic core systems.
- Strict layer separation.
- No dynamic allocation in deterministic ticks.

## Pending Tasks

- Download/store this package.
- Continue at `game/g_world.cpp.txt` if requested.
- Resolve dweather/dhydro/dai_core conflicts.
- Normalise dmem/dserialize APIs.
- Audit C89/C++98 compliance.
- Verify platform/library/tool/legal claims.
- Inspect `/docs/...`.

## Open Questions

- Which duplicated system specs are canonical?
- Were missing early/platform specs generated in skipped context?
- Are `/docs/...` docs complete?
- What is the actual retro support tier?
- Is Codex 5.1 Max current and available?

## Files / Artifacts / Prompts to Preserve

- The full generated devspec list.
- All visible generated specs through `g_world.h.txt`.
- Top-level docs references.
- Context MD references.
- Legal/policy doc references.
- Cross-dependencies doc reference.
- This report package.

## What to Verify Before Acting

- `/docs/...` content.
- External API/tool/platform claims.
- Legal docs.
- C89/C++98 compatibility.
- dmem/dserialize canonical APIs.
- Duplicate specs.

## Best Next Step

If continuing documentation: generate **`game/g_world.cpp.txt`** next. If preparing implementation: run an **API canonicalisation pass** first.
