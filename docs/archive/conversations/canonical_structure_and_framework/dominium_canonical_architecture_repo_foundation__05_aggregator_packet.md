# Aggregator Packet — Dominium Canonical Architecture, Repository Foundation, and Provider Model

## Packet Metadata

* Chat label: Dominium Canonical Architecture, Repository Foundation, and Provider Model
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial visible transcript with skipped/expired portions
* Confidence: 4/5 for main doctrine, 3/5 for exact chronology/live status
* Staleness risk: Medium to High for repo/library current facts
* Merge priority: High
* Main limitations: Some turns hidden; repo status changed repeatedly; live verification required.

## Ultra-Condensed Carry-Forward Capsule

This chat records the evolution of Dominium from a chaotic directory/refactor problem into a broader Domino/Dominium architecture doctrine. The user’s primary concern was that months of planning and cleanup had blocked actual development. The user wanted structure to be fixed enough to build Workbench, client, engine, game, providers, modules, and packs without repeating the refactor cycle.

The settled top-level source roots are `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`, with `.aide`, `.github`, `.vscode`, and `.aide.local.example` as project/tooling roots. New top-level roots such as `framework`, `modules`, `plugins`, `profiles`, `labs`, `sdk`, `src`, and `source` are rejected unless a future root contract explicitly authorizes them.

The core doctrine is: path is not identity, implementation is not contract, UI is not authority, and generated output is not source truth. Stable identity lives in contracts, manifests, registries, stable IDs, public headers, compatibility corpus, release metadata, and tests. Private implementations live in folders and can be replaced behind conformance and compatibility proof.

Domino is the reusable deterministic substrate/framework. Dominium is one game/product family using Domino. Workbench is the production/editing/validation/evidence environment over shared commands/views/documents/evidence. AIDE is the repo/control-plane harness. Contracts define law; runtime implements services/projections/providers; apps compose products; content supplies authored payload; tools validate/generate/migrate/audit; tests/replay/evidence prove behavior; archive preserves history.

The chat also settled that Domino Framework should not be a new top-level `framework/` root. It should be a public-surface package formed from contracts, public headers, service/provider law, ABI rules, and conformance tests. Mainline language baseline is C17 + C++17, with a C-compatible public ABI and no C++ ABI leakage.

Provider architecture became service-first: `runtime/<service>/providers/<provider>/`. Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and ImGui may be used aggressively as providers, but cannot become engine/game/contracts/content law. Apps remain generic; profiles select providers. Third-party types must not cross stable boundaries.

Many Codex/AIDE prompts and user-reported commits addressed actual cleanup. The final known status is structurally credible but not fully release-green. Full CTest/T4 and stale generated evidence/proof debt remain. Future work should be targeted: proof hygiene, projection conformance, provider conformance, presentation contracts, pack internal layout, and full-gate audits—not broad root redesign.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Closed top-level root model | Decision | DECISION-01 | Prevents root sprawl | FACT | High |
| P0 | No `src/source` wrappers | Constraint | CONSTRAINT-02 | Prevents ownership ambiguity | FACT | High |
| P0 | Domino framework as public surfaces, not root | Decision | DECISION-04 | Prevents `framework/` sprawl | FACT | High |
| P0 | Service-first providers | Decision | DECISION-06 | Enables raylib/SDL/Lua replacement | FACT | High |
| P0 | Verify live repo state | Task | TASK-01 | Reports changed repeatedly | FACT | High |
| P1 | Projection conformance | Task | TASK-04 | Needed before broad UI/Workbench | FACT | Medium |

## Workstream Summaries

See Workstream Register in File 04. Main active workstreams: canonical structure, framework boundary, API/ABI governance, provider architecture, Workbench/product spine, full-gate proof, third-party fencing, preservation.

## Compact Registers for Merge

Use File 04 for complete registers. Merge DECISION-01 through DECISION-09, TASK-01 through TASK-08, CONSTRAINT-01 through CONSTRAINT-07, QUESTION-01 through QUESTION-05, ARTIFACT-01 through ARTIFACT-06, RISK-01 through RISK-05, and VERIFY-01 through VERIFY-05.

## Possible Cross-Chat Duplicates

Workbench module/workspace architecture; raylib/SDL/Lua provider plan; repo structure cleanup; C17/C++17 language baseline; AIDE/Codex workflow law; full-gate proof debt.

## Possible Cross-Chat Conflicts

Older chats may still recommend C89/C++98, top-level `src`, `framework/`, vendor-shaped raylib structure, or Workbench-as-authority. Treat those as superseded unless reaffirmed later.

## Spec Book Integration Guidance

This chat should inform formal requirements for repo layout, public surfaces, ABI law, provider structure, Workbench semantics, proof gates, and third-party boundaries. It should remain background context for emotional/project history but formal requirements should be extracted into concise normative sections.

## Aggregator Warnings

Do not merge assistant brainstorms as user decisions. Preserve uncertainty. Verify current repo state. Do not restart root-structure debate unless fresh evidence shows hard blockers.
