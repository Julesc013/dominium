Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Λ, Σ, Φ, Υ, Ζ
Binding Sources: `docs/planning/BLUEPRINT_RECONCILIATION_REPORT.md`, `data/planning/reconciliation/keep_extend_merge_replace_quarantine.json`, `docs/planning/FOUNDATION_READINESS_REPORT.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`

# Extend-Not-Replace Ledger

## 1. Purpose

This ledger is the anti-reinvention surface for the post-P planning stack.
It records which live repo areas later work should preserve, extend, or consolidate rather than replacing wholesale.

The goal is simple:

- prevent later prompts from discarding live architecture that already matches direction
- force later work to mine existing substrate before inventing new layers
- keep extension-over-replacement explicit across Λ, Σ, Φ, Υ, and Ζ

This ledger does not overrule P-2.
It operationalizes P-2 for later prompt generation.

## 2. Product And Application Roots

| Surface | Path Family | Status | Why Extension Is Preferred | Later Series |
| --- | --- | --- | --- | --- |
| compiled product roots | `client`, `server`, `launcher`, `setup` | `preserve` | these are already the stable product anchors and downstream consumers of semantic, runtime, and release work | `Λ`, `Φ`, `Υ`, `Ζ` |
| tools and appshell surfaces | `appshell`, `tools` | `extend` | the repo already exposes operator- and product-adjacent tooling here, so later work should mine it before creating new operator-facing products | `Σ`, `Φ`, `Υ`, `Ζ` |

## 3. Runtime And Service Surfaces

| Surface | Path Family | Status | Why Extension Is Preferred | Later Series |
| --- | --- | --- | --- | --- |
| engine and game spine | `engine`, `game`, `game/content/core` | `preserve` | this is the strongest live runtime foundation and already embodies the lawful engine/game split | `Λ`, `Φ`, `Υ`, `Ζ` |
| runtime substrate cluster | `app`, `compat`, `control`, `core`, `libs/appcore`, `libs/contracts`, `net`, `process`, `server/net`, `server/persistence`, `server/runtime` | `extend` | the repo already contains distributed runtime, compat, persistence, and orchestration substrate here; later Φ should extract and freeze boundaries from it | `Φ`, `Υ`, `Ζ` |
| thin runtime root caution | `runtime` | `do-not-replace` | this path is not the clear canonical orchestrator home; later prompts must not pivot the entire runtime plan around it | `Φ` |

## 4. Semantic And Domain Surfaces

| Surface | Path Family | Status | Why Extension Is Preferred | Later Series |
| --- | --- | --- | --- | --- |
| core reality and world roots | `worldgen`, `geo`, `reality`, `materials`, `logic`, `signals`, `system`, `universe`, `game/content/core` | `extend` | Λ is formalization over live semantic embodiment, not discovery from zero | `Λ`, `Φ`, `Ζ` |
| specialist domain roots | `epistemics`, `diegetics`, `infrastructure`, `machines`, `embodiment`, `physics`, `chem`, `astro`, `electric`, `pollution`, `packs/domain`, `packs/experience`, `packs/law` | `extend` | these already represent candidate first-class semantic families and should be formalized rather than reinvented | `Λ`, `Σ`, `Φ`, `Υ` |
| pack and registry backbone | `schema`, `packs`, `data/architecture`, `data/registries`, `repo/release_policy.toml` | `preserve` | pack-driven integration, compatibility, and policy meaning already live here and should stay the primary authority backbone | `Λ`, `Φ`, `Υ`, `Ζ` |

## 5. Governance And Instruction Surfaces

| Surface | Path Family | Status | Why Extension Is Preferred | Later Series |
| --- | --- | --- | --- | --- |
| authority planning stack | `AGENTS.md`, `docs/planning` | `do-not-replace` | this is already the live governance and intake spine; later prompts must preserve it as the binding planning layer | `Σ`, `Φ`, `Υ`, `Ζ` |
| mirrored governance docs | `docs/agents`, `docs/governance`, `docs/xstack`, `DOMINIUM.md`, `GOVERNANCE.md`, `README.md`, `SECURITY.md` | `consolidate` | the problem is mirrored ownership and drift, not absence; later Σ should normalize instead of duplicating | `Σ`, `Υ` |
| blueprint archive | `docs/blueprint` | `extend` | the blueprint archive remains useful, but only through the P-2 reconciled lens rather than as raw truth | `Λ`, `Σ`, `Φ`, `Υ`, `Ζ` |

## 6. Release, Versioning, And Control-Plane Surfaces

| Surface | Path Family | Status | Why Extension Is Preferred | Later Series |
| --- | --- | --- | --- | --- |
| control-plane backbone | `release`, `repo`, `updates`, `data/architecture`, `data/registries`, `tools/xstack` | `do-not-replace` | Υ is consolidation over strong existing control-plane and release substrate, not a greenfield control-plane track | `Υ`, `Ζ` |
| operator and trust tooling | `governance`, `security/trust`, `tools/compatx`, `tools/controlx`, `tools/distribution`, `tools/release`, `tools/securex` | `extend` | these tools already embody operator, trust, compat, and release flows that later work should unify rather than bypass | `Σ`, `Υ`, `Ζ` |
| generated release echoes caution | `.xstack_cache`, `artifacts`, `build`, `run_meta` | `consolidate-with-provenance-only` | these are useful evidence surfaces but not primary policy authority; later prompts should consume them only with explicit provenance | `Υ`, `Ζ` |

## 7. Build And Automation Surfaces

| Surface | Path Family | Status | Why Extension Is Preferred | Later Series |
| --- | --- | --- | --- | --- |
| build and CI backbone | `.github/workflows/ci.yml`, `CMakeLists.txt`, `CMakePresets.json`, `cmake`, `scripts`, `setup/packages/scripts` | `do-not-replace` | the repo already has a substantial governed build substrate that later Υ should lock and normalize | `Υ` |
| preset and toolchain matrix | `cmake/ide`, `cmake/toolchains`, `ide/manifests` | `consolidate` | the matrix already exists and should be normalized into doctrine rather than redesigned from scratch | `Υ` |

## 8. Ledger Consequences

The ledger means later prompts must do all of the following:

- preserve live stable anchors before proposing new roots
- extract and formalize runtime/service boundaries from the distributed substrate
- formalize semantic/domain roots instead of inventing a clean-room ontology
- normalize governance mirrors instead of creating new overlapping guidance layers
- consolidate release/versioning/control-plane law over the live release substrate

The ledger also means later prompts must not do any of the following:

- replace product roots because a future architecture looks tidier on paper
- assume runtime invention starts from zero
- treat release/control-plane work as if the repo had not already solved most substrate problems
- duplicate governance or versioning layers because existing ones feel fragmented
- promote generated echoes into canonical release law without provenance

## 9. Human Review Sensitive Entries

The following ledger areas remain review-sensitive:

- `field` versus `fields`
- `schema` versus `schemas`
- `packs` versus `data/packs`
- generated echoes under `build`, `artifacts`, `.xstack_cache`, and `run_meta`

Those areas are not in this ledger as replace targets.
They remain explicit quarantine or merge-review zones.
