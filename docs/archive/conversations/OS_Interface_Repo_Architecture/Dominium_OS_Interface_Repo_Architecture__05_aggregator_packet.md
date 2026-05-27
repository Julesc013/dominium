# Aggregator Packet — Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer

## Packet Metadata

* Chat label: Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial visible transcript plus surfaced repo evidence
* Confidence: 4/5
* Staleness risk: Medium
* Merge priority: High
* Main limitations: No chronological complete `/docs` walk; no visible `docs.zip`; repo status should be re-verified.

## Ultra-Condensed Carry-Forward Capsule

This chat contributes the strongest synthesis so far of Dominium as a deterministic simulation operating environment and not merely a game, engine, launcher, or editor suite. It began with GUI and binary lane strategy, moved through repo convergence and distribution planning, audited current code/data reality, then evolved into OS-like architecture and finally a reusable Interface Operating Layer.

The core architectural direction is: contracts define law; engine executes deterministic truth; game/domains provide lawful interpreters; runtime provides services and drivers; apps expose userland shells; content/packs mount authored data; release/proof infrastructure verifies and packages everything. The current post-CONVERGE repo roots support this: apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, archive. Domain work must split across contracts/game/content/docs/tests.

The UI/UX direction supersedes the old UI Editor / Tool Editor plan. The final target is a reusable Interface Operating Layer with one command/result/refusal/document/event spine projected into CLI, TUI, rendered GUI, and headless report mode. Workbench is a product/host over this layer, not the layer itself. The Workbench should be a modular rendered userland tools host with modules such as Validation Dashboard, Pack Browser, UI/HUD Sandbox, Renderer Sandbox, Replay/Trace Viewer, Release Forge, and Agent Work Board.

Important caveats: current code is not yet fully data-driven or deeply moddable. The repo has strong documentation, registries, validators, and build targets, but client behavior still includes hard-coded help, command registries, session stages, UI overlay, interaction definitions, software glyphs, and null audio. Product boot and portable projection proof were partial/blocked in inspected docs. Command graph adoption is partial. AppShell currently says rendered mode is client-only, which conflicts with a rendered Workbench; future doctrine must make rendered mode product-declared by capability and contract.

Highest-priority carry-forward items: finish proof spine, formalize operating environment doctrine, formalize interface law, update rendered-mode capability law, unify command dispatch, design module/document/result/refusal schemas, and build a minimal Workbench shell with Validation Dashboard.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Unify command dispatch | Task | TASK-09 | Core to CLI/TUI/rendered/headless parity | FACT/INFERENCE | High |
| P0 | Update rendered-mode law | Decision/task | DECISION-08/TASK-07 | Workbench rendered mode otherwise violates AppShell doctrine | FACT/INFERENCE | Medium |
| P0 | Proof spine | Workstream | WORKSTREAM-02 | Implementation claims need build/boot/projection proof | FACT | Medium |
| P1 | Formalize operating environment | Doctrine | WORKSTREAM-03 | Captures OS-like synthesis | INFERENCE | Medium-high |
| P1 | Build Workbench modular host | Product | WORKSTREAM-06 | Main dogfooding surface | INFERENCE | Medium-high |

## Workstream Summaries

See full Workstream Register in File 04. Priority workstreams: proof spine, Interface Operating Layer, command unification, Workbench, no-assets UI floor, repo ownership.

## Compact Registers for Merge

Decision, task, constraint, open-question, artifact, risk, and verification registers are included in the generated registers file.

## Possible Cross-Chat Duplicates

UI Editor, Workbench, repo convergence, packaging, GUI platform lanes, worldgen/domain split, AIDE/agent work board, release forge.

## Possible Cross-Chat Conflicts

Product names, exact root names, current implementation status, platform support matrix, whether engine is renamed kernel, first Workbench module, plugin policy.

## Spec Book Integration Guidance

Feed this chat into architecture doctrine, interface/UI platform, Workbench, repository ownership, distribution/versioning, and MVP proof-spine chapters. Make CLI/TUI/rendered/headless parity and no-assets UI floor formal requirements after review. Do not merge current implementation-status claims without re-verification.

## Aggregator Warnings

Do not treat assistant proposals as final user decisions. Do not ignore rendered-mode AppShell conflict. Do not put shipped Workbench modules under repo-only tools. Do not assume full data-driven runtime exists already.
