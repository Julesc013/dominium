Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: legacy top-level `GOVERNANCE.md` FUTURE0 summary
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived public governance overview derived from canon, AGENTS, contracts, and current queue state

# Dominium Governance

This document is the public governance summary for Dominium. It explains how
repo decisions, public claims, implementation changes, and agent work are
expected to stay aligned.

This file is derived. `AGENTS.md` is the canonical governance source for humans,
agents, and tool-mediated repo work. If this file conflicts with
`docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`,
active contracts, `.aide/queue/current.toml`, or reviewed audits, the
higher-authority artifact wins.

## Governance Purpose

Dominium governance exists to prevent simplification drift. It keeps the project
from accidentally converting:

- planned architecture into implemented claims
- generated output into source truth
- renderer or UI convenience into authoritative simulation behavior
- mode flags into product variation
- hidden fallbacks into compatibility behavior
- broad feature work into narrow-slice authorization

## Authority Order

Use this order when interpreting requirements:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. Active contracts, registries, current queue state, and reviewed audits
5. Canonical architecture documents under `docs/architecture/`
6. Public derived docs such as `README.md`, `DOMINIUM.md`, `docs/STATUS.md`,
`docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`
7. Archived or superseded documents, for provenance only

Prompts, chat memory, generated echoes, convenience summaries, and old planning
notes do not override repository truth.

## Non-Negotiable Invariants

All repo work must preserve these invariants unless a higher-authority reviewed
change explicitly updates the governing law:

- authoritative simulation outcomes are deterministic for identical canonical
inputs
- authoritative state mutation occurs only through lawful deterministic Process
execution
- truth, perceived state, and rendering remain separate
- behavior composition comes from profiles, bundles, law surfaces, and
constraints rather than hardcoded runtime mode flags
- capability permits an attempt; law decides accept/refuse/transform
- invalid, unsupported, or incompatible actions produce explicit deterministic
refusals
- packs are data-first and registry/contract governed
- public identity is registered and versioned, not inferred from file existence

## Current Work Boundary

The current queue authorizes narrow governed product-spine work only. It does
not authorize broad feature work.

Currently blocked until a later reviewed phase opens them:

- broad Workbench UI
- runtime module loading
- provider runtime
- package runtime
- gameplay
- renderer implementation
- native GUI
- release publication

Use `docs/STATUS.md`, `docs/ROADMAP.md`, and `.aide/queue/current.toml` before
changing public language about current capability.

## Review Discipline

Explicit review discipline is required for changes that:

- alter canon, glossary, or architecture invariants
- reinterpret authority ordering or governance rules
- change contracts, schemas, registries, public surfaces, compatibility, or
refusal semantics
- change release, publication, trust, security, licensing, or public policy
meaning
- cross ownership-sensitive, projected, transitional, or quarantined roots
- touch broad feature areas that the current queue keeps blocked
- promote generated outputs into source truth

Protected does not mean untouchable. It means the change must be scoped,
authorized, validated, and reported with provenance.

## Public Claim Governance

Public docs must separate:

```text
Implemented
In review
Experimental
Planned
Blocked
Not planned / not current trust model
```

Before making a public claim, identify the evidence source:

| Claim type | Evidence source |
|---|---|
| Current task or queue state | `.aide/queue/current.toml` |
| Foundation status | `docs/repo/FOUNDATION_LOCK.md` |
| Canonical invariant | `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md` |
| Public surface | `contracts/public_surface/public_surface.contract.toml` |
| Command/result/refusal behavior | command, view, diagnostic, refusal, and capability contracts/registries |
| Build/validation status | current queue, test-tier contract, validators, reviewed audits |
| Product architecture | `docs/ARCHITECTURE.md` plus canonical architecture docs |
| Future sequencing | `docs/ROADMAP.md` and current queue |

Do not claim production readiness, full certification, release availability,
complete Workbench UI, gameplay, renderer/native GUI, provider runtime, package
runtime, runtime module loading, or executable mod support unless the relevant
higher-authority artifact explicitly supports it.

## Agent And Tool Governance

Agents and automated tools may help operate the repository, but they do not
replace canon, contracts, validation, or evidence.

Agent work must:

1. use the task shape in `AGENTS.md`
2. state touched paths and relevant invariants
3. state contract/schema impact
4. keep edits inside authorized scope
5. run or report relevant validation
6. avoid describing unrun validation as passed
7. avoid claiming implementation progress from docs-only work
8. treat generated outputs as evidence unless a stronger source promotes them

## Decision Pattern

When deciding whether a change is valid:

```text
1. Does canon allow it?
2. Does glossary meaning stay stable?
3. Does AGENTS.md authorize the work shape?
4. Does the current queue or task scope open the area?
5. Do active contracts/registries need updates?
6. Are deterministic refusal, replay, evidence, and validation implications covered?
7. Are public docs updated without overclaiming?
```

If the answer is unclear, narrow the change instead of widening authority by
assumption.

## Maintenance Rule

When governance meaning changes:

1. Update the governing canon, glossary, `AGENTS.md`, contract, queue, or audit
first.
2. Update this file only as a public derived summary.
3. Update `README.md`, `docs/STATUS.md`, and `docs/ROADMAP.md` if the public
front-door story, current truth boundary, or sequencing changed.
4. Keep the distinction between governance truth and public explanation visible.
