# Aggregator Packet — Dominium Canonical Structure and Domino Framework Architecture

## Packet Metadata

* Chat label: Dominium Canonical Structure and Domino Framework Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial but substantial
* Confidence: 4/5 for accessible substance; lower for exact latest repo state
* Staleness risk: Medium to High for live repo status and third-party versions
* Merge priority: High
* Main limitations: Full transcript not separately exported; some uploads expired; several structure bundles were stale/mixed.

## Ultra-Condensed Carry-Forward Capsule

This chat is the main architecture/convergence thread for Dominium’s repository structure and Domino framework model. The user wanted to stop months of structure churn and finally make the repo suitable for real development. The conversation converged on a closed top-level root model: apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, archive, plus limited project/tooling roots. New top-level framework/modules/plugins/services/profiles/labs/sdk/src/source roots were rejected.

The central doctrine is: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. Domino is the reusable deterministic/runtime framework; Dominium is the game/product family; Workbench is the production/evidence/editor environment; AIDE is the control-plane harness. Domino Framework should not become a `framework/` root. It is represented by contracts, public surfaces, ABI law, service/provider law, public headers, and conformance tests.

The chat defined precise vocabulary: component = source/build unit; service = callable runtime capability; provider = replaceable implementation; pack = authored distributable payload; module = declared extension unit; workspace = Workbench composition; app = product composition; artifact = persisted versioned object. Workbench modules are not the general module system.

Presentation architecture became a major result. CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench panels, AIDE, and CI should all project the same semantic spine: intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view/action model → projection → shell.

The chat also set the raylib/SDL/Lua doctrine. Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and possibly ImGui are providers. Their code belongs under external and runtime provider paths. Third-party types must not leak into engine, game, contracts, content, saves, replays, packs, or public ABI. Provider choices live in profiles, not app path names.

Multiple cleanup tasks/prompts were generated and user-reported commits landed: actual canonical structure cleanup, full-gate legacy path routing, provider structure enforcement, and Domino framework boundary definition. The current state is credible but not full release green. Structure is mostly fixed; fast strict/smoke generally pass or pass with warnings; full CTest/T4 remains debt; broad feature work remains blocked; narrow governed work can continue after gate-specific blockers are repaired.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Closed top-level root set | Requirement | DECISION-01 | Prevents root sprawl | FACT | High |
| P0 | No top-level framework/ | Requirement | DECISION-04 | Preserves contract/public-header model | FACT | High |
| P0 | Service-first provider structure | Requirement | DECISION-06 | Enables raylib/SDL/Lua without lock-in | FACT | High |
| P0 | C-compatible ABI | Requirement | DECISION-05 | Enables portability/replacement | FACT | Medium-High |
| P1 | Projection spine | Requirement | DECISION-08 | Prevents four UI systems | FACT | High |
| P1 | Full CTest/T4 debt remains | Open issue | QUESTION-01 | Blocks release/full proof | FACT | High |

## Workstream Summaries

* ID: WORKSTREAM-01
* Name: Canonical Repository Structure
* Objective: Keep source roots closed and active paths canonical.
* Current state: Mostly clean with warnings.
* Desired end state: No stale active paths; validators enforce structure.
* Priority: P0
* Decisions: DECISION-01, DECISION-02
* Tasks: targeted residuals only.
* Constraints: no new roots, no src/source.
* Artifacts: structure cleanup audits, dirfiles exports.
* Risks: restarting broad churn.
* Open questions: latest live status.
* Next action: verify latest tree if needed.

* ID: WORKSTREAM-04
* Name: Service-first Provider Architecture
* Objective: Use raylib/SDL/Lua as replaceable providers.
* Current state: Provider law/structure reported in place; implementation pending.
* Desired end state: runtime/<service>/providers/<provider> with profiles and conformance.
* Priority: P0
* Decisions: DECISION-06
* Tasks: Provider wedge after proof hygiene.
* Constraints: no third-party leakage.
* Risks: vendor-shaped architecture.
* Open questions: Lua version, external path convention.

## Compact Registers for Merge

Use sections 17–28 of the full register file as authoritative compact registers.

## Possible Cross-Chat Duplicates

Workbench brainstorming, language baseline, raylib/SDL/Lua provider discussions, AIDE workflow law, and worldgen/module composition may overlap with other old chats.

## Possible Cross-Chat Conflicts

Exact naming of `external/upstream` versus `external/vendor`, Lua version, diagnostic/diagnostics root, and the timing of provider wedge versus presentation contract may conflict with later chats.

## Spec Book Integration Guidance

This chat should feed into chapters on repo structure, framework boundary, provider architecture, public surfaces, ABI, Workbench/presentation, modules/packs/apps, testing/proof gates, and AIDE governance. Treat most architecture doctrine as candidate requirements; treat exact current repo status as verification-dependent.

## Aggregator Warnings

Do not merge assistant brainstorming as final user decisions unless user accepted it. Do not overclaim full green. Do not add new roots. Verify live repo state before executing tasks.
