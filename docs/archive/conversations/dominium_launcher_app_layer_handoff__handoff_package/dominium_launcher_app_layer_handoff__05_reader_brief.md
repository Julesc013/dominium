# Reader Brief — Dominium Launcher Application Layer Handoff

## What This Chat Was About

This chat focused on the Dominium / Domino application layer, especially the Dominium Launcher. It began with the user asking whether the post-Plan 8 system could support a fast, native-feeling, cross-platform launcher with one common codebase and minimal/no renderer, inspired by pre-2016 Minecraft launcher examples. The discussion evolved into a deeper launcher architecture and repository-boundary conversation.

The major outcome is that older standalone launcher layouts and IDE-project advice were superseded by a canonical product-first monorepo structure. The launcher is now a first-class product under `launcher/`, not an engine subcomponent. Engine purity is locked: engine must not include or export launcher/setup/tools/contracts. Cross-product contracts belong in `libs/contracts/include/dom_contracts`, and canonical schemas live in `schema/`. Setup is the only install mutation authority; launcher consumes setup output through schemas/manifests/contracts only.

The user later pasted application-layer and overall project canon from another chat. That canon says architecture is closed, applications are orchestration shells, CLI is canonical, GUI/TUI are views over the same command graph, UI is data via UI IR, accessibility/localisation are mandatory, tools are read-only by default, and RepoX/TestX/BUILD-ID-0 enforcement must not be bypassed.

Two Codex prompts were said to have been applied: one for CMake/VS2026/build repair and one for engine purity/contract ownership. Their results must still be verified against the repo. The likely next action is to run verification gates, then execute or audit the generated “Launcher Spec Completion, Gap Closure, and Documentation Hardening” prompt.

## Most Important Things to Know

- Architecture is closed; do not redesign.
- Launcher is first-class under `launcher/`.
- Canonical launcher structure: `core/discover`, `core/profile`, `core/invoke`, `ui`, `platform`, `tests`.
- Engine purity is non-negotiable.
- Engine must not include `dom_contracts`.
- Cross-product contracts live in `libs/contracts/include/dom_contracts`.
- Setup is the only install mutation authority.
- Launcher/setup communicate only via schemas, manifests, and contracts.
- CMake is authoritative for VS2026; manual IDE-project advice is superseded.
- CLI is canonical.
- GUI/TUI are views over the same command graph.
- UI is data via UI IR, never business logic.
- Accessibility and localisation are mandatory.
- Apps must run with zero content packs installed.
- RepoX generates changelogs and compatibility/build metadata.
- BUILD-ID-0 versioning and mismatch refusal are locked.
- Actual repo state remains unverified in this package.

## Active Plans or Workstreams

- Launcher product hardening.
- Engine purity verification.
- Setup/launcher boundary enforcement.
- Neutral contracts and schema usage.
- UI command graph/UI IR validation.
- CMake/VS2026/CI gate verification.
- RepoX/TestX/BUILD-ID-0 integration.

## Decisions Already Made

- Launcher is not in engine.
- CMake is the authoritative build graph.
- Setup alone mutates installs.
- CLI is canonical.
- UI IR is required.
- Tools are read-only by default.
- Manual changelogs are rejected.

## Pending Tasks

- Run sanity scripts and build/test gates.
- Determine whether launcher hardening prompt was applied.
- Verify CANON_INDEX and docs status headers.
- Verify command graph and UI IR implementation.
- Verify UI binding validator and zero-pack tests.
- Verify RepoX/build identity launcher behavior.

## Open Questions

- Did applied Codex prompts fully succeed?
- Has launcher hardening already run?
- Do command graph/UI IR/binding validator exist?
- Does launcher run with zero packs and missing locale?
- Does launcher refuse BUILD-ID mismatches?
- Are any shared headers ambiguously owned?

## Files / Artifacts / Prompts to Preserve

- The two applied Codex prompts.
- The launcher hardening prompt.
- Canonical repo update prompt.
- Application-layer canon prompt.
- Latest overall canon prompt.
- Previous Context Transfer Packet.
- Uploaded Plan 8 file/repo archive if available.
- Minecraft launcher reference images as UX background only.

## What to Verify Before Acting

- `scripts/verify_tree_sanity.bat`
- `python scripts/verify_includes_sanity.py`
- `cmake --preset vs2026-x64-debug`
- `cmake --build --preset vs2026-x64-debug`
- `ctest --preset vs2026-x64-debug`
- `launcher --help`
- `setup --help`

## Best Next Step

Run the verification gates, then execute or audit the launcher spec completion/hardening prompt. Do not generate new feature plans until launcher code/docs are confirmed up to spec.
